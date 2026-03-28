"""
Redis connection module for AI Marketplace Assistant

This module provides Redis connection management for:
- Caching
- Task queues
- Session storage
- Temporary state
"""

import redis
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from typing import Optional

from backend.config import settings, get_logger

logger = get_logger(__name__)


class RedisManager:
    """Redis connection manager"""
    
    def __init__(self):
        self._redis_client: Optional[Redis] = None
        self._async_redis_client: Optional[AsyncRedis] = None
    
    def init_redis(self) -> None:
        """Initialize Redis connection"""
        if self._redis_client is not None:
            logger.warning("Redis already initialized")
            return
        
        logger.info("Initializing Redis connection")
        
        try:
            # Parse Redis URL
            redis_url = str(settings.redis_url)
            
            # Create Redis client
            self._redis_client = redis.from_url(
                redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            
            # Test connection
            self._redis_client.ping()
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def init_async_redis(self) -> None:
        """Initialize async Redis connection"""
        if self._async_redis_client is not None:
            logger.warning("Async Redis already initialized")
            return
        
        logger.info("Initializing async Redis connection")
        
        try:
            # Parse Redis URL
            redis_url = str(settings.redis_url)
            
            # Create async Redis client
            self._async_redis_client = await AsyncRedis.from_url(
                redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            
            # Test connection
            await self._async_redis_client.ping()
            logger.info("Async Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize async Redis: {e}")
            raise
    
    def get_redis(self) -> Redis:
        """
        Get Redis client
        
        Returns:
            Redis client instance
        """
        if self._redis_client is None:
            self.init_redis()
        return self._redis_client
    
    async def get_async_redis(self) -> AsyncRedis:
        """
        Get async Redis client
        
        Returns:
            Async Redis client instance
        """
        if self._async_redis_client is None:
            await self.init_async_redis()
        return self._async_redis_client
    
    def close(self) -> None:
        """Close Redis connections"""
        if self._redis_client:
            self._redis_client.close()
            logger.info("Redis connection closed")
    
    async def close_async(self) -> None:
        """Close async Redis connections"""
        if self._async_redis_client:
            await self._async_redis_client.close()
            logger.info("Async Redis connection closed")
    
    def set_value(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set a value in Redis
        
        Args:
            key: Redis key
            value: Value to store
            expire: Expiration time in seconds
            
        Returns:
            True if successful
        """
        client = self.get_redis()
        return client.set(key, value, ex=expire)
    
    def get_value(self, key: str) -> Optional[str]:
        """
        Get a value from Redis
        
        Args:
            key: Redis key
            
        Returns:
            Value or None if not found
        """
        client = self.get_redis()
        return client.get(key)
    
    def delete_value(self, key: str) -> int:
        """
        Delete a value from Redis
        
        Args:
            key: Redis key
            
        Returns:
            Number of keys deleted
        """
        client = self.get_redis()
        return client.delete(key)
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis
        
        Args:
            key: Redis key
            
        Returns:
            True if key exists
        """
        client = self.get_redis()
        return client.exists(key) > 0


# Global Redis manager instance
redis_manager = RedisManager()


def get_redis_client() -> Redis:
    """
    Dependency for getting Redis client in FastAPI endpoints
    
    Returns:
        Redis client
    """
    return redis_manager.get_redis()


async def get_async_redis_client() -> AsyncRedis:
    """
    Dependency for getting async Redis client in FastAPI endpoints
    
    Returns:
        Async Redis client
    """
    return await redis_manager.get_async_redis()
