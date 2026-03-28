"""
FastAPI application for AI Marketplace Assistant

Main application module that initializes FastAPI and all components.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings, get_logger
from backend.database import db_manager, redis_manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting AI Marketplace Assistant backend")
    logger.info(f"Version: {settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database
    try:
        db_manager.init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Initialize Redis
    try:
        redis_manager.init_redis()
        logger.info("Redis initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    # Close database connections
    db_manager.close()
    
    # Close Redis connections
    redis_manager.close()
    
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        FastAPI application instance
    """
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered marketplace assistant for sellers",
        lifespan=lifespan,
        debug=settings.debug,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register API routers
    from backend.api import v1
    app.include_router(v1.router)
    
    # Root endpoint (kept for backward compatibility)
    @app.get("/", tags=["root"])
    async def root():
        """
        Root endpoint (deprecated)
        
        Use /api/v1/ instead.
        """
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "api_version": "v1",
            "status": "running",
            "message": "Use /api/v1/ for API access"
        }
    
    return app


# Create application instance
app = create_app()
