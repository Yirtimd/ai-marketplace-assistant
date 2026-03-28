"""
Singleton Task implementation with Redis locking

Prevents concurrent execution of the same task with same arguments.
"""

from celery import Task
from redis import Redis
from typing import Any, Tuple
import hashlib
import json
from config import get_logger, settings

logger = get_logger(__name__)


class SingletonTask(Task):
    """
    Base task that ensures only one instance runs at a time for given arguments.
    
    Uses Redis for distributed locking across multiple workers.
    """
    
    _redis_client = None
    
    @property
    def redis_client(self) -> Redis:
        """Get Redis client (lazy initialization)"""
        if self._redis_client is None:
            self._redis_client = Redis.from_url(
                settings.redis_url or "redis://localhost:6379/0",
                decode_responses=True
            )
        return self._redis_client
    
    def _generate_lock_key(self, args: Tuple, kwargs: dict) -> str:
        """
        Generate unique lock key based on task name and arguments
        
        Args:
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Redis key for lock
        """
        # Create deterministic hash of arguments
        args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        args_hash = hashlib.md5(args_str.encode()).hexdigest()
        
        return f"task_lock:{self.name}:{args_hash}"
    
    def __call__(self, *args, **kwargs):
        """
        Execute task with singleton lock
        
        If task with same arguments is already running, skip execution.
        """
        lock_key = self._generate_lock_key(args, kwargs)
        
        # Try to acquire lock (TTL = task_time_limit + buffer)
        lock_timeout = 1800  # 30 minutes (same as task_time_limit)
        lock_acquired = self.redis_client.set(
            lock_key,
            "locked",
            nx=True,  # Only set if not exists
            ex=lock_timeout
        )
        
        if not lock_acquired:
            logger.warning(
                f"Task {self.name} already running with same arguments, skipping. "
                f"Lock key: {lock_key}"
            )
            return {
                "status": "skipped",
                "reason": "already_running",
                "lock_key": lock_key
            }
        
        logger.info(f"Lock acquired for task {self.name}, lock_key: {lock_key}")
        
        try:
            # Execute the task
            result = super().__call__(*args, **kwargs)
            return result
        
        except Exception as e:
            logger.error(f"Task {self.name} failed: {e}")
            raise
        
        finally:
            # Always release lock
            self.redis_client.delete(lock_key)
            logger.info(f"Lock released for task {self.name}, lock_key: {lock_key}")
