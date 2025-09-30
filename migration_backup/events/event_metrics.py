"""🚀 Event Metrics System - IA Influencer Agent Platform
=========================================================
Module: events/event_metrics.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 PERFORMANCE METRICS COLLECTION
Advanced event system performance monitoring and metrics
- Real-time performance tracking
- Detailed statistics and analytics
- SLA monitoring and alerting
- Resource utilization tracking
- Business intelligence metrics
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading
import statistics

from .core.base_event import BaseEvent

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


@dataclass
class MetricPoint:
    """Single metric measurement point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class EventProcessingMetrics:
    """Event processing performance metrics"""
    event_type: str
    total_events: int = 0
    successful_events: int = 0
    failed_events: int = 0
    total_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    max_processing_time: float = 0.0
    last_processed: Optional[datetime] = None
    error_rate: float = 0.0
    throughput_per_second: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_events == 0:
            return 1.0
        return self.successful_events / self.total_events
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time"""
        if self.successful_events == 0:
            return 0.0
        return self.total_processing_time / self.successful_events


@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_events_published: int = 0
    total_events_processed: int = 0
    total_events_failed: int = 0
    active_subscriptions: int = 0
    active_handlers: int = 0
    queue_depth: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    uptime_seconds: float = 0.0
    
    @property
    def overall_success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_events_published == 0:
            return 1.0
        return self.total_events_processed / self.total_events_published


@dataclass
class AlertRule:
    """Metric-based alert rule"""
    rule_id: str
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    duration_seconds: int = 60
    active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


class EventMetricsCollector:
    """Advanced event metrics collection and analysis system"""
    
    def __init__(self,
                 collection_interval: int = 10,
                 retention_period_hours: int = 24,
                 enable_real_time: bool = True,
                 max_metric_points: int = 10000):
        """Initialize metrics collector
        
        Args:
            collection_interval: Metrics collection interval in seconds
            retention_period_hours: How long to retain metric data
            enable_real_time: Enable real-time metric collection
            max_metric_points: Maximum metric points to store per metric
        """
        self.collection_interval = collection_interval
        self.retention_period = timedelta(hours=retention_period_hours)
        self.enable_real_time = enable_real_time
        self.max_metric_points = max_metric_points
        
        # Metrics storage
        self.event_metrics: Dict[str, EventProcessingMetrics] = {}
        self.system_metrics = SystemMetrics()
        self.metric_points: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metric_points))
        
        # Processing times for histogram calculation
        self.processing_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Alert system
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Set[str] = set()
        
        # Timing
        self.start_time = datetime.utcnow()
        self.last_collection = datetime.utcnow()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Callbacks
        self.on_alert_triggered: Optional[callable] = None
        self.on_alert_resolved: Optional[callable] = None
        
        logger.info("Event metrics collector initialized")
    
    def record_event_published(self, event: BaseEvent) -> None:
        """Record an event publication"""
        with self._lock:
            # Update system metrics
            self.system_metrics.total_events_published += 1
            
            # Update event type metrics
            if event.event_type not in self.event_metrics:
                self.event_metrics[event.event_type] = EventProcessingMetrics(
                    event_type=event.event_type
                )
            
            metrics = self.event_metrics[event.event_type]
            metrics.total_events += 1
            
            # Record metric point
            if self.enable_real_time:
                self._record_metric_point("events.published", 1.0, {
                    "event_type": event.event_type
                })
    
    def record_event_processed(self,
                              event: BaseEvent,
                              processing_time: float,
                              success: bool) -> None:
        """Record event processing completion
        
        Args:
            event: Processed event
            processing_time: Processing time in seconds
            success: Whether processing was successful
        """
        with self._lock:
            # Update system metrics
            if success:
                self.system_metrics.total_events_processed += 1
            else:
                self.system_metrics.total_events_failed += 1
            
            # Update event type metrics
            if event.event_type not in self.event_metrics:
                self.event_metrics[event.event_type] = EventProcessingMetrics(
                    event_type=event.event_type
                )
            
            metrics = self.event_metrics[event.event_type]
            
            if success:
                metrics.successful_events += 1
                metrics.total_processing_time += processing_time
                metrics.min_processing_time = min(metrics.min_processing_time, processing_time)
                metrics.max_processing_time = max(metrics.max_processing_time, processing_time)
                
                # Store processing time for histogram
                self.processing_times[event.event_type].append(processing_time)
            else:
                metrics.failed_events += 1
            
            metrics.last_processed = datetime.utcnow()
            
            # Calculate rates
            self._update_rates(metrics)
            
            # Record metric points
            if self.enable_real_time:
                self._record_metric_point("events.processed", 1.0, {
                    "event_type": event.event_type,
                    "success": str(success)
                })
                
                self._record_metric_point("processing.time", processing_time, {
                    "event_type": event.event_type
                })
    
    def record_queue_depth(self, depth: int) -> None:
        """Record current queue depth"""
        with self._lock:
            self.system_metrics.queue_depth = depth
            
            if self.enable_real_time:
                self._record_metric_point("queue.depth", float(depth))
    
    def record_subscription_count(self, count: int) -> None:
        """Record active subscription count"""
        with self._lock:
            self.system_metrics.active_subscriptions = count
            
            if self.enable_real_time:
                self._record_metric_point("subscriptions.active", float(count))
    
    def record_handler_count(self, count: int) -> None:
        """Record active handler count"""
        with self._lock:
            self.system_metrics.active_handlers = count
            
            if self.enable_real_time:
                self._record_metric_point("handlers.active", float(count))
    
    def record_system_resources(self, memory_mb: float, cpu_percent: float) -> None:
        """Record system resource usage"""
        with self._lock:
            self.system_metrics.memory_usage_mb = memory_mb
            self.system_metrics.cpu_usage_percent = cpu_percent
            
            if self.enable_real_time:
                self._record_metric_point("system.memory", memory_mb)
                self._record_metric_point("system.cpu", cpu_percent)
    
    def get_event_metrics(self, event_type: Optional[str] = None) -> Dict[str, Any]:
        """Get event processing metrics
        
        Args:
            event_type: Specific event type, or all if None
            
        Returns:
            Event metrics dictionary
        """
        with self._lock:
            if event_type:
                if event_type in self.event_metrics:
                    return {event_type: self.event_metrics[event_type]}
                else:
                    return {}
            
            return dict(self.event_metrics)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get system-wide metrics"""
        with self._lock:
            # Update uptime
            self.system_metrics.uptime_seconds = (
                datetime.utcnow() - self.start_time
            ).total_seconds()
            
            return self.system_metrics
    
    def get_throughput_stats(self, time_window_minutes: int = 5) -> Dict[str, float]:
        """Get throughput statistics for time window
        
        Args:
            time_window_minutes: Time window for calculation
            
        Returns:
            Throughput statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        with self._lock:
            stats = {}
            
            for event_type, points in self.metric_points.items():
                if not event_type.startswith("events."):
                    continue
                
                recent_points = [
                    p for p in points 
                    if p.timestamp >= cutoff_time
                ]
                
                if recent_points:
                    total_events = sum(p.value for p in recent_points)
                    throughput = total_events / (time_window_minutes * 60)
                    stats[event_type] = throughput
            
            return stats
    
    def get_percentiles(self, event_type: str, percentiles: List[float] = None) -> Dict[str, float]:
        """Get processing time percentiles for event type
        
        Args:
            event_type: Event type to analyze
            percentiles: List of percentiles to calculate (default: [50, 90, 95, 99])
            
        Returns:
            Percentile values
        """
        if percentiles is None:
            percentiles = [50, 90, 95, 99]
        
        with self._lock:
            if event_type not in self.processing_times:
                return {}
            
            times = list(self.processing_times[event_type])
            if not times:
                return {}
            
            result = {}
            for p in percentiles:
                try:
                    value = statistics.quantiles(times, n=100)[int(p) - 1]
                    result[f"p{p}"] = value
                except (IndexError, statistics.StatisticsError):
                    result[f"p{p}"] = 0.0
            
            return result
    
    def create_alert_rule(self,
                         rule_id: str,
                         name: str,
                         metric_name: str,
                         condition: str,
                         threshold: float,
                         duration_seconds: int = 60) -> bool:
        """Create a metric alert rule
        
        Args:
            rule_id: Unique rule identifier
            name: Human-readable rule name
            metric_name: Metric to monitor
            condition: Condition type (gt, lt, eq, gte, lte)
            threshold: Threshold value
            duration_seconds: Duration before triggering
            
        Returns:
            True if rule was created
        """
        if rule_id in self.alert_rules:
            logger.warning(f"Alert rule already exists: {rule_id}")
            return False
        
        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            duration_seconds=duration_seconds
        )
        
        self.alert_rules[rule_id] = rule
        logger.info(f"Alert rule created: {rule_id}")
        return True
    
    def check_alerts(self) -> List[str]:
        """Check all alert rules and trigger alerts
        
        Returns:
            List of triggered alert rule IDs
        """
        triggered_alerts = []
        current_time = datetime.utcnow()
        
        with self._lock:
            for rule_id, rule in self.alert_rules.items():
                if not rule.active:
                    continue
                
                # Get current metric value
                metric_value = self._get_current_metric_value(rule.metric_name)
                if metric_value is None:
                    continue
                
                # Check condition
                condition_met = self._evaluate_condition(
                    metric_value, rule.condition, rule.threshold
                )
                
                if condition_met:
                    # Check if alert should be triggered
                    if (rule.last_triggered is None or 
                        (current_time - rule.last_triggered).total_seconds() >= rule.duration_seconds):
                        
                        rule.last_triggered = current_time
                        rule.trigger_count += 1
                        triggered_alerts.append(rule_id)
                        self.active_alerts.add(rule_id)
                        
                        # Trigger callback
                        if self.on_alert_triggered:
                            try:
                                self.on_alert_triggered(rule, metric_value)
                            except Exception as e:
                                logger.error(f"Alert callback failed: {e}")
                        
                        logger.warning(f"Alert triggered: {rule.name} (value: {metric_value})")
                else:
                    # Resolve alert if it was active
                    if rule_id in self.active_alerts:
                        self.active_alerts.remove(rule_id)
                        
                        # Trigger callback
                        if self.on_alert_resolved:
                            try:
                                self.on_alert_resolved(rule, metric_value)
                            except Exception as e:
                                logger.error(f"Alert resolve callback failed: {e}")
                        
                        logger.info(f"Alert resolved: {rule.name}")
        
        return triggered_alerts
    
    def get_alert_status(self) -> Dict[str, Any]:
        """Get current alert status"""
        with self._lock:
            return {
                "active_alerts": list(self.active_alerts),
                "total_rules": len(self.alert_rules),
                "active_rules": sum(1 for r in self.alert_rules.values() if r.active),
                "rule_details": {
                    rule_id: {
                        "name": rule.name,
                        "active": rule.active,
                        "trigger_count": rule.trigger_count,
                        "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
                    }
                    for rule_id, rule in self.alert_rules.items()
                }
            }
    
    def cleanup_old_metrics(self) -> int:
        """Clean up old metric points beyond retention period
        
        Returns:
            Number of points cleaned up
        """
        cutoff_time = datetime.utcnow() - self.retention_period
        cleaned_count = 0
        
        with self._lock:
            for metric_name, points in self.metric_points.items():
                original_size = len(points)
                
                # Remove old points
                while points and points[0].timestamp < cutoff_time:
                    points.popleft()
                    cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old metric points")
        
        return cleaned_count
    
    def _record_metric_point(self, metric_name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a metric point"""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        
        self.metric_points[metric_name].append(point)
    
    def _update_rates(self, metrics: EventProcessingMetrics) -> None:
        """Update calculated rates for event metrics"""
        if metrics.total_events > 0:
            metrics.error_rate = metrics.failed_events / metrics.total_events
        
        # Calculate throughput (events per second)
        if metrics.last_processed:
            time_diff = (datetime.utcnow() - self.start_time).total_seconds()
            if time_diff > 0:
                metrics.throughput_per_second = metrics.total_events / time_diff
    
    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric"""
        # System metrics
        if metric_name == "system.memory":
            return self.system_metrics.memory_usage_mb
        elif metric_name == "system.cpu":
            return self.system_metrics.cpu_usage_percent
        elif metric_name == "queue.depth":
            return float(self.system_metrics.queue_depth)
        elif metric_name == "success_rate":
            return self.system_metrics.overall_success_rate
        
        # Event type metrics
        parts = metric_name.split(".")
        if len(parts) >= 2 and parts[0] in self.event_metrics:
            event_metrics = self.event_metrics[parts[0]]
            if parts[1] == "success_rate":
                return event_metrics.success_rate
            elif parts[1] == "throughput":
                return event_metrics.throughput_per_second
            elif parts[1] == "avg_processing_time":
                return event_metrics.average_processing_time
        
        # Recent metric points
        if metric_name in self.metric_points:
            points = self.metric_points[metric_name]
            if points:
                return points[-1].value
        
        return None
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == "gt":
            return value > threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "lte":
            return value <= threshold
        elif condition == "eq":
            return abs(value - threshold) < 1e-6
        else:
            logger.error(f"Unknown condition: {condition}")
            return False
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive metrics report"""
        with self._lock:
            system_metrics = self.get_system_metrics()
            
            # Calculate aggregated statistics
            total_success_rate = system_metrics.overall_success_rate
            avg_processing_time = 0.0
            
            if self.event_metrics:
                processing_times = [
                    m.average_processing_time for m in self.event_metrics.values()
                    if m.successful_events > 0
                ]
                if processing_times:
                    avg_processing_time = statistics.mean(processing_times)
            
            return {
                "collection_info": {
                    "start_time": self.start_time.isoformat(),
                    "uptime_seconds": system_metrics.uptime_seconds,
                    "last_collection": self.last_collection.isoformat(),
                    "retention_hours": self.retention_period.total_seconds() / 3600
                },
                "system_metrics": {
                    "total_events_published": system_metrics.total_events_published,
                    "total_events_processed": system_metrics.total_events_processed,
                    "total_events_failed": system_metrics.total_events_failed,
                    "overall_success_rate": total_success_rate,
                    "average_processing_time": avg_processing_time,
                    "active_subscriptions": system_metrics.active_subscriptions,
                    "active_handlers": system_metrics.active_handlers,
                    "queue_depth": system_metrics.queue_depth,
                    "memory_usage_mb": system_metrics.memory_usage_mb,
                    "cpu_usage_percent": system_metrics.cpu_usage_percent
                },
                "event_type_metrics": {
                    event_type: {
                        "total_events": metrics.total_events,
                        "successful_events": metrics.successful_events,
                        "failed_events": metrics.failed_events,
                        "success_rate": metrics.success_rate,
                        "average_processing_time": metrics.average_processing_time,
                        "min_processing_time": metrics.min_processing_time,
                        "max_processing_time": metrics.max_processing_time,
                        "throughput_per_second": metrics.throughput_per_second,
                        "last_processed": metrics.last_processed.isoformat() if metrics.last_processed else None
                    }
                    for event_type, metrics in self.event_metrics.items()
                },
                "throughput_stats": self.get_throughput_stats(),
                "alert_status": self.get_alert_status(),
                "metric_points_count": {
                    name: len(points) for name, points in self.metric_points.items()
                }
            }


# Global metrics collector instance
_global_metrics_collector: Optional[EventMetricsCollector] = None


def get_global_metrics_collector() -> EventMetricsCollector:
    """Get or create global metrics collector instance"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = EventMetricsCollector()
    return _global_metrics_collector


def record_event_published(event: BaseEvent) -> None:
    """Convenience function to record event publication globally"""
    collector = get_global_metrics_collector()
    collector.record_event_published(event)


def record_event_processed(event: BaseEvent, processing_time: float, success: bool) -> None:
    """Convenience function to record event processing globally"""
    collector = get_global_metrics_collector()
    collector.record_event_processed(event, processing_time, success)