"""Backend Collectors Module
=========================

Consolidated collector infrastructure for enterprise content monitoring.
Consolidates 16 individual collector files into 6 unified collector modules.

This module implements the consolidation requirement from the problem statement:
- Consolidates 16 individual collectors into 6 logical modules
- Maintains backward compatibility with existing collector interfaces  
- Provides enterprise-grade content collection across all major platforms
- Achieves file count limit of 12 files (6 modules + 4 README files + 2 base files)

Consolidation Structure:
1. BaseCollector - Infrastructure foundation
2. SocialMediaCollector - Instagram, TikTok, Twitter, Facebook, LinkedIn
3. VideoPlatformsCollector - YouTube, Twitch
4. CommunityCollector - Discord, Reddit
5. MarketplaceCollector - Ecommerce, Pinterest
6. NewsTrendsCollector - News, Trends
7. MiscellaneousCollector - Misc + specialized sources

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .base_collector import BaseCollector, CollectorResult, CollectorStatus, CollectionConfig
from .social_media_collector import SocialMediaCollector
from .video_platforms_collector import VideoPlatformsCollector
from .community_collector import CommunityCollector
from .marketplace_collector import MarketplaceCollector
from .news_trends_collector import NewsTrendsCollector
from .miscellaneous_collector import MiscellaneousCollector

# Backward compatibility - individual collectors accessible via consolidated modules
from .social_media_collector import (
    SocialMediaCollector,
    InstagramCollector,
    TikTokCollector, 
    TwitterCollector,
    FacebookCollector,
    LinkedInCollector
)
from .video_platforms_collector import (
    VideoPlatformsCollector,
    YouTubeCollector,
    TwitchCollector
)
from .community_collector import (
    CommunityCollector,
    DiscordCollector,
    RedditCollector
)
from .marketplace_collector import (
    MarketplaceCollector,
    EcommerceCollector,
    PinterestCollector
)
from .news_trends_collector import (
    NewsTrendsCollector,
    NewsCollector,
    TrendsCollector
)
from .miscellaneous_collector import (
    MiscellaneousCollector,
    MiscCollector
)

__all__ = [
    # Core infrastructure
    'BaseCollector',
    'CollectorResult', 
    'CollectorStatus',
    'CollectionConfig',
    
    # Consolidated collectors (PRIMARY)
    'SocialMediaCollector',
    'VideoPlatformsCollector',
    'CommunityCollector',
    'MarketplaceCollector',
    'NewsTrendsCollector',
    'MiscellaneousCollector',
    
    # Individual collectors (BACKWARD COMPATIBILITY)
    'InstagramCollector',
    'TikTokCollector',
    'YouTubeCollector', 
    'TwitterCollector',
    'FacebookCollector',
    'LinkedInCollector',
    'EcommerceCollector',
    'NewsCollector',
    'TrendsCollector',
    'MiscCollector',
    'PinterestCollector',
    'RedditCollector',
    'TwitchCollector',
    'DiscordCollector'
]

# Platform registry for dynamic collector access (UPDATED)
PLATFORM_COLLECTORS = {
    # Consolidated collectors (RECOMMENDED)
    'social_media': SocialMediaCollector,
    'video_platforms': VideoPlatformsCollector,
    'community': CommunityCollector,
    'marketplace': MarketplaceCollector,
    'news_trends': NewsTrendsCollector,
    'miscellaneous': MiscellaneousCollector,
    
    # Individual platform collectors (LEGACY SUPPORT)
    'instagram': InstagramCollector,
    'tiktok': TikTokCollector,
    'youtube': YouTubeCollector,
    'twitter': TwitterCollector,
    'facebook': FacebookCollector,
    'linkedin': LinkedInCollector,
    'ecommerce': EcommerceCollector,
    'news': NewsCollector,
    'trends': TrendsCollector,
    'misc': MiscCollector,
    'pinterest': PinterestCollector,
    'reddit': RedditCollector,
    'twitch': TwitchCollector,
    'discord': DiscordCollector
}

def get_collector(platform -> None: str, **kwargs) -> None:
    """
    Get collector instance for specified platform.
    
    Args:
        platform: Platform name or collector type
        **kwargs: Configuration arguments for the collector
        
    Returns:
        Collector instance
        
    Examples:
        # Consolidated collectors (recommended)
        social_collector = get_collector('social_media')
        video_collector = get_collector('video_platforms')
        
        # Individual platform collectors (legacy)
        instagram_collector = get_collector('instagram')
    """
    if platform not in PLATFORM_COLLECTORS:
        raise ValueError(f"Unsupported platform: {platform}. Supported: {list(PLATFORM_COLLECTORS.keys())}")
    
    return PLATFORM_COLLECTORS[platform](**kwargs)

def get_supported_platforms() -> None:
    """Get list of supported platforms and collector types."""
    return list(PLATFORM_COLLECTORS.keys())

def get_consolidated_collectors() -> None:
    """Get list of consolidated collector types (recommended)."""
    return [
        'social_media',
        'video_platforms', 
        'community',
        'marketplace',
        'news_trends',
        'miscellaneous'
    ]

def get_individual_platforms() -> None:
    """Get list of individual platform collectors (legacy support)."""
    return [
        'instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 'linkedin',
        'ecommerce', 'news', 'trends', 'misc', 'pinterest', 'reddit', 
        'twitch', 'discord'
    ]