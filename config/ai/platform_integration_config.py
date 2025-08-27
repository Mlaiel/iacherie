"""
Platform Integration AI Configuration for IA-Influencer Agent Platform
======================================================================

Professional platform integration and API management configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class PlatformType(str, Enum):
    """Supported social media and content platforms."""
    
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    APPLE_PODCASTS = "apple_podcasts"
    DISCORD = "discord"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    PATREON = "patreon"


class IntegrationType(str, Enum):
    """Types of platform integrations."""
    
    CONTENT_UPLOAD = "content_upload"
    ANALYTICS_API = "analytics_api"
    MONETIZATION_API = "monetization_api"
    AUTHENTICATION = "authentication"
    WEBHOOK = "webhook"
    REAL_TIME_SYNC = "real_time_sync"
    BULK_OPERATIONS = "bulk_operations"
    SEARCH_API = "search_api"


class APIVersion(str, Enum):
    """API versions for different platforms."""
    
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    V4 = "v4"
    LATEST = "latest"
    BETA = "beta"


@dataclass
class PlatformIntegration:
    """Platform integration configuration."""
    
    platform: PlatformType
    integration_types: List[IntegrationType]
    api_version: APIVersion
    base_url: str
    authentication_type: str
    rate_limits: Dict[str, int]
    supported_content_types: List[str]
    max_file_size_mb: int
    webhook_endpoints: List[str]
    sdk_available: bool = False
    documentation_url: str = ""
    status: str = "active"


class PlatformIntegrationConfig(BaseSettings):
    """
    Professional Platform Integration Configuration.
    
    Manages comprehensive integration with social media platforms,
    content platforms, and third-party services for the influencer ecosystem.
    """
    
    # Core Integration Configuration
    INTEGRATION_STORAGE_PATH: str = "/data/integrations"
    DEFAULT_TIMEOUT_SECONDS: int = 30
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    CONNECTION_POOL_SIZE: int = 20
    
    # Authentication Configuration
    USE_OAUTH2: bool = True
    USE_API_KEYS: bool = True
    USE_JWT_TOKENS: bool = True
    TOKEN_REFRESH_ENABLED: bool = True
    TOKEN_EXPIRY_BUFFER_MINUTES: int = 10
    
    # YouTube Integration
    YOUTUBE_API_ENABLED: bool = True
    YOUTUBE_API_VERSION: str = "v3"
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    YOUTUBE_WEBHOOK_SECRET: Optional[str] = None
    YOUTUBE_QUOTA_LIMIT_DAILY: int = 10000
    YOUTUBE_UPLOAD_CHUNK_SIZE: int = 8388608  # 8MB
    
    # TikTok Integration
    TIKTOK_API_ENABLED: bool = True
    TIKTOK_API_VERSION: str = "v1"
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_RATE_LIMIT_PER_HOUR: int = 1000
    TIKTOK_MAX_VIDEO_SIZE_MB: int = 500
    
    # Instagram Integration
    INSTAGRAM_API_ENABLED: bool = True
    INSTAGRAM_API_VERSION: str = "v18.0"
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_RATE_LIMIT_PER_HOUR: int = 200
    INSTAGRAM_MAX_IMAGE_SIZE_MB: int = 30
    
    # Facebook Integration
    FACEBOOK_API_ENABLED: bool = True
    FACEBOOK_API_VERSION: str = "v18.0"
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_PAGE_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_RATE_LIMIT_PER_HOUR: int = 200
    
    # Twitter/X Integration
    TWITTER_API_ENABLED: bool = True
    TWITTER_API_VERSION: str = "v2"
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_RATE_LIMIT_PER_15MIN: int = 300
    
    # Spotify Integration
    SPOTIFY_API_ENABLED: bool = True
    SPOTIFY_API_VERSION: str = "v1"
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: Optional[str] = None
    SPOTIFY_RATE_LIMIT_PER_SECOND: int = 10
    
    # SoundCloud Integration
    SOUNDCLOUD_API_ENABLED: bool = True
    SOUNDCLOUD_CLIENT_ID: Optional[str] = None
    SOUNDCLOUD_CLIENT_SECRET: Optional[str] = None
    SOUNDCLOUD_RATE_LIMIT_PER_HOUR: int = 15000
    SOUNDCLOUD_MAX_TRACK_SIZE_MB: int = 500
    
    # Twitch Integration
    TWITCH_API_ENABLED: bool = True
    TWITCH_CLIENT_ID: Optional[str] = None
    TWITCH_CLIENT_SECRET: Optional[str] = None
    TWITCH_RATE_LIMIT_PER_MINUTE: int = 800
    
    # Pinterest Integration
    PINTEREST_API_ENABLED: bool = True
    PINTEREST_API_VERSION: str = "v5"
    PINTEREST_APP_ID: Optional[str] = None
    PINTEREST_APP_SECRET: Optional[str] = None
    PINTEREST_RATE_LIMIT_PER_HOUR: int = 1000
    
    # LinkedIn Integration
    LINKEDIN_API_ENABLED: bool = True
    LINKEDIN_API_VERSION: str = "v2"
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_RATE_LIMIT_PER_DAY: int = 100000
    
    # Apple Podcasts Integration
    APPLE_PODCASTS_API_ENABLED: bool = True
    APPLE_PODCASTS_KEY_ID: Optional[str] = None
    APPLE_PODCASTS_ISSUER_ID: Optional[str] = None
    APPLE_PODCASTS_PRIVATE_KEY: Optional[str] = None
    
    # Discord Integration
    DISCORD_API_ENABLED: bool = True
    DISCORD_BOT_TOKEN: Optional[str] = None
    DISCORD_CLIENT_ID: Optional[str] = None
    DISCORD_CLIENT_SECRET: Optional[str] = None
    DISCORD_RATE_LIMIT_PER_SECOND: int = 5
    
    # Patreon Integration
    PATREON_API_ENABLED: bool = True
    PATREON_CLIENT_ID: Optional[str] = None
    PATREON_CLIENT_SECRET: Optional[str] = None
    PATREON_RATE_LIMIT_PER_HOUR: int = 1000
    
    # Webhook Configuration
    WEBHOOK_BASE_URL: str = "https://api.ia-influencer.com/webhooks"
    WEBHOOK_SECRET_KEY: Optional[str] = None
    WEBHOOK_TIMEOUT_SECONDS: int = 15
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    WEBHOOK_SIGNATURE_VERIFICATION: bool = True
    
    # Real-time Sync Configuration
    REAL_TIME_SYNC_ENABLED: bool = True
    SYNC_INTERVAL_SECONDS: int = 300  # 5 minutes
    SYNC_BATCH_SIZE: int = 100
    SYNC_QUEUE_SIZE: int = 10000
    FAILED_SYNC_RETRY_HOURS: int = 24
    
    # Content Upload Configuration
    PARALLEL_UPLOADS_ENABLED: bool = True
    MAX_CONCURRENT_UPLOADS: int = 5
    UPLOAD_CHUNK_SIZE_MB: int = 5
    UPLOAD_TIMEOUT_MINUTES: int = 30
    UPLOAD_RESUME_ENABLED: bool = True
    
    # Analytics Configuration
    ANALYTICS_SYNC_ENABLED: bool = True
    ANALYTICS_SYNC_FREQUENCY_HOURS: int = 6
    HISTORICAL_DATA_DAYS: int = 365
    REAL_TIME_METRICS_ENABLED: bool = True
    
    # Content Monitoring
    CONTENT_MONITORING_ENABLED: bool = True
    MONITORING_FREQUENCY_MINUTES: int = 15
    CONTENT_CHANGE_DETECTION: bool = True
    PERFORMANCE_TRACKING: bool = True
    
    # Error Handling and Logging
    LOG_API_REQUESTS: bool = True
    LOG_API_RESPONSES: bool = False  # Privacy consideration
    ERROR_NOTIFICATION_ENABLED: bool = True
    CIRCUIT_BREAKER_ENABLED: bool = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    
    # Security Configuration
    ENCRYPT_API_KEYS: bool = True
    VALIDATE_WEBHOOK_SIGNATURES: bool = True
    IP_WHITELIST_ENABLED: bool = False
    API_KEY_ROTATION_ENABLED: bool = True
    API_KEY_ROTATION_DAYS: int = 90
    
    # Performance Optimization
    RESPONSE_CACHING_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300
    CONNECTION_POOLING_ENABLED: bool = True
    REQUEST_COMPRESSION_ENABLED: bool = True
    BATCH_REQUEST_OPTIMIZATION: bool = True
    
    @validator("MAX_CONCURRENT_UPLOADS")
    def validate_concurrent_uploads(cls, v):
        if v <= 0 or v > 20:
            raise ValueError("Concurrent uploads must be between 1 and 20")
        return v
    
    @validator("DEFAULT_TIMEOUT_SECONDS")
    def validate_timeout(cls, v):
        if v <= 0 or v > 300:
            raise ValueError("Timeout must be between 1 and 300 seconds")
        return v
    
    def get_platform_integration(self, platform: PlatformType) -> PlatformIntegration:
        """Get integration configuration for specific platform."""
        
        integrations = {
            PlatformType.YOUTUBE: PlatformIntegration(
                platform=platform,
                integration_types=[
                    IntegrationType.CONTENT_UPLOAD,
                    IntegrationType.ANALYTICS_API,
                    IntegrationType.MONETIZATION_API,
                    IntegrationType.AUTHENTICATION,
                    IntegrationType.WEBHOOK
                ],
                api_version=APIVersion.V3,
                base_url="https://www.googleapis.com/youtube/v3",
                authentication_type="OAuth2",
                rate_limits={
                    "queries_per_day": self.YOUTUBE_QUOTA_LIMIT_DAILY,
                    "uploads_per_day": 100,
                    "requests_per_second": 10
                },
                supported_content_types=["video", "live_stream", "shorts"],
                max_file_size_mb=2048,  # 2GB
                webhook_endpoints=[
                    f"{self.WEBHOOK_BASE_URL}/youtube/upload",
                    f"{self.WEBHOOK_BASE_URL}/youtube/analytics"
                ],
                sdk_available=True,
                documentation_url="https://developers.google.com/youtube/v3",
                status="active"
            ),
            PlatformType.TIKTOK: PlatformIntegration(
                platform=platform,
                integration_types=[
                    IntegrationType.CONTENT_UPLOAD,
                    IntegrationType.ANALYTICS_API,
                    IntegrationType.AUTHENTICATION
                ],
                api_version=APIVersion.V1,
                base_url="https://open-api.tiktok.com",
                authentication_type="OAuth2",
                rate_limits={
                    "requests_per_hour": self.TIKTOK_RATE_LIMIT_PER_HOUR,
                    "uploads_per_day": 50
                },
                supported_content_types=["video", "image"],
                max_file_size_mb=self.TIKTOK_MAX_VIDEO_SIZE_MB,
                webhook_endpoints=[f"{self.WEBHOOK_BASE_URL}/tiktok/events"],
                sdk_available=True,
                documentation_url="https://developers.tiktok.com",
                status="active"
            ),
            PlatformType.INSTAGRAM: PlatformIntegration(
                platform=platform,
                integration_types=[
                    IntegrationType.CONTENT_UPLOAD,
                    IntegrationType.ANALYTICS_API,
                    IntegrationType.AUTHENTICATION
                ],
                api_version=APIVersion.LATEST,
                base_url="https://graph.facebook.com/v18.0",
                authentication_type="OAuth2",
                rate_limits={
                    "requests_per_hour": self.INSTAGRAM_RATE_LIMIT_PER_HOUR,
                    "posts_per_day": 100
                },
                supported_content_types=["image", "video", "carousel", "story", "reel"],
                max_file_size_mb=self.INSTAGRAM_MAX_IMAGE_SIZE_MB,
                webhook_endpoints=[f"{self.WEBHOOK_BASE_URL}/instagram/media"],
                sdk_available=True,
                documentation_url="https://developers.facebook.com/docs/instagram-api",
                status="active"
            ),
            PlatformType.SPOTIFY: PlatformIntegration(
                platform=platform,
                integration_types=[
                    IntegrationType.ANALYTICS_API,
                    IntegrationType.AUTHENTICATION,
                    IntegrationType.SEARCH_API
                ],
                api_version=APIVersion.V1,
                base_url="https://api.spotify.com/v1",
                authentication_type="OAuth2",
                rate_limits={
                    "requests_per_second": self.SPOTIFY_RATE_LIMIT_PER_SECOND,
                    "requests_per_hour": 36000
                },
                supported_content_types=["track", "album", "playlist", "podcast"],
                max_file_size_mb=0,  # No direct upload
                webhook_endpoints=[],
                sdk_available=True,
                documentation_url="https://developer.spotify.com/documentation/web-api",
                status="active"
            )
        }
        
        return integrations.get(platform, PlatformIntegration(
            platform=platform,
            integration_types=[IntegrationType.AUTHENTICATION],
            api_version=APIVersion.V1,
            base_url="",
            authentication_type="API_Key",
            rate_limits={"requests_per_hour": 1000},
            supported_content_types=[],
            max_file_size_mb=100,
            webhook_endpoints=[],
            sdk_available=False,
            documentation_url="",
            status="inactive"
        ))
    
    def get_platform_credentials(self, platform: PlatformType) -> Dict[str, Any]:
        """Get credentials for specific platform."""
        
        credentials = {
            PlatformType.YOUTUBE: {
                "client_id": self.YOUTUBE_CLIENT_ID,
                "client_secret": self.YOUTUBE_CLIENT_SECRET,
                "api_key": self.YOUTUBE_API_KEY,
                "webhook_secret": self.YOUTUBE_WEBHOOK_SECRET
            },
            PlatformType.TIKTOK: {
                "client_key": self.TIKTOK_CLIENT_KEY,
                "client_secret": self.TIKTOK_CLIENT_SECRET,
                "access_token": self.TIKTOK_ACCESS_TOKEN
            },
            PlatformType.INSTAGRAM: {
                "app_id": self.INSTAGRAM_APP_ID,
                "app_secret": self.INSTAGRAM_APP_SECRET,
                "access_token": self.INSTAGRAM_ACCESS_TOKEN
            },
            PlatformType.SPOTIFY: {
                "client_id": self.SPOTIFY_CLIENT_ID,
                "client_secret": self.SPOTIFY_CLIENT_SECRET,
                "redirect_uri": self.SPOTIFY_REDIRECT_URI
            }
        }
        
        return credentials.get(platform, {})
    
    def get_active_platforms(self) -> List[PlatformType]:
        """Get list of active platform integrations."""
        
        active_platforms = []
        
        platform_status = {
            PlatformType.YOUTUBE: self.YOUTUBE_API_ENABLED,
            PlatformType.TIKTOK: self.TIKTOK_API_ENABLED,
            PlatformType.INSTAGRAM: self.INSTAGRAM_API_ENABLED,
            PlatformType.FACEBOOK: self.FACEBOOK_API_ENABLED,
            PlatformType.TWITTER: self.TWITTER_API_ENABLED,
            PlatformType.SPOTIFY: self.SPOTIFY_API_ENABLED,
            PlatformType.SOUNDCLOUD: self.SOUNDCLOUD_API_ENABLED,
            PlatformType.TWITCH: self.TWITCH_API_ENABLED,
            PlatformType.PINTEREST: self.PINTEREST_API_ENABLED,
            PlatformType.LINKEDIN: self.LINKEDIN_API_ENABLED,
            PlatformType.APPLE_PODCASTS: self.APPLE_PODCASTS_API_ENABLED,
            PlatformType.DISCORD: self.DISCORD_API_ENABLED,
            PlatformType.PATREON: self.PATREON_API_ENABLED
        }
        
        return [platform for platform, enabled in platform_status.items() if enabled]
    
    def get_webhook_config(self, platform: PlatformType) -> Dict[str, Any]:
        """Get webhook configuration for platform."""
        
        return {
            "base_url": self.WEBHOOK_BASE_URL,
            "endpoint": f"{self.WEBHOOK_BASE_URL}/{platform.value}/events",
            "secret_key": self.WEBHOOK_SECRET_KEY,
            "timeout_seconds": self.WEBHOOK_TIMEOUT_SECONDS,
            "retry_attempts": self.WEBHOOK_RETRY_ATTEMPTS,
            "signature_verification": self.WEBHOOK_SIGNATURE_VERIFICATION
        }
    
    def get_upload_config(self, platform: PlatformType) -> Dict[str, Any]:
        """Get upload configuration for platform."""
        
        integration = self.get_platform_integration(platform)
        
        return {
            "max_file_size_mb": integration.max_file_size_mb,
            "supported_types": integration.supported_content_types,
            "chunk_size_mb": self.UPLOAD_CHUNK_SIZE_MB,
            "timeout_minutes": self.UPLOAD_TIMEOUT_MINUTES,
            "resume_enabled": self.UPLOAD_RESUME_ENABLED,
            "parallel_enabled": self.PARALLEL_UPLOADS_ENABLED,
            "max_concurrent": self.MAX_CONCURRENT_UPLOADS
        }
    
    class Config:
        env_prefix = "PLATFORM_INTEGRATION_"
        case_sensitive = True


# Global instance for easy import
platform_integration_config = PlatformIntegrationConfig()
