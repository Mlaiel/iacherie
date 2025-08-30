"""
Mobile Analytics Engine
Mobile usage tracking, performance monitoring, and business insights

Author: Fahed Mlaiel <mlaiel@live.de>
Business Logic: Data-driven insights for mobile creator engagement and platform optimization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
import uuid
import statistics

# Internal imports
try:
    from core.config import get_settings
    from core.logging import get_logger
    from core.database import get_database_session
except ImportError:
    # Fallback for standalone operation
    def get_logger(name: str):
        return logging.getLogger(name)
    
    def get_settings():
        return {"analytics_retention_days": 90}
    
    def get_database_session():
        return None


@dataclass
class MobileEvent:
    """Mobile analytics event."""
    event_id: str
    user_id: str
    device_id: str
    session_id: str
    event_type: str  # app_open, content_upload, collaboration_request, etc.
    event_category: str  # engagement, performance, business, security
    timestamp: datetime
    properties: Dict[str, Any] = field(default_factory=dict)
    device_info: Optional[Dict[str, Any]] = None
    location_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class PerformanceMetric:
    """Mobile performance metric."""
    metric_id: str
    device_id: str
    session_id: str
    metric_type: str  # load_time, api_response_time, battery_usage, memory_usage
    value: float
    unit: str  # ms, mb, percentage
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class UserSession:
    """Mobile user session tracking."""
    session_id: str
    user_id: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    page_views: int = 0
    actions_performed: int = 0
    is_active: bool = True
    session_quality: Optional[str] = None  # high, medium, low
    
    def end_session(self):
        """End the session and calculate duration."""
        self.end_time = datetime.utcnow()
        self.is_active = False
        if self.start_time:
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
    
    def calculate_quality(self) -> str:
        """Calculate session quality based on engagement."""
        if self.duration_seconds is None:
            return "unknown"
        
        if self.duration_seconds > 300 and self.actions_performed > 5:  # 5+ minutes, 5+ actions
            return "high"
        elif self.duration_seconds > 60 and self.actions_performed > 2:  # 1+ minute, 2+ actions
            return "medium"
        else:
            return "low"


@dataclass
class BusinessMetric:
    """Business performance metric."""
    metric_id: str
    user_id: str
    device_id: str
    metric_type: str  # revenue, uploads, collaborations, engagement
    value: float
    currency: Optional[str] = None
    timestamp: datetime = None
    period: str = "daily"  # daily, weekly, monthly
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class MobileAnalytics:
    """Professional mobile analytics tracking system."""
    
    def __init__(self):
        self.logger = get_logger("mobile.analytics")
        self.settings = get_settings()
        self.events: List[MobileEvent] = []
        self.sessions: Dict[str, UserSession] = {}
        self.performance_metrics: List[PerformanceMetric] = []
        self.business_metrics: List[BusinessMetric] = []
    
    async def track_event(
        self,
        user_id: str,
        device_id: str,
        session_id: str,
        event_type: str,
        event_category: str = "engagement",
        properties: Optional[Dict[str, Any]] = None,
        device_info: Optional[Dict[str, Any]] = None,
        location_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track mobile analytics event."""
        
        event_id = str(uuid.uuid4())
        
        event = MobileEvent(
            event_id=event_id,
            user_id=user_id,
            device_id=device_id,
            session_id=session_id,
            event_type=event_type,
            event_category=event_category,
            timestamp=datetime.utcnow(),
            properties=properties or {},
            device_info=device_info,
            location_info=location_info
        )
        
        self.events.append(event)
        
        # Update session activity
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.actions_performed += 1
            
            if event_type == "page_view":
                session.page_views += 1
        
        self.logger.info(
            f"Event tracked: {event_type} for user {user_id} on device {device_id}"
        )
        
        return event_id
    
    async def start_session(
        self,
        user_id: str,
        device_id: str,
        session_id: Optional[str] = None
    ) -> UserSession:
        """Start new user session."""
        
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            start_time=datetime.utcnow()
        )
        
        self.sessions[session_id] = session
        
        # Track session start event
        await self.track_event(
            user_id, device_id, session_id, "session_start", "engagement"
        )
        
        self.logger.info(f"Session started: {session_id} for user {user_id}")
        
        return session
    
    async def end_session(self, session_id: str) -> Optional[UserSession]:
        """End user session."""
        
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        session.end_session()
        session.session_quality = session.calculate_quality()
        
        # Track session end event
        await self.track_event(
            session.user_id,
            session.device_id,
            session_id,
            "session_end",
            "engagement",
            {
                "duration_seconds": session.duration_seconds,
                "page_views": session.page_views,
                "actions_performed": session.actions_performed,
                "session_quality": session.session_quality
            }
        )
        
        self.logger.info(
            f"Session ended: {session_id} - {session.duration_seconds}s, "
            f"{session.actions_performed} actions, quality: {session.session_quality}"
        )
        
        return session
    
    async def track_business_metric(
        self,
        user_id: str,
        device_id: str,
        metric_type: str,
        value: float,
        currency: Optional[str] = None,
        period: str = "daily"
    ) -> str:
        """Track business performance metric."""
        
        metric_id = str(uuid.uuid4())
        
        metric = BusinessMetric(
            metric_id=metric_id,
            user_id=user_id,
            device_id=device_id,
            metric_type=metric_type,
            value=value,
            currency=currency,
            period=period
        )
        
        self.business_metrics.append(metric)
        
        self.logger.info(
            f"Business metric tracked: {metric_type} = {value} for user {user_id}"
        )
        
        return metric_id
    
    async def get_user_analytics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for user."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter user events
        user_events = [
            event for event in self.events
            if event.user_id == user_id and event.timestamp >= cutoff_date
        ]
        
        # Filter user sessions
        user_sessions = [
            session for session in self.sessions.values()
            if session.user_id == user_id and session.start_time >= cutoff_date
        ]
        
        # Filter business metrics
        user_business_metrics = [
            metric for metric in self.business_metrics
            if metric.user_id == user_id and metric.timestamp >= cutoff_date
        ]
        
        # Calculate analytics
        analytics = {
            "user_id": user_id,
            "period_days": days,
            "engagement": self._calculate_engagement_metrics(user_events, user_sessions),
            "content": self._calculate_content_metrics(user_events),
            "collaboration": self._calculate_collaboration_metrics(user_events),
            "revenue": self._calculate_revenue_metrics(user_business_metrics),
            "device_usage": self._calculate_device_usage(user_events),
            "session_summary": self._calculate_session_summary(user_sessions)
        }
        
        return analytics
    
    async def get_platform_insights(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get platform-wide analytics insights."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter recent data
        recent_events = [
            event for event in self.events
            if event.timestamp >= cutoff_date
        ]
        
        recent_sessions = [
            session for session in self.sessions.values()
            if session.start_time >= cutoff_date
        ]
        
        insights = {
            "platform_overview": {
                "total_events": len(recent_events),
                "total_sessions": len(recent_sessions),
                "active_users": len(set(event.user_id for event in recent_events)),
                "active_devices": len(set(event.device_id for event in recent_events))
            },
            "top_events": self._get_top_events(recent_events),
            "platform_distribution": self._get_platform_distribution(recent_events),
            "engagement_trends": self._get_engagement_trends(recent_sessions),
            "performance_summary": self._get_performance_summary()
        }
        
        return insights
    
    def _calculate_engagement_metrics(
        self,
        events: List[MobileEvent],
        sessions: List[UserSession]
    ) -> Dict[str, Any]:
        """Calculate user engagement metrics."""
        
        if not events:
            return {"total_events": 0, "average_session_duration": 0}
        
        # Calculate session durations
        completed_sessions = [s for s in sessions if s.duration_seconds is not None]
        avg_session_duration = (
            statistics.mean([s.duration_seconds for s in completed_sessions])
            if completed_sessions else 0
        )
        
        # Event frequency
        event_types = defaultdict(int)
        for event in events:
            event_types[event.event_type] += 1
        
        return {
            "total_events": len(events),
            "total_sessions": len(sessions),
            "average_session_duration": avg_session_duration,
            "events_per_session": len(events) / len(sessions) if sessions else 0,
            "top_event_types": dict(sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def _calculate_content_metrics(self, events: List[MobileEvent]) -> Dict[str, Any]:
        """Calculate content-related metrics."""
        
        content_events = [e for e in events if "content" in e.event_type]
        
        upload_events = [e for e in events if e.event_type == "content_upload"]
        view_events = [e for e in events if e.event_type == "content_view"]
        share_events = [e for e in events if e.event_type == "content_share"]
        
        return {
            "total_content_events": len(content_events),
            "uploads": len(upload_events),
            "views": len(view_events),
            "shares": len(share_events),
            "engagement_rate": len(view_events) / len(upload_events) if upload_events else 0
        }
    
    def _calculate_collaboration_metrics(self, events: List[MobileEvent]) -> Dict[str, Any]:
        """Calculate collaboration metrics."""
        
        collab_events = [e for e in events if "collaboration" in e.event_type]
        
        request_events = [e for e in events if e.event_type == "collaboration_request"]
        accept_events = [e for e in events if e.event_type == "collaboration_accept"]
        
        return {
            "total_collaboration_events": len(collab_events),
            "requests_sent": len(request_events),
            "requests_accepted": len(accept_events),
            "acceptance_rate": len(accept_events) / len(request_events) if request_events else 0
        }
    
    def _calculate_revenue_metrics(self, business_metrics: List[BusinessMetric]) -> Dict[str, Any]:
        """Calculate revenue metrics."""
        
        revenue_metrics = [m for m in business_metrics if m.metric_type == "revenue"]
        
        total_revenue = sum(m.value for m in revenue_metrics)
        avg_revenue = statistics.mean([m.value for m in revenue_metrics]) if revenue_metrics else 0
        
        return {
            "total_revenue": total_revenue,
            "average_revenue": avg_revenue,
            "revenue_transactions": len(revenue_metrics)
        }
    
    def _calculate_device_usage(self, events: List[MobileEvent]) -> Dict[str, Any]:
        """Calculate device usage patterns."""
        
        devices = defaultdict(int)
        platforms = defaultdict(int)
        
        for event in events:
            devices[event.device_id] += 1
            if event.device_info:
                platform = event.device_info.get("platform", "unknown")
                platforms[platform] += 1
        
        return {
            "unique_devices": len(devices),
            "platform_distribution": dict(platforms),
            "most_active_device": max(devices.items(), key=lambda x: x[1])[0] if devices else None
        }
    
    def _calculate_session_summary(self, sessions: List[UserSession]) -> Dict[str, Any]:
        """Calculate session summary statistics."""
        
        completed_sessions = [s for s in sessions if s.duration_seconds is not None]
        
        if not completed_sessions:
            return {"total_sessions": 0}
        
        durations = [s.duration_seconds for s in completed_sessions]
        qualities = [s.session_quality for s in completed_sessions if s.session_quality]
        
        quality_counts = defaultdict(int)
        for quality in qualities:
            quality_counts[quality] += 1
        
        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed_sessions),
            "average_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "session_qualities": dict(quality_counts)
        }
    
    def _get_top_events(self, events: List[MobileEvent]) -> Dict[str, int]:
        """Get top event types."""
        
        event_counts = defaultdict(int)
        for event in events:
            event_counts[event.event_type] += 1
        
        return dict(sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _get_platform_distribution(self, events: List[MobileEvent]) -> Dict[str, int]:
        """Get platform distribution."""
        
        platforms = defaultdict(int)
        for event in events:
            if event.device_info:
                platform = event.device_info.get("platform", "unknown")
                platforms[platform] += 1
        
        return dict(platforms)
    
    def _get_engagement_trends(self, sessions: List[UserSession]) -> Dict[str, Any]:
        """Get engagement trends."""
        
        if not sessions:
            return {}
        
        # Group sessions by day
        daily_sessions = defaultdict(list)
        for session in sessions:
            day = session.start_time.date()
            daily_sessions[day].append(session)
        
        # Calculate daily averages
        daily_metrics = {}
        for day, day_sessions in daily_sessions.items():
            completed = [s for s in day_sessions if s.duration_seconds is not None]
            avg_duration = statistics.mean([s.duration_seconds for s in completed]) if completed else 0
            
            daily_metrics[day.isoformat()] = {
                "sessions": len(day_sessions),
                "average_duration": avg_duration
            }
        
        return daily_metrics
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        
        if not self.performance_metrics:
            return {}
        
        # Group by metric type
        by_type = defaultdict(list)
        for metric in self.performance_metrics:
            by_type[metric.metric_type].append(metric.value)
        
        summary = {}
        for metric_type, values in by_type.items():
            summary[metric_type] = {
                "average": statistics.mean(values),
                "median": statistics.median(values),
                "count": len(values)
            }
        
        return summary


class PerformanceTracker:
    """Mobile performance monitoring and tracking."""
    
    def __init__(self, analytics: MobileAnalytics):
        self.logger = get_logger("mobile.performance_tracker")
        self.analytics = analytics
    
    async def track_performance_metric(
        self,
        device_id: str,
        session_id: str,
        metric_type: str,
        value: float,
        unit: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track performance metric."""
        
        metric_id = str(uuid.uuid4())
        
        metric = PerformanceMetric(
            metric_id=metric_id,
            device_id=device_id,
            session_id=session_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            context=context or {}
        )
        
        self.analytics.performance_metrics.append(metric)
        
        self.logger.info(
            f"Performance metric tracked: {metric_type} = {value} {unit} for device {device_id}"
        )
        
        return metric_id
    
    async def get_performance_report(
        self,
        device_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance report."""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter metrics
        metrics = [
            m for m in self.analytics.performance_metrics
            if m.timestamp >= cutoff_time and (device_id is None or m.device_id == device_id)
        ]
        
        if not metrics:
            return {"message": "No performance data available"}
        
        # Group by metric type
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric.metric_type].append(metric.value)
        
        report = {
            "period_hours": hours,
            "device_id": device_id,
            "total_metrics": len(metrics),
            "performance_summary": {}
        }
        
        for metric_type, values in by_type.items():
            report["performance_summary"][metric_type] = {
                "count": len(values),
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "median": statistics.median(values)
            }
        
        return report


class UsageMonitor:
    """Mobile usage pattern monitoring."""
    
    def __init__(self, analytics: MobileAnalytics):
        self.logger = get_logger("mobile.usage_monitor")
        self.analytics = analytics
    
    async def generate_usage_insights(
        self,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Generate comprehensive usage insights."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter events
        events = [
            e for e in self.analytics.events
            if e.timestamp >= cutoff_date and (user_id is None or e.user_id == user_id)
        ]
        
        if not events:
            return {"message": "No usage data available"}
        
        insights = {
            "period_days": days,
            "user_id": user_id,
            "usage_patterns": self._analyze_usage_patterns(events),
            "feature_adoption": self._analyze_feature_adoption(events),
            "user_journey": self._analyze_user_journey(events),
            "recommendations": self._generate_recommendations(events)
        }
        
        return insights
    
    def _analyze_usage_patterns(self, events: List[MobileEvent]) -> Dict[str, Any]:
        """Analyze usage patterns."""
        
        # Time-based patterns
        hourly_usage = defaultdict(int)
        daily_usage = defaultdict(int)
        
        for event in events:
            hourly_usage[event.timestamp.hour] += 1
            daily_usage[event.timestamp.weekday()] += 1
        
        # Most active hours and days
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1])[0] if hourly_usage else None
        peak_day = max(daily_usage.items(), key=lambda x: x[1])[0] if daily_usage else None
        
        return {
            "peak_hour": peak_hour,
            "peak_day": peak_day,
            "hourly_distribution": dict(hourly_usage),
            "daily_distribution": dict(daily_usage)
        }
    
    def _analyze_feature_adoption(self, events: List[MobileEvent]) -> Dict[str, Any]:
        """Analyze feature adoption patterns."""
        
        feature_usage = defaultdict(int)
        unique_users_per_feature = defaultdict(set)
        
        for event in events:
            feature_usage[event.event_type] += 1
            unique_users_per_feature[event.event_type].add(event.user_id)
        
        # Convert sets to counts
        feature_user_counts = {
            feature: len(users) for feature, users in unique_users_per_feature.items()
        }
        
        return {
            "feature_usage_counts": dict(feature_usage),
            "feature_user_adoption": feature_user_counts,
            "most_popular_feature": max(feature_usage.items(), key=lambda x: x[1])[0] if feature_usage else None
        }
    
    def _analyze_user_journey(self, events: List[MobileEvent]) -> Dict[str, Any]:
        """Analyze user journey patterns."""
        
        # Group events by user and session
        user_journeys = defaultdict(lambda: defaultdict(list))
        
        for event in events:
            user_journeys[event.user_id][event.session_id].append(event)
        
        # Analyze common paths
        common_sequences = defaultdict(int)
        
        for user_id, sessions in user_journeys.items():
            for session_id, session_events in sessions.items():
                # Sort events by timestamp
                session_events.sort(key=lambda e: e.timestamp)
                
                # Extract sequence of event types
                sequence = [e.event_type for e in session_events]
                if len(sequence) > 1:
                    sequence_str = " -> ".join(sequence[:5])  # Limit to first 5 events
                    common_sequences[sequence_str] += 1
        
        # Get top sequences
        top_sequences = sorted(common_sequences.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_journeys": sum(len(sessions) for sessions in user_journeys.values()),
            "unique_users": len(user_journeys),
            "common_sequences": dict(top_sequences)
        }
    
    def _generate_recommendations(self, events: List[MobileEvent]) -> List[str]:
        """Generate usage-based recommendations."""
        
        recommendations = []
        
        # Analyze engagement patterns
        upload_events = [e for e in events if e.event_type == "content_upload"]
        view_events = [e for e in events if e.event_type == "content_view"]
        
        if upload_events and view_events:
            engagement_ratio = len(view_events) / len(upload_events)
            if engagement_ratio < 0.5:
                recommendations.append("Consider improving content discovery to increase engagement")
        
        # Analyze collaboration patterns
        collab_events = [e for e in events if "collaboration" in e.event_type]
        if len(collab_events) < len(upload_events) * 0.1:
            recommendations.append("Promote collaboration features to increase creator connections")
        
        # Analyze session patterns
        session_starts = [e for e in events if e.event_type == "session_start"]
        if len(session_starts) > 0:
            avg_events_per_session = len(events) / len(session_starts)
            if avg_events_per_session < 3:
                recommendations.append("Improve user onboarding to increase session engagement")
        
        return recommendations


# Service factory functions
def create_mobile_analytics() -> MobileAnalytics:
    """Create mobile analytics instance."""
    return MobileAnalytics()


def create_performance_tracker(analytics: MobileAnalytics = None) -> PerformanceTracker:
    """Create performance tracker instance."""
    if analytics is None:
        analytics = create_mobile_analytics()
    return PerformanceTracker(analytics)


def create_usage_monitor(analytics: MobileAnalytics = None) -> UsageMonitor:
    """Create usage monitor instance."""
    if analytics is None:
        analytics = create_mobile_analytics()
    return UsageMonitor(analytics)


# Main execution for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_mobile_analytics():
        """Test mobile analytics functionality."""
        
        # Create analytics system
        analytics = create_mobile_analytics()
        performance_tracker = create_performance_tracker(analytics)
        usage_monitor = create_usage_monitor(analytics)
        
        # Start a session
        session = await analytics.start_session("user123", "device456")
        print(f"Session started: {session.session_id}")
        
        # Track some events
        await analytics.track_event(
            "user123", "device456", session.session_id, "content_upload", "business",
            {"content_type": "audio", "file_size": 1024000}
        )
        
        await analytics.track_event(
            "user123", "device456", session.session_id, "content_view", "engagement"
        )
        
        await analytics.track_event(
            "user123", "device456", session.session_id, "collaboration_request", "business"
        )
        
        # Track performance metrics
        await performance_tracker.track_performance_metric(
            "device456", session.session_id, "api_response_time", 250.5, "ms"
        )
        
        # Track business metrics
        await analytics.track_business_metric(
            "user123", "device456", "revenue", 15.99, "USD"
        )
        
        # End session
        await analytics.end_session(session.session_id)
        
        # Get analytics
        user_analytics = await analytics.get_user_analytics("user123")
        print(f"User analytics: {json.dumps(user_analytics, indent=2, default=str)}")
        
        # Get performance report
        perf_report = await performance_tracker.get_performance_report("device456")
        print(f"Performance report: {json.dumps(perf_report, indent=2, default=str)}")
        
        # Get usage insights
        usage_insights = await usage_monitor.generate_usage_insights("user123")
        print(f"Usage insights: {json.dumps(usage_insights, indent=2, default=str)}")
    
    # Run tests
    asyncio.run(test_mobile_analytics())