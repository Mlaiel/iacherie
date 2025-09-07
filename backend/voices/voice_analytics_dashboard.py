"""Voice Analytics Dashboard - Enterprise Voice Performance Analytics System

Comprehensive voice content analytics and business intelligence dashboard for creators.
Provides real-time performance tracking, audience insights, and revenue analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from collections import defaultdict
import statistics

class AnalyticsMetric(Enum):
    """Voice analytics metrics"""
    LISTENS = "listens"
    DOWNLOADS = "downloads"
    SHARES = "shares"
    LIKES = "likes"
    COMMENTS = "comments"
    SUBSCRIBERS = "subscribers"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    COMPLETION_RATE = "completion_rate"
    RETENTION_RATE = "retention_rate"
    DISCOVERY_RATE = "discovery_rate"
    VIRAL_COEFFICIENT = "viral_coefficient"

class TimeRange(Enum):
    """Analytics time range options"""
    REAL_TIME = "real_time"
    LAST_HOUR = "last_hour"
    LAST_24_HOURS = "last_24_hours"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_YEAR = "last_year"
    ALL_TIME = "all_time"
    CUSTOM = "custom"

class PlatformType(Enum):
    """Voice platform types for analytics"""
    PODCAST = "podcast"
    MUSIC_STREAMING = "music_streaming"
    AUDIOBOOK = "audiobook"
    VOICE_SOCIAL = "voice_social"
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    RADIO = "radio"
    ALL_PLATFORMS = "all_platforms"

class AudienceSegment(Enum):
    """Audience segmentation categories"""
    AGE_GROUP = "age_group"
    GENDER = "gender"
    LOCATION = "location"
    INTERESTS = "interests"
    LISTENING_BEHAVIOR = "listening_behavior"
    DEVICE_TYPE = "device_type"
    SUBSCRIPTION_STATUS = "subscription_status"
    ENGAGEMENT_LEVEL = "engagement_level"

@dataclass
class AnalyticsDataPoint:
    """Single analytics data point"""
    metric: AnalyticsMetric
    value: float
    timestamp: datetime
    platform: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AudienceInsight:
    """Audience analytics insight"""
    segment: AudienceSegment
    segment_value: str
    total_listeners: int
    percentage: float
    engagement_score: float
    average_session_duration: float
    top_content: List[str]
    growth_rate: float
    retention_rate: float

@dataclass
class ContentPerformance:
    """Content performance analytics"""
    content_id: str
    title: str
    content_type: str
    platform: str
    total_listens: int
    total_downloads: int
    engagement_rate: float
    completion_rate: float
    share_rate: float
    revenue_generated: float
    audience_reach: int
    trending_score: float
    performance_trend: List[float]
    top_regions: List[Tuple[str, int]]
    peak_listening_hours: List[int]

@dataclass
class RevenueAnalytics:
    """Revenue performance analytics"""
    total_revenue: float
    revenue_by_platform: Dict[str, float]
    revenue_by_content: Dict[str, float]
    revenue_trend: List[Tuple[datetime, float]]
    average_rpm: float  # Revenue per mille (thousand listens)
    subscription_revenue: float
    advertising_revenue: float
    licensing_revenue: float
    growth_rate: float
    projected_revenue: float

@dataclass
class EngagementAnalytics:
    """Engagement performance analytics"""
    total_engagements: int
    engagement_rate: float
    engagement_by_type: Dict[str, int]
    engagement_trend: List[Tuple[datetime, float]]
    peak_engagement_times: List[Tuple[int, float]]  # (hour, engagement_rate)
    audience_sentiment: Dict[str, float]
    viral_content: List[str]
    collaboration_engagement: Dict[str, float]

@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: str
    title: str
    metric: AnalyticsMetric
    time_range: TimeRange
    platform_filter: Optional[PlatformType] = None
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (1, 1)
    refresh_interval: int = 300  # seconds
    chart_type: str = "line"
    show_comparison: bool = False
    comparison_period: Optional[TimeRange] = None

class VoiceAnalyticsDashboard:
    """Enterprise Voice Analytics Dashboard
    
    Comprehensive analytics and business intelligence system for voice content creators.
    Provides real-time insights, performance tracking, and audience analytics.
    """
    
    def __init__(self, creator_id: str):
        """Initialize voice analytics dashboard"""
        self.creator_id = creator_id
        self.analytics_data: List[AnalyticsDataPoint] = []
        self.widgets: Dict[str, DashboardWidget] = {}
        self.cached_analytics: Dict[str, Any] = {}
        self.real_time_listeners: int = 0
        self.alerts_config: Dict[str, Any] = {}
        
        self._initialize_default_widgets()
        self._initialize_alert_thresholds()
    
    def _initialize_default_widgets(self):
        """Initialize default dashboard widgets"""
        
        # Real-time listeners widget
        self.widgets["real_time_listeners"] = DashboardWidget(
            widget_id="real_time_listeners",
            widget_type="metric",
            title="Real-time Listeners",
            metric=AnalyticsMetric.LISTENS,
            time_range=TimeRange.REAL_TIME,
            position=(0, 0),
            size=(1, 1),
            refresh_interval=30,
            chart_type="counter"
        )
        
        # Total listens widget
        self.widgets["total_listens_7d"] = DashboardWidget(
            widget_id="total_listens_7d",
            widget_type="metric",
            title="Total Listens (7 Days)",
            metric=AnalyticsMetric.LISTENS,
            time_range=TimeRange.LAST_7_DAYS,
            position=(1, 0),
            size=(1, 1),
            refresh_interval=300,
            chart_type="line",
            show_comparison=True,
            comparison_period=TimeRange.LAST_7_DAYS
        )
        
        # Revenue widget
        self.widgets["revenue_30d"] = DashboardWidget(
            widget_id="revenue_30d",
            widget_type="metric",
            title="Revenue (30 Days)",
            metric=AnalyticsMetric.REVENUE,
            time_range=TimeRange.LAST_30_DAYS,
            position=(2, 0),
            size=(1, 1),
            refresh_interval=300,
            chart_type="bar"
        )
        
        # Engagement rate widget
        self.widgets["engagement_rate"] = DashboardWidget(
            widget_id="engagement_rate",
            widget_type="metric",
            title="Engagement Rate",
            metric=AnalyticsMetric.ENGAGEMENT_RATE,
            time_range=TimeRange.LAST_7_DAYS,
            position=(0, 1),
            size=(2, 1),
            refresh_interval=300,
            chart_type="area"
        )
        
        # Platform performance widget
        self.widgets["platform_performance"] = DashboardWidget(
            widget_id="platform_performance",
            widget_type="breakdown",
            title="Platform Performance",
            metric=AnalyticsMetric.LISTENS,
            time_range=TimeRange.LAST_30_DAYS,
            position=(0, 2),
            size=(3, 1),
            refresh_interval=600,
            chart_type="pie"
        )
    
    def _initialize_alert_thresholds(self):
        """Initialize alert thresholds"""
        self.alerts_config = {
            "low_engagement": {"threshold": 0.05, "enabled": True},
            "revenue_drop": {"threshold": 0.20, "enabled": True},
            "viral_content": {"threshold": 1000, "enabled": True},
            "technical_issues": {"threshold": 0.95, "enabled": True}
        }
    
    async def add_analytics_data(self, data_points: List[AnalyticsDataPoint]):
        """Add new analytics data points"""
        self.analytics_data.extend(data_points)
        
        # Update cached analytics
        await self._update_cached_analytics()
        
        # Check for alerts
        await self._check_alert_conditions(data_points)
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)
        
        # Get recent data points
        recent_data = [
            dp for dp in self.analytics_data 
            if dp.timestamp >= last_hour
        ]
        
        # Calculate real-time metrics
        current_listeners = self.real_time_listeners
        
        listens_last_hour = len([
            dp for dp in recent_data 
            if dp.metric == AnalyticsMetric.LISTENS
        ])
        
        engagement_events = len([
            dp for dp in recent_data 
            if dp.metric in [AnalyticsMetric.LIKES, AnalyticsMetric.SHARES, AnalyticsMetric.COMMENTS]
        ])
        
        return {
            "current_listeners": current_listeners,
            "listens_last_hour": listens_last_hour,
            "engagement_events_last_hour": engagement_events,
            "trending_content": await self._get_trending_content(),
            "live_revenue": await self._calculate_live_revenue(),
            "audience_locations": await self._get_live_audience_locations(),
            "last_updated": current_time.isoformat()
        }
    
    async def get_content_performance(
        self, 
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
        platform: Optional[PlatformType] = None
    ) -> List[ContentPerformance]:
        """Get content performance analytics"""
        
        start_time, end_time = self._get_time_range_bounds(time_range)
        
        # Filter data by time range and platform
        filtered_data = [
            dp for dp in self.analytics_data
            if start_time <= dp.timestamp <= end_time
        ]
        
        if platform and platform != PlatformType.ALL_PLATFORMS:
            filtered_data = [
                dp for dp in filtered_data
                if dp.platform == platform.value
            ]
        
        # Group by content
        content_metrics = defaultdict(lambda: {
            "listens": 0,
            "downloads": 0,
            "shares": 0,
            "likes": 0,
            "comments": 0,
            "revenue": 0.0,
            "platforms": set()
        })
        
        for dp in filtered_data:
            if dp.content_id:
                content_metrics[dp.content_id][dp.metric.value] += dp.value
                if dp.platform:
                    content_metrics[dp.content_id]["platforms"].add(dp.platform)
        
        # Calculate performance metrics
        performance_list = []
        
        for content_id, metrics in content_metrics.items():
            if metrics["listens"] > 0:  # Only include content with listens
                
                engagement_rate = (
                    (metrics["likes"] + metrics["shares"] + metrics["comments"]) /
                    metrics["listens"]
                ) if metrics["listens"] > 0 else 0
                
                performance = ContentPerformance(
                    content_id=content_id,
                    title=self._get_content_title(content_id),
                    content_type=self._get_content_type(content_id),
                    platform=", ".join(metrics["platforms"]),
                    total_listens=int(metrics["listens"]),
                    total_downloads=int(metrics["downloads"]),
                    engagement_rate=engagement_rate,
                    completion_rate=self._calculate_completion_rate(content_id, filtered_data),
                    share_rate=metrics["shares"] / metrics["listens"] if metrics["listens"] > 0 else 0,
                    revenue_generated=metrics["revenue"],
                    audience_reach=int(metrics["listens"] * 1.2),  # Estimated reach
                    trending_score=self._calculate_trending_score(content_id, filtered_data),
                    performance_trend=self._get_performance_trend(content_id, filtered_data),
                    top_regions=self._get_top_regions(content_id, filtered_data),
                    peak_listening_hours=self._get_peak_hours(content_id, filtered_data)
                )
                
                performance_list.append(performance)
        
        # Sort by total listens
        performance_list.sort(key=lambda x: x.total_listens, reverse=True)
        
        return performance_list
    
    async def get_audience_insights(
        self, 
        time_range: TimeRange = TimeRange.LAST_30_DAYS
    ) -> List[AudienceInsight]:
        """Get audience analytics insights"""
        
        start_time, end_time = self._get_time_range_bounds(time_range)
        
        # Filter data by time range
        filtered_data = [
            dp for dp in self.analytics_data
            if start_time <= dp.timestamp <= end_time and dp.metric == AnalyticsMetric.LISTENS
        ]
        
        insights = []
        
        # Analyze by different segments
        for segment in AudienceSegment:
            segment_data = self._analyze_audience_segment(segment, filtered_data)
            insights.extend(segment_data)
        
        return insights
    
    async def get_revenue_analytics(
        self, 
        time_range: TimeRange = TimeRange.LAST_30_DAYS
    ) -> RevenueAnalytics:
        """Get revenue analytics"""
        
        start_time, end_time = self._get_time_range_bounds(time_range)
        
        # Filter revenue data
        revenue_data = [
            dp for dp in self.analytics_data
            if (start_time <= dp.timestamp <= end_time and 
                dp.metric == AnalyticsMetric.REVENUE)
        ]
        
        total_revenue = sum(dp.value for dp in revenue_data)
        
        # Revenue by platform
        platform_revenue = defaultdict(float)
        for dp in revenue_data:
            if dp.platform:
                platform_revenue[dp.platform] += dp.value
        
        # Revenue by content
        content_revenue = defaultdict(float)
        for dp in revenue_data:
            if dp.content_id:
                content_revenue[dp.content_id] += dp.value
        
        # Revenue trend
        revenue_trend = self._calculate_revenue_trend(revenue_data, time_range)
        
        # Calculate RPM (Revenue per Mille)
        total_listens = len([
            dp for dp in self.analytics_data
            if (start_time <= dp.timestamp <= end_time and 
                dp.metric == AnalyticsMetric.LISTENS)
        ])
        
        average_rpm = (total_revenue / total_listens * 1000) if total_listens > 0 else 0
        
        return RevenueAnalytics(
            total_revenue=total_revenue,
            revenue_by_platform=dict(platform_revenue),
            revenue_by_content=dict(content_revenue),
            revenue_trend=revenue_trend,
            average_rpm=average_rpm,
            subscription_revenue=total_revenue * 0.6,  # Estimated
            advertising_revenue=total_revenue * 0.3,
            licensing_revenue=total_revenue * 0.1,
            growth_rate=self._calculate_revenue_growth_rate(revenue_data),
            projected_revenue=self._project_future_revenue(revenue_data)
        )
    
    async def get_engagement_analytics(
        self, 
        time_range: TimeRange = TimeRange.LAST_30_DAYS
    ) -> EngagementAnalytics:
        """Get engagement analytics"""
        
        start_time, end_time = self._get_time_range_bounds(time_range)
        
        # Filter engagement data
        engagement_metrics = [
            AnalyticsMetric.LIKES, 
            AnalyticsMetric.SHARES, 
            AnalyticsMetric.COMMENTS
        ]
        
        engagement_data = [
            dp for dp in self.analytics_data
            if (start_time <= dp.timestamp <= end_time and 
                dp.metric in engagement_metrics)
        ]
        
        listens_data = [
            dp for dp in self.analytics_data
            if (start_time <= dp.timestamp <= end_time and 
                dp.metric == AnalyticsMetric.LISTENS)
        ]
        
        total_engagements = len(engagement_data)
        total_listens = len(listens_data)
        engagement_rate = total_engagements / total_listens if total_listens > 0 else 0
        
        # Engagement by type
        engagement_by_type = defaultdict(int)
        for dp in engagement_data:
            engagement_by_type[dp.metric.value] += int(dp.value)
        
        return EngagementAnalytics(
            total_engagements=total_engagements,
            engagement_rate=engagement_rate,
            engagement_by_type=dict(engagement_by_type),
            engagement_trend=self._calculate_engagement_trend(engagement_data, time_range),
            peak_engagement_times=self._get_peak_engagement_times(engagement_data),
            audience_sentiment=self._analyze_sentiment(engagement_data),
            viral_content=self._identify_viral_content(engagement_data),
            collaboration_engagement=self._analyze_collaboration_engagement(engagement_data)
        )
    
    def create_custom_widget(self, widget_config: DashboardWidget):
        """Create custom dashboard widget"""
        self.widgets[widget_config.widget_id] = widget_config
    
    def remove_widget(self, widget_id: str):
        """Remove dashboard widget"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
    
    async def export_analytics_report(
        self, 
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        
        report = {
            "creator_id": self.creator_id,
            "report_period": time_range.value,
            "generated_at": datetime.now().isoformat(),
            "real_time_metrics": await self.get_real_time_metrics(),
            "content_performance": await self.get_content_performance(time_range),
            "audience_insights": await self.get_audience_insights(time_range),
            "revenue_analytics": await self.get_revenue_analytics(time_range),
            "engagement_analytics": await self.get_engagement_analytics(time_range)
        }
        
        if format_type == "json":
            return report
        else:
            # Could implement CSV, PDF export
            return report
    
    # Helper methods
    
    def _get_time_range_bounds(self, time_range: TimeRange) -> Tuple[datetime, datetime]:
        """Get start and end time for time range"""
        
        end_time = datetime.now()
        
        if time_range == TimeRange.LAST_HOUR:
            start_time = end_time - timedelta(hours=1)
        elif time_range == TimeRange.LAST_24_HOURS:
            start_time = end_time - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7_DAYS:
            start_time = end_time - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            start_time = end_time - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            start_time = end_time - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            start_time = end_time - timedelta(days=365)
        else:  # ALL_TIME
            start_time = datetime.min
        
        return start_time, end_time
    
    def _get_content_title(self, content_id: str) -> str:
        """Get content title by ID"""
        # Would fetch from content database
        return f"Content {content_id[:8]}"
    
    def _get_content_type(self, content_id: str) -> str:
        """Get content type by ID"""
        # Would fetch from content database
        return "podcast"
    
    def _calculate_completion_rate(self, content_id: str, data: List[AnalyticsDataPoint]) -> float:
        """Calculate content completion rate"""
        # Simplified calculation
        return 0.75  # 75% average completion rate
    
    def _calculate_trending_score(self, content_id: str, data: List[AnalyticsDataPoint]) -> float:
        """Calculate trending score for content"""
        # Simplified trending calculation
        content_data = [dp for dp in data if dp.content_id == content_id]
        return len(content_data) * 0.1
    
    def _get_performance_trend(self, content_id: str, data: List[AnalyticsDataPoint]) -> List[float]:
        """Get performance trend for content"""
        # Simplified trend calculation
        return [1.0, 1.2, 1.5, 1.3, 1.7, 1.4, 1.6]
    
    def _get_top_regions(self, content_id: str, data: List[AnalyticsDataPoint]) -> List[Tuple[str, int]]:
        """Get top regions for content"""
        # Simplified region data
        return [("United States", 100), ("United Kingdom", 75), ("Canada", 50)]
    
    def _get_peak_hours(self, content_id: str, data: List[AnalyticsDataPoint]) -> List[int]:
        """Get peak listening hours for content"""
        # Simplified peak hours
        return [8, 12, 18, 20]
    
    def _analyze_audience_segment(
        self, 
        segment: AudienceSegment, 
        data: List[AnalyticsDataPoint]
    ) -> List[AudienceInsight]:
        """Analyze audience segment"""
        # Simplified audience analysis
        if segment == AudienceSegment.AGE_GROUP:
            return [
                AudienceInsight(
                    segment=segment,
                    segment_value="25-34",
                    total_listeners=500,
                    percentage=35.0,
                    engagement_score=0.75,
                    average_session_duration=1800,
                    top_content=["content1", "content2"],
                    growth_rate=0.15,
                    retention_rate=0.80
                )
            ]
        return []
    
    def _calculate_revenue_trend(
        self, 
        revenue_data: List[AnalyticsDataPoint], 
        time_range: TimeRange
    ) -> List[Tuple[datetime, float]]:
        """Calculate revenue trend"""
        # Simplified trend calculation
        return [(datetime.now() - timedelta(days=i), 100.0 + i * 10) for i in range(7)]
    
    def _calculate_revenue_growth_rate(self, revenue_data: List[AnalyticsDataPoint]) -> float:
        """Calculate revenue growth rate"""
        # Simplified growth calculation
        return 0.15  # 15% growth
    
    def _project_future_revenue(self, revenue_data: List[AnalyticsDataPoint]) -> float:
        """Project future revenue"""
        # Simplified projection
        current_total = sum(dp.value for dp in revenue_data)
        return current_total * 1.15  # 15% growth projection
    
    def _calculate_engagement_trend(
        self, 
        engagement_data: List[AnalyticsDataPoint], 
        time_range: TimeRange
    ) -> List[Tuple[datetime, float]]:
        """Calculate engagement trend"""
        # Simplified engagement trend
        return [(datetime.now() - timedelta(days=i), 0.05 + i * 0.01) for i in range(7)]
    
    def _get_peak_engagement_times(self, engagement_data: List[AnalyticsDataPoint]) -> List[Tuple[int, float]]:
        """Get peak engagement times"""
        # Simplified peak times
        return [(8, 0.12), (12, 0.15), (18, 0.18), (20, 0.20)]
    
    def _analyze_sentiment(self, engagement_data: List[AnalyticsDataPoint]) -> Dict[str, float]:
        """Analyze audience sentiment"""
        # Simplified sentiment analysis
        return {"positive": 0.7, "neutral": 0.2, "negative": 0.1}
    
    def _identify_viral_content(self, engagement_data: List[AnalyticsDataPoint]) -> List[str]:
        """Identify viral content"""
        # Simplified viral identification
        return ["content1", "content3"]
    
    def _analyze_collaboration_engagement(self, engagement_data: List[AnalyticsDataPoint]) -> Dict[str, float]:
        """Analyze collaboration engagement"""
        # Simplified collaboration analysis
        return {"solo_content": 0.12, "collaboration_content": 0.18}
    
    async def _get_trending_content(self) -> List[str]:
        """Get currently trending content"""
        # Simplified trending content
        return ["trending_content_1", "trending_content_2"]
    
    async def _calculate_live_revenue(self) -> float:
        """Calculate live revenue"""
        # Simplified live revenue calculation
        return 125.50
    
    async def _get_live_audience_locations(self) -> Dict[str, int]:
        """Get live audience locations"""
        # Simplified location data
        return {"US": 45, "UK": 23, "CA": 12, "AU": 8}
    
    async def _update_cached_analytics(self):
        """Update cached analytics data"""
        # Implementation for caching frequently accessed analytics
        pass
    
    async def _check_alert_conditions(self, data_points: List[AnalyticsDataPoint]):
        """Check for alert conditions"""
        # Implementation for alert checking
        pass


# Export classes for external use
__all__ = [
    'VoiceAnalyticsDashboard',
    'AnalyticsMetric',
    'TimeRange',
    'PlatformType',
    'AudienceSegment',
    'AnalyticsDataPoint',
    'AudienceInsight',
    'ContentPerformance',
    'RevenueAnalytics',
    'EngagementAnalytics',
    'DashboardWidget'
]