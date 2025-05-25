from datetime import datetime
from .db import db

class PriceRecord(db.Model):
    __tablename__ = 'price_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    platform = db.Column(db.String(50), nullable=False, default='Amazon') # Add platform column
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'price': self.price,
            'platform': self.platform, # Include platform in dict
            'timestamp': self.timestamp.isoformat() if hasattr(self.timestamp, 'isoformat') else self.timestamp
        }
