import logging
from models.db import db
from models.product import Product
from models.price_record import PriceRecord
from models.price_alert import PriceAlert
from services.scraper import scrape_product
from services.email_service import send_price_alert_email
from datetime import datetime

logger = logging.getLogger(__name__)

def update_all_prices(app):
    """
    Update prices for all tracked products
    This function is called by the scheduler
    """
    with app.app_context():
        logger.info("Starting scheduled price update for all products")
        
        products = Product.query.all()
        logger.info(f"Found {len(products)} products to update")
        
        for product in products:
            try:
                update_product_price(product)
            except Exception as e:
                logger.error(f"Error updating price for product {product.id}: {str(e)}")
        
        logger.info("Completed scheduled price update")

def update_product_price(product):
    """Update price for a single product and check alerts"""
    logger.info(f"Updating price for product: {product.name} (ID: {product.id})")
    
    # Scrape current product data
    product_data = scrape_product(product.url)
    
    if not product_data or 'price' not in product_data:
        logger.warning(f"Failed to scrape price for product {product.id}")
        return
    
    new_price = product_data['price']
    old_price = product.current_price
    
    # Update product with new price
    product.current_price = new_price
    product.updated_at = datetime.utcnow()
    
    # Create new price record
    price_record = PriceRecord(
        product_id=product.id,
        price=new_price
    )
    
    db.session.add(price_record)
    
    # Check if price has changed
    if old_price is not None and new_price != old_price:
        logger.info(f"Price changed for product {product.id}: {old_price} -> {new_price}")
        
        # Check for alerts to trigger
        if new_price < old_price:
            check_price_alerts(product, new_price)
    
    db.session.commit()
    logger.info(f"Price updated for product {product.id}")

def check_price_alerts(product, new_price):
    """Check if any price alerts should be triggered"""
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
