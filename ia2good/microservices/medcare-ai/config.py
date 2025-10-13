"""
Configuration for MedCare-AI microservice
"""
import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "medcare-ai"
    SERVICE_VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8004"))
    
    # IACherie AI Integration
    IACHERIE_API_URL: str = os.getenv("IACHERIE_API_URL", "http://localhost:8000")
    IACHERIE_API_KEY: Optional[str] = os.getenv("IACHERIE_API_KEY", "")
    
    # Database - PostgreSQL (Docker sur port 5433, partagé avec EduVerify)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ia2good:ia2good_secure_2025@localhost:5433/ia2good"
    )
    ASYNC_DATABASE_URL: str = os.getenv(
        "ASYNC_DATABASE_URL",
        "postgresql+asyncpg://ia2good:ia2good_secure_2025@localhost:5433/ia2good"
    )
    
    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # ML Models
    ML_MODELS_PATH: str = os.getenv("ML_MODELS_PATH", "./ml_models")
    SYMPTOM_MODEL_PATH: str = f"{ML_MODELS_PATH}/symptom_classifier.pkl"
    SKIN_MODEL_PATH: str = f"{ML_MODELS_PATH}/skin_condition_model.h5"
    XRAY_MODEL_PATH: str = f"{ML_MODELS_PATH}/xray_analyzer.h5"
    
    # WebRTC / Video Calls
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_API_KEY: Optional[str] = os.getenv("TWILIO_API_KEY")
    TWILIO_API_SECRET: Optional[str] = os.getenv("TWILIO_API_SECRET")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Medical Data Compliance
    HIPAA_ENCRYPTION_KEY: str = os.getenv("HIPAA_ENCRYPTION_KEY", "change-in-production")
    DATA_RETENTION_DAYS: int = 2555  # 7 years for medical records
    
    # External Services
    PHARMACY_API_URL: Optional[str] = os.getenv("PHARMACY_API_URL")
    EMERGENCY_SERVICES_API: Optional[str] = os.getenv("EMERGENCY_SERVICES_API")
    
    # Redis (for caching and real-time)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Monitoring
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

settings = Settings()
