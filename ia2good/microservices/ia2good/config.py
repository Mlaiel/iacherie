"""Configuration for IA2GOOD module"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "IA2GOOD"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ia2good:ia2good@localhost:5432/ia2good"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage (S3/MinIO)
    S3_ENDPOINT: Optional[str] = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY")
    S3_BUCKET: str = "ia2good-media"
    
    # AI Services
    AI_ORCHESTRATION_URL: str = os.getenv(
        "AI_ORCHESTRATION_URL",
        "http://localhost:8001"
    )
    
    # Geolocation
    MAPBOX_API_KEY: Optional[str] = os.getenv("MAPBOX_API_KEY")
    DEFAULT_MAX_DISTANCE_KM: int = 20
    
    # Notifications
    NOTIFICATION_SERVICE_URL: str = os.getenv(
        "NOTIFICATION_SERVICE_URL",
        "http://localhost:8002"
    )
    
    # Matching Algorithm
    MATCHING_SCORE_THRESHOLD: int = 80
    AUTO_ASSIGN_ENABLED: bool = False
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://ia2good.com",
        "https://*.app.github.dev",  # GitHub Codespaces
        "*",  # Allow all origins in development
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
