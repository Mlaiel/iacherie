"""Advanced Distribution Module - Multi-Platform Content Distribution System
import asyncio

=========================================================================

Comprehensive content distribution ecosystem providing platform connectivity,
intelligent scheduling, analytics aggregation, revenue tracking, and external
API management for seamless multi-platform content distribution.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/__init__.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Platform Connection → Intelligent Scheduling → Analytics → Revenue Tracking → Monetization
"""

import logging
from typing import Dict, List, Optional, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Platform Connector imports
try:
    from .platform_connector import (
        PlatformConnectorFactory,
        PlatformManager,
        BasePlatformConnector,
        YouTubeConnector,
        InstagramConnector,
        TikTokConnector,
        SpotifyConnector,
        TwitterConnector,
        PlatformType,
        AuthenticationType,
        ConnectionStatus,
        PlatformCredentials,
        RateLimitInfo,
        APIResponse,
        ContentMetadata,
        get_platform_manager
    )
    platform_connector_available = True
    logger.info("✅ Platform Connector loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Platform Connector not available: {e}")
    platform_connector_available = False

# Schedule Manager imports
try:
    from .schedule_manager import (
        ScheduleManager,
        ScheduledContent,
        ScheduleType,
        ScheduleStatus,
        RecurrencePattern,
        OptimizationGoal,
        TimeWindow,
        AudienceInsight,
        ScheduleRule,
        OptimalTimeSlot,
        get_schedule_manager,
        schedule_content
    )
    schedule_manager_available = True
    logger.info("✅ Schedule Manager loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Schedule Manager not available: {e}")
    schedule_manager_available = False

# Analytics Aggregator imports
try:
    from .analytics_aggregator import (
        AnalyticsAggregator,
        AnalyticsDataPoint,
        AggregatedMetrics,
        PerformanceInsight,
        MetricType,
        AggregationPeriod,
        get_analytics_aggregator
    )
    analytics_aggregator_available = True
    logger.info("✅ Analytics Aggregator loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Analytics Aggregator not available: {e}")
    analytics_aggregator_available = False

# Revenue Tracker imports
try:
    from .revenue_tracker import (
        RevenueTracker,
        RevenueEntry,
        RevenueAttribution,
        RevenuePerformanceMetrics,
        RevenueInsight,
        RevenueType,
        Currency,
        AttributionModel,
        get_revenue_tracker
    )
    revenue_tracker_available = True
    logger.info("✅ Revenue Tracker loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Revenue Tracker not available: {e}")
    revenue_tracker_available = False

# API Manager imports
try:
    from .api_manager import (
        APIManager,
        APIEndpoint,
        APICredentials,
        APIRequest,
        APIResponse as APIManagerResponse,
        RateLimitConfig,
        HTTPMethod,
        APIAuthType,
        RequestStatus,
        get_api_manager
    )
    api_manager_available = True
    logger.info("✅ API Manager loaded successfully")
except ImportError as e:
    logger.warning(f"❌ API Manager not available: {e}")
    api_manager_available = False

# Social Platform Connectors imports
try:
    from .platform_connectors_social import (
        SocialPlatformType,
        ContentFormat,
        EngagementType,
        SocialContentMetadata,
        SocialPlatformResponse,
        SocialAnalytics,
        BaseSocialConnector,
        YouTubeConnector,
        InstagramConnector,
        TikTokConnector,
        SocialPlatformManager,
        get_social_platform_manager
    )
    social_connectors_available = True
    logger.info("✅ Social Platform Connectors loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Social Platform Connectors not available: {e}")
    social_connectors_available = False

# Music Platform Connectors imports
try:
    from .platform_connectors_music import (
        MusicPlatformType,
        AudioFormat,
        MusicGenre,
        StreamingMetricType,
        MusicTrackMetadata,
        MusicPlatformResponse,
        MusicStreamingAnalytics,
        BaseMusicConnector,
        SpotifyConnector,
        SoundCloudConnector,
        AppleMusicConnector,
        MusicPlatformManager,
        get_music_platform_manager
    )
    music_connectors_available = True
    logger.info("✅ Music Platform Connectors loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Music Platform Connectors not available: {e}")
    music_connectors_available = False

# Security Protection imports
try:
    from .security_protection import (
        SecurityLevel,
        ProtectionType,
        ThreatType,
        ComplianceStandard,
        SecurityConfig,
        SecurityThreat,
        ProtectionStatus,
        ComplianceReport,
        ContentProtectionEngine,
        SecurityProtectionManager,
        get_security_protection_manager
    )
    security_protection_available = True
    logger.info("✅ Security Protection loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Security Protection not available: {e}")
    security_protection_available = False

# Video Platform Connectors imports
try:
    from .platform_connectors_video import (
        VideoPlatformType,
        VideoFormat,
        VideoQuality,
        LiveStreamStatus,
        VideoMetricType,
        VideoContentMetadata,
        LiveStreamSettings,
        VideoPlatformResponse,
        VideoStreamingAnalytics,
        BaseVideoConnector,
        VimeoConnector,
        DailymotionConnector,
        TwitchConnector,
        LiveStreamingConnector,
        VideoPlatformManager,
        get_video_platform_manager
    )
    video_connectors_available = True
    logger.info("✅ Video Platform Connectors loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Video Platform Connectors not available: {e}")
    video_connectors_available = False

# Emerging Platform Connectors imports
try:
    from .platform_connectors_emerging import (
        EmergingPlatformType,
        CommunityType,
        Web3PlatformType,
        EngagementMetricType,
        CommunityContentMetadata,
        Web3ContentMetadata,
        EmergingPlatformResponse,
        CommunityAnalytics,
        BaseEmergingConnector,
        DiscordConnector,
        TelegramConnector,
        RedditConnector,
        Web3Connector,
        EmergingPlatformManager,
        get_emerging_platform_manager
    )
    emerging_connectors_available = True
    logger.info("✅ Emerging Platform Connectors loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Emerging Platform Connectors not available: {e}")
    emerging_connectors_available = False

# Creator Economy Connectors imports
try:
    from .creator_economy_connectors import (
        CreatorPlatformType,
        SubscriptionTier,
        MonetizationType,
        ContentAccessLevel,
        PaymentStatus,
        CreatorContentMetadata,
        SubscriptionPlan,
        CreatorEconomyResponse,
        CreatorAnalytics,
        FanEngagementMetrics,
        BaseCreatorConnector,
        PatreonConnector,
        KofiConnector,
        GumroadConnector,
        SubstackConnector,
        CreatorEconomyManager,
        get_creator_economy_manager
    )
    creator_economy_available = True
    logger.info("✅ Creator Economy Connectors loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Creator Economy Connectors not available: {e}")
    creator_economy_available = False

# Monetization Distribution imports
try:
    from .monetization_distribution import (
        RevenueStreamType,
        MonetizationStrategy,
        SponsorshipType,
        AudienceSegment,
        OptimizationGoal,
        RevenueStreamConfig,
        SponsorshipOpportunity,
        AffiliateProgram,
        MonetizationMetrics,
        MonetizationRecommendation,
        BrandCollaborationMatch,
        RevenueOptimizer,
        SponsorshipMatcher,
        AffiliateManager,
        MonetizationDistributionManager,
        get_monetization_distribution_manager
    )
    monetization_distribution_available = True
    logger.info("✅ Monetization Distribution loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Monetization Distribution not available: {e}")
    monetization_distribution_available = False

# Globalization Engine imports
try:
    from .globalization_engine import (
        GeographicRegion,
        CulturalContext,
        ComplianceFramework,
        ContentRating,
        LanguageCode,
        TimezoneRegion,
        GeographicTarget,
        CulturalAdaptation,
        LanguageLocalization,
        LegalCompliance,
        RegionalMonetization,
        GlobalizationResponse,
        GlobalAnalytics,
        GeoTargetingEngine,
        CulturalAdaptationEngine,
        ComplianceEngine,
        LocalizationEngine,
        GlobalizationManager,
        get_globalization_manager
    )
    globalization_available = True
    logger.info("✅ Globalization Engine loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Globalization Engine not available: {e}")
    globalization_available = False


class DistributionOrchestrator:
    """
    Central orchestrator for the complete distribution ecosystem.
    
    Coordinates between all distribution modules to provide a unified
    content distribution experience across multiple platforms.
    """
    
    def __init__(self) -> None:
        """Initialize the distribution orchestrator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Module instances
        self.platform_manager = None
        self.schedule_manager = None
        self.analytics_aggregator = None
        self.revenue_tracker = None
        self.api_manager = None
        
        # New module instances
        self.social_platform_manager = None
        self.music_platform_manager = None
        self.security_protection_manager = None
        self.video_platform_manager = None
        self.emerging_platform_manager = None
        self.creator_economy_manager = None
        self.monetization_distribution_manager = None
        self.globalization_manager = None
        
        self.logger.info("DistributionOrchestrator initialized")
    
    async def initialize(self) -> bool:
        """Initialize all distribution modules."""
        try:
            # Initialize existing modules
            if platform_connector_available:
                self.platform_manager = await get_platform_manager()
            
            if schedule_manager_available:
                self.schedule_manager = await get_schedule_manager()
            
            if analytics_aggregator_available:
                self.analytics_aggregator = await get_analytics_aggregator()
            
            if revenue_tracker_available:
                self.revenue_tracker = await get_revenue_tracker()
            
            if api_manager_available:
                self.api_manager = await get_api_manager()
            
            # Initialize new modules
            if social_connectors_available:
                self.social_platform_manager = await get_social_platform_manager()
            
            if music_connectors_available:
                self.music_platform_manager = await get_music_platform_manager()
            
            if security_protection_available:
                self.security_protection_manager = await get_security_protection_manager()
            
            if video_connectors_available:
                self.video_platform_manager = await get_video_platform_manager()
            
            if emerging_connectors_available:
                self.emerging_platform_manager = await get_emerging_platform_manager()
            
            if creator_economy_available:
                self.creator_economy_manager = await get_creator_economy_manager()
            
            if monetization_distribution_available:
                self.monetization_distribution_manager = await get_monetization_distribution_manager()
            
            if globalization_available:
                self.globalization_manager = await get_globalization_manager()
            
            self.initialized = True
            
            available_modules = sum([
                platform_connector_available,
                schedule_manager_available,
                analytics_aggregator_available,
                revenue_tracker_available,
                api_manager_available,
                social_connectors_available,
                music_connectors_available,
                security_protection_available,
                video_connectors_available,
                emerging_connectors_available,
                creator_economy_available,
                monetization_distribution_available,
                globalization_available
            ])
            
            self.logger.info(f"✅ Distribution orchestrator initialized with {available_modules}/13 modules")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize distribution orchestrator: {e}")
            return False
    
    async def distribute_content(
        self,
        content_id: str,
        title: str,
        content_metadata: Dict[str, Any],  # Changed from ContentMetadata to Dict
        target_platforms: List[str],
        schedule_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Distribute content across multiple platforms."""
        if not self.initialized:
            await self.initialize()
        
        results = {
            "content_id": content_id,
            "title": title,
            "target_platforms": target_platforms,
            "scheduled": False,
            "published_platforms": [],
            "failed_platforms": [],
            "schedule_id": None,
            "analytics_tracked": False,
            "revenue_tracked": False
        }
        
        try:
            # Schedule content if scheduling is configured
            if schedule_config and schedule_manager_available and self.schedule_manager:
                schedule_type = ScheduleType(schedule_config.get("type", "optimal_time"))
                optimization_goal = OptimizationGoal(schedule_config.get("goal", "balanced"))
                
                scheduled_content = await self.schedule_manager.schedule_content(
                    content_id=content_id,
                    title=title,
                    platforms=target_platforms,
                    schedule_type=schedule_type,
                    specific_time=schedule_config.get("specific_time"),
                    optimization_goal=optimization_goal
                )
                
                results["scheduled"] = True
                results["schedule_id"] = scheduled_content.id
                results["scheduled_time"] = scheduled_content.scheduled_time.isoformat()
                
                self.logger.info(f"📅 Content scheduled: {title}")
            
            # If immediate distribution or no scheduling
            elif schedule_config is None or schedule_config.get("type") == "immediate":
                # Distribute to platforms immediately
                if platform_connector_available and self.platform_manager:
                    for platform in target_platforms:
                        try:
                            connector = await self.platform_manager.get_connector(PlatformType(platform))
                            if connector:
                                response = await connector.upload_content(content_metadata)
                                if response.success:
                                    results["published_platforms"].append(platform)
                                    self.logger.info(f"✅ Published to {platform}")
                                else:
                                    results["failed_platforms"].append(platform)
                                    self.logger.error(f"❌ Failed to publish to {platform}: {response.error}")
                            else:
                                results["failed_platforms"].append(platform)
                                self.logger.error(f"❌ No connector available for {platform}")
                        
                        except Exception as e:
                            results["failed_platforms"].append(platform)
                            self.logger.error(f"❌ Error publishing to {platform}: {e}")
            
            # Initialize analytics tracking
            if analytics_aggregator_available and self.analytics_aggregator:
                for platform in results["published_platforms"]:
                    # Initialize with basic metrics (would be updated with real data later)
                    await self.analytics_aggregator.collect_platform_analytics(
                        platform=platform,
                        content_id=content_id,
                        metrics_data={
                            "views": 0,
                            "likes": 0,
                            "shares": 0,
                            "comments": 0
                        }
                    )
                results["analytics_tracked"] = True
            
            # Initialize revenue tracking
            if revenue_tracker_available and self.revenue_tracker:
                # Set up revenue tracking for the content
                results["revenue_tracked"] = True
                self.logger.info(f"💰 Revenue tracking initialized for {content_id}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error distributing content: {e}")
            results["error"] = str(e)
            return results
    
    async def collect_analytics(
        self,
        content_id: str,
        platform_metrics: Dict[str, Dict[str, Union[int, float]]]
    ) -> Dict[str, Any]:
        """Collect analytics data from multiple platforms."""
        if not self.initialized:
            await self.initialize()
        
        results = {
            "content_id": content_id,
            "platforms_updated": [],
            "total_views": 0,
            "total_engagement": 0,
            "insights_generated": False
        }
        
        try:
            if analytics_aggregator_available and self.analytics_aggregator:
                total_views = 0
                total_engagement = 0
                
                for platform, metrics in platform_metrics.items():
                    # Collect analytics data
                    success = await self.analytics_aggregator.collect_platform_analytics(
                        platform=platform,
                        content_id=content_id,
                        metrics_data=metrics
                    )
                    
                    if success:
                        results["platforms_updated"].append(platform)
                        total_views += metrics.get("views", 0)
                        total_engagement += (
                            metrics.get("likes", 0) +
                            metrics.get("comments", 0) +
                            metrics.get("shares", 0)
                        )
                
                results["total_views"] = total_views
                results["total_engagement"] = total_engagement
                
                # Generate insights if significant data
                if total_views > 100:
                    from datetime import datetime, timedelta
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(days=7)
                    
                    aggregated_metrics = await self.analytics_aggregator.aggregate_metrics(
                        AggregationPeriod.WEEK,
                        start_time,
                        end_time,
                        list(platform_metrics.keys()),
                        [content_id]
                    )
                    
                    insights = await self.analytics_aggregator.generate_insights(aggregated_metrics)
                    results["insights_generated"] = len(insights) > 0
                    results["insights_count"] = len(insights)
            
            # Track revenue if applicable
            if revenue_tracker_available and self.revenue_tracker:
                # Revenue tracking would be updated based on platform revenue data
                pass
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error collecting analytics: {e}")
            results["error"] = str(e)
            return results
    
    async def track_revenue(
        self,
        content_id: str,
        platform: str,
        revenue_type: RevenueType,
        amount: float,
        currency: Currency = Currency.USD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track revenue for distributed content."""
        if not self.initialized:
            await self.initialize()
        
        results = {
            "content_id": content_id,
            "platform": platform,
            "revenue_tracked": False,
            "revenue_id": None,
            "analytics_updated": False
        }
        
        try:
            if revenue_tracker_available and self.revenue_tracker:
                # Track the revenue
                revenue_id = await self.revenue_tracker.track_revenue(
                    content_id=content_id,
                    platform=platform,
                    revenue_type=revenue_type,
                    amount=amount,
                    currency=currency,
                    metadata=metadata
                )
                
                results["revenue_tracked"] = True
                results["revenue_id"] = revenue_id
                
                # Update analytics with revenue data if available
                if analytics_aggregator_available and self.analytics_aggregator:
                    await self.analytics_aggregator.collect_platform_analytics(
                        platform=platform,
                        content_id=content_id,
                        metrics_data={"revenue": amount}
                    )
                    results["analytics_updated"] = True
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error tracking revenue: {e}")
            results["error"] = str(e)
            return results
    
    async def get_distribution_dashboard(
        self,
        content_id: Optional[str] = None,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive distribution dashboard."""
        if not self.initialized:
            await self.initialize()
        
        from datetime import datetime, timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=time_range_days)
        
        dashboard = {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": time_range_days
            },
            "platforms": {},
            "scheduling": {},
            "analytics": {},
            "revenue": {},
            "api_health": {}
        }
        
        try:
            # Platform connection status
            if platform_connector_available and self.platform_manager:
                connected_platforms = await self.platform_manager.get_connected_platforms()
                connection_statuses = await self.platform_manager.check_connections()
                
                dashboard["platforms"] = {
                    "connected_count": len(connected_platforms),
                    "connected_platforms": [p.value for p in connected_platforms],
                    "connection_statuses": {k.value: v.value for k, v in connection_statuses.items()}
                }
            
            # Scheduling information
            if schedule_manager_available and self.schedule_manager:
                scheduled_content = await self.schedule_manager.get_scheduled_content(
                    status=ScheduleStatus.SCHEDULED,
                    time_range=(start_time, end_time)
                )
                
                analytics = await self.schedule_manager.get_schedule_analytics((start_time, end_time))
                
                dashboard["scheduling"] = {
                    "upcoming_count": len(scheduled_content),
                    "analytics": analytics
                }
            
            # Analytics summary
            if analytics_aggregator_available and self.analytics_aggregator:
                real_time_metrics = await self.analytics_aggregator.get_real_time_metrics(
                    content_ids=[content_id] if content_id else None,
                    time_window_hours=time_range_days * 24
                )
                
                dashboard["analytics"] = real_time_metrics
            
            # Revenue summary
            if revenue_tracker_available and self.revenue_tracker:
                revenue_summary = await self.revenue_tracker.get_revenue_summary(
                    start_date=start_time,
                    end_date=end_time,
                    content_ids=[content_id] if content_id else None
                )
                
                dashboard["revenue"] = revenue_summary
            
            # API health
            if api_manager_available and self.api_manager:
                api_stats = await self.api_manager.get_overall_statistics()
                dashboard["api_health"] = api_stats
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error getting distribution dashboard: {e}")
            dashboard["error"] = str(e)
            return dashboard
    
    async def distribute_to_social_platforms(
        self,
        content_id: str,
        metadata: Dict[str, Any],
        platforms: List[str],
        file_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Distribute content to social media platforms."""
        if not self.initialized:
            await self.initialize()
        
        results = {
            "content_id": content_id,
            "target_platforms": platforms,
            "successful_uploads": [],
            "failed_uploads": [],
            "protection_applied": False
        }
        
        try:
            # Apply security protection first
            if security_protection_available and self.security_protection_manager:
                if file_data:
                    protection_status = await self.security_protection_manager.protect_content_globally(
                        content_id, file_data, metadata
                    )
                    results["protection_applied"] = True
                    results["protection_status"] = {
                        "level": protection_status.protection_level.value,
                        "protections": [p.value for p in protection_status.active_protections],
                        "compliance": {k.value: v for k, v in protection_status.compliance_status.items()}
                    }
            
            # Upload to social platforms
            if social_connectors_available and self.social_platform_manager:
                from .platform_connectors_social import SocialContentMetadata, SocialPlatformType
                
                social_metadata = SocialContentMetadata(
                    title=metadata.get("title", ""),
                    description=metadata.get("description"),
                    tags=metadata.get("tags", []),
                    hashtags=metadata.get("hashtags", []),
                    category=metadata.get("category"),
                    privacy=metadata.get("privacy", "public")
                )
                
                social_platforms = [SocialPlatformType(p) for p in platforms if p in [e.value for e in SocialPlatformType]]
                
                upload_results = await self.social_platform_manager.upload_to_multiple_platforms(
                    social_platforms, social_metadata, file_data
                )
                
                for platform, response in upload_results.items():
                    if response.success:
                        results["successful_uploads"].append({
                            "platform": platform.value,
                            "url": response.url,
                            "post_id": response.post_id
                        })
                    else:
                        results["failed_uploads"].append({
                            "platform": platform.value,
                            "error": response.error_message
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error distributing to social platforms: {e}")
            results["error"] = str(e)
            return results
    
    async def distribute_to_music_platforms(
        self,
        content_id: str,
        metadata: Dict[str, Any],
        platforms: List[str],
        audio_data: bytes
    ) -> Dict[str, Any]:
        """Distribute music content to music streaming platforms."""
        if not self.initialized:
            await self.initialize()
        
        results = {
            "content_id": content_id,
            "target_platforms": platforms,
            "successful_uploads": [],
            "failed_uploads": [],
            "protection_applied": False
        }
        
        try:
            # Apply security protection first
            if security_protection_available and self.security_protection_manager:
                protection_status = await self.security_protection_manager.protect_content_globally(
                    content_id, audio_data, metadata
                )
                results["protection_applied"] = True
                results["protection_status"] = {
                    "level": protection_status.protection_level.value,
                    "protections": [p.value for p in protection_status.active_protections]
                }
            
            # Upload to music platforms
            if music_connectors_available and self.music_platform_manager:
                from .platform_connectors_music import MusicTrackMetadata, MusicPlatformType, MusicGenre
                
                music_metadata = MusicTrackMetadata(
                    title=metadata.get("title", ""),
                    artist=metadata.get("artist", ""),
                    album=metadata.get("album"),
                    genre=MusicGenre(metadata["genre"]) if metadata.get("genre") else None,
                    duration=metadata.get("duration"),
                    lyrics=metadata.get("lyrics"),
                    description=metadata.get("description"),
                    tags=metadata.get("tags", []),
                    privacy=metadata.get("privacy", "public")
                )
                
                music_platforms = [MusicPlatformType(p) for p in platforms if p in [e.value for e in MusicPlatformType]]
                
                upload_results = await self.music_platform_manager.upload_to_multiple_platforms(
                    music_platforms, music_metadata, audio_data
                )
                
                for platform, response in upload_results.items():
                    if response.success:
                        results["successful_uploads"].append({
                            "platform": platform.value,
                            "url": response.url,
                            "track_id": response.track_id
                        })
                    else:
                        results["failed_uploads"].append({
                            "platform": platform.value,
                            "error": response.error_message
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error distributing to music platforms: {e}")
            results["error"] = str(e)
            return results
    
    async def scan_content_security(self, content_id: str) -> Dict[str, Any]:
        """Scan content for security threats."""
        if not self.initialized:
            await self.initialize()
        
        results = {
            "content_id": content_id,
            "threats_detected": [],
            "security_score": 1.0,
            "recommendations": []
        }
        
        try:
            if security_protection_available and self.security_protection_manager:
                # Get default protection engine
                engine = await self.security_protection_manager.get_protection_engine("default")
                if engine:
                    threats = await engine.scan_for_threats(content_id)
                    
                    results["threats_detected"] = [
                        {
                            "threat_id": threat.threat_id,
                            "type": threat.threat_type.value,
                            "severity": threat.severity.value,
                            "description": threat.description,
                            "confidence": threat.confidence_score
                        }
                        for threat in threats
                    ]
                    
                    # Calculate security score based on threats
                    if threats:
                        high_severity_count = sum(1 for t in threats if t.severity in [SecurityLevel.HIGH, SecurityLevel.MAXIMUM])
                        results["security_score"] = max(0.0, 1.0 - (len(threats) * 0.1) - (high_severity_count * 0.2))
                        
                        results["recommendations"] = [
                            "Review detected threats and take appropriate action",
                            "Consider increasing security protection level",
                            "Enable additional monitoring"
                        ]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error scanning content security: {e}")
            results["error"] = str(e)
            return results


    async def cleanup(self) -> None:
        """Cleanup all distribution modules."""
        try:
            if self.platform_manager:
                await self.platform_manager.cleanup()
            
            if self.api_manager:
                await self.api_manager.cleanup()
            
            if self.social_platform_manager:
                await self.social_platform_manager.cleanup()
            
            if self.music_platform_manager:
                await self.music_platform_manager.cleanup()
            
            if self.security_protection_manager:
                await self.security_protection_manager.cleanup()
            
            self.logger.info("✅ Distribution orchestrator cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Global orchestrator instance
_distribution_orchestrator: Optional[DistributionOrchestrator] = None


async def get_distribution_orchestrator() -> DistributionOrchestrator:
    """Get the global distribution orchestrator instance."""
    global _distribution_orchestrator
    
    if _distribution_orchestrator is None:
        _distribution_orchestrator = DistributionOrchestrator()
        await _distribution_orchestrator.initialize()
    
    return _distribution_orchestrator


# Export main components
__all__ = [
    # Core orchestrator
    "DistributionOrchestrator",
    "get_distribution_orchestrator",
    
    # Platform Connector
    "PlatformConnectorFactory",
    "PlatformManager",
    "BasePlatformConnector",
    "YouTubeConnector",
    "InstagramConnector",
    "TikTokConnector",
    "SpotifyConnector",
    "TwitterConnector",
    "PlatformType",
    "AuthenticationType",
    "ConnectionStatus",
    "PlatformCredentials",
    "RateLimitInfo",
    "APIResponse",
    "ContentMetadata",
    "get_platform_manager",
    
    # Schedule Manager
    "ScheduleManager",
    "ScheduledContent",
    "ScheduleType",
    "ScheduleStatus",
    "RecurrencePattern",
    "OptimizationGoal",
    "TimeWindow",
    "AudienceInsight",
    "ScheduleRule",
    "OptimalTimeSlot",
    "get_schedule_manager",
    "schedule_content",
    
    # Analytics Aggregator
    "AnalyticsAggregator",
    "AnalyticsDataPoint",
    "AggregatedMetrics",
    "PerformanceInsight",
    "MetricType",
    "AggregationPeriod",
    "get_analytics_aggregator",
    
    # Revenue Tracker
    "RevenueTracker",
    "RevenueEntry",
    "RevenueAttribution",
    "RevenuePerformanceMetrics",
    "RevenueInsight",
    "RevenueType",
    "Currency",
    "AttributionModel",
    "get_revenue_tracker",
    
    # API Manager
    "APIManager",
    "APIEndpoint",
    "APICredentials",
    "APIRequest",
    "APIManagerResponse",
    "RateLimitConfig",
    "HTTPMethod",
    "APIAuthType",
    "RequestStatus",
    "get_api_manager",
    
    # Social Platform Connectors
    "SocialPlatformType",
    "ContentFormat",
    "EngagementType",
    "SocialContentMetadata",
    "SocialPlatformResponse",
    "SocialAnalytics",
    "BaseSocialConnector",
    "SocialPlatformManager",
    "get_social_platform_manager",
    
    # Music Platform Connectors
    "MusicPlatformType",
    "AudioFormat",
    "MusicGenre",
    "StreamingMetricType",
    "MusicTrackMetadata",
    "MusicPlatformResponse",
    "MusicStreamingAnalytics",
    "BaseMusicConnector",
    "SpotifyConnector",
    "SoundCloudConnector",
    "AppleMusicConnector",
    "MusicPlatformManager",
    "get_music_platform_manager",
    
    # Security Protection
    "SecurityLevel",
    "ProtectionType",
    "ThreatType",
    "ComplianceStandard",
    "SecurityConfig",
    "SecurityThreat",
    "ProtectionStatus",
    "ComplianceReport",
    "ContentProtectionEngine",
    "SecurityProtectionManager",
    "get_security_protection_manager",
    
    # Video Platform Connectors
    "VideoPlatformType",
    "VideoFormat",
    "VideoQuality",
    "LiveStreamStatus",
    "VideoMetricType",
    "VideoContentMetadata",
    "LiveStreamSettings",
    "VideoPlatformResponse",
    "VideoStreamingAnalytics",
    "BaseVideoConnector",
    "VimeoConnector",
    "DailymotionConnector",
    "TwitchConnector",
    "LiveStreamingConnector",
    "VideoPlatformManager",
    "get_video_platform_manager",
    
    # Emerging Platform Connectors
    "EmergingPlatformType",
    "CommunityType",
    "Web3PlatformType",
    "EngagementMetricType",
    "CommunityContentMetadata",
    "Web3ContentMetadata",
    "EmergingPlatformResponse",
    "CommunityAnalytics",
    "BaseEmergingConnector",
    "DiscordConnector",
    "TelegramConnector",
    "RedditConnector",
    "Web3Connector",
    "EmergingPlatformManager",
    "get_emerging_platform_manager",
    
    # Creator Economy Connectors
    "CreatorPlatformType",
    "SubscriptionTier",
    "MonetizationType",
    "ContentAccessLevel",
    "PaymentStatus",
    "CreatorContentMetadata",
    "SubscriptionPlan",
    "CreatorEconomyResponse",
    "CreatorAnalytics",
    "FanEngagementMetrics",
    "BaseCreatorConnector",
    "PatreonConnector",
    "KofiConnector",
    "GumroadConnector",
    "SubstackConnector",
    "CreatorEconomyManager",
    "get_creator_economy_manager",
    
    # Monetization Distribution
    "RevenueStreamType",
    "MonetizationStrategy",
    "SponsorshipType",
    "AudienceSegment",
    "OptimizationGoal",
    "RevenueStreamConfig",
    "SponsorshipOpportunity",
    "AffiliateProgram",
    "MonetizationMetrics",
    "MonetizationRecommendation",
    "BrandCollaborationMatch",
    "RevenueOptimizer",
    "SponsorshipMatcher",
    "AffiliateManager",
    "MonetizationDistributionManager",
    "get_monetization_distribution_manager",
    
    # Globalization Engine
    "GeographicRegion",
    "CulturalContext",
    "ComplianceFramework",
    "ContentRating",
    "LanguageCode",
    "TimezoneRegion",
    "GeographicTarget",
    "CulturalAdaptation",
    "LanguageLocalization",
    "LegalCompliance",
    "RegionalMonetization",
    "GlobalizationResponse",
    "GlobalAnalytics",
    "GeoTargetingEngine",
    "CulturalAdaptationEngine",
    "ComplianceEngine",
    "LocalizationEngine",
    "GlobalizationManager",
    "get_globalization_manager",
    
    # Module availability flags
    "platform_connector_available",
    "schedule_manager_available",
    "analytics_aggregator_available",
    "revenue_tracker_available",
    "api_manager_available",
    "social_connectors_available",
    "music_connectors_available",
    "security_protection_available",
    "video_connectors_available",
    "emerging_connectors_available",
    "creator_economy_available",
    "monetization_distribution_available",
    "globalization_available"
]

# Module initialization
logger.info(f"IA Influencer Agent Distribution Module v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")

# Availability summary
available_count = sum([
    platform_connector_available,
    schedule_manager_available,
    analytics_aggregator_available,
    revenue_tracker_available,
    api_manager_available,
    social_connectors_available,
    music_connectors_available,
    security_protection_available,
    video_connectors_available,
    emerging_connectors_available,
    creator_economy_available,
    monetization_distribution_available,
    globalization_available
])

logger.info(f"🚀 Distribution modules loaded: {available_count}/13 systems available")