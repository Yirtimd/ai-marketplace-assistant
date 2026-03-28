"""
Configuration module for AI Marketplace Assistant

This module manages all application settings using pydantic-settings.
Settings are loaded from environment variables with support for .env files.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application settings
    app_name: str = Field(default="AI Marketplace Assistant", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    
    # Database settings
    database_url: PostgresDsn = Field(
        description="PostgreSQL database URL",
        examples=["postgresql://user:password@localhost:5432/ai_marketplace"]
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")
    
    # Redis settings
    redis_url: RedisDsn = Field(
        description="Redis URL",
        examples=["redis://localhost:6379/0"]
    )
    redis_max_connections: int = Field(default=10, description="Redis max connections")
    
    # Celery settings
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    log_file: Optional[str] = Field(default="logs/app.log", description="Log file path")
    
    # AI Service settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API key")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API base URL (OpenAI-compatible)",
    )
    deepseek_model: str = Field(default="deepseek-chat", description="Default DeepSeek model")
    openai_model: str = Field(default="gpt-4o-mini", description="Default OpenAI chat model")
    openai_image_model: str = Field(default="gpt-image-1", description="Default OpenAI image model")
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest", description="Default Anthropic model")
    
    # Wildberries API settings
    wb_api_key: Optional[str] = Field(default=None, description="Wildberries API key")
    wb_api_url: str = Field(
        default="https://suppliers-api.wildberries.ru",
        description="Wildberries API base URL"
    )
    
    # Security settings
    secret_key: str = Field(description="Secret key for JWT and encryption")
    access_token_expire_minutes: int = Field(default=60, description="Access token expiration time")
    
    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL, fallback to Redis if not set"""
        return self.celery_broker_url or str(self.redis_url)
    
    @property
    def celery_backend(self) -> str:
        """Get Celery result backend URL, fallback to Redis if not set"""
        return self.celery_result_backend or str(self.redis_url)


# Global settings instance
settings = Settings()
