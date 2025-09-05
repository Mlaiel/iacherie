"""Social Media Collector
======================

Consolidated social media collector combining functionality from:
- Instagram (posts, stories, reels, analytics)
- TikTok (videos, trending, analytics)
- Twitter (tweets, trends, analytics)
- Facebook (posts, pages, groups, analytics)
- LinkedIn (posts, articles, company pages, analytics)

This module consolidates 5 individual platform collectors into a unified
social media monitoring solution for creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
from datetime import datetime, timedelta

from .base_collector import BaseCollector, CollectorResult, CollectionConfig
from .instagram import InstagramCollector
from .tiktok import TikTokCollector
from .twitter import TwitterCollector
from .facebook import FacebookCollector
from .linkedin import LinkedInCollector

logger = logging.getLogger(__name__)

class SocialMediaCollector(BaseCollector):
    """
    Unified social media collector for comprehensive cross-platform monitoring.
    
    Consolidates Instagram, TikTok, Twitter, Facebook, and LinkedIn collectors
    into a single interface for efficient social media content collection.
    """
    
    def __init__(self, platform_configs: Optional[Dict[str, Dict]] = None):
        """Initialize with platform-specific configurations."""
        super().__init__("social_media", rate_limit=200)
        
        # Initialize individual platform collectors
        configs = platform_configs or {}
        
        self.instagram = InstagramCollector(**configs.get('instagram', {}))
        self.tiktok = TikTokCollector(**configs.get('tiktok', {}))
        self.twitter = TwitterCollector(**configs.get('twitter', {}))
        self.facebook = FacebookCollector(**configs.get('facebook', {}))
        self.linkedin = LinkedInCollector(**configs.get('linkedin', {}))
        
        self.collectors = {
            'instagram': self.instagram,
            'tiktok': self.tiktok,
            'twitter': self.twitter,
            'facebook': self.facebook,
            'linkedin': self.linkedin
        }
        
        logger.info("Initialized unified social media collector")
    
    async def search_content(self, query: str, config: CollectionConfig, 
                           platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Search content across all or specified social media platforms.
        
        Args:
            query: Search query
            config: Collection configuration
            platforms: List of platforms to search (default: all)
            
        Returns:
            List of collected content from all platforms
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        tasks = []
        
        # Create search tasks for each platform
        for platform in platforms:
            if platform in self.collectors:
                task = self.collectors[platform].search_content(query, config)
                tasks.append((platform, task))
        
        # Execute searches concurrently
        for platform, task in tasks:
            try:
                platform_results = await task
                results.extend(platform_results)
                logger.info(f"Collected {len(platform_results)} results from {platform}")
            except Exception as e:
                logger.error(f"Search failed for {platform}: {e}")
        
        return results
    
    async def get_content_details(self, content_id: str, platform: str = None) -> Optional[CollectorResult]:
        """
        Get detailed information about specific content.
        
        Args:
            content_id: ID of content to retrieve
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Detailed content information
        """
        if platform and platform in self.collectors:
            return await self.collectors[platform].get_content_details(content_id)
        
        # Try all platforms if platform not specified
        for platform_name, collector in self.collectors.items():
            try:
                result = await collector.get_content_details(content_id)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Content not found on {platform_name}: {e}")
        
        return None
    
    async def get_user_content(self, user_id: str, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get content from specific user across platforms.
        
        Args:
            user_id: User/creator identifier
            config: Collection configuration
            platforms: List of platforms to search
            
        Returns:
            List of user content from all platforms
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        tasks = []
        
        for platform in platforms:
            if platform in self.collectors:
                task = self.collectors[platform].get_user_content(user_id, config)
                tasks.append((platform, task))
        
        for platform, task in tasks:
            try:
                platform_results = await task
                results.extend(platform_results)
            except Exception as e:
                logger.error(f"User content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor hashtags across social media platforms in real-time.
        
        Args:
            hashtags: List of hashtags to monitor
            config: Collection configuration
            platforms: List of platforms to monitor
            
        Yields:
            Real-time content matching hashtags
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        # Create async generators for each platform
        generators = []
        for platform in platforms:
            if platform in self.collectors:
                try:
                    gen = self.collectors[platform].monitor_hashtags(hashtags, config)
                    generators.append(gen)
                except Exception as e:
                    logger.error(f"Hashtag monitoring failed for {platform}: {e}")
        
        # Yield results from all generators as they become available
        while generators:
            for i, gen in enumerate(generators[:]):
                try:
                    result = await gen.__anext__()
                    yield result
                except StopAsyncIteration:
                    generators.remove(gen)
                except Exception as e:
                    logger.error(f"Hashtag monitoring error: {e}")
                    generators.remove(gen)
    
    async def get_trending_content(self, config: CollectionConfig,
                                 platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get trending content across social media platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of trending content from all platforms
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        tasks = []
        
        for platform in platforms:
            if platform in self.collectors:
                task = self.collectors[platform].get_trending_content(config)
                tasks.append((platform, task))
        
        for platform, task in tasks:
            try:
                platform_results = await task
                results.extend(platform_results)
            except Exception as e:
                logger.error(f"Trending content collection failed for {platform}: {e}")
        
        return results
    
    async def analyze_cross_platform_presence(self, creator_id: str) -> Dict[str, Any]:
        """
        Analyze creator's presence across all social media platforms.
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Cross-platform analytics and insights
        """
        presence_data = {}
        
        for platform_name, collector in self.collectors.items():
            try:
                # Get creator content from each platform
                config = CollectionConfig(max_results=20)
                content = await collector.get_user_content(creator_id, config)
                
                presence_data[platform_name] = {
                    'content_count': len(content),
                    'latest_post': content[0].timestamp if content else None,
                    'engagement_total': sum(
                        result.engagement_metrics.get('total_engagement', 0) 
                        for result in content 
                        if result.engagement_metrics
                    ),
                    'active': len(content) > 0
                }
            except Exception as e:
                logger.error(f"Cross-platform analysis failed for {platform_name}: {e}")
                presence_data[platform_name] = {'error': str(e), 'active': False}
        
        return {
            'creator_id': creator_id,
            'platforms': presence_data,
            'total_platforms': len([p for p in presence_data.values() if p.get('active', False)]),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def detect_viral_content(self, threshold_multiplier: float = 2.0) -> List[CollectorResult]:
        """
        Detect potentially viral content across platforms.
        
        Args:
            threshold_multiplier: Multiplier for viral detection threshold
            
        Returns:
            List of potentially viral content
        """
        viral_content = []
        
        for platform_name, collector in self.collectors.items():
            try:
                # Get trending content and analyze engagement
                config = CollectionConfig(max_results=50)
                trending = await collector.get_trending_content(config)
                
                for content in trending:
                    if content.engagement_metrics:
                        engagement = content.engagement_metrics.get('total_engagement', 0)
                        views = content.engagement_metrics.get('views', 0)
                        
                        # Simple viral detection based on engagement rate
                        if views > 0:
                            engagement_rate = engagement / views
                            if engagement_rate > (0.05 * threshold_multiplier):  # 5% base rate
                                viral_content.append(content)
                
            except Exception as e:
                logger.error(f"Viral detection failed for {platform_name}: {e}")
        
        # Sort by engagement rate
        viral_content.sort(
            key=lambda x: x.engagement_metrics.get('total_engagement', 0) / 
                         max(x.engagement_metrics.get('views', 1), 1), 
            reverse=True
        )
        
        return viral_content
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all social media platform collectors."""
        status = {
            'unified_collector': {
                'status': self.status.value,
                'total_collected': self.total_collected,
                'stats': self.stats
            },
            'platforms': {}
        }
        
        for platform_name, collector in self.collectors.items():
            status['platforms'][platform_name] = collector.get_platform_info()
        
        return status