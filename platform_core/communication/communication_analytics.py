"""
Communication Analytics module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Communication Analytics Engine - Enterprise Analytics Component
Message flow analytics, performance monitoring, and communication insights

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive communication analytics including:
- Message flow analytics and pattern analysis
- Performance monitoring and bottleneck identification
- Communication pattern analysis and optimization
- Real-time metrics and historical trend analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, deque
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    """Alert level enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CommunicationMetric:
    """Communication metric data"""
    metric_id: str
    metric_name: str
    metric_type: MetricType
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageFlowEvent:
    """Message flow tracking event"""
    event_id: str
    message_id: str
    source_service: str
    target_service: str
    event_type: str  # sent, received, processed, failed
    timestamp: datetime
    duration_ms: Optional[float] = None
    message_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert definition"""
    alert_id: str
    alert_name: str
    level: AlertLevel
    metric_name: str
    threshold: float
    current_value: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class CommunicationPattern:
    """Communication pattern analysis"""
    pattern_id: str
    pattern_type: str
    source_service: str
    target_service: str
    frequency: int
    avg_message_size: float
    avg_response_time: float
    error_rate: float
    peak_hours: List[int]
    analysis_period: timedelta
    detected_at: datetime


class CommunicationAnalyticsEngine:
    """
    Enterprise Communication Analytics Engine
    
    Provides comprehensive analytics for platform communications including
    message flow monitoring, performance analysis, pattern detection,
    and real-time insights for optimization and troubleshooting.
    """
    
    def __init__(self, retention_hours -> None: int = 168) -> None:  # 7 days default
        self.metrics: Dict[str, List[CommunicationMetric]] = defaultdict(list)
        self.message_flows: List[MessageFlowEvent] = []
        self.patterns: Dict[str, CommunicationPattern] = {}
        self.alerts: List[PerformanceAlert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.retention_hours = retention_hours
        
        # Real-time metrics storage
        self.realtime_counters: Dict[str, int] = defaultdict(int)
        self.realtime_gauges: Dict[str, float] = defaultdict(float)
        self.realtime_timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Analysis cache
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        # Initialize default alert rules
        self._initialize_default_alert_rules()
        
        logger.info("Communication Analytics Engine initialized")
    
    def _initialize_default_alert_rules(self) -> None:
        """Initialize default alert rules"""
        try:
            default_rules = {
                "high_error_rate": {
                    "metric": "error_rate",
                    "threshold": 0.05,  # 5%
                    "level": AlertLevel.WARNING,
                    "condition": "greater_than"
                },
                "high_response_time": {
                    "metric": "avg_response_time",
                    "threshold": 5000,  # 5 seconds
                    "level": AlertLevel.WARNING,
                    "condition": "greater_than"
                },
                "message_queue_backlog": {
                    "metric": "queue_depth",
                    "threshold": 10000,
                    "level": AlertLevel.ERROR,
                    "condition": "greater_than"
                },
                "connection_failures": {
                    "metric": "connection_failures",
                    "threshold": 10,
                    "level": AlertLevel.CRITICAL,
                    "condition": "greater_than"
                }
            }
            
            self.alert_rules.update(default_rules)
            logger.info("Default alert rules initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default alert rules: {e}")
    
    # Metric Collection
    async def record_metric(self, metric: CommunicationMetric) -> bool:
        """Record a communication metric"""
        try:
            # Store metric
            self.metrics[metric.metric_name].append(metric)
            
            # Update real-time storage
            if metric.metric_type == MetricType.COUNTER:
                self.realtime_counters[metric.metric_name] += metric.value
            elif metric.metric_type == MetricType.GAUGE:
                self.realtime_gauges[metric.metric_name] = metric.value
            elif metric.metric_type == MetricType.TIMER:
                self.realtime_timers[metric.metric_name].append(metric.value)
            
            # Check alert rules
            await self._check_alert_rules(metric)
            
            # Invalidate relevant cache
            await self._invalidate_cache(metric.metric_name)
            
            logger.debug(f"Metric {metric.metric_name} recorded: {metric.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric.metric_name}: {e}")
            return False
    
    async def record_message_flow(self, flow_event: MessageFlowEvent) -> bool:
        """Record message flow event"""
        try:
            self.message_flows.append(flow_event)
            
            # Create derived metrics
            await self._create_flow_metrics(flow_event)
            
            # Check for patterns
            await self._analyze_communication_patterns()
            
            logger.debug(f"Message flow event recorded: {flow_event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record message flow: {e}")
            return False
    
    async def _create_flow_metrics(self, flow_event: MessageFlowEvent) -> None:
        """Create metrics from flow events"""
        try:
            timestamp = flow_event.timestamp
            labels = {
                "source": flow_event.source_service,
                "target": flow_event.target_service,
                "event_type": flow_event.event_type
            }
            
            # Message count metric
            count_metric = CommunicationMetric(
                metric_id=f"flow_count_{flow_event.event_id}",
                metric_name="message_count",
                metric_type=MetricType.COUNTER,
                value=1,
                labels=labels,
                timestamp=timestamp
            )
            await self.record_metric(count_metric)
            
            # Duration metric (if available)
            if flow_event.duration_ms is not None:
                duration_metric = CommunicationMetric(
                    metric_id=f"flow_duration_{flow_event.event_id}",
                    metric_name="message_duration",
                    metric_type=MetricType.TIMER,
                    value=flow_event.duration_ms,
                    labels=labels,
                    timestamp=timestamp
                )
                await self.record_metric(duration_metric)
            
            # Message size metric (if available)
            if flow_event.message_size_bytes is not None:
                size_metric = CommunicationMetric(
                    metric_id=f"flow_size_{flow_event.event_id}",
                    metric_name="message_size",
                    metric_type=MetricType.HISTOGRAM,
                    value=flow_event.message_size_bytes,
                    labels=labels,
                    timestamp=timestamp
                )
                await self.record_metric(size_metric)
            
            # Error metric (if error)
            if flow_event.error_message:
                error_metric = CommunicationMetric(
                    metric_id=f"flow_error_{flow_event.event_id}",
                    metric_name="error_count",
                    metric_type=MetricType.COUNTER,
                    value=1,
                    labels={**labels, "error_type": "communication_error"},
                    timestamp=timestamp
                )
                await self.record_metric(error_metric)
            
        except Exception as e:
            logger.error(f"Failed to create flow metrics: {e}")
    
    # Analytics and Insights
    async def get_communication_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get communication summary for specified time period"""
        try:
            cache_key = f"summary_{hours}h"
            if await self._is_cache_valid(cache_key):
                return self.analysis_cache[cache_key]
            
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter flow events by time
            recent_flows = [f for f in self.message_flows if f.timestamp >= start_time]
            
            if not recent_flows:
                return {"message": "No communication data available", "period_hours": hours}
            
            summary = {
                "analysis_period_hours": hours,
                "total_messages": len(recent_flows),
                "unique_services": len(set(f.source_service for f in recent_flows) | 
                                  set(f.target_service for f in recent_flows)),
                "message_types": {},
                "service_pairs": {},
                "error_analysis": {},
                "performance_metrics": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Analyze message types
            type_counts = defaultdict(int)
            for flow in recent_flows:
                type_counts[flow.event_type] += 1
            summary["message_types"] = dict(type_counts)
            
            # Analyze service pairs
            pair_counts = defaultdict(int)
            for flow in recent_flows:
                pair = f"{flow.source_service} -> {flow.target_service}"
                pair_counts[pair] += 1
            summary["service_pairs"] = dict(sorted(pair_counts.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10])
            
            # Error analysis
            error_flows = [f for f in recent_flows if f.error_message]
            summary["error_analysis"] = {
                "total_errors": len(error_flows),
                "error_rate": len(error_flows) / len(recent_flows) if recent_flows else 0,
                "top_error_services": self._get_top_error_services(error_flows)
            }
            
            # Performance metrics
            durations = [f.duration_ms for f in recent_flows if f.duration_ms is not None]
            if durations:
                summary["performance_metrics"] = {
                    "avg_duration_ms": statistics.mean(durations),
                    "median_duration_ms": statistics.median(durations),
                    "p95_duration_ms": np.percentile(durations, 95),
                    "max_duration_ms": max(durations),
                    "min_duration_ms": min(durations)
                }
            
            # Cache result
            self.analysis_cache[cache_key] = summary
            self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=5)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get communication summary: {e}")
            return {"error": str(e)}
    
    def _get_top_error_services(self, error_flows: List[MessageFlowEvent]) -> Dict[str, int]:
        """Get top services with errors"""
        try:
            error_counts = defaultdict(int)
            for flow in error_flows:
                error_counts[flow.source_service] += 1
                error_counts[flow.target_service] += 1
            
            return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            
        except Exception as e:
            logger.error(f"Failed to get top error services: {e}")
            return {}
    
    async def get_performance_metrics(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for specified metric"""
        try:
            cache_key = f"performance_{metric_name}_{hours}h"
            if await self._is_cache_valid(cache_key):
                return self.analysis_cache[cache_key]
            
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get metrics for the time period
            metric_data = []
            if metric_name in self.metrics:
                metric_data = [m for m in self.metrics[metric_name] if m.timestamp >= start_time]
            
            if not metric_data:
                return {"message": f"No data available for metric {metric_name}", "period_hours": hours}
            
            values = [m.value for m in metric_data]
            
            performance = {
                "metric_name": metric_name,
                "period_hours": hours,
                "total_samples": len(values),
                "statistics": {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values)
                },
                "percentiles": {
                    "p50": np.percentile(values, 50),
                    "p75": np.percentile(values, 75),
                    "p90": np.percentile(values, 90),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99)
                },
                "trend_analysis": await self._analyze_trend(values),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            self.analysis_cache[cache_key] = performance
            self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=3)
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics for {metric_name}: {e}")
            return {"error": str(e)}
    
    async def _analyze_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze trend in metric values"""
        try:
            if len(values) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate simple trend
            x = list(range(len(values)))
            slope = np.polyfit(x, values, 1)[0]
            
            if abs(slope) < 0.01:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            # Calculate rate of change
            rate_of_change = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
            
            return {
                "trend": trend,
                "slope": slope,
                "rate_of_change_percent": rate_of_change,
                "volatility": statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze trend: {e}")
            return {"trend": "error", "error": str(e)}
    
    # Pattern Analysis
    async def _analyze_communication_patterns(self) -> None:
        """Analyze communication patterns"""
        try:
            # Analyze patterns for last 24 hours
            start_time = datetime.utcnow() - timedelta(hours=24)
            recent_flows = [f for f in self.message_flows if f.timestamp >= start_time]
            
            if len(recent_flows) < 10:  # Need minimum data for pattern analysis
                return
            
            # Group by service pairs
            service_pairs = defaultdict(list)
            for flow in recent_flows:
                pair_key = f"{flow.source_service}->{flow.target_service}"
                service_pairs[pair_key].append(flow)
            
            # Analyze each service pair
            for pair_key, flows in service_pairs.items():
                if len(flows) >= 5:  # Minimum threshold for pattern
                    pattern = await self._create_communication_pattern(pair_key, flows)
                    if pattern:
                        self.patterns[pattern.pattern_id] = pattern
            
        except Exception as e:
            logger.error(f"Failed to analyze communication patterns: {e}")
    
    async def _create_communication_pattern(self, pair_key: str, flows: List[MessageFlowEvent]) -> Optional[CommunicationPattern]:
        """Create communication pattern from flows"""
        try:
            source_service, target_service = pair_key.split('->')
            
            # Calculate metrics
            total_messages = len(flows)
            message_sizes = [f.message_size_bytes for f in flows if f.message_size_bytes is not None]
            durations = [f.duration_ms for f in flows if f.duration_ms is not None]
            errors = [f for f in flows if f.error_message]
            
            # Analyze timing patterns
            hours = [f.timestamp.hour for f in flows]
            hour_counts = defaultdict(int)
            for hour in hours:
                hour_counts[hour] += 1
            
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_hours = [hour for hour, count in peak_hours]
            
            pattern = CommunicationPattern(
                pattern_id=f"pattern_{pair_key}_{int(datetime.utcnow().timestamp())}",
                pattern_type="service_communication",
                source_service=source_service,
                target_service=target_service,
                frequency=total_messages,
                avg_message_size=statistics.mean(message_sizes) if message_sizes else 0,
                avg_response_time=statistics.mean(durations) if durations else 0,
                error_rate=len(errors) / total_messages if total_messages > 0 else 0,
                peak_hours=peak_hours,
                analysis_period=timedelta(hours=24),
                detected_at=datetime.utcnow()
            )
            
            return pattern
            
        except Exception as e:
            logger.error(f"Failed to create communication pattern: {e}")
            return None
    
    async def get_communication_patterns(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get detected communication patterns"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            recent_patterns = [p for p in self.patterns.values() if p.detected_at >= start_time]
            
            pattern_data = []
            for pattern in recent_patterns:
                pattern_dict = {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "source_service": pattern.source_service,
                    "target_service": pattern.target_service,
                    "frequency": pattern.frequency,
                    "avg_message_size": pattern.avg_message_size,
                    "avg_response_time": pattern.avg_response_time,
                    "error_rate": pattern.error_rate,
                    "peak_hours": pattern.peak_hours,
                    "detected_at": pattern.detected_at.isoformat()
                }
                pattern_data.append(pattern_dict)
            
            return pattern_data
            
        except Exception as e:
            logger.error(f"Failed to get communication patterns: {e}")
            return []
    
    # Alert Management
    async def _check_alert_rules(self, metric: CommunicationMetric) -> None:
        """Check metric against alert rules"""
        try:
            for rule_name, rule in self.alert_rules.items():
                if rule["metric"] == metric.metric_name:
                    should_alert = False
                    
                    if rule["condition"] == "greater_than" and metric.value > rule["threshold"]:
                        should_alert = True
                    elif rule["condition"] == "less_than" and metric.value < rule["threshold"]:
                        should_alert = True
                    
                    if should_alert:
                        alert = PerformanceAlert(
                            alert_id=f"alert_{rule_name}_{int(datetime.utcnow().timestamp())}",
                            alert_name=rule_name,
                            level=rule["level"],
                            metric_name=metric.metric_name,
                            threshold=rule["threshold"],
                            current_value=metric.value,
                            message=f"Metric {metric.metric_name} exceeded threshold: {metric.value} > {rule['threshold']}",
                            timestamp=datetime.utcnow()
                        )
                        
                        self.alerts.append(alert)
                        logger.warning(f"Alert triggered: {alert.alert_name} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to check alert rules: {e}")
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        try:
            active_alerts = [a for a in self.alerts if not a.resolved]
            
            alert_data = []
            for alert in active_alerts:
                alert_dict = {
                    "alert_id": alert.alert_id,
                    "alert_name": alert.alert_name,
                    "level": alert.level.value,
                    "metric_name": alert.metric_name,
                    "threshold": alert.threshold,
                    "current_value": alert.current_value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "age_minutes": (datetime.utcnow() - alert.timestamp).total_seconds() / 60
                }
                alert_data.append(alert_dict)
            
            return alert_data
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolution_time = datetime.utcnow()
                    logger.info(f"Alert resolved: {alert_id}")
                    return True
            
            logger.warning(f"Alert not found or already resolved: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    # Real-time Metrics
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics snapshot"""
        try:
            realtime = {
                "timestamp": datetime.utcnow().isoformat(),
                "counters": dict(self.realtime_counters),
                "gauges": dict(self.realtime_gauges),
                "timers": {}
            }
            
            # Calculate timer statistics
            for timer_name, values in self.realtime_timers.items():
                if values:
                    realtime["timers"][timer_name] = {
                        "count": len(values),
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": np.percentile(values, 95) if len(values) > 1 else values[0]
                    }
            
            return realtime
            
        except Exception as e:
            logger.error(f"Failed to get realtime metrics: {e}")
            return {"error": str(e)}
    
    # Cache Management
    async def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        try:
            if cache_key not in self.analysis_cache:
                return False
            
            if cache_key not in self.cache_expiry:
                return False
            
            return datetime.utcnow() < self.cache_expiry[cache_key]
            
        except Exception as e:
            logger.error(f"Failed to check cache validity: {e}")
            return False
    
    async def _invalidate_cache(self, metric_name: str) -> None:
        """Invalidate cache entries related to metric"""
        try:
            keys_to_remove = []
            for cache_key in self.analysis_cache.keys():
                if metric_name in cache_key or "summary" in cache_key:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                self.analysis_cache.pop(key, None)
                self.cache_expiry.pop(key, None)
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
    
    # Data Cleanup
    async def cleanup_old_data(self) -> int:
        """Clean up old data beyond retention period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
            cleaned_count = 0
            
            # Clean up message flows
            original_flow_count = len(self.message_flows)
            self.message_flows = [f for f in self.message_flows if f.timestamp > cutoff_time]
            cleaned_count += original_flow_count - len(self.message_flows)
            
            # Clean up metrics
            for metric_name, metric_list in self.metrics.items():
                original_count = len(metric_list)
                self.metrics[metric_name] = [m for m in metric_list if m.timestamp > cutoff_time]
                cleaned_count += original_count - len(self.metrics[metric_name])
            
            # Clean up patterns
            original_pattern_count = len(self.patterns)
            self.patterns = {k: v for k, v in self.patterns.items() if v.detected_at > cutoff_time}
            cleaned_count += original_pattern_count - len(self.patterns)
            
            # Clean up alerts (keep resolved alerts for 24 hours)
            alert_cutoff = datetime.utcnow() - timedelta(hours=24)
            original_alert_count = len(self.alerts)
            self.alerts = [a for a in self.alerts if not a.resolved or 
                          (a.resolution_time and a.resolution_time > alert_cutoff)]
            cleaned_count += original_alert_count - len(self.alerts)
            
            logger.info(f"Cleaned up {cleaned_count} old analytics records")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0


# Factory function for easier instantiation
def create_communication_analytics_engine(retention_hours: int = 168) -> CommunicationAnalyticsEngine:
    """Factory function to create a Communication Analytics Engine"""
    return CommunicationAnalyticsEngine(retention_hours)


# Example usage
async def main() -> None:
    """Example usage of Communication Analytics Engine"""
    analytics = create_communication_analytics_engine()
    
    # Record some test metrics
    test_metrics = [
        CommunicationMetric("m1", "message_count", MetricType.COUNTER, 100),
        CommunicationMetric("m2", "avg_response_time", MetricType.GAUGE, 250.5),
        CommunicationMetric("m3", "error_rate", MetricType.GAUGE, 0.02),
        CommunicationMetric("m4", "message_size", MetricType.HISTOGRAM, 1024)
    ]
    
    for metric in test_metrics:
        await analytics.record_metric(metric)
    
    # Record message flow events
    flow_events = [
        MessageFlowEvent(
            event_id="flow1",
            message_id="msg1",
            source_service="content_service",
            target_service="ai_service",
            event_type="sent",
            timestamp=datetime.utcnow(),
            duration_ms=150.5,
            message_size_bytes=2048
        ),
        MessageFlowEvent(
            event_id="flow2",
            message_id="msg1",
            source_service="ai_service",
            target_service="content_service",
            event_type="received",
            timestamp=datetime.utcnow(),
            duration_ms=200.0
        )
    ]
    
    for flow in flow_events:
        await analytics.record_message_flow(flow)
    
    # Get analytics
    summary = await analytics.get_communication_summary(hours=1)
    print(f"Communication Summary: {summary}")
    
    performance = await analytics.get_performance_metrics("avg_response_time", hours=1)
    print(f"Performance Metrics: {performance}")
    
    realtime = await analytics.get_realtime_metrics()
    print(f"Real-time Metrics: {realtime}")
    
    alerts = await analytics.get_active_alerts()
    print(f"Active Alerts: {alerts}")


if __name__ == "__main__":
    asyncio.run(main())