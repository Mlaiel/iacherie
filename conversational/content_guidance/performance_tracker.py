"""Performance Tracker - Advanced Analytics and Performance Monitoring System
========================================================================

This module provides comprehensive performance tracking, analytics, and
insights for content creators across multiple platforms and metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.analytics.metrics_collector import MetricsCollectionService
from backend.ai.ml.performance_predictor import PerformancePredictionEngine
from backend.integrations.platform_apis import PlatformAPIManager

logger = get_logger(__name__)
settings = get_settings()


class MetricType(Enum):
    """
Types of performance metrics."""

    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    FOLLOWER_GROWTH = "follower_growth"
    AUDIENCE_RETENTION = "audience_retention"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"
    BRAND_MENTIONS = "brand_mentions"
    SENTIMENT_SCORE = "sentiment_score"
    REVENUE = "revenue"
    CPM = "cpm"
    CPC = "cpc"
    ROI = "roi"


class TimeFrame(Enum):
    """Time frame for performance analysis."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class PerformanceCategory(Enum):
    """Categories of performance analysis."""

    CONTENT_PERFORMANCE = "content_performance"
    AUDIENCE_GROWTH = "audience_growth"
    ENGAGEMENT_QUALITY = "engagement_quality"
    MONETIZATION = "monetization"
    BRAND_METRICS = "brand_metrics"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    PLATFORM_OPTIMIZATION = "platform_optimization"


class TrendDirection(Enum):
    """Direction of performance trends."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    SEASONAL = "seasonal"


@dataclass
class MetricDataPoint:
    """Individual metric data point."""
    timestamp: datetime
    metric_type: MetricType
    value: float
    platform: str
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceTrend:
    """
Performance trend analysis."""
    metric_type: MetricType
    trend_direction: TrendDirection
    growth_rate: float
    confidence_interval: Tuple[float, float]
    trend_strength: float
    seasonality_detected: bool
    anomalies: List[Dict[str, Any]]
    forecast: List[Dict[str, Any]]


@dataclass
class ContentPerformanceMetrics:
    """
Performance metrics for individual content."""
    content_id: str
    content_type: str
    platform: str
    publish_date: datetime
    metrics: Dict[MetricType, float]
    engagement_rate: float
    reach: int
    performance_score: float
    ranking_percentile: float
    best_performing_aspects: List[str]
    improvement_opportunities: List[str]


@dataclass
class PlatformPerformance:
    """
Platform-specific performance summary."""
    platform: str
    time_period: TimeFrame
    total_content: int
    avg_engagement_rate: float
    total_reach: int
    total_followers: int
    follower_growth_rate: float
    top_performing_content: List[str]
    performance_trends: List[PerformanceTrend]
    competitive_position: Dict[str, Any]
    optimization_recommendations: List[str]


@dataclass
class PerformanceBenchmark:
    """
Performance benchmark comparison."""
    metric_type: MetricType
    creator_value: float
    industry_average: float
    industry_percentile: float
    top_10_percent_threshold: float
    improvement_potential: float
    benchmark_category: str


@dataclass
class PerformanceInsight:
    """
Actionable performance insight."""
    insight_id: str
    insight_type: str
    title: str
    description: str
    key_findings: List[str]
    actionable_recommendations: List[str]
    expected_impact: str
    confidence_score: float
    priority_level: str
    supporting_data: Dict[str, Any]
    generated_at: datetime


@dataclass
class PerformanceReport:
    """
Comprehensive performance report."""
    report_id: str
    creator_id: str
    report_period: Dict[str, datetime]
    overall_performance_score: float
    platform_performances: List[PlatformPerformance]
    content_performances: List[ContentPerformanceMetrics]
    performance_trends: List[PerformanceTrend]
    benchmarks: List[PerformanceBenchmark]
    insights: List[PerformanceInsight]
    recommendations: List[str]
    goals_progress: Dict[str, float]
    generated_at: datetime


class MetricsCollector:
    """
    Advanced metrics collection system that gathers performance data
    from multiple platforms and sources.
    """
    
    def __init__(self):
        """
Initialize the metrics collector."""
        self.collection_service = MetricsCollectionService()
        self.platform_manager = PlatformAPIManager()
        
        # Data storage and processing
        self.metrics_cache = defaultdict(list)
        self.aggregation_rules = self._initialize_aggregation_rules()
        
        # Platform-specific metric mappings
        self.platform_metrics = self._initialize_platform_metrics()
        
        logger.info("Metrics collector initialized successfully")
    
    def _initialize_aggregation_rules(self) -> Dict[MetricType, Dict[str, Any]]:
        """Initialize metric aggregation rules."""
        
        return {
            MetricType.ENGAGEMENT_RATE: {
                'calculation': 'weighted_average',
                'weights': 'impressions',
                'range': (0, 1),
                'format': 'percentage'
            },
            MetricType.REACH: {
                'calculation': 'sum',
                'range': (0, float('inf')),
                'format': 'integer'
            },
            MetricType.FOLLOWER_GROWTH: {
                'calculation': 'net_change',
                'range': (-float('inf'), float('inf')),
                'format': 'integer'
            },
            MetricType.REVENUE: {
                'calculation': 'sum',
                'range': (0, float('inf')),
                'format': 'currency'
            },
            MetricType.SENTIMENT_SCORE: {
                'calculation': 'average',
                'range': (-1, 1),
                'format': 'decimal'
            }
        }
    
    def _initialize_platform_metrics(self) -> Dict[str, List[MetricType]]:
        """
Initialize platform-specific available metrics."""
        
        return {
            'instagram': [
                MetricType.ENGAGEMENT_RATE, MetricType.REACH, MetricType.IMPRESSIONS,
                MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES, MetricType.SAVES,
                MetricType.FOLLOWER_GROWTH, MetricType.CLICK_THROUGH_RATE
            ],
            'tiktok': [
                MetricType.ENGAGEMENT_RATE, MetricType.VIEWS, MetricType.LIKES,
                MetricType.COMMENTS, MetricType.SHARES, MetricType.COMPLETION_RATE,
                MetricType.FOLLOWER_GROWTH, MetricType.WATCH_TIME
            ],
            'youtube': [
                MetricType.VIEWS, MetricType.WATCH_TIME, MetricType.ENGAGEMENT_RATE,
                MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES,
                MetricType.AUDIENCE_RETENTION, MetricType.CLICK_THROUGH_RATE,
                MetricType.FOLLOWER_GROWTH, MetricType.REVENUE
            ],
            'spotify': [
                MetricType.VIEWS, MetricType.COMPLETION_RATE, MetricType.SAVES,
                MetricType.FOLLOWER_GROWTH, MetricType.AUDIENCE_RETENTION
            ],
            'twitter': [
                MetricType.ENGAGEMENT_RATE, MetricType.IMPRESSIONS, MetricType.LIKES,
                MetricType.COMMENTS, MetricType.SHARES, MetricType.CLICK_THROUGH_RATE,
                MetricType.FOLLOWER_GROWTH
            ]
        }
    
    async def collect_platform_metrics(
        self,
        creator_id: str,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[MetricDataPoint]:
        """
        Collect metrics from multiple platforms for a creator.
        
        Args:
            creator_id: Creator identifier
            platforms: List of platforms to collect from
            start_date: Start date for metric collection
            end_date: End date for metric collection
            
        Returns:
            List of collected metric data points
        """
        
        try:
            all_metrics = []
            
            for platform in platforms:
                platform_metrics = await self._collect_platform_specific_metrics(
                    creator_id, platform, start_date, end_date
                )
                all_metrics.extend(platform_metrics)
            
            logger.info(f"Collected {len(all_metrics)} metric data points for creator {creator_id}")
            return all_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect platform metrics: {e}")
            return []
    
    async def _collect_platform_specific_metrics(
        self,
        creator_id: str,
        platform: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[MetricDataPoint]:
        """Collect metrics from a specific platform."""
        
        metrics = []
        available_metrics = self.platform_metrics.get(platform, [])
        
        try:
            # This would make actual API calls to platform in production
            # For now, generate realistic synthetic data
            
            current_date = start_date
            while current_date <= end_date:
                for metric_type in available_metrics:
                    # Generate realistic metric values
                    value = self._generate_realistic_metric_value(
                        metric_type, platform, current_date
                    )
                    
                    metric_point = MetricDataPoint(
                        timestamp=current_date,
                        metric_type=metric_type,
                        value=value,
                        platform=platform,
                        content_id=None,  # Platform-level metric
                        metadata={
                            'source': f'{platform}_api',
                            'collection_method': 'automated'
                        }
                    )
                    metrics.append(metric_point)
                
                current_date += timedelta(days=1)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics from {platform}: {e}")
            return []
    
    def _generate_realistic_metric_value(
        self, metric_type: MetricType, platform: str, date: datetime
    ) -> float:
        """Generate realistic metric values for testing."""
        
        # Base values by platform and metric type
        base_values = {
            'instagram': {
                MetricType.ENGAGEMENT_RATE: 0.045,
                MetricType.REACH: 15000,
                MetricType.LIKES: 800,
                MetricType.COMMENTS: 45,
                MetricType.FOLLOWER_GROWTH: 50
            },
            'tiktok': {
                MetricType.ENGAGEMENT_RATE: 0.08,
                MetricType.VIEWS: 25000,
                MetricType.LIKES: 2000,
                MetricType.COMMENTS: 120,
                MetricType.COMPLETION_RATE: 0.75
            },
            'youtube': {
                MetricType.VIEWS: 5000,
                MetricType.WATCH_TIME: 3000,
                MetricType.ENGAGEMENT_RATE: 0.06,
                MetricType.LIKES: 300,
                MetricType.COMMENTS: 25
            }
        }
        
        platform_base = base_values.get(platform, {})
        base_value = platform_base.get(metric_type, 100)
        
        # Add realistic variation
        day_of_week_factor = 1.0
        if date.weekday() in [5, 6]:  # Weekend boost
            day_of_week_factor = 1.2
        
        seasonal_factor = 1.0 + 0.1 * np.sin(date.timetuple().tm_yday * 2 * np.pi / 365)
        
        random_variation = np.random.normal(1.0, 0.2)
        
        final_value = base_value * day_of_week_factor * seasonal_factor * random_variation
        
        # Apply metric-specific constraints
        if metric_type in [MetricType.ENGAGEMENT_RATE, MetricType.COMPLETION_RATE]:
            final_value = max(0, min(1, final_value))
        elif metric_type in [MetricType.SENTIMENT_SCORE]:
            final_value = max(-1, min(1, final_value))
        else:
            final_value = max(0, final_value)
        
        return round(final_value, 4)
    
    async def collect_content_metrics(
        self,
        content_ids: List[str],
        platforms: List[str]
    ) -> Dict[str, List[MetricDataPoint]]:
        """
        Collect metrics for specific content pieces.
        
        Args:
            content_ids: List of content identifiers
            platforms: Platforms to collect from
            
        Returns:
            Dictionary mapping content IDs to their metrics
        """
        
        content_metrics = {}
        
        for content_id in content_ids:
            content_metrics[content_id] = []
            
            for platform in platforms:
                # This would fetch actual content metrics from platform APIs
                # For now, generate synthetic data
                
                metrics = await self._generate_content_metrics(content_id, platform)
                content_metrics[content_id].extend(metrics)
        
        return content_metrics
    
    async def _generate_content_metrics(
        self, content_id: str, platform: str
    ) -> List[MetricDataPoint]:
        """
Generate realistic content-specific metrics."""
        
        metrics = []
        content_metrics = self.platform_metrics.get(platform, [])
        
        # Generate metrics for the content
        for metric_type in content_metrics:
            value = self._generate_realistic_metric_value(
                metric_type, platform, datetime.now()
            )
            
            # Content-specific adjustments
            if metric_type == MetricType.ENGAGEMENT_RATE:
                # Some content performs better
                content_boost = np.random.choice([0.8, 1.0, 1.2, 1.5], p=[0.3, 0.4, 0.2, 0.1])
                value *= content_boost
            
            metric_point = MetricDataPoint(
                timestamp=datetime.now(timezone.utc),
                metric_type=metric_type,
                value=value,
                platform=platform,
                content_id=content_id,
                metadata={
                    'source': f'{platform}_content_api',
                    'collection_method': 'content_specific'
                }
            )
            metrics.append(metric_point)
        
        return metrics


class PerformanceAnalyzer:
    """
    Advanced performance analysis engine that processes metrics and
    generates insights and trends.
    """
    
    def __init__(self):
        """
Initialize the performance analyzer."""
        self.prediction_engine = PerformancePredictionEngine()
        
        # ML models for analysis
        self.trend_analyzer = LinearRegression()
        self.anomaly_detector = KMeans(n_clusters=3)
        self.performance_predictor = RandomForestRegressor(n_estimators=100)
        self.scaler = StandardScaler()
        
        # Analysis parameters
        self.trend_detection_window = 30  # days
        self.anomaly_threshold = 2.0  # standard deviations
        self.forecast_horizon = 30  # days
        
        # Industry benchmarks (would be loaded from database)
        self.industry_benchmarks = self._load_industry_benchmarks()
        
        logger.info("Performance analyzer initialized successfully")
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[MetricType, Dict[str, float]]]:
        """Load industry benchmark data."""
        
        return {
            'instagram': {
                MetricType.ENGAGEMENT_RATE: {
                    'average': 0.045,
                    'top_10_percent': 0.12,
                    'top_25_percent': 0.08
                },
                MetricType.FOLLOWER_GROWTH: {
                    'average': 2.5,  # percent per month
                    'top_10_percent': 8.0,
                    'top_25_percent': 5.0
                }
            },
            'tiktok': {
                MetricType.ENGAGEMENT_RATE: {
                    'average': 0.055,
                    'top_10_percent': 0.15,
                    'top_25_percent': 0.10
                },
                MetricType.COMPLETION_RATE: {
                    'average': 0.65,
                    'top_10_percent': 0.85,
                    'top_25_percent': 0.75
                }
            },
            'youtube': {
                MetricType.ENGAGEMENT_RATE: {
                    'average': 0.035,
                    'top_10_percent': 0.08,
                    'top_25_percent': 0.055
                },
                MetricType.AUDIENCE_RETENTION: {
                    'average': 0.45,
                    'top_10_percent': 0.70,
                    'top_25_percent': 0.60
                }
            }
        }
    
    async def analyze_performance_trends(
        self,
        metrics: List[MetricDataPoint],
        time_frame: TimeFrame = TimeFrame.DAILY
    ) -> List[PerformanceTrend]:
        """
        Analyze performance trends from metric data.
        
        Args:
            metrics: List of metric data points
            time_frame: Time frame for trend analysis
            
        Returns:
            List of performance trends
        """
        
        try:
            trends = []
            
            # Group metrics by type and platform
            grouped_metrics = defaultdict(lambda: defaultdict(list))
            
            for metric in metrics:
                key = (metric.metric_type, metric.platform)
                grouped_metrics[key].append(metric)
            
            # Analyze trends for each metric type/platform combination
            for (metric_type, platform), metric_list in grouped_metrics.items():
                if len(metric_list) < 7:  # Need minimum data points
                    continue
                
                trend = await self._analyze_single_metric_trend(
                    metric_type, platform, metric_list, time_frame
                )
                trends.append(trend)
            
            logger.info(f"Analyzed {len(trends)} performance trends")
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")
            return []
    
    async def _analyze_single_metric_trend(
        self,
        metric_type: MetricType,
        platform: str,
        metrics: List[MetricDataPoint],
        time_frame: TimeFrame
    ) -> PerformanceTrend:
        """Analyze trend for a single metric type."""
        
        # Sort metrics by timestamp
        metrics.sort(key=lambda x: x.timestamp)
        
        # Extract values and timestamps
        values = [m.value for m in metrics]
        timestamps = [m.timestamp.timestamp() for m in metrics]
        
        # Calculate trend direction and growth rate
        if len(values) >= 2:
            # Linear regression for trend
            X = np.array(timestamps).reshape(-1, 1)
            y = np.array(values)
            
            # Normalize timestamps to avoid numerical issues
            X_normalized = (X - X.min()) / (X.max() - X.min()) if X.max() != X.min() else X
            
            self.trend_analyzer.fit(X_normalized, y)
            slope = self.trend_analyzer.coef_[0]
            r2 = self.trend_analyzer.score(X_normalized, y)
            
            # Determine trend direction
            if abs(slope) < np.std(values) * 0.1:
                trend_direction = TrendDirection.STABLE
            elif slope > 0:
                trend_direction = TrendDirection.INCREASING
            else:
                trend_direction = TrendDirection.DECREASING
            
            # Calculate growth rate
            if len(values) > 1:
                start_value = values[0] if values[0] != 0 else 0.01
                end_value = values[-1]
                periods = len(values) - 1
                
                growth_rate = ((end_value / start_value) ** (1/periods) - 1) if periods > 0 else 0
            else:
                growth_rate = 0
            
            # Calculate confidence interval
            prediction = self.trend_analyzer.predict(X_normalized)
            residuals = y - prediction
            std_error = np.std(residuals)
            confidence_interval = (
                prediction[-1] - 1.96 * std_error,
                prediction[-1] + 1.96 * std_error
            )
            
            trend_strength = min(1.0, r2)
        else:
            trend_direction = TrendDirection.STABLE
            growth_rate = 0
            confidence_interval = (values[0], values[0])
            trend_strength = 0
        
        # Detect seasonality (simplified)
        seasonality_detected = self._detect_seasonality(values)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(metrics, values)
        
        # Generate forecast
        forecast = self._generate_forecast(metrics, metric_type)
        
        return PerformanceTrend(
            metric_type=metric_type,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            confidence_interval=confidence_interval,
            trend_strength=trend_strength,
            seasonality_detected=seasonality_detected,
            anomalies=anomalies,
            forecast=forecast
        )
    
    def _detect_seasonality(self, values: List[float]) -> bool:
        """
Detect if there's seasonality in the data."""
        
        if len(values) < 14:  # Need at least 2 weeks
            return False
        
        # Simple seasonality detection using autocorrelation
        # Check for weekly patterns (7-day cycle)
        if len(values) >= 14:
            weekly_correlation = np.corrcoef(values[:-7], values[7:])[0, 1]
            return abs(weekly_correlation) > 0.3
        
        return False
    
    def _detect_anomalies(
        self, metrics: List[MetricDataPoint], values: List[float]
    ) -> List[Dict[str, Any]]:
        """
Detect anomalous data points."""
        
        anomalies = []
        
        if len(values) < 5:
            return anomalies
        
        # Calculate rolling statistics
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        # Detect outliers using z-score
        for i, (metric, value) in enumerate(zip(metrics, values)):
            z_score = abs(value - mean_value) / std_value if std_value > 0 else 0
            
            if z_score > self.anomaly_threshold:
                anomaly_type = "spike" if value > mean_value else "drop"
                
                anomalies.append({
                    'timestamp': metric.timestamp,
                    'value': value,
                    'expected_value': mean_value,
                    'deviation': z_score,
                    'type': anomaly_type,
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    def _generate_forecast(
        self, metrics: List[MetricDataPoint], metric_type: MetricType
    ) -> List[Dict[str, Any]]:
        """Generate forecast for metric values."""
        
        forecast = []
        
        if len(metrics) < 7:
            return forecast
        
        values = [m.value for m in metrics]
        
        # Simple trend-based forecast
        recent_trend = np.mean(np.diff(values[-7:]))  # Last week's trend
        last_value = values[-1]
        
        for i in range(1, self.forecast_horizon + 1):
            forecasted_value = max(0, last_value + recent_trend * i)
            
            forecast_point = {
                'days_ahead': i,
                'forecasted_value': forecasted_value,
                'confidence': max(0.1, 1.0 - i * 0.02),  # Decreasing confidence
                'lower_bound': forecasted_value * 0.8,
                'upper_bound': forecasted_value * 1.2
            }
            forecast.append(forecast_point)
        
        return forecast[:10]  # Return only next 10 days
    
    async def analyze_content_performance(
        self,
        content_metrics: Dict[str, List[MetricDataPoint]]
    ) -> List[ContentPerformanceMetrics]:
        """
        Analyze performance of individual content pieces.
        
        Args:
            content_metrics: Dictionary mapping content IDs to their metrics
            
        Returns:
            List of content performance analyses
        """
        
        try:
            content_performances = []
            
            for content_id, metrics in content_metrics.items():
                if not metrics:
                    continue
                
                performance = await self._analyze_single_content_performance(
                    content_id, metrics
                )
                content_performances.append(performance)
            
            # Rank content by performance
            content_performances.sort(
                key=lambda x: x.performance_score, reverse=True
            )
            
            # Calculate percentiles
            for i, content in enumerate(content_performances):
                content.ranking_percentile = (
                    (len(content_performances) - i) / len(content_performances) * 100
                )
            
            return content_performances
            
        except Exception as e:
            logger.error(f"Failed to analyze content performance: {e}")
            return []
    
    async def _analyze_single_content_performance(
        self, content_id: str, metrics: List[MetricDataPoint]
    ) -> ContentPerformanceMetrics:
        """Analyze performance of a single content piece."""
        
        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for metric in metrics:
            metrics_by_type[metric.metric_type].append(metric.value)
        
        # Calculate aggregate metrics
        aggregated_metrics = {}
        for metric_type, values in metrics_by_type.items():
            if values:
                aggregated_metrics[metric_type] = np.mean(values)
        
        # Calculate engagement rate
        engagement_rate = aggregated_metrics.get(MetricType.ENGAGEMENT_RATE, 0)
        
        # Calculate reach
        reach = int(aggregated_metrics.get(MetricType.REACH, 0))
        
        # Calculate performance score
        performance_score = self._calculate_content_performance_score(aggregated_metrics)
        
        # Identify best performing aspects
        best_aspects = self._identify_best_performing_aspects(aggregated_metrics)
        
        # Identify improvement opportunities
        improvements = self._identify_improvement_opportunities(aggregated_metrics)
        
        # Get content metadata
        platform = metrics[0].platform if metrics else "unknown"
        content_type = "post"  # Would be determined from content data
        
        return ContentPerformanceMetrics(
            content_id=content_id,
            content_type=content_type,
            platform=platform,
            publish_date=metrics[0].timestamp if metrics else datetime.now(timezone.utc),
            metrics=aggregated_metrics,
            engagement_rate=engagement_rate,
            reach=reach,
            performance_score=performance_score,
            ranking_percentile=0,  # Will be calculated later
            best_performing_aspects=best_aspects,
            improvement_opportunities=improvements
        )
    
    def _calculate_content_performance_score(
        self, metrics: Dict[MetricType, float]
    ) -> float:
        """Calculate overall performance score for content."""
        
        # Weighted scoring based on metric importance
        weights = {
            MetricType.ENGAGEMENT_RATE: 0.3,
            MetricType.REACH: 0.2,
            MetricType.COMPLETION_RATE: 0.2,
            MetricType.SHARES: 0.15,
            MetricType.SAVES: 0.15
        }
        
        total_score = 0
        total_weight = 0
        
        for metric_type, weight in weights.items():
            if metric_type in metrics:
                # Normalize metrics to 0-1 scale
                normalized_value = self._normalize_metric_value(
                    metric_type, metrics[metric_type]
                )
                total_score += normalized_value * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _normalize_metric_value(self, metric_type: MetricType, value: float) -> float:
        """
Normalize metric value to 0-1 scale."""
        
        # Normalization ranges based on typical values
        normalization_ranges = {
            MetricType.ENGAGEMENT_RATE: (0, 0.2),
            MetricType.COMPLETION_RATE: (0, 1),
            MetricType.REACH: (0, 100000),
            MetricType.VIEWS: (0, 100000),
            MetricType.LIKES: (0, 5000),
            MetricType.COMMENTS: (0, 500),
            MetricType.SHARES: (0, 1000)
        }
        
        min_val, max_val = normalization_ranges.get(metric_type, (0, 1))
        
        if max_val == min_val:
            return 1.0
        
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(1, normalized))
    
    def _identify_best_performing_aspects(
        self, metrics: Dict[MetricType, float]
    ) -> List[str]:
        """
Identify the best performing aspects of content."""
        
        best_aspects = []
        
        # Check for high engagement
        engagement_rate = metrics.get(MetricType.ENGAGEMENT_RATE, 0)
        if engagement_rate > 0.08:
            best_aspects.append("High engagement rate")
        
        # Check for high completion rate
        completion_rate = metrics.get(MetricType.COMPLETION_RATE, 0)
        if completion_rate > 0.8:
            best_aspects.append("Excellent viewer retention")
        
        # Check for high share rate
        shares = metrics.get(MetricType.SHARES, 0)
        likes = metrics.get(MetricType.LIKES, 1)
        share_rate = shares / likes if likes > 0 else 0
        
        if share_rate > 0.1:
            best_aspects.append("High shareability")
        
        # Check for high save rate
        saves = metrics.get(MetricType.SAVES, 0)
        save_rate = saves / likes if likes > 0 else 0
        
        if save_rate > 0.05:
            best_aspects.append("High save rate")
        
        return best_aspects
    
    def _identify_improvement_opportunities(
        self, metrics: Dict[MetricType, float]
    ) -> List[str]:
        """Identify improvement opportunities for content."""
        
        opportunities = []
        
        # Low engagement opportunities
        engagement_rate = metrics.get(MetricType.ENGAGEMENT_RATE, 0)
        if engagement_rate < 0.03:
            opportunities.append("Improve content engagement through better hooks")
        
        # Low completion rate
        completion_rate = metrics.get(MetricType.COMPLETION_RATE, 0)
        if completion_rate < 0.5:
            opportunities.append("Improve content pacing to increase retention")
        
        # Low reach
        reach = metrics.get(MetricType.REACH, 0)
        impressions = metrics.get(MetricType.IMPRESSIONS, reach)
        reach_rate = reach / impressions if impressions > 0 else 0
        
        if reach_rate < 0.1:
            opportunities.append("Optimize content for better algorithm performance")
        
        # Low interaction diversity
        comments = metrics.get(MetricType.COMMENTS, 0)
        likes = metrics.get(MetricType.LIKES, 1)
        comment_rate = comments / likes if likes > 0 else 0
        
        if comment_rate < 0.02:
            opportunities.append("Encourage more comments with questions and CTAs")
        
        return opportunities
    
    async def generate_benchmarks(
        self,
        creator_metrics: List[MetricDataPoint],
        platforms: List[str]
    ) -> List[PerformanceBenchmark]:
        """
        Generate performance benchmarks comparing creator to industry standards.
        
        Args:
            creator_metrics: Creator's performance metrics
            platforms: Platforms to benchmark against
            
        Returns:
            List of performance benchmarks
        """
        
        benchmarks = []
        
        # Group metrics by platform and type
        platform_metrics = defaultdict(lambda: defaultdict(list))
        
        for metric in creator_metrics:
            platform_metrics[metric.platform][metric.metric_type].append(metric.value)
        
        # Generate benchmarks for each platform and metric
        for platform in platforms:
            platform_benchmarks = self.industry_benchmarks.get(platform, {})
            
            for metric_type, values in platform_metrics[platform].items():
                if not values or metric_type not in platform_benchmarks:
                    continue
                
                creator_value = np.mean(values)
                industry_data = platform_benchmarks[metric_type]
                
                benchmark = self._create_benchmark(
                    metric_type, creator_value, industry_data, platform
                )
                benchmarks.append(benchmark)
        
        return benchmarks
    
    def _create_benchmark(
        self,
        metric_type: MetricType,
        creator_value: float,
        industry_data: Dict[str, float],
        platform: str
    ) -> PerformanceBenchmark:
        """
Create a performance benchmark."""
        
        industry_average = industry_data.get('average', 0)
        top_10_threshold = industry_data.get('top_10_percent', 0)
        top_25_threshold = industry_data.get('top_25_percent', 0)
        
        # Calculate percentile
        if creator_value >= top_10_threshold:
            percentile = 95
        elif creator_value >= top_25_threshold:
            percentile = 80
        elif creator_value >= industry_average:
            percentile = 60
        else:
            percentile = max(10, (creator_value / industry_average) * 50)
        
        # Calculate improvement potential
        improvement_potential = max(0, top_10_threshold - creator_value) / top_10_threshold
        
        # Determine benchmark category
        if percentile >= 90:
            category = "Top Performer"
        elif percentile >= 75:
            category = "Above Average"
        elif percentile >= 50:
            category = "Average"
        else:
            category = "Below Average"
        
        return PerformanceBenchmark(
            metric_type=metric_type,
            creator_value=creator_value,
            industry_average=industry_average,
            industry_percentile=percentile,
            top_10_percent_threshold=top_10_threshold,
            improvement_potential=improvement_potential,
            benchmark_category=category
        )


class PerformanceTracker:
    """
    Master performance tracking system that coordinates metrics collection,
    analysis, and reporting for content creators.
    """
    
    def __init__(self):
        """
Initialize the performance tracker."""
        self.metrics_collector = MetricsCollector()
        self.performance_analyzer = PerformanceAnalyzer()
        
        logger.info("Performance tracker initialized successfully")
    
    async def generate_performance_report(
        self,
        creator_id: str,
        platforms: List[str],
        time_period: Dict[str, datetime],
        include_benchmarks: bool = True,
        include_forecasts: bool = True
    ) -> PerformanceReport:
        """
        Generate comprehensive performance report for a creator.
        
        Args:
            creator_id: Creator identifier
            platforms: Platforms to include in report
            time_period: Dictionary with 'start_date' and 'end_date'
            include_benchmarks: Whether to include industry benchmarks
            include_forecasts: Whether to include performance forecasts
            
        Returns:
            Comprehensive performance report
        """
        
        try:
            start_date = time_period['start_date']
            end_date = time_period['end_date']
            
            # Collect metrics
            metrics = await self.metrics_collector.collect_platform_metrics(
                creator_id, platforms, start_date, end_date
            )
            
            # Analyze trends
            trends = await self.performance_analyzer.analyze_performance_trends(
                metrics, TimeFrame.DAILY
            )
            
            # Generate platform performances
            platform_performances = await self._generate_platform_performances(
                platforms, metrics, trends
            )
            
            # Collect and analyze content performance
            content_performances = await self._analyze_content_performance(
                creator_id, platforms, start_date, end_date
            )
            
            # Generate benchmarks
            benchmarks = []
            if include_benchmarks:
                benchmarks = await self.performance_analyzer.generate_benchmarks(
                    metrics, platforms
                )
            
            # Generate insights
            insights = await self._generate_performance_insights(
                metrics, trends, benchmarks, content_performances
            )
            
            # Calculate overall performance score
            overall_score = self._calculate_overall_performance_score(
                platform_performances, benchmarks
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                insights, trends, benchmarks
            )
            
            # Calculate goals progress (placeholder)
            goals_progress = {
                'follower_growth': 0.75,
                'engagement_improvement': 0.60,
                'reach_expansion': 0.80
            }
            
            report = PerformanceReport(
                report_id=f"report_{creator_id}_{int(datetime.now().timestamp())}",
                creator_id=creator_id,
                report_period=time_period,
                overall_performance_score=overall_score,
                platform_performances=platform_performances,
                content_performances=content_performances,
                performance_trends=trends,
                benchmarks=benchmarks,
                insights=insights,
                recommendations=recommendations,
                goals_progress=goals_progress,
                generated_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"Performance report generated for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise
    
    async def _generate_platform_performances(
        self,
        platforms: List[str],
        metrics: List[MetricDataPoint],
        trends: List[PerformanceTrend]
    ) -> List[PlatformPerformance]:
        """Generate platform-specific performance summaries."""
        
        platform_performances = []
        
        for platform in platforms:
            platform_metrics = [m for m in metrics if m.platform == platform]
            platform_trends = [t for t in trends if any(
                m.platform == platform for m in metrics 
                if m.metric_type == t.metric_type
            )]
            
            if not platform_metrics:
                continue
            
            # Calculate aggregated metrics
            engagement_rates = [
                m.value for m in platform_metrics 
                if m.metric_type == MetricType.ENGAGEMENT_RATE
            ]
            avg_engagement = np.mean(engagement_rates) if engagement_rates else 0
            
            reach_values = [
                m.value for m in platform_metrics 
                if m.metric_type == MetricType.REACH
            ]
            total_reach = int(np.sum(reach_values)) if reach_values else 0
            
            # Calculate follower growth
            follower_growth_values = [
                m.value for m in platform_metrics 
                if m.metric_type == MetricType.FOLLOWER_GROWTH
            ]
            follower_growth_rate = np.mean(follower_growth_values) if follower_growth_values else 0
            
            # Generate optimization recommendations
            optimization_recs = self._generate_platform_optimization_recommendations(
                platform, platform_metrics, platform_trends
            )
            
            performance = PlatformPerformance(
                platform=platform,
                time_period=TimeFrame.MONTHLY,
                total_content=len(set(m.content_id for m in platform_metrics if m.content_id)),
                avg_engagement_rate=avg_engagement,
                total_reach=total_reach,
                total_followers=50000,  # Placeholder
                follower_growth_rate=follower_growth_rate,
                top_performing_content=[],  # Would be populated with actual content IDs
                performance_trends=platform_trends,
                competitive_position={'rank': 'Top 25%'},  # Placeholder
                optimization_recommendations=optimization_recs
            )
            
            platform_performances.append(performance)
        
        return platform_performances
    
    def _generate_platform_optimization_recommendations(
        self,
        platform: str,
        metrics: List[MetricDataPoint],
        trends: List[PerformanceTrend]
    ) -> List[str]:
        """
Generate platform-specific optimization recommendations."""
        
        recommendations = []
        
        # Analyze engagement trends
        engagement_trends = [
            t for t in trends 
            if t.metric_type == MetricType.ENGAGEMENT_RATE
        ]
        
        if engagement_trends:
            trend = engagement_trends[0]
            if trend.trend_direction == TrendDirection.DECREASING:
                recommendations.append(f"Address declining engagement on {platform}")
            elif trend.growth_rate > 0.1:
                recommendations.append(f"Scale successful strategies on {platform}")
        
        # Platform-specific recommendations
        if platform == 'tiktok':
            recommendations.extend([
                "Leverage trending audio and hashtags",
                "Focus on hook optimization in first 3 seconds",
                "Experiment with different posting times"
            ])
        elif platform == 'instagram':
            recommendations.extend([
                "Optimize Stories and Reels content mix",
                "Improve caption engagement strategies",
                "Utilize Instagram Shopping features"
            ])
        elif platform == 'youtube':
            recommendations.extend([
                "Optimize thumbnails and titles for CTR",
                "Focus on audience retention improvements",
                "Develop consistent upload schedule"
            ])
        
        return recommendations
    
    async def _analyze_content_performance(
        self,
        creator_id: str,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentPerformanceMetrics]:
        """Analyze individual content performance."""
        
        # Get content IDs for the period (would come from content database)
        content_ids = [f"content_{i}" for i in range(1, 21)]  # Sample 20 pieces
        
        # Collect content-specific metrics
        content_metrics = await self.metrics_collector.collect_content_metrics(
            content_ids, platforms
        )
        
        # Analyze performance
        content_performances = await self.performance_analyzer.analyze_content_performance(
            content_metrics
        )
        
        return content_performances
    
    async def _generate_performance_insights(
        self,
        metrics: List[MetricDataPoint],
        trends: List[PerformanceTrend],
        benchmarks: List[PerformanceBenchmark],
        content_performances: List[ContentPerformanceMetrics]
    ) -> List[PerformanceInsight]:
        """Generate actionable performance insights."""
        
        insights = []
        
        # Trend-based insights
        for trend in trends:
            if trend.trend_direction == TrendDirection.INCREASING and trend.growth_rate > 0.1:
                insight = PerformanceInsight(
                    insight_id=f"trend_insight_{int(datetime.now().timestamp())}",
                    insight_type="positive_trend",
                    title=f"Strong Growth in {trend.metric_type.value}",
                    description=f"Your {trend.metric_type.value} is showing strong upward trend",
                    key_findings=[
                        f"Growth rate: {trend.growth_rate:.1%}",
                        f"Trend strength: {trend.trend_strength:.2f}",
                        f"Forecast shows continued growth"
                    ],
                    actionable_recommendations=[
                        "Continue current successful strategies",
                        "Scale content production in high-performing areas",
                        "Document successful tactics for replication"
                    ],
                    expected_impact="High",
                    confidence_score=trend.trend_strength,
                    priority_level="High",
                    supporting_data={
                        'trend_data': trend.forecast[:5],
                        'growth_rate': trend.growth_rate
                    },
                    generated_at=datetime.now(timezone.utc)
                )
                insights.append(insight)
        
        # Benchmark-based insights
        underperforming_metrics = [
            b for b in benchmarks 
            if b.industry_percentile < 50 and b.improvement_potential > 0.2
        ]
        
        if underperforming_metrics:
            metric = underperforming_metrics[0]  # Focus on worst performing
            
            insight = PerformanceInsight(
                insight_id=f"benchmark_insight_{int(datetime.now().timestamp())}",
                insight_type="improvement_opportunity",
                title=f"Opportunity to Improve {metric.metric_type.value}",
                description=f"Your {metric.metric_type.value} is below industry average",
                key_findings=[
                    f"Current value: {metric.creator_value:.3f}",
                    f"Industry average: {metric.industry_average:.3f}",
                    f"Top 10% threshold: {metric.top_10_percent_threshold:.3f}"
                ],
                actionable_recommendations=[
                    f"Focus on improving {metric.metric_type.value}",
                    "Study top performers in your niche",
                    "A/B test different content strategies"
                ],
                expected_impact="Medium",
                confidence_score=0.8,
                priority_level="Medium",
                supporting_data={
                    'benchmark_data': {
                        'current': metric.creator_value,
                        'target': metric.top_10_percent_threshold
                    }
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        # Content performance insights
        if content_performances:
            top_content = content_performances[0]
            
            insight = PerformanceInsight(
                insight_id=f"content_insight_{int(datetime.now().timestamp())}",
                insight_type="content_analysis",
                title="Top Performing Content Analysis",
                description="Analysis of your best performing content",
                key_findings=[
                    f"Top content achieved {top_content.performance_score:.2f} performance score",
                    f"Best aspects: {', '.join(top_content.best_performing_aspects)}",
                    f"Engagement rate: {top_content.engagement_rate:.3f}"
                ],
                actionable_recommendations=[
                    "Replicate successful elements in future content",
                    "Create content series based on top performers",
                    "Analyze timing and format of best content"
                ],
                expected_impact="High",
                confidence_score=0.9,
                priority_level="High",
                supporting_data={
                    'top_content_id': top_content.content_id,
                    'performance_score': top_content.performance_score
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_overall_performance_score(
        self,
        platform_performances: List[PlatformPerformance],
        benchmarks: List[PerformanceBenchmark]
    ) -> float:
        """Calculate overall performance score."""
        
        if not platform_performances and not benchmarks:
            return 0.5
        
        scores = []
        
        # Platform-based scoring
        for platform in platform_performances:
            # Simple scoring based on engagement rate
            platform_score = min(1.0, platform.avg_engagement_rate / 0.1)  # Normalize to 10%
            scores.append(platform_score)
        
        # Benchmark-based scoring
        for benchmark in benchmarks:
            percentile_score = benchmark.industry_percentile / 100
            scores.append(percentile_score)
        
        return np.mean(scores) if scores else 0.5
    
    def _generate_recommendations(
        self,
        insights: List[PerformanceInsight],
        trends: List[PerformanceTrend],
        benchmarks: List[PerformanceBenchmark]
    ) -> List[str]:
        """
Generate high-level recommendations."""
        
        recommendations = []
        
        # Extract recommendations from insights
        for insight in insights:
            if insight.priority_level == "High":
                recommendations.extend(insight.actionable_recommendations[:2])
        
        # Add trend-based recommendations
        declining_trends = [
            t for t in trends 
            if t.trend_direction == TrendDirection.DECREASING
        ]
        if declining_trends:
            recommendations.append("Address declining performance metrics")
        
        # Add benchmark-based recommendations
        below_average_metrics = [
            b for b in benchmarks 
            if b.industry_percentile < 50
        ]
        if below_average_metrics:
            recommendations.append("Focus on improving below-average metrics")
        
        # Remove duplicates and limit to top 5
        recommendations = list(set(recommendations))[:5]
        
        return recommendations
