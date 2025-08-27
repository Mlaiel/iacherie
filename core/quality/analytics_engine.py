"""
Quality Analytics Engine - Enterprise Quality Intelligence & Insights System

Advanced analytics engine for quality data processing, trend analysis, 
predictive insights, and comprehensive quality intelligence reporting.

Business Logic:
Quality data collection → Statistical analysis → Trend detection →
Predictive modeling → Insights generation → Performance optimization

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import statistics
import math
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirection(Enum):
    """Trend direction indicators"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class AnalyticsMetricType(Enum):
    """Types of analytics metrics"""
    QUALITY_SCORE = "quality_score"
    VALIDATION_ERRORS = "validation_errors"
    PERFORMANCE_METRICS = "performance_metrics"
    COMPLIANCE_SCORE = "compliance_score"
    SEO_SCORE = "seo_score"
    SECURITY_SCORE = "security_score"
    MONETIZATION_SCORE = "monetization_score"
    PLATFORM_PERFORMANCE = "platform_performance"
    CONTENT_ENGAGEMENT = "content_engagement"
    PROCESSING_TIME = "processing_time"


class InsightType(Enum):
    """Types of quality insights"""
    TREND = "trend"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"
    PREDICTION = "prediction"
    COMPARISON = "comparison"
    ALERT = "alert"


class InsightPriority(Enum):
    """Insight priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityMetricPoint:
    """Individual quality metric data point"""
    metric_id: str
    metric_type: AnalyticsMetricType
    value: float
    timestamp: datetime
    
    # Context information
    content_id: Optional[str] = None
    platform: Optional[str] = None
    category: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'content_id': self.content_id,
            'platform': self.platform,
            'category': self.category,
            'metadata': self.metadata
        }


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_type: AnalyticsMetricType
    timeframe: AnalyticsTimeframe
    direction: TrendDirection
    strength: float  # 0.0-1.0
    
    # Statistical data
    current_value: float
    previous_value: float
    change_percentage: float
    confidence: float  # 0.0-1.0
    
    # Trend details
    data_points: int
    time_period: str
    slope: float  # Rate of change
    correlation: float  # R-squared value
    
    # Context
    description: str = ""
    significance: str = "medium"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_type': self.metric_type.value,
            'timeframe': self.timeframe.value,
            'direction': self.direction.value,
            'strength': self.strength,
            'statistics': {
                'current_value': self.current_value,
                'previous_value': self.previous_value,
                'change_percentage': self.change_percentage,
                'confidence': self.confidence
            },
            'trend_details': {
                'data_points': self.data_points,
                'time_period': self.time_period,
                'slope': self.slope,
                'correlation': self.correlation
            },
            'context': {
                'description': self.description,
                'significance': self.significance
            }
        }


@dataclass
class QualityInsight:
    """Quality insight generated from analytics"""
    insight_id: str
    insight_type: InsightType
    priority: InsightPriority
    title: str
    description: str
    
    # Impact assessment
    impact_score: float  # 0-100
    confidence: float  # 0.0-1.0
    urgency: str = "medium"  # low, medium, high
    
    # Supporting data
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    affected_metrics: List[AnalyticsMetricType] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    
    # Context
    timeframe: Optional[AnalyticsTimeframe] = None
    affected_platforms: List[str] = field(default_factory=list)
    affected_categories: List[str] = field(default_factory=list)
    
    # Metadata
    generation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'insight_id': self.insight_id,
            'insight_type': self.insight_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'description': self.description,
            'impact': {
                'score': self.impact_score,
                'confidence': self.confidence,
                'urgency': self.urgency
            },
            'supporting_data': self.supporting_data,
            'affected_metrics': [metric.value for metric in self.affected_metrics],
            'recommendations': self.recommendations,
            'action_items': self.action_items,
            'context': {
                'timeframe': self.timeframe.value if self.timeframe else None,
                'affected_platforms': self.affected_platforms,
                'affected_categories': self.affected_categories
            },
            'generation_timestamp': self.generation_timestamp.isoformat()
        }


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    timeframe: AnalyticsTimeframe
    start_date: datetime
    end_date: datetime
    
    # Summary statistics
    total_content_analyzed: int = 0
    average_quality_score: float = 0.0
    total_issues_found: int = 0
    total_optimizations_identified: int = 0
    
    # Trend analyses
    trends: List[TrendAnalysis] = field(default_factory=list)
    
    # Insights and recommendations
    insights: List[QualityInsight] = field(default_factory=list)
    
    # Performance metrics
    platform_performance: Dict[str, float] = field(default_factory=dict)
    category_performance: Dict[str, float] = field(default_factory=dict)
    
    # Quality breakdown
    quality_distribution: Dict[str, int] = field(default_factory=dict)
    issue_categories: Dict[str, int] = field(default_factory=dict)
    
    # Processing statistics
    processing_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Report metadata
    generation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
    
    def add_trend(self, trend: TrendAnalysis):
        """Add trend analysis to report"""
        self.trends.append(trend)
    
    def add_insight(self, insight: QualityInsight):
        """Add insight to report"""
        self.insights.append(insight)
    
    def get_critical_insights(self) -> List[QualityInsight]:
        """Get critical priority insights"""
        return [insight for insight in self.insights 
                if insight.priority == InsightPriority.CRITICAL]
    
    def get_insights_by_type(self, insight_type: InsightType) -> List[QualityInsight]:
        """Get insights by type"""
        return [insight for insight in self.insights 
                if insight.insight_type == insight_type]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'timeframe': self.timeframe.value,
            'period': {
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat()
            },
            'summary': {
                'total_content_analyzed': self.total_content_analyzed,
                'average_quality_score': self.average_quality_score,
                'total_issues_found': self.total_issues_found,
                'total_optimizations_identified': self.total_optimizations_identified
            },
            'trends': [trend.to_dict() for trend in self.trends],
            'insights': [insight.to_dict() for insight in self.insights],
            'performance': {
                'platform_performance': self.platform_performance,
                'category_performance': self.category_performance
            },
            'quality_breakdown': {
                'quality_distribution': self.quality_distribution,
                'issue_categories': self.issue_categories
            },
            'processing_statistics': self.processing_statistics,
            'metadata': {
                'generation_timestamp': self.generation_timestamp.isoformat(),
                'processing_time_ms': self.processing_time_ms
            }
        }


class StatisticalAnalyzer:
    """Statistical analysis for quality metrics"""
    
    def __init__(self):
        self.significance_threshold = 0.05
        self.confidence_level = 0.95
    
    def calculate_descriptive_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate descriptive statistics for a dataset"""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(values)
        
        stats = {
            'count': n,
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'mode': statistics.mode(values) if n > 1 else values[0],
            'std_dev': statistics.stdev(values) if n > 1 else 0.0,
            'variance': statistics.variance(values) if n > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }
        
        # Percentiles
        stats.update({
            'q1': self._percentile(sorted_values, 25),
            'q3': self._percentile(sorted_values, 75),
            'p90': self._percentile(sorted_values, 90),
            'p95': self._percentile(sorted_values, 95),
            'p99': self._percentile(sorted_values, 99)
        })
        
        # IQR and outlier detection
        stats['iqr'] = stats['q3'] - stats['q1']
        stats['outlier_threshold_low'] = stats['q1'] - 1.5 * stats['iqr']
        stats['outlier_threshold_high'] = stats['q3'] + 1.5 * stats['iqr']
        
        return stats
    
    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not sorted_values:
            return 0.0
        
        k = (len(sorted_values) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        
        if f == c:
            return sorted_values[int(k)]
        
        d0 = sorted_values[int(f)] * (c - k)
        d1 = sorted_values[int(c)] * (k - f)
        
        return d0 + d1
    
    def detect_outliers(self, values: List[float]) -> Tuple[List[float], List[int]]:
        """Detect outliers using IQR method"""
        if len(values) < 4:
            return [], []
        
        stats = self.calculate_descriptive_statistics(values)
        low_threshold = stats['outlier_threshold_low']
        high_threshold = stats['outlier_threshold_high']
        
        outliers = []
        outlier_indices = []
        
        for i, value in enumerate(values):
            if value < low_threshold or value > high_threshold:
                outliers.append(value)
                outlier_indices.append(i)
        
        return outliers, outlier_indices
    
    def calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        try:
            return statistics.correlation(x_values, y_values)
        except statistics.StatisticsError:
            return 0.0
    
    def linear_regression(self, x_values: List[float], y_values: List[float]) -> Tuple[float, float, float]:
        """Calculate linear regression slope, intercept, and R-squared"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0, 0.0, 0.0
        
        n = len(x_values)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        
        # Calculate slope
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0, y_mean, 0.0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        ss_res = sum((y_values[i] - (slope * x_values[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y_values[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        return slope, intercept, r_squared
    
    def detect_trend(self, values: List[float], timestamps: List[datetime]) -> TrendDirection:
        """Detect trend direction in time series data"""
        if len(values) < 3:
            return TrendDirection.STABLE
        
        # Convert timestamps to numeric values for regression
        base_time = timestamps[0]
        x_values = [(ts - base_time).total_seconds() for ts in timestamps]
        
        slope, _, r_squared = self.linear_regression(x_values, values)
        
        # Determine trend based on slope and correlation strength
        if r_squared < 0.3:  # Low correlation indicates volatility
            return TrendDirection.VOLATILE
        elif slope > 0.1:  # Positive trend
            return TrendDirection.RISING
        elif slope < -0.1:  # Negative trend
            return TrendDirection.FALLING
        else:  # Stable trend
            return TrendDirection.STABLE


class TrendDetector:
    """Trend detection and analysis system"""
    
    def __init__(self):
        self.statistical_analyzer = StatisticalAnalyzer()
        self.min_data_points = 5
    
    def analyze_metric_trends(self, metric_points: List[QualityMetricPoint],
                            timeframe: AnalyticsTimeframe) -> List[TrendAnalysis]:
        """Analyze trends for quality metrics"""
        trends = []
        
        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for point in metric_points:
            metrics_by_type[point.metric_type].append(point)
        
        # Analyze each metric type
        for metric_type, points in metrics_by_type.items():
            if len(points) < self.min_data_points:
                continue
            
            # Sort by timestamp
            points.sort(key=lambda p: p.timestamp)
            
            trend = self._analyze_single_metric_trend(points, metric_type, timeframe)
            if trend:
                trends.append(trend)
        
        return trends
    
    def _analyze_single_metric_trend(self, points: List[QualityMetricPoint],
                                   metric_type: AnalyticsMetricType,
                                   timeframe: AnalyticsTimeframe) -> Optional[TrendAnalysis]:
        """Analyze trend for a single metric type"""
        if len(points) < self.min_data_points:
            return None
        
        values = [point.value for point in points]
        timestamps = [point.timestamp for point in points]
        
        # Detect trend direction
        direction = self.statistical_analyzer.detect_trend(values, timestamps)
        
        # Calculate trend statistics
        current_value = values[-1]
        previous_value = values[-2] if len(values) > 1 else current_value
        
        change_percentage = 0.0
        if previous_value != 0:
            change_percentage = ((current_value - previous_value) / previous_value) * 100
        
        # Calculate slope and correlation
        base_time = timestamps[0]
        x_values = [(ts - base_time).total_seconds() for ts in timestamps]
        slope, _, correlation = self.statistical_analyzer.linear_regression(x_values, values)
        
        # Calculate trend strength
        strength = min(1.0, abs(correlation))
        
        # Calculate confidence based on data quality
        confidence = self._calculate_trend_confidence(values, correlation, len(points))
        
        # Generate description
        description = self._generate_trend_description(
            metric_type, direction, change_percentage, timeframe
        )
        
        # Determine significance
        significance = self._determine_trend_significance(
            abs(change_percentage), correlation, len(points)
        )
        
        return TrendAnalysis(
            metric_type=metric_type,
            timeframe=timeframe,
            direction=direction,
            strength=strength,
            current_value=current_value,
            previous_value=previous_value,
            change_percentage=change_percentage,
            confidence=confidence,
            data_points=len(points),
            time_period=f"{timestamps[0].strftime('%Y-%m-%d')} to {timestamps[-1].strftime('%Y-%m-%d')}",
            slope=slope,
            correlation=correlation,
            description=description,
            significance=significance
        )
    
    def _calculate_trend_confidence(self, values: List[float], 
                                  correlation: float, data_points: int) -> float:
        """Calculate confidence in trend analysis"""
        # Base confidence on correlation strength
        correlation_confidence = abs(correlation)
        
        # Boost confidence with more data points
        data_confidence = min(1.0, data_points / 20.0)  # Max confidence at 20+ points
        
        # Reduce confidence if data is too variable
        if len(values) > 1:
            cv = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 1.0
            variability_penalty = max(0.0, 1.0 - cv)
        else:
            variability_penalty = 0.5
        
        # Combine factors
        confidence = (correlation_confidence * 0.5 + data_confidence * 0.3 + variability_penalty * 0.2)
        
        return min(1.0, max(0.0, confidence))
    
    def _generate_trend_description(self, metric_type: AnalyticsMetricType,
                                  direction: TrendDirection,
                                  change_percentage: float,
                                  timeframe: AnalyticsTimeframe) -> str:
        """Generate human-readable trend description"""
        metric_name = metric_type.value.replace('_', ' ').title()
        timeframe_name = timeframe.value
        
        if direction == TrendDirection.RISING:
            return f"{metric_name} is trending upward with a {abs(change_percentage):.1f}% increase over the {timeframe_name} period"
        elif direction == TrendDirection.FALLING:
            return f"{metric_name} is trending downward with a {abs(change_percentage):.1f}% decrease over the {timeframe_name} period"
        elif direction == TrendDirection.VOLATILE:
            return f"{metric_name} shows high volatility with fluctuating values over the {timeframe_name} period"
        else:
            return f"{metric_name} remains stable with minimal change over the {timeframe_name} period"
    
    def _determine_trend_significance(self, change_percentage: float,
                                    correlation: float, data_points: int) -> str:
        """Determine trend significance level"""
        # Strong correlation and significant change
        if abs(correlation) > 0.7 and change_percentage > 20:
            return "high"
        # Moderate correlation or change
        elif abs(correlation) > 0.5 or change_percentage > 10:
            return "medium"
        # Weak trend
        else:
            return "low"


class InsightGenerator:
    """Quality insight generation system"""
    
    def __init__(self):
        self.trend_detector = TrendDetector()
        self.statistical_analyzer = StatisticalAnalyzer()
    
    def generate_insights(self, metric_points: List[QualityMetricPoint],
                         trends: List[TrendAnalysis],
                         timeframe: AnalyticsTimeframe) -> List[QualityInsight]:
        """Generate quality insights from analytics data"""
        insights = []
        
        # Generate trend-based insights
        insights.extend(self._generate_trend_insights(trends))
        
        # Generate anomaly insights
        insights.extend(self._generate_anomaly_insights(metric_points))
        
        # Generate performance insights
        insights.extend(self._generate_performance_insights(metric_points))
        
        # Generate predictive insights
        insights.extend(self._generate_predictive_insights(trends, timeframe))
        
        # Generate comparison insights
        insights.extend(self._generate_comparison_insights(metric_points))
        
        return insights
    
    def _generate_trend_insights(self, trends: List[TrendAnalysis]) -> List[QualityInsight]:
        """Generate insights from trend analysis"""
        insights = []
        
        for trend in trends:
            if trend.significance == "high" and trend.confidence > 0.7:
                insight = self._create_trend_insight(trend)
                insights.append(insight)
        
        return insights
    
    def _create_trend_insight(self, trend: TrendAnalysis) -> QualityInsight:
        """Create insight from trend analysis"""
        metric_name = trend.metric_type.value.replace('_', ' ').title()
        
        if trend.direction == TrendDirection.RISING:
            if trend.metric_type in [AnalyticsMetricType.QUALITY_SCORE, 
                                   AnalyticsMetricType.SEO_SCORE,
                                   AnalyticsMetricType.SECURITY_SCORE]:
                priority = InsightPriority.LOW  # Good trend
                title = f"Improving {metric_name}"
                description = f"{metric_name} has improved by {abs(trend.change_percentage):.1f}% - great progress!"
                recommendations = [
                    "Continue current optimization strategies",
                    "Document successful practices for replication",
                    "Consider expanding successful approaches"
                ]
            else:  # Rising errors or issues
                priority = InsightPriority.HIGH
                title = f"Increasing {metric_name}"
                description = f"{metric_name} has increased by {abs(trend.change_percentage):.1f}% - attention needed"
                recommendations = [
                    "Investigate root causes of increase",
                    "Implement corrective measures",
                    "Monitor closely for further changes"
                ]
        
        elif trend.direction == TrendDirection.FALLING:
            if trend.metric_type in [AnalyticsMetricType.VALIDATION_ERRORS,
                                   AnalyticsMetricType.PROCESSING_TIME]:
                priority = InsightPriority.LOW  # Good trend
                title = f"Decreasing {metric_name}"
                description = f"{metric_name} has decreased by {abs(trend.change_percentage):.1f}% - excellent improvement!"
                recommendations = [
                    "Maintain current optimization efforts",
                    "Share successful strategies across teams",
                    "Set targets for further improvements"
                ]
            else:  # Falling quality scores
                priority = InsightPriority.HIGH
                title = f"Declining {metric_name}"
                description = f"{metric_name} has declined by {abs(trend.change_percentage):.1f}% - immediate action required"
                recommendations = [
                    "Identify factors causing decline",
                    "Implement quality improvement measures",
                    "Review and adjust quality processes"
                ]
        
        else:  # Volatile or stable
            priority = InsightPriority.MEDIUM
            title = f"{metric_name} Pattern Analysis"
            description = f"{metric_name} shows {trend.direction.value} behavior over time"
            recommendations = [
                "Monitor for pattern changes",
                "Analyze underlying factors",
                "Consider trend stabilization measures"
            ]
        
        return QualityInsight(
            insight_id=f"trend_{trend.metric_type.value}_{trend.timeframe.value}",
            insight_type=InsightType.TREND,
            priority=priority,
            title=title,
            description=description,
            impact_score=min(100.0, abs(trend.change_percentage) * 2),
            confidence=trend.confidence,
            supporting_data={
                'trend_direction': trend.direction.value,
                'change_percentage': trend.change_percentage,
                'correlation': trend.correlation,
                'data_points': trend.data_points
            },
            affected_metrics=[trend.metric_type],
            recommendations=recommendations,
            timeframe=trend.timeframe
        )
    
    def _generate_anomaly_insights(self, metric_points: List[QualityMetricPoint]) -> List[QualityInsight]:
        """Generate insights from anomaly detection"""
        insights = []
        
        # Group by metric type for anomaly detection
        metrics_by_type = defaultdict(list)
        for point in metric_points:
            metrics_by_type[point.metric_type].append(point)
        
        for metric_type, points in metrics_by_type.items():
            if len(points) < 10:  # Need sufficient data for anomaly detection
                continue
            
            values = [point.value for point in points]
            outliers, outlier_indices = self.statistical_analyzer.detect_outliers(values)
            
            if outliers:
                insight = self._create_anomaly_insight(metric_type, points, outlier_indices)
                insights.append(insight)
        
        return insights
    
    def _create_anomaly_insight(self, metric_type: AnalyticsMetricType,
                              points: List[QualityMetricPoint],
                              outlier_indices: List[int]) -> QualityInsight:
        """Create insight from anomaly detection"""
        metric_name = metric_type.value.replace('_', ' ').title()
        outlier_count = len(outlier_indices)
        
        # Get outlier values and timestamps
        outlier_points = [points[i] for i in outlier_indices]
        outlier_values = [point.value for point in outlier_points]
        
        # Determine if outliers are high or low
        stats = self.statistical_analyzer.calculate_descriptive_statistics([p.value for p in points])
        high_outliers = [v for v in outlier_values if v > stats['q3']]
        low_outliers = [v for v in outlier_values if v < stats['q1']]
        
        if high_outliers and low_outliers:
            anomaly_type = "both high and low values"
        elif high_outliers:
            anomaly_type = "unusually high values"
        else:
            anomaly_type = "unusually low values"
        
        return QualityInsight(
            insight_id=f"anomaly_{metric_type.value}",
            insight_type=InsightType.ANOMALY,
            priority=InsightPriority.MEDIUM,
            title=f"{metric_name} Anomalies Detected",
            description=f"Detected {outlier_count} anomalous data points with {anomaly_type}",
            impact_score=min(100.0, outlier_count * 10),
            confidence=0.8,
            supporting_data={
                'outlier_count': outlier_count,
                'outlier_values': outlier_values,
                'outlier_timestamps': [p.timestamp.isoformat() for p in outlier_points],
                'statistical_summary': stats
            },
            affected_metrics=[metric_type],
            recommendations=[
                "Investigate root causes of anomalous values",
                "Review data collection processes",
                "Implement anomaly detection monitoring",
                "Consider data quality improvements"
            ],
            action_items=[
                "Analyze specific instances of anomalous data",
                "Check for system issues during anomaly periods",
                "Update quality thresholds if needed"
            ]
        )
    
    def _generate_performance_insights(self, metric_points: List[QualityMetricPoint]) -> List[QualityInsight]:
        """Generate performance-based insights"""
        insights = []
        
        # Analyze processing time performance
        processing_points = [p for p in metric_points 
                           if p.metric_type == AnalyticsMetricType.PROCESSING_TIME]
        
        if processing_points:
            values = [p.value for p in processing_points]
            stats = self.statistical_analyzer.calculate_descriptive_statistics(values)
            
            # Check for performance issues
            if stats['mean'] > 5000:  # 5 seconds average
                insight = QualityInsight(
                    insight_id="performance_processing_time",
                    insight_type=InsightType.ALERT,
                    priority=InsightPriority.HIGH,
                    title="High Processing Times Detected",
                    description=f"Average processing time is {stats['mean']:.0f}ms, which may impact user experience",
                    impact_score=80.0,
                    confidence=0.9,
                    supporting_data=stats,
                    affected_metrics=[AnalyticsMetricType.PROCESSING_TIME],
                    recommendations=[
                        "Optimize processing algorithms",
                        "Review system resources and scaling",
                        "Implement performance monitoring",
                        "Consider caching strategies"
                    ],
                    urgency="high"
                )
                insights.append(insight)
        
        return insights
    
    def _generate_predictive_insights(self, trends: List[TrendAnalysis],
                                    timeframe: AnalyticsTimeframe) -> List[QualityInsight]:
        """Generate predictive insights based on trends"""
        insights = []
        
        for trend in trends:
            if trend.confidence > 0.7 and abs(trend.slope) > 0.1:
                # Project future values
                future_prediction = self._predict_future_value(trend, timeframe)
                
                if future_prediction:
                    insight = self._create_predictive_insight(trend, future_prediction, timeframe)
                    insights.append(insight)
        
        return insights
    
    def _predict_future_value(self, trend: TrendAnalysis, 
                            timeframe: AnalyticsTimeframe) -> Optional[Dict[str, Any]]:
        """Predict future metric values based on trend"""
        if trend.correlation < 0.5:  # Low correlation reduces prediction reliability
            return None
        
        # Project one timeframe period into the future
        time_multiplier = {
            AnalyticsTimeframe.DAILY: 1,
            AnalyticsTimeframe.WEEKLY: 7,
            AnalyticsTimeframe.MONTHLY: 30,
            AnalyticsTimeframe.QUARTERLY: 90,
            AnalyticsTimeframe.YEARLY: 365
        }.get(timeframe, 7)
        
        # Simple linear projection
        projected_change = trend.slope * time_multiplier * 24 * 3600  # Convert to seconds
        projected_value = trend.current_value + projected_change
        
        # Calculate confidence in prediction (decreases with projection distance)
        prediction_confidence = trend.confidence * 0.8  # Reduce confidence for prediction
        
        return {
            'projected_value': projected_value,
            'current_value': trend.current_value,
            'projected_change': projected_change,
            'confidence': prediction_confidence,
            'timeframe': timeframe.value
        }
    
    def _create_predictive_insight(self, trend: TrendAnalysis,
                                 prediction: Dict[str, Any],
                                 timeframe: AnalyticsTimeframe) -> QualityInsight:
        """Create predictive insight"""
        metric_name = trend.metric_type.value.replace('_', ' ').title()
        
        change_direction = "increase" if prediction['projected_change'] > 0 else "decrease"
        change_magnitude = abs(prediction['projected_change'])
        
        # Determine priority based on predicted impact
        if change_magnitude > 20:  # Significant change predicted
            priority = InsightPriority.HIGH
        elif change_magnitude > 10:
            priority = InsightPriority.MEDIUM
        else:
            priority = InsightPriority.LOW
        
        return QualityInsight(
            insight_id=f"prediction_{trend.metric_type.value}_{timeframe.value}",
            insight_type=InsightType.PREDICTION,
            priority=priority,
            title=f"Predicted {metric_name} Changes",
            description=f"Based on current trends, {metric_name} is predicted to {change_direction} by {change_magnitude:.1f} over the next {timeframe.value}",
            impact_score=min(100.0, change_magnitude * 3),
            confidence=prediction['confidence'],
            supporting_data=prediction,
            affected_metrics=[trend.metric_type],
            recommendations=[
                "Monitor trend closely for validation",
                "Prepare for predicted changes",
                "Consider preventive measures if needed",
                "Update forecasting models"
            ],
            timeframe=timeframe
        )
    
    def _generate_comparison_insights(self, metric_points: List[QualityMetricPoint]) -> List[QualityInsight]:
        """Generate comparison insights across platforms/categories"""
        insights = []
        
        # Compare platform performance
        platform_insights = self._compare_platform_performance(metric_points)
        insights.extend(platform_insights)
        
        # Compare category performance
        category_insights = self._compare_category_performance(metric_points)
        insights.extend(category_insights)
        
        return insights
    
    def _compare_platform_performance(self, metric_points: List[QualityMetricPoint]) -> List[QualityInsight]:
        """Compare performance across platforms"""
        insights = []
        
        # Group by platform and metric type
        platform_metrics = defaultdict(lambda: defaultdict(list))
        
        for point in metric_points:
            if point.platform:
                platform_metrics[point.platform][point.metric_type].append(point.value)
        
        # Compare quality scores across platforms
        quality_scores = {}
        for platform, metrics in platform_metrics.items():
            if AnalyticsMetricType.QUALITY_SCORE in metrics:
                values = metrics[AnalyticsMetricType.QUALITY_SCORE]
                quality_scores[platform] = statistics.mean(values)
        
        if len(quality_scores) > 1:
            best_platform = max(quality_scores.items(), key=lambda x: x[1])
            worst_platform = min(quality_scores.items(), key=lambda x: x[1])
            
            performance_gap = best_platform[1] - worst_platform[1]
            
            if performance_gap > 10:  # Significant difference
                insight = QualityInsight(
                    insight_id="platform_comparison_quality",
                    insight_type=InsightType.COMPARISON,
                    priority=InsightPriority.MEDIUM,
                    title="Platform Performance Variation",
                    description=f"{best_platform[0]} outperforms {worst_platform[0]} by {performance_gap:.1f} points in quality score",
                    impact_score=performance_gap * 2,
                    confidence=0.8,
                    supporting_data={
                        'platform_scores': quality_scores,
                        'best_platform': best_platform,
                        'worst_platform': worst_platform,
                        'performance_gap': performance_gap
                    },
                    affected_metrics=[AnalyticsMetricType.QUALITY_SCORE],
                    affected_platforms=list(quality_scores.keys()),
                    recommendations=[
                        f"Analyze best practices from {best_platform[0]}",
                        f"Improve optimization strategies for {worst_platform[0]}",
                        "Standardize quality processes across platforms",
                        "Implement platform-specific optimizations"
                    ]
                )
                insights.append(insight)
        
        return insights
    
    def _compare_category_performance(self, metric_points: List[QualityMetricPoint]) -> List[QualityInsight]:
        """Compare performance across content categories"""
        insights = []
        
        # Group by category and metric type
        category_metrics = defaultdict(lambda: defaultdict(list))
        
        for point in metric_points:
            if point.category:
                category_metrics[point.category][point.metric_type].append(point.value)
        
        # Compare quality scores across categories
        quality_scores = {}
        for category, metrics in category_metrics.items():
            if AnalyticsMetricType.QUALITY_SCORE in metrics:
                values = metrics[AnalyticsMetricType.QUALITY_SCORE]
                quality_scores[category] = statistics.mean(values)
        
        if len(quality_scores) > 1:
            best_category = max(quality_scores.items(), key=lambda x: x[1])
            worst_category = min(quality_scores.items(), key=lambda x: x[1])
            
            performance_gap = best_category[1] - worst_category[1]
            
            if performance_gap > 15:  # Significant difference
                insight = QualityInsight(
                    insight_id="category_comparison_quality",
                    insight_type=InsightType.COMPARISON,
                    priority=InsightPriority.MEDIUM,
                    title="Content Category Performance Variation",
                    description=f"{best_category[0]} content performs {performance_gap:.1f} points better than {worst_category[0]} content",
                    impact_score=performance_gap * 1.5,
                    confidence=0.8,
                    supporting_data={
                        'category_scores': quality_scores,
                        'best_category': best_category,
                        'worst_category': worst_category,
                        'performance_gap': performance_gap
                    },
                    affected_metrics=[AnalyticsMetricType.QUALITY_SCORE],
                    affected_categories=list(quality_scores.keys()),
                    recommendations=[
                        f"Apply successful strategies from {best_category[0]} to other categories",
                        f"Focus improvement efforts on {worst_category[0]} content",
                        "Develop category-specific quality guidelines",
                        "Analyze content characteristics driving performance differences"
                    ]
                )
                insights.append(insight)
        
        return insights


class QualityAnalyticsEngine:
    """Enterprise quality analytics and intelligence engine"""
    
    def __init__(self):
        self.statistical_analyzer = StatisticalAnalyzer()
        self.trend_detector = TrendDetector()
        self.insight_generator = InsightGenerator()
        
        # Data storage (in production, this would be a database)
        self.metric_points: List[QualityMetricPoint] = []
        self.reports: List[AnalyticsReport] = []
    
    def add_metric_point(self, metric_point: QualityMetricPoint):
        """Add a quality metric data point"""
        self.metric_points.append(metric_point)
    
    def add_quality_data(self, content_id: str, quality_data: Dict[str, Any],
                        platform: Optional[str] = None, category: Optional[str] = None):
        """Add quality data from validation results"""
        timestamp = datetime.now(timezone.utc)
        
        # Extract metrics from quality data
        metrics_to_extract = [
            ('overall_quality_score', AnalyticsMetricType.QUALITY_SCORE),
            ('seo_score', AnalyticsMetricType.SEO_SCORE),
            ('security_score', AnalyticsMetricType.SECURITY_SCORE),
            ('monetization_score', AnalyticsMetricType.MONETIZATION_SCORE),
            ('compliance_score', AnalyticsMetricType.COMPLIANCE_SCORE),
            ('processing_time_ms', AnalyticsMetricType.PROCESSING_TIME),
            ('validation_errors', AnalyticsMetricType.VALIDATION_ERRORS)
        ]
        
        for field_name, metric_type in metrics_to_extract:
            if field_name in quality_data:
                metric_point = QualityMetricPoint(
                    metric_id=f"{content_id}_{metric_type.value}_{timestamp.timestamp()}",
                    metric_type=metric_type,
                    value=float(quality_data[field_name]),
                    timestamp=timestamp,
                    content_id=content_id,
                    platform=platform,
                    category=category,
                    metadata=quality_data.get('metadata', {})
                )
                self.add_metric_point(metric_point)
    
    def generate_analytics_report(self, timeframe: AnalyticsTimeframe,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        report_start_time = datetime.now(timezone.utc)
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now(timezone.utc)
        
        if not start_date:
            time_deltas = {
                AnalyticsTimeframe.DAILY: timedelta(days=1),
                AnalyticsTimeframe.WEEKLY: timedelta(weeks=1),
                AnalyticsTimeframe.MONTHLY: timedelta(days=30),
                AnalyticsTimeframe.QUARTERLY: timedelta(days=90),
                AnalyticsTimeframe.YEARLY: timedelta(days=365)
            }
            start_date = end_date - time_deltas.get(timeframe, timedelta(weeks=1))
        
        # Filter metric points by date range
        filtered_points = [
            point for point in self.metric_points
            if start_date <= point.timestamp <= end_date
        ]
        
        # Initialize report
        report = AnalyticsReport(
            report_id=f"report_{timeframe.value}_{report_start_time.timestamp()}",
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        try:
            # Calculate summary statistics
            self._calculate_summary_statistics(filtered_points, report)
            
            # Analyze trends
            trends = self.trend_detector.analyze_metric_trends(filtered_points, timeframe)
            for trend in trends:
                report.add_trend(trend)
            
            # Generate insights
            insights = self.insight_generator.generate_insights(
                filtered_points, trends, timeframe
            )
            for insight in insights:
                report.add_insight(insight)
            
            # Calculate performance metrics
            self._calculate_performance_metrics(filtered_points, report)
            
            # Calculate quality distribution
            self._calculate_quality_distribution(filtered_points, report)
            
            # Calculate processing statistics
            self._calculate_processing_statistics(filtered_points, report)
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            # Add error insight
            error_insight = QualityInsight(
                insight_id="report_generation_error",
                insight_type=InsightType.ALERT,
                priority=InsightPriority.CRITICAL,
                title="Report Generation Error",
                description=f"Error occurred during report generation: {str(e)}",
                impact_score=100.0,
                confidence=1.0
            )
            report.add_insight(error_insight)
        
        # Finalize report
        report_end_time = datetime.now(timezone.utc)
        report.processing_time_ms = (report_end_time - report_start_time).total_seconds() * 1000
        
        # Store report
        self.reports.append(report)
        
        return report
    
    def _calculate_summary_statistics(self, metric_points: List[QualityMetricPoint],
                                    report: AnalyticsReport):
        """Calculate summary statistics for the report"""
        if not metric_points:
            return
        
        # Total content analyzed
        unique_content = set(point.content_id for point in metric_points if point.content_id)
        report.total_content_analyzed = len(unique_content)
        
        # Average quality score
        quality_points = [point for point in metric_points 
                         if point.metric_type == AnalyticsMetricType.QUALITY_SCORE]
        if quality_points:
            report.average_quality_score = statistics.mean(point.value for point in quality_points)
        
        # Total issues
        error_points = [point for point in metric_points 
                       if point.metric_type == AnalyticsMetricType.VALIDATION_ERRORS]
        if error_points:
            report.total_issues_found = int(sum(point.value for point in error_points))
        
        # Count optimizations (this would need to be tracked separately in real implementation)
        report.total_optimizations_identified = len(metric_points) // 10  # Rough estimate
    
    def _calculate_performance_metrics(self, metric_points: List[QualityMetricPoint],
                                     report: AnalyticsReport):
        """Calculate platform and category performance metrics"""
        # Platform performance
        platform_metrics = defaultdict(list)
        for point in metric_points:
            if point.platform and point.metric_type == AnalyticsMetricType.QUALITY_SCORE:
                platform_metrics[point.platform].append(point.value)
        
        for platform, values in platform_metrics.items():
            report.platform_performance[platform] = statistics.mean(values)
        
        # Category performance
        category_metrics = defaultdict(list)
        for point in metric_points:
            if point.category and point.metric_type == AnalyticsMetricType.QUALITY_SCORE:
                category_metrics[point.category].append(point.value)
        
        for category, values in category_metrics.items():
            report.category_performance[category] = statistics.mean(values)
    
    def _calculate_quality_distribution(self, metric_points: List[QualityMetricPoint],
                                      report: AnalyticsReport):
        """Calculate quality score distribution"""
        quality_points = [point for point in metric_points 
                         if point.metric_type == AnalyticsMetricType.QUALITY_SCORE]
        
        if not quality_points:
            return
        
        # Categorize quality scores
        for point in quality_points:
            score = point.value
            if score >= 90:
                category = "Excellent (90-100)"
            elif score >= 80:
                category = "Good (80-89)"
            elif score >= 70:
                category = "Fair (70-79)"
            elif score >= 60:
                category = "Poor (60-69)"
            else:
                category = "Critical (<60)"
            
            report.quality_distribution[category] = report.quality_distribution.get(category, 0) + 1
    
    def _calculate_processing_statistics(self, metric_points: List[QualityMetricPoint],
                                       report: AnalyticsReport):
        """Calculate processing performance statistics"""
        processing_points = [point for point in metric_points 
                           if point.metric_type == AnalyticsMetricType.PROCESSING_TIME]
        
        if processing_points:
            values = [point.value for point in processing_points]
            stats = self.statistical_analyzer.calculate_descriptive_statistics(values)
            
            report.processing_statistics = {
                'average_processing_time_ms': stats['mean'],
                'median_processing_time_ms': stats['median'],
                'max_processing_time_ms': stats['max'],
                'min_processing_time_ms': stats['min'],
                'p95_processing_time_ms': stats['p95'],
                'total_processing_events': len(processing_points)
            }
    
    def get_real_time_insights(self, lookback_hours: int = 24) -> List[QualityInsight]:
        """Get real-time insights for recent data"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        
        recent_points = [
            point for point in self.metric_points
            if point.timestamp >= cutoff_time
        ]
        
        if not recent_points:
            return []
        
        # Generate quick insights for recent data
        insights = []
        
        # Check for recent anomalies
        anomaly_insights = self.insight_generator._generate_anomaly_insights(recent_points)
        insights.extend(anomaly_insights)
        
        # Check for performance issues
        performance_insights = self.insight_generator._generate_performance_insights(recent_points)
        insights.extend(performance_insights)
        
        return insights
    
    def get_metric_summary(self, metric_type: AnalyticsMetricType,
                          days_back: int = 30) -> Dict[str, Any]:
        """Get summary statistics for a specific metric"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        metric_points = [
            point for point in self.metric_points
            if point.metric_type == metric_type and point.timestamp >= cutoff_time
        ]
        
        if not metric_points:
            return {}
        
        values = [point.value for point in metric_points]
        stats = self.statistical_analyzer.calculate_descriptive_statistics(values)
        
        # Add trend information
        timestamps = [point.timestamp for point in metric_points]
        trend_direction = self.statistical_analyzer.detect_trend(values, timestamps)
        
        return {
            'metric_type': metric_type.value,
            'data_points': len(metric_points),
            'time_period_days': days_back,
            'statistics': stats,
            'trend_direction': trend_direction.value,
            'latest_value': values[-1] if values else 0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def export_data(self, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """Export analytics data"""
        data = {
            'metric_points': [point.to_dict() for point in self.metric_points],
            'reports': [report.to_dict() for report in self.reports],
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_metric_points': len(self.metric_points),
            'total_reports': len(self.reports)
        }
        
        if format_type.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            return data
    
    def clear_old_data(self, days_to_keep: int = 90):
        """Clear old metric data to manage storage"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        # Remove old metric points
        self.metric_points = [
            point for point in self.metric_points
            if point.timestamp >= cutoff_time
        ]
        
        # Remove old reports
        self.reports = [
            report for report in self.reports
            if report.generation_timestamp >= cutoff_time
        ]
        
        logger.info(f"Cleared analytics data older than {days_to_keep} days")
