"""📊 Business Metrics - Advanced KPI Tracking System
=================================================

Enterprise-grade business metrics collection and analysis for the Ainflue platform.
Tracks revenue, user engagement, content performance, and licensing analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of business metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricPeriod(Enum):
    """Metric aggregation periods"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class BusinessMetric:
    """Individual business metric"""
    name: str
    value: Union[int, float, Decimal]
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Aggregated metric data"""
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
        """Initialize business metrics collector"""
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
__all__ = [
    "BusinessMetricsCollector",
    "BusinessMetric",
    "MetricAggregation",
    "MetricType",
    "MetricPeriod"
]
