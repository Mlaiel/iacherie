"""
Multi-Platform Distribution Configuration - Enterprise Configuration Management
Enterprise configuration for multi-platform and global distribution business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        class Config:
            env_prefix = ""
            extra = "allow"
    def Field(**kwargs):
        return kwargs.get('default_factory', kwargs.get('default'))()


class DistributionPlatform(str, Enum):
    """Distribution platforms"""
    # Social Media
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    
    # Streaming
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    
    # Content Platforms
    MEDIUM = "medium"
    SUBSTACK = "substack"
    WORDPRESS = "wordpress"
    
    # Professional
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    GITHUB = "github"


class ContentFormat(str, Enum):
    """Content formats for distribution"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image" 
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    PODCAST = "podcast"


@dataclass
class PlatformConfiguration:
    """Platform-specific configuration"""
    platform: DistributionPlatform
    enabled: bool
    api_credentials: Dict[str, str]
    supported_formats: List[ContentFormat]
    content_requirements: Dict[str, Any]
    publishing_schedule: Dict[str, Any]
    analytics_enabled: bool
    auto_optimization: bool


class MultiPlatformDistributionSettings(BaseSettings):
    """Multi-platform distribution configuration settings"""
    
    # Platform Configurations
    platforms: Dict[str, PlatformConfiguration] = Field(
        default_factory=lambda: {
            "youtube": PlatformConfiguration(
                platform=DistributionPlatform.YOUTUBE,
                enabled=True,
                api_credentials={"api_key": "", "client_id": "", "client_secret": ""},
                supported_formats=[ContentFormat.VIDEO, ContentFormat.LIVE_STREAM],
                content_requirements={
                    "video_formats": ["mp4", "mov", "avi"],
                    "max_file_size": "256GB",
                    "min_resolution": "360p",
                    "max_duration": "12h",
                    "thumbnail_required": True
                },
                publishing_schedule={"optimal_times": ["18:00", "20:00"], "timezone": "UTC"},
                analytics_enabled=True,
                auto_optimization=True
            ),
            "instagram": PlatformConfiguration(
                platform=DistributionPlatform.INSTAGRAM,
                enabled=True,
                api_credentials={"access_token": "", "app_id": "", "app_secret": ""},
                supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.STORY, ContentFormat.REEL],
                content_requirements={
                    "image_formats": ["jpg", "png"],
                    "video_formats": ["mp4", "mov"],
                    "max_file_size": "100MB",
                    "aspect_ratios": ["1:1", "4:5", "9:16"],
                    "max_duration": "60s"
                },
                publishing_schedule={"optimal_times": ["11:00", "14:00", "17:00"], "timezone": "UTC"},
                analytics_enabled=True,
                auto_optimization=True
            ),
            "spotify": PlatformConfiguration(
                platform=DistributionPlatform.SPOTIFY,
                enabled=True,
                api_credentials={"client_id": "", "client_secret": ""},
                supported_formats=[ContentFormat.AUDIO, ContentFormat.PODCAST],
                content_requirements={
                    "audio_formats": ["mp3", "wav", "flac"],
                    "bitrate": "320kbps",
                    "sample_rate": "44.1kHz",
                    "metadata_required": True
                },
                publishing_schedule={"release_fridays": True, "timezone": "UTC"},
                analytics_enabled=True,
                auto_optimization=True
            )
        }
    )
    
    # Global Distribution Settings
    global_distribution: Dict[str, Any] = Field(
        default_factory=lambda: {
            "cdn_integration": {
                "enabled": True,
                "providers": ["cloudflare", "aws_cloudfront", "fastly"],
                "global_edge_servers": True,
                "automatic_optimization": True,
                "geo_routing": True
            },
            "localization": {
                "enabled": True,
                "supported_languages": [
                    "en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar", "hi", "ru"
                ],
                "auto_translation": True,
                "cultural_adaptation": True,
                "local_content_guidelines": True
            },
            "regional_compliance": {
                "gdpr_europe": True,
                "ccpa_california": True,
                "coppa_children": True,
                "local_content_laws": True,
                "age_restrictions": True,
                "content_filtering": True
            }
        }
    )
    
    # Content Synchronization
    content_sync: Dict[str, Any] = Field(
        default_factory=lambda: {
            "cross_platform_sync": True,
            "automated_publishing": True,
            "scheduled_releases": True,
            "version_control": True,
            "conflict_resolution": True,
            "rollback_capability": True,
            "batch_processing": True,
            "priority_queuing": True
        }
    )
    
    # Analytics & Performance
    analytics_performance: Dict[str, Any] = Field(
        default_factory=lambda: {
            "unified_analytics": True,
            "cross_platform_metrics": True,
            "audience_insights": True,
            "engagement_tracking": True,
            "revenue_attribution": True,
            "conversion_tracking": True,
            "real_time_monitoring": True,
            "predictive_analytics": True
        }
    )
    
    # Optimization & AI
    optimization_ai: Dict[str, Any] = Field(
        default_factory=lambda: {
            "ai_content_optimization": True,
            "platform_specific_formatting": True,
            "optimal_timing": True,
            "audience_targeting": True,
            "hashtag_optimization": True,
            "thumbnail_generation": True,
            "caption_optimization": True,
            "trend_analysis": True
        }
    )
    
    class Config:
        env_prefix = "MULTI_PLATFORM_DISTRIBUTION_"
        case_sensitive = False
        extra = "allow"
    
    def validate_configuration(self) -> List[str]:
        """Validate multi-platform distribution configuration"""
        errors = []
        enabled_platforms = [name for name, config in self.platforms.items() if config.enabled]
        if not enabled_platforms:
            errors.append("No distribution platforms enabled")
        
        for platform_name, config in self.platforms.items():
            if config.enabled and not config.supported_formats:
                errors.append(f"Platform '{platform_name}' has no supported formats")
        
        return errors


# Global multi-platform distribution settings instance
multi_platform_distribution_settings = MultiPlatformDistributionSettings()

__all__ = [
    "MultiPlatformDistributionSettings",
    "multi_platform_distribution_settings",
    "DistributionPlatform",
    "ContentFormat",
    "PlatformConfiguration"
]