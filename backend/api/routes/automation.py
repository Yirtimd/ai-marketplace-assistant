"""
Automation API routes

Endpoints for Stage 11 automation controls.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import settings
from services.task_service import task_service
from services.automation_service import automation_service

router = APIRouter(prefix="/automation", tags=["Automation"])


class AutomationRunRequest(BaseModel):
    shop_id: Optional[int] = None
    execute_actions: Optional[bool] = None


@router.get("/config")
async def get_automation_config():
    """Get current automation settings."""
    return {
        "automation_enabled": settings.automation_enabled,
        "automation_execute_actions": settings.automation_execute_actions,
        "automation_sales_drop_threshold_pct": settings.automation_sales_drop_threshold_pct,
        "automation_low_stock_threshold": settings.automation_low_stock_threshold,
    }


@router.post("/run")
async def run_automation(request: AutomationRunRequest):
    """Run automation cycle synchronously (immediate result)."""
    try:
        return await automation_service.run_automation_cycle(
            shop_id=request.shop_id,
            execute_actions=request.execute_actions,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run-async")
async def run_automation_async(request: AutomationRunRequest):
    """Schedule automation cycle in Celery queue."""
    try:
        return await task_service.create_task(
            task_name="tasks.automation.run_automation_cycle_task",
            kwargs={
                "shop_id": request.shop_id,
                "execute_actions": request.execute_actions
                if request.execute_actions is not None
                else settings.automation_execute_actions,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
