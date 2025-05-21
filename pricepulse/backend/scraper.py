import requests
import time
import random
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

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

def get_soup_with_requests(url):
    """Attempt to get the soup using the requests library."""
    try:
        # Add a random delay to avoid being blocked
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        return BeautifulSoup(response.content, 'lxml')
    except requests.RequestException as e:
        logger.error(f"Error using requests: {e}")
        return None

def get_soup_with_selenium(url):
    """Get the soup using Selenium when requests fails."""
    driver = None
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
        
        # Initialize the Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )
        
        # Add a random delay to simulate human behavior
        time.sleep(random.uniform(2, 5))
        
        # Get the page source
        page_source = driver.page_source
        
        return BeautifulSoup(page_source, 'lxml')
    except (TimeoutException, WebDriverException) as e:
        logger.error(f"Error using Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def extract_amazon_product_info(url):
    """
    Extract product information from an Amazon product URL.
    
    Args:
        url (str): The Amazon product URL
        
    Returns:
        dict: Dictionary containing product information or error details
    """
    logger.info(f"Scraping Amazon product: {url}")
    
    # Try with requests first
    soup = get_soup_with_requests(url)
    
    # If requests failed, try with Selenium
    if not soup:
        logger.info("Requests approach failed, trying with Selenium")
        soup = get_soup_with_selenium(url)
    
    # If both methods failed, return an error
    if not soup:
        logger.error("Both scraping methods failed")
        return {
            'success': False,
            'error': 'Failed to retrieve product information'
        }
    
    try:
        # Extract product name
        product_name_element = soup.select_one('#productTitle')
        product_name = product_name_element.get_text().strip() if product_name_element else 'Name not found'
        
        # Extract product image
        image_element = soup.select_one('#landingImage') or soup.select_one('#imgBlkFront')
        image_url = image_element.get('src') if image_element else None
        
        # Extract price
        price_element = soup.select_one('.a-price .a-offscreen') or soup.select_one('#priceblock_ourprice') or soup.select_one('#priceblock_dealprice')
        
        if price_element:
            price_text = price_element.get_text().strip()
            # Remove currency symbol and commas, then convert to float
            price_text = price_text.replace('₹', '').replace(',', '').replace('$', '').strip()
            # Handle price ranges (e.g., "₹1,234 - ₹5,678")
            if ' - ' in price_text:
                price_text = price_text.split(' - ')[0]
            try:
                price = float(price_text)
            except ValueError:
                logger.error(f"Could not convert price text to float: {price_text}")
                price = None
        else:
            price = None
        
        # Determine currency
        currency = '₹'  # Default for Amazon India
        if price_element and price_element.get_text().strip().startswith('$'):
            currency = '$'
            
        return {
            'success': True,
            'name': product_name,
            'image_url': image_url,
            'price': price,
            'currency': currency,
            'url': url
        }
    
    except Exception as e:
        logger.error(f"Error extracting product information: {e}")
        return {
            'success': False,
            'error': f'Error extracting product information: {str(e)}'
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
        product = models.Product.query.filter_by(url=url).first()
        
        if not product:
            # Create new product
            product = models.Product(
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
            price_record = models.PriceRecord(
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
        alerts = models.PriceAlert.query.filter_by(
            product_id=product_id,
            alert_sent=False
        ).filter(
            models.PriceAlert.target_price >= current_price
        ).all()
        
        for alert in alerts:
            # Mark alert as sent
            alert.alert_sent = True
            db.session.commit()
            
            # Send email alert (this will be implemented in email.py)
            logger.info(f"Price alert triggered for product {product_id} - Target: {alert.target_price}, Current: {current_price}")
            
            # TODO: Call email sending function
            # send_price_alert_email(alert, current_price)
    
    except Exception as e:
        logger.error(f"Error checking price alerts: {e}")
        db.session.rollback()