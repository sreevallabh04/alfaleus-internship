import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_service')

# Get email configuration from environment variables
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', EMAIL_USER)

def send_price_alert_email(alert, product, current_price):
    """
    Send a price alert email to the user.
    
    Args:
        alert: PriceAlert model instance
        product: Product model instance
        current_price (float): Current product price
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("Email credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Price Drop Alert: {product.name}"
        msg['From'] = EMAIL_FROM
        msg['To'] = alert.email
        
        # Create HTML content
        html = generate_email_html(product, alert.target_price, current_price)
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Price alert email sent to {alert.email} for product {product.id}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending price alert email: {e}")
        return False

def generate_email_html(product, target_price, current_price):
    """
    Generate HTML content for the price alert email.
    
    Args:
        product: Product model instance
        target_price (float): Target price set by the user
        current_price (float): Current product price
        
    Returns:
        str: HTML content for the email
    """
    # Format prices for display
    target_price_formatted = f"₹{target_price:,.2f}"
    current_price_formatted = f"₹{current_price:,.2f}"
    
    # Calculate savings
    savings = target_price - current_price
    savings_formatted = f"₹{savings:,.2f}"
    
    # Product image HTML
    image_html = f'<img src="{product.image_url}" alt="{product.name}" style="max-width: 300px; max-height: 300px; margin-bottom: 20px;">' if product.image_url else ''
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Price Drop Alert: {product.name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 24px;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                padding: 20px;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }}
            .product-name {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .price-info {{
                margin: 15px 0;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }}
            .current-price {{
                color: #4CAF50;
                font-size: 22px;
                font-weight: bold;
            }}
            .target-price {{
                font-size: 18px;
            }}
            .savings {{
                color: #4CAF50;
                font-weight: bold;
            }}
            .button {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            Price Drop Alert!
        </div>
        <div class="content">
            <p>Good news! A product you're tracking has dropped in price below your target:</p>
            
            <div class="product-name">{product.name}</div>
            
            {image_html}
            
            <div class="price-info">
                <p class="current-price">Current Price: {current_price_formatted}</p>
                <p class="target-price">Your Target Price: {target_price_formatted}</p>
                <p>You're saving: <span class="savings">{savings_formatted}</span></p>
            </div>
            
            <p>Don't miss this opportunity to grab it at a lower price!</p>
            
            <a href="{product.url}" class="button">View Product</a>
        </div>
        <div class="footer">
            <p>This is an automated alert from PricePulse. You're receiving this because you set up a price alert for this product.</p>
            <p>© 2025 PricePulse - E-Commerce Price Tracker & Smart Comparator</p>
        </div>
    </body>
    </html>
    """
    
    return html