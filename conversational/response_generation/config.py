"""Response Generation Configuration - IA Influencer Agent

Enterprise configuration management for response generation system with 
comprehensive environment-specific settings, AI model configurations, 
platform integrations, and advanced system tuning for multi-format creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de

Features:
- Multi-environment configuration management
- AI model configuration and optimization
- Platform-specific API configurations
- Security and encryption settings
- Performance tuning and scaling options
- Multi-language and localization settings
- Business intelligence configuration
- Content protection and compliance settings
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from decimal import Decimal

from pydantic import BaseSettings, Field, validator, SecretStr
import yaml
from cryptography.fernet import Fernet


class Environment(Enum):
    """
Environment types for deployment"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    LOCAL = "local"


class ResponseQualityLevel(Enum):
    """Response quality configuration levels"""

    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ModelProvider(Enum):
    """AI model provider types"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"
    CUSTOM = "custom"


class PlatformType(Enum):
    """Platform integration types"""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    DISCORD = "discord"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


@dataclass
class ModelConfiguration:
    """AI model configuration for response generation"""
    model_name: str
    model_type: str
    provider: ModelProvider
    api_endpoint: Optional[str] = None
    api_key: Optional[SecretStr] = None
    api_version: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    timeout: int = 30
    retry_attempts: int = 3
    backup_models: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    context_window: int = 8192
    fine_tuned_model_id: Optional[str] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class PlatformConfiguration:
    """
Platform-specific API configuration"""
    platform: PlatformType
    client_id: Optional[SecretStr] = None
    client_secret: Optional[SecretStr] = None
    access_token: Optional[SecretStr] = None
    refresh_token: Optional[SecretStr] = None
    api_key: Optional[SecretStr] = None
    api_version: str = "v1"
    base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    rate_limit_per_hour: int = 1000
    timeout: int = 30
    enabled: bool = True
    sandbox_mode: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class DatabaseConfiguration:
    """Database connection and optimization settings"""
    database_url: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    isolation_level: str = "READ_COMMITTED"
    connection_timeout: int = 30
    query_timeout: int = 60
    enable_query_cache: bool = True
    cache_size: int = 1000
    encryption_key: Optional[SecretStr] = None


@dataclass
class CacheConfiguration:
    """Cache system configuration"""
    redis_url: str
    default_ttl: int = 3600
    max_connections: int = 100
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    health_check_interval: int = 30
    retry_on_timeout: bool = True
    decode_responses: bool = True
    key_prefix: str = "response_gen:"
    cluster_mode: bool = False
    sentinel_hosts: List[str] = field(default_factory=list)


@dataclass
class SecurityConfiguration:
    """Security and encryption settings"""
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    encryption_key: SecretStr
    password_hash_algorithm: str = "bcrypt"
    password_hash_rounds: int = 12
    api_key_length: int = 32
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    enable_2fa: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    ssl_verify: bool = True
    content_security_policy: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class QualityConfiguration:
    """Response quality assurance settings"""
    quality_level: ResponseQualityLevel = ResponseQualityLevel.HIGH
    min_confidence_score: float = 0.8
    enable_fact_checking: bool = True
    enable_bias_detection: bool = True
    enable_toxicity_filtering: bool = True
    enable_plagiarism_check: bool = True
    max_response_length: int = 2000
    min_response_length: int = 50
    enable_grammar_check: bool = True
    enable_style_consistency: bool = True
    quality_metrics_tracking: bool = True
    a_b_testing_enabled: bool = True
    performance_monitoring: bool = True


@dataclass
class PersonalizationConfiguration:
    """
User personalization settings"""
    enable_personalization: bool = True
    learning_rate: float = 0.01
    min_interactions_for_personalization: int = 10
    max_user_profile_size: int = 10000
    enable_collaborative_filtering: bool = True
    enable_content_based_filtering: bool = True
    enable_demographic_targeting: bool = True
    enable_behavioral_analysis: bool = True
    segment_update_frequency_hours: int = 24
    preference_decay_rate: float = 0.95
    enable_real_time_adaptation: bool = True


@dataclass
class BusinessIntelligenceConfiguration:
    """
Business intelligence and analytics settings"""
    enable_revenue_tracking: bool = True
    enable_market_analysis: bool = True
    enable_competitor_monitoring: bool = True
    enable_trend_prediction: bool = True
    financial_data_retention_days: int = 730
    market_data_update_frequency_hours: int = 6
    enable_roi_calculation: bool = True
    enable_investment_recommendations: bool = True
    currency_conversion_api: Optional[str] = None
    tax_calculation_regions: List[str] = field(default_factory=list)
    enable_compliance_monitoring: bool = True


@dataclass
class ContentProtectionConfiguration:
    """
Content protection and IP management settings"""
    enable_fingerprinting: bool = True
    enable_monitoring: bool = True
    enable_automated_takedowns: bool = True
    fingerprint_similarity_threshold: float = 0.85
    monitoring_frequency_hours: int = 24
    legal_document_templates_path: str = "templates/legal/"
    supported_jurisdictions: List[str] = field(default_factory=list)
    enable_blockchain_timestamping: bool = True
    enable_watermarking: bool = True
    dmca_auto_response: bool = True


@dataclass
class MultimodalConfiguration:
    """Multimodal content generation settings"""
    enable_audio_generation: bool = True
    enable_image_generation: bool = True
    enable_video_generation: bool = True
    enable_text_to_speech: bool = True
    enable_speech_to_text: bool = True
    max_audio_duration_seconds: int = 300
    max_image_resolution: str = "1920x1080"
    max_video_duration_seconds: int = 600
    supported_audio_formats: List[str] = field(default_factory=lambda: ["mp3", "wav", "flac"])
    supported_image_formats: List[str] = field(default_factory=lambda: ["jpg", "png", "webp"])
    supported_video_formats: List[str] = field(default_factory=lambda: ["mp4", "mov", "avi"])
    enable_accessibility_features: bool = True


@dataclass
class InternationalizationConfiguration:
    """Multi-language and localization settings"""
    default_language: str = "en"
    supported_languages: List[str] = field(default_factory=lambda: [
        "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"
    ])
    enable_auto_translation: bool = True
    translation_service: str = "google_translate"
    enable_cultural_adaptation: bool = True
    regional_content_filters: Dict[str, List[str]] = field(default_factory=dict)
    currency_by_region: Dict[str, str] = field(default_factory=dict)
    timezone_handling: str = "auto_detect"


@dataclass
class PerformanceConfiguration:
    """Performance optimization settings"""
    enable_caching: bool = True
    enable_async_processing: bool = True
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 30
    enable_request_batching: bool = True
    batch_size: int = 10
    enable_response_compression: bool = True
    enable_cdn: bool = True
    cdn_url: Optional[str] = None
    enable_load_balancing: bool = True
    health_check_interval_seconds: int = 30


@dataclass
class LoggingConfiguration:
    """
Logging and monitoring settings"""
    log_level: str = "INFO"
    log_format: str = "json"
    enable_structured_logging: bool = True
    enable_performance_logging: bool = True
    enable_audit_logging: bool = True
    log_retention_days: int = 90
    enable_log_aggregation: bool = True
    log_aggregation_service: Optional[str] = None
    enable_error_tracking: bool = True
    error_tracking_service: Optional[str] = None
    enable_metrics_collection: bool = True
    metrics_export_interval_seconds: int = 60


class ResponseGenerationConfig(BaseSettings):
    """Main configuration class for the response generation system"""
    
    # Environment settings
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    testing: bool = Field(default=False, env="TESTING")
    
    # Model configurations
    primary_model: ModelConfiguration = None
    fallback_models: List[ModelConfiguration] = field(default_factory=list)
    
    # Platform configurations
    platforms: List[PlatformConfiguration] = field(default_factory=list)
    
    # System configurations
    database: DatabaseConfiguration = None
    cache: CacheConfiguration = None
    security: SecurityConfiguration = None
    quality: QualityConfiguration = field(default_factory=QualityConfiguration)
    personalization: PersonalizationConfiguration = field(default_factory=PersonalizationConfiguration)
    business_intelligence: BusinessIntelligenceConfiguration = field(default_factory=BusinessIntelligenceConfiguration)
    content_protection: ContentProtectionConfiguration = field(default_factory=ContentProtectionConfiguration)
    multimodal: MultimodalConfiguration = field(default_factory=MultimodalConfiguration)
    internationalization: InternationalizationConfiguration = field(default_factory=InternationalizationConfiguration)
    performance: PerformanceConfiguration = field(default_factory=PerformanceConfiguration)
    logging: LoggingConfiguration = field(default_factory=LoggingConfiguration)
    
    # Feature flags
    enable_neural_generation: bool = Field(default=True, env="ENABLE_NEURAL_GENERATION")
    enable_business_intelligence: bool = Field(default=True, env="ENABLE_BUSINESS_INTELLIGENCE")
    enable_content_protection: bool = Field(default=True, env="ENABLE_CONTENT_PROTECTION")
    enable_collaboration_intelligence: bool = Field(default=True, env="ENABLE_COLLABORATION_INTELLIGENCE")
    enable_revenue_intelligence: bool = Field(default=True, env="ENABLE_REVENUE_INTELLIGENCE")
    enable_multimodal_generation: bool = Field(default=True, env="ENABLE_MULTIMODAL_GENERATION")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    
    class Config:
        env_file = ".env"
        env_prefix = "RESPONSE_GEN_"
        case_sensitive = True
        use_enum_values = True
    
    @validator('primary_model', pre=True)
    def validate_primary_model(cls, v):
        if isinstance(v, dict):
            return ModelConfiguration(**v)
        return v
    
    @validator('platforms', pre=True)
    def validate_platforms(cls, v):
        if isinstance(v, list):
            return [PlatformConfiguration(**item) if isinstance(item, dict) else item for item in v]
        return v
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'ResponseGenerationConfig':
        """Load configuration from YAML or JSON file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.yaml' or config_file.suffix.lower() == '.yml':
                config_data = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to YAML or JSON file"""
        config_file = Path(config_path)
        config_data = self.dict()
        
        # Convert SecretStr objects to strings for serialization
        def convert_secrets(obj):
            if isinstance(obj, dict):
                return {k: convert_secrets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_secrets(item) for item in obj]
            elif hasattr(obj, 'get_secret_value'):
                return obj.get_secret_value()
            else:
                return obj
        
        config_data = convert_secrets(config_data)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.yaml' or config_file.suffix.lower() == '.yml':
                yaml.safe_dump(config_data, f, default_flow_style=False, indent=2)
            elif config_file.suffix.lower() == '.json':
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
    
    def get_platform_config(self, platform: PlatformType) -> Optional[PlatformConfiguration]:
        """Get configuration for a specific platform"""
        for platform_config in self.platforms:
            if platform_config.platform == platform:
                return platform_config
        return None
    
    def is_production(self) -> bool:
        """
Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def get_model_config(self, model_name: Optional[str] = None) -> ModelConfiguration:
        """
Get model configuration by name or return primary model"""
        if model_name:
            for model in self.fallback_models:
                if model.model_name == model_name:
                    return model
        return self.primary_model


# Default configurations for different environments
DEFAULT_CONFIGS = {
    Environment.DEVELOPMENT: {
        "debug": True,
        "quality": {"quality_level": "standard", "enable_fact_checking": False},
        "performance": {"max_concurrent_requests": 10},
        "logging": {"log_level": "DEBUG"}
    },
    Environment.STAGING: {
        "debug": False,
        "quality": {"quality_level": "high"},
        "performance": {"max_concurrent_requests": 50},
        "logging": {"log_level": "INFO"}
    },
    Environment.PRODUCTION: {
        "debug": False,
        "quality": {"quality_level": "enterprise"},
        "performance": {"max_concurrent_requests": 100},
        "logging": {"log_level": "WARNING"},
        "security": {"enable_2fa": True, "ssl_verify": True}
    }
}


def create_config_for_environment(env: Environment) -> ResponseGenerationConfig:
    """Create configuration for specific environment"""
    base_config = DEFAULT_CONFIGS.get(env, {})
    return ResponseGenerationConfig(environment=env, **base_config)


def encrypt_sensitive_config(config: ResponseGenerationConfig, encryption_key: bytes) -> Dict[str, Any]:
    """
Encrypt sensitive configuration values"""
    fernet = Fernet(encryption_key)
    config_dict = config.dict()
    
    # Encrypt sensitive fields
    sensitive_fields = [
        'primary_model.api_key',
        'database.database_url',
        'cache.redis_url',
        'security.jwt_secret_key',
        'security.encryption_key'
    ]
    
    for field_path in sensitive_fields:
        keys = field_path.split('.')
        current = config_dict
        
        for key in keys[:-1]:
            if key in current and isinstance(current[key], dict):
                current = current[key]
            else:
                break
        else:
            final_key = keys[-1]
            if final_key in current and current[final_key]:
                value = str(current[final_key])
                encrypted_value = fernet.encrypt(value.encode()).decode()
                current[final_key] = encrypted_value
    
    return config_dict
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    retry_attempts: int = 3
    cache_ttl: int = 3600
    rate_limit: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseConfiguration:
    """
Response generation configuration"""
    max_length: int = 2000
    min_length: int = 50
    quality_threshold: float = 0.8
    personalization_level: float = 0.7
    context_window: int = 10
    enable_multimodal: bool = True
    enable_neural_generation: bool = True
    enable_template_fallback: bool = True
    response_timeout: int = 15
    concurrent_limit: int = 50
    cache_responses: bool = True
    cache_ttl: int = 1800


class ResponseGenerationSettings(BaseSettings):
    """
    Comprehensive settings for response generation system
    """
    
    # Environment Configuration
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    elasticsearch_url: str = Field(..., env="ELASTICSEARCH_URL")
    
    # AI Model Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    huggingface_api_key: Optional[str] = Field(None, env="HUGGINGFACE_API_KEY")
    
    # Response Quality Configuration
    quality_level: ResponseQualityLevel = ResponseQualityLevel.HIGH
    enable_quality_assurance: bool = True
    enable_real_time_optimization: bool = True
    
    # Performance Configuration
    max_concurrent_responses: int = 100
    response_timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600
    
    # Security Configuration
    enable_content_filtering: bool = True
    enable_privacy_protection: bool = True
    enable_audit_logging: bool = True
    
    # Feature Flags
    enable_revenue_intelligence: bool = True
    enable_protection_responses: bool = True
    enable_collaboration_intelligence: bool = True
    enable_neural_generation: bool = True
    enable_multimodal_responses: bool = True
    
    # Analytics Configuration
    enable_analytics: bool = True
    analytics_sampling_rate: float = 1.0
    enable_ab_testing: bool = True
    
    # Monitoring Configuration
    enable_metrics: bool = True
    metrics_interval: int = 60
    enable_tracing: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ResponseGenerationConfig:
    """
    Central configuration manager for response generation system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.settings = ResponseGenerationSettings()
        self._load_configuration()
    
    def _get_default_config_path(self) -> str:
        """
Get default configuration file path"""
        return os.path.join(
            os.path.dirname(__file__), 
            "config", 
            f"response_generation_{self.settings.environment.value}.yaml"
        )
    
    def _load_configuration(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                self._merge_configuration(config_data)
    
    def _merge_configuration(self, config_data: Dict[str, Any]):
        """
Merge configuration data with settings"""
        # Implementation for merging configuration
        pass
    
    def get_model_config(self, model_name: str) -> ModelConfiguration:
        """
Get configuration for specific AI model"""
        model_configs = {
            "gpt-4": ModelConfiguration(
                model_name="gpt-4",
                model_type="openai",
                max_tokens=4096,
                temperature=0.7,
                timeout=30
            ),
            "claude-3": ModelConfiguration(
                model_name="claude-3-opus-20240229",
                model_type="anthropic",
                max_tokens=4096,
                temperature=0.7,
                timeout=30
            ),
            "t5-large": ModelConfiguration(
                model_name="t5-large",
                model_type="huggingface",
                max_tokens=2048,
                temperature=0.7,
                timeout=20
            )
        }
        
        return model_configs.get(model_name, model_configs["gpt-4"])
    
    def get_response_config(self, response_type: str) -> ResponseConfiguration:
        """Get configuration for specific response type"""
        base_config = ResponseConfiguration()
        
        type_specific_configs = {
            "business": ResponseConfiguration(
                max_length=3000,
                quality_threshold=0.9,
                personalization_level=0.8
            ),
            "creative": ResponseConfiguration(
                max_length=2500,
                quality_threshold=0.8,
                personalization_level=0.9
            ),
            "technical": ResponseConfiguration(
                max_length=4000,
                quality_threshold=0.95,
                personalization_level=0.6
            ),
            "quick": ResponseConfiguration(
                max_length=500,
                quality_threshold=0.7,
                response_timeout=5
            )
        }
        
        return type_specific_configs.get(response_type, base_config)
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return {
            "revenue_intelligence": self.settings.enable_revenue_intelligence,
            "protection_responses": self.settings.enable_protection_responses,
            "collaboration_intelligence": self.settings.enable_collaboration_intelligence,
            "neural_generation": self.settings.enable_neural_generation,
            "multimodal_responses": self.settings.enable_multimodal_responses,
            "quality_assurance": self.settings.enable_quality_assurance,
            "real_time_optimization": self.settings.enable_real_time_optimization,
            "analytics": self.settings.enable_analytics,
            "ab_testing": self.settings.enable_ab_testing
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            "max_concurrent_responses": self.settings.max_concurrent_responses,
            "response_timeout": self.settings.response_timeout,
            "cache_enabled": self.settings.cache_enabled,
            "cache_ttl": self.settings.cache_ttl,
            "metrics_interval": self.settings.metrics_interval
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "content_filtering": self.settings.enable_content_filtering,
            "privacy_protection": self.settings.enable_privacy_protection,
            "audit_logging": self.settings.enable_audit_logging
        }
    
    def update_setting(self, key: str, value: Any):
        """Update a specific setting"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
        else:
            raise ValueError(f"Unknown setting: {key}")
    
    def save_configuration(self):
        """Save current configuration to file"""
        config_data = {
            "environment": self.settings.environment.value,
            "quality_level": self.settings.quality_level.value,
            "performance": self.get_performance_config(),
            "security": self.get_security_config(),
            "features": self.get_feature_flags()
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)


# Global configuration instance
config = ResponseGenerationConfig()


# Configuration presets for different deployment scenarios
DEVELOPMENT_CONFIG = {
    "debug": True,
    "log_level": "DEBUG",
    "enable_analytics": False,
    "cache_enabled": False,
    "max_concurrent_responses": 10
}

PRODUCTION_CONFIG = {
    "debug": False,
    "log_level": "WARNING",
    "enable_analytics": True,
    "cache_enabled": True,
    "max_concurrent_responses": 200,
    "enable_quality_assurance": True,
    "enable_real_time_optimization": True
}

TESTING_CONFIG = {
    "debug": True,
    "log_level": "DEBUG",
    "enable_analytics": False,
    "cache_enabled": False,
    "response_timeout": 5,
    "max_concurrent_responses": 5
}


def get_config_for_environment(env: Environment) -> Dict[str, Any]:
    """Get configuration preset for specific environment"""
    configs = {
        Environment.DEVELOPMENT: DEVELOPMENT_CONFIG,
        Environment.PRODUCTION: PRODUCTION_CONFIG,
        Environment.TESTING: TESTING_CONFIG,
        Environment.STAGING: PRODUCTION_CONFIG  # Use production config for staging
    }
    
    return configs.get(env, DEVELOPMENT_CONFIG)


def apply_environment_config(env: Environment):
    """
Apply environment-specific configuration"""
    env_config = get_config_for_environment(env)
    
    for key, value in env_config.items():
        config.update_setting(key, value)
    
    return config
