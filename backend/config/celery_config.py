"""
Celery configuration module

Configures Celery with Redis as broker and backend.
"""

from typing import Dict, Any


class CeleryConfig:
    """Celery configuration class"""
    
    # Broker settings
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
    
    # Task settings
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: list = ["json"]
    timezone: str = "UTC"
    enable_utc: bool = True
    
    # Task execution settings
    task_track_started: bool = True
    task_time_limit: int = 30 * 60  # 30 minutes
    task_soft_time_limit: int = 25 * 60  # 25 minutes
    task_acks_late: bool = True
    task_reject_on_worker_lost: bool = True
    
    # Autoretry settings for transient failures
    task_autoretry_for: tuple = (
        Exception,  # Retry on any exception (can be refined)
    )
    task_retry_kwargs: dict = {
        'max_retries': 5,
        'countdown': 5  # Initial delay (5 seconds)
    }
    task_retry_backoff: bool = True  # Enable exponential backoff
    task_retry_backoff_max: int = 600  # Max delay: 10 minutes
    task_retry_jitter: bool = True  # Add random jitter to prevent thundering herd
    
    # Result backend settings
    result_expires: int = 3600  # 1 hour
    result_persistent: bool = True
    
    # Worker settings
    worker_prefetch_multiplier: int = 4
    worker_max_tasks_per_child: int = 1000
    worker_disable_rate_limits: bool = False
    
    # Rate limiting for sync tasks
    task_annotations: Dict[str, Dict[str, Any]] = {
        'tasks.sync.sync_products_task': {'rate_limit': '10/m'},  # 10 per minute
        'tasks.sync.sync_sales_task': {'rate_limit': '10/m'},
        'tasks.sync.sync_reviews_task': {'rate_limit': '10/m'},
    }
    
    # Beat schedule settings
    beat_schedule: Dict[str, Any] = {
        # Sync products every 6 hours
        "sync-products-every-6-hours": {
            "task": "tasks.sync.sync_all_products_task",
            "schedule": 6 * 60 * 60,  # 6 hours in seconds
        },
        # Sync sales every hour
        "sync-sales-every-hour": {
            "task": "tasks.sync.sync_all_sales_task",
            "schedule": 60 * 60,  # 1 hour in seconds
        },
        # Sync reviews every 2 hours
        "sync-reviews-every-2-hours": {
            "task": "tasks.sync.sync_all_reviews_task",
            "schedule": 2 * 60 * 60,  # 2 hours in seconds
        },
        # Check stock levels every 30 minutes
        "check-stock-levels-every-30-min": {
            "task": "tasks.monitoring.check_stock_levels_task",
            "schedule": 30 * 60,  # 30 minutes in seconds
        },
        # Stage 11 automation cycle every 15 minutes
        "run-automation-cycle-every-15-min": {
            "task": "tasks.automation.run_automation_cycle_task",
            "schedule": 15 * 60,  # 15 minutes in seconds
            "kwargs": {
                "execute_actions": False
            }
        },
    }


def get_celery_config() -> CeleryConfig:
    """Get Celery configuration instance"""
    return CeleryConfig()
