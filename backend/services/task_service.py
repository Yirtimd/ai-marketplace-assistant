"""
Task Service

Service for managing Celery tasks: creation, monitoring, cancellation.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from celery.result import AsyncResult
from celery_app import celery_app
from config import get_logger
from database.models.task import TaskStatus

logger = get_logger(__name__)


class TaskService:
    """Service for task management"""
    
    def __init__(self):
        self.celery = celery_app
    
    async def create_task(
        self,
        task_name: str,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        eta: Optional[datetime] = None,
        countdown: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create and execute a Celery task
        
        Args:
            task_name: Full task name (e.g., 'tasks.sync.sync_products_task')
            args: Positional arguments for task
            kwargs: Keyword arguments for task
            eta: Exact time to execute task
            countdown: Seconds to wait before executing
            
        Returns:
            Task info including task_id
        """
        logger.info(f"Creating task: {task_name}")
        
        try:
            task = self.celery.send_task(
                task_name,
                args=args or (),
                kwargs=kwargs or {},
                eta=eta,
                countdown=countdown
            )
            
            result = {
                "task_id": task.id,
                "task_name": task_name,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Task created: {task.id}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to create task {task_name}: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status and result
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Task status information
        """
        try:
            result = AsyncResult(task_id, app=self.celery)
            
            status_map = {
                "PENDING": TaskStatus.PENDING,
                "STARTED": TaskStatus.IN_PROGRESS,
                "SUCCESS": TaskStatus.COMPLETED,
                "FAILURE": TaskStatus.FAILED,
                "REVOKED": TaskStatus.CANCELLED,
                "RETRY": TaskStatus.IN_PROGRESS,
            }
            
            status_info = {
                "task_id": task_id,
                "status": status_map.get(result.state, result.state),
                "state": result.state,
            }
            
            if result.ready():
                if result.successful():
                    status_info["result"] = result.result
                else:
                    status_info["error"] = str(result.info)
            
            return status_info
        
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            raise
    
    async def cancel_task(self, task_id: str, terminate: bool = False) -> Dict[str, Any]:
        """
        Cancel a running task
        
        Args:
            task_id: Celery task ID
            terminate: Force terminate (default: False)
            
        Returns:
            Cancellation result
        """
        logger.info(f"Cancelling task: {task_id}, terminate={terminate}")
        
        try:
            result = AsyncResult(task_id, app=self.celery)
            result.revoke(terminate=terminate)
            
            return {
                "task_id": task_id,
                "status": "cancelled",
                "terminated": terminate
            }
        
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            raise
    
    async def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of all active tasks
        
        Returns:
            List of active tasks
        """
        try:
            inspect = self.celery.control.inspect()
            
            active_tasks = []
            
            # Get active tasks from all workers
            active = inspect.active()
            if active:
                for worker, tasks in active.items():
                    for task in tasks:
                        active_tasks.append({
                            "task_id": task["id"],
                            "task_name": task["name"],
                            "worker": worker,
                            "args": task.get("args", []),
                            "kwargs": task.get("kwargs", {}),
                        })
            
            return active_tasks
        
        except Exception as e:
            logger.error(f"Failed to get active tasks: {e}")
            raise
    
    async def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduled (pending) tasks
        
        Returns:
            List of scheduled tasks
        """
        try:
            inspect = self.celery.control.inspect()
            
            scheduled_tasks = []
            
            # Get scheduled tasks from all workers
            scheduled = inspect.scheduled()
            if scheduled:
                for worker, tasks in scheduled.items():
                    for task in tasks:
                        scheduled_tasks.append({
                            "task_id": task["request"]["id"],
                            "task_name": task["request"]["name"],
                            "worker": worker,
                            "eta": task.get("eta"),
                        })
            
            return scheduled_tasks
        
        except Exception as e:
            logger.error(f"Failed to get scheduled tasks: {e}")
            raise
    
    async def trigger_sync_products(self, shop_id: int, limit: int = 100) -> Dict[str, Any]:
        """Trigger product sync task"""
        return await self.create_task(
            "tasks.sync.sync_products_task",
            kwargs={"shop_id": shop_id, "limit": limit}
        )
    
    async def trigger_sync_sales(self, shop_id: int, days_back: int = 7) -> Dict[str, Any]:
        """Trigger sales sync task"""
        return await self.create_task(
            "tasks.sync.sync_sales_task",
            kwargs={"shop_id": shop_id, "days_back": days_back}
        )
    
    async def trigger_sync_reviews(self, shop_id: int) -> Dict[str, Any]:
        """Trigger reviews sync task"""
        return await self.create_task(
            "tasks.sync.sync_reviews_task",
            kwargs={"shop_id": shop_id}
        )


# Singleton instance
task_service = TaskService()
