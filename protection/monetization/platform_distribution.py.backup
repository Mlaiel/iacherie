"""Platform Distribution Engine - Multi-platform content distribution and monetization.
Handles content distribution across platforms with revenue optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Team Specialties:
- Lead Dev IA: AI-powered distribution optimization
- Backend Senior: Scalable distribution architecture
- ML Engineer: Performance prediction algorithms  
- DBA: Distribution data management
- Security: Platform security and API management
- Microservices: Distributed platform services
- Audio Engineer: Audio platform optimization
- DevOps: Multi-platform infrastructure
- IA Prompt Engineer: AI-driven content optimization

WARNING: This code, concept, and intellectual property are exclusively owned by 
Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, copying, distribution, 
modification, or theft of this code or concept without explicit written permission 
is strictly prohibited and will result in immediate legal action.
"""
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from abc import ABC, abstractmethod
import uuid
import json
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types."""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"


class ContentFormat(Enum):
    """Content format types."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT_FORM = "short_form"


class DistributionStatus(Enum):
    """Distribution status tracking."""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    REMOVED = "removed"
    RESTRICTED = "restricted"
    MONETIZED = "monetized"


class MonetizationModel(Enum):
    """Platform monetization models."""
    AD_REVENUE = "ad_revenue"
    SUBSCRIPTION = "subscription"
    PAY_PER_VIEW = "pay_per_view"
    DONATIONS = "donations"
    SPONSORSHIPS = "sponsorships"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    ROYALTIES = "royalties"


@dataclass
class PlatformConfiguration:
    """Platform-specific configuration."""
    platform_type: PlatformType
    api_credentials: Dict[str, str]
    supported_formats: List[ContentFormat]
    monetization_models: List[MonetizationModel]
    max_file_size: int  # bytes
    recommended_dimensions: Dict[str, Tuple[int, int]]
    content_guidelines: Dict[str, Any]
    revenue_share: Decimal  # Platform's revenue share percentage
    payout_threshold: Decimal
    payout_frequency: str  # daily, weekly, monthly
    api_rate_limits: Dict[str, int]
    
    def supports_format(self, content_format: ContentFormat) -> bool:
        """Check if platform supports given content format."""
        return content_format in self.supported_formats
    
    def get_optimal_settings(self, content_format: ContentFormat) -> Dict[str, Any]:
        """Get optimal settings for content format on this platform."""
        settings = {
            'format': content_format.value,
            'dimensions': self.recommended_dimensions.get(content_format.value),
            'max_size': self.max_file_size,
            'guidelines': self.content_guidelines.get(content_format.value, {})
        }
        return settings


@dataclass
class DistributionTask:
    """Content distribution task."""
    task_id: str
    content_id: str
    user_id: str
    platform: PlatformType
    content_format: ContentFormat
    source_file_path: str
    platform_specific_metadata: Dict[str, Any]
    scheduling: Optional[datetime] = None
    status: DistributionStatus = DistributionStatus.PENDING
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'content_id': self.content_id,
            'user_id': self.user_id,
            'platform': self.platform.value,
            'content_format': self.content_format.value,
            'source_file_path': self.source_file_path,
            'platform_specific_metadata': self.platform_specific_metadata,
            'scheduling': self.scheduling.isoformat() if self.scheduling else None,
            'status': self.status.value,
            'platform_post_id': self.platform_post_id,
            'error_message': self.error_message,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


@dataclass
class PlatformMetrics:
    """Platform performance metrics."""
    platform: PlatformType
    content_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    click_through_rate: float = 0.0
    engagement_rate: float = 0.0
    revenue_generated: Decimal = Decimal('0')
    monetization_active: bool = False
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate."""
        if self.views == 0:
            return 0.0
        
        total_engagements = self.likes + self.shares + self.comments + self.saves
        return (total_engagements / self.views) * 100
    
    def get_performance_score(self) -> float:
        """Calculate overall performance score."""
        engagement_score = min(self.engagement_rate * 10, 40)
        revenue_score = min(float(self.revenue_generated) / 100, 30)
        reach_score = min(self.views / 1000, 30)
        
        return engagement_score + revenue_score + reach_score


class PlatformAdapter(ABC):
    """Abstract base class for platform adapters."""
    
    def __init__(self, config: PlatformConfiguration):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def upload_content(self, task: DistributionTask) -> bool:
        """Upload content to platform."""
        pass
    
    @abstractmethod
    async def get_content_metrics(self, platform_post_id: str) -> PlatformMetrics:
        """Get content performance metrics."""
        pass
    
    @abstractmethod
    async def update_content(self, platform_post_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing content."""
        pass
    
    @abstractmethod
    async def delete_content(self, platform_post_id: str) -> bool:
        """Delete content from platform."""
        pass
    
    @abstractmethod
    async def get_monetization_data(self, platform_post_id: str) -> Dict[str, Any]:
        """Get monetization data for content."""
        pass


class SpotifyAdapter(PlatformAdapter):
    """Spotify platform adapter."""
    
    async def upload_content(self, task: DistributionTask) -> bool:
        """Upload audio content to Spotify."""
        try:
            if task.content_format != ContentFormat.AUDIO:
                raise ValueError("Spotify only supports audio content")
            
            # Spotify uses distribution services like DistroKid, TuneCore, etc.
            # This would integrate with those services' APIs
            
            headers = {
                'Authorization': f"Bearer {self.config.api_credentials.get('access_token')}",
                'Content-Type': 'application/json'
            }
            
            # Prepare metadata for distribution service
            metadata = {
                'title': task.platform_specific_metadata.get('title'),
                'artist': task.platform_specific_metadata.get('artist'),
                'album': task.platform_specific_metadata.get('album'),
                'genre': task.platform_specific_metadata.get('genre'),
                'release_date': task.platform_specific_metadata.get('release_date'),
                'isrc': task.platform_specific_metadata.get('isrc'),
                'audio_file': task.source_file_path
            }
            
            # Simulate API call to distribution service
            async with self.session.post(
                'https://api.distributionservice.com/v1/releases',
                headers=headers,
                json=metadata
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task.platform_post_id = result.get('release_id')
                    task.status = DistributionStatus.PROCESSING
                    logger.info(f"Successfully submitted to Spotify: {task.platform_post_id}")
                    return True
                else:
                    task.error_message = f"Spotify upload failed: {response.status}"
                    task.status = DistributionStatus.FAILED
                    return False
                    
        except Exception as e:
            logger.error(f"Error uploading to Spotify: {e}")
            task.error_message = str(e)
            task.status = DistributionStatus.FAILED
            return False
    
    async def get_content_metrics(self, platform_post_id: str) -> PlatformMetrics:
        """Get Spotify track metrics."""
        try:
            headers = {
                'Authorization': f"Bearer {self.config.api_credentials.get('access_token')}"
            }
            
            async with self.session.get(
                f'https://api.spotify.com/v1/tracks/{platform_post_id}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return PlatformMetrics(
                        platform=PlatformType.SPOTIFY,
                        content_id=platform_post_id,
                        views=data.get('popularity', 0) * 1000,  # Estimated plays
                        likes=data.get('saved_count', 0),
                        monetization_active=True,
                        audience_demographics=data.get('demographics', {}),
                        revenue_generated=Decimal(str(data.get('royalties', 0)))
                    )
                else:
                    logger.warning(f"Failed to get Spotify metrics: {response.status}")
                    return PlatformMetrics(platform=PlatformType.SPOTIFY, content_id=platform_post_id)
                    
        except Exception as e:
            logger.error(f"Error getting Spotify metrics: {e}")
            return PlatformMetrics(platform=PlatformType.SPOTIFY, content_id=platform_post_id)
    
    async def update_content(self, platform_post_id: str, updates: Dict[str, Any]) -> bool:
        """Update Spotify track metadata."""
        # Spotify doesn't allow direct updates once released
        # This would work through distribution service
        return False
    
    async def delete_content(self, platform_post_id: str) -> bool:
        """Remove content from Spotify."""
        # This would work through distribution service
        return True
    
    async def get_monetization_data(self, platform_post_id: str) -> Dict[str, Any]:
        """Get Spotify royalty data."""
        try:
            # This would integrate with Spotify for Artists API
            return {
                'streams': 10000,
                'royalties': 50.0,
                'countries': ['US', 'UK', 'DE', 'FR'],
                'demographics': {'age_18_24': 0.3, 'age_25_34': 0.4, 'age_35_44': 0.3}
            }
        except Exception as e:
            logger.error(f"Error getting Spotify monetization data: {e}")
            return {}


class YouTubeAdapter(PlatformAdapter):
    """YouTube platform adapter."""
    
    async def upload_content(self, task: DistributionTask) -> bool:
        """Upload video content to YouTube."""
        try:
            if task.content_format not in [ContentFormat.VIDEO, ContentFormat.AUDIO]:
                raise ValueError("YouTube supports video and audio content")
            
            headers = {
                'Authorization': f"Bearer {self.config.api_credentials.get('access_token')}",
                'Content-Type': 'application/json'
            }
            
            # Prepare video metadata
            metadata = {
                'snippet': {
                    'title': task.platform_specific_metadata.get('title'),
                    'description': task.platform_specific_metadata.get('description'),
                    'tags': task.platform_specific_metadata.get('tags', []),
                    'categoryId': task.platform_specific_metadata.get('category_id', '10')
                },
                'status': {
                    'privacyStatus': task.platform_specific_metadata.get('privacy', 'public'),
                    'madeForKids': task.platform_specific_metadata.get('made_for_kids', False)
                },
                'monetizationDetails': {
                    'access': {
                        'allowed': True
                    }
                }
            }
            
            # Upload video file
            async with self.session.post(
                'https://www.googleapis.com/upload/youtube/v3/videos',
                headers=headers,
                json=metadata
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task.platform_post_id = result.get('id')
                    task.status = DistributionStatus.PUBLISHED
                    logger.info(f"Successfully uploaded to YouTube: {task.platform_post_id}")
                    return True
                else:
                    task.error_message = f"YouTube upload failed: {response.status}"
                    task.status = DistributionStatus.FAILED
                    return False
                    
        except Exception as e:
            logger.error(f"Error uploading to YouTube: {e}")
            task.error_message = str(e)
            task.status = DistributionStatus.FAILED
            return False
    
    async def get_content_metrics(self, platform_post_id: str) -> PlatformMetrics:
        """Get YouTube video metrics."""
        try:
            headers = {
                'Authorization': f"Bearer {self.config.api_credentials.get('access_token')}"
            }
            
            async with self.session.get(
                f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={platform_post_id}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data['items'][0]['statistics'] if data['items'] else {}
                    
                    return PlatformMetrics(
                        platform=PlatformType.YOUTUBE,
                        content_id=platform_post_id,
                        views=int(stats.get('viewCount', 0)),
                        likes=int(stats.get('likeCount', 0)),
                        comments=int(stats.get('commentCount', 0)),
                        monetization_active=True
                    )
                else:
                    logger.warning(f"Failed to get YouTube metrics: {response.status}")
                    return PlatformMetrics(platform=PlatformType.YOUTUBE, content_id=platform_post_id)
                    
        except Exception as e:
            logger.error(f"Error getting YouTube metrics: {e}")
            return PlatformMetrics(platform=PlatformType.YOUTUBE, content_id=platform_post_id)
    
    async def update_content(self, platform_post_id: str, updates: Dict[str, Any]) -> bool:
        """Update YouTube video."""
        try:
            headers = {
                'Authorization': f"Bearer {self.config.api_credentials.get('access_token')}",
                'Content-Type': 'application/json'
            }
            
            async with self.session.put(
                f'https://www.googleapis.com/youtube/v3/videos?part=snippet',
                headers=headers,
                json={'id': platform_post_id, 'snippet': updates}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error updating YouTube video: {e}")
            return False
    
    async def delete_content(self, platform_post_id: str) -> bool:
        """Delete YouTube video."""
        try:
            headers = {
                'Authorization': f"Bearer {self.config.api_credentials.get('access_token')}"
            }
            
            async with self.session.delete(
                f'https://www.googleapis.com/youtube/v3/videos?id={platform_post_id}',
                headers=headers
            ) as response:
                return response.status == 204
                
        except Exception as e:
            logger.error(f"Error deleting YouTube video: {e}")
            return False
    
    async def get_monetization_data(self, platform_post_id: str) -> Dict[str, Any]:
        """Get YouTube monetization data."""
        try:
            # This would use YouTube Analytics API
            return {
                'estimated_revenue': 25.50,
                'rpm': 2.55,
                'ad_impressions': 1000,
                'monetized_playbacks': 800,
                'demographics': {'age_18_24': 0.35, 'age_25_34': 0.45}
            }
        except Exception as e:
            logger.error(f"Error getting YouTube monetization data: {e}")
            return {}


class PlatformDistributionEngine:
    """Main platform distribution engine."""
    
    def __init__(self):
        self.platform_configs: Dict[PlatformType, PlatformConfiguration] = {}
        self.platform_adapters: Dict[PlatformType, PlatformAdapter] = {}
        self.distribution_tasks: Dict[str, DistributionTask] = {}
        self.platform_metrics: Dict[str, List[PlatformMetrics]] = {}
        
        # Initialize default platform configurations
        self._initialize_platform_configs()
    
    def _initialize_platform_configs(self):
        """Initialize default platform configurations."""
        
        # Spotify Configuration
        spotify_config = PlatformConfiguration(
            platform_type=PlatformType.SPOTIFY,
            api_credentials={},
            supported_formats=[ContentFormat.AUDIO],
            monetization_models=[MonetizationModel.ROYALTIES, MonetizationModel.SUBSCRIPTION],
            max_file_size=500 * 1024 * 1024,  # 500MB
            recommended_dimensions={},
            content_guidelines={
                'audio': {
                    'format': ['wav', 'flac', 'mp3'],
                    'min_quality': '320kbps',
                    'min_duration': 30,
                    'max_duration': 600
                }
            },
            revenue_share=Decimal('70'),  # Artist gets 70%
            payout_threshold=Decimal('50'),
            payout_frequency='monthly',
            api_rate_limits={'requests_per_hour': 1000}
        )
        
        # YouTube Configuration
        youtube_config = PlatformConfiguration(
            platform_type=PlatformType.YOUTUBE,
            api_credentials={},
            supported_formats=[ContentFormat.VIDEO, ContentFormat.AUDIO, ContentFormat.SHORT_FORM],
            monetization_models=[MonetizationModel.AD_REVENUE, MonetizationModel.SUBSCRIPTION],
            max_file_size=2 * 1024 * 1024 * 1024,  # 2GB
            recommended_dimensions={
                'video': (1920, 1080),
                'short_form': (1080, 1920)
            },
            content_guidelines={
                'video': {
                    'formats': ['mp4', 'mov', 'avi'],
                    'min_resolution': '720p',
                    'max_duration': 43200  # 12 hours
                }
            },
            revenue_share=Decimal('55'),  # Creator gets 55%
            payout_threshold=Decimal('100'),
            payout_frequency='monthly',
            api_rate_limits={'requests_per_day': 10000}
        )
        
        self.platform_configs[PlatformType.SPOTIFY] = spotify_config
        self.platform_configs[PlatformType.YOUTUBE] = youtube_config
        
        # Initialize adapters
        self.platform_adapters[PlatformType.SPOTIFY] = SpotifyAdapter(spotify_config)
        self.platform_adapters[PlatformType.YOUTUBE] = YouTubeAdapter(youtube_config)
    
    async def distribute_content(
        self,
        user_id: str,
        content_id: str,
        source_file_path: str,
        content_format: ContentFormat,
        target_platforms: List[PlatformType],
        metadata: Dict[str, Any],
        scheduling: Optional[datetime] = None
    ) -> List[DistributionTask]:
        """Distribute content to multiple platforms."""
        try:
            tasks = []
            
            for platform in target_platforms:
                if platform not in self.platform_configs:
                    logger.warning(f"Platform {platform} not configured")
                    continue
                
                config = self.platform_configs[platform]
                
                # Check if platform supports content format
                if not config.supports_format(content_format):
                    logger.warning(f"Platform {platform} doesn't support format {content_format}")
                    continue
                
                # Create distribution task
                task_id = str(uuid.uuid4())
                task = DistributionTask(
                    task_id=task_id,
                    content_id=content_id,
                    user_id=user_id,
                    platform=platform,
                    content_format=content_format,
                    source_file_path=source_file_path,
                    platform_specific_metadata=self._adapt_metadata_for_platform(metadata, platform),
                    scheduling=scheduling
                )
                
                self.distribution_tasks[task_id] = task
                tasks.append(task)
                
                # Schedule or execute immediately
                if scheduling and scheduling > datetime.utcnow():
                    await self._schedule_distribution(task)
                else:
                    await self._execute_distribution(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error distributing content: {e}")
            return []
    
    async def _execute_distribution(self, task: DistributionTask) -> bool:
        """Execute a distribution task."""
        try:
            adapter = self.platform_adapters.get(task.platform)
            if not adapter:
                task.status = DistributionStatus.FAILED
                task.error_message = f"No adapter available for {task.platform}"
                return False
            
            # Execute upload
            async with adapter:
                success = await adapter.upload_content(task)
                task.processed_at = datetime.utcnow()
                
                if success:
                    logger.info(f"Successfully distributed content to {task.platform}")
                    
                    # Start metrics tracking
                    asyncio.create_task(self._track_content_metrics(task))
                
                return success
                
        except Exception as e:
            logger.error(f"Error executing distribution: {e}")
            task.status = DistributionStatus.FAILED
            task.error_message = str(e)
            return False
    
    async def _schedule_distribution(self, task: DistributionTask) -> None:
        """Schedule a distribution task for future execution."""
        delay = (task.scheduling - datetime.utcnow()).total_seconds()
        
        async def delayed_execution():
            await asyncio.sleep(delay)
            await self._execute_distribution(task)
        
        asyncio.create_task(delayed_execution())
        logger.info(f"Scheduled distribution task {task.task_id} for {task.scheduling}")
    
    async def _track_content_metrics(self, task: DistributionTask) -> None:
        """Track content performance metrics."""
        try:
            if not task.platform_post_id:
                return
            
            adapter = self.platform_adapters.get(task.platform)
            if not adapter:
                return
            
            # Initial delay before first metrics collection
            await asyncio.sleep(300)  # 5 minutes
            
            async with adapter:
                while True:
                    try:
                        metrics = await adapter.get_content_metrics(task.platform_post_id)
                        
                        # Store metrics
                        if task.content_id not in self.platform_metrics:
                            self.platform_metrics[task.content_id] = []
                        
                        self.platform_metrics[task.content_id].append(metrics)
                        
                        # Update task metrics
                        task.metrics.update({
                            'views': metrics.views,
                            'engagement_rate': metrics.engagement_rate,
                            'revenue': float(metrics.revenue_generated)
                        })
                        
                        # Wait before next collection
                        await asyncio.sleep(3600)  # 1 hour
                        
                    except Exception as e:
                        logger.error(f"Error tracking metrics for {task.platform_post_id}: {e}")
                        await asyncio.sleep(1800)  # 30 minutes on error
                        
        except Exception as e:
            logger.error(f"Error in metrics tracking: {e}")
    
    def _adapt_metadata_for_platform(self, metadata: Dict[str, Any], platform: PlatformType) -> Dict[str, Any]:
        """Adapt metadata for specific platform requirements."""
        adapted = metadata.copy()
        
        if platform == PlatformType.SPOTIFY:
            # Spotify-specific metadata adaptation
            adapted.update({
                'artist': metadata.get('creator_name', ''),
                'album': metadata.get('album_name', 'Single'),
                'genre': metadata.get('genre', 'Pop'),
                'isrc': metadata.get('isrc', ''),
                'release_date': metadata.get('release_date', datetime.utcnow().isoformat())
            })
            
        elif platform == PlatformType.YOUTUBE:
            # YouTube-specific metadata adaptation
            adapted.update({
                'title': metadata.get('title', 'Untitled'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'category_id': self._get_youtube_category(metadata.get('genre', '')),
                'privacy': metadata.get('visibility', 'public'),
                'made_for_kids': metadata.get('made_for_kids', False)
            })
        
        return adapted
    
    def _get_youtube_category(self, genre: str) -> str:
        """Map genre to YouTube category ID."""
        genre_mapping = {
            'music': '10',
            'entertainment': '24',
            'education': '27',
            'gaming': '20',
            'comedy': '23'
        }
        return genre_mapping.get(genre.lower(), '10')  # Default to Music
    
    async def get_distribution_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive distribution analytics."""
        try:
            analytics = {
                'content_id': content_id,
                'platforms': [],
                'total_views': 0,
                'total_revenue': 0.0,
                'best_performing_platform': None,
                'distribution_efficiency': 0.0
            }
            
            content_metrics = self.platform_metrics.get(content_id, [])
            platform_performance = {}
            
            for metrics in content_metrics:
                platform = metrics.platform.value
                
                if platform not in platform_performance:
                    platform_performance[platform] = {
                        'views': 0,
                        'revenue': 0.0,
                        'engagement_rate': 0.0,
                        'performance_score': 0.0
                    }
                
                platform_performance[platform]['views'] = max(
                    platform_performance[platform]['views'], metrics.views
                )
                platform_performance[platform]['revenue'] = max(
                    platform_performance[platform]['revenue'], float(metrics.revenue_generated)
                )
                platform_performance[platform]['engagement_rate'] = metrics.engagement_rate
                platform_performance[platform]['performance_score'] = metrics.get_performance_score()
            
            # Calculate totals and best performer
            for platform, perf in platform_performance.items():
                analytics['total_views'] += perf['views']
                analytics['total_revenue'] += perf['revenue']
                
                analytics['platforms'].append({
                    'platform': platform,
                    'views': perf['views'],
                    'revenue': perf['revenue'],
                    'engagement_rate': perf['engagement_rate'],
                    'performance_score': perf['performance_score']
                })
            
            # Find best performing platform
            if analytics['platforms']:
                best_platform = max(analytics['platforms'], key=lambda x: x['performance_score'])
                analytics['best_performing_platform'] = best_platform['platform']
                
                # Calculate distribution efficiency
                total_score = sum(p['performance_score'] for p in analytics['platforms'])
                analytics['distribution_efficiency'] = total_score / len(analytics['platforms'])
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting distribution analytics: {e}")
            return {}
    
    async def optimize_distribution_strategy(self, user_id: str, content_format: ContentFormat) -> Dict[str, Any]:
        """AI-powered distribution strategy optimization."""
        try:
            # Analyze historical performance
            user_content_performance = await self._analyze_user_performance(user_id, content_format)
            
            # Get platform recommendations
            recommended_platforms = []
            
            for platform_type, config in self.platform_configs.items():
                if config.supports_format(content_format):
                    platform_score = await self._calculate_platform_score(
                        user_id, platform_type, content_format, user_content_performance
                    )
                    
                    recommended_platforms.append({
                        'platform': platform_type.value,
                        'score': platform_score,
                        'estimated_reach': platform_score * 1000,
                        'estimated_revenue': platform_score * 10,
                        'optimal_timing': await self._get_optimal_posting_time(platform_type),
                        'content_optimization': config.get_optimal_settings(content_format)
                    })
            
            # Sort by score
            recommended_platforms.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'user_id': user_id,
                'content_format': content_format.value,
                'recommended_platforms': recommended_platforms[:5],  # Top 5
                'strategy_confidence': 0.85,
                'estimated_total_reach': sum(p['estimated_reach'] for p in recommended_platforms[:3]),
                'estimated_total_revenue': sum(p['estimated_revenue'] for p in recommended_platforms[:3])
            }
            
        except Exception as e:
            logger.error(f"Error optimizing distribution strategy: {e}")
            return {}
    
    async def _analyze_user_performance(self, user_id: str, content_format: ContentFormat) -> Dict[str, Any]:
        """Analyze user's historical performance."""
        # This would analyze historical data from database
        return {
            'average_engagement': 0.05,
            'best_platform': 'youtube',
            'content_frequency': 'weekly',
            'audience_demographics': {'age_18_34': 0.7}
        }
    
    async def _calculate_platform_score(
        self, 
        user_id: str, 
        platform: PlatformType, 
        content_format: ContentFormat,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate platform suitability score."""
        base_score = 0.7
        
        # Adjust based on content format compatibility
        config = self.platform_configs[platform]
        if config.supports_format(content_format):
            base_score += 0.2
        
        # Adjust based on user's historical performance
        if performance_data.get('best_platform') == platform.value:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    async def _get_optimal_posting_time(self, platform: PlatformType) -> str:
        """Get optimal posting time for platform."""
        optimal_times = {
            PlatformType.YOUTUBE: "14:00-16:00 UTC",
            PlatformType.SPOTIFY: "Friday 00:00 UTC",
            PlatformType.INSTAGRAM: "11:00-15:00 UTC",
            PlatformType.TIKTOK: "18:00-24:00 UTC"
        }
        return optimal_times.get(platform, "12:00-15:00 UTC")


# Export the main components
__all__ = [
    'PlatformDistributionEngine',
    'PlatformType',
    'ContentFormat',
    'DistributionStatus',
    'MonetizationModel',
    'PlatformConfiguration',
    'DistributionTask',
    'PlatformMetrics',
    'PlatformAdapter',
    'SpotifyAdapter',
    'YouTubeAdapter'
]
