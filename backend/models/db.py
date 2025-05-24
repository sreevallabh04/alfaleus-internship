from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

def get_db_url():
    """Get database URL with proper configuration for production/development"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.warning("DATABASE_URL not found, using SQLite as fallback")
        return 'sqlite:///pricepulse.db'
    
    # For Neon PostgreSQL, we need to configure SSL and connection pooling
    if 'neon.tech' in database_url:
        logger.info("Neon PostgreSQL detected, configuring for serverless environment")
        
        # In serverless environments like Vercel, we should use NullPool
        # to avoid connection pool issues with ephemeral functions
        if os.getenv('VERCEL', 'false').lower() == 'true':
            engine = create_engine(database_url, poolclass=NullPool, connect_args={
                "sslmode": "require"
            })
            return engine.url
    
    return database_url

def init_db(app):
    """Initialize database with proper configuration"""
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before using them
        'pool_recycle': 300,    # Recycle connections every 5 minutes
    }
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created or verified")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
