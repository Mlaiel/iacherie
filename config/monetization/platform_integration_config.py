"""
Platform Integration Configuration Module
=========================================

Professional configuration for external platform integrations and API management.
Handles multi-platform revenue APIs, authentication, and data synchronization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + FinTech Expert

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class PlatformType(str, Enum):
    """Platform type classification for integration."""
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    LIVE_STREAMING = "live_streaming"
    MARKETPLACE = "marketplace"
    SUBSCRIPTION = "subscription"
    ADVERTISING = "advertising"
    NFT_PLATFORM = "nft_platform"
    MERCHANDISING = "merchandising"


class AuthenticationType(str, Enum):
    """Authentication method types."""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"


class DataSyncFrequency(str, Enum):
    """Data synchronization frequency options."""
    REAL_TIME = "real_time"
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class PlatformEndpoints:
    """Platform API endpoints configuration."""
    base_url: str
    auth_url: Optional[str] = None
    refresh_url: Optional[str] = None
    revenue_url: Optional[str] = None
    analytics_url: Optional[str] = None
    user_info_url: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limit_info_url: Optional[str] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration for platform APIs."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    cooldown_seconds: int = 60
    exponential_backoff: bool = True


@dataclass
class PlatformCredentials:
    """Secure platform credentials configuration."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Ensure sensitive data is properly handled."""
        # In production, these should be encrypted or fetched from secure vault
        self.client_secret = self.client_secret or os.getenv(f"{self.client_id}_SECRET")
        self.api_key = self.api_key or os.getenv(f"{self.client_id}_API_KEY")


@dataclass
class PlatformIntegrationConfig:
    """Complete platform integration configuration."""
    platform_name: str
    platform_type: PlatformType
    authentication_type: AuthenticationType
    endpoints: PlatformEndpoints
    credentials: PlatformCredentials
    rate_limits: RateLimitConfig
    
    # Data Configuration
    sync_frequency: DataSyncFrequency = DataSyncFrequency.HOURLY
    enable_webhooks: bool = False
    enable_real_time_sync: bool = False
    data_retention_days: int = 2555  # 7 years
    
    # Revenue Configuration
    commission_rate: Decimal = Decimal("0.0")
    minimum_payout: Decimal = Decimal("10.00")
    currency: str = "EUR"
    
    # Status and Health
    enabled: bool = True
    health_check_enabled: bool = True
    health_check_interval_minutes: int = 15
    max_consecutive_failures: int = 5
    
    # Advanced Features
    supports_analytics: bool = False
    supports_real_time_revenue: bool = False
    supports_bulk_operations: bool = False
    supports_webhook_verification: bool = False


class PlatformIntegrationManager:
    """
    Central manager for all platform integrations.
    Handles configuration, authentication, and health monitoring.
    """
    
    def __init__(self):
        """Initialize platform integration manager."""
        self.platforms: Dict[str, PlatformIntegrationConfig] = {}
        self._initialize_default_platforms()
    
    def _initialize_default_platforms(self):
        """Initialize default platform configurations."""
        
        # Spotify Integration
        self.platforms["spotify"] = PlatformIntegrationConfig(
            platform_name="Spotify",
            platform_type=PlatformType.MUSIC_STREAMING,
            authentication_type=AuthenticationType.OAUTH2,
            endpoints=PlatformEndpoints(
                base_url="https://api.spotify.com/v1",
                auth_url="https://accounts.spotify.com/authorize",
                refresh_url="https://accounts.spotify.com/api/token",
                analytics_url="https://api.spotify.com/v1/me/player/recently-played",
                user_info_url="https://api.spotify.com/v1/me"
            ),
            credentials=PlatformCredentials(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                scopes=["user-read-playback-state", "user-read-currently-playing", "streaming"]
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=6000,
                requests_per_day=50000,
                burst_limit=200
            ),
            sync_frequency=DataSyncFrequency.EVERY_5_MINUTES,
            supports_analytics=True,
            supports_real_time_revenue=True
        )
        
        # YouTube Integration
        self.platforms["youtube"] = PlatformIntegrationConfig(
            platform_name="YouTube",
            platform_type=PlatformType.VIDEO_STREAMING,
            authentication_type=AuthenticationType.OAUTH2,
            endpoints=PlatformEndpoints(
                base_url="https://www.googleapis.com/youtube/v3",
                auth_url="https://accounts.google.com/oauth2/auth",
                refresh_url="https://oauth2.googleapis.com/token",
                revenue_url="https://youtubeanalytics.googleapis.com/v2/reports",
                analytics_url="https://youtubeanalytics.googleapis.com/v2/reports"
            ),
            credentials=PlatformCredentials(
                client_id=os.getenv("YOUTUBE_CLIENT_ID"),
                scopes=["https://www.googleapis.com/auth/youtube.readonly",
                       "https://www.googleapis.com/auth/yt-analytics.readonly"]
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=10000,
                requests_per_day=1000000,
                burst_limit=300
            ),
            commission_rate=Decimal("45.0"),
            minimum_payout=Decimal("100.00"),
            currency="USD",
            supports_analytics=True,
            supports_real_time_revenue=True
        )
        
        # Instagram Integration
        self.platforms["instagram"] = PlatformIntegrationConfig(
            platform_name="Instagram",
            platform_type=PlatformType.SOCIAL_MEDIA,
            authentication_type=AuthenticationType.OAUTH2,
            endpoints=PlatformEndpoints(
                base_url="https://graph.instagram.com",
                auth_url="https://api.instagram.com/oauth/authorize",
                refresh_url="https://graph.instagram.com/refresh_access_token",
                analytics_url="https://graph.instagram.com/{media-id}/insights"
            ),
            credentials=PlatformCredentials(
                client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
                scopes=["user_profile", "user_media", "instagram_basic"]
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=200,
                requests_per_hour=5000,
                requests_per_day=50000,
                burst_limit=400
            ),
            commission_rate=Decimal("30.0"),
            supports_analytics=True
        )
        
        # TikTok Integration
        self.platforms["tiktok"] = PlatformIntegrationConfig(
            platform_name="TikTok",
            platform_type=PlatformType.SOCIAL_MEDIA,
            authentication_type=AuthenticationType.OAUTH2,
            endpoints=PlatformEndpoints(
                base_url="https://open-api.tiktok.com",
                auth_url="https://www.tiktok.com/auth/authorize/",
                refresh_url="https://open-api.tiktok.com/oauth/refresh_token/",
                analytics_url="https://open-api.tiktok.com/video/query/"
            ),
            credentials=PlatformCredentials(
                client_id=os.getenv("TIKTOK_CLIENT_KEY"),
                scopes=["user.info.basic", "video.list", "video.insights"]
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_limit=150
            ),
            commission_rate=Decimal("50.0"),
            supports_analytics=True
        )
        
        # Apple Music Integration
        self.platforms["apple_music"] = PlatformIntegrationConfig(
            platform_name="Apple Music",
            platform_type=PlatformType.MUSIC_STREAMING,
            authentication_type=AuthenticationType.JWT,
            endpoints=PlatformEndpoints(
                base_url="https://api.music.apple.com/v1",
                analytics_url="https://api.appstoreconnect.apple.com/v1/salesReports"
            ),
            credentials=PlatformCredentials(
                api_key=os.getenv("APPLE_MUSIC_PRIVATE_KEY"),
                client_id=os.getenv("APPLE_MUSIC_KEY_ID")
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=20,
                requests_per_hour=1000,
                requests_per_day=20000,
                burst_limit=50
            ),
            commission_rate=Decimal("30.0"),
            minimum_payout=Decimal("100.00"),
            currency="USD"
        )
        
        # Patreon Integration
        self.platforms["patreon"] = PlatformIntegrationConfig(
            platform_name="Patreon",
            platform_type=PlatformType.SUBSCRIPTION,
            authentication_type=AuthenticationType.OAUTH2,
            endpoints=PlatformEndpoints(
                base_url="https://www.patreon.com/api/oauth2/v2",
                auth_url="https://www.patreon.com/oauth2/authorize",
                refresh_url="https://www.patreon.com/api/oauth2/token",
                user_info_url="https://www.patreon.com/api/oauth2/v2/identity",
                webhook_url="https://www.patreon.com/api/oauth2/v2/webhooks"
            ),
            credentials=PlatformCredentials(
                client_id=os.getenv("PATREON_CLIENT_ID"),
                scopes=["identity", "campaigns", "pledges-to-me"]
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=60,
                requests_per_hour=3600,
                requests_per_day=50000,
                burst_limit=100
            ),
            commission_rate=Decimal("5.0"),
            minimum_payout=Decimal("1.00"),
            enable_webhooks=True,
            supports_webhook_verification=True
        )
        
        # Twitch Integration
        self.platforms["twitch"] = PlatformIntegrationConfig(
            platform_name="Twitch",
            platform_type=PlatformType.LIVE_STREAMING,
            authentication_type=AuthenticationType.OAUTH2,
            endpoints=PlatformEndpoints(
                base_url="https://api.twitch.tv/helix",
                auth_url="https://id.twitch.tv/oauth2/authorize",
                refresh_url="https://id.twitch.tv/oauth2/token",
                analytics_url="https://api.twitch.tv/helix/analytics/games",
                webhook_url="https://api.twitch.tv/helix/webhooks/hub"
            ),
            credentials=PlatformCredentials(
                client_id=os.getenv("TWITCH_CLIENT_ID"),
                scopes=["analytics:read:games", "bits:read", "channel:read:subscriptions"]
            ),
            rate_limits=RateLimitConfig(
                requests_per_minute=800,
                requests_per_hour=48000,
                requests_per_day=1000000,
                burst_limit=1200
            ),
            enable_webhooks=True,
            supports_analytics=True,
            supports_real_time_revenue=True
        )
    
    def get_platform_config(self, platform_name: str) -> Optional[PlatformIntegrationConfig]:
        """Get configuration for a specific platform."""
        return self.platforms.get(platform_name.lower())
    
    def get_enabled_platforms(self) -> List[PlatformIntegrationConfig]:
        """Get all enabled platform configurations."""
        return [config for config in self.platforms.values() if config.enabled]
    
    def get_platforms_by_type(self, platform_type: PlatformType) -> List[PlatformIntegrationConfig]:
        """Get all platforms of a specific type."""
        return [
            config for config in self.platforms.values() 
            if config.platform_type == platform_type and config.enabled
        ]
    
    def get_real_time_platforms(self) -> List[PlatformIntegrationConfig]:
        """Get platforms that support real-time revenue tracking."""
        return [
            config for config in self.platforms.values()
            if config.supports_real_time_revenue and config.enabled
        ]
    
    def add_custom_platform(self, platform_config: PlatformIntegrationConfig):
        """Add a custom platform configuration."""
        self.platforms[platform_config.platform_name.lower()] = platform_config
    
    def update_platform_credentials(self, platform_name: str, credentials: PlatformCredentials):
        """Update credentials for a specific platform."""
        if platform_name.lower() in self.platforms:
            self.platforms[platform_name.lower()].credentials = credentials
    
    def disable_platform(self, platform_name: str):
        """Disable a specific platform."""
        if platform_name.lower() in self.platforms:
            self.platforms[platform_name.lower()].enabled = False
    
    def enable_platform(self, platform_name: str):
        """Enable a specific platform."""
        if platform_name.lower() in self.platforms:
            self.platforms[platform_name.lower()].enabled = True
    
    def get_platform_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all platforms."""
        status = {}
        for name, config in self.platforms.items():
            status[name] = {
                "enabled": config.enabled,
                "health_check_enabled": config.health_check_enabled,
                "authentication_type": config.authentication_type.value,
                "supports_real_time": config.supports_real_time_revenue,
                "last_sync": None,  # This would be populated by the actual service
                "error_count": 0    # This would be populated by monitoring
            }
        return status


# Global configuration instance
platform_integration_config = PlatformIntegrationManager()
