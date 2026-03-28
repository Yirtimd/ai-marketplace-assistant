"""
Stock History Repository

Repository for StockHistory model with time-series queries.
"""

from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.stock_history import StockHistory
from .base import BaseRepository


class StockHistoryRepository(BaseRepository[StockHistory]):
    """Repository for StockHistory operations"""
    
    def __init__(self):
        super().__init__(StockHistory)
    
    async def get_by_product(
        self,
        db: AsyncSession,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockHistory]:
        """Get stock history by product"""
        return await self.get_many_by_field(db, "product_id", product_id, skip, limit)
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        product_id: int,
        date_from: datetime,
        date_to: datetime
    ) -> List[StockHistory]:
        """Get stock history in date range"""
        result = await db.execute(
            select(StockHistory)
            .where(StockHistory.product_id == product_id)
            .where(StockHistory.recorded_at >= date_from)
            .where(StockHistory.recorded_at <= date_to)
            .order_by(StockHistory.recorded_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_latest(
        self,
        db: AsyncSession,
        product_id: int
    ) -> StockHistory:
        """Get latest stock history record"""
        result = await db.execute(
            select(StockHistory)
            .where(StockHistory.product_id == product_id)
            .order_by(StockHistory.recorded_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


stock_history_repository = StockHistoryRepository()
