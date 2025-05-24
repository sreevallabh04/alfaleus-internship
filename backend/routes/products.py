from flask import Blueprint, request, jsonify
import asyncio
import logging
from services.database import (
    get_all_products, get_product_by_id, get_price_history,
    insert_product, insert_price_record, update_product_price,
    delete_product_by_id, check_product_exists
)
from services.scraper import scrape_product
from services.url_normalizer import normalize_amazon_url

logger = logging.getLogger(__name__)
products_bp = Blueprint('products', __name__)

def run_async(coro):
    """Helper function to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@products_bp.route('', methods=['GET'])
def get_all_products_route():
    """Get all tracked products"""
    try:
        products = run_async(get_all_products())
        
        # Products are already in dict format from database.py
        products_list = products
        
        return jsonify({
            'success': True,
            'products': products_list
        }), 200
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch products',
            'error': str(e)
        }), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product_route(product_id):
    """Get a specific product with its price history"""
    try:
        product = run_async(get_product_by_id(product_id))
        if not product:
            return jsonify({
                'success': False,
                'message': f'Product with ID {product_id} not found'
            }), 404
        
        # Get price history
        price_records = run_async(get_price_history(product_id))
        
        # Product is already in dict format from database.py
        product_dict = product
        
        # Price records are already in dict format from database.py
        price_history = price_records
        
        return jsonify({
            'success': True,
            'product': product_dict,
            'price_history': price_history
        }), 200
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to fetch product with ID {product_id}',
            'error': str(e)
        }), 500

@products_bp.route('', methods=['POST'])
def add_product_route():
    """Add a new product to track"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'message': 'URL is required'
            }), 400
        
        # Normalize URL if it's an Amazon URL
        url = normalize_amazon_url(data['url'])
        
        # Check if product already exists
        existing_product = run_async(check_product_exists(url))
        if existing_product:
            # Product is already in dict format with properly formatted dates
            product_dict = existing_product
            return jsonify({
                'success': True,
                'message': 'Product is already being tracked',
                'product': product_dict
            }), 200
        
        # Scrape product details
        product_data = scrape_product(url)
        if not product_data:
            return jsonify({
                'success': False,
                'message': 'Failed to scrape product information'
            }), 400
        
        # Create new product
        new_product = run_async(insert_product(
            product_data['name'],
            url,
            product_data.get('image_url'),
            product_data.get('description'),
            product_data.get('price'),
            product_data.get('currency', 'USD')
        ))
        
        # Create initial price record
        if product_data.get('price'):
            run_async(insert_price_record(new_product['id'], product_data['price']))
        
        logger.info(f"Added new product: {new_product['name']} (ID: {new_product['id']})")
        
        # Product is already in dict format with properly formatted dates
        product_dict = new_product
        
        return jsonify({
            'success': True,
            'message': 'Product added successfully',
            'product': product_dict
        }), 201
    except Exception as e:
        logger.error(f"Error adding product: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to add product',
            'error': str(e)
        }), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    """Delete a product and all its associated data"""
    try:
        deleted_product = run_async(delete_product_by_id(product_id))
        if not deleted_product:
            return jsonify({
                'success': False,
                'message': f'Product with ID {product_id} not found'
            }), 404
        
        logger.info(f"Deleted product: {deleted_product['name']} (ID: {product_id})")
        
        return jsonify({
            'success': True,
            'message': f'Product {deleted_product["name"]} deleted successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to delete product with ID {product_id}',
            'error': str(e)
        }), 500

@products_bp.route('/update', methods=['POST'])
def update_product_price_route():
    """Manually update a product's price (for serverless environments)"""
    try:
        data = request.get_json()
        
        if not data or 'product_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Product ID is required'
            }), 400
        
        product = run_async(get_product_by_id(data['product_id']))
        if not product:
            return jsonify({
                'success': False,
                'message': f'Product with ID {data["product_id"]} not found'
            }), 404
        
        # Scrape current product data
        product_data = scrape_product(product['url'])
        
        if not product_data or 'price' not in product_data:
            return jsonify({
                'success': False,
                'message': 'Failed to scrape current price'
            }), 400
        
        new_price = product_data['price']
        
        # Update product price
        updated_product = run_async(update_product_price(product['id'], new_price))
        
        # Add price record
        run_async(insert_price_record(product['id'], new_price))
        
        # Check for alerts
        from services.alerts import check_and_trigger_alerts
        run_async(check_and_trigger_alerts(product['id'], new_price))
        
        return jsonify({
            'success': True,
            'message': f'Price updated for product: {product["name"]}',
            'current_price': new_price
        }), 200
    except Exception as e:
        logger.error(f"Error updating product price: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update product price',
            'error': str(e)
        }), 500
