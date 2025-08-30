"""
Simplified Configuration for Development/Testing
Fallback configuration that doesn't require external dependencies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Optional, List


class SimpleSettings:
    """Simple settings class without external dependencies"""
    
    def __init__(self):
        # Application settings
        self.app_name = os.getenv("APP_NAME", "Ainflue")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.app_description = os.getenv("APP_DESCRIPTION", "AI-Powered Content Protection & Monetization Platform")
        
        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # CORS Configuration
        self.cors_origins = ["*"]
        self.cors_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        # API Configuration
        self.api_prefix = os.getenv("API_PREFIX", "/api/v1")
        self.docs_url = os.getenv("DOCS_URL", "/docs")
        self.redoc_url = os.getenv("REDOC_URL", "/redoc")


class SimpleApplicationSettings(SimpleSettings):
    """Application settings for compatibility"""
    pass


class SimpleDatabaseSettings:
    """Simple database settings"""
    
    def __init__(self):
        # PostgreSQL Primary Database
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_user = os.getenv("POSTGRES_USER", "ainflue")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "")
        self.postgres_db = os.getenv("POSTGRES_DB", "ainflue_platform")
        
        # Redis Cache Database
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        self.redis_db = int(os.getenv("REDIS_DB", "0"))


class SimpleSecuritySettings:
    """Simple security settings"""
    
    def __init__(self):
        # JWT Configuration
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE", "3600"))  # 1 hour
        self.jwt_refresh_token_expire = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE", "604800"))  # 7 days
        
        # Encryption Configuration
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "dev-encryption-key-change-in-production")
        self.password_salt = os.getenv("PASSWORD_SALT", "dev-password-salt-change-in-production")
        
        # Rate Limiting
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour


class SimpleAISettings:
    """Simple AI settings"""
    
    def __init__(self):
        # Model Configuration
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN", None)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", None)
        
        # Content Processing
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
        self.supported_audio_formats = ["mp3", "wav", "flac", "m4a", "ogg"]
        self.supported_video_formats = ["mp4", "avi", "mov", "mkv", "webm"]
        self.supported_image_formats = ["jpg", "jpeg", "png", "gif", "bmp", "tiff"]
        self.supported_text_formats = ["txt", "md", "doc", "docx", "pdf"]


class SimplePlatformSettings:
    """Simple platform settings"""
    
    def __init__(self):
        # YouTube Integration
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY", None)
        self.youtube_client_id = os.getenv("YOUTUBE_CLIENT_ID", None)
        self.youtube_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", None)
        
        # Spotify Integration
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID", None)
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", None)


class SimplePaymentSettings:
    """Simple payment settings"""
    
    def __init__(self):
        # Stripe Configuration
        self.stripe_public_key = os.getenv("STRIPE_PUBLIC_KEY", None)
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", None)
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", None)


class SimpleStorageSettings:
    """Simple storage settings"""
    
    def __init__(self):
        # Local Storage
        self.local_storage_path = os.getenv("LOCAL_STORAGE_PATH", "./storage")
        
        # AWS S3 Configuration
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", None)
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", None)
        self.aws_region = os.getenv("AWS_REGION", "eu-central-1")
        self.aws_s3_bucket = os.getenv("AWS_S3_BUCKET", "ainflue-content")


class SimpleMonitoringSettings:
    """Simple monitoring settings"""
    
    def __init__(self):
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")  # json or text
        
        # Prometheus Configuration
        self.prometheus_enabled = os.getenv("PROMETHEUS_ENABLED", "True").lower() == "true"
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))


class SimpleSettingsAggregator:
    """Simple settings aggregator without external dependencies"""
    
    def __init__(self):
        self.app = SimpleApplicationSettings()
        self.database = SimpleDatabaseSettings()
        self.security = SimpleSecuritySettings()
        self.ai = SimpleAISettings()
        self.platforms = SimplePlatformSettings()
        self.payments = SimplePaymentSettings()
        self.storage = SimpleStorageSettings()
        self.monitoring = SimpleMonitoringSettings()


# Try to import the main config, fall back to simple config
try:
    from config import settings
    print("✅ Using full configuration with pydantic")
except ImportError:
    settings = SimpleSettingsAggregator()
    print("⚠️  Using simplified configuration (pydantic not available)")


# Compatibility functions
def get_settings():
    """Get settings instance for dependency injection"""
    return settings


# Export the settings
__all__ = ['settings', 'get_settings']