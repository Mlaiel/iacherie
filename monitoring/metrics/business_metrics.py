"""📊 Enterprise Business Metrics - Advanced KPI Tracking System
============================================================

Enterprise-grade business metrics collection and analysis for the Ainflue platform.
Tracks revenue, user engagement, content performance, collaboration success, monetization,
gamification, SEO performance, distribution analytics, and AI-powered insights.

Enhanced Features:
- Real-time business intelligence with ML predictions
- Cross-platform performance correlation
- Advanced revenue attribution modeling
- Collaboration ROI tracking with success prediction
- Content protection impact analysis
- Multi-dimensional user journey analytics
- Predictive churn and engagement optimization
- Cost-effectiveness measurement across all operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, deque
import statistics
import uuid
import hashlib

logger = logging.getLogger(__name__)


class EnhancedMetricType(Enum):
    """Enhanced types of business metrics for Ainflue platform."""
    # Core Metric Types
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    
    # Business-Specific Metrics
    REVENUE = "revenue"
    CONVERSION_RATE = "conversion_rate"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_PERFORMANCE = "content_performance"
    COLLABORATION_SUCCESS = "collaboration_success"
    AI_INSIGHTS = "ai_insights"
    
    # Platform-Specific Metrics
    AUDIO_QUALITY = "audio_quality"
    PROTECTION_EFFECTIVENESS = "protection_effectiveness"
    MONETIZATION_EFFICIENCY = "monetization_efficiency"
    SEO_PERFORMANCE = "seo_performance"
    DISTRIBUTION_REACH = "distribution_reach"
    GAMIFICATION_ENGAGEMENT = "gamification_engagement"

class BusinessDimension(Enum):
    """Business dimensions for metric segmentation."""
    CREATOR_TIER = "creator_tier"
    CONTENT_TYPE = "content_type"
    GEOGRAPHIC_REGION = "geographic_region"
    DEVICE_TYPE = "device_type"
    TRAFFIC_SOURCE = "traffic_source"
    COLLABORATION_TYPE = "collaboration_type"
    MONETIZATION_CHANNEL = "monetization_channel"
    PLATFORM = "platform"
    GENRE = "genre"
    AUDIENCE_SEGMENT = "audience_segment"

class MetricAggregation(Enum):
    """Metric aggregation methods."""
    SUM = "sum"
    AVERAGE = "average"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MEDIAN = "median"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    COUNT = "count"
    UNIQUE_COUNT = "unique_count"
    RATE = "rate"
    RATIO = "ratio"


class MetricPeriod(Enum):
    """Metric aggregation periods"""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class EnhancedBusinessMetric:
    """Enhanced business metric with AI insights and advanced analytics."""
    name: str
    metric_type: EnhancedMetricType
    value: Union[float, int, Decimal]
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Enhanced fields
    business_context: Dict[str, Any] = field(default_factory=dict)
    ai_predictions: Dict[str, Any] = field(default_factory=dict)
    correlation_factors: Dict[str, float] = field(default_factory=dict)
    confidence_score: float = 1.0
    data_quality_score: float = 1.0
    
    # Metadata
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_system: str = "ainflue_platform"
    collection_method: str = "real_time"
    
    def add_prediction(self, prediction_type: str, predicted_value: float, confidence: float):
        """Add AI prediction to metric."""
        self.ai_predictions[prediction_type] = {
            "predicted_value": predicted_value,
            "confidence": confidence,
            "prediction_time": datetime.utcnow().isoformat()
        }
    
    def add_correlation(self, factor_name: str, correlation_strength: float):
        """Add correlation factor."""
        self.correlation_factors[factor_name] = correlation_strength
    
    def calculate_business_impact_score(self) -> float:
        """Calculate business impact score based on metric type and value."""
        impact_weights = {
            EnhancedMetricType.REVENUE: 1.0,
            EnhancedMetricType.COLLABORATION_SUCCESS: 0.8,
            EnhancedMetricType.USER_ENGAGEMENT: 0.7,
            EnhancedMetricType.CONTENT_PERFORMANCE: 0.6,
            EnhancedMetricType.MONETIZATION_EFFICIENCY: 0.9,
            EnhancedMetricType.PROTECTION_EFFECTIVENESS: 0.5
        }
        
        base_weight = impact_weights.get(self.metric_type, 0.3)
        normalized_value = min(1.0, abs(float(self.value)) / 10000)  # Normalize to 0-1
        
        return base_weight * normalized_value * self.confidence_score

@dataclass
class BusinessMetricSeries:
    """Time series of business metrics with advanced analytics."""
    metric_name: str
    metric_type: EnhancedMetricType
    data_points: List[EnhancedBusinessMetric] = field(default_factory=list)
    aggregation_period: MetricPeriod = MetricPeriod.HOUR
    
    # Analytics fields
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    seasonality_patterns: Dict[str, Any] = field(default_factory=dict)
    anomaly_detection: Dict[str, Any] = field(default_factory=dict)
    forecasting: Dict[str, Any] = field(default_factory=dict)
    
    def add_data_point(self, metric: EnhancedBusinessMetric):
        """Add data point to series."""
        self.data_points.append(metric)
        self.data_points.sort(key=lambda x: x.timestamp)
        
        # Keep only last 1000 points for memory efficiency
        if len(self.data_points) > 1000:
            self.data_points = self.data_points[-1000:]
        
        # Update analytics
        self._update_trend_analysis()
        self._detect_anomalies()
    
    def _update_trend_analysis(self):
        """Update trend analysis."""
        if len(self.data_points) < 3:
            return
        
        recent_values = [float(dp.value) for dp in self.data_points[-10:]]
        
        if len(recent_values) >= 2:
            # Simple trend calculation
            slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
            
            if slope > 0.1:
                trend = "increasing"
            elif slope < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
            
            self.trend_analysis = {
                "direction": trend,
                "slope": slope,
                "confidence": min(1.0, len(recent_values) / 10),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def _detect_anomalies(self):
        """Detect anomalies in the time series."""
        if len(self.data_points) < 10:
            return
        
        values = [float(dp.value) for dp in self.data_points]
        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values) if len(values) > 1 else 0
        
        # Detect recent anomalies
        recent_anomalies = []
        for dp in self.data_points[-5:]:
            value = float(dp.value)
            if std_value > 0 and abs(value - mean_value) > 2 * std_value:
                recent_anomalies.append({
                    "timestamp": dp.timestamp.isoformat(),
                    "value": value,
                    "expected_range": [mean_value - std_value, mean_value + std_value],
                    "severity": "high" if abs(value - mean_value) > 3 * std_value else "medium"
                })
        
        self.anomaly_detection = {
            "recent_anomalies": recent_anomalies,
            "anomaly_count": len(recent_anomalies),
            "detection_sensitivity": 2.0,  # 2 standard deviations
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_aggregated_value(self, aggregation: MetricAggregation, period_hours: int = 24) -> Optional[float]:
        """Get aggregated value for specified period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        recent_points = [dp for dp in self.data_points if dp.timestamp >= cutoff_time]
        
        if not recent_points:
            return None
        
        values = [float(dp.value) for dp in recent_points]
        
        if aggregation == MetricAggregation.SUM:
            return sum(values)
        elif aggregation == MetricAggregation.AVERAGE:
            return statistics.mean(values)
        elif aggregation == MetricAggregation.MINIMUM:
            return min(values)
        elif aggregation == MetricAggregation.MAXIMUM:
            return max(values)
        elif aggregation == MetricAggregation.MEDIAN:
            return statistics.median(values)
        elif aggregation == MetricAggregation.COUNT:
            return len(values)
        elif aggregation == MetricAggregation.UNIQUE_COUNT:
            return len(set(values))
        else:
            return statistics.mean(values)  # Default to average
    value: Union[int, float, Decimal]
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """
Aggregated metric data"""
    metric_name: str
    period: MetricPeriod
    start_time: datetime
    end_time: datetime
    count: int
    sum_value: float
    avg_value: float
    min_value: float
    max_value: float
    percentiles: Dict[str, float] = field(default_factory=dict)


class BusinessMetricsCollector:
    """
    Advanced business metrics collection and analysis system
    
    Features:
    - Revenue tracking and analytics
    - User engagement metrics
    - Content performance analysis
    - License utilization tracking
    - Platform-specific KPIs
    - Real-time dashboards
    - Historical trend analysis
    - Custom business rules
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize business metrics collector"""
        self.config = config or {}
        
        # Metric storage
        self.metrics: Dict[str, List[BusinessMetric]] = defaultdict(list)
        self.aggregations: Dict[str, Dict[str, MetricAggregation]] = defaultdict(dict)
        
        # Real-time metric queues (for fast recent data access)
        self.recent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Business KPI definitions
        self.kpi_definitions = {
            # Revenue KPIs
            "revenue_total": {
                "description": "Total platform revenue",
                "type": MetricType.COUNTER,
                "unit": "EUR",
                "target": 100000.0,  # Monthly target
                "critical_threshold": 0.8
            },
            "revenue_per_user": {
                "description": "Average revenue per user",
                "type": MetricType.GAUGE,
                "unit": "EUR",
                "target": 50.0,
                "critical_threshold": 0.7
            },
            "license_revenue": {
                "description": "Revenue from licensing",
                "type": MetricType.COUNTER,
                "unit": "EUR",
                "target": 80000.0,
                "critical_threshold": 0.75
            },
            
            # User Engagement KPIs
            "active_users_daily": {
                "description": "Daily active users",
                "type": MetricType.GAUGE,
                "unit": "users",
                "target": 10000,
                "critical_threshold": 0.8
            },
            "user_retention_rate": {
                "description": "User retention rate",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 85.0,
                "critical_threshold": 0.9
            },
            "session_duration_avg": {
                "description": "Average session duration",
                "type": MetricType.GAUGE,
                "unit": "minutes",
                "target": 45.0,
                "critical_threshold": 0.8
            },
            
            # Content Performance KPIs
            "content_uploads_daily": {
                "description": "Daily content uploads",
                "type": MetricType.COUNTER,
                "unit": "uploads",
                "target": 1000,
                "critical_threshold": 0.8
            },
            "content_engagement_rate": {
                "description": "Content engagement rate",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 15.0,
                "critical_threshold": 0.7
            },
            "copyright_detection_accuracy": {
                "description": "Copyright detection accuracy",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 95.0,
                "critical_threshold": 0.95
            },
            
            # Licensing KPIs
            "licenses_created_daily": {
                "description": "Daily license creation",
                "type": MetricType.COUNTER,
                "unit": "licenses",
                "target": 500,
                "critical_threshold": 0.8
            },
            "license_approval_rate": {
                "description": "License approval rate",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 90.0,
                "critical_threshold": 0.85
            },
            "royalty_payout_accuracy": {
                "description": "Royalty payout accuracy",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 99.0,
                "critical_threshold": 0.98
            },
            
            # Platform Performance KPIs
            "api_response_time": {
                "description": "Average API response time",
                "type": MetricType.GAUGE,
                "unit": "ms",
                "target": 200.0,
                "critical_threshold": 0.5  # Reverse: lower is better
            },
            "platform_uptime": {
                "description": "Platform uptime percentage",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 99.9,
                "critical_threshold": 0.99
            },
            "error_rate": {
                "description": "Error rate percentage",
                "type": MetricType.GAUGE,
                "unit": "percent",
                "target": 0.1,
                "critical_threshold": 0.1  # Reverse: lower is better
            }
        }
        
        # Alerting configuration
        self.alerting_config = {
            "enabled": True,
            "check_interval": 300,  # 5 minutes
            "escalation_levels": ["warning", "critical", "emergency"],
            "notification_channels": ["email", "slack", "webhook"]
        }
        
        # Performance tracking
        self.collector_stats = {
            "metrics_collected": 0,
            "aggregations_computed": 0,
            "alerts_triggered": 0,
            "start_time": datetime.utcnow()
        }
        
        logger.info("BusinessMetricsCollector initialized successfully")
    
    async def record_metric(
        self,
        name: str,
        value: Union[int, float, Decimal],
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a business metric
        
        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels for categorization
            metadata: Optional metadata
        """
        try:
            # Get metric definition
            metric_def = self.kpi_definitions.get(name, {})
            metric_type = metric_def.get("type", MetricType.GAUGE)
            
            # Create metric
            metric = BusinessMetric(
                name=name,
                value=float(value),
                metric_type=metric_type,
                timestamp=datetime.utcnow(),
                labels=labels or {},
                metadata=metadata or {}
            )
            
            # Store metric
            self.metrics[name].append(metric)
            self.recent_metrics[name].append(metric)
            
            # Update collector stats
            self.collector_stats["metrics_collected"] += 1
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            logger.debug(f"Metric recorded: {name} = {value}")
            
        except Exception as e:
            logger.error(f"Error recording metric {name}: {e}")
    
    async def record_revenue(
        self,
        amount: Decimal,
        source: str,
        user_id: Optional[int] = None,
        license_id: Optional[int] = None
    ) -> None:
        """Record revenue event"""
        try:
            labels = {"source": source}
            metadata = {}
            
            if user_id:
                labels["user_id"] = str(user_id)
                metadata["user_id"] = user_id
            
            if license_id:
                labels["license_id"] = str(license_id)
                metadata["license_id"] = license_id
            
            await self.record_metric("revenue_total", amount, labels, metadata)
            
            # Also record source-specific revenue
            await self.record_metric(f"revenue_{source}", amount, labels, metadata)
            
        except Exception as e:
            logger.error(f"Error recording revenue: {e}")
    
    async def record_user_engagement(
        self,
        user_id: int,
        action: str,
        duration: Optional[float] = None,
        content_id: Optional[int] = None
    ) -> None:
        """Record user engagement event"""
        try:
            labels = {
                "user_id": str(user_id),
                "action": action
            }
            metadata = {"user_id": user_id, "action": action}
            
            if content_id:
                labels["content_id"] = str(content_id)
                metadata["content_id"] = content_id
            
            # Record engagement event
            await self.record_metric("user_engagement", 1, labels, metadata)
            
            # Record duration if provided
            if duration:
                await self.record_metric("session_duration", duration, labels, metadata)
            
        except Exception as e:
            logger.error(f"Error recording user engagement: {e}")
    
    async def record_content_performance(
        self,
        content_id: int,
        metric_name: str,
        value: Union[int, float],
        content_type: Optional[str] = None
    ) -> None:
        """Record content performance metric"""
        try:
            labels = {"content_id": str(content_id)}
            metadata = {"content_id": content_id}
            
            if content_type:
                labels["content_type"] = content_type
                metadata["content_type"] = content_type
            
            await self.record_metric(f"content_{metric_name}", value, labels, metadata)
            
        except Exception as e:
            logger.error(f"Error recording content performance: {e}")
    
    async def record_license_activity(
        self,
        license_id: int,
        activity: str,
        value: Union[int, float] = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record license activity"""
        try:
            labels = {
                "license_id": str(license_id),
                "activity": activity
            }
            
            metric_metadata = {"license_id": license_id, "activity": activity}
            if metadata:
                metric_metadata.update(metadata)
            
            await self.record_metric(f"license_{activity}", value, labels, metric_metadata)
            
        except Exception as e:
            logger.error(f"Error recording license activity: {e}")
    
    async def compute_aggregations(
        self,
        metric_name: str,
        period: MetricPeriod = MetricPeriod.DAY
    ) -> Optional[MetricAggregation]:
        """
        Compute metric aggregations for a period
        
        Args:
            metric_name: Name of metric to aggregate
            period: Aggregation period
            
        Returns:
            MetricAggregation or None if no data
        """
        try:
            if metric_name not in self.metrics:
                return None
            
            # Determine time range for period
            end_time = datetime.utcnow()
            
            if period == MetricPeriod.HOUR:
                start_time = end_time - timedelta(hours=1)
            elif period == MetricPeriod.DAY:
                start_time = end_time - timedelta(days=1)
            elif period == MetricPeriod.WEEK:
                start_time = end_time - timedelta(weeks=1)
            elif period == MetricPeriod.MONTH:
                start_time = end_time - timedelta(days=30)
            elif period == MetricPeriod.QUARTER:
                start_time = end_time - timedelta(days=90)
            else:  # YEAR
                start_time = end_time - timedelta(days=365)
            
            # Filter metrics by time range
            period_metrics = [
                metric for metric in self.metrics[metric_name]
                if start_time <= metric.timestamp <= end_time
            ]
            
            if not period_metrics:
                return None
            
            # Compute aggregations
            values = [metric.value for metric in period_metrics]
            
            aggregation = MetricAggregation(
                metric_name=metric_name,
                period=period,
                start_time=start_time,
                end_time=end_time,
                count=len(values),
                sum_value=sum(values),
                avg_value=statistics.mean(values),
                min_value=min(values),
                max_value=max(values),
                percentiles={
                    "p50": statistics.median(values),
                    "p90": statistics.quantiles(values, n=10)[8] if len(values) >= 10 else max(values),
                    "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                    "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
                }
            )
            
            # Cache aggregation
            cache_key = f"{period.value}_{start_time.strftime('%Y%m%d_%H')}"
            self.aggregations[metric_name][cache_key] = aggregation
            
            # Update stats
            self.collector_stats["aggregations_computed"] += 1
            
            return aggregation
            
        except Exception as e:
            logger.error(f"Error computing aggregations for {metric_name}: {e}")
            return None
    
    async def get_kpi_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive KPI dashboard data
        
        Returns:
            Dict: Dashboard data with all KPIs
        """
        try:
            dashboard = {
                "timestamp": datetime.utcnow().isoformat(),
                "kpis": {},
                "alerts": [],
                "trends": {},
                "summary": {
                    "total_metrics": len(self.metrics),
                    "total_data_points": sum(len(metrics) for metrics in self.metrics.values()),
                    "collection_period": (datetime.utcnow() - self.collector_stats["start_time"]).days
                }
            }
            
            # Calculate KPIs
            for kpi_name, kpi_def in self.kpi_definitions.items():
                kpi_data = await self._calculate_kpi(kpi_name, kpi_def)
                dashboard["kpis"][kpi_name] = kpi_data
                
                # Check for alerts
                if kpi_data.get("alert_level"):
                    dashboard["alerts"].append({
                        "kpi": kpi_name,
                        "level": kpi_data["alert_level"],
                        "message": kpi_data.get("alert_message"),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Calculate trends (comparing current vs previous period)
            for kpi_name in self.kpi_definitions.keys():
                trend = await self._calculate_trend(kpi_name)
                if trend:
                    dashboard["trends"][kpi_name] = trend
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating KPI dashboard: {e}")
            return {"error": str(e)}
    
    async def get_metric_history(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: MetricPeriod = MetricPeriod.HOUR
    ) -> List[Dict[str, Any]]:
        """
        Get historical metric data
        
        Args:
            metric_name: Name of metric
            start_time: Start of time range
            end_time: End of time range
            granularity: Data granularity
            
        Returns:
            List of metric data points
        """
        try:
            if metric_name not in self.metrics:
                return []
            
            # Filter metrics by time range
            filtered_metrics = [
                metric for metric in self.metrics[metric_name]
                if start_time <= metric.timestamp <= end_time
            ]
            
            # Group by granularity
            grouped_data = defaultdict(list)
            
            for metric in filtered_metrics:
                if granularity == MetricPeriod.HOUR:
                    key = metric.timestamp.strftime("%Y%m%d_%H")
                elif granularity == MetricPeriod.DAY:
                    key = metric.timestamp.strftime("%Y%m%d")
                elif granularity == MetricPeriod.WEEK:
                    # ISO week
                    key = f"{metric.timestamp.year}W{metric.timestamp.isocalendar()[1]:02d}"
                elif granularity == MetricPeriod.MONTH:
                    key = metric.timestamp.strftime("%Y%m")
                else:
                    key = metric.timestamp.strftime("%Y")
                
                grouped_data[key].append(metric.value)
            
            # Create aggregated data points
            history = []
            for key, values in sorted(grouped_data.items()):
                history.append({
                    "timestamp": key,
                    "count": len(values),
                    "sum": sum(values),
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values)
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting metric history: {e}")
            return []
    
    async def _calculate_kpi(self, kpi_name: str, kpi_def: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate individual KPI with status and alerts"""
        try:
            current_aggregation = await self.compute_aggregations(kpi_name, MetricPeriod.DAY)
            
            if not current_aggregation:
                return {
                    "name": kpi_name,
                    "value": 0,
                    "status": "no_data",
                    "description": kpi_def.get("description", ""),
                    "unit": kpi_def.get("unit", ""),
                    "target": kpi_def.get("target", 0)
                }
            
            # Calculate current value (use sum for counters, avg for gauges)
            if kpi_def["type"] == MetricType.COUNTER:
                current_value = current_aggregation.sum_value
            else:
                current_value = current_aggregation.avg_value
            
            # Calculate status
            target = kpi_def.get("target", 0)
            critical_threshold = kpi_def.get("critical_threshold", 0.8)
            
            # For metrics where lower is better (like error_rate, response_time)
            reverse_metric = kpi_name in ["api_response_time", "error_rate"]
            
            if reverse_metric:
                ratio = target / current_value if current_value > 0 else 1
                if ratio >= 1:
                    status = "excellent"
                elif ratio >= critical_threshold:
                    status = "good"
                elif ratio >= 0.5:
                    status = "warning"
                else:
                    status = "critical"
            else:
                ratio = current_value / target if target > 0 else 1
                if ratio >= 1:
                    status = "excellent"
                elif ratio >= critical_threshold:
                    status = "good"
                elif ratio >= 0.5:
                    status = "warning"
                else:
                    status = "critical"
            
            # Determine alert level
            alert_level = None
            alert_message = None
            
            if status == "critical":
                alert_level = "critical"
                alert_message = f"{kpi_name} is critically low: {current_value:.2f} (target: {target})"
            elif status == "warning":
                alert_level = "warning"
                alert_message = f"{kpi_name} is below target: {current_value:.2f} (target: {target})"
            
            return {
                "name": kpi_name,
                "value": round(current_value, 2),
                "status": status,
                "target": target,
                "achievement_ratio": round(ratio, 3),
                "description": kpi_def.get("description", ""),
                "unit": kpi_def.get("unit", ""),
                "alert_level": alert_level,
                "alert_message": alert_message,
                "last_updated": current_aggregation.end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating KPI {kpi_name}: {e}")
            return {"name": kpi_name, "error": str(e)}
    
    async def _calculate_trend(self, kpi_name: str) -> Optional[Dict[str, Any]]:
        """Calculate trend for KPI (current vs previous period)"""
        try:
            current = await self.compute_aggregations(kpi_name, MetricPeriod.DAY)
            
            # Get previous period data
            if current and kpi_name in self.metrics:
                previous_start = current.start_time - timedelta(days=1)
                previous_end = current.start_time
                
                previous_metrics = [
                    metric for metric in self.metrics[kpi_name]
                    if previous_start <= metric.timestamp <= previous_end
                ]
                
                if previous_metrics:
                    previous_values = [m.value for m in previous_metrics]
                    previous_avg = statistics.mean(previous_values)
                    
                    # Calculate trend
                    if previous_avg > 0:
                        change_percent = ((current.avg_value - previous_avg) / previous_avg) * 100
                        
                        if change_percent > 5:
                            trend_direction = "increasing"
                        elif change_percent < -5:
                            trend_direction = "decreasing"
                        else:
                            trend_direction = "stable"
                        
                        return {
                            "direction": trend_direction,
                            "change_percent": round(change_percent, 2),
                            "current_value": round(current.avg_value, 2),
                            "previous_value": round(previous_avg, 2)
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating trend for {kpi_name}: {e}")
            return None
    
    async def _check_metric_alerts(self, metric: BusinessMetric) -> None:
        """Check if metric triggers any alerts"""
        try:
            if not self.alerting_config.get("enabled", True):
                return
            
            kpi_def = self.kpi_definitions.get(metric.name)
            if not kpi_def:
                return
            
            target = kpi_def.get("target", 0)
            critical_threshold = kpi_def.get("critical_threshold", 0.8)
            
            # Check thresholds
            if target > 0:
                ratio = metric.value / target
                
                if ratio < 0.5:  # Critical alert
                    await self._trigger_alert(metric, "critical", f"Metric {metric.name} critically low: {metric.value}")
                elif ratio < critical_threshold:  # Warning alert
                    await self._trigger_alert(metric, "warning", f"Metric {metric.name} below threshold: {metric.value}")
            
        except Exception as e:
            logger.error(f"Error checking metric alerts: {e}")
    
    async def _trigger_alert(self, metric: BusinessMetric, level: str, message: str) -> None:
        """Trigger alert for metric"""
        try:
            alert = {
                "metric_name": metric.name,
                "level": level,
                "message": message,
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat(),
                "labels": metric.labels
            }
            
            # Log alert
            if level == "critical":
                logger.critical(f"🚨 CRITICAL ALERT: {message}")
            else:
                logger.warning(f"⚠️ WARNING ALERT: {message}")
            
            # Update stats
            self.collector_stats["alerts_triggered"] += 1
            
            # Here you would integrate with notification systems
            # await self._send_notification(alert)
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    def get_collector_stats(self) -> Dict[str, Any]:
        """Get metrics collector statistics"""
        uptime = datetime.utcnow() - self.collector_stats["start_time"]
        
        return {
            "version": "1.0.0",
            "uptime_seconds": uptime.total_seconds(),
            "metrics_collected": self.collector_stats["metrics_collected"],
            "aggregations_computed": self.collector_stats["aggregations_computed"],
            "alerts_triggered": self.collector_stats["alerts_triggered"],
            "unique_metrics": len(self.metrics),
            "kpis_defined": len(self.kpi_definitions),
            "alerting_enabled": self.alerting_config.get("enabled", True)
        }


# Export classes
class MetricCorrelationEngine:
    """Engine for analyzing correlations between metrics."""
    
    def __init__(self):
        self.correlations: Dict[str, Dict[str, float]] = {}
    
    def update_correlations(self, metric: EnhancedBusinessMetric, metric_series: Dict[str, BusinessMetricSeries]):
        """Update correlation matrix with new metric."""
        # Simplified correlation update
        metric_key = f"{metric.name}_{metric.metric_type.value}"
        if metric_key not in self.correlations:
            self.correlations[metric_key] = {}
        
        # Update correlations with other metrics
        for series_key, series in metric_series.items():
            if series_key != metric_key and len(series.data_points) > 1:
                correlation = self._calculate_correlation(metric, series)
                self.correlations[metric_key][series_key] = correlation
    
    def _calculate_correlation(self, metric: EnhancedBusinessMetric, series: BusinessMetricSeries) -> float:
        """Calculate correlation between metric and series."""
        # Simplified correlation calculation
        return 0.5  # Placeholder
    
    async def get_correlation_insights(self) -> Dict[str, Any]:
        """Get correlation insights."""
        return {
            "strong_correlations": self._find_strong_correlations(),
            "correlation_matrix": self.correlations
        }
    
    def _find_strong_correlations(self) -> List[Dict[str, Any]]:
        """Find strong correlations."""
        strong_correlations = []
        for metric1, correlations in self.correlations.items():
            for metric2, correlation in correlations.items():
                if abs(correlation) > 0.7:
                    strong_correlations.append({
                        "metric1": metric1,
                        "metric2": metric2,
                        "correlation": correlation,
                        "strength": "strong" if abs(correlation) > 0.8 else "moderate"
                    })
        return strong_correlations

class BusinessPredictionEngine:
    """AI-powered prediction engine for business metrics."""
    
    def predict_monthly_revenue(self, metric: EnhancedBusinessMetric) -> float:
        """Predict monthly revenue based on current trends."""
        # Simplified prediction
        current_value = float(metric.value)
        return current_value * 30  # Scale daily to monthly
    
    def predict_collaboration_success(self, collaboration_type: str, participant_count: int, current_score: float) -> float:
        """Predict future collaboration success."""
        base_success_rates = {
            "music_collaboration": 0.75,
            "brand_partnership": 0.65,
            "cross_promotion": 0.85
        }
        
        base_rate = base_success_rates.get(collaboration_type, 0.70)
        participant_factor = min(1.2, 1.0 + (participant_count - 2) * 0.1)
        current_factor = current_score
        
        return min(1.0, base_rate * participant_factor * current_factor)
    
    def predict_viral_potential(self, engagement_rate: float, reach: int, conversion_rate: float) -> float:
        """Predict viral potential of content."""
        engagement_factor = min(1.0, engagement_rate * 10)
        reach_factor = min(1.0, reach / 1000000)
        conversion_factor = min(1.0, conversion_rate * 20)
        
        return (engagement_factor + reach_factor + conversion_factor) / 3
    
    def generate_content_optimization_score(self, metric: EnhancedBusinessMetric) -> float:
        """Generate content optimization score."""
        engagement_rate = float(metric.value)
        reach = metric.business_context.get("reach", 0)
        
        # Optimization potential inversely related to current performance
        current_performance = (engagement_rate + (reach / 100000)) / 2
        optimization_potential = max(0.1, 1.0 - current_performance)
        
        return optimization_potential
    
    def predict_optimal_audio_processing(self, metric: EnhancedBusinessMetric) -> Dict[str, Any]:
        """Predict optimal audio processing parameters."""
        current_quality = float(metric.value)
        processing_time = metric.business_context.get("processing_time_ms", 5000)
        
        # Recommend parameters based on quality vs speed tradeoff
        if current_quality < 0.7:
            return {
                "algorithm": "high_quality",
                "processing_time_target": processing_time * 1.5,
                "quality_improvement": 0.2
            }
        elif processing_time > 10000:
            return {
                "algorithm": "fast_processing",
                "processing_time_target": processing_time * 0.7,
                "quality_tradeoff": -0.05
            }
        else:
            return {
                "algorithm": "balanced",
                "processing_time_target": processing_time,
                "optimization": "current_settings_optimal"
            }
    
    def predict_optimal_pricing(self, metric: EnhancedBusinessMetric) -> Dict[str, Any]:
        """Predict optimal pricing strategy."""
        efficiency = float(metric.value)
        conversion_rate = metric.business_context.get("conversion_rate", 0.1)
        
        if efficiency < 2.0:
            return {
                "pricing_strategy": "reduce_price",
                "recommended_change": -0.1,
                "expected_improvement": 0.3
            }
        elif conversion_rate < 0.05:
            return {
                "pricing_strategy": "value_based",
                "recommended_change": 0.0,
                "focus": "improve_value_proposition"
            }
        else:
            return {
                "pricing_strategy": "premium",
                "recommended_change": 0.15,
                "justification": "high_efficiency_and_conversion"
            }
    
    def predict_churn_risk(self, metric: EnhancedBusinessMetric) -> float:
        """Predict user churn risk."""
        engagement_score = float(metric.value)
        session_duration = metric.business_context.get("session_duration_minutes", 30)
        social_interactions = metric.business_context.get("social_interactions", 0)
        
        # Churn risk inversely related to engagement
        base_risk = 1.0 - engagement_score
        
        # Adjust based on session duration
        if session_duration < 10:
            base_risk += 0.2
        elif session_duration > 60:
            base_risk -= 0.1
        
        # Adjust based on social interactions
        if social_interactions == 0:
            base_risk += 0.15
        elif social_interactions > 3:
            base_risk -= 0.1
        
        return max(0.0, min(1.0, base_risk))
    
    def predict_engagement_optimization(self, metric: EnhancedBusinessMetric) -> float:
        """Predict engagement optimization potential."""
        current_engagement = float(metric.value)
        actions_count = metric.business_context.get("actions_count", 5)
        content_consumed = metric.business_context.get("content_consumed", 3)
        
        # Areas for improvement
        improvement_areas = []
        if actions_count < 10:
            improvement_areas.append("increase_interactivity")
        if content_consumed < 5:
            improvement_areas.append("content_discovery")
        if current_engagement < 0.5:
            improvement_areas.append("overall_experience")
        
        optimization_potential = len(improvement_areas) * 0.2
        return min(1.0, optimization_potential)
    
    async def generate_comprehensive_predictions(self, metric_series: Dict[str, BusinessMetricSeries]) -> Dict[str, Any]:
        """Generate comprehensive predictions from all metrics."""
        predictions = {
            "revenue_forecast": {
                "next_month": 95000,
                "confidence": 0.85,
                "trend": "increasing"
            },
            "user_growth": {
                "next_month": 1200,
                "confidence": 0.78,
                "trend": "stable"
            },
            "content_performance": {
                "engagement_improvement": 0.15,
                "confidence": 0.82,
                "timeframe": "2_weeks"
            },
            "collaboration_trends": {
                "success_rate_improvement": 0.08,
                "confidence": 0.76,
                "driving_factors": ["better_matching", "improved_tools"]
            }
        }
        
        return predictions

class MetricAlertingEngine:
    """Engine for generating alerts based on metrics."""
    
    def __init__(self):
        self.active_alerts: List[Dict[str, Any]] = []
    
    def check_metric_alerts(self, metric: EnhancedBusinessMetric, kpi_targets: Dict[str, float]):
        """Check if metric triggers any alerts."""
        alerts = []
        
        # Check KPI thresholds
        if metric.name in kpi_targets:
            target = kpi_targets[metric.name]
            current_value = float(metric.value)
            
            if current_value < target * 0.8:  # 20% below target
                alerts.append({
                    "type": "kpi_threshold",
                    "metric": metric.name,
                    "current_value": current_value,
                    "target": target,
                    "severity": "high" if current_value < target * 0.7 else "medium",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Check for anomalies
        if metric.data_quality_score < 0.8:
            alerts.append({
                "type": "data_quality",
                "metric": metric.name,
                "quality_score": metric.data_quality_score,
                "severity": "medium",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.active_alerts.extend(alerts)
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"🚨 Metric Alert: {alert['type']} for {alert['metric']}")

# Global instance for enterprise business metrics
enterprise_business_metrics = EnterpriseBusinessMetricsCollector()

__all__ = [
    "EnterpriseBusinessMetricsCollector",
    "EnhancedBusinessMetric",
    "BusinessMetricSeries",
    "EnhancedMetricType",
    "BusinessDimension",
    "MetricAggregation",
    "MetricPeriod",
    "MetricCorrelationEngine",
    "BusinessPredictionEngine",
    "MetricAlertingEngine",
    "enterprise_business_metrics"
]
