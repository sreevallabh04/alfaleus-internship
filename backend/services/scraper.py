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
                
                # If we now have both name and price, we can proceed (but don't return yet)
                if 'name' in aggregated_data and 'price' in aggregated_data and 'extraction_method' not in aggregated_data:
                    aggregated_data['extraction_method'] = 'meta_tags'
                    logger.info("Successfully extracted name and price from meta tags")
            
            # Method 5: Extract from dynamic price API
            if product_id and ('price' not in aggregated_data or not aggregated_data['price']):
                logger.info("Trying to extract price from dynamic price API")
                dynamic_price = extract_from_dynamic_price_api(product_id, session, headers)
                if dynamic_price:
                    logger.info(f"Successfully extracted price from dynamic API: {dynamic_price}")
                    aggregated_data['price'] = dynamic_price
                    aggregated_data['currency'] = 'INR'
                    if 'extraction_method' not in aggregated_data:
                        aggregated_data['extraction_method'] = 'dynamic_price_api'
            
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
                
                # Extract key features/bullet points if not already present
                if 'key_features' not in aggregated_data or not aggregated_data['key_features']:
                    features = extract_key_features(soup)
                    if features:
                        aggregated_data['key_features'] = features
                        logger.info(f"Extracted {len(features)} key features")
                
                # Make sure we have an image URL (very important for UI)
                if 'image_url' not in aggregated_data or not aggregated_data['image_url']:
                    logger.warning("No image URL found - trying additional methods")
                    # Check for image in Open Graph tags as last resort
                    og_image = soup.find('meta', {'property': 'og:image'})
                    if og_image and 'content' in og_image.attrs:
                        aggregated_data['image_url'] = og_image['content'].strip()
                        logger.info("Found image URL in Open Graph tags")
                
                # Set price to null if not found (instead of omitting the field)
                if 'price' not in aggregated_data:
                    aggregated_data['price'] = None
                    aggregated_data['currency'] = 'INR'  # Default currency
                    logger.warning("Price data not found, setting to null")
                
                # Add extraction attempt information
                aggregated_data['extraction_method'] = 'combined'
                aggregated_data['extraction_attempts'] = attempt + 1
                
                # If we have the product ID from the URL, add it for verification
                if product_id:
                    aggregated_data['product_id'] = product_id
                
                # Add URL to the data
                aggregated_data['url'] = url
                
                # Add detailed error message if partial data
                if ('price' not in aggregated_data or not aggregated_data['price'] or 
                    'image_url' not in aggregated_data or not aggregated_data['image_url']):
                    aggregated_data['scraping_warning'] = "Some product data could not be extracted. Amazon may be limiting access."
                
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
    
    # Last resort: Try more aggressive approach to get product data
    if product_id:
        logger.warning("All standard scraping attempts failed, trying aggressive fallback methods")
        
        # Try a direct product page with mobile user agent
        try:
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
            
            # Try the mobile version of the site
            mobile_url = f"https://www.amazon.in/gp/aw/d/{product_id}"
            logger.info(f"Trying mobile URL: {mobile_url}")
            
            mobile_response = requests.get(mobile_url, headers=mobile_headers, timeout=10)
            if mobile_response.status_code == 200:
                mobile_soup = BeautifulSoup(mobile_response.content, 'html.parser')
                
                # Look for product title in mobile version
                mobile_title = mobile_soup.select_one('#title, .a-text-normal')
                if mobile_title and mobile_title.text.strip():
                    product_name = mobile_title.text.strip()
                    logger.info(f"Successfully extracted product name from mobile site: {product_name}")
                    
                    # Try to get image and price
                    mobile_image = mobile_soup.select_one('img.a-dynamic-image, #landingImage')
                    mobile_price = mobile_soup.select_one('.a-price, .a-color-price')
                    
                    result = {
                        'name': product_name,
                        'description': f"Product details for {product_name}",
                        'url': url,
                        'product_id': product_id,
                        'extraction_method': 'mobile_site_fallback'
                    }
                    
                    if mobile_image and 'src' in mobile_image.attrs:
                        result['image_url'] = mobile_image['src']
                    
                    if mobile_price and mobile_price.text.strip():
                        price_text = mobile_price.text.strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            try:
                                result['price'] = float(price_match.group().replace(',', ''))
                                result['currency'] = 'INR'
                            except (ValueError, AttributeError):
                                result['price'] = None
                    
                    return result
        except Exception as e:
            logger.error(f"Error in mobile site fallback: {str(e)}")
        
        # Try direct API access as a last resort
        try:
            api_url = f"https://www.amazon.in/hz/ajax/render/dpMobileWeb?deviceType=web&asin={product_id}"
            api_headers = get_enhanced_headers()
            api_headers['X-Requested-With'] = 'XMLHttpRequest'
            
            logger.info(f"Trying API URL: {api_url}")
            api_response = requests.get(api_url, headers=api_headers, timeout=15)
            
            if api_response.status_code == 200 and api_response.text:
                # Try to extract JSON data
                try:
                    api_data = json.loads(api_response.text)
                    if 'dpHtml' in api_data:
                        api_soup = BeautifulSoup(api_data['dpHtml'], 'html.parser')
                        api_title = api_soup.select_one('#title, .a-text-normal, .product-title')
                        
                        if api_title and api_title.text.strip():
                            product_name = api_title.text.strip()
                            logger.info(f"Successfully extracted product name from API: {product_name}")
                            
                            result = {
                                'name': product_name,
                                'description': f"Product details for {product_name}",
                                'url': url,
                                'product_id': product_id,
                                'extraction_method': 'api_fallback'
                            }
                            
                            # Try to get price
                            api_price = api_soup.select_one('.a-price, .a-color-price')
                            if api_price and api_price.text.strip():
                                price_text = api_price.text.strip()
                                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                                if price_match:
                                    try:
                                        result['price'] = float(price_match.group().replace(',', ''))
                                        result['currency'] = 'INR'
                                    except (ValueError, AttributeError):
                                        result['price'] = None
                            
                            return result
                except json.JSONDecodeError:
                    logger.error("Failed to parse API response as JSON")
        except Exception as e:
            logger.error(f"Error in API fallback: {str(e)}")
            
        # If we still don't have product data, try another approach with different headers
        try:
            # Completely different user agent and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Sec-Ch-Ua': '"Microsoft Edge";v="124", "Chromium";v="124", "Not-A.Brand";v="99"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Try different URL pattern
            direct_url = f"https://www.amazon.in/dp/{product_id}/"
            logger.info(f"Trying final attempt with URL: {direct_url}")
            
            response = requests.get(direct_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Check title tag at minimum
                title_tag = soup.title
                if title_tag and title_tag.string:
                    title_text = title_tag.string.strip()
                    # Remove common Amazon suffixes
                    for suffix in [" | Amazon.in", " | Amazon.com", " - Amazon", "Amazon.in", "Amazon.com"]:
                        if title_text.endswith(suffix):
                            title_text = title_text[:-len(suffix)].strip()
                    
                    if title_text and len(title_text) > 5 and title_text != f"Amazon.in: {product_id}":
                        logger.info(f"Extracted product name from title tag: {title_text}")
                        
                        result = {
                            'name': title_text,
                            'description': f"Product details for {title_text}",
                            'url': url,
                            'product_id': product_id,
                            'extraction_method': 'title_tag_fallback',
                            'price': None,
                            'currency': 'INR'
                        }
                        
                        return result
        except Exception as e:
            logger.error(f"Error in final fallback attempt: {str(e)}")
    
    # If we get here, truly nothing worked - return a clear error
    logger.error(f"Complete failure to extract any product data from {url}")
    
    # Instead of returning "Amazon Product {ASIN}", return a clear error
    return {
        'scraping_failed': True,
        'url': url,
        'error': 'Unable to extract product name from Amazon. Their anti-bot measures might be active.',
        'is_real_data': False,
        'product_id': product_id
    }

def get_enhanced_headers():
    """
    Generate enhanced headers with browser fingerprinting for better Amazon scraping
    """
    cookies = {
        'session-id': f"{random.randint(100000000, 999999999)}",
        'session-token': f"random{random.randint(10000, 99999)}",
        'ubid-acbin': f"{random.randint(250, 300)}-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}",
        'csm-hit': f"tb:{random.randint(10000000000000000000, 99999999999999999999)}+s-{random.randint(10000000000000000000, 99999999999999999999)}|{int(time.time()*1000)}",
    }
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Chromium";v="124", "Not)A;Brand";v="24", "Google Chrome";v="124"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Priority': 'u=0, i',
        'Dnt': '1',
        'Cookie': '; '.join([f"{k}={v}" for k, v in cookies.items()])
    }
    
    return headers

def extract_from_price_data_script(soup, product_id):
    """
    Extract product price from Amazon's price data script
    This is often found in a script containing pricing data
    """
    try:
        price_data = {}
        
        # Look for price data in scripts
        for script in soup.find_all('script'):
            script_text = script.string
            if not script_text:
                continue
                
            # Check for price data patterns
            if 'priceData' in script_text or 'aodPreredirect' in script_text:
                logger.info("Found price data script")
                
                # Try to extract price
                price_match = re.search(r'"displayPrice":\s*"([^"]+)"', script_text)
                if price_match:
                    price_text = price_match.group(1)
                    # Extract numeric price
                    price_value_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_value_match:
                        try:
                            price_str = price_value_match.group().replace(',', '')
                            price_data['price'] = float(price_str)
                            price_data['currency'] = 'INR' if '₹' in price_text or 'Rs' in price_text else 'USD'
                            logger.info(f"Extracted price from price data script: {price_data['price']} {price_data['currency']}")
                        except (ValueError, AttributeError) as e:
                            logger.warning(f"Error parsing price from script: {str(e)}")
                
                # Try to extract product title
                title_match = re.search(r'"productTitle":\s*"([^"]+)"', script_text)
                if title_match:
                    price_data['name'] = title_match.group(1)
                    logger.info(f"Extracted title from price data script: {price_data['name']}")
                
                # Try to extract image URL
                image_match = re.search(r'"imageUrl":\s*"([^"]+)"', script_text)
                if image_match:
                    price_data['image_url'] = image_match.group(1)
                    logger.info(f"Extracted image URL from price data script")
                
                # If we found something useful, return it
                if price_data:
                    return price_data
            
            # Check for another format of price data
            if 'twister-js-init-dpx-data' in script_text:
                logger.info("Found twister data script")
                
                # Try to extract ASIN-specific data if product_id is provided
                if product_id:
                    asin_data_match = re.search(rf'"{product_id}":\s*(\{{[^{{}}]*\}})', script_text)
                    if asin_data_match:
                        try:
                            # This is often malformed JSON, so we need to clean it up
                            asin_data_text = asin_data_match.group(1)
                            # Add quotes around keys to make it valid JSON
                            asin_data_text = re.sub(r'([{,])\s*(\w+):', r'\1"\2":', asin_data_text)
                            asin_data = json.loads(asin_data_text)
                            
                            if 'price' in asin_data:
                                price_text = asin_data['price']
                                # Extract numeric price
                                price_value_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                                if price_value_match:
                                    price_str = price_value_match.group().replace(',', '')
                                    price_data['price'] = float(price_str)
                                    price_data['currency'] = 'INR' if '₹' in price_text or 'Rs' in price_text else 'USD'
                                    logger.info(f"Extracted price from twister data: {price_data['price']} {price_data['currency']}")
                        except (json.JSONDecodeError, ValueError) as e:
                            logger.warning(f"Error parsing twister data: {str(e)}")
    except Exception as e:
        logger.error(f"Error extracting from price data script: {str(e)}")
    
    return price_data

def extract_from_dynamic_price_api(product_id, session, headers):
    """
    Extract price from Amazon's dynamic price API with enhanced reliability
    Uses multiple API endpoints and consensus checking for increased accuracy
    """
    if not product_id:
        return None
        
    try:
        # Use a comprehensive set of API URLs with varying formats for better coverage
        api_urls = [
            # Standard product offer display AJAX endpoint
            f"https://www.amazon.in/gp/product/ajax/ref=dp_aod_unknown_mbc?asin={product_id}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp",
            
            # All offers display AJAX endpoint
            f"https://www.amazon.in/gp/aod/ajax/ref=aod_page_1?asin={product_id}&pc=dp",
            
            # Price block display API
            f"https://www.amazon.in/gp/product/ajax/price-load/ref=dp_price_load?asin={product_id}",
            
            # Mobile web render API
            f"https://www.amazon.in/hz/ajax/render/dpMobileWeb?deviceType=web&asin={product_id}&refTag=spkl_1_spkl",
            
            # Price calculation API
            f"https://www.amazon.in/twister/api/priceCalculation?asin={product_id}&deviceType=web&exp=desktop-twister-prices",
            
            # Deals API that sometimes contains price info
            f"https://www.amazon.in/gp/deals/ajax/get-all-deals?asin={product_id}",
            
            # Buy box API
            f"https://www.amazon.in/gp/product/ajax/buybox/ref=dp_buybox?asin={product_id}"
        ]
        
        # Track all collected prices for consensus analysis
        collected_prices = []
        
        for api_url in api_urls:
            try:
                logger.info(f"Trying dynamic price API: {api_url}")
                
                # Add specific headers for AJAX request, varying by endpoint
                ajax_headers = headers.copy() if headers else get_enhanced_headers()
                ajax_headers['X-Requested-With'] = 'XMLHttpRequest'
                ajax_headers['Referer'] = f"https://www.amazon.in/dp/{product_id}"
                
                # Add some additional headers to appear more like a regular browser
                if 'twister' in api_url:
                    ajax_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
                    ajax_headers['Content-Type'] = 'application/json'
                else:
                    ajax_headers['Accept'] = 'text/html, */*; q=0.01'
                
                # Add random cookies to appear more like a real browser session
                cookies = {
                    'session-id': f"{random.randint(100000000, 999999999)}",
                    'session-token': f"random{random.randint(10000, 99999)}",
                    'ubid-acbin': f"{random.randint(250, 300)}-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}",
                    'csm-hit': f"tb:{random.randint(10000000000000000000, 99999999999999999999)}+s-{random.randint(10000000000000000000, 99999999999999999999)}|{int(time.time()*1000)}",
                }
                ajax_headers['Cookie'] = '; '.join([f"{k}={v}" for k, v in cookies.items()])
                
                # Add a small delay to avoid rate limiting
                time.sleep(random.uniform(0.5, 1.5))
                
                # Increase timeout for potentially slow API responses
                response = session.get(api_url, headers=ajax_headers, timeout=15)
                
                # Log response details for debugging
                logger.debug(f"API response status: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}, Length: {len(response.text)}")
                
                if response.status_code == 200:
                    # First, try to parse as JSON if it looks like JSON
                    if 'application/json' in response.headers.get('Content-Type', '') or response.text.strip().startswith('{'):
                        try:
                            json_data = response.json()
                            logger.debug(f"Successfully parsed JSON response from {api_url}")
                            
                            # Process JSON response for price information
                            if isinstance(json_data, dict):
                                # Check various JSON structures that might contain price
                                
                                # 1. Direct price fields
                                price_fields = ['priceAmount', 'price', 'buyingPrice', 'displayPrice', 'salePrice', 'amount']
                                for field in price_fields:
                                    if field in json_data:
                                        if isinstance(json_data[field], (int, float)):
                                            price_value = float(json_data[field])
                                            if 100 <= price_value <= 500000:  # Reasonable price range
                                                logger.info(f"Extracted price from JSON field '{field}': ₹{price_value}")
                                                collected_prices.append(('json_direct_field', price_value))
                                                break
                                        elif isinstance(json_data[field], str):
                                            # Handle string with currency symbol or formatting
                                            price_match = re.search(r'[\d,]+\.?\d*', json_data[field].replace(',', ''))
                                            if price_match:
                                                try:
                                                    price_value = float(price_match.group().replace(',', ''))
                                                    if 100 <= price_value <= 500000:
                                                        logger.info(f"Extracted price from JSON string field '{field}': ₹{price_value}")
                                                        collected_prices.append(('json_string_field', price_value))
                                                        break
                                                except (ValueError, AttributeError):
                                                    pass
                                
                                # 2. Look for nested price objects
                                if 'offers' in json_data and isinstance(json_data['offers'], list) and json_data['offers']:
                                    for offer in json_data['offers']:
                                        if isinstance(offer, dict) and 'price' in offer:
                                            if isinstance(offer['price'], (int, float)):
                                                price_value = float(offer['price'])
                                                if 100 <= price_value <= 500000:
                                                    logger.info(f"Extracted price from offers array: ₹{price_value}")
                                                    collected_prices.append(('offers_array', price_value))
                                                    break
                                            elif isinstance(offer['price'], str):
                                                price_match = re.search(r'[\d,]+\.?\d*', offer['price'].replace(',', ''))
                                                if price_match:
                                                    try:
                                                        price_value = float(price_match.group().replace(',', ''))
                                                        if 100 <= price_value <= 500000:
                                                            logger.info(f"Extracted price from offers array string: ₹{price_value}")
                                                            collected_prices.append(('offers_array_string', price_value))
                                                            break
                                                    except (ValueError, AttributeError):
                                                        pass
                                
                                # 3. Deep search for any field containing price information
                                def search_json_for_prices(obj, path=""):
                                    if isinstance(obj, dict):
                                        for key, value in obj.items():
                                            # Check for price-related field names
                                            if any(price_term in key.lower() for price_term in ['price', 'cost', 'amount', 'value']):
                                                if isinstance(value, (int, float)) and 100 <= value <= 500000:
                                                    logger.info(f"Found price in nested JSON at {path}.{key}: ₹{value}")
                                                    collected_prices.append(('nested_json', value))
                                                elif isinstance(value, str):
                                                    price_match = re.search(r'[\d,]+\.?\d*', value.replace(',', ''))
                                                    if price_match:
                                                        try:
                                                            price_value = float(price_match.group().replace(',', ''))
                                                            if 100 <= price_value <= 500000:
                                                                logger.info(f"Found price in nested JSON string at {path}.{key}: ₹{price_value}")
                                                                collected_prices.append(('nested_json_string', price_value))
                                                        except (ValueError, AttributeError):
                                                            pass
                                            # Recursively search nested objects
                                            search_json_for_prices(value, f"{path}.{key}" if path else key)
                                    elif isinstance(obj, list):
                                        for i, item in enumerate(obj):
                                            search_json_for_prices(item, f"{path}[{i}]")
                                
                                # Start recursive price search for complex JSON responses
                                search_json_for_prices(json_data)
                                
                                # 4. Check for HTML in dpHtml field (mobile web render)
                                if 'dpHtml' in json_data and isinstance(json_data['dpHtml'], str):
                                    html_soup = BeautifulSoup(json_data['dpHtml'], 'html.parser')
                                    # Search for price elements within the HTML
                                    extract_prices_from_html(html_soup, 'dpHtml_content', collected_prices)
                        except json.JSONDecodeError:
                            logger.debug(f"Response from {api_url} is not valid JSON")
                    
                    # Process HTML responses
                    soup = BeautifulSoup(response.content, 'html.parser')
                    extract_prices_from_html(soup, api_url, collected_prices)
                    
            except Exception as e:
                logger.warning(f"Error with dynamic price API URL {api_url}: {str(e)}")
                continue
        
        # Analyze collected prices and return the most reliable one
        if collected_prices:
            # Log all collected prices for debugging
            logger.info(f"Collected {len(collected_prices)} price points: {[price for _, price in collected_prices]}")
            
            # If we have multiple prices, look for consensus
            if len(collected_prices) > 1:
                # Group by price value and count occurrences
                price_counts = {}
                for _, price in collected_prices:
                    # Round to nearest rupee to handle minor floating point differences
                    rounded_price = round(price)
                    price_counts[rounded_price] = price_counts.get(rounded_price, 0) + 1
                
                # Sort by frequency (most common first)
                sorted_prices = sorted(price_counts.items(), key=lambda x: x[1], reverse=True)
                most_common_price = sorted_prices[0][0]
                
                logger.info(f"Selected most common price: ₹{most_common_price} (appeared {sorted_prices[0][1]} times)")
                return float(most_common_price)
            else:
                # If only one price, return it
                source, price = collected_prices[0]
                logger.info(f"Using single price from {source}: ₹{price}")
                return price
                
    except Exception as e:
        logger.error(f"Error extracting from dynamic price API: {str(e)}")
    
    return None

def extract_prices_from_html(soup, source_info, collected_prices):
    """
    Helper function to extract prices from HTML content
    Used by the dynamic price API function
    """
    # Check for price elements with multiple selectors
    price_selectors = [
        '.a-price .a-offscreen',
        '.a-color-price',
        '.a-price',
        '.a-text-price',
        '.priceToPay',
        '[data-feature-name="priceInsideBuyBox"]',
        '.offer-price',
        '.a-price-whole',
        '#priceblock_ourprice',
        '#priceblock_dealprice'
    ]
    
    for selector in price_selectors:
        price_elements = soup.select(selector)
        for element in price_elements:
            price_text = element.text.strip()
            
            # Skip elements that clearly aren't prices
            if len(price_text) < 2 or not re.search(r'[\d\.,₹$£€]', price_text):
                continue
                
            # Enhanced price extraction for rupees
            if '₹' in price_text:
                price_match = re.search(r'₹\s*([\d,]+\.?\d*)', price_text)
                if price_match:
                    try:
                        price_value = float(price_match.group(1).replace(',', ''))
                        if 100 <= price_value <= 500000:
                            logger.info(f"Extracted ₹ price from {selector} in {source_info}: ₹{price_value}")
                            collected_prices.append((f'html_{selector}', price_value))
                            return  # Return after finding first valid price
                    except (ValueError, AttributeError):
                        continue
            else:
                # General pattern for numbers
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        price_value = float(price_match.group().replace(',', ''))
                        if 100 <= price_value <= 500000:
                            logger.info(f"Extracted price from {selector} in {source_info}: ₹{price_value}")
                            collected_prices.append((f'html_{selector}', price_value))
                            return  # Return after finding first valid price
                    except (ValueError, AttributeError):
                        continue
    
    # Look for text nodes containing price indicators
    price_indicators = ['₹', 'Rs.', 'Rs ', 'INR', 'Price:', 'MRP:']
    for indicator in price_indicators:
        price_texts = [text for text in soup.stripped_strings if indicator in text]
        for price_text in price_texts:
            if '₹' in price_text:
                price_match = re.search(r'₹\s*([\d,]+\.?\d*)', price_text)
                if price_match:
                    try:
                        price_value = float(price_match.group(1).replace(',', ''))
                        if 100 <= price_value <= 500000:
                            logger.info(f"Extracted price from text node in {source_info}: ₹{price_value}")
                            collected_prices.append(('text_node', price_value))
                            return  # Return after finding first valid price
                    except (ValueError, AttributeError):
                        continue
            else:
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        price_value = float(price_match.group().replace(',', ''))
                        if 100 <= price_value <= 500000:
                            logger.info(f"Extracted general price from text node in {source_info}: ₹{price_value}")
                            collected_prices.append(('text_node', price_value))
                            return  # Return after finding first valid price
                    except (ValueError, AttributeError):
                        continue

def extract_key_features(soup):
    """
    Extract key features (bullet points) from Amazon product page
    """
    features = []
    try:
        # Try multiple selectors for feature bullets
        bullet_selectors = [
            '#feature-bullets ul li:not(.aok-hidden) span.a-list-item',
            '#feature-bullets .a-unordered-list .a-list-item',
            '.a-unordered-list .a-list-item:not(.aok-hidden)',
            '.feature-bullets .a-list-item'
        ]
        
        for selector in bullet_selectors:
            bullet_elements = soup.select(selector)
            if bullet_elements:
                for element in bullet_elements:
                    feature_text = element.text.strip()
                    # Skip empty features or known non-feature text
                    if (feature_text and 
                        len(feature_text) > 5 and 
                        not feature_text.startswith('Make sure') and
                        not 'this fits' in feature_text.lower()):
                        features.append(feature_text)
                
                # If we found some features, no need to try other selectors
                if features:
                    break
        
        # Limit to a reasonable number of features
        if len(features) > 5:
            features = features[:5]
            
        return features
    except Exception as e:
        logger.error(f"Error extracting key features: {str(e)}")
        return []

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
    
    # ENHANCED: More comprehensive price extraction with priority and validation
    # First, try to find the primary price with high precision selectors
    primary_price_selectors = [
        '.priceToPay .a-offscreen',  # Amazon's current primary price selector
        '.priceToPay span.a-price-whole',  # Whole number part
        '#priceblock_ourprice',  # Classic price block
        '#priceblock_dealprice',  # Deal price
        '.a-price[data-a-color="price"] .a-offscreen',  # Current price format
        'span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay',  # Mobile format
        '#corePrice_desktop .a-offscreen',  # Desktop core price
        '#apex_desktop .a-color-price'  # Apex price display
    ]
    
    found_price = False
    price_sources = []
    
    # Step 1: Try primary high-confidence selectors first
    for selector in primary_price_selectors:
        price_elements = soup.select(selector)
        for element in price_elements:
            if element:
                price_text = element.text.strip()
                logger.debug(f"Found potential price text from {selector}: {price_text}")
                
                # Skip elements that clearly aren't prices
                if len(price_text) < 2 or not re.search(r'[\d\.,₹$£€]', price_text):
                    continue
                    
                # More precise pattern matching for rupees (₹) specifically
                if '₹' in price_text:
                    price_match = re.search(r'₹\s*([\d,]+\.?\d*)', price_text)
                    if price_match:
                        try:
                            price_str = price_match.group(1).replace(',', '')
                            price_value = float(price_str)
                            # Only accept reasonable prices (₹100 to ₹500,000)
                            if 100 <= price_value <= 500000:
                                price_sources.append(('primary_selector', price_value, 'INR', selector))
                                found_price = True
                                logger.info(f"Extracted primary INR price: ₹{price_value} from {selector}")
                        except (ValueError, AttributeError) as e:
                            logger.debug(f"Failed to parse INR price from {price_text}: {str(e)}")
                
                # General pattern for all currencies
                else:
                    # Match any number that might be a price
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        try:
                            price_str = price_match.group().replace(',', '')
                            price_value = float(price_str)
                            
                            # Determine currency and validate price range
                            if '₹' in price_text or 'Rs' in price_text or 'INR' in price_text:
                                currency = 'INR'
                                valid_price = 100 <= price_value <= 500000
                            elif '$' in price_text:
                                currency = 'USD'
                                valid_price = 1 <= price_value <= 10000
                            elif '€' in price_text:
                                currency = 'EUR'
                                valid_price = 1 <= price_value <= 10000
                            elif '£' in price_text:
                                currency = 'GBP'
                                valid_price = 1 <= price_value <= 10000
                            else:
                                # Default to INR for Indian Amazon
                                currency = 'INR'
                                valid_price = 100 <= price_value <= 500000
                            
                            if valid_price:
                                price_sources.append(('primary_selector', price_value, currency, selector))
                                found_price = True
                                logger.info(f"Extracted primary price: {price_value} {currency} from {selector}")
                        except (ValueError, AttributeError) as e:
                            logger.debug(f"Failed to parse price from {price_text}: {str(e)}")
    
    # Step 2: If no price found yet, try secondary selectors (less reliable)
    if not found_price:
        secondary_price_selectors = [
            '.a-color-price',
            '[data-a-color="price"]',
            '#price',
            '.a-price',
            '.price-section',
            '.offer-price',
            '.price'
        ]
        
        for selector in secondary_price_selectors:
            price_elements = soup.select(selector)
            for element in price_elements:
                if element:
                    price_text = element.text.strip()
                    logger.debug(f"Found potential secondary price text from {selector}: {price_text}")
                    
                    # Skip elements that clearly aren't prices
                    if len(price_text) < 2 or not re.search(r'[\d\.,₹$£€]', price_text):
                        continue
                    
                    # Enhanced pattern matching
                    if '₹' in price_text:
                        price_match = re.search(r'₹\s*([\d,]+\.?\d*)', price_text)
                    else:
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    
                    if price_match:
                        try:
                            if '₹' in price_text:
                                price_str = price_match.group(1).replace(',', '')
                            else:
                                price_str = price_match.group().replace(',', '')
                                
                            price_value = float(price_str)
                            
                            # Determine currency
                            if '₹' in price_text or 'Rs' in price_text or 'INR' in price_text:
                                currency = 'INR'
                                valid_price = 100 <= price_value <= 500000
                            elif '$' in price_text:
                                currency = 'USD'
                                valid_price = 1 <= price_value <= 10000
                            elif '€' in price_text:
                                currency = 'EUR'
                                valid_price = 1 <= price_value <= 10000
                            elif '£' in price_text:
                                currency = 'GBP'
                                valid_price = 1 <= price_value <= 10000
                            else:
                                # For Indian site, default to INR
                                currency = 'INR'
                                valid_price = 100 <= price_value <= 500000
                            
                            if valid_price:
                                price_sources.append(('secondary_selector', price_value, currency, selector))
                                found_price = True
                                logger.info(f"Extracted secondary price: {price_value} {currency} from {selector}")
                        except (ValueError, AttributeError) as e:
                            logger.debug(f"Failed to parse secondary price from {price_text}: {str(e)}")
    
    # Step 3: Check for prices in the text nodes that might contain price information
    if not found_price:
        # Look for text nodes containing price indicators
        price_indicators = ['₹', 'Rs.', 'Rs ', 'INR', 'Price:', 'MRP:']
        for indicator in price_indicators:
            price_texts = [text for text in soup.stripped_strings if indicator in text]
            for price_text in price_texts:
                logger.debug(f"Found potential price text from text node: {price_text}")
                
                # Enhanced pattern matching for rupees
                if '₹' in price_text:
                    price_match = re.search(r'₹\s*([\d,]+\.?\d*)', price_text)
                    if price_match:
                        try:
                            price_str = price_match.group(1).replace(',', '')
                            price_value = float(price_str)
                            if 100 <= price_value <= 500000:  # Reasonable price range in INR
                                price_sources.append(('text_node', price_value, 'INR', 'text_content'))
                                found_price = True
                                logger.info(f"Extracted text node INR price: ₹{price_value}")
                        except (ValueError, AttributeError):
                            continue
                # General pattern for all currencies
                else:
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        try:
                            price_str = price_match.group().replace(',', '')
                            price_value = float(price_str)
                            
                            # Determine currency
                            if 'Rs.' in price_text or 'Rs ' in price_text or 'INR' in price_text:
                                currency = 'INR'
                                valid_price = 100 <= price_value <= 500000
                            else:
                                # Default to INR for Indian Amazon
                                currency = 'INR'
                                valid_price = 100 <= price_value <= 500000
                            
                            if valid_price:
                                price_sources.append(('text_node', price_value, currency, 'text_content'))
                                found_price = True
                                logger.info(f"Extracted text node price: {price_value} {currency}")
                        except (ValueError, AttributeError):
                            continue
    
    # Now determine the final price based on all sources collected
    if price_sources:
        # Sort by source reliability (primary > secondary > text_node)
        price_sources.sort(key=lambda x: 0 if x[0] == 'primary_selector' else 1 if x[0] == 'secondary_selector' else 2)
        
        # Use the most reliable price
        source_type, price_value, currency, selector = price_sources[0]
        product['price'] = price_value
        product['currency'] = currency
        product['price_source'] = f"{source_type}:{selector}"
        
        logger.info(f"Final selected price: {price_value} {currency} from {source_type}:{selector}")
    else:
        logger.warning("No valid price found using any selectors")
    
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
        brand = "Unknown Brand"
        
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
            mock_data['brand'] = "Unknown Brand"
        
        mock_data['is_mock_data'] = True
        logger.info(f"Generated enhanced mock data from existing metadata for: {mock_data.get('name')}")
        return mock_data
    
    # Try to extract a meaningful name from the URL
    url_name = extract_name_from_url(url)
    if url_name:
        logger.info(f"Extracted product name from URL: {url_name}")
        name = url_name
        
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
    
    brand = "Unknown Brand"
    
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