import logging
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
import pytz
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_scheduler')

class PriceScheduler:
    """
    Scheduler for automated price tracking.
    Uses APScheduler to run scraping jobs at regular intervals.
    """
    
    def __init__(self, app=None, interval_minutes=60, job_function=None, db=None, models=None):
        """
        Initialize the scheduler.
        
        Args:
            app (Flask): The Flask app instance needed for application context
            interval_minutes (int): Interval in minutes between price checks
            job_function (callable): Function to call for scraping
            db: SQLAlchemy database instance
            models: Dictionary containing database models (e.g., {"Product": ProductModel})
        """
        self.app = app
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
        self.interval_minutes = interval_minutes
        self.job_function = job_function
        self.db = db
        self.models = models
        
        # Track all scheduled job IDs for easier management
        self.scheduled_jobs = set()
        
        logger.info(f"Initializing price scheduler with {interval_minutes} minute interval")
        
        # Log the models information for debugging
        if models:
            try:
                logger.info(f"Models type: {type(models)}")
                logger.info(f"Available models: {list(models.keys()) if isinstance(models, dict) else 'Not a dictionary'}")
            except Exception as e:
                logger.error(f"Error logging models information: {e}")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            if not self.app:
                logger.error("Cannot start scheduler: Flask app instance not provided")
                return False
                
            self.scheduler.start()
            logger.info("Price scheduler started")
            
            # Schedule a job to update all products
            self._schedule_update_all_products_job()
            
            return True
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Price scheduler shutdown")
    
    def _schedule_update_all_products_job(self):
        """Schedule a job to update all products at the specified interval."""
        job_id = 'update_all_products_job'
        
        try:
            # Remove existing job if it exists
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass
        
        # Add the job
        self.scheduler.add_job(
            self._update_all_products,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id=job_id,
            replace_existing=True,
            next_run_time=datetime.now(pytz.UTC)  # Run immediately
        )
        
        logger.info(f"Scheduled job to update all products every {self.interval_minutes} minutes")
    
    def _update_all_products(self):
        """Update all products in the database."""
        if not self.app:
            logger.error("Cannot update products: Flask app instance not provided")
            return
            
        if not self.db or not self.models or not self.job_function:
            logger.error("Cannot update products: db, models, or job_function not set")
            return
        
        logger.info("Running scheduled update for all products")
        
        try:
            # All database operations must be within app context
            with self.app.app_context():
                # Get the Product model from the models dictionary
                try:
                    if not isinstance(self.models, dict):
                        logger.error(f"Models is not a dictionary. Type: {type(self.models)}")
                        return
                        
                    if "Product" not in self.models:
                        logger.error(f"'Product' key not found in models dictionary. Available keys: {list(self.models.keys())}")
                        return
                        
                    ProductModel = self.models["Product"]
                    logger.info(f"Successfully retrieved Product model: {ProductModel}")
                except (TypeError, KeyError) as e:
                    logger.error(f"Invalid models dictionary: 'Product' model not found. Error: {e}")
                    return
                
                # Get all products from the database
                products = ProductModel.query.all()
            
            if not products:
                logger.info("No products found in the database")
                return
            
            logger.info(f"Found {len(products)} products to update")
            
            # Update each product
            for product in products:
                try:
                    # Log the product type for debugging
                    product_type = type(product)
                    logger.info(f"Product type: {product_type}")
                    
                    # Handle both dictionary and object access patterns
                    if isinstance(product, dict):
                        product_id = product.get('id', 'unknown')
                        product_name = product.get('name', 'unknown')
                        product_url = product.get('url', '')
                        logger.info(f"Updating product (dict): {product_name} (ID: {product_id})")
                    else:
                        # Assume it's an ORM object with attributes
                        product_id = getattr(product, 'id', 'unknown')
                        product_name = getattr(product, 'name', 'unknown')
                        product_url = getattr(product, 'url', '')
                        logger.info(f"Updating product (object): {product_name} (ID: {product_id})")
                    
                    # Only proceed if we have a URL
                    if product_url:
                        # Run job function within app context
                        with self.app.app_context():
                            self.job_function(product_url, self.db, self.models)
                    else:
                        logger.warning(f"Cannot update product {product_id}: URL is missing")
                        
                except AttributeError as e:
                    logger.error(f"AttributeError with product: {e}")
                    logger.error(f"Product data: {product}")
                    # Try alternate access method if first one fails
                    try:
                        # All operations within app context
                        with self.app.app_context():
                            if hasattr(product, 'Product'):
                                # This handles the case where product is an object with a Product attribute
                                p = product.Product
                                logger.info(f"Found nested Product object, trying to update with URL: {p.url}")
                                self.job_function(p.url, self.db, self.models)
                            elif isinstance(product, dict) and 'Product' in product:
                                # This handles the case where product is a dict with a 'Product' key
                                p = product['Product']
                                product_url = p.get('url') if isinstance(p, dict) else p.url
                                logger.info(f"Found nested Product in dict, trying to update with URL: {product_url}")
                                self.job_function(product_url, self.db, self.models)
                            else:
                                logger.error("Could not access product data in any format")
                    except Exception as nested_e:
                        logger.error(f"Failed alternate access method: {nested_e}")
                except Exception as e:
                    # Get the product ID for the error message, handling both dict and object
                    try:
                        product_id = product.id if hasattr(product, 'id') else product.get('id', 'unknown')
                        logger.error(f"Error updating product {product_id}: {e}")
                    except:
                        logger.error(f"Error updating product (could not get ID): {e}")
            
            logger.info("Completed scheduled update for all products")
        
        except Exception as e:
            logger.error(f"Error in scheduled update: {e}")
            # Log more details about the exception
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def add_product(self, product_id, product_url):
        """
        Add a product to be tracked immediately.
        
        Args:
            product_id (int): The product ID
            product_url (str): The product URL
        """
        if not self.app:
            logger.error("Cannot add product: Flask app instance not provided")
            return False
            
        if not self.job_function:
            logger.error("Cannot add product: job_function not set")
            return False
        
        logger.info(f"Adding product {product_id} to scheduler for immediate tracking")
        
        try:
            # Run the job immediately for the new product
            if self.db and self.models:
                # Log the models type for debugging
                logger.info(f"Models type: {type(self.models)}")
                # Run within app context
                with self.app.app_context():
                    self.job_function(product_url, self.db, self.models)
                return True
            else:
                logger.error("Cannot add product: db or models not set")
                return False
        except Exception as e:
            logger.error(f"Error adding product {product_id} to scheduler: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
            
    def update_interval(self, minutes):
        """
        Update the interval between price checks.
        
        Args:
            minutes (int): New interval in minutes
        """
        if minutes < 1:
            logger.error("Invalid interval: must be at least 1 minute")
            return False
        
        logger.info(f"Updating scheduler interval from {self.interval_minutes} to {minutes} minutes")
        
        self.interval_minutes = minutes
        
        # Reschedule the update job with the new interval
        self._schedule_update_all_products_job()
        
        return True