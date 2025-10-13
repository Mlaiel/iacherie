"""
Configuration for Guardian Volunteer Platform
Support de 644+ langues et dialectes
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Guardian service configuration avec support multilingue complet"""
    
    # Service Info
    SERVICE_NAME: str = "guardian"
    SERVICE_VERSION: str = "3.0.0"  # Version avec support de 644 langues
    SERVICE_PORT: int = 8001
    
    # ========================================================================
    # SUPPORT MULTILINGUE (644+ LANGUES ET DIALECTES)
    # ========================================================================
    
    # APIs de traduction
    DEEPL_API_KEY: Optional[str] = None
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    LIBRETRANSLATE_URL: str = "https://libretranslate.com"
    
    # Langue par défaut
    DEFAULT_LANGUAGE: str = "EN"
    
    # Total des langues supportées par IACherie
    TOTAL_LANGUAGES_SUPPORTED: int = 644
    
    # Langues actives pour la modération de contenu
    ACTIVE_MODERATION_LANGUAGES: list = [
        "EN", "FR", "DE", "AR", "ES", "IT", "PT", "RU", "ZH", "JA",
        "KO", "HI", "TR", "PL", "NL", "SV", "VI", "TH", "EL", "IW"
    ]
    
    # IACherie Integration
    IACHERIE_API_URL: str = "http://localhost:8000"
    IACHERIE_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://ia2good:ia2good_secure_2025@localhost:5433/ia2good"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "guardian_humanitarian_secret_2025"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "guardian@ia2good.org"
    
    # Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET: str = "guardian-missions"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Development
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # External APIs
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
