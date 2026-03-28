"""
Product Repository

Repository for Product model with specialized queries.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.product import Product
from .base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository for Product operations"""
    
    def __init__(self):
        super().__init__(Product)
    
    async def get_by_nm_id(self, db: AsyncSession, nm_id: int) -> Optional[Product]:
        """Get product by Wildberries nmID"""
        return await self.get_by_field(db, "nm_id", nm_id)
    
    async def get_by_shop(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by shop"""
        return await self.get_many_by_field(db, "shop_id", shop_id, skip, limit)
    
    async def get_by_vendor_code(
        self,
        db: AsyncSession,
        vendor_code: str
    ) -> Optional[Product]:
        """Get product by vendor code"""
        return await self.get_by_field(db, "vendor_code", vendor_code)


product_repository = ProductRepository()
