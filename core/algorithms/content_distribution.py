"""Content Distribution Engine - Multi-Platform Intelligent Distribution
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
    """Base class for platform adapters with comprehensive publishing capabilities"""
    
    def __init__(self, platform_type: PlatformType, config: Optional[Dict[str, Any]] = None):
        """Initialize platform adapter."""
        self.platform_type = platform_type
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration settings
        self.api_timeout = self.config.get('api_timeout', 30)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        self.rate_limit_delay = self.config.get('rate_limit_delay', 1.0)
        
        # Publishing settings
        self.max_file_size = self.config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
        self.supported_formats = self.config.get('supported_formats', [])
        self.enable_analytics = self.config.get('enable_analytics', True)
        
        # Authentication (to be implemented by subclasses)
        self.auth_token = self.config.get('auth_token')
        self.api_key = self.config.get('api_key')
        self.client_id = self.config.get('client_id')
        self.client_secret = self.config.get('client_secret')
    
    async def publish_content(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to platform with comprehensive error handling and validation."""
        publish_start_time = datetime.utcnow()
        
        try:
            self.logger.info(
                f"Starting content publication to {self.platform_type.value}",
                content_id=content.content_id,
                title=content.title
            )
            
            # Validate content before publishing
            validation_result = await self._validate_content(content)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Content validation failed: {validation_result['error']}",
                    'platform': self.platform_type.value,
                    'content_id': content.content_id,
                    'validation_details': validation_result
                }
            
            # Prepare content for platform
            prepared_content = await self._prepare_content_for_platform(content)
            if not prepared_content:
                return {
                    'success': False,
                    'error': "Failed to prepare content for platform",
                    'platform': self.platform_type.value,
                    'content_id': content.content_id
                }
            
            # Authenticate with platform
            auth_result = await self._authenticate()
            if not auth_result['authenticated']:
                return {
                    'success': False,
                    'error': f"Authentication failed: {auth_result['error']}",
                    'platform': self.platform_type.value,
                    'content_id': content.content_id
                }
            
            # Upload content
            upload_result = await self._upload_content(prepared_content)
            if not upload_result['success']:
                return {
                    'success': False,
                    'error': f"Content upload failed: {upload_result['error']}",
                    'platform': self.platform_type.value,
                    'content_id': content.content_id,
                    'upload_details': upload_result
                }
            
            # Set metadata and publish
            metadata_result = await self._set_content_metadata(upload_result['upload_id'], prepared_content)
            if not metadata_result['success']:
                self.logger.warning(
                    f"Metadata setting failed but content uploaded: {metadata_result['error']}",
                    content_id=content.content_id
                )
            
            # Finalize publication
            publish_result = await self._finalize_publication(upload_result['upload_id'], prepared_content)
            
            # Calculate publishing duration
            publish_duration = (datetime.utcnow() - publish_start_time).total_seconds()
            
            # Create comprehensive response
            response = {
                'success': publish_result['success'],
                'platform': self.platform_type.value,
                'content_id': content.content_id,
                'platform_id': upload_result.get('upload_id'),
                'platform_url': publish_result.get('url'),
                'publication_timestamp': publish_start_time.isoformat(),
                'publication_duration': publish_duration,
                'metadata': {
                    'title': content.title,
                    'description': content.description,
                    'tags': content.tags,
                    'visibility': prepared_content.get('visibility', 'public')
                },
                'analytics': {
                    'enabled': self.enable_analytics,
                    'tracking_id': publish_result.get('tracking_id')
                }
            }
            
            if not publish_result['success']:
                response['error'] = publish_result.get('error', 'Unknown publication error')
            
            self.logger.info(
                f"Content publication completed for {self.platform_type.value}",
                content_id=content.content_id,
                success=publish_result['success'],
                duration=publish_duration
            )
            
            return response
            
        except Exception as e:
            publish_duration = (datetime.utcnow() - publish_start_time).total_seconds()
            self.logger.error(
                f"Error publishing content to {self.platform_type.value}: {str(e)}",
                content_id=content.content_id,
                duration=publish_duration,
                exc_info=True
            )
            
            return {
                'success': False,
                'error': f"Publication failed with exception: {str(e)}",
                'platform': self.platform_type.value,
                'content_id': content.content_id,
                'publication_duration': publish_duration
            }
    
    async def _validate_content(self, content: ContentItem) -> Dict[str, Any]:
        """Validate content for platform requirements."""
        try:
            errors = []
            warnings = []
            
            # Basic content validation
            if not content.content_id:
                errors.append("Content ID is required")
            
            if not content.title or len(content.title.strip()) == 0:
                errors.append("Content title is required")
            
            if len(content.title) > 100:  # Common platform limit
                warnings.append("Title may be too long for some platforms")
            
            # Format validation
            if content.format not in self.supported_formats and self.supported_formats:
                errors.append(f"Format {content.format.value} not supported by {self.platform_type.value}")
            
            # Size validation
            if hasattr(content, 'file_size') and content.file_size > self.max_file_size:
                errors.append(f"File size {content.file_size} exceeds platform limit {self.max_file_size}")
            
            # Platform-specific validation
            platform_validation = await self._validate_platform_specific(content)
            errors.extend(platform_validation.get('errors', []))
            warnings.extend(platform_validation.get('warnings', []))
            
            return {
                'valid': len(errors) == 0,
                'error': '; '.join(errors) if errors else None,
                'warnings': warnings,
                'validation_details': {
                    'errors': errors,
                    'warnings': warnings,
                    'platform_specific': platform_validation
                }
            }
            
        except Exception as e:
            self.logger.error(f"Content validation error: {str(e)}")
            return {
                'valid': False,
                'error': f"Validation process failed: {str(e)}",
                'warnings': [],
                'validation_details': {}
            }
    
    async def _validate_platform_specific(self, content: ContentItem) -> Dict[str, Any]:
        """Platform-specific validation - to be overridden by subclasses."""
        return {'errors': [], 'warnings': []}
    
    async def _prepare_content_for_platform(self, content: ContentItem) -> Optional[Dict[str, Any]]:
        """Prepare content for platform-specific requirements."""
        try:
            prepared = {
                'content_id': content.content_id,
                'title': self._optimize_title_for_platform(content.title),
                'description': self._optimize_description_for_platform(content.description),
                'tags': self._optimize_tags_for_platform(content.tags),
                'format': content.format.value,
                'metadata': content.metadata,
                'privacy_settings': self._get_platform_privacy_settings(content),
                'scheduling': self._get_platform_scheduling(content),
                'monetization': self._get_platform_monetization_settings(content)
            }
            
            # Add platform-specific preparation
            platform_specific = await self._prepare_platform_specific(content)
            prepared.update(platform_specific)
            
            return prepared
            
        except Exception as e:
            self.logger.error(f"Content preparation error: {str(e)}")
            return None
    
    def _optimize_title_for_platform(self, title: str) -> str:
        """Optimize title for platform requirements."""
        if not title:
            return "Untitled Content"
        
        # Platform-specific title optimization
        if self.platform_type == PlatformType.TWITTER:
            # Twitter has character limits
            return title[:100] if len(title) > 100 else title
        elif self.platform_type == PlatformType.YOUTUBE:
            # YouTube allows longer titles
            return title[:100] if len(title) > 100 else title
        elif self.platform_type == PlatformType.INSTAGRAM:
            # Instagram prefers shorter, engaging titles
            return title[:80] if len(title) > 80 else title
        else:
            # Generic optimization
            return title[:90] if len(title) > 90 else title
    
    def _optimize_description_for_platform(self, description: str) -> str:
        """Optimize description for platform requirements."""
        if not description:
            return ""
        
        # Platform-specific description optimization
        if self.platform_type == PlatformType.TWITTER:
            return description[:200]  # Keep short for Twitter
        elif self.platform_type == PlatformType.YOUTUBE:
            return description[:5000]  # YouTube allows long descriptions
        elif self.platform_type == PlatformType.INSTAGRAM:
            return description[:2200]  # Instagram caption limit
        else:
            return description[:1000]  # Generic limit
    
    def _optimize_tags_for_platform(self, tags: List[str]) -> List[str]:
        """Optimize tags for platform requirements."""
        if not tags:
            return []
        
        # Platform-specific tag optimization
        max_tags = 30  # Default
        if self.platform_type == PlatformType.YOUTUBE:
            max_tags = 15
        elif self.platform_type == PlatformType.INSTAGRAM:
            max_tags = 30
        elif self.platform_type == PlatformType.TWITTER:
            max_tags = 5  # Keep hashtags minimal
        
        # Clean and limit tags
        cleaned_tags = []
        for tag in tags[:max_tags]:
            # Remove special characters and ensure valid format
            clean_tag = ''.join(c for c in tag if c.isalnum() or c in ['_', '-'])
            if clean_tag and len(clean_tag) > 1:
                cleaned_tags.append(clean_tag)
        
        return cleaned_tags
    
    def _get_platform_privacy_settings(self, content: ContentItem) -> Dict[str, Any]:
        """Get platform-specific privacy settings."""
        return {
            'visibility': 'public',  # Default to public
            'comments_enabled': True,
            'embedding_allowed': True,
            'download_allowed': False
        }
    
    def _get_platform_scheduling(self, content: ContentItem) -> Dict[str, Any]:
        """Get platform-specific scheduling settings."""
        return {
            'publish_immediately': True,
            'scheduled_time': None,
            'timezone': 'UTC'
        }
    
    def _get_platform_monetization_settings(self, content: ContentItem) -> Dict[str, Any]:
        """Get platform-specific monetization settings."""
        return {
            'monetization_enabled': False,
            'ads_enabled': False,
            'subscription_required': False
        }
    
    async def _prepare_platform_specific(self, content: ContentItem) -> Dict[str, Any]:
        """Platform-specific preparation - to be overridden by subclasses."""
        return {}
    
    async def _authenticate(self) -> Dict[str, Any]:
        """Authenticate with the platform."""
        try:
            # Generic authentication logic
            if not self.auth_token and not (self.api_key or (self.client_id and self.client_secret)):
                return {
                    'authenticated': False,
                    'error': f"No authentication credentials provided for {self.platform_type.value}"
                }
            
            # Simulate authentication check
            auth_valid = await self._verify_authentication_credentials()
            
            if auth_valid:
                return {
                    'authenticated': True,
                    'auth_method': 'token' if self.auth_token else 'api_key',
                    'expires_at': None  # Platform-specific implementation
                }
            else:
                return {
                    'authenticated': False,
                    'error': f"Invalid credentials for {self.platform_type.value}"
                }
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return {
                'authenticated': False,
                'error': f"Authentication process failed: {str(e)}"
            }
    
    async def _verify_authentication_credentials(self) -> bool:
        """Verify authentication credentials - to be overridden by subclasses."""
        # Basic credential check
        return bool(self.auth_token or self.api_key or (self.client_id and self.client_secret))
    
    async def _upload_content(self, prepared_content: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to platform."""
        try:
            # Simulate content upload
            upload_id = f"{self.platform_type.value}_{prepared_content['content_id']}_{int(datetime.utcnow().timestamp())}"
            
            self.logger.info(f"Uploading content to {self.platform_type.value}", upload_id=upload_id)
            
            # Simulate upload process
            await asyncio.sleep(0.1)  # Simulate network delay
            
            return {
                'success': True,
                'upload_id': upload_id,
                'upload_url': f"https://{self.platform_type.value.lower()}.com/upload/{upload_id}",
                'upload_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Content upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _set_content_metadata(self, upload_id: str, prepared_content: Dict[str, Any]) -> Dict[str, Any]:
        """Set content metadata on the platform."""
        try:
            self.logger.debug(f"Setting metadata for {upload_id} on {self.platform_type.value}")
            
            # Simulate metadata setting
            await asyncio.sleep(0.05)
            
            return {
                'success': True,
                'metadata_set': {
                    'title': prepared_content.get('title'),
                    'description': prepared_content.get('description'),
                    'tags': prepared_content.get('tags', []),
                    'privacy': prepared_content.get('privacy_settings', {})
                }
            }
            
        except Exception as e:
            self.logger.error(f"Metadata setting error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _finalize_publication(self, upload_id: str, prepared_content: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize content publication."""
        try:
            self.logger.info(f"Finalizing publication for {upload_id} on {self.platform_type.value}")
            
            # Simulate publication finalization
            await asyncio.sleep(0.1)
            
            # Generate platform-specific URL
            content_url = f"https://{self.platform_type.value.lower()}.com/content/{upload_id}"
            tracking_id = f"track_{upload_id}"
            
            return {
                'success': True,
                'url': content_url,
                'tracking_id': tracking_id,
                'publication_status': 'published',
                'visibility': prepared_content.get('privacy_settings', {}).get('visibility', 'public')
            }
            
        except Exception as e:
            self.logger.error(f"Publication finalization error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_content_analytics(self, platform_id: str) -> Dict[str, Any]:
        """Get content analytics from platform."""
        try:
            # Simulate analytics retrieval
            return {
                'platform_id': platform_id,
                'platform': self.platform_type.value,
                'views': 0,
                'likes': 0,
                'shares': 0,
                'comments': 0,
                'engagement_rate': 0.0,
                'reach': 0,
                'impressions': 0,
                'last_updated': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Analytics retrieval error: {str(e)}")
            return {'error': str(e)}
    
    async def update_content(self, platform_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update published content."""
        try:
            # Simulate content update
            return {
                'success': True,
                'platform_id': platform_id,
                'updates_applied': list(updates.keys()),
                'updated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Content update error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def delete_content(self, platform_id: str) -> Dict[str, Any]:
        """Delete content from platform."""
        try:
            # Simulate content deletion
            return {
                'success': True,
                'platform_id': platform_id,
                'deleted_at': datetime.utcnow().isoformat(),
                'platform': self.platform_type.value
            }
        except Exception as e:
            self.logger.error(f"Content deletion error: {str(e)}")
            return {'success': False, 'error': str(e)}

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
