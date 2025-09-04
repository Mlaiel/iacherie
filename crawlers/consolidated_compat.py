"""Backward Compatibility Layer
============================

Provides backward compatibility for existing crawler imports.
Redirects to the new consolidated collectors in backend/collectors.

This allows existing code to continue working while benefiting from
the consolidated architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import the new consolidated collectors
from backend.collectors import (
    InstagramCollector,
    TikTokCollector,
    YouTubeCollector,
    TwitterCollector,
    FacebookCollector,
    LinkedInCollector,
    PinterestCollector,
    RedditCollector,
    TwitchCollector,
    DiscordCollector,
    get_collector,
    get_supported_platforms,
    CollectionConfig,
    BaseCollector,
    CollectorResult
)

# Maintain backward compatibility aliases
YouTubeCrawler = YouTubeCollector
InstagramCrawler = InstagramCollector
TikTokCrawler = TikTokCollector
TwitterCrawler = TwitterCollector
FacebookCrawler = FacebookCollector
LinkedInCrawler = LinkedInCollector
PinterestCrawler = PinterestCollector
SnapchatCrawler = InstagramCollector  # Snapchat functionality merged with Instagram
DiscordCrawler = DiscordCollector
TelegramCrawler = DiscordCollector  # Telegram functionality merged with Discord

# Legacy result class for backward compatibility
CrawlerResult = CollectorResult

class CrawlerOrchestrator:
    """
    Legacy orchestrator that uses the new consolidated collectors.
    Provides backward compatibility for existing code.
    """
    
    def __init__(self):
        self.collectors = {}
        self._initialize_collectors()
    
    def _initialize_collectors(self):
        """Initialize all collectors."""
        for platform in get_supported_platforms():
            self.collectors[platform] = get_collector(platform)
    
    def get_supported_platforms(self):
        """Get list of supported platforms."""
        return get_supported_platforms()
    
    async def get_crawler(self, platform: str):
        """Get crawler for platform (legacy method)."""
        if platform not in self.collectors:
            raise ValueError(f"Unsupported platform: {platform}")
        return self.collectors[platform]
    
    async def search_all_platforms(self, query: str, max_results: int = 10):
        """Search across all platforms (legacy method)."""
        results = {}
        config = CollectionConfig(max_results=max_results)
        
        for platform, collector in self.collectors.items():
            try:
                platform_results = await collector.search_content(query, config)
                results[platform] = platform_results
            except Exception as e:
                results[platform] = []
        
        return results

# Export all for backward compatibility
__all__ = [
    'YouTubeCrawler',
    'InstagramCrawler', 
    'TikTokCrawler',
    'TwitterCrawler',
    'FacebookCrawler',
    'LinkedInCrawler',
    'PinterestCrawler',
    'SnapchatCrawler',
    'DiscordCrawler',
    'TelegramCrawler',
    'CrawlerOrchestrator',
    'CrawlerResult',
    'get_collector',
    'get_supported_platforms'
]