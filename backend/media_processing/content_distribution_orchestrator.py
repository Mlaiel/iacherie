#!/usr/bin/env python3
"""🚀 Content Distribution Orchestrator - Multi-Platform Distribution Engine
===============================================================================
Module: backend/media_processing/content_distribution_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Distribution Specialist + Platform Integration Expert + Analytics Engineer + Marketing Strategist
Type: Advanced Distribution Processing System - Production-Ready
Responsibility: Multi-platform content distribution orchestration and optimization
===================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🚀 DISTRIBUTION CAPABILITIES:
- Multi-platform content adaptation and optimization
- Automated scheduling and publishing workflows
- Cross-platform analytics and performance tracking
- Audience targeting and engagement optimization
- Revenue optimization and monetization strategies
- Real-time distribution monitoring and adjustment
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json

# Import existing distribution systems for integration
try:
    from ...distribution.publishing_engine import MultiPlatformPublisher
    from ...distribution.analytics_engine import DistributionAnalytics
    from ...distribution.optimization_engine import DistributionOptimizer
    from ...distribution.monetization_engine import MonetizationOptimizer
    from ...backend.core.content_processing_engine import ContentProcessingEngine
    DISTRIBUTION_SYSTEMS_AVAILABLE = True
except ImportError:
    DISTRIBUTION_SYSTEMS_AVAILABLE = False

# Import analytics and scheduling libraries
try:
    import pandas as pd
    from datetime import datetime
    import pytz
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Distribution platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"


class ContentFormat(Enum):
    """Content formats for distribution"""
    VIDEO_SHORT = "video_short"  # <60s
    VIDEO_MEDIUM = "video_medium"  # 1-10 min
    VIDEO_LONG = "video_long"  # >10 min
    AUDIO_TRACK = "audio_track"
    AUDIO_PODCAST = "audio_podcast"
    IMAGE_SINGLE = "image_single"
    IMAGE_CAROUSEL = "image_carousel"
    TEXT_POST = "text_post"
    STORY = "story"
    LIVE_STREAM = "live_stream"


class DistributionStatus(Enum):
    """Distribution workflow status"""
    PREPARING = "preparing"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    PAUSED = "paused"


class AudienceSegment(Enum):
    """Audience targeting segments"""
    GENERAL = "general"
    NICHE_ENTHUSIASTS = "niche_enthusiasts"
    YOUNG_ADULTS = "young_adults"
    PROFESSIONALS = "professionals"
    CREATORS = "creators"
    EARLY_ADOPTERS = "early_adopters"
    MAINSTREAM = "mainstream"


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: Platform
    enabled: bool = True
    format_preferences: List[ContentFormat] = field(default_factory=list)
    optimal_posting_times: List[str] = field(default_factory=list)
    hashtag_limit: int = 30
    character_limit: Optional[int] = None
    aspect_ratios: List[str] = field(default_factory=list)
    monetization_enabled: bool = False
    auto_crosspost: bool = True


@dataclass
class DistributionPlan:
    """Content distribution plan"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    creator_id: str = ""
    target_platforms: List[Platform] = field(default_factory=list)
    content_formats: Dict[Platform, ContentFormat] = field(default_factory=dict)
    scheduling_strategy: str = "optimal_timing"
    audience_targeting: Dict[Platform, AudienceSegment] = field(default_factory=dict)
    monetization_settings: Dict[str, Any] = field(default_factory=dict)
    cross_promotion_enabled: bool = True
    analytics_tracking: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PublishingSchedule:
    """Content publishing schedule"""
    plan_id: str
    platform: Platform
    content_format: ContentFormat
    scheduled_time: datetime
    timezone: str = "UTC"
    status: DistributionStatus = DistributionStatus.SCHEDULED
    metadata: Dict[str, Any] = field(default_factory=dict)
    schedule_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class DistributionMetrics:
    """Distribution performance metrics"""
    platform: Platform
    content_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    reach: int = 0
    impressions: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CrossPlatformAnalytics:
    """Cross-platform analytics summary"""
    content_id: str
    total_views: int = 0
    total_engagement: int = 0
    average_engagement_rate: float = 0.0
    best_performing_platform: Optional[Platform] = None
    platform_metrics: Dict[Platform, DistributionMetrics] = field(default_factory=dict)
    roi_analysis: Dict[str, float] = field(default_factory=dict)
    audience_insights: Dict[str, Any] = field(default_factory=dict)


class ContentDistributionOrchestrator:
    """Multi-Platform Distribution Engine
    
    Comprehensive content distribution system with automated scheduling,
    platform optimization, audience targeting, and performance analytics.
    """

    def __init__(self):
        """Initialize content distribution orchestrator"""
        self.distribution_plans: Dict[str, DistributionPlan] = {}
        self.publishing_schedules: Dict[str, List[PublishingSchedule]] = {}
        self.platform_configs: Dict[Platform, PlatformConfig] = {}
        self.performance_metrics: Dict[str, List[DistributionMetrics]] = {}
        
        # Initialize existing distribution systems if available
        if DISTRIBUTION_SYSTEMS_AVAILABLE:
            self.publisher = MultiPlatformPublisher()
            self.analytics = DistributionAnalytics()
            self.optimizer = DistributionOptimizer()
            self.monetization = MonetizationOptimizer()
            self.content_engine = ContentProcessingEngine()
        else:
            logger.warning("Distribution systems not available - running in simulation mode")
            self.publisher = None
            self.analytics = None
            self.optimizer = None
            self.monetization = None
            self.content_engine = None
        
        # Initialize platform configurations
        self._initialize_platform_configs()

    def _initialize_platform_configs(self):
        """Initialize default platform configurations"""
        
        self.platform_configs = {
            Platform.YOUTUBE: PlatformConfig(
                platform=Platform.YOUTUBE,
                format_preferences=[ContentFormat.VIDEO_MEDIUM, ContentFormat.VIDEO_LONG],
                optimal_posting_times=["14:00", "15:00", "16:00"],
                hashtag_limit=500,
                aspect_ratios=["16:9", "9:16"],
                monetization_enabled=True
            ),
            Platform.INSTAGRAM: PlatformConfig(
                platform=Platform.INSTAGRAM,
                format_preferences=[ContentFormat.IMAGE_SINGLE, ContentFormat.VIDEO_SHORT, ContentFormat.STORY],
                optimal_posting_times=["11:00", "13:00", "19:00"],
                hashtag_limit=30,
                character_limit=2200,
                aspect_ratios=["1:1", "9:16", "4:5"],
                monetization_enabled=True
            ),
            Platform.TIKTOK: PlatformConfig(
                platform=Platform.TIKTOK,
                format_preferences=[ContentFormat.VIDEO_SHORT],
                optimal_posting_times=["18:00", "19:00", "20:00"],
                hashtag_limit=100,
                character_limit=300,
                aspect_ratios=["9:16"],
                monetization_enabled=True
            ),
            Platform.TWITTER: PlatformConfig(
                platform=Platform.TWITTER,
                format_preferences=[ContentFormat.TEXT_POST, ContentFormat.IMAGE_SINGLE, ContentFormat.VIDEO_SHORT],
                optimal_posting_times=["09:00", "12:00", "15:00"],
                hashtag_limit=2,
                character_limit=280,
                aspect_ratios=["16:9", "1:1"],
                monetization_enabled=False
            ),
            Platform.SPOTIFY: PlatformConfig(
                platform=Platform.SPOTIFY,
                format_preferences=[ContentFormat.AUDIO_TRACK, ContentFormat.AUDIO_PODCAST],
                optimal_posting_times=["00:00"],  # Releases typically at midnight
                hashtag_limit=0,
                monetization_enabled=True
            ),
            Platform.LINKEDIN: PlatformConfig(
                platform=Platform.LINKEDIN,
                format_preferences=[ContentFormat.TEXT_POST, ContentFormat.IMAGE_SINGLE, ContentFormat.VIDEO_MEDIUM],
                optimal_posting_times=["08:00", "12:00", "17:00"],
                hashtag_limit=5,
                character_limit=3000,
                aspect_ratios=["16:9", "1:1"],
                monetization_enabled=False
            )
        }

    async def create_distribution_plan(
        self,
        content_id: str,
        creator_id: str,
        target_platforms: List[Platform],
        content_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> DistributionPlan:
        """Create comprehensive distribution plan"""
        
        if options is None:
            options = {}
        
        # Determine optimal content formats for each platform
        content_formats = await self._determine_content_formats(content_type, target_platforms)
        
        # Analyze audience targeting for each platform
        audience_targeting = await self._analyze_audience_targeting(
            creator_id, target_platforms, content_type
        )
        
        # Configure monetization settings
        monetization_settings = await self._configure_monetization(
            creator_id, target_platforms, options
        )
        
        distribution_plan = DistributionPlan(
            content_id=content_id,
            creator_id=creator_id,
            target_platforms=target_platforms,
            content_formats=content_formats,
            scheduling_strategy=options.get('scheduling_strategy', 'optimal_timing'),
            audience_targeting=audience_targeting,
            monetization_settings=monetization_settings,
            cross_promotion_enabled=options.get('cross_promotion', True),
            analytics_tracking=options.get('analytics_tracking', True)
        )
        
        self.distribution_plans[distribution_plan.plan_id] = distribution_plan
        
        logger.info(f"Created distribution plan {distribution_plan.plan_id} for content {content_id}")
        
        return distribution_plan

    async def _determine_content_formats(
        self,
        content_type: str,
        target_platforms: List[Platform]
    ) -> Dict[Platform, ContentFormat]:
        """Determine optimal content format for each platform"""
        
        content_formats = {}
        
        # Content type to format mapping
        format_mapping = {
            'video': {
                Platform.YOUTUBE: ContentFormat.VIDEO_MEDIUM,
                Platform.INSTAGRAM: ContentFormat.VIDEO_SHORT,
                Platform.TIKTOK: ContentFormat.VIDEO_SHORT,
                Platform.FACEBOOK: ContentFormat.VIDEO_MEDIUM,
                Platform.TWITTER: ContentFormat.VIDEO_SHORT,
                Platform.LINKEDIN: ContentFormat.VIDEO_MEDIUM
            },
            'audio': {
                Platform.SPOTIFY: ContentFormat.AUDIO_TRACK,
                Platform.SOUNDCLOUD: ContentFormat.AUDIO_TRACK,
                Platform.YOUTUBE: ContentFormat.VIDEO_MEDIUM,  # Audio with visualization
                Platform.INSTAGRAM: ContentFormat.STORY,  # Audio story
                Platform.TWITTER: ContentFormat.TEXT_POST  # Audio link
            },
            'image': {
                Platform.INSTAGRAM: ContentFormat.IMAGE_SINGLE,
                Platform.PINTEREST: ContentFormat.IMAGE_SINGLE,
                Platform.FACEBOOK: ContentFormat.IMAGE_SINGLE,
                Platform.TWITTER: ContentFormat.IMAGE_SINGLE,
                Platform.LINKEDIN: ContentFormat.IMAGE_SINGLE
            },
            'text': {
                Platform.TWITTER: ContentFormat.TEXT_POST,
                Platform.LINKEDIN: ContentFormat.TEXT_POST,
                Platform.FACEBOOK: ContentFormat.TEXT_POST,
                Platform.INSTAGRAM: ContentFormat.TEXT_POST
            }
        }
        
        base_mapping = format_mapping.get(content_type, {})
        
        for platform in target_platforms:
            if platform in base_mapping:
                content_formats[platform] = base_mapping[platform]
            else:
                # Default fallback based on platform preferences
                config = self.platform_configs.get(platform)
                if config and config.format_preferences:
                    content_formats[platform] = config.format_preferences[0]
                else:
                    content_formats[platform] = ContentFormat.IMAGE_SINGLE
        
        return content_formats

    async def _analyze_audience_targeting(
        self,
        creator_id: str,
        target_platforms: List[Platform],
        content_type: str
    ) -> Dict[Platform, AudienceSegment]:
        """Analyze optimal audience targeting for each platform"""
        
        audience_targeting = {}
        
        # Platform-specific audience mapping
        platform_audiences = {
            Platform.YOUTUBE: AudienceSegment.GENERAL,
            Platform.INSTAGRAM: AudienceSegment.YOUNG_ADULTS,
            Platform.TIKTOK: AudienceSegment.YOUNG_ADULTS,
            Platform.LINKEDIN: AudienceSegment.PROFESSIONALS,
            Platform.TWITTER: AudienceSegment.EARLY_ADOPTERS,
            Platform.SPOTIFY: AudienceSegment.MAINSTREAM,
            Platform.FACEBOOK: AudienceSegment.MAINSTREAM
        }
        
        # Content type influences audience
        content_audience_mapping = {
            'music': AudienceSegment.NICHE_ENTHUSIASTS,
            'education': AudienceSegment.PROFESSIONALS,
            'entertainment': AudienceSegment.GENERAL,
            'comedy': AudienceSegment.YOUNG_ADULTS,
            'business': AudienceSegment.PROFESSIONALS
        }
        
        base_audience = content_audience_mapping.get(content_type, AudienceSegment.GENERAL)
        
        for platform in target_platforms:
            # Combine platform preference with content type
            platform_pref = platform_audiences.get(platform, AudienceSegment.GENERAL)
            
            # Use content-specific audience if it aligns with platform
            if base_audience == AudienceSegment.PROFESSIONALS and platform in [Platform.LINKEDIN]:
                audience_targeting[platform] = AudienceSegment.PROFESSIONALS
            elif base_audience == AudienceSegment.YOUNG_ADULTS and platform in [Platform.TIKTOK, Platform.INSTAGRAM]:
                audience_targeting[platform] = AudienceSegment.YOUNG_ADULTS
            else:
                audience_targeting[platform] = platform_pref
        
        return audience_targeting

    async def _configure_monetization(
        self,
        creator_id: str,
        target_platforms: List[Platform],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure monetization settings"""
        
        monetization_settings = {
            "enabled": options.get('monetization_enabled', True),
            "revenue_sharing": options.get('revenue_sharing', True),
            "ad_placement": options.get('ad_placement', 'auto'),
            "subscription_tier": options.get('subscription_tier', 'premium'),
            "merchandise_integration": options.get('merchandise', False),
            "sponsorship_opportunities": options.get('sponsorships', True)
        }
        
        # Platform-specific monetization
        platform_monetization = {}
        
        for platform in target_platforms:
            config = self.platform_configs.get(platform)
            if config and config.monetization_enabled:
                if platform == Platform.YOUTUBE:
                    platform_monetization[platform.value] = {
                        "ads_enabled": True,
                        "channel_memberships": True,
                        "super_chat": True,
                        "merchandise_shelf": True
                    }
                elif platform == Platform.INSTAGRAM:
                    platform_monetization[platform.value] = {
                        "reels_play_bonus": True,
                        "branded_content": True,
                        "shopping_tags": True,
                        "live_badges": True
                    }
                elif platform == Platform.TIKTOK:
                    platform_monetization[platform.value] = {
                        "creator_fund": True,
                        "live_gifts": True,
                        "brand_partnerships": True
                    }
                elif platform == Platform.SPOTIFY:
                    platform_monetization[platform.value] = {
                        "streaming_royalties": True,
                        "playlist_placement": True,
                        "podcast_ads": True
                    }
        
        monetization_settings["platform_specific"] = platform_monetization
        
        return monetization_settings

    async def generate_publishing_schedule(
        self,
        plan_id: str,
        start_date: Optional[datetime] = None,
        schedule_options: Optional[Dict[str, Any]] = None
    ) -> List[PublishingSchedule]:
        """Generate optimized publishing schedule"""
        
        if plan_id not in self.distribution_plans:
            raise ValueError(f"Distribution plan {plan_id} not found")
        
        plan = self.distribution_plans[plan_id]
        
        if start_date is None:
            start_date = datetime.now(timezone.utc) + timedelta(hours=1)
        
        if schedule_options is None:
            schedule_options = {}
        
        schedules = []
        
        # Use optimizer if available
        if self.optimizer:
            try:
                optimized_schedule = await self.optimizer.generate_schedule(
                    plan.content_id,
                    plan.target_platforms,
                    start_date,
                    schedule_options
                )
                
                # Convert to our format
                for schedule_item in optimized_schedule:
                    schedule = PublishingSchedule(
                        plan_id=plan_id,
                        platform=Platform(schedule_item['platform']),
                        content_format=ContentFormat(schedule_item['format']),
                        scheduled_time=schedule_item['time'],
                        timezone=schedule_item.get('timezone', 'UTC'),
                        metadata=schedule_item.get('metadata', {})
                    )
                    schedules.append(schedule)
                    
            except Exception as e:
                logger.error(f"Optimizer failed: {str(e)}")
        
        # Fallback: Generate schedule using our algorithm
        if not schedules:
            schedules = await self._generate_schedule_internal(plan, start_date, schedule_options)
        
        # Store schedules
        self.publishing_schedules[plan_id] = schedules
        
        return schedules

    async def _generate_schedule_internal(
        self,
        plan: DistributionPlan,
        start_date: datetime,
        options: Dict[str, Any]
    ) -> List[PublishingSchedule]:
        """Internal schedule generation algorithm"""
        
        schedules = []
        current_time = start_date
        
        # Scheduling strategies
        strategy = plan.scheduling_strategy
        
        if strategy == "optimal_timing":
            # Schedule based on platform optimal times
            for platform in plan.target_platforms:
                config = self.platform_configs.get(platform)
                if not config:
                    continue
                
                # Find optimal time for this platform
                optimal_times = config.optimal_posting_times
                if optimal_times:
                    # Choose best time from optimal times
                    optimal_hour = int(optimal_times[0].split(':')[0])
                    
                    # Schedule for next occurrence of optimal time
                    scheduled_time = current_time.replace(
                        hour=optimal_hour,
                        minute=0,
                        second=0,
                        microsecond=0
                    )
                    
                    # If time has passed today, schedule for tomorrow
                    if scheduled_time <= current_time:
                        scheduled_time += timedelta(days=1)
                else:
                    # Default to 2 hours from now
                    scheduled_time = current_time + timedelta(hours=2)
                
                schedule = PublishingSchedule(
                    plan_id=plan.plan_id,
                    platform=platform,
                    content_format=plan.content_formats.get(platform, ContentFormat.IMAGE_SINGLE),
                    scheduled_time=scheduled_time,
                    metadata={
                        "audience_segment": plan.audience_targeting.get(platform, AudienceSegment.GENERAL).value,
                        "monetization_enabled": platform.value in plan.monetization_settings.get("platform_specific", {})
                    }
                )
                schedules.append(schedule)
        
        elif strategy == "sequential":
            # Schedule platforms sequentially with gaps
            gap_hours = options.get('gap_hours', 2)
            
            for i, platform in enumerate(plan.target_platforms):
                scheduled_time = current_time + timedelta(hours=i * gap_hours)
                
                schedule = PublishingSchedule(
                    plan_id=plan.plan_id,
                    platform=platform,
                    content_format=plan.content_formats.get(platform, ContentFormat.IMAGE_SINGLE),
                    scheduled_time=scheduled_time,
                    metadata={
                        "sequence_order": i + 1,
                        "audience_segment": plan.audience_targeting.get(platform, AudienceSegment.GENERAL).value
                    }
                )
                schedules.append(schedule)
        
        elif strategy == "simultaneous":
            # Schedule all platforms at the same time
            scheduled_time = current_time + timedelta(hours=1)
            
            for platform in plan.target_platforms:
                schedule = PublishingSchedule(
                    plan_id=plan.plan_id,
                    platform=platform,
                    content_format=plan.content_formats.get(platform, ContentFormat.IMAGE_SINGLE),
                    scheduled_time=scheduled_time,
                    metadata={
                        "batch_publish": True,
                        "audience_segment": plan.audience_targeting.get(platform, AudienceSegment.GENERAL).value
                    }
                )
                schedules.append(schedule)
        
        return schedules

    async def execute_distribution(self, plan_id: str) -> Dict[str, Any]:
        """Execute distribution plan"""
        
        if plan_id not in self.distribution_plans:
            raise ValueError(f"Distribution plan {plan_id} not found")
        
        if plan_id not in self.publishing_schedules:
            # Generate schedule if not exists
            await self.generate_publishing_schedule(plan_id)
        
        plan = self.distribution_plans[plan_id]
        schedules = self.publishing_schedules[plan_id]
        
        execution_results = {
            "plan_id": plan_id,
            "total_platforms": len(schedules),
            "successful_publishes": 0,
            "failed_publishes": 0,
            "platform_results": {},
            "execution_time": datetime.now(timezone.utc).isoformat()
        }
        
        # Execute publishing for each scheduled platform
        for schedule in schedules:
            try:
                result = await self._publish_to_platform(plan, schedule)
                
                if result["success"]:
                    schedule.status = DistributionStatus.PUBLISHED
                    execution_results["successful_publishes"] += 1
                else:
                    schedule.status = DistributionStatus.FAILED
                    execution_results["failed_publishes"] += 1
                
                execution_results["platform_results"][schedule.platform.value] = result
                
            except Exception as e:
                logger.error(f"Publishing failed for {schedule.platform.value}: {str(e)}")
                schedule.status = DistributionStatus.FAILED
                execution_results["failed_publishes"] += 1
                execution_results["platform_results"][schedule.platform.value] = {
                    "success": False,
                    "error": str(e)
                }
        
        return execution_results

    async def _publish_to_platform(
        self,
        plan: DistributionPlan,
        schedule: PublishingSchedule
    ) -> Dict[str, Any]:
        """Publish content to specific platform"""
        
        if self.publisher:
            try:
                # Use existing publisher
                result = await self.publisher.publish(
                    platform=schedule.platform.value,
                    content_id=plan.content_id,
                    format=schedule.content_format.value,
                    metadata=schedule.metadata,
                    monetization=plan.monetization_settings
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Publisher failed: {str(e)}")
        
        # Simulate publishing
        success_rate = 0.95  # 95% success rate
        import random
        
        if random.random() < success_rate:
            return {
                "success": True,
                "platform": schedule.platform.value,
                "post_id": f"post_{uuid.uuid4().hex[:8]}",
                "url": f"https://{schedule.platform.value}.com/post/{uuid.uuid4().hex[:8]}",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "initial_metrics": {
                    "views": random.randint(10, 100),
                    "likes": random.randint(1, 20),
                    "shares": random.randint(0, 5)
                }
            }
        else:
            return {
                "success": False,
                "platform": schedule.platform.value,
                "error": "Simulated publishing failure",
                "retry_possible": True
            }

    async def track_performance(self, plan_id: str) -> CrossPlatformAnalytics:
        """Track cross-platform performance"""
        
        if plan_id not in self.distribution_plans:
            raise ValueError(f"Distribution plan {plan_id} not found")
        
        plan = self.distribution_plans[plan_id]
        
        # Use existing analytics if available
        if self.analytics:
            try:
                analytics_data = await self.analytics.get_cross_platform_metrics(
                    content_id=plan.content_id,
                    platforms=[p.value for p in plan.target_platforms]
                )
                
                # Convert to our format
                platform_metrics = {}
                for platform_data in analytics_data.get('platforms', []):
                    platform = Platform(platform_data['platform'])
                    metrics = DistributionMetrics(
                        platform=platform,
                        content_id=plan.content_id,
                        views=platform_data.get('views', 0),
                        likes=platform_data.get('likes', 0),
                        shares=platform_data.get('shares', 0),
                        comments=platform_data.get('comments', 0),
                        engagement_rate=platform_data.get('engagement_rate', 0.0),
                        reach=platform_data.get('reach', 0),
                        revenue=platform_data.get('revenue', 0.0)
                    )
                    platform_metrics[platform] = metrics
                
                return CrossPlatformAnalytics(
                    content_id=plan.content_id,
                    total_views=analytics_data.get('total_views', 0),
                    total_engagement=analytics_data.get('total_engagement', 0),
                    average_engagement_rate=analytics_data.get('avg_engagement_rate', 0.0),
                    best_performing_platform=Platform(analytics_data.get('best_platform')) if analytics_data.get('best_platform') else None,
                    platform_metrics=platform_metrics,
                    roi_analysis=analytics_data.get('roi_analysis', {}),
                    audience_insights=analytics_data.get('audience_insights', {})
                )
                
            except Exception as e:
                logger.error(f"Analytics tracking failed: {str(e)}")
        
        # Simulate performance tracking
        return await self._simulate_performance_tracking(plan)

    async def _simulate_performance_tracking(self, plan: DistributionPlan) -> CrossPlatformAnalytics:
        """Simulate performance tracking"""
        
        import random
        
        platform_metrics = {}
        total_views = 0
        total_engagement = 0
        
        # Simulate metrics for each platform
        for platform in plan.target_platforms:
            base_views = random.randint(100, 10000)
            
            # Platform multipliers
            multipliers = {
                Platform.YOUTUBE: 1.5,
                Platform.TIKTOK: 2.0,
                Platform.INSTAGRAM: 1.2,
                Platform.FACEBOOK: 1.0,
                Platform.TWITTER: 0.8,
                Platform.LINKEDIN: 0.6
            }
            
            multiplier = multipliers.get(platform, 1.0)
            views = int(base_views * multiplier)
            likes = int(views * random.uniform(0.02, 0.08))
            shares = int(views * random.uniform(0.001, 0.01))
            comments = int(views * random.uniform(0.005, 0.02))
            engagement = likes + shares + comments
            engagement_rate = engagement / views if views > 0 else 0.0
            
            metrics = DistributionMetrics(
                platform=platform,
                content_id=plan.content_id,
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                engagement_rate=engagement_rate,
                reach=int(views * 1.2),
                revenue=views * random.uniform(0.001, 0.01) if platform in [Platform.YOUTUBE, Platform.SPOTIFY] else 0.0
            )
            
            platform_metrics[platform] = metrics
            total_views += views
            total_engagement += engagement
        
        # Find best performing platform
        best_platform = max(platform_metrics.keys(), 
                          key=lambda p: platform_metrics[p].engagement_rate) if platform_metrics else None
        
        avg_engagement_rate = total_engagement / total_views if total_views > 0 else 0.0
        
        return CrossPlatformAnalytics(
            content_id=plan.content_id,
            total_views=total_views,
            total_engagement=total_engagement,
            average_engagement_rate=avg_engagement_rate,
            best_performing_platform=best_platform,
            platform_metrics=platform_metrics,
            roi_analysis={
                "total_revenue": sum(m.revenue for m in platform_metrics.values()),
                "cost_per_acquisition": random.uniform(0.5, 2.0),
                "return_on_investment": random.uniform(1.2, 3.5)
            },
            audience_insights={
                "primary_demographics": "18-34 years",
                "engagement_patterns": "High morning and evening engagement",
                "content_preferences": "Video content performs 40% better than images"
            }
        )

    async def optimize_distribution(
        self,
        plan_id: str,
        performance_data: Optional[CrossPlatformAnalytics] = None
    ) -> Dict[str, Any]:
        """Optimize distribution based on performance"""
        
        if plan_id not in self.distribution_plans:
            raise ValueError(f"Distribution plan {plan_id} not found")
        
        plan = self.distribution_plans[plan_id]
        
        if performance_data is None:
            performance_data = await self.track_performance(plan_id)
        
        optimization_recommendations = []
        
        # Analyze platform performance
        if performance_data.platform_metrics:
            # Find underperforming platforms
            avg_engagement = performance_data.average_engagement_rate
            
            for platform, metrics in performance_data.platform_metrics.items():
                if metrics.engagement_rate < avg_engagement * 0.7:
                    optimization_recommendations.append({
                        "type": "platform_optimization",
                        "platform": platform.value,
                        "issue": "Low engagement rate",
                        "recommendation": f"Adjust content format or posting time for {platform.value}",
                        "current_engagement": metrics.engagement_rate,
                        "target_engagement": avg_engagement
                    })
        
        # Content format optimization
        best_platform = performance_data.best_performing_platform
        if best_platform:
            best_format = plan.content_formats.get(best_platform)
            if best_format:
                optimization_recommendations.append({
                    "type": "format_optimization",
                    "recommendation": f"Consider using {best_format.value} format on other platforms",
                    "rationale": f"{best_platform.value} performed best with this format"
                })
        
        # Timing optimization
        optimization_recommendations.append({
            "type": "timing_optimization",
            "recommendation": "Analyze posting times and adjust schedule",
            "suggested_action": "Test different posting times for underperforming platforms"
        })
        
        # Monetization optimization
        if performance_data.roi_analysis.get("return_on_investment", 0) < 2.0:
            optimization_recommendations.append({
                "type": "monetization_optimization",
                "recommendation": "Review monetization strategy",
                "suggested_action": "Enable additional revenue streams or adjust pricing"
            })
        
        return {
            "plan_id": plan_id,
            "optimization_score": min(performance_data.average_engagement_rate * 10, 10.0),
            "recommendations": optimization_recommendations,
            "performance_summary": {
                "total_reach": sum(m.reach for m in performance_data.platform_metrics.values()),
                "best_platform": best_platform.value if best_platform else None,
                "improvement_potential": len(optimization_recommendations) * 10  # Percentage
            },
            "next_actions": [
                "Implement platform-specific optimizations",
                "Test new content formats",
                "Adjust posting schedule",
                "Monitor performance changes"
            ]
        }

    async def get_distribution_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive distribution insights for creator"""
        
        # Find all plans for creator
        creator_plans = [
            plan for plan in self.distribution_plans.values()
            if plan.creator_id == creator_id
        ]
        
        if not creator_plans:
            return {
                "creator_id": creator_id,
                "total_distributions": 0,
                "insights": ["No distribution data available"],
                "recommendations": ["Create your first distribution plan"]
            }
        
        # Aggregate metrics
        total_distributions = len(creator_plans)
        platforms_used = set()
        total_performance_data = []
        
        for plan in creator_plans:
            platforms_used.update(plan.target_platforms)
            try:
                perf_data = await self.track_performance(plan.plan_id)
                total_performance_data.append(perf_data)
            except:
                continue
        
        # Calculate aggregated metrics
        total_views = sum(data.total_views for data in total_performance_data)
        total_engagement = sum(data.total_engagement for data in total_performance_data)
        avg_engagement_rate = total_engagement / total_views if total_views > 0 else 0.0
        
        # Platform performance analysis
        platform_performance = {}
        for platform in platforms_used:
            platform_views = 0
            platform_engagement = 0
            
            for data in total_performance_data:
                if platform in data.platform_metrics:
                    platform_views += data.platform_metrics[platform].views
                    platform_engagement += (
                        data.platform_metrics[platform].likes +
                        data.platform_metrics[platform].shares +
                        data.platform_metrics[platform].comments
                    )
            
            platform_performance[platform.value] = {
                "views": platform_views,
                "engagement": platform_engagement,
                "engagement_rate": platform_engagement / platform_views if platform_views > 0 else 0.0
            }
        
        # Generate insights
        insights = []
        recommendations = []
        
        if total_distributions >= 5:
            insights.append(f"You're an active distributor with {total_distributions} distributions")
        else:
            insights.append(f"You have {total_distributions} distributions - consider increasing frequency")
        
        if platform_performance:
            best_platform = max(platform_performance.keys(), 
                              key=lambda p: platform_performance[p]["engagement_rate"])
            insights.append(f"Your best performing platform is {best_platform}")
            recommendations.append(f"Focus more content on {best_platform}")
        
        if avg_engagement_rate > 0.05:
            insights.append("You have strong audience engagement")
        else:
            insights.append("There's room to improve audience engagement")
            recommendations.append("Experiment with different content formats and posting times")
        
        return {
            "creator_id": creator_id,
            "summary": {
                "total_distributions": total_distributions,
                "platforms_used": len(platforms_used),
                "total_views": total_views,
                "total_engagement": total_engagement,
                "average_engagement_rate": avg_engagement_rate
            },
            "platform_performance": platform_performance,
            "insights": insights,
            "recommendations": recommendations,
            "distribution_score": min(avg_engagement_rate * 100 + (total_distributions / 10) * 10, 100),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }


# Global distribution orchestrator instance
_distribution_orchestrator_instance = None


def get_distribution_orchestrator() -> ContentDistributionOrchestrator:
    """Get the global distribution orchestrator instance"""
    global _distribution_orchestrator_instance
    if _distribution_orchestrator_instance is None:
        _distribution_orchestrator_instance = ContentDistributionOrchestrator()
    return _distribution_orchestrator_instance