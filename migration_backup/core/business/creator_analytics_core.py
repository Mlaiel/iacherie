"""Ainflue Core Creator Analytics - Advanced Analytics & Business Intelligence
=======================================================================

Enterprise creator analytics providing performance metrics, audience insights,
revenue optimization, trend analysis, and predictive analytics
for the Ainflue platform business core.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
from datetime import datetime, timedelta
import json
import statistics

logger = logging.getLogger(__name__)

class AnalyticsMetric(str, Enum):
    """Analytics metrics"""
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    FOLLOWERS = "followers"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"
    CHURN_RATE = "churn_rate"
    LIFETIME_VALUE = "lifetime_value"

class TimeRange(str, Enum):
    """Time range for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"

class AggregationType(str, Enum):
    """Data aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"

@dataclass
class DataPoint:
    """Single analytics data point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorMetrics:
    """Creator performance metrics"""
    creator_id: str
    total_views: int = 0
    total_engagement: int = 0
    total_revenue: float = 0.0
    follower_count: int = 0
    content_count: int = 0
    avg_engagement_rate: float = 0.0
    trending_score: float = 0.0
    growth_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentMetrics:
    """Content performance metrics"""
    content_id: str
    creator_id: str
    content_type: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    completion_rate: float = 0.0
    revenue_generated: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AudienceInsight:
    """Audience insight data"""
    creator_id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    engagement_times: List[int] = field(default_factory=list)  # Hours of day
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    device_usage: Dict[str, float] = field(default_factory=dict)
    platform_preferences: Dict[str, float] = field(default_factory=dict)

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric: str
    trend_direction: str  # "up", "down", "stable"
    growth_rate: float
    confidence_score: float
    time_range: str
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    creator_id: str
    report_type: str
    time_range: TimeRange
    metrics: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    charts_data: Dict[str, List[DataPoint]] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)

class CreatorAnalyticsCore:
    """Enterprise creator analytics core management system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize creator analytics core"""
        self.level = level
        self.start_time = time.time()
        
        # Data storage
        self.creator_metrics: Dict[str, CreatorMetrics] = {}
        self.content_metrics: Dict[str, ContentMetrics] = {}
        self.audience_insights: Dict[str, AudienceInsight] = {}
        self.time_series_data: Dict[str, List[DataPoint]] = {}
        self.analytics_reports: Dict[str, AnalyticsReport] = {}
        
        # Real-time tracking
        self.real_time_events: List[Dict[str, Any]] = []
        self.event_processors: Dict[str, callable] = {}
        
        # Analytics cache
        self.metrics_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Background processing
        self.processing_queue: List[Dict[str, Any]] = []
        
        # Health monitoring
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._analytics_processor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("📊 Creator Analytics Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize analytics core"""
        try:
            logger.info("🚀 Initializing creator analytics core")
            
            # Setup event processors
            self._setup_event_processors()
            
            # Initialize sample data (for demonstration)
            await self._create_sample_data()
            
            logger.info("✅ Creator analytics core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics initialization failed: {str(e)}")
            return False
    
    def _setup_event_processors(self):
        """Setup event processors for real-time analytics"""
        self.event_processors = {
            "content_view": self._process_view_event,
            "content_like": self._process_engagement_event,
            "content_share": self._process_engagement_event,
            "content_comment": self._process_engagement_event,
            "creator_follow": self._process_follow_event,
            "revenue_generated": self._process_revenue_event
        }
    
    async def _create_sample_data(self):
        """Create sample analytics data"""
        sample_creators = ["creator_001", "creator_002", "creator_003"]
        
        for creator_id in sample_creators:
            # Create creator metrics
            self.creator_metrics[creator_id] = CreatorMetrics(
                creator_id=creator_id,
                total_views=int(10000 + hash(creator_id) % 50000),
                total_engagement=int(500 + hash(creator_id) % 2000),
                total_revenue=float(100 + hash(creator_id) % 5000),
                follower_count=int(1000 + hash(creator_id) % 10000),
                content_count=int(10 + hash(creator_id) % 50)
            )
            
            # Create audience insights
            self.audience_insights[creator_id] = AudienceInsight(
                creator_id=creator_id,
                demographics={
                    "age_18_24": 25.0,
                    "age_25_34": 35.0,
                    "age_35_44": 25.0,
                    "age_45_plus": 15.0,
                    "male": 45.0,
                    "female": 55.0
                },
                interests=["technology", "gaming", "music", "fitness"],
                geographic_distribution={
                    "US": 40.0, "EU": 30.0, "Asia": 20.0, "Other": 10.0
                }
            )
            
            # Create time series data
            await self._generate_time_series(creator_id)
    
    async def _generate_time_series(self, creator_id: str):
        """Generate sample time series data"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)
        
        for metric in [AnalyticsMetric.VIEWS, AnalyticsMetric.ENGAGEMENT, AnalyticsMetric.REVENUE]:
            key = f"{creator_id}_{metric.value}"
            self.time_series_data[key] = []
            
            current_time = start_time
            while current_time <= end_time:
                # Generate sample data with some trend and randomness
                base_value = 100 + hash(f"{creator_id}_{metric}") % 500
                trend_factor = (current_time - start_time).days * 0.1
                random_factor = (hash(str(current_time)) % 100) / 100.0
                
                value = base_value + trend_factor + random_factor * 50
                
                self.time_series_data[key].append(DataPoint(
                    timestamp=current_time,
                    value=value
                ))
                
                current_time += timedelta(hours=1)
    
    async def start(self) -> bool:
        """Start analytics core"""
        try:
            if not hasattr(self, '_initialized'):
                await self.initialize()
                self._initialized = True
            
            # Start background processors
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            self._analytics_processor_task = asyncio.create_task(self._analytics_processor_loop())
            
            logger.info("🚀 Creator analytics core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics core start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop analytics core"""
        try:
            logger.info("🛑 Stopping creator analytics core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            for task in [self._health_monitor_task, self._analytics_processor_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("✅ Creator analytics core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics core stop failed: {str(e)}")
            return False
    
    async def track_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Track real-time event"""
        try:
            event = {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.utcnow(),
                "event_id": str(uuid.uuid4())
            }
            
            self.real_time_events.append(event)
            
            # Process event immediately for real-time updates
            processor = self.event_processors.get(event_type)
            if processor:
                await processor(data)
            
            # Add to processing queue for batch processing
            self.processing_queue.append(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Event tracking failed: {str(e)}")
            return False
    
    async def _process_view_event(self, data: Dict[str, Any]):
        """Process content view event"""
        creator_id = data.get("creator_id")
        content_id = data.get("content_id")
        
        if creator_id:
            # Update creator metrics
            if creator_id in self.creator_metrics:
                self.creator_metrics[creator_id].total_views += 1
            
            # Update content metrics
            if content_id:
                if content_id not in self.content_metrics:
                    self.content_metrics[content_id] = ContentMetrics(
                        content_id=content_id,
                        creator_id=creator_id,
                        content_type=data.get("content_type", "unknown")
                    )
                self.content_metrics[content_id].views += 1
    
    async def _process_engagement_event(self, data: Dict[str, Any]):
        """Process engagement event (like, share, comment)"""
        creator_id = data.get("creator_id")
        content_id = data.get("content_id")
        engagement_type = data.get("engagement_type")
        
        if creator_id and creator_id in self.creator_metrics:
            self.creator_metrics[creator_id].total_engagement += 1
        
        if content_id and content_id in self.content_metrics:
            if engagement_type == "like":
                self.content_metrics[content_id].likes += 1
            elif engagement_type == "share":
                self.content_metrics[content_id].shares += 1
            elif engagement_type == "comment":
                self.content_metrics[content_id].comments += 1
    
    async def _process_follow_event(self, data: Dict[str, Any]):
        """Process follow event"""
        creator_id = data.get("creator_id")
        
        if creator_id and creator_id in self.creator_metrics:
            self.creator_metrics[creator_id].follower_count += 1
    
    async def _process_revenue_event(self, data: Dict[str, Any]):
        """Process revenue event"""
        creator_id = data.get("creator_id")
        amount = data.get("amount", 0.0)
        
        if creator_id and creator_id in self.creator_metrics:
            self.creator_metrics[creator_id].total_revenue += amount
    
    async def get_creator_analytics(self, creator_id: str, time_range: TimeRange = TimeRange.MONTH) -> Optional[Dict[str, Any]]:
        """Get comprehensive creator analytics"""
        try:
            # Check cache first
            cache_key = f"{creator_id}_{time_range.value}"
            cached = self.metrics_cache.get(cache_key)
            if cached and time.time() - cached["timestamp"] < self.cache_ttl:
                return cached["data"]
            
            if creator_id not in self.creator_metrics:
                return None
            
            metrics = self.creator_metrics[creator_id]
            
            # Get time series data
            time_series = await self._get_time_series_data(creator_id, time_range)
            
            # Calculate derived metrics
            engagement_rate = 0.0
            if metrics.follower_count > 0:
                engagement_rate = (metrics.total_engagement / metrics.follower_count) * 100
            
            # Get audience insights
            audience = self.audience_insights.get(creator_id, AudienceInsight(creator_id=creator_id))
            
            # Trend analysis
            trends = await self._analyze_trends(creator_id, time_range)
            
            analytics_data = {
                "creator_id": creator_id,
                "overview": {
                    "total_views": metrics.total_views,
                    "total_engagement": metrics.total_engagement,
                    "total_revenue": metrics.total_revenue,
                    "follower_count": metrics.follower_count,
                    "content_count": metrics.content_count,
                    "engagement_rate": engagement_rate,
                    "avg_revenue_per_content": metrics.total_revenue / max(metrics.content_count, 1)
                },
                "time_series": time_series,
                "audience_insights": {
                    "demographics": audience.demographics,
                    "interests": audience.interests,
                    "geographic_distribution": audience.geographic_distribution,
                    "device_usage": audience.device_usage
                },
                "trends": trends,
                "top_content": await self._get_top_content(creator_id, limit=10),
                "performance_scores": await self._calculate_performance_scores(creator_id)
            }
            
            # Cache the result
            self.metrics_cache[cache_key] = {
                "data": analytics_data,
                "timestamp": time.time()
            }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to get creator analytics: {str(e)}")
            return None
    
    async def _get_time_series_data(self, creator_id: str, time_range: TimeRange) -> Dict[str, List[Dict[str, Any]]]:
        """Get time series data for creator"""
        result = {}
        
        for metric in [AnalyticsMetric.VIEWS, AnalyticsMetric.ENGAGEMENT, AnalyticsMetric.REVENUE]:
            key = f"{creator_id}_{metric.value}"
            if key in self.time_series_data:
                # Filter by time range
                end_time = datetime.utcnow()
                if time_range == TimeRange.DAY:
                    start_time = end_time - timedelta(days=1)
                elif time_range == TimeRange.WEEK:
                    start_time = end_time - timedelta(weeks=1)
                elif time_range == TimeRange.MONTH:
                    start_time = end_time - timedelta(days=30)
                elif time_range == TimeRange.QUARTER:
                    start_time = end_time - timedelta(days=90)
                elif time_range == TimeRange.YEAR:
                    start_time = end_time - timedelta(days=365)
                else:
                    start_time = datetime.min
                
                filtered_data = [
                    {
                        "timestamp": dp.timestamp.isoformat(),
                        "value": dp.value,
                        "metadata": dp.metadata
                    }
                    for dp in self.time_series_data[key]
                    if dp.timestamp >= start_time
                ]
                
                result[metric.value] = filtered_data
        
        return result
    
    async def _analyze_trends(self, creator_id: str, time_range: TimeRange) -> List[TrendAnalysis]:
        """Analyze trends for creator metrics"""
        trends = []
        
        for metric in [AnalyticsMetric.VIEWS, AnalyticsMetric.ENGAGEMENT, AnalyticsMetric.REVENUE]:
            key = f"{creator_id}_{metric.value}"
            if key in self.time_series_data:
                data_points = self.time_series_data[key]
                if len(data_points) >= 2:
                    # Simple trend analysis
                    recent_values = [dp.value for dp in data_points[-10:]]
                    older_values = [dp.value for dp in data_points[-20:-10]] if len(data_points) >= 20 else []
                    
                    if older_values:
                        recent_avg = statistics.mean(recent_values)
                        older_avg = statistics.mean(older_values)
                        growth_rate = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
                        
                        if growth_rate > 5:
                            trend_direction = "up"
                        elif growth_rate < -5:
                            trend_direction = "down"
                        else:
                            trend_direction = "stable"
                        
                        trends.append(TrendAnalysis(
                            metric=metric.value,
                            trend_direction=trend_direction,
                            growth_rate=growth_rate,
                            confidence_score=0.8,  # Simplified confidence
                            time_range=time_range.value
                        ))
        
        return trends
    
    async def _get_top_content(self, creator_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content for creator"""
        creator_content = [
            content for content in self.content_metrics.values()
            if content.creator_id == creator_id
        ]
        
        # Sort by engagement rate
        creator_content.sort(
            key=lambda c: c.engagement_rate if c.views > 0 else 0,
            reverse=True
        )
        
        return [
            {
                "content_id": content.content_id,
                "content_type": content.content_type,
                "views": content.views,
                "likes": content.likes,
                "shares": content.shares,
                "comments": content.comments,
                "engagement_rate": content.engagement_rate,
                "revenue_generated": content.revenue_generated
            }
            for content in creator_content[:limit]
        ]
    
    async def _calculate_performance_scores(self, creator_id: str) -> Dict[str, float]:
        """Calculate performance scores"""
        metrics = self.creator_metrics.get(creator_id)
        if not metrics:
            return {}
        
        # Simple scoring algorithm (0-100)
        view_score = min(metrics.total_views / 1000, 100)  # 1000 views = 100 points
        engagement_score = min(metrics.total_engagement / 100, 100)  # 100 engagements = 100 points
        revenue_score = min(metrics.total_revenue / 1000, 100)  # $1000 = 100 points
        follower_score = min(metrics.follower_count / 10000, 100)  # 10k followers = 100 points
        
        overall_score = (view_score + engagement_score + revenue_score + follower_score) / 4
        
        return {
            "overall_score": round(overall_score, 2),
            "view_score": round(view_score, 2),
            "engagement_score": round(engagement_score, 2),
            "revenue_score": round(revenue_score, 2),
            "follower_score": round(follower_score, 2)
        }
    
    async def generate_analytics_report(self, creator_id: str, report_type: str = "comprehensive") -> Optional[str]:
        """Generate comprehensive analytics report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Get analytics data
            analytics_data = await self.get_creator_analytics(creator_id, TimeRange.MONTH)
            if not analytics_data:
                return None
            
            # Generate insights and recommendations
            insights = await self._generate_insights(analytics_data)
            recommendations = await self._generate_recommendations(analytics_data)
            
            report = AnalyticsReport(
                report_id=report_id,
                creator_id=creator_id,
                report_type=report_type,
                time_range=TimeRange.MONTH,
                metrics=analytics_data["overview"],
                insights=insights,
                recommendations=recommendations,
                charts_data=analytics_data["time_series"]
            )
            
            self.analytics_reports[report_id] = report
            
            logger.info(f"📈 Generated analytics report '{report_id}' for creator '{creator_id}'")
            return report_id
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return None
    
    async def _generate_insights(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights"""
        insights = []
        overview = analytics_data["overview"]
        
        # Engagement insights
        if overview["engagement_rate"] > 5.0:
            insights.append("Your engagement rate is above average, indicating strong audience connection.")
        elif overview["engagement_rate"] < 2.0:
            insights.append("Your engagement rate is below average. Consider more interactive content.")
        
        # Revenue insights
        revenue_per_content = overview["avg_revenue_per_content"]
        if revenue_per_content > 50:
            insights.append("Your content monetization is performing well.")
        elif revenue_per_content < 10:
            insights.append("Consider exploring additional monetization strategies.")
        
        # Growth insights
        trends = analytics_data.get("trends", [])
        for trend in trends:
            if trend.trend_direction == "up" and trend.growth_rate > 10:
                insights.append(f"Your {trend.metric} is trending upward with {trend.growth_rate:.1f}% growth.")
            elif trend.trend_direction == "down" and trend.growth_rate < -10:
                insights.append(f"Your {trend.metric} is declining. Consider content strategy adjustments.")
        
        return insights
    
    async def _generate_recommendations(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        overview = analytics_data["overview"]
        audience = analytics_data["audience_insights"]
        
        # Content recommendations
        if overview["engagement_rate"] < 3.0:
            recommendations.append("Try posting more interactive content like polls, Q&As, or live streams.")
        
        # Timing recommendations
        if audience.get("device_usage", {}).get("mobile", 0) > 70:
            recommendations.append("Optimize your content for mobile viewing as most of your audience uses mobile devices.")
        
        # Monetization recommendations
        if overview["total_revenue"] < overview["follower_count"] * 0.1:
            recommendations.append("Explore additional revenue streams like merchandise, courses, or premium content.")
        
        # Audience recommendations
        top_location = max(audience["geographic_distribution"].items(), key=lambda x: x[1])[0]
        recommendations.append(f"Consider creating content tailored to your largest audience in {top_location}.")
        
        return recommendations
    
    async def _analytics_processor_loop(self):
        """Background analytics processor"""
        while not self._shutdown_event.is_set():
            try:
                # Process queued events
                if self.processing_queue:
                    events_to_process = self.processing_queue[:100]  # Process in batches
                    self.processing_queue = self.processing_queue[100:]
                    
                    for event in events_to_process:
                        await self._process_batch_event(event)
                
                # Update calculated metrics
                await self._update_calculated_metrics()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(60)  # Process every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics processor error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _process_batch_event(self, event: Dict[str, Any]):
        """Process event in batch mode"""
        # Add to time series data
        event_type = event["event_type"]
        data = event["data"]
        timestamp = event["timestamp"]
        
        creator_id = data.get("creator_id")
        if creator_id:
            for metric in [AnalyticsMetric.VIEWS, AnalyticsMetric.ENGAGEMENT]:
                if event_type.startswith(metric.value) or event_type in ["content_view", "content_like", "content_share"]:
                    key = f"{creator_id}_{metric.value}"
                    if key not in self.time_series_data:
                        self.time_series_data[key] = []
                    
                    self.time_series_data[key].append(DataPoint(
                        timestamp=timestamp,
                        value=1.0,  # Increment by 1
                        metadata={"event_type": event_type}
                    ))
    
    async def _update_calculated_metrics(self):
        """Update calculated metrics like engagement rates"""
        for content_id, content in self.content_metrics.items():
            total_engagements = content.likes + content.shares + content.comments
            if content.views > 0:
                content.engagement_rate = (total_engagements / content.views) * 100
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory bloat"""
        cutoff_time = datetime.utcnow() - timedelta(days=90)  # Keep 90 days
        
        # Clean up real-time events
        self.real_time_events = [
            event for event in self.real_time_events
            if event["timestamp"] > cutoff_time
        ]
        
        # Clean up time series data
        for key in self.time_series_data:
            self.time_series_data[key] = [
                dp for dp in self.time_series_data[key]
                if dp.timestamp > cutoff_time
            ]
    
    async def health_check(self) -> bool:
        """Perform analytics health check"""
        try:
            # Check if we have any data
            if not self.creator_metrics and not self.content_metrics:
                return False
            
            # Check if background processing is working
            if len(self.processing_queue) > 10000:  # Too many unprocessed events
                logger.warning("Analytics processing queue is too large")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Analytics health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics health monitor error: {str(e)}")
                await asyncio.sleep(600)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_creators": len(self.creator_metrics),
            "total_content": len(self.content_metrics),
            "total_events_processed": len(self.real_time_events),
            "processing_queue_size": len(self.processing_queue),
            "cache_size": len(self.metrics_cache),
            "reports_generated": len(self.analytics_reports),
            "time_series_keys": len(self.time_series_data),
            "uptime_seconds": int(time.time() - self.start_time)
        }

# Module exports
__all__ = [
    "CreatorAnalyticsCore", "CreatorMetrics", "ContentMetrics", "AudienceInsight",
    "TrendAnalysis", "AnalyticsReport", "AnalyticsMetric", "TimeRange", "AggregationType"
]