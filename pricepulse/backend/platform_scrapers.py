import logging
import re
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

# Import platform-specific scrapers
from scraper import extract_amazon_product_info
from scraper_flipkart import extract_flipkart_product_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('platform_scrapers')

# Headers for search requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

def clean_product_name(name):
    """
    Clean and standardize product name for better comparison.
    
    Args:
        name (str): Product name to clean
        
    Returns:
        str: Cleaned product name
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove model numbers, special characters, and extra whitespace
    name = re.sub(r'\([^)]*\)', ' ', name)  # Remove text in parentheses
    name = re.sub(r'\b\w+\d+\w*\b', ' ', name)  # Remove model numbers like A12B or 123XYZ
    name = re.sub(r'[^\w\s]', ' ', name)  # Remove special characters
    name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
    
    return name

def extract_product_metadata(product_name):
    """
    Extract key metadata from product name to aid in cross-platform matching.
    
    Args:
        product_name (str): Product name
        
    Returns:
        dict: Extracted metadata like brand, category, model, etc.
    """
    metadata = {
        'original_name': product_name,
        'cleaned_name': clean_product_name(product_name),
        'brand': None,
        'category': None,
        'key_features': []
    }
    
    # Extract brand (common brands as example)
    brands = [
        'samsung', 'apple', 'xiaomi', 'redmi', 'realme', 'oneplus', 'vivo', 'oppo',
        'lenovo', 'hp', 'dell', 'asus', 'acer', 'msi', 'lg', 'sony', 'panasonic',
        'bosch', 'philips', 'havells', 'prestige', 'milton', 'nike', 'adidas', 'puma'
    ]
    
    clean_name = metadata['cleaned_name']
    for brand in brands:
        if re.search(r'\b' + re.escape(brand) + r'\b', clean_name):
            metadata['brand'] = brand
            break
    
    # Try to detect category based on keywords
    categories = {
        'phone': ['phone', 'smartphone', 'mobile'],
        'laptop': ['laptop', 'notebook', 'macbook'],
        'tv': ['tv', 'television', 'smart tv', 'led tv'],
        'headphone': ['headphone', 'earphone', 'earbud', 'airpod'],
        'watch': ['watch', 'smartwatch', 'fitness band'],
        'camera': ['camera', 'dslr', 'mirrorless'],
        'speaker': ['speaker', 'soundbar', 'home theater'],
        'appliance': ['refrigerator', 'washing machine', 'microwave', 'air conditioner']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in clean_name:
                metadata['category'] = category
                break
        if metadata['category']:
            break
    
    # Extract key features like storage capacity, RAM, etc.
    # Look for storage patterns like 128GB, 1TB, etc.
    storage_match = re.search(r'\b(\d+)\s*(gb|tb)\b', clean_name, re.IGNORECASE)
    if storage_match:
        metadata['key_features'].append(f"{storage_match.group(1)}{storage_match.group(2).upper()}")
    
    # Look for RAM patterns like 8GB RAM, 16GB, etc.
    ram_match = re.search(r'\b(\d+)\s*gb\s*ram\b', clean_name, re.IGNORECASE)
    if ram_match:
        metadata['key_features'].append(f"{ram_match.group(1)}GB RAM")
    
    # Look for screen size patterns like 6.1 inch, 15.6", etc.
    screen_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:inch|"|\'\')\b', clean_name, re.IGNORECASE)
    if screen_match:
        metadata['key_features'].append(f"{screen_match.group(1)}\"")
    
    return metadata

def search_amazon(query, max_results=5):
    """
    Search for products on Amazon.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of product URLs
    """
    try:
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        product_cards = soup.select('.s-result-item[data-asin]:not([data-asin=""])')
        
        results = []
        for card in product_cards[:max_results]:
            product_link = card.select_one('h2 a')
            if product_link and product_link.get('href'):
                url = 'https://www.amazon.in' + product_link.get('href')
                results.append(url)
        
        return results
    except Exception as e:
        logger.error(f"Error searching Amazon: {e}")
        return []

def search_flipkart(query, max_results=5):
    """
    Search for products on Flipkart.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of product URLs
    """
    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        product_cards = soup.select('._1AtVbE._13oc-S')
        
        results = []
        for card in product_cards[:max_results]:
            product_link = card.select_one('._1fQZEK, ._3bPFwb, ._2rpwqI')
            if product_link and product_link.get('href'):
                url = 'https://www.flipkart.com' + product_link.get('href')
                results.append(url)
        
        return results
    except Exception as e:
        logger.error(f"Error searching Flipkart: {e}")
        return []

def find_similar_products(product_name, metadata=None):
    """
    Find similar products across different platforms.
    
    Args:
        product_name (str): Product name to search for
        metadata (dict, optional): Pre-extracted metadata to aid in matching
        
    Returns:
        dict: Results from different platforms
    """
    if not metadata:
        metadata = extract_product_metadata(product_name)
    
    search_query = product_name
    
    # If we have extracted brand and category, create a more focused query
    if metadata['brand'] and metadata['category']:
        search_query = f"{metadata['brand']} {metadata['category']} {' '.join(metadata['key_features'])}"
    
    logger.info(f"Searching for: {search_query}")
    
    # Search each platform in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        amazon_future = executor.submit(search_amazon, search_query)
        flipkart_future = executor.submit(search_flipkart, search_query)
        
        amazon_urls = amazon_future.result()
        flipkart_urls = flipkart_future.result()
    
    results = {
        'amazon': [],
        'flipkart': []
    }
    
    # Process Amazon results
    for url in amazon_urls:
        try:
            amazon_info = extract_amazon_product_info(url)
            if amazon_info['success']:
                results['amazon'].append(amazon_info)
        except Exception as e:
            logger.error(f"Error extracting Amazon product info: {e}")
    
    # Process Flipkart results
    for url in flipkart_urls:
        try:
            flipkart_info = extract_flipkart_product_info(url)
            if flipkart_info['success']:
                results['flipkart'].append(flipkart_info)
        except Exception as e:
            logger.error(f"Error extracting Flipkart product info: {e}")
    
    return results

def compare_product_across_platforms(product_url, platform='amazon'):
    """
    Compare a specific product across different platforms.
    
    Args:
        product_url (str): URL of the product to compare
        platform (str): Platform of the original product URL ('amazon' or 'flipkart')
        
    Returns:
        dict: Comparison results
    """
    logger.info(f"Comparing product across platforms: {product_url} (platform: {platform})")
    
    # Extract information about the original product
    if platform.lower() == 'amazon':
        original_info = extract_amazon_product_info(product_url)
    elif platform.lower() == 'flipkart':
        original_info = extract_flipkart_product_info(product_url)
    else:
        return {
            'success': False,
            'error': f"Unsupported platform: {platform}"
        }
    
    if not original_info['success']:
        return {
            'success': False,
            'error': f"Failed to extract information from original product: {original_info.get('error', 'Unknown error')}"
        }
    
    # Extract metadata from the product name
    metadata = extract_product_metadata(original_info['name'])
    
    # Find similar products
    comparison_results = find_similar_products(original_info['name'], metadata)
    
    return {
        'success': True,
        'original_product': original_info,
        'comparison': comparison_results
    }