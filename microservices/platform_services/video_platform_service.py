"""
🎬 VIDEO PLATFORM SERVICE - ENTERPRISE MICROSERVICE
Video platform integration service for creator content distribution and monetization.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import aiohttp

logger = logging.getLogger(__name__)

class VideoPlatform(Enum):
    """Supported video platforms"""
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    FACEBOOK_VIDEO = "facebook_video"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    TWITTER_VIDEO = "twitter_video"
    LINKEDIN_VIDEO = "linkedin_video"
    SNAPCHAT = "snapchat"
    PINTEREST_VIDEO = "pinterest_video"
    REDDIT_VIDEO = "reddit_video"
    TWITCH_CLIPS = "twitch_clips"
    RUMBLE = "rumble"
    ODYSSEY = "odyssey"
    BITCHUTE = "bitchute"

class VideoCategory(Enum):
    """Video content categories"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    MUSIC = "music"
    GAMING = "gaming"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    TRAVEL = "travel"
    COOKING = "cooking"
    FITNESS = "fitness"
    BUSINESS = "business"
    NEWS = "news"
    DOCUMENTARY = "documentary"
    COMEDY = "comedy"
    TUTORIAL = "tutorial"
    REVIEW = "review"

class VideoStatus(Enum):
    """Video publishing status"""
    DRAFT = "draft"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    MONETIZED = "monetized"
    DEMONETIZED = "demonetized"
    REMOVED = "removed"
    COPYRIGHT_CLAIMED = "copyright_claimed"

@dataclass
class VideoContent:
    """Video content definition"""
    video_id: str
    title: str
    description: str
    category: VideoCategory
    creator_id: str
    file_path: str
    thumbnail_path: Optional[str] = None
    duration_seconds: int = 0
    resolution: str = "1080p"
    tags: List[str] = None
    language: str = "en"
    monetization_enabled: bool = True
    age_restriction: bool = False
    privacy_setting: str = "public"
    scheduled_publish: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PlatformVideoConfig:
    """Video platform configuration"""
    platform: VideoPlatform
    api_endpoint: str
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    enabled: bool = True
    max_file_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    max_duration: int = 3600  # 1 hour
    supported_formats: List[str] = None
    monetization_available: bool = True
    auto_captions: bool = True
    analytics_enabled: bool = True
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.mp4', '.mov', '.avi', '.mkv']

@dataclass
class VideoPublishResult:
    """Video publishing result"""
    result_id: str
    video_id: str
    platform: VideoPlatform
    status: VideoStatus
    platform_video_id: Optional[str] = None
    platform_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    revenue: float = 0.0
    cpm: float = 0.0
    watch_time_minutes: int = 0
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

class VideoPlatformService:
    """
    🎬 Video Platform Service
    
    Comprehensive video platform integration service supporting multiple
    video platforms, content distribution, analytics, and creator monetization.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Platform configurations
        self.platform_configs: Dict[VideoPlatform, PlatformVideoConfig] = {}
        
        # Content cache
        self.video_cache: Dict[str, VideoContent] = {}
        self.publish_results: Dict[str, VideoPublishResult] = {}
        
        # Platform adapters
        self.platform_adapters = {}
        
        # Analytics
        self.analytics = {
            'total_uploads': 0,
            'total_views': 0,
            'total_revenue': 0.0,
            'total_watch_time': 0,
            'platform_performance': {},
            'top_performing_videos': []
        }
        
        # Content optimization
        self.optimization_rules = {
            'title_max_length': {
                VideoPlatform.YOUTUBE: 100,
                VideoPlatform.TIKTOK: 150,
                VideoPlatform.INSTAGRAM_REELS: 125
            },
            'description_max_length': {
                VideoPlatform.YOUTUBE: 5000,
                VideoPlatform.TIKTOK: 2200,
                VideoPlatform.VIMEO: 5000
            },
            'optimal_durations': {
                VideoPlatform.TIKTOK: (15, 60),  # 15 seconds to 1 minute
                VideoPlatform.INSTAGRAM_REELS: (15, 90),
                VideoPlatform.YOUTUBE: (300, 600),  # 5-10 minutes
                VideoPlatform.FACEBOOK_VIDEO: (60, 300)  # 1-5 minutes
            }
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize video platform service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load platform configurations
            await self._load_platform_configs()
            
            # Initialize platform adapters
            await self._initialize_platform_adapters()
            
            # Load cached content
            await self._load_cached_videos()
            
            # Start background tasks
            asyncio.create_task(self._analytics_sync_task())
            asyncio.create_task(self._content_monitoring_task())
            asyncio.create_task(self._optimization_analysis_task())
            
            self.running = True
            logger.info("Video Platform service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize video platform service: {e}")
            raise
            
    async def _load_platform_configs(self):
        """Load platform configurations"""
        try:
            configs_data = await self.redis.get("video_platforms:configs")
            if configs_data:
                configs = json.loads(configs_data)
                for config_data in configs:
                    config = PlatformVideoConfig(**config_data)
                    self.platform_configs[config.platform] = config
                    
            # Initialize default configs if none loaded
            if not self.platform_configs:
                await self._initialize_default_configs()
                
        except Exception as e:
            logger.error(f"Failed to load platform configs: {e}")
            await self._initialize_default_configs()
            
    async def _initialize_default_configs(self):
        """Initialize default platform configurations"""
        default_configs = [
            PlatformVideoConfig(
                platform=VideoPlatform.YOUTUBE,
                api_endpoint="https://www.googleapis.com/youtube/v3",
                client_id="youtube_client_id",
                client_secret="youtube_client_secret",
                max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
                max_duration=12 * 3600,  # 12 hours
                monetization_available=True,
                auto_captions=True
            ),
            PlatformVideoConfig(
                platform=VideoPlatform.VIMEO,
                api_endpoint="https://api.vimeo.com",
                client_id="vimeo_client_id",
                client_secret="vimeo_client_secret",
                max_file_size=5 * 1024 * 1024 * 1024,  # 5GB
                monetization_available=True
            ),
            PlatformVideoConfig(
                platform=VideoPlatform.TIKTOK,
                api_endpoint="https://open-api.tiktok.com",
                client_id="tiktok_client_id",
                client_secret="tiktok_client_secret",
                max_duration=180,  # 3 minutes
                max_file_size=2 * 1024 * 1024 * 1024,  # 2GB
                monetization_available=True
            ),
            PlatformVideoConfig(
                platform=VideoPlatform.INSTAGRAM_REELS,
                api_endpoint="https://graph.facebook.com",
                client_id="instagram_client_id",
                client_secret="instagram_client_secret",
                max_duration=90,  # 90 seconds
                max_file_size=1024 * 1024 * 1024,  # 1GB
                monetization_available=True
            ),
            PlatformVideoConfig(
                platform=VideoPlatform.FACEBOOK_VIDEO,
                api_endpoint="https://graph.facebook.com",
                client_id="facebook_client_id",
                client_secret="facebook_client_secret",
                max_file_size=10 * 1024 * 1024 * 1024,  # 10GB
                monetization_available=True
            )
        ]
        
        for config in default_configs:
            self.platform_configs[config.platform] = config
            
        await self._save_platform_configs()
        
    async def _initialize_platform_adapters(self):
        """Initialize platform-specific adapters"""
        self.platform_adapters = {
            VideoPlatform.YOUTUBE: YouTubeAdapter(),
            VideoPlatform.VIMEO: VimeoAdapter(),
            VideoPlatform.TIKTOK: TikTokAdapter(),
            VideoPlatform.INSTAGRAM_REELS: InstagramReelsAdapter(),
            VideoPlatform.FACEBOOK_VIDEO: FacebookVideoAdapter()
        }
        
    async def _load_cached_videos(self):
        """Load cached videos from Redis"""
        try:
            video_keys = await self.redis.keys("video_content:*")
            for key in video_keys:
                video_data = await self.redis.get(key)
                if video_data:
                    video = VideoContent(**json.loads(video_data))
                    self.video_cache[video.video_id] = video
        except Exception as e:
            logger.error(f"Failed to load cached videos: {e}")
            
    async def upload_video(self, video: VideoContent) -> str:
        """Upload video content"""
        try:
            # Validate video
            await self._validate_video(video)
            
            # Store video
            self.video_cache[video.video_id] = video
            
            # Cache in Redis
            await self.redis.setex(
                f"video_content:{video.video_id}",
                86400,  # 24 hours
                json.dumps(asdict(video), default=str)
            )
            
            # Update analytics
            self.analytics['total_uploads'] += 1
            
            logger.info(f"Video uploaded: {video.video_id}")
            return video.video_id
            
        except Exception as e:
            logger.error(f"Failed to upload video {video.video_id}: {e}")
            raise
            
    async def _validate_video(self, video: VideoContent):
        """Validate video content"""
        # Check required fields
        if not video.title or not video.description:
            raise ValueError("Title and description are required")
            
        # Check file path
        if not video.file_path:
            raise ValueError("File path is required")
            
        # Check duration
        if video.duration_seconds <= 0:
            raise ValueError("Valid duration is required")
            
        # Check category
        if video.category not in VideoCategory:
            raise ValueError(f"Invalid category: {video.category}")
            
    async def optimize_for_platform(self, video_id: str, platform: VideoPlatform) -> VideoContent:
        """Optimize video content for specific platform"""
        if video_id not in self.video_cache:
            raise ValueError(f"Video {video_id} not found")
            
        video = self.video_cache[video_id]
        optimized_video = VideoContent(**asdict(video))
        
        # Optimize title length
        title_max = self.optimization_rules['title_max_length'].get(platform)
        if title_max and len(optimized_video.title) > title_max:
            optimized_video.title = optimized_video.title[:title_max-3] + "..."
            
        # Optimize description length
        desc_max = self.optimization_rules['description_max_length'].get(platform)
        if desc_max and len(optimized_video.description) > desc_max:
            optimized_video.description = optimized_video.description[:desc_max-3] + "..."
            
        # Add platform-specific optimizations
        if platform == VideoPlatform.TIKTOK:
            # Add trending hashtags for TikTok
            trending_tags = ["#fyp", "#viral", "#trending"]
            optimized_video.tags.extend([tag for tag in trending_tags if tag not in optimized_video.tags])
            
        elif platform == VideoPlatform.YOUTUBE:
            # Optimize for YouTube SEO
            if "youtube" not in optimized_video.tags:
                optimized_video.tags.append("youtube")
                
        elif platform == VideoPlatform.INSTAGRAM_REELS:
            # Instagram-specific optimizations
            instagram_tags = ["#reels", "#instagram"]
            optimized_video.tags.extend([tag for tag in instagram_tags if tag not in optimized_video.tags])
            
        return optimized_video
        
    async def publish_to_platform(self, video_id: str, platform: VideoPlatform,
                                 publish_options: Optional[Dict[str, Any]] = None) -> VideoPublishResult:
        """Publish video to specific platform"""
        try:
            # Get and optimize video for platform
            optimized_video = await self.optimize_for_platform(video_id, platform)
            
            # Get platform config
            if platform not in self.platform_configs:
                raise ValueError(f"Platform {platform} not configured")
                
            config = self.platform_configs[platform]
            
            if not config.enabled:
                raise ValueError(f"Platform {platform} is disabled")
                
            # Validate against platform constraints
            await self._validate_platform_constraints(optimized_video, config)
            
            # Get platform adapter
            adapter = self.platform_adapters.get(platform)
            if not adapter:
                raise ValueError(f"No adapter available for platform {platform}")
                
            # Publish video
            publish_result = await adapter.publish_video(optimized_video, config, publish_options)
            
            # Store result
            self.publish_results[publish_result.result_id] = publish_result
            
            # Update platform performance
            await self._update_platform_performance(platform, publish_result)
            
            return publish_result
            
        except Exception as e:
            logger.error(f"Failed to publish video {video_id} to {platform}: {e}")
            raise
            
    async def _validate_platform_constraints(self, video: VideoContent, config: PlatformVideoConfig):
        """Validate video against platform constraints"""
        # Check file size (simulated)
        file_size = video.metadata.get('file_size', 0)
        if file_size > config.max_file_size:
            raise ValueError(f"File size {file_size} exceeds platform limit {config.max_file_size}")
            
        # Check duration
        if video.duration_seconds > config.max_duration:
            raise ValueError(f"Duration {video.duration_seconds}s exceeds platform limit {config.max_duration}s")
            
        # Check format (simulated)
        file_extension = video.metadata.get('file_extension', '.mp4')
        if file_extension not in config.supported_formats:
            raise ValueError(f"Format {file_extension} not supported on platform")
            
    async def publish_to_multiple_platforms(self, video_id: str, 
                                          platforms: List[VideoPlatform],
                                          publish_options: Optional[Dict[str, Any]] = None) -> List[VideoPublishResult]:
        """Publish video to multiple platforms"""
        results = []
        
        for platform in platforms:
            try:
                result = await self.publish_to_platform(video_id, platform, publish_options)
                results.append(result)
            except Exception as e:
                # Create failed result
                failed_result = VideoPublishResult(
                    result_id=f"failed_{video_id}_{platform.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    video_id=video_id,
                    platform=platform,
                    status=VideoStatus.REMOVED,
                    error_message=str(e)
                )
                results.append(failed_result)
                
        return results
        
    async def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a video"""
        if video_id not in self.video_cache:
            raise ValueError(f"Video {video_id} not found")
            
        video = self.video_cache[video_id]
        
        # Get publish results for this video
        video_results = [
            result for result in self.publish_results.values()
            if result.video_id == video_id
        ]
        
        # Calculate aggregate metrics
        total_views = sum(result.view_count for result in video_results)
        total_likes = sum(result.like_count for result in video_results)
        total_comments = sum(result.comment_count for result in video_results)
        total_revenue = sum(result.revenue for result in video_results)
        total_watch_time = sum(result.watch_time_minutes for result in video_results)
        
        # Platform breakdown
        platform_breakdown = {}
        for result in video_results:
            platform_key = result.platform.value
            platform_breakdown[platform_key] = {
                'views': result.view_count,
                'likes': result.like_count,
                'comments': result.comment_count,
                'revenue': result.revenue,
                'watch_time': result.watch_time_minutes,
                'status': result.status.value,
                'platform_url': result.platform_url,
                'cpm': result.cpm
            }
            
        # Calculate engagement rate
        engagement_rate = 0
        if total_views > 0:
            engagement_rate = ((total_likes + total_comments) / total_views) * 100
            
        return {
            'video_id': video_id,
            'title': video.title,
            'category': video.category.value,
            'duration_seconds': video.duration_seconds,
            'total_platforms': len(video_results),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_revenue': total_revenue,
            'total_watch_time_minutes': total_watch_time,
            'engagement_rate': round(engagement_rate, 2),
            'average_view_duration': (total_watch_time * 60 / total_views) if total_views > 0 else 0,
            'platform_breakdown': platform_breakdown,
            'performance_score': await self._calculate_performance_score(video_results)
        }
        
    async def _calculate_performance_score(self, results: List[VideoPublishResult]) -> float:
        """Calculate performance score for video"""
        if not results:
            return 0.0
            
        total_score = 0
        for result in results:
            # Score based on views, engagement, and revenue
            view_score = min(result.view_count / 1000, 100)  # Max 100 points for views
            engagement_score = min((result.like_count + result.comment_count) / 100, 50)  # Max 50 points
            revenue_score = min(result.revenue, 25)  # Max 25 points for revenue
            
            total_score += view_score + engagement_score + revenue_score
            
        return round(total_score / len(results), 2)
        
    async def get_creator_analytics(self, creator_id: str, 
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive analytics for a creator"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
            
        # Get creator videos
        creator_videos = [
            video for video in self.video_cache.values()
            if video.creator_id == creator_id
        ]
        
        # Get relevant publish results
        creator_results = []
        for result in self.publish_results.values():
            if (result.video_id in [v.video_id for v in creator_videos] and
                result.published_at and
                start_date <= result.published_at <= end_date):
                creator_results.append(result)
                
        # Calculate metrics
        total_videos = len(creator_videos)
        total_publishes = len(creator_results)
        total_views = sum(result.view_count for result in creator_results)
        total_revenue = sum(result.revenue for result in creator_results)
        total_watch_time = sum(result.watch_time_minutes for result in creator_results)
        
        # Category performance
        category_performance = {}
        for video in creator_videos:
            category = video.category.value
            if category not in category_performance:
                category_performance[category] = {'videos': 0, 'views': 0, 'revenue': 0}
                
            category_performance[category]['videos'] += 1
            
            # Add metrics from results
            video_results = [r for r in creator_results if r.video_id == video.video_id]
            category_performance[category]['views'] += sum(r.view_count for r in video_results)
            category_performance[category]['revenue'] += sum(r.revenue for r in video_results)
            
        # Platform performance
        platform_performance = {}
        for result in creator_results:
            platform_key = result.platform.value
            if platform_key not in platform_performance:
                platform_performance[platform_key] = {
                    'videos': 0, 'views': 0, 'revenue': 0, 'avg_cpm': 0
                }
                
            platform_performance[platform_key]['videos'] += 1
            platform_performance[platform_key]['views'] += result.view_count
            platform_performance[platform_key]['revenue'] += result.revenue
            
        # Calculate average CPM per platform
        for platform_key in platform_performance:
            platform_results = [r for r in creator_results if r.platform.value == platform_key]
            if platform_results:
                avg_cpm = sum(r.cpm for r in platform_results) / len(platform_results)
                platform_performance[platform_key]['avg_cpm'] = round(avg_cpm, 2)
                
        # Top performing videos
        top_videos = await self._get_top_performing_videos(creator_id, limit=5)
        
        return {
            'creator_id': creator_id,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_videos': total_videos,
            'total_publishes': total_publishes,
            'total_views': total_views,
            'total_revenue': round(total_revenue, 2),
            'total_watch_time_hours': round(total_watch_time / 60, 2),
            'average_views_per_video': round(total_views / max(total_videos, 1), 2),
            'average_revenue_per_video': round(total_revenue / max(total_videos, 1), 2),
            'category_performance': category_performance,
            'platform_performance': platform_performance,
            'top_performing_videos': top_videos,
            'growth_metrics': await self._calculate_growth_metrics(creator_id, start_date, end_date)
        }
        
    async def _get_top_performing_videos(self, creator_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing videos for creator"""
        creator_videos = [
            video for video in self.video_cache.values()
            if video.creator_id == creator_id
        ]
        
        video_scores = []
        for video in creator_videos:
            results = [
                result for result in self.publish_results.values()
                if result.video_id == video.video_id
            ]
            
            total_views = sum(r.view_count for r in results)
            total_revenue = sum(r.revenue for r in results)
            performance_score = await self._calculate_performance_score(results)
            
            video_scores.append({
                'video_id': video.video_id,
                'title': video.title,
                'category': video.category.value,
                'total_views': total_views,
                'total_revenue': round(total_revenue, 2),
                'performance_score': performance_score
            })
            
        # Sort by performance score
        video_scores.sort(key=lambda x: x['performance_score'], reverse=True)
        return video_scores[:limit]
        
    async def _calculate_growth_metrics(self, creator_id: str, 
                                      start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate growth metrics for creator"""
        # This would typically compare with previous period
        # For now, return simplified growth metrics
        
        return {
            'view_growth_rate': 15.2,  # Simulated
            'revenue_growth_rate': 22.8,  # Simulated
            'subscriber_growth_rate': 8.5,  # Simulated
            'engagement_growth_rate': 12.1  # Simulated
        }
        
    async def _update_platform_performance(self, platform: VideoPlatform, result: VideoPublishResult):
        """Update platform performance metrics"""
        platform_key = platform.value
        
        if platform_key not in self.analytics['platform_performance']:
            self.analytics['platform_performance'][platform_key] = {
                'total_videos': 0,
                'total_views': 0,
                'total_revenue': 0.0,
                'avg_cpm': 0.0,
                'success_rate': 100.0
            }
            
        perf = self.analytics['platform_performance'][platform_key]
        perf['total_videos'] += 1
        perf['total_views'] += result.view_count
        perf['total_revenue'] += result.revenue
        
        # Update global analytics
        self.analytics['total_views'] += result.view_count
        self.analytics['total_revenue'] += result.revenue
        self.analytics['total_watch_time'] += result.watch_time_minutes
        
    async def _analytics_sync_task(self):
        """Background task for syncing analytics from platforms"""
        while self.running:
            try:
                for platform in self.platform_configs:
                    if platform in self.platform_adapters:
                        adapter = self.platform_adapters[platform]
                        config = self.platform_configs[platform]
                        
                        if config.analytics_enabled:
                            # Sync analytics data
                            analytics_data = await adapter.sync_analytics(config)
                            
                            # Update local results with fresh data
                            for result_id, updated_data in analytics_data.items():
                                if result_id in self.publish_results:
                                    result = self.publish_results[result_id]
                                    result.view_count = updated_data.get('views', result.view_count)
                                    result.like_count = updated_data.get('likes', result.like_count)
                                    result.comment_count = updated_data.get('comments', result.comment_count)
                                    result.revenue = updated_data.get('revenue', result.revenue)
                                    result.watch_time_minutes = updated_data.get('watch_time', result.watch_time_minutes)
                                    result.last_updated = datetime.utcnow()
                                    
                await asyncio.sleep(1800)  # Sync every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in analytics sync task: {e}")
                await asyncio.sleep(1800)
                
    async def _content_monitoring_task(self):
        """Background task for monitoring content status"""
        while self.running:
            try:
                # Check status of published videos
                for result in self.publish_results.values():
                    if result.status in [VideoStatus.PROCESSING, VideoStatus.UPLOADING]:
                        # Check if processing is complete
                        platform = result.platform
                        if platform in self.platform_adapters:
                            adapter = self.platform_adapters[platform]
                            config = self.platform_configs.get(platform)
                            
                            if config:
                                updated_status = await adapter.check_video_status(
                                    result.platform_video_id, config
                                )
                                if updated_status != result.status:
                                    result.status = updated_status
                                    logger.info(f"Video {result.video_id} status updated to {updated_status}")
                                    
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in content monitoring task: {e}")
                await asyncio.sleep(600)
                
    async def _optimization_analysis_task(self):
        """Background task for analyzing content performance and optimization"""
        while self.running:
            try:
                # Analyze performance patterns
                await self._analyze_performance_patterns()
                
                # Update optimization recommendations
                await self._update_optimization_recommendations()
                
                await asyncio.sleep(3600)  # Analyze every hour
                
            except Exception as e:
                logger.error(f"Error in optimization analysis task: {e}")
                await asyncio.sleep(3600)
                
    async def _analyze_performance_patterns(self):
        """Analyze performance patterns across platforms"""
        # This would analyze which types of content perform best on which platforms
        # For now, just a placeholder
        pass
        
    async def _update_optimization_recommendations(self):
        """Update optimization recommendations based on performance data"""
        # This would update optimization rules based on performance analysis
        # For now, just a placeholder
        pass
        
    async def _save_platform_configs(self):
        """Save platform configurations to Redis"""
        try:
            configs_data = [asdict(config) for config in self.platform_configs.values()]
            await self.redis.set(
                "video_platforms:configs",
                json.dumps(configs_data, default=str)
            )
        except Exception as e:
            logger.error(f"Failed to save platform configs: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check for video platform service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        enabled_platforms = len([c for c in self.platform_configs.values() if c.enabled])
        
        return {
            'service': 'video_platform',
            'status': 'healthy' if redis_status == "healthy" else 'degraded',
            'redis': redis_status,
            'configured_platforms': len(self.platform_configs),
            'enabled_platforms': enabled_platforms,
            'cached_videos': len(self.video_cache),
            'publish_results': len(self.publish_results)
        }
        
    async def shutdown(self):
        """Shutdown video platform service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Video Platform service shut down")

# Platform adapters (simplified implementations)
class YouTubeAdapter:
    """YouTube platform adapter"""
    
    async def publish_video(self, video: VideoContent, config: PlatformVideoConfig, 
                          options: Optional[Dict[str, Any]] = None) -> VideoPublishResult:
        # Simulate YouTube publishing
        await asyncio.sleep(2.0)  # YouTube takes longer to process
        
        import random
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            return VideoPublishResult(
                result_id=f"youtube_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.YOUTUBE,
                status=VideoStatus.PUBLISHED,
                platform_video_id=f"yt_{random.randint(10000000, 99999999)}",
                platform_url=f"https://www.youtube.com/watch?v={random.randint(10000000, 99999999)}",
                view_count=random.randint(100, 10000),
                like_count=random.randint(10, 500),
                comment_count=random.randint(1, 100),
                revenue=random.uniform(5.0, 100.0),
                cpm=random.uniform(1.0, 5.0),
                published_at=datetime.utcnow()
            )
        else:
            return VideoPublishResult(
                result_id=f"youtube_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.YOUTUBE,
                status=VideoStatus.REMOVED,
                error_message="Video violates YouTube community guidelines"
            )
            
    async def sync_analytics(self, config: PlatformVideoConfig) -> Dict[str, Dict[str, Any]]:
        # Simulate analytics sync
        return {}
        
    async def check_video_status(self, platform_video_id: str, config: PlatformVideoConfig) -> VideoStatus:
        return VideoStatus.PUBLISHED

class VimeoAdapter:
    """Vimeo platform adapter"""
    
    async def publish_video(self, video: VideoContent, config: PlatformVideoConfig, 
                          options: Optional[Dict[str, Any]] = None) -> VideoPublishResult:
        await asyncio.sleep(1.5)
        
        import random
        success = random.random() > 0.02  # 98% success rate
        
        if success:
            return VideoPublishResult(
                result_id=f"vimeo_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.VIMEO,
                status=VideoStatus.PUBLISHED,
                platform_video_id=f"vm_{random.randint(100000, 999999)}",
                platform_url=f"https://vimeo.com/{random.randint(100000, 999999)}",
                view_count=random.randint(50, 5000),
                like_count=random.randint(5, 200),
                comment_count=random.randint(1, 50),
                revenue=random.uniform(2.0, 50.0),
                published_at=datetime.utcnow()
            )
        else:
            return VideoPublishResult(
                result_id=f"vimeo_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.VIMEO,
                status=VideoStatus.REMOVED,
                error_message="Content does not meet Vimeo guidelines"
            )
            
    async def sync_analytics(self, config: PlatformVideoConfig) -> Dict[str, Dict[str, Any]]:
        return {}
        
    async def check_video_status(self, platform_video_id: str, config: PlatformVideoConfig) -> VideoStatus:
        return VideoStatus.PUBLISHED

class TikTokAdapter:
    """TikTok platform adapter"""
    
    async def publish_video(self, video: VideoContent, config: PlatformVideoConfig, 
                          options: Optional[Dict[str, Any]] = None) -> VideoPublishResult:
        await asyncio.sleep(0.8)
        
        import random
        success = random.random() > 0.08  # 92% success rate
        
        if success:
            return VideoPublishResult(
                result_id=f"tiktok_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.TIKTOK,
                status=VideoStatus.PUBLISHED,
                platform_video_id=f"tt_{random.randint(1000000, 9999999)}",
                platform_url=f"https://www.tiktok.com/@user/video/{random.randint(1000000, 9999999)}",
                view_count=random.randint(1000, 100000),
                like_count=random.randint(100, 5000),
                comment_count=random.randint(10, 500),
                revenue=random.uniform(1.0, 20.0),
                published_at=datetime.utcnow()
            )
        else:
            return VideoPublishResult(
                result_id=f"tiktok_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.TIKTOK,
                status=VideoStatus.REMOVED,
                error_message="Video violates TikTok community guidelines"
            )
            
    async def sync_analytics(self, config: PlatformVideoConfig) -> Dict[str, Dict[str, Any]]:
        return {}
        
    async def check_video_status(self, platform_video_id: str, config: PlatformVideoConfig) -> VideoStatus:
        return VideoStatus.PUBLISHED

class InstagramReelsAdapter:
    """Instagram Reels platform adapter"""
    
    async def publish_video(self, video: VideoContent, config: PlatformVideoConfig, 
                          options: Optional[Dict[str, Any]] = None) -> VideoPublishResult:
        await asyncio.sleep(1.0)
        
        import random
        success = random.random() > 0.06  # 94% success rate
        
        if success:
            return VideoPublishResult(
                result_id=f"instagram_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.INSTAGRAM_REELS,
                status=VideoStatus.PUBLISHED,
                platform_video_id=f"ig_{random.randint(1000000, 9999999)}",
                platform_url=f"https://www.instagram.com/reel/{random.randint(1000000, 9999999)}",
                view_count=random.randint(500, 50000),
                like_count=random.randint(50, 2500),
                comment_count=random.randint(5, 250),
                revenue=random.uniform(0.5, 15.0),
                published_at=datetime.utcnow()
            )
        else:
            return VideoPublishResult(
                result_id=f"instagram_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.INSTAGRAM_REELS,
                status=VideoStatus.REMOVED,
                error_message="Content violates Instagram community standards"
            )
            
    async def sync_analytics(self, config: PlatformVideoConfig) -> Dict[str, Dict[str, Any]]:
        return {}
        
    async def check_video_status(self, platform_video_id: str, config: PlatformVideoConfig) -> VideoStatus:
        return VideoStatus.PUBLISHED

class FacebookVideoAdapter:
    """Facebook Video platform adapter"""
    
    async def publish_video(self, video: VideoContent, config: PlatformVideoConfig, 
                          options: Optional[Dict[str, Any]] = None) -> VideoPublishResult:
        await asyncio.sleep(1.2)
        
        import random
        success = random.random() > 0.04  # 96% success rate
        
        if success:
            return VideoPublishResult(
                result_id=f"facebook_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.FACEBOOK_VIDEO,
                status=VideoStatus.PUBLISHED,
                platform_video_id=f"fb_{random.randint(1000000, 9999999)}",
                platform_url=f"https://www.facebook.com/watch/?v={random.randint(1000000, 9999999)}",
                view_count=random.randint(200, 20000),
                like_count=random.randint(20, 1000),
                comment_count=random.randint(2, 100),
                revenue=random.uniform(1.0, 30.0),
                published_at=datetime.utcnow()
            )
        else:
            return VideoPublishResult(
                result_id=f"facebook_{video.video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                video_id=video.video_id,
                platform=VideoPlatform.FACEBOOK_VIDEO,
                status=VideoStatus.REMOVED,
                error_message="Video violates Facebook community standards"
            )
            
    async def sync_analytics(self, config: PlatformVideoConfig) -> Dict[str, Dict[str, Any]]:
        return {}
        
    async def check_video_status(self, platform_video_id: str, config: PlatformVideoConfig) -> VideoStatus:
        return VideoStatus.PUBLISHED

# Example usage
async def create_video_platform_service():
    """Factory function to create video platform service"""
    service = VideoPlatformService()
    await service.initialize()
    return service

if __name__ == "__main__":
    async def main():
        video_service = await create_video_platform_service()
        
        # Example video content
        video = VideoContent(
            video_id="video_123",
            title="How to Create Amazing Content",
            description="Learn the secrets of creating engaging video content that gets views and subscribers!",
            category=VideoCategory.EDUCATION,
            creator_id="creator_456",
            file_path="/videos/tutorial.mp4",
            duration_seconds=600,
            tags=["tutorial", "content creation", "youtube", "education"],
            monetization_enabled=True
        )
        
        # Upload video
        video_id = await video_service.upload_video(video)
        print(f"Video uploaded: {video_id}")
        
        # Publish to multiple platforms
        platforms = [VideoPlatform.YOUTUBE, VideoPlatform.TIKTOK, VideoPlatform.INSTAGRAM_REELS]
        results = await video_service.publish_to_multiple_platforms(video_id, platforms)
        
        for result in results:
            print(f"Platform: {result.platform.value}, Status: {result.status.value}")
            if result.platform_url:
                print(f"URL: {result.platform_url}")
                
        # Get analytics
        analytics = await video_service.get_video_analytics(video_id)
        print(f"Video analytics: {analytics}")
        
        await video_service.shutdown()
        
    asyncio.run(main())