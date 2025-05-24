from flask import Flask, request, jsonify
import os
import asyncio
import logging
from services.database import get_all_products, get_product_by_id, update_product_price, insert_price_record
from services.scraper import scrape_product
from services.alerts import check_and_trigger_alerts

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_all_products():
    """Update prices for all tracked products"""
    try:
        logger.info("Starting scheduled price update for all products")
        
        products = await get_all_products()
        logger.info(f"Found {len(products)} products to update")
        
        updated_count = 0
        for product in products:
            try:
                # Scrape current product data
                product_data = scrape_product(product['url'])
                
                if not product_data or 'price' not in product_data:
                    logger.warning(f"Failed to scrape price for product {product['id']}")
                    continue
                
                new_price = product_data['price']
                old_price = product['current_price']
                
                # Update product price
                await update_product_price(product['id'], new_price)
                
                # Add price record
                await insert_price_record(product['id'], new_price)
                
                # Check for alerts if price dropped
                if old_price and new_price < old_price:
                    await check_and_trigger_alerts(product['id'], new_price)
                
                updated_count += 1
                logger.info(f"Updated price for product {product['id']}: {old_price} -> {new_price}")
                
            except Exception as e:
                logger.error(f"Error updating product {product['id']}: {str(e)}")
        
        logger.info(f"Completed scheduled price update. Updated {updated_count} products.")
        return updated_count
    except Exception as e:
        logger.error(f"Error in scheduled price update: {str(e)}")
        raise

@app.route('/api/cron', methods=['POST'])
def cron_handler():
    """Serverless function for scheduled price updates"""
    # Verify the request is authorized
    auth_header = request.headers.get('Authorization')
    expected_token = f"Bearer {os.getenv('CRON_SECRET')}"
    
    if not auth_header or auth_header != expected_token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Run the async update function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            updated_count = loop.run_until_complete(update_all_products())
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'message': f'Updated prices for {updated_count} products'
        }), 200
    except Exception as e:
        logger.error(f"Error in cron job: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run()
