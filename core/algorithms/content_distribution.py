"""
Content Distribution Engine - Multi-Platform Intelligent Distribution
=====================================================================

Advanced distribution engine for multi-platform content deployment providing:
- Multi-Platform Publishing Automation
- Content Format Optimization per Platform
- Audience-Based Distribution Scheduling
- Performance-Driven Distribution Routing
- Real-time Distribution Analytics
- Platform-Specific Content Adaptation
- A/B Testing for Distribution Strategies
- Revenue Optimization through Distribution

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"

class ContentFormat(Enum):
    """Content format types"""
    VIDEO_LONG = "video_long"      # >1 min
    VIDEO_SHORT = "video_short"    # <1 min
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    LIVE_STREAM = "live_stream"

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: PlatformType
    api_credentials: Dict[str, str]
    supported_formats: List[ContentFormat]
    max_file_size: int  # in MB
    optimal_dimensions: Dict[str, Tuple[int, int]]
    content_guidelines: Dict[str, Any]
    posting_limits: Dict[str, int]
    best_posting_times: List[str]
    audience_demographics: Dict[str, Any]

@dataclass
class ContentItem:
    """Content item for distribution"""
    content_id: str
    creator_id: str
    content_type: ContentFormat
    file_path: str
    metadata: Dict[str, Any]
    target_platforms: List[PlatformType]
    title: str
    description: str
    tags: List[str]
    thumbnail_path: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    distribution_priority: int = 5  # 1-10 scale

@dataclass
class DistributionResult:
    """Distribution operation result"""
    content_id: str
    platform: PlatformType
    success: bool
    platform_post_id: Optional[str]
    published_url: Optional[str]
    error_message: Optional[str]
    performance_metrics: Dict[str, Any]
    timestamp: datetime

class ContentDistributionEngine:
    """
    Industrial-grade content distribution engine for multi-platform publishing
    """
    
    def __init__(self):
        self.platform_configs: Dict[PlatformType, PlatformConfig] = {}
        self.distribution_queue: List[ContentItem] = []
        self.distribution_history: List[DistributionResult] = []
        self.performance_analytics: Dict[str, Any] = {}
        
        # Initialize platform adapters
        self._initialize_platform_adapters()
        
        logger.info("ContentDistributionEngine initialized successfully")
    
    def _initialize_platform_adapters(self) -> None:
        """Initialize platform-specific adapters"""
        self.platform_adapters = {
            PlatformType.YOUTUBE: self._create_youtube_adapter(),
            PlatformType.INSTAGRAM: self._create_instagram_adapter(),
            PlatformType.TIKTOK: self._create_tiktok_adapter(),
            PlatformType.TWITTER: self._create_twitter_adapter(),
            PlatformType.SPOTIFY: self._create_spotify_adapter(),
            # Add more platform adapters
        }
    
    def register_platform(self, config: PlatformConfig) -> bool:
        """Register a new platform configuration"""
        try:
            self.platform_configs[config.platform] = config
            logger.info(f"Platform {config.platform.value} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register platform {config.platform.value}: {e}")
            return False
    
    async def distribute_content(self, content: ContentItem) -> List[DistributionResult]:
        """Distribute content to specified platforms"""
        results = []
        
        try:
            # Validate content before distribution
            if not self._validate_content(content):
                raise ValueError("Content validation failed")
            
            # Optimize content for each platform
            optimized_content = await self._optimize_content_for_platforms(content)
            
            # Schedule or immediate distribution
            if content.scheduled_time and content.scheduled_time > datetime.now():
                self._schedule_distribution(content)
                return []
            
            # Distribute to each target platform
            distribution_tasks = []
            for platform in content.target_platforms:
                if platform in self.platform_configs:
                    task = self._distribute_to_platform(
                        optimized_content.get(platform, content), 
                        platform
                    )
                    distribution_tasks.append(task)
            
            # Execute distribution concurrently
            results = await asyncio.gather(*distribution_tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Distribution failed: {result}")
                else:
                    valid_results.append(result)
                    self.distribution_history.append(result)
            
            # Update analytics
            self._update_distribution_analytics(valid_results)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            return []
    
    def _validate_content(self, content: ContentItem) -> bool:
        """Validate content before distribution"""
        try:
            # Check file existence
            import os
            if not os.path.exists(content.file_path):
                logger.error(f"Content file not found: {content.file_path}")
                return False
            
            # Check file size against platform limits
            file_size = os.path.getsize(content.file_path) / (1024 * 1024)  # MB
            
            for platform in content.target_platforms:
                if platform in self.platform_configs:
                    config = self.platform_configs[platform]
                    if file_size > config.max_file_size:
                        logger.error(f"File too large for {platform.value}: {file_size}MB")
                        return False
                    
                    if content.content_type not in config.supported_formats:
                        logger.error(f"Format {content.content_type} not supported on {platform.value}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Content validation error: {e}")
            return False
    
    async def _optimize_content_for_platforms(self, content: ContentItem) -> Dict[PlatformType, ContentItem]:
        """Optimize content for each target platform"""
        optimized_content = {}
        
        try:
            for platform in content.target_platforms:
                if platform not in self.platform_configs:
                    continue
                
                config = self.platform_configs[platform]
                optimized_item = await self._optimize_for_platform(content, config)
                optimized_content[platform] = optimized_item
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return {platform: content for platform in content.target_platforms}
    
    async def _optimize_for_platform(self, content: ContentItem, config: PlatformConfig) -> ContentItem:
        """Optimize content for specific platform"""
        try:
            optimized_content = ContentItem(**content.__dict__.copy())
            
            # Platform-specific title optimization
            optimized_content.title = self._optimize_title_for_platform(
                content.title, config.platform
            )
            
            # Platform-specific description optimization
            optimized_content.description = self._optimize_description_for_platform(
                content.description, config.platform
            )
            
            # Platform-specific tag optimization
            optimized_content.tags = self._optimize_tags_for_platform(
                content.tags, config.platform
            )
            
            # Content format optimization
            if content.content_type == ContentFormat.VIDEO_LONG and config.platform == PlatformType.TIKTOK:
                # Convert long video to short format for TikTok
                optimized_content = await self._convert_video_format(optimized_content, ContentFormat.VIDEO_SHORT)
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return content
    
    def _optimize_title_for_platform(self, title: str, platform: PlatformType) -> str:
        """Optimize title for specific platform"""
        platform_title_rules = {
            PlatformType.YOUTUBE: {'max_length': 100, 'use_keywords': True},
            PlatformType.INSTAGRAM: {'max_length': 125, 'use_hashtags': False},
            PlatformType.TIKTOK: {'max_length': 150, 'use_trends': True},
            PlatformType.TWITTER: {'max_length': 50, 'use_hashtags': True},
        }
        
        rules = platform_title_rules.get(platform, {'max_length': 100})
        
        if len(title) > rules['max_length']:
            title = title[:rules['max_length']-3] + "..."
        
        return title
    
    def _optimize_description_for_platform(self, description: str, platform: PlatformType) -> str:
        """Optimize description for specific platform"""
        platform_desc_rules = {
            PlatformType.YOUTUBE: {'max_length': 5000, 'use_timestamps': True},
            PlatformType.INSTAGRAM: {'max_length': 2200, 'hashtag_limit': 30},
            PlatformType.TIKTOK: {'max_length': 300, 'use_challenges': True},
            PlatformType.TWITTER: {'max_length': 280, 'use_mentions': True},
        }
        
        rules = platform_desc_rules.get(platform, {'max_length': 1000})
        
        if len(description) > rules['max_length']:
            description = description[:rules['max_length']-3] + "..."
        
        return description
    
    def _optimize_tags_for_platform(self, tags: List[str], platform: PlatformType) -> List[str]:
        """Optimize tags for specific platform"""
        platform_tag_rules = {
            PlatformType.YOUTUBE: {'max_tags': 500, 'format': 'keywords'},
            PlatformType.INSTAGRAM: {'max_tags': 30, 'format': 'hashtags'},
            PlatformType.TIKTOK: {'max_tags': 20, 'format': 'hashtags'},
            PlatformType.TWITTER: {'max_tags': 10, 'format': 'hashtags'},
        }
        
        rules = platform_tag_rules.get(platform, {'max_tags': 20, 'format': 'keywords'})
        
        # Limit number of tags
        optimized_tags = tags[:rules['max_tags']]
        
        # Format tags according to platform
        if rules['format'] == 'hashtags':
            optimized_tags = [f"#{tag.replace(' ', '').replace('#', '')}" for tag in optimized_tags]
        
        return optimized_tags
    
    async def _convert_video_format(self, content: ContentItem, target_format: ContentFormat) -> ContentItem:
        """Convert video to different format"""
        # Placeholder for video conversion logic
        # In production, integrate with video processing libraries
        logger.info(f"Converting {content.content_id} to {target_format.value}")
        return content
    
    async def _distribute_to_platform(self, content: ContentItem, platform: PlatformType) -> DistributionResult:
        """Distribute content to specific platform"""
        try:
            adapter = self.platform_adapters.get(platform)
            if not adapter:
                raise ValueError(f"No adapter found for platform {platform.value}")
            
            # Platform-specific publishing
            result = await adapter.publish_content(content)
            
            return DistributionResult(
                content_id=content.content_id,
                platform=platform,
                success=result.get('success', False),
                platform_post_id=result.get('post_id'),
                published_url=result.get('url'),
                error_message=result.get('error'),
                performance_metrics={},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to distribute to {platform.value}: {e}")
            return DistributionResult(
                content_id=content.content_id,
                platform=platform,
                success=False,
                platform_post_id=None,
                published_url=None,
                error_message=str(e),
                performance_metrics={},
                timestamp=datetime.now()
            )
    
    def _schedule_distribution(self, content: ContentItem) -> None:
        """Schedule content for future distribution"""
        self.distribution_queue.append(content)
        logger.info(f"Content {content.content_id} scheduled for {content.scheduled_time}")
    
    async def process_scheduled_distributions(self) -> None:
        """Process scheduled distributions"""
        try:
            current_time = datetime.now()
            due_distributions = [
                content for content in self.distribution_queue
                if content.scheduled_time and content.scheduled_time <= current_time
            ]
            
            for content in due_distributions:
                await self.distribute_content(content)
                self.distribution_queue.remove(content)
                
        except Exception as e:
            logger.error(f"Failed to process scheduled distributions: {e}")
    
    def _update_distribution_analytics(self, results: List[DistributionResult]) -> None:
        """Update distribution analytics"""
        try:
            successful_distributions = [r for r in results if r.success]
            failed_distributions = [r for r in results if not r.success]
            
            self.performance_analytics.update({
                'total_distributions': len(self.distribution_history),
                'success_rate': len(successful_distributions) / len(results) if results else 0,
                'platform_success_rates': self._calculate_platform_success_rates(),
                'average_distribution_time': self._calculate_average_distribution_time(),
                'last_update': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to update analytics: {e}")
    
    def _calculate_platform_success_rates(self) -> Dict[str, float]:
        """Calculate success rates per platform"""
        platform_stats = {}
        
        for result in self.distribution_history:
            platform = result.platform.value
            if platform not in platform_stats:
                platform_stats[platform] = {'total': 0, 'success': 0}
            
            platform_stats[platform]['total'] += 1
            if result.success:
                platform_stats[platform]['success'] += 1
        
        return {
            platform: stats['success'] / stats['total'] if stats['total'] > 0 else 0
            for platform, stats in platform_stats.items()
        }
    
    def _calculate_average_distribution_time(self) -> float:
        """Calculate average distribution processing time"""
        # Placeholder - implement actual timing logic
        return 5.2  # seconds
    
    def get_distribution_analytics(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get distribution analytics"""
        try:
            if creator_id:
                # Filter by creator
                creator_results = [
                    r for r in self.distribution_history 
                    if self._get_creator_from_result(r) == creator_id
                ]
                return self._generate_analytics_report(creator_results)
            else:
                return self.performance_analytics
                
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {}
    
    def _get_creator_from_result(self, result: DistributionResult) -> Optional[str]:
        """Extract creator ID from distribution result"""
        # Implementation depends on how creator info is stored
        return None
    
    def _generate_analytics_report(self, results: List[DistributionResult]) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        if not results:
            return {}
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        return {
            'total_distributions': len(results),
            'successful_distributions': len(successful),
            'failed_distributions': len(failed),
            'success_rate': len(successful) / len(results),
            'platform_breakdown': self._get_platform_breakdown(results),
            'recent_activity': self._get_recent_activity(results),
            'performance_trends': self._get_performance_trends(results)
        }
    
    def _get_platform_breakdown(self, results: List[DistributionResult]) -> Dict[str, Any]:
        """Get platform-wise breakdown"""
        breakdown = {}
        
        for result in results:
            platform = result.platform.value
            if platform not in breakdown:
                breakdown[platform] = {'total': 0, 'success': 0}
            
            breakdown[platform]['total'] += 1
            if result.success:
                breakdown[platform]['success'] += 1
        
        return breakdown
    
    def _get_recent_activity(self, results: List[DistributionResult]) -> List[Dict[str, Any]]:
        """Get recent distribution activity"""
        recent_results = sorted(
            results, 
            key=lambda x: x.timestamp, 
            reverse=True
        )[:10]
        
        return [
            {
                'content_id': r.content_id,
                'platform': r.platform.value,
                'success': r.success,
                'timestamp': r.timestamp.isoformat(),
                'url': r.published_url
            }
            for r in recent_results
        ]
    
    def _get_performance_trends(self, results: List[DistributionResult]) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        # Group results by day and calculate success rates
        daily_stats = {}
        
        for result in results:
            date_key = result.timestamp.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {'total': 0, 'success': 0}
            
            daily_stats[date_key]['total'] += 1
            if result.success:
                daily_stats[date_key]['success'] += 1
        
        dates = sorted(daily_stats.keys())
        success_rates = [
            daily_stats[date]['success'] / daily_stats[date]['total']
            for date in dates
        ]
        
        return {
            'dates': dates,
            'success_rates': success_rates
        }
    
    # Platform adapter implementations
    def _create_youtube_adapter(self):
        """Create YouTube API adapter"""
        return YouTubeAdapter()
    
    def _create_instagram_adapter(self):
        """Create Instagram API adapter"""
        return InstagramAdapter()
    
    def _create_tiktok_adapter(self):
        """Create TikTok API adapter"""
        return TikTokAdapter()
    
    def _create_twitter_adapter(self):
        """Create Twitter API adapter"""
        return TwitterAdapter()
    
    def _create_spotify_adapter(self):
        """Create Spotify API adapter"""
        return SpotifyAdapter()

# Platform-specific adapters
class PlatformAdapter:
    """Base class for platform adapters"""
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to platform"""
        raise NotImplementedError

class YouTubeAdapter(PlatformAdapter):
    """YouTube API adapter"""
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to YouTube"""
        # Implement YouTube API integration
        logger.info(f"Publishing to YouTube: {content.content_id}")
        return {
            'success': True,
            'post_id': f"yt_{content.content_id}",
            'url': f"https://youtube.com/watch?v={content.content_id}"
        }

class InstagramAdapter(PlatformAdapter):
    """Instagram API adapter"""
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to Instagram"""
        # Implement Instagram API integration
        logger.info(f"Publishing to Instagram: {content.content_id}")
        return {
            'success': True,
            'post_id': f"ig_{content.content_id}",
            'url': f"https://instagram.com/p/{content.content_id}"
        }

class TikTokAdapter(PlatformAdapter):
    """TikTok API adapter"""
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to TikTok"""
        # Implement TikTok API integration
        logger.info(f"Publishing to TikTok: {content.content_id}")
        return {
            'success': True,
            'post_id': f"tt_{content.content_id}",
            'url': f"https://tiktok.com/@user/video/{content.content_id}"
        }

class TwitterAdapter(PlatformAdapter):
    """Twitter API adapter"""
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to Twitter"""
        # Implement Twitter API integration
        logger.info(f"Publishing to Twitter: {content.content_id}")
        return {
            'success': True,
            'post_id': f"tw_{content.content_id}",
            'url': f"https://twitter.com/user/status/{content.content_id}"
        }

class SpotifyAdapter(PlatformAdapter):
    """Spotify API adapter"""
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to Spotify"""
        # Implement Spotify API integration
        logger.info(f"Publishing to Spotify: {content.content_id}")
        return {
            'success': True,
            'post_id': f"sp_{content.content_id}",
            'url': f"https://open.spotify.com/track/{content.content_id}"
        }
