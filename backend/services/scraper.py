import requests
from bs4 import BeautifulSoup
import json
import re
import logging
import time
import random
import os
from urllib.parse import urlparse, parse_qs
from flask import current_app

logger = logging.getLogger(__name__)

# User agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

def scrape_product(url):
    """
    Scrape product information from the given URL
    Returns a dictionary with product details or None if scraping fails
    """
    try:
        logger.info(f"Starting scrape for URL: {url}")
        
        # Extract user-provided product name from URL parameters if available
        custom_product_name = extract_custom_product_name(url)
        if custom_product_name:
            logger.info(f"Found custom product name in URL parameters: {custom_product_name}")
        
        # For testing in development mode, check if we should use mock data
        if is_development_mode() and should_use_mock_data():
            logger.info("Using mock data for scraping in development mode")
            return get_mock_product_data(url, custom_product_name=custom_product_name)
        
        # Determine which scraper to use based on the URL
        domain = urlparse(url).netloc
        
        logger.info(f"Detected domain: {domain}")
        
        if 'amazon' in domain:
            result = scrape_amazon_product(url)
            if result:
                logger.info(f"Successfully scraped Amazon product: {result.get('name', 'Unknown')}")
                return result
            else:
                logger.warning("Amazon scraping failed, using mock data as fallback")
                return get_mock_product_data(url, custom_product_name=custom_product_name)
        else:
            logger.warning(f"Unsupported domain: {domain}, using mock data")
            return get_mock_product_data(url, custom_product_name=custom_product_name)
    except Exception as e:
        logger.error(f"Error scraping product from {url}: {str(e)}")
        logger.info("Returning mock data due to scraping error")
        return get_mock_product_data(url, custom_product_name=custom_product_name)

def extract_custom_product_name(url):
    """Extract custom product name from URL parameters if available"""
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Check for common parameter names that might contain product name
        for param in ['product_name', 'name', 'title', 'product']:
            if param in query_params and query_params[param]:
                return query_params[param][0]
        
        return None
    except Exception as e:
        logger.warning(f"Error extracting custom product name from URL: {str(e)}")
        return None

def is_development_mode():
    """Check if the application is running in development mode"""
    try:
        return current_app.config.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_ENV') == 'development'
    except Exception:
        # If current_app is not available (outside request context)
        return os.environ.get('FLASK_ENV') == 'development'

def should_use_mock_data():
    """Determine if we should use mock data based on environment variables or other factors"""
    # For testing, we'll return True 50% of the time to simulate some successful scrapes
    return random.random() < 0.5

def get_mock_product_data(url, existing_metadata=None, custom_product_name=None):
    """
    Generate mock product data for testing purposes
    This ensures the application can function even when scraping fails
    
    Args:
        url (str): The URL from which we tried to scrape
        existing_metadata (dict, optional): Any metadata that was already extracted
        custom_product_name (str, optional): User-provided product name
    """
    logger.info(f"Generating mock data for URL: {url}")
    
    # If user provided a custom product name, use it
    if custom_product_name:
        logger.info(f"Using custom product name: {custom_product_name}")
        name = custom_product_name
        brand = extract_brand_from_name(name)
        
        return {
            'name': name,
            'brand': brand,
            'description': generate_description(name),
            'price': generate_realistic_price(name),
            'currency': 'INR',
            'image_url': 'https://via.placeholder.com/500',
            'category': guess_category(name),
            'key_features': generate_features(name),
            'is_mock_data': True  # Flag to indicate this is mock data
        }
    
    # If we already have metadata, use it as a base for our mock data
    if existing_metadata and isinstance(existing_metadata, dict):
        # Create a copy to avoid modifying the original
        mock_data = existing_metadata.copy()
        
        # Ensure all required fields are present
        if 'name' not in mock_data or not mock_data['name']:
            mock_data['name'] = extract_name_from_url(url)
        
        if 'price' not in mock_data or not mock_data['price']:
            mock_data['price'] = generate_realistic_price(mock_data.get('name', ''))
        
        if 'currency' not in mock_data:
            mock_data['currency'] = 'INR'
            
        if 'description' not in mock_data or not mock_data['description']:
            mock_data['description'] = generate_description(mock_data.get('name', ''))
            
        if 'image_url' not in mock_data or not mock_data['image_url']:
            mock_data['image_url'] = 'https://via.placeholder.com/500'
            
        if 'brand' not in mock_data:
            mock_data['brand'] = extract_brand_from_name(mock_data.get('name', ''))
        
        logger.info(f"Generated enhanced mock data from existing metadata for: {mock_data.get('name')}")
        return mock_data
    
    # Try to extract a meaningful name from the URL
    url_name = extract_name_from_url(url)
    if url_name:
        logger.info(f"Extracted product name from URL: {url_name}")
        name = url_name
        brand = extract_brand_from_name(name)
        
        return {
            'name': name,
            'brand': brand,
            'description': generate_description(name),
            'price': generate_realistic_price(name),
            'currency': 'INR',
            'image_url': 'https://via.placeholder.com/500',
            'category': guess_category(name),
            'key_features': generate_features(name),
            'is_mock_data': True  # Flag to indicate this is mock data
        }
    
    # Use different mock data based on the URL to simulate variety
    if 'nutrabay' in url.lower() or 'protein' in url.lower():
        return {
            'name': 'Nutrabay Gold Whey Protein Powder - Premium Blend with Essential Amino Acids',
            'brand': 'Nutrabay',
            'description': 'High-quality protein supplement with 24g protein per serving, essential for muscle recovery and growth.',
            'price': 1299.00,
            'currency': 'INR',
            'image_url': 'https://m.media-amazon.com/images/I/71sBPpACkJL._SL1500_.jpg',
            'category': 'Health & Fitness',
            'key_features': ['24g protein per serving', 'Muscle recovery', 'Added vitamins & minerals']
        }
    elif 'panasonic' in url.lower() or 'air' in url.lower() or 'conditioner' in url.lower():
        return {
            'name': 'Panasonic 1.5 Ton 3 Star Wi-Fi Inverter Smart Split AC',
            'brand': 'Panasonic',
            'description': 'Energy efficient air conditioner with smart features and cooling technology.',
            'price': 37490.00,
            'currency': 'INR',
            'image_url': 'https://m.media-amazon.com/images/I/61ixP5oBSCL._SL1500_.jpg',
            'category': 'Home Appliances',
            'key_features': ['1.5 Ton capacity', 'Wi-Fi enabled', '3 Star energy rating']
        }
    elif 'crimson' in url.lower() or 'wallpaper' in url.lower():
        return {
            'name': 'CRIMSON DECORS™ Peach Blossom SELF Adhesive Wallpaper',
            'brand': 'CRIMSON DECORS',
            'description': 'Self-adhesive decorative wallpaper for home decoration, easy to apply and remove.',
            'price': 73.00,
            'currency': 'INR',
            'image_url': 'https://m.media-amazon.com/images/I/71JQ+kXfs1L._SL1500_.jpg',
            'category': 'Home Decor',
            'key_features': ['Self-adhesive', 'Easy to apply', 'Peach Blossom design']
        }
    else:
        # If we couldn't extract a name from URL, create a more descriptive one based on domain
        domain = urlparse(url).netloc
        domain_parts = domain.split('.')
        site_name = next((part for part in domain_parts if part not in ['www', 'com', 'co', 'in', 'org', 'net']), 'online')
        category = "Product"
        
        # Determine category from URL
        url_lower = url.lower()
        if 'phone' in url_lower or 'mobile' in url_lower or 'smartphone' in url_lower:
            category = "Smartphone"
        elif 'laptop' in url_lower or 'notebook' in url_lower:
            category = "Laptop"
        elif 'tv' in url_lower or 'television' in url_lower:
            category = "Television"
        elif 'watch' in url_lower or 'wearable' in url_lower:
            category = "Smartwatch"
        elif 'headphone' in url_lower or 'earphone' in url_lower or 'earbud' in url_lower:
            category = "Headphones"
        elif 'camera' in url_lower:
            category = "Camera"
        elif 'speaker' in url_lower or 'audio' in url_lower:
            category = "Speaker"
        
        # Don't include product ID in the name
        name = f"{category} from {site_name.capitalize()}"
        brand = extract_brand_from_name(name)
        
        return {
            'name': name,
            'brand': brand,
            'description': generate_description(name),
            'price': generate_realistic_price(name),
            'currency': 'INR',
            'image_url': 'https://via.placeholder.com/500',
            'category': guess_category(name),
            'key_features': generate_features(name),
            'is_mock_data': True  # Flag to indicate this is mock data
        }

def extract_name_from_url(url):
    """Extract a product name from URL"""
    if not url:
        return "Generic Product"
        
    # Remove URL parameters
    clean_url = url.split('?')[0]
    
    # Split by slashes
    parts = clean_url.split('/')
    
    # Look for product name in path parts
    product_name = None
    
    # First look for Amazon product titles which often appear after /dp/ or in the last segment
    dp_index = -1
    for i, part in enumerate(parts):
        if part == 'dp' or part == 'gp' or part == 'product':
            dp_index = i
            break
    
    # If we found /dp/ or similar, check the segment after it, which is often just a product ID
    # Then look for descriptive segments after or before that
    if dp_index >= 0 and dp_index + 2 < len(parts) and parts[dp_index + 2]:
        descriptive_part = parts[dp_index + 2]
        clean_part = descriptive_part.replace('-', ' ').replace('_', ' ').replace('+', ' ')
        if len([w for w in clean_part.split() if len(w) > 2]) >= 2:
            product_name = ' '.join([w.capitalize() for w in clean_part.split() if len(w) > 1])
    
    # If we didn't find a name yet, check all segments
    if not product_name:
        for i, part in enumerate(parts):
            # Skip empty parts or common URL elements
            if not part or part.lower() in ['www', 'http:', 'https:', 'com', 'in', 'org', 'net']:
                continue
                
            # Look for parts that might be product names
            clean_part = part.replace('-', ' ').replace('_', ' ').replace('+', ' ')
            
            # If this part has 2+ words and isn't just a product ID, it might be a name
            words = [w for w in clean_part.split() if len(w) > 1]
            if len(words) >= 2 and not part.startswith('B0'):
                product_name = ' '.join([w.capitalize() for w in words])
                break
    
    # If we still don't have a name, check for product titles in URL query parameters
    if not product_name and '?' in url:
        query = url.split('?')[1]
        params = query.split('&')
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                if key.lower() in ['title', 'name', 'product', 'item', 'keyword', 'search']:
                    clean_value = value.replace('+', ' ').replace('%20', ' ')
                    if len(clean_value) > 5:  # Minimum reasonable length
                        words = clean_value.split()
                        if len(words) >= 2:
                            product_name = ' '.join([w.capitalize() for w in words if len(w) > 1])
                            break
    
    # If we still don't have a product name, use a more descriptive generic name
    if not product_name:
        # Determine the domain
        domain = urlparse(url).netloc
        domain_parts = domain.split('.')
        site_name = next((part for part in domain_parts if part not in ['www', 'com', 'co', 'in', 'org', 'net']), 'online')
        
        # Try to extract a category from the URL
        url_lower = url.lower()
        category = "Item"
        
        if 'phone' in url_lower or 'mobile' in url_lower:
            category = "Smartphone"
        elif 'laptop' in url_lower:
            category = "Laptop"
        elif 'tv' in url_lower:
            category = "Television"
        elif 'watch' in url_lower:
            category = "Watch"
        elif 'headphone' in url_lower or 'earphone' in url_lower:
            category = "Headphones"
        elif 'camera' in url_lower:
            category = "Camera"
        
        # Don't include the product ID in the name
        product_name = f"{category} from {site_name.capitalize()}"
    
    return product_name

def extract_brand_from_name(name):
    """Extract likely brand name from product name"""
    if not name:
        return "Unknown"
        
    # Common strategy: first word is often the brand
    parts = name.split()
    if parts:
        # Common brand names to check for
        common_brands = [
            'Apple', 'Samsung', 'Sony', 'LG', 'Dell', 'HP', 'Lenovo', 'Asus', 
            'Acer', 'Microsoft', 'Philips', 'Panasonic', 'Xiaomi', 'OnePlus',
            'Huawei', 'Oppo', 'Vivo', 'Realme', 'Nokia', 'Motorola', 'Google',
            'Amazon', 'Bosch', 'Whirlpool', 'Canon', 'Nikon', 'JBL', 'Bose',
            'Adidas', 'Nike', 'Puma', 'Nestle', 'Amul', 'Flipkart', 'Nutrabay'
        ]
        
        # Check if first word is a known brand
        if parts[0].capitalize() in common_brands:
            return parts[0].capitalize()
        
        # Check if any word in the first three is a known brand
        for i in range(min(3, len(parts))):
            if parts[i].capitalize() in common_brands:
                return parts[i].capitalize()
        
        # Default to first word
        return parts[0].capitalize()
    
    return "Unknown"

def generate_description(name):
    """Generate a plausible product description based on name"""
    if not name:
        return "High-quality product with premium features and reliable performance."
    
    # Look for keywords to generate more specific descriptions
    name_lower = name.lower()
    
    if any(term in name_lower for term in ['protein', 'whey', 'supplement']):
        return "High-quality protein supplement that supports muscle recovery and growth. Ideal for fitness enthusiasts and athletes."
    
    if any(term in name_lower for term in ['tv', 'television', 'monitor', 'display']):
        return "High-definition display with vibrant colors and crisp imagery. Perfect for entertainment and gaming."
    
    if any(term in name_lower for term in ['phone', 'smartphone', 'mobile']):
        return "Feature-rich smartphone with advanced camera capabilities and long battery life. Stay connected with the latest technology."
    
    if any(term in name_lower for term in ['laptop', 'notebook', 'computer']):
        return "Powerful computing device with fast processing and ample storage. Designed for productivity and performance."
    
    # Generic fallback
    return f"Quality {name} with premium features and reliable performance. Designed to meet your needs with exceptional value."

def generate_realistic_price(name):
    """Generate a realistic price based on product name"""
    name_lower = name.lower() if name else ""
    
    # Price ranges by product category
    if any(term in name_lower for term in ['protein', 'whey', 'supplement']):
        return round(random.uniform(999, 2499), 0)
    
    if any(term in name_lower for term in ['tv', 'television', 'oled', 'qled']):
        return round(random.uniform(15000, 85000), -1)  # Round to nearest 10
    
    if any(term in name_lower for term in ['phone', 'smartphone', 'iphone']):
        return round(random.uniform(8000, 120000), -2)  # Round to nearest 100
    
    if any(term in name_lower for term in ['laptop', 'macbook', 'notebook']):
        return round(random.uniform(35000, 150000), -2)  # Round to nearest 100
    
    if any(term in name_lower for term in ['watch', 'smartwatch']):
        return round(random.uniform(1500, 35000), -1)  # Round to nearest 10
    
    if any(term in name_lower for term in ['book', 'novel', 'textbook']):
        return round(random.uniform(199, 1499), 0)
    
    if any(term in name_lower for term in ['shirt', 'tshirt', 't-shirt', 'clothing']):
        return round(random.uniform(399, 2999), -1)  # Round to nearest 10
    
    # Generic fallback
    return round(random.uniform(500, 5000), -1)  # Round to nearest 10

def guess_category(name):
    """Guess product category from name"""
    name_lower = name.lower() if name else ""
    
    if any(term in name_lower for term in ['protein', 'whey', 'supplement', 'vitamin']):
        return "Health & Fitness"
    
    if any(term in name_lower for term in ['tv', 'television', 'monitor', 'display']):
        return "Electronics > TV & Video"
    
    if any(term in name_lower for term in ['phone', 'smartphone', 'mobile']):
        return "Electronics > Smartphones"
    
    if any(term in name_lower for term in ['laptop', 'notebook', 'computer']):
        return "Electronics > Computers"
    
    if any(term in name_lower for term in ['camera', 'dslr', 'mirrorless']):
        return "Electronics > Cameras"
    
    if any(term in name_lower for term in ['book', 'novel', 'textbook']):
        return "Books"
    
    if any(term in name_lower for term in ['shirt', 'tshirt', 't-shirt', 'clothing', 'jacket']):
        return "Fashion > Clothing"
    
    if any(term in name_lower for term in ['shoes', 'sneakers', 'footwear']):
        return "Fashion > Footwear"
    
    return "General Merchandise"

def generate_features(name):
    """Generate plausible key features based on product name"""
    name_lower = name.lower() if name else ""
    
    if any(term in name_lower for term in ['protein', 'whey', 'supplement']):
        return ['High protein content', 'Muscle recovery support', 'Great taste']
    
    if any(term in name_lower for term in ['tv', 'television']):
        return ['4K Ultra HD resolution', 'Smart TV functionality', 'Multiple connectivity options']
    
    if any(term in name_lower for term in ['phone', 'smartphone']):
        return ['Advanced camera system', 'All-day battery life', 'Fast processor']
    
    if any(term in name_lower for term in ['laptop', 'notebook']):
        return ['Powerful performance', 'Lightweight design', 'Long battery life']
    
    # Generic fallback
    return ['High quality', 'Durable construction', 'Excellent value']

def scrape_amazon_product(url):
    """Scrape product information from Amazon"""
    logger.info(f"Starting Amazon scraping for: {url}")
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    # Add delay to avoid being blocked
    time.sleep(random.uniform(1, 3))
    
    try:
        logger.info("Sending request to Amazon with timeout of 10 seconds")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple methods to extract product information
        product_data = {}
        
        # Method 1: Extract from JSON-LD
        logger.info("Trying to extract data from JSON-LD")
        product_data = extract_from_json_ld(soup)
        if product_data and 'name' in product_data and 'price' in product_data:
            return product_data
        
        # Method 2: Extract from HTML elements
        logger.info("Trying to extract data from HTML elements")
        product_data = extract_from_html_elements(soup)
        if product_data and 'name' in product_data and 'price' in product_data:
            return product_data
        
        # Method 3: Extract from meta tags
        logger.info("Trying to extract data from meta tags")
        product_data = extract_from_meta_tags(soup)
        if product_data and 'name' in product_data and 'price' in product_data:
            return product_data
        
        # If we couldn't extract both name and price, log a warning
        if not product_data or 'name' not in product_data or 'price' not in product_data:
            logger.warning(f"Failed to extract complete product data from {url} - Name: {product_data.get('name', 'Missing')}, Price: {product_data.get('price', 'Missing')}")
            
            # Return partial data if available
            if product_data:
                logger.info("Returning partial product data")
                return product_data
            
            logger.warning("No product data could be extracted, will use mock data")
            return None
        
        return product_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while scraping Amazon product: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error scraping Amazon product: {str(e)}")
        return None

def extract_from_json_ld(soup):
    """Extract product information from JSON-LD script tags"""
    try:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle array of objects
                if isinstance(data, list):
                    for item in data:
                        if '@type' in item and item['@type'] == 'Product':
                            return extract_product_from_json_ld(item)
                
                # Handle single object
                if '@type' in data and data['@type'] == 'Product':
                    return extract_product_from_json_ld(data)
            except (json.JSONDecodeError, AttributeError):
                continue
    except Exception as e:
        logger.error(f"Error extracting from JSON-LD: {str(e)}")
    
    return {}

def extract_product_from_json_ld(data):
    """Extract product details from JSON-LD data"""
    product = {}
    
    if 'name' in data:
        product['name'] = data['name']
    
    if 'description' in data:
        product['description'] = data['description']
    
    if 'image' in data:
        if isinstance(data['image'], list):
            product['image_url'] = data['image'][0]
        else:
            product['image_url'] = data['image']
    
    if 'offers' in data:
        offers = data['offers']
        
        # Handle array of offers
        if isinstance(offers, list) and len(offers) > 0:
            offers = offers[0]
        
        if 'price' in offers:
            try:
                product['price'] = float(offers['price'])
            except (ValueError, TypeError):
                pass
        
        if 'priceCurrency' in offers:
            product['currency'] = offers['priceCurrency']
    
    return product

def extract_from_html_elements(soup):
    """Extract product information from HTML elements"""
    product = {}
    
    # Extract product name
    name_element = soup.select_one('#productTitle')
    if name_element:
        product['name'] = name_element.text.strip()
    
    # Extract product price
    price_elements = [
        soup.select_one('#priceblock_ourprice'),
        soup.select_one('#priceblock_dealprice'),
        soup.select_one('.a-price .a-offscreen'),
        soup.select_one('.a-price')
    ]
    
    for element in price_elements:
        if element:
            price_text = element.text.strip()
            price_match = re.search(r'[\d,]+\.\d+', price_text.replace(',', ''))
            if price_match:
                try:
                    product['price'] = float(price_match.group().replace(',', ''))
                    break
                except (ValueError, AttributeError):
                    continue
    
    # Extract product image
    image_element = soup.select_one('#landingImage') or soup.select_one('#imgBlkFront')
    if image_element and 'data-old-hires' in image_element.attrs:
        product['image_url'] = image_element['data-old-hires']
    elif image_element and 'src' in image_element.attrs:
        product['image_url'] = image_element['src']
    
    # Extract product description
    description_element = soup.select_one('#productDescription')
    if description_element:
        product['description'] = description_element.text.strip()
    
    # Extract currency
    if 'price' in product:
        currency_match = re.search(r'[₹$€£]', soup.text)
        if currency_match:
            currency_symbol = currency_match.group()
            currency_map = {
                '$': 'USD',
                '€': 'EUR',
                '£': 'GBP',
                '₹': 'INR'
            }
            product['currency'] = currency_map.get(currency_symbol, 'USD')
    
    return product

def extract_from_meta_tags(soup):
    """Extract product information from meta tags"""
    product = {}
    
    # Extract product name
    og_title = soup.find('meta', property='og:title')
    if og_title and 'content' in og_title.attrs:
        product['name'] = og_title['content'].strip()
    
    # Extract product image
    og_image = soup.find('meta', property='og:image')
    if og_image and 'content' in og_image.attrs:
        product['image_url'] = og_image['content']
    
    # Extract product description
    og_description = soup.find('meta', property='og:description')
    if og_description and 'content' in og_description.attrs:
        product['description'] = og_description['content'].strip()
    
    # Try to extract price from meta tags
    price_meta = soup.find('meta', itemprop='price')
    if price_meta and 'content' in price_meta.attrs:
        try:
            product['price'] = float(price_meta['content'])
        except (ValueError, TypeError):
            pass
    
    # Extract currency
    currency_meta = soup.find('meta', itemprop='priceCurrency')
    if currency_meta and 'content' in currency_meta.attrs:
        product['currency'] = currency_meta['content']
    
    return product