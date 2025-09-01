"""Platform Integration Module

Central module for all social media and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
from typing import Dict, List, Any

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus,
    PlatformManager
)

# Core platform management
from .distributor import (
    PlatformDistributor, DistributionStrategy, DistributionResult,
    PlatformTarget, DistributionTask, DistributionRule
)
from .aggregator import (
    PlatformAggregator, AggregationType, TimeFrame, MetricDefinition,
    CrossPlatformContent, AggregatedMetrics, PlatformPerformance,
    AudienceInsights
)
from .monitor import (
    PlatformMonitor, MonitorSeverity, MonitorStatus, HealthCheckResult,
    MonitorAlert, log_alert_handler, webhook_alert_handler
)
from .connector import (
    PlatformConnector, PlatformConnectionPool, ConnectionState,
    ConnectionMetrics, get_connector, cleanup_connector
)

# Advanced features
from .metrics import (
    MetricsCollector, MetricType, MetricInterval, MetricPoint,
    MetricSeries, PerformanceMetrics, EngagementMetrics,
    get_metrics_collector, start_metrics_collection, stop_metrics_collection
)
from .scheduler import (
    PlatformScheduler, ScheduleType, TaskStatus, TaskPriority,
    ScheduleConfig, ScheduledTask, get_scheduler, start_scheduler, stop_scheduler
)
from .automation import (
    get_automation_engine, AutomationEngine, AutomationRule,
    AutomationTrigger, AutomationAction, WorkflowStatus
)
from .validation import (
    validate_platform_ecosystem, quick_validation,
    get_ecosystem_health, PlatformValidator
)

# Platform index and ecosystem
from .index import (
    PlatformFactory, PlatformEcosystem, PLATFORM_REGISTRY,
    create_platform, get_available_platforms, is_platform_supported,
    get_ecosystem, shutdown_ecosystem
)

# Original 16 platform implementations
from .spotify import SpotifyPlatform
from .youtube import YouTubePlatform
from .instagram import InstagramPlatform
from .tiktok import TikTokPlatform
from .twitter import TwitterPlatform
from .facebook import FacebookPlatform
from .twitch import TwitchPlatform
from .soundcloud import SoundCloudPlatform
from .apple_music import AppleMusicPlatform
from .bandcamp import BandcampPlatform
from .reddit import RedditPlatform
from .linkedin import LinkedInPlatform
from .pinterest import PinterestPlatform
from .snapchat import SnapchatPlatform
from .discord import DiscordPlatform
from .telegram import TelegramPlatform

# Extended platform implementations for complete ecosystem coverage
from .whatsapp import WhatsAppPlatform
from .vimeo import VimeoPlatform
from .clubhouse import ClubhousePlatform
from .medium import MediumPlatform
from .mastodon import MastodonPlatform
from .bereal import BeRealPlatform
from .onlyfans import OnlyFansPlatform
from .patreon import PatreonPlatform
from .substack import SubstackPlatform
from .threads import ThreadsPlatform
from .kick import KickPlatform
from .rumble import RumblePlatform


# Platform registry for easy access
SUPPORTED_PLATFORMS = {
    # Core original platforms (16)
    PlatformType.SPOTIFY: SpotifyPlatform,
    PlatformType.YOUTUBE: YouTubePlatform,
    PlatformType.INSTAGRAM: InstagramPlatform,
    PlatformType.TIKTOK: TikTokPlatform,
    PlatformType.TWITTER: TwitterPlatform,
    PlatformType.FACEBOOK: FacebookPlatform,
    PlatformType.TWITCH: TwitchPlatform,
    PlatformType.SOUNDCLOUD: SoundCloudPlatform,
    PlatformType.APPLE_MUSIC: AppleMusicPlatform,
    PlatformType.BANDCAMP: BandcampPlatform,
    PlatformType.REDDIT: RedditPlatform,
    PlatformType.LINKEDIN: LinkedInPlatform,
    PlatformType.PINTEREST: PinterestPlatform,
    PlatformType.SNAPCHAT: SnapchatPlatform,
    PlatformType.DISCORD: DiscordPlatform,
    PlatformType.TELEGRAM: TelegramPlatform,
    
    # Extended platforms for complete ecosystem coverage (12 additional)
    PlatformType.WHATSAPP: WhatsAppPlatform,
    PlatformType.VIMEO: VimeoPlatform,
    PlatformType.CLUBHOUSE: ClubhousePlatform,
    PlatformType.MEDIUM: MediumPlatform,
    PlatformType.MASTODON: MastodonPlatform,
    PlatformType.BEREAL: BeRealPlatform,
    PlatformType.ONLYFANS: OnlyFansPlatform,
    PlatformType.PATREON: PatreonPlatform,
    PlatformType.SUBSTACK: SubstackPlatform,
    PlatformType.THREADS: ThreadsPlatform,
    PlatformType.KICK: KickPlatform,
    PlatformType.RUMBLE: RumblePlatform,
}


def get_platform_count() -> int:
    """Get total number of supported platforms"""
    return len(SUPPORTED_PLATFORMS)


def get_platform_categories() -> Dict[str, List[str]]:
    """Get platforms organized by categories"""
    return {
        "social_media": [
            "instagram", "tiktok", "twitter", "facebook", "linkedin", 
            "snapchat", "reddit", "discord", "mastodon", "bereal", "threads"
        ],
        "video_platforms": [
            "youtube", "twitch", "vimeo", "kick", "rumble"
        ],
        "music_audio": [
            "spotify", "soundcloud", "apple_music", "bandcamp", "clubhouse"
        ],
        "messaging": [
            "telegram", "whatsapp", "discord"
        ],
        "creator_economy": [
            "onlyfans", "patreon", "substack"
        ],
        "publishing": [
            "medium", "substack", "linkedin"
        ],
        "visual_content": [
            "instagram", "pinterest", "snapchat", "bereal"
        ]
    }


def get_ecosystem_info() -> Dict[str, Any]:
    """Get comprehensive ecosystem information"""
    return {
        "total_platforms": get_platform_count(),
        "core_platforms": 16,
        "extended_platforms": 12,
        "categories": get_platform_categories(),
        "supported_content_types": [
            ContentType.AUDIO.value,
            ContentType.VIDEO.value,
            ContentType.IMAGE.value,
            ContentType.TEXT.value,
            ContentType.PLAYLIST.value,
            ContentType.ALBUM.value,
            ContentType.TRACK.value
        ],
        "management_features": [
            "content_distribution",
            "analytics_aggregation", 
            "real_time_monitoring",
            "connection_pooling",
            "metrics_collection",
            "task_scheduling",
            "health_checking",
            "performance_monitoring"
        ]
    }


# Export everything for easy imports
__all__ = [
    # Base classes and enums
    'PlatformBase',
    'PlatformConfig', 
    'PlatformType',
    'ContentType',
    'ContentMetadata',
    'UploadResult',
    'AnalyticsData',
    'PlatformStatus',
    'PlatformManager',
    
    # Management classes
    'PlatformDistributor',
    'DistributionStrategy',
    'DistributionResult',
    'PlatformTarget', 
    'DistributionTask',
    'DistributionRule',
    'PlatformAggregator',
    'AggregationType',
    'TimeFrame',
    'MetricDefinition',
    'CrossPlatformContent',
    'AggregatedMetrics',
    'PlatformPerformance',
    'AudienceInsights',
    'PlatformMonitor',
    'MonitorSeverity',
    'MonitorStatus',
    'HealthCheckResult',
    'MonitorAlert',
    'PlatformConnector',
    'PlatformConnectionPool',
    'ConnectionState',
    'ConnectionMetrics',
    
    # Advanced features
    'MetricsCollector',
    'MetricType',
    'MetricInterval',
    'MetricPoint',
    'MetricSeries',
    'PerformanceMetrics',
    'EngagementMetrics',
    'PlatformScheduler',
    'ScheduleType',
    'TaskStatus',
    'TaskPriority',
    'ScheduleConfig',
    'ScheduledTask',
    
    # Ecosystem
    'PlatformFactory',
    'PlatformEcosystem',
    'PLATFORM_REGISTRY',
    
    # Platform implementations - Core (16)
    'SpotifyPlatform',
    'YouTubePlatform',
    'InstagramPlatform',
    'TikTokPlatform',
    'TwitterPlatform',
    'FacebookPlatform',
    'TwitchPlatform',
    'SoundCloudPlatform',
    'AppleMusicPlatform',
    'BandcampPlatform',
    'RedditPlatform',
    'LinkedInPlatform',
    'PinterestPlatform',
    'SnapchatPlatform',
    'DiscordPlatform',
    'TelegramPlatform',
    
    # Platform implementations - Extended (12)
    'WhatsAppPlatform',
    'VimeoPlatform',
    'ClubhousePlatform',
    'MediumPlatform',
    'MastodonPlatform',
    'BeRealPlatform',
    'OnlyFansPlatform',
    'PatreonPlatform',
    'SubstackPlatform',
    'ThreadsPlatform',
    'KickPlatform',
    'RumblePlatform',
    
    # Utility functions
    'create_platform',
    'get_available_platforms',
    'is_platform_supported',
    'get_ecosystem',
    'shutdown_ecosystem',
    'get_connector',
    'cleanup_connector',
    'get_metrics_collector',
    'start_metrics_collection',
    'stop_metrics_collection',
    'get_scheduler',
    'start_scheduler',
    'stop_scheduler',
    'log_alert_handler',
    'webhook_alert_handler',
    
    # Validation utilities
    'validate_platform_ecosystem',
    'quick_validation',
    'get_ecosystem_health',
    'PlatformValidator',
    
    # Data structures
    'SUPPORTED_PLATFORMS',
    
    # Information functions
    'get_platform_count',
    'get_platform_categories',
    'get_ecosystem_info'
]
from .threads import ThreadsPlatform
from .kick import KickPlatform
from .rumble import RumblePlatform

__all__ = [
    # Base classes
    'PlatformBase',
    'PlatformConfig', 
    'PlatformType',
    'ContentType',
    'ContentMetadata',
    'UploadResult',
    'AnalyticsData',
    'PlatformStatus',
    'AuthMethod',
    
    # Core management
    'ContentDistributor',
    'AnalyticsAggregator',
    'PlatformMonitor',
    'PlatformConnector',
    
    # Original 16 platform implementations
    'SpotifyPlatform',
    'YouTubePlatform',
    'InstagramPlatform',
    'TikTokPlatform',
    'TwitterPlatform',
    'FacebookPlatform',
    'TwitchPlatform',
    'SoundCloudPlatform',
    'AppleMusicPlatform',
    'BandcampPlatform',
    'RedditPlatform',
    'LinkedInPlatform',
    'PinterestPlatform',
    'SnapchatPlatform',
    'DiscordPlatform',
    'TelegramPlatform',
    
    # Extended platform implementations (12 additional platforms)
    'WhatsAppPlatform',
    'VimeoPlatform',
    'ClubhousePlatform',
    'MediumPlatform',
    'MastodonPlatform',
    'BeRealPlatform',
    'OnlyFansPlatform',
    'PatreonPlatform',
    'SubstackPlatform',
    'ThreadsPlatform',
    'KickPlatform',
    'RumblePlatform'
]

# Platform registry for dynamic instantiation
PLATFORM_REGISTRY = {
    # Original 16 platforms
    PlatformType.SPOTIFY: SpotifyPlatform,
    PlatformType.YOUTUBE: YouTubePlatform,
    PlatformType.INSTAGRAM: InstagramPlatform,
    PlatformType.TIKTOK: TikTokPlatform,
    PlatformType.TWITTER: TwitterPlatform,
    PlatformType.FACEBOOK: FacebookPlatform,
    PlatformType.TWITCH: TwitchPlatform,
    PlatformType.SOUNDCLOUD: SoundCloudPlatform,
    PlatformType.APPLE_MUSIC: AppleMusicPlatform,
    PlatformType.BANDCAMP: BandcampPlatform,
    PlatformType.REDDIT: RedditPlatform,
    PlatformType.LINKEDIN: LinkedInPlatform,
    PlatformType.PINTEREST: PinterestPlatform,
    PlatformType.SNAPCHAT: SnapchatPlatform,
    PlatformType.DISCORD: DiscordPlatform,
    PlatformType.TELEGRAM: TelegramPlatform,
    
    # Extended platforms for complete ecosystem coverage
    PlatformType.WHATSAPP: WhatsAppPlatform,
    PlatformType.VIMEO: VimeoPlatform,
    PlatformType.CLUBHOUSE: ClubhousePlatform,
    PlatformType.MEDIUM: MediumPlatform,
    PlatformType.MASTODON: MastodonPlatform,
    PlatformType.BEREAL: BeRealPlatform,
    PlatformType.ONLYFANS: OnlyFansPlatform,
    PlatformType.PATREON: PatreonPlatform,
    PlatformType.SUBSTACK: SubstackPlatform,
    PlatformType.THREADS: ThreadsPlatform,
    PlatformType.KICK: KickPlatform,
    PlatformType.RUMBLE: RumblePlatform
}

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus,
    PlatformCredentials, PlatformManager
)

from .spotify import SpotifyPlatform
from .youtube import YouTubePlatform
from .instagram import InstagramPlatform
from .tiktok import TikTokPlatform
from .twitter import TwitterPlatform
from .facebook import FacebookPlatform
from .twitch import TwitchPlatform
from .soundcloud import SoundCloudPlatform
from .apple_music import AppleMusicPlatform
from .bandcamp import BandcampPlatform
from .reddit import RedditPlatform
from .linkedin import LinkedInPlatform
from .pinterest import PinterestPlatform
from .snapchat import SnapchatPlatform
from .discord import DiscordPlatform
from .telegram import TelegramPlatform

from .distributor import PlatformDistributor, DistributionStrategy
from .aggregator import PlatformAggregator
from .monitor import PlatformMonitor, MonitorSeverity, MonitorStatus, HealthCheckResult, MonitorAlert
from .connector import PlatformConnector, PlatformConnectionPool, ConnectionState, get_connector, cleanup_connector

__all__ = [
    # Base classes
    'PlatformBase', 'PlatformConfig', 'PlatformType', 'ContentType',
    'ContentMetadata', 'UploadResult', 'AnalyticsData', 'PlatformStatus',
    'PlatformCredentials', 'PlatformManager',
    
    # Platform implementations
    'SpotifyPlatform', 'YouTubePlatform', 'InstagramPlatform', 'TikTokPlatform',
    'TwitterPlatform', 'FacebookPlatform', 'TwitchPlatform', 'SoundCloudPlatform',
    'AppleMusicPlatform', 'BandcampPlatform', 'RedditPlatform', 'LinkedInPlatform',
    'PinterestPlatform', 'SnapchatPlatform', 'DiscordPlatform', 'TelegramPlatform',
    
    # Core modules
    'PlatformDistributor', 'DistributionStrategy', 'PlatformAggregator',
    'PlatformMonitor', 'MonitorSeverity', 'MonitorStatus', 'HealthCheckResult', 'MonitorAlert',
    'PlatformConnector', 'PlatformConnectionPool', 'ConnectionState', 'get_connector', 'cleanup_connector'
]

from .base import PlatformBase, PlatformManager
from .spotify import SpotifyPlatform
from .youtube import YouTubePlatform
from .instagram import InstagramPlatform
from .tiktok import TikTokPlatform
from .twitter import TwitterPlatform
from .facebook import FacebookPlatform
from .twitch import TwitchPlatform
from .soundcloud import SoundCloudPlatform
from .bandcamp import BandcampPlatform
from .apple_music import AppleMusicPlatform
from .distributor import PlatformDistributor
from .aggregator import PlatformAggregator
from .monitor import PlatformMonitor
from .connector import PlatformConnector

__all__ = [
    'PlatformBase',
    'PlatformManager',
    'SpotifyPlatform',
    'YouTubePlatform',
    'InstagramPlatform',
    'TikTokPlatform',
    'TwitterPlatform',
    'FacebookPlatform',
    'TwitchPlatform',
    'SoundCloudPlatform',
    'BandcampPlatform',
    'AppleMusicPlatform',
    'PlatformDistributor',
    'PlatformAggregator',
    'PlatformMonitor',
    'PlatformConnector'
]
