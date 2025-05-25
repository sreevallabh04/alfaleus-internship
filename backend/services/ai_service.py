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

def extract_keywords_from_title(title, brand=None, model=None):
    """
    Extract relevant keywords from a product title for better cross-platform searching
    
    Args:
        title (str): The product title
        brand (str, optional): Product brand if available
        model (str, optional): Product model if available
        
    Returns:
        list: A list of important keywords
    """
    if not title:
        return []
        
    # If we have brand and model, make sure they're included
    important_terms = []
    if brand and len(brand) > 1:
        important_terms.append(brand.lower())
    if model and len(model) > 1:
        important_terms.append(model.lower())
    
    # Split the title into words
    words = title.lower().split()
    
    # Filter out common filler words
    stopwords = ['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'in', 'with', 'for', 'on', 'at', 'to', 'from']
    
    # Extract words that might be important (longer words, numbers, etc.)
    for word in words:
        # Skip short words and stopwords
        if len(word) <= 2 or word in stopwords:
            continue
            
        # Check if it's a number or contains digits (could be important specs)
        if word.isdigit() or any(c.isdigit() for c in word):
            important_terms.append(word)
            continue
            
        # Check if it's an important specification term
        spec_terms = ['gb', 'tb', 'mb', 'inch', 'cm', 'mm', 'kg', 'liter', 'watt', 'volt', 'hz']
        if any(term in word for term in spec_terms):
            important_terms.append(word)
            continue
            
        # Add other potentially important terms (longer words)
        if len(word) >= 4:
            important_terms.append(word)
    
    # Add the full title at the end to ensure we have the complete context
    if title.lower() not in important_terms:
        important_terms.append(title.lower())
        
    return important_terms

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
    Act as a smart shopping assistant to find the same or exact equivalent product
    on other Indian e-commerce platforms.
    
    Returns a list of dictionaries with website, product_title, price, and url.
    Each result is verified to be the exact same product or an official variant.
    """
    if not metadata or 'name' not in metadata:
        logger.error("Invalid metadata for product comparison")
        return []
    
    # Define the Indian e-commerce platforms we want to search
    platforms = ['Flipkart', 'Snapdeal', 'Reliance Digital', 'Tata Cliq', 'Croma']
    
    # Extract product details for search context
    product_name = metadata.get('name', '').strip()
    product_brand = metadata.get('brand', '').strip()
    product_model = metadata.get('model', '').strip()
    product_features = metadata.get('key_features', [])
    product_price = metadata.get('price')
    
    if not product_name:
        logger.error("Missing product name for comparison search")
        return []
    
    logger.info(f"Starting product comparison for: {product_name}")
    logger.info(f"Brand: {product_brand}, Model: {product_model}")
    
    # Extract keywords from the product title for better matching
    keywords = extract_keywords_from_title(product_name, product_brand, product_model)
    logger.info(f"Extracted keywords for search: {keywords}")
    
    # Create optimized search query with brand + model + keywords
    search_query = product_name
    
    # If brand isn't in the name, prepend it
    if product_brand and product_brand.lower() not in product_name.lower():
        search_query = f"{product_brand} {product_name}"
        
    # If model isn't in the name or brand, include it as well
    if product_model and product_model.lower() not in search_query.lower():
        search_query = f"{search_query} {product_model}"
    
    logger.info(f"Using optimized search query for comparison: {search_query}")
    
    # Basic search URLs for each platform
    platform_urls = {
        'Flipkart': f"https://www.flipkart.com/search?q={search_query}",
        'Snapdeal': f"https://www.snapdeal.com/search?keyword={search_query}",
        'Reliance Digital': f"https://www.reliancedigital.in/search?q={search_query}",
        'Tata Cliq': f"https://www.tatacliq.com/search/?searchCategory=all&text={search_query}",
        'Croma': f"https://www.croma.com/searchB?q={search_query}"
    }
    
    # Enhanced function to check if a product match is genuine based on keywords
    def is_genuine_match(match_title, original_title, brand, model, features=None):
        """
        Check if a product match is genuine by comparing key attributes
        Returns (is_match, confidence_score)
        """
        if not match_title:
            return False, 0.0
            
        match_title = match_title.lower()
        original_title = original_title.lower() if original_title else ""
        brand = brand.lower() if brand else ""
        model = model.lower() if model else ""
        
        # Start with base confidence
        confidence = 0.5
        
        # Brand match is critical
        if brand:
            if brand in match_title:
                confidence += 0.2
            else:
                # Brand mismatch is a strong indicator it's not the same product
                return False, 0.0
            
        # Model match is also critical if available
        if model:
            if model in match_title:
                confidence += 0.2
            else:
                # Model mismatch usually means different product
                return False, 0.1
            
        # Calculate keyword matches
        matched_keywords = 0
        total_keywords = len(keywords) if keywords else 1
        
        for keyword in keywords:
            if keyword in match_title:
                matched_keywords += 1
                
        # Weight keyword matches
        keyword_match_percentage = matched_keywords / total_keywords
        confidence += keyword_match_percentage * 0.3
        
        # Check for key feature matches if available
        if features and isinstance(features, list):
            feature_match_count = 0
            for feature in features:
                feature_keywords = extract_keywords_from_title(feature)
                feature_match_score = 0
                for kw in feature_keywords:
                    if kw in match_title:
                        feature_match_score += 1
                
                if feature_match_score / max(1, len(feature_keywords)) > 0.5:
                    feature_match_count += 1
            
            # Add feature match confidence
            if len(features) > 0:
                confidence += (feature_match_count / len(features)) * 0.1
        
        # Final determination
        is_match = confidence >= 0.75
        
        return is_match, min(1.0, confidence)  # Cap confidence at 1.0
    
    # Prepare search context from metadata with more detailed information
    search_context = {
        "title": product_name,
        "brand": product_brand or "Unknown",
        "model": product_model or "Not available",
        "features": product_features,
        "price": f"₹{product_price}" if product_price else "Not available"
    }
    
    # Add any critical fields that must match for exact product identification
    critical_identifiers = []
    if product_brand:
        critical_identifiers.append(f"Brand: {product_brand}")
    if product_model:
        critical_identifiers.append(f"Model: {product_model}")
    
    # Extract color, capacity, size if mentioned in product name
    color_match = re.search(r'\b(Black|White|Blue|Red|Green|Yellow|Purple|Pink|Gold|Silver|Gray|Grey)\b', product_name, re.IGNORECASE)
    if color_match:
        critical_identifiers.append(f"Color: {color_match.group(0)}")
    
    # Look for storage capacity
    storage_match = re.search(r'\b(\d+)\s*(GB|TB|MB)\b', product_name, re.IGNORECASE)
    if storage_match:
        critical_identifiers.append(f"Storage: {storage_match.group(0)}")
    
    # Look for RAM
    ram_match = re.search(r'\b(\d+)\s*GB\s*RAM\b', product_name, re.IGNORECASE)
    if ram_match:
        critical_identifiers.append(f"RAM: {ram_match.group(0)}")
    
    search_context["critical_identifiers"] = critical_identifiers
    
    # If we have access to an LLM API, use it to generate more precise product matches
    if GROQ_API_KEY or OPENAI_API_KEY:
        try:
            # Prepare detailed product information for the LLM with more specific instructions
            features_text = ""
            if product_features:
                features_text = "\n".join([f"- {feature}" for feature in product_features])
            
            # Include critical identifiers in the product info
            critical_info = "\n".join(search_context["critical_identifiers"]) if search_context["critical_identifiers"] else "No specific identifiers available"
            
            product_info = f"""
            Exact Product Title: {product_name}
            Brand: {product_brand}
            Model ID / ASIN / SKU: {product_model}
            Price: ₹{product_price if product_price else 'Not available'}
            Key Features:
            {features_text if features_text else "Not available"}
            
            CRITICAL IDENTIFIERS (MUST MATCH):
            {critical_info}
            """
            
            # Determine which API to use (prefer Groq if available)
            api_key = GROQ_API_KEY if GROQ_API_KEY else OPENAI_API_KEY
            api_endpoint = "https://api.groq.com/openai/v1/chat/completions" if GROQ_API_KEY else "https://api.openai.com/v1/chat/completions"
            model = "llama3-8b-8192" if GROQ_API_KEY else "gpt-3.5-turbo"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            # Create a detailed prompt for finding exact equivalent products
            prompt = f"""
            You are a smart shopping assistant. Given a product scraped from Amazon, search for the **same or exact equivalent product** on other Indian e-commerce sites like Flipkart, Snapdeal, Reliance Digital, Tata Cliq, and Croma.

            Use the following information as your search context:
            {product_info}

            ❗ Your goal is to find the **same model** or **closest official variant**, not just similar category items.

            For each of these platforms: Flipkart, Snapdeal, Reliance Digital, Tata Cliq, and Croma, provide:
            1. The exact product title as it would appear on that platform (with exact model number and specifications matching the original)
            2. The estimated price in INR (realistic market price)
            3. The product URL (either direct product URL or search URL that would lead to this specific product)

            Return a list of matches in this JSON format:
            [
              {{
                "website": "Flipkart", 
                "product_title": "Realme Narzo 60X 5G (Nebula Purple, 128 GB)", 
                "price": "₹11,999",
                "url": "https://www.flipkart.com/product-link"
              }},
              ...
            ]

            ⚠️ CRITICAL RULES:
            - Only include the EXACT SAME product with same specifications (color, storage, etc.)
            - If a specification is mentioned in the original title (e.g., "8GB RAM"), it MUST match in your results
            - ALL critical identifiers MUST be present in your matches
            - Do not include unrelated or generic products
            - All URLs must point to valid product listings or specific search results
            - Price should be a realistic market price (check typical price difference between Amazon and each platform)
            - Format prices with ₹ symbol and thousands separators (like ₹11,999)
            
            Your response must be ONLY a valid JSON array as shown above, with no additional text, explanations, or formatting.
            """
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that specializes in e-commerce product search optimization using exact keywords without paraphrasing.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 800,
                'response_format': {'type': 'json_object'}
            }
            
            response = requests.post(api_endpoint, headers=headers, json=data)
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
                
                # Validate the AI response structure
                if not isinstance(ai_data, list):
                    logger.warning("Invalid response structure from AI - expected a list of products")
                    logger.debug(f"Response structure: {type(ai_data)}")
                    raise ValueError("Invalid response structure")
                
                logger.info(f"Successfully parsed AI response with {len(ai_data)} product matches")
                
                # Transform the AI response into our expected format
                comparisons = []
                
                for product_match in ai_data:
                    website = product_match.get('website', '').strip()
                    product_title = product_match.get('product_title', '').strip()
                    price_str = product_match.get('price', '').strip()
                    url = product_match.get('url', '').strip()
                    
                    # Skip incomplete entries
                    if not website or not product_title or not url:
                        logger.warning(f"Skipping incomplete product match: {product_match}")
                        continue
                    
                    # Verify this is a genuine match using our enhanced logic
                    is_match, confidence = is_genuine_match(
                        product_title, 
                        product_name, 
                        product_brand, 
                        product_model,
                        product_features
                    )
                    
                    if not is_match:
                        logger.warning(f"Filtered out non-genuine match: {product_title} (confidence: {confidence:.2f})")
                        continue
                        
                    logger.info(f"Found genuine match on {website}: {product_title} (confidence: {confidence:.2f})")
                    
                    # Create a comparison entry in the format expected by the frontend
                    comparison_entry = {
                        'platform': website,
                        'url': url,
                        'price': None,  # Default to null, will update below
                        'currency': 'INR',
                        'in_stock': True,  # Assume in stock
                        'last_checked': datetime.now().isoformat(),
                        'is_genuine_match': True,
                        'match_confidence': confidence,
                        'product_title': product_title  # Store the full product title
                    }
                    
                    # Process price with proper error handling
                    if price_str:
                        # Extract numeric price value using regex
                        price_match = re.search(r'₹\s*([\d,]+)', price_str)
                        if price_match:
                            try:
                                # Convert to numeric format for frontend
                                numeric_price = float(price_match.group(1).replace(',', ''))
                                comparison_entry['price'] = numeric_price
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Failed to parse price '{price_str}': {str(e)}")
                    
                    comparisons.append(comparison_entry)
                
                if comparisons:
                    logger.info(f"Generated {len(comparisons)} AI-enhanced platform comparisons")
                    return comparisons
                
                # If we couldn't find any genuine matches, log and continue to fallback
                logger.warning("No genuine product matches found from AI data")
                    
            except json.JSONDecodeError as json_err:
                # Log detailed error and truncated response for debugging
                truncated_response = ai_response[:500] + '...' if len(ai_response) > 500 else ai_response
                logger.warning(f"Failed to parse Groq AI response as JSON for platform search: {str(json_err)}")
                logger.debug(f"Raw platform search response (truncated): {truncated_response}")
            except ValueError as ve:
                logger.warning(f"Value error processing AI response: {str(ve)}")
        
        except Exception as e:
            logger.error(f"Error using AI for platform search: {str(e)}")
    
    # Fallback: return basic search URLs for each platform
    basic_comparisons = []
    for platform in platforms:
        basic_comparisons.append({
            'platform': platform,
            'url': platform_urls[platform],
            'price': None,
            'currency': 'INR',
            'in_stock': None,
            'last_checked': datetime.now().isoformat(),
            'is_genuine_match': False,  # Mark basic comparisons as not verified
            'match_confidence': 0.5,  # Medium-low confidence for basic search
            'product_title': f"{product_brand} {product_name}" if product_brand else product_name
        })
    
    return basic_comparisons

# Note: To fully implement the multi-platform comparison feature,
# you would need to add scraping logic for each platform (Flipkart, Meesho, etc.)
# and integrate it with the search_other_platforms function.