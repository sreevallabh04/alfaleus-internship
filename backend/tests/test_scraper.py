import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper import scrape_product, extract_from_json_ld, extract_from_html_elements, extract_from_meta_tags
from services.url_normalizer import normalize_amazon_url, extract_amazon_asin

class TestScraper(unittest.TestCase):
    
    @patch('services.scraper.requests.get')
    def test_scrape_amazon_product_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <head>
                <script type="application/ld+json">
                    {
                        "@type": "Product",
                        "name": "Test Product",
                        "description": "This is a test product",
                        "image": "https://example.com/image.jpg",
                        "offers": {
                            "price": 99.99,
                            "priceCurrency": "USD"
                        }
                    }
                </script>
            </head>
            <body>
                <div id="productTitle">Test Product</div>
                <div id="priceblock_ourprice">$99.99</div>
                <img id="landingImage" data-old-hires="https://example.com/image.jpg" />
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Test scraping
        result = scrape_product("https://www.amazon.com/dp/B08N5KWB9H")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Test Product")
        self.assertEqual(result['price'], 99.99)
        self.assertEqual(result['image_url'], "https://example.com/image.jpg")
    
    def test_normalize_amazon_url(self):
        # Test various Amazon URL formats
        test_cases = [
            {
                'input': 'https://www.amazon.com/dp/B08N5KWB9H',
                'expected': 'https://www.amazon.com/dp/B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/Sony-WH-1000XM4-Canceling-Headphones-phone-call/dp/B08N5KWB9H/ref=sr_1_1',
                'expected': 'https://www.amazon.com/dp/B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/gp/product/B08N5KWB9H',
                'expected': 'https://www.amazon.com/dp/B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/gp/product/B08N5KWB9H?pf_rd_r=ABC123',
                'expected': 'https://www.amazon.com/dp/B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.in/dp/B08N5KWB9H',
                'expected': 'https://www.amazon.in/dp/B08N5KWB9H'
            }
        ]
        
        for case in test_cases:
            result = normalize_amazon_url(case['input'])
            self.assertEqual(result, case['expected'])
    
    def test_extract_amazon_asin(self):
        # Test ASIN extraction from various URL formats
        test_cases = [
            {
                'input': 'https://www.amazon.com/dp/B08N5KWB9H',
                'expected': 'B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/Sony-WH-1000XM4-Canceling-Headphones-phone-call/dp/B08N5KWB9H/ref=sr_1_1',
                'expected': 'B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/gp/product/B08N5KWB9H',
                'expected': 'B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/gp/product/B08N5KWB9H?pf_rd_r=ABC123',
                'expected': 'B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/some-product/B08N5KWB9H/',
                'expected': 'B08N5KWB9H'
            },
            {
                'input': 'https://www.amazon.com/some-product/?ASIN=B08N5KWB9H',
                'expected': 'B08N5KWB9H'
            }
        ]
        
        for case in test_cases:
            result = extract_amazon_asin(case['input'])
            self.assertEqual(result, case['expected'])

if __name__ == '__main__':
    unittest.main()
