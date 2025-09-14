#!/usr/bin/env python3
"""
📊 Gateway Monitoring - Enterprise API Gateway Service
======================================================

Comprehensive monitoring and observability service for enterprise API gateway.
Provides real-time metrics, alerting, and performance monitoring capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Metric data structure."""
    name: str
    type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold: float
    is_active: bool = True
    resolved_at: Optional[datetime] = None


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric_name: str
    condition: str  # "greater_than", "less_than", "equals"
    threshold: float
    duration_seconds: int = 60
    severity: AlertSeverity = AlertSeverity.WARNING
    description: str = ""
    enabled: bool = True


class GatewayMonitoring:
    """
    📊 Enterprise Gateway Monitoring Service
    
    Provides comprehensive monitoring, metrics collection, and alerting
    for API gateway operations with enterprise-grade observability.
    """

    def __init__(self):
        """Initialize the monitoring service."""
        self.metrics: Dict[str, List[Metric]] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.performance_data: Dict[str, Any] = {
            'request_rates': [],
            'response_times': [],
            'error_rates': [],
            'throughput': []
        }
        
        # Configure default alert rules
        self._setup_default_alert_rules()
        
        # Start monitoring tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("📊 Gateway Monitoring Service initialized")

    async def start(self):
        """Start the monitoring service."""
        logger.info("🚀 Starting Gateway Monitoring Service")
        
        # Start monitoring loops
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Gateway Monitoring Service started")

    async def stop(self):
        """Stop the monitoring service."""
        logger.info("🛑 Stopping Gateway Monitoring Service")
        
        # Cancel tasks
        tasks = [self.monitoring_task, self.cleanup_task]
        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("✅ Gateway Monitoring Service stopped")

    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE, 
                     labels: Optional[Dict[str, str]] = None, help_text: str = ""):
        """Record a metric value."""
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {},
            help_text=help_text
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Keep only last 1000 measurements per metric
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
        
        # Check alert rules
        self._check_alert_rules(name, value)

    def record_request_metrics(self, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Record comprehensive request metrics."""
        # Extract metrics from request/response
        response_time = response_data.get('response_time', 0)
        status_code = response_data.get('status_code', 200)
        method = request_data.get('method', 'GET')
        path = request_data.get('path', '/')
        
        # Record basic metrics
        self.record_metric("gateway_requests_total", 1, MetricType.COUNTER, 
                          labels={'method': method, 'path': path, 'status': str(status_code)})
        
        self.record_metric("gateway_request_duration_seconds", response_time, MetricType.HISTOGRAM,
                          labels={'method': method, 'path': path})
        
        # Error rate tracking
        if status_code >= 400:
            self.record_metric("gateway_errors_total", 1, MetricType.COUNTER,
                              labels={'method': method, 'path': path, 'status': str(status_code)})
        
        # Update performance data
        self.performance_data['response_times'].append(response_time)
        if len(self.performance_data['response_times']) > 1000:
            self.performance_data['response_times'] = self.performance_data['response_times'][-1000:]

    def record_backend_metrics(self, server_id: str, response_time: float, success: bool):
        """Record backend server metrics."""
        labels = {'server_id': server_id, 'status': 'success' if success else 'error'}
        
        self.record_metric("gateway_backend_requests_total", 1, MetricType.COUNTER, labels=labels)
        self.record_metric("gateway_backend_duration_seconds", response_time, MetricType.HISTOGRAM, 
                          labels={'server_id': server_id})
        
        if not success:
            self.record_metric("gateway_backend_errors_total", 1, MetricType.COUNTER,
                              labels={'server_id': server_id})

    def get_metrics_summary(self, time_window_minutes: int = 5) -> Dict[str, Any]:
        """Get metrics summary for the specified time window."""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        summary = {
            'request_rate': self._calculate_request_rate(cutoff_time),
            'avg_response_time': self._calculate_avg_response_time(cutoff_time),
            'error_rate': self._calculate_error_rate(cutoff_time),
            'p95_response_time': self._calculate_percentile_response_time(cutoff_time, 95),
            'p99_response_time': self._calculate_percentile_response_time(cutoff_time, 99),
            'active_alerts': len(self.active_alerts),
            'backend_health': self._get_backend_health_summary(cutoff_time),
            'throughput': self._calculate_throughput(cutoff_time)
        }
        
        return summary

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics for all tracked metrics."""
        detailed = {}
        
        for metric_name, measurements in self.metrics.items():
            if not measurements:
                continue
            
            latest = measurements[-1]
            values = [m.value for m in measurements[-100:]]  # Last 100 measurements
            
            detailed[metric_name] = {
                'current_value': latest.value,
                'timestamp': latest.timestamp.isoformat(),
                'type': latest.type.value,
                'help': latest.help_text,
                'labels': latest.labels,
                'statistics': {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': statistics.mean(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0,
                    'median': statistics.median(values) if values else 0
                } if len(values) > 0 else {}
            }
        
        return detailed

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules[rule.name] = rule
        logger.info(f"➕ Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule."""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"➖ Removed alert rule: {rule_name}")

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self.alert_history[-limit:]

    def _setup_default_alert_rules(self):
        """Setup default alert rules."""
        default_rules = [
            AlertRule(
                name="high_response_time",
                metric_name="gateway_request_duration_seconds",
                condition="greater_than",
                threshold=1.0,
                severity=AlertSeverity.WARNING,
                description="Average response time is too high"
            ),
            AlertRule(
                name="high_error_rate",
                metric_name="gateway_errors_total",
                condition="greater_than",
                threshold=10.0,
                severity=AlertSeverity.ERROR,
                description="Error rate is too high"
            ),
            AlertRule(
                name="low_request_rate",
                metric_name="gateway_requests_total",
                condition="less_than",
                threshold=1.0,
                duration_seconds=300,
                severity=AlertSeverity.WARNING,
                description="Request rate is unusually low"
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)

    def _check_alert_rules(self, metric_name: str, value: float):
        """Check if any alert rules are triggered."""
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled or rule.metric_name != metric_name:
                continue
            
            triggered = False
            
            if rule.condition == "greater_than" and value > rule.threshold:
                triggered = True
            elif rule.condition == "less_than" and value < rule.threshold:
                triggered = True
            elif rule.condition == "equals" and value == rule.threshold:
                triggered = True
            
            if triggered:
                self._trigger_alert(rule, value)
            else:
                self._resolve_alert(rule_name)

    def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger an alert."""
        alert_id = f"{rule.name}_{int(time.time())}"
        
        # Check if alert already exists
        if rule.name in self.active_alerts:
            return
        
        alert = Alert(
            id=alert_id,
            title=f"Alert: {rule.name}",
            description=rule.description,
            severity=rule.severity,
            timestamp=datetime.now(),
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold
        )
        
        self.active_alerts[rule.name] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"🚨 Alert triggered: {rule.name} - {rule.description}")

    def _resolve_alert(self, rule_name: str):
        """Resolve an active alert."""
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.is_active = False
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[rule_name]
            
            logger.info(f"✅ Alert resolved: {rule_name}")

    def _calculate_request_rate(self, since: datetime) -> float:
        """Calculate requests per second since the given time."""
        if "gateway_requests_total" not in self.metrics:
            return 0.0
        
        recent_requests = [
            m for m in self.metrics["gateway_requests_total"]
            if m.timestamp >= since
        ]
        
        if not recent_requests:
            return 0.0
        
        time_window = (datetime.now() - since).total_seconds()
        return len(recent_requests) / max(time_window, 1)

    def _calculate_avg_response_time(self, since: datetime) -> float:
        """Calculate average response time since the given time."""
        if "gateway_request_duration_seconds" not in self.metrics:
            return 0.0
        
        recent_times = [
            m.value for m in self.metrics["gateway_request_duration_seconds"]
            if m.timestamp >= since
        ]
        
        return statistics.mean(recent_times) if recent_times else 0.0

    def _calculate_error_rate(self, since: datetime) -> float:
        """Calculate error rate since the given time."""
        total_requests = len([
            m for m in self.metrics.get("gateway_requests_total", [])
            if m.timestamp >= since
        ])
        
        error_requests = len([
            m for m in self.metrics.get("gateway_errors_total", [])
            if m.timestamp >= since
        ])
        
        if total_requests == 0:
            return 0.0
        
        return (error_requests / total_requests) * 100

    def _calculate_percentile_response_time(self, since: datetime, percentile: int) -> float:
        """Calculate percentile response time."""
        if "gateway_request_duration_seconds" not in self.metrics:
            return 0.0
        
        recent_times = [
            m.value for m in self.metrics["gateway_request_duration_seconds"]
            if m.timestamp >= since
        ]
        
        if not recent_times:
            return 0.0
        
        return statistics.quantiles(recent_times, n=100)[percentile-1] if len(recent_times) > 1 else recent_times[0]

    def _calculate_throughput(self, since: datetime) -> float:
        """Calculate throughput in bytes per second."""
        # This would typically track bytes transferred
        return 0.0  # Placeholder

    def _get_backend_health_summary(self, since: datetime) -> Dict[str, Any]:
        """Get backend health summary."""
        # This would aggregate backend health metrics
        return {
            'healthy_backends': 3,
            'unhealthy_backends': 0,
            'total_backends': 3
        }

    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Monitoring loop error: {e}")
                await asyncio.sleep(30)

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Cleanup every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Cleanup loop error: {e}")
                await asyncio.sleep(3600)

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.record_metric("gateway_cpu_usage_percent", cpu_percent, MetricType.GAUGE)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.record_metric("gateway_memory_usage_percent", memory.percent, MetricType.GAUGE)
        self.record_metric("gateway_memory_usage_bytes", memory.used, MetricType.GAUGE)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.record_metric("gateway_disk_usage_percent", disk.percent, MetricType.GAUGE)

    async def _cleanup_old_data(self):
        """Clean up old metrics and alerts."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Clean old metrics
        for metric_name, measurements in self.metrics.items():
            self.metrics[metric_name] = [
                m for m in measurements if m.timestamp >= cutoff_time
            ]
        
        # Clean old alert history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        logger.info("🧹 Cleaned up old monitoring data")


async def main():
    """Example usage of the Gateway Monitoring service."""
    print("📊 Gateway Monitoring Example")
    print("=" * 35)
    
    # Create monitoring service
    monitoring = GatewayMonitoring()
    await monitoring.start()
    
    # Simulate some metrics
    print("\n📈 Simulating metrics...")
    for i in range(10):
        # Simulate request metrics
        request_data = {'method': 'GET', 'path': f'/api/test/{i}'}
        response_data = {'response_time': 0.1 + (i * 0.05), 'status_code': 200 if i < 8 else 500}
        
        monitoring.record_request_metrics(request_data, response_data)
        
        # Simulate backend metrics
        monitoring.record_backend_metrics(f"server_{i % 3}", response_data['response_time'], response_data['status_code'] == 200)
        
        await asyncio.sleep(0.1)
    
    # Get metrics summary
    summary = monitoring.get_metrics_summary(time_window_minutes=5)
    print(f"\n📊 Metrics Summary:")
    print(f"   Request rate: {summary['request_rate']:.2f} req/s")
    print(f"   Avg response time: {summary['avg_response_time']:.3f}s")
    print(f"   Error rate: {summary['error_rate']:.1f}%")
    print(f"   Active alerts: {summary['active_alerts']}")
    
    # Check for alerts
    alerts = monitoring.get_active_alerts()
    if alerts:
        print(f"\n🚨 Active Alerts:")
        for alert in alerts:
            print(f"   {alert.severity.value.upper()}: {alert.title}")
    
    await monitoring.stop()
    print("\n🛑 Monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())