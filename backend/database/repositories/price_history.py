"""
Price History Repository

Repository for PriceHistory model with time-series queries.
"""

from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.price_history import PriceHistory
from .base import BaseRepository


class PriceHistoryRepository(BaseRepository[PriceHistory]):
    """Repository for PriceHistory operations"""
    
    def __init__(self):
        super().__init__(PriceHistory)
    
    async def get_by_product(
        self,
        db: AsyncSession,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[PriceHistory]:
        """Get price history by product"""
        return await self.get_many_by_field(db, "product_id", product_id, skip, limit)
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        product_id: int,
        date_from: datetime,
        date_to: datetime
    ) -> List[PriceHistory]:
        """Get price history in date range"""
        result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .where(PriceHistory.changed_at >= date_from)
            .where(PriceHistory.changed_at <= date_to)
            .order_by(PriceHistory.changed_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_latest(
        self,
        db: AsyncSession,
        product_id: int
    ) -> PriceHistory:
        """Get latest price history record"""
        result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.changed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


price_history_repository = PriceHistoryRepository()
