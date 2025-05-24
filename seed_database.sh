#!/bin/bash

# This script seeds the database with sample products for demo purposes

# Function to display messages
print_message() {
  echo "====================================="
  echo "$1"
  echo "====================================="
}

# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Create Python script for seeding
cat > seed_db.py << EOL
import os
import sys
from datetime import datetime, timedelta
import random
from app import app
from models.db import db
from models.product import Product
from models.price_record import PriceRecord

# Sample products
SAMPLE_PRODUCTS = [
    {
        "name": "Samsung Galaxy M14 5G",
        "url": "https://www.amazon.in/dp/B0CV7KZLL4/",
        "image_url": "https://m.media-amazon.com/images/I/41Iyj5moShL._SX300_SY300_QL70_FMwebp_.jpg",
        "description": "Samsung Galaxy M14 5G (ICY Silver,6GB,128GB)|50MP Triple Cam|Segment's Only 6000 mAh 5G SP|5nm Processor|2 Gen. OS Upgrade & 4 Year Security Update|12GB RAM with RAM Plus|Android 13|Without Charger",
        "current_price": 13990,
        "currency": "INR"
    },
    {
        "name": "Apple iPhone 13",
        "url": "https://www.amazon.in/dp/B09G9D8KRQ/",
        "image_url": "https://m.media-amazon.com/images/I/61l9ppRIiqL._SX679_.jpg",
        "description": "Apple iPhone 13 (128GB) - Blue",
        "current_price": 52999,
        "currency": "INR"
    }
]

def seed_database():
    """Seed the database with sample products and price history"""
    print("Seeding database with sample products...")
    
    with app.app_context():
        # Check if products already exist
        if Product.query.count() > 0:
            print("Database already has products. Skipping seed.")
            return
        
        # Add sample products
        for product_data in SAMPLE_PRODUCTS:
            product = Product(
                name=product_data["name"],
                url=product_data["url"],
                image_url=product_data["image_url"],
                description=product_data["description"],
                current_price=product_data["current_price"],
                currency=product_data["currency"],
                created_at=datetime.utcnow() - timedelta(days=7)  # Created 7 days ago
            )
            db.session.add(product)
            db.session.commit()
            
            # Generate price history for the last 7 days
            base_price = product_data["current_price"]
            for days_ago in range(7, 0, -1):
                # Random price fluctuation within 5%
                price_change = random.uniform(-0.05, 0.05)
                historical_price = base_price * (1 + price_change)
                
                price_record = PriceRecord(
                    product_id=product.id,
                    price=round(historical_price, 2),
                    timestamp=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.session.add(price_record)
            
            # Add current price as the latest record
            price_record = PriceRecord(
                product_id=product.id,
                price=product_data["current_price"],
                timestamp=datetime.utcnow()
            )
            db.session.add(price_record)
            
            db.session.commit()
            print(f"Added product: {product.name} with price history")
    
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
EOL

# Run the seed script
print_message "Seeding database with sample products..."
python seed_db.py

# Deactivate virtual environment
deactivate

cd ..

print_message "Database seeding completed!"
