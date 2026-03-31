"""
Event Repository

Repository for Event model operations.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.event import Event
from .base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """Repository for Event operations"""

    def __init__(self):
        super().__init__(Event)

    async def get_by_shop(
        self,
        db: AsyncSession,
        shop_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        """Get events by shop"""
        result = await db.execute(
            select(Event)
            .where(Event.shop_id == shop_id)
            .order_by(Event.event_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent_by_source(
        self,
        db: AsyncSession,
        source: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        """Get recent events by source"""
        result = await db.execute(
            select(Event)
            .where(Event.source == source)
            .order_by(Event.event_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


event_repository = EventRepository()
