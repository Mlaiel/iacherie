"""Validation Configuration - Centralized Enterprise Configuration System
=====================================================================

Central configuration management for the IA Influencer Agent Platform
validation system, providing enterprise-grade settings, performance
optimization, and platform-specific configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Configuration Categories:
- Performance settings (timeouts, parallelism, caching)
- Quality thresholds per content type
- Security and compliance settings
- Platform-specific configurations (YouTube, Instagram, TikTok, Spotify)
- AI model settings and optimization
- Monitoring and logging configuration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any, Set
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import yaml

logger = logging.getLogger(__name__)

class ConfigLevel(Enum):
    """Configuration severity levels."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"

class ValidationMode(Enum):
    """Validation execution modes."""
    STRICT = "strict"
    NORMAL = "normal"
    PERMISSIVE = "permissive"
    CUSTOM = "custom"

class PlatformType(Enum):
    """Supported platform types."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    DISCORD = "discord"
    CUSTOM = "custom"

@dataclass
class PerformanceConfig:
    """Performance optimization settings."""
    max_concurrent_validations: int = 10
    validation_timeout_seconds: int = 30
    cache_ttl_seconds: int = 3600
    max_workers: int = 4
    parallel_processing: bool = True
    memory_limit_mb: int = 512
    cpu_limit_percent: int = 80
    enable_async_processing: bool = True
    batch_size: int = 100
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0

@dataclass
class QualityThresholds:
    """Content quality assessment thresholds."""
    min_content_quality_score: float = 0.7
    min_security_score: float = 0.9
    min_business_compliance_score: float = 0.8
    max_file_size_mb: int = 500
    min_audio_bitrate_kbps: int = 128
    min_video_resolution: str = "720p"
    max_processing_time_seconds: int = 120
    min_metadata_completeness: float = 0.8
    allow_explicit_content: bool = False
    require_thumbnail: bool = True

@dataclass
class SecurityConfig:
    """Security and compliance settings."""
    threat_detection_enabled: bool = True
    gdpr_compliance_check: bool = True
    ccpa_compliance_check: bool = True
    dmca_validation: bool = True
    malware_scanning: bool = True
    content_fingerprinting: bool = True
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_logging: bool = True
    data_retention_days: int = 365
    sensitive_data_detection: bool = True
    anonymization_required: bool = True

@dataclass
class PlatformConfig:
    """Platform-specific configuration."""
    platform: PlatformType
    enabled: bool = True
    
    # General limits
    max_file_size_mb: int = 100
    max_duration_seconds: int = 3600
    supported_formats: List[str] = field(default_factory=list)
    
    # Metadata requirements
    title_max_length: int = 100
    description_max_length: int = 5000
    tags_max_count: int = 30
    
    # Quality requirements
    min_resolution: str = "480p"
    max_resolution: str = "4K"
    supported_aspect_ratios: List[str] = field(default_factory=list)
    
    # Monetization settings
    monetization_enabled: bool = True
    copyright_check_required: bool = True
    content_rating_required: bool = True

@dataclass
class AIModelConfig:
    """AI model configuration settings."""
    ai_analysis_enabled: bool = True
    ml_model_version: str = "v2.1"
    ai_confidence_threshold: float = 0.8
    content_analysis_model: str = "ainflue-content-v2"
    sentiment_analysis_model: str = "ainflue-sentiment-v2"
    quality_scoring_model: str = "ainflue-quality-v2"
    threat_detection_model: str = "ainflue-security-v2"
    model_cache_enabled: bool = True
    model_update_check_hours: int = 24
    fallback_to_traditional: bool = True
    gpu_acceleration: bool = True
    model_batch_size: int = 32

@dataclass
class MonitoringConfig:
    """Monitoring and observability settings."""
    metrics_enabled: bool = True
    detailed_logging: bool = True
    performance_monitoring: bool = True
    business_metrics_tracking: bool = True
    log_level: str = "INFO"
    
    # Alerting
    alert_on_failures: bool = True
    alert_threshold_error_rate: float = 0.05
    alert_threshold_latency_ms: int = 5000
    
    # Exports
    prometheus_metrics: bool = True
    elasticsearch_logs: bool = True
    grafana_dashboards: bool = True
    
    # Retention
    metrics_retention_days: int = 90
    logs_retention_days: int = 30
    traces_retention_days: int = 7

class ValidationConfig:
    """Centralized validation configuration management."""
    
    def __init__(self, config_level: ConfigLevel = ConfigLevel.DEVELOPMENT):
        """Initialize validation configuration.
        
        Args:
            config_level: Configuration environment level
        """
        self.config_level = config_level
        self.validation_mode = ValidationMode.NORMAL
        
        # Core configuration components
        self.performance = PerformanceConfig()
        self.quality = QualityThresholds()
        self.security = SecurityConfig()
        self.ai_models = AIModelConfig()
        self.monitoring = MonitoringConfig()
        
        # Platform configurations
        self.platforms: Dict[PlatformType, PlatformConfig] = {}
        self._init_default_platforms()
        
        # Custom settings
        self.custom_settings: Dict[str, Any] = {}
        
        # Apply environment-specific settings
        self._apply_environment_settings()
        
        logger.info(f"ValidationConfig initialized for {config_level.value} environment")
    
    def _init_default_platforms(self) -> None:
        """Initialize default platform configurations."""
        
        # YouTube configuration
        self.platforms[PlatformType.YOUTUBE] = PlatformConfig(
            platform=PlatformType.YOUTUBE,
            max_file_size_mb=128000,  # 128GB
            max_duration_seconds=43200,  # 12 hours
            supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
            title_max_length=100,
            description_max_length=5000,
            tags_max_count=500,
            supported_aspect_ratios=["16:9", "4:3", "1:1", "9:16"]
        )
        
        # Instagram configuration
        self.platforms[PlatformType.INSTAGRAM] = PlatformConfig(
            platform=PlatformType.INSTAGRAM,
            max_file_size_mb=4000,  # 4GB for IGTV
            max_duration_seconds=3600,  # 60 minutes for IGTV
            supported_formats=["mp4", "mov", "jpg", "png", "gif"],
            title_max_length=150,
            description_max_length=2200,
            tags_max_count=30,
            supported_aspect_ratios=["1:1", "4:5", "16:9", "9:16"]
        )
        
        # TikTok configuration
        self.platforms[PlatformType.TIKTOK] = PlatformConfig(
            platform=PlatformType.TIKTOK,
            max_file_size_mb=4000,  # 4GB
            max_duration_seconds=600,  # 10 minutes
            supported_formats=["mp4", "mov", "webm"],
            title_max_length=150,
            description_max_length=4000,
            tags_max_count=100,
            supported_aspect_ratios=["9:16", "1:1", "16:9"]
        )
        
        # Spotify configuration (for podcasts)
        self.platforms[PlatformType.SPOTIFY] = PlatformConfig(
            platform=PlatformType.SPOTIFY,
            max_file_size_mb=200,  # 200MB
            max_duration_seconds=14400,  # 4 hours
            supported_formats=["mp3", "wav", "flac", "m4a"],
            title_max_length=100,
            description_max_length=4000,
            tags_max_count=50,
            min_resolution="audio",  # Audio-only
            supported_aspect_ratios=["audio"]
        )
    
    def _apply_environment_settings(self) -> None:
        """Apply environment-specific configuration overrides."""
        
        if self.config_level == ConfigLevel.PRODUCTION:
            # Production optimizations
            self.performance.max_concurrent_validations = 20
            self.performance.max_workers = 8
            self.performance.memory_limit_mb = 2048
            self.quality.min_content_quality_score = 0.85
            self.security.audit_logging = True
            self.security.encryption_at_rest = True
            self.monitoring.detailed_logging = False
            self.monitoring.log_level = "WARNING"
            
        elif self.config_level == ConfigLevel.ENTERPRISE:
            # Enterprise-grade settings
            self.performance.max_concurrent_validations = 50
            self.performance.max_workers = 16
            self.performance.memory_limit_mb = 4096
            self.performance.cpu_limit_percent = 90
            self.quality.min_content_quality_score = 0.9
            self.quality.min_security_score = 0.95
            self.security.malware_scanning = True
            self.security.data_retention_days = 2555  # 7 years
            self.ai_models.gpu_acceleration = True
            self.ai_models.model_batch_size = 64
            self.monitoring.prometheus_metrics = True
            self.monitoring.elasticsearch_logs = True
            
        elif self.config_level == ConfigLevel.DEVELOPMENT:
            # Development convenience settings
            self.performance.validation_timeout_seconds = 60
            self.quality.min_content_quality_score = 0.5
            self.security.threat_detection_enabled = False
            self.monitoring.detailed_logging = True
            self.monitoring.log_level = "DEBUG"
    
    def get_platform_config(self, platform: Union[PlatformType, str]) -> Optional[PlatformConfig]:
        """Get configuration for specific platform.
        
        Args:
            platform: Platform type or name
            
        Returns:
            Platform configuration or None if not found
        """
        if isinstance(platform, str):
            try:
                platform = PlatformType(platform.lower())
            except ValueError:
                logger.warning(f"Unknown platform: {platform}")
                return None
        
        return self.platforms.get(platform)
    
    def update_platform_config(self, platform: PlatformType, config: PlatformConfig) -> None:
        """Update platform-specific configuration.
        
        Args:
            platform: Platform type
            config: New platform configuration
        """
        self.platforms[platform] = config
        logger.info(f"Updated {platform.value} platform configuration")
    
    def set_custom_setting(self, key: str, value: Any) -> None:
        """Set custom configuration setting.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.custom_settings[key] = value
        logger.debug(f"Set custom setting: {key} = {value}")
    
    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """Get custom configuration setting.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self.custom_settings.get(key, default)
    
    def load_from_file(self, config_path: Union[str, Path]) -> None:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self._apply_config_data(config_data)
            logger.info(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise
    
    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to file.
        
        Args:
            config_path: Path where to save configuration
        """
        config_path = Path(config_path)
        config_data = self.to_dict()
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise
    
    def _apply_config_data(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data from loaded file.
        
        Args:
            config_data: Configuration data dictionary
        """
        # Update performance settings
        if 'performance' in config_data:
            for key, value in config_data['performance'].items():
                if hasattr(self.performance, key):
                    setattr(self.performance, key, value)
        
        # Update quality thresholds
        if 'quality' in config_data:
            for key, value in config_data['quality'].items():
                if hasattr(self.quality, key):
                    setattr(self.quality, key, value)
        
        # Update security settings
        if 'security' in config_data:
            for key, value in config_data['security'].items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)
        
        # Update AI model settings
        if 'ai_models' in config_data:
            for key, value in config_data['ai_models'].items():
                if hasattr(self.ai_models, key):
                    setattr(self.ai_models, key, value)
        
        # Update monitoring settings
        if 'monitoring' in config_data:
            for key, value in config_data['monitoring'].items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
        
        # Update custom settings
        if 'custom_settings' in config_data:
            self.custom_settings.update(config_data['custom_settings'])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return {
            'config_level': self.config_level.value,
            'validation_mode': self.validation_mode.value,
            'performance': asdict(self.performance),
            'quality': asdict(self.quality),
            'security': asdict(self.security),
            'ai_models': asdict(self.ai_models),
            'monitoring': asdict(self.monitoring),
            'platforms': {
                platform.value: asdict(config) 
                for platform, config in self.platforms.items()
            },
            'custom_settings': self.custom_settings
        }
    
    def validate_config(self) -> List[str]:
        """Validate configuration settings.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate performance settings
        if self.performance.max_concurrent_validations <= 0:
            errors.append("max_concurrent_validations must be positive")
        
        if self.performance.validation_timeout_seconds <= 0:
            errors.append("validation_timeout_seconds must be positive")
        
        # Validate quality thresholds
        if not 0 <= self.quality.min_content_quality_score <= 1:
            errors.append("min_content_quality_score must be between 0 and 1")
        
        if not 0 <= self.quality.min_security_score <= 1:
            errors.append("min_security_score must be between 0 and 1")
        
        # Validate AI model settings
        if not 0 <= self.ai_models.ai_confidence_threshold <= 1:
            errors.append("ai_confidence_threshold must be between 0 and 1")
        
        return errors

# Global configuration instance
_default_config: Optional[ValidationConfig] = None

def get_config() -> ValidationConfig:
    """Get global validation configuration instance.
    
    Returns:
        Global ValidationConfig instance
    """
    global _default_config
    if _default_config is None:
        # Determine environment from environment variable
        env = os.getenv('AINFLUE_ENV', 'development').lower()
        try:
            config_level = ConfigLevel(env)
        except ValueError:
            config_level = ConfigLevel.DEVELOPMENT
            logger.warning(f"Unknown environment '{env}', using development")
        
        _default_config = ValidationConfig(config_level)
    
    return _default_config

def configure_global(config: ValidationConfig) -> None:
    """Set global validation configuration.
    
    Args:
        config: Configuration instance to use globally
    """
    global _default_config
    _default_config = config
    logger.info("Global validation configuration updated")

def load_config_from_env() -> ValidationConfig:
    """Load configuration from environment variables.
    
    Returns:
        ValidationConfig instance with environment settings
    """
    config = get_config()
    
    # Performance settings from environment
    if os.getenv('VALIDATION_MAX_WORKERS'):
        config.performance.max_workers = int(os.getenv('VALIDATION_MAX_WORKERS'))
    
    if os.getenv('VALIDATION_TIMEOUT'):
        config.performance.validation_timeout_seconds = int(os.getenv('VALIDATION_TIMEOUT'))
    
    # Quality settings from environment
    if os.getenv('MIN_QUALITY_SCORE'):
        config.quality.min_content_quality_score = float(os.getenv('MIN_QUALITY_SCORE'))
    
    # Security settings from environment
    if os.getenv('ENABLE_THREAT_DETECTION'):
        config.security.threat_detection_enabled = os.getenv('ENABLE_THREAT_DETECTION').lower() == 'true'
    
    # AI model settings from environment
    if os.getenv('AI_MODEL_VERSION'):
        config.ai_models.ml_model_version = os.getenv('AI_MODEL_VERSION')
    
    return config

# Export main configuration classes
__all__ = [
    'ValidationConfig',
    'ConfigLevel',
    'ValidationMode',
    'PlatformType',
    'PerformanceConfig',
    'QualityThresholds',
    'SecurityConfig',
    'PlatformConfig',
    'AIModelConfig',
    'MonitoringConfig',
    'get_config',
    'configure_global',
    'load_config_from_env'
]