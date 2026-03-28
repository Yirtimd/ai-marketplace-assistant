"""
Data Sync Service

Service for synchronizing Wildberries data to database.
Implements the data transformation layer: WB API → Service → Transform → Database
"""

from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_logger
from services.wildberries import WBProductsService, WBFeedbacksService, WBSalesService
from database.repositories import (
    product_repository, 
    sale_repository, 
    review_repository
)

logger = get_logger(__name__)


class DataSyncService:
    """
    Service for syncing WB data to database
    
    This service handles:
    - Fetching data from WB API
    - Transforming WB format to DB format
    - Saving/updating records in database
    """
    
    def __init__(
        self,
        products_service: WBProductsService,
        feedbacks_service: WBFeedbacksService,
        sales_service: WBSalesService
    ):
        self.products_service = products_service
        self.feedbacks_service = feedbacks_service
        self.sales_service = sales_service
    
    async def sync_products(
        self,
        db: AsyncSession,
        shop_id: int,
        limit: int = 100,
        track_history: bool = True
    ) -> Dict[str, Any]:
        """
        Sync products from WB to database
        
        Strategy: UPDATE with optional history tracking
        Products represent current state, but we track price/stock/rating changes.
        
        Args:
            db: Database session
            shop_id: Shop ID
            limit: Max products to fetch
            track_history: Track price/stock/rating changes (default: True)
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting products sync for shop {shop_id}, track_history={track_history}")
        
        created = 0
        updated = 0
        price_changes = 0
        stock_changes = 0
        rating_changes = 0
        errors = 0
        
        try:
            wb_response = await self.products_service.get_products(limit=limit)
            wb_products = wb_response.get("cards", [])
            
            for wb_product in wb_products:
                try:
                    nm_id = wb_product.get("nmID")
                    
                    existing_product = await product_repository.get_by_nm_id(db, nm_id)
                    
                    # Extract current data
                    new_price = wb_product.get("price")
                    new_discount = wb_product.get("discount", 0)
                    new_rating = wb_product.get("rating")
                    new_reviews_count = wb_product.get("reviews_count", 0)
                    new_stock = wb_product.get("stock", 0)
                    
                    product_data = {
                        "shop_id": shop_id,
                        "nm_id": nm_id,
                        "imt_id": wb_product.get("imtID"),
                        "vendor_code": wb_product.get("vendorCode"),
                        "brand": wb_product.get("brand"),
                        "title": wb_product.get("title"),
                        "description": wb_product.get("description"),
                        "subject_name": wb_product.get("subjectName"),
                        "price": new_price,
                        "discount": new_discount,
                        "rating": new_rating,
                        "reviews_count": new_reviews_count,
                        "current_stock": new_stock,
                        "last_sync_at": datetime.utcnow(),
                        "sizes": wb_product.get("sizes"),
                        "photos": wb_product.get("photos"),
                        "characteristics": wb_product.get("characteristics"),
                    }
                    
                    if existing_product:
                        # Track history if enabled
                        if track_history:
                            # Import here to avoid circular imports
                            from database.repositories.price_history import price_history_repository
                            from database.repositories.stock_history import stock_history_repository
                            from database.repositories.rating_history import rating_history_repository
                            
                            # Track price changes
                            if new_price and existing_product.price != new_price:
                                await price_history_repository.create(db, {
                                    "product_id": existing_product.id,
                                    "price": new_price,
                                    "discount": new_discount,
                                    "final_price": new_price * (1 - new_discount / 100) if new_discount else new_price,
                                    "changed_at": datetime.utcnow(),
                                    "source": "wb_sync"
                                })
                                price_changes += 1
                                logger.debug(f"Price changed for product {nm_id}: {existing_product.price} -> {new_price}")
                            
                            # Track stock changes
                            if existing_product.current_stock != new_stock:
                                await stock_history_repository.create(db, {
                                    "product_id": existing_product.id,
                                    "stock_total": new_stock,
                                    "stock_warehouse": new_stock,
                                    "stock_in_transit": 0,
                                    "recorded_at": datetime.utcnow(),
                                    "source": "wb_sync"
                                })
                                stock_changes += 1
                                logger.debug(f"Stock changed for product {nm_id}: {existing_product.current_stock} -> {new_stock}")
                            
                            # Track rating changes
                            if new_rating and (existing_product.rating != new_rating or existing_product.reviews_count != new_reviews_count):
                                await rating_history_repository.create(db, {
                                    "product_id": existing_product.id,
                                    "rating": new_rating,
                                    "reviews_count": new_reviews_count,
                                    "recorded_at": datetime.utcnow()
                                })
                                rating_changes += 1
                                logger.debug(f"Rating changed for product {nm_id}: {existing_product.rating} -> {new_rating}")
                        
                        # Update product
                        await product_repository.update(db, existing_product.id, product_data)
                        updated += 1
                    else:
                        # Create new product
                        await product_repository.create(db, product_data)
                        created += 1
                
                except Exception as e:
                    logger.error(f"Error syncing product {wb_product.get('nmID')}: {e}")
                    errors += 1
            
            logger.info(f"Products sync completed: created={created}, updated={updated}, "
                       f"price_changes={price_changes}, stock_changes={stock_changes}, "
                       f"rating_changes={rating_changes}, errors={errors}")
            
            return {
                "status": "completed",
                "created": created,
                "updated": updated,
                "history_tracked": {
                    "price_changes": price_changes,
                    "stock_changes": stock_changes,
                    "rating_changes": rating_changes
                },
                "errors": errors,
                "total": len(wb_products)
            }
        
        except Exception as e:
            logger.error(f"Products sync failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def sync_sales(
        self,
        db: AsyncSession,
        shop_id: int,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """
        Sync sales from WB to database
        
        Strategy: APPEND ONLY (sales are immutable historical records)
        Sales should never be updated - only created if not exists.
        
        Args:
            db: Database session
            shop_id: Shop ID
            date_from: Start date
            date_to: End date
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting sales sync for shop {shop_id}")
        
        created = 0
        skipped = 0  # Changed from "updated"
        errors = 0
        
        try:
            wb_response = await self.sales_service.get_sales(date_from=date_from, date_to=date_to)
            wb_sales = wb_response.get("data", [])
            
            for wb_sale in wb_sales:
                try:
                    sale_id = wb_sale.get("saleID")
                    
                    # Check if sale already exists
                    existing_sale = await sale_repository.get_by_field(db, "sale_id", sale_id)
                    
                    if existing_sale:
                        # Sales are immutable - skip if exists ✅
                        logger.debug(f"Sale {sale_id} already exists, skipping")
                        skipped += 1
                        continue
                    
                    # Get product
                    nm_id = wb_sale.get("nmID")
                    product = await product_repository.get_by_nm_id(db, nm_id)
                    
                    if not product:
                        logger.warning(f"Product {nm_id} not found for sale {sale_id}")
                        continue
                    
                    # Create new sale
                    sale_data = {
                        "shop_id": shop_id,
                        "product_id": product.id,
                        "sale_id": sale_id,
                        "order_id": wb_sale.get("orderID"),
                        "nm_id": nm_id,
                        "vendor_code": wb_sale.get("vendorCode"),
                        "sale_date": wb_sale.get("date"),
                        "quantity": wb_sale.get("quantity"),
                        "price": wb_sale.get("price"),
                        "discount": wb_sale.get("discount"),
                        "total_price": wb_sale.get("totalPrice"),
                        "warehouse_name": wb_sale.get("warehouseName"),
                        "oblast": wb_sale.get("oblast"),
                        "region": wb_sale.get("region"),
                    }
                    
                    await sale_repository.create(db, sale_data)
                    created += 1
                
                except Exception as e:
                    logger.error(f"Error syncing sale {wb_sale.get('saleID')}: {e}")
                    errors += 1
            
            logger.info(f"Sales sync completed: created={created}, skipped={skipped}, errors={errors}")
            
            return {
                "status": "completed",
                "created": created,
                "skipped": skipped,  # Changed from "updated"
                "errors": errors,
                "total": len(wb_sales)
            }
        
        except Exception as e:
            logger.error(f"Sales sync failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def sync_reviews(
        self,
        db: AsyncSession,
        shop_id: int,
        is_answered: bool = None
    ) -> Dict[str, Any]:
        """
        Sync reviews/feedbacks from WB to database
        
        Strategy: APPEND ONLY for new reviews, UPDATE for answered status
        Reviews are historical, but answers can be added later.
        
        Args:
            db: Database session
            shop_id: Shop ID
            is_answered: Filter by answered status
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting reviews sync for shop {shop_id}")
        
        created = 0
        updated = 0  # Only for answer updates
        skipped = 0
        errors = 0
        
        try:
            wb_response = await self.feedbacks_service.get_feedbacks(is_answered=is_answered)
            wb_feedbacks = wb_response.get("data", [])
            
            for wb_feedback in wb_feedbacks:
                try:
                    feedback_id = wb_feedback.get("id")
                    nm_id = wb_feedback.get("nmId")
                    
                    product = await product_repository.get_by_nm_id(db, nm_id)
                    if not product:
                        logger.warning(f"Product {nm_id} not found for feedback {feedback_id}")
                        continue
                    
                    existing_review = await review_repository.get_by_field(db, "wb_feedback_id", feedback_id)
                    
                    review_data = {
                        "shop_id": shop_id,
                        "product_id": product.id,
                        "wb_feedback_id": feedback_id,
                        "nm_id": nm_id,
                        "review_type": "feedback",
                        "text": wb_feedback.get("text"),
                        "rating": wb_feedback.get("rating"),
                        "user_name": wb_feedback.get("userName", "Покупатель"),
                        "created_date": wb_feedback.get("createdAt"),
                        "is_answered": wb_feedback.get("isAnswered", False),
                        "answer_text": wb_feedback.get("answer", {}).get("text") if wb_feedback.get("answer") else None,
                        "answered_at": wb_feedback.get("answer", {}).get("createdAt") if wb_feedback.get("answer") else None,
                    }
                    
                    if existing_review:
                        # Update only if answer was added
                        if not existing_review.is_answered and review_data["is_answered"]:
                            await review_repository.update(db, existing_review.id, {
                                "is_answered": review_data["is_answered"],
                                "answer_text": review_data["answer_text"],
                                "answered_at": review_data["answered_at"]
                            })
                            updated += 1
                            logger.debug(f"Review {feedback_id} answer updated")
                        else:
                            skipped += 1
                    else:
                        await review_repository.create(db, review_data)
                        created += 1
                
                except Exception as e:
                    logger.error(f"Error syncing feedback {wb_feedback.get('id')}: {e}")
                    errors += 1
            
            logger.info(f"Reviews sync completed: created={created}, updated={updated}, skipped={skipped}, errors={errors}")
            
            return {
                "status": "completed",
                "created": created,
                "updated": updated,
                "skipped": skipped,
                "errors": errors,
                "total": len(wb_feedbacks)
            }
        
        except Exception as e:
            logger.error(f"Reviews sync failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
