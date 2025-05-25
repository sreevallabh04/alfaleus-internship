import logging
import time
import random
import traceback
from sqlalchemy.exc import SQLAlchemyError
from models.db import db
from models.product import Product
from models.price_record import PriceRecord
from models.price_alert import PriceAlert
from services.scraper import scrape_product # Assuming this is for Amazon
from services.flipkart_scraper import scrape_flipkart_price # Import the new scraper
from services.email_service import send_price_alert_email
from services.ai_service import extract_product_metadata, search_other_platforms # Import AI service functions
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Constants for retry and rate limiting
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # Base delay in seconds
RATE_LIMIT_DELAY = 1.5  # Delay between requests to avoid rate limiting

def update_all_prices(app):
    """
    Update prices for all tracked products across all relevant platforms.
    This function is called by the scheduler.
    Enhanced with better error handling, retries, and transaction management.
    """
    with app.app_context():
        start_time = datetime.utcnow()
        logger.info("Starting scheduled price update for all products and platforms")
        
        try:
            products = Product.query.all()
            total_products = len(products)
            logger.info(f"Found {total_products} products to update")
            
            success_count = 0
            error_count = 0
            
            for index, product in enumerate(products):
                logger.info(f"Processing product {index+1}/{total_products}: {product.name} (ID: {product.id})")
                
                # Create a separate transaction for each product
                try:
                    # Apply rate limiting between product updates
                    if index > 0:
                        time.sleep(random.uniform(0.5, RATE_LIMIT_DELAY))
                    
                    # Update the product with retries
                    success = update_product_with_retries(product)
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Unhandled error updating product {product.id}: {str(e)}")
                    logger.debug(traceback.format_exc())
            
            # Log summary statistics
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Completed scheduled price update in {duration:.2f} seconds")
            logger.info(f"Results: {success_count} successful updates, {error_count} failures out of {total_products} products")
            
            # Record the last update time for monitoring
            app.config['LAST_PRICE_UPDATE'] = {
                'timestamp': end_time.isoformat(),
                'success_count': success_count,
                'error_count': error_count,
                'total_products': total_products,
                'duration_seconds': duration
            }
            
        except Exception as e:
            logger.error(f"Critical error in price update scheduler: {str(e)}")
            logger.error(traceback.format_exc())

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
