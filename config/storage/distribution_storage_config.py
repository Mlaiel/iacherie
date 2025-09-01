"""Multi-Platform Distribution Storage Configuration for IA-Influencer Agent Platform
===================================================================================

Professional multi-platform content distribution and syndication storage configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

class DistributionPlatform(Enum):
    """
Supported content distribution platforms."""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

class ContentFormat(Enum):
    """Content formats for distribution."""

    VIDEO_SHORT = "video_short"  # TikTok, YouTube Shorts, Instagram Reels
    VIDEO_LONG = "video_long"    # YouTube, Facebook, LinkedIn
    AUDIO_TRACK = "audio_track"  # Spotify, Apple Music, SoundCloud
    AUDIO_PODCAST = "audio_podcast"  # Spotify, Apple Podcasts
    IMAGE_POST = "image_post"    # Instagram, Pinterest, Twitter
    IMAGE_STORY = "image_story"  # Instagram Stories, Snapchat
    TEXT_POST = "text_post"      # Twitter, LinkedIn, Facebook
    CAROUSEL = "carousel"        # Instagram, LinkedIn
    LIVE_STREAM = "live_stream"  # Twitch, YouTube Live, Instagram Live

class DistributionStatus(Enum):
    """Status of content distribution."""

    PENDING = "pending"
    PROCESSING = "processing"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"
    ARCHIVED = "archived"

@dataclass
class PlatformDistributionConfig:
    """Configuration for individual platform distribution."""
    
    platform: DistributionPlatform
    api_credentials_storage: str
    content_storage_path: str
    metadata_storage_path: str
    supported_formats: List[ContentFormat]
    max_file_size_mb: int
    max_duration_seconds: Optional[int] = None
    supported_aspect_ratios: List[str] = field(default_factory=list)
    supported_resolutions: List[str] = field(default_factory=list)
    api_rate_limits: Dict[str, int] = field(default_factory=dict)
    posting_schedule_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MultiPlatformDistributionConfig:
    """
    Comprehensive multi-platform content distribution configuration.
    Handles content adaptation, scheduling, and syndication across platforms.
    """
    
    # Distribution storage paths
    distribution_queue_path: str = "distribution/queue"
    processed_content_path: str = "distribution/processed"
    distribution_logs_path: str = "distribution/logs"
    analytics_path: str = "distribution/analytics"
    failed_distributions_path: str = "distribution/failed"
    
    # Platform-specific configurations
    platform_configs: Dict[DistributionPlatform, PlatformDistributionConfig] = field(default_factory=dict)
    
    # Content adaptation configuration
    content_adaptation_config: Dict[str, Any] = field(default_factory=lambda: {
        'enable_auto_adaptation': True,
        'quality_optimization': True,
        'format_conversion': True,
        'resolution_scaling': True,
        'aspect_ratio_adjustment': True,
        'subtitle_generation': True,
        'thumbnail_generation': True,
        'watermark_application': True
    })
    
    # Scheduling and automation
    scheduling_config: Dict[str, Any] = field(default_factory=lambda: {
        'enable_bulk_scheduling': True,
        'optimal_timing_ai': True,
        'timezone_adaptation': True,
        'audience_analysis_scheduling': True,
        'cross_platform_coordination': True,
        'retry_failed_posts': True,
        'max_retry_attempts': 3
    })
    
    # Cross-platform analytics
    analytics_config: Dict[str, Any] = field(default_factory=lambda: {
        'unified_analytics': True,
        'real_time_tracking': True,
        'engagement_correlation': True,
        'roi_calculation': True,
        'audience_overlap_analysis': True,
        'content_performance_optimization': True
    })
    
    # Quality control and moderation
    quality_control_config: Dict[str, Any] = field(default_factory=lambda: {
        'auto_content_review': True,
        'platform_guidelines_check': True,
        'copyright_clearance_check': True,
        'brand_safety_scan': True,
        'hashtag_optimization': True,
        'content_categorization': True
    })
    
    def __post_init__(self):
        """Initialize platform-specific distribution configurations."""
        if not self.platform_configs:
            self.platform_configs = {
                DistributionPlatform.YOUTUBE: PlatformDistributionConfig(
                    platform=DistributionPlatform.YOUTUBE,
                    api_credentials_storage="secrets/youtube/credentials",
                    content_storage_path=f"{self.processed_content_path}/youtube",
                    metadata_storage_path=f"{self.analytics_path}/youtube",
                    supported_formats=[
                        ContentFormat.VIDEO_LONG,
                        ContentFormat.VIDEO_SHORT,
                        ContentFormat.LIVE_STREAM
                    ],
                    max_file_size_mb=256000,  # 256GB for YouTube
                    max_duration_seconds=43200,  # 12 hours
                    supported_aspect_ratios=['16:9', '9:16', '1:1'],
                    supported_resolutions=['1920x1080', '1280x720', '3840x2160'],
                    api_rate_limits={
                        'uploads_per_day': 50,
                        'api_calls_per_second': 10
                    },
                    posting_schedule_config={
                        'optimal_times': ['14:00', '17:00', '20:00'],
                        'timezone': 'UTC',
                        'frequency_limit': 'daily'
                    }
                ),
                
                DistributionPlatform.INSTAGRAM: PlatformDistributionConfig(
                    platform=DistributionPlatform.INSTAGRAM,
                    api_credentials_storage="secrets/instagram/credentials",
                    content_storage_path=f"{self.processed_content_path}/instagram",
                    metadata_storage_path=f"{self.analytics_path}/instagram",
                    supported_formats=[
                        ContentFormat.IMAGE_POST,
                        ContentFormat.IMAGE_STORY,
                        ContentFormat.VIDEO_SHORT,
                        ContentFormat.CAROUSEL,
                        ContentFormat.LIVE_STREAM
                    ],
                    max_file_size_mb=100,  # 100MB for Instagram
                    max_duration_seconds=90,  # 90 seconds for Reels
                    supported_aspect_ratios=['1:1', '9:16', '4:5'],
                    supported_resolutions=['1080x1080', '1080x1920', '1080x1350'],
                    api_rate_limits={
                        'posts_per_day': 25,
                        'api_calls_per_hour': 200
                    },
                    posting_schedule_config={
                        'optimal_times': ['11:00', '13:00', '17:00'],
                        'timezone': 'UTC',
                        'frequency_limit': '3_per_day'
                    }
                ),
                
                DistributionPlatform.TIKTOK: PlatformDistributionConfig(
                    platform=DistributionPlatform.TIKTOK,
                    api_credentials_storage="secrets/tiktok/credentials",
                    content_storage_path=f"{self.processed_content_path}/tiktok",
                    metadata_storage_path=f"{self.analytics_path}/tiktok",
                    supported_formats=[ContentFormat.VIDEO_SHORT],
                    max_file_size_mb=287,  # 287MB for TikTok
                    max_duration_seconds=180,  # 3 minutes
                    supported_aspect_ratios=['9:16'],
                    supported_resolutions=['1080x1920', '720x1280'],
                    api_rate_limits={
                        'uploads_per_day': 10,
                        'api_calls_per_minute': 20
                    },
                    posting_schedule_config={
                        'optimal_times': ['18:00', '19:00', '21:00'],
                        'timezone': 'UTC',
                        'frequency_limit': '2_per_day'
                    }
                ),
                
                DistributionPlatform.SPOTIFY: PlatformDistributionConfig(
                    platform=DistributionPlatform.SPOTIFY,
                    api_credentials_storage="secrets/spotify/credentials",
                    content_storage_path=f"{self.processed_content_path}/spotify",
                    metadata_storage_path=f"{self.analytics_path}/spotify",
                    supported_formats=[
                        ContentFormat.AUDIO_TRACK,
                        ContentFormat.AUDIO_PODCAST
                    ],
                    max_file_size_mb=650,  # 650MB for Spotify
                    max_duration_seconds=None,  # No duration limit
                    supported_aspect_ratios=[],  # Not applicable for audio
                    supported_resolutions=[],  # Not applicable for audio
                    api_rate_limits={
                        'track_uploads_per_day': 100,
                        'api_calls_per_second': 1
                    },
                    posting_schedule_config={
                        'release_timing': 'friday_midnight',
                        'timezone': 'UTC',
                        'frequency_limit': 'weekly'
                    }
                )
            }
    
    def get_platform_config(self, platform: DistributionPlatform) -> Optional[PlatformDistributionConfig]:
        """Get configuration for specific platform."""
        return self.platform_configs.get(platform)
    
    def get_supported_platforms_for_format(self, content_format: ContentFormat) -> List[DistributionPlatform]:
        """
Get platforms that support specific content format."""
        supported_platforms = []
        for platform, config in self.platform_configs.items():
            if content_format in config.supported_formats:
                supported_platforms.append(platform)
        return supported_platforms
    
    def is_content_adaptation_enabled(self) -> bool:
        """
Check if automatic content adaptation is enabled."""
        return self.content_adaptation_config.get('enable_auto_adaptation', False)

@dataclass
class ContentSyndicationConfig:
    """
Configuration for content syndication and cross-posting."""
    
    # Syndication rules and logic
    syndication_rules: Dict[str, Any] = field(default_factory=lambda: {
        'enable_auto_syndication': True,
        'cross_platform_tagging': True,
        'unified_hashtag_strategy': True,
        'audience_segmentation': True,
        'content_localization': True,
        'engagement_optimization': True
    })
    
    # Content variation configuration
    content_variation_config: Dict[str, Any] = field(default_factory=lambda: {
        'platform_specific_optimization': True,
        'title_variation': True,
        'description_variation': True,
        'hashtag_variation': True,
        'thumbnail_variation': True,
        'call_to_action_variation': True
    })
    
    # Cross-platform coordination
    coordination_config: Dict[str, Any] = field(default_factory=lambda: {
        'synchronized_posting': True,
        'staggered_release_strategy': True,
        'platform_priority_ordering': True,
        'audience_overlap_prevention': True,
        'content_cannibalization_prevention': True
    })

@dataclass
class DistributionAnalyticsConfig:
    """
Configuration for distribution analytics and performance tracking."""
    
    # Analytics collection configuration
    analytics_collection: Dict[str, Any] = field(default_factory=lambda: {
        'real_time_metrics': True,
        'engagement_tracking': True,
        'reach_analysis': True,
        'conversion_tracking': True,
        'audience_demographics': True,
        'content_performance_scoring': True
    })
    
    # Performance optimization
    optimization_config: Dict[str, Any] = field(default_factory=lambda: {
        'ai_powered_optimization': True,
        'a_b_testing': True,
        'content_scoring': True,
        'optimal_timing_prediction': True,
        'hashtag_performance_analysis': True,
        'competitor_analysis': True
    })
    
    # Reporting and insights
    reporting_config: Dict[str, Any] = field(default_factory=lambda: {
        'automated_reports': True,
        'custom_dashboards': True,
        'alert_notifications': True,
        'trend_analysis': True,
        'roi_calculation': True,
        'growth_projections': True
    })

# Global configuration instances
multi_platform_distribution_config = MultiPlatformDistributionConfig()
content_syndication_config = ContentSyndicationConfig()
distribution_analytics_config = DistributionAnalyticsConfig()

# Configuration validation functions
def validate_distribution_config() -> bool:
    """
Validate multi-platform distribution configuration."""
    try:
        # Validate required paths
        required_paths = [
            multi_platform_distribution_config.distribution_queue_path,
            multi_platform_distribution_config.processed_content_path,
            multi_platform_distribution_config.distribution_logs_path,
            multi_platform_distribution_config.analytics_path
        ]
        
        for path in required_paths:
            if not path or not isinstance(path, str):
                return False
        
        # Validate platform configurations
        required_platforms = [
            DistributionPlatform.YOUTUBE,
            DistributionPlatform.INSTAGRAM,
            DistributionPlatform.TIKTOK
        ]
        
        for platform in required_platforms:
            if platform not in multi_platform_distribution_config.platform_configs:
                return False
        
        return True
        
    except Exception:
        return False

def validate_content_syndication_config() -> bool:
    """
Validate content syndication configuration."""
    try:
        # Validate syndication rules
        rules = content_syndication_config.syndication_rules
        required_keys = ['enable_auto_syndication', 'cross_platform_tagging']
        
        for key in required_keys:
            if key not in rules:
                return False
        
        return True
        
    except Exception:
        return False

# Export all configurations
__all__ = [
    'MultiPlatformDistributionConfig',
    'ContentSyndicationConfig',
    'DistributionAnalyticsConfig',
    'PlatformDistributionConfig',
    'DistributionPlatform',
    'ContentFormat',
    'DistributionStatus',
    'multi_platform_distribution_config',
    'content_syndication_config',
    'distribution_analytics_config',
    'validate_distribution_config',
    'validate_content_syndication_config'
]
