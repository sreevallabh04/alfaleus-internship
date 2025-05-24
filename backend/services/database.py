import os
import logging
from dotenv import load_dotenv
from flask import current_app
from sqlalchemy.sql import text
from datetime import datetime

# Import models
from models.db import db
from models.product import Product
from models.price_record import PriceRecord
from models.price_alert import PriceAlert

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

async def execute_query(query, params=None):
    """Execute a SQL query using SQLAlchemy"""
    try:
        if params:
            result = db.session.execute(text(query), params)
        else:
            result = db.session.execute(text(query))
        db.session.commit()
        return [dict(row) for row in result]
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database query error: {str(e)}")
        raise

async def get_all_products():
    """Get all products from database"""
    try:
        products = Product.query.order_by(Product.created_at.desc()).all()
        return [product.to_dict() for product in products]
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise

async def get_product_by_id(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.get(product_id)
        return product.to_dict() if product else None
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise

async def get_price_history(product_id):
    """Get price history for a product"""
    try:
        price_records = PriceRecord.query.filter_by(product_id=product_id).order_by(PriceRecord.timestamp.asc()).all()
        return [record.to_dict() for record in price_records]
    except Exception as e:
        logger.error(f"Error getting price history for product {product_id}: {str(e)}")
        raise

async def insert_product(name, url, image_url, description, current_price, currency):
    """Insert a new product"""
    try:
        product = Product(
            name=name,
            url=url,
            image_url=image_url,
            description=description,
            current_price=current_price,
            currency=currency
        )
        db.session.add(product)
        db.session.commit()
        return product.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inserting product: {str(e)}")
        raise

async def insert_price_record(product_id, price):
    """Insert a new price record"""
    try:
        price_record = PriceRecord(
            product_id=product_id,
            price=price
        )
        db.session.add(price_record)
        db.session.commit()
        return price_record.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inserting price record: {str(e)}")
        raise

async def update_product_price(product_id, new_price):
    """Update product's current price"""
    try:
        product = Product.query.get(product_id)
        if product:
            product.current_price = new_price
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return product.to_dict()
        return None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating product price: {str(e)}")
        raise

async def insert_price_alert(product_id, email, target_price):
    """Insert a new price alert"""
    try:
        alert = PriceAlert(
            product_id=product_id,
            email=email,
            target_price=target_price
        )
        db.session.add(alert)
        db.session.commit()
        return alert.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inserting price alert: {str(e)}")
        raise

async def get_untriggered_alerts(product_id, current_price):
    """Get untriggered alerts for a product where target price is met"""
    try:
        alerts = PriceAlert.query.filter(
            PriceAlert.product_id == product_id,
            PriceAlert.target_price >= current_price,
            PriceAlert.triggered == False
        ).all()
        return [alert.to_dict() for alert in alerts]
    except Exception as e:
        logger.error(f"Error getting untriggered alerts: {str(e)}")
        raise

async def mark_alert_triggered(alert_id):
    """Mark an alert as triggered"""
    try:
        alert = PriceAlert.query.get(alert_id)
        if alert:
            alert.triggered = True
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking alert as triggered: {str(e)}")
        raise

async def delete_product_by_id(product_id):
    """Delete a product and all related records"""
    try:
        product = Product.query.get(product_id)
        if product:
            name = product.name
            db.session.delete(product)
            db.session.commit()
            return {"name": name}
        return None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product: {str(e)}")
        raise

async def check_product_exists(url):
    """Check if a product with the given URL already exists"""
    try:
        product = Product.query.filter_by(url=url).first()
        return product.to_dict() if product else None
    except Exception as e:
        logger.error(f"Error checking if product exists: {str(e)}")
        raise