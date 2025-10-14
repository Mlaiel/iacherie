"""
Configuration for EduVerify microservice
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "EduVerify"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # IACherie AI Integration
    IACHERIE_API_URL: str = os.getenv("IACHERIE_API_URL", "http://localhost:8000")
    IACHERIE_API_KEY: Optional[str] = os.getenv("IACHERIE_API_KEY", "")
    
        # Database - PostgreSQL (Docker sur port 5433)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ia2good:ia2good_secure_2025@localhost:5433/ia2good"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "eduverify-jwt-secret-key-2025"))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_GEMINI_API_KEY: Optional[str] = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    # Storage (S3/MinIO like IA2GOOD)
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT_URL", os.getenv("S3_ENDPOINT", "http://localhost:9000"))
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin123")
    S3_BUCKET: str = os.getenv("S3_BUCKET_NAME", os.getenv("S3_BUCKET", "eduverify-content"))
    
    # Content Processing
    MAX_FILE_SIZE_MB: int = 50
    SUPPORTED_FILE_TYPES: list = [".pdf", ".docx", ".txt", ".mp3", ".wav", ".mp4", ".avi"]
    
    # Quiz Generation
    DEFAULT_QUIZ_QUESTIONS: int = 10
    MIN_QUIZ_QUESTIONS: int = 5
    MAX_QUIZ_QUESTIONS: int = 50
    QUIZ_QUALITY_THRESHOLD: float = 0.85
    
    # Fact-Checking
    FACT_CHECK_CONFIDENCE_THRESHOLD: float = 0.70
    MIN_SOURCES_REQUIRED: int = 2
    FACT_CHECK_PRECISION_TARGET: float = 0.92
    
    # Language Support
    SUPPORTED_LANGUAGES: int = 100  # Target
    DEFAULT_LANGUAGE: str = "fr"
    
    # Live Lecture
    LIVE_TRANSCRIPTION_LATENCY_TARGET: float = 3.0  # seconds
    LIVE_FACT_CHECK_ENABLED: bool = True
    
    # Storage
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "/tmp/uploads")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
