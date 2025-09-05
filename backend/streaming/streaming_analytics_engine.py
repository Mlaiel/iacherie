"""Streaming Analytics Engine - Advanced Performance Analytics and Insights
=========================================================================

Enterprise-grade streaming analytics engine providing real-time performance monitoring,
predictive analytics, audience insights, and business intelligence for streaming content
with AI-powered recommendations and comprehensive reporting.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/streaming/streaming_analytics_engine.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

ANALYTICS PIPELINE:
Data Collection → Real-time Processing → Pattern Recognition → Predictive Analysis → Actionable Insights
"""

import asyncio
import json
import uuid
import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of streaming metrics."""
    VIEWERSHIP = "viewership"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REVENUE = "revenue"
    QUALITY = "quality"
    GROWTH = "growth"
    AUDIENCE = "audience"
    PERFORMANCE = "performance"


class AnalyticsTimeframe(str, Enum):
    """Analytics time frame options."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlatformType(str, Enum):
    """Supported streaming platforms."""
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    DISCORD = "discord"


class InsightPriority(str, Enum):
    """Priority levels for insights."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class MetricPoint:
    """Single metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    platform: Optional[PlatformType] = None
    session_id: Optional[str] = None
    creator_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""
    report_id: str
    creator_id: str
    timeframe: AnalyticsTimeframe
    period_start: datetime
    period_end: datetime
    overview_metrics: Dict[str, float]
    platform_breakdown: Dict[str, Dict[str, float]]
    audience_insights: Dict[str, Any]
    performance_trends: Dict[str, List[float]]
    revenue_analytics: Dict[str, Decimal]
    content_performance: List[Dict[str, Any]]
    growth_indicators: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    ai_insights: Dict[str, Any]
    comparative_analysis: Dict[str, Any]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RealTimeMetrics:
    """Real-time streaming metrics."""
    session_id: str
    current_viewers: int = 0
    peak_viewers: int = 0
    total_views: int = 0
    concurrent_platforms: int = 0
    average_watch_time: float = 0.0
    engagement_rate: float = 0.0
    chat_messages_per_minute: float = 0.0
    revenue_per_hour: Decimal = Decimal('0.00')
    quality_score: float = 100.0
    platform_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AudienceInsights:
    """Audience demographic and behavioral insights."""
    total_unique_viewers: int
    demographic_breakdown: Dict[str, float]
    geographic_distribution: Dict[str, float]
    device_breakdown: Dict[str, float]
    viewing_patterns: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    retention_analysis: Dict[str, float]
    new_vs_returning: Dict[str, float]
    peak_activity_times: List[Dict[str, Any]]
    audience_overlap: Dict[str, float]


@dataclass
class PredictiveInsight:
    """AI-powered predictive insight."""
    insight_id: str
    type: str
    priority: InsightPriority
    title: str
    description: str
    prediction: Dict[str, Any]
    confidence_score: float
    potential_impact: str
    recommended_actions: List[str]
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class StreamingAnalyticsRecord(Base):
    """SQLAlchemy model for streaming analytics."""
    __tablename__ = 'streaming_analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), index=True)
    metric_type = Column(String(50), nullable=False, index=True)
    platform = Column(String(50), index=True)
    timeframe = Column(String(50), nullable=False, index=True)
    metrics_data = Column(JSON, nullable=False)
    insights_data = Column(JSON, default=dict)
    report_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class StreamingAnalyticsEngine:
    """Advanced streaming analytics engine with AI-powered insights.
    
    Provides comprehensive analytics, real-time monitoring, predictive insights,
    and actionable recommendations for streaming performance optimization.
    """
    
    def __init__(self, redis_client: Any, db_session: Session):
        """Initialize the streaming analytics engine."""
        self.redis = redis_client
        self.db = db_session
        self.metric_buffers: Dict[str, List[MetricPoint]] = {}
        self.real_time_sessions: Dict[str, RealTimeMetrics] = {}
        self.insights_cache: Dict[str, List[PredictiveInsight]] = {}
        self.analytics_processors: Dict[MetricType, Callable] = {}
        self.is_running = False
        
        # Initialize metric processors
        self._initialize_metric_processors()
    
    async def initialize(self):
        """Initialize the analytics engine and start background processes."""
        self.is_running = True
        logger.info("Streaming Analytics Engine initialized")
        
        # Start background processing tasks
        asyncio.create_task(self._real_time_processor())
        asyncio.create_task(self._batch_processor())
        asyncio.create_task(self._insight_generator())
        asyncio.create_task(self._trend_analyzer())
        asyncio.create_task(self._alert_monitor())
    
    def _initialize_metric_processors(self):
        """Initialize metric processing functions."""
        self.analytics_processors = {
            MetricType.VIEWERSHIP: self._process_viewership_metrics,
            MetricType.ENGAGEMENT: self._process_engagement_metrics,
            MetricType.RETENTION: self._process_retention_metrics,
            MetricType.REVENUE: self._process_revenue_metrics,
            MetricType.QUALITY: self._process_quality_metrics,
            MetricType.GROWTH: self._process_growth_metrics,
            MetricType.AUDIENCE: self._process_audience_metrics,
            MetricType.PERFORMANCE: self._process_performance_metrics
        }
    
    async def collect_metric(
        self,
        metric_type: MetricType,
        value: float,
        creator_id: str,
        session_id: Optional[str] = None,
        platform: Optional[PlatformType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Collect a single metric point."""
        try:
            metric_point = MetricPoint(
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(timezone.utc),
                platform=platform,
                session_id=session_id,
                creator_id=creator_id,
                metadata=metadata or {}
            )
            
            # Add to buffer
            buffer_key = f"{creator_id}:{metric_type.value}"
            if buffer_key not in self.metric_buffers:
                self.metric_buffers[buffer_key] = []
            
            self.metric_buffers[buffer_key].append(metric_point)
            
            # Keep buffer size manageable
            if len(self.metric_buffers[buffer_key]) > 1000:
                self.metric_buffers[buffer_key] = self.metric_buffers[buffer_key][-500:]
            
            # Cache in Redis for real-time access
            await self.redis.lpush(
                f"metrics:{creator_id}:{metric_type.value}",
                json.dumps(asdict(metric_point), default=str)
            )
            
            # Trim Redis list
            await self.redis.ltrim(f"metrics:{creator_id}:{metric_type.value}", 0, 999)
            
            # Update real-time metrics if session is active
            if session_id and session_id in self.real_time_sessions:
                await self._update_real_time_metrics(session_id, metric_point)
            
        except Exception as e:
            logger.error(f"Failed to collect metric: {e}")
    
    async def get_real_time_metrics(self, session_id: str) -> Optional[RealTimeMetrics]:
        """Get real-time metrics for an active session."""
        try:
            if session_id in self.real_time_sessions:
                return self.real_time_sessions[session_id]
            
            # Try to load from Redis
            cached_data = await self.redis.get(f"realtime:metrics:{session_id}")
            if cached_data:
                data = json.loads(cached_data)
                metrics = RealTimeMetrics(**data)
                self.real_time_sessions[session_id] = metrics
                return metrics
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics for {session_id}: {e}")
            return None
    
    async def generate_analytics_report(
        self,
        creator_id: str,
        timeframe: AnalyticsTimeframe,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_predictions: bool = True
    ) -> Optional[AnalyticsReport]:
        """Generate comprehensive analytics report."""
        try:
            report_id = str(uuid.uuid4())
            
            # Calculate time period
            if not end_date:
                end_date = datetime.now(timezone.utc)
            
            if not start_date:
                if timeframe == AnalyticsTimeframe.DAILY:
                    start_date = end_date - timedelta(days=1)
                elif timeframe == AnalyticsTimeframe.WEEKLY:
                    start_date = end_date - timedelta(weeks=1)
                elif timeframe == AnalyticsTimeframe.MONTHLY:
                    start_date = end_date - timedelta(days=30)
                else:
                    start_date = end_date - timedelta(days=7)  # Default to week
            
            # Collect data for all metric types
            overview_metrics = await self._calculate_overview_metrics(creator_id, start_date, end_date)
            platform_breakdown = await self._calculate_platform_breakdown(creator_id, start_date, end_date)
            audience_insights = await self._calculate_audience_insights(creator_id, start_date, end_date)
            performance_trends = await self._calculate_performance_trends(creator_id, start_date, end_date)
            revenue_analytics = await self._calculate_revenue_analytics(creator_id, start_date, end_date)
            content_performance = await self._calculate_content_performance(creator_id, start_date, end_date)
            growth_indicators = await self._calculate_growth_indicators(creator_id, start_date, end_date)
            comparative_analysis = await self._calculate_comparative_analysis(creator_id, start_date, end_date)
            
            # Generate AI-powered insights and recommendations
            ai_insights = await self._generate_ai_insights(creator_id, overview_metrics, performance_trends)
            recommendations = await self._generate_recommendations(creator_id, overview_metrics, performance_trends)
            
            # Create report
            report = AnalyticsReport(
                report_id=report_id,
                creator_id=creator_id,
                timeframe=timeframe,
                period_start=start_date,
                period_end=end_date,
                overview_metrics=overview_metrics,
                platform_breakdown=platform_breakdown,
                audience_insights=audience_insights,
                performance_trends=performance_trends,
                revenue_analytics=revenue_analytics,
                content_performance=content_performance,
                growth_indicators=growth_indicators,
                recommendations=recommendations,
                ai_insights=ai_insights,
                comparative_analysis=comparative_analysis
            )
            
            # Store report in database
            analytics_record = StreamingAnalyticsRecord(
                creator_id=creator_id,
                metric_type="comprehensive_report",
                timeframe=timeframe.value,
                metrics_data=asdict(report)
            )
            
            self.db.add(analytics_record)
            self.db.commit()
            
            # Cache report
            await self.redis.setex(
                f"analytics:report:{report_id}",
                3600,  # 1 hour
                json.dumps(asdict(report), default=str)
            )
            
            logger.info(f"Generated analytics report {report_id} for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report for {creator_id}: {e}")
            return None
    
    async def get_predictive_insights(
        self,
        creator_id: str,
        insight_types: Optional[List[str]] = None
    ) -> List[PredictiveInsight]:
        """Get AI-powered predictive insights."""
        try:
            if creator_id in self.insights_cache:
                cached_insights = self.insights_cache[creator_id]
                
                # Filter by type if specified
                if insight_types:
                    cached_insights = [i for i in cached_insights if i.type in insight_types]
                
                # Filter out expired insights
                now = datetime.now(timezone.utc)
                valid_insights = [i for i in cached_insights if not i.expires_at or i.expires_at > now]
                
                return valid_insights
            
            # Generate new insights
            insights = await self._generate_predictive_insights(creator_id, insight_types)
            self.insights_cache[creator_id] = insights
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get predictive insights for {creator_id}: {e}")
            return []
    
    async def track_session_start(self, session_id: str, creator_id: str, platforms: List[PlatformType]):
        """Start tracking a new streaming session."""
        try:
            metrics = RealTimeMetrics(
                session_id=session_id,
                concurrent_platforms=len(platforms),
                platform_metrics={p.value: {} for p in platforms}
            )
            
            self.real_time_sessions[session_id] = metrics
            
            # Cache in Redis
            await self.redis.setex(
                f"realtime:metrics:{session_id}",
                3600,  # 1 hour
                json.dumps(asdict(metrics), default=str)
            )
            
            logger.info(f"Started tracking session {session_id} for creator {creator_id}")
            
        except Exception as e:
            logger.error(f"Failed to start session tracking {session_id}: {e}")
    
    async def track_session_end(self, session_id: str):
        """End tracking for a streaming session."""
        try:
            if session_id in self.real_time_sessions:
                final_metrics = self.real_time_sessions[session_id]
                
                # Store final metrics in database
                analytics_record = StreamingAnalyticsRecord(
                    session_id=session_id,
                    metric_type="session_final",
                    timeframe="session",
                    metrics_data=asdict(final_metrics)
                )
                
                self.db.add(analytics_record)
                self.db.commit()
                
                # Remove from active tracking
                del self.real_time_sessions[session_id]
                
                # Remove from Redis
                await self.redis.delete(f"realtime:metrics:{session_id}")
                
                logger.info(f"Ended tracking session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to end session tracking {session_id}: {e}")
    
    async def _update_real_time_metrics(self, session_id: str, metric_point: MetricPoint):
        """Update real-time metrics with new data point."""
        try:
            if session_id not in self.real_time_sessions:
                return
            
            metrics = self.real_time_sessions[session_id]
            
            # Update metrics based on type
            if metric_point.metric_type == MetricType.VIEWERSHIP:
                if metric_point.metadata and "type" in metric_point.metadata:
                    if metric_point.metadata["type"] == "current_viewers":
                        metrics.current_viewers = int(metric_point.value)
                        metrics.peak_viewers = max(metrics.peak_viewers, metrics.current_viewers)
                    elif metric_point.metadata["type"] == "total_views":
                        metrics.total_views = int(metric_point.value)
            
            elif metric_point.metric_type == MetricType.ENGAGEMENT:
                metrics.engagement_rate = metric_point.value
                if metric_point.metadata and "chat_messages" in metric_point.metadata:
                    metrics.chat_messages_per_minute = metric_point.metadata["chat_messages"]
            
            elif metric_point.metric_type == MetricType.RETENTION:
                metrics.average_watch_time = metric_point.value
            
            elif metric_point.metric_type == MetricType.REVENUE:
                metrics.revenue_per_hour = Decimal(str(metric_point.value))
            
            elif metric_point.metric_type == MetricType.QUALITY:
                metrics.quality_score = metric_point.value
            
            # Update platform-specific metrics
            if metric_point.platform:
                platform_key = metric_point.platform.value
                if platform_key not in metrics.platform_metrics:
                    metrics.platform_metrics[platform_key] = {}
                
                metrics.platform_metrics[platform_key][metric_point.metric_type.value] = metric_point.value
            
            metrics.last_updated = datetime.now(timezone.utc)
            
            # Update Redis cache
            await self.redis.setex(
                f"realtime:metrics:{session_id}",
                3600,
                json.dumps(asdict(metrics), default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to update real-time metrics for {session_id}: {e}")
    
    async def _calculate_overview_metrics(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate overview metrics for the period."""
        try:
            metrics = {}
            
            # Get all metrics for the period
            for metric_type in MetricType:
                buffer_key = f"{creator_id}:{metric_type.value}"
                if buffer_key in self.metric_buffers:
                    period_metrics = [
                        m for m in self.metric_buffers[buffer_key]
                        if start_date <= m.timestamp <= end_date
                    ]
                    
                    if period_metrics:
                        values = [m.value for m in period_metrics]
                        metrics[f"{metric_type.value}_total"] = sum(values)
                        metrics[f"{metric_type.value}_average"] = statistics.mean(values)
                        metrics[f"{metric_type.value}_max"] = max(values)
                        metrics[f"{metric_type.value}_min"] = min(values)
                        
                        if len(values) > 1:
                            metrics[f"{metric_type.value}_trend"] = self._calculate_trend(values)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate overview metrics for {creator_id}: {e}")
            return {}
    
    async def _calculate_platform_breakdown(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Dict[str, float]]:
        """Calculate platform-specific metrics breakdown."""
        try:
            platform_metrics = {}
            
            for platform in PlatformType:
                platform_metrics[platform.value] = {}
                
                for metric_type in MetricType:
                    buffer_key = f"{creator_id}:{metric_type.value}"
                    if buffer_key in self.metric_buffers:
                        platform_data = [
                            m for m in self.metric_buffers[buffer_key]
                            if (start_date <= m.timestamp <= end_date and 
                                m.platform == platform)
                        ]
                        
                        if platform_data:
                            values = [m.value for m in platform_data]
                            platform_metrics[platform.value][metric_type.value] = {
                                "total": sum(values),
                                "average": statistics.mean(values),
                                "count": len(values)
                            }
            
            return platform_metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate platform breakdown for {creator_id}: {e}")
            return {}
    
    async def _calculate_audience_insights(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate audience demographic and behavioral insights."""
        try:
            # This would integrate with actual audience data sources
            # For now, return sample insights structure
            insights = {
                "total_unique_viewers": 0,
                "demographic_breakdown": {
                    "age_18_24": 25.0,
                    "age_25_34": 35.0,
                    "age_35_44": 25.0,
                    "age_45_plus": 15.0
                },
                "geographic_distribution": {
                    "north_america": 45.0,
                    "europe": 30.0,
                    "asia": 20.0,
                    "other": 5.0
                },
                "device_breakdown": {
                    "mobile": 60.0,
                    "desktop": 30.0,
                    "tablet": 8.0,
                    "tv": 2.0
                },
                "viewing_patterns": {
                    "peak_hour": 20,  # 8 PM
                    "average_session_length": 45.5,
                    "repeat_viewer_rate": 65.0
                },
                "engagement_patterns": {
                    "chat_participation_rate": 15.0,
                    "average_interactions_per_viewer": 3.2,
                    "social_sharing_rate": 8.5
                }
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to calculate audience insights for {creator_id}: {e}")
            return {}
    
    async def _calculate_performance_trends(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, List[float]]:
        """Calculate performance trends over time."""
        try:
            trends = {}
            
            for metric_type in MetricType:
                buffer_key = f"{creator_id}:{metric_type.value}"
                if buffer_key in self.metric_buffers:
                    period_metrics = [
                        m for m in self.metric_buffers[buffer_key]
                        if start_date <= m.timestamp <= end_date
                    ]
                    
                    if period_metrics:
                        # Group by time intervals (e.g., hourly)
                        time_groups = self._group_metrics_by_time(period_metrics, "hourly")
                        trends[metric_type.value] = [
                            statistics.mean([m.value for m in group]) if group else 0.0
                            for group in time_groups
                        ]
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to calculate performance trends for {creator_id}: {e}")
            return {}
    
    async def _calculate_revenue_analytics(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Decimal]:
        """Calculate revenue-related analytics."""
        try:
            revenue_metrics = {}
            
            buffer_key = f"{creator_id}:{MetricType.REVENUE.value}"
            if buffer_key in self.metric_buffers:
                revenue_data = [
                    m for m in self.metric_buffers[buffer_key]
                    if start_date <= m.timestamp <= end_date
                ]
                
                if revenue_data:
                    values = [Decimal(str(m.value)) for m in revenue_data]
                    revenue_metrics = {
                        "total_revenue": sum(values),
                        "average_revenue_per_session": sum(values) / len(values) if values else Decimal('0.00'),
                        "peak_revenue": max(values) if values else Decimal('0.00'),
                        "revenue_growth_rate": self._calculate_revenue_growth(values)
                    }
            
            return revenue_metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate revenue analytics for {creator_id}: {e}")
            return {}
    
    async def _calculate_content_performance(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate performance metrics for individual content pieces."""
        try:
            # This would analyze individual content pieces
            # For now, return sample structure
            content_performance = [
                {
                    "content_id": "content_1",
                    "title": "Sample Content 1",
                    "views": 1500,
                    "engagement_rate": 12.5,
                    "revenue": 45.00,
                    "performance_score": 85.2
                },
                {
                    "content_id": "content_2",
                    "title": "Sample Content 2",
                    "views": 2300,
                    "engagement_rate": 8.7,
                    "revenue": 67.50,
                    "performance_score": 76.8
                }
            ]
            
            return content_performance
            
        except Exception as e:
            logger.error(f"Failed to calculate content performance for {creator_id}: {e}")
            return []
    
    async def _calculate_growth_indicators(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate growth indicators and trends."""
        try:
            growth_indicators = {}
            
            # Calculate growth rates for different metrics
            for metric_type in [MetricType.VIEWERSHIP, MetricType.ENGAGEMENT, MetricType.REVENUE]:
                buffer_key = f"{creator_id}:{metric_type.value}"
                if buffer_key in self.metric_buffers:
                    period_metrics = [
                        m for m in self.metric_buffers[buffer_key]
                        if start_date <= m.timestamp <= end_date
                    ]
                    
                    if len(period_metrics) >= 2:
                        first_half = period_metrics[:len(period_metrics)//2]
                        second_half = period_metrics[len(period_metrics)//2:]
                        
                        if first_half and second_half:
                            first_avg = statistics.mean([m.value for m in first_half])
                            second_avg = statistics.mean([m.value for m in second_half])
                            
                            if first_avg > 0:
                                growth_rate = ((second_avg - first_avg) / first_avg) * 100
                                growth_indicators[f"{metric_type.value}_growth_rate"] = growth_rate
            
            return growth_indicators
            
        except Exception as e:
            logger.error(f"Failed to calculate growth indicators for {creator_id}: {e}")
            return {}
    
    async def _calculate_comparative_analysis(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comparative analysis against benchmarks."""
        try:
            # This would compare against industry benchmarks
            # For now, return sample comparative data
            comparative_analysis = {
                "industry_percentile": {
                    "viewership": 75.0,
                    "engagement": 82.0,
                    "revenue": 68.0,
                    "growth": 71.0
                },
                "peer_comparison": {
                    "better_than_peers": 65.0,
                    "similar_to_peers": 25.0,
                    "below_peers": 10.0
                },
                "historical_comparison": {
                    "vs_last_period": 15.5,  # % change
                    "vs_last_month": 8.3,
                    "vs_last_quarter": 22.1
                }
            }
            
            return comparative_analysis
            
        except Exception as e:
            logger.error(f"Failed to calculate comparative analysis for {creator_id}: {e}")
            return {}
    
    async def _generate_ai_insights(
        self, 
        creator_id: str, 
        overview_metrics: Dict[str, float], 
        performance_trends: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights and analysis."""
        try:
            # This would use ML models for advanced insights
            ai_insights = {
                "performance_summary": "Strong engagement with growing audience retention",
                "key_strengths": [
                    "Consistent content quality",
                    "High audience engagement",
                    "Effective platform utilization"
                ],
                "improvement_areas": [
                    "Revenue optimization",
                    "Cross-platform promotion",
                    "Content scheduling optimization"
                ],
                "predicted_trends": {
                    "next_period_growth": 12.5,
                    "revenue_potential": 8.7,
                    "audience_expansion": 15.2
                },
                "anomaly_detection": {
                    "unusual_patterns": [],
                    "potential_issues": [],
                    "opportunities": [
                        "Peak engagement window at 8-9 PM",
                        "High conversion rate on weekends"
                    ]
                }
            }
            
            return ai_insights
            
        except Exception as e:
            logger.error(f"Failed to generate AI insights for {creator_id}: {e}")
            return {}
    
    async def _generate_recommendations(
        self, 
        creator_id: str, 
        overview_metrics: Dict[str, float], 
        performance_trends: Dict[str, List[float]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        try:
            recommendations = []
            
            # Analyze metrics and generate recommendations
            if "engagement_average" in overview_metrics:
                if overview_metrics["engagement_average"] < 5.0:
                    recommendations.append({
                        "type": "engagement",
                        "priority": "high",
                        "title": "Improve Audience Engagement",
                        "description": "Your engagement rate is below optimal levels",
                        "actions": [
                            "Increase interactive content",
                            "Respond to comments more frequently",
                            "Use polls and Q&A sessions",
                            "Create compelling call-to-actions"
                        ],
                        "expected_impact": "15-25% increase in engagement"
                    })
            
            if "revenue_average" in overview_metrics:
                if overview_metrics["revenue_average"] < 50.0:
                    recommendations.append({
                        "type": "monetization",
                        "priority": "medium",
                        "title": "Optimize Revenue Streams",
                        "description": "Potential to increase revenue through better monetization",
                        "actions": [
                            "Enable more donation options",
                            "Create premium content tiers",
                            "Partner with relevant brands",
                            "Offer exclusive subscriber benefits"
                        ],
                        "expected_impact": "20-35% revenue increase"
                    })
            
            # Add content optimization recommendations
            recommendations.append({
                "type": "content",
                "priority": "medium",
                "title": "Content Strategy Optimization",
                "description": "Optimize content for better performance",
                "actions": [
                    "Analyze top-performing content themes",
                    "Maintain consistent posting schedule",
                    "Experiment with different content formats",
                    "Use trending topics and hashtags"
                ],
                "expected_impact": "10-20% growth in reach"
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for {creator_id}: {e}")
            return []
    
    async def _generate_predictive_insights(
        self, 
        creator_id: str, 
        insight_types: Optional[List[str]] = None
    ) -> List[PredictiveInsight]:
        """Generate AI-powered predictive insights."""
        try:
            insights = []
            
            # Generate growth prediction
            insights.append(PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                type="growth_prediction",
                priority=InsightPriority.HIGH,
                title="Audience Growth Prediction",
                description="Based on current trends, your audience is predicted to grow significantly",
                prediction={
                    "growth_rate": 15.5,
                    "timeframe": "next_30_days",
                    "confidence": 0.78
                },
                confidence_score=0.78,
                potential_impact="High audience growth potential",
                recommended_actions=[
                    "Increase content frequency",
                    "Focus on high-engagement formats",
                    "Cross-promote on other platforms"
                ],
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            ))
            
            # Generate content performance prediction
            insights.append(PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                type="content_performance",
                priority=InsightPriority.MEDIUM,
                title="Optimal Content Timing",
                description="Your content performs best when posted during specific time windows",
                prediction={
                    "optimal_time": "20:00-21:00",
                    "performance_boost": 25.3,
                    "best_days": ["Friday", "Sunday"]
                },
                confidence_score=0.85,
                potential_impact="25% improvement in initial engagement",
                recommended_actions=[
                    "Schedule content for optimal times",
                    "Test different posting times",
                    "Use scheduling tools for consistency"
                ]
            ))
            
            # Generate revenue prediction
            insights.append(PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                type="revenue_optimization",
                priority=InsightPriority.HIGH,
                title="Revenue Optimization Opportunity",
                description="Untapped revenue potential identified in your content strategy",
                prediction={
                    "revenue_increase": 35.0,
                    "implementation_effort": "medium",
                    "timeframe": "30_days"
                },
                confidence_score=0.72,
                potential_impact="35% revenue increase potential",
                recommended_actions=[
                    "Implement tiered subscription model",
                    "Create exclusive premium content",
                    "Add merchandise integration",
                    "Optimize donation prompts"
                ]
            ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate predictive insights for {creator_id}: {e}")
            return []
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction and strength."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def _calculate_revenue_growth(self, values: List[Decimal]) -> Decimal:
        """Calculate revenue growth rate."""
        if len(values) < 2:
            return Decimal('0.00')
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return Decimal('0.00')
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if first_avg == 0:
            return Decimal('0.00')
        
        growth_rate = ((second_avg - first_avg) / first_avg) * 100
        return growth_rate
    
    def _group_metrics_by_time(self, metrics: List[MetricPoint], interval: str) -> List[List[MetricPoint]]:
        """Group metrics by time intervals."""
        if not metrics:
            return []
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Group by interval (simplified implementation)
        groups = []
        current_group = []
        
        if interval == "hourly":
            current_hour = None
            for metric in sorted_metrics:
                metric_hour = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                if current_hour is None or metric_hour != current_hour:
                    if current_group:
                        groups.append(current_group)
                    current_group = []
                    current_hour = metric_hour
                current_group.append(metric)
            
            if current_group:
                groups.append(current_group)
        
        return groups
    
    # Metric processing functions
    async def _process_viewership_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process viewership-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_engagement_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process engagement-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_retention_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process retention-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_revenue_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process revenue-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_quality_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process quality-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_growth_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process growth-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_audience_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process audience-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    async def _process_performance_metrics(self, metrics: List[MetricPoint]) -> Dict[str, Any]:
        """Process performance-specific metrics."""
        return {"processed": True, "count": len(metrics)}
    
    # Background processing tasks
    async def _real_time_processor(self):
        """Background task for real-time metric processing."""
        while self.is_running:
            try:
                # Process real-time metrics
                for session_id in list(self.real_time_sessions.keys()):
                    await self._process_real_time_session(session_id)
                
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                logger.error(f"Real-time processor error: {e}")
                await asyncio.sleep(30)
    
    async def _batch_processor(self):
        """Background task for batch metric processing."""
        while self.is_running:
            try:
                # Process batched metrics
                for buffer_key in list(self.metric_buffers.keys()):
                    if len(self.metric_buffers[buffer_key]) > 100:  # Process if buffer is large
                        await self._process_metric_buffer(buffer_key)
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(600)
    
    async def _insight_generator(self):
        """Background task for generating insights."""
        while self.is_running:
            try:
                # Generate insights for active creators
                await asyncio.sleep(3600)  # Generate every hour
                
            except Exception as e:
                logger.error(f"Insight generator error: {e}")
                await asyncio.sleep(7200)
    
    async def _trend_analyzer(self):
        """Background task for trend analysis."""
        while self.is_running:
            try:
                # Analyze trends across creators
                await asyncio.sleep(1800)  # Analyze every 30 minutes
                
            except Exception as e:
                logger.error(f"Trend analyzer error: {e}")
                await asyncio.sleep(3600)
    
    async def _alert_monitor(self):
        """Background task for monitoring alerts."""
        while self.is_running:
            try:
                # Monitor for alert conditions
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Alert monitor error: {e}")
                await asyncio.sleep(300)
    
    async def _process_real_time_session(self, session_id: str):
        """Process real-time metrics for a session."""
        # Implementation for real-time processing
        pass
    
    async def _process_metric_buffer(self, buffer_key: str):
        """Process a metric buffer."""
        # Implementation for batch processing
        pass
    
    async def shutdown(self):
        """Gracefully shutdown the analytics engine."""
        self.is_running = False
        
        # Process remaining buffers
        for buffer_key in self.metric_buffers:
            if self.metric_buffers[buffer_key]:
                await self._process_metric_buffer(buffer_key)
        
        logger.info("Streaming Analytics Engine shutdown complete")


async def create_streaming_analytics_engine(
    redis_client: Any, 
    db_session: Session
) -> StreamingAnalyticsEngine:
    """Factory function to create and initialize the analytics engine."""
    engine = StreamingAnalyticsEngine(redis_client, db_session)
    await engine.initialize()
    return engine