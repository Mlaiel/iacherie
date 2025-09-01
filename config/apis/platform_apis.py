"""Platform APIs Configuration - Social Media & Streaming Platform Integration
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module configures all external platform APIs including Spotify, YouTube, Instagram,
TikTok, Twitter/X, and other social media platforms for content distribution and analytics.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class PlatformType(Enum):
    """
Platform type enumeration"""

    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    SOCIAL_MEDIA = "social_media"
    PROFESSIONAL = "professional"
    MESSAGING = "messaging"

class AuthenticationType(Enum):
    """API authentication types"""

    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BEARER_TOKEN = "bearer_token"

@dataclass
class PlatformAPIConfig:
    """Configuration class for platform APIs"""
    platform_name: str
    platform_type: PlatformType
    base_url: str
    auth_url: str
    token_url: str
    api_version: str
    authentication_type: AuthenticationType
    
    # API Keys and Secrets (from environment)
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # OAuth2 Configuration
    redirect_uri: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 3600
    burst_limit: int = 10
    
    # Request Configuration
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0
    
    # Feature Flags
    supports_upload: bool = False
    supports_analytics: bool = False
    supports_live_streaming: bool = False
    supports_monetization: bool = False
    supports_webhooks: bool = False
    
    # Environment-specific configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> Dict[str, Any]:
        """Get configuration for specific environment"""
        base_config = self.__dict__.copy()
        env_config = self.environments.get(environment, {})
        base_config.update(env_config)
        return base_config

# Spotify Configuration
SPOTIFY_CONFIG = PlatformAPIConfig(
    platform_name="spotify",
    platform_type=PlatformType.MUSIC_STREAMING,
    base_url="https://api.spotify.com/v1",
    auth_url="https://accounts.spotify.com/authorize",
    token_url="https://accounts.spotify.com/api/token",
    api_version="v1",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "https://app.ia-influencer.com/callback/spotify"),
    scopes=[
        "user-read-email",
        "user-read-private",
        "user-library-read",
        "user-top-read",
        "user-read-recently-played",
        "user-follow-read",
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-public",
        "playlist-modify-private",
        "user-library-modify",
        "user-follow-modify",
        "streaming",
        "user-read-playback-state",
        "user-modify-playback-state"
    ],
    rate_limit_per_minute=100,
    rate_limit_per_hour=6000,
    supports_analytics=True,
    supports_monetization=True,
    environments={
        "development": {
            "redirect_uri": "http://localhost:3000/callback/spotify",
            "rate_limit_per_minute": 20
        },
        "staging": {
            "redirect_uri": "https://staging.ia-influencer.com/callback/spotify",
            "rate_limit_per_minute": 50
        }
    }
)

# YouTube Configuration
YOUTUBE_CONFIG = PlatformAPIConfig(
    platform_name="youtube",
    platform_type=PlatformType.VIDEO_PLATFORM,
    base_url="https://www.googleapis.com/youtube/v3",
    auth_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://oauth2.googleapis.com/token",
    api_version="v3",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("YOUTUBE_CLIENT_ID"),
    client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
    api_key=os.getenv("YOUTUBE_API_KEY"),
    redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI", "https://app.ia-influencer.com/callback/youtube"),
    scopes=[
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtube-paid-content"
    ],
    rate_limit_per_minute=100,
    rate_limit_per_hour=10000,
    supports_upload=True,
    supports_analytics=True,
    supports_live_streaming=True,
    supports_monetization=True,
    supports_webhooks=True
)

# Instagram Configuration
INSTAGRAM_CONFIG = PlatformAPIConfig(
    platform_name="instagram",
    platform_type=PlatformType.SOCIAL_MEDIA,
    base_url="https://graph.instagram.com",
    auth_url="https://api.instagram.com/oauth/authorize",
    token_url="https://api.instagram.com/oauth/access_token",
    api_version="v17.0",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
    client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET"),
    redirect_uri=os.getenv("INSTAGRAM_REDIRECT_URI", "https://app.ia-influencer.com/callback/instagram"),
    scopes=[
        "instagram_basic",
        "instagram_content_publish",
        "instagram_manage_insights",
        "instagram_manage_comments",
        "pages_show_list",
        "pages_read_engagement",
        "business_management"
    ],
    rate_limit_per_minute=200,
    rate_limit_per_hour=4800,
    supports_upload=True,
    supports_analytics=True,
    supports_monetization=True
)

# TikTok Configuration
TIKTOK_CONFIG = PlatformAPIConfig(
    platform_name="tiktok",
    platform_type=PlatformType.SOCIAL_MEDIA,
    base_url="https://open-api.tiktok.com",
    auth_url="https://www.tiktok.com/auth/authorize",
    token_url="https://open-api.tiktok.com/oauth/access_token",
    api_version="v1",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("TIKTOK_CLIENT_ID"),
    client_secret=os.getenv("TIKTOK_CLIENT_SECRET"),
    redirect_uri=os.getenv("TIKTOK_REDIRECT_URI", "https://app.ia-influencer.com/callback/tiktok"),
    scopes=[
        "user.info.basic",
        "video.list",
        "video.upload",
        "user.info.profile",
        "user.info.stats"
    ],
    rate_limit_per_minute=100,
    rate_limit_per_hour=10000,
    supports_upload=True,
    supports_analytics=True,
    supports_monetization=True
)

# Twitter/X Configuration
TWITTER_CONFIG = PlatformAPIConfig(
    platform_name="twitter",
    platform_type=PlatformType.SOCIAL_MEDIA,
    base_url="https://api.twitter.com/2",
    auth_url="https://twitter.com/i/oauth2/authorize",
    token_url="https://api.twitter.com/2/oauth2/token",
    api_version="2",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("TWITTER_CLIENT_ID"),
    client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
    api_key=os.getenv("TWITTER_API_KEY"),
    redirect_uri=os.getenv("TWITTER_REDIRECT_URI", "https://app.ia-influencer.com/callback/twitter"),
    scopes=[
        "tweet.read",
        "tweet.write",
        "users.read",
        "follows.read",
        "follows.write",
        "space.read",
        "offline.access"
    ],
    rate_limit_per_minute=300,
    rate_limit_per_hour=18000,
    supports_upload=True,
    supports_analytics=True,
    supports_live_streaming=True
)

# LinkedIn Configuration
LINKEDIN_CONFIG = PlatformAPIConfig(
    platform_name="linkedin",
    platform_type=PlatformType.PROFESSIONAL,
    base_url="https://api.linkedin.com/v2",
    auth_url="https://www.linkedin.com/oauth/v2/authorization",
    token_url="https://www.linkedin.com/oauth/v2/accessToken",
    api_version="v2",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("LINKEDIN_CLIENT_ID"),
    client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
    redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", "https://app.ia-influencer.com/callback/linkedin"),
    scopes=[
        "r_liteprofile",
        "r_emailaddress",
        "w_member_social",
        "r_organization_social",
        "w_organization_social"
    ],
    rate_limit_per_minute=100,
    rate_limit_per_hour=5000,
    supports_upload=True,
    supports_analytics=True
)

# Twitch Configuration
TWITCH_CONFIG = PlatformAPIConfig(
    platform_name="twitch",
    platform_type=PlatformType.VIDEO_PLATFORM,
    base_url="https://api.twitch.tv/helix",
    auth_url="https://id.twitch.tv/oauth2/authorize",
    token_url="https://id.twitch.tv/oauth2/token",
    api_version="helix",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("TWITCH_CLIENT_ID"),
    client_secret=os.getenv("TWITCH_CLIENT_SECRET"),
    redirect_uri=os.getenv("TWITCH_REDIRECT_URI", "https://app.ia-influencer.com/callback/twitch"),
    scopes=[
        "analytics:read:extensions",
        "analytics:read:games",
        "channel:read:subscriptions",
        "channel:manage:videos",
        "user:read:email",
        "clips:edit"
    ],
    rate_limit_per_minute=120,
    rate_limit_per_hour=7200,
    supports_live_streaming=True,
    supports_analytics=True,
    supports_monetization=True,
    supports_webhooks=True
)

# SoundCloud Configuration
SOUNDCLOUD_CONFIG = PlatformAPIConfig(
    platform_name="soundcloud",
    platform_type=PlatformType.MUSIC_STREAMING,
    base_url="https://api.soundcloud.com",
    auth_url="https://soundcloud.com/connect",
    token_url="https://api.soundcloud.com/oauth2/token",
    api_version="v1",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("SOUNDCLOUD_CLIENT_ID"),
    client_secret=os.getenv("SOUNDCLOUD_CLIENT_SECRET"),
    redirect_uri=os.getenv("SOUNDCLOUD_REDIRECT_URI", "https://app.ia-influencer.com/callback/soundcloud"),
    scopes=["non-expiring"],
    rate_limit_per_minute=15000,
    supports_upload=True,
    supports_analytics=True
)

# Discord Configuration
DISCORD_CONFIG = PlatformAPIConfig(
    platform_name="discord",
    platform_type=PlatformType.MESSAGING,
    base_url="https://discord.com/api/v10",
    auth_url="https://discord.com/api/oauth2/authorize",
    token_url="https://discord.com/api/oauth2/token",
    api_version="v10",
    authentication_type=AuthenticationType.OAUTH2,
    client_id=os.getenv("DISCORD_CLIENT_ID"),
    client_secret=os.getenv("DISCORD_CLIENT_SECRET"),
    redirect_uri=os.getenv("DISCORD_REDIRECT_URI", "https://app.ia-influencer.com/callback/discord"),
    scopes=[
        "identify",
        "email",
        "guilds",
        "guilds.join",
        "gdm.join",
        "messages.read"
    ],
    rate_limit_per_minute=50,
    supports_webhooks=True
)

# Platform configurations registry
PLATFORM_CONFIGS: Dict[str, PlatformAPIConfig] = {
    "spotify": SPOTIFY_CONFIG,
    "youtube": YOUTUBE_CONFIG,
    "instagram": INSTAGRAM_CONFIG,
    "tiktok": TIKTOK_CONFIG,
    "twitter": TWITTER_CONFIG,
    "linkedin": LINKEDIN_CONFIG,
    "twitch": TWITCH_CONFIG,
    "soundcloud": SOUNDCLOUD_CONFIG,
    "discord": DISCORD_CONFIG
}

def get_platform_config(platform: str) -> Optional[PlatformAPIConfig]:
    """Get platform configuration by name"""
    return PLATFORM_CONFIGS.get(platform.lower())

def get_platforms_by_type(platform_type: PlatformType) -> List[PlatformAPIConfig]:
    """
Get all platforms of specific type"""
    return [config for config in PLATFORM_CONFIGS.values() 
            if config.platform_type == platform_type]
