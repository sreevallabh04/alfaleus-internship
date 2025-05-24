import re
from urllib.parse import urlparse, parse_qs

def normalize_amazon_url(url):
    """
    Normalize Amazon product URLs to a canonical format
    Returns the normalized URL with only the essential parts
    """
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Check if it's an Amazon URL
    if 'amazon' not in parsed_url.netloc:
        return url
    
    # Extract ASIN from URL
    asin = extract_amazon_asin(url)
    
    if asin:
        # Construct canonical URL with ASIN
        domain = parsed_url.netloc
        return f"https://{domain}/dp/{asin}"
    
    # If ASIN extraction fails, return the original URL
    return url

def extract_amazon_asin(url):
    """
    Extract ASIN (Amazon Standard Identification Number) from an Amazon URL
    Returns the ASIN if found, otherwise None
    """
    # Method 1: Extract from /dp/ or /gp/product/ path
    dp_pattern = r'/dp/([A-Z0-9]{10})'
    gp_pattern = r'/gp/product/([A-Z0-9]{10})'
    
    dp_match = re.search(dp_pattern, url)
    if dp_match:
        return dp_match.group(1)
    
    gp_match = re.search(gp_pattern, url)
    if gp_match:
        return gp_match.group(1)
    
    # Method 2: Extract from query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'ASIN' in query_params:
        return query_params['ASIN'][0]
    
    if 'asin' in query_params:
        return query_params['asin'][0]
    
    # Method 3: Look for ASIN in the path segments
    path_segments = parsed_url.path.split('/')
    for segment in path_segments:
        if re.match(r'^[A-Z0-9]{10}$', segment):
            return segment
    
    # ASIN not found
    return None
