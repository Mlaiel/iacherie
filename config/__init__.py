"""
Configuration Management
Centralized configuration for the entire application
"""

import os
from typing import Optional, List

# Import specialized configuration modules
from .settings import ApplicationSettings, app_settings
from .database import DatabaseSettings, db_settings, get_database_url, get_database_config
from .redis import RedisSettings, redis_settings, get_redis_url, get_redis_config
from .celery import CelerySettings, celery_settings, get_celery_config, create_celery_app

# Import business logic configuration modules
from .creator_multi_format_config import (
    CreatorMultiFormatSettings, creator_multi_format_settings,
    ContentFormat, CreatorType, MonetizationStream, DistributionPlatform
)
from .content_format_config import (
    ContentFormatSettings, content_format_settings,
    AudioFormat, VideoFormat, ImageFormat, TextFormat, VoiceFormat, AvatarFormat
)
from .ia_processing_config import (
    IAProcessingSettings, ia_processing_settings,
    AIModel, ProcessingMode, OptimizationType, AccuracyLevel
)
from .ai_model_config import (
    AIModelSettings, ai_model_settings,
    ModelType, ModelProvider, ModelStatus, ModelTier
)

# Import new business logic configuration modules
from .creator_types_config import (
    CreatorTypesSettings, creator_types_settings,
    CreatorCategory, CreatorSpecialization, CreatorExperienceLevel, CreatorTier,
    CreatorTypeRequirements, CreatorTypeCapabilities, CreatorTypeMetrics
)
from .content_ingestion_config import (
    ContentIngestionSettings, content_ingestion_settings,
    IngestionMethod, ValidationLevel, ProcessingPriority, ContentStatus,
    FileSizeLimit, QualityStandard, ValidationRule, IngestionWorkflow
)
from .ml_pipeline_config import (
    MLPipelineSettings, ml_pipeline_settings,
    PipelineStage, ModelType as MLModelType, TrainingMode, DeploymentStrategy,
    TrainingConfiguration, ModelConfiguration, PipelineConfiguration, InferenceConfiguration
)
from .intelligent_analysis_config import (
    IntelligentAnalysisSettings, intelligent_analysis_settings,
    AnalysisType, AnalysisEngine, AnalysisPriority, AccuracyLevel as AnalysisAccuracyLevel,
    AnalysisModel, AnalysisWorkflow, QualityMetrics
)
from .copyright_fingerprinting_config import (
    CopyrightFingerprintingSettings, copyright_fingerprinting_settings,
    FingerprintAlgorithm, ContentType as FingerprintContentType, MatchingThreshold, FingerprintDatabase,
    AlgorithmConfiguration, MatchingConfiguration, DatabaseConfiguration
)
from .collaboration_business_config import (
    CollaborationBusinessSettings, collaboration_business_settings,
    CollaborationType, CollaborationStatus, RevenueModel, MatchingCriteria,
    CollaborationTemplate, RevenueDistribution, CollaborationWorkflow
)
from .seo_business_config import (
    SEOBusinessSettings, seo_business_settings,
    SEOStrategy, SearchEngine, ContentType as SEOContentType, OptimizationLevel,
    KeywordStrategy, ContentOptimization, TechnicalSEO, SEOAnalytics
)
from .distribution_business_config import (
    DistributionBusinessSettings, distribution_business_settings,
    DistributionPlatform as DistPlatform, DistributionStrategy, ContentFormat as DistContentFormat, DistributionStatus,
    PlatformConfiguration, DistributionRule, GlobalDistributionSettings
)

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

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
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
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
        extra = "allow"

# Global settings instance
settings = Settings()

# Backwards compatibility exports
DATABASE_URL = settings.database_url
SECRET_KEY = settings.secret_key
DEBUG = settings.debug
ENVIRONMENT = settings.environment
API_V1_PREFIX = settings.api_v1_prefix
CORS_ORIGINS = settings.cors_origins_list

__all__ = [
    # Main settings
    "settings",
    "Settings",
    
    # Specialized configuration classes and instances
    "ApplicationSettings", "app_settings",
    "DatabaseSettings", "db_settings", "get_database_url", "get_database_config",
    "RedisSettings", "redis_settings", "get_redis_url", "get_redis_config", 
    "CelerySettings", "celery_settings", "get_celery_config", "create_celery_app",
    
    # Business logic configuration classes and instances
    "CreatorMultiFormatSettings", "creator_multi_format_settings",
    "ContentFormat", "CreatorType", "MonetizationStream", "DistributionPlatform",
    "ContentFormatSettings", "content_format_settings",
    "AudioFormat", "VideoFormat", "ImageFormat", "TextFormat", "VoiceFormat", "AvatarFormat",
    "IAProcessingSettings", "ia_processing_settings",
    "AIModel", "ProcessingMode", "OptimizationType", "AccuracyLevel",
    "AIModelSettings", "ai_model_settings",
    "ModelType", "ModelProvider", "ModelStatus", "ModelTier",
    
    # New business logic configuration classes and instances
    "CreatorTypesSettings", "creator_types_settings",
    "CreatorCategory", "CreatorSpecialization", "CreatorExperienceLevel", "CreatorTier",
    "CreatorTypeRequirements", "CreatorTypeCapabilities", "CreatorTypeMetrics",
    "ContentIngestionSettings", "content_ingestion_settings",
    "IngestionMethod", "ValidationLevel", "ProcessingPriority", "ContentStatus",
    "FileSizeLimit", "QualityStandard", "ValidationRule", "IngestionWorkflow",
    "MLPipelineSettings", "ml_pipeline_settings",
    "PipelineStage", "MLModelType", "TrainingMode", "DeploymentStrategy",
    "TrainingConfiguration", "ModelConfiguration", "PipelineConfiguration", "InferenceConfiguration",
    "IntelligentAnalysisSettings", "intelligent_analysis_settings",
    "AnalysisType", "AnalysisEngine", "AnalysisPriority", "AnalysisAccuracyLevel",
    "AnalysisModel", "AnalysisWorkflow", "QualityMetrics",
    "CopyrightFingerprintingSettings", "copyright_fingerprinting_settings",
    "FingerprintAlgorithm", "FingerprintContentType", "MatchingThreshold", "FingerprintDatabase",
    "AlgorithmConfiguration", "MatchingConfiguration", "DatabaseConfiguration",
    "CollaborationBusinessSettings", "collaboration_business_settings",
    "CollaborationType", "CollaborationStatus", "RevenueModel", "MatchingCriteria",
    "CollaborationTemplate", "RevenueDistribution", "CollaborationWorkflow",
    "SEOBusinessSettings", "seo_business_settings",
    "SEOStrategy", "SearchEngine", "SEOContentType", "OptimizationLevel",
    "KeywordStrategy", "ContentOptimization", "TechnicalSEO", "SEOAnalytics",
    "DistributionBusinessSettings", "distribution_business_settings",
    "DistPlatform", "DistributionStrategy", "DistContentFormat", "DistributionStatus",
    "PlatformConfiguration", "DistributionRule", "GlobalDistributionSettings",
    
    # Backwards compatibility exports
    "DATABASE_URL",
    "SECRET_KEY", 
    "DEBUG",
    "ENVIRONMENT",
    "API_V1_PREFIX",
    "CORS_ORIGINS"
]
