"""Business Metrics Aggregator - Real-Time for Ainflue Platform

import asyncio

Real-time business metrics aggregation with intelligent dashboards,
KPI tracking, and automated alerts for Ainflue business performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of business metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    REVENUE = "revenue"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"


class AggregationPeriod(Enum):
    """Aggregation time periods"""
    REAL_TIME = "real_time"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class MetricDefinition:
    """Definition of a business metric"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    aggregation_periods: List[AggregationPeriod]
    business_importance: str = "medium"
    alert_thresholds: Optional[Dict[str, float]] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class MetricValue:
    """A metric value with metadata"""
    metric_name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    metric_name: str
    period: AggregationPeriod
    start_time: datetime
    end_time: datetime
    value: float
    count: int
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class BusinessAlert:
    """Business metric alert"""
    alert_id: str
    metric_name: str
    threshold_type: str
    threshold_value: float
    actual_value: float
    severity: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.utcnow)


class BusinessMetricsAggregator:
    """
    Real-time business metrics aggregator for Ainflue platform
    Tracks KPIs, generates insights, and provides automated alerting
    """
    
    def __init__(self, buffer_size -> None: int = 10000) -> None:
        self.buffer_size = buffer_size
        self.metric_definitions = self._initialize_metric_definitions()
        self.raw_metrics: deque = deque(maxlen=buffer_size)
        self.aggregated_metrics: Dict[str, Dict[str, AggregatedMetric]] = defaultdict(dict)
        self.alert_handlers: List[Callable] = []
        self.active_alerts: List[BusinessAlert] = []
        
        logger.info("BusinessMetricsAggregator initialized for Ainflue platform")
    
    def _initialize_metric_definitions(self) -> Dict[str, MetricDefinition]:
        """Initialize Ainflue business metric definitions"""
        
        definitions = {}
        
        # Content metrics
        definitions["content_uploads"] = MetricDefinition(
            name="content_uploads",
            metric_type=MetricType.COUNTER,
            description="Number of content uploads",
            unit="count",
            aggregation_periods=[AggregationPeriod.REAL_TIME, AggregationPeriod.HOUR, AggregationPeriod.DAY],
            business_importance="high",
            alert_thresholds={"min_hourly": 10, "max_hourly": 1000},
            tags=["content", "upload", "user_activity"]
        )
        
        definitions["content_processing_time"] = MetricDefinition(
            name="content_processing_time",
            metric_type=MetricType.HISTOGRAM,
            description="Average content processing time",
            unit="seconds",
            aggregation_periods=[AggregationPeriod.MINUTE, AggregationPeriod.HOUR],
            business_importance="high",
            alert_thresholds={"max_avg": 300},  # 5 minutes max
            tags=["content", "processing", "performance"]
        )
        
        # User engagement metrics
        definitions["active_users"] = MetricDefinition(
            name="active_users",
            metric_type=MetricType.GAUGE,
            description="Number of active users",
            unit="count",
            aggregation_periods=[AggregationPeriod.REAL_TIME, AggregationPeriod.HOUR, AggregationPeriod.DAY],
            business_importance="critical",
            alert_thresholds={"min_hourly": 50},
            tags=["users", "engagement", "activity"]
        )
        
        definitions["collaboration_requests"] = MetricDefinition(
            name="collaboration_requests",
            metric_type=MetricType.COUNTER,
            description="Number of collaboration requests",
            unit="count",
            aggregation_periods=[AggregationPeriod.HOUR, AggregationPeriod.DAY],
            business_importance="high",
            tags=["collaboration", "social", "matching"]
        )
        
        definitions["collaboration_success_rate"] = MetricDefinition(
            name="collaboration_success_rate",
            metric_type=MetricType.CONVERSION,
            description="Rate of successful collaborations",
            unit="percentage",
            aggregation_periods=[AggregationPeriod.HOUR, AggregationPeriod.DAY],
            business_importance="critical",
            alert_thresholds={"min_daily": 0.6},  # 60% minimum
            tags=["collaboration", "conversion", "success"]
        )
        
        # Revenue metrics
        definitions["revenue_generated"] = MetricDefinition(
            name="revenue_generated",
            metric_type=MetricType.REVENUE,
            description="Total revenue generated",
            unit="USD",
            aggregation_periods=[AggregationPeriod.HOUR, AggregationPeriod.DAY, AggregationPeriod.MONTH],
            business_importance="critical",
            alert_thresholds={"min_daily": 1000},
            tags=["revenue", "monetization", "business"]
        )
        
        definitions["average_transaction_value"] = MetricDefinition(
            name="average_transaction_value",
            metric_type=MetricType.GAUGE,
            description="Average transaction value",
            unit="USD",
            aggregation_periods=[AggregationPeriod.HOUR, AggregationPeriod.DAY],
            business_importance="high",
            tags=["revenue", "transaction", "value"]
        )
        
        # AI/ML metrics
        definitions["ai_processing_requests"] = MetricDefinition(
            name="ai_processing_requests",
            metric_type=MetricType.COUNTER,
            description="Number of AI processing requests",
            unit="count",
            aggregation_periods=[AggregationPeriod.MINUTE, AggregationPeriod.HOUR],
            business_importance="high",
            tags=["ai", "processing", "ml"]
        )
        
        definitions["ai_quality_score"] = MetricDefinition(
            name="ai_quality_score",
            metric_type=MetricType.GAUGE,
            description="Average AI processing quality score",
            unit="score",
            aggregation_periods=[AggregationPeriod.HOUR, AggregationPeriod.DAY],
            business_importance="high",
            alert_thresholds={"min_daily": 0.8},
            tags=["ai", "quality", "performance"]
        )
        
        # System performance metrics
        definitions["api_response_time"] = MetricDefinition(
            name="api_response_time",
            metric_type=MetricType.HISTOGRAM,
            description="API response time",
            unit="milliseconds",
            aggregation_periods=[AggregationPeriod.MINUTE, AggregationPeriod.HOUR],
            business_importance="high",
            alert_thresholds={"max_avg": 500},  # 500ms max
            tags=["api", "performance", "latency"]
        )
        
        definitions["error_rate"] = MetricDefinition(
            name="error_rate",
            metric_type=MetricType.CONVERSION,
            description="System error rate",
            unit="percentage",
            aggregation_periods=[AggregationPeriod.MINUTE, AggregationPeriod.HOUR],
            business_importance="critical",
            alert_thresholds={"max_hourly": 0.05},  # 5% max
            tags=["errors", "reliability", "system"]
        )
        
        return definitions
    
    async def record_metric_from_event(self, event_data -> None: Dict[str, Any]) -> None:
        """Extract and record metrics from event data"""
        
        event_type = event_data.get("event_type", "")
        timestamp = self._parse_timestamp(event_data.get("timestamp"))
        payload = event_data.get("payload", {})
        
        # Content upload metrics
        if event_type == "content.upload.completed":
            await self.record_metric("content_uploads", 1, timestamp, {
                "user_tier": payload.get("user_tier", "unknown"),
                "content_type": payload.get("content_type", "unknown")
            })
            
            # Processing time if available
            processing_time = payload.get("processing_time")
            if processing_time:
                await self.record_metric("content_processing_time", processing_time, timestamp)
        
        # User activity metrics
        elif event_type in ["user.login", "user.activity"]:
            await self.record_metric("active_users", 1, timestamp, {
                "user_tier": payload.get("user_tier", "unknown")
            })
        
        # Collaboration metrics
        elif event_type == "collaboration.requested":
            await self.record_metric("collaboration_requests", 1, timestamp, {
                "collaboration_type": payload.get("collaboration_type", "unknown")
            })
        
        elif event_type == "collaboration.completed":
            success = payload.get("success", False)
            await self.record_metric("collaboration_success_rate", 1 if success else 0, timestamp)
        
        # Revenue metrics
        elif event_type in ["revenue.generated", "payment.completed"]:
            amount = payload.get("amount", 0)
            await self.record_metric("revenue_generated", amount, timestamp, {
                "payment_method": payload.get("payment_method", "unknown"),
                "user_tier": payload.get("user_tier", "unknown")
            })
            
            await self.record_metric("average_transaction_value", amount, timestamp)
        
        # AI processing metrics
        elif event_type == "ai.processing.started":
            await self.record_metric("ai_processing_requests", 1, timestamp, {
                "processing_type": payload.get("processing_type", "unknown")
            })
        
        elif event_type == "ai.processing.completed":
            quality_score = payload.get("quality_score")
            if quality_score:
                await self.record_metric("ai_quality_score", quality_score, timestamp)
        
        # System metrics
        elif event_type.startswith("api."):
            response_time = payload.get("response_time")
            if response_time:
                await self.record_metric("api_response_time", response_time, timestamp, {
                    "endpoint": payload.get("endpoint", "unknown"),
                    "method": payload.get("method", "unknown")
                })
            
            if payload.get("error"):
                await self.record_metric("error_rate", 1, timestamp)
            else:
                await self.record_metric("error_rate", 0, timestamp)
    
    async def record_metric(self, metric_name -> None: str, value -> None: float, 
                          timestamp -> None: Optional[datetime] = None,
                          tags -> None: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value"""
        
        if metric_name not in self.metric_definitions:
            logger.warning(f"Unknown metric: {metric_name}")
            return
        
        timestamp = timestamp or datetime.utcnow()
        tags = tags or {}
        
        metric_value = MetricValue(
            metric_name=metric_name,
            value=value,
            timestamp=timestamp,
            tags=tags
        )
        
        self.raw_metrics.append(metric_value)
        
        # Trigger real-time aggregation
        await self._update_real_time_aggregations(metric_value)
        
        # Check for alerts
        await self._check_metric_alerts(metric_name, value, tags)
        
        logger.debug(f"Recorded metric {metric_name}: {value}")
    
    async def _update_real_time_aggregations(self, metric_value -> None: MetricValue) -> None:
        """Update real-time aggregations for a metric"""
        
        metric_def = self.metric_definitions[metric_value.metric_name]
        
        if AggregationPeriod.REAL_TIME in metric_def.aggregation_periods:
            # Update real-time aggregation
            key = f"{metric_value.metric_name}_real_time"
            
            if key not in self.aggregated_metrics:
                self.aggregated_metrics[key] = {}
            
            now = datetime.utcnow()
            period_key = now.strftime("%Y-%m-%d_%H:%M")
            
            if period_key not in self.aggregated_metrics[key]:
                self.aggregated_metrics[key][period_key] = AggregatedMetric(
                    metric_name=metric_value.metric_name,
                    period=AggregationPeriod.REAL_TIME,
                    start_time=now.replace(second=0, microsecond=0),
                    end_time=now.replace(second=0, microsecond=0) + timedelta(minutes=1),
                    value=0,
                    count=0,
                    tags=metric_value.tags
                )
            
            agg_metric = self.aggregated_metrics[key][period_key]
            
            # Update aggregation based on metric type
            if metric_def.metric_type in [MetricType.COUNTER, MetricType.REVENUE]:
                agg_metric.value += metric_value.value
            elif metric_def.metric_type == MetricType.GAUGE:
                agg_metric.value = metric_value.value  # Latest value for gauges
            elif metric_def.metric_type == MetricType.HISTOGRAM:
                # Update running average
                total = agg_metric.value * agg_metric.count + metric_value.value
                agg_metric.count += 1
                agg_metric.value = total / agg_metric.count
                
                # Update min/max
                if agg_metric.min_value is None or metric_value.value < agg_metric.min_value:
                    agg_metric.min_value = metric_value.value
                if agg_metric.max_value is None or metric_value.value > agg_metric.max_value:
                    agg_metric.max_value = metric_value.value
            
            agg_metric.count += 1
    
    async def get_aggregated_metrics(self, 
                                   metric_names: Optional[List[str]] = None,
                                   period: AggregationPeriod = AggregationPeriod.HOUR,
                                   start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None) -> List[AggregatedMetric]:
        """Get aggregated metrics for specified period"""
        
        end_time = end_time or datetime.utcnow()
        start_time = start_time or end_time - timedelta(hours=24)
        
        metrics_to_query = metric_names or list(self.metric_definitions.keys())
        results = []
        
        for metric_name in metrics_to_query:
            if metric_name not in self.metric_definitions:
                continue
            
            metric_def = self.metric_definitions[metric_name]
            
            if period not in metric_def.aggregation_periods:
                continue
            
            # Calculate aggregation from raw metrics
            aggregated = await self._calculate_aggregation(metric_name, period, start_time, end_time)
            results.extend(aggregated)
        
        return results
    
    async def _calculate_aggregation(self, metric_name: str, period: AggregationPeriod,
                                   start_time: datetime, end_time: datetime) -> List[AggregatedMetric]:
        """Calculate aggregation for a metric over time period"""
        
        metric_def = self.metric_definitions[metric_name]
        
        # Filter relevant metrics
        relevant_metrics = [
            m for m in self.raw_metrics
            if (m.metric_name == metric_name and 
                start_time <= m.timestamp <= end_time)
        ]
        
        if not relevant_metrics:
            return []
        
        # Group by time period
        period_groups = defaultdict(list)
        
        for metric in relevant_metrics:
            period_key = self._get_period_key(metric.timestamp, period)
            period_groups[period_key].append(metric)
        
        # Calculate aggregations
        results = []
        for period_key, metrics in period_groups.items():
            period_start, period_end = self._get_period_bounds(period_key, period)
            
            if metric_def.metric_type in [MetricType.COUNTER, MetricType.REVENUE]:
                # Sum for counters and revenue
                total_value = sum(m.value for m in metrics)
                agg_metric = AggregatedMetric(
                    metric_name=metric_name,
                    period=period,
                    start_time=period_start,
                    end_time=period_end,
                    value=total_value,
                    count=len(metrics)
                )
            
            elif metric_def.metric_type == MetricType.GAUGE:
                # Latest value for gauges
                latest_metric = max(metrics, key=lambda m: m.timestamp)
                agg_metric = AggregatedMetric(
                    metric_name=metric_name,
                    period=period,
                    start_time=period_start,
                    end_time=period_end,
                    value=latest_metric.value,
                    count=len(metrics)
                )
            
            elif metric_def.metric_type in [MetricType.HISTOGRAM, MetricType.CONVERSION]:
                # Average for histograms and conversions
                values = [m.value for m in metrics]
                avg_value = sum(values) / len(values)
                agg_metric = AggregatedMetric(
                    metric_name=metric_name,
                    period=period,
                    start_time=period_start,
                    end_time=period_end,
                    value=avg_value,
                    count=len(metrics),
                    min_value=min(values),
                    max_value=max(values),
                    avg_value=avg_value
                )
            
            results.append(agg_metric)
        
        return results
    
    def _get_period_key(self, timestamp: datetime, period: AggregationPeriod) -> str:
        """Get period key for grouping"""
        
        if period == AggregationPeriod.MINUTE:
            return timestamp.strftime("%Y-%m-%d_%H:%M")
        elif period == AggregationPeriod.HOUR:
            return timestamp.strftime("%Y-%m-%d_%H")
        elif period == AggregationPeriod.DAY:
            return timestamp.strftime("%Y-%m-%d")
        elif period == AggregationPeriod.WEEK:
            year, week, _ = timestamp.isocalendar()
            return f"{year}-W{week:02d}"
        elif period == AggregationPeriod.MONTH:
            return timestamp.strftime("%Y-%m")
        else:
            return timestamp.strftime("%Y-%m-%d_%H:%M")
    
    def _get_period_bounds(self, period_key: str, period: AggregationPeriod) -> Tuple[datetime, datetime]:
        """Get start and end time for period key"""
        
        if period == AggregationPeriod.MINUTE:
            start = datetime.strptime(period_key, "%Y-%m-%d_%H:%M")
            end = start + timedelta(minutes=1)
        elif period == AggregationPeriod.HOUR:
            start = datetime.strptime(period_key, "%Y-%m-%d_%H")
            end = start + timedelta(hours=1)
        elif period == AggregationPeriod.DAY:
            start = datetime.strptime(period_key, "%Y-%m-%d")
            end = start + timedelta(days=1)
        elif period == AggregationPeriod.WEEK:
            year, week = period_key.split("-W")
            start = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
            end = start + timedelta(weeks=1)
        elif period == AggregationPeriod.MONTH:
            start = datetime.strptime(period_key, "%Y-%m")
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        else:
            start = datetime.strptime(period_key, "%Y-%m-%d_%H:%M")
            end = start + timedelta(minutes=1)
        
        return start, end
    
    async def _check_metric_alerts(self, metric_name -> None: str, value -> None: float, tags -> None: Dict[str, str]) -> None:
        """Check if metric value triggers any alerts"""
        
        metric_def = self.metric_definitions.get(metric_name)
        if not metric_def or not metric_def.alert_thresholds:
            return
        
        thresholds = metric_def.alert_thresholds
        
        for threshold_type, threshold_value in thresholds.items():
            alert_triggered = False
            severity = "warning"
            
            if threshold_type.startswith("min_"):
                if value < threshold_value:
                    alert_triggered = True
                    severity = "warning" if metric_def.business_importance != "critical" else "critical"
            
            elif threshold_type.startswith("max_"):
                if value > threshold_value:
                    alert_triggered = True
                    severity = "critical"
            
            if alert_triggered:
                alert = BusinessAlert(
                    alert_id=f"alert_{metric_name}_{int(time.time())}",
                    metric_name=metric_name,
                    threshold_type=threshold_type,
                    threshold_value=threshold_value,
                    actual_value=value,
                    severity=severity,
                    message=f"Metric {metric_name} {threshold_type} threshold breached: {value} vs {threshold_value}"
                )
                
                self.active_alerts.append(alert)
                await self._trigger_alert(alert)
    
    async def _trigger_alert(self, alert -> None: BusinessAlert) -> None:
        """Trigger alert to registered handlers"""
        
        logger.warning(f"ALERT: {alert.message}")
        
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def register_alert_handler(self, handler -> None: Callable[[BusinessAlert], None]) -> None:
        """Register an alert handler function"""
        self.alert_handlers.append(handler)
    
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> datetime:
        """Parse timestamp string to datetime"""
        
        if not timestamp_str:
            return datetime.utcnow()
        
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()
    
    def get_business_dashboard_data(self) -> Dict[str, Any]:
        """Get data for business dashboard"""
        
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        dashboard_data = {
            "timestamp": now.isoformat(),
            "kpis": {},
            "trends": {},
            "alerts": {
                "active": len([a for a in self.active_alerts if (now - a.triggered_at).total_seconds() < 3600]),
                "critical": len([a for a in self.active_alerts if a.severity == "critical"]),
                "recent": self.active_alerts[-5:] if self.active_alerts else []
            }
        }
        
        # Calculate key KPIs
        key_metrics = ["active_users", "revenue_generated", "collaboration_success_rate", "error_rate"]
        
        for metric_name in key_metrics:
            if metric_name in self.metric_definitions:
                # Get latest value
                recent_metrics = [
                    m for m in self.raw_metrics
                    if m.metric_name == metric_name and m.timestamp >= hour_ago
                ]
                
                if recent_metrics:
                    latest = max(recent_metrics, key=lambda m: m.timestamp)
                    dashboard_data["kpis"][metric_name] = {
                        "current_value": latest.value,
                        "timestamp": latest.timestamp.isoformat(),
                        "unit": self.metric_definitions[metric_name].unit
                    }
                    
                    # Calculate trend
                    older_metrics = [
                        m for m in self.raw_metrics
                        if m.metric_name == metric_name and day_ago <= m.timestamp < hour_ago
                    ]
                    
                    if older_metrics:
                        older_avg = sum(m.value for m in older_metrics) / len(older_metrics)
                        recent_avg = sum(m.value for m in recent_metrics) / len(recent_metrics)
                        
                        trend = "up" if recent_avg > older_avg else "down" if recent_avg < older_avg else "stable"
                        trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                        
                        dashboard_data["trends"][metric_name] = {
                            "direction": trend,
                            "percentage": round(trend_percentage, 2)
                        }
        
        return dashboard_data
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        
        return {
            "total_metrics_defined": len(self.metric_definitions),
            "total_raw_values": len(self.raw_metrics),
            "total_aggregations": sum(len(periods) for periods in self.aggregated_metrics.values()),
            "active_alerts": len(self.active_alerts),
            "metric_categories": {
                "content": len([m for m in self.metric_definitions.values() if "content" in m.tags]),
                "revenue": len([m for m in self.metric_definitions.values() if "revenue" in m.tags]),
                "collaboration": len([m for m in self.metric_definitions.values() if "collaboration" in m.tags]),
                "ai": len([m for m in self.metric_definitions.values() if "ai" in m.tags]),
                "system": len([m for m in self.metric_definitions.values() if any(tag in m.tags for tag in ["api", "performance", "errors"])])
            }
        }


# Export main classes
__all__ = [
    'BusinessMetricsAggregator',
    'MetricType',
    'AggregationPeriod',
    'MetricDefinition',
    'MetricValue',
    'AggregatedMetric',
    'BusinessAlert'
]