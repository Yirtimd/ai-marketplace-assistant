"""
Shop Repository

Repository for Shop model with specialized queries.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.shop import Shop
from .base import BaseRepository


class ShopRepository(BaseRepository[Shop]):
    """Repository for Shop operations"""
    
    def __init__(self):
        super().__init__(Shop)
    
    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Shop]:
        """Get shops by user"""
        return await self.get_many_by_field(db, "user_id", user_id, skip, limit)
    
    async def get_by_supplier_id(
        self,
        db: AsyncSession,
        supplier_id: str
    ) -> Optional[Shop]:
        """Get shop by WB supplier ID"""
        return await self.get_by_field(db, "wb_supplier_id", supplier_id)


shop_repository = ShopRepository()
