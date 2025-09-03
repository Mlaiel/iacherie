"""Performance Tracker - Monetization Performance Monitoring
==========================================================

Advanced performance tracking system for monitoring monetization
metrics, KPIs, and system performance across all revenue streams.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import uuid
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class PerformanceMetric(str, Enum):
    """Performance metric types."""
    CONVERSION_RATE = "conversion_rate"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    CHURN_RATE = "churn_rate"
    RETENTION_RATE = "retention_rate"
    AVERAGE_ORDER_VALUE = "average_order_value"
    PAYMENT_SUCCESS_RATE = "payment_success_rate"
    SUBSCRIPTION_GROWTH = "subscription_growth"
    REVENUE_PER_USER = "revenue_per_user"
    TIME_TO_FIRST_PURCHASE = "time_to_first_purchase"
    MARKETPLACE_COMMISSION = "marketplace_commission"


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    URGENT = "urgent"


class MetricStatus(str, Enum):
    """Metric status indicators."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class PerformanceDataPoint:
    """Performance metric data point."""
    metric: PerformanceMetric
    value: Union[float, Decimal, int]
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert notification."""
    id: str
    metric: PerformanceMetric
    level: AlertLevel
    message: str
    current_value: Union[float, Decimal, int]
    threshold_value: Union[float, Decimal, int]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MetricThreshold:
    """Performance metric threshold configuration."""
    metric: PerformanceMetric
    warning_threshold: Union[float, Decimal, int]
    critical_threshold: Union[float, Decimal, int]
    comparison_operator: str  # "gt", "lt", "eq"
    enabled: bool = True


@dataclass
class PerformanceDashboard:
    """Performance dashboard data."""
    timestamp: datetime
    overall_health_score: float
    metric_statuses: Dict[str, MetricStatus]
    key_metrics: List[PerformanceDataPoint]
    active_alerts: List[PerformanceAlert]
    trends: Dict[str, Any]
    recommendations: List[str]


class PerformanceTracker:
    """Advanced monetization performance tracking system."""
    
    def __init__(self, retention_days: int = 90):
        """Initialize performance tracker.
        
        Args:
            retention_days: Days to retain performance data
        """
        self.retention_days = retention_days
        self.data_points: List[PerformanceDataPoint] = []
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.thresholds: Dict[PerformanceMetric, MetricThreshold] = {}
        
        # Circular buffer for real-time metrics (last 1000 points per metric)
        self.real_time_buffer: Dict[PerformanceMetric, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        # Performance tracking state
        self.tracking_active = True
        self.alert_cooldown: Dict[str, datetime] = {}
        
        logger.info("Performance tracker initialized")
    
    def _initialize_default_thresholds(self) -> None:
        """Initialize default performance thresholds."""
        default_thresholds = {
            PerformanceMetric.CONVERSION_RATE: MetricThreshold(
                metric=PerformanceMetric.CONVERSION_RATE,
                warning_threshold=0.02,  # 2%
                critical_threshold=0.01,  # 1%
                comparison_operator="lt"  # Alert if below threshold
            ),
            PerformanceMetric.CHURN_RATE: MetricThreshold(
                metric=PerformanceMetric.CHURN_RATE,
                warning_threshold=0.10,  # 10%
                critical_threshold=0.20,  # 20%
                comparison_operator="gt"  # Alert if above threshold
            ),
            PerformanceMetric.PAYMENT_SUCCESS_RATE: MetricThreshold(
                metric=PerformanceMetric.PAYMENT_SUCCESS_RATE,
                warning_threshold=0.95,  # 95%
                critical_threshold=0.90,  # 90%
                comparison_operator="lt"  # Alert if below threshold
            ),
            PerformanceMetric.CUSTOMER_LIFETIME_VALUE: MetricThreshold(
                metric=PerformanceMetric.CUSTOMER_LIFETIME_VALUE,
                warning_threshold=100.0,
                critical_threshold=50.0,
                comparison_operator="lt"
            ),
            PerformanceMetric.RETENTION_RATE: MetricThreshold(
                metric=PerformanceMetric.RETENTION_RATE,
                warning_threshold=0.70,  # 70%
                critical_threshold=0.50,  # 50%
                comparison_operator="lt"
            )
        }
        
        self.thresholds.update(default_thresholds)
    
    async def record_metric(
        self,
        metric: PerformanceMetric,
        value: Union[float, Decimal, int],
        dimensions: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> PerformanceDataPoint:
        """Record a performance metric data point.
        
        Args:
            metric: Performance metric type
            value: Metric value
            dimensions: Metric dimensions (e.g., platform, region)
            metadata: Additional metadata
            timestamp: Data point timestamp
            
        Returns:
            Recorded performance data point
        """
        try:
            if not self.tracking_active:
                logger.warning("Performance tracking is disabled")
                return None
            
            data_point = PerformanceDataPoint(
                metric=metric,
                value=value,
                timestamp=timestamp or datetime.now(),
                dimensions=dimensions or {},
                metadata=metadata or {}
            )
            
            # Store in main data collection
            self.data_points.append(data_point)
            
            # Store in real-time buffer
            self.real_time_buffer[metric].append(data_point)
            
            # Check thresholds and generate alerts
            await self._check_thresholds(data_point)
            
            # Clean old data periodically
            if len(self.data_points) % 1000 == 0:
                await self._cleanup_old_data()
            
            logger.debug(f"Metric recorded: {metric.value} = {value}")
            return data_point
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            raise
    
    async def _check_thresholds(self, data_point: PerformanceDataPoint) -> None:
        """Check if metric exceeds configured thresholds.
        
        Args:
            data_point: Performance data point to check
        """
        try:
            threshold = self.thresholds.get(data_point.metric)
            if not threshold or not threshold.enabled:
                return
            
            # Check if we're in cooldown period for this metric
            cooldown_key = f"{data_point.metric.value}_{threshold.comparison_operator}"
            if cooldown_key in self.alert_cooldown:
                if datetime.now() - self.alert_cooldown[cooldown_key] < timedelta(minutes=5):
                    return  # Still in cooldown
            
            # Determine alert level based on thresholds
            alert_level = None
            threshold_exceeded = None
            
            if threshold.comparison_operator == "gt":
                if data_point.value > threshold.critical_threshold:
                    alert_level = AlertLevel.CRITICAL
                    threshold_exceeded = threshold.critical_threshold
                elif data_point.value > threshold.warning_threshold:
                    alert_level = AlertLevel.WARNING
                    threshold_exceeded = threshold.warning_threshold
            elif threshold.comparison_operator == "lt":
                if data_point.value < threshold.critical_threshold:
                    alert_level = AlertLevel.CRITICAL
                    threshold_exceeded = threshold.critical_threshold
                elif data_point.value < threshold.warning_threshold:
                    alert_level = AlertLevel.WARNING
                    threshold_exceeded = threshold.warning_threshold
            
            # Generate alert if threshold exceeded
            if alert_level and threshold_exceeded is not None:
                await self._generate_alert(
                    data_point.metric,
                    alert_level,
                    data_point.value,
                    threshold_exceeded,
                    data_point.timestamp
                )
                
                # Set cooldown
                self.alert_cooldown[cooldown_key] = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to check thresholds: {e}")
    
    async def _generate_alert(
        self,
        metric: PerformanceMetric,
        level: AlertLevel,
        current_value: Union[float, Decimal, int],
        threshold_value: Union[float, Decimal, int],
        timestamp: datetime
    ) -> PerformanceAlert:
        """Generate performance alert.
        
        Args:
            metric: Performance metric
            level: Alert level
            current_value: Current metric value
            threshold_value: Threshold that was exceeded
            timestamp: Alert timestamp
            
        Returns:
            Generated alert
        """
        try:
            alert_id = str(uuid.uuid4())
            
            # Generate alert message
            if metric == PerformanceMetric.CONVERSION_RATE:
                message = f"Conversion rate has dropped to {current_value:.2%} (threshold: {threshold_value:.2%})"
            elif metric == PerformanceMetric.CHURN_RATE:
                message = f"Churn rate has increased to {current_value:.2%} (threshold: {threshold_value:.2%})"
            elif metric == PerformanceMetric.PAYMENT_SUCCESS_RATE:
                message = f"Payment success rate has dropped to {current_value:.2%} (threshold: {threshold_value:.2%})"
            else:
                message = f"{metric.value.replace('_', ' ').title()} alert: {current_value} (threshold: {threshold_value})"
            
            alert = PerformanceAlert(
                id=alert_id,
                metric=metric,
                level=level,
                message=message,
                current_value=current_value,
                threshold_value=threshold_value,
                timestamp=timestamp
            )
            
            self.alerts[alert_id] = alert
            
            logger.warning(f"Performance alert generated: {level.value} - {message}")
            return alert
            
        except Exception as e:
            logger.error(f"Failed to generate alert: {e}")
            raise
    
    async def get_metric_trend(
        self,
        metric: PerformanceMetric,
        hours: int = 24,
        dimensions: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Get trend analysis for a specific metric.
        
        Args:
            metric: Performance metric
            hours: Hours of historical data to analyze
            dimensions: Dimension filters
            
        Returns:
            Trend analysis data
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter data points
            filtered_points = [
                point for point in self.data_points
                if (point.metric == metric and 
                    point.timestamp >= cutoff_time and
                    (not dimensions or all(
                        point.dimensions.get(k) == v for k, v in dimensions.items()
                    )))
            ]
            
            if not filtered_points:
                return {"error": "No data available for trend analysis"}
            
            # Sort by timestamp
            filtered_points.sort(key=lambda p: p.timestamp)
            
            # Calculate trend statistics
            values = [float(point.value) for point in filtered_points]
            
            trend_data = {
                "metric": metric.value,
                "period_hours": hours,
                "data_points": len(values),
                "current_value": values[-1] if values else 0,
                "min_value": min(values) if values else 0,
                "max_value": max(values) if values else 0,
                "average_value": statistics.mean(values) if values else 0,
                "median_value": statistics.median(values) if values else 0,
                "trend_direction": self._calculate_trend_direction(values),
                "volatility": statistics.stdev(values) if len(values) > 1 else 0,
                "timestamps": [point.timestamp.isoformat() for point in filtered_points[-20:]]  # Last 20 points
            }
            
            # Calculate percentage change
            if len(values) >= 2:
                trend_data["percentage_change"] = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
            else:
                trend_data["percentage_change"] = 0
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Failed to get metric trend: {e}")
            return {"error": str(e)}
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate overall trend direction.
        
        Args:
            values: List of metric values
            
        Returns:
            Trend direction string
        """
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation based on first and last values
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.05:  # 5% increase
            return "increasing"
        elif second_avg < first_avg * 0.95:  # 5% decrease
            return "decreasing"
        else:
            return "stable"
    
    async def calculate_health_score(self) -> float:
        """Calculate overall monetization health score.
        
        Returns:
            Health score between 0.0 and 1.0
        """
        try:
            # Get latest values for key metrics
            key_metrics = [
                PerformanceMetric.CONVERSION_RATE,
                PerformanceMetric.PAYMENT_SUCCESS_RATE,
                PerformanceMetric.RETENTION_RATE,
                PerformanceMetric.CUSTOMER_LIFETIME_VALUE
            ]
            
            metric_scores = []
            
            for metric in key_metrics:
                latest_value = await self._get_latest_metric_value(metric)
                if latest_value is None:
                    continue
                
                threshold = self.thresholds.get(metric)
                if not threshold:
                    continue
                
                # Calculate score based on threshold comparison
                if threshold.comparison_operator == "gt":
                    # Higher is better
                    if latest_value >= threshold.warning_threshold:
                        score = 1.0
                    elif latest_value >= threshold.critical_threshold:
                        score = 0.6
                    else:
                        score = 0.2
                else:  # "lt" - Lower is better
                    # Invert for metrics where lower is better
                    if latest_value <= threshold.critical_threshold:
                        score = 1.0
                    elif latest_value <= threshold.warning_threshold:
                        score = 0.6
                    else:
                        score = 0.2
                
                metric_scores.append(score)
            
            # Calculate overall health score
            if metric_scores:
                health_score = statistics.mean(metric_scores)
            else:
                health_score = 0.5  # Default neutral score
            
            return health_score
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.0
    
    async def _get_latest_metric_value(self, metric: PerformanceMetric) -> Optional[Union[float, Decimal, int]]:
        """Get latest value for a specific metric.
        
        Args:
            metric: Performance metric
            
        Returns:
            Latest metric value if available
        """
        try:
            recent_points = [
                point for point in self.data_points
                if point.metric == metric and point.timestamp >= datetime.now() - timedelta(hours=1)
            ]
            
            if recent_points:
                # Return most recent value
                latest_point = max(recent_points, key=lambda p: p.timestamp)
                return latest_point.value
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest metric value: {e}")
            return None
    
    async def generate_dashboard(self) -> PerformanceDashboard:
        """Generate performance dashboard data.
        
        Returns:
            Performance dashboard data
        """
        try:
            # Calculate health score
            health_score = await self.calculate_health_score()
            
            # Get metric statuses
            metric_statuses = {}
            key_metrics = []
            
            for metric in PerformanceMetric:
                latest_value = await self._get_latest_metric_value(metric)
                if latest_value is not None:
                    # Determine status based on thresholds
                    threshold = self.thresholds.get(metric)
                    if threshold:
                        if threshold.comparison_operator == "gt":
                            if latest_value < threshold.critical_threshold:
                                status = MetricStatus.CRITICAL
                            elif latest_value < threshold.warning_threshold:
                                status = MetricStatus.WARNING
                            else:
                                status = MetricStatus.HEALTHY
                        else:  # "lt"
                            if latest_value > threshold.critical_threshold:
                                status = MetricStatus.CRITICAL
                            elif latest_value > threshold.warning_threshold:
                                status = MetricStatus.WARNING
                            else:
                                status = MetricStatus.HEALTHY
                    else:
                        status = MetricStatus.UNKNOWN
                    
                    metric_statuses[metric.value] = status
                    
                    # Add to key metrics if has recent data
                    if latest_value is not None:
                        key_metrics.append(PerformanceDataPoint(
                            metric=metric,
                            value=latest_value,
                            timestamp=datetime.now()
                        ))
            
            # Get active alerts
            active_alerts = [
                alert for alert in self.alerts.values()
                if not alert.resolved and alert.timestamp >= datetime.now() - timedelta(hours=24)
            ]
            
            # Generate trends for key metrics
            trends = {}
            for metric in [PerformanceMetric.CONVERSION_RATE, PerformanceMetric.REVENUE_PER_USER]:
                trend_data = await self.get_metric_trend(metric, hours=24)
                if "error" not in trend_data:
                    trends[metric.value] = trend_data
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                health_score, metric_statuses, active_alerts
            )
            
            dashboard = PerformanceDashboard(
                timestamp=datetime.now(),
                overall_health_score=health_score,
                metric_statuses=metric_statuses,
                key_metrics=key_metrics,
                active_alerts=active_alerts,
                trends=trends,
                recommendations=recommendations
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")
            raise
    
    async def _generate_performance_recommendations(
        self,
        health_score: float,
        metric_statuses: Dict[str, MetricStatus],
        active_alerts: List[PerformanceAlert]
    ) -> List[str]:
        """Generate performance recommendations.
        
        Args:
            health_score: Overall health score
            metric_statuses: Current metric statuses
            active_alerts: Active performance alerts
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Health score based recommendations
            if health_score < 0.3:
                recommendations.append(
                    "Critical: Overall monetization health is poor. Immediate action required across multiple metrics."
                )
            elif health_score < 0.6:
                recommendations.append(
                    "Warning: Monetization performance needs attention. Review underperforming metrics."
                )
            
            # Metric-specific recommendations
            critical_metrics = [
                metric for metric, status in metric_statuses.items()
                if status == MetricStatus.CRITICAL
            ]
            
            if critical_metrics:
                recommendations.append(
                    f"Address critical metrics: {', '.join(critical_metrics)}"
                )
            
            # Alert-based recommendations
            if len(active_alerts) > 5:
                recommendations.append(
                    "Multiple active alerts detected. Consider implementing automated response workflows."
                )
            
            # Specific metric recommendations
            if metric_statuses.get("conversion_rate") == MetricStatus.CRITICAL:
                recommendations.append(
                    "Low conversion rate detected. Review pricing, user onboarding, and payment flow."
                )
            
            if metric_statuses.get("churn_rate") == MetricStatus.CRITICAL:
                recommendations.append(
                    "High churn rate detected. Implement retention campaigns and improve customer success."
                )
            
            if metric_statuses.get("payment_success_rate") == MetricStatus.CRITICAL:
                recommendations.append(
                    "Low payment success rate. Check payment gateway configuration and fraud detection settings."
                )
            
            # Default recommendation if no issues detected
            if not recommendations and health_score > 0.8:
                recommendations.append(
                    "Monetization performance is healthy. Consider A/B testing new pricing strategies for optimization."
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Unable to generate recommendations due to processing error."]
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old performance data beyond retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Remove old data points
            self.data_points = [
                point for point in self.data_points
                if point.timestamp >= cutoff_date
            ]
            
            # Remove old resolved alerts
            old_alert_ids = [
                alert_id for alert_id, alert in self.alerts.items()
                if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_date
            ]
            
            for alert_id in old_alert_ids:
                del self.alerts[alert_id]
            
            logger.info(f"Cleaned up old data: {len(old_alert_ids)} old alerts removed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve a performance alert.
        
        Args:
            alert_id: Alert identifier
            resolved_by: Who resolved the alert
            
        Returns:
            True if alert was resolved
        """
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            if "resolved_by" not in alert.metadata:
                alert.metadata = {}
            alert.metadata["resolved_by"] = resolved_by
            
            logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def set_metric_threshold(
        self,
        metric: PerformanceMetric,
        warning_threshold: Union[float, Decimal, int],
        critical_threshold: Union[float, Decimal, int],
        comparison_operator: str = "lt"
    ) -> bool:
        """Set threshold for a performance metric.
        
        Args:
            metric: Performance metric
            warning_threshold: Warning threshold value
            critical_threshold: Critical threshold value
            comparison_operator: Comparison operator ("gt", "lt", "eq")
            
        Returns:
            True if threshold was set
        """
        try:
            threshold = MetricThreshold(
                metric=metric,
                warning_threshold=warning_threshold,
                critical_threshold=critical_threshold,
                comparison_operator=comparison_operator
            )
            
            self.thresholds[metric] = threshold
            
            logger.info(f"Threshold set for {metric.value}: {comparison_operator} {warning_threshold}/{critical_threshold}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set metric threshold: {e}")
            return False
    
    def get_alert(self, alert_id: str) -> Optional[PerformanceAlert]:
        """Get performance alert by ID.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            Performance alert if found
        """
        return self.alerts.get(alert_id)
    
    def list_active_alerts(self) -> List[PerformanceAlert]:
        """List all active performance alerts.
        
        Returns:
            List of active alerts
        """
        return [
            alert for alert in self.alerts.values()
            if not alert.resolved
        ]