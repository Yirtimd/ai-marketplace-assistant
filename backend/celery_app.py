"""
Celery application instance

Main Celery app configuration and initialization.
"""

from celery import Celery
from config.celery_config import get_celery_config
from config import get_logger

logger = get_logger(__name__)

# Create Celery application
celery_app = Celery("ai_marketplace_assistant")

# Load configuration
celery_config = get_celery_config()
celery_app.config_from_object(celery_config)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "tasks.sync",
    "tasks.monitoring",
    "tasks.analytics",
    "tasks.automation",
])

logger.info("Celery application initialized")


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    logger.info(f"Request: {self.request!r}")
    return f"Task executed: {self.request.id}"
