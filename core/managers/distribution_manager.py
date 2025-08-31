"""Distribution Manager - IA-Influencer-Agent
================================================================================
Module: backend/core/managers/distribution_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Manager Core - Multi-Platform Content Distribution
Responsibility: Advanced multi-platform content distribution with intelligent optimization
Technologies: Python, Platform APIs, Content Optimization, Social Media Integration
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Contenu optimisé → Analyse plateformes → Distribution intelligente → 
Optimisation formats → Publication coordonnée → Monitoring performance → Analytics cross-platform
"""
from typing import Any, Dict, List, Optional, Union, Tuple, Set, Callable
import logging
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import time
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Plateformes de distribution supportées"""    # Video platforms
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    VIMEO = "vimeo"
    TWITCH = "twitch"
    FACEBOOK_VIDEO = "facebook_video"
    INSTAGRAM_REELS = "instagram_reels"
    
    # Audio platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    DEEZER = "deezer"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    AUDIOMACK = "audiomack"
    
    # Social media
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    
    # Professional platforms
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    DEVIANTART = "deviantart"
    FLICKR = "flickr"
    
    # Blog platforms
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    TUMBLR = "tumblr"
    
    # E-commerce
    ETSY = "etsy"
    SHOPIFY = "shopify"
    AMAZON = "amazon"
    
    # Custom platforms
    WEBSITE = "website"
    EMAIL = "email"
    SMS = "sms"


class ContentFormat(Enum):
    """Formats de contenu"""    VIDEO_SHORT = "video_short"  # <60s
    VIDEO_LONG = "video_long"    # >60s
    AUDIO_TRACK = "audio_track"
    AUDIO_PODCAST = "audio_podcast"
    IMAGE_SINGLE = "image_single"
    IMAGE_CAROUSEL = "image_carousel"
    TEXT_POST = "text_post"
    ARTICLE = "article"
    STORY = "story"
    LIVE_STREAM = "live_stream"


class DistributionStatus(Enum):
    """Statuts de distribution"""    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    DRAFT = "draft"
    ARCHIVED = "archived"


class OptimizationType(Enum):
    """Types d'optimisation"""    FORMAT_CONVERSION = "format_conversion"
    SIZE_OPTIMIZATION = "size_optimization"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    SEO_OPTIMIZATION = "seo_optimization"
    METADATA_ENHANCEMENT = "metadata_enhancement"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    CAPTION_GENERATION = "caption_generation"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"


@dataclass
class DistributionConfig:
    """Configuration du gestionnaire de distribution"""    # Platform management
    max_concurrent_distributions: int = 20
    distribution_timeout: int = 300
    retry_attempts: int = 3
    enable_cross_posting: bool = True
    
    # Content optimization
    auto_format_conversion: bool = True
    auto_size_optimization: bool = True
    auto_quality_enhancement: bool = True
    preserve_original_quality: bool = True
    
    # Scheduling
    enable_optimal_timing: bool = True
    enable_batch_scheduling: bool = True
    timezone_optimization: bool = True
    audience_targeting: bool = True
    
    # Analytics and monitoring
    enable_performance_tracking: bool = True
    enable_engagement_analytics: bool = True
    real_time_monitoring: bool = True
    cross_platform_analytics: bool = True
    
    # SEO and discovery
    auto_seo_optimization: bool = True
    auto_hashtag_generation: bool = True
    auto_caption_generation: bool = True
    keyword_optimization: bool = True
    
    # Error handling
    auto_retry_failed: bool = True
    fallback_platforms: bool = True
    error_notification: bool = True
    
    # Content protection
    watermark_application: bool = True
    metadata_preservation: bool = True
    license_enforcement: bool = True
    
    # Performance optimization
    cdn_acceleration: bool = True
    adaptive_bitrate: bool = True
    progressive_upload: bool = True
    bandwidth_optimization: bool = True


@dataclass
class PlatformConfig:
    """Configuration spécifique à une plateforme"""    platform: Platform
    name: str
    api_endpoint: str = ""
    
    # Authentication
    api_key: str = ""
    access_token: str = ""
    refresh_token: str = ""
    client_id: str = ""
    client_secret: str = ""
    
    # Capabilities
    supported_formats: List[ContentFormat] = field(default_factory=list)
    max_file_size_mb: int = 100
    max_duration_seconds: int = 3600
    max_resolution: str = "1920x1080"
    
    # Optimization settings
    preferred_format: str = "mp4"
    preferred_quality: str = "high"
    auto_thumbnail: bool = True
    auto_captions: bool = False
    
    # Publishing settings
    default_visibility: str = "public"  # public, private, unlisted
    allow_comments: bool = True
    allow_downloads: bool = False
    monetization_enabled: bool = False
    
    # Content requirements
    min_title_length: int = 1
    max_title_length: int = 100
    max_description_length: int = 5000
    required_tags: List[str] = field(default_factory=list)
    
    # Rate limits
    requests_per_minute: int = 60
    uploads_per_day: int = 100
    
    # Analytics
    analytics_supported: bool = True
    realtime_analytics: bool = False
    
    # Status
    active: bool = True
    last_sync: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DistributionRequest:
    """Requête de distribution"""    id: str
    user_id: str
    content_id: str
    platforms: List[Platform]
    
    # Content information
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = ""
    language: str = "en"
    
    # Content URLs
    content_url: str = ""
    thumbnail_url: str = ""
    preview_url: str = ""
    
    # Distribution settings
    scheduled_at: Optional[datetime] = None
    visibility: str = "public"
    allow_comments: bool = True
    enable_monetization: bool = False
    
    # Optimization options
    auto_optimize: bool = True
    optimization_types: List[OptimizationType] = field(default_factory=list)
    
    # Platform-specific settings
    platform_settings: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    
    # Results
    distribution_results: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    
    # Status tracking
    status: DistributionStatus = DistributionStatus.PENDING
    progress_percent: float = 0.0
    
    # Error handling
    errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    
    # Performance metrics
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    engagement_rate: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class DistributionResult:
    """Résultat de distribution sur une plateforme"""    platform: Platform
    content_id: str
    platform_content_id: str = ""
    
    # URLs
    platform_url: str = ""
    embed_url: str = ""
    analytics_url: str = ""
    
    # Status
    status: DistributionStatus = DistributionStatus.PENDING
    published_at: Optional[datetime] = None
    
    # Performance metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    reach: int = 0
    impressions: int = 0
    
    # Engagement metrics
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    completion_rate: float = 0.0
    
    # Revenue metrics (if monetized)
    revenue: float = 0.0
    ad_revenue: float = 0.0
    subscription_revenue: float = 0.0
    
    # Error information
    error_code: str = ""
    error_message: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrossPlatformAnalytics:
    """Analytics cross-platform"""    request_id: str
    total_platforms: int
    successful_platforms: int
    
    # Aggregate metrics
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    total_reach: int = 0
    
    # Performance metrics
    average_engagement_rate: float = 0.0
    best_performing_platform: Optional[Platform] = None
    worst_performing_platform: Optional[Platform] = None
    
    # Platform breakdown
    platform_performance: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    
    # Time-based analytics
    hourly_views: Dict[int, int] = field(default_factory=dict)
    daily_engagement: Dict[str, float] = field(default_factory=dict)
    
    # Audience analytics
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Generated at
    generated_at: datetime = field(default_factory=datetime.utcnow)


class DistributionManager(ABC):
    """    🌐 Advanced Multi-Platform Distribution Manager - IA-Influencer-Agent
    
    Responsabilité:
    Gestionnaire industriel pour distribution multi-plateformes intelligente
    
    Technologies:
    - Platform APIs: Native integration with 30+ content platforms
    - Content Optimization: Format conversion and quality enhancement
    - Intelligent Scheduling: Optimal timing based on audience analytics
    - Cross-Platform Analytics: Unified performance tracking
    - SEO Optimization: Platform-specific search optimization
    - Automated Workflows: Batch processing and error recovery
    
    Fonctionnalités industrielles:
    - Distribution simultanée 30+ plateformes
    - Optimisation formats automatique
    - Scheduling intelligent basé audience
    - Analytics performance unifiées
    - Retry automatique en cas d'échec
    - Gestion rate limits plateforme
    - SEO et hashtags optimisés
    - Monitoring temps réel
    - Cross-posting coordonné
    - Watermarking et protection
    - Revenue tracking multi-plateforme
    - Audience targeting avancé
    """    
    def __init__(self, config: DistributionConfig = None):
        self.config = config or DistributionConfig()
        
        # Platform management
        self._platforms: Dict[Platform, PlatformConfig] = {}
        self._platform_clients: Dict[Platform, Any] = {}
        
        # Distribution system
        self._distribution_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._active_distributions: Dict[str, DistributionRequest] = {}
        self._distribution_results: Dict[str, List[DistributionResult]] = {}
        
        # Content optimization
        self._optimization_cache: Dict[str, Dict[str, Any]] = {}
        self._format_converters: Dict[str, Callable] = {}
        
        # Analytics and monitoring
        self._platform_analytics: Dict[Platform, Dict[str, Any]] = defaultdict(dict)
        self._cross_platform_analytics: Dict[str, CrossPlatformAnalytics] = {}
        
        # Performance tracking
        self._distribution_stats: Dict[Platform, Dict[str, Any]] = defaultdict(dict)
        self._error_tracking: Dict[Platform, List[Dict[str, Any]]] = defaultdict(list)
        
        # Background tasks
        self._processing_tasks: Set[asyncio.Task] = set()
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._monitoring_active = False
        self._lock = threading.Lock()
        
        # Performance metrics
        self._metrics = {
            "total_platforms": 0,
            "active_platforms": 0,
            "total_distributions": 0,
            "successful_distributions": 0,
            "failed_distributions": 0,
            "average_distribution_time": 0.0,
            "total_content_published": 0,
            "total_views_generated": 0,
            "total_engagement": 0,
            "average_engagement_rate": 0.0,
            "revenue_generated": 0.0,
            "most_successful_platform": "",
            "optimization_success_rate": 0.0
        }
        
        logger.info(f"🌐 Distribution Manager initialized - Supporting {len(Platform)} platforms")
    
    @abstractmethod
    async def initialize_platforms(self) -> bool:
        """        Initialize platform connections and configurations
        
        Returns:
            bool: True if initialization successful
        """        pass
    
    @abstractmethod
    async def register_platform(
        self,
        platform: Platform,
        config: PlatformConfig
    ) -> bool:
        """        Register and configure platform for distribution
        
        Args:
            platform: Platform to register
            config: Platform configuration
            
        Returns:
            bool: True if registration successful
        """        pass
    
    @abstractmethod
    async def optimize_content_for_platform(
        self,
        content_url: str,
        platform: Platform,
        optimization_types: List[OptimizationType] = None
    ) -> Dict[str, Any]:
        """        Optimize content for specific platform requirements
        
        Args:
            content_url: URL to content to optimize
            platform: Target platform
            optimization_types: Types of optimization to apply
            
        Returns:
            Dict: Optimization results with optimized content URLs
        """        pass
    
    @abstractmethod
    async def publish_to_platform(
        self,
        platform: Platform,
        content_data: Dict[str, Any],
        settings: Dict[str, Any] = None
    ) -> DistributionResult:
        """        Publish content to specific platform
        
        Args:
            platform: Platform to publish to
            content_data: Content data and metadata
            settings: Platform-specific settings
            
        Returns:
            DistributionResult: Publishing result
        """        pass
    
    async def distribute_content(
        self,
        user_id: str,
        content_id: str,
        platforms: List[Platform],
        content_data: Dict[str, Any],
        distribution_settings: Dict[str, Any] = None
    ) -> DistributionRequest:
        """        Distribute content to multiple platforms
        
        Args:
            user_id: User requesting distribution
            content_id: Content identifier
            platforms: Platforms to distribute to
            content_data: Content data and metadata
            distribution_settings: Distribution configuration
            
        Returns:
            DistributionRequest: Distribution request tracking
        """        try:
            settings = distribution_settings or {}
            
            # Create distribution request
            request = DistributionRequest(
                id=str(uuid.uuid4()),
                user_id=user_id,
                content_id=content_id,
                platforms=platforms,
                title=content_data.get("title", ""),
                description=content_data.get("description", ""),
                tags=content_data.get("tags", []),
                category=content_data.get("category", ""),
                language=content_data.get("language", "en"),
                content_url=content_data.get("content_url", ""),
                thumbnail_url=content_data.get("thumbnail_url", ""),
                scheduled_at=settings.get("scheduled_at"),
                visibility=settings.get("visibility", "public"),
                auto_optimize=settings.get("auto_optimize", True),
                optimization_types=settings.get("optimization_types", []),
                platform_settings=settings.get("platform_settings", {})
            )
            
            # Store request
            with self._lock:
                self._active_distributions[request.id] = request
            
            # Queue for processing
            priority = 0 if request.scheduled_at else 1  # Immediate processing has higher priority
            await self._distribution_queue.put((priority, time.time(), request))
            
            # Start processing if not already running
            if not self._monitoring_active:
                await self._start_distribution_processing()
            
            logger.info(f"🌐 Distribution queued: {request.id} to {len(platforms)} platforms")
            return request
            
        except Exception as e:
            logger.error(f"❌ Distribution submission failed: {e}")
            raise
    
    async def schedule_batch_distribution(
        self,
        user_id: str,
        distributions: List[Dict[str, Any]],
        schedule_config: Dict[str, Any] = None
    ) -> List[DistributionRequest]:
        """        Schedule batch distribution across multiple contents and platforms
        
        Args:
            user_id: User requesting batch distribution
            distributions: List of distribution configurations
            schedule_config: Batch scheduling configuration
            
        Returns:
            List[DistributionRequest]: List of distribution requests
        """        try:
            config = schedule_config or {}
            requests = []
            
            # Calculate optimal scheduling times
            base_time = config.get("start_time", datetime.utcnow())
            interval_minutes = config.get("interval_minutes", 15)
            
            for i, dist_config in enumerate(distributions):
                # Calculate scheduled time
                scheduled_time = base_time + timedelta(minutes=i * interval_minutes)
                
                # Create distribution request
                request = await self.distribute_content(
                    user_id=user_id,
                    content_id=dist_config["content_id"],
                    platforms=dist_config["platforms"],
                    content_data=dist_config["content_data"],
                    distribution_settings={
                        **dist_config.get("settings", {}),
                        "scheduled_at": scheduled_time
                    }
                )
                
                requests.append(request)
            
            logger.info(f"🌐 Batch distribution scheduled: {len(requests)} distributions")
            return requests
            
        except Exception as e:
            logger.error(f"❌ Batch distribution failed: {e}")
            raise
    
    async def get_distribution_analytics(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        platform: Optional[Platform] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive distribution analytics
        
        Args:
            request_id: Optional specific request filter
            user_id: Optional user filter
            platform: Optional platform filter
            time_range: Optional time range filter
            
        Returns:
            Dict: Complete distribution analytics
        """        with self._lock:
            # Filter distributions
            distributions = list(self._active_distributions.values())
            
            if request_id:
                distributions = [d for d in distributions if d.id == request_id]
            if user_id:
                distributions = [d for d in distributions if d.user_id == user_id]
            if time_range:
                start_time, end_time = time_range
                distributions = [
                    d for d in distributions 
                    if d.created_at and start_time <= d.created_at <= end_time
                ]
            
            # Aggregate metrics
            total_distributions = len(distributions)
            successful = len([d for d in distributions if d.status == DistributionStatus.PUBLISHED])
            failed = len([d for d in distributions if d.status == DistributionStatus.FAILED])
            
            # Platform performance
            platform_performance = {}
            for p in Platform:
                if platform and p != platform:
                    continue
                
                platform_dists = [
                    d for d in distributions 
                    if p in d.platforms
                ]
                
                if platform_dists:
                    platform_stats = self._distribution_stats.get(p, {})
                    platform_performance[p.value] = {
                        "total_distributions": len(platform_dists),
                        "success_rate": len([d for d in platform_dists if d.status == DistributionStatus.PUBLISHED]) / len(platform_dists) * 100,
                        "total_views": sum(d.total_views for d in platform_dists),
                        "total_engagement": sum(d.total_likes + d.total_shares + d.total_comments for d in platform_dists),
                        "average_engagement_rate": sum(d.engagement_rate for d in platform_dists) / len(platform_dists),
                        "errors": len(self._error_tracking.get(p, [])),
                        "last_distribution": max(d.created_at for d in platform_dists) if platform_dists else None
                    }
            
            # Content type analysis
            content_types = defaultdict(int)
            for dist in distributions:
                for result in self._distribution_results.get(dist.id, []):
                    content_types[result.platform.value] += 1
            
            # Time-based analytics
            hourly_distributions = defaultdict(int)
            daily_success_rate = defaultdict(list)
            
            for dist in distributions:
                hour = dist.created_at.hour
                day = dist.created_at.date().isoformat()
                
                hourly_distributions[hour] += 1
                daily_success_rate[day].append(1 if dist.status == DistributionStatus.PUBLISHED else 0)
            
            # Calculate daily success rates
            daily_success_rates = {
                day: sum(successes) / len(successes) * 100 
                for day, successes in daily_success_rate.items()
            }
            
            # Revenue analytics
            total_revenue = 0.0
            revenue_by_platform = {}
            
            for dist in distributions:
                for result in self._distribution_results.get(dist.id, []):
                    total_revenue += result.revenue
                    platform_key = result.platform.value
                    revenue_by_platform[platform_key] = revenue_by_platform.get(platform_key, 0.0) + result.revenue
            
            # Top performing content
            top_content = sorted(
                distributions,
                key=lambda x: x.total_views + x.total_likes * 2 + x.total_shares * 3,
                reverse=True
            )[:10]
            
            top_content_data = [
                {
                    "id": dist.id,
                    "title": dist.title,
                    "platforms": [p.value for p in dist.platforms],
                    "total_views": dist.total_views,
                    "total_engagement": dist.total_likes + dist.total_shares + dist.total_comments,
                    "engagement_rate": dist.engagement_rate,
                    "created_at": dist.created_at.isoformat()
                }
                for dist in top_content
            ]
            
            return {
                # Core metrics
                "total_distributions": total_distributions,
                "successful_distributions": successful,
                "failed_distributions": failed,
                "success_rate": successful / max(total_distributions, 1) * 100,
                
                # Platform analysis
                "platform_performance": platform_performance,
                "content_type_distribution": dict(content_types),
                
                # Engagement metrics
                "total_views": sum(d.total_views for d in distributions),
                "total_likes": sum(d.total_likes for d in distributions),
                "total_shares": sum(d.total_shares for d in distributions),
                "total_comments": sum(d.total_comments for d in distributions),
                "average_engagement_rate": sum(d.engagement_rate for d in distributions) / max(total_distributions, 1),
                
                # Revenue metrics
                "total_revenue": total_revenue,
                "revenue_by_platform": revenue_by_platform,
                
                # Time-based analytics
                "hourly_distribution_pattern": dict(hourly_distributions),
                "daily_success_rates": daily_success_rates,
                
                # Top performers
                "top_performing_content": top_content_data,
                "best_performing_platform": max(platform_performance.keys(), key=lambda x: platform_performance[x]["total_views"]) if platform_performance else None,
                
                # System health
                "queue_size": self._distribution_queue.qsize(),
                "active_distributions": len([d for d in distributions if d.status in [DistributionStatus.PROCESSING, DistributionStatus.QUEUED]]),
                "error_rate": failed / max(total_distributions, 1) * 100,
                
                # Generated at
                "generated_at": datetime.utcnow().isoformat(),
                "filters_applied": {
                    "request_id": request_id,
                    "user_id": user_id,
                    "platform": platform.value if platform else None,
                    "time_range": time_range
                }
            }
    
    async def optimize_distribution_strategy(
        self,
        user_id: str,
        content_analysis: Dict[str, Any],
        target_audience: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """        Optimize distribution strategy based on content and audience analysis
        
        Args:
            user_id: User requesting optimization
            content_analysis: Analysis of content characteristics
            target_audience: Target audience demographics and preferences
            
        Returns:
            Dict: Optimized distribution strategy
        """        try:
            # Analyze content characteristics
            content_type = content_analysis.get("type", "unknown")
            content_format = content_analysis.get("format", "unknown")
            content_duration = content_analysis.get("duration", 0)
            content_quality = content_analysis.get("quality_score", 0.0)
            
            # Get user's historical performance
            user_analytics = await self.get_distribution_analytics(user_id=user_id)
            
            # Platform recommendation based on content type
            recommended_platforms = []
            
            if content_type == "video":
                if content_duration < 60:  # Short video
                    recommended_platforms.extend([Platform.TIKTOK, Platform.INSTAGRAM_REELS, Platform.YOUTUBE])
                else:  # Long video
                    recommended_platforms.extend([Platform.YOUTUBE, Platform.VIMEO, Platform.FACEBOOK_VIDEO])
            elif content_type == "audio":
                recommended_platforms.extend([Platform.SPOTIFY, Platform.SOUNDCLOUD, Platform.APPLE_MUSIC])
            elif content_type == "image":
                recommended_platforms.extend([Platform.INSTAGRAM, Platform.PINTEREST, Platform.BEHANCE])
            elif content_type == "text":
                recommended_platforms.extend([Platform.MEDIUM, Platform.LINKEDIN, Platform.TWITTER])
            
            # Filter by user's best performing platforms
            best_platforms = user_analytics.get("platform_performance", {})
            platform_scores = {}
            
            for platform in recommended_platforms:
                platform_key = platform.value
                platform_data = best_platforms.get(platform_key, {})
                
                # Calculate platform score
                success_rate = platform_data.get("success_rate", 50.0)
                engagement_rate = platform_data.get("average_engagement_rate", 1.0)
                total_views = platform_data.get("total_views", 0)
                
                score = (success_rate * 0.4) + (engagement_rate * 0.4) + (min(total_views / 1000, 100) * 0.2)
                platform_scores[platform] = score
            
            # Sort platforms by score
            sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Optimal timing analysis
            audience = target_audience or {}
            timezone = audience.get("timezone", "UTC")
            age_group = audience.get("age_group", "25-34")
            
            # Platform-specific optimal times (simplified)
            optimal_times = {
                Platform.INSTAGRAM: "19:00",
                Platform.TIKTOK: "18:00",
                Platform.YOUTUBE: "20:00",
                Platform.FACEBOOK: "15:00",
                Platform.TWITTER: "12:00",
                Platform.LINKEDIN: "09:00"
            }
            
            # Content optimization recommendations
            optimization_recommendations = []
            
            if content_quality < 0.8:
                optimization_recommendations.append(OptimizationType.QUALITY_ENHANCEMENT)
            
            optimization_recommendations.extend([
                OptimizationType.SEO_OPTIMIZATION,
                OptimizationType.HASHTAG_OPTIMIZATION,
                OptimizationType.THUMBNAIL_GENERATION
            ])
            
            # Generate distribution schedule
            distribution_schedule = []
            base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            
            for i, (platform, score) in enumerate(sorted_platforms[:5]):  # Top 5 platforms
                optimal_time = optimal_times.get(platform, "12:00")
                hour, minute = map(int, optimal_time.split(":"))
                
                scheduled_time = base_time.replace(hour=hour, minute=minute)
                if scheduled_time < datetime.utcnow():
                    scheduled_time += timedelta(days=1)
                
                # Stagger posting times
                scheduled_time += timedelta(minutes=i * 10)
                
                distribution_schedule.append({
                    "platform": platform.value,
                    "scheduled_time": scheduled_time.isoformat(),
                    "score": score,
                    "optimization_types": optimization_recommendations
                })
            
            # Cross-promotion strategy
            cross_promotion = {
                "primary_platform": sorted_platforms[0][0].value if sorted_platforms else None,
                "support_platforms": [p[0].value for p in sorted_platforms[1:3]],
                "hashtag_strategy": await self._generate_hashtag_strategy(content_analysis),
                "caption_variations": await self._generate_caption_variations(content_analysis)
            }
            
            return {
                "recommended_platforms": [p[0].value for p in sorted_platforms],
                "platform_scores": {p[0].value: p[1] for p in sorted_platforms},
                "distribution_schedule": distribution_schedule,
                "optimization_recommendations": [opt.value for opt in optimization_recommendations],
                "cross_promotion": cross_promotion,
                "estimated_reach": self._calculate_estimated_reach(sorted_platforms, content_analysis),
                "expected_engagement": self._calculate_expected_engagement(sorted_platforms, content_analysis),
                "confidence_score": min(content_quality + 0.2, 1.0),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Distribution strategy optimization failed: {e}")
            raise
    
    async def _start_distribution_processing(self) -> None:
        """Start background distribution processing"""        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        
        # Start distribution processor
        for i in range(self.config.max_concurrent_distributions):
            task = asyncio.create_task(self._distribution_processor(f"processor_{i}"))
            self._processing_tasks.add(task)
        
        # Start analytics monitoring
        analytics_task = asyncio.create_task(self._analytics_monitor())
        self._monitoring_tasks.add(analytics_task)
        
        logger.info("🌐 Distribution processing started")
    
    async def _distribution_processor(self, processor_id: str) -> None:
        """Background distribution processor"""        while self._monitoring_active:
            try:
                # Get next distribution from queue
                priority, timestamp, request = await asyncio.wait_for(
                    self._distribution_queue.get(),
                    timeout=5.0
                )
                
                # Process distribution
                await self._process_distribution(request)
                
                # Mark queue task as done
                self._distribution_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Distribution processor {processor_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_distribution(self, request: DistributionRequest) -> None:
        """Process individual distribution request"""        try:
            request.status = DistributionStatus.PROCESSING
            request.started_at = datetime.utcnow()
            
            results = []
            
            # Process each platform
            for platform in request.platforms:
                try:
                    # Check if platform is configured
                    if platform not in self._platforms:
                        logger.warning(f"⚠️ Platform not configured: {platform.value}")
                        continue
                    
                    # Optimize content for platform
                    optimized_content = await self.optimize_content_for_platform(
                        content_url=request.content_url,
                        platform=platform,
                        optimization_types=request.optimization_types
                    )
                    
                    # Prepare content data
                    content_data = {
                        "title": request.title,
                        "description": request.description,
                        "tags": request.tags,
                        "category": request.category,
                        "language": request.language,
                        "content_url": optimized_content.get("optimized_url", request.content_url),
                        "thumbnail_url": optimized_content.get("thumbnail_url", request.thumbnail_url),
                        "metadata": optimized_content.get("metadata", {})
                    }
                    
                    # Get platform-specific settings
                    platform_settings = request.platform_settings.get(platform, {})
                    
                    # Publish to platform
                    result = await self.publish_to_platform(
                        platform=platform,
                        content_data=content_data,
                        settings=platform_settings
                    )
                    
                    results.append(result)
                    
                    # Update request metrics
                    request.total_views += result.views
                    request.total_likes += result.likes
                    request.total_shares += result.shares
                    request.total_comments += result.comments
                    
                    logger.info(f"🌐 Published to {platform.value}: {result.platform_content_id}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to publish to {platform.value}: {e}")
                    
                    # Create error result
                    error_result = DistributionResult(
                        platform=platform,
                        content_id=request.content_id,
                        status=DistributionStatus.FAILED,
                        error_code="PUBLISH_ERROR",
                        error_message=str(e)
                    )
                    results.append(error_result)
                    
                    # Track error
                    self._error_tracking[platform].append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": str(e),
                        "request_id": request.id
                    })
            
            # Store results
            with self._lock:
                self._distribution_results[request.id] = results
                
                # Update request status
                successful_results = [r for r in results if r.status == DistributionStatus.PUBLISHED]
                
                if successful_results:
                    request.status = DistributionStatus.PUBLISHED
                    request.completed_at = datetime.utcnow()
                    request.progress_percent = 100.0
                    
                    # Calculate engagement rate
                    total_engagement = request.total_likes + request.total_shares + request.total_comments
                    request.engagement_rate = total_engagement / max(request.total_views, 1) * 100
                    
                    # Update metrics
                    self._metrics["successful_distributions"] += 1
                    self._metrics["total_content_published"] += 1
                    self._metrics["total_views_generated"] += request.total_views
                    self._metrics["total_engagement"] += total_engagement
                else:
                    request.status = DistributionStatus.FAILED
                    self._metrics["failed_distributions"] += 1
                
                self._metrics["total_distributions"] += 1
            
            logger.info(f"🌐 Distribution completed: {request.id} - {len(successful_results)}/{len(results)} platforms")
            
        except Exception as e:
            request.status = DistributionStatus.FAILED
            logger.error(f"❌ Distribution processing failed: {request.id} - {e}")
    
    async def _analytics_monitor(self) -> None:
        """Background analytics monitoring"""        while self._monitoring_active:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                await self._update_platform_analytics()
            except Exception as e:
                logger.error(f"❌ Analytics monitor error: {e}")
    
    async def _update_platform_analytics(self) -> None:
        """Update platform analytics data"""        # This would fetch real-time analytics from platforms
        # Simplified implementation
        pass
    
    async def _generate_hashtag_strategy(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hashtag strategy based on content analysis"""        # Simplified hashtag generation
        content_type = content_analysis.get("type", "")
        category = content_analysis.get("category", "")
        
        base_hashtags = ["#content", "#creator", "#viral"]
        
        if content_type == "video":
            base_hashtags.extend(["#video", "#entertainment"])
        elif content_type == "audio":
            base_hashtags.extend(["#music", "#audio"])
        
        return {
            "primary_hashtags": base_hashtags[:5],
            "secondary_hashtags": base_hashtags[5:10],
            "trending_hashtags": ["#trending", "#new"],
            "platform_specific": {
                "instagram": base_hashtags + ["#insta", "#ig"],
                "tiktok": base_hashtags + ["#fyp", "#viral"],
                "twitter": base_hashtags[:3]  # Twitter has character limits
            }
        }
    
    async def _generate_caption_variations(self, content_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate caption variations for different platforms"""        title = content_analysis.get("title", "")
        description = content_analysis.get("description", "")
        
        return {
            "instagram": f"{title}\n\n{description[:500]}...",
            "tiktok": f"{title} 🔥\n\n{description[:150]}...",
            "youtube": f"{title}\n\n{description}",
            "twitter": f"{title}\n\n{description[:200]}...",
            "linkedin": f"{title}\n\n{description}"
        }
    
    def _calculate_estimated_reach(
        self,
        platforms: List[Tuple[Platform, float]],
        content_analysis: Dict[str, Any]
    ) -> int:
        """Calculate estimated reach based on platform scores"""        # Simplified reach calculation
        base_reach = 1000
        quality_multiplier = content_analysis.get("quality_score", 0.5)
        
        total_reach = 0
        for platform, score in platforms:
            platform_reach = int(base_reach * score * quality_multiplier)
            total_reach += platform_reach
        
        return total_reach
    
    def _calculate_expected_engagement(
        self,
        platforms: List[Tuple[Platform, float]],
        content_analysis: Dict[str, Any]
    ) -> float:
        """Calculate expected engagement rate"""        # Simplified engagement calculation
        base_engagement = 2.0  # 2% base engagement rate
        quality_multiplier = content_analysis.get("quality_score", 0.5)
        
        weighted_engagement = 0.0
        total_weight = 0.0
        
        for platform, score in platforms:
            weight = score
            engagement = base_engagement * quality_multiplier * score
            weighted_engagement += engagement * weight
            total_weight += weight
        
        return weighted_engagement / max(total_weight, 1)
    
    @asynccontextmanager
    async def get_distribution_session(self, user_id: str):
        """Context manager for distribution operations"""        session_id = str(uuid.uuid4())
        try:
            logger.info(f"🌐 Distribution session started: {session_id} for user {user_id}")
            yield session_id
        finally:
            logger.info(f"🌐 Distribution session ended: {session_id}")
    
    async def cleanup(self) -> bool:
        """Cleanup distribution resources"""        try:
            # Stop monitoring
            self._monitoring_active = False
            
            # Cancel processing tasks
            for task in self._processing_tasks:
                task.cancel()
            for task in self._monitoring_tasks:
                task.cancel()
            
            await asyncio.gather(
                *self._processing_tasks,
                *self._monitoring_tasks,
                return_exceptions=True
            )
            
            with self._lock:
                # Clear queues
                while not self._distribution_queue.empty():
                    self._distribution_queue.get_nowait()
                
                # Clear data
                self._active_distributions.clear()
                self._distribution_results.clear()
                self._optimization_cache.clear()
                self._platform_analytics.clear()
                self._cross_platform_analytics.clear()
                self._processing_tasks.clear()
                self._monitoring_tasks.clear()
                
                # Reset metrics
                self._metrics = {
                    "total_platforms": 0,
                    "active_platforms": 0,
                    "total_distributions": 0,
                    "successful_distributions": 0,
                    "failed_distributions": 0,
                    "average_distribution_time": 0.0,
                    "total_content_published": 0,
                    "total_views_generated": 0,
                    "total_engagement": 0,
                    "average_engagement_rate": 0.0,
                    "revenue_generated": 0.0,
                    "most_successful_platform": "",
                    "optimization_success_rate": 0.0
                }
            
            logger.info("🧹 Distribution Manager cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Distribution cleanup failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get distribution system statistics"""        with self._lock:
            return {
                "platforms_configured": len(self._platforms),
                "active_distributions": len(self._active_distributions),
                "queue_size": self._distribution_queue.qsize(),
                "total_results": sum(len(results) for results in self._distribution_results.values()),
                "cache_size": len(self._optimization_cache),
                "config": {
                    "max_concurrent_distributions": self.config.max_concurrent_distributions,
                    "auto_format_conversion": self.config.auto_format_conversion,
                    "enable_optimal_timing": self.config.enable_optimal_timing,
                    "enable_cross_posting": self.config.enable_cross_posting,
                    "auto_seo_optimization": self.config.auto_seo_optimization,
                    "real_time_monitoring": self.config.real_time_monitoring
                },
                "metrics": dict(self._metrics),
                "system_health": {
                    "memory_usage": (
                        len(self._active_distributions) + 
                        len(self._distribution_results) +
                        len(self._optimization_cache)
                    ),
                    "background_tasks": len(self._processing_tasks) + len(self._monitoring_tasks),
                    "error_rate": self._metrics["failed_distributions"] / max(self._metrics["total_distributions"], 1) * 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }


# Global instance
distribution_manager = None


def get_distribution_manager() -> DistributionManager:
    """    Get the global distribution manager instance
    
    Returns:
        DistributionManager: Global distribution manager
    """    global distribution_manager
    if distribution_manager is None:
        from ..implementations.distribution_manager_impl import DistributionManagerImpl
        distribution_manager = DistributionManagerImpl()
    return distribution_manager
