"""Distribution business service for IA Influencer Agent platform.

This service handles multi-platform content distribution, scheduling,
and cross-platform synchronization for maximum reach and engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.

WARNING: This code is proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution is strictly
prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.content import Content
from ..models.distribution import (
    DistributionPlan, PlatformSchedule, ContentAdaptation,
    DistributionAnalytics, CrossPlatformSync
)
from ..integrations.social_platforms import (
    YouTubeDistributor, InstagramDistributor, TikTokDistributor,
    TwitterDistributor, LinkedInDistributor, FacebookDistributor,
    SpotifyDistributor, SoundCloudDistributor
)
from ..utils.content_formatter import ContentFormatter
from ..utils.scheduler import AdvancedScheduler
from ..utils.analytics_tracker import AnalyticsTracker

logger = logging.getLogger(__name__)

class DistributionStatus(Enum):
    """Distribution status enumeration."""    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRAFT = "draft"

class PlatformType(Enum):
    """Supported platform types."""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"

class ContentAdaptationType(Enum):
    """Content adaptation types for different platforms."""    FORMAT_CONVERSION = "format_conversion"
    RESOLUTION_OPTIMIZATION = "resolution_optimization"
    DURATION_ADJUSTMENT = "duration_adjustment"
    ASPECT_RATIO_CHANGE = "aspect_ratio_change"
    CAPTION_GENERATION = "caption_generation"
    THUMBNAIL_CREATION = "thumbnail_creation"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"

@dataclass
class DistributionTarget:
    """Distribution target configuration."""    platform: PlatformType
    account_id: str
    publish_time: datetime
    adaptation_settings: Dict[str, Any]
    custom_metadata: Dict[str, Any]
    priority: int = 1

@dataclass
class DistributionResult:
    """Distribution operation result."""    platform: PlatformType
    status: DistributionStatus
    platform_post_id: Optional[str]
    published_url: Optional[str]
    error_message: Optional[str]
    analytics_data: Dict[str, Any]
    published_at: Optional[datetime]

@dataclass
class CrossPlatformStrategy:
    """Cross-platform distribution strategy."""    primary_platform: PlatformType
    secondary_platforms: List[PlatformType]
    staggered_release: bool = True
    time_intervals: Dict[PlatformType, int] = None  # minutes between releases
    content_variations: Dict[PlatformType, Dict[str, Any]] = None

class DistributionService:
    """    Comprehensive multi-platform content distribution service.
    
    Handles intelligent content distribution across social media platforms,
    streaming services, and content networks with optimal timing and formatting.
    """    
    def __init__(self):
        self.platform_distributors = {
            PlatformType.YOUTUBE: YouTubeDistributor(),
            PlatformType.INSTAGRAM: InstagramDistributor(),
            PlatformType.TIKTOK: TikTokDistributor(),
            PlatformType.TWITTER: TwitterDistributor(),
            PlatformType.LINKEDIN: LinkedInDistributor(),
            PlatformType.FACEBOOK: FacebookDistributor(),
            PlatformType.SPOTIFY: SpotifyDistributor(),
            PlatformType.SOUNDCLOUD: SoundCloudDistributor()
        }
        
        self.content_formatter = ContentFormatter()
        self.scheduler = AdvancedScheduler()
        self.analytics_tracker = AnalyticsTracker()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def create_distribution_plan(
        self,
        content_id: str,
        targets: List[DistributionTarget],
        strategy: Optional[CrossPlatformStrategy] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Create comprehensive distribution plan for content.
        
        Args:
            content_id: Content identifier
            targets: Distribution targets for different platforms
            strategy: Cross-platform distribution strategy
            db: Database session
            
        Returns:
            Distribution plan with scheduling and optimization details
        """        if db is None:
            db = next(get_db())
        
        try:
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            # Analyze content for platform suitability
            platform_analysis = await self._analyze_content_platform_suitability(content, targets)
            
            # Optimize publishing schedule
            optimized_schedule = await self._optimize_publishing_schedule(
                content, targets, strategy
            )
            
            # Generate content adaptations
            content_adaptations = await self._generate_content_adaptations(
                content, targets
            )
            
            # Create distribution timeline
            distribution_timeline = await self._create_distribution_timeline(
                optimized_schedule, strategy
            )
            
            # Calculate expected reach and engagement
            projected_metrics = await self._calculate_projected_metrics(
                content, targets, strategy
            )
            
            distribution_plan = {
                "content_id": content_id,
                "plan_id": f"dp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.utcnow(),
                "status": DistributionStatus.PENDING.value,
                "platform_analysis": platform_analysis,
                "optimized_schedule": optimized_schedule,
                "content_adaptations": content_adaptations,
                "distribution_timeline": distribution_timeline,
                "projected_metrics": projected_metrics,
                "strategy": strategy.__dict__ if strategy else None,
                "total_platforms": len(targets)
            }
            
            # Store distribution plan
            await self._store_distribution_plan(distribution_plan, db)
            
            return distribution_plan
            
        except Exception as e:
            logger.error(f"Error creating distribution plan: {str(e)}")
            raise
    
    async def execute_distribution_plan(
        self,
        plan_id: str,
        dry_run: bool = False,
        db: Session = None
    ) -> Dict[str, List[DistributionResult]]:
        """        Execute distribution plan across all target platforms.
        
        Args:
            plan_id: Distribution plan identifier
            dry_run: Whether to perform dry run without actual publishing
            db: Database session
            
        Returns:
            Distribution results for all platforms
        """        if db is None:
            db = next(get_db())
        
        try:
            # Retrieve distribution plan
            plan = await self._get_distribution_plan(plan_id, db)
            if not plan:
                raise ValueError(f"Distribution plan {plan_id} not found")
            
            content = db.query(Content).filter(Content.id == plan["content_id"]).first()
            if not content:
                raise ValueError(f"Content {plan['content_id']} not found")
            
            distribution_results = {
                "immediate": [],
                "scheduled": [],
                "failed": []
            }
            
            # Process immediate publications
            immediate_targets = [
                target for target in plan["optimized_schedule"]
                if target["publish_time"] <= datetime.utcnow() + timedelta(minutes=5)
            ]
            
            if immediate_targets:
                immediate_results = await self._execute_immediate_distribution(
                    content, immediate_targets, dry_run
                )
                distribution_results["immediate"] = immediate_results
            
            # Schedule future publications
            future_targets = [
                target for target in plan["optimized_schedule"]
                if target["publish_time"] > datetime.utcnow() + timedelta(minutes=5)
            ]
            
            if future_targets:
                scheduled_results = await self._schedule_future_distribution(
                    content, future_targets, plan_id
                )
                distribution_results["scheduled"] = scheduled_results
            
            # Update distribution plan status
            await self._update_distribution_plan_status(
                plan_id, DistributionStatus.PUBLISHING, db
            )
            
            # Start analytics tracking
            await self._start_distribution_analytics_tracking(
                plan_id, distribution_results
            )
            
            return distribution_results
            
        except Exception as e:
            logger.error(f"Error executing distribution plan: {str(e)}")
            await self._update_distribution_plan_status(
                plan_id, DistributionStatus.FAILED, db
            )
            raise
    
    async def schedule_recurring_distribution(
        self,
        content_template_id: str,
        platforms: List[PlatformType],
        schedule_pattern: Dict[str, Any],
        duration: timedelta,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Schedule recurring content distribution.
        
        Args:
            content_template_id: Template for content generation
            platforms: Target platforms for distribution
            schedule_pattern: Recurring schedule pattern
            duration: Duration for recurring schedule
            db: Database session
            
        Returns:
            Recurring distribution configuration
        """        if db is None:
            db = next(get_db())
        
        try:
            # Create recurring schedule
            recurring_schedule = await self.scheduler.create_recurring_schedule(
                schedule_pattern, duration
            )
            
            # Generate distribution targets for each occurrence
            recurring_targets = []
            for occurrence in recurring_schedule["occurrences"]:
                targets = [
                    DistributionTarget(
                        platform=platform,
                        account_id=f"default_{platform.value}",
                        publish_time=occurrence["datetime"],
                        adaptation_settings={},
                        custom_metadata={}
                    )
                    for platform in platforms
                ]
                recurring_targets.append({
                    "occurrence_id": occurrence["id"],
                    "publish_time": occurrence["datetime"],
                    "targets": targets
                })
            
            recurring_config = {
                "id": f"rec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "content_template_id": content_template_id,
                "platforms": [p.value for p in platforms],
                "schedule_pattern": schedule_pattern,
                "duration": duration.total_seconds(),
                "recurring_targets": recurring_targets,
                "created_at": datetime.utcnow(),
                "status": "active",
                "total_occurrences": len(recurring_targets)
            }
            
            # Store recurring distribution config
            await self._store_recurring_distribution(recurring_config, db)
            
            # Schedule first batch of distributions
            await self._schedule_next_recurring_batch(recurring_config)
            
            return recurring_config
            
        except Exception as e:
            logger.error(f"Error scheduling recurring distribution: {str(e)}")
            raise
    
    async def optimize_cross_platform_timing(
        self,
        user_id: str,
        platforms: List[PlatformType],
        content_type: str,
        target_audience: Dict[str, Any],
        db: Session = None
    ) -> Dict[str, Any]:
        """        Optimize posting times across platforms based on audience behavior.
        
        Args:
            user_id: User identifier
            platforms: Target platforms
            content_type: Type of content being distributed
            target_audience: Target audience characteristics
            db: Database session
            
        Returns:
            Optimized timing recommendations
        """        if db is None:
            db = next(get_db())
        
        try:
            timing_analysis = {}
            
            for platform in platforms:
                # Analyze platform-specific optimal timing
                platform_timing = await self._analyze_platform_optimal_timing(
                    user_id, platform, content_type, target_audience, db
                )
                
                # Get historical performance data
                historical_performance = await self._get_historical_performance_by_time(
                    user_id, platform, content_type, db
                )
                
                # Calculate audience activity patterns
                audience_activity = await self._analyze_audience_activity_patterns(
                    user_id, platform, target_audience, db
                )
                
                timing_analysis[platform.value] = {
                    "optimal_times": platform_timing["optimal_times"],
                    "peak_engagement_hours": platform_timing["peak_hours"],
                    "audience_timezone_distribution": audience_activity["timezones"],
                    "historical_best_times": historical_performance["best_times"],
                    "day_of_week_performance": historical_performance["day_performance"],
                    "engagement_score_by_hour": platform_timing["hourly_scores"]
                }
            
            # Generate cross-platform strategy
            cross_platform_strategy = await self._generate_cross_platform_timing_strategy(
                timing_analysis, content_type
            )
            
            # Calculate staggered release schedule
            staggered_schedule = await self._calculate_staggered_release_schedule(
                timing_analysis, cross_platform_strategy
            )
            
            optimization_result = {
                "user_id": user_id,
                "platforms": [p.value for p in platforms],
                "content_type": content_type,
                "timing_analysis": timing_analysis,
                "cross_platform_strategy": cross_platform_strategy,
                "staggered_schedule": staggered_schedule,
                "recommendations": await self._generate_timing_recommendations(timing_analysis),
                "confidence_score": await self._calculate_timing_confidence_score(timing_analysis),
                "generated_at": datetime.utcnow()
            }
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing cross-platform timing: {str(e)}")
            raise
    
    async def track_distribution_performance(
        self,
        plan_id: str,
        time_period: int = 7,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Track and analyze distribution performance across platforms.
        
        Args:
            plan_id: Distribution plan identifier
            time_period: Time period in days for analysis
            db: Database session
            
        Returns:
            Comprehensive distribution performance analytics
        """        if db is None:
            db = next(get_db())
        
        try:
            # Get distribution plan and results
            plan = await self._get_distribution_plan(plan_id, db)
            distribution_results = await self._get_distribution_results(plan_id, db)
            
            performance_data = {
                "plan_overview": {
                    "plan_id": plan_id,
                    "content_id": plan["content_id"],
                    "total_platforms": len(distribution_results),
                    "successful_publications": len([r for r in distribution_results if r["status"] == "published"]),
                    "failed_publications": len([r for r in distribution_results if r["status"] == "failed"]),
                    "average_publish_delay": await self._calculate_average_publish_delay(distribution_results),
                    "tracking_period_days": time_period
                },
                "platform_performance": {},
                "comparative_analysis": {},
                "engagement_timeline": {},
                "roi_analysis": {},
                "optimization_insights": []
            }
            
            # Analyze performance by platform
            for result in distribution_results:
                platform = result["platform"]
                
                # Get detailed analytics from platform
                platform_analytics = await self._get_platform_analytics(
                    result["platform_post_id"], platform, time_period
                )
                
                performance_data["platform_performance"][platform] = {
                    "post_id": result["platform_post_id"],
                    "published_url": result["published_url"],
                    "publish_status": result["status"],
                    "analytics": platform_analytics,
                    "engagement_rate": platform_analytics.get("engagement_rate", 0),
                    "reach": platform_analytics.get("reach", 0),
                    "impressions": platform_analytics.get("impressions", 0),
                    "clicks": platform_analytics.get("clicks", 0),
                    "shares": platform_analytics.get("shares", 0),
                    "comments": platform_analytics.get("comments", 0),
                    "likes": platform_analytics.get("likes", 0)
                }
            
            # Comparative analysis across platforms
            performance_data["comparative_analysis"] = await self._perform_comparative_analysis(
                performance_data["platform_performance"]
            )
            
            # Generate engagement timeline
            performance_data["engagement_timeline"] = await self._generate_engagement_timeline(
                plan_id, time_period, db
            )
            
            # Calculate ROI analysis
            performance_data["roi_analysis"] = await self._calculate_distribution_roi(
                plan, performance_data["platform_performance"]
            )
            
            # Generate optimization insights
            performance_data["optimization_insights"] = await self._generate_optimization_insights(
                performance_data
            )
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error tracking distribution performance: {str(e)}")
            raise
    
    async def synchronize_cross_platform_content(
        self,
        content_id: str,
        platforms: List[PlatformType],
        sync_settings: Dict[str, Any],
        db: Session = None
    ) -> Dict[str, Any]:
        """        Synchronize content updates and interactions across platforms.
        
        Args:
            content_id: Content identifier
            platforms: Platforms to synchronize
            sync_settings: Synchronization configuration
            db: Database session
            
        Returns:
            Synchronization results and status
        """        if db is None:
            db = next(get_db())
        
        try:
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            sync_results = {
                "content_id": content_id,
                "sync_started_at": datetime.utcnow(),
                "platforms": platforms,
                "sync_operations": [],
                "errors": [],
                "success_count": 0,
                "total_operations": 0
            }
            
            # Get current content state across platforms
            current_states = {}
            for platform in platforms:
                try:
                    state = await self._get_platform_content_state(
                        content_id, platform, db
                    )
                    current_states[platform.value] = state
                except Exception as e:
                    sync_results["errors"].append({
                        "platform": platform.value,
                        "operation": "get_state",
                        "error": str(e)
                    })
            
            # Perform synchronization operations based on settings
            if sync_settings.get("sync_metadata", True):
                metadata_sync = await self._synchronize_metadata(
                    content, current_states, platforms
                )
                sync_results["sync_operations"].extend(metadata_sync)
            
            if sync_settings.get("sync_engagement", True):
                engagement_sync = await self._synchronize_engagement_data(
                    content_id, current_states, platforms, db
                )
                sync_results["sync_operations"].extend(engagement_sync)
            
            if sync_settings.get("sync_comments", False):
                comments_sync = await self._synchronize_comments(
                    content_id, current_states, platforms, db
                )
                sync_results["sync_operations"].extend(comments_sync)
            
            if sync_settings.get("sync_analytics", True):
                analytics_sync = await self._synchronize_analytics_data(
                    content_id, current_states, platforms, db
                )
                sync_results["sync_operations"].extend(analytics_sync)
            
            # Calculate success metrics
            sync_results["total_operations"] = len(sync_results["sync_operations"])
            sync_results["success_count"] = len([
                op for op in sync_results["sync_operations"]
                if op.get("status") == "success"
            ])
            sync_results["sync_completed_at"] = datetime.utcnow()
            sync_results["success_rate"] = (
                sync_results["success_count"] / sync_results["total_operations"]
                if sync_results["total_operations"] > 0 else 0
            )
            
            # Store synchronization results
            await self._store_sync_results(sync_results, db)
            
            return sync_results
            
        except Exception as e:
            logger.error(f"Error synchronizing cross-platform content: {str(e)}")
            raise
    
    # Private helper methods
    async def _analyze_content_platform_suitability(
        self,
        content: Content,
        targets: List[DistributionTarget]
    ) -> Dict[str, Any]:
        """Analyze content suitability for different platforms."""        suitability_analysis = {}
        
        for target in targets:
            platform = target.platform
            
            # Analyze content format compatibility
            format_compatibility = await self._check_format_compatibility(
                content, platform
            )
            
            # Analyze content length/duration suitability
            duration_suitability = await self._check_duration_suitability(
                content, platform
            )
            
            # Analyze audience alignment
            audience_alignment = await self._check_audience_alignment(
                content, platform
            )
            
            # Calculate overall suitability score
            suitability_score = (
                format_compatibility * 0.3 +
                duration_suitability * 0.3 +
                audience_alignment * 0.4
            )
            
            suitability_analysis[platform.value] = {
                "suitability_score": round(suitability_score, 2),
                "format_compatibility": format_compatibility,
                "duration_suitability": duration_suitability,
                "audience_alignment": audience_alignment,
                "recommended": suitability_score >= 0.7,
                "adaptation_required": format_compatibility < 0.8
            }
        
        return suitability_analysis
    
    async def _optimize_publishing_schedule(
        self,
        content: Content,
        targets: List[DistributionTarget],
        strategy: Optional[CrossPlatformStrategy]
    ) -> List[Dict[str, Any]]:
        """Optimize publishing schedule for maximum engagement."""        optimized_schedule = []
        
        if strategy and strategy.staggered_release:
            # Implement staggered release strategy
            primary_target = next(
                (t for t in targets if t.platform == strategy.primary_platform),
                targets[0]
            )
            
            # Schedule primary platform first
            optimized_schedule.append({
                "platform": primary_target.platform.value,
                "account_id": primary_target.account_id,
                "publish_time": primary_target.publish_time,
                "priority": 1,
                "is_primary": True
            })
            
            # Schedule secondary platforms with intervals
            for i, target in enumerate(targets):
                if target.platform != strategy.primary_platform:
                    interval = strategy.time_intervals.get(target.platform, 15) if strategy.time_intervals else 15
                    adjusted_time = primary_target.publish_time + timedelta(minutes=interval * (i + 1))
                    
                    optimized_schedule.append({
                        "platform": target.platform.value,
                        "account_id": target.account_id,
                        "publish_time": adjusted_time,
                        "priority": i + 2,
                        "is_primary": False
                    })
        else:
            # Simultaneous release
            for target in targets:
                optimized_schedule.append({
                    "platform": target.platform.value,
                    "account_id": target.account_id,
                    "publish_time": target.publish_time,
                    "priority": target.priority,
                    "is_primary": target.priority == 1
                })
        
        return optimized_schedule
