"""Tracking Module - User Behavior and Performance Tracking

Analytics tracking services for user behavior, content performance,
and engagement metrics collection and analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from .user_behavior import UserBehaviorTracker
from .content_performance import ContentPerformanceTracker
from .engagement_metrics import EngagementMetrics

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of analytics events."""
    PAGE_VIEW = "page_view"
    CONTENT_VIEW = "content_view"
    CONTENT_UPLOAD = "content_upload"
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    PURCHASE = "purchase"
    DOWNLOAD = "download"
    SHARE = "share"
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    SEARCH = "search"


@dataclass
class AnalyticsEvent:
    """Analytics event data structure."""
    id: str
    event_type: EventType
    user_id: Optional[str]
    session_id: Optional[str]
    timestamp: datetime
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardMetrics:
    """Dashboard metrics data structure."""
    total_users: int
    active_users_24h: int
    total_content: int
    content_views_24h: int
    revenue_24h: float
    top_content: List[Dict[str, Any]]
    user_growth: List[Dict[str, Any]]
    engagement_rate: float
    platform_breakdown: Dict[str, int]
    updated_at: datetime = field(default_factory=datetime.now)


class AnalyticsTracker:
    """
    Main analytics tracker that coordinates all tracking modules
    and provides unified analytics functionality.
    """
    
    def __init__(self):
        """Initialize analytics tracker."""
        self.logger = logging.getLogger(f"{__name__}.AnalyticsTracker")
        
        # Initialize tracking modules
        self.user_behavior = UserBehaviorTracker()
        self.content_performance = ContentPerformanceTracker()
        self.engagement_metrics = EngagementMetrics()
        
        # Event storage (in production, would be a database)
        self.events: List[AnalyticsEvent] = []
        self.dashboard_cache: Optional[DashboardMetrics] = None
        self.cache_expiry: Optional[datetime] = None
        
        self.logger.info("Analytics tracker initialized")
    
    async def track_event(
        self,
        event_type: EventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track an analytics event.
        
        Args:
            event_type: Type of event
            user_id: User identifier
            session_id: Session identifier
            properties: Event properties
            metadata: Additional metadata
            
        Returns:
            True if event was tracked successfully
        """
        try:
            event = AnalyticsEvent(
                id=str(uuid.uuid4()),
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(),
                properties=properties or {},
                metadata=metadata or {}
            )
            
            self.events.append(event)
            
            # Route event to appropriate tracking modules
            if event_type in [EventType.PAGE_VIEW, EventType.USER_LOGIN, EventType.SEARCH]:
                await self.user_behavior.track_behavior(event)
            
            if event_type in [EventType.CONTENT_VIEW, EventType.CONTENT_UPLOAD, EventType.DOWNLOAD]:
                await self.content_performance.track_content_event(event)
            
            if event_type in [EventType.LIKE, EventType.COMMENT, EventType.SHARE, EventType.FOLLOW]:
                await self.engagement_metrics.track_engagement(event)
            
            # Invalidate dashboard cache
            self.dashboard_cache = None
            
            self.logger.debug(f"Event tracked: {event_type} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track event: {e}")
            return False
    
    async def get_dashboard_data(
        self,
        timeframe: str = "24h",
        force_refresh: bool = False
    ) -> DashboardMetrics:
        """Get dashboard analytics data.
        
        Args:
            timeframe: Time period for data (24h, 7d, 30d)
            force_refresh: Force refresh of cached data
            
        Returns:
            Dashboard metrics
        """
        try:
            # Check cache validity
            if (not force_refresh and 
                self.dashboard_cache and 
                self.cache_expiry and 
                datetime.now() < self.cache_expiry):
                return self.dashboard_cache
            
            # Calculate timeframe
            hours = {"24h": 24, "7d": 168, "30d": 720}.get(timeframe, 24)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter events by timeframe
            recent_events = [
                event for event in self.events
                if event.timestamp >= cutoff_time
            ]
            
            # Calculate metrics
            total_users = len(set(event.user_id for event in self.events if event.user_id))
            active_users = len(set(event.user_id for event in recent_events if event.user_id))
            
            total_content = len([
                event for event in self.events
                if event.event_type == EventType.CONTENT_UPLOAD
            ])
            
            content_views = len([
                event for event in recent_events
                if event.event_type == EventType.CONTENT_VIEW
            ])
            
            # Calculate revenue (simplified)
            revenue_events = [
                event for event in recent_events
                if event.event_type == EventType.PURCHASE
            ]
            revenue_24h = sum(
                float(event.properties.get('amount', 0))
                for event in revenue_events
            )
            
            # Get top content
            content_views_by_id = {}
            for event in recent_events:
                if event.event_type == EventType.CONTENT_VIEW:
                    content_id = event.properties.get('content_id')
                    if content_id:
                        content_views_by_id[content_id] = content_views_by_id.get(content_id, 0) + 1
            
            top_content = [
                {
                    "content_id": content_id,
                    "views": views,
                    "title": f"Content {content_id[:8]}"  # Simplified
                }
                for content_id, views in sorted(
                    content_views_by_id.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ]
            
            # Calculate user growth (daily for past week)
            user_growth = []
            for i in range(7):
                day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                day_registrations = len([
                    event for event in self.events
                    if (event.event_type == EventType.USER_REGISTRATION and
                        day_start <= event.timestamp < day_end)
                ])
                
                user_growth.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "new_users": day_registrations
                })
            
            # Calculate engagement rate
            total_interactions = len([
                event for event in recent_events
                if event.event_type in [EventType.LIKE, EventType.COMMENT, EventType.SHARE]
            ])
            engagement_rate = (total_interactions / max(content_views, 1)) * 100
            
            # Platform breakdown
            platform_breakdown = {}
            for event in recent_events:
                platform = event.properties.get('platform', 'unknown')
                platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1
            
            # Create dashboard metrics
            dashboard_metrics = DashboardMetrics(
                total_users=total_users,
                active_users_24h=active_users,
                total_content=total_content,
                content_views_24h=content_views,
                revenue_24h=revenue_24h,
                top_content=top_content,
                user_growth=user_growth,
                engagement_rate=round(engagement_rate, 2),
                platform_breakdown=platform_breakdown
            )
            
            # Cache the results for 5 minutes
            self.dashboard_cache = dashboard_metrics
            self.cache_expiry = datetime.now() + timedelta(minutes=5)
            
            return dashboard_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return DashboardMetrics(0, 0, 0, 0, 0.0, [], [], 0.0, {})
    
    async def generate_report(
        self,
        report_type: str = "summary",
        timeframe: str = "7d",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate analytics report.
        
        Args:
            report_type: Type of report (summary, detailed, user_specific)
            timeframe: Time period for report
            user_id: Specific user ID for user reports
            
        Returns:
            Generated report data
        """
        try:
            # Calculate timeframe
            hours = {"24h": 24, "7d": 168, "30d": 720}.get(timeframe, 168)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter events
            events = self.events
            if user_id:
                events = [event for event in events if event.user_id == user_id]
            
            recent_events = [
                event for event in events
                if event.timestamp >= cutoff_time
            ]
            
            if report_type == "summary":
                return await self._generate_summary_report(recent_events, timeframe)
            elif report_type == "detailed":
                return await self._generate_detailed_report(recent_events, timeframe)
            elif report_type == "user_specific":
                return await self._generate_user_report(recent_events, user_id, timeframe)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return {"error": str(e)}
    
    async def _generate_summary_report(
        self,
        events: List[AnalyticsEvent],
        timeframe: str
    ) -> Dict[str, Any]:
        """Generate summary report."""
        event_counts = {}
        for event in events:
            event_counts[event.event_type.value] = event_counts.get(event.event_type.value, 0) + 1
        
        unique_users = len(set(event.user_id for event in events if event.user_id))
        
        return {
            "report_type": "summary",
            "timeframe": timeframe,
            "generated_at": datetime.now().isoformat(),
            "total_events": len(events),
            "unique_users": unique_users,
            "event_breakdown": event_counts,
            "top_events": sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    async def _generate_detailed_report(
        self,
        events: List[AnalyticsEvent],
        timeframe: str
    ) -> Dict[str, Any]:
        """Generate detailed report."""
        dashboard_data = await self.get_dashboard_data(timeframe)
        summary = await self._generate_summary_report(events, timeframe)
        
        # Additional detailed metrics
        hourly_breakdown = {}
        for event in events:
            hour = event.timestamp.strftime("%Y-%m-%d %H:00")
            hourly_breakdown[hour] = hourly_breakdown.get(hour, 0) + 1
        
        return {
            **summary,
            "report_type": "detailed",
            "dashboard_metrics": dashboard_data,
            "hourly_breakdown": hourly_breakdown,
            "user_behavior_insights": await self.user_behavior.get_insights(),
            "content_performance_insights": await self.content_performance.get_insights(),
            "engagement_insights": await self.engagement_metrics.get_insights()
        }
    
    async def _generate_user_report(
        self,
        events: List[AnalyticsEvent],
        user_id: Optional[str],
        timeframe: str
    ) -> Dict[str, Any]:
        """Generate user-specific report."""
        if not user_id:
            return {"error": "User ID required for user-specific report"}
        
        user_events = [event for event in events if event.user_id == user_id]
        
        # User activity timeline
        activity_timeline = [
            {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "properties": event.properties
            }
            for event in sorted(user_events, key=lambda x: x.timestamp, reverse=True)[:50]
        ]
        
        # User behavior summary
        behavior_summary = {}
        for event in user_events:
            behavior_summary[event.event_type.value] = behavior_summary.get(event.event_type.value, 0) + 1
        
        return {
            "report_type": "user_specific",
            "user_id": user_id,
            "timeframe": timeframe,
            "generated_at": datetime.now().isoformat(),
            "total_events": len(user_events),
            "behavior_summary": behavior_summary,
            "activity_timeline": activity_timeline,
            "most_active_day": self._get_most_active_day(user_events),
            "engagement_score": self._calculate_user_engagement_score(user_events)
        }
    
    def _get_most_active_day(self, events: List[AnalyticsEvent]) -> Optional[str]:
        """Get user's most active day."""
        if not events:
            return None
        
        daily_counts = {}
        for event in events:
            day = event.timestamp.strftime("%Y-%m-%d")
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        if not daily_counts:
            return None
        
        return max(daily_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_user_engagement_score(self, events: List[AnalyticsEvent]) -> float:
        """Calculate user engagement score."""
        if not events:
            return 0.0
        
        # Simple engagement scoring
        engagement_events = [
            EventType.LIKE, EventType.COMMENT, EventType.SHARE,
            EventType.CONTENT_UPLOAD, EventType.FOLLOW
        ]
        
        engagement_count = len([
            event for event in events
            if event.event_type in engagement_events
        ])
        
        total_events = len(events)
        return round((engagement_count / total_events) * 100, 2) if total_events > 0 else 0.0
    
    async def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary for specific user."""
        user_events = [event for event in self.events if event.user_id == user_id]
        
        return {
            "user_id": user_id,
            "total_events": len(user_events),
            "first_seen": min(event.timestamp for event in user_events).isoformat() if user_events else None,
            "last_seen": max(event.timestamp for event in user_events).isoformat() if user_events else None,
            "engagement_score": self._calculate_user_engagement_score(user_events)
        }


__all__ = [
    'AnalyticsTracker',
    'UserBehaviorTracker',
    'ContentPerformanceTracker',
    'EngagementMetrics',
    'EventType',
    'AnalyticsEvent',
    'DashboardMetrics'
]