"""Analytics Engine
================

Advanced analytics and metrics engine for content creator monetization.
Provides real-time analytics, time series analysis, performance reporting,
and predictive analytics with machine learning capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import json
import statistics

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

# Import from enterprise revenue intelligence for shared types
from .enterprise_revenue_intelligence_engine import (
    AnalyticsMetric, TimeSeriesData, PerformanceReport, MetricType, 
    TimeGranularity, AnalyticsType, PlatformType
)


class AggregationType(Enum):
    """Data aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    RATE = "rate"
    GROWTH = "growth"
    VARIANCE = "variance"
    PERCENTILE = "percentile"


class TrendDirection(Enum):
    """Trend direction indicators"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    CYCLICAL = "cyclical"


class AlertSeverity(Enum):
    """Analytics alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class AnalyticsQuery:
    """Analytics query configuration"""
    query_id: str
    user_id: str
    metrics: List[MetricType]
    platforms: List[PlatformType]
    time_range: Dict[str, datetime]
    granularity: TimeGranularity
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregations: List[AggregationType] = field(default_factory=list)


@dataclass
class MetricDefinition:
    """Metric definition and configuration"""
    metric_id: str
    name: str
    metric_type: MetricType
    description: str
    unit: str
    data_source: str
    calculation_method: str
    aggregation_methods: List[AggregationType]
    threshold_rules: Dict[str, Any] = field(default_factory=dict)
    alert_configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsAlert:
    """Analytics alert"""
    alert_id: str
    user_id: str
    metric_type: MetricType
    severity: AlertSeverity
    title: str
    message: str
    current_value: Union[int, float, Decimal]
    threshold_value: Union[int, float, Decimal]
    platform: Optional[PlatformType] = None
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    analysis_id: str
    metric_type: MetricType
    direction: TrendDirection
    slope: float
    correlation: float
    seasonality_detected: bool
    trend_strength: float  # 0-1
    confidence_level: float  # 0-1
    forecast_accuracy: float  # 0-1
    analysis_period: int  # days
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComparisonAnalysis:
    """Comparison analysis between periods or segments"""
    comparison_id: str
    metric_type: MetricType
    baseline_value: Decimal
    comparison_value: Decimal
    change_absolute: Decimal
    change_percentage: float
    statistical_significance: bool
    confidence_interval: List[float]
    p_value: Optional[float] = None


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data"""
    benchmark_id: str
    metric_type: MetricType
    industry_average: Decimal
    top_quartile: Decimal
    median: Decimal
    bottom_quartile: Decimal
    user_percentile: float
    benchmark_date: datetime = field(default_factory=datetime.now)


@dataclass
class AnalyticsInsight:
    """Analytics insight"""
    insight_id: str
    user_id: str
    insight_type: str
    title: str
    description: str
    impact_score: float  # 0-1
    confidence_score: float  # 0-1
    recommended_actions: List[str]
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalyticsCollector:
    """Analytics data collector configuration"""
    collector_id: str
    data_sources: List[str]
    collection_frequency: timedelta
    data_retention: timedelta
    quality_checks: List[str]
    transformation_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MetricsAggregator:
    """Metrics aggregation configuration"""
    aggregator_id: str
    aggregation_rules: List[Dict[str, Any]]
    schedule: Dict[str, Any]
    output_targets: List[str]
    data_quality_threshold: float = 0.95


@dataclass
class AnalyticsVisualizer:
    """Analytics visualization configuration"""
    visualizer_id: str
    chart_types: List[str]
    color_schemes: Dict[str, Any]
    interactive_features: List[str]
    export_formats: List[str]
    refresh_frequency: timedelta = timedelta(minutes=5)


@dataclass
class PredictiveAnalytics:
    """Predictive analytics configuration"""
    model_id: str
    algorithm_type: str
    features: List[str]
    target_variable: str
    prediction_horizon: int  # days
    model_accuracy: float
    last_trained: datetime
    prediction_confidence: float = 0.85


class AnalyticsEngine:
    """
    Advanced analytics and metrics engine for content creator monetization.
    
    Provides comprehensive analytics including real-time metrics, time series analysis,
    performance reporting, predictive analytics, and automated insights generation.
    """
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: Redis) -> None:
        """
        Initialize Analytics Engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.analytics_collector = self._initialize_analytics_collector()
        self.metrics_aggregator = self._initialize_metrics_aggregator()
        self.analytics_visualizer = self._initialize_analytics_visualizer()
        self.predictive_analytics = self._initialize_predictive_analytics()
        
        # Configuration
        self.cache_ttl = 300  # 5 minutes for real-time data
        self.long_cache_ttl = 3600  # 1 hour for aggregated data
        self.max_data_points = 10000
        self.alert_cooldown = timedelta(hours=1)
        
        # Metric definitions
        self.metric_definitions = self._initialize_metric_definitions()
        
        # Performance thresholds
        self.performance_thresholds = {
            MetricType.VIEWS: {"good": 10000, "excellent": 100000},
            MetricType.ENGAGEMENT_RATE: {"good": 0.05, "excellent": 0.10},
            MetricType.REVENUE: {"good": 1000, "excellent": 10000},
            MetricType.CONVERSIONS: {"good": 100, "excellent": 1000},
            MetricType.GROWTH_RATE: {"good": 0.10, "excellent": 0.25}
        }
    
    async def collect_real_time_metrics(self, user_id: str, 
                                      platforms: List[PlatformType]) -> Dict[str, AnalyticsMetric]:
        """
        Collect real-time metrics from all platforms.
        
        Args:
            user_id: User identifier
            platforms: List of platforms to collect from
            
        Returns:
            Dictionary of current metrics
        """
        try:
            current_metrics = {}
            timestamp = datetime.now()
            
            for platform in platforms:
                # Collect platform-specific metrics
                platform_metrics = await self._collect_platform_metrics(user_id, platform)
                
                for metric_type, value in platform_metrics.items():
                    metric = AnalyticsMetric(
                        metric_id=str(uuid.uuid4()),
                        user_id=user_id,
                        metric_type=metric_type,
                        value=value,
                        timestamp=timestamp,
                        platform=platform,
                        metadata={"collection_method": "real_time"}
                    )
                    
                    key = f"{platform.value}_{metric_type.value}"
                    current_metrics[key] = metric
                    
                    # Store in cache for real-time access
                    await self._cache_metric(metric)
                    
                    # Check alert thresholds
                    await self._check_metric_alerts(user_id, metric)
            
            # Store metrics batch
            await self._store_metrics_batch(list(current_metrics.values()))
            
            return current_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting real-time metrics: {str(e)}")
            raise
    
    async def generate_time_series_analysis(self, user_id: str, metric_type: MetricType,
                                          days: int = 30, 
                                          granularity: TimeGranularity = TimeGranularity.DAILY) -> TimeSeriesData:
        """
        Generate time series analysis for specific metric.
        
        Args:
            user_id: User identifier
            metric_type: Type of metric to analyze
            days: Number of days to analyze
            granularity: Time granularity for analysis
            
        Returns:
            Time series data with analysis
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Collect historical data
            historical_data = await self._get_historical_metric_data(
                user_id, metric_type, start_date, end_date, granularity
            )
            
            # Process data points
            data_points = []
            for data_point in historical_data:
                data_points.append({
                    "timestamp": data_point["timestamp"],
                    "value": float(data_point["value"])
                })
            
            # Sort by timestamp
            data_points.sort(key=lambda x: x["timestamp"])
            
            # Perform trend analysis
            trend_analysis = await self._analyze_trend(data_points, metric_type)
            
            # Detect seasonality
            seasonality = await self._detect_seasonality(data_points)
            
            # Generate forecasts
            forecasts = await self._generate_forecasts(data_points, 7)  # 7 days ahead
            
            time_series = TimeSeriesData(
                data_id=str(uuid.uuid4()),
                user_id=user_id,
                metric_type=metric_type,
                granularity=granularity,
                data_points=data_points,
                start_date=start_date,
                end_date=end_date
            )
            
            # Add analysis metadata
            time_series.metadata = {
                "trend_analysis": trend_analysis,
                "seasonality": seasonality,
                "forecasts": forecasts,
                "data_quality_score": await self._calculate_data_quality(data_points)
            }
            
            # Cache time series data
            await self._cache_time_series(time_series)
            
            return time_series
            
        except Exception as e:
            self.logger.error(f"Error generating time series analysis: {str(e)}")
            raise
    
    async def calculate_revenue_analytics(self, user_id: str, days: int = 90) -> Dict[str, Any]:
        """
        Calculate comprehensive revenue analytics.
        
        Args:
            user_id: User identifier
            days: Analysis period in days
            
        Returns:
            Comprehensive revenue analytics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Collect revenue data
            revenue_data = await self._get_revenue_data(user_id, start_date, end_date)
            
            # Calculate basic metrics
            total_revenue = sum(r["amount"] for r in revenue_data)
            average_daily_revenue = total_revenue / days if days > 0 else 0
            
            # Calculate growth metrics
            growth_analysis = await self._calculate_revenue_growth(revenue_data, days)
            
            # Platform breakdown
            platform_breakdown = await self._calculate_platform_breakdown(revenue_data)
            
            # Revenue stream analysis
            stream_analysis = await self._analyze_revenue_streams(revenue_data)
            
            # Trend analysis
            trend_analysis = await self._analyze_revenue_trends(revenue_data)
            
            # Seasonal patterns
            seasonal_patterns = await self._detect_revenue_seasonality(revenue_data)
            
            # Performance benchmarks
            benchmarks = await self._get_revenue_benchmarks(user_id, total_revenue)
            
            analytics = {
                "user_id": user_id,
                "analysis_period": f"{days} days",
                "summary": {
                    "total_revenue": float(total_revenue),
                    "average_daily_revenue": float(average_daily_revenue),
                    "revenue_days": len([r for r in revenue_data if r["amount"] > 0]),
                    "top_revenue_day": max(revenue_data, key=lambda x: x["amount"])["amount"] if revenue_data else 0
                },
                "growth_analysis": growth_analysis,
                "platform_breakdown": platform_breakdown,
                "stream_analysis": stream_analysis,
                "trend_analysis": trend_analysis,
                "seasonal_patterns": seasonal_patterns,
                "benchmarks": benchmarks,
                "insights": await self._generate_revenue_insights(user_id, revenue_data),
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue analytics: {str(e)}")
            raise
    
    async def generate_performance_report(self, user_id: str, 
                                        report_type: str = "comprehensive",
                                        period_days: int = 30) -> PerformanceReport:
        """
        Generate comprehensive performance report.
        
        Args:
            user_id: User identifier
            report_type: Type of report to generate
            period_days: Report period in days
            
        Returns:
            Comprehensive performance report
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Calculate performance score
            performance_score = await self._calculate_overall_performance_score(user_id, period_days)
            
            # Collect key metrics
            key_metrics = await self._collect_key_performance_metrics(user_id, start_date, end_date)
            
            # Generate trend analysis
            trends = await self._generate_performance_trends(user_id, period_days)
            
            # Benchmark comparison
            benchmark_comparison = await self._compare_with_benchmarks(user_id, key_metrics)
            
            # Identify improvement areas
            improvement_areas = await self._identify_improvement_areas(user_id, key_metrics, trends)
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                user_id, performance_score, improvement_areas
            )
            
            report = PerformanceReport(
                report_id=str(uuid.uuid4()),
                user_id=user_id,
                period=f"{period_days} days",
                performance_score=performance_score,
                key_metrics=key_metrics,
                trends=trends,
                benchmark_comparison=benchmark_comparison
            )
            
            # Add additional analysis
            report.metadata = {
                "improvement_areas": improvement_areas,
                "recommendations": recommendations,
                "data_quality_score": await self._assess_data_quality(user_id, period_days),
                "report_type": report_type
            }
            
            # Store report
            await self._store_performance_report(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            raise
    
    async def detect_anomalies(self, user_id: str, 
                             lookback_days: int = 30) -> List[AnalyticsAlert]:
        """
        Detect anomalies in user metrics.
        
        Args:
            user_id: User identifier
            lookback_days: Days to look back for anomaly detection
            
        Returns:
            List of detected anomalies
        """
        try:
            anomalies = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get all metrics for analysis
            for metric_type in MetricType:
                try:
                    # Get historical data
                    historical_data = await self._get_historical_metric_data(
                        user_id, metric_type, start_date, end_date, TimeGranularity.DAILY
                    )
                    
                    if len(historical_data) < 7:  # Need minimum data
                        continue
                    
                    # Calculate statistical thresholds
                    values = [float(d["value"]) for d in historical_data]
                    mean_value = statistics.mean(values)
                    std_dev = statistics.stdev(values) if len(values) > 1 else 0
                    
                    # Define anomaly thresholds (2 standard deviations)
                    upper_threshold = mean_value + (2 * std_dev)
                    lower_threshold = max(0, mean_value - (2 * std_dev))
                    
                    # Check recent values for anomalies
                    recent_data = historical_data[-3:]  # Last 3 days
                    
                    for data_point in recent_data:
                        value = float(data_point["value"])
                        
                        if value > upper_threshold:
                            anomaly = AnalyticsAlert(
                                alert_id=str(uuid.uuid4()),
                                user_id=user_id,
                                metric_type=metric_type,
                                severity=AlertSeverity.WARNING,
                                title=f"High {metric_type.value} detected",
                                message=f"{metric_type.value} value {value} exceeds normal range",
                                current_value=value,
                                threshold_value=upper_threshold,
                                triggered_at=data_point["timestamp"]
                            )
                            anomalies.append(anomaly)
                        
                        elif value < lower_threshold and lower_threshold > 0:
                            anomaly = AnalyticsAlert(
                                alert_id=str(uuid.uuid4()),
                                user_id=user_id,
                                metric_type=metric_type,
                                severity=AlertSeverity.WARNING,
                                title=f"Low {metric_type.value} detected",
                                message=f"{metric_type.value} value {value} below normal range",
                                current_value=value,
                                threshold_value=lower_threshold,
                                triggered_at=data_point["timestamp"]
                            )
                            anomalies.append(anomaly)
                
                except Exception as e:
                    self.logger.warning(f"Error detecting anomalies for {metric_type}: {str(e)}")
                    continue
            
            # Store anomalies
            for anomaly in anomalies:
                await self._store_anomaly_alert(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            raise
    
    # Helper methods
    
    def _initialize_analytics_collector(self) -> AnalyticsCollector:
        """Initialize analytics data collector"""
        return AnalyticsCollector(
            collector_id=str(uuid.uuid4()),
            data_sources=["platforms", "content_analytics", "user_actions"],
            collection_frequency=timedelta(minutes=5),
            data_retention=timedelta(days=365),
            quality_checks=["completeness", "accuracy", "timeliness"]
        )
    
    def _initialize_metrics_aggregator(self) -> MetricsAggregator:
        """Initialize metrics aggregator"""
        return MetricsAggregator(
            aggregator_id=str(uuid.uuid4()),
            aggregation_rules=[
                {"metric": "views", "aggregation": "sum", "granularity": "daily"},
                {"metric": "revenue", "aggregation": "sum", "granularity": "daily"},
                {"metric": "engagement_rate", "aggregation": "average", "granularity": "daily"}
            ],
            schedule={"frequency": "hourly", "offset_minutes": 0},
            output_targets=["database", "cache", "dashboard"]
        )
    
    def _initialize_analytics_visualizer(self) -> AnalyticsVisualizer:
        """Initialize analytics visualizer"""
        return AnalyticsVisualizer(
            visualizer_id=str(uuid.uuid4()),
            chart_types=["line", "bar", "pie", "heatmap", "scatter"],
            color_schemes={"primary": ["#1f77b4", "#ff7f0e", "#2ca02c"]},
            interactive_features=["zoom", "filter", "drill_down"],
            export_formats=["png", "pdf", "svg", "json"]
        )
    
    def _initialize_predictive_analytics(self) -> PredictiveAnalytics:
        """Initialize predictive analytics"""
        return PredictiveAnalytics(
            model_id=str(uuid.uuid4()),
            algorithm_type="ensemble",
            features=["historical_revenue", "engagement_metrics", "content_performance"],
            target_variable="future_revenue",
            prediction_horizon=30,
            model_accuracy=0.85,
            last_trained=datetime.now()
        )
    
    def _initialize_metric_definitions(self) -> Dict[str, MetricDefinition]:
        """Initialize metric definitions"""
        definitions = {}
        
        definitions["views"] = MetricDefinition(
            metric_id="views",
            name="Views",
            metric_type=MetricType.VIEWS,
            description="Total content views across platforms",
            unit="count",
            data_source="platform_apis",
            calculation_method="sum",
            aggregation_methods=[AggregationType.SUM, AggregationType.AVERAGE],
            threshold_rules={"low": 1000, "high": 100000}
        )
        
        definitions["revenue"] = MetricDefinition(
            metric_id="revenue",
            name="Revenue",
            metric_type=MetricType.REVENUE,
            description="Total revenue generated",
            unit="EUR",
            data_source="payment_systems",
            calculation_method="sum",
            aggregation_methods=[AggregationType.SUM],
            threshold_rules={"low": 100, "high": 10000}
        )
        
        return definitions
    
    async def _collect_platform_metrics(self, user_id: str, 
                                       platform: PlatformType) -> Dict[MetricType, Union[int, float]]:
        """Collect metrics from specific platform"""
        # Simulate platform metric collection
        base_metrics = {
            MetricType.VIEWS: 5000,
            MetricType.CLICKS: 250,
            MetricType.ENGAGEMENT_RATE: 0.05,
            MetricType.REVENUE: 150.00
        }
        
        # Add some variation based on platform
        platform_multipliers = {
            PlatformType.YOUTUBE: 1.5,
            PlatformType.INSTAGRAM: 1.2,
            PlatformType.TIKTOK: 2.0,
            PlatformType.SPOTIFY: 0.8
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        
        return {
            metric_type: value * multiplier 
            for metric_type, value in base_metrics.items()
        }
    
    async def _cache_metric(self, metric -> None: AnalyticsMetric) -> None:
        """Cache metric for real-time access"""
        cache_key = f"metric:{metric.user_id}:{metric.platform.value if metric.platform else 'all'}:{metric.metric_type.value}"
        await self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps({
                "value": float(metric.value),
                "timestamp": metric.timestamp.isoformat(),
                "metadata": metric.metadata
            })
        )
    
    async def _check_metric_alerts(self, user_id -> None: str, metric -> None: AnalyticsMetric) -> None:
        """Check if metric triggers any alerts"""
        thresholds = self.performance_thresholds.get(metric.metric_type, {})
        
        if thresholds and metric.value > thresholds.get("excellent", float('inf')):
            # Trigger positive alert
            alert = AnalyticsAlert(
                alert_id=str(uuid.uuid4()),
                user_id=user_id,
                metric_type=metric.metric_type,
                severity=AlertSeverity.INFO,
                title=f"Excellent {metric.metric_type.value} performance",
                message=f"{metric.metric_type.value} reached {metric.value}",
                current_value=metric.value,
                threshold_value=thresholds["excellent"],
                platform=metric.platform
            )
            await self._store_alert(alert)
    
    async def _get_historical_metric_data(self, user_id: str, metric_type: MetricType,
                                        start_date: datetime, end_date: datetime,
                                        granularity: TimeGranularity) -> List[Dict[str, Any]]:
        """Get historical metric data"""
        # Simulate historical data generation
        days = (end_date - start_date).days
        data = []
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # Generate simulated data with some trend and randomness
            base_value = 1000 + (i * 10)  # Upward trend
            noise = (-50 + (i % 100))  # Some variation
            value = max(0, base_value + noise)
            
            data.append({
                "timestamp": date,
                "value": value,
                "granularity": granularity.value
            })
        
        return data
    
    async def _store_metrics_batch(self, metrics -> None: List[AnalyticsMetric]) -> None:
        """Store batch of metrics"""
        # Placeholder implementation
        self.logger.info(f"Storing batch of {len(metrics)} metrics")
    
    async def _analyze_trend(self, data_points: List[Dict], metric_type: MetricType) -> TrendAnalysis:
        """Analyze trend in data points"""
        if len(data_points) < 2:
            return TrendAnalysis(
                analysis_id=str(uuid.uuid4()),
                metric_type=metric_type,
                direction=TrendDirection.STABLE,
                slope=0.0,
                correlation=0.0,
                seasonality_detected=False,
                trend_strength=0.0,
                confidence_level=0.0,
                forecast_accuracy=0.0,
                analysis_period=len(data_points)
            )
        
        # Simple linear trend calculation
        values = [point["value"] for point in data_points]
        x_values = list(range(len(values)))
        
        # Calculate slope (simplified)
        if len(values) > 1:
            slope = (values[-1] - values[0]) / len(values)
        else:
            slope = 0
        
        # Determine direction
        if slope > 5:
            direction = TrendDirection.INCREASING
        elif slope < -5:
            direction = TrendDirection.DECREASING
        else:
            direction = TrendDirection.STABLE
        
        return TrendAnalysis(
            analysis_id=str(uuid.uuid4()),
            metric_type=metric_type,
            direction=direction,
            slope=slope,
            correlation=0.75,  # Simplified
            seasonality_detected=False,
            trend_strength=min(1.0, abs(slope) / 100),
            confidence_level=0.85,
            forecast_accuracy=0.80,
            analysis_period=len(data_points)
        )