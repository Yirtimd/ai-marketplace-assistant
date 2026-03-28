"""
TaskExecution Repository

Repository for managing task execution records.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.base import BaseRepository
from database.models.task_execution import TaskExecution


class TaskExecutionRepository(BaseRepository[TaskExecution]):
    """Repository for TaskExecution model"""
    
    def __init__(self):
        super().__init__(TaskExecution)
    
    async def get_by_task_id(self, db: AsyncSession, task_id: str) -> Optional[TaskExecution]:
        """Get execution by Celery task ID"""
        query = select(TaskExecution).where(TaskExecution.task_id == task_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_shop(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskExecution]:
        """Get executions by shop"""
        query = (
            select(TaskExecution)
            .where(TaskExecution.shop_id == shop_id)
            .order_by(TaskExecution.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_task_name(
        self,
        db: AsyncSession,
        task_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskExecution]:
        """Get executions by task name"""
        query = (
            select(TaskExecution)
            .where(TaskExecution.task_name == task_name)
            .order_by(TaskExecution.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(
        self,
        db: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskExecution]:
        """Get executions by status"""
        query = (
            select(TaskExecution)
            .where(TaskExecution.status == status)
            .order_by(TaskExecution.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
        shop_id: Optional[int] = None,
        task_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskExecution]:
        """Get executions by date range with optional filters"""
        conditions = [
            TaskExecution.started_at >= date_from,
            TaskExecution.started_at <= date_to
        ]
        
        if shop_id:
            conditions.append(TaskExecution.shop_id == shop_id)
        
        if task_name:
            conditions.append(TaskExecution.task_name == task_name)
        
        query = (
            select(TaskExecution)
            .where(and_(*conditions))
            .order_by(TaskExecution.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_failed_executions(
        self,
        db: AsyncSession,
        hours_back: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskExecution]:
        """Get recent failed executions"""
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = (
            select(TaskExecution)
            .where(
                and_(
                    TaskExecution.status == "failed",
                    TaskExecution.started_at >= cutoff_time
                )
            )
            .order_by(TaskExecution.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_workflow(
        self,
        db: AsyncSession,
        workflow_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskExecution]:
        """Get executions by workflow ID"""
        query = (
            select(TaskExecution)
            .where(TaskExecution.workflow_id == workflow_id)
            .order_by(TaskExecution.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


# Singleton instance
task_execution_repository = TaskExecutionRepository()
