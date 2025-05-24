import sys
import os
import unittest
import json
from unittest.mock import patch

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as flask_app
from models.db import db
from models.product import Product
from models.price_record import PriceRecord
from models.price_alert import PriceAlert

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        # Configure the app for testing
        flask_app.app.config['TESTING'] = True
        flask_app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Create test client
        self.app = flask_app.app.test_client()
        
        # Create database tables
        with flask_app.app.app_context():
            db.create_all()
            
            # Add test data
            test_product = Product(
                name='Test Product',
                url='https://www.amazon.com/dp/B08N5KWB9H',
                image_url='https://example.com/image.jpg',
                description='This is a test product',
                current_price=99.99,
                currency='USD'
            )
            db.session.add(test_product)
            db.session.commit()
            
            # Add price record
            price_record = PriceRecord(
                product_id=test_product.id,
                price=99.99
            )
            db.session.add(price_record)
            db.session.commit()
    
    def tearDown(self):
        # Clean up after tests
        with flask_app.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_health_check(self):
        # Test health check endpoint
        response = self.app.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'OK')
    
    def test_get_all_products(self):
        # Test getting all products
        response = self.app.get('/api/products')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['products']), 1)
        self.assertEqual(data['products'][0]['name'], 'Test Product')
    
    def test_get_product(self):
        # Test getting a specific product
        response = self.app.get('/api/products/1')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['name'], 'Test Product')
        self.assertEqual(len(data['price_history']), 1)
    
    @patch('services.scraper.scrape_product')
    def test_add_product(self, mock_scrape):
        # Mock scraper response
        mock_scrape.return_value = {
            'name': 'New Test Product',
            'price': 149.99,
            'image_url': 'https://example.com/new-image.jpg',
            'description': 'This is a new test product',
            'currency': 'USD'
        }
        
        # Test adding a new product
        response = self.app.post('/api/products', 
                                json={'url': 'https://www.amazon.com/dp/B08N5KWB9H2'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['name'], 'New Test Product')
        
        # Verify product was added to database
        with flask_app.app.app_context():
            products = Product.query.all()
            self.assertEqual(len(products), 2)
    
    def test_create_alert(self):
        # Test creating a price alert
        response = self.app.post('/api/alerts', 
                                json={
                                    'product_id': 1,
                                    'email': 'test@example.com',
                                    'target_price': 89.99
                                })
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        
        # Verify alert was added to database
        with flask_app.app.app_context():
            alerts = PriceAlert.query.all()
            self.assertEqual(len(alerts), 1)
            self.assertEqual(alerts[0].email, 'test@example.com')
            self.assertEqual(alerts[0].target_price, 89.99)
    
    def test_delete_product(self):
        # Test deleting a product
        response = self.app.delete('/api/products/1')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify product was deleted from database
        with flask_app.app.app_context():
            products = Product.query.all()
            self.assertEqual(len(products), 0)

if __name__ == '__main__':
    unittest.main()
