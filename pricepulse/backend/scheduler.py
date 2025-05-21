import logging
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
    
    def __init__(self, interval_minutes=60, job_function=None, db=None, models=None):
        """
        Initialize the scheduler.
        
        Args:
            interval_minutes (int): Interval in minutes between price checks
            job_function (callable): Function to call for scraping
            db: SQLAlchemy database instance
            models: Database models module
        """
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
        self.interval_minutes = interval_minutes
        self.job_function = job_function
        self.db = db
        self.models = models
        
        # Track all scheduled job IDs for easier management
        self.scheduled_jobs = set()
        
        logger.info(f"Initializing price scheduler with {interval_minutes} minute interval")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Price scheduler started")
            
            # Schedule a job to update all products
            self._schedule_update_all_products_job()
    
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
        if not self.db or not self.models or not self.job_function:
            logger.error("Cannot update products: db, models, or job_function not set")
            return
        
        logger.info("Running scheduled update for all products")
        
        try:
            # Get all products from the database
            products = self.models.Product.query.all()
            
            if not products:
                logger.info("No products found in the database")
                return
            
            logger.info(f"Found {len(products)} products to update")
            
            # Update each product
            for product in products:
                try:
                    logger.info(f"Updating product: {product.name} (ID: {product.id})")
                    self.job_function(product.url, self.db, self.models)
                except Exception as e:
                    logger.error(f"Error updating product {product.id}: {e}")
            
            logger.info("Completed scheduled update for all products")
        
        except Exception as e:
            logger.error(f"Error in scheduled update: {e}")
    
    def add_product(self, product_id, product_url):
        """
        Add a product to be tracked immediately.
        
        Args:
            product_id (int): The product ID
            product_url (str): The product URL
        """
        if not self.job_function:
            logger.error("Cannot add product: job_function not set")
            return False
        
        logger.info(f"Adding product {product_id} to scheduler for immediate tracking")
        
        try:
            # Run the job immediately for the new product
            if self.db and self.models:
                self.job_function(product_url, self.db, self.models)
                return True
            else:
                logger.error("Cannot add product: db or models not set")
                return False
        except Exception as e:
            logger.error(f"Error adding product {product_id} to scheduler: {e}")
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