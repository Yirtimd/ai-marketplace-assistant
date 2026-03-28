"""
Logging configuration module for AI Marketplace Assistant

This module sets up structured logging for the application with:
- Console and file handlers
- Configurable log levels
- Proper formatting
- Rotating file handler support
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from .settings import settings


class LoggerSetup:
    """Logger setup and configuration"""
    
    _initialized = False
    
    @classmethod
    def setup_logging(cls, log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        Setup application logging
        
        Args:
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file
        """
        if cls._initialized:
            return
        
        level = log_level or settings.log_level
        file_path = log_file or settings.log_file
        
        # Convert string level to logging constant
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            settings.log_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Remove existing handlers
        root_logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        if file_path:
            log_path = Path(file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Silence noisy loggers
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        
        cls._initialized = True
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized at {level} level")
        if file_path:
            logger.info(f"Log file: {file_path}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get logger instance for a module
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        if not cls._initialized:
            cls.setup_logging()
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return LoggerSetup.get_logger(name)


# Initialize logging on module import
LoggerSetup.setup_logging()
