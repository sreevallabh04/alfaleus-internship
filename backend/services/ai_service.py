import os
import logging
import requests
import json
from datetime import datetime
from services.scraper import scrape_product
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def extract_product_metadata(url):
    """
    Extract product metadata using AI or scraping
    Returns a dictionary with product details
    """
    try:
        # First try to scrape the product directly
        product_data = scrape_product(url)
        
        if not product_data or 'name' not in product_data:
            logger.warning(f"Failed to scrape product data from {url}")
            return None
        
        # If we have Groq API key, enhance the metadata
        if GROQ_API_KEY:
            enhanced_metadata = enhance_metadata_with_groq(product_data)
            if enhanced_metadata:
                return enhanced_metadata
        # Fallback to OpenAI if available
        elif OPENAI_API_KEY:
            enhanced_metadata = enhance_metadata_with_openai(product_data)
            if enhanced_metadata:
                return enhanced_metadata
        
        # Return the scraped data as fallback
        metadata = {
            'name': product_data.get('name', ''),
            'brand': extract_brand_from_name(product_data.get('name', '')),
            'description': product_data.get('description', ''),
            'price': product_data.get('price'),
            'currency': product_data.get('currency', 'INR'),
            'image_url': product_data.get('image_url', '')
        }
        
        return metadata
    except Exception as e:
        logger.error(f"Error extracting product metadata: {str(e)}")
        return None

def enhance_metadata_with_groq(product_data):
    """
    Use Groq API to enhance product metadata
    """
    if not GROQ_API_KEY:
        return None
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GROQ_API_KEY}'
        }
        
        # Make prompt more explicit about returning valid JSON
        prompt = f"""
        Extract detailed product metadata from this information:
        
        Product Name: {product_data.get('name', '')}
        Description: {product_data.get('description', '')}
        
        Return a valid JSON object with the following fields:
        - name: The full product name
        - brand: The brand name
        - model: The model number or name
        - category: The product category
        - key_features: A list of key features (up to 3)
        
        IMPORTANT: Your response must be ONLY a valid JSON object, with no additional text, explanations, or formatting.
        """
        
        data = {
            'model': 'llama3-8b-8192',  # Groq's LLaMA 3 model
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that extracts structured product metadata as valid JSON only.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,  # Lower temperature for more consistent formatting
            'max_tokens': 500,
            'response_format': {'type': 'json_object'}  # Request JSON format if supported
        }
        
        # Groq's API is compatible with OpenAI's API
        response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Validate AI response before parsing
        if not ai_response or not ai_response.strip():
            logger.warning("Empty response from Groq AI")
            return None
        
        # Try to parse the JSON response
        try:
            # Clean the response before parsing
            cleaned_response = sanitize_json_string(ai_response)
            metadata = json.loads(cleaned_response)
            
            logger.info(f"Successfully parsed Groq AI response for product: {metadata.get('name', 'Unknown')}")
            
            # Add the original price and image
            metadata['price'] = product_data.get('price')
            metadata['currency'] = product_data.get('currency', 'INR')
            metadata['image_url'] = product_data.get('image_url', '')
            
            return metadata
        except json.JSONDecodeError as json_err:
            # Log detailed error and truncated response for debugging
            truncated_response = ai_response[:500] + '...' if len(ai_response) > 500 else ai_response
            logger.warning(f"Failed to parse Groq AI response as JSON: {str(json_err)}")
            logger.debug(f"Raw response content (truncated): {truncated_response}")
            
            # Fallback to base metadata from product_data
            logger.info("Using fallback metadata from scraped product data")
            return {
                'name': product_data.get('name', ''),
                'brand': extract_brand_from_name(product_data.get('name', '')),
                'description': product_data.get('description', ''),
                'price': product_data.get('price'),
                'currency': product_data.get('currency', 'INR'),
                'image_url': product_data.get('image_url', ''),
                'category': guess_product_category(product_data.get('name', ''), product_data.get('description', '')),
                'key_features': []
            }
    except Exception as e:
        logger.error(f"Error enhancing metadata with Groq AI: {str(e)}")
        return None

def sanitize_json_string(json_str):
    """
    Clean and sanitize a string that should contain JSON to help with parsing
    """
    if not json_str:
        return '{}'
        
    # Remove any markdown code block markers
    json_str = json_str.replace('```json', '').replace('```', '')
    
    # Trim whitespace
    json_str = json_str.strip()
    
    # Make sure it starts with { and ends with }
    if not json_str.startswith('{'):
        start_idx = json_str.find('{')
        if start_idx >= 0:
            json_str = json_str[start_idx:]
        else:
            return '{}'
            
    if not json_str.endswith('}'):
        end_idx = json_str.rfind('}')
        if end_idx >= 0:
            json_str = json_str[:end_idx+1]
        else:
            return '{}'
    
    return json_str

def guess_product_category(name, description):
    """
    Guess a product category based on name and description
    Used as fallback when AI categorization fails
    """
    name_lower = (name or '').lower()
    desc_lower = (description or '').lower()
    combined = name_lower + ' ' + desc_lower
    
    category_keywords = {
        'Electronics': ['phone', 'laptop', 'computer', 'tv', 'headphone', 'camera', 'tablet'],
        'Fashion': ['shirt', 'pant', 'dress', 'shoe', 'clothing', 'apparel', 'fashion'],
        'Home & Kitchen': ['kitchen', 'furniture', 'bed', 'sofa', 'chair', 'table', 'appliance'],
        'Health & Personal Care': ['health', 'vitamin', 'supplement', 'protein', 'personal care'],
        'Beauty': ['beauty', 'makeup', 'cosmetic', 'skin care', 'hair care'],
        'Grocery': ['food', 'grocery', 'snack', 'beverage', 'drink'],
        'Sports & Fitness': ['sport', 'fitness', 'exercise', 'gym', 'yoga', 'workout']
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in combined for keyword in keywords):
            return category
    
    return "General"

def enhance_metadata_with_openai(product_data):
    """
    Use OpenAI API to enhance product metadata (fallback)
    """
    if not OPENAI_API_KEY:
        return None
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        
        prompt = f"""
        Extract detailed product metadata from this information:
        
        Product Name: {product_data.get('name', '')}
        Description: {product_data.get('description', '')}
        
        Return a JSON object with the following fields:
        - name: The full product name
        - brand: The brand name
        - model: The model number or name
        - category: The product category
        - key_features: A list of key features (up to 3)
        """
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that extracts structured product metadata.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 500
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Try to parse the JSON response
        try:
            metadata = json.loads(ai_response)
            
            # Add the original price and image
            metadata['price'] = product_data.get('price')
            metadata['currency'] = product_data.get('currency', 'INR')
            metadata['image_url'] = product_data.get('image_url', '')
            
            return metadata
        except json.JSONDecodeError:
            logger.warning("Failed to parse OpenAI response as JSON")
            return None
    except Exception as e:
        logger.error(f"Error enhancing metadata with OpenAI: {str(e)}")
        return None

def extract_brand_from_name(name):
    """
    Extract brand from product name (fallback if AI is not available)
    """
    if not name:
        return ""
    
    # Simple heuristic: take the first word as the brand
    words = name.split()
    if words:
        return words[0]
    
    return ""

def search_other_platforms(metadata):
    """
    Search for the product on other platforms using Groq AI
    Returns a list of dictionaries with platform, url, price, etc.
    """
    if not metadata or 'name' not in metadata:
        logger.error("Invalid metadata for product comparison")
        return []
    
    # Define the platforms we want to search
    platforms = ['Flipkart', 'Meesho', 'BigBasket', 'Swiggy Instamart']
    
    # Extract product name and ensure it's complete
    product_name = metadata.get('name', '')
    if not product_name:
        logger.error("Missing product name for comparison search")
        return []
        
    # Extract brand for better search precision
    product_brand = metadata.get('brand', '')
    
    # Create search query with brand + product name for better results
    search_query = product_name
    if product_brand and product_brand.lower() not in product_name.lower():
        search_query = f"{product_brand} {product_name}"
    
    logger.info(f"Using exact product title for comparison: {search_query}")
    
    # Basic search URLs for each platform with full product name
    platform_urls = {
        'Flipkart': f"https://www.flipkart.com/search?q={search_query}",
        'Meesho': f"https://www.meesho.com/search?q={search_query}",
        'BigBasket': f"https://www.bigbasket.com/ps/?q={search_query}",
        'Swiggy Instamart': f"https://www.swiggy.com/search?query={search_query}"
    }
    
    # If we have Groq API, use it to generate more precise search results
    if GROQ_API_KEY:
        try:
            # Prepare product information for AI with exact product title
            product_info = f"""
            Exact Product Title: {product_name}
            Brand: {product_brand}
            """
            
            if 'model' in metadata and metadata['model']:
                product_info += f"Model: {metadata['model']}\n"
                
            if 'category' in metadata and metadata['category']:
                product_info += f"Category: {metadata['category']}\n"
                
            if 'key_features' in metadata and metadata['key_features']:
                features = "\n".join([f"- {feature}" for feature in metadata['key_features']])
                product_info += f"Key Features:\n{features}\n"
            
            # Use Groq to generate improved search queries
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}'
            }
            
            prompt = f"""
            I need to find the same product on different e-commerce platforms in India.
            
            Product details:
            {product_info}
            
            For each of these platforms: Flipkart, Meesho, BigBasket, and Swiggy Instamart,
            provide:
            1. The best search query to find this exact product
            2. An estimated price range in INR (if you can infer it)
            
            Return your response as a JSON object in this format:
            {{
              "platforms": [
                {{
                  "name": "Platform Name",
                  "search_query": "optimized search query",
                  "estimated_price": number or null,
                  "currency": "INR"
                }},
                ...
              ]
            }}
            """
            
            data = {
                'model': 'llama3-8b-8192',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that specializes in e-commerce product search optimization.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 800
            }
            
            response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Make prompt more explicit about returning valid JSON
            prompt = f"""
            I need to find the EXACT SAME product on different e-commerce platforms in India. This is critical - we need to compare the same exact product, not similar or related products.
            
            Exact Product details:
            {product_info}
            
            For each of these platforms: Flipkart, Meesho, BigBasket, and Swiggy Instamart,
            provide:
            1. The best search query to find this EXACT same product (use the complete product title)
            2. An estimated price range in INR (if you can infer it)
            
            Return your response as a valid JSON object in this format:
            {{
              "platforms": [
                {{
                  "name": "Platform Name",
                  "search_query": "optimized search query using exact product title",
                  "estimated_price": number or null,
                  "currency": "INR"
                }},
                ...
              ]
            }}
            
            IMPORTANT: Your response must be ONLY a valid JSON object, with no additional text, explanations, or formatting.
            DO NOT modify or shorten the product title - use it exactly as provided to ensure we find the exact same product.
            """
            
            data = {
                'model': 'llama3-8b-8192',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that specializes in e-commerce product search optimization. You always respond with valid JSON.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 800,
                'response_format': {'type': 'json_object'}  # Request JSON format if supported
            }
            
            response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Validate AI response before parsing
            if not ai_response or not ai_response.strip():
                logger.warning("Empty response from Groq AI for platform search")
                raise ValueError("Empty response from AI")
            
            # Try to parse the JSON response
            try:
                # Clean the response before parsing
                cleaned_response = sanitize_json_string(ai_response)
                ai_data = json.loads(cleaned_response)
                
                # Validate the expected structure
                if 'platforms' not in ai_data or not isinstance(ai_data['platforms'], list):
                    logger.warning("Invalid response structure from Groq AI - missing 'platforms' array")
                    logger.debug(f"Response structure: {ai_data.keys()}")
                    raise ValueError("Invalid response structure")
                
                logger.info(f"Successfully parsed Groq AI response with {len(ai_data['platforms'])} platform entries")
                
                # Update the platform URLs with AI-optimized queries
                if 'platforms' in ai_data:
                    for platform_info in ai_data['platforms']:
                        platform_name = platform_info.get('name')
                        search_query = platform_info.get('search_query')
                        
                        if platform_name in platform_urls and search_query:
                            # For Flipkart
                            if platform_name == 'Flipkart':
                                platform_urls[platform_name] = f"https://www.flipkart.com/search?q={search_query}"
                            
                            # For Meesho
                            elif platform_name == 'Meesho':
                                platform_urls[platform_name] = f"https://www.meesho.com/search?q={search_query}"
                            
                            # For BigBasket
                            elif platform_name == 'BigBasket':
                                platform_urls[platform_name] = f"https://www.bigbasket.com/ps/?q={search_query}"
                            
                            # For Swiggy Instamart
                            elif platform_name == 'Swiggy Instamart':
                                platform_urls[platform_name] = f"https://www.swiggy.com/search?query={search_query}"
                
                # Build the comparison results with AI-estimated prices
                comparisons = []
                for platform_info in ai_data.get('platforms', []):
                    platform_name = platform_info.get('name')
                    if platform_name in platform_urls:
                        comparisons.append({
                            'platform': platform_name,
                            'url': platform_urls[platform_name],
                            'price': platform_info.get('estimated_price'),
                            'currency': platform_info.get('currency', 'INR'),
                            'in_stock': None,  # We don't have this information yet
                            'last_checked': datetime.now().isoformat()
                        })
                
                if comparisons:
                    logger.info(f"Generated {len(comparisons)} AI-enhanced platform comparisons")
                    return comparisons
                
                # If we couldn't build comparisons from the AI data, log and continue to fallback
                logger.warning("Could not generate platform comparisons from AI data")
                    
            except json.JSONDecodeError as json_err:
                # Log detailed error and truncated response for debugging
                truncated_response = ai_response[:500] + '...' if len(ai_response) > 500 else ai_response
                logger.warning(f"Failed to parse Groq AI response as JSON for platform search: {str(json_err)}")
                logger.debug(f"Raw platform search response (truncated): {truncated_response}")
            except ValueError as ve:
                logger.warning(f"Value error processing AI response: {str(ve)}")
        
        except Exception as e:
            logger.error(f"Error using Groq for platform search: {str(e)}")
    
    # Fallback: return basic search URLs without AI enhancement
    return [
        {
            'platform': platform,
            'url': platform_urls[platform],
            'price': None,
            'currency': 'INR',
            'in_stock': None,
            'last_checked': datetime.now().isoformat()
        } for platform in platforms
    ]

# Note: To fully implement the multi-platform comparison feature,
# you would need to add scraping logic for each platform (Flipkart, Meesho, etc.)
# and integrate it with the search_other_platforms function.
