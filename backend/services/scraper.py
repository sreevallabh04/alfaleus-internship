import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional, Tuple, Any
import re
from urllib.parse import urlparse
import random

logger = logging.getLogger(__name__)

def get_mock_product_data():
    """
    Generate mock product data for testing purposes.
    Used for development and testing when real scraping is not available.
    """
    mock_products = [
        {
            'title': 'iPhone 14 Pro Max (256GB, Deep Purple)',
            'current_price': 120999.00,
            'image_url': 'https://example.com/images/iphone.jpg',
            'amazon_url': 'https://www.amazon.in/Apple-iPhone-Pro-Max-256GB/dp/B0BDJH6GL1'
        },
        {
            'title': 'Samsung Galaxy S23 Ultra (12GB RAM, 256GB Storage)',
            'current_price': 104999.00,
            'image_url': 'https://example.com/images/samsung.jpg',
            'amazon_url': 'https://www.amazon.in/Samsung-Galaxy-Ultra-Storage-Phantom/dp/B0BT9CXXXX'
        },
        {
            'title': 'Sony WH-1000XM5 Wireless Noise Cancelling Headphones',
            'current_price': 29990.00,
            'image_url': 'https://example.com/images/sony.jpg',
            'amazon_url': 'https://www.amazon.in/Sony-WH-1000XM5-Cancelling-Headphones-Black/dp/B09XXX'
        }
    ]
    
    # Return a random product from the list
    return random.choice(mock_products)

# Standalone function for compatibility with imports
def scrape_product(url: str) -> Dict[str, Any]:
    """
    Scrape product information from Amazon.
    Wrapper around AmazonScraper for compatibility.
    """
    scraper = AmazonScraper()
    success, data = scraper.scrape_product(url)
    if success:
        return data
    return {}

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def is_valid_amazon_url(self, url: str) -> bool:
        """Check if the URL is a valid Amazon product URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc in ['www.amazon.com', 'amazon.com', 'www.amazon.in', 'amazon.in']
        except Exception as e:
            logger.error(f"Error validating Amazon URL: {e}")
            return False
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract the product ID from an Amazon URL."""
        try:
            # Match patterns like /dp/PRODUCT_ID or /gp/product/PRODUCT_ID
            patterns = [
                r'/dp/([A-Z0-9]{10})',
                r'/gp/product/([A-Z0-9]{10})',
                r'/product/([A-Z0-9]{10})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            logger.error(f"Error extracting product ID: {e}")
            return None
    
    def scrape_product(self, url: str) -> Tuple[bool, Dict]:
        """
        Scrape product information from Amazon.
        Returns a tuple of (success, data).
        """
        try:
            if not self.is_valid_amazon_url(url):
                return False, {'error': 'Invalid Amazon URL'}
            
            product_id = self.extract_product_id(url)
            if not product_id:
                return False, {'error': 'Could not extract product ID from URL'}
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_elem = soup.find('span', {'id': 'productTitle'})
            title = title_elem.text.strip() if title_elem else None
            
            # Extract price
            price_elem = soup.find('span', {'class': 'a-price-whole'})
            price = float(price_elem.text.replace(',', '')) if price_elem else None
            
            # Extract image URL
            image_elem = soup.find('img', {'id': 'landingImage'})
            image_url = image_elem.get('data-old-hires') or image_elem.get('src') if image_elem else None
            
            if not all([title, price, image_url]):
                return False, {'error': 'Could not extract all required product information'}
            
            return True, {
                'title': title,
                'current_price': price,
                'image_url': image_url,
                'amazon_url': url
            }
            
        except requests.RequestException as e:
            logger.error(f"Request error while scraping Amazon: {e}")
            return False, {'error': 'Failed to fetch product information'}
        except Exception as e:
            logger.error(f"Error scraping Amazon product: {e}")
            return False, {'error': 'An unexpected error occurred'}