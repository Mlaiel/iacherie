"""
import logging

Distribution Business Configuration - Enterprise Configuration Management
Enterprise configuration for distribution business logic and multi-platform systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)


class DistributionPlatform(str, Enum):
    """Distribution platform types"""
    # Social Media Platforms
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    
    # Content Platforms
    WORDPRESS = "wordpress"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    GHOST = "ghost"
    
    # Music Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    
    # Video Platforms
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    
    # Professional Platforms
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    GITHUB = "github"
    
    # E-commerce Platforms
    SHOPIFY = "shopify"
    ETSY = "etsy"
    AMAZON = "amazon"


class DistributionStrategy(str, Enum):
    """Distribution strategies"""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PRIORITY_BASED = "priority_based"
    AUDIENCE_TARGETED = "audience_targeted"
    PLATFORM_OPTIMIZED = "platform_optimized"
    TIME_ZONE_OPTIMIZED = "time_zone_optimized"


class ContentFormat(str, Enum):
    """Content format adaptations"""
    ORIGINAL = "original"
    CROPPED = "cropped"
    RESIZED = "resized"
    COMPRESSED = "compressed"
    TRANSCODED = "transcoded"
    OPTIMIZED = "optimized"


class DistributionStatus(str, Enum):
    """Distribution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class PlatformConfiguration:
    """Platform-specific configuration"""
    platform_name: str
    api_endpoints: Dict[str, str]
    authentication: Dict[str, Any]
    content_formats: List[str]
    size_limits: Dict[str, int]
    rate_limits: Dict[str, int]
    optimization_settings: Dict[str, Any]
    posting_schedule: Dict[str, Any]


@dataclass
class DistributionRule:
    """Distribution rule configuration"""
    rule_name: str
    conditions: Dict[str, Any]
    target_platforms: List[DistributionPlatform]
    content_adaptations: Dict[str, ContentFormat]
    scheduling_preferences: Dict[str, Any]
    priority_level: int


@dataclass
class GlobalDistributionSettings:
    """Global distribution settings"""
    cdn_enabled: bool
    regional_optimization: bool
    language_localization: bool
    timezone_optimization: bool
    performance_tracking: bool
    analytics_integration: bool


class DistributionBusinessSettings:
    """Distribution business configuration settings"""
    
    def __init__(self) -> None:
        # Platform Configurations
        self.platform_configurations = {
            DistributionPlatform.INSTAGRAM: PlatformConfiguration(
                platform_name="Instagram",
                api_endpoints={
                    "post": "https://graph.instagram.com/v18.0/me/media",
                    "auth": "https://api.instagram.com/oauth/authorize",
                    "insights": "https://graph.instagram.com/v18.0/{media-id}/insights"
                },
                authentication={
                    "type": "oauth2",
                    "scopes": ["instagram_basic", "instagram_content_publish"],
                    "token_refresh": True
                },
                content_formats=["image", "video", "carousel", "reel", "story"],
                size_limits={
                    "image_max_size": 8 * 1024 * 1024,  # 8MB
                    "video_max_size": 100 * 1024 * 1024,  # 100MB
                    "video_max_duration": 60  # seconds
                },
                rate_limits={
                    "posts_per_hour": 25,
                    "posts_per_day": 200,
                    "api_calls_per_hour": 200
                },
                optimization_settings={
                    "image_aspect_ratios": ["1:1", "4:5", "9:16"],
                    "video_aspect_ratios": ["1:1", "4:5", "9:16"],
                    "optimal_posting_times": ["11:00", "14:00", "19:00"],
                    "hashtag_limit": 30
                },
                posting_schedule={
                    "timezone": "UTC",
                    "batch_posting": True,
                    "auto_schedule": True,
                    "peak_times": ["12:00-14:00", "17:00-20:00"]
                }
            ),
            
            DistributionPlatform.YOUTUBE: PlatformConfiguration(
                platform_name="YouTube",
                api_endpoints={
                    "upload": "https://www.googleapis.com/upload/youtube/v3/videos",
                    "auth": "https://accounts.google.com/oauth2/v2/auth",
                    "analytics": "https://youtubeanalytics.googleapis.com/v2/reports"
                },
                authentication={
                    "type": "oauth2",
                    "scopes": ["youtube.upload", "youtube.readonly"],
                    "token_refresh": True
                },
                content_formats=["video", "short", "livestream"],
                size_limits={
                    "video_max_size": 128 * 1024 * 1024 * 1024,  # 128GB
                    "video_max_duration": 12 * 60 * 60,  # 12 hours
                    "thumbnail_max_size": 2 * 1024 * 1024  # 2MB
                },
                rate_limits={
                    "uploads_per_day": 100,
                    "api_calls_per_day": 10000
                },
                optimization_settings={
                    "video_resolutions": ["1080p", "720p", "480p"],
                    "thumbnail_size": "1280x720",
                    "optimal_posting_times": ["14:00", "15:00", "20:00"],
                    "tag_limit": 12
                },
                posting_schedule={
                    "timezone": "UTC",
                    "scheduled_publishing": True,
                    "premiere_scheduling": True,
                    "peak_times": ["14:00-16:00", "19:00-21:00"]
                }
            ),
            
            DistributionPlatform.TIKTOK: PlatformConfiguration(
                platform_name="TikTok",
                api_endpoints={
                    "upload": "https://open-api.tiktok.com/share/video/upload/",
                    "auth": "https://www.tiktok.com/auth/authorize/",
                    "analytics": "https://open-api.tiktok.com/video/data/"
                },
                authentication={
                    "type": "oauth2",
                    "scopes": ["video.upload", "user.info.basic"],
                    "token_refresh": True
                },
                content_formats=["video", "image_slideshow"],
                size_limits={
                    "video_max_size": 500 * 1024 * 1024,  # 500MB
                    "video_max_duration": 180,  # 3 minutes
                    "video_min_duration": 3
                },
                rate_limits={
                    "uploads_per_day": 50,
                    "api_calls_per_hour": 100
                },
                optimization_settings={
                    "video_aspect_ratio": "9:16",
                    "video_resolution": "1080x1920",
                    "optimal_posting_times": ["06:00", "10:00", "19:00"],
                    "hashtag_limit": 100
                },
                posting_schedule={
                    "timezone": "UTC",
                    "auto_publish": True,
                    "trend_timing": True,
                    "peak_times": ["06:00-10:00", "19:00-23:00"]
                }
            ),
            
            DistributionPlatform.SPOTIFY: PlatformConfiguration(
                platform_name="Spotify",
                api_endpoints={
                    "upload": "https://api.spotify.com/v1/albums",
                    "auth": "https://accounts.spotify.com/authorize",
                    "analytics": "https://api.spotify.com/v1/me/player/recently-played"
                },
                authentication={
                    "type": "oauth2",
                    "scopes": ["user-read-private", "user-modify-playback-state"],
                    "token_refresh": True
                },
                content_formats=["audio", "podcast"],
                size_limits={
                    "audio_max_size": 100 * 1024 * 1024,  # 100MB
                    "audio_max_duration": 10 * 60,  # 10 minutes
                    "cover_art_size": 3000 * 3000  # 3000x3000 pixels
                },
                rate_limits={
                    "uploads_per_day": 10,
                    "api_calls_per_hour": 100
                },
                optimization_settings={
                    "audio_quality": "320kbps",
                    "cover_art_format": "JPEG",
                    "metadata_requirements": ["title", "artist", "album", "genre"],
                    "release_scheduling": True
                },
                posting_schedule={
                    "timezone": "UTC",
                    "release_time": "00:00",
                    "pre_save_campaigns": True,
                    "playlist_pitching": True
                }
            )
        }
        
        # Distribution Rules
        self.distribution_rules = [
            DistributionRule(
                rule_name="musician_content_distribution",
                conditions={
                    "creator_type": "musicians",
                    "content_type": "audio",
                    "quality_score": ">0.8"
                },
                target_platforms=[
                    DistributionPlatform.SPOTIFY,
                    DistributionPlatform.APPLE_MUSIC,
                    DistributionPlatform.YOUTUBE_MUSIC,
                    DistributionPlatform.SOUNDCLOUD
                ],
                content_adaptations={
                    "spotify": ContentFormat.ORIGINAL,
                    "youtube": ContentFormat.OPTIMIZED,
                    "soundcloud": ContentFormat.COMPRESSED
                },
                scheduling_preferences={
                    "strategy": DistributionStrategy.SEQUENTIAL,
                    "delay_hours": 2,
                    "peak_time_optimization": True
                },
                priority_level=1
            ),
            
            DistributionRule(
                rule_name="influencer_social_distribution",
                conditions={
                    "creator_type": "influencers",
                    "content_type": ["image", "video"],
                    "engagement_prediction": ">0.7"
                },
                target_platforms=[
                    DistributionPlatform.INSTAGRAM,
                    DistributionPlatform.TIKTOK,
                    DistributionPlatform.YOUTUBE,
                    DistributionPlatform.TWITTER
                ],
                content_adaptations={
                    "instagram": ContentFormat.OPTIMIZED,
                    "tiktok": ContentFormat.CROPPED,
                    "youtube": ContentFormat.ORIGINAL,
                    "twitter": ContentFormat.COMPRESSED
                },
                scheduling_preferences={
                    "strategy": DistributionStrategy.SIMULTANEOUS,
                    "optimal_timing": True,
                    "cross_promotion": True
                },
                priority_level=2
            ),
            
            DistributionRule(
                rule_name="blogger_content_distribution",
                conditions={
                    "creator_type": "bloggers",
                    "content_type": "article",
                    "seo_score": ">0.75"
                },
                target_platforms=[
                    DistributionPlatform.WORDPRESS,
                    DistributionPlatform.MEDIUM,
                    DistributionPlatform.LINKEDIN,
                    DistributionPlatform.TWITTER
                ],
                content_adaptations={
                    "wordpress": ContentFormat.ORIGINAL,
                    "medium": ContentFormat.OPTIMIZED,
                    "linkedin": ContentFormat.COMPRESSED,
                    "twitter": ContentFormat.CROPPED
                },
                scheduling_preferences={
                    "strategy": DistributionStrategy.PRIORITY_BASED,
                    "seo_optimization": True,
                    "audience_timing": True
                },
                priority_level=1
            )
        ]
        
        # Global Distribution Settings
        self.global_settings = GlobalDistributionSettings(
            cdn_enabled=True,
            regional_optimization=True,
            language_localization=True,
            timezone_optimization=True,
            performance_tracking=True,
            analytics_integration=True
        )
        
        # Content Adaptation Settings
        self.content_adaptation = {
            "automatic_resizing": True,
            "format_conversion": True,
            "quality_optimization": True,
            "compression_settings": {
                "image_quality": 85,
                "video_bitrate": "adaptive",
                "audio_bitrate": "320kbps"
            },
            "aspect_ratio_adaptation": {
                "enabled": True,
                "maintain_quality": True,
                "smart_cropping": True,
                "ai_powered": True
            }
        }
        
        # Scheduling and Timing
        self.scheduling_settings = {
            "optimal_timing_analysis": True,
            "audience_timezone_detection": True,
            "peak_time_calculation": True,
            "cross_platform_coordination": True,
            "batch_scheduling": True,
            "real_time_adjustments": True
        }
        
        # Analytics and Tracking
        self.analytics_settings = {
            "performance_tracking": True,
            "engagement_monitoring": True,
            "reach_analysis": True,
            "conversion_tracking": True,
            "roi_calculation": True,
            "cross_platform_attribution": True,
            "real_time_dashboards": True
        }
        
        # Automation Settings
        self.automation_settings = {
            "auto_distribution": True,
            "smart_scheduling": True,
            "content_optimization": True,
            "error_handling": "retry_with_fallback",
            "success_validation": True,
            "performance_adjustments": True
        }
        
        # Business Intelligence
        self.business_intelligence = {
            "distribution_effectiveness": True,
            "platform_performance_comparison": True,
            "audience_growth_tracking": True,
            "revenue_attribution": True,
            "cost_per_platform": True,
            "predictive_analytics": True
        }
        
        # Compliance and Legal
        self.compliance_settings = {
            "copyright_verification": True,
            "platform_guidelines_check": True,
            "content_moderation": True,
            "age_restriction_handling": True,
            "geographic_restrictions": True,
            "licensing_compliance": True
        }
        
        # Quality Assurance
        self.quality_assurance = {
            "pre_distribution_validation": True,
            "format_compatibility_check": True,
            "metadata_validation": True,
            "content_quality_assessment": True,
            "platform_specific_optimization": True,
            "error_detection": True
        }
    
    def get_platform_config(self, platform: DistributionPlatform) -> Optional[PlatformConfiguration]:
        """Get platform configuration"""
        return self.platform_configurations.get(platform)
    
    def get_distribution_rules_for_creator(self, creator_type: str) -> List[DistributionRule]:
        """Get applicable distribution rules for creator type"""
        applicable_rules = []
        for rule in self.distribution_rules:
            if rule.conditions.get("creator_type") == creator_type:
                applicable_rules.append(rule)
        return sorted(applicable_rules, key=lambda x: x.priority_level)
    
    def get_optimal_platforms_for_content(self, content_type: str, 
                                        creator_type: str) -> List[DistributionPlatform]:
        """Get optimal platforms for content and creator type"""
        rules = self.get_distribution_rules_for_creator(creator_type)
        platforms = []
        
        for rule in rules:
            conditions = rule.conditions
            if (content_type in conditions.get("content_type", []) or 
                conditions.get("content_type") == content_type):
                platforms.extend(rule.target_platforms)
        
        return list(set(platforms))
    
    def calculate_distribution_score(self, platform: DistributionPlatform,
                                   content_metrics: Dict[str, Any]) -> float:
        """Calculate distribution effectiveness score"""
        base_score = 0.7
        
        # Platform-specific scoring logic
        platform_weights = {
            DistributionPlatform.INSTAGRAM: {"engagement": 0.4, "reach": 0.3, "growth": 0.3},
            DistributionPlatform.YOUTUBE: {"watch_time": 0.4, "subscribers": 0.3, "views": 0.3},
            DistributionPlatform.TIKTOK: {"viral_potential": 0.5, "engagement": 0.3, "shares": 0.2}
        }
        
        weights = platform_weights.get(platform, {"engagement": 0.5, "reach": 0.5})
        score = base_score
        
        for metric, weight in weights.items():
            metric_value = content_metrics.get(metric, 0.5)
            score += metric_value * weight * 0.3
        
        return min(score, 1.0)
    
    def get_content_adaptations(self, source_format: str, 
                              target_platform: DistributionPlatform) -> Dict[str, Any]:
        """Get required content adaptations for platform"""
        platform_config = self.get_platform_config(target_platform)
        if not platform_config:
            return {}
        
        adaptations = {
            "format_conversion": False,
            "resize_required": False,
            "compression_needed": False,
            "aspect_ratio_change": False
        }
        
        # Platform-specific adaptation logic
        if target_platform == DistributionPlatform.INSTAGRAM:
            if source_format == "video":
                adaptations.update({
                    "aspect_ratio_change": True,
                    "target_ratio": "1:1",
                    "max_duration": 60,
                    "compression_needed": True
                })
        
        return adaptations
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete distribution configuration"""
        errors = []
        
        # Validate platform configurations
        for platform, config in self.platform_configurations.items():
            if not config.api_endpoints:
                errors.append(f"Missing API endpoints for platform '{platform}'")
            if not config.content_formats:
                errors.append(f"No content formats specified for platform '{platform}'")
        
        # Validate distribution rules
        for rule in self.distribution_rules:
            if not rule.target_platforms:
                errors.append(f"Distribution rule '{rule.rule_name}' has no target platforms")
            if rule.priority_level < 1:
                errors.append(f"Invalid priority level for rule '{rule.rule_name}'")
        
        # Validate global settings
        if not self.global_settings.cdn_enabled:
            errors.append("CDN should be enabled for global distribution")
        
        return errors


# Global distribution business settings instance
distribution_business_settings = DistributionBusinessSettings()

__all__ = [
    "DistributionBusinessSettings",
    "distribution_business_settings",
    "DistributionPlatform",
    "DistributionStrategy",
    "ContentFormat",
    "DistributionStatus",
    "PlatformConfiguration",
    "DistributionRule",
    "GlobalDistributionSettings"
]