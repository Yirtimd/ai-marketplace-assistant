"""
Database module for AI Marketplace Assistant

This module provides database connection and session management using SQLAlchemy.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator, Generator

from backend.config import settings, get_logger
from backend.database.base import Base

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection and session manager"""
    
    def __init__(self):
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
    
    def init_db(self) -> None:
        """Initialize database connection"""
        if self._engine is not None:
            logger.warning("Database already initialized")
            return
        
        logger.info("Initializing database connection")
        
        # Create synchronous engine
        self._engine = create_engine(
            str(settings.database_url),
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
        )
        
        # Create session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info("Database connection initialized")
    
    def init_async_db(self) -> None:
        """Initialize async database connection"""
        if self._async_engine is not None:
            logger.warning("Async database already initialized")
            return
        
        logger.info("Initializing async database connection")
        
        # Convert postgresql:// to postgresql+asyncpg://
        async_url = str(settings.database_url).replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        
        # Create async engine
        self._async_engine = create_async_engine(
            async_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
        )
        
        # Create async session factory
        self._async_session_factory = async_sessionmaker(
            bind=self._async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info("Async database connection initialized")
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session
        
        Yields:
            Database session
        """
        if self._session_factory is None:
            self.init_db()
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncIterator[AsyncSession]:
        """
        Get async database session
        
        Yields:
            Async database session
        """
        if self._async_session_factory is None:
            self.init_async_db()
        
        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database session error: {e}")
                raise
    
    def create_all_tables(self) -> None:
        """Create all database tables"""
        if self._engine is None:
            self.init_db()
        
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=self._engine)
        logger.info("Database tables created")
    
    async def create_all_tables_async(self) -> None:
        """Create all database tables asynchronously"""
        if self._async_engine is None:
            self.init_async_db()
        
        logger.info("Creating database tables (async)")
        async with self._async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (async)")
    
    def close(self) -> None:
        """Close database connections"""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection closed")
        
        if self._async_engine:
            self._async_engine.sync_engine.dispose()
            logger.info("Async database connection closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session in FastAPI endpoints
    
    Yields:
        Database session
    """
    yield from db_manager.get_session()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session in FastAPI endpoints
    
    Yields:
        Async database session
    """
    async with db_manager.get_async_session() as session:
        yield session
