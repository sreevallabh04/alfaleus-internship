import requests
import time
import random
import logging
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('amazon_scraper')

# Headers to mimic a browser visit
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/'
}

def get_normalized_amazon_url(url):
    """
    Extract and normalize the Amazon product URL to get a clean ASIN-based URL.
    
    Args:
        url (str): The Amazon product URL
        
    Returns:
        str: Normalized Amazon URL or original URL if parsing fails
    """
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if it's an Amazon domain
        if not any(domain in parsed_url.netloc for domain in ['amazon.com', 'amazon.in', 'amazon.']):
            return url
        
        # Try to extract ASIN from URL path
        asin_match = re.search(r'/dp/([A-Z0-9]{10})(?:/|$)', url)
        if asin_match:
            asin = asin_match.group(1)
        else:
            # Try to get it from query parameters
            query_params = parse_qs(parsed_url.query)
            asin = query_params.get('asin', [None])[0]
            
            # If still not found, try additional patterns
            if not asin:
                # Try product ID pattern
                prod_match = re.search(r'/product/([A-Z0-9]{10})(?:/|$)', url)
                if prod_match:
                    asin = prod_match.group(1)
                else:
                    # Try gp/product pattern
                    gp_match = re.search(r'/gp/product/([A-Z0-9]{10})(?:/|$)', url)
                    if gp_match:
                        asin = gp_match.group(1)
        
        # If ASIN found, construct a clean URL
        if asin:
            domain = parsed_url.netloc
            return f"https://{domain}/dp/{asin}"
        
        return url
    except Exception as e:
        logger.error(f"Error normalizing Amazon URL: {e}")
        return url

def get_soup_with_requests(url, retries=3):
    """Get the soup using the requests library with multiple retries."""
    for attempt in range(retries):
        try:
            # Rotate user agents
            headers = HEADERS.copy()
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
            ]
            headers['User-Agent'] = random.choice(user_agents)
            
            # Add a random delay to avoid being blocked
            delay = random.uniform(1, 3) * (attempt + 1)
            time.sleep(delay)
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Check if we got a captcha page
            if 'captcha' in response.text.lower() or 'robot check' in response.text.lower():
                logger.warning(f"Captcha detected on attempt {attempt+1}. Retrying...")
                continue
                
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.warning(f"Request attempt {attempt+1} failed: {e}")
            if attempt == retries - 1:
                logger.error(f"All {retries} attempts failed")
                return None

def extract_amazon_product_info(url):
    """
    Extract product information from an Amazon product URL.
    
    Args:
        url (str): The Amazon product URL
        
    Returns:
        dict: Dictionary containing product information or error details
    """
    logger.info(f"Scraping Amazon product: {url}")
    
    # Normalize the URL to get a clean ASIN-based URL
    normalized_url = get_normalized_amazon_url(url)
    logger.info(f"Normalized URL: {normalized_url}")
    
    # Try with requests with multiple retries
    soup = get_soup_with_requests(normalized_url, retries=3)
    
    # If all methods failed, return an error
    if not soup:
        logger.error("Scraping failed")
        return {
            'success': False,
            'error': 'Failed to retrieve product information. Please check the URL and try again.'
        }
    
    try:
        # First try to extract data using JSON-LD
        json_ld = None
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if '@type' in data and data['@type'] in ['Product', 'ItemPage']:
                    json_ld = data
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Extract product name
        product_name = None
        if json_ld and 'name' in json_ld:
            product_name = json_ld['name']
        
        if not product_name:
            product_name_element = soup.select_one('#productTitle')
            product_name = product_name_element.get_text().strip() if product_name_element else None
        
        if not product_name:
            # Try alternative selectors
            alt_title_selectors = ['.product-title-word-break', '.a-size-large.product-title-word-break']
            for selector in alt_title_selectors:
                element = soup.select_one(selector)
                if element:
                    product_name = element.get_text().strip()
                    break
        
        if not product_name:
            product_name = "Amazon Product"  # Fallback name
        
        # Extract product image
        image_url = None
        if json_ld and 'image' in json_ld:
            image_url = json_ld['image'] if isinstance(json_ld['image'], str) else json_ld['image'][0]
        
        if not image_url:
            image_selectors = ['#landingImage', '#imgBlkFront', '#main-image', 'img.a-dynamic-image']
            for selector in image_selectors:
                image_element = soup.select_one(selector)
                if image_element and image_element.get('src'):
                    image_url = image_element.get('src')
                    break
        
        # Try to find image in image gallery
        if not image_url:
            # Look for image data in scripts
            for script in soup.find_all('script'):
                if script.string and 'ImageBlockATF' in script.string:
                    try:
                        # Extract image URL using regex
                        match = re.search(r'"hiRes":"([^"]+)"', script.string)
                        if match:
                            image_url = match.group(1)
                            break
                    except:
                        pass
        
        # Extract price
        price = None
        currency = '₹'  # Default for Amazon India
        
        # Try to get price from JSON-LD
        if json_ld and 'offers' in json_ld:
            offers = json_ld['offers']
            if isinstance(offers, dict):
                if 'price' in offers:
                    try:
                        price = float(offers['price'])
                    except (ValueError, TypeError):
                        pass
                if 'priceCurrency' in offers:
                    currency = offers['priceCurrency']
        
        # If not found in JSON-LD, try HTML selectors
        if price is None:
            price_selectors = [
                '.a-price .a-offscreen', 
                '#priceblock_ourprice', 
                '#priceblock_dealprice',
                '.a-price .a-price-whole',
                '.a-section.a-spacing-small .a-price .a-offscreen'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    # Determine currency
                    if price_text.startswith('$'):
                        currency = '$'
                    elif price_text.startswith('₹'):
                        currency = '₹'
                    elif price_text.startswith('€'):
                        currency = '€'
                    elif price_text.startswith('£'):
                        currency = '£'
                    
                    # Remove currency symbol and commas, then convert to float
                    price_text = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
                    # Handle price ranges (e.g., "₹1,234 - ₹5,678")
                    if ' - ' in price_text:
                        price_text = price_text.split(' - ')[0]
                    try:
                        if price_text:
                            price = float(price_text)
                            break
                    except ValueError:
                        logger.warning(f"Could not convert price text to float: {price_text}")
        
        # If still no price, look for it in scripts
        if price is None:
            for script in soup.find_all('script'):
                if script.string and ('priceAmount' in script.string or '"price":' in script.string):
                    try:
                        # Try to find price using regex
                        price_match = re.search(r'"priceAmount":(\d+\.\d+)', script.string)
                        if price_match:
                            price = float(price_match.group(1))
                            break
                            
                        price_match = re.search(r'"price":(\d+\.\d+)', script.string)
                        if price_match:
                            price = float(price_match.group(1))
                            break
                    except:
                        pass
        
        # Build the result
        result = {
            'success': True,
            'name': product_name,
            'image_url': image_url,
            'price': price,
            'currency': currency,
            'url': normalized_url  # Use the normalized URL
        }
        
        # Validate result
        if not product_name or product_name == "Amazon Product":
            logger.warning("Could not extract proper product name")
            if not price:
                # If we also couldn't get price, the scraping probably failed
                logger.error("Could not extract product name or price - scraping likely failed")
                return {
                    'success': False,
                    'error': 'Could not extract essential product information. Please check the URL and try again.'
                }
        
        return result
    
    except Exception as e:
        logger.error(f"Error extracting product information: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'Error extracting product information. Please try again with a different URL or contact support.'
        }

def scrape_product(url, db, models):
    """
    Scrape a product and update the database.
    
    Args:
        url (str): The Amazon product URL
        db: SQLAlchemy database instance
        models: Database models module
        
    Returns:
        dict: Result of the scraping operation
    """
    # Extract product information
    result = extract_amazon_product_info(url)
    
    if not result['success']:
        return result
    
    try:
        # Check if product exists in database
        product = models["Product"].query.filter_by(url=url).first()
        
        if not product:
            # Create new product
            product = models["Product"](
                url=url,
                name=result['name'],
                image_url=result['image_url']
            )
            db.session.add(product)
            db.session.commit()
        else:
            # Update existing product if needed
            if product.name != result['name'] or product.image_url != result['image_url']:
                product.name = result['name']
                product.image_url = result['image_url']
                db.session.commit()
        
        if result['price']:
            # Add new price record
            price_record = models["PriceRecord"](
                product_id=product.id,
                price=result['price'],
                currency=result['currency']
            )
            db.session.add(price_record)
            db.session.commit()
            
            # Check for price alerts
            check_price_alerts(product.id, result['price'], db, models)
        
        return {
            'success': True,
            'message': 'Product scraped and database updated successfully',
            'product_id': product.id,
            'current_price': result['price'],
            'currency': result['currency']
        }
    
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        db.session.rollback()
        return {
            'success': False,
            'error': f'Error updating database: {str(e)}'
        }

def check_price_alerts(product_id, current_price, db, models):
    """
    Check if any price alerts should be triggered.
    
    Args:
        product_id (int): The product ID
        current_price (float): The current price
        db: SQLAlchemy database instance
        models: Database models module
    """
    try:
        # Find all un-triggered alerts where the current price is below the target price
        alerts = models["PriceAlert"].query.filter_by(
            product_id=product_id,
            alert_sent=False
        ).filter(
            models["PriceAlert"].target_price >= current_price
        ).all()
        
        for alert in alerts:
            # Mark alert as sent
            alert.alert_sent = True
            db.session.commit()
            
            # Send email alert (this will be implemented in email.py)
            logger.info(f"Price alert triggered for product {product_id} - Target: {alert.target_price}, Current: {current_price}")
            
            # Import and send email alert
            from email_service import send_price_alert_email
            
            # Get the product using modern SQLAlchemy method
            product = db.session.get(models["Product"], alert.product_id)
            if product:
                send_price_alert_email(alert, product, current_price)
    
    except Exception as e:
        logger.error(f"Error checking price alerts: {e}")
        db.session.rollback()