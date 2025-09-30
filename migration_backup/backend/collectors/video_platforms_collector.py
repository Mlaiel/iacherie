"""Video Platforms Collector
=========================

Consolidated video platforms collector combining functionality from:
- YouTube (videos, channels, playlists, analytics, live streams)
- Twitch (streams, clips, VODs, analytics, chat)
- Other video platforms (future expansion)

This module consolidates video platform collectors into a unified
video content monitoring solution for creators and streamers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
from datetime import datetime, timedelta

from base_collector import BaseCollector, CollectorResult, CollectionConfig

logger = logging.getLogger(__name__)

# Individual platform collector classes (simplified implementations)
class YouTubeCollector(BaseCollector):
    """YouTube content collector."""
    def __init__(self, **kwargs):
        super().__init__("youtube", rate_limit=100)
    
    async def search_content(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def get_content_details(self, content_id: str) -> Optional[CollectorResult]:
        return None
    async def get_user_content(self, user_id: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig) -> AsyncGenerator[CollectorResult, None]:
        return
        yield
    async def get_trending_content(self, config: CollectionConfig) -> List[CollectorResult]:
        return []

class TwitchCollector(BaseCollector):
    """Twitch content collector."""
    def __init__(self, **kwargs):
        super().__init__("twitch", rate_limit=50)
    
    async def search_content(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def get_content_details(self, content_id: str) -> Optional[CollectorResult]:
        return None
    async def get_user_content(self, user_id: str, config: CollectionConfig) -> List[CollectorResult]:
        return []
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig) -> AsyncGenerator[CollectorResult, None]:
        return
        yield
    async def get_trending_content(self, config: CollectionConfig) -> List[CollectorResult]:
        return []

class VideoPlatformsCollector(BaseCollector):
    """
    Unified video platforms collector for comprehensive streaming content monitoring.
    
    Consolidates YouTube, Twitch, and other video platform collectors
    into a single interface for efficient video content collection.
    """
    
    def __init__(self, platform_configs: Optional[Dict[str, Dict]] = None):
        """Initialize with platform-specific configurations."""
        super().__init__("video_platforms", rate_limit=150)
        
        # Initialize individual platform collectors
        configs = platform_configs or {}
        
        self.youtube = YouTubeCollector(**configs.get('youtube', {}))
        self.twitch = TwitchCollector(**configs.get('twitch', {}))
        
        self.collectors = {
            'youtube': self.youtube,
            'twitch': self.twitch
        }
        
        logger.info("Initialized unified video platforms collector")
    
    async def search_content(self, query: str, config: CollectionConfig,
                           platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Search video content across all or specified platforms.
        
        Args:
            query: Search query
            config: Collection configuration
            platforms: List of platforms to search (default: all)
            
        Returns:
            List of collected video content from all platforms
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
                logger.info(f"Collected {len(platform_results)} video results from {platform}")
            except Exception as e:
                logger.error(f"Video search failed for {platform}: {e}")
        
        return results
    
    async def get_content_details(self, content_id: str, platform: str = None) -> Optional[CollectorResult]:
        """
        Get detailed information about specific video content.
        
        Args:
            content_id: ID of video content to retrieve
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Detailed video content information
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
                logger.debug(f"Video content not found on {platform_name}: {e}")
        
        return None
    
    async def get_user_content(self, user_id: str, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get video content from specific creator across platforms.
        
        Args:
            user_id: Creator/channel identifier
            config: Collection configuration
            platforms: List of platforms to search
            
        Returns:
            List of creator video content from all platforms
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
                logger.error(f"Creator video content collection failed for {platform}: {e}")
        
        return results
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor hashtags in video content across platforms in real-time.
        
        Args:
            hashtags: List of hashtags to monitor
            config: Collection configuration
            platforms: List of platforms to monitor
            
        Yields:
            Real-time video content matching hashtags
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
                    logger.error(f"Video hashtag monitoring failed for {platform}: {e}")
        
        # Yield results from all generators as they become available
        while generators:
            for i, gen in enumerate(generators[:]):
                try:
                    result = await gen.__anext__()
                    yield result
                except StopAsyncIteration:
                    generators.remove(gen)
                except Exception as e:
                    logger.error(f"Video hashtag monitoring error: {e}")
                    generators.remove(gen)
    
    async def get_trending_content(self, config: CollectionConfig,
                                 platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get trending video content across platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of trending video content from all platforms
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
                logger.error(f"Trending video content collection failed for {platform}: {e}")
        
        return results
    
    async def get_live_streams(self, config: CollectionConfig,
                             platforms: Optional[List[str]] = None) -> List[CollectorResult]:
        """
        Get currently live streams across video platforms.
        
        Args:
            config: Collection configuration
            platforms: List of platforms to check
            
        Returns:
            List of currently live streams
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
        
        results = []
        
        for platform in platforms:
            if platform in self.collectors:
                try:
                    # Get live content from each platform
                    live_content = await self.collectors[platform].get_trending_content(config)
                    
                    # Filter for live streams
                    live_streams = [
                        content for content in live_content
                        if content.metadata.get('is_live', False) or 
                           content.content_type.lower() in ['live', 'stream']
                    ]
                    
                    results.extend(live_streams)
                    logger.info(f"Found {len(live_streams)} live streams on {platform}")
                    
                except Exception as e:
                    logger.error(f"Live streams collection failed for {platform}: {e}")
        
        return results
    
    async def analyze_video_performance(self, video_id: str, platform: str = None) -> Dict[str, Any]:
        """
        Analyze video performance metrics across platforms.
        
        Args:
            video_id: Video identifier
            platform: Specific platform (auto-detect if None)
            
        Returns:
            Comprehensive video performance analytics
        """
        performance_data = {}
        
        platforms_to_check = [platform] if platform else list(self.collectors.keys())
        
        for platform_name in platforms_to_check:
            if platform_name in self.collectors:
                try:
                    # Get video details
                    video_data = await self.collectors[platform_name].get_content_details(video_id)
                    
                    if video_data:
                        performance_data[platform_name] = {
                            'views': video_data.engagement_metrics.get('views', 0) if video_data.engagement_metrics else 0,
                            'likes': video_data.engagement_metrics.get('likes', 0) if video_data.engagement_metrics else 0,
                            'comments': video_data.engagement_metrics.get('comments', 0) if video_data.engagement_metrics else 0,
                            'shares': video_data.engagement_metrics.get('shares', 0) if video_data.engagement_metrics else 0,
                            'duration': video_data.metadata.get('duration', 0),
                            'upload_date': video_data.timestamp,
                            'engagement_rate': self._calculate_engagement_rate(video_data),
                            'platform_specific': video_data.metadata
                        }
                        
                        # YouTube-specific metrics
                        if platform_name == 'youtube':
                            performance_data[platform_name].update({
                                'watch_time': video_data.metadata.get('watch_time', 0),
                                'retention_rate': video_data.metadata.get('retention_rate', 0),
                                'subscriber_growth': video_data.metadata.get('subscriber_growth', 0)
                            })
                        
                        # Twitch-specific metrics
                        elif platform_name == 'twitch':
                            performance_data[platform_name].update({
                                'peak_viewers': video_data.metadata.get('peak_viewers', 0),
                                'average_viewers': video_data.metadata.get('average_viewers', 0),
                                'follower_growth': video_data.metadata.get('follower_growth', 0)
                            })
                
                except Exception as e:
                    logger.error(f"Video performance analysis failed for {platform_name}: {e}")
                    performance_data[platform_name] = {'error': str(e)}
        
        return {
            'video_id': video_id,
            'platforms': performance_data,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def track_creator_growth(self, creator_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Track creator growth metrics across video platforms.
        
        Args:
            creator_id: Creator identifier
            days: Number of days to analyze
            
        Returns:
            Creator growth analytics
        """
        growth_data = {}
        
        for platform_name, collector in self.collectors.items():
            try:
                # Get creator's recent content
                config = CollectionConfig(max_results=100)
                recent_content = await collector.get_user_content(creator_id, config)
                
                # Filter content by date range
                cutoff_date = datetime.now() - timedelta(days=days)
                period_content = [
                    content for content in recent_content
                    if datetime.fromtimestamp(content.timestamp) >= cutoff_date
                ]
                
                if period_content:
                    total_views = sum(
                        content.engagement_metrics.get('views', 0) 
                        for content in period_content 
                        if content.engagement_metrics
                    )
                    
                    total_engagement = sum(
                        content.engagement_metrics.get('total_engagement', 0) 
                        for content in period_content 
                        if content.engagement_metrics
                    )
                    
                    growth_data[platform_name] = {
                        'videos_published': len(period_content),
                        'total_views': total_views,
                        'total_engagement': total_engagement,
                        'avg_views_per_video': total_views / len(period_content),
                        'avg_engagement_per_video': total_engagement / len(period_content),
                        'upload_frequency': len(period_content) / days,
                        'performance_trend': 'improving' if total_engagement > 0 else 'stable'
                    }
                else:
                    growth_data[platform_name] = {
                        'videos_published': 0,
                        'status': 'inactive'
                    }
                
            except Exception as e:
                logger.error(f"Creator growth tracking failed for {platform_name}: {e}")
                growth_data[platform_name] = {'error': str(e)}
        
        return {
            'creator_id': creator_id,
            'analysis_period_days': days,
            'platforms': growth_data,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_engagement_rate(self, content: CollectorResult) -> float:
        """Calculate engagement rate for video content."""
        if not content.engagement_metrics:
            return 0.0
        
        views = content.engagement_metrics.get('views', 0)
        total_engagement = content.engagement_metrics.get('total_engagement', 0)
        
        if views > 0:
            return (total_engagement / views) * 100
        return 0.0
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all video platform collectors."""
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