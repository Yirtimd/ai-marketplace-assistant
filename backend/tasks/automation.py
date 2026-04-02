"""
Automation tasks

Celery tasks for Stage 11 automation cycle.
"""

from celery_app import celery_app
from config import get_logger
from services.automation_service import automation_service
from tasks.singleton import SingletonTask

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    base=SingletonTask,
    name="tasks.automation.run_automation_cycle_task",
)
async def run_automation_cycle_task(
    self,
    shop_id: int = None,
    execute_actions: bool = False,
) -> dict:
    """
    Run automation cycle for one shop or all shops.
    """
    logger.info(
        "run_automation_cycle_task started, shop_id=%s, execute_actions=%s",
        shop_id,
        execute_actions,
    )
    result = await automation_service.run_automation_cycle(
        shop_id=shop_id,
        execute_actions=execute_actions,
    )
    logger.info("run_automation_cycle_task completed")
    return result
