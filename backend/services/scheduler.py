import logging
from models.db import db
from models.product import Product
from models.price_record import PriceRecord
from models.price_alert import PriceAlert
from services.scraper import scrape_product # Assuming this is for Amazon
from services.flipkart_scraper import scrape_flipkart_price # Import the new scraper
from services.email_service import send_price_alert_email
from services.ai_service import extract_product_metadata, search_other_platforms # Import AI service functions
from datetime import datetime

logger = logging.getLogger(__name__)

def update_all_prices(app):
    """
    Update prices for all tracked products across all relevant platforms.
    This function is called by the scheduler.
    """
    with app.app_context():
        logger.info("Starting scheduled price update for all products and platforms")

        products = Product.query.all()
        logger.info(f"Found {len(products)} products to update")

        for product in products:
            try:
                update_product_prices_for_all_platforms(product)
            except Exception as e:
                logger.error(f"Error updating prices for product {product.id}: {str(e)}")

        db.session.commit() # Commit changes after processing all products
        logger.info("Completed scheduled price update")


def update_product_prices_for_all_platforms(product):
    """
    Update prices for a single product across its main platform and other found platforms.
    """
    logger.info(f"Updating prices for product: {product.name} (ID: {product.id})")

    # --- Update price for the main product URL (assuming Amazon) ---
    product_data = scrape_product(product.url)

    if product_data and 'price' in product_data and product_data['price'] is not None:
        new_price = product_data['price']
        old_price = product.current_price

        # Update product's current price and timestamp
        product.current_price = new_price
        product.updated_at = datetime.utcnow()

        # Create new price record for the main platform (Amazon)
        price_record = PriceRecord(
            product_id=product.id,
            price=new_price,
            platform='Amazon' # Explicitly set platform
        )
        db.session.add(price_record)
        logger.info(f"Updated Amazon price for product {product.id}: {new_price}")

        # Check for alerts only based on the main product price change
        if old_price is not None and new_price < old_price:
             logger.info(f"Amazon price dropped for product {product.id}: {old_price} -> {new_price}. Checking alerts.")
             check_price_alerts(product, new_price)
        elif old_price is None:
             logger.info(f"Initial Amazon price recorded for product {product.id}: {new_price}")


    else:
        logger.warning(f"Failed to scrape price for main product URL {product.url} (ID: {product.id})")


    # --- Find and update prices for other platforms ---
    try:
        # Get product metadata to use for searching other platforms
        # Note: This might be slow if AI keys are used and called for every product on every run.
        # A more scalable approach would store comparison URLs.
        metadata = extract_product_metadata(product.url)

        if metadata and 'name' in metadata:
            comparisons = search_other_platforms(metadata)
            logger.info(f"Found {len(comparisons)} potential comparisons for product {product.id} on other platforms.")

            for comparison in comparisons:
                platform_name = comparison.get('platform')
                platform_url = comparison.get('url')
                # Only process if we have a platform name and URL, and it's not the main platform
                if platform_name and platform_url and platform_name.lower() != 'amazon':
                    scraped_price = None
                    # Call the appropriate scraper based on platform_name
                    if platform_name == 'Flipkart':
                        scraped_price = scrape_flipkart_price(platform_url)
                    # Add elif for other platforms as scrapers are implemented

                    if scraped_price is not None:
                        # Create new price record for the competitor platform
                        price_record = PriceRecord(
                            product_id=product.id,
                            price=scraped_price,
                            platform=platform_name
                        )
                        db.session.add(price_record)
                        logger.info(f"Updated {platform_name} price for product {product.id}: {scraped_price}")
                    else:
                        logger.warning(f"Failed to scrape price from {platform_name} URL: {platform_url} for product {product.id}")
        else:
             logger.warning(f"Could not extract metadata for product {product.id} to search other platforms.")

    except Exception as e:
        logger.error(f"Error searching/scraping other platforms for product {product.id}: {str(e)}")

    # Note: db.session.commit() is now called once in update_all_prices after the loop


def check_price_alerts(product, new_price):
    """Check if any price alerts should be triggered for the main product price"""
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
            db.session.add(alert)

            logger.info(f"Triggered alert {alert.id} for product {product.id}")
        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {str(e)}")
