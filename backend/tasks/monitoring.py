"""
Monitoring tasks

Celery tasks for monitoring products, stock levels, and other metrics.
"""

from celery_app import celery_app
from config import get_logger
from database import db_manager
from database.repositories import product_repository, shop_repository

logger = get_logger(__name__)


@celery_app.task(bind=True, name="tasks.monitoring.check_stock_levels_task")
async def check_stock_levels_task(self, threshold: int = 10) -> dict:
    """
    Check stock levels for all products and identify low stock
    
    Args:
        threshold: Stock level threshold for alert
        
    Returns:
        List of products with low stock
    """
    logger.info(f"Starting check_stock_levels_task with threshold={threshold}")
    
    low_stock_products = []
    
    try:
        async with db_manager.get_async_session() as db:
            shops = await shop_repository.get_all(db, skip=0, limit=1000)
            
            for shop in shops:
                products = await product_repository.get_by_shop(db, shop.id, skip=0, limit=10000)
                
                for product in products:
                    if product.is_active and product.current_stock <= threshold:
                        low_stock_products.append({
                            "shop_id": shop.id,
                            "shop_name": shop.name,
                            "product_id": product.id,
                            "nm_id": product.nm_id,
                            "title": product.title,
                            "current_stock": product.current_stock,
                            "vendor_code": product.vendor_code
                        })
            
            result = {
                "threshold": threshold,
                "low_stock_count": len(low_stock_products),
                "products": low_stock_products
            }
            
            logger.info(f"check_stock_levels_task completed: found {len(low_stock_products)} products with low stock")
            return result
    
    except Exception as e:
        logger.error(f"check_stock_levels_task failed: {e}")
        raise
