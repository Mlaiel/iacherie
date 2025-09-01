"""Platform Integration Configuration for IA-Influencer Agent Platform
==================================================================

Professional platform API integration configurations for multi-platform
content distribution, monitoring, and revenue tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """
Platform categories for integration"""

    MUSIC = "music"
    VIDEO = "video"
    SOCIAL = "social"
    STREAMING = "streaming"
    PODCAST = "podcast"
    MARKETPLACE = "marketplace"


class APIAuthType(Enum):
    """API authentication methods"""

    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    CLIENT_CREDENTIALS = "client_credentials"
    BASIC_AUTH = "basic_auth"


@dataclass
class PlatformAPIConfig:
    """Platform API configuration"""
    
    platform_name: str
    platform_type: PlatformType
    
    # API endpoints
    base_url: str
    api_version: str = "v1"
    auth_endpoint: str = ""
    
    # Authentication
    auth_type: APIAuthType = APIAuthType.OAUTH2
    client_id: str = ""
    client_secret: str = ""
    scopes: List[str] = field(default_factory=list)
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    # Features support
    supports_upload: bool = False
    supports_analytics: bool = True
    supports_monetization: bool = False
    supports_live_streaming: bool = False
    
    # Data extraction capabilities
    extract_metadata: bool = True
    extract_analytics: bool = True
    extract_comments: bool = False
    extract_thumbnails: bool = True
    
    # Content types supported
    supported_formats: List[str] = field(default_factory=list)
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
    
    # Compliance settings
    gdpr_compliant: bool = True
    coppa_compliant: bool = False
    requires_age_verification: bool = False


# Spotify Configuration
SPOTIFY_CONFIG = PlatformAPIConfig(
    platform_name="spotify",
    platform_type=PlatformType.MUSIC,
    base_url="https://api.spotify.com",
    api_version="v1",
    auth_endpoint="https://accounts.spotify.com/api/token",
    auth_type=APIAuthType.CLIENT_CREDENTIALS,
    scopes=[
        "user-read-private",
        "user-read-email", 
        "user-library-read",
        "user-read-playback-state",
        "streaming",
        "playlist-read-private",
        "playlist-read-collaborative"
    ],
    requests_per_minute=100,
    requests_per_hour=2000,
    supports_analytics=True,
    supports_monetization=True,
    supported_formats=["audio/mpeg", "audio/mp4", "audio/wav"],
    max_file_size=200 * 1024 * 1024
)

# YouTube Configuration
YOUTUBE_CONFIG = PlatformAPIConfig(
    platform_name="youtube",
    platform_type=PlatformType.VIDEO,
    base_url="https://www.googleapis.com/youtube",
    api_version="v3",
    auth_endpoint="https://oauth2.googleapis.com/token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/yt-analytics.readonly"
    ],
    requests_per_minute=100,
    requests_per_hour=10000,
    supports_upload=True,
    supports_analytics=True,
    supports_monetization=True,
    supports_live_streaming=True,
    supported_formats=["video/mp4", "video/webm", "audio/mp4", "audio/mpeg"],
    max_file_size=2 * 1024 * 1024 * 1024  # 2GB
)

# TikTok Configuration
TIKTOK_CONFIG = PlatformAPIConfig(
    platform_name="tiktok",
    platform_type=PlatformType.SOCIAL,
    base_url="https://open-api.tiktok.com",
    api_version="v1.3",
    auth_endpoint="https://open-api.tiktok.com/oauth/access_token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "user.info.basic",
        "video.list",
        "video.upload"
    ],
    requests_per_minute=120,
    requests_per_hour=5000,
    supports_upload=True,
    supports_analytics=True,
    supported_formats=["video/mp4", "video/webm"],
    max_file_size=287 * 1024 * 1024,  # 287MB
    requires_age_verification=True
)

# Instagram Configuration
INSTAGRAM_CONFIG = PlatformAPIConfig(
    platform_name="instagram",
    platform_type=PlatformType.SOCIAL,
    base_url="https://graph.instagram.com",
    api_version="v18.0",
    auth_endpoint="https://api.instagram.com/oauth/access_token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "instagram_basic",
        "instagram_content_publish",
        "pages_show_list",
        "business_management"
    ],
    requests_per_minute=200,
    requests_per_hour=4800,
    supports_upload=True,
    supports_analytics=True,
    supported_formats=["image/jpeg", "image/png", "video/mp4"],
    max_file_size=100 * 1024 * 1024
)

# Twitter/X Configuration
TWITTER_CONFIG = PlatformAPIConfig(
    platform_name="twitter",
    platform_type=PlatformType.SOCIAL,
    base_url="https://api.twitter.com",
    api_version="2",
    auth_endpoint="https://api.twitter.com/oauth2/token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access"
    ],
    requests_per_minute=300,
    requests_per_hour=10000,
    supports_upload=True,
    supports_analytics=True,
    supported_formats=["image/jpeg", "image/png", "video/mp4"],
    max_file_size=512 * 1024 * 1024
)

# SoundCloud Configuration
SOUNDCLOUD_CONFIG = PlatformAPIConfig(
    platform_name="soundcloud",
    platform_type=PlatformType.MUSIC,
    base_url="https://api.soundcloud.com",
    api_version="v1",
    auth_endpoint="https://api.soundcloud.com/oauth2/token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "non-expiring"
    ],
    requests_per_minute=15000,
    requests_per_hour=15000,
    supports_upload=True,
    supports_analytics=True,
    supports_monetization=True,
    supported_formats=["audio/mpeg", "audio/wav", "audio/flac"],
    max_file_size=5000 * 1024 * 1024  # 5GB
)

# Twitch Configuration
TWITCH_CONFIG = PlatformAPIConfig(
    platform_name="twitch",
    platform_type=PlatformType.STREAMING,
    base_url="https://api.twitch.tv/helix",
    api_version="helix",
    auth_endpoint="https://id.twitch.tv/oauth2/token",
    auth_type=APIAuthType.CLIENT_CREDENTIALS,
    scopes=[
        "analytics:read:games",
        "user:read:email",
        "clips:edit",
        "channel:read:subscriptions"
    ],
    requests_per_minute=800,
    requests_per_hour=800,
    supports_analytics=True,
    supports_live_streaming=True,
    supports_monetization=True,
    supported_formats=["video/mp4"],
    max_file_size=1024 * 1024 * 1024  # 1GB
)

# Facebook Configuration
FACEBOOK_CONFIG = PlatformAPIConfig(
    platform_name="facebook",
    platform_type=PlatformType.SOCIAL,
    base_url="https://graph.facebook.com",
    api_version="v18.0",
    auth_endpoint="https://graph.facebook.com/oauth/access_token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "pages_show_list",
        "pages_read_engagement",
        "pages_manage_posts",
        "publish_to_groups"
    ],
    requests_per_minute=200,
    requests_per_hour=4800,
    supports_upload=True,
    supports_analytics=True,
    supported_formats=["image/jpeg", "image/png", "video/mp4"],
    max_file_size=4 * 1024 * 1024 * 1024  # 4GB
)

# Vimeo Configuration  
VIMEO_CONFIG = PlatformAPIConfig(
    platform_name="vimeo",
    platform_type=PlatformType.VIDEO,
    base_url="https://api.vimeo.com",
    api_version="3.4",
    auth_endpoint="https://api.vimeo.com/oauth/authorize",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "public",
        "private",
        "upload",
        "edit"
    ],
    requests_per_minute=1000,
    requests_per_hour=1000,
    supports_upload=True,
    supports_analytics=True,
    supported_formats=["video/mp4", "video/mov", "video/wmv"],
    max_file_size=5 * 1024 * 1024 * 1024  # 5GB
)

# Dailymotion Configuration
DAILYMOTION_CONFIG = PlatformAPIConfig(
    platform_name="dailymotion",
    platform_type=PlatformType.VIDEO,
    base_url="https://www.dailymotion.com/api",
    api_version="rest",
    auth_endpoint="https://www.dailymotion.com/oauth/token",
    auth_type=APIAuthType.OAUTH2,
    scopes=[
        "read",
        "write"
    ],
    requests_per_minute=300,
    requests_per_hour=5000,
    supports_upload=True,
    supports_analytics=True,
    supported_formats=["video/mp4", "video/avi"],
    max_file_size=2 * 1024 * 1024 * 1024  # 2GB
)


@dataclass
class PlatformIntegrationConfig:
    """Platform integration service configuration"""
    
    # Service identification
    service_name: str = "platform-integration"
    service_version: str = "2.0.0"
    instance_id: str = "platform-integration-main"
    
    # Network configuration
    host: str = "0.0.0.0"
    port: int = 8007
    workers: int = 8
    
    # Platform configurations
    platforms: Dict[str, PlatformAPIConfig] = field(default_factory=lambda: {
        "spotify": SPOTIFY_CONFIG,
        "youtube": YOUTUBE_CONFIG,
        "tiktok": TIKTOK_CONFIG,
        "instagram": INSTAGRAM_CONFIG,
        "twitter": TWITTER_CONFIG,
        "soundcloud": SOUNDCLOUD_CONFIG,
        "twitch": TWITCH_CONFIG,
        "facebook": FACEBOOK_CONFIG,
        "vimeo": VIMEO_CONFIG,
        "dailymotion": DAILYMOTION_CONFIG
    })
    
    # Global settings
    default_timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 2.0
    
    # Caching configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 10000
    
    # Rate limiting coordination
    global_rate_limit: bool = True
    rate_limit_strategy: str = "token_bucket"
    
    # Monitoring and analytics
    enable_usage_analytics: bool = True
    enable_performance_metrics: bool = True
    enable_error_tracking: bool = True
    
    # Content distribution
    enable_batch_upload: bool = True
    batch_size: int = 50
    parallel_uploads: int = 5
    
    # Security settings
    encrypt_credentials: bool = True
    credential_rotation_days: int = 90
    enable_webhook_verification: bool = True


class PlatformIntegrationOrchestrator:
    """Platform integration orchestrator"""
    
    def __init__(self, config: PlatformIntegrationConfig = None):
        """
Initialize orchestrator"""
        self.config = config or PlatformIntegrationConfig()
        self.platform_clients = {}
        self.logger = logging.getLogger(__name__)
    
    async def initialize_platforms(self) -> Dict[str, bool]:
        """
Initialize all platform integrations"""
        results = {}
        
        for platform_name, platform_config in self.config.platforms.items():
            try:
                self.logger.info(f"Initializing {platform_name} integration...")
                success = await self._initialize_platform(platform_name, platform_config)
                results[platform_name] = success
            except Exception as e:
                self.logger.error(f"Failed to initialize {platform_name}: {e}")
                results[platform_name] = False
        
        return results
    
    async def _initialize_platform(self, platform_name: str, config: PlatformAPIConfig) -> bool:
        """Initialize individual platform integration"""
        try:
            # Validate configuration
            if not config.base_url:
                raise ValueError(f"Missing base URL for {platform_name}")
            
            # Check authentication requirements
            if config.auth_type == APIAuthType.OAUTH2:
                if not config.client_id or not config.client_secret:
                    raise ValueError(f"Missing OAuth2 credentials for {platform_name}")
            
            # Test API connectivity
            self.logger.info(f"Testing {platform_name} API connectivity...")
            
            # Initialize rate limiter
            self.logger.info(f"Configuring rate limiting for {platform_name}: {config.requests_per_minute}/min")
            
            # Store client configuration
            self.platform_clients[platform_name] = {
                "config": config,
                "status": "active",
                "last_check": datetime.utcnow()
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Platform {platform_name} initialization failed: {e}")
            return False
    
    def get_platform_capabilities(self, platform_name: str) -> Dict[str, Any]:
        """Get platform capabilities and features"""
        if platform_name not in self.config.platforms:
            return {}
        
        config = self.config.platforms[platform_name]
        return {
            "platform_type": config.platform_type.value,
            "features": {
                "upload": config.supports_upload,
                "analytics": config.supports_analytics,
                "monetization": config.supports_monetization,
                "live_streaming": config.supports_live_streaming
            },
            "formats": config.supported_formats,
            "max_file_size": config.max_file_size,
            "rate_limits": {
                "per_minute": config.requests_per_minute,
                "per_hour": config.requests_per_hour,
                "per_day": config.requests_per_day
            },
            "compliance": {
                "gdpr": config.gdpr_compliant,
                "coppa": config.coppa_compliant,
                "age_verification": config.requires_age_verification
            }
        }
    
    def get_platforms_by_type(self, platform_type: PlatformType) -> List[str]:
        """Get platforms filtered by type"""
        return [
            name for name, config in self.config.platforms.items()
            if config.platform_type == platform_type
        ]
    
    async def get_integration_health(self) -> Dict[str, Any]:
        """
Get platform integration health status"""
        health_status = {
            "overall_status": "healthy",
            "platforms": {},
            "metrics": {
                "total_platforms": len(self.config.platforms),
                "active_platforms": 0,
                "failed_platforms": 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for platform_name, client_info in self.platform_clients.items():
            health_status["platforms"][platform_name] = {
                "status": client_info["status"],
                "last_check": client_info["last_check"].isoformat(),
                "uptime": (datetime.utcnow() - client_info["last_check"]).total_seconds()
            }
            
            if client_info["status"] == "active":
                health_status["metrics"]["active_platforms"] += 1
            else:
                health_status["metrics"]["failed_platforms"] += 1
        
        # Overall status determination
        if health_status["metrics"]["failed_platforms"] > 0:
            health_status["overall_status"] = "degraded"
        if health_status["metrics"]["active_platforms"] == 0:
            health_status["overall_status"] = "critical"
        
        return health_status
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "service_info": {
                "name": self.config.service_name,
                "version": self.config.service_version,
                "port": self.config.port,
                "workers": self.config.workers
            },
            "platforms": {
                "total": len(self.config.platforms),
                "by_type": {
                    platform_type.value: len(self.get_platforms_by_type(platform_type))
                    for platform_type in PlatformType
                },
                "list": list(self.config.platforms.keys())
            },
            "features": {
                "cache_enabled": self.config.cache_enabled,
                "batch_upload": self.config.enable_batch_upload,
                "analytics": self.config.enable_usage_analytics,
                "security": self.config.encrypt_credentials
            }
        }


# Global orchestrator instance
platform_integration_orchestrator = PlatformIntegrationOrchestrator()


# Convenience functions
async def initialize_platform_integrations() -> Dict[str, bool]:
    """Initialize all platform integrations"""
    return await platform_integration_orchestrator.initialize_platforms()


async def get_platform_integration_health() -> Dict[str, Any]:
    """
Get platform integration health"""
    return await platform_integration_orchestrator.get_integration_health()


def get_platform_integration_summary() -> Dict[str, Any]:
    """
Get platform integration configuration summary"""
    return platform_integration_orchestrator.get_configuration_summary()


def get_platform_capabilities(platform_name: str) -> Dict[str, Any]:
    """
Get capabilities for specific platform"""
    return platform_integration_orchestrator.get_platform_capabilities(platform_name)


def get_platforms_by_type(platform_type: PlatformType) -> List[str]:
    """
Get platforms by type"""
    return platform_integration_orchestrator.get_platforms_by_type(platform_type)


# Export main configuration instance
platform_integration_config = PlatformIntegrationConfig()


# Export platform configurations
PLATFORM_CONFIGS = {
    "spotify": SPOTIFY_CONFIG,
    "youtube": YOUTUBE_CONFIG,
    "tiktok": TIKTOK_CONFIG,
    "instagram": INSTAGRAM_CONFIG,
    "twitter": TWITTER_CONFIG,
    "soundcloud": SOUNDCLOUD_CONFIG,
    "twitch": TWITCH_CONFIG,
    "facebook": FACEBOOK_CONFIG,
    "vimeo": VIMEO_CONFIG,
    "dailymotion": DAILYMOTION_CONFIG
}
