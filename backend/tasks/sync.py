"""
Data synchronization tasks

Celery tasks for syncing data from Wildberries API to database.
"""

from celery import Task
from celery_app import celery_app
from config import get_logger
from database import db_manager
from database.repositories import shop_repository
from services.wildberries import WBProductsService, WBFeedbacksService, WBSalesService
from services.wildberries.exceptions import WildberriesServiceError, WildberriesRateLimitError
from services.data_sync_service import DataSyncService
from tasks.singleton import SingletonTask
from tasks.workflow_aware import WorkflowAwareTask
import httpx

logger = get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    
    _db_session = None
    
    @property
    def db_session(self):
        if self._db_session is None:
            self._db_session = db_manager.get_async_session()
        return self._db_session


class DatabaseSingletonTask(SingletonTask, DatabaseTask):
    """Singleton task with database session management"""
    pass


class WorkflowDatabaseTask(WorkflowAwareTask, SingletonTask, DatabaseTask):
    """
    Task with workflow integration, singleton locking, and database session
    
    Combines all features:
    - Workflow context (workflow_id, user_id)
    - Singleton locking (prevents concurrent execution)
    - Database session management
    """
    pass


@celery_app.task(
    bind=True,
    base=WorkflowDatabaseTask,
    name="tasks.sync.sync_products_task",
    autoretry_for=(WildberriesServiceError, httpx.RequestError, httpx.TimeoutException),
    retry_kwargs={'max_retries': 5, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
async def sync_products_task(
    self,
    shop_id: int,
    limit: int = 100,
    offset: int = 0,
    chunk_size: int = 50,
    auto_chunk: bool = True
) -> dict:
    """
    Sync products for a specific shop with automatic chunking
    
    Args:
        shop_id: Shop ID to sync
        limit: Maximum products to sync (total)
        offset: Offset for pagination
        chunk_size: Number of products per chunk
        auto_chunk: Automatically schedule next chunks
        
    Returns:
        Sync result statistics
    """
    logger.info(f"Starting sync_products_task for shop {shop_id}, offset={offset}, limit={limit}")
    
    try:
        async with db_manager.get_async_session() as db:
            # Initialize services
            products_service = WBProductsService()
            feedbacks_service = WBFeedbacksService()
            sales_service = WBSalesService()
            
            sync_service = DataSyncService(
                products_service=products_service,
                feedbacks_service=feedbacks_service,
                sales_service=sales_service
            )
            
            # Calculate actual chunk size for this iteration
            remaining = limit - offset
            current_chunk_size = min(chunk_size, remaining)
            
            # Sync current chunk with history tracking
            result = await sync_service.sync_products(
                db=db,
                shop_id=shop_id,
                limit=current_chunk_size,
                track_history=True
            )
            
            # Check if there are more products to process
            next_offset = offset + current_chunk_size
            if auto_chunk and next_offset < limit and result.get("status") == "completed":
                # Schedule next chunk
                sync_products_task.delay(
                    shop_id=shop_id,
                    limit=limit,
                    offset=next_offset,
                    chunk_size=chunk_size,
                    auto_chunk=True
                )
                result["next_chunk_scheduled"] = True
                result["next_offset"] = next_offset
                logger.info(f"Scheduled next chunk for shop {shop_id}, offset={next_offset}")
            else:
                result["next_chunk_scheduled"] = False
            
            result["current_offset"] = offset
            result["chunk_size"] = current_chunk_size
            
            logger.info(f"sync_products_task completed for shop {shop_id}: {result}")
            return result
    
    except Exception as e:
        logger.error(f"sync_products_task failed for shop {shop_id}: {e}")
        raise


@celery_app.task(
    bind=True,
    base=WorkflowDatabaseTask,
    name="tasks.sync.sync_sales_task",
    autoretry_for=(WildberriesServiceError, httpx.RequestError, httpx.TimeoutException),
    retry_kwargs={'max_retries': 5, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
async def sync_sales_task(self, shop_id: int, days_back: int = 7) -> dict:
    """
    Sync sales for a specific shop
    
    Args:
        shop_id: Shop ID to sync
        days_back: Number of days to sync back
        
    Returns:
        Sync result statistics
    """
    logger.info(f"Starting sync_sales_task for shop {shop_id}")
    
    try:
        from datetime import datetime, timedelta
        
        async with db_manager.get_async_session() as db:
            # Initialize services
            products_service = WBProductsService()
            feedbacks_service = WBFeedbacksService()
            sales_service = WBSalesService()
            
            sync_service = DataSyncService(
                products_service=products_service,
                feedbacks_service=feedbacks_service,
                sales_service=sales_service
            )
            
            # Calculate date range
            date_to = datetime.utcnow()
            date_from = date_to - timedelta(days=days_back)
            
            # Sync sales (append-only strategy)
            result = await sync_service.sync_sales(
                db=db,
                shop_id=shop_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"sync_sales_task completed for shop {shop_id}: {result}")
            return result
    
    except Exception as e:
        logger.error(f"sync_sales_task failed for shop {shop_id}: {e}")
        raise


@celery_app.task(
    bind=True,
    base=WorkflowDatabaseTask,
    name="tasks.sync.sync_reviews_task",
    autoretry_for=(WildberriesServiceError, httpx.RequestError, httpx.TimeoutException),
    retry_kwargs={'max_retries': 5, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
async def sync_reviews_task(self, shop_id: int, is_answered: bool = None) -> dict:
    """
    Sync reviews for a specific shop
    
    Args:
        shop_id: Shop ID to sync
        is_answered: Filter by answered status (None = all)
        
    Returns:
        Sync result statistics
    """
    logger.info(f"Starting sync_reviews_task for shop {shop_id}")
    
    try:
        async with db_manager.get_async_session() as db:
            # Initialize services
            products_service = WBProductsService()
            feedbacks_service = WBFeedbacksService()
            sales_service = WBSalesService()
            
            sync_service = DataSyncService(
                products_service=products_service,
                feedbacks_service=feedbacks_service,
                sales_service=sales_service
            )
            
            # Sync reviews
            result = await sync_service.sync_reviews(
                db=db,
                shop_id=shop_id,
                is_answered=is_answered
            )
            
            logger.info(f"sync_reviews_task completed for shop {shop_id}: {result}")
            return result
    
    except Exception as e:
        logger.error(f"sync_reviews_task failed for shop {shop_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.sync.sync_all_products_task")
async def sync_all_products_task(self) -> dict:
    """
    Sync products for all active shops
    
    Scheduled task that runs periodically.
    Spawns individual tasks for each shop via Celery queue.
    
    Returns:
        Summary of scheduled operations
    """
    logger.info("Starting sync_all_products_task for all shops")
    
    scheduled = []
    errors = 0
    
    try:
        async with db_manager.get_async_session() as db:
            # Get all active shops
            shops = await shop_repository.get_all(db, skip=0, limit=1000)
            
            logger.info(f"Found {len(shops)} shops to sync")
            
            for shop in shops:
                try:
                    # Schedule task via Celery (not direct call)
                    task = sync_products_task.delay(shop.id, limit=100)
                    scheduled.append({
                        "shop_id": shop.id,
                        "shop_name": shop.name,
                        "task_id": task.id,
                        "status": "scheduled"
                    })
                    logger.debug(f"Scheduled sync_products_task for shop {shop.id}, task_id: {task.id}")
                except Exception as e:
                    logger.error(f"Failed to schedule sync for shop {shop.id}: {e}")
                    errors += 1
            
            summary = {
                "total_shops": len(shops),
                "scheduled": len(scheduled),
                "errors": errors,
                "tasks": scheduled
            }
            
            logger.info(f"sync_all_products_task completed: {summary}")
            return summary
    
    except Exception as e:
        logger.error(f"sync_all_products_task failed: {e}")
        raise


@celery_app.task(bind=True, name="tasks.sync.sync_all_sales_task")
async def sync_all_sales_task(self, days_back: int = 1) -> dict:
    """
    Sync sales for all active shops
    
    Scheduled task that runs periodically.
    Spawns individual tasks for each shop via Celery queue.
    
    Args:
        days_back: Number of days to sync back
        
    Returns:
        Summary of scheduled operations
    """
    logger.info(f"Starting sync_all_sales_task for all shops (last {days_back} days)")
    
    scheduled = []
    errors = 0
    
    try:
        async with db_manager.get_async_session() as db:
            shops = await shop_repository.get_all(db, skip=0, limit=1000)
            
            logger.info(f"Found {len(shops)} shops to sync sales")
            
            for shop in shops:
                try:
                    # Schedule task via Celery
                    task = sync_sales_task.delay(shop.id, days_back=days_back)
                    scheduled.append({
                        "shop_id": shop.id,
                        "shop_name": shop.name,
                        "task_id": task.id,
                        "status": "scheduled"
                    })
                    logger.debug(f"Scheduled sync_sales_task for shop {shop.id}, task_id: {task.id}")
                except Exception as e:
                    logger.error(f"Failed to schedule sync for shop {shop.id}: {e}")
                    errors += 1
            
            summary = {
                "total_shops": len(shops),
                "scheduled": len(scheduled),
                "errors": errors,
                "tasks": scheduled
            }
            
            logger.info(f"sync_all_sales_task completed: {summary}")
            return summary
    
    except Exception as e:
        logger.error(f"sync_all_sales_task failed: {e}")
        raise


@celery_app.task(bind=True, name="tasks.sync.sync_all_reviews_task")
async def sync_all_reviews_task(self) -> dict:
    """
    Sync reviews for all active shops
    
    Scheduled task that runs periodically.
    Spawns individual tasks for each shop via Celery queue.
    
    Returns:
        Summary of scheduled operations
    """
    logger.info("Starting sync_all_reviews_task for all shops")
    
    scheduled = []
    errors = 0
    
    try:
        async with db_manager.get_async_session() as db:
            shops = await shop_repository.get_all(db, skip=0, limit=1000)
            
            logger.info(f"Found {len(shops)} shops to sync reviews")
            
            for shop in shops:
                try:
                    # Schedule task via Celery, sync only unanswered reviews
                    task = sync_reviews_task.delay(shop.id, is_answered=False)
                    scheduled.append({
                        "shop_id": shop.id,
                        "shop_name": shop.name,
                        "task_id": task.id,
                        "status": "scheduled"
                    })
                    logger.debug(f"Scheduled sync_reviews_task for shop {shop.id}, task_id: {task.id}")
                except Exception as e:
                    logger.error(f"Failed to schedule sync for shop {shop.id}: {e}")
                    errors += 1
            
            summary = {
                "total_shops": len(shops),
                "scheduled": len(scheduled),
                "errors": errors,
                "tasks": scheduled
            }
            
            logger.info(f"sync_all_reviews_task completed: {summary}")
            return summary
    
    except Exception as e:
        logger.error(f"sync_all_reviews_task failed: {e}")
        raise
