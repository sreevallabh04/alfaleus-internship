from flask import Blueprint, request, jsonify
from models.db import db
from models.product import Product
from models.price_history import PriceHistory
from services.scraper import AmazonScraper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
products_bp = Blueprint('products', __name__)
scraper = AmazonScraper()

@products_bp.route('/products', methods=['POST'])
def add_product():
    """Add a new product to track"""
    try:
        data = request.get_json()
        amazon_url = data.get('amazon_url')
        target_price = data.get('target_price')
        email = data.get('email')

        if not all([amazon_url, target_price, email]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate Amazon URL
        if not scraper.is_valid_amazon_url(amazon_url):
            return jsonify({'error': 'Invalid Amazon URL'}), 400

        # Check if product already exists
        existing_product = Product.query.filter_by(amazon_url=amazon_url).first()
        if existing_product:
            return jsonify({'error': 'Product already being tracked'}), 409

        # Scrape product details
        success, data = scraper.scrape_product(amazon_url)
        if not success:
            return jsonify({'error': data.get('error', 'Failed to scrape product details')}), 400

        # Create new product
        product = Product(
            amazon_url=amazon_url,
            title=data['title'],
            image_url=data['image_url'],
            current_price=data['current_price'],
            target_price=target_price,
            email=email
        )
        db.session.add(product)

        # Add initial price history
        price_history = PriceHistory(
            product_id=product.id,
            price=data['current_price']
        )
        db.session.add(price_history)
        db.session.commit()

        return jsonify(product.to_dict()), 201

    except Exception as e:
        logger.error(f"Error adding product: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all tracked products"""
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])

    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get details of a specific product"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())

    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>/history', methods=['GET'])
def get_price_history(product_id):
    """Get price history for a specific product"""
    try:
        history = PriceHistory.query.filter_by(product_id=product_id).order_by(PriceHistory.timestamp.desc()).all()
        return jsonify([record.to_dict() for record in history])

    except Exception as e:
        logger.error(f"Error fetching price history for product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a tracked product"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return '', 204

    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@products_bp.errorhandler(405)
def method_not_allowed_error(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'message': 'Method not allowed'
    }), 405

@products_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500