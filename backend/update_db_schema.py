"""
Database Schema Update Script

This script updates the price_records table to add the 'platform' column
that is defined in the model but missing from the actual database schema.
"""
import os
import sys
import logging
import sqlite3
from flask import Flask
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def update_sqlite_schema():
    """
    Update the SQLite database schema to add the platform column
    to the price_records table if it doesn't exist.
    """
    try:
        # Get the database path
        db_path = os.getenv('DATABASE_URL', 'sqlite:///pricepulse.db')
        
        # Remove sqlite:/// prefix if present
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]
        
        # Make sure path is relative to backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(backend_dir, db_path)
            
        logger.info(f"Connecting to SQLite database at: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the platform column exists
        cursor.execute("PRAGMA table_info(price_records)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'platform' not in column_names:
            logger.info("'platform' column does not exist in price_records table. Adding it now...")
            
            # Add the platform column with default value 'Amazon'
            cursor.execute("ALTER TABLE price_records ADD COLUMN platform TEXT NOT NULL DEFAULT 'Amazon'")
            conn.commit()
            
            logger.info("Successfully added 'platform' column to price_records table")
        else:
            logger.info("'platform' column already exists in price_records table")
        
        # Close the connection
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database schema update")
    
    # Check database type
    db_url = os.getenv('DATABASE_URL', '')
    
    if 'sqlite' in db_url or db_url == '':
        success = update_sqlite_schema()
    else:
        logger.error(f"Unsupported database type: {db_url}")
        logger.error("This script only supports SQLite databases")
        sys.exit(1)
    
    if success:
        logger.info("Database schema update completed successfully")
        sys.exit(0)
    else:
        logger.error("Database schema update failed")
        sys.exit(1)