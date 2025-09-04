"""Backend Collectors Module
=========================

Consolidated collector infrastructure for enterprise content monitoring.
Consolidates 117+ individual crawlers into 10 organized collector modules.

This module implements the consolidation requirement from the problem statement:
- Consolidates scattered crawler functionality into organized modules
- Maintains backward compatibility with existing crawler interfaces
- Provides enterprise-grade content collection across all major platforms

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .base_collector import BaseCollector, CollectorResult, CollectorStatus, CollectionConfig
from .instagram import InstagramCollector
from .tiktok import TikTokCollector
from .youtube import YouTubeCollector
from .twitter import TwitterCollector
from .facebook import FacebookCollector
from .linkedin import LinkedInCollector
from .ecommerce import EcommerceCollector
from .news import NewsCollector
from .trends import TrendsCollector
from .misc import MiscCollector
# Keep the existing collectors that are not mentioned in the problem statement
from .pinterest_collector import PinterestCollector
from .reddit_collector import RedditCollector
from .twitch_collector import TwitchCollector
from .discord_collector import DiscordCollector

__all__ = [
    'BaseCollector',
    'CollectorResult', 
    'CollectorStatus',
    'CollectionConfig',
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

# Platform registry for dynamic collector access
PLATFORM_COLLECTORS = {
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

def get_collector(platform: str, **kwargs):
    """Get collector instance for specified platform."""
    if platform not in PLATFORM_COLLECTORS:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return PLATFORM_COLLECTORS[platform](**kwargs)

def get_supported_platforms():
    """Get list of supported platforms."""
    return list(PLATFORM_COLLECTORS.keys())