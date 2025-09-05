"""
Configuration Management
Centralized configuration for the entire application
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "Ainflue"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Server Settings
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    
    # Database Settings
    database_url: Optional[str] = None
    postgres_user: str = "ainflue"
    postgres_password: str = "ainflue_secure"
    postgres_db: str = "ainflue_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Redis Settings
    redis_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Security Settings
    secret_key: str = "ainflue_super_secret_key_2024"
    jwt_secret: str = "jwt_secret_key_ainflue"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"]
    
    # Monitoring Settings
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True
    opentelemetry_enabled: bool = True
    
    # AI Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Social Media API Keys
    youtube_api_key: Optional[str] = None
    twitter_api_key: Optional[str] = None
    facebook_api_key: Optional[str] = None
    instagram_api_key: Optional[str] = None
    tiktok_api_key: Optional[str] = None
    
    # File Storage
    upload_dir: str = "/tmp/ainflue_uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: List[str] = [".mp3", ".mp4", ".wav", ".avi", ".mov", ".jpg", ".png", ".pdf"]
    
    # Crawler Settings
    crawler_user_agent: str = "Ainflue-Bot/1.0"
    crawler_delay: float = 1.0
    crawler_timeout: int = 30
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()

# Backwards compatibility exports
DATABASE_URL = settings.database_url
SECRET_KEY = settings.secret_key
DEBUG = settings.debug
ENVIRONMENT = settings.environment
API_V1_PREFIX = settings.api_v1_prefix
CORS_ORIGINS = settings.cors_origins

__all__ = [
    "settings",
    "Settings",
    "DATABASE_URL",
    "SECRET_KEY", 
    "DEBUG",
    "ENVIRONMENT",
    "API_V1_PREFIX",
    "CORS_ORIGINS"
]
