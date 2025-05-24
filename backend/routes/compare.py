from flask import Blueprint, request, jsonify, current_app
import logging
import traceback
import random
from datetime import datetime
from services.ai_service import extract_product_metadata, search_other_platforms
from services.scraper import get_mock_product_data
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)
compare_bp = Blueprint('compare', __name__)

@compare_bp.route('', methods=['POST'])
def compare_prices():
    """Compare prices across multiple platforms using AI"""
    try:
        logger.info("Price comparison request received")
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data in request")
            return jsonify({
                'success': False,
                'message': 'No data provided in request'
            }), 400
            
        if 'url' not in data:
            logger.error("URL not provided in request")
            return jsonify({
                'success': False,
                'message': 'URL is required'
            }), 400
        
        logger.info(f"Extracting product metadata from URL: {data['url']}")
        # Extract product metadata using AI
        metadata = extract_product_metadata(data['url'])
        
        if not metadata:
            logger.error("Failed to extract any product metadata")
            return jsonify({
                'success': False,
                'message': 'Failed to extract product data from the URL'
            }), 400
            
        if 'name' not in metadata:
            logger.error("Product name not found in metadata")
            return jsonify({
                'success': False,
                'message': 'Failed to extract product name from metadata'
            }), 400
        
        logger.info(f"Successfully extracted metadata for product: {metadata.get('name')}")
        
        # Search for the product on other platforms
        logger.info("Searching for product on other platforms")
        comparisons = search_other_platforms(metadata)
        
        logger.info(f"Found {len(comparisons)} platform comparisons")
        
        # Only use mock data if specifically requested or if no real comparisons found in development mode
        if not comparisons:
            if is_development_mode() and should_generate_mock_comparisons():
                logger.warning("No comparisons found and mock data requested, generating mock comparison data")
                
                # Use the actual metadata for generating relevant mock comparisons
                comparisons = generate_mock_comparisons(metadata)
                
                logger.info(f"Generated {len(comparisons)} mock platform comparisons based on product: {metadata.get('name')}")
                
                # Clearly mark this as mock data in the response
                return jsonify({
                    'success': True,
                    'metadata': metadata,
                    'comparisons': comparisons,
                    'is_mock_data': True
                }), 200
            else:
                logger.info("No comparisons found and mock data not requested")
        
        return jsonify({
            'success': True,
            'metadata': metadata,
            'comparisons': comparisons
        }), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error comparing prices: {str(e)}\n{error_traceback}")
        return jsonify({
            'success': False,
            'message': 'Failed to compare prices. Please try again.',
            'error': str(e)
        }), 500

def is_development_mode():
    """Check if the application is running in development mode"""
    try:
        return current_app.config.get('FLASK_ENV') == 'development' or current_app.config.get('TESTING', False)
    except Exception:
        return False

def should_generate_mock_comparisons():
    """Determine if we should generate mock comparison data"""
    # Only generate mock data if specifically requested via a URL parameter
    mock_param = request.args.get('mock', 'false').lower() == 'true'
    return mock_param

def generate_mock_comparisons(metadata):
    """
    Generate realistic mock comparison data based on actual product metadata
    
    Args:
        metadata (dict): The extracted product metadata
    """
    if not metadata or not isinstance(metadata, dict):
        logger.error("Invalid metadata provided for mock comparison generation")
        return []
    
    product_name = metadata.get('name', '')
    product_brand = metadata.get('brand', '')
    product_price = metadata.get('price')
    
    if not product_name:
        logger.error("Product name missing in metadata for mock comparison generation")
        return []
    
    logger.info(f"Generating mock comparisons for {product_name}")
    
    # Define the platforms we want to include
    platforms = [
        {
            'name': 'Flipkart', 
            'url_template': f"https://www.flipkart.com/search?q={product_name}",
            'price_variance': (-0.05, 0.10)  # -5% to +10% price variance
        },
        {
            'name': 'Meesho',
            'url_template': f"https://www.meesho.com/search?q={product_name}",
            'price_variance': (0.02, 0.15)  # +2% to +15% price variance
        },
        {
            'name': 'BigBasket',
            'url_template': f"https://www.bigbasket.com/ps/?q={product_name}",
            'price_variance': (-0.10, 0.05)  # -10% to +5% price variance
        },
        {
            'name': 'Swiggy Instamart',
            'url_template': f"https://www.swiggy.com/search?query={product_name}",
            'price_variance': (0.10, 0.20)  # +10% to +20% price variance
        }
    ]
    
    comparisons = []
    
    # Generate timestamp for consistent "last checked" values
    timestamp = datetime.now().isoformat()
    
    # If we have a price, generate realistic price variations
    base_price = None
    if product_price and isinstance(product_price, (int, float)) and product_price > 0:
        base_price = float(product_price)
    else:
        # If no price available, make a reasonable guess based on product name
        base_price = random.uniform(500, 5000)
        if 'protein' in product_name.lower() or 'supplement' in product_name.lower():
            base_price = random.uniform(1000, 3000)
        elif 'phone' in product_name.lower() or 'smartphone' in product_name.lower():
            base_price = random.uniform(10000, 50000)
        elif 'laptop' in product_name.lower() or 'computer' in product_name.lower():
            base_price = random.uniform(30000, 100000)
    
    # Create comparison entries for each platform
    for platform in platforms:
        # Calculate a realistic price variation
        min_var, max_var = platform['price_variance']
        price_factor = 1.0 + random.uniform(min_var, max_var)
        varied_price = round(base_price * price_factor, -1)  # Round to nearest 10
        
        # Some platforms might not have the product
        in_stock = random.random() < 0.9  # 90% chance of being in stock
        
        comparisons.append({
            'platform': platform['name'],
            'url': platform['url_template'],
            'price': varied_price if in_stock else None,
            'currency': metadata.get('currency', 'INR'),
            'in_stock': in_stock,
            'last_checked': timestamp,
            'is_genuine_match': False,  # Mark mock data as not genuine matches
            'match_confidence': 0.5  # Medium-low confidence for mock data
        })
    
    # Ensure at least one platform has a better price
    if len(comparisons) > 1 and base_price:
        # Find a random platform to give a better price
        better_platform_idx = random.randint(0, len(comparisons) - 1)
        comparisons[better_platform_idx]['price'] = round(base_price * 0.9, -1)  # 10% lower price
    
    return comparisons