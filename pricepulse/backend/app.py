import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import time

# Import application modules
from models import db, Product, PriceRecord, PriceAlert
from scraper import scrape_product
from scheduler import PriceScheduler
from email_service import send_price_alert_email

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_pulse_app')

# Create scheduler as a global variable
scheduler = None

def create_app():
    """Create and configure the Flask application."""
    global scheduler
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure CORS with more specific settings
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///pricepulse.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            # Don't raise here, let the app continue to start
    
    # Initialize the scheduler
    try:
        scheduler_interval = int(os.getenv('SCHEDULER_INTERVAL_MINUTES', 60))
        # Create explicit model dictionary instead of globals()
        model_dict = {
            "Product": Product,
            "PriceRecord": PriceRecord,
            "PriceAlert": PriceAlert
        }
        scheduler = PriceScheduler(
            app=app,  # Pass the Flask app instance for context
            interval_minutes=scheduler_interval,
            job_function=scrape_product,
            db=db,
            models=model_dict  # Pass explicit model dictionary
        )
        scheduler.start()
        logger.info(f"Scheduler started with {scheduler_interval} minute interval")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        import traceback
        logger.error(f"Scheduler error details: {traceback.format_exc()}")
        # Don't raise here, the app can function without the scheduler
    
    # Register API routes with the app
    register_routes(app)
    
    return app

def register_routes(app):
    """Register API routes with the Flask app."""
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'ok',
            'message': 'PricePulse API is running'
        })

    @app.route('/api/products', methods=['GET'])
    def get_products():
        """Get all tracked products."""
        try:
            products = Product.query.all()
            return jsonify({
                'success': True,
                'products': [product.to_dict() for product in products]
            })
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve products'
            }), 500

    @app.route('/api/products', methods=['POST'])
    def add_product():
        """Add a new product to track."""
        try:
            data = request.json
            
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            url = data['url']
            
            # Check if product already exists
            existing_product = Product.query.filter_by(url=url).first()
            if existing_product:
                return jsonify({
                    'success': True,
                    'message': 'Product is already being tracked',
                    'product': existing_product.to_dict()
                })
            
            # Scrape product and add to database
            # Create model dictionary for scraper
            model_dict = {
                "Product": Product,
                "PriceRecord": PriceRecord,
                "PriceAlert": PriceAlert
            }
            result = scrape_product(url, db, model_dict)
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to scrape product')
                }), 400
            
            # Add to scheduler for tracking
            if scheduler:
                scheduler.add_product(result['product_id'], url)
            
            # Get the product to return in response
            product = Product.query.get(result['product_id'])
            
            return jsonify({
                'success': True,
                'message': 'Product added successfully',
                'product': product.to_dict()
            })
        
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to add product'
            }), 500

    @app.route('/api/products/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        """Get product details by ID."""
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return jsonify({
                    'success': False,
                    'error': 'Product not found'
                }), 404
            
            return jsonify({
                'success': True,
                'product': product.to_dict()
            })
        
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve product'
            }), 500

    @app.route('/api/products/<int:product_id>/prices', methods=['GET'])
    def get_price_history(product_id):
        """Get price history for a product."""
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return jsonify({
                    'success': False,
                    'error': 'Product not found'
                }), 404
            
            # Get price records
            price_records = PriceRecord.query.filter_by(product_id=product_id).order_by(PriceRecord.timestamp).all()
            
            return jsonify({
                'success': True,
                'product': product.to_dict(),
                'price_history': [record.to_dict() for record in price_records]
            })
        
        except Exception as e:
            logger.error(f"Error getting price history for product {product_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve price history'
            }), 500

    @app.route('/api/alerts', methods=['POST'])
    def create_alert():
        """Create a new price alert."""
        try:
            data = request.json
            
            if not data or 'product_id' not in data or 'email' not in data or 'target_price' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Product ID, email, and target price are required'
                }), 400
            
            product_id = data['product_id']
            email = data['email']
            target_price = float(data['target_price'])
            
            # Check if product exists
            product = Product.query.get(product_id)
            if not product:
                return jsonify({
                    'success': False,
                    'error': 'Product not found'
                }), 404
            
            # Check if alert already exists
            existing_alert = PriceAlert.query.filter_by(
                product_id=product_id,
                email=email
            ).first()
            
            if existing_alert:
                # Update existing alert
                existing_alert.target_price = target_price
                existing_alert.alert_sent = False  # Reset alert flag
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Price alert updated',
                    'alert': existing_alert.to_dict()
                })
            
            # Create new alert
            alert = PriceAlert(
                product_id=product_id,
                email=email,
                target_price=target_price
            )
            db.session.add(alert)
            db.session.commit()
            
            # Get latest price
            latest_price_record = PriceRecord.query.filter_by(product_id=product_id).order_by(PriceRecord.timestamp.desc()).first()
            
            # Check if should send alert right away
            if latest_price_record and latest_price_record.price <= target_price:
                alert.alert_sent = True
                db.session.commit()
                
                # Send email
                send_price_alert_email(alert, product, latest_price_record.price)
            
            return jsonify({
                'success': True,
                'message': 'Price alert created',
                'alert': alert.to_dict()
            })
        
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to create price alert'
            }), 500

    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    def delete_product(product_id):
        """Delete a product and related data."""
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return jsonify({
                    'success': False,
                    'error': 'Product not found'
                }), 404
            
            # Product will be deleted along with related price records and alerts
            # due to cascade option in the model relationships
            db.session.delete(product)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Product deleted successfully'
            })
        
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to delete product'
            }), 500

    @app.route('/api/test-scraper', methods=['POST'])
    def test_scraper():
        """Test the scraper with a URL without saving to database."""
        try:
            data = request.json
            
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            # Import directly to avoid circular imports
            from scraper import extract_amazon_product_info
            
            url = data['url']
            result = extract_amazon_product_info(url)
            
            return jsonify(result)
        
        except Exception as e:
            logger.error(f"Error testing scraper: {e}")
            return jsonify({
                'success': False,
                'error': 'Scraper test failed'
            }), 500

# Create app instance
if __name__ == '__main__':
    app = create_app()
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"Starting PricePulse backend on {host}:{port}")
    app.run(host=host, port=port, debug=True)
else:
    app = create_app()