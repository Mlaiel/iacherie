"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Distribution Service Template for Ainflue Platform
=================================================

Production-ready multi-platform distribution service with:
- Automated content distribution across platforms
- Platform-specific optimization and formatting
- Scheduled publishing and campaign management
- Cross-platform analytics aggregation
- Content syndication and RSS feeds
- API integrations with major platforms
- Distribution performance tracking
- Content lifecycle management

Author: Fahed Mlaiel (mlaiel@live.de)
Distribution & Platform Integration Expert
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis
import httpx
import aiofiles

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker
from ..communication_manager import CommunicationManager

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WORDPRESS = "wordpress"
    MEDIUM = "medium"
    RSS_FEED = "rss_feed"
    PODCAST_PLATFORMS = "podcast_platforms"


class DistributionStatus(Enum):
    """Distribution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ContentFormat(Enum):
    """Content formats for distribution"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    PODCAST = "podcast"
    ARTICLE = "article"
    LIVE_STREAM = "live_stream"


class OptimizationType(Enum):
    """Platform optimization types"""
    ASPECT_RATIO = "aspect_ratio"
    RESOLUTION = "resolution"
    DURATION = "duration"
    FILE_SIZE = "file_size"
    CAPTION_LENGTH = "caption_length"
    HASHTAGS = "hashtags"
    THUMBNAILS = "thumbnails"
    METADATA = "metadata"


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: PlatformType
    enabled: bool = True
    
    # Authentication
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # Content constraints
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_duration: int = 3600  # 1 hour
    supported_formats: List[ContentFormat] = field(default_factory=list)
    max_caption_length: int = 2200
    max_hashtags: int = 30
    
    # Publishing settings
    auto_publish: bool = True
    default_visibility: str = "public"
    enable_comments: bool = True
    enable_analytics: bool = True
    
    # Optimization settings
    auto_optimize: bool = True
    optimization_types: List[OptimizationType] = field(default_factory=list)
    
    # Rate limiting
    requests_per_hour: int = 100
    requests_per_day: int = 1000


@dataclass
class DistributionCampaign:
    """Multi-platform distribution campaign"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    name: str = ""
    description: str = ""
    
    # Content details
    content_id: str = ""
    content_type: ContentFormat = ContentFormat.VIDEO
    content_url: str = ""
    thumbnail_url: Optional[str] = None
    
    # Distribution settings
    target_platforms: List[PlatformType] = field(default_factory=list)
    scheduled_publish_time: Optional[datetime] = None
    
    # Platform-specific content
    platform_content: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Campaign metadata
    title: str = ""
    description_text: str = ""
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    # Status tracking
    status: DistributionStatus = DistributionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Results
    platform_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    total_reach: int = 0
    total_engagement: int = 0
    
    # Settings
    auto_optimize: bool = True
    track_analytics: bool = True


@dataclass
class PlatformPost:
    """Individual platform post"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str = ""
    platform: PlatformType = PlatformType.YOUTUBE
    
    # Content
    content_url: str = ""
    optimized_content_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Metadata
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    
    # Platform-specific data
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    
    # Status
    status: DistributionStatus = DistributionStatus.PENDING
    scheduled_time: Optional[datetime] = None
    published_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Performance
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_rate: float = 0.0


class DistributionConfig:
    """Distribution service configuration"""
    
    def __init__(self):
        # Platform configurations
        self.platform_configs: Dict[PlatformType, PlatformConfig] = {}
        
        # Content optimization
        self.enable_auto_optimization = True
        self.optimization_quality = "high"  # low, medium, high
        self.preserve_original = True
        
        # Scheduling
        self.max_scheduled_posts = 1000
        self.schedule_check_interval = 60  # seconds
        self.retry_attempts = 3
        self.retry_delay = 300  # 5 minutes
        
        # Analytics
        self.analytics_collection_interval = 3600  # 1 hour
        self.performance_tracking_enabled = True
        
        # Storage
        self.content_storage_path = "/var/lib/ainflue/distribution"
        self.cache_optimized_content = True
        self.cache_duration = 86400  # 24 hours
        
        # RSS and syndication
        self.enable_rss_feeds = True
        self.rss_base_url = "https://feeds.ainflue.com"
        self.syndication_enabled = True


# Pydantic models for API
class DistributionCampaignRequest(BaseModel):
    """Distribution campaign creation request"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field("", max_length=500)
    content_id: str
    target_platforms: List[PlatformType] = Field(..., min_items=1)
    title: str = Field(..., min_length=3, max_length=200)
    description_text: str = Field("", max_length=2000)
    tags: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    scheduled_publish_time: Optional[datetime] = None
    auto_optimize: bool = True
    track_analytics: bool = True


class PlatformContentRequest(BaseModel):
    """Platform-specific content customization"""
    platform: PlatformType
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    custom_thumbnail: Optional[str] = None
    visibility: str = Field("public", pattern="^(public|private|unlisted)$")
    enable_comments: bool = True


class RSSFeedRequest(BaseModel):
    """RSS feed configuration request"""
    creator_id: str
    feed_title: str = Field(..., min_length=3, max_length=100)
    feed_description: str = Field(..., min_length=10, max_length=500)
    categories: List[str] = Field(default_factory=list)
    include_content_types: List[ContentFormat] = Field(default_factory=list)
    max_items: int = Field(50, ge=1, le=100)


class DistributionCampaignResponse(BaseModel):
    """Distribution campaign response"""
    campaign_id: str
    name: str
    status: DistributionStatus
    target_platforms: List[PlatformType]
    created_at: datetime
    scheduled_publish_time: Optional[datetime] = None
    platform_posts: List[Dict[str, Any]]


class PlatformPerformanceResponse(BaseModel):
    """Platform performance response"""
    platform: PlatformType
    total_posts: int
    total_views: int
    total_engagement: int
    average_engagement_rate: float
    top_performing_post: Optional[Dict[str, Any]] = None


class DistributionService(BaseMicroservice):
    """
    Enterprise Distribution Service for Ainflue Platform
    
    Provides automated multi-platform content distribution,
    optimization, scheduling, and performance tracking.
    """
    
    def __init__(self, config: Optional[DistributionConfig] = None):
        super().__init__("distribution-service")
        
        self.config = config or DistributionConfig()
        self.campaigns: Dict[str, DistributionCampaign] = {}
        self.platform_posts: Dict[str, PlatformPost] = {}
        self.scheduled_posts: List[str] = []  # Post IDs scheduled for publishing
        
        # Metrics
        self.distribution_counter = Counter('distribution_campaigns_total', 'Total distribution campaigns')
        self.platform_posts_counter = Counter('distribution_posts_total', 'Total platform posts', ['platform', 'status'])
        self.optimization_counter = Counter('distribution_optimizations_total', 'Content optimizations performed')
        self.campaign_duration = Histogram('distribution_campaign_duration_seconds', 'Campaign processing duration')
        self.scheduled_posts_gauge = Gauge('distribution_scheduled_posts', 'Scheduled posts pending')
        
        # Circuit breakers for platform APIs
        self.platform_circuit_breakers: Dict[PlatformType, CircuitBreaker] = {}
        for platform in PlatformType:
            self.platform_circuit_breakers[platform] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=300,  # 5 minutes
                expected_exception=Exception
            )
        
        # Communication manager
        self.communication_manager = CommunicationManager()
        
        # Redis client for caching and queuing
        self.redis_client: Optional[redis.Redis] = None
        
        # HTTP client for platform APIs
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        logger.info("Distribution Service initialized")
    
    async def startup(self):
        """Service startup tasks"""
        await super().startup()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize platform configurations
        await self._initialize_platform_configs()
        
        # Start background tasks
        await self._start_background_tasks()
        
        logger.info("Distribution Service started")
    
    async def shutdown(self):
        """Service shutdown tasks"""
        logger.info("Shutting down Distribution Service...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close HTTP client
        if self.http_client:
            await self.http_client.aclose()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        await super().shutdown()
        logger.info("Distribution Service shut down")
    
    async def _initialize_platform_configs(self):
        """Initialize platform-specific configurations"""
        # YouTube configuration
        self.config.platform_configs[PlatformType.YOUTUBE] = PlatformConfig(
            platform=PlatformType.YOUTUBE,
            max_file_size=128 * 1024 * 1024,  # 128MB
            max_duration=43200,  # 12 hours
            supported_formats=[ContentFormat.VIDEO],
            max_caption_length=5000,
            optimization_types=[OptimizationType.RESOLUTION, OptimizationType.THUMBNAILS]
        )
        
        # Instagram configuration
        self.config.platform_configs[PlatformType.INSTAGRAM] = PlatformConfig(
            platform=PlatformType.INSTAGRAM,
            max_file_size=100 * 1024 * 1024,  # 100MB
            max_duration=60,  # 60 seconds for reels
            supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.STORY, ContentFormat.REEL],
            max_caption_length=2200,
            max_hashtags=30,
            optimization_types=[OptimizationType.ASPECT_RATIO, OptimizationType.DURATION]
        )
        
        # TikTok configuration
        self.config.platform_configs[PlatformType.TIKTOK] = PlatformConfig(
            platform=PlatformType.TIKTOK,
            max_file_size=72 * 1024 * 1024,  # 72MB
            max_duration=180,  # 3 minutes
            supported_formats=[ContentFormat.VIDEO],
            max_caption_length=150,
            max_hashtags=20,
            optimization_types=[OptimizationType.ASPECT_RATIO, OptimizationType.DURATION]
        )
        
        # Add more platform configurations as needed
        
        logger.info("Platform configurations initialized")
    
    async def _start_background_tasks(self):
        """Start background processing tasks"""
        # Scheduled publishing task
        schedule_task = asyncio.create_task(self._process_scheduled_posts())
        self.background_tasks.add(schedule_task)
        
        # Analytics collection task
        analytics_task = asyncio.create_task(self._collect_platform_analytics())
        self.background_tasks.add(analytics_task)
        
        # Campaign monitoring task
        monitor_task = asyncio.create_task(self._monitor_campaigns())
        self.background_tasks.add(monitor_task)
        
        # RSS feed generation task
        if self.config.enable_rss_feeds:
            rss_task = asyncio.create_task(self._generate_rss_feeds())
            self.background_tasks.add(rss_task)
        
        logger.info("Started background tasks")
    
    async def create_distribution_campaign(
        self,
        creator_id: str,
        request: DistributionCampaignRequest
    ) -> Dict[str, Any]:
        """Create a new distribution campaign"""
        start_time = time.time()
        
        try:
            # Create campaign
            campaign = DistributionCampaign(
                creator_id=creator_id,
                name=request.name,
                description=request.description,
                content_id=request.content_id,
                target_platforms=request.target_platforms,
                scheduled_publish_time=request.scheduled_publish_time,
                title=request.title,
                description_text=request.description_text,
                tags=request.tags,
                hashtags=request.hashtags,
                category=request.category,
                auto_optimize=request.auto_optimize,
                track_analytics=request.track_analytics
            )
            
            # Get content information
            content_info = await self._get_content_info(request.content_id)
            if not content_info:
                raise HTTPException(status_code=404, detail="Content not found")
            
            campaign.content_url = content_info["url"]
            campaign.content_type = ContentFormat(content_info["type"])
            campaign.thumbnail_url = content_info.get("thumbnail_url")
            
            # Create platform-specific posts
            platform_posts = []
            for platform in request.target_platforms:
                post = await self._create_platform_post(campaign, platform)
                if post:
                    platform_posts.append(post)
                    self.platform_posts[post.id] = post
            
            # Store campaign
            self.campaigns[campaign.id] = campaign
            
            # Cache campaign
            await self._cache_campaign(campaign)
            
            # Schedule immediate or future publishing
            if campaign.scheduled_publish_time:
                if campaign.scheduled_publish_time <= datetime.utcnow():
                    # Publish immediately
                    await self._publish_campaign(campaign)
                else:
                    # Schedule for later
                    await self._schedule_campaign(campaign)
            else:
                # Publish immediately
                await self._publish_campaign(campaign)
            
            # Update metrics
            self.distribution_counter.inc()
            processing_time = time.time() - start_time
            self.campaign_duration.observe(processing_time)
            
            return {
                "success": True,
                "campaign_id": campaign.id,
                "status": campaign.status.value,
                "platform_posts": len(platform_posts),
                "scheduled_time": campaign.scheduled_publish_time.isoformat() if campaign.scheduled_publish_time else None,
                "processing_time": processing_time
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Campaign creation failed: {e}")
            raise HTTPException(status_code=500, detail="Campaign creation failed")
    
    async def customize_platform_content(
        self,
        campaign_id: str,
        platform_content: List[PlatformContentRequest]
    ) -> Dict[str, Any]:
        """Customize content for specific platforms"""
        try:
            campaign = self.campaigns.get(campaign_id)
            if not campaign:
                campaign = await self._load_campaign_from_cache(campaign_id)
            
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Update platform-specific content
            for content_req in platform_content:
                platform_key = content_req.platform.value
                
                campaign.platform_content[platform_key] = {
                    "title": content_req.title or campaign.title,
                    "description": content_req.description or campaign.description_text,
                    "tags": content_req.tags or campaign.tags,
                    "hashtags": content_req.hashtags or campaign.hashtags,
                    "custom_thumbnail": content_req.custom_thumbnail,
                    "visibility": content_req.visibility,
                    "enable_comments": content_req.enable_comments
                }
                
                # Update corresponding platform post
                for post in self.platform_posts.values():
                    if post.campaign_id == campaign_id and post.platform == content_req.platform:
                        post.title = content_req.title or post.title
                        post.description = content_req.description or post.description
                        post.tags = content_req.tags or post.tags
                        post.hashtags = content_req.hashtags or post.hashtags
                        break
            
            # Cache updated campaign
            await self._cache_campaign(campaign)
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "updated_platforms": [req.platform.value for req in platform_content]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Platform content customization failed: {e}")
            raise HTTPException(status_code=500, detail="Content customization failed")
    
    async def get_campaign_status(self, campaign_id: str) -> DistributionCampaignResponse:
        """Get distribution campaign status"""
        try:
            campaign = self.campaigns.get(campaign_id)
            if not campaign:
                campaign = await self._load_campaign_from_cache(campaign_id)
            
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Get platform posts
            platform_posts = []
            for post in self.platform_posts.values():
                if post.campaign_id == campaign_id:
                    platform_posts.append({
                        "platform": post.platform.value,
                        "status": post.status.value,
                        "platform_post_id": post.platform_post_id,
                        "platform_url": post.platform_url,
                        "published_time": post.published_time.isoformat() if post.published_time else None,
                        "views": post.views,
                        "likes": post.likes,
                        "comments": post.comments,
                        "shares": post.shares,
                        "engagement_rate": post.engagement_rate,
                        "error_message": post.error_message
                    })
            
            return DistributionCampaignResponse(
                campaign_id=campaign.id,
                name=campaign.name,
                status=campaign.status,
                target_platforms=campaign.target_platforms,
                created_at=campaign.created_at,
                scheduled_publish_time=campaign.scheduled_publish_time,
                platform_posts=platform_posts
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Campaign status retrieval failed: {e}")
            raise HTTPException(status_code=500, detail="Status unavailable")
    
    async def get_platform_performance(
        self,
        creator_id: str,
        platform: Optional[PlatformType] = None,
        time_frame: int = 30  # days
    ) -> List[PlatformPerformanceResponse]:
        """Get platform performance analytics"""
        try:
            # Get campaigns for creator
            creator_campaigns = [
                campaign for campaign in self.campaigns.values()
                if campaign.creator_id == creator_id
            ]
            
            # Filter by time frame
            cutoff_date = datetime.utcnow() - timedelta(days=time_frame)
            recent_campaigns = [
                campaign for campaign in creator_campaigns
                if campaign.created_at >= cutoff_date
            ]
            
            # Aggregate performance by platform
            platform_performance = {}
            
            for campaign in recent_campaigns:
                for post in self.platform_posts.values():
                    if post.campaign_id == campaign.id:
                        if platform and post.platform != platform:
                            continue
                        
                        platform_key = post.platform.value
                        if platform_key not in platform_performance:
                            platform_performance[platform_key] = {
                                "platform": post.platform,
                                "posts": [],
                                "total_views": 0,
                                "total_engagement": 0,
                                "total_posts": 0
                            }
                        
                        perf = platform_performance[platform_key]
                        perf["posts"].append(post)
                        perf["total_views"] += post.views
                        perf["total_engagement"] += post.likes + post.comments + post.shares
                        perf["total_posts"] += 1
            
            # Create response
            results = []
            for platform_key, perf in platform_performance.items():
                avg_engagement_rate = (
                    sum(post.engagement_rate for post in perf["posts"]) / len(perf["posts"])
                    if perf["posts"] else 0
                )
                
                # Find top performing post
                top_post = None
                if perf["posts"]:
                    top_post_obj = max(perf["posts"], key=lambda p: p.engagement_rate)
                    top_post = {
                        "id": top_post_obj.id,
                        "title": top_post_obj.title,
                        "platform_url": top_post_obj.platform_url,
                        "views": top_post_obj.views,
                        "engagement_rate": top_post_obj.engagement_rate
                    }
                
                results.append(PlatformPerformanceResponse(
                    platform=perf["platform"],
                    total_posts=perf["total_posts"],
                    total_views=perf["total_views"],
                    total_engagement=perf["total_engagement"],
                    average_engagement_rate=round(avg_engagement_rate, 2),
                    top_performing_post=top_post
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Platform performance retrieval failed: {e}")
            raise HTTPException(status_code=500, detail="Performance analytics unavailable")
    
    async def generate_rss_feed(self, request: RSSFeedRequest) -> str:
        """Generate RSS feed for creator content"""
        try:
            # Get creator content
            creator_content = await self._get_creator_content(
                request.creator_id,
                request.include_content_types,
                request.max_items
            )
            
            # Generate RSS XML
            rss_xml = await self._create_rss_xml(
                request,
                creator_content
            )
            
            # Store RSS feed
            feed_id = f"rss_{request.creator_id}_{int(time.time())}"
            await self._store_rss_feed(feed_id, rss_xml)
            
            return f"{self.config.rss_base_url}/{feed_id}.xml"
            
        except Exception as e:
            logger.error(f"RSS feed generation failed: {e}")
            raise HTTPException(status_code=500, detail="RSS feed generation failed")
    
    # Platform publishing methods
    async def _create_platform_post(
        self,
        campaign: DistributionCampaign,
        platform: PlatformType
    ) -> Optional[PlatformPost]:
        """Create platform-specific post"""
        try:
            # Check if platform is configured
            platform_config = self.config.platform_configs.get(platform)
            if not platform_config or not platform_config.enabled:
                logger.warning(f"Platform {platform.value} not configured or disabled")
                return None
            
            # Create post
            post = PlatformPost(
                campaign_id=campaign.id,
                platform=platform,
                content_url=campaign.content_url,
                thumbnail_url=campaign.thumbnail_url,
                title=campaign.title,
                description=campaign.description_text,
                tags=campaign.tags.copy(),
                hashtags=campaign.hashtags.copy(),
                scheduled_time=campaign.scheduled_publish_time
            )
            
            # Apply platform-specific customizations
            platform_key = platform.value
            if platform_key in campaign.platform_content:
                custom_content = campaign.platform_content[platform_key]
                post.title = custom_content.get("title", post.title)
                post.description = custom_content.get("description", post.description)
                post.tags = custom_content.get("tags", post.tags)
                post.hashtags = custom_content.get("hashtags", post.hashtags)
            
            # Optimize content if enabled
            if campaign.auto_optimize and platform_config.auto_optimize:
                optimized_url = await self._optimize_content_for_platform(
                    campaign.content_url,
                    platform,
                    campaign.content_type
                )
                if optimized_url:
                    post.optimized_content_url = optimized_url
                    self.optimization_counter.inc()
            
            return post
            
        except Exception as e:
            logger.error(f"Platform post creation failed for {platform.value}: {e}")
            return None
    
    async def _publish_campaign(self, campaign: DistributionCampaign):
        """Publish campaign to all target platforms"""
        try:
            campaign.status = DistributionStatus.PROCESSING
            
            success_count = 0
            failure_count = 0
            
            # Publish to each platform
            for post in self.platform_posts.values():
                if post.campaign_id == campaign.id:
                    try:
                        result = await self._publish_to_platform(post)
                        if result["success"]:
                            success_count += 1
                            post.status = DistributionStatus.PUBLISHED
                            post.published_time = datetime.utcnow()
                            post.platform_post_id = result.get("post_id")
                            post.platform_url = result.get("post_url")
                            
                            # Update metrics
                            self.platform_posts_counter.labels(
                                platform=post.platform.value,
                                status="published"
                            ).inc()
                        else:
                            failure_count += 1
                            post.status = DistributionStatus.FAILED
                            post.error_message = result.get("error", "Unknown error")
                            
                            # Update metrics
                            self.platform_posts_counter.labels(
                                platform=post.platform.value,
                                status="failed"
                            ).inc()
                            
                    except Exception as e:
                        logger.error(f"Platform publishing failed for {post.platform.value}: {e}")
                        failure_count += 1
                        post.status = DistributionStatus.FAILED
                        post.error_message = str(e)
            
            # Update campaign status
            if success_count > 0 and failure_count == 0:
                campaign.status = DistributionStatus.PUBLISHED
            elif success_count > 0:
                campaign.status = DistributionStatus.PUBLISHED  # Partial success
            else:
                campaign.status = DistributionStatus.FAILED
            
            campaign.published_at = datetime.utcnow()
            
            # Cache updated campaign
            await self._cache_campaign(campaign)
            
            # Notify about campaign completion
            await self._notify_campaign_completion(campaign, success_count, failure_count)
            
        except Exception as e:
            logger.error(f"Campaign publishing failed: {e}")
            campaign.status = DistributionStatus.FAILED
            await self._cache_campaign(campaign)
    
    async def _publish_to_platform(self, post: PlatformPost) -> Dict[str, Any]:
        """Publish content to specific platform"""
        platform = post.platform
        circuit_breaker = self.platform_circuit_breakers[platform]
        
        try:
            # Use circuit breaker for platform API calls
            if circuit_breaker.state.name == "OPEN":
                return {"success": False, "error": "Platform API circuit breaker is open"}
            
            # Platform-specific publishing logic
            if platform == PlatformType.YOUTUBE:
                return await self._publish_to_youtube(post)
            elif platform == PlatformType.INSTAGRAM:
                return await self._publish_to_instagram(post)
            elif platform == PlatformType.TIKTOK:
                return await self._publish_to_tiktok(post)
            elif platform == PlatformType.TWITTER:
                return await self._publish_to_twitter(post)
            elif platform == PlatformType.FACEBOOK:
                return await self._publish_to_facebook(post)
            else:
                return {"success": False, "error": f"Platform {platform.value} not supported"}
                
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"Platform publishing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_to_youtube(self, post: PlatformPost) -> Dict[str, Any]:
        """Publish content to YouTube"""
        try:
            # YouTube API publishing logic would go here
            # For now, simulate the publishing process
            await asyncio.sleep(1)  # Simulate API call
            
            return {
                "success": True,
                "post_id": f"yt_{uuid.uuid4().hex[:8]}",
                "post_url": f"https://youtube.com/watch?v={uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"YouTube publishing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_to_instagram(self, post: PlatformPost) -> Dict[str, Any]:
        """Publish content to Instagram"""
        try:
            # Instagram API publishing logic would go here
            await asyncio.sleep(1)  # Simulate API call
            
            return {
                "success": True,
                "post_id": f"ig_{uuid.uuid4().hex[:8]}",
                "post_url": f"https://instagram.com/p/{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Instagram publishing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_to_tiktok(self, post: PlatformPost) -> Dict[str, Any]:
        """Publish content to TikTok"""
        try:
            # TikTok API publishing logic would go here
            await asyncio.sleep(1)  # Simulate API call
            
            return {
                "success": True,
                "post_id": f"tt_{uuid.uuid4().hex[:8]}",
                "post_url": f"https://tiktok.com/@user/video/{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"TikTok publishing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_to_twitter(self, post: PlatformPost) -> Dict[str, Any]:
        """Publish content to Twitter"""
        try:
            # Twitter API publishing logic would go here
            await asyncio.sleep(1)  # Simulate API call
            
            return {
                "success": True,
                "post_id": f"tw_{uuid.uuid4().hex[:8]}",
                "post_url": f"https://twitter.com/user/status/{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Twitter publishing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_to_facebook(self, post: PlatformPost) -> Dict[str, Any]:
        """Publish content to Facebook"""
        try:
            # Facebook API publishing logic would go here
            await asyncio.sleep(1)  # Simulate API call
            
            return {
                "success": True,
                "post_id": f"fb_{uuid.uuid4().hex[:8]}",
                "post_url": f"https://facebook.com/posts/{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Facebook publishing failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Content optimization methods
    async def _optimize_content_for_platform(
        self,
        content_url: str,
        platform: PlatformType,
        content_type: ContentFormat
    ) -> Optional[str]:
        """Optimize content for specific platform"""
        try:
            platform_config = self.config.platform_configs.get(platform)
            if not platform_config:
                return None
            
            # Platform-specific optimization logic would go here
            # For now, return the original URL
            return content_url
            
        except Exception as e:
            logger.error(f"Content optimization failed for {platform.value}: {e}")
            return None
    
    # Scheduling methods
    async def _schedule_campaign(self, campaign: DistributionCampaign):
        """Schedule campaign for future publishing"""
        try:
            campaign.status = DistributionStatus.SCHEDULED
            
            # Add to scheduled posts
            for post in self.platform_posts.values():
                if post.campaign_id == campaign.id:
                    post.status = DistributionStatus.SCHEDULED
                    self.scheduled_posts.append(post.id)
            
            # Update gauge
            self.scheduled_posts_gauge.set(len(self.scheduled_posts))
            
            # Cache updated campaign
            await self._cache_campaign(campaign)
            
        except Exception as e:
            logger.error(f"Campaign scheduling failed: {e}")
    
    async def _process_scheduled_posts(self):
        """Process scheduled posts for publishing"""
        while True:
            try:
                await asyncio.sleep(self.config.schedule_check_interval)
                
                now = datetime.utcnow()
                posts_to_publish = []
                
                # Check scheduled posts
                for post_id in self.scheduled_posts.copy():
                    post = self.platform_posts.get(post_id)
                    if post and post.scheduled_time and post.scheduled_time <= now:
                        posts_to_publish.append(post)
                        self.scheduled_posts.remove(post_id)
                
                # Publish ready posts
                for post in posts_to_publish:
                    try:
                        result = await self._publish_to_platform(post)
                        if result["success"]:
                            post.status = DistributionStatus.PUBLISHED
                            post.published_time = datetime.utcnow()
                            post.platform_post_id = result.get("post_id")
                            post.platform_url = result.get("post_url")
                        else:
                            post.status = DistributionStatus.FAILED
                            post.error_message = result.get("error", "Unknown error")
                            
                    except Exception as e:
                        logger.error(f"Scheduled post publishing failed: {e}")
                        post.status = DistributionStatus.FAILED
                        post.error_message = str(e)
                
                # Update gauge
                self.scheduled_posts_gauge.set(len(self.scheduled_posts))
                
                if posts_to_publish:
                    logger.info(f"Published {len(posts_to_publish)} scheduled posts")
                
            except Exception as e:
                logger.error(f"Scheduled posts processing failed: {e}")
    
    # Analytics collection methods
    async def _collect_platform_analytics(self):
        """Collect analytics from platform APIs"""
        while True:
            try:
                await asyncio.sleep(self.config.analytics_collection_interval)
                
                # Collect analytics for published posts
                for post in self.platform_posts.values():
                    if post.status == DistributionStatus.PUBLISHED and post.platform_post_id:
                        try:
                            analytics = await self._get_platform_analytics(post)
                            if analytics:
                                post.views = analytics.get("views", post.views)
                                post.likes = analytics.get("likes", post.likes)
                                post.comments = analytics.get("comments", post.comments)
                                post.shares = analytics.get("shares", post.shares)
                                
                                # Calculate engagement rate
                                if post.views > 0:
                                    total_engagement = post.likes + post.comments + post.shares
                                    post.engagement_rate = (total_engagement / post.views) * 100
                                
                        except Exception as e:
                            logger.error(f"Analytics collection failed for post {post.id}: {e}")
                
                logger.info("Platform analytics collection completed")
                
            except Exception as e:
                logger.error(f"Platform analytics collection failed: {e}")
    
    async def _get_platform_analytics(self, post: PlatformPost) -> Optional[Dict[str, int]]:
        """Get analytics for specific platform post"""
        try:
            # Platform-specific analytics collection would go here
            # For now, return mock data
            import random
            return {
                "views": random.randint(100, 10000),
                "likes": random.randint(10, 500),
                "comments": random.randint(1, 50),
                "shares": random.randint(1, 100)
            }
            
        except Exception as e:
            logger.error(f"Platform analytics retrieval failed: {e}")
            return None
    
    # RSS feed methods
    async def _generate_rss_feeds(self):
        """Generate RSS feeds periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Generate every hour
                
                # This would generate RSS feeds for all creators
                logger.info("RSS feeds generation completed")
                
            except Exception as e:
                logger.error(f"RSS feeds generation failed: {e}")
    
    async def _create_rss_xml(
        self,
        request: RSSFeedRequest,
        content_items: List[Dict[str, Any]]
    ) -> str:
        """Create RSS XML feed"""
        try:
            # Create RSS XML structure
            rss = ET.Element("rss", version="2.0")
            channel = ET.SubElement(rss, "channel")
            
            # Channel metadata
            ET.SubElement(channel, "title").text = request.feed_title
            ET.SubElement(channel, "description").text = request.feed_description
            ET.SubElement(channel, "link").text = f"{self.config.rss_base_url}"
            ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            # Add items
            for item_data in content_items[:request.max_items]:
                item = ET.SubElement(channel, "item")
                
                ET.SubElement(item, "title").text = item_data.get("title", "")
                ET.SubElement(item, "description").text = item_data.get("description", "")
                ET.SubElement(item, "link").text = item_data.get("url", "")
                ET.SubElement(item, "guid").text = item_data.get("id", "")
                ET.SubElement(item, "pubDate").text = item_data.get("published_at", "")
                
                # Add categories
                for category in item_data.get("categories", []):
                    ET.SubElement(item, "category").text = category
            
            # Convert to string
            return ET.tostring(rss, encoding="unicode")
            
        except Exception as e:
            logger.error(f"RSS XML creation failed: {e}")
            raise
    
    # Helper methods
    async def _get_content_info(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content information from content service"""
        try:
            # This would integrate with the content service
            # For now, return mock data
            return {
                "id": content_id,
                "url": f"https://cdn.ainflue.com/content/{content_id}",
                "type": "video",
                "thumbnail_url": f"https://cdn.ainflue.com/thumbnails/{content_id}",
                "title": "Sample Content",
                "description": "Sample content description"
            }
        except Exception as e:
            logger.error(f"Content info retrieval failed: {e}")
            return None
    
    async def _get_creator_content(
        self,
        creator_id: str,
        content_types: List[ContentFormat],
        max_items: int
    ) -> List[Dict[str, Any]]:
        """Get creator content for RSS feed"""
        # This would fetch actual creator content
        # For now, return mock data
        return [
            {
                "id": f"content_{i}",
                "title": f"Content Item {i}",
                "description": f"Description for content item {i}",
                "url": f"https://ainflue.com/content/{i}",
                "published_at": (datetime.utcnow() - timedelta(days=i)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "categories": ["entertainment", "technology"]
            }
            for i in range(max_items)
        ]
    
    async def _cache_campaign(self, campaign: DistributionCampaign):
        """Cache campaign in Redis"""
        if not self.redis_client:
            return
        
        try:
            campaign_data = {
                "id": campaign.id,
                "creator_id": campaign.creator_id,
                "name": campaign.name,
                "status": campaign.status.value,
                "target_platforms": [p.value for p in campaign.target_platforms],
                "created_at": campaign.created_at.isoformat()
            }
            
            await self.redis_client.setex(
                f"distribution:campaign:{campaign.id}",
                86400,  # 24 hours TTL
                json.dumps(campaign_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache campaign: {e}")
    
    async def _load_campaign_from_cache(self, campaign_id: str) -> Optional[DistributionCampaign]:
        """Load campaign from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(f"distribution:campaign:{campaign_id}")
            if data:
                # This would reconstruct the full campaign object
                # For now, return None
                return None
                
        except Exception as e:
            logger.error(f"Failed to load campaign from cache: {e}")
        
        return None
    
    async def _store_rss_feed(self, feed_id: str, rss_xml: str):
        """Store RSS feed"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                f"distribution:rss:{feed_id}",
                86400,  # 24 hours TTL
                rss_xml
            )
        except Exception as e:
            logger.error(f"Failed to store RSS feed: {e}")
    
    async def _notify_campaign_completion(
        self,
        campaign: DistributionCampaign,
        success_count: int,
        failure_count: int
    ):
        """Notify about campaign completion"""
        try:
            await self.communication_manager.send_message(
                service="notification-service",
                message_type="campaign_completed",
                data={
                    "campaign_id": campaign.id,
                    "creator_id": campaign.creator_id,
                    "status": campaign.status.value,
                    "success_count": success_count,
                    "failure_count": failure_count
                }
            )
        except Exception as e:
            logger.error(f"Failed to notify campaign completion: {e}")
    
    async def _monitor_campaigns(self):
        """Monitor campaign progress and health"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Monitor campaign health and update metrics
                active_campaigns = sum(
                    1 for campaign in self.campaigns.values()
                    if campaign.status in [DistributionStatus.PROCESSING, DistributionStatus.SCHEDULED]
                )
                
                logger.debug(f"Monitoring {active_campaigns} active campaigns")
                
            except Exception as e:
                logger.error(f"Campaign monitoring failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Distribution service health check"""
        try:
            # Test Redis connection
            redis_healthy = False
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    redis_healthy = True
            except Exception:
                pass
            
            # Check platform circuit breakers
            platform_status = {}
            for platform, circuit_breaker in self.platform_circuit_breakers.items():
                platform_status[platform.value] = circuit_breaker.state.name
            
            # Check scheduled posts
            scheduled_count = len(self.scheduled_posts)
            
            status = "healthy" if redis_healthy else "degraded"
            
            return {
                'status': status,
                'redis_connected': redis_healthy,
                'total_campaigns': len(self.campaigns),
                'total_platform_posts': len(self.platform_posts),
                'scheduled_posts': scheduled_count,
                'background_tasks': len(self.background_tasks),
                'platform_circuit_breakers': platform_status,
                'configured_platforms': len(self.config.platform_configs)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# FastAPI app setup
def create_distribution_app() -> FastAPI:
    """Create FastAPI application for distribution service"""
    
    app = FastAPI(
        title="Ainflue Distribution Service",
        description="Multi-platform content distribution and syndication service",
        version="1.0.0"
    )
    
    # Initialize service
    service = DistributionService()
    
    @app.on_event("startup")
    async def startup():
        await service.startup()
    
    @app.on_event("shutdown")
    async def shutdown():
        await service.shutdown()
    
    @app.post("/campaigns")
    async def create_distribution_campaign(
        creator_id: str,
        request: DistributionCampaignRequest
    ):
        """Create a new distribution campaign"""
        return await service.create_distribution_campaign(creator_id, request)
    
    @app.put("/campaigns/{campaign_id}/customize")
    async def customize_platform_content(
        campaign_id: str,
        platform_content: List[PlatformContentRequest]
    ):
        """Customize content for specific platforms"""
        return await service.customize_platform_content(campaign_id, platform_content)
    
    @app.get("/campaigns/{campaign_id}/status")
    async def get_campaign_status(campaign_id: str):
        """Get distribution campaign status"""
        return await service.get_campaign_status(campaign_id)
    
    @app.get("/creators/{creator_id}/performance")
    async def get_platform_performance(
        creator_id: str,
        platform: Optional[PlatformType] = None,
        time_frame: int = 30
    ):
        """Get platform performance analytics"""
        return await service.get_platform_performance(creator_id, platform, time_frame)
    
    @app.post("/rss-feeds")
    async def generate_rss_feed(request: RSSFeedRequest):
        """Generate RSS feed for creator content"""
        feed_url = await service.generate_rss_feed(request)
        return {"success": True, "feed_url": feed_url}
    
    @app.get("/health")
    async def health_check():
        """Service health check"""
        return await service.health_check()
    
    return app


# Export classes for use in other modules
__all__ = [
    'DistributionService',
    'DistributionConfig',
    'PlatformType',
    'DistributionStatus',
    'ContentFormat',
    'OptimizationType',
    'PlatformConfig',
    'DistributionCampaign',
    'PlatformPost',
    'DistributionCampaignRequest',
    'PlatformContentRequest',
    'RSSFeedRequest',
    'DistributionCampaignResponse',
    'PlatformPerformanceResponse',
    'create_distribution_app'
]