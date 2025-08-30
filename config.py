"""
Ainflue Platform Configuration
Core configuration management for the AI-powered content protection platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn


class APISettings(BaseSettings):
    """API and web server configuration"""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Configuration
    api_root_prefix: str = Field(default="/api", env="API_ROOT_PREFIX")
    api_version: str = Field(default="v1", env="API_VERSION")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    openapi_url: str = Field(default="/openapi.json", env="OPENAPI_URL")
    
    # CORS Settings
    cors_allow_origins: List[str] = Field(
        default=["*"], 
        env="CORS_ALLOW_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["*"], 
        env="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"], 
        env="CORS_ALLOW_HEADERS"
    )
    
    # Request/Response Settings
    max_request_size: int = Field(default=100 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 100MB
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes
    response_timeout: int = Field(default=60, env="RESPONSE_TIMEOUT")  # 1 minute
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"





class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # PostgreSQL Primary Database
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT") 
    postgres_user: str = Field(default="ainflue", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="ainflue_platform", env="POSTGRES_DB")
    postgres_max_connections: int = Field(default=20, env="POSTGRES_MAX_CONNECTIONS")
    postgres_ssl_mode: str = Field(default="prefer", env="POSTGRES_SSL_MODE")
    
    # Redis Cache Database
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    redis_timeout: int = Field(default=5, env="REDIS_TIMEOUT")
    
    # MongoDB Document Database
    mongodb_host: str = Field(default="localhost", env="MONGODB_HOST")
    mongodb_port: int = Field(default=27017, env="MONGODB_PORT")
    mongodb_user: str = Field(default="ainflue", env="MONGODB_USER")
    mongodb_password: str = Field(default="", env="MONGODB_PASSWORD")
    mongodb_db: str = Field(default="ainflue_documents", env="MONGODB_DB")
    mongodb_max_connections: int = Field(default=50, env="MONGODB_MAX_CONNECTIONS")
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?sslmode={self.postgres_ssl_mode}"
    
    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def mongodb_url(self) -> str:
        return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SecuritySettings(BaseSettings):
    """Security and authentication configuration"""
    
    # JWT Configuration
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire: int = Field(default=3600, env="JWT_ACCESS_TOKEN_EXPIRE")  # 1 hour
    jwt_refresh_token_expire: int = Field(default=604800, env="JWT_REFRESH_TOKEN_EXPIRE")  # 7 days
    
    # OAuth2 Configuration
    oauth2_google_client_id: Optional[str] = Field(default=None, env="OAUTH2_GOOGLE_CLIENT_ID")
    oauth2_google_client_secret: Optional[str] = Field(default=None, env="OAUTH2_GOOGLE_CLIENT_SECRET")
    oauth2_github_client_id: Optional[str] = Field(default=None, env="OAUTH2_GITHUB_CLIENT_ID")
    oauth2_github_client_secret: Optional[str] = Field(default=None, env="OAUTH2_GITHUB_CLIENT_SECRET")
    
    # Encryption Configuration
    encryption_key: str = Field(default="dev-encryption-key-change-in-production", env="ENCRYPTION_KEY")
    password_salt: str = Field(default="dev-password-salt-change-in-production", env="PASSWORD_SALT")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AISettings(BaseSettings):
    """AI and Machine Learning configuration"""
    
    # Model Configuration
    huggingface_token: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Content Processing
    max_file_size_mb: int = Field(default=500, env="MAX_FILE_SIZE_MB")
    supported_audio_formats: List[str] = Field(default=["mp3", "wav", "flac", "m4a", "ogg"])
    supported_video_formats: List[str] = Field(default=["mp4", "avi", "mov", "mkv", "webm"])
    supported_image_formats: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "bmp", "tiff"])
    supported_text_formats: List[str] = Field(default=["txt", "md", "doc", "docx", "pdf"])
    
    # Vector Database
    faiss_index_path: str = Field(default="./data/faiss_indexes", env="FAISS_INDEX_PATH")
    vector_dimension: int = Field(default=768, env="VECTOR_DIMENSION")
    similarity_threshold: float = Field(default=0.85, env="SIMILARITY_THRESHOLD")


class PlatformSettings(BaseSettings):
    """Platform integrations configuration"""
    
    # YouTube Integration
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    youtube_client_id: Optional[str] = Field(default=None, env="YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[str] = Field(default=None, env="YOUTUBE_CLIENT_SECRET")
    
    # Instagram Integration
    instagram_access_token: Optional[str] = Field(default=None, env="INSTAGRAM_ACCESS_TOKEN")
    instagram_client_id: Optional[str] = Field(default=None, env="INSTAGRAM_CLIENT_ID")
    instagram_client_secret: Optional[str] = Field(default=None, env="INSTAGRAM_CLIENT_SECRET")
    
    # TikTok Integration
    tiktok_api_key: Optional[str] = Field(default=None, env="TIKTOK_API_KEY")
    tiktok_client_id: Optional[str] = Field(default=None, env="TIKTOK_CLIENT_ID")
    tiktok_client_secret: Optional[str] = Field(default=None, env="TIKTOK_CLIENT_SECRET")
    
    # Spotify Integration
    spotify_client_id: Optional[str] = Field(default=None, env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: Optional[str] = Field(default=None, env="SPOTIFY_CLIENT_SECRET")
    
    # Twitter/X Integration
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_SECRET")


class PaymentSettings(BaseSettings):
    """Payment processing configuration"""
    
    # Stripe Configuration
    stripe_public_key: Optional[str] = Field(default=None, env="STRIPE_PUBLIC_KEY")
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # PayPal Configuration
    paypal_client_id: Optional[str] = Field(default=None, env="PAYPAL_CLIENT_ID")
    paypal_client_secret: Optional[str] = Field(default=None, env="PAYPAL_CLIENT_SECRET")
    paypal_environment: str = Field(default="sandbox", env="PAYPAL_ENVIRONMENT")  # sandbox or live
    
    # Wise Configuration
    wise_api_key: Optional[str] = Field(default=None, env="WISE_API_KEY")
    wise_environment: str = Field(default="sandbox", env="WISE_ENVIRONMENT")


class StorageSettings(BaseSettings):
    """File storage configuration"""
    
    # AWS S3 Configuration
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="eu-central-1", env="AWS_REGION")
    aws_s3_bucket: str = Field(default="ainflue-content", env="AWS_S3_BUCKET")
    
    # Local Storage Fallback
    local_storage_path: str = Field(default="./storage", env="LOCAL_STORAGE_PATH")
    
    # CDN Configuration
    cdn_base_url: Optional[str] = Field(default=None, env="CDN_BASE_URL")


class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration"""
    
    # Prometheus Configuration
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    
    # Sentry Configuration
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="production", env="SENTRY_ENVIRONMENT")


class ApplicationSettings(BaseSettings):
    """Main application configuration"""
    
    # Application Info
    app_name: str = Field(default="Ainflue", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_description: str = Field(default="AI-Powered Content Protection & Monetization Platform", env="APP_DESCRIPTION")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Environment
    environment: str = Field(default="production", env="ENVIRONMENT")  # development, staging, production
    
    # CORS Configuration
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "PATCH"], env="CORS_METHODS")
    
    # API Configuration
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: Optional[str] = Field(default="/docs", env="DOCS_URL")
    redoc_url: Optional[str] = Field(default="/redoc", env="REDOC_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings:
    """Main settings aggregator"""
    
    def __init__(self):
        self.app = ApplicationSettings()
        self.database = DatabaseSettings()
        self.security = SecuritySettings()
        self.ai = AISettings()
        self.platforms = PlatformSettings()
        self.payments = PaymentSettings()
        self.storage = StorageSettings()
        self.monitoring = MonitoringSettings()


# Global settings instance
settings = Settings()

# Compatibility aliases for existing code
def get_settings():
    """Get settings instance for dependency injection."""
    return settings