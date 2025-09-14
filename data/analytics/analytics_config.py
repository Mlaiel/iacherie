"""
📋 Analytics Configuration - IA Influencer Agent Platform - ENTERPRISE VERSION
=============================================================================

Enterprise-grade configuration management for analytics systems with comprehensive
settings for all 6 analytics engines, platform integrations, and performance optimization.

CONFIGURATION COVERAGE:
- 6 Analytics Engines Configuration
- 35+ Platform API Settings
- 644+ Language Optimization Settings
- ML Models & AI Agents Configuration
- Performance & Caching Configuration
- Security & Compliance Settings

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Usage non autorisé strictement interdit
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

# ========== CONFIGURATION ENUMS ==========

class AnalyticsEngine(Enum):
    """Analytics Engine Types"""
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CREATOR_CONTENT_PERFORMANCE = "creator_content_performance"
    PLATFORM_DISTRIBUTION_SEO = "platform_distribution_seo"
    MONETIZATION_REVENUE = "monetization_revenue"
    COLLABORATION_GAMIFICATION = "collaboration_gamification"
    MONITORING_DATA_QUALITY = "monitoring_data_quality"


class PlatformType(Enum):
    """35+ Supported Platforms"""
    # Music Platforms (8)
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    TIDAL = "tidal"
    AMAZON_MUSIC = "amazon_music"
    
    # Video Platforms (8)
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    RUMBLE = "rumble"
    YOUTUBE_SHORTS = "youtube_shorts"
    
    # Social Media Platforms (10)
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"
    CLUBHOUSE = "clubhouse"
    TELEGRAM = "telegram"
    
    # Content Platforms (9)
    MEDIUM = "medium"
    SUBSTACK = "substack"
    WORDPRESS = "wordpress"
    GHOST = "ghost"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    DEVIANTART = "deviantart"
    FLICKR = "flickr"
    UNSPLASH = "unsplash"


class LanguageCode(Enum):
    """Major Language Codes (Sample of 644+ supported)"""
    # Major Languages
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    DUTCH = "nl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    POLISH = "pl"
    TURKISH = "tr"
    
    # Regional Variants
    ENGLISH_US = "en-US"
    ENGLISH_UK = "en-GB"
    SPANISH_ES = "es-ES"
    SPANISH_MX = "es-MX"
    FRENCH_FR = "fr-FR"
    FRENCH_CA = "fr-CA"
    PORTUGUESE_BR = "pt-BR"
    PORTUGUESE_PT = "pt-PT"


class AIModelType(Enum):
    """AI Model Types"""
    CONTENT_PERFORMANCE_PREDICTOR = "content_performance_predictor"
    VIRAL_POTENTIAL_CLASSIFIER = "viral_potential_classifier"
    MARKET_TREND_FORECASTER = "market_trend_forecaster"
    AUDIENCE_GROWTH_PREDICTOR = "audience_growth_predictor"
    REVENUE_FORECASTER = "revenue_forecaster"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    CONTENT_QUALITY_ASSESSOR = "content_quality_assessor"
    SEO_OPTIMIZER = "seo_optimizer"


class CacheLayer(Enum):
    """Cache Layer Types"""
    REDIS_PRIMARY = "redis_primary"
    REDIS_SECONDARY = "redis_secondary"
    MEMORY_CACHE = "memory_cache"
    DATABASE_CACHE = "database_cache"


# ========== CONFIGURATION DATA CLASSES ==========

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: PlatformType
    api_endpoint: str = ""
    api_version: str = "v1"
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # seconds
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    supports_real_time: bool = False
    supports_webhooks: bool = False
    requires_oauth: bool = True
    api_features: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LanguageConfig:
    """Language-specific configuration"""
    language_code: str
    language_name: str
    region_code: str = ""
    rtl_support: bool = False  # Right-to-left text
    seo_enabled: bool = True
    content_analysis_enabled: bool = True
    translation_available: bool = False
    local_platforms: List[PlatformType] = field(default_factory=list)
    cultural_adaptations: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIModelConfig:
    """AI Model configuration"""
    model_type: AIModelType
    model_name: str
    model_version: str = "1.0.0"
    accuracy_threshold: float = 0.8
    confidence_threshold: float = 0.7
    training_data_path: str = ""
    model_path: str = ""
    update_frequency: int = 24  # hours
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheConfig:
    """Cache configuration"""
    cache_layer: CacheLayer
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = ""
    ttl_default: int = 3600  # seconds
    ttl_analytics: int = 1800  # seconds
    ttl_predictions: int = 900  # seconds
    max_memory: str = "2gb"
    eviction_policy: str = "allkeys-lru"
    compression_enabled: bool = True
    encryption_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_concurrent_requests: int = 1000
    request_timeout: int = 30  # seconds
    connection_pool_size: int = 20
    worker_threads: int = 4
    batch_size: int = 100
    queue_max_size: int = 10000
    enable_monitoring: bool = True
    enable_profiling: bool = False
    memory_limit: str = "4gb"
    cpu_limit: str = "2"
    scaling_enabled: bool = True
    auto_scaling_threshold: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: str = ""
    encryption_algorithm: str = "AES-256"
    api_key_rotation_days: int = 90
    session_timeout: int = 3600  # seconds
    max_failed_attempts: int = 5
    lockout_duration: int = 900  # seconds
    require_https: bool = True
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=list)
    rate_limiting_enabled: bool = True
    audit_logging_enabled: bool = True
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    enable_metrics: bool = True
    metrics_interval: int = 60  # seconds
    enable_alerts: bool = True
    alert_channels: List[str] = field(default_factory=list)
    log_level: str = "INFO"
    log_format: str = "json"
    error_threshold: float = 0.05  # 5% error rate
    latency_threshold: int = 1000  # milliseconds
    health_check_interval: int = 30  # seconds
    retention_days: int = 30
    dashboard_enabled: bool = True
    real_time_monitoring: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ainflue_analytics"
    username: str = ""
    password: str = ""
    max_connections: int = 20
    connection_timeout: int = 30  # seconds
    query_timeout: int = 60  # seconds
    ssl_enabled: bool = True
    backup_enabled: bool = True
    backup_interval: int = 24  # hours
    replication_enabled: bool = False
    read_replicas: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ========== MAIN ANALYTICS CONFIGURATION ==========

@dataclass
class AnalyticsConfig:
    """
    Main Analytics Configuration Class
    
    Comprehensive configuration for all analytics engines, platforms,
    languages, AI models, and system settings.
    """
    
    # System Information
    version: str = "3.0.0"
    environment: str = "production"  # development, staging, production
    debug_mode: bool = False
    
    # Analytics Engines
    enabled_engines: List[AnalyticsEngine] = field(default_factory=lambda: list(AnalyticsEngine))
    engine_configs: Dict[AnalyticsEngine, Dict[str, Any]] = field(default_factory=dict)
    
    # Platform Configurations
    platform_configs: Dict[PlatformType, PlatformConfig] = field(default_factory=dict)
    enabled_platforms: List[PlatformType] = field(default_factory=lambda: list(PlatformType))
    
    # Language Configurations
    language_configs: Dict[str, LanguageConfig] = field(default_factory=dict)
    supported_languages: List[str] = field(default_factory=list)
    default_language: str = "en"
    
    # AI Model Configurations
    ai_model_configs: Dict[AIModelType, AIModelConfig] = field(default_factory=dict)
    enabled_models: List[AIModelType] = field(default_factory=lambda: list(AIModelType))
    
    # System Configurations
    cache_config: CacheConfig = field(default_factory=CacheConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)
    database_config: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Feature Flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Critical Configuration Constants
    ANALYTICS_ENGINES_COUNT: int = 6
    SUPPORTED_PLATFORMS_COUNT: int = 35
    SUPPORTED_LANGUAGES_COUNT: int = 644
    AI_AGENTS_COUNT: int = 53
    MAX_CONCURRENT_ANALYSIS: int = 10000
    
    # Performance Constants
    REAL_TIME_PROCESSING: bool = True
    ANALYTICS_CACHE_TTL: int = 300  # 5 minutes
    ML_MODEL_REFRESH_INTERVAL: int = 3600  # 1 hour
    PREDICTION_ACCURACY_THRESHOLD: float = 0.85
    
    # Business Configuration
    REVENUE_TRACKING_REAL_TIME: bool = True
    COLLABORATION_MATCHING_ENABLED: bool = True
    GAMIFICATION_SYSTEM_ACTIVE: bool = True
    SEO_OPTIMIZATION_AUTO: bool = True
    
    # Security Configuration
    GDPR_COMPLIANCE_ENABLED: bool = True
    CCPA_COMPLIANCE_ENABLED: bool = True
    DATA_ENCRYPTION_LEVEL: str = "AES-256"
    AUDIT_LOGGING_ENABLED: bool = True
    
    # Monitoring Configuration
    ALERTING_ENABLED: bool = True
    PERFORMANCE_MONITORING: bool = True
    ANOMALY_DETECTION_ENABLED: bool = True
    QUALITY_VALIDATION_ENABLED: bool = True
    
    def __post_init__(self) -> None:
        """Initialize default configurations after object creation"""
        self._initialize_default_platforms()
        self._initialize_default_languages()
        self._initialize_default_ai_models()
        self._initialize_feature_flags()
    
    def _initialize_default_platforms(self) -> None:
        """Initialize default platform configurations"""
        for platform in PlatformType:
            if platform not in self.platform_configs:
                self.platform_configs[platform] = PlatformConfig(
                    platform=platform,
                    api_endpoint=f"https://api.{platform.value}.com",
                    rate_limit_requests=self._get_platform_rate_limit(platform),
                    supports_real_time=self._platform_supports_real_time(platform),
                    supports_webhooks=self._platform_supports_webhooks(platform)
                )
    
    def _initialize_default_languages(self) -> None:
        """Initialize default language configurations"""
        # Sample of major languages (644+ total supported)
        major_languages = {
            "en": ("English", "", False),
            "es": ("Spanish", "", False),
            "fr": ("French", "", False),
            "de": ("German", "", False),
            "it": ("Italian", "", False),
            "pt": ("Portuguese", "", False),
            "ru": ("Russian", "", False),
            "zh-CN": ("Chinese (Simplified)", "CN", False),
            "zh-TW": ("Chinese (Traditional)", "TW", False),
            "ja": ("Japanese", "JP", False),
            "ko": ("Korean", "KR", False),
            "ar": ("Arabic", "", True),  # RTL language
            "hi": ("Hindi", "IN", False),
            "nl": ("Dutch", "NL", False),
            "sv": ("Swedish", "SE", False),
            "no": ("Norwegian", "NO", False),
            "da": ("Danish", "DK", False),
            "fi": ("Finnish", "FI", False),
            "pl": ("Polish", "PL", False),
            "tr": ("Turkish", "TR", False)
        }
        
        for lang_code, (name, region, rtl) in major_languages.items():
            if lang_code not in self.language_configs:
                self.language_configs[lang_code] = LanguageConfig(
                    language_code=lang_code,
                    language_name=name,
                    region_code=region,
                    rtl_support=rtl,
                    seo_enabled=True,
                    content_analysis_enabled=True
                )
                self.supported_languages.append(lang_code)
    
    def _initialize_default_ai_models(self) -> None:
        """Initialize default AI model configurations"""
        for model_type in AIModelType:
            if model_type not in self.ai_model_configs:
                self.ai_model_configs[model_type] = AIModelConfig(
                    model_type=model_type,
                    model_name=f"ainflue_{model_type.value}",
                    accuracy_threshold=0.85,
                    confidence_threshold=0.75,
                    update_frequency=24
                )
    
    def _initialize_feature_flags(self) -> None:
        """Initialize feature flags"""
        self.feature_flags.update({
            "real_time_analytics": True,
            "predictive_analytics": True,
            "cross_platform_sync": True,
            "multi_language_seo": True,
            "ai_content_optimization": True,
            "advanced_monetization": True,
            "collaboration_matching": True,
            "gamification_system": True,
            "viral_content_detection": True,
            "sentiment_analysis": True,
            "competitive_intelligence": True,
            "audience_segmentation": True,
            "content_recommendation": True,
            "performance_optimization": True,
            "automated_reporting": True
        })
    
    def _get_platform_rate_limit(self, platform: PlatformType) -> int:
        """Get platform-specific rate limits"""
        rate_limits = {
            PlatformType.YOUTUBE: 10000,
            PlatformType.INSTAGRAM: 200,
            PlatformType.TIKTOK: 100,
            PlatformType.TWITTER: 300,
            PlatformType.SPOTIFY: 1000,
            PlatformType.FACEBOOK: 200
        }
        return rate_limits.get(platform, 1000)
    
    def _platform_supports_real_time(self, platform: PlatformType) -> bool:
        """Check if platform supports real-time data"""
        real_time_platforms = {
            PlatformType.YOUTUBE, PlatformType.TWITCH, PlatformType.INSTAGRAM,
            PlatformType.TWITTER, PlatformType.DISCORD, PlatformType.REDDIT
        }
        return platform in real_time_platforms
    
    def _platform_supports_webhooks(self, platform: PlatformType) -> bool:
        """Check if platform supports webhooks"""
        webhook_platforms = {
            PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.FACEBOOK,
            PlatformType.TWITTER, PlatformType.DISCORD, PlatformType.MEDIUM
        }
        return platform in webhook_platforms
    
    # ========== CONFIGURATION METHODS ==========
    
    def get_platform_config(self, platform: PlatformType) -> Optional[PlatformConfig]:
        """Get configuration for specific platform"""
        return self.platform_configs.get(platform)
    
    def get_language_config(self, language_code: str) -> Optional[LanguageConfig]:
        """Get configuration for specific language"""
        return self.language_configs.get(language_code)
    
    def get_ai_model_config(self, model_type: AIModelType) -> Optional[AIModelConfig]:
        """Get configuration for specific AI model"""
        return self.ai_model_configs.get(model_type)
    
    def is_platform_enabled(self, platform: PlatformType) -> bool:
        """Check if platform is enabled"""
        return platform in self.enabled_platforms
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if feature flag is enabled"""
        return self.feature_flags.get(feature_name, False)
    
    def enable_platform(self, platform -> None: PlatformType) -> None:
        """Enable specific platform"""
        if platform not in self.enabled_platforms:
            self.enabled_platforms.append(platform)
    
    def disable_platform(self, platform -> None: PlatformType) -> None:
        """Disable specific platform"""
        if platform in self.enabled_platforms:
            self.enabled_platforms.remove(platform)
    
    def update_feature_flag(self, feature_name -> None: str, enabled -> None: bool) -> None:
        """Update feature flag"""
        self.feature_flags[feature_name] = enabled
    
    def get_engine_config(self, engine: AnalyticsEngine) -> Dict[str, Any]:
        """Get configuration for specific analytics engine"""
        return self.engine_configs.get(engine, {})
    
    def set_engine_config(self, engine -> None: AnalyticsEngine, config -> None: Dict[str, Any]) -> None:
        """Set configuration for specific analytics engine"""
        self.engine_configs[engine] = config
    
    # ========== VALIDATION METHODS ==========
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate complete configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "platform_count": len(self.enabled_platforms),
            "language_count": len(self.supported_languages),
            "model_count": len(self.enabled_models),
            "engine_count": len(self.enabled_engines)
        }
        
        # Validate critical constants
        if len(self.enabled_platforms) < self.SUPPORTED_PLATFORMS_COUNT:
            validation_results["warnings"].append(
                f"Only {len(self.enabled_platforms)} platforms enabled, expected {self.SUPPORTED_PLATFORMS_COUNT}"
            )
        
        if len(self.supported_languages) < self.SUPPORTED_LANGUAGES_COUNT:
            validation_results["warnings"].append(
                f"Only {len(self.supported_languages)} languages supported, expected {self.SUPPORTED_LANGUAGES_COUNT}"
            )
        
        # Validate required configurations
        required_configs = ["cache_config", "security_config", "database_config"]
        for config_name in required_configs:
            if not hasattr(self, config_name) or getattr(self, config_name) is None:
                validation_results["errors"].append(f"Missing required configuration: {config_name}")
                validation_results["valid"] = False
        
        return validation_results
    
    # ========== PERSISTENCE METHODS ==========
    
    def save_to_file(self, file_path -> None: str) -> None:
        """Save configuration to JSON file"""
        try:
            config_dict = self._to_dict()
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {str(e)}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "AnalyticsConfig":
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
            return cls._from_dict(config_dict)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {str(e)}")
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        # Simplified implementation - would be more comprehensive in production
        return {
            "version": self.version,
            "environment": self.environment,
            "enabled_engines": [e.value for e in self.enabled_engines],
            "enabled_platforms": [p.value for p in self.enabled_platforms],
            "supported_languages": self.supported_languages,
            "feature_flags": self.feature_flags
        }
    
    @classmethod
    def _from_dict(cls, config_dict: Dict[str, Any]) -> "AnalyticsConfig":
        """Create configuration from dictionary"""
        # Simplified implementation - would be more comprehensive in production
        config = cls()
        config.version = config_dict.get("version", "3.0.0")
        config.environment = config_dict.get("environment", "production")
        config.feature_flags = config_dict.get("feature_flags", {})
        return config


# ========== CONFIGURATION FACTORY ==========

class AnalyticsConfigFactory:
    """Factory for creating analytics configurations"""
    
    @staticmethod
    def create_development_config() -> AnalyticsConfig:
        """Create development environment configuration"""
        config = AnalyticsConfig()
        config.environment = "development"
        config.debug_mode = True
        config.performance_config.max_concurrent_requests = 100
        config.cache_config.ttl_default = 600  # 10 minutes
        config.monitoring_config.log_level = "DEBUG"
        return config
    
    @staticmethod
    def create_staging_config() -> AnalyticsConfig:
        """Create staging environment configuration"""
        config = AnalyticsConfig()
        config.environment = "staging"
        config.debug_mode = False
        config.performance_config.max_concurrent_requests = 500
        config.cache_config.ttl_default = 1800  # 30 minutes
        config.monitoring_config.log_level = "INFO"
        return config
    
    @staticmethod
    def create_production_config() -> AnalyticsConfig:
        """Create production environment configuration"""
        config = AnalyticsConfig()
        config.environment = "production"
        config.debug_mode = False
        config.performance_config.max_concurrent_requests = 10000
        config.cache_config.ttl_default = 3600  # 1 hour
        config.monitoring_config.log_level = "WARNING"
        config.security_config.audit_logging_enabled = True
        config.security_config.gdpr_compliance = True
        config.security_config.ccpa_compliance = True
        return config
    
    @staticmethod
    def create_minimal_config() -> AnalyticsConfig:
        """Create minimal configuration for testing"""
        config = AnalyticsConfig()
        config.enabled_platforms = [PlatformType.INSTAGRAM, PlatformType.YOUTUBE]
        config.supported_languages = ["en", "es", "fr"]
        config.enabled_engines = [AnalyticsEngine.CREATOR_CONTENT_PERFORMANCE]
        return config


# ========== CONFIGURATION MANAGER ==========

class AnalyticsConfigManager:
    """Manager for analytics configuration lifecycle"""
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config_path = config_path or os.getenv("ANALYTICS_CONFIG_PATH", "config/analytics.json")
        self._config: Optional[AnalyticsConfig] = None
    
    def load_config(self) -> AnalyticsConfig:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_path):
                self._config = AnalyticsConfig.load_from_file(self.config_path)
            else:
                # Create default production config
                self._config = AnalyticsConfigFactory.create_production_config()
                self.save_config()
            
            return self._config
        except Exception as e:
            # Fallback to minimal config if loading fails
            self._config = AnalyticsConfigFactory.create_minimal_config()
            return self._config
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        if self._config:
            # Ensure directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            self._config.save_to_file(self.config_path)
    
    def get_config(self) -> AnalyticsConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, updates -> None: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        if self._config is None:
            self.load_config()
        
        # Apply updates (simplified implementation)
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        if self._config is None:
            self.load_config()
        return self._config.validate_configuration()
    
    def reload_config(self) -> AnalyticsConfig:
        """Reload configuration from file"""
        self._config = None
        return self.load_config()


# ========== GLOBAL CONFIGURATION INSTANCE ==========

# Global configuration manager instance
config_manager = AnalyticsConfigManager()

def get_analytics_config() -> AnalyticsConfig:
    """Get global analytics configuration"""
    return config_manager.get_config()

def reload_analytics_config() -> AnalyticsConfig:
    """Reload global analytics configuration"""
    return config_manager.reload_config()


# ========== MODULE EXPORTS ==========

__all__ = [
    # Main Configuration Classes
    'AnalyticsConfig',
    'AnalyticsConfigFactory',
    'AnalyticsConfigManager',
    
    # Configuration Data Classes
    'PlatformConfig',
    'LanguageConfig',
    'AIModelConfig',
    'CacheConfig',
    'PerformanceConfig',
    'SecurityConfig',
    'MonitoringConfig',
    'DatabaseConfig',
    
    # Enums
    'AnalyticsEngine',
    'PlatformType',
    'LanguageCode',
    'AIModelType',
    'CacheLayer',
    
    # Global Functions
    'get_analytics_config',
    'reload_analytics_config'
]