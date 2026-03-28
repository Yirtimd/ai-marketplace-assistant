"""
Event Listener Service

Listens to system events and triggers appropriate actions (tasks, workflows).
"""

from typing import Optional
from config import get_logger
from database.models.event import Event, EventType
from tasks.monitoring import check_stock_levels_task

logger = get_logger(__name__)


class EventListener:
    """
    Event listener that triggers tasks and workflows based on system events
    
    Integrated with Orchestrator to trigger AI workflows.
    """
    
    def __init__(self):
        self._orchestrator = None  # Lazy initialization to avoid circular imports
    
    @property
    def orchestrator(self):
        """Lazy load orchestrator"""
        if self._orchestrator is None:
            from orchestrator import orchestrator
            self._orchestrator = orchestrator
        return self._orchestrator
    
    async def on_event(self, event: Event):
        """
        Main event handler - routes events to specific handlers
        
        Args:
            event: System event
        """
        logger.info(f"Processing event: {event.type}, level: {event.level}")
        
        try:
            # Route event to appropriate handler
            handler = self._get_handler(event.type)
            if handler:
                await handler(event)
            else:
                logger.debug(f"No handler for event type: {event.type}")
        
        except Exception as e:
            logger.error(f"Failed to handle event {event.id}: {e}")
    
    def _get_handler(self, event_type: EventType):
        """Get handler method for event type"""
        handlers = {
            EventType.LOW_STOCK: self.on_low_stock,
            EventType.NEGATIVE_REVIEW: self.on_negative_review,
            EventType.SYNC_COMPLETED: self.on_sync_completed,
            EventType.SYNC_FAILED: self.on_sync_failed,
            EventType.PRICE_CHANGED: self.on_price_changed,
        }
        return handlers.get(event_type)
    
    async def on_low_stock(self, event: Event):
        """
        Handle low stock event
        
        Triggers:
        - Immediate stock check for affected shop
        - AI workflow for inventory analysis
        """
        logger.warning(f"Low stock detected: {event.details}")
        
        shop_id = event.shop_id
        product_id = event.details.get("product_id")
        
        if shop_id:
            # Trigger stock check task
            task = check_stock_levels_task.delay(threshold=10)
            logger.info(f"Triggered stock check task: {task.id}")
            
            # Trigger AI workflow for inventory recommendations
            workflow_result = await self.orchestrator.execute_workflow(
                workflow_name="inventory_workflow",
                context={
                    "shop_id": shop_id,
                    "product_id": product_id,
                    "threshold": 10,
                    "trigger": "low_stock_event"
                },
                shop_id=shop_id
            )
            logger.info(f"Triggered check_inventory workflow: {workflow_result.get('workflow_id')}")
    
    async def on_negative_review(self, event: Event):
        """
        Handle negative review event
        
        Triggers:
        - (Future) AI workflow for review response generation
        """
        logger.warning(f"Negative review detected: {event.details}")
        
        shop_id = event.shop_id
        review_id = event.details.get("review_id")
        
        if shop_id:
            # Stage 7: review workflow is available
            # workflow_result = await self.orchestrator.execute_workflow(
            #     workflow_name="review_workflow",
            #     context={"shop_id": shop_id, "review_id": review_id},
            #     shop_id=shop_id
            # )
            logger.info(f"Would trigger review response workflow for shop {shop_id}, review {review_id}")
    
    async def on_sync_completed(self, event: Event):
        """
        Handle sync completion event
        
        Logs successful sync and optionally triggers dependent syncs.
        """
        logger.info(f"Sync completed: {event.details}")
        
        task_name = event.details.get("task_name")
        shop_id = event.shop_id
        
        # Example: After products sync, trigger sales sync
        if task_name == "sync_products_task" and shop_id:
            logger.info(f"Products synced for shop {shop_id}, considering sales sync")
            # Optionally trigger sales sync
            # sync_sales_task.delay(shop_id=shop_id, days_back=1)
    
    async def on_sync_failed(self, event: Event):
        """
        Handle sync failure event
        
        Logs error and optionally sends alert.
        """
        logger.error(f"Sync failed: {event.details}")
        
        # TODO: Send alert to monitoring system
        # alert_service.send_alert(f"Sync failed: {event.details}")
    
    async def on_price_changed(self, event: Event):
        """
        Handle price change event
        
        Triggers:
        - (Future) AI workflow for competitive pricing analysis
        """
        logger.info(f"Price changed: {event.details}")
        
        shop_id = event.shop_id
        product_id = event.details.get("product_id")
        old_price = event.details.get("old_price")
        new_price = event.details.get("new_price")
        
        if shop_id and product_id:
            logger.info(
                f"Product {product_id} price changed: {old_price} -> {new_price} "
                f"for shop {shop_id}"
            )
            # Stage 7: pricing workflow is available
            # workflow_result = await self.orchestrator.execute_workflow(
            #     workflow_name="pricing_workflow",
            #     context={
            #         "shop_id": shop_id,
            #         "product_id": product_id,
            #         "old_price": old_price,
            #         "new_price": new_price
            #     },
            #     shop_id=shop_id
            # )


# Singleton instance
event_listener = EventListener()
