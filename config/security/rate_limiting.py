"""Rate Limiting Configuration Module
==================================

Advanced rate limiting and throttling configuration for IA Influencer Agent platform.
Provides comprehensive API rate limiting, content processing throttling,
and resource usage management for creators and platform integrations.

Business Logic Integration:
- Content upload rate limiting by creator tier
- Platform API rate limiting for distribution
- Processing throttling during IA protection workflows
- Revenue API rate limiting for financial operations

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import timedelta


class RateLimitType(Enum):
    """Types of rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class ThrottleAction(Enum):
    """Actions to take when rate limit is exceeded."""
    REJECT = "reject"
    QUEUE = "queue"
    DELAY = "delay"
    DOWNGRADE = "downgrade"
    NOTIFY = "notify"


class ResourceType(Enum):
    """Types of resources that can be rate limited."""
    API_CALLS = "api_calls"
    FILE_UPLOADS = "file_uploads"
    CONTENT_PROCESSING = "content_processing"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"
    FINGERPRINT_OPERATIONS = "fingerprint_operations"
    PLATFORM_INTEGRATIONS = "platform_integrations"
    REVENUE_OPERATIONS = "revenue_operations"


@dataclass
class RateLimit:
    """Individual rate limit configuration."""
    limit: int  # Number of operations allowed
    window_seconds: int  # Time window in seconds
    rate_type: RateLimitType = RateLimitType.SLIDING_WINDOW
    action: ThrottleAction = ThrottleAction.REJECT
    
    # Token bucket specific settings
    burst_limit: Optional[int] = None
    refill_rate: Optional[float] = None
    
    # Queue settings for QUEUE action
    queue_size: int = 100
    queue_timeout_seconds: int = 300
    
    # Delay settings for DELAY action
    delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    
    # Adaptive settings
    adaptive_threshold: float = 0.8
    scale_factor: float = 1.5


@dataclass
class ApiRateLimiting:
    """API-specific rate limiting configuration."""
    
    # Global API limits
    global_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "requests_per_second": RateLimit(
            limit=100, window_seconds=1, rate_type=RateLimitType.SLIDING_WINDOW
        ),
        "requests_per_minute": RateLimit(
            limit=1000, window_seconds=60, rate_type=RateLimitType.SLIDING_WINDOW
        ),
        "requests_per_hour": RateLimit(
            limit=10000, window_seconds=3600, rate_type=RateLimitType.SLIDING_WINDOW
        ),
        "requests_per_day": RateLimit(
            limit=100000, window_seconds=86400, rate_type=RateLimitType.FIXED_WINDOW
        )
    })
    
    # Endpoint-specific limits
    endpoint_limits: Dict[str, Dict[str, RateLimit]] = field(default_factory=lambda: {
        "/api/v1/content/upload": {
            "per_minute": RateLimit(limit=10, window_seconds=60),
            "per_hour": RateLimit(limit=100, window_seconds=3600)
        },
        "/api/v1/fingerprint/create": {
            "per_minute": RateLimit(limit=20, window_seconds=60),
            "per_hour": RateLimit(limit=500, window_seconds=3600)
        },
        "/api/v1/analytics": {
            "per_second": RateLimit(limit=10, window_seconds=1),
            "per_minute": RateLimit(limit=200, window_seconds=60)
        },
        "/api/v1/revenue": {
            "per_minute": RateLimit(limit=5, window_seconds=60),
            "per_hour": RateLimit(limit=100, window_seconds=3600)
        },
        "/api/v1/platforms/connect": {
            "per_hour": RateLimit(limit=10, window_seconds=3600),
            "per_day": RateLimit(limit=50, window_seconds=86400)
        }
    })
    
    # Tier-based API limits
    tier_limits: Dict[str, Dict[str, RateLimit]] = field(default_factory=lambda: {
        "free": {
            "requests_per_hour": RateLimit(limit=100, window_seconds=3600),
            "requests_per_day": RateLimit(limit=1000, window_seconds=86400),
            "bandwidth_mb_per_hour": RateLimit(limit=100, window_seconds=3600)
        },
        "basic": {
            "requests_per_hour": RateLimit(limit=500, window_seconds=3600),
            "requests_per_day": RateLimit(limit=10000, window_seconds=86400),
            "bandwidth_mb_per_hour": RateLimit(limit=1000, window_seconds=3600)
        },
        "professional": {
            "requests_per_hour": RateLimit(limit=2000, window_seconds=3600),
            "requests_per_day": RateLimit(limit=50000, window_seconds=86400),
            "bandwidth_mb_per_hour": RateLimit(limit=5000, window_seconds=3600)
        },
        "enterprise": {
            "requests_per_hour": RateLimit(limit=10000, window_seconds=3600),
            "requests_per_day": RateLimit(limit=500000, window_seconds=86400),
            "bandwidth_mb_per_hour": RateLimit(limit=50000, window_seconds=3600)
        }
    })


@dataclass
class ContentProcessingLimits:
    """Content processing rate limiting configuration."""
    
    # Upload limits by content type
    upload_limits: Dict[str, Dict[str, RateLimit]] = field(default_factory=lambda: {
        "audio": {
            "files_per_hour": RateLimit(limit=50, window_seconds=3600),
            "mb_per_hour": RateLimit(limit=500, window_seconds=3600),
            "processing_minutes_per_hour": RateLimit(limit=60, window_seconds=3600)
        },
        "video": {
            "files_per_hour": RateLimit(limit=20, window_seconds=3600),
            "mb_per_hour": RateLimit(limit=2000, window_seconds=3600),
            "processing_minutes_per_hour": RateLimit(limit=120, window_seconds=3600)
        },
        "image": {
            "files_per_hour": RateLimit(limit=200, window_seconds=3600),
            "mb_per_hour": RateLimit(limit=1000, window_seconds=3600)
        },
        "text": {
            "files_per_hour": RateLimit(limit=1000, window_seconds=3600),
            "characters_per_hour": RateLimit(limit=1000000, window_seconds=3600)
        }
    })
    
    # Processing queue limits
    queue_limits: Dict[str, int] = field(default_factory=lambda: {
        "max_concurrent_jobs": 10,
        "max_queued_jobs": 100,
        "max_job_duration_minutes": 30,
        "priority_queue_size": 20
    })
    
    # Tier-based processing limits
    tier_processing_limits: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "free": {
            "concurrent_uploads": 1,
            "max_file_size_mb": 50,
            "processing_priority": "low",
            "queue_timeout_minutes": 30
        },
        "basic": {
            "concurrent_uploads": 3,
            "max_file_size_mb": 200,
            "processing_priority": "normal",
            "queue_timeout_minutes": 15
        },
        "professional": {
            "concurrent_uploads": 10,
            "max_file_size_mb": 1000,
            "processing_priority": "high",
            "queue_timeout_minutes": 5
        },
        "enterprise": {
            "concurrent_uploads": 50,
            "max_file_size_mb": -1,  # unlimited
            "processing_priority": "highest",
            "queue_timeout_minutes": 1
        }
    })


@dataclass
class FingerprintingLimits:
    """Fingerprinting operation rate limiting."""
    
    # Fingerprint creation limits
    creation_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "fingerprints_per_hour": RateLimit(limit=500, window_seconds=3600),
        "batch_operations_per_hour": RateLimit(limit=50, window_seconds=3600),
        "similarity_searches_per_minute": RateLimit(limit=100, window_seconds=60)
    })
    
    # Content type specific fingerprinting limits
    content_type_limits: Dict[str, Dict[str, RateLimit]] = field(default_factory=lambda: {
        "audio": {
            "fingerprints_per_hour": RateLimit(limit=200, window_seconds=3600),
            "duration_minutes_per_hour": RateLimit(limit=300, window_seconds=3600)
        },
        "video": {
            "fingerprints_per_hour": RateLimit(limit=50, window_seconds=3600),
            "duration_minutes_per_hour": RateLimit(limit=120, window_seconds=3600)
        },
        "image": {
            "fingerprints_per_hour": RateLimit(limit=1000, window_seconds=3600),
            "megapixels_per_hour": RateLimit(limit=10000, window_seconds=3600)
        }
    })
    
    # Matching and comparison limits
    matching_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "comparisons_per_second": RateLimit(limit=100, window_seconds=1),
        "batch_comparisons_per_hour": RateLimit(limit=1000, window_seconds=3600),
        "database_queries_per_minute": RateLimit(limit=500, window_seconds=60)
    })


@dataclass
class PlatformIntegrationLimits:
    """Platform-specific integration rate limiting."""
    
    # Platform API limits (respecting external API limits)
    platform_limits: Dict[str, Dict[str, RateLimit]] = field(default_factory=lambda: {
        "spotify": {
            "api_calls_per_second": RateLimit(limit=1, window_seconds=1),
            "api_calls_per_hour": RateLimit(limit=1000, window_seconds=3600),
            "track_uploads_per_day": RateLimit(limit=50, window_seconds=86400)
        },
        "youtube": {
            "api_calls_per_second": RateLimit(limit=2, window_seconds=1),
            "api_calls_per_day": RateLimit(limit=10000, window_seconds=86400),
            "video_uploads_per_day": RateLimit(limit=20, window_seconds=86400)
        },
        "instagram": {
            "api_calls_per_hour": RateLimit(limit=200, window_seconds=3600),
            "media_uploads_per_hour": RateLimit(limit=25, window_seconds=3600),
            "story_uploads_per_day": RateLimit(limit=100, window_seconds=86400)
        },
        "tiktok": {
            "api_calls_per_hour": RateLimit(limit=100, window_seconds=3600),
            "video_uploads_per_day": RateLimit(limit=10, window_seconds=86400)
        }
    })
    
    # Connection and authentication limits
    connection_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "oauth_requests_per_hour": RateLimit(limit=20, window_seconds=3600),
        "token_refresh_per_hour": RateLimit(limit=100, window_seconds=3600),
        "failed_auth_per_hour": RateLimit(limit=10, window_seconds=3600)
    })
    
    # Distribution limits
    distribution_limits: Dict[str, Dict[str, RateLimit]] = field(default_factory=lambda: {
        "simultaneous_distributions": RateLimit(limit=5, window_seconds=1),
        "content_updates_per_hour": RateLimit(limit=50, window_seconds=3600),
        "metadata_updates_per_hour": RateLimit(limit=200, window_seconds=3600)
    })


@dataclass
class RevenueLimits:
    """Revenue and financial operation rate limiting."""
    
    # Revenue tracking limits
    tracking_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "revenue_queries_per_hour": RateLimit(limit=100, window_seconds=3600),
        "report_generations_per_day": RateLimit(limit=10, window_seconds=86400),
        "analytics_requests_per_hour": RateLimit(limit=200, window_seconds=3600)
    })
    
    # Payment processing limits
    payment_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "payout_requests_per_day": RateLimit(limit=5, window_seconds=86400),
        "payment_method_updates_per_hour": RateLimit(limit=10, window_seconds=3600),
        "transaction_queries_per_hour": RateLimit(limit=50, window_seconds=3600)
    })
    
    # Financial security limits
    security_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "failed_payment_attempts_per_hour": RateLimit(
            limit=3, window_seconds=3600, action=ThrottleAction.DELAY
        ),
        "suspicious_activity_threshold": RateLimit(
            limit=10, window_seconds=3600, action=ThrottleAction.NOTIFY
        )
    })


@dataclass
class SecurityRateLimiting:
    """Security-focused rate limiting configuration."""
    
    # Authentication limits
    auth_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "login_attempts_per_minute": RateLimit(
            limit=5, window_seconds=60, action=ThrottleAction.DELAY
        ),
        "failed_login_attempts_per_hour": RateLimit(
            limit=10, window_seconds=3600, action=ThrottleAction.DELAY
        ),
        "password_reset_per_hour": RateLimit(limit=3, window_seconds=3600),
        "mfa_attempts_per_minute": RateLimit(
            limit=10, window_seconds=60, action=ThrottleAction.DELAY
        )
    })
    
    # API security limits
    api_security_limits: Dict[str, RateLimit] = field(default_factory=lambda: {
        "invalid_api_key_per_hour": RateLimit(
            limit=20, window_seconds=3600, action=ThrottleAction.DELAY
        ),
        "suspicious_requests_per_hour": RateLimit(
            limit=50, window_seconds=3600, action=ThrottleAction.NOTIFY
        ),
        "large_payload_requests_per_hour": RateLimit(limit=100, window_seconds=3600)
    })
    
    # Resource abuse protection
    abuse_protection: Dict[str, RateLimit] = field(default_factory=lambda: {
        "repeated_requests_per_second": RateLimit(
            limit=10, window_seconds=1, action=ThrottleAction.DELAY
        ),
        "bandwidth_abuse_mb_per_hour": RateLimit(
            limit=10000, window_seconds=3600, action=ThrottleAction.QUEUE
        ),
        "storage_abuse_operations_per_hour": RateLimit(limit=1000, window_seconds=3600)
    })


@dataclass
class AdaptiveRateLimiting:
    """Adaptive and intelligent rate limiting configuration."""
    
    # Machine learning based adaptation
    ml_adaptation_enabled: bool = True
    learning_window_hours: int = 24
    adaptation_sensitivity: float = 0.5
    
    # Traffic pattern analysis
    pattern_analysis_enabled: bool = True
    spike_detection_threshold: float = 2.0
    gradual_increase_threshold: float = 1.5
    
    # Dynamic adjustment
    dynamic_adjustment_enabled: bool = True
    min_adjustment_factor: float = 0.5
    max_adjustment_factor: float = 3.0
    adjustment_cooldown_minutes: int = 15
    
    # Predictive scaling
    predictive_scaling: bool = True
    prediction_horizon_hours: int = 4
    confidence_threshold: float = 0.8


@dataclass
class RateLimitingStorage:
    """Rate limiting storage and persistence configuration."""
    
    # Storage backend
    storage_backend: str = "redis"  # redis, memory, database
    redis_config: Dict[str, Any] = field(default_factory=lambda: {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_RATE_LIMIT_DB", "1")),
        "password": os.getenv("REDIS_PASSWORD"),
        "connection_pool_size": 20
    })
    
    # Key management
    key_prefix: str = "ia_rl:"
    key_expiry_seconds: int = 86400  # 24 hours
    cleanup_interval_minutes: int = 60
    
    # Performance optimization
    batch_operations: bool = True
    pipeline_operations: bool = True
    lua_script_optimization: bool = True


@dataclass
class RateLimitingMonitoring:
    """Rate limiting monitoring and alerting configuration."""
    
    # Metrics collection
    collect_metrics: bool = True
    metrics_interval_seconds: int = 60
    detailed_metrics: bool = True
    
    # Alerting
    alerting_enabled: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "limit_exceeded_percentage": 80.0,
        "error_rate_percentage": 5.0,
        "response_time_ms": 1000.0
    })
    
    # Alert channels
    alert_channels: List[str] = field(default_factory=lambda: [
        "email", "slack", "webhook"
    ])
    
    # Dashboard integration
    dashboard_integration: bool = True
    real_time_updates: bool = True
    historical_data_retention_days: int = 90


@dataclass
class RateLimitingConfig:
    """Main rate limiting configuration container."""
    
    # Core configurations
    api_limits: ApiRateLimiting = field(default_factory=ApiRateLimiting)
    content_processing: ContentProcessingLimits = field(default_factory=ContentProcessingLimits)
    fingerprinting: FingerprintingLimits = field(default_factory=FingerprintingLimits)
    platform_integration: PlatformIntegrationLimits = field(default_factory=PlatformIntegrationLimits)
    revenue_limits: RevenueLimits = field(default_factory=RevenueLimits)
    security_limits: SecurityRateLimiting = field(default_factory=SecurityRateLimiting)
    
    # Advanced features
    adaptive_limiting: AdaptiveRateLimiting = field(default_factory=AdaptiveRateLimiting)
    storage: RateLimitingStorage = field(default_factory=RateLimitingStorage)
    monitoring: RateLimitingMonitoring = field(default_factory=RateLimitingMonitoring)
    
    # Global settings
    rate_limiting_enabled: bool = True
    default_rate_limit_type: RateLimitType = RateLimitType.SLIDING_WINDOW
    default_throttle_action: ThrottleAction = ThrottleAction.REJECT
    
    # Error handling
    fallback_on_storage_error: bool = True
    graceful_degradation: bool = True
    circuit_breaker_enabled: bool = True
    
    # Performance
    async_processing: bool = True
    batch_size: int = 100
    max_memory_usage_mb: int = 512


# Default configuration instance
rate_limiting_config = RateLimitingConfig()


def get_rate_limiting_config() -> RateLimitingConfig:
    """Get the rate limiting configuration instance."""
    return rate_limiting_config


def get_tier_rate_limits(tier: str) -> Dict[str, RateLimit]:
    """Get rate limits for specific subscription tier."""
    config = get_rate_limiting_config()
    return config.api_limits.tier_limits.get(tier, config.api_limits.tier_limits["basic"])


def get_platform_rate_limits(platform: str) -> Dict[str, RateLimit]:
    """Get rate limits for specific platform integration."""
    config = get_rate_limiting_config()
    return config.platform_integration.platform_limits.get(platform, {})


def get_content_type_limits(content_type: str) -> Dict[str, RateLimit]:
    """Get rate limits for specific content type processing."""
    config = get_rate_limiting_config()
    return config.content_processing.upload_limits.get(content_type, {})


def validate_rate_limiting_config(config: RateLimitingConfig) -> bool:
    """Validate rate limiting configuration settings."""
    # Validate rate limit values
    for tier_limits in config.api_limits.tier_limits.values():
        for limit in tier_limits.values():
            if limit.limit <= 0:
                raise ValueError(f"Rate limit must be positive: {limit.limit}")
            if limit.window_seconds <= 0:
                raise ValueError(f"Window seconds must be positive: {limit.window_seconds}")
    
    # Validate storage configuration
    if config.storage.storage_backend not in ["redis", "memory", "database"]:
        raise ValueError(f"Invalid storage backend: {config.storage.storage_backend}")
    
    return True
