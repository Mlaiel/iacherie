"""
Enterprise Matching Module Metrics & Monitoring

Advanced metrics collection, monitoring, and observability system for the
enterprise creator collaboration matching platform with real-time analytics,
performance tracking, and business intelligence dashboards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

  INTELLECTUAL PROPERTY WARNING 
This monitoring module contains proprietary metrics and algorithms
developed by Fahed Mlaiel. Unauthorized use is prohibited.
"""

import time
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import logging
import traceback
from contextlib import contextmanager
import psutil
import numpy as np
from functools import wraps


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Single metric data point"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class Alert:
    """System alert"""
    id: str
    name: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold: float
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


@dataclass
class PerformanceStats:
    """Performance statistics"""
    requests_per_second: float = 0.0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0


@dataclass
class BusinessMetrics:
    """Business-specific metrics"""
    total_matches_created: int = 0
    successful_collaborations: int = 0
    average_match_score: float = 0.0
    revenue_generated: float = 0.0
    user_satisfaction_score: float = 0.0
    collaboration_completion_rate: float = 0.0
    average_time_to_match: float = 0.0
    top_creator_categories: List[str] = field(default_factory=list)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)


class MetricsCollector:
    """Advanced metrics collection system"""
    
    def __init__(self, max_data_points: int = 10000):
        self.max_data_points = max_data_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_data_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.labels: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._lock = threading.Lock()
        
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric"""
        with self._lock:
            self.counters[name] += value
            if labels:
                self.labels[name] = labels
            self._add_metric_point(name, self.counters[name], MetricType.COUNTER, labels)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value"""
        with self._lock:
            self.gauges[name] = value
            if labels:
                self.labels[name] = labels
            self._add_metric_point(name, value, MetricType.GAUGE, labels)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric value"""
        with self._lock:
            self.histograms[name].append(value)
            # Keep only recent values
            if len(self.histograms[name]) > self.max_data_points:
                self.histograms[name] = self.histograms[name][-self.max_data_points:]
            if labels:
                self.labels[name] = labels
            self._add_metric_point(name, value, MetricType.HISTOGRAM, labels)
    
    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a timer metric value"""
        with self._lock:
            self.timers[name].append(duration)
            # Keep only recent values
            if len(self.timers[name]) > self.max_data_points:
                self.timers[name] = self.timers[name][-self.max_data_points:]
            if labels:
                self.labels[name] = labels
            self._add_metric_point(name, duration, MetricType.TIMER, labels)
    
    def _add_metric_point(self, name: str, value: float, metric_type: MetricType, labels: Optional[Dict[str, str]]) -> None:
        """Add a metric point to the time series"""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {},
            metric_type=metric_type
        )
        self.metrics[name].append(point)
    
    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        with self._lock:
            if name not in self.metrics:
                return {}
            
            points = list(self.metrics[name])
            if not points:
                return {}
            
            values = [point.value for point in points]
            
            summary = {
                "name": name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "current": values[-1] if values else 0,
                "timestamp": points[-1].timestamp.isoformat() if points else None
            }
            
            if len(values) > 1:
                summary["std_dev"] = statistics.stdev(values)
                summary["median"] = statistics.median(values)
                
                # Percentiles for histograms and timers
                if name in self.histograms or name in self.timers:
                    sorted_values = sorted(values)
                    summary["p50"] = np.percentile(sorted_values, 50)
                    summary["p90"] = np.percentile(sorted_values, 90)
                    summary["p95"] = np.percentile(sorted_values, 95)
                    summary["p99"] = np.percentile(sorted_values, 99)
            
            return summary
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metric summaries"""
        with self._lock:
            return {name: self.get_metric_summary(name) for name in self.metrics.keys()}
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        with self._lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()
            self.labels.clear()


class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.start_time = time.time()
        self.request_times: deque = deque(maxlen=1000)
        self.error_count = 0
        self.total_requests = 0
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def start_monitoring(self, interval: float = 10.0) -> None:
        """Start performance monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
    
    def _monitor_loop(self, interval: float) -> None:
        """Main monitoring loop"""
        while self._monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
    
    def _collect_system_metrics(self) -> None:
        """Collect system performance metrics"""



        try:
            # System metrics
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self.metrics.set_gauge("system_memory_usage_mb", memory_mb)
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            self.metrics.set_gauge("system_cpu_usage_percent", cpu_percent)
            
            # Request rate
            current_time = time.time()
            uptime = current_time - self.start_time
            requests_per_second = self.total_requests / uptime if uptime > 0 else 0
            self.metrics.set_gauge("requests_per_second", requests_per_second)
            
            # Error rate
            error_rate = self.error_count / self.total_requests if self.total_requests > 0 else 0
            self.metrics.set_gauge("error_rate", error_rate)
            
            # Response time statistics
            if self.request_times:
                avg_response_time = statistics.mean(self.request_times)
                self.metrics.set_gauge("average_response_time", avg_response_time)
                
                sorted_times = sorted(self.request_times)
                p95_time = np.percentile(sorted_times, 95)
                p99_time = np.percentile(sorted_times, 99)
                self.metrics.set_gauge("p95_response_time", p95_time)
                self.metrics.set_gauge("p99_response_time", p99_time)
        
        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")
    
    @contextmanager
    def measure_request(self):
        """Context manager to measure request duration"""
        start_time = time.time()
        success = True
        
        try:
            yield
        except Exception as e:
            success = False
            self.error_count += 1
            raise
        finally:
            duration = time.time() - start_time
            self.request_times.append(duration)
            self.total_requests += 1
            
            # Record metrics
            self.metrics.record_timer("request_duration", duration)
            if success:
                self.metrics.increment_counter("successful_requests")
            else:
                self.metrics.increment_counter("failed_requests")
    
    def get_performance_stats(self) -> PerformanceStats:
        """Get current performance statistics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        return PerformanceStats(
            requests_per_second=self.total_requests / uptime if uptime > 0 else 0,
            average_response_time=statistics.mean(self.request_times) if self.request_times else 0,
            p95_response_time=np.percentile(sorted(self.request_times), 95) if self.request_times else 0,
            p99_response_time=np.percentile(sorted(self.request_times), 99) if self.request_times else 0,
            error_rate=self.error_count / self.total_requests if self.total_requests > 0 else 0,
            memory_usage_mb=psutil.Process().memory_info().rss / (1024 * 1024),
            cpu_usage_percent=psutil.Process().cpu_percent(),
            total_requests=self.total_requests,
            successful_requests=self.total_requests - self.error_count,
            failed_requests=self.error_count
        )


class AlertManager:
    """Alert management system"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self._checking = False
        self._check_thread: Optional[threading.Thread] = None
    
    def add_alert_rule(self, name: str, metric_name: str, threshold: float, 
                      condition: str = "greater", severity: AlertSeverity = AlertSeverity.WARNING) -> None:
        """Add an alert rule"""
        self.alert_rules[name] = {
            "metric_name": metric_name,
            "threshold": threshold,
            "condition": condition,  # greater, less, equal
            "severity": severity
        }
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def start_alert_checking(self, interval: float = 30.0) -> None:
        """Start alert checking"""
        if self._checking:
            return
        
        self._checking = True
        self._check_thread = threading.Thread(
            target=self._check_alerts_loop,
            args=(interval,),
            daemon=True
        )
        self._check_thread.start()
    
    def stop_alert_checking(self) -> None:
        """Stop alert checking"""
        self._checking = False
        if self._check_thread:
            self._check_thread.join(timeout=5.0)
    
    def _check_alerts_loop(self, interval: float) -> None:
        """Main alert checking loop"""
        while self._checking:
            try:
                self._check_all_rules()
                time.sleep(interval)
            except Exception as e:
                logging.error(f"Error in alert checking loop: {e}")
    
    def _check_all_rules(self) -> None:
        """Check all alert rules"""
        for rule_name, rule in self.alert_rules.items():
            try:
                self._check_rule(rule_name, rule)
            except Exception as e:
                logging.error(f"Error checking rule {rule_name}: {e}")
    
    def _check_rule(self, rule_name: str, rule: Dict[str, Any]) -> None:
        """Check a specific alert rule"""
        metric_name = rule["metric_name"]
        threshold = rule["threshold"]
        condition = rule["condition"]
        severity = rule["severity"]
        
        # Get current metric value
        summary = self.metrics.get_metric_summary(metric_name)
        if not summary:
            return
        
        current_value = summary.get("current", 0)
        
        # Check condition
        alert_triggered = False
        if condition == "greater" and current_value > threshold:
            alert_triggered = True
        elif condition == "less" and current_value < threshold:
            alert_triggered = True
        elif condition == "equal" and abs(current_value - threshold) < 0.001:
            alert_triggered = True
        
        # Handle alert state
        if alert_triggered and rule_name not in self.active_alerts:
            self._trigger_alert(rule_name, metric_name, current_value, threshold, severity)
        elif not alert_triggered and rule_name in self.active_alerts:
            self._resolve_alert(rule_name)
    
    def _trigger_alert(self, rule_name: str, metric_name: str, current_value: float, 
                      threshold: float, severity: AlertSeverity) -> None:
        """Trigger a new alert"""
        alert = Alert(
            id=f"{rule_name}_{int(time.time())}",
            name=rule_name,
            message=f"Alert {rule_name}: {metric_name} value {current_value} exceeds threshold {threshold}",
            severity=severity,
            timestamp=datetime.now(),
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold
        )
        
        self.active_alerts[rule_name] = alert
        self.alert_history.append(alert)
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logging.error(f"Error in alert callback: {e}")
        
        logging.warning(f"Alert triggered: {alert.message}")
    
    def _resolve_alert(self, rule_name: str) -> None:
        """Resolve an active alert"""
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.resolved = True
            alert.resolution_timestamp = datetime.now()
            
            del self.active_alerts[rule_name]
            
            logging.info(f"Alert resolved: {alert.name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""



        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""



        return self.alert_history[-limit:]


class BusinessMetricsCollector:
    """Business-specific metrics collection"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.business_data: Dict[str, Any] = defaultdict(int)
        self._lock = threading.Lock()
    
    def record_match_created(self, creator_categories: List[str], match_score: float, 
                           geographic_region: str) -> None:
        """Record a new match creation"""
        with self._lock:
            self.metrics.increment_counter("matches_created_total")
            self.metrics.record_histogram("match_scores", match_score)
            
            # Update business data
            self.business_data["total_matches"] += 1
            self.business_data["total_match_score"] += match_score
            
            # Category tracking
            for category in creator_categories:
                self.business_data[f"category_{category}"] += 1
            
            # Geographic tracking
            self.business_data[f"region_{geographic_region}"] += 1
    
    def record_collaboration_success(self, revenue: float, satisfaction_score: float, 
                                   duration_days: int) -> None:
        """Record a successful collaboration"""
        with self._lock:
            self.metrics.increment_counter("collaborations_successful_total")
            self.metrics.record_histogram("collaboration_revenue", revenue)
            self.metrics.record_histogram("collaboration_satisfaction", satisfaction_score)
            self.metrics.record_histogram("collaboration_duration_days", duration_days)
            
            # Update business data
            self.business_data["successful_collaborations"] += 1
            self.business_data["total_revenue"] += revenue
            self.business_data["total_satisfaction"] += satisfaction_score
    
    def record_collaboration_failure(self, reason: str) -> None:
        """Record a failed collaboration"""
        with self._lock:
            self.metrics.increment_counter("collaborations_failed_total")
            self.business_data[f"failure_reason_{reason}"] += 1
    
    def record_user_activity(self, user_type: str, action: str) -> None:
        """Record user activity"""
        with self._lock:
            self.metrics.increment_counter(f"user_activity_{user_type}_{action}")
    
    def get_business_metrics(self) -> BusinessMetrics:
        """Get current business metrics"""
        with self._lock:
            total_matches = self.business_data.get("total_matches", 0)
            successful_collaborations = self.business_data.get("successful_collaborations", 0)
            total_match_score = self.business_data.get("total_match_score", 0)
            total_revenue = self.business_data.get("total_revenue", 0)
            total_satisfaction = self.business_data.get("total_satisfaction", 0)
            
            # Calculate rates
            avg_match_score = total_match_score / total_matches if total_matches > 0 else 0
            avg_satisfaction = total_satisfaction / successful_collaborations if successful_collaborations > 0 else 0
            completion_rate = successful_collaborations / total_matches if total_matches > 0 else 0
            
            # Get top categories
            categories = [(k.replace("category_", ""), v) for k, v in self.business_data.items() 
                         if k.startswith("category_")]
            top_categories = [cat for cat, _ in sorted(categories, key=lambda x: x[1], reverse=True)[:5]]
            
            # Get geographic distribution
            geographic = {k.replace("region_", ""): v for k, v in self.business_data.items() 
                         if k.startswith("region_")}
            
            return BusinessMetrics(
                total_matches_created=total_matches,
                successful_collaborations=successful_collaborations,
                average_match_score=avg_match_score,
                revenue_generated=total_revenue,
                user_satisfaction_score=avg_satisfaction,
                collaboration_completion_rate=completion_rate,
                top_creator_categories=top_categories,
                geographic_distribution=geographic
            )


def timer_decorator(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to time function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Get global metrics collector
                from . import get_metrics_collector
                metrics = get_metrics_collector()
                metrics.record_timer(metric_name, duration, labels)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Get global metrics collector
                from . import get_metrics_collector
                metrics = get_metrics_collector()
                metrics.record_timer(metric_name, duration, labels)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def counter_decorator(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to count function calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # Get global metrics collector
                from . import get_metrics_collector
                metrics = get_metrics_collector()
                metrics.increment_counter(f"{metric_name}_success", 1, labels)
                return result
            except Exception as e:
                # Get global metrics collector
                from . import get_metrics_collector
                metrics = get_metrics_collector()
                metrics.increment_counter(f"{metric_name}_error", 1, labels)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Get global metrics collector
                from . import get_metrics_collector
                metrics = get_metrics_collector()
                metrics.increment_counter(f"{metric_name}_success", 1, labels)
                return result
            except Exception as e:
                # Get global metrics collector
                from . import get_metrics_collector
                metrics = get_metrics_collector()
                metrics.increment_counter(f"{metric_name}_error", 1, labels)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class MonitoringService:
    """Complete monitoring service orchestrator"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.performance_monitor = PerformanceMonitor(self.metrics_collector)
        self.alert_manager = AlertManager(self.metrics_collector)
        self.business_metrics = BusinessMetricsCollector(self.metrics_collector)
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    def _setup_default_alerts(self) -> None:
        """Setup default alert rules"""
        # Performance alerts
        self.alert_manager.add_alert_rule(
            "high_error_rate", "error_rate", 0.05, "greater", AlertSeverity.ERROR
        )
        self.alert_manager.add_alert_rule(
            "high_response_time", "p95_response_time", 2000, "greater", AlertSeverity.WARNING
        )
        self.alert_manager.add_alert_rule(
            "high_memory_usage", "system_memory_usage_mb", 2048, "greater", AlertSeverity.WARNING
        )
        self.alert_manager.add_alert_rule(
            "high_cpu_usage", "system_cpu_usage_percent", 80, "greater", AlertSeverity.WARNING
        )
        
        # Business alerts
        self.alert_manager.add_alert_rule(
            "low_match_score", "match_scores", 0.4, "less", AlertSeverity.WARNING
        )
        self.alert_manager.add_alert_rule(
            "low_satisfaction", "collaboration_satisfaction", 3.0, "less", AlertSeverity.ERROR
        )
    
    def start_monitoring(self, performance_interval: float = 10.0, alert_interval: float = 30.0) -> None:
        """Start all monitoring services"""
        self.performance_monitor.start_monitoring(performance_interval)
        self.alert_manager.start_alert_checking(alert_interval)
    
    def stop_monitoring(self) -> None:
        """Stop all monitoring services"""
        self.performance_monitor.stop_monitoring()
        self.alert_manager.stop_alert_checking()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get complete system health status"""
        performance_stats = self.performance_monitor.get_performance_stats()
        business_metrics = self.business_metrics.get_business_metrics()
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Determine overall health
        health_score = 100.0
        if performance_stats.error_rate > 0.05:
            health_score -= 20
        if performance_stats.p95_response_time > 2000:
            health_score -= 15
        if performance_stats.memory_usage_mb > 2048:
            health_score -= 10
        if len(active_alerts) > 0:
            health_score -= 20
        
        health_status = "healthy"
        if health_score < 50:
            health_status = "critical"
        elif health_score < 70:
            health_status = "degraded"
        elif health_score < 90:
            health_status = "warning"
        
        return {
            "status": health_status,
            "health_score": health_score,
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "requests_per_second": performance_stats.requests_per_second,
                "average_response_time": performance_stats.average_response_time,
                "error_rate": performance_stats.error_rate,
                "memory_usage_mb": performance_stats.memory_usage_mb,
                "cpu_usage_percent": performance_stats.cpu_usage_percent
            },
            "business": {
                "total_matches": business_metrics.total_matches_created,
                "successful_collaborations": business_metrics.successful_collaborations,
                "average_match_score": business_metrics.average_match_score,
                "revenue_generated": business_metrics.revenue_generated
            },
            "alerts": {
                "active_count": len(active_alerts),
                "critical_count": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "error_count": len([a for a in active_alerts if a.severity == AlertSeverity.ERROR])
            }
        }
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        all_metrics = self.metrics_collector.get_all_metrics()
        
        if format_type == "json":
            return json.dumps(all_metrics, indent=2, default=str)
        elif format_type == "prometheus":
            return self._export_prometheus_format(all_metrics)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_prometheus_format(self, metrics: Dict[str, Any]) -> str:
        """Export metrics in Prometheus format"""
        output = []
        
        for name, data in metrics.items():
            if not data:
                continue
            
            # Add help text
            output.append(f"# HELP {name} {name}")
            
            # Add type
            metric_type = "gauge"  # Default to gauge
            output.append(f"# TYPE {name} {metric_type}")
            
            # Add metric value
            value = data.get("current", 0)
            output.append(f"{name} {value}")
            
            output.append("")  # Empty line
        
        return "\n".join(output)


# Global monitoring service instance
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """Get global monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector"""



    return get_monitoring_service().metrics_collector


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""



    return get_monitoring_service().performance_monitor


def get_alert_manager() -> AlertManager:
    """Get global alert manager"""



    return get_monitoring_service().alert_manager


def get_business_metrics() -> BusinessMetricsCollector:
    """Get global business metrics collector"""



    return get_monitoring_service().business_metrics


if __name__ == "__main__":
    """Demonstration of monitoring capabilities"""
    import random
    
    # Create monitoring service
    monitoring = MonitoringService()
    monitoring.start_monitoring()
    
    print("Starting monitoring demonstration...")
    
    # Simulate some metrics
    for i in range(100):
        # Simulate requests
        with monitoring.performance_monitor.measure_request():
            time.sleep(random.uniform(0.01, 0.1))
        
        # Simulate business metrics
        if random.random() < 0.3:
            monitoring.business_metrics.record_match_created(
                ["tech", "lifestyle"], 
                random.uniform(0.5, 0.95),
                "US"
            )
        
        if random.random() < 0.1:
            monitoring.business_metrics.record_collaboration_success(
                random.uniform(100, 5000),
                random.uniform(3.0, 5.0),
                random.randint(30, 180)
            )
    
    # Wait for metrics collection
    time.sleep(2)
    
    # Show health status
    health = monitoring.get_health_status()
    print("\nSystem Health Status:")
    print(json.dumps(health, indent=2))
    
    # Show metrics export
    print("\nMetrics Export (sample):")
    metrics_json = monitoring.export_metrics("json")
    print(metrics_json[:500] + "..." if len(metrics_json) > 500 else metrics_json)
    
    monitoring.stop_monitoring()
    print("\nMonitoring demonstration completed!")
