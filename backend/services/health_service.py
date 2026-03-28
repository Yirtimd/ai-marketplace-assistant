"""
Health check service for AI Marketplace Assistant

This service provides health check functionality for all system components.
"""

from typing import Dict, Any
from dataclasses import dataclass

from backend.config import get_logger
from backend.database import db_manager, redis_manager

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    """Health status data class"""
    status: str  # "healthy" or "unhealthy"
    database: str  # "connected", "disconnected", "unknown"
    redis: str  # "connected", "disconnected", "unknown"
    version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status,
            "database": self.database,
            "redis": self.redis,
            "version": self.version
        }


class HealthService:
    """Health check service"""
    
    @staticmethod
    async def check_database() -> str:
        """
        Check database connection
        
        Returns:
            Connection status: "connected", "disconnected", or "unknown"
        """
        try:
            # Try to get database connection
            db_manager.get_redis()
            logger.debug("Database health check: connected")
            return "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "disconnected"
    
    @staticmethod
    async def check_redis() -> str:
        """
        Check Redis connection
        
        Returns:
            Connection status: "connected", "disconnected", or "unknown"
        """
        try:
            # Try to ping Redis
            redis_client = redis_manager.get_redis()
            redis_client.ping()
            logger.debug("Redis health check: connected")
            return "connected"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return "disconnected"
    
    @staticmethod
    async def get_health_status(version: str) -> HealthStatus:
        """
        Get overall health status
        
        Args:
            version: Application version
            
        Returns:
            HealthStatus object with all component statuses
        """
        # Check all components
        db_status = await HealthService.check_database()
        redis_status = await HealthService.check_redis()
        
        # Determine overall status
        overall_status = "healthy"
        if db_status == "disconnected" or redis_status == "disconnected":
            overall_status = "unhealthy"
        
        return HealthStatus(
            status=overall_status,
            database=db_status,
            redis=redis_status,
            version=version
        )


# Service instance
health_service = HealthService()
