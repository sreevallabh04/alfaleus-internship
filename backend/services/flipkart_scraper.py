import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

def scrape_flipkart_price(url):
    """
    Scrape product price from a Flipkart URL.
    Returns the price as a float or None if scraping fails.
    """
    try:
        logger.info(f"Attempting to scrape Flipkart price from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Common selectors for Flipkart price - these might need adjustment based on current Flipkart HTML
        price_elements = soup.select('div._30jeq3, div._1Vfi6u, div._25b18c ._30jeq3')

        price_text = None
        for element in price_elements:
            if element.text:
                price_text = element.text.strip()
                break

        if price_text:
            # Clean the price text (remove currency symbols, commas, etc.)
            cleaned_price = re.sub(r'[^\d.]', '', price_text)
            try:
                price = float(cleaned_price)
                logger.info(f"Successfully scraped price {price} from Flipkart URL: {url}")
                return price
            except ValueError:
                logger.warning(f"Could not convert scraped price '{cleaned_price}' to float for URL: {url}")
                return None
        else:
            logger.warning(f"Could not find price element for Flipkart URL: {url}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error scraping Flipkart price from {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while scraping Flipkart price from {url}: {str(e)}")
        return None

# Example usage (for testing)
if __name__ == '__main__':
    test_url = "https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itm9b3900c843377" # Replace with a valid Flipkart URL
    price = scrape_flipkart_price(test_url)
    if price is not None:
        print(f"Scraped price: {price}")
    else:
        print("Failed to scrape price.")