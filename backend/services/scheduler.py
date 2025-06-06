import logging
import time
import random
import traceback
import statistics
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from models.db import db
from models.product import Product
from models.price_record import PriceRecord
from models.price_alert import PriceAlert
from services.scraper import scrape_product, AmazonScraper
from services.flipkart_scraper import scrape_flipkart_price
from services.email_service import send_price_alert_email
from services.ai_service import extract_product_metadata, search_other_platforms
from datetime import datetime, timedelta
from models.price_history import PriceHistory

logger = logging.getLogger(__name__)

# Constants for retry and rate limiting
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # Base delay in seconds
RATE_LIMIT_DELAY = 1.5  # Delay between requests to avoid rate limiting

# Constants for prioritization
DEFAULT_UPDATE_INTERVAL = 24  # Default hours between updates for normal priority products
MAX_PRODUCTS_PER_RUN = 100  # Maximum number of products to update in one run (0 for no limit)
VOLATILITY_WINDOW_DAYS = 7  # Number of days to look back for volatility calculation
ALERT_PRIORITY_MULTIPLIER = 2.0  # Priority multiplier for products with active alerts
RECENT_PRICE_CHANGE_WINDOW_HOURS = 48  # Window to consider recent price changes
RECENT_PRICE_CHANGE_MULTIPLIER = 1.5  # Priority multiplier for products with recent price changes

def calculate_update_priority(product, current_time=None):
    """
    Calculate a priority score for updating a product based on multiple factors.
    Higher scores indicate higher priority for updates.
    
    Factors considered:
    1. Time since last update (older updates get higher priority)
    2. Price volatility (more volatile products get higher priority)
    3. Number of active alerts (products with alerts get higher priority)
    4. Recent price changes (products with recent changes get higher priority)
    
    Returns:
        dict: Contains priority score and component factors
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    priority_data = {
        'product_id': product.id,
        'product_name': product.name,
        'time_factor': 0,
        'volatility_factor': 0,
        'alert_factor': 0,
        'recent_change_factor': 0,
        'total_score': 0
    }
    
    try:
        # 1. Time since last update factor
        time_since_update = 0
        if product.updated_at:
            hours_since_update = (current_time - product.updated_at).total_seconds() / 3600
            # Normalize against expected update interval
            time_since_update = hours_since_update / DEFAULT_UPDATE_INTERVAL
        else:
            # Never updated products get highest priority
            time_since_update = 5.0
        priority_data['time_factor'] = time_since_update
        
        # 2. Price volatility factor (based on coefficient of variation)
        try:
            lookback_date = current_time - timedelta(days=VOLATILITY_WINDOW_DAYS)
            recent_prices = db.session.query(PriceRecord.price).filter(
                PriceRecord.product_id == product.id,
                PriceRecord.platform == 'Amazon',  # Focus on main platform for volatility
                PriceRecord.timestamp >= lookback_date
            ).all()
            
            prices = [p[0] for p in recent_prices]
            if len(prices) >= 3:  # Need at least 3 data points for meaningful volatility
                mean_price = statistics.mean(prices)
                if mean_price > 0:
                    std_dev = statistics.stdev(prices)
                    # Coefficient of variation (higher value = more volatile)
                    volatility = std_dev / mean_price
                    priority_data['volatility_factor'] = min(volatility * 10, 3.0)  # Cap at 3.0
                else:
                    priority_data['volatility_factor'] = 0
            else:
                # Not enough data points, give medium-low priority
                priority_data['volatility_factor'] = 0.5
        except Exception as e:
            logger.warning(f"Error calculating volatility for product {product.id}: {str(e)}")
            priority_data['volatility_factor'] = 0.5  # Default to medium-low priority
        
        # 3. Active alerts factor
        active_alerts = db.session.query(func.count(PriceAlert.id)).filter(
            PriceAlert.product_id == product.id,
            PriceAlert.triggered == False
        ).scalar()
        
        # Products with alerts get higher priority
        if active_alerts > 0:
            priority_data['alert_factor'] = min(active_alerts * 0.5, 2.0) * ALERT_PRIORITY_MULTIPLIER
        
        # 4. Recent price changes factor
        recent_change_window = current_time - timedelta(hours=RECENT_PRICE_CHANGE_WINDOW_HOURS)
        recent_price_changes = db.session.query(PriceRecord).filter(
            PriceRecord.product_id == product.id,
            PriceRecord.timestamp >= recent_change_window
        ).order_by(desc(PriceRecord.timestamp)).limit(5).all()
        
        if len(recent_price_changes) >= 2:
            # Check if there's a significant price change in recent records
            prices = [record.price for record in recent_price_changes]
            max_price = max(prices)
            min_price = min(prices)
            
            if max_price > 0:  # Avoid division by zero
                price_range_percent = (max_price - min_price) / max_price * 100
                
                if price_range_percent >= 5.0:  # 5% or more variation in recent prices
                    priority_data['recent_change_factor'] = RECENT_PRICE_CHANGE_MULTIPLIER
        
        # Calculate total priority score (sum of all factors)
        priority_data['total_score'] = (
            priority_data['time_factor'] + 
            priority_data['volatility_factor'] + 
            priority_data['alert_factor'] + 
            priority_data['recent_change_factor']
        )
        
    except Exception as e:
        logger.error(f"Error calculating priority for product {product.id}: {str(e)}")
        logger.debug(traceback.format_exc())
        # Default to medium priority based on time since update only
        priority_data['total_score'] = priority_data['time_factor']
    
    return priority_data

def update_all_prices(app, max_products=MAX_PRODUCTS_PER_RUN):
    """
    Update prices for all tracked products.
    This function is called by the scheduler.
    """
    with app.app_context():
        try:
            # Get all products that need price updates
            products = Product.query.limit(max_products).all()
            logger.info(f"Updating prices for {len(products)} products")
            
            scraper = AmazonScraper()
            
            for product in products:
                try:
                    # Scrape current price
                    success, data = scraper.scrape_product(product.amazon_url)
                    
                    if success:
                        # Update product price
                        product.current_price = data['current_price']
                        product.updated_at = datetime.utcnow()
                        
                        # Add price to history
                        price_history = PriceHistory(
                            product_id=product.id,
                            price=data['current_price']
                        )
                        db.session.add(price_history)
                        
                        logger.info(f"Updated price for product {product.id}: {data['current_price']}")
                    else:
                        logger.error(f"Failed to scrape price for product {product.id}: {data.get('error')}")
                
                except Exception as e:
                    logger.error(f"Error updating price for product {product.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            logger.info("Completed price update cycle")
            
        except Exception as e:
            logger.error(f"Error in price update cycle: {str(e)}")
            db.session.rollback()

def update_product_with_retries(product):
    """
    Update a single product with retry logic
    Returns True if successful, False otherwise
    """
    for attempt in range(MAX_RETRIES):
        try:
            # If not first attempt, add exponential backoff delay
            if attempt > 0:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                logger.info(f"Retry attempt {attempt+1} for product {product.id} after {delay:.2f}s delay")
                time.sleep(delay)
            
            # Create a new transaction for this attempt
            update_product_prices_for_all_platforms(product)
            db.session.commit()
            
            logger.info(f"Successfully updated product {product.id} on attempt {attempt+1}")
            return True
            
        except SQLAlchemyError as db_err:
            # Database-related errors
            logger.error(f"Database error updating product {product.id} (attempt {attempt+1}/{MAX_RETRIES}): {str(db_err)}")
            db.session.rollback()
            
            # If this was the last attempt, mark as failed
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to update product {product.id} after {MAX_RETRIES} attempts")
                return False
                
        except Exception as e:
            # Other errors
            logger.error(f"Error updating product {product.id} (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}")
            logger.debug(traceback.format_exc())
            db.session.rollback()
            
            # If this was the last attempt, mark as failed
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to update product {product.id} after {MAX_RETRIES} attempts")
                return False
    
    return False  # Should never reach here, but just in case


def update_product_prices_for_all_platforms(product):
    """
    Update prices for a single product across its main platform and other found platforms.
    """
    logger.info(f"Updating prices for product: {product.name} (ID: {product.id})")
    
    # Track whether we successfully updated at least one price source
    updated_any_price = False
    last_exception = None

    # --- Update price for the main product URL (assuming Amazon) ---
    try:
        product_data = scrape_product(product.url)
        
        if product_data and 'price' in product_data and product_data['price'] is not None:
            new_price = product_data['price']
            old_price = product.current_price
            
            # Validate price data
            if not isinstance(new_price, (int, float)) or new_price <= 0:
                logger.warning(f"Invalid price data for product {product.id}: {new_price}. Skipping update.")
            else:
                # Update product's current price and timestamp
                product.current_price = new_price
                product.updated_at = datetime.utcnow()
                
                # Create new price record for the main platform (Amazon)
                price_record = PriceRecord(
                    product_id=product.id,
                    price=new_price,
                    platform='Amazon', # Explicitly set platform
                    recorded_at=datetime.utcnow()
                )
                db.session.add(price_record)
                logger.info(f"Updated Amazon price for product {product.id}: {new_price}")
                updated_any_price = True
                
                # Check for alerts only based on the main product price change
                if old_price is not None and new_price < old_price:
                    logger.info(f"Amazon price dropped for product {product.id}: {old_price} -> {new_price}. Checking alerts.")
                    check_price_alerts(product, new_price)
                elif old_price is None:
                    logger.info(f"Initial Amazon price recorded for product {product.id}: {new_price}")
        else:
            logger.warning(f"Failed to scrape price for main product URL {product.url} (ID: {product.id})")
            if product_data and 'scraping_failed' in product_data and product_data['scraping_failed']:
                logger.warning(f"Scraper reported failure reason: {product_data.get('error', 'Unknown error')}")
    except Exception as e:
        last_exception = e
        logger.error(f"Error updating main platform price for product {product.id}: {str(e)}")
        logger.debug(traceback.format_exc())

    # --- Find and update prices for other platforms ---
    try:
        # Get product metadata to use for searching other platforms
        metadata = extract_product_metadata(product.url)
        
        if metadata and 'name' in metadata:
            # Apply rate limiting before API call
            time.sleep(random.uniform(0.5, RATE_LIMIT_DELAY))
            
            comparisons = search_other_platforms(metadata)
            logger.info(f"Found {len(comparisons)} potential comparisons for product {product.id} on other platforms.")
            
            # Process each platform with individual error handling
            for comparison in comparisons:
                try:
                    platform_name = comparison.get('platform')
                    platform_url = comparison.get('url')
                    existing_price = comparison.get('price')
                    
                    # Only process if we have a platform name and URL, and it's not the main platform
                    if platform_name and platform_url and platform_name.lower() != 'amazon':
                        # Apply rate limiting between scraping requests
                        time.sleep(random.uniform(0.5, RATE_LIMIT_DELAY))
                        
                        scraped_price = None
                        # Call the appropriate scraper based on platform_name
                        if platform_name == 'Flipkart':
                            scraped_price = scrape_flipkart_price(platform_url)
                        # Add elif for other platforms as scrapers are implemented
                        
                        # If scraping failed but AI provided a price estimate, use that as fallback
                        if scraped_price is None and existing_price is not None:
                            logger.info(f"Using AI-provided price estimate for {platform_name}: {existing_price}")
                            scraped_price = existing_price
                        
                        if scraped_price is not None:
                            # Validate price data
                            if not isinstance(scraped_price, (int, float)) or scraped_price <= 0:
                                logger.warning(f"Invalid price from {platform_name} for product {product.id}: {scraped_price}")
                                continue
                                
                            # Create new price record for the competitor platform
                            price_record = PriceRecord(
                                product_id=product.id,
                                price=scraped_price,
                                platform=platform_name,
                                recorded_at=datetime.utcnow()
                            )
                            db.session.add(price_record)
                            logger.info(f"Updated {platform_name} price for product {product.id}: {scraped_price}")
                            updated_any_price = True
                        else:
                            logger.warning(f"Failed to scrape price from {platform_name} URL: {platform_url} for product {product.id}")
                except Exception as platform_err:
                    logger.error(f"Error processing {comparison.get('platform', 'unknown')} platform for product {product.id}: {str(platform_err)}")
                    # Continue with other platforms despite errors
        else:
            logger.warning(f"Could not extract metadata for product {product.id} to search other platforms.")
    except Exception as e:
        last_exception = e
        logger.error(f"Error searching/scraping other platforms for product {product.id}: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # If we didn't update any prices successfully, raise the last exception
    # This will trigger a retry in the update_product_with_retries function
    if not updated_any_price and last_exception:
        raise last_exception
    
    # Return success status
    return updated_any_price


def check_price_alerts(product, new_price):
    """Check if any price alerts should be triggered for the main product price"""
    try:
        # Alerts are currently only tied to the main product price (Amazon)
        alerts = PriceAlert.query.filter(
            PriceAlert.product_id == product.id,
            PriceAlert.target_price >= new_price,
            PriceAlert.triggered == False
        ).all()
        
        logger.info(f"Found {len(alerts)} alerts to trigger for product {product.id}")
        
        for alert in alerts:
            try:
                # Send email notification
                send_price_alert_email(alert, product, new_price)
                
                # Mark alert as triggered
                alert.triggered = True
                alert.triggered_at = datetime.utcnow()
                alert.triggered_price = new_price
                db.session.add(alert)
                
                logger.info(f"Triggered alert {alert.id} for product {product.id}")
            except Exception as e:
                logger.error(f"Error triggering alert {alert.id}: {str(e)}")
                logger.debug(traceback.format_exc())
    except Exception as e:
        logger.error(f"Error checking price alerts for product {product.id}: {str(e)}")
        logger.debug(traceback.format_exc())
