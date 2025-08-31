"""
Platform Integration Security Configuration Module
================================================

Advanced security configuration for platform integrations and API management
for IA Influencer Agent platform. Provides comprehensive security settings for
third-party platform connections, API gateway security, and integration monitoring.

Business Logic Integration:
- Secure connections to Spotify, YouTube, Instagram, TikTok APIs
- OAuth2 flow security for creator platform connections
- Rate limiting and abuse prevention for platform integrations
- Webhook security and verification for real-time updates

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security + API Integration Engineers

 COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum


class Platform(Enum):
    """Supported content and social media platforms."""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    VIMEO = "vimeo"
    TWITCH = "twitch"
    PINTEREST = "pinterest"


class AuthFlow(Enum):
    """OAuth2 authentication flow types."""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    REFRESH_TOKEN = "refresh_token"


class SecurityLevel(Enum):
    """Security levels for platform integrations."""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class WebhookEvent(Enum):
    """Webhook event types for platform notifications."""
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_REMOVED = "content_removed"
    REVENUE_UPDATE = "revenue_update"
    COPYRIGHT_CLAIM = "copyright_claim"
    ENGAGEMENT_UPDATE = "engagement_update"
    ACCOUNT_SUSPENDED = "account_suspended"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class PlatformCredentials:
    """Platform-specific credential configuration."""
    client_id: str = ""
    client_secret: str = ""
    api_key: str = ""
    access_token: str = ""
    refresh_token: str = ""
    
    # Additional security tokens
    webhook_secret: str = ""
    app_secret: str = ""
    partner_key: str = ""
    
    # Token expiration and rotation
    token_expires_in: int = 3600
    auto_refresh: bool = True
    rotation_interval_days: int = 30


@dataclass
class RateLimitConfig:
    """Rate limiting configuration for API calls."""
    # General rate limits
    requests_per_minute: int = 100
    requests_per_hour: int = 5000
    requests_per_day: int = 100000
    
    # Burst allowance
    burst_limit: int = 200
    burst_window_seconds: int = 60
    
    # Rate limit enforcement
    enforcement_enabled: bool = True
    queue_requests: bool = True
    retry_after_seconds: int = 60
    
    # Per-platform overrides
    platform_limits: Dict[Platform, Dict[str, int]] = field(default_factory=lambda: {
        Platform.SPOTIFY: {
            "requests_per_minute": 100,
            "requests_per_hour": 3000,
            "requests_per_day": 50000
        },
        Platform.YOUTUBE: {
            "requests_per_minute": 50,
            "requests_per_hour": 2000,
            "requests_per_day": 20000
        },
        Platform.INSTAGRAM: {
            "requests_per_minute": 200,
            "requests_per_hour": 4000,
            "requests_per_day": 80000
        },
        Platform.TIKTOK: {
            "requests_per_minute": 30,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        }
    })
    
    # Creator tier rate limits
    tier_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "free": 1.0,
        "professional": 2.5,
        "enterprise": 5.0
    })


@dataclass
class OAuth2SecurityConfig:
    """OAuth2 security configuration for platform integrations."""
    # OAuth2 flow security
    state_parameter_required: bool = True
    pkce_enabled: bool = True  # Proof Key for Code Exchange
    nonce_verification: bool = True
    
    # Token security
    jwt_tokens: bool = True
    token_encryption: bool = True
    secure_token_storage: bool = True
    
    # Scope management
    minimal_scopes: bool = True
    scope_validation: bool = True
    dynamic_scopes: bool = True
    
    # Platform-specific OAuth2 configurations
    platform_oauth_configs: Dict[Platform, Dict[str, Any]] = field(default_factory=lambda: {
        Platform.SPOTIFY: {
            "authorization_url": "https://accounts.spotify.com/authorize",
            "token_url": "https://accounts.spotify.com/api/token",
            "scopes": [
                "user-read-private",
                "user-read-email", 
                "playlist-read-private",
                "user-library-read",
                "user-top-read"
            ],
            "redirect_uri": "/auth/spotify/callback",
            "response_type": "code",
            "show_dialog": False
        },
        Platform.YOUTUBE: {
            "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scopes": [
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/yt-analytics.readonly"
            ],
            "redirect_uri": "/auth/youtube/callback",
            "access_type": "offline",
            "prompt": "consent"
        },
        Platform.INSTAGRAM: {
            "authorization_url": "https://api.instagram.com/oauth/authorize",
            "token_url": "https://api.instagram.com/oauth/access_token",
            "scopes": [
                "user_profile",
                "user_media",
                "instagram_content_publish",
                "pages_show_list"
            ],
            "redirect_uri": "/auth/instagram/callback",
            "response_type": "code"
        },
        Platform.TIKTOK: {
            "authorization_url": "https://www.tiktok.com/auth/authorize/",
            "token_url": "https://open-api.tiktok.com/oauth/access_token/",
            "scopes": [
                "user.info.basic",
                "video.list",
                "video.publish"
            ],
            "redirect_uri": "/auth/tiktok/callback",
            "response_type": "code"
        }
    })
    
    # Security validations
    redirect_uri_validation: bool = True
    state_validation_timeout: int = 600  # 10 minutes
    token_validation_enabled: bool = True


@dataclass
class WebhookSecurityConfig:
    """Webhook security configuration for platform notifications."""
    # Webhook validation
    signature_verification: bool = True
    timestamp_validation: bool = True
    duplicate_prevention: bool = True
    
    # Security headers
    required_headers: List[str] = field(default_factory=lambda: [
        "X-Signature",
        "X-Timestamp",
        "User-Agent",
        "Content-Type"
    ])
    
    # Validation timeframes
    timestamp_tolerance_seconds: int = 300  # 5 minutes
    signature_algorithm: str = "sha256"
    
    # Platform-specific webhook configurations
    platform_webhook_configs: Dict[Platform, Dict[str, Any]] = field(default_factory=lambda: {
        Platform.SPOTIFY: {
            "secret_header": "X-Spotify-Signature",
            "timestamp_header": "X-Spotify-Timestamp",
            "user_agent_pattern": "Spotify/*",
            "content_type": "application/json",
            "supported_events": [
                "track.update",
                "playlist.update",
                "user.update"
            ]
        },
        Platform.YOUTUBE: {
            "secret_header": "X-Hub-Signature",
            "timestamp_header": "X-YouTube-Timestamp",
            "user_agent_pattern": "YouTube/*",
            "content_type": "application/atom+xml",
            "supported_events": [
                "video.upload",
                "video.update",
                "channel.update"
            ]
        },
        Platform.INSTAGRAM: {
            "secret_header": "X-Hub-Signature-256",
            "timestamp_header": "X-FB-Timestamp",
            "user_agent_pattern": "facebookexternalua/*",
            "content_type": "application/json",
            "supported_events": [
                "media.create",
                "media.update",
                "comments.create"
            ]
        }
    })
    
    # Webhook processing
    async_processing: bool = True
    retry_failed_webhooks: bool = True
    max_retry_attempts: int = 3
    retry_backoff_seconds: int = 60


@dataclass
class ApiGatewayConfig:
    """API Gateway security configuration."""
    # Gateway features
    request_validation: bool = True
    response_filtering: bool = True
    api_versioning: bool = True
    
    # Security middleware
    cors_enabled: bool = True
    csrf_protection: bool = True
    request_sanitization: bool = True
    
    # CORS configuration
    cors_origins: List[str] = field(default_factory=lambda: [
        "https://app.ia-influencer-agent.com",
        "https://dashboard.ia-influencer-agent.com"
    ])
    cors_methods: List[str] = field(default_factory=lambda: [
        "GET", "POST", "PUT", "DELETE", "OPTIONS"
    ])
    cors_headers: List[str] = field(default_factory=lambda: [
        "Authorization", "Content-Type", "X-API-Key"
    ])
    
    # Request/Response limits
    max_request_size_mb: int = 100
    max_response_size_mb: int = 50
    timeout_seconds: int = 30
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 50
    recovery_timeout_seconds: int = 60
    half_open_max_calls: int = 10


@dataclass
class MonitoringConfig:
    """Integration monitoring and alerting configuration."""
    # Real-time monitoring
    health_checks_enabled: bool = True
    health_check_interval_seconds: int = 30
    performance_monitoring: bool = True
    
    # Metrics collection
    collect_api_metrics: bool = True
    collect_business_metrics: bool = True
    collect_security_metrics: bool = True
    
    # Alert conditions
    alert_conditions: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "high_error_rate": {
            "threshold": 0.05,  # 5% error rate
            "window_minutes": 5,
            "severity": "warning"
        },
        "api_timeout": {
            "threshold": 0.02,  # 2% timeout rate
            "window_minutes": 5,
            "severity": "error"
        },
        "quota_exceeded": {
            "threshold": 0.9,  # 90% of quota used
            "window_minutes": 60,
            "severity": "warning"
        },
        "security_breach": {
            "threshold": 1,  # Any security event
            "window_minutes": 1,
            "severity": "critical"
        }
    })
    
    # Log aggregation
    centralized_logging: bool = True
    log_retention_days: int = 90
    structured_logging: bool = True
    
    # Performance thresholds
    response_time_p95_ms: int = 2000
    response_time_p99_ms: int = 5000
    availability_target: float = 0.999  # 99.9%


@dataclass
class SecurityScanningConfig:
    """Security scanning configuration for integrations."""
    # Automated security scanning
    vulnerability_scanning: bool = True
    dependency_scanning: bool = True
    api_security_testing: bool = True
    
    # Scan frequency
    daily_scans: bool = True
    pre_deployment_scans: bool = True
    continuous_monitoring: bool = True
    
    # Security tools
    scanning_tools: List[str] = field(default_factory=lambda: [
        "owasp_zap",
        "snyk",
        "semgrep",
        "bandit"
    ])
    
    # Vulnerability management
    auto_remediation: bool = False
    vulnerability_reporting: bool = True
    risk_assessment: bool = True
    
    # Compliance scanning
    compliance_frameworks: List[str] = field(default_factory=lambda: [
        "owasp_top_10",
        "nist_cybersecurity",
        "iso_27001",
        "gdpr_technical"
    ])


@dataclass
class DataProtectionConfig:
    """Data protection configuration for platform integrations."""
    # Data encryption
    encryption_in_transit: bool = True
    encryption_at_rest: bool = True
    end_to_end_encryption: bool = True
    
    # Data anonymization
    personal_data_anonymization: bool = True
    creator_data_pseudonymization: bool = True
    analytics_data_aggregation: bool = True
    
    # Data retention
    retention_policies: Dict[str, int] = field(default_factory=lambda: {
        "api_logs": 90,  # days
        "user_data": 2555,  # 7 years
        "analytics_data": 1825,  # 5 years
        "security_logs": 3650  # 10 years
    })
    
    # Data residency
    data_residency_compliance: bool = True
    supported_regions: List[str] = field(default_factory=lambda: [
        "EU", "US", "UK", "CA", "AU"
    ])
    
    # Privacy compliance
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    data_subject_rights: bool = True
    
    # Data sharing controls
    third_party_sharing_controls: bool = True
    consent_management: bool = True
    data_minimization: bool = True


@dataclass
class PlatformIntegrationSecurityConfig:
    """Main platform integration security configuration container."""
    credentials: Dict[Platform, PlatformCredentials] = field(default_factory=dict)
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)
    oauth2_security: OAuth2SecurityConfig = field(default_factory=OAuth2SecurityConfig)
    webhook_security: WebhookSecurityConfig = field(default_factory=WebhookSecurityConfig)
    api_gateway: ApiGatewayConfig = field(default_factory=ApiGatewayConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security_scanning: SecurityScanningConfig = field(default_factory=SecurityScanningConfig)
    data_protection: DataProtectionConfig = field(default_factory=DataProtectionConfig)
    
    # Global integration settings
    security_level: SecurityLevel = SecurityLevel.HIGH
    enabled_platforms: Set[Platform] = field(default_factory=lambda: {
        Platform.SPOTIFY,
        Platform.YOUTUBE,
        Platform.INSTAGRAM,
        Platform.TIKTOK
    })
    
    # Fallback and redundancy
    fallback_mechanisms: bool = True
    redundant_connections: bool = True
    graceful_degradation: bool = True
    
    # Integration testing
    sandbox_mode: bool = False
    testing_webhooks: bool = True
    integration_health_checks: bool = True


# Default configuration instance
platform_integration_security_config = PlatformIntegrationSecurityConfig()


def get_platform_integration_security_config() -> PlatformIntegrationSecurityConfig:
    """Get the platform integration security configuration instance."""



    return platform_integration_security_config


def validate_platform_integration_config(config: PlatformIntegrationSecurityConfig) -> bool:
    """Validate platform integration security configuration settings."""
    # Validate rate limits
    if config.rate_limiting.requests_per_minute <= 0:
        raise ValueError("Requests per minute must be positive")
    
    if config.rate_limiting.requests_per_hour < config.rate_limiting.requests_per_minute:
        raise ValueError("Hourly limit must be >= minute limit * 60")
    
    # Validate OAuth2 configuration
    for platform, oauth_config in config.oauth2_security.platform_oauth_configs.items():
        if not oauth_config.get("authorization_url"):
            raise ValueError(f"Authorization URL required for {platform}")
        if not oauth_config.get("token_url"):
            raise ValueError(f"Token URL required for {platform}")
    
    # Validate webhook configuration
    if config.webhook_security.timestamp_tolerance_seconds <= 0:
        raise ValueError("Webhook timestamp tolerance must be positive")
    
    # Validate API gateway timeouts
    if config.api_gateway.timeout_seconds <= 0:
        raise ValueError("API gateway timeout must be positive")
    
    return True


def get_platform_specific_config(platform: Platform) -> Dict[str, Any]:
    """Get platform-specific security configuration."""
    platform_configs = {
        Platform.SPOTIFY: {
            "rate_limiting.requests_per_minute": 100,
            "oauth2_security.required_scopes": [
                "user-read-private",
                "user-read-email",
                "playlist-read-private"
            ],
            "webhook_security.signature_algorithm": "sha256",
            "security_level": SecurityLevel.HIGH
        },
        Platform.YOUTUBE: {
            "rate_limiting.requests_per_minute": 50,
            "oauth2_security.required_scopes": [
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/yt-analytics.readonly"
            ],
            "webhook_security.signature_algorithm": "sha1",
            "security_level": SecurityLevel.HIGH
        },
        Platform.INSTAGRAM: {
            "rate_limiting.requests_per_minute": 200,
            "oauth2_security.required_scopes": [
                "user_profile",
                "user_media"
            ],
            "webhook_security.signature_algorithm": "sha256",
            "security_level": SecurityLevel.STANDARD
        },
        Platform.TIKTOK: {
            "rate_limiting.requests_per_minute": 30,
            "oauth2_security.required_scopes": [
                "user.info.basic",
                "video.list"
            ],
            "webhook_security.signature_algorithm": "sha256",
            "security_level": SecurityLevel.STANDARD
        }
    }
    
    return platform_configs.get(platform, {})
