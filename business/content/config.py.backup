"""Content Module Configuration - IA Influencer Agent Platform
===========================================================

Configuration management for the content management system with environment-specific
settings, feature flags, and deployment configurations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from ...core.config import BaseConfig


@dataclass
class ContentProcessingConfig:
    """Configuration for content processing engine."""
    
    # Processing limits
    max_file_size_mb: int = 1024  # 1GB default
    max_processing_time_minutes: int = 30
    concurrent_processing_limit: int = 5
    
    # Quality settings
    default_video_quality: str = "1080p"
    default_audio_bitrate: int = 256  # kbps
    default_image_quality: int = 85  # JPEG quality
    
    # AI processing
    enable_ai_enhancement: bool = True
    ai_processing_timeout: int = 300  # 5 minutes
    ai_model_cache_size: int = 3
    
    # Storage settings
    temp_storage_path: str = "/tmp/content_processing"
    processed_storage_path: str = "/storage/processed"
    backup_retention_days: int = 30
    
    # Feature flags
    enable_batch_processing: bool = True
    enable_real_time_processing: bool = True
    enable_preview_generation: bool = True
    enable_thumbnail_generation: bool = True


@dataclass
class DistributionConfig:
    """Configuration for content distribution."""
    
    # Platform configurations
    platforms: Dict[str, Dict[str, Any]] = None
    
    # API rate limits
    api_rate_limits: Dict[str, int] = None
    
    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Quality settings per platform
    platform_quality_presets: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = {
                "youtube": {
                    "max_file_size_mb": 128000,  # 128GB
                    "max_duration_hours": 12,
                    "supported_formats": ["mp4", "mov", "webm"],
                    "required_metadata": ["title", "description"],
                    "api_version": "v3"
                },
                "instagram": {
                    "max_file_size_mb": 4096,  # 4GB
                    "max_duration_minutes": 60,
                    "supported_formats": ["mp4", "jpg", "png"],
                    "required_metadata": ["caption"],
                    "api_version": "v1"
                },
                "tiktok": {
                    "max_file_size_mb": 500,
                    "max_duration_minutes": 10,
                    "supported_formats": ["mp4"],
                    "required_metadata": ["description"],
                    "api_version": "v1"
                },
                "twitter": {
                    "max_file_size_mb": 512,
                    "max_duration_minutes": 2.2,
                    "supported_formats": ["mp4", "gif", "jpg", "png"],
                    "required_metadata": ["text"],
                    "api_version": "v2"
                },
                "linkedin": {
                    "max_file_size_mb": 5120,  # 5GB
                    "max_duration_minutes": 30,
                    "supported_formats": ["mp4", "jpg", "png"],
                    "required_metadata": ["commentary"],
                    "api_version": "v2"
                }
            }
        
        if self.api_rate_limits is None:
            self.api_rate_limits = {
                "youtube": 10000,      # requests per day
                "instagram": 200,      # requests per hour
                "tiktok": 100,         # requests per hour
                "twitter": 300,        # requests per 15 minutes
                "linkedin": 100        # requests per hour
            }
        
        if self.platform_quality_presets is None:
            self.platform_quality_presets = {
                "youtube": {
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "container": "mp4",
                    "max_bitrate": "8000k",
                    "resolution": "1920x1080",
                    "fps": 30
                },
                "instagram": {
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "container": "mp4",
                    "max_bitrate": "3500k",
                    "resolution": "1080x1080",
                    "fps": 30
                },
                "tiktok": {
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "container": "mp4",
                    "max_bitrate": "2000k",
                    "resolution": "1080x1920",
                    "fps": 30
                }
            }


@dataclass
class MonetizationConfig:
    """Configuration for monetization engine."""
    
    # Commission rates by strategy type
    commission_rates: Dict[str, Decimal] = None
    
    # Payment gateway settings
    payment_gateways: Dict[str, Dict[str, Any]] = None
    
    # Payout settings
    minimum_payout_amount: Decimal = Decimal('25.00')
    payout_schedule: str = "weekly"  # weekly, monthly
    payout_processing_fee: Decimal = Decimal('0.25')  # $0.25
    
    # NFT settings
    nft_platforms: List[str] = None
    default_blockchain: str = "ethereum"
    default_royalty_percentage: int = 10
    
    # Subscription settings
    subscription_trial_days: int = 7
    subscription_grace_period_days: int = 3
    
    def __post_init__(self):
        if self.commission_rates is None:
            self.commission_rates = {
                "subscription": Decimal('0.05'),        # 5%
                "pay_per_view": Decimal('0.08'),        # 8%
                "nft_sales": Decimal('0.025'),          # 2.5%
                "brand_partnerships": Decimal('0.15'),  # 15%
                "donations": Decimal('0.03'),           # 3%
                "premium_features": Decimal('0.10')     # 10%
            }
        
        if self.payment_gateways is None:
            self.payment_gateways = {
                "stripe": {
                    "enabled": True,
                    "processing_fee": Decimal('0.029'),  # 2.9% + $0.30
                    "fixed_fee": Decimal('0.30'),
                    "supported_currencies": ["USD", "EUR", "GBP"],
                    "payout_schedule": "daily"
                },
                "paypal": {
                    "enabled": True,
                    "processing_fee": Decimal('0.034'),  # 3.4% + $0.30
                    "fixed_fee": Decimal('0.30'),
                    "supported_currencies": ["USD", "EUR", "GBP"],
                    "payout_schedule": "instant"
                },
                "crypto": {
                    "enabled": False,
                    "processing_fee": Decimal('0.01'),   # 1%
                    "fixed_fee": Decimal('0.00'),
                    "supported_currencies": ["BTC", "ETH", "USDC"],
                    "payout_schedule": "instant"
                }
            }
        
        if self.nft_platforms is None:
            self.nft_platforms = ["opensea", "rarible", "foundation", "superrare"]


@dataclass
class QualityAssuranceConfig:
    """Configuration for quality assurance system."""
    
    # Processing timeouts
    automated_analysis_timeout: int = 600     # 10 minutes
    human_review_timeout: int = 86400        # 24 hours
    compliance_check_timeout: int = 1800     # 30 minutes
    
    # Quality thresholds
    quality_thresholds: Dict[str, Dict[str, float]] = None
    
    # Review assignment
    auto_assign_reviewers: bool = True
    reviewer_workload_limit: int = 10
    priority_review_multiplier: float = 2.0
    
    # Batch processing
    batch_size: int = 50
    batch_processing_interval: int = 300  # 5 minutes
    
    def __post_init__(self):
        if self.quality_thresholds is None:
            self.quality_thresholds = {
                "basic": {
                    "technical_compliance": 0.6,
                    "content_quality": 0.5,
                    "safety_score": 0.8,
                    "overall_minimum": 0.6
                },
                "standard": {
                    "technical_compliance": 0.7,
                    "content_quality": 0.6,
                    "safety_score": 0.85,
                    "overall_minimum": 0.7
                },
                "premium": {
                    "technical_compliance": 0.85,
                    "content_quality": 0.8,
                    "safety_score": 0.9,
                    "overall_minimum": 0.8
                }
            }


@dataclass
class CollaborationConfig:
    """Configuration for collaboration hub."""
    
    # Session settings
    max_session_duration_hours: int = 24
    max_participants_per_session: int = 20
    session_idle_timeout_minutes: int = 60
    
    # Real-time features
    websocket_heartbeat_interval: int = 30  # seconds
    max_websocket_connections: int = 1000
    message_history_retention_days: int = 30
    
    # File sharing
    max_shared_file_size_mb: int = 100
    shared_storage_quota_gb: int = 10
    
    # Notifications
    enable_email_notifications: bool = True
    enable_push_notifications: bool = True
    notification_batch_size: int = 100


class ContentModuleConfig(BaseConfig):
    """Main configuration class for content module."""
    
    def __init__(self, env: str = "development"):
        super().__init__(env)
        
        # Load sub-configurations
        self.processing = ContentProcessingConfig()
        self.distribution = DistributionConfig()
        self.monetization = MonetizationConfig()
        self.quality_assurance = QualityAssuranceConfig()
        self.collaboration = CollaborationConfig()
        
        # Module-level settings
        self.module_enabled = True
        self.debug_mode = env == "development"
        self.log_level = "DEBUG" if self.debug_mode else "INFO"
        
        # Storage configuration
        self.storage_backend = os.getenv("CONTENT_STORAGE_BACKEND", "local")
        self.storage_base_path = os.getenv("CONTENT_STORAGE_PATH", "/storage/content")
        self.cdn_url = os.getenv("CONTENT_CDN_URL", "")
        
        # Database settings
        self.content_db_pool_size = int(os.getenv("CONTENT_DB_POOL_SIZE", "10"))
        self.content_cache_ttl = int(os.getenv("CONTENT_CACHE_TTL", "3600"))
        
        # Security settings
        self.enable_content_encryption = os.getenv("CONTENT_ENCRYPTION_ENABLED", "true").lower() == "true"
        self.encryption_key_rotation_days = int(os.getenv("ENCRYPTION_KEY_ROTATION_DAYS", "90"))
        self.content_access_logging = True
        
        # Performance settings
        self.max_concurrent_operations = int(os.getenv("MAX_CONCURRENT_OPERATIONS", "20"))
        self.operation_timeout = int(os.getenv("OPERATION_TIMEOUT", "1800"))  # 30 minutes
        self.memory_limit_mb = int(os.getenv("MEMORY_LIMIT_MB", "4096"))      # 4GB
        
        # Feature flags from environment
        self._load_feature_flags()
    
    def _load_feature_flags(self):
        """Load feature flags from environment variables."""
        self.features = {
            "ai_enhancement": os.getenv("FEATURE_AI_ENHANCEMENT", "true").lower() == "true",
            "real_time_collaboration": os.getenv("FEATURE_REAL_TIME_COLLAB", "true").lower() == "true",
            "advanced_analytics": os.getenv("FEATURE_ADVANCED_ANALYTICS", "true").lower() == "true",
            "nft_support": os.getenv("FEATURE_NFT_SUPPORT", "false").lower() == "true",
            "blockchain_integration": os.getenv("FEATURE_BLOCKCHAIN", "false").lower() == "true",
            "multi_language_support": os.getenv("FEATURE_MULTI_LANGUAGE", "true").lower() == "true",
            "automated_moderation": os.getenv("FEATURE_AUTO_MODERATION", "true").lower() == "true",
            "brand_partnerships": os.getenv("FEATURE_BRAND_PARTNERSHIPS", "true").lower() == "true",
            "premium_quality_checks": os.getenv("FEATURE_PREMIUM_QA", "false").lower() == "true"
        }
    
    def get_platform_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific platform."""
        return self.distribution.platforms.get(platform)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature, False)
    
    def get_quality_threshold(self, level: str, metric: str) -> float:
        """Get quality threshold for specific level and metric."""
        return self.quality_assurance.quality_thresholds.get(level, {}).get(metric, 0.5)
    
    def get_commission_rate(self, strategy: str) -> Decimal:
        """Get commission rate for monetization strategy."""
        return self.monetization.commission_rates.get(strategy, Decimal('0.10'))
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check required directories
        required_dirs = [
            self.processing.temp_storage_path,
            self.processing.processed_storage_path,
            self.storage_base_path
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                issues.append(f"Required directory does not exist: {dir_path}")
        
        # Check payment gateway configuration
        enabled_gateways = [
            name for name, config in self.monetization.payment_gateways.items()
            if config.get("enabled", False)
        ]
        
        if not enabled_gateways:
            issues.append("No payment gateways are enabled")
        
        # Check platform API credentials
        for platform in self.distribution.platforms:
            api_key_var = f"{platform.upper()}_API_KEY"
            if not os.getenv(api_key_var):
                issues.append(f"Missing API key for {platform}: {api_key_var}")
        
        # Check AI model availability
        if self.features["ai_enhancement"]:
            ai_models_path = os.getenv("AI_MODELS_PATH", "/models")
            if not Path(ai_models_path).exists():
                issues.append(f"AI models directory not found: {ai_models_path}")
        
        return issues
    
    def update_from_database(self) -> None:
        """Update configuration from database settings."""
        # This would load dynamic configuration from database
        # Implementation would depend on your database schema
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "processing": self.processing.__dict__,
            "distribution": self.distribution.__dict__,
            "monetization": {
                **self.monetization.__dict__,
                "commission_rates": {k: float(v) for k, v in self.monetization.commission_rates.items()}
            },
            "quality_assurance": self.quality_assurance.__dict__,
            "collaboration": self.collaboration.__dict__,
            "features": self.features,
            "storage": {
                "backend": self.storage_backend,
                "base_path": self.storage_base_path,
                "cdn_url": self.cdn_url
            },
            "performance": {
                "max_concurrent_operations": self.max_concurrent_operations,
                "operation_timeout": self.operation_timeout,
                "memory_limit_mb": self.memory_limit_mb
            }
        }


# Global configuration instance
_content_config = None


def get_content_config(env: Optional[str] = None) -> ContentModuleConfig:
    """Get content module configuration singleton."""
    global _content_config
    
    if _content_config is None:
        env = env or os.getenv("ENVIRONMENT", "development")
        _content_config = ContentModuleConfig(env)
    
    return _content_config


def reload_content_config(env: Optional[str] = None) -> ContentModuleConfig:
    """Reload content configuration."""
    global _content_config
    env = env or os.getenv("ENVIRONMENT", "development")
    _content_config = ContentModuleConfig(env)
    return _content_config
