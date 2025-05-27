from datetime import datetime
from models.db import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    amazon_url = db.Column(db.String(500), unique=True, nullable=False)
    title = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    current_price = db.Column(db.Float)
    target_price = db.Column(db.Float)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'amazon_url': self.amazon_url,
            'title': self.title,
            'image_url': self.image_url,
            'current_price': self.current_price,
            'target_price': self.target_price,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
