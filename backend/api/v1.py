"""
API v1 router for AI Marketplace Assistant

This module contains all v1 API routes.
"""

from fastapi import APIRouter, Depends

from backend.config import settings, dependencies
from backend.services.health_service import health_service
from backend.api.routes import products, feedbacks, sales, ai, actions

# Create v1 router
router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/")
async def root():
    """
    Root endpoint
    
    Returns basic information about the API.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "api_version": "v1",
        "status": "running"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Checks the status of all system components:
    - Database (PostgreSQL)
    - Redis
    
    Returns:
        Health status of all components
    """
    health_status = await health_service.get_health_status(settings.app_version)
    return health_status.to_dict()


# Include route groups
router.include_router(products.router)
router.include_router(feedbacks.router)
router.include_router(sales.router)
router.include_router(ai.router)
router.include_router(actions.router)

# Import and include tasks router
from backend.api.routes import tasks
router.include_router(tasks.router)

# Import and include workflows router
from backend.api.routes import workflows
router.include_router(workflows.router)

