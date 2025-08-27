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

__all__ = [
    "YouTubeCrawler",
    "TikTokCrawler",
    "InstagramCrawler", 
    "TwitterCrawler",
    "GenericWebCrawler",
    "CrawlerManager"
]