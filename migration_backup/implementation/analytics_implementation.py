"""Analytics Implementation - Enterprise Business Intelligence & Performance Analytics

Advanced analytics system for Ainflue creator economy platform providing
comprehensive business intelligence, performance metrics, and predictive insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
import math

logger = logging.getLogger(__name__)


class AnalyticsCategory(Enum):
    """Analytics categories for different business aspects"""
    
    CONTENT_PERFORMANCE = "content_performance"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    REVENUE_ANALYTICS = "revenue_analytics"
    CREATOR_GROWTH = "creator_growth"
    PLATFORM_PERFORMANCE = "platform_performance"
    COLLABORATION_METRICS = "collaboration_metrics"
    SEO_PERFORMANCE = "seo_performance"
    MONETIZATION_ANALYTICS = "monetization_analytics"
    USER_BEHAVIOR = "user_behavior"
    MARKET_INTELLIGENCE = "market_intelligence"


class MetricType(Enum):
    """Types of metrics tracked"""
    
    COUNTER = "counter"           # Incremental values
    GAUGE = "gauge"              # Point-in-time values
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Duration measurements
    RATE = "rate"                # Frequency measurements
    PERCENTAGE = "percentage"     # Ratio values
    CURRENCY = "currency"        # Monetary values
    SCORE = "score"              # Calculated scores


class TimeGranularity(Enum):
    """Time granularity for analytics aggregation"""
    
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class TrendDirection(Enum):
    """Trend direction indicators"""
    
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


@dataclass
class MetricDefinition:
    """Definition of an analytics metric"""
    metric_id: str
    name: str
    description: str
    category: AnalyticsCategory
    metric_type: MetricType
    unit: str
    aggregation_methods: List[str]  # sum, avg, min, max, count
    dimensions: List[str]  # Grouping dimensions
    is_critical: bool = False
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    
    
@dataclass
class DataPoint:
    """Individual data point for analytics"""
    timestamp: datetime
    metric_id: str
    value: Union[int, float]
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class AggregatedMetric:
    """Aggregated metric over a time period"""
    metric_id: str
    time_period: datetime
    granularity: TimeGranularity
    aggregated_value: float
    aggregation_method: str
    sample_count: int
    dimensions: Dict[str, str] = field(default_factory=dict)
    

@dataclass
class TrendAnalysis:
    """Trend analysis for a metric"""
    metric_id: str
    trend_direction: TrendDirection
    trend_strength: float  # 0-1 scale
    growth_rate: float
    seasonality_detected: bool
    forecast_next_period: Optional[float] = None
    confidence_interval: Optional[Dict[str, float]] = None
    

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    report_type: str
    entity_id: str  # creator_id, content_id, etc.
    time_period: Dict[str, datetime]
    metrics: Dict[str, AggregatedMetric]
    trends: List[TrendAnalysis]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    

@dataclass
class Dashboard:
    """Analytics dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    owner_id: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int  # minutes
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class AnalyticsImplementation:
    """
    Enterprise Analytics Implementation for Ainflue Creator Economy Platform
    
    Comprehensive business intelligence system providing real-time analytics,
    performance monitoring, trend analysis, and predictive insights.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Analytics data storage
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.data_points: List[DataPoint] = []
        self.aggregated_metrics: Dict[str, List[AggregatedMetric]] = {}
        self.performance_reports: Dict[str, PerformanceReport] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Real-time metrics buffer
        self.real_time_buffer: Dict[str, List[DataPoint]] = {}
        
        # Trend analysis cache
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        
        # Analytics configuration
        self.analytics_config = self.config.get("analytics", {
            "data_retention_days": 365,
            "aggregation_batch_size": 1000,
            "real_time_buffer_size": 10000,
            "trend_analysis_window_days": 30,
            "alert_check_interval_minutes": 5,
            "auto_insights_enabled": True
        })
        
        # Initialize core metrics
        self._initialize_core_metrics()
        
        # Performance tracking
        self.system_metrics = {
            "total_data_points": 0,
            "metrics_processed_today": 0,
            "reports_generated": 0,
            "alerts_triggered": 0,
            "active_dashboards": 0,
            "insights_generated": 0
        }
    
    async def register_metric(
        self,
        metric_id: str,
        name: str,
        description: str,
        category: AnalyticsCategory,
        metric_type: MetricType,
        unit: str,
        **kwargs
    ) -> MetricDefinition:
        """Register a new analytics metric"""
        
        metric_def = MetricDefinition(
            metric_id=metric_id,
            name=name,
            description=description,
            category=category,
            metric_type=metric_type,
            unit=unit,
            aggregation_methods=kwargs.get("aggregation_methods", ["sum", "avg"]),
            dimensions=kwargs.get("dimensions", []),
            is_critical=kwargs.get("is_critical", False),
            alert_thresholds=kwargs.get("alert_thresholds", {})
        )
        
        self.metric_definitions[metric_id] = metric_def
        
        # Initialize aggregation storage
        self.aggregated_metrics[metric_id] = []
        
        self.logger.info(f"Registered metric: {metric_id} ({name})")
        
        return metric_def
    
    async def record_metric(
        self,
        metric_id: str,
        value: Union[int, float],
        dimensions: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Record a metric data point"""
        
        if metric_id not in self.metric_definitions:
            self.logger.warning(f"Unknown metric: {metric_id}")
            return False
        
        data_point = DataPoint(
            timestamp=timestamp or datetime.utcnow(),
            metric_id=metric_id,
            value=value,
            dimensions=dimensions or {},
            metadata=metadata or {}
        )
        
        # Store data point
        self.data_points.append(data_point)
        
        # Add to real-time buffer
        if metric_id not in self.real_time_buffer:
            self.real_time_buffer[metric_id] = []
        
        self.real_time_buffer[metric_id].append(data_point)
        
        # Maintain buffer size
        buffer_size = self.analytics_config["real_time_buffer_size"]
        if len(self.real_time_buffer[metric_id]) > buffer_size:
            self.real_time_buffer[metric_id] = self.real_time_buffer[metric_id][-buffer_size:]
        
        # Update system metrics
        self.system_metrics["total_data_points"] += 1
        self.system_metrics["metrics_processed_today"] += 1
        
        # Check for alerts if critical metric
        metric_def = self.metric_definitions[metric_id]
        if metric_def.is_critical:
            await self._check_metric_alerts(metric_id, value)
        
        return True
    
    async def aggregate_metrics(
        self,
        metric_id: str,
        granularity: TimeGranularity,
        start_time: datetime,
        end_time: datetime,
        dimensions: Optional[Dict[str, str]] = None
    ) -> List[AggregatedMetric]:
        """Aggregate metric data over time periods"""
        
        if metric_id not in self.metric_definitions:
            return []
        
        metric_def = self.metric_definitions[metric_id]
        
        # Filter data points
        filtered_points = [
            dp for dp in self.data_points
            if (dp.metric_id == metric_id and
                start_time <= dp.timestamp <= end_time and
                (not dimensions or self._dimensions_match(dp.dimensions, dimensions)))
        ]
        
        # Group by time periods
        time_groups = self._group_by_time_period(filtered_points, granularity)
        
        aggregated = []
        
        for time_period, points in time_groups.items():
            if not points:
                continue
            
            values = [dp.value for dp in points]
            
            for agg_method in metric_def.aggregation_methods:
                agg_value = self._calculate_aggregation(values, agg_method)
                
                agg_metric = AggregatedMetric(
                    metric_id=metric_id,
                    time_period=time_period,
                    granularity=granularity,
                    aggregated_value=agg_value,
                    aggregation_method=agg_method,
                    sample_count=len(values),
                    dimensions=dimensions or {}
                )
                
                aggregated.append(agg_metric)
        
        # Store aggregated metrics
        self.aggregated_metrics[metric_id].extend(aggregated)
        
        return aggregated
    
    async def analyze_trends(
        self,
        metric_id: str,
        analysis_window_days: Optional[int] = None
    ) -> TrendAnalysis:
        """Analyze trends for a specific metric"""
        
        window_days = analysis_window_days or self.analytics_config["trend_analysis_window_days"]
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=window_days)
        
        # Get recent aggregated data
        aggregated_data = await self.aggregate_metrics(
            metric_id=metric_id,
            granularity=TimeGranularity.DAY,
            start_time=start_time,
            end_time=end_time
        )
        
        if len(aggregated_data) < 7:  # Need at least a week of data
            return TrendAnalysis(
                metric_id=metric_id,
                trend_direction=TrendDirection.UNKNOWN,
                trend_strength=0.0,
                growth_rate=0.0,
                seasonality_detected=False
            )
        
        # Extract daily averages
        daily_values = []
        for agg in sorted(aggregated_data, key=lambda x: x.time_period):
            if agg.aggregation_method == "avg":
                daily_values.append(agg.aggregated_value)
        
        # Calculate trend metrics
        trend_direction = self._calculate_trend_direction(daily_values)
        trend_strength = self._calculate_trend_strength(daily_values)
        growth_rate = self._calculate_growth_rate(daily_values)
        seasonality = self._detect_seasonality(daily_values)
        
        # Generate forecast
        forecast = self._generate_forecast(daily_values)
        
        trend_analysis = TrendAnalysis(
            metric_id=metric_id,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            growth_rate=growth_rate,
            seasonality_detected=seasonality,
            forecast_next_period=forecast.get("next_value"),
            confidence_interval=forecast.get("confidence_interval")
        )
        
        # Cache the analysis
        self.trend_cache[metric_id] = trend_analysis
        
        return trend_analysis
    
    async def generate_performance_report(
        self,
        entity_id: str,
        entity_type: str,
        report_type: str,
        time_period: Dict[str, datetime],
        include_trends: bool = True
    ) -> PerformanceReport:
        """Generate comprehensive performance report"""
        
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        
        # Determine relevant metrics based on entity type
        relevant_metrics = self._get_relevant_metrics_for_entity(entity_type)
        
        # Aggregate metrics for the time period
        aggregated_metrics = {}
        trends = []
        
        for metric_id in relevant_metrics:
            # Get aggregated data
            agg_data = await self.aggregate_metrics(
                metric_id=metric_id,
                granularity=TimeGranularity.DAY,
                start_time=time_period["start"],
                end_time=time_period["end"],
                dimensions={"entity_id": entity_id}
            )
            
            if agg_data:
                # Take the most recent aggregated value
                latest_agg = max(agg_data, key=lambda x: x.time_period)
                aggregated_metrics[metric_id] = latest_agg
                
                # Generate trend analysis if requested
                if include_trends:
                    trend = await self.analyze_trends(metric_id)
                    trends.append(trend)
        
        # Generate insights and recommendations
        insights = await self._generate_insights(entity_id, entity_type, aggregated_metrics, trends)
        recommendations = await self._generate_recommendations(entity_id, entity_type, aggregated_metrics, trends)
        
        report = PerformanceReport(
            report_id=report_id,
            report_type=report_type,
            entity_id=entity_id,
            time_period=time_period,
            metrics=aggregated_metrics,
            trends=trends,
            insights=insights,
            recommendations=recommendations
        )
        
        self.performance_reports[report_id] = report
        self.system_metrics["reports_generated"] += 1
        
        self.logger.info(f"Generated performance report {report_id} for {entity_type} {entity_id}")
        
        return report
    
    async def create_dashboard(
        self,
        name: str,
        description: str,
        owner_id: str,
        widgets: List[Dict[str, Any]],
        **kwargs
    ) -> Dashboard:
        """Create a new analytics dashboard"""
        
        dashboard_id = f"dashboard_{uuid.uuid4().hex[:12]}"
        
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            owner_id=owner_id,
            widgets=widgets,
            refresh_interval=kwargs.get("refresh_interval", 5),
            is_public=kwargs.get("is_public", False)
        )
        
        self.dashboards[dashboard_id] = dashboard
        self.system_metrics["active_dashboards"] += 1
        
        self.logger.info(f"Created dashboard {dashboard_id}: {name}")
        
        return dashboard
    
    async def get_real_time_metrics(
        self,
        metric_ids: List[str],
        time_window_minutes: int = 60
    ) -> Dict[str, List[DataPoint]]:
        """Get real-time metrics for specified metric IDs"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        real_time_data = {}
        
        for metric_id in metric_ids:
            if metric_id in self.real_time_buffer:
                # Filter by time window
                recent_points = [
                    dp for dp in self.real_time_buffer[metric_id]
                    if dp.timestamp >= cutoff_time
                ]
                real_time_data[metric_id] = recent_points
            else:
                real_time_data[metric_id] = []
        
        return real_time_data
    
    async def get_creator_analytics_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get analytics summary for a specific creator"""
        
        # Define time periods
        now = datetime.utcnow()
        last_30_days = {"start": now - timedelta(days=30), "end": now}
        last_7_days = {"start": now - timedelta(days=7), "end": now}
        
        # Get key metrics
        content_performance = await self._get_creator_content_metrics(creator_id, last_30_days)
        engagement_metrics = await self._get_creator_engagement_metrics(creator_id, last_30_days)
        revenue_metrics = await self._get_creator_revenue_metrics(creator_id, last_30_days)
        growth_metrics = await self._get_creator_growth_metrics(creator_id, last_30_days)
        
        # Calculate growth rates (compare to previous 30 days)
        previous_30_days = {"start": now - timedelta(days=60), "end": now - timedelta(days=30)}
        previous_metrics = await self._get_creator_content_metrics(creator_id, previous_30_days)
        
        growth_rates = self._calculate_period_growth_rates(content_performance, previous_metrics)
        
        # Get recent performance report
        recent_report = await self.generate_performance_report(
            entity_id=creator_id,
            entity_type="creator",
            report_type="monthly_summary",
            time_period=last_30_days
        )
        
        return {
            "creator_id": creator_id,
            "summary_period": "last_30_days",
            "content_performance": content_performance,
            "engagement_metrics": engagement_metrics,
            "revenue_metrics": revenue_metrics,
            "growth_metrics": growth_metrics,
            "growth_rates": growth_rates,
            "top_insights": recent_report.insights[:5],
            "recommendations": recent_report.recommendations[:3],
            "generated_at": now.isoformat()
        }
    
    # Private helper methods
    
    def _initialize_core_metrics(self):
        """Initialize core Ainflue platform metrics"""
        
        core_metrics = [
            # Content Performance
            ("content_views", "Content Views", "Number of content views", 
             AnalyticsCategory.CONTENT_PERFORMANCE, MetricType.COUNTER, "views"),
            ("content_likes", "Content Likes", "Number of content likes", 
             AnalyticsCategory.CONTENT_PERFORMANCE, MetricType.COUNTER, "likes"),
            ("content_shares", "Content Shares", "Number of content shares", 
             AnalyticsCategory.CONTENT_PERFORMANCE, MetricType.COUNTER, "shares"),
            ("content_comments", "Content Comments", "Number of content comments", 
             AnalyticsCategory.CONTENT_PERFORMANCE, MetricType.COUNTER, "comments"),
            
            # Audience Engagement
            ("engagement_rate", "Engagement Rate", "Audience engagement rate", 
             AnalyticsCategory.AUDIENCE_ENGAGEMENT, MetricType.PERCENTAGE, "percent"),
            ("follower_count", "Follower Count", "Number of followers", 
             AnalyticsCategory.AUDIENCE_ENGAGEMENT, MetricType.GAUGE, "followers"),
            ("session_duration", "Session Duration", "Average session duration", 
             AnalyticsCategory.AUDIENCE_ENGAGEMENT, MetricType.TIMER, "seconds"),
            
            # Revenue Analytics
            ("revenue_total", "Total Revenue", "Total revenue generated", 
             AnalyticsCategory.REVENUE_ANALYTICS, MetricType.CURRENCY, "USD"),
            ("revenue_per_view", "Revenue Per View", "Revenue per content view", 
             AnalyticsCategory.REVENUE_ANALYTICS, MetricType.CURRENCY, "USD"),
            ("subscriber_revenue", "Subscriber Revenue", "Revenue from subscriptions", 
             AnalyticsCategory.REVENUE_ANALYTICS, MetricType.CURRENCY, "USD"),
            
            # Creator Growth
            ("new_followers", "New Followers", "New followers gained", 
             AnalyticsCategory.CREATOR_GROWTH, MetricType.COUNTER, "followers"),
            ("content_upload_frequency", "Upload Frequency", "Content upload frequency", 
             AnalyticsCategory.CREATOR_GROWTH, MetricType.RATE, "uploads/day"),
            ("creator_score", "Creator Score", "Overall creator performance score", 
             AnalyticsCategory.CREATOR_GROWTH, MetricType.SCORE, "score"),
            
            # Platform Performance
            ("platform_reach", "Platform Reach", "Reach across platforms", 
             AnalyticsCategory.PLATFORM_PERFORMANCE, MetricType.GAUGE, "reach"),
            ("cross_platform_engagement", "Cross-Platform Engagement", "Engagement across platforms", 
             AnalyticsCategory.PLATFORM_PERFORMANCE, MetricType.PERCENTAGE, "percent"),
            
            # SEO Performance
            ("search_ranking", "Search Ranking", "Average search ranking", 
             AnalyticsCategory.SEO_PERFORMANCE, MetricType.GAUGE, "position"),
            ("organic_traffic", "Organic Traffic", "Organic search traffic", 
             AnalyticsCategory.SEO_PERFORMANCE, MetricType.COUNTER, "visits"),
            
            # Collaboration Metrics
            ("collaboration_success_rate", "Collaboration Success Rate", "Rate of successful collaborations", 
             AnalyticsCategory.COLLABORATION_METRICS, MetricType.PERCENTAGE, "percent"),
            ("collaboration_revenue", "Collaboration Revenue", "Revenue from collaborations", 
             AnalyticsCategory.COLLABORATION_METRICS, MetricType.CURRENCY, "USD")
        ]
        
        for metric_id, name, description, category, metric_type, unit in core_metrics:
            asyncio.create_task(self.register_metric(
                metric_id=metric_id,
                name=name,
                description=description,
                category=category,
                metric_type=metric_type,
                unit=unit,
                dimensions=["creator_id", "content_id", "platform"],
                aggregation_methods=["sum", "avg", "max", "min"] if metric_type in [MetricType.COUNTER, MetricType.GAUGE] else ["avg"]
            ))
    
    def _dimensions_match(self, dp_dimensions: Dict[str, str], filter_dimensions: Dict[str, str]) -> bool:
        """Check if data point dimensions match filter criteria"""
        
        for key, value in filter_dimensions.items():
            if key not in dp_dimensions or dp_dimensions[key] != value:
                return False
        return True
    
    def _group_by_time_period(
        self, 
        data_points: List[DataPoint], 
        granularity: TimeGranularity
    ) -> Dict[datetime, List[DataPoint]]:
        """Group data points by time periods"""
        
        groups = {}
        
        for dp in data_points:
            period_start = self._get_period_start(dp.timestamp, granularity)
            
            if period_start not in groups:
                groups[period_start] = []
            
            groups[period_start].append(dp)
        
        return groups
    
    def _get_period_start(self, timestamp: datetime, granularity: TimeGranularity) -> datetime:
        """Get the start of the time period for a given timestamp"""
        
        if granularity == TimeGranularity.MINUTE:
            return timestamp.replace(second=0, microsecond=0)
        elif granularity == TimeGranularity.HOUR:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.DAY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.WEEK:
            days_since_monday = timestamp.weekday()
            week_start = timestamp - timedelta(days=days_since_monday)
            return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.MONTH:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.QUARTER:
            quarter_start_month = ((timestamp.month - 1) // 3) * 3 + 1
            return timestamp.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.YEAR:
            return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return timestamp
    
    def _calculate_aggregation(self, values: List[float], method: str) -> float:
        """Calculate aggregated value using specified method"""
        
        if not values:
            return 0.0
        
        if method == "sum":
            return sum(values)
        elif method == "avg":
            return statistics.mean(values)
        elif method == "min":
            return min(values)
        elif method == "max":
            return max(values)
        elif method == "count":
            return len(values)
        elif method == "median":
            return statistics.median(values)
        elif method == "stddev":
            return statistics.stdev(values) if len(values) > 1 else 0.0
        
        return 0.0
    
    def _calculate_trend_direction(self, values: List[float]) -> TrendDirection:
        """Calculate trend direction from a series of values"""
        
        if len(values) < 2:
            return TrendDirection.UNKNOWN
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return TrendDirection.STABLE
        
        slope = numerator / denominator
        
        # Determine trend based on slope and variance
        if abs(slope) < 0.1:  # Small slope threshold
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.DECREASING
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength (0-1 scale)"""
        
        if len(values) < 2:
            return 0.0
        
        try:
            # Calculate correlation coefficient between values and time
            n = len(values)
            x = list(range(n))
            
            # Pearson correlation coefficient
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(values)
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            
            x_var = sum((x[i] - x_mean) ** 2 for i in range(n))
            y_var = sum((values[i] - y_mean) ** 2 for i in range(n))
            
            if x_var == 0 or y_var == 0:
                return 0.0
            
            correlation = numerator / math.sqrt(x_var * y_var)
            
            # Return absolute correlation as strength
            return abs(correlation)
            
        except:
            return 0.0
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate from first to last value"""
        
        if len(values) < 2 or values[0] == 0:
            return 0.0
        
        first_value = values[0]
        last_value = values[-1]
        
        growth_rate = (last_value - first_value) / first_value * 100
        
        return growth_rate
    
    def _detect_seasonality(self, values: List[float]) -> bool:
        """Detect if there's seasonality in the data"""
        
        # Simple seasonality detection based on autocorrelation
        if len(values) < 14:  # Need at least 2 weeks of daily data
            return False
        
        # Check for weekly patterns (7-day cycle)
        weekly_correlation = self._calculate_autocorrelation(values, 7)
        
        # Threshold for detecting seasonality
        return weekly_correlation > 0.3
    
    def _calculate_autocorrelation(self, values: List[float], lag: int) -> float:
        """Calculate autocorrelation at specified lag"""
        
        if len(values) <= lag:
            return 0.0
        
        try:
            n = len(values) - lag
            mean_val = statistics.mean(values)
            
            numerator = sum((values[i] - mean_val) * (values[i + lag] - mean_val) for i in range(n))
            denominator = sum((values[i] - mean_val) ** 2 for i in range(len(values)))
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except:
            return 0.0
    
    def _generate_forecast(self, values: List[float]) -> Dict[str, Any]:
        """Generate simple forecast for next period"""
        
        if len(values) < 3:
            return {"next_value": None, "confidence_interval": None}
        
        # Simple moving average forecast
        recent_values = values[-3:]  # Use last 3 values
        forecast_value = statistics.mean(recent_values)
        
        # Simple confidence interval based on recent variance
        if len(values) > 1:
            variance = statistics.variance(recent_values)
            std_dev = math.sqrt(variance)
            
            confidence_interval = {
                "lower": forecast_value - 1.96 * std_dev,
                "upper": forecast_value + 1.96 * std_dev
            }
        else:
            confidence_interval = None
        
        return {
            "next_value": forecast_value,
            "confidence_interval": confidence_interval
        }
    
    async def _check_metric_alerts(self, metric_id: str, value: float):
        """Check if metric value triggers any alerts"""
        
        metric_def = self.metric_definitions[metric_id]
        
        for threshold_type, threshold_value in metric_def.alert_thresholds.items():
            alert_triggered = False
            
            if threshold_type == "max" and value > threshold_value:
                alert_triggered = True
            elif threshold_type == "min" and value < threshold_value:
                alert_triggered = True
            
            if alert_triggered:
                await self._trigger_alert(metric_id, threshold_type, value, threshold_value)
    
    async def _trigger_alert(self, metric_id: str, threshold_type: str, value: float, threshold: float):
        """Trigger an alert for a metric threshold violation"""
        
        self.system_metrics["alerts_triggered"] += 1
        
        # In real implementation, this would send notifications
        self.logger.warning(f"Alert triggered: {metric_id} {threshold_type} threshold violated. Value: {value}, Threshold: {threshold}")
    
    def _get_relevant_metrics_for_entity(self, entity_type: str) -> List[str]:
        """Get relevant metrics for a specific entity type"""
        
        metric_mapping = {
            "creator": [
                "content_views", "content_likes", "content_shares", "content_comments",
                "engagement_rate", "follower_count", "revenue_total", "new_followers",
                "creator_score", "collaboration_success_rate"
            ],
            "content": [
                "content_views", "content_likes", "content_shares", "content_comments",
                "engagement_rate", "revenue_per_view", "search_ranking"
            ],
            "platform": [
                "platform_reach", "cross_platform_engagement", "revenue_total",
                "organic_traffic"
            ]
        }
        
        return metric_mapping.get(entity_type, [])
    
    async def _generate_insights(
        self,
        entity_id: str,
        entity_type: str,
        metrics: Dict[str, AggregatedMetric],
        trends: List[TrendAnalysis]
    ) -> List[str]:
        """Generate AI-powered insights from metrics and trends"""
        
        insights = []
        
        # Engagement insights
        if "engagement_rate" in metrics:
            engagement_rate = metrics["engagement_rate"].aggregated_value
            if engagement_rate > 5.0:
                insights.append(f"Excellent engagement rate of {engagement_rate:.1f}% - well above platform average")
            elif engagement_rate < 2.0:
                insights.append(f"Low engagement rate of {engagement_rate:.1f}% - consider content optimization")
        
        # Growth insights
        for trend in trends:
            if trend.metric_id == "follower_count":
                if trend.trend_direction == TrendDirection.INCREASING:
                    insights.append(f"Strong follower growth with {trend.growth_rate:.1f}% increase")
                elif trend.trend_direction == TrendDirection.DECREASING:
                    insights.append(f"Declining follower count - growth strategy needed")
        
        # Revenue insights
        if "revenue_total" in metrics:
            revenue = metrics["revenue_total"].aggregated_value
            if revenue > 1000:
                insights.append(f"Strong monetization with ${revenue:.2f} revenue generated")
            elif revenue < 100:
                insights.append("Low revenue - explore additional monetization opportunities")
        
        # Content performance insights
        if "content_views" in metrics and "content_upload_frequency" in metrics:
            views = metrics["content_views"].aggregated_value
            frequency = metrics["content_upload_frequency"].aggregated_value
            
            if frequency > 0:
                views_per_content = views / (frequency * 30)  # Assuming monthly period
                if views_per_content > 10000:
                    insights.append("High-performing content with excellent view rates")
                elif views_per_content < 1000:
                    insights.append("Content performance below average - focus on quality improvement")
        
        self.system_metrics["insights_generated"] += len(insights)
        
        return insights
    
    async def _generate_recommendations(
        self,
        entity_id: str,
        entity_type: str,
        metrics: Dict[str, AggregatedMetric],
        trends: List[TrendAnalysis]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Engagement recommendations
        if "engagement_rate" in metrics:
            engagement_rate = metrics["engagement_rate"].aggregated_value
            if engagement_rate < 3.0:
                recommendations.append("Increase engagement by posting at optimal times and using interactive content formats")
        
        # Growth recommendations
        for trend in trends:
            if trend.metric_id == "new_followers" and trend.trend_direction == TrendDirection.DECREASING:
                recommendations.append("Implement follower acquisition strategies: collaborations, cross-promotion, and trending hashtags")
        
        # Content recommendations
        if "content_upload_frequency" in metrics:
            frequency = metrics["content_upload_frequency"].aggregated_value
            if frequency < 0.5:  # Less than 0.5 uploads per day
                recommendations.append("Increase content consistency - aim for daily or every-other-day publishing")
        
        # Revenue recommendations
        if "revenue_total" in metrics:
            revenue = metrics["revenue_total"].aggregated_value
            if revenue < 500:
                recommendations.append("Explore premium content offerings and subscription models to increase revenue")
        
        return recommendations
    
    async def _get_creator_content_metrics(self, creator_id: str, time_period: Dict[str, datetime]) -> Dict[str, float]:
        """Get content performance metrics for a creator"""
        
        # Simulate aggregated content metrics
        return {
            "total_views": 15420,
            "total_likes": 892,
            "total_shares": 156,
            "total_comments": 234,
            "average_engagement_rate": 4.2,
            "content_count": 12
        }
    
    async def _get_creator_engagement_metrics(self, creator_id: str, time_period: Dict[str, datetime]) -> Dict[str, float]:
        """Get engagement metrics for a creator"""
        
        return {
            "follower_count": 8750,
            "average_session_duration": 185.5,
            "repeat_visitor_rate": 34.2,
            "engagement_score": 78.5
        }
    
    async def _get_creator_revenue_metrics(self, creator_id: str, time_period: Dict[str, datetime]) -> Dict[str, float]:
        """Get revenue metrics for a creator"""
        
        return {
            "total_revenue": 1250.75,
            "subscription_revenue": 800.50,
            "ad_revenue": 350.25,
            "collaboration_revenue": 100.00,
            "revenue_per_follower": 0.14
        }
    
    async def _get_creator_growth_metrics(self, creator_id: str, time_period: Dict[str, datetime]) -> Dict[str, float]:
        """Get growth metrics for a creator"""
        
        return {
            "new_followers": 342,
            "follower_growth_rate": 4.1,
            "content_growth_rate": 12.5,
            "engagement_growth_rate": 8.3
        }
    
    def _calculate_period_growth_rates(
        self, 
        current_metrics: Dict[str, float], 
        previous_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate growth rates between two periods"""
        
        growth_rates = {}
        
        for metric, current_value in current_metrics.items():
            if metric in previous_metrics and previous_metrics[metric] > 0:
                previous_value = previous_metrics[metric]
                growth_rate = ((current_value - previous_value) / previous_value) * 100
                growth_rates[f"{metric}_growth_rate"] = growth_rate
        
        return growth_rates


# Export all classes and enums for the implementation module
__all__ = [
    'AnalyticsImplementation',
    'AnalyticsCategory',
    'MetricType',
    'TimeGranularity',
    'TrendDirection',
    'MetricDefinition',
    'DataPoint',
    'AggregatedMetric',
    'TrendAnalysis',
    'PerformanceReport',
    'Dashboard'
]