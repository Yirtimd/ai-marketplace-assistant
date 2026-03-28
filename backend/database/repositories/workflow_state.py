"""
WorkflowState Repository

Repository for managing workflow execution state.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.base import BaseRepository
from database.models.workflow_state import WorkflowState, WorkflowStatus


class WorkflowStateRepository(BaseRepository[WorkflowState]):
    """Repository for WorkflowState model"""
    
    def __init__(self):
        super().__init__(WorkflowState)
    
    async def get_by_workflow_id(
        self,
        db: AsyncSession,
        workflow_id: str
    ) -> Optional[WorkflowState]:
        """Get workflow state by workflow ID"""
        query = select(WorkflowState).where(WorkflowState.workflow_id == workflow_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowState]:
        """Get workflows by user"""
        query = (
            select(WorkflowState)
            .where(WorkflowState.user_id == user_id)
            .order_by(WorkflowState.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_shop(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowState]:
        """Get workflows by shop"""
        query = (
            select(WorkflowState)
            .where(WorkflowState.shop_id == shop_id)
            .order_by(WorkflowState.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(
        self,
        db: AsyncSession,
        status: WorkflowStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowState]:
        """Get workflows by status"""
        query = (
            select(WorkflowState)
            .where(WorkflowState.status == status)
            .order_by(WorkflowState.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_running_workflows(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowState]:
        """Get currently running workflows"""
        return await self.get_by_status(db, WorkflowStatus.RUNNING, skip, limit)


# Singleton instance
workflow_state_repository = WorkflowStateRepository()
