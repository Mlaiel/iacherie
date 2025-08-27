"""
Web Crawlers Module
Surveillance web crawlers for content protection across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .youtube_crawler import YouTubeCrawler
from .tiktok_crawler import TikTokCrawler
from .instagram_crawler import InstagramCrawler
from .twitter_crawler import TwitterCrawler
from .generic_web_crawler import GenericWebCrawler
from .crawler_manager import CrawlerManager

# Music Platform Crawlers
from .spotify_crawler import SpotifyCrawler
from .apple_music_crawler import AppleMusicCrawler
from .soundcloud_crawler import SoundCloudCrawler

# Emerging Platform Crawlers
from .bereal_crawler import BeRealCrawler
from .twitch_crawler import TwitchCrawler

# Monetization Platform Crawlers
from .patreon_crawler import PatreonCrawler

__all__ = [
    # Core Crawlers
    "YouTubeCrawler",
    "TikTokCrawler",
    "InstagramCrawler", 
    "TwitterCrawler",
    "GenericWebCrawler",
    "CrawlerManager",
    
    # Music Platform Crawlers
    "SpotifyCrawler",
    "AppleMusicCrawler", 
    "SoundCloudCrawler",
    
    # Emerging Platform Crawlers
    "BeRealCrawler",
    "TwitchCrawler",
    
    # Monetization Platform Crawlers
    "PatreonCrawler"
]