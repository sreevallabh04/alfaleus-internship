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
logger = logging.getLogger('flipkart_scraper')

# Headers to mimic a browser visit
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/'
}

def get_normalized_flipkart_url(url):
    """
    Extract and normalize the Flipkart product URL to get a clean URL.
    
    Args:
        url (str): The Flipkart product URL
        
    Returns:
        str: Normalized Flipkart URL or original URL if parsing fails
    """
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if it's a Flipkart domain
        if 'flipkart.com' not in parsed_url.netloc:
            return url
        
        # Try to extract product ID from URL path
        pid_match = re.search(r'/p/([^/]+)(?:/|$)', url)
        if pid_match:
            product_id = pid_match.group(1)
            # Clean URL with just the product ID
            return f"https://www.flipkart.com/p/{product_id}"
        
        # If we can't extract a product ID, just return the original URL
        return url
    except Exception as e:
        logger.error(f"Error normalizing Flipkart URL: {e}")
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
            if 'captcha' in response.text.lower():
                logger.warning(f"Captcha detected on attempt {attempt+1}. Retrying...")
                continue
                
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.warning(f"Request attempt {attempt+1} failed: {e}")
            if attempt == retries - 1:
                logger.error(f"All {retries} attempts failed")
                return None

def extract_flipkart_product_info(url):
    """
    Extract product information from a Flipkart product URL.
    
    Args:
        url (str): The Flipkart product URL
        
    Returns:
        dict: Dictionary containing product information or error details
    """
    logger.info(f"Scraping Flipkart product: {url}")
    
    # Normalize the URL to get a clean URL
    normalized_url = get_normalized_flipkart_url(url)
    logger.info(f"Normalized URL: {normalized_url}")
    
    # Try with requests with multiple retries
    soup = get_soup_with_requests(normalized_url, retries=3)
    
    # If all methods failed, return an error
    if not soup:
        logger.error("Scraping failed")
        return {
            'success': False,
            'error': 'Failed to retrieve product information. Please check the URL and try again.',
            'platform': 'Flipkart'
        }
    
    try:
        # Extract product name
        product_name = None
        product_name_element = soup.select_one('.B_NuCI')
        if product_name_element:
            product_name = product_name_element.get_text().strip()
        
        if not product_name:
            # Try alternative selectors
            alt_title_selectors = ['.yhB1nd', '._35KyD6', '._3wU53n']
            for selector in alt_title_selectors:
                element = soup.select_one(selector)
                if element:
                    product_name = element.get_text().strip()
                    break
        
        if not product_name:
            product_name = "Flipkart Product"  # Fallback name
        
        # Extract product image
        image_url = None
        image_selectors = ['._396cs4', '._2r_T1I', '._3exPp9']
        for selector in image_selectors:
            image_element = soup.select_one(selector)
            if image_element and image_element.get('src'):
                image_url = image_element.get('src')
                break
        
        # Extract price
        price = None
        currency = '₹'  # Default for Flipkart India
        
        price_selectors = [
            '._30jeq3._1_WHN1', 
            '._30jeq3', 
            '.CEmiEU'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text().strip()
                # Remove currency symbol and commas, then convert to float
                price_text = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
                try:
                    if price_text:
                        price = float(price_text)
                        break
                except ValueError:
                    logger.warning(f"Could not convert price text to float: {price_text}")
        
        # Extract rating
        rating = None
        rating_element = soup.select_one('._3LWZlK')
        if rating_element:
            try:
                rating = float(rating_element.get_text().strip())
            except ValueError:
                logger.warning("Could not convert rating to float")
        
        # Extract delivery information
        delivery = "Standard Delivery"
        delivery_element = soup.select_one('._3XINqE')
        if delivery_element:
            delivery = delivery_element.get_text().strip()
        
        # Build the result
        result = {
            'success': True,
            'name': product_name,
            'image_url': image_url,
            'price': price,
            'currency': currency,
            'url': normalized_url,
            'platform': 'Flipkart',
            'rating': rating,
            'delivery': delivery
        }
        
        # Validate result
        if not product_name or product_name == "Flipkart Product":
            logger.warning("Could not extract proper product name")
            if not price:
                # If we also couldn't get price, the scraping probably failed
                logger.error("Could not extract product name or price - scraping likely failed")
                return {
                    'success': False,
                    'error': 'Could not extract essential product information. Please check the URL and try again.',
                    'platform': 'Flipkart'
                }
        
        return result
    
    except Exception as e:
        logger.error(f"Error extracting product information: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'Error extracting product information. Please try again with a different URL or contact support.',
            'platform': 'Flipkart'
        }