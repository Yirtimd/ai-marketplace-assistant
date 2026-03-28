"""
Rating History Repository

Repository for RatingHistory model with time-series queries.
"""

from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.rating_history import RatingHistory
from .base import BaseRepository


class RatingHistoryRepository(BaseRepository[RatingHistory]):
    """Repository for RatingHistory operations"""
    
    def __init__(self):
        super().__init__(RatingHistory)
    
    async def get_by_product(
        self,
        db: AsyncSession,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[RatingHistory]:
        """Get rating history by product"""
        return await self.get_many_by_field(db, "product_id", product_id, skip, limit)
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        product_id: int,
        date_from: datetime,
        date_to: datetime
    ) -> List[RatingHistory]:
        """Get rating history in date range"""
        result = await db.execute(
            select(RatingHistory)
            .where(RatingHistory.product_id == product_id)
            .where(RatingHistory.recorded_at >= date_from)
            .where(RatingHistory.recorded_at <= date_to)
            .order_by(RatingHistory.recorded_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_latest(
        self,
        db: AsyncSession,
        product_id: int
    ) -> RatingHistory:
        """Get latest rating history record"""
        result = await db.execute(
            select(RatingHistory)
            .where(RatingHistory.product_id == product_id)
            .order_by(RatingHistory.recorded_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


rating_history_repository = RatingHistoryRepository()
