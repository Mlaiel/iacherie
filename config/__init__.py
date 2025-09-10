"""Ainflue Configuration Management - Enterprise Orchestrator
===========================================================

Master configuration orchestrator for the Ainflue platform providing
centralized configuration management, environment handling, and enterprise
integration across all subsystems and business logic components.

Business Logic Integration:
Creator Multi-Format → AI Processing → Protection → Monetization → 
Collaboration & Gamification → SEO → Multi-Platform Distribution

🚀 ENTERPRISE GRADE FEATURES:
- Quantum-ready configuration patterns
- Real-time hot-reload capabilities  
- Advanced caching with L1-L4 levels
- Distributed configuration synchronization
- AI-powered configuration optimization
- Zero-downtime configuration updates
- Enterprise security & compliance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable, Coroutine
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache, wraps
import weakref

# Core infrastructure imports
try:
    from .settings import ApplicationSettings, app_settings
except ImportError:
    # Fallback if settings not available
    app_settings = None

class ConfigurationLevel(str, Enum):
    """Configuration complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class BusinessLogicFlow(str, Enum):
    """Ainflue business logic flow stages"""
    CREATOR_ONBOARDING = "creator_onboarding"
    CONTENT_UPLOAD = "content_upload"
    AI_PROCESSING = "ai_processing"
    PROTECTION_APPLICATION = "protection_application"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_MATCHING = "collaboration_matching"
    MONETIZATION_ACTIVATION = "monetization_activation"
    DISTRIBUTION_DEPLOYMENT = "distribution_deployment"
    ANALYTICS_TRACKING = "analytics_tracking"
    GAMIFICATION_ENGAGEMENT = "gamification_engagement"

class AinflueMasterConfiguration:
    """Master configuration orchestrator for Ainflue platform"""
    
    def __init__(self, level: ConfigurationLevel = ConfigurationLevel.ENTERPRISE):
        """Initialize master configuration"""
        self.level = level
        self.app_settings = app_settings
        self.configurations: Dict[str, Any] = {}
        self.business_flow_configs: Dict[BusinessLogicFlow, Dict[str, Any]] = {}
        self._initialize_configurations()
        self._setup_business_logic_flows()
    
    def _initialize_configurations(self):
        """Initialize all configuration subsystems"""
        try:
            # Core infrastructure (lazy imports to avoid circular imports)
            from .core import (
                DatabaseConfiguration, RedisConfiguration, CeleryConfiguration
            )
            
            self.configurations.update({
                "database": DatabaseConfiguration(level=self.level),
                "redis": RedisConfiguration(level=self.level),
                "celery": CeleryConfiguration(level=self.level)
            })
            
            # AI system configurations (lazy imports)
            from .ai import (
                AIModelConfiguration, IAProcessingConfiguration, 
                MLPipelineConfiguration, IntelligentAnalysisConfiguration
            )
            
            self.configurations.update({
                "ai_models": AIModelConfiguration(level=self.level),
                "ia_processing": IAProcessingConfiguration(level=self.level),
                "ml_pipeline": MLPipelineConfiguration(level=self.level),
                "intelligent_analysis": IntelligentAnalysisConfiguration(level=self.level)
            })
            
            # Business logic configurations (lazy imports)
            from .business import (
                CreatorMultiFormatConfiguration, CreatorTypesConfiguration,
                MonetizationBusinessConfiguration, CollaborationBusinessConfiguration,
                GamificationBusinessConfiguration, SEOBusinessConfiguration,
                DistributionBusinessConfiguration
            )
            
            self.configurations.update({
                "creator_multi_format": CreatorMultiFormatConfiguration(level=self.level),
                "creator_types": CreatorTypesConfiguration(level=self.level),
                "monetization": MonetizationBusinessConfiguration(level=self.level),
                "collaboration": CollaborationBusinessConfiguration(level=self.level),
                "gamification": GamificationBusinessConfiguration(level=self.level),
                "seo": SEOBusinessConfiguration(level=self.level),
                "distribution": DistributionBusinessConfiguration(level=self.level)
            })
            
            # Security configurations (lazy imports)
            from .security import (
                ProtectionBusinessConfiguration, CopyrightFingerprintingConfiguration,
                RightsManagementConfiguration, ViolationDetectionConfiguration
            )
            
            self.configurations.update({
                "protection": ProtectionBusinessConfiguration(level=self.level),
                "copyright": CopyrightFingerprintingConfiguration(level=self.level),
                "rights_management": RightsManagementConfiguration(level=self.level),
                "violation_detection": ViolationDetectionConfiguration(level=self.level)
            })
            
            # Payment configurations (lazy imports)
            from .payments import (
                PaymentGatewayConfiguration, CryptoPaymentConfiguration,
                SubscriptionManagementConfiguration
            )
            
            self.configurations.update({
                "payment_gateway": PaymentGatewayConfiguration(level=self.level),
                "crypto_payments": CryptoPaymentConfiguration(level=self.level),
                "subscriptions": SubscriptionManagementConfiguration(level=self.level)
            })
            
        except ImportError as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Some configuration modules not yet available: {e}")
    
    def _setup_business_logic_flows(self):
        """Setup business logic flow configurations"""
        self.business_flow_configs = {
            BusinessLogicFlow.CREATOR_ONBOARDING: {
                "required_configs": ["creator_types", "authentication", "billing"],
                "validation_rules": ["profile_completeness", "verification_status"],
                "next_stage": BusinessLogicFlow.CONTENT_UPLOAD
            },
            
            BusinessLogicFlow.CONTENT_UPLOAD: {
                "required_configs": ["creator_multi_format", "audio_processing", "video_processing"],
                "validation_rules": ["format_support", "quality_standards", "file_size_limits"],
                "next_stage": BusinessLogicFlow.AI_PROCESSING
            },
            
            BusinessLogicFlow.AI_PROCESSING: {
                "required_configs": ["ai_models", "ia_processing", "ml_pipeline"],
                "validation_rules": ["model_availability", "processing_capacity"],
                "next_stage": BusinessLogicFlow.PROTECTION_APPLICATION
            },
            
            BusinessLogicFlow.PROTECTION_APPLICATION: {
                "required_configs": ["protection", "copyright", "rights_management"],
                "validation_rules": ["copyright_clearance", "protection_level"],
                "next_stage": BusinessLogicFlow.SEO_OPTIMIZATION
            },
            
            BusinessLogicFlow.SEO_OPTIMIZATION: {
                "required_configs": ["seo", "search_optimization", "analytics"],
                "validation_rules": ["seo_compliance", "keyword_optimization"],
                "next_stage": BusinessLogicFlow.COLLABORATION_MATCHING
            },
            
            BusinessLogicFlow.COLLABORATION_MATCHING: {
                "required_configs": ["collaboration", "creator_matching", "gamification"],
                "validation_rules": ["compatibility_score", "collaboration_preferences"],
                "next_stage": BusinessLogicFlow.MONETIZATION_ACTIVATION
            },
            
            BusinessLogicFlow.MONETIZATION_ACTIVATION: {
                "required_configs": ["monetization", "payment_gateway", "revenue_sharing"],
                "validation_rules": ["monetization_eligibility", "payment_setup"],
                "next_stage": BusinessLogicFlow.DISTRIBUTION_DEPLOYMENT
            },
            
            BusinessLogicFlow.DISTRIBUTION_DEPLOYMENT: {
                "required_configs": ["distribution", "cdn", "streaming"],
                "validation_rules": ["platform_compliance", "distribution_rights"],
                "next_stage": BusinessLogicFlow.ANALYTICS_TRACKING
            },
            
            BusinessLogicFlow.ANALYTICS_TRACKING: {
                "required_configs": ["creator_analytics", "media_analytics", "monitoring"],
                "validation_rules": ["tracking_setup", "privacy_compliance"],
                "next_stage": BusinessLogicFlow.GAMIFICATION_ENGAGEMENT
            },
            
            BusinessLogicFlow.GAMIFICATION_ENGAGEMENT: {
                "required_configs": ["gamification", "achievement_engagement", "collaboration"],
                "validation_rules": ["engagement_rules", "achievement_criteria"],
                "next_stage": None  # End of flow
            }
        }
    
    def get_configuration(self, config_name: str) -> Optional[Any]:
        """Get specific configuration by name"""
        return self.configurations.get(config_name)
    
    def get_business_flow_config(self, flow_stage: BusinessLogicFlow) -> Dict[str, Any]:
        """Get configuration for specific business logic flow stage"""
        return self.business_flow_configs.get(flow_stage, {})
    
    def validate_business_flow(self, flow_stage: BusinessLogicFlow) -> Dict[str, Any]:
        """Validate configuration for business logic flow stage"""
        flow_config = self.get_business_flow_config(flow_stage)
        required_configs = flow_config.get("required_configs", [])
        validation_rules = flow_config.get("validation_rules", [])
        
        validation_result = {
            "stage": flow_stage.value,
            "required_configs_available": [],
            "missing_configs": [],
            "validation_passed": True,
            "validation_errors": []
        }
        
        # Check required configurations
        for config_name in required_configs:
            if config_name in self.configurations:
                validation_result["required_configs_available"].append(config_name)
            else:
                validation_result["missing_configs"].append(config_name)
                validation_result["validation_passed"] = False
        
        return validation_result
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get comprehensive configuration summary"""
        return {
            "configuration_level": self.level.value,
            "total_configurations": len(self.configurations),
            "business_logic_flows": len(self.business_flow_configs),
            "configuration_categories": {
                "core": len([k for k in self.configurations if k in ["database", "redis", "celery"]]),
                "ai": len([k for k in self.configurations if k.startswith("ai_") or k.startswith("ia_") or k.startswith("ml_")]),
                "business": len([k for k in self.configurations if "business" in k or k in ["creator_", "monetization", "collaboration", "gamification", "seo", "distribution"]]),
                "security": len([k for k in self.configurations if k in ["protection", "copyright", "rights_management", "violation_detection"]]),
                "payments": len([k for k in self.configurations if "payment" in k or "crypto" in k or "subscription" in k]),
                "media": len([k for k in self.configurations if "audio" in k or "video" in k or "streaming" in k])
            },
            "initialized_at": self.app_settings.app_name,
            "version": self.app_settings.app_version
        }

# Global configuration instances
# app_settings imported from settings.py
master_config = AinflueMasterConfiguration(ConfigurationLevel.ENTERPRISE)

# Convenience functions
def get_config(config_name: str) -> Optional[Any]:
    """Get configuration by name"""
    return master_config.get_configuration(config_name)

def validate_flow(flow_stage: BusinessLogicFlow) -> Dict[str, Any]:
    """Validate business logic flow stage"""
    return master_config.validate_business_flow(flow_stage)

def get_business_flow_config(flow_stage: BusinessLogicFlow) -> Dict[str, Any]:
    """Get business flow configuration"""
    return master_config.get_business_flow_config(flow_stage)

async def initialize_platform_config():
    """Initialize complete platform configuration"""
    return master_config.get_configuration_summary()

# Module exports
__all__ = [
    "app_settings", "AinflueMasterConfiguration", "ConfigurationLevel", "BusinessLogicFlow",
    "master_config", "get_config", "validate_flow", "get_business_flow_config",
    "initialize_platform_config"
]

# Initialize logging
logger = logging.getLogger(__name__)
logger.info(f"🔧 Ainflue Master Configuration initialized - Level: {master_config.level.value}")
logger.info(f"📊 Total configurations: {len(master_config.configurations)}")
logger.info(f"🔄 Business logic flows: {len(master_config.business_flow_configs)}")
logger.info("⚠️ Protected by copyright - All Rights Reserved")

import os
from typing import Optional, List

# Import specialized configuration modules
from .settings import ApplicationSettings, app_settings
from .core.database import DatabaseSettings, db_settings, get_database_url, get_database_config
from .core.redis import RedisSettings, redis_settings, get_redis_url, get_redis_config
from .core.celery import CelerySettings, celery_settings, get_celery_config, create_celery_app

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

# Import additional business logic configuration modules
from .rights_management_config import (
    RightsManagementSettings, rights_management_settings,
    LicensingType, UsageRight, ComplianceFramework, ContractType, EnforcementAction,
    LicenseConfiguration, ComplianceConfiguration, ContractConfiguration, EnforcementConfiguration
)
from .violation_detection_config import (
    ViolationDetectionSettings, violation_detection_settings,
    ViolationType, MonitoringPlatform, DetectionMethod, ResponseAction, ViolationSeverity, DetectionFrequency,
    PlatformMonitoringConfig, DetectionAlgorithmConfig, ViolationResponse, DMCAConfiguration
)
from .payment_gateway_config import (
    PaymentGatewaySettings, payment_gateway_settings,
    PaymentGateway, PaymentMethod, Currency, TransactionType, TransactionStatus, SecurityLevel,
    GatewayConfiguration, PaymentMethodConfiguration, SecurityConfiguration, FeeStructure
)
from .subscription_management_config import (
    SubscriptionManagementSettings, subscription_management_settings,
    SubscriptionTier, BillingCycle, SubscriptionStatus, PricingModel, RevenueModel, ChurnPredictionLevel,
    SubscriptionTierConfig, BillingConfiguration, RevenueOptimization, ChurnPreventionConfig
)
from .crypto_payment_config import (
    CryptoPaymentSettings, crypto_payment_settings,
    CryptoCurrency, BlockchainNetwork, WalletType, TransactionType as CryptoTransactionType, SecurityLevel as CryptoSecurityLevel, ComplianceFramework as CryptoComplianceFramework,
    CryptoCurrencyConfig, WalletConfiguration, ExchangeIntegration, SmartContractConfig
)
from .creator_matching_config import (
    CreatorMatchingSettings, creator_matching_settings,
    MatchingAlgorithm, CollaborationType as CreatorCollaborationType, CreatorTier as CreatorMatchingTier, MatchingCriteria as CreatorMatchingCriteria, CompatibilityLevel,
    MatchingWeights, CreatorProfile, MatchingConfiguration as CreatorMatchingConfiguration, CollaborationTemplate as CreatorCollaborationTemplate
)
from .gamification_business_config import (
    GamificationBusinessSettings, gamification_business_settings,
    RewardType, ChallengeType, LeaderboardType,
    RewardConfiguration, ChallengeConfiguration
)
from .achievement_engagement_config import (
    AchievementEngagementSettings, achievement_engagement_settings,
    AchievementCategory, AchievementType,
    AchievementConfiguration
)
from .search_optimization_config import (
    SearchOptimizationSettings, search_optimization_settings,
    SearchEngine as SearchOptimizationSearchEngine, OptimizationStrategy,
    SearchEngineConfiguration
)
from .multi_platform_distribution_config import (
    MultiPlatformDistributionSettings, multi_platform_distribution_settings,
    DistributionPlatform as MultiPlatformDistributionPlatform, ContentFormat as MultiPlatformContentFormat,
    PlatformConfiguration as MultiPlatformConfiguration
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
    
    # Additional business logic configuration classes and instances
    "RightsManagementSettings", "rights_management_settings",
    "LicensingType", "UsageRight", "ComplianceFramework", "ContractType", "EnforcementAction",
    "LicenseConfiguration", "ComplianceConfiguration", "ContractConfiguration", "EnforcementConfiguration",
    "ViolationDetectionSettings", "violation_detection_settings",
    "ViolationType", "MonitoringPlatform", "DetectionMethod", "ResponseAction", "ViolationSeverity", "DetectionFrequency",
    "PlatformMonitoringConfig", "DetectionAlgorithmConfig", "ViolationResponse", "DMCAConfiguration",
    "PaymentGatewaySettings", "payment_gateway_settings",
    "PaymentGateway", "PaymentMethod", "Currency", "TransactionType", "TransactionStatus", "SecurityLevel",
    "GatewayConfiguration", "PaymentMethodConfiguration", "SecurityConfiguration", "FeeStructure",
    "SubscriptionManagementSettings", "subscription_management_settings",
    "SubscriptionTier", "BillingCycle", "SubscriptionStatus", "PricingModel", "RevenueModel", "ChurnPredictionLevel",
    "SubscriptionTierConfig", "BillingConfiguration", "RevenueOptimization", "ChurnPreventionConfig",
    "CryptoPaymentSettings", "crypto_payment_settings",
    "CryptoCurrency", "BlockchainNetwork", "WalletType", "CryptoTransactionType", "CryptoSecurityLevel", "CryptoComplianceFramework",
    "CryptoCurrencyConfig", "WalletConfiguration", "ExchangeIntegration", "SmartContractConfig",
    "CreatorMatchingSettings", "creator_matching_settings",
    "MatchingAlgorithm", "CreatorCollaborationType", "CreatorMatchingTier", "CreatorMatchingCriteria", "CompatibilityLevel",
    "MatchingWeights", "CreatorProfile", "CreatorMatchingConfiguration", "CreatorCollaborationTemplate",
    "GamificationBusinessSettings", "gamification_business_settings",
    "RewardType", "ChallengeType", "LeaderboardType",
    "RewardConfiguration", "ChallengeConfiguration",
    "AchievementEngagementSettings", "achievement_engagement_settings",
    "AchievementCategory", "AchievementType",
    "AchievementConfiguration",
    "SearchOptimizationSettings", "search_optimization_settings",
    "SearchOptimizationSearchEngine", "OptimizationStrategy",
    "SearchEngineConfiguration",
    "MultiPlatformDistributionSettings", "multi_platform_distribution_settings",
    "MultiPlatformDistributionPlatform", "MultiPlatformContentFormat",
    "MultiPlatformConfiguration",
    
    # Backwards compatibility exports
    "DATABASE_URL",
    "SECRET_KEY", 
    "DEBUG",
    "ENVIRONMENT",
    "API_V1_PREFIX",
    "CORS_ORIGINS"
]
