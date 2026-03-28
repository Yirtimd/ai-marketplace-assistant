"""
Review Repository

Repository for Review model with specialized queries.
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.review import Review
from .base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Repository for Review operations"""
    
    def __init__(self):
        super().__init__(Review)
    
    async def get_by_shop(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """Get reviews by shop"""
        return await self.get_many_by_field(db, "shop_id", shop_id, skip, limit)
    
    async def get_by_product(
        self,
        db: AsyncSession,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """Get reviews by product"""
        return await self.get_many_by_field(db, "product_id", product_id, skip, limit)
    
    async def get_unanswered(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """Get unanswered reviews"""
        result = await db.execute(
            select(Review)
            .where(Review.shop_id == shop_id)
            .where(Review.is_answered == False)
            .order_by(Review.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


review_repository = ReviewRepository()
