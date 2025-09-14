"""
Application Settings Configuration
Core application settings and environment configuration
"""

import os
from typing import Optional, List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
    """Config: class implementation"""
            env_file = ".env"
            extra = "allow"


class ApplicationSettings(BaseSettings):
    """Application-specific settings"""
    
    # Application Settings
    app_name: str = "Ainflue"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Server Settings
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003"
    
    # Security Settings
    secret_key: str = "ainflue_super_secret_key_2024"
    jwt_secret: str = "jwt_secret_key_ainflue"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    
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
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
    """Config: class implementation"""
        env_file = ".env"
        extra = "allow"


# Application settings instance
app_settings = ApplicationSettings()

__all__ = ["ApplicationSettings", "app_settings"]