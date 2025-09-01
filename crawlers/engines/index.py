"""Crawling Engines Index

Professional index module for IA Influencer Agent crawling engines.
Provides centralized access to all platform-specific crawling engines.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. 
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

from typing import Dict, Type, List, Optional, Any
import logging

# Import all engines
from . import (
    # Core video platforms
    YouTubeCrawlerEngine,
    VimeoEngine,
    RumbleEngine,
    
    # Social media platforms
    FacebookCrawlerEngine,
    InstagramCrawlerEngine,
    TwitterCrawlerEngine,
    ThreadsEngine,
    SnapchatEngine,
    
    # Professional platforms
    LinkedInCrawlerEngine,
    
    # Music platforms
    SpotifyCrawlerEngine,
    AppleMusicEngine,
    SoundCloudEngine,
    BandcampEngine,
    
    # Content creation platforms
    TikTokCrawlerEngine,
    OnlyFansEngine,
    PatreonEngine,
    PinterestEngine,
    
    # Communication platforms
    DiscordCrawlerEngine,
    TelegramCrawlerEngine,
    WhatsAppEngine,
    
    # Alternative platforms
    MastodonEngine,
    RedditEngine,
    MediumEngine,
    SubstackEngine,
    
    # Gaming/Streaming
    TwitchCrawlerEngine,
    KickEngine,
    
    # Emerging platforms
    BeRealEngine,
    ClubhouseEngine,
    
    # Generic engine
    GenericWebCrawlerEngine
)

logger = logging.getLogger(__name__)


class EngineRegistry:
    """
    Registry for all crawling engines with advanced discovery and management capabilities.
    """
    
    def __init__(self):
        self._engines: Dict[str, Type] = {}
        self._categories: Dict[str, List[str]] = {}
        self._initialize_registry()
        
    def _initialize_registry(self):
        """
Initialize the engine registry with all available engines"""
        
        # Video platforms
        self._engines.update({
            'youtube': YouTubeCrawlerEngine,
            'vimeo': VimeoEngine,
            'rumble': RumbleEngine
        })
        
        # Social media platforms
        self._engines.update({
            'facebook': FacebookCrawlerEngine,
            'instagram': InstagramCrawlerEngine,
            'twitter': TwitterCrawlerEngine,
            'threads': ThreadsEngine,
            'snapchat': SnapchatEngine,
            'tiktok': TikTokCrawlerEngine
        })
        
        # Professional platforms
        self._engines.update({
            'linkedin': LinkedInCrawlerEngine
        })
        
        # Music platforms
        self._engines.update({
            'spotify': SpotifyCrawlerEngine,
            'apple_music': AppleMusicEngine,
            'soundcloud': SoundCloudEngine,
            'bandcamp': BandcampEngine
        })
        
        # Content creation platforms
        self._engines.update({
            'onlyfans': OnlyFansEngine,
            'patreon': PatreonEngine,
            'pinterest': PinterestEngine
        })
        
        # Communication platforms
        self._engines.update({
            'discord': DiscordCrawlerEngine,
            'telegram': TelegramCrawlerEngine,
            'whatsapp': WhatsAppEngine
        })
        
        # Alternative platforms
        self._engines.update({
            'mastodon': MastodonEngine,
            'reddit': RedditEngine,
            'medium': MediumEngine,
            'substack': SubstackEngine
        })
        
        # Gaming/Streaming
        self._engines.update({
            'twitch': TwitchCrawlerEngine,
            'kick': KickEngine
        })
        
        # Emerging platforms
        self._engines.update({
            'bereal': BeRealEngine,
            'clubhouse': ClubhouseEngine
        })
        
        # Generic engine
        self._engines.update({
            'generic': GenericWebCrawlerEngine
        })
        
        # Initialize categories
        self._initialize_categories()
        
    def _initialize_categories(self):
        """
Initialize engine categories for easy discovery"""
        
        self._categories = {
            'video': ['youtube', 'vimeo', 'rumble', 'tiktok'],
            'social': ['facebook', 'instagram', 'twitter', 'threads', 'snapchat'],
            'professional': ['linkedin'],
            'music': ['spotify', 'apple_music', 'soundcloud', 'bandcamp'],
            'content_creation': ['onlyfans', 'patreon', 'pinterest'],
            'communication': ['discord', 'telegram', 'whatsapp'],
            'alternative': ['mastodon', 'reddit', 'medium', 'substack'],
            'gaming': ['twitch', 'kick'],
            'emerging': ['bereal', 'clubhouse'],
            'monetization': ['onlyfans', 'patreon', 'spotify', 'youtube'],
            'ephemeral': ['snapchat', 'bereal'],
            'long_form': ['youtube', 'vimeo', 'medium', 'substack'],
            'real_time': ['twitter', 'threads', 'discord', 'twitch']
        }
        
    def get_engine(self, platform: str) -> Optional[Type]:
        """
        Get engine class for a specific platform
        
        Args:
            platform: Platform name (e.g., 'youtube', 'instagram')
            
        Returns:
            Engine class or None if not found
        """
        return self._engines.get(platform.lower())
        
    def list_engines(self) -> List[str]:
        """
List all available engine platforms"""
        return list(self._engines.keys())
        
    def list_categories(self) -> List[str]:
        """
List all available categories"""
        return list(self._categories.keys())
        
    def get_engines_by_category(self, category: str) -> List[str]:
        """
        Get engines by category
        
        Args:
            category: Category name (e.g., 'video', 'social')
            
        Returns:
            List of engine platform names
        """
        return self._categories.get(category, [])
        
    def get_engine_categories(self, platform: str) -> List[str]:
        """
        Get categories for a specific platform
        
        Args:
            platform: Platform name
            
        Returns:
            List of categories this platform belongs to
        """
        categories = []
        for category, platforms in self._categories.items():
            if platform.lower() in platforms:
                categories.append(category)
        return categories
        
    def search_engines(self, query: str) -> List[str]:
        """
        Search engines by name or category
        
        Args:
            query: Search query
            
        Returns:
            List of matching engine platform names
        """
        query_lower = query.lower()
        matches = []
        
        # Search by platform name
        for platform in self._engines.keys():
            if query_lower in platform.lower():
                matches.append(platform)
                
        # Search by category
        for category, platforms in self._categories.items():
            if query_lower in category.lower():
                matches.extend(platforms)
                
        return list(set(matches))  # Remove duplicates
        
    def register_engine(self, platform: str, engine_class: Type, categories: List[str] = None):
        """
        Register a new engine
        
        Args:
            platform: Platform name
            engine_class: Engine class
            categories: List of categories for this engine
        """
        self._engines[platform.lower()] = engine_class
        
        if categories:
            for category in categories:
                if category not in self._categories:
                    self._categories[category] = []
                if platform.lower() not in self._categories[category]:
                    self._categories[category].append(platform.lower())
                    
        logger.info(f"Registered engine for platform: {platform}")
        
    def unregister_engine(self, platform: str):
        """
        Unregister an engine
        
        Args:
            platform: Platform name to remove
        """
        platform_lower = platform.lower()
        
        if platform_lower in self._engines:
            del self._engines[platform_lower]
            
            # Remove from categories
            for category in self._categories:
                if platform_lower in self._categories[category]:
                    self._categories[category].remove(platform_lower)
                    
            logger.info(f"Unregistered engine for platform: {platform}")
            
    def get_engine_info(self, platform: str) -> Dict[str, Any]:
        """
        Get comprehensive information about an engine
        
        Args:
            platform: Platform name
            
        Returns:
            Dictionary with engine information
        """
        engine_class = self.get_engine(platform)
        if not engine_class:
            return {}
            
        return {
            'platform': platform,
            'class': engine_class.__name__,
            'module': engine_class.__module__,
            'categories': self.get_engine_categories(platform),
            'docstring': engine_class.__doc__,
            'available': True
        }
        
    def validate_engines(self) -> Dict[str, bool]:
        """
        Validate all registered engines
        
        Returns:
            Dictionary with validation results for each engine
        """
        validation_results = {}
        
        for platform, engine_class in self._engines.items():
            try:
                # Basic validation - check if class can be instantiated
                # (with empty config for validation)
                engine_class({})
                validation_results[platform] = True
            except Exception as e:
                logger.error(f"Engine validation failed for {platform}: {str(e)}")
                validation_results[platform] = False
                
        return validation_results
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics
        
        Returns:
            Dictionary with registry statistics
        """
        return {
            'total_engines': len(self._engines),
            'total_categories': len(self._categories),
            'engines_per_category': {
                category: len(platforms)
                for category, platforms in self._categories.items()
            },
            'most_popular_category': max(
                self._categories.items(),
                key=lambda x: len(x[1]),
                default=('none', [])
            )[0],
            'available_platforms': list(self._engines.keys())
        }


# Global registry instance
engine_registry = EngineRegistry()

# Convenience functions
def get_engine(platform: str) -> Optional[Type]:
    """
Get engine class for platform"""
    return engine_registry.get_engine(platform)

def list_engines() -> List[str]:
    """
List all available engines"""
    return engine_registry.list_engines()

def get_engines_by_category(category: str) -> List[str]:
    """
Get engines by category"""
    return engine_registry.get_engines_by_category(category)

def search_engines(query: str) -> List[str]:
    """
Search engines by query"""
    return engine_registry.search_engines(query)

def get_engine_info(platform: str) -> Dict[str, Any]:
    """
Get engine information"""
    return engine_registry.get_engine_info(platform)

def validate_engines() -> Dict[str, bool]:
    """
Validate all engines"""
    return engine_registry.validate_engines()

def get_registry_statistics() -> Dict[str, Any]:
    """
Get registry statistics"""
    return engine_registry.get_statistics()


# Export all functions
__all__ = [
    'EngineRegistry',
    'engine_registry',
    'get_engine',
    'list_engines',
    'get_engines_by_category',
    'search_engines',
    'get_engine_info',
    'validate_engines',
    'get_registry_statistics'
]
