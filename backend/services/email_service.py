import os
import smtplib
import asyncio
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'pricepulse@example.com')

# Track connection status
_smtp_connection_verified = False
_smtp_last_attempt = 0
_smtp_retry_interval = 300  # 5 minutes

def validate_smtp_config():
    """
    Check if SMTP configuration is valid
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured")
        return False
    
    if not SMTP_SERVER or not SMTP_PORT:
        logger.warning("SMTP server or port not configured")
        return False
    
    return True

def test_smtp_connection():
    """
    Test SMTP connection and credentials
    Returns True if connection successful, False otherwise
    """
    global _smtp_connection_verified, _smtp_last_attempt
    
    # Don't retry too frequently
    current_time = time.time()
    if _smtp_connection_verified or (current_time - _smtp_last_attempt < _smtp_retry_interval):
        return _smtp_connection_verified
    
    _smtp_last_attempt = current_time
    
    if not validate_smtp_config():
        return False
    
    logger.info(f"Testing SMTP connection to {SMTP_SERVER}:{SMTP_PORT}")
    
    try:
        # First check if server is reachable
        socket.create_connection((SMTP_SERVER, SMTP_PORT), timeout=10)
        
        # Then test SMTP authentication
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            logger.info("SMTP connection test successful")
            _smtp_connection_verified = True
            return True
    except socket.error as e:
        logger.error(f"SMTP server unreachable: {str(e)}")
        _smtp_connection_verified = False
        return False
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed - check username and password")
        _smtp_connection_verified = False
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error during connection test: {str(e)}")
        _smtp_connection_verified = False
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing SMTP connection: {str(e)}")
        _smtp_connection_verified = False
        return False

async def send_price_alert_email(alert, product, current_price):
    """
    Send a price alert email notification
    """
    # Validate config and test connection
    if not validate_smtp_config():
        logger.warning("SMTP not configured correctly. Email not sent.")
        return False
    
    # Test connection if not verified recently
    if not _smtp_connection_verified and not test_smtp_connection():
        logger.warning("SMTP connection test failed. Email not sent.")
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Preparing price alert email to {alert['email']} at {timestamp}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Price Drop Alert: {product['name']}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = alert['email']
        msg['Date'] = timestamp
        msg['X-PricePulse-AlertID'] = str(alert.get('id', 0))
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 300; }}
                .content {{ padding: 30px 20px; }}
                .product-card {{ background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .product-name {{ font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 10px; }}
                .price-info {{ display: flex; justify-content: space-between; align-items: center; margin: 15px 0; }}
                .current-price {{ font-size: 32px; color: #27ae60; font-weight: bold; }}
                .target-price {{ font-size: 16px; color: #7f8c8d; }}
                .savings {{ background-color: #e8f5e8; color: #27ae60; padding: 8px 16px; border-radius: 20px; font-weight: 600; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: 600; text-align: center; }}
                .cta-button:hover {{ opacity: 0.9; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef; }}
                .footer p {{ margin: 5px 0; font-size: 12px; color: #6c757d; }}
                .emoji {{ font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="emoji">🎉</div>
                    <h1>Price Drop Alert!</h1>
                    <p>Your target price has been reached</p>
                </div>
                <div class="content">
                    <p>Great news! The price of a product you're tracking has dropped below your target price.</p>
                    
                    <div class="product-card">
                        <div class="product-name">{product['name']}</div>
                        <div class="price-info">
                            <div>
                                <div class="current-price">{product.get('currency', 'USD')} {current_price:.2f}</div>
                                <div class="target-price">Target: {product.get('currency', 'USD')} {alert['target_price']:.2f}</div>
                            </div>
                            <div class="savings">
                                Save {product.get('currency', 'USD')} {(alert['target_price'] - current_price):.2f}
                            </div>
                        </div>
                    </div>
                    
                    <p>Don't miss this opportunity to save money! Click the button below to view the product.</p>
                    
                    <div style="text-align: center;">
                        <a href="{product['url']}" class="cta-button">🛒 View Product Now</a>
                    </div>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #7f8c8d;">
                        <strong>💡 Pro Tip:</strong> Prices can change quickly. We recommend purchasing soon if you're interested!
                    </p>
                </div>
                <div class="footer">
                    <p><strong>PricePulse</strong> - Your Smart Price Tracking Assistant</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>© 2024 PricePulse. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Add a plain text alternative
        plain_text = f"""
        PRICE DROP ALERT!
        
        Great news! The price of {product['name']} has dropped below your target price.
        
        Current Price: {product.get('currency', 'USD')} {current_price:.2f}
        Your Target: {product.get('currency', 'USD')} {alert['target_price']:.2f}
        You Save: {product.get('currency', 'USD')} {(alert['target_price'] - current_price):.2f}
        
        View the product here: {product.get('url', '')}
        
        Prices can change quickly. We recommend purchasing soon if you're interested!
        
        -- 
        PricePulse - Your Smart Price Tracking Assistant
        """
        msg.attach(MIMEText(plain_text, 'plain'))
        
        # Send email in a separate thread to avoid blocking
        def send_email():
            retry_count = 0
            max_retries = 3
            retry_delay = 2  # seconds
            
            while retry_count < max_retries:
                try:
                    # Use with context to ensure proper cleanup
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        server.send_message(msg)
                        logger.info(f"Email sent successfully to {alert['email']}")
                        return True
                except smtplib.SMTPAuthenticationError:
                    logger.error("SMTP authentication failed - check username and password")
                    return False  # Don't retry auth failures
                except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, socket.error) as e:
                    logger.warning(f"SMTP connection error (attempt {retry_count+1}/{max_retries}): {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                except smtplib.SMTPException as e:
                    logger.error(f"SMTP error: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                except Exception as e:
                    logger.error(f"Unexpected error sending email: {str(e)}")
                    return False
            
            logger.error(f"Failed to send email after {max_retries} attempts")
            return False
        
        # Run email sending in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, send_email)
        
        if result:
            logger.info(f"Price alert email sent to {alert['email']} for product {product['id']}")
        else:
            logger.error(f"Failed to send price alert email to {alert['email']}")
        
        return result
    except Exception as e:
        logger.error(f"Error sending price alert email: {str(e)}")
        return False
