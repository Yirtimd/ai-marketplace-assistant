"""
Tasks API routes

Endpoints for triggering and managing Celery tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime

from services.task_service import task_service, TaskService
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Request/Response models
class TriggerSyncRequest(BaseModel):
    """Request to trigger sync task"""
    shop_id: int
    limit: Optional[int] = 100


class TriggerSalesSync(BaseModel):
    """Request to trigger sales sync"""
    shop_id: int
    days_back: Optional[int] = 7


class TaskResponse(BaseModel):
    """Task creation response"""
    task_id: str
    task_name: str
    status: str
    created_at: str


class TaskStatusResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: str
    state: str
    result: Optional[dict] = None
    error: Optional[str] = None


# Dependency
def get_task_service() -> TaskService:
    """Get TaskService instance"""
    return task_service


# === Trigger tasks endpoints ===

@router.post("/sync/products", response_model=TaskResponse)
async def trigger_sync_products(
    request: TriggerSyncRequest,
    service: TaskService = Depends(get_task_service)
):
    """
    Trigger product synchronization task
    
    Starts a background task to sync products from Wildberries API.
    """
    try:
        result = await service.trigger_sync_products(
            shop_id=request.shop_id,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/sales", response_model=TaskResponse)
async def trigger_sync_sales(
    request: TriggerSalesSync,
    service: TaskService = Depends(get_task_service)
):
    """
    Trigger sales synchronization task
    
    Starts a background task to sync sales from Wildberries API.
    """
    try:
        result = await service.trigger_sync_sales(
            shop_id=request.shop_id,
            days_back=request.days_back
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/reviews", response_model=TaskResponse)
async def trigger_sync_reviews(
    shop_id: int = Query(..., description="Shop ID to sync"),
    service: TaskService = Depends(get_task_service)
):
    """
    Trigger reviews synchronization task
    
    Starts a background task to sync reviews from Wildberries API.
    """
    try:
        result = await service.trigger_sync_reviews(shop_id=shop_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Task status endpoints ===

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    """
    Get task status by ID
    
    Returns current status and result of a task.
    """
    try:
        status = await service.get_task_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    terminate: bool = Query(False, description="Force terminate"),
    service: TaskService = Depends(get_task_service)
):
    """
    Cancel a running task
    
    Revokes the task. Use terminate=true to force kill.
    """
    try:
        result = await service.cancel_task(task_id, terminate=terminate)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
async def list_tasks(
    service: TaskService = Depends(get_task_service)
):
    """
    List all active and scheduled tasks
    
    Returns lists of currently running and scheduled tasks.
    """
    try:
        active = await service.get_active_tasks()
        scheduled = await service.get_scheduled_tasks()
        
        return {
            "active": active,
            "scheduled": scheduled,
            "total_active": len(active),
            "total_scheduled": len(scheduled)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
