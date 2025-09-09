"""Core Configuration Module for Ainflue Platform
Centralized configuration management with environment-based settings.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Any, Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Settings
    app_name: str = Field(default="Ainflue AI Platform", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Security Settings
    secret_key: str = Field(default="ainflue-secret-key-change-in-production", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Database Settings
    database_url: str = Field(default="postgresql://postgres:password@localhost:5432/ainflue", env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    # AI/ML Settings
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    huggingface_token: str = Field(default="", env="HUGGINGFACE_TOKEN")
    model_cache_dir: str = Field(default="/tmp/ainflue_models", env="MODEL_CACHE_DIR")
    
    # Content Protection Settings
    enable_fingerprinting: bool = Field(default=True, env="ENABLE_FINGERPRINTING")
    enable_watermarking: bool = Field(default=True, env="ENABLE_WATERMARKING")
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    
    # Crawling Settings
    crawler_max_concurrent: int = Field(default=50, env="CRAWLER_MAX_CONCURRENT")
    crawler_delay_seconds: float = Field(default=1.0, env="CRAWLER_DELAY_SECONDS")
    crawler_timeout_seconds: int = Field(default=30, env="CRAWLER_TIMEOUT_SECONDS")
    
    # CORS Settings
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
        env="CORS_ORIGINS"
    )
    
    # Monitoring Settings
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Payment Settings
    stripe_api_key: str = Field(default="", env="STRIPE_API_KEY")
    stripe_webhook_secret: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")
    
    # Email Settings
    smtp_host: str = Field(default="localhost", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env file


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings


def get_database_url() -> str:
    """Get database connection URL."""
    return settings.database_url


def get_redis_url() -> str:
    """Get Redis connection URL."""
    return settings.redis_url


def is_debug_mode() -> bool:
    """Check if application is in debug mode."""
    return settings.debug


def get_cors_origins() -> List[str]:
    """Get CORS allowed origins."""
    return settings.cors_origins.split(",")


# Environment-specific configurations
class DevelopmentConfig(Settings):
    """Development environment configuration."""
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionConfig(Settings):
    """Production environment configuration."""
    debug: bool = False
    log_level: str = "WARNING"
    workers: int = 8


class TestingConfig(Settings):
    """Testing environment configuration."""
    debug: bool = True
    database_url: str = "sqlite:///test.db"
    redis_url: str = "redis://localhost:6379/1"


# Configuration factory
def get_config_by_environment(env: str = None) -> Settings:
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()