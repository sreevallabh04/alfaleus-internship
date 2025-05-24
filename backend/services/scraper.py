import requests
from bs4 import BeautifulSoup
import json
import re
import logging
import time
import random
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from flask import current_app

logger = logging.getLogger(__name__)

# User agents to rotate - use more recent browser versions
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
]

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

def is_development_mode():
    """
    Check if the application is running in development mode
    This is more strict to ensure production never uses mock data
    """
    try:
        # Check Flask environment
        flask_env = current_app.config.get('FLASK_ENV')
        os_env = os.environ.get('FLASK_ENV')
        testing_mode = current_app.config.get('TESTING', False)
        
        # Only return True if explicitly set to development
        return flask_env == 'development' or os_env == 'development' or testing_mode
    except Exception:
        # If current_app is not available (outside request context)
        return os.environ.get('FLASK_ENV') == 'development'

def should_use_mock_data():
    """
    Determine if we should use mock data based on environment variables
    This is now deterministic and not random for consistency
    """
    # Check for explicit environment variable to allow mocks
    allow_mocks = os.environ.get('ALLOW_MOCK_DATA', 'false').lower() == 'true'
    
    # Only allow mock data if explicitly enabled AND in development mode
    if is_development_mode() and allow_mocks:
        logger.warning("Mock data is allowed in development mode")
        return True
    
    # In production, NEVER use mock data
    return False

def scrape_product(url):
    """
    Scrape product information from the given URL
    Returns a dictionary with product details or error information
    Never returns None - always returns a dict with either product data or error details
    """
    try:
        logger.info(f"Starting scrape for URL: {url}")
        
        # Extract user-provided product name from URL parameters if available
        custom_product_name = extract_custom_product_name(url)
        if custom_product_name:
            logger.info(f"Found custom product name in URL parameters: {custom_product_name}")
        
        # Determine which scraper to use based on the URL
        domain = urlparse(url).netloc
        logger.info(f"Detected domain: {domain}")
        
        if 'amazon' in domain:
            # Make multiple attempts with different scraping methods
            for attempt in range(3):
                logger.info(f"Amazon scraping attempt {attempt+1}/3")
                result = scrape_amazon_product(url)
                
                if result and 'name' in result and result['name'] and not result.get('scraping_failed', False):
                    logger.info(f"Successfully scraped Amazon product: {result.get('name', 'Unknown')}")
                    
                    # Flag to indicate this is real data, not mock
                    result['is_real_data'] = True
                    
                    # Add a timestamp
                    result['scraped_at'] = datetime.now().isoformat()
                    
                    return result
                
                # Wait briefly between attempts
                if attempt < 2:  # Don't sleep after last attempt
                    time.sleep(random.uniform(1, 3))
            
            # All attempts failed, log an error
            logger.error(f"All Amazon scraping attempts failed for URL: {url}")
            
            # For development only, use mock data if allowed
            if is_development_mode() and should_use_mock_data():
                logger.warning("Using mock data as fallback in development mode only")
                mock_data = get_mock_product_data(url, custom_product_name=custom_product_name)
                if mock_data:
                    mock_data['is_mock_data'] = True
                    mock_data['scraping_failed'] = True
                    return mock_data
            
            # In production, return failure instead of fake data
            return {
                'scraping_failed': True,
                'url': url,
                'error': 'Failed to extract product data after multiple attempts',
                'is_real_data': False
            }
        else:
            logger.warning(f"Unsupported domain: {domain}")
            
            # Only use mock data in development if explicitly allowed
            if is_development_mode() and should_use_mock_data():
                logger.warning("Using mock data for unsupported domain in development mode")
                mock_data = get_mock_product_data(url, custom_product_name=custom_product_name)
                if mock_data:
                    mock_data['is_mock_data'] = True
                    return mock_data
            
            # In production, return failure for unsupported domains
            return {
                'scraping_failed': True,
                'url': url,
                'error': f'Unsupported domain: {domain}',
                'is_real_data': False
            }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error scraping product from {url}: {error_message}")
        
        # Only use mock data in development if explicitly allowed
        if is_development_mode() and should_use_mock_data():
            logger.warning("Using mock data due to error in development mode only")
            mock_data = get_mock_product_data(url, custom_product_name=custom_product_name)
            if mock_data:
                mock_data['is_mock_data'] = True
                mock_data['scraping_failed'] = True
                mock_data['error'] = error_message
                return mock_data
        
        # In production, return the error information instead of fake data
        return {
            'scraping_failed': True,
            'url': url,
            'error': error_message,
            'is_real_data': False
        }

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

def scrape_amazon_product(url):
    """
    Scrape product information from Amazon with multiple methods and high resilience
    Never returns mock data - either returns real scraped data or fails with informative error
    """
    logger.info(f"Starting Amazon scraping for: {url}")
    
    # Store the product ID for validation
    product_id = None
    url_path = urlparse(url).path
    
    # Extract product ID from URL (typically starts with B0)
    if '/dp/' in url or '/gp/product/' in url:
        for segment in url_path.split('/'):
            if segment.startswith('B0') and len(segment) >= 10:
                product_id = segment
                logger.info(f"Extracted product ID from URL: {product_id}")
                break
    
    # Prepare headers with extensive browser-like properties
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Priority': 'u=0, i'
    }
    
    # Increased number of attempts for production reliability
    max_attempts = 5
    aggregated_data = {}
    
    for attempt in range(max_attempts):
        try:
            # Use a different user agent and headers for each attempt
            headers['User-Agent'] = get_random_user_agent()
            
            # Add random cookies and referrers to appear more like a real browser
            if attempt > 1:
                if random.random() > 0.5:
                    headers['Referer'] = 'https://www.google.com/'
                else:
                    headers['Referer'] = 'https://www.amazon.in/'
                    
                # Add some cookies
                headers['Cookie'] = f'session-id={random.randint(100000000, 999999999)}; session-token=random{random.randint(10000, 99999)}'
            
            # Progressive delay strategy to avoid blocks
            delay = random.uniform(1, 2 + attempt * 0.5)
            logger.info(f"Waiting {delay:.2f} seconds before attempt {attempt+1}/{max_attempts}")
            time.sleep(delay)
            
            # Increase timeout for later attempts
            timeout = 15 + (attempt * 5)
            logger.info(f"Sending request to Amazon (attempt {attempt+1}/{max_attempts}) with timeout of {timeout} seconds")
            
            # Use session for better connection reuse
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Check if we got a captcha or other block
            if 'captcha' in response.text.lower() or 'robot' in response.text.lower():
                logger.warning(f"Detected captcha/bot protection on attempt {attempt+1}")
                continue
                
            # Save the response for debugging in case of issues
            if attempt == 0:
                with open('amazon_response_debug.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("Saved response HTML for debugging")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Extract from JSON-LD (most reliable)
            logger.info("Trying to extract data from JSON-LD")
            json_ld_data = extract_from_json_ld(soup)
            if json_ld_data and 'name' in json_ld_data:
                logger.info(f"Successfully extracted product name from JSON-LD: {json_ld_data['name']}")
                # Merge with aggregated data, prioritizing JSON-LD
                aggregated_data.update(json_ld_data)
                
                # If we have both name and price, we can return early
                if 'name' in aggregated_data and 'price' in aggregated_data:
                    aggregated_data['extraction_method'] = 'json_ld'
                    return aggregated_data
            
            # Method 2: Extract from HTML elements
            logger.info("Trying to extract data from HTML elements")
            html_data = extract_from_html_elements(soup)
            if html_data:
                logger.info(f"Extracted data from HTML elements: {', '.join(html_data.keys())}")
                # Add any new fields from HTML extraction
                for key, value in html_data.items():
                    if key not in aggregated_data or not aggregated_data[key]:
                        aggregated_data[key] = value
                
                # If we now have both name and price, we can return
                if 'name' in aggregated_data and 'price' in aggregated_data:
                    aggregated_data['extraction_method'] = 'html_elements'
                    return aggregated_data
            
            # Method 3: Extract from meta tags
            logger.info("Trying to extract data from meta tags")
            meta_data = extract_from_meta_tags(soup)
            if meta_data:
                logger.info(f"Extracted data from meta tags: {', '.join(meta_data.keys())}")
                # Add any new fields from meta extraction
                for key, value in meta_data.items():
                    if key not in aggregated_data or not aggregated_data[key]:
                        aggregated_data[key] = value
                
                # If we now have both name and price, we can return
                if 'name' in aggregated_data and 'price' in aggregated_data:
                    aggregated_data['extraction_method'] = 'meta_tags'
                    return aggregated_data
            
            # Method 4: Extract from title tag as last resort
            logger.info("Trying to extract data from page title")
            title_tag = soup.title
            if title_tag and title_tag.string:
                title_text = title_tag.string.strip()
                # Remove common Amazon title suffixes
                for suffix in [" | Amazon.in", " | Amazon.com", " - Amazon", "Amazon.in", "Amazon.com"]:
                    if title_text.endswith(suffix):
                        title_text = title_text[:-len(suffix)].strip()
                
                if title_text and len(title_text) > 5:
                    logger.info(f"Extracted product name from title: {title_text}")
                    
                    # Only use title if we don't already have a name
                    if 'name' not in aggregated_data or not aggregated_data['name']:
                        aggregated_data['name'] = title_text
                    
                    if 'description' not in aggregated_data:
                        aggregated_data['description'] = title_text
                    
                    # Try to extract price if not already present
                    if 'price' not in aggregated_data:
                        price_elements = soup.find_all(text=re.compile(r'₹|₨|Rs\.?\s*\d+|\$\s*\d+|\d+\.?\d*'))
                        for price_text in price_elements:
                            price_match = re.search(r'\d+(?:,\d+)*(?:\.\d+)?', price_text)
                            if price_match:
                                try:
                                    price_str = price_match.group().replace(',', '')
                                    price = float(price_str)
                                    # Sanity check - price must be reasonable
                                    if 10 <= price <= 500000:  # Reasonable price range in INR
                                        aggregated_data['price'] = price
                                        aggregated_data['currency'] = 'INR' if '₹' in price_text or 'Rs' in price_text else 'USD'
                                        break
                                except ValueError:
                                    continue
            
            # Check if we have sufficient data after this attempt
            if 'name' in aggregated_data:
                # Even if we're missing some data, we have a name which is critical
                logger.info(f"Extracted product name after attempt {attempt+1}: {aggregated_data['name']}")
                
                # Add extraction attempt information
                aggregated_data['extraction_method'] = 'combined'
                aggregated_data['extraction_attempts'] = attempt + 1
                
                # If we have the product ID from the URL, add it for verification
                if product_id:
                    aggregated_data['product_id'] = product_id
                
                # Add URL to the data
                aggregated_data['url'] = url
                
                # Return the best data we have so far
                return aggregated_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on attempt {attempt+1}/{max_attempts}: {str(e)}")
            # Don't break, try a different strategy on next attempt
        except Exception as e:
            logger.error(f"Error on attempt {attempt+1}/{max_attempts}: {str(e)}")
            # Don't break, try a different strategy on next attempt
    
    # After all attempts failed, check if we've collected any useful data
    if aggregated_data and 'name' in aggregated_data:
        logger.warning("All direct scraping attempts had issues, but we collected partial data")
        
        # Add URL to the data
        aggregated_data['url'] = url
        aggregated_data['partial_data'] = True
        
        return aggregated_data
    
    # Last resort: Try to extract meaningful info directly from the URL
    logger.warning("All scraping attempts failed, extracting from URL as last resort")
    
    # Get product ID if we didn't extract it earlier
    if not product_id:
        for segment in url_path.split('/'):
            if segment.startswith('B0') and len(segment) >= 10:
                product_id = segment
                break
    
    # Extract a meaningful name from URL components
    url_name = extract_name_from_url(url)
    
    if url_name:
        logger.info(f"Extracted name from URL: {url_name}")
        result = {
            'name': url_name,
            'description': f"Product details for {url_name}",
            'url': url,
            'is_url_extracted': True,  # Flag to indicate this is URL-extracted data
            'extraction_method': 'url_fallback'
        }
        
        if product_id:
            result['product_id'] = product_id
            
        return result
    
    # If we get here, we've exhausted all options and failed to get meaningful data
    logger.error(f"Complete failure to extract any product data from {url}")
    return {
        'scraping_failed': True,
        'url': url,
        'error': 'Failed to extract any product data after multiple methods',
        'is_real_data': False
    }

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
    
    # Try to extract brand
    if 'brand' in data:
        try:
            if isinstance(data['brand'], dict) and 'name' in data['brand']:
                product['brand'] = data['brand']['name']
            elif isinstance(data['brand'], str):
                product['brand'] = data['brand']
        except Exception:
            pass
    
    return product

def extract_from_html_elements(soup):
    """Extract product information from HTML elements with more selectors"""
    product = {}
    
    # Extract product name
    name_selectors = ['#productTitle', '.product-title', '.product-name', 'h1.a-size-large']
    for selector in name_selectors:
        name_element = soup.select_one(selector)
        if name_element and name_element.text.strip():
            product['name'] = name_element.text.strip()
            break
    
    # Extract product price - try multiple selectors
    price_selectors = [
        '#priceblock_ourprice',
        '#priceblock_dealprice',
        '.a-price .a-offscreen',
        '.a-price',
        '.priceToPay',
        '.a-color-price',
        '#price',
        '[data-a-color="price"]'
    ]
    
    for selector in price_selectors:
        price_elements = soup.select(selector)
        for element in price_elements:
            if element:
                price_text = element.text.strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        price_str = price_match.group().replace(',', '')
                        product['price'] = float(price_str)
                        
                        # Get currency
                        if '₹' in price_text or 'Rs' in price_text:
                            product['currency'] = 'INR'
                        elif '$' in price_text:
                            product['currency'] = 'USD'
                        elif '€' in price_text:
                            product['currency'] = 'EUR'
                        elif '£' in price_text:
                            product['currency'] = 'GBP'
                        else:
                            product['currency'] = 'INR'  # Default for Indian store
                            
                        break
                    except (ValueError, AttributeError):
                        continue
            if 'price' in product:  # Break outer loop if price found
                break
    
    # Extract product image with multiple selectors
    image_selectors = [
        '#landingImage', 
        '#imgBlkFront', 
        '.a-dynamic-image', 
        '#main-image',
        '.product-image img',
        '.imgTagWrapper img'
    ]
    
    for selector in image_selectors:
        image_element = soup.select_one(selector)
        if image_element:
            # Try different attributes
            for attr in ['data-old-hires', 'data-a-dynamic-image', 'src']:
                if attr in image_element.attrs:
                    if attr == 'data-a-dynamic-image':
                        # This is a JSON string with URLs
                        try:
                            image_urls = json.loads(image_element[attr])
                            if image_urls and isinstance(image_urls, dict):
                                # Get the first URL (key)
                                product['image_url'] = list(image_urls.keys())[0]
                                break
                        except (json.JSONDecodeError, IndexError):
                            pass
                    else:
                        product['image_url'] = image_element[attr]
                        break
            
            if 'image_url' in product:
                break
    
    # Extract product description
    description_selectors = [
        '#productDescription', 
        '#feature-bullets', 
        '.product-description',
        '.aplus-module-wrapper'
    ]
    
    for selector in description_selectors:
        description_element = soup.select_one(selector)
        if description_element and description_element.text.strip():
            product['description'] = description_element.text.strip()
            break
    
    # Extract brand
    brand_selectors = [
        '.po-brand .a-span9',
        '.a-section .a-spacing-small:contains("Brand")',
        '#bylineInfo',
        '.product-by-line'
    ]
    
    for selector in brand_selectors:
        try:
            if selector.endswith('("Brand")'):
                # Handle contains selector
                brand_row = None
                for row in soup.select('.a-section .a-spacing-small'):
                    if 'Brand' in row.text:
                        brand_row = row
                        break
                
                if brand_row:
                    # Find the value part
                    value_element = brand_row.select_one('.a-span9')
                    if value_element:
                        product['brand'] = value_element.text.strip()
            else:
                # Regular selector
                brand_element = soup.select_one(selector)
                if brand_element:
                    brand_text = brand_element.text.strip()
                    # Clean up common prefixes
                    for prefix in ['Brand:', 'Visit the', 'Store']:
                        if brand_text.startswith(prefix):
                            brand_text = brand_text[len(prefix):].strip()
                    product['brand'] = brand_text
        except Exception:
            continue
        
        if 'brand' in product and product['brand']:
            break
    
    # Extract availability
    availability_selectors = [
        '#availability',
        '.availability',
        '#deliveryMessageMirId'
    ]
    
    for selector in availability_selectors:
        avail_element = soup.select_one(selector)
        if avail_element:
            avail_text = avail_element.text.strip().lower()
            if 'in stock' in avail_text:
                product['in_stock'] = True
            elif 'out of stock' in avail_text or 'unavailable' in avail_text:
                product['in_stock'] = False
            break
    
    return product

def extract_from_meta_tags(soup):
    """Extract product information from meta tags"""
    product = {}
    
    # Extract product name
    name_meta_selectors = [
        ('meta', {'property': 'og:title'}),
        ('meta', {'name': 'title'}),
        ('meta', {'itemprop': 'name'})
    ]
    
    for tag, attrs in name_meta_selectors:
        element = soup.find(tag, attrs)
        if element and 'content' in element.attrs and element['content'].strip():
            product['name'] = element['content'].strip()
            # Remove common Amazon suffixes
            for suffix in [" | Amazon.in", " | Amazon.com", " - Amazon"]:
                if product['name'].endswith(suffix):
                    product['name'] = product['name'][:-len(suffix)].strip()
            break
    
    # Extract product image
    image_meta_selectors = [
        ('meta', {'property': 'og:image'}),
        ('meta', {'itemprop': 'image'})
    ]
    
    for tag, attrs in image_meta_selectors:
        element = soup.find(tag, attrs)
        if element and 'content' in element.attrs and element['content'].strip():
            product['image_url'] = element['content'].strip()
            break
    
    # Extract product description
    desc_meta_selectors = [
        ('meta', {'property': 'og:description'}),
        ('meta', {'name': 'description'}),
        ('meta', {'itemprop': 'description'})
    ]
    
    for tag, attrs in desc_meta_selectors:
        element = soup.find(tag, attrs)
        if element and 'content' in element.attrs and element['content'].strip():
            product['description'] = element['content'].strip()
            break
    
    # Try to extract price from meta tags
    price_meta_selectors = [
        ('meta', {'itemprop': 'price'}),
        ('meta', {'property': 'product:price:amount'})
    ]
    
    for tag, attrs in price_meta_selectors:
        element = soup.find(tag, attrs)
        if element and 'content' in element.attrs:
            try:
                price_str = element['content'].replace(',', '')
                product['price'] = float(price_str)
                break
            except (ValueError, TypeError):
                pass
    
    # Extract currency
    currency_meta_selectors = [
        ('meta', {'itemprop': 'priceCurrency'}),
        ('meta', {'property': 'product:price:currency'})
    ]
    
    for tag, attrs in currency_meta_selectors:
        element = soup.find(tag, attrs)
        if element and 'content' in element.attrs:
            product['currency'] = element['content']
            break
    
    return product

def extract_name_from_url(url):
    """Extract a product name from URL"""
    if not url:
        return "Unknown Product"
        
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
    
    # If we still don't have a product name, use the product ID if available
    if not product_name:
        product_id = None
        for segment in parts:
            if segment.startswith('B0') and len(segment) >= 10:
                product_id = segment
                break
        
        if product_id:
            # Get domain for a more specific name
            domain = urlparse(url).netloc
            if 'amazon' in domain:
                return f"Amazon Product {product_id}"
            else:
                return f"Product {product_id}"
    
    return product_name or "Unknown Product"

# Keep mock data functions for development/testing only

def get_mock_product_data(url, existing_metadata=None, custom_product_name=None):
    """
    Generate mock product data for testing purposes
    This ensures the application can function even when scraping fails
    Only used in development mode when explicitly enabled
    
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
        
        mock_data['is_mock_data'] = True
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
    
    # Extract product ID from URL for a more specific fallback
    product_id = None
    for segment in url.split('/'):
        if segment.startswith('B0') and len(segment) >= 10:
            product_id = segment
            break
    
    # Extract keywords from URL segments
    url_keywords = []
    for segment in url.split('/'):
        if segment and segment not in ['www', 'http:', 'https:', 'com', 'in', 'org', 'net', 'dp', 'product', 'gp']:
            clean_segment = segment.replace('-', ' ').replace('_', ' ').replace('+', ' ')
            potential_keywords = [w for w in clean_segment.split() if len(w) > 3 and not w.startswith('B0')]
            url_keywords.extend(potential_keywords)
    
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
    else:
        category = "Product"
    
    # Use keywords to create a more specific name
    if url_keywords:
        keywords_str = ' '.join([k.capitalize() for k in url_keywords[:3]])
        name = f"{keywords_str} {category}"
    else:
        # Use product ID if available
        name = f"{category} {product_id}" if product_id else f"Unknown {category}"
    
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
        'is_mock_data': True
    }

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