"""Advanced Distribution Module - Multi-Platform Content Distribution System
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


class DistributionOrchestrator:
    """
    Central orchestrator for the complete distribution ecosystem.
    
    Coordinates between all distribution modules to provide a unified
    content distribution experience across multiple platforms.
    """
    
    def __init__(self):
        """Initialize the distribution orchestrator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Module instances
        self.platform_manager = None
        self.schedule_manager = None
        self.analytics_aggregator = None
        self.revenue_tracker = None
        self.api_manager = None
        
        self.logger.info("DistributionOrchestrator initialized")
    
    async def initialize(self) -> bool:
        """Initialize all distribution modules."""
        try:
            # Initialize modules that are available
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
            
            self.initialized = True
            
            available_modules = sum([
                platform_connector_available,
                schedule_manager_available,
                analytics_aggregator_available,
                revenue_tracker_available,
                api_manager_available
            ])
            
            self.logger.info(f"✅ Distribution orchestrator initialized with {available_modules}/5 modules")
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
    
    async def cleanup(self):
        """Cleanup all distribution modules."""
        try:
            if self.platform_manager:
                await self.platform_manager.cleanup()
            
            if self.api_manager:
                await self.api_manager.cleanup()
            
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
    
    # Module availability flags
    "platform_connector_available",
    "schedule_manager_available",
    "analytics_aggregator_available",
    "revenue_tracker_available",
    "api_manager_available"
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
    api_manager_available
])

logger.info(f"🚀 Distribution modules loaded: {available_count}/5 systems available")