"""
Dependency injection container for AI Marketplace Assistant

This module provides centralized dependency injection for FastAPI endpoints.
All dependencies should be defined here for better testability and maintainability.
"""

from typing import AsyncGenerator, Generator
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings, Settings
from backend.database import db_manager, redis_manager


# ============================================
# Configuration Dependencies
# ============================================

def get_settings() -> Settings:
    """
    Get application settings
    
    Returns:
        Application settings instance
        
    Example:
        ```python
        @app.get("/info")
        async def info(settings: Settings = Depends(get_settings)):
            return {"app_name": settings.app_name}
        ```
    """
    return settings


# ============================================
# Database Dependencies
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    Get synchronous database session
    
    Yields:
        SQLAlchemy session
        
    Example:
        ```python
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            return db.query(Product).all()
        ```
    """
    yield from db_manager.get_session()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session
    
    Yields:
        Async SQLAlchemy session
        
    Example:
        ```python
        @app.get("/products")
        async def get_products(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Product))
            return result.scalars().all()
        ```
    """
    async with db_manager.get_async_session() as session:
        yield session


# ============================================
# Redis Dependencies
# ============================================

def get_redis() -> Redis:
    """
    Get synchronous Redis client
    
    Returns:
        Redis client instance
        
    Example:
        ```python
        @app.get("/cache")
        def get_cache(redis: Redis = Depends(get_redis)):
            return redis.get("key")
        ```
    """
    return redis_manager.get_redis()


async def get_async_redis() -> AsyncRedis:
    """
    Get async Redis client
    
    Returns:
        Async Redis client instance
        
    Example:
        ```python
        @app.get("/cache")
        async def get_cache(redis: AsyncRedis = Depends(get_async_redis)):
            return await redis.get("key")
        ```
    """
    return await redis_manager.get_async_redis()


# ============================================
# Services Dependencies
# ============================================

def get_wb_products_service():
    """Get Wildberries Products service instance"""
    from backend.services.wildberries import WBProductsService
    return WBProductsService()


def get_wb_feedbacks_service():
    """Get Wildberries Feedbacks service instance"""
    from backend.services.wildberries import WBFeedbacksService
    return WBFeedbacksService()


def get_wb_sales_service():
    """Get Wildberries Sales service instance"""
    from backend.services.wildberries import WBSalesService
    return WBSalesService()


# ============================================
# Future Dependencies
# ============================================

# These will be added in future stages:
# - get_current_user() - authentication
# - get_ai_service() - AI service instance
# - get_orchestrator() - workflow orchestrator
