"""
Base Repository Pattern for database operations

This module provides a generic base repository that other repositories can inherit from.
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository for CRUD operations
    
    This class provides common database operations that all repositories can use.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get all records with pagination"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(
        self,
        db: AsyncSession,
        id: int,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update a record"""
        await db.execute(
            update(self.model).where(self.model.id == id).values(**obj_in)
        )
        await db.commit()
        return await self.get_by_id(db, id)
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record"""
        result = await db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        field_value: Any
    ) -> Optional[ModelType]:
        """Get record by any field"""
        result = await db.execute(
            select(self.model).where(getattr(self.model, field_name) == field_value)
        )
        return result.scalar_one_or_none()
    
    async def get_many_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records by field"""
        result = await db.execute(
            select(self.model)
            .where(getattr(self.model, field_name) == field_value)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
