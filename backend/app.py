from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import atexit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from routes.products import products_bp
from routes.alerts import alerts_bp
from routes.health import health_bp
from routes.compare import compare_bp
from services.scheduler import update_all_prices
from models.db import init_db
from services.scraper import AmazonScraper
from services.email_service import EmailService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log") if not os.getenv('VERCEL') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
if os.getenv('FLASK_ENV') == 'production':
    # In production, only allow specific origins
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
    CORS(app, origins=allowed_origins)
    logger.info(f"CORS configured for specific origins: {allowed_origins}")
else:
    # In development, allow all origins
    CORS(app)
    logger.info("CORS configured for all origins (development mode)")

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pricepulse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure email settings
app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', 587))
app.config['SMTP_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Register blueprints
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
app.register_blueprint(health_bp, url_prefix='/api/health')
app.register_blueprint(compare_bp, url_prefix='/api/compare')

# Initialize services
scraper = AmazonScraper()
email_service = EmailService(
    app.config['SMTP_SERVER'],
    app.config['SMTP_PORT'],
    app.config['SMTP_USERNAME'],
    app.config['SMTP_PASSWORD']
)

# Add scheduler job
scheduler.add_job(
    func=lambda: update_all_prices(app),
    trigger='interval',
    hours=6,  # Run every 6 hours
    id='price_update_job',
    name='Update product prices',
    replace_existing=True
)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"success": False, "message": "Internal server error"}), 500

# Health check endpoint (root path for serverless environments)
@app.route('/')
def root_health_check():
    return jsonify({
        "status": "OK",
        "message": "PricePulse API is running",
        "environment": os.getenv('FLASK_ENV', 'development'),
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
