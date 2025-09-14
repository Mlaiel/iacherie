"""
🔥 ENTERPRISE PERFORMANCE ANALYZER - AINFLUE PLATFORM
Ultra-advanced performance analytics and tracking system
Consolidates: performance_tracking_workflow.py + real_time_insights_workflow.py + predictive_analytics_workflow.py
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import logging
import statistics
import math
from collections import defaultdict, deque

try:
    from ..utils.metrics import MetricsCollector
    from ..services.analytics.data_processor import DataProcessor
    from ..services.analytics.trend_analyzer import TrendAnalyzer
    from ..services.ai.predictive_engine import PredictiveEngine
except ImportError:
    # Fallback for missing dependencies
    class MetricsCollector: pass
    class DataProcessor: pass
    class TrendAnalyzer: pass
    class PredictiveEngine: pass


class PerformanceMetricType(Enum):
    """Types of performance metrics to track."""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    CLICK_THROUGH_RATE = "ctr"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CONVERSION_RATE = "conversion_rate"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"
    REVENUE = "revenue"
    SUBSCRIBER_GROWTH = "subscriber_growth"
    BOUNCE_RATE = "bounce_rate"


class PlatformType(Enum):
    """Social media and content platforms."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"


class AnalysisTimeframe(Enum):
    """Analysis timeframe options."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class TrendDirection(Enum):
    """Trend direction indicators."""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    metric_type: PerformanceMetricType
    value: float
    previous_value: float = 0.0
    change_absolute: float = 0.0
    change_percentage: float = 0.0
    trend_direction: TrendDirection = TrendDirection.STABLE
    platform: Optional[PlatformType] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RealTimeMetrics:
    """Real-time metrics snapshot."""
    user_id: str = ""
    content_id: str = ""
    metrics: List[PerformanceMetric] = field(default_factory=list)
    live_viewers: int = 0
    active_engagement: float = 0.0
    current_velocity: float = 0.0  # Rate of change
    anomaly_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceInsight:
    """Performance insight and recommendation."""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: str = ""
    title: str = ""
    description: str = ""
    priority: int = 1  # 1 = highest, 10 = lowest
    confidence_score: float = 0.0
    impact_estimate: str = ""
    recommendations: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PredictiveAnalysis:
    """Predictive analytics results."""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_metric: PerformanceMetricType = PerformanceMetricType.VIEWS
    predicted_value: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    prediction_horizon: timedelta = field(default=timedelta(days=7))
    model_accuracy: float = 0.0
    contributing_factors: List[str] = field(default_factory=list)
    scenario_analysis: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceReport:
    """Comprehensive performance report."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    timeframe: AnalysisTimeframe = AnalysisTimeframe.WEEKLY
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=datetime.utcnow)
    metrics_summary: Dict[str, PerformanceMetric] = field(default_factory=dict)
    platform_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)
    top_performing_content: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[PerformanceInsight] = field(default_factory=list)
    predictions: List[PredictiveAnalysis] = field(default_factory=list)
    benchmarks: Dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceAnalyzerConfig:
    """Performance analyzer configuration."""
    enable_real_time_tracking: bool = True
    enable_predictive_analytics: bool = True
    real_time_update_interval: int = 60  # seconds
    data_retention_days: int = 365
    anomaly_detection_threshold: float = 2.0  # standard deviations
    min_data_points_for_prediction: int = 30
    prediction_accuracy_threshold: float = 0.7
    enable_cross_platform_analysis: bool = True
    enable_competitor_benchmarking: bool = True


class PerformanceAnalyzer:
    """
    🔥 ENTERPRISE PERFORMANCE ANALYZER
    
    Ultra-advanced performance analytics with:
    - Real-time performance tracking
    - Cross-platform analytics
    - Predictive performance modeling
    - Anomaly detection
    - Trend analysis
    - Competitive benchmarking
    - Performance insights and recommendations
    - Advanced reporting capabilities
    """
    
    def __init__(self, config: PerformanceAnalyzerConfig = None):
        """Initialize enterprise performance analyzer."""
        self.config = config or PerformanceAnalyzerConfig()
        
        # Performance data storage
        self.performance_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.real_time_metrics: Dict[str, RealTimeMetrics] = {}
        self.performance_reports: Dict[str, PerformanceReport] = {}
        self.insights_cache: Dict[str, List[PerformanceInsight]] = {}
        self.predictions_cache: Dict[str, List[PredictiveAnalysis]] = {}
        
        # Analytics state
        self.baseline_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.anomaly_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.trend_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Background tasks
        self._analyzer_active = True
        self._real_time_task = None
        self._analysis_task = None
        self._cleanup_task = None
        
        # Services
        self.data_processor = DataProcessor() if DataProcessor else None
        self.trend_analyzer = TrendAnalyzer() if TrendAnalyzer else None
        self.predictive_engine = PredictiveEngine() if PredictiveEngine else None
        self.metrics = MetricsCollector() if MetricsCollector else None
        
        self.logger = logging.getLogger(__name__)
        
        # Start background processing
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background analytics tasks."""
        if self.config.enable_real_time_tracking and not self._real_time_task:
            self._real_time_task = asyncio.create_task(self._real_time_tracking_loop())
        
        if not self._analysis_task:
            self._analysis_task = asyncio.create_task(self._analysis_loop())
        
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    # REAL-TIME PERFORMANCE TRACKING
    
    async def track_real_time_performance(
        self,
        user_id: str,
        content_id: str = "",
        platform_data: Dict[PlatformType, Dict[str, float]] = None
    ) -> RealTimeMetrics:
        """Track real-time performance metrics."""
        if not platform_data:
            platform_data = {}
        
        # Aggregate metrics across platforms
        aggregated_metrics = []
        total_metrics = defaultdict(float)
        
        for platform, metrics_data in platform_data.items():
            for metric_name, value in metrics_data.items():
                try:
                    metric_type = PerformanceMetricType(metric_name)
                    
                    # Get previous value for trend calculation
                    key = f"{user_id}_{platform.value}_{metric_name}"
                    previous_value = self._get_latest_metric_value(key)
                    
                    # Calculate changes
                    change_absolute = value - previous_value
                    change_percentage = (change_absolute / previous_value * 100) if previous_value > 0 else 0
                    
                    # Determine trend direction
                    trend_direction = self._calculate_trend_direction(change_percentage)
                    
                    metric = PerformanceMetric(
                        metric_type=metric_type,
                        value=value,
                        previous_value=previous_value,
                        change_absolute=change_absolute,
                        change_percentage=change_percentage,
                        trend_direction=trend_direction,
                        platform=platform
                    )
                    
                    aggregated_metrics.append(metric)
                    total_metrics[metric_name] += value
                    
                    # Store for historical tracking
                    self._store_metric_data(key, value)
                
                except ValueError:
                    # Skip unknown metric types
                    continue
        
        # Calculate performance velocity
        velocity = self._calculate_performance_velocity(user_id, total_metrics)
        
        # Detect anomalies
        anomaly_score = self._detect_anomalies(user_id, total_metrics)
        
        # Create real-time metrics
        real_time_metrics = RealTimeMetrics(
            user_id=user_id,
            content_id=content_id,
            metrics=aggregated_metrics,
            current_velocity=velocity,
            anomaly_score=anomaly_score
        )
        
        # Cache for real-time access
        self.real_time_metrics[user_id] = real_time_metrics
        
        # Record metrics
        if self.metrics:
            self.metrics.record_histogram("performance_velocity", velocity)
            self.metrics.record_histogram("anomaly_score", anomaly_score)
        
        return real_time_metrics
    
    def _get_latest_metric_value(self, key: str) -> float:
        """Get latest metric value for comparison."""
        if key in self.performance_data and self.performance_data[key]:
            return self.performance_data[key][-1]
        return 0.0
    
    def _store_metric_data(self, key: str, value: float):
        """Store metric data for historical analysis."""
        self.performance_data[key].append(value)
    
    def _calculate_trend_direction(self, change_percentage: float) -> TrendDirection:
        """Calculate trend direction based on change percentage."""
        if abs(change_percentage) < 1:
            return TrendDirection.STABLE
        elif change_percentage > 5:
            return TrendDirection.RISING
        elif change_percentage < -5:
            return TrendDirection.FALLING
        elif abs(change_percentage) > 20:
            return TrendDirection.VOLATILE
        else:
            return TrendDirection.STABLE
    
    def _calculate_performance_velocity(self, user_id: str, metrics: Dict[str, float]) -> float:
        """Calculate performance velocity (rate of change)."""
        # Simple velocity calculation based on recent metric changes
        velocity_scores = []
        
        for metric_name, current_value in metrics.items():
            key = f"{user_id}_{metric_name}"
            if key in self.performance_data and len(self.performance_data[key]) >= 2:
                recent_values = list(self.performance_data[key])[-5:]  # Last 5 data points
                if len(recent_values) >= 2:
                    # Calculate trend slope
                    x_vals = list(range(len(recent_values)))
                    y_vals = recent_values
                    
                    # Simple linear regression slope
                    n = len(recent_values)
                    slope = (n * sum(x*y for x, y in zip(x_vals, y_vals)) - sum(x_vals) * sum(y_vals)) / (n * sum(x*x for x in x_vals) - sum(x_vals)**2) if n > 1 else 0
                    velocity_scores.append(slope)
        
        return statistics.mean(velocity_scores) if velocity_scores else 0.0
    
    def _detect_anomalies(self, user_id: str, metrics: Dict[str, float]) -> float:
        """Detect anomalies in performance metrics."""
        anomaly_scores = []
        
        for metric_name, current_value in metrics.items():
            key = f"{user_id}_{metric_name}"
            if key in self.performance_data and len(self.performance_data[key]) >= 10:
                historical_values = list(self.performance_data[key])
                
                # Calculate z-score
                mean_val = statistics.mean(historical_values)
                std_val = statistics.stdev(historical_values) if len(historical_values) > 1 else 1
                
                z_score = abs((current_value - mean_val) / std_val) if std_val > 0 else 0
                anomaly_scores.append(z_score)
        
        return max(anomaly_scores) if anomaly_scores else 0.0
    
    # PERFORMANCE ANALYSIS
    
    async def analyze_performance(
        self,
        user_id: str,
        timeframe: AnalysisTimeframe = AnalysisTimeframe.WEEKLY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        platforms: Optional[List[PlatformType]] = None
    ) -> PerformanceReport:
        """Analyze performance metrics for specified timeframe."""
        if not start_date:
            if timeframe == AnalysisTimeframe.DAILY:
                start_date = datetime.utcnow() - timedelta(days=1)
            elif timeframe == AnalysisTimeframe.WEEKLY:
                start_date = datetime.utcnow() - timedelta(weeks=1)
            elif timeframe == AnalysisTimeframe.MONTHLY:
                start_date = datetime.utcnow() - timedelta(days=30)
            else:
                start_date = datetime.utcnow() - timedelta(days=7)
        
        if not end_date:
            end_date = datetime.utcnow()
        
        # Analyze metrics
        metrics_summary = await self._analyze_metrics_summary(user_id, start_date, end_date)
        platform_breakdown = await self._analyze_platform_breakdown(user_id, platforms, start_date, end_date)
        top_content = await self._identify_top_performing_content(user_id, start_date, end_date)
        insights = await self._generate_performance_insights(user_id, metrics_summary, platform_breakdown)
        predictions = await self._generate_predictions(user_id, metrics_summary) if self.config.enable_predictive_analytics else []
        benchmarks = await self._calculate_benchmarks(user_id, metrics_summary)
        
        # Create performance report
        report = PerformanceReport(
            user_id=user_id,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            metrics_summary=metrics_summary,
            platform_breakdown=platform_breakdown,
            top_performing_content=top_content,
            insights=insights,
            predictions=predictions,
            benchmarks=benchmarks
        )
        
        # Cache report
        self.performance_reports[report.report_id] = report
        
        self.logger.info(f"Generated performance report {report.report_id} for user {user_id}")
        
        return report
    
    async def _analyze_metrics_summary(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, PerformanceMetric]:
        """Analyze metrics summary for timeframe."""
        summary = {}
        
        for metric_type in PerformanceMetricType:
            key = f"{user_id}_{metric_type.value}"
            if key in self.performance_data:
                values = list(self.performance_data[key])
                if values:
                    current_value = values[-1] if values else 0
                    previous_value = values[-2] if len(values) > 1 else 0
                    
                    change_absolute = current_value - previous_value
                    change_percentage = (change_absolute / previous_value * 100) if previous_value > 0 else 0
                    trend_direction = self._calculate_trend_direction(change_percentage)
                    
                    metric = PerformanceMetric(
                        metric_type=metric_type,
                        value=current_value,
                        previous_value=previous_value,
                        change_absolute=change_absolute,
                        change_percentage=change_percentage,
                        trend_direction=trend_direction
                    )
                    
                    summary[metric_type.value] = metric
        
        return summary
    
    async def _analyze_platform_breakdown(
        self,
        user_id: str,
        platforms: Optional[List[PlatformType]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Dict[str, float]]:
        """Analyze performance breakdown by platform."""
        breakdown = {}
        
        target_platforms = platforms or list(PlatformType)
        
        for platform in target_platforms:
            platform_metrics = {}
            
            for metric_type in PerformanceMetricType:
                key = f"{user_id}_{platform.value}_{metric_type.value}"
                if key in self.performance_data and self.performance_data[key]:
                    platform_metrics[metric_type.value] = self.performance_data[key][-1]
            
            if platform_metrics:
                breakdown[platform.value] = platform_metrics
        
        return breakdown
    
    async def _identify_top_performing_content(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Identify top performing content."""
        # Placeholder implementation
        return [
            {
                "content_id": "content_1",
                "title": "Top Performing Video",
                "views": 100000,
                "engagement_rate": 8.5,
                "platform": "youtube"
            },
            {
                "content_id": "content_2",
                "title": "Viral Post",
                "views": 50000,
                "engagement_rate": 12.3,
                "platform": "instagram"
            }
        ]
    
    async def _generate_performance_insights(
        self,
        user_id: str,
        metrics_summary: Dict[str, PerformanceMetric],
        platform_breakdown: Dict[str, Dict[str, float]]
    ) -> List[PerformanceInsight]:
        """Generate performance insights and recommendations."""
        insights = []
        
        # Analyze engagement trends
        if 'engagement_rate' in metrics_summary:
            engagement_metric = metrics_summary['engagement_rate']
            if engagement_metric.trend_direction == TrendDirection.FALLING:
                insights.append(PerformanceInsight(
                    insight_type="engagement_decline",
                    title="Engagement Rate Declining",
                    description=f"Engagement rate has decreased by {abs(engagement_metric.change_percentage):.1f}%",
                    priority=2,
                    confidence_score=0.8,
                    impact_estimate="medium",
                    recommendations=[
                        "Experiment with different content formats",
                        "Increase interaction with audience",
                        "Post at optimal times",
                        "Use trending hashtags and topics"
                    ]
                ))
        
        # Analyze platform performance
        best_platform = max(platform_breakdown.items(), key=lambda x: x[1].get('engagement_rate', 0)) if platform_breakdown else None
        if best_platform:
            insights.append(PerformanceInsight(
                insight_type="platform_optimization",
                title=f"Strong Performance on {best_platform[0].title()}",
                description=f"Your content performs best on {best_platform[0]}",
                priority=1,
                confidence_score=0.9,
                impact_estimate="high",
                recommendations=[
                    f"Focus more content creation on {best_platform[0]}",
                    f"Cross-promote {best_platform[0]} content on other platforms",
                    f"Study successful {best_platform[0]} content patterns"
                ]
            ))
        
        # Growth opportunity insights
        for metric_name, metric in metrics_summary.items():
            if metric.trend_direction == TrendDirection.RISING and metric.change_percentage > 10:
                insights.append(PerformanceInsight(
                    insight_type="growth_opportunity",
                    title=f"Strong Growth in {metric_name.replace('_', ' ').title()}",
                    description=f"{metric_name.replace('_', ' ').title()} increased by {metric.change_percentage:.1f}%",
                    priority=1,
                    confidence_score=0.85,
                    impact_estimate="high",
                    recommendations=[
                        f"Continue current strategy for {metric_name}",
                        "Scale successful content types",
                        "Analyze what's driving this growth"
                    ]
                ))
        
        return insights
    
    async def _generate_predictions(
        self,
        user_id: str,
        metrics_summary: Dict[str, PerformanceMetric]
    ) -> List[PredictiveAnalysis]:
        """Generate predictive analytics."""
        predictions = []
        
        if not self.predictive_engine:
            return predictions
        
        for metric_name, metric in metrics_summary.items():
            try:
                metric_type = PerformanceMetricType(metric_name)
                key = f"{user_id}_{metric_name}"
                
                if key in self.performance_data and len(self.performance_data[key]) >= self.config.min_data_points_for_prediction:
                    historical_data = list(self.performance_data[key])
                    
                    # Simple trend-based prediction
                    recent_values = historical_data[-10:]  # Last 10 data points
                    if len(recent_values) >= 3:
                        # Linear trend prediction
                        x_vals = list(range(len(recent_values)))
                        y_vals = recent_values
                        
                        # Calculate trend
                        n = len(recent_values)
                        slope = (n * sum(x*y for x, y in zip(x_vals, y_vals)) - sum(x_vals) * sum(y_vals)) / (n * sum(x*x for x in x_vals) - sum(x_vals)**2) if n > 1 else 0
                        
                        # Predict next week value
                        predicted_value = recent_values[-1] + (slope * 7)  # 7 days ahead
                        
                        # Simple confidence interval (±20%)
                        confidence_interval = (predicted_value * 0.8, predicted_value * 1.2)
                        
                        prediction = PredictiveAnalysis(
                            target_metric=metric_type,
                            predicted_value=max(0, predicted_value),  # Ensure non-negative
                            confidence_interval=confidence_interval,
                            prediction_horizon=timedelta(days=7),
                            model_accuracy=0.75,  # Placeholder accuracy
                            contributing_factors=["historical_trend", "recent_performance"]
                        )
                        
                        predictions.append(prediction)
            
            except (ValueError, ZeroDivisionError):
                continue
        
        return predictions
    
    async def _calculate_benchmarks(
        self,
        user_id: str,
        metrics_summary: Dict[str, PerformanceMetric]
    ) -> Dict[str, float]:
        """Calculate performance benchmarks."""
        # Industry benchmark placeholders
        benchmarks = {
            "engagement_rate": 3.5,  # Industry average
            "click_through_rate": 2.1,
            "conversion_rate": 1.8,
            "subscriber_growth": 5.0
        }
        
        return benchmarks
    
    # BACKGROUND TASKS
    
    async def _real_time_tracking_loop(self):
        """Background task for real-time tracking."""
        while self._analyzer_active:
            try:
                # Update real-time metrics for active users
                for user_id in list(self.real_time_metrics.keys()):
                    await self._update_real_time_metrics(user_id)
                
                await asyncio.sleep(self.config.real_time_update_interval)
            except Exception as e:
                self.logger.error(f"Real-time tracking loop error: {e}")
                await asyncio.sleep(60)
    
    async def _analysis_loop(self):
        """Background task for periodic analysis."""
        while self._analyzer_active:
            try:
                # Perform periodic analysis for active users
                await self._perform_periodic_analysis()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Analysis loop error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_loop(self):
        """Background cleanup task."""
        while self._analyzer_active:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(24 * 3600)  # Run daily
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(3600)
    
    async def _update_real_time_metrics(self, user_id: str):
        """Update real-time metrics for user."""
        # Placeholder for real-time metric updates
        pass
    
    async def _perform_periodic_analysis(self):
        """Perform periodic analysis for insights generation."""
        # Placeholder for periodic analysis
        pass
    
    async def _cleanup_old_data(self):
        """Clean up old performance data."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.data_retention_days)
        
        # Clean up old reports
        old_reports = [
            report_id for report_id, report in self.performance_reports.items()
            if report.generated_at < cutoff_date
        ]
        
        for report_id in old_reports:
            del self.performance_reports[report_id]
    
    # PUBLIC API METHODS
    
    def get_real_time_metrics(self, user_id: str) -> Optional[RealTimeMetrics]:
        """Get current real-time metrics for user."""
        return self.real_time_metrics.get(user_id)
    
    def get_performance_report(self, report_id: str) -> Optional[PerformanceReport]:
        """Get performance report by ID."""
        return self.performance_reports.get(report_id)
    
    def get_analyzer_status(self) -> Dict[str, Any]:
        """Get performance analyzer status."""
        return {
            "active": self._analyzer_active,
            "real_time_tracking_enabled": self.config.enable_real_time_tracking,
            "predictive_analytics_enabled": self.config.enable_predictive_analytics,
            "tracked_users": len(self.real_time_metrics),
            "generated_reports": len(self.performance_reports),
            "data_points": sum(len(data) for data in self.performance_data.values())
        }
    
    async def shutdown(self):
        """Shutdown performance analyzer."""
        self._analyzer_active = False
        
        if self._real_time_task:
            self._real_time_task.cancel()
        
        if self._analysis_task:
            self._analysis_task.cancel()
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        self.logger.info("Performance analyzer shutdown completed")