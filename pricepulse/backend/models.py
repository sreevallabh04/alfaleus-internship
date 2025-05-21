from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    """Model for storing product information."""
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with PriceRecord
    price_records = db.relationship('PriceRecord', backref='product', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with PriceAlert
    price_alerts = db.relationship('PriceAlert', backref='product', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PriceRecord(db.Model):
    """Model for storing price history."""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='₹')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PriceRecord {self.price} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'price': self.price,
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat()
        }

class PriceAlert(db.Model):
    """Model for storing price alert configurations."""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    alert_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PriceAlert {self.email} - {self.target_price}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'email': self.email,
            'target_price': self.target_price,
            'alert_sent': self.alert_sent,
            'created_at': self.created_at.isoformat()
        }