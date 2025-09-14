"""
Configuration Module - Platform Configurations
Advanced platform-specific configuration management for Ainflue Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from pathlib import Path

class PlatformType(Enum):
    """Supported platform types"""
    SOCIAL_VIDEO = "social_video"
    SOCIAL_AUDIO = "social_audio"
    SOCIAL_IMAGE = "social_image"
    SOCIAL_TEXT = "social_text"
    PROFESSIONAL = "professional"
    STREAMING = "streaming"
    PODCAST = "podcast"
    BLOG = "blog"
    ECOMMERCE = "ecommerce"

class ContentFormat(Enum):
    """Supported content formats"""
    VIDEO_MP4 = "video/mp4"
    VIDEO_MOV = "video/mov"
    VIDEO_AVI = "video/avi"
    AUDIO_MP3 = "audio/mp3"
    AUDIO_WAV = "audio/wav"
    AUDIO_AAC = "audio/aac"
    IMAGE_JPG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    TEXT_MARKDOWN = "text/markdown"

@dataclass
class PlatformLimits:
    """Platform-specific limits and constraints"""
    max_file_size: int  # bytes
    max_video_length: Optional[int] = None  # seconds
    max_audio_length: Optional[int] = None  # seconds
    max_text_length: Optional[int] = None  # characters
    max_images_per_post: Optional[int] = None
    supported_formats: List[ContentFormat] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    
@dataclass
class PlatformAuth:
    """Platform authentication configuration"""
    auth_type: str  # oauth2, api_key, bearer_token
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_url: Optional[str] = None
    auth_url: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    
@dataclass
class PlatformEndpoints:
    """Platform API endpoints"""
    base_url: str
    upload_endpoint: str
    publish_endpoint: str
    analytics_endpoint: Optional[str] = None
    delete_endpoint: Optional[str] = None
    update_endpoint: Optional[str] = None
    user_info_endpoint: Optional[str] = None
    
@dataclass
class PlatformConfig:
    """Complete platform configuration"""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    enabled: bool
    limits: PlatformLimits
    auth: PlatformAuth
    endpoints: PlatformEndpoints
    features: Dict[str, bool] = field(default_factory=dict)
    metadata_fields: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class PlatformConfigManager:
    """
    Manages platform-specific configurations for all supported platforms
    Provides centralized configuration management with environment-specific overrides
    """
    
    def __init__(self, config_dir -> None: str = "config/platforms") -> None:
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, PlatformConfig] = {}
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Load all platform configurations
        self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """Load all platform configurations"""
        # YouTube Configuration
        self.configs["youtube"] = PlatformConfig(
            platform_id="youtube",
            platform_name="YouTube",
            platform_type=PlatformType.SOCIAL_VIDEO,
            enabled=True,
            limits=PlatformLimits(
                max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
                max_video_length=12 * 3600,  # 12 hours
                supported_formats=[
                    ContentFormat.VIDEO_MP4,
                    ContentFormat.VIDEO_MOV,
                    ContentFormat.VIDEO_AVI
                ],
                rate_limits={
                    "uploads_per_day": 6,
                    "api_calls_per_day": 10000,
                    "quota_units_per_day": 1000000
                }
            ),
            auth=PlatformAuth(
                auth_type="oauth2",
                client_id=os.getenv("YOUTUBE_CLIENT_ID"),
                client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
                token_url="https://oauth2.googleapis.com/token",
                auth_url="https://accounts.google.com/o/oauth2/auth",
                scopes=[
                    "https://www.googleapis.com/auth/youtube.upload",
                    "https://www.googleapis.com/auth/youtube",
                    "https://www.googleapis.com/auth/youtube.readonly"
                ]
            ),
            endpoints=PlatformEndpoints(
                base_url="https://www.googleapis.com/youtube/v3",
                upload_endpoint="/videos",
                publish_endpoint="/videos",
                analytics_endpoint="/reports",
                delete_endpoint="/videos",
                update_endpoint="/videos"
            ),
            features={
                "live_streaming": True,
                "scheduled_publishing": True,
                "thumbnails": True,
                "captions": True,
                "end_screens": True,
                "cards": True,
                "monetization": True
            },
            metadata_fields=[
                "title", "description", "tags", "category_id",
                "default_language", "thumbnail", "privacy_status"
            ]
        )
        
        # TikTok Configuration
        self.configs["tiktok"] = PlatformConfig(
            platform_id="tiktok",
            platform_name="TikTok",
            platform_type=PlatformType.SOCIAL_VIDEO,
            enabled=True,
            limits=PlatformLimits(
                max_file_size=287 * 1024 * 1024,  # 287MB
                max_video_length=600,  # 10 minutes
                supported_formats=[ContentFormat.VIDEO_MP4],
                rate_limits={
                    "uploads_per_day": 30,
                    "api_calls_per_hour": 1000
                }
            ),
            auth=PlatformAuth(
                auth_type="oauth2",
                client_id=os.getenv("TIKTOK_CLIENT_ID"),
                client_secret=os.getenv("TIKTOK_CLIENT_SECRET"),
                token_url="https://open-api.tiktok.com/oauth/access_token/",
                auth_url="https://open-api.tiktok.com/platform/oauth/connect/",
                scopes=["video.upload", "user.info.basic"]
            ),
            endpoints=PlatformEndpoints(
                base_url="https://open.tiktokapis.com/v2",
                upload_endpoint="/post/publish/video/init/",
                publish_endpoint="/post/publish/",
                analytics_endpoint="/research/video/query/",
                user_info_endpoint="/user/info/"
            ),
            features={
                "duets": True,
                "reactions": True,
                "effects": True,
                "sounds": True,
                "hashtag_challenges": True,
                "live_streaming": True
            },
            metadata_fields=[
                "caption", "privacy_level", "comment_disabled",
                "duet_disabled", "stitch_disabled"
            ]
        )
        
        # Instagram Configuration
        self.configs["instagram"] = PlatformConfig(
            platform_id="instagram",
            platform_name="Instagram",
            platform_type=PlatformType.SOCIAL_IMAGE,
            enabled=True,
            limits=PlatformLimits(
                max_file_size=100 * 1024 * 1024,  # 100MB for videos
                max_video_length=60,  # 60 seconds for reels
                max_images_per_post=10,
                supported_formats=[
                    ContentFormat.IMAGE_JPG,
                    ContentFormat.IMAGE_PNG,
                    ContentFormat.VIDEO_MP4
                ],
                rate_limits={
                    "posts_per_day": 25,
                    "api_calls_per_hour": 200
                }
            ),
            auth=PlatformAuth(
                auth_type="oauth2",
                client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
                client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET"),
                token_url="https://api.instagram.com/oauth/access_token",
                auth_url="https://api.instagram.com/oauth/authorize",
                scopes=["instagram_basic", "instagram_content_publish"]
            ),
            endpoints=PlatformEndpoints(
                base_url="https://graph.instagram.com",
                upload_endpoint="/me/media",
                publish_endpoint="/me/media_publish",
                analytics_endpoint="/me/insights",
                user_info_endpoint="/me"
            ),
            features={
                "stories": True,
                "reels": True,
                "igtv": True,
                "shopping": True,
                "live_streaming": True,
                "filters": True
            },
            metadata_fields=[
                "caption", "location_id", "user_tags",
                "product_tags", "alt_text"
            ]
        )
        
        # Twitter/X Configuration
        self.configs["twitter"] = PlatformConfig(
            platform_id="twitter",
            platform_name="Twitter/X",
            platform_type=PlatformType.SOCIAL_TEXT,
            enabled=True,
            limits=PlatformLimits(
                max_file_size=512 * 1024 * 1024,  # 512MB for videos
                max_video_length=140,  # 140 seconds
                max_text_length=280,  # 280 characters
                max_images_per_post=4,
                supported_formats=[
                    ContentFormat.IMAGE_JPG,
                    ContentFormat.IMAGE_PNG,
                    ContentFormat.IMAGE_GIF,
                    ContentFormat.VIDEO_MP4
                ],
                rate_limits={
                    "tweets_per_day": 2400,
                    "api_calls_per_15min": 300
                }
            ),
            auth=PlatformAuth(
                auth_type="oauth2",
                client_id=os.getenv("TWITTER_CLIENT_ID"),
                client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
                token_url="https://api.twitter.com/2/oauth2/token",
                auth_url="https://twitter.com/i/oauth2/authorize",
                scopes=["tweet.read", "tweet.write", "users.read"]
            ),
            endpoints=PlatformEndpoints(
                base_url="https://api.twitter.com/2",
                upload_endpoint="/tweets",
                publish_endpoint="/tweets",
                analytics_endpoint="/tweets/search/recent",
                delete_endpoint="/tweets",
                user_info_endpoint="/users/me"
            ),
            features={
                "threads": True,
                "polls": True,
                "spaces": True,
                "fleets": False,
                "communities": True,
                "monetization": True
            },
            metadata_fields=[
                "text", "media_ids", "poll_options", "poll_duration",
                "reply_settings", "geo"
            ]
        )
        
        # Spotify Configuration
        self.configs["spotify"] = PlatformConfig(
            platform_id="spotify",
            platform_name="Spotify",
            platform_type=PlatformType.SOCIAL_AUDIO,
            enabled=True,
            limits=PlatformLimits(
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_audio_length=None,  # No limit
                supported_formats=[
                    ContentFormat.AUDIO_MP3,
                    ContentFormat.AUDIO_WAV,
                    ContentFormat.AUDIO_AAC
                ],
                rate_limits={
                    "api_calls_per_second": 100,
                    "uploads_per_day": 1000
                }
            ),
            auth=PlatformAuth(
                auth_type="oauth2",
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                token_url="https://accounts.spotify.com/api/token",
                auth_url="https://accounts.spotify.com/authorize",
                scopes=[
                    "playlist-modify-public",
                    "playlist-modify-private",
                    "user-read-private"
                ]
            ),
            endpoints=PlatformEndpoints(
                base_url="https://api.spotify.com/v1",
                upload_endpoint="/artists/{artist_id}/albums",
                publish_endpoint="/playlists/{playlist_id}/tracks",
                analytics_endpoint="/artists/{artist_id}/top-tracks",
                user_info_endpoint="/me"
            ),
            features={
                "playlists": True,
                "podcasts": True,
                "albums": True,
                "singles": True,
                "collaborative_playlists": True,
                "podcast_monetization": True
            },
            metadata_fields=[
                "name", "description", "genre", "explicit",
                "release_date", "copyright", "album_art"
            ]
        )
        
        # LinkedIn Configuration
        self.configs["linkedin"] = PlatformConfig(
            platform_id="linkedin",
            platform_name="LinkedIn",
            platform_type=PlatformType.PROFESSIONAL,
            enabled=True,
            limits=PlatformLimits(
                max_file_size=200 * 1024 * 1024,  # 200MB
                max_video_length=600,  # 10 minutes
                max_text_length=3000,  # 3000 characters
                supported_formats=[
                    ContentFormat.IMAGE_JPG,
                    ContentFormat.IMAGE_PNG,
                    ContentFormat.VIDEO_MP4,
                    ContentFormat.TEXT_PLAIN
                ],
                rate_limits={
                    "posts_per_day": 100,
                    "api_calls_per_day": 500000
                }
            ),
            auth=PlatformAuth(
                auth_type="oauth2",
                client_id=os.getenv("LINKEDIN_CLIENT_ID"),
                client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
                token_url="https://www.linkedin.com/oauth/v2/accessToken",
                auth_url="https://www.linkedin.com/oauth/v2/authorization",
                scopes=["r_liteprofile", "r_emailaddress", "w_member_social"]
            ),
            endpoints=PlatformEndpoints(
                base_url="https://api.linkedin.com/v2",
                upload_endpoint="/assets",
                publish_endpoint="/shares",
                analytics_endpoint="/socialActions",
                user_info_endpoint="/people/~"
            ),
            features={
                "articles": True,
                "newsletters": True,
                "live_events": True,
                "polls": True,
                "document_sharing": True,
                "company_pages": True
            },
            metadata_fields=[
                "text", "visibility", "target_audience",
                "content_certification_required"
            ]
        )
        
    def get_config(self, platform_id: str) -> Optional[PlatformConfig]:
        """Get configuration for a specific platform"""
        return self.configs.get(platform_id)
    
    def get_enabled_platforms(self) -> List[PlatformConfig]:
        """Get all enabled platform configurations"""
        return [config for config in self.configs.values() if config.enabled]
    
    def get_platforms_by_type(self, platform_type: PlatformType) -> List[PlatformConfig]:
        """Get platforms by type"""
        return [
            config for config in self.configs.values()
            if config.platform_type == platform_type and config.enabled
        ]
    
    def get_platforms_supporting_format(self, content_format: ContentFormat) -> List[PlatformConfig]:
        """Get platforms that support a specific content format"""
        return [
            config for config in self.configs.values()
            if content_format in config.limits.supported_formats and config.enabled
        ]
    
    def update_platform_auth(self, platform_id -> None: str, auth_data -> None: Dict[str, Any]) -> None:
        """Update authentication data for a platform"""
        if platform_id in self.configs:
            config = self.configs[platform_id]
            
            if "access_token" in auth_data:
                config.auth.access_token = auth_data["access_token"]
            if "refresh_token" in auth_data:
                config.auth.refresh_token = auth_data["refresh_token"]
            if "api_key" in auth_data:
                config.auth.api_key = auth_data["api_key"]
    
    def validate_content_for_platform(
        self,
        platform_id: str,
        content_format: ContentFormat,
        file_size: int,
        duration: Optional[int] = None,
        text_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """Validate content against platform limits"""
        config = self.get_config(platform_id)
        if not config:
            return {
                "valid": False,
                "errors": [f"Platform {platform_id} not found"]
            }
        
        errors = []
        warnings = []
        
        # Check if platform is enabled
        if not config.enabled:
            errors.append(f"Platform {platform_id} is disabled")
        
        # Check format support
        if content_format not in config.limits.supported_formats:
            errors.append(f"Format {content_format.value} not supported")
        
        # Check file size
        if file_size > config.limits.max_file_size:
            errors.append(
                f"File size {file_size} exceeds limit of {config.limits.max_file_size}"
            )
        
        # Check duration limits
        if duration and config.limits.max_video_length:
            if duration > config.limits.max_video_length:
                errors.append(
                    f"Duration {duration}s exceeds limit of {config.limits.max_video_length}s"
                )
        
        if duration and config.limits.max_audio_length:
            if duration > config.limits.max_audio_length:
                errors.append(
                    f"Audio duration {duration}s exceeds limit of {config.limits.max_audio_length}s"
                )
        
        # Check text length
        if text_length and config.limits.max_text_length:
            if text_length > config.limits.max_text_length:
                errors.append(
                    f"Text length {text_length} exceeds limit of {config.limits.max_text_length}"
                )
            elif text_length > config.limits.max_text_length * 0.9:
                warnings.append(
                    f"Text length {text_length} is close to limit of {config.limits.max_text_length}"
                )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "platform_config": config
        }
    
    def get_optimal_platforms_for_content(
        self,
        content_format: ContentFormat,
        file_size: int,
        duration: Optional[int] = None,
        text_length: Optional[int] = None
    ) -> List[str]:
        """Get optimal platforms for given content specifications"""
        optimal_platforms = []
        
        for platform_id, config in self.configs.items():
            validation = self.validate_content_for_platform(
                platform_id, content_format, file_size, duration, text_length
            )
            
            if validation["valid"]:
                optimal_platforms.append(platform_id)
        
        return optimal_platforms
    
    def export_config(self, platform_id: str) -> Dict[str, Any]:
        """Export platform configuration as dictionary"""
        config = self.get_config(platform_id)
        if not config:
            return {}
        
        return {
            "platform_id": config.platform_id,
            "platform_name": config.platform_name,
            "platform_type": config.platform_type.value,
            "enabled": config.enabled,
            "limits": {
                "max_file_size": config.limits.max_file_size,
                "max_video_length": config.limits.max_video_length,
                "max_audio_length": config.limits.max_audio_length,
                "max_text_length": config.limits.max_text_length,
                "max_images_per_post": config.limits.max_images_per_post,
                "supported_formats": [f.value for f in config.limits.supported_formats],
                "rate_limits": config.limits.rate_limits
            },
            "auth": {
                "auth_type": config.auth.auth_type,
                "scopes": config.auth.scopes,
                "token_url": config.auth.token_url,
                "auth_url": config.auth.auth_url
            },
            "endpoints": {
                "base_url": config.endpoints.base_url,
                "upload_endpoint": config.endpoints.upload_endpoint,
                "publish_endpoint": config.endpoints.publish_endpoint,
                "analytics_endpoint": config.endpoints.analytics_endpoint
            },
            "features": config.features,
            "metadata_fields": config.metadata_fields,
            "custom_settings": config.custom_settings
        }
    
    def save_config_to_file(self, platform_id -> None: str, file_path -> None: str) -> None:
        """Save platform configuration to JSON file"""
        config_data = self.export_config(platform_id)
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_config_from_file(self, platform_id -> None: str, file_path -> None: str) -> None:
        """Load platform configuration from JSON file"""
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        
        # Convert back to PlatformConfig object
        limits = PlatformLimits(
            max_file_size=config_data["limits"]["max_file_size"],
            max_video_length=config_data["limits"].get("max_video_length"),
            max_audio_length=config_data["limits"].get("max_audio_length"),
            max_text_length=config_data["limits"].get("max_text_length"),
            max_images_per_post=config_data["limits"].get("max_images_per_post"),
            supported_formats=[
                ContentFormat(f) for f in config_data["limits"]["supported_formats"]
            ],
            rate_limits=config_data["limits"]["rate_limits"]
        )
        
        auth = PlatformAuth(
            auth_type=config_data["auth"]["auth_type"],
            scopes=config_data["auth"]["scopes"],
            token_url=config_data["auth"].get("token_url"),
            auth_url=config_data["auth"].get("auth_url")
        )
        
        endpoints = PlatformEndpoints(
            base_url=config_data["endpoints"]["base_url"],
            upload_endpoint=config_data["endpoints"]["upload_endpoint"],
            publish_endpoint=config_data["endpoints"]["publish_endpoint"],
            analytics_endpoint=config_data["endpoints"].get("analytics_endpoint")
        )
        
        platform_config = PlatformConfig(
            platform_id=config_data["platform_id"],
            platform_name=config_data["platform_name"],
            platform_type=PlatformType(config_data["platform_type"]),
            enabled=config_data["enabled"],
            limits=limits,
            auth=auth,
            endpoints=endpoints,
            features=config_data["features"],
            metadata_fields=config_data["metadata_fields"],
            custom_settings=config_data["custom_settings"]
        )
        
        self.configs[platform_id] = platform_config
    
    def get_all_platform_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all platform configurations"""
        summaries = {}
        
        for platform_id, config in self.configs.items():
            summaries[platform_id] = {
                "name": config.platform_name,
                "type": config.platform_type.value,
                "enabled": config.enabled,
                "supported_formats": [f.value for f in config.limits.supported_formats],
                "max_file_size_mb": config.limits.max_file_size // (1024 * 1024),
                "features_count": len(config.features),
                "auth_configured": bool(config.auth.client_id or config.auth.api_key)
            }
        
        return summaries

# Global platform config manager instance
platform_config_manager = PlatformConfigManager()

# Convenience functions
def get_platform_config(platform_id: str) -> Optional[PlatformConfig]:
    """Get platform configuration"""
    return platform_config_manager.get_config(platform_id)

def get_enabled_platforms() -> List[PlatformConfig]:
    """Get all enabled platforms"""
    return platform_config_manager.get_enabled_platforms()

def validate_content_for_platform(
    platform_id: str,
    content_format: ContentFormat,
    file_size: int,
    **kwargs
) -> Dict[str, Any]:
    """Validate content for platform"""
    return platform_config_manager.validate_content_for_platform(
        platform_id, content_format, file_size, **kwargs
    )


# Aliases for backward compatibility
PlatformConfiguration = PlatformConfig
PlatformSettings = PlatformConfig
APILimits = PlatformLimits
ContentSpecs = PlatformLimits


# Export all classes
__all__ = [
    'PlatformType',
    'ContentFormat', 
    'PlatformLimits',
    'PlatformAuth',
    'PlatformEndpoints',
    'PlatformConfig',
    'PlatformConfigManager',
    'PlatformConfiguration',  # Alias
    'PlatformSettings',       # Alias
    'APILimits',             # Alias
    'ContentSpecs',          # Alias
    'platform_config_manager',
    'get_platform_config',
    'get_enabled_platforms',
    'validate_content_for_platform'
]