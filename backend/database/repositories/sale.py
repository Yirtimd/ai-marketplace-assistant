"""
Sale Repository

Repository for Sale model with specialized queries.
"""

from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.sale import Sale
from .base import BaseRepository


class SaleRepository(BaseRepository[Sale]):
    """Repository for Sale operations"""
    
    def __init__(self):
        super().__init__(Sale)
    
    async def get_by_shop(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sale]:
        """Get sales by shop"""
        return await self.get_many_by_field(db, "shop_id", shop_id, skip, limit)
    
    async def get_by_product(
        self,
        db: AsyncSession,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sale]:
        """Get sales by product"""
        return await self.get_many_by_field(db, "product_id", product_id, skip, limit)
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        shop_id: int,
        date_from: datetime,
        date_to: datetime
    ) -> List[Sale]:
        """Get sales in date range"""
        result = await db.execute(
            select(Sale)
            .where(Sale.shop_id == shop_id)
            .where(Sale.sale_date >= date_from)
            .where(Sale.sale_date <= date_to)
            .order_by(Sale.sale_date.desc())
        )
        return list(result.scalars().all())


sale_repository = SaleRepository()
