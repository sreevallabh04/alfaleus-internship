import asyncio
import logging
from services.database import get_untriggered_alerts, mark_alert_triggered, get_product_by_id
from services.email_service import send_price_alert_email

logger = logging.getLogger(__name__)

async def check_and_trigger_alerts(product_id, current_price):
    """Check and trigger price alerts for a product"""
    try:
        # Get untriggered alerts where target price is met
        alerts = await get_untriggered_alerts(product_id, current_price)
        
        if not alerts:
            return
        
        # Get product details for email
        product = await get_product_by_id(product_id)
        if not product:
            logger.error(f"Product {product_id} not found when checking alerts")
            return
        
        logger.info(f"Found {len(alerts)} alerts to trigger for product {product_id}")
        
        for alert in alerts:
            try:
                # Send email notification
                email_sent = await send_price_alert_email(alert, product, current_price)
                
                if email_sent:
                    # Mark alert as triggered
                    await mark_alert_triggered(alert['id'])
                    logger.info(f"Triggered alert {alert['id']} for product {product_id}")
                else:
                    logger.error(f"Failed to send email for alert {alert['id']}")
            except Exception as e:
                logger.error(f"Error triggering alert {alert['id']}: {str(e)}")
    except Exception as e:
        logger.error(f"Error checking alerts for product {product_id}: {str(e)}")
