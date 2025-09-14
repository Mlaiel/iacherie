"""Integration Monitoring and Health - Enterprise Monitoring System
================================================================

Comprehensive monitoring system for integration health, performance tracking,
and real-time observability across all third-party integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

import httpx
import psutil
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry


class IntegrationHealth(Enum):
    """Integration health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Metric types for monitoring."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class HealthCheck:
    """Health check configuration."""
    name: str
    endpoint: str
    method: str = "GET"
    timeout: float = 5.0
    interval: float = 30.0
    headers: Dict[str, str] = field(default_factory=dict)
    expected_status: Set[int] = field(default_factory=lambda: {200})
    expected_response_time: float = 2.0
    dependency_checks: List[str] = field(default_factory=list)


@dataclass
class IntegrationMetrics:
    """Integration performance metrics."""
    integration_name: str
    request_count: int = 0
    error_count: int = 0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None
    health_status: IntegrationHealth = IntegrationHealth.UNKNOWN
    uptime_percentage: float = 0.0


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    condition: str  # Python expression
    threshold: float
    duration: timedelta
    severity: str = "warning"  # info, warning, error, critical
    channels: List[str] = field(default_factory=list)
    enabled: bool = True


class IntegrationMonitoring:
    """Enterprise integration monitoring system."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.health_checks: Dict[str, HealthCheck] = {}
        self.integration_metrics: Dict[str, IntegrationMetrics] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # System monitoring
        self.system_metrics = {
            'cpu_usage': deque(maxlen=100),
            'memory_usage': deque(maxlen=100),
            'disk_usage': deque(maxlen=100),
            'network_io': deque(maxlen=100)
        }
        
        # Monitoring tasks
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()
        
        # Performance tracking
        self.performance_baselines = {}
        self.anomaly_detection_enabled = True
        
    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics collectors."""
        self.prometheus_metrics = {
            'request_counter': Counter(
                'integration_requests_total',
                'Total integration requests',
                ['integration', 'status'],
                registry=self.registry
            ),
            'response_time': Histogram(
                'integration_response_seconds',
                'Integration response time in seconds',
                ['integration'],
                registry=self.registry
            ),
            'health_gauge': Gauge(
                'integration_health_status',
                'Integration health status (0=unhealthy, 1=healthy)',
                ['integration'],
                registry=self.registry
            ),
            'error_rate': Gauge(
                'integration_error_rate',
                'Integration error rate percentage',
                ['integration'],
                registry=self.registry
            )
        }
    
    def add_health_check(self, health_check -> None: HealthCheck) -> None:
        """Add health check configuration."""
        self.health_checks[health_check.name] = health_check
        if health_check.name not in self.integration_metrics:
            self.integration_metrics[health_check.name] = IntegrationMetrics(
                integration_name=health_check.name
            )
        self.logger.info(f"Added health check: {health_check.name}")
    
    def add_alert_rule(self, alert_rule -> None: AlertRule) -> None:
        """Add alert rule configuration."""
        self.alert_rules[alert_rule.name] = alert_rule
        self.logger.info(f"Added alert rule: {alert_rule.name}")
    
    async def start_monitoring(self) -> None:
        """Start monitoring services."""
        self.logger.info("Starting integration monitoring")
        
        # Start health check monitoring
        for name, health_check in self.health_checks.items():
            task = asyncio.create_task(
                self._monitor_health_check(name, health_check)
            )
            self._monitoring_tasks.add(task)
        
        # Start system monitoring
        system_task = asyncio.create_task(self._monitor_system_metrics())
        self._monitoring_tasks.add(system_task)
        
        # Start alert processing
        alert_task = asyncio.create_task(self._process_alerts())
        self._monitoring_tasks.add(alert_task)
        
        # Start performance analysis
        analysis_task = asyncio.create_task(self._analyze_performance())
        self._monitoring_tasks.add(analysis_task)
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring services."""
        self.logger.info("Stopping integration monitoring")
        self._shutdown_event.set()
        
        # Cancel all monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
        self._monitoring_tasks.clear()
    
    async def _monitor_health_check(self, name -> None: str, health_check -> None: HealthCheck) -> None:
        """Monitor a specific health check."""
        while not self._shutdown_event.is_set():
            try:
                start_time = time.time()
                
                # Perform health check
                async with httpx.AsyncClient(timeout=health_check.timeout) as client:
                    response = await client.request(
                        method=health_check.method,
                        url=health_check.endpoint,
                        headers=health_check.headers
                    )
                
                response_time = time.time() - start_time
                
                # Update metrics
                metrics = self.integration_metrics[name]
                metrics.request_count += 1
                metrics.response_times.append(response_time)
                
                # Check health status
                if (response.status_code in health_check.expected_status and
                    response_time <= health_check.expected_response_time):
                    metrics.health_status = IntegrationHealth.HEALTHY
                    metrics.last_success = datetime.now()
                    
                    # Update Prometheus metrics
                    self.prometheus_metrics['request_counter'].labels(
                        integration=name, status='success'
                    ).inc()
                    self.prometheus_metrics['health_gauge'].labels(
                        integration=name
                    ).set(1)
                else:
                    metrics.health_status = IntegrationHealth.DEGRADED
                    metrics.error_count += 1
                    
                    self.prometheus_metrics['request_counter'].labels(
                        integration=name, status='error'
                    ).inc()
                    self.prometheus_metrics['health_gauge'].labels(
                        integration=name
                    ).set(0)
                
                # Update response time metric
                self.prometheus_metrics['response_time'].labels(
                    integration=name
                ).observe(response_time)
                
                # Calculate error rate
                error_rate = (metrics.error_count / metrics.request_count) * 100
                self.prometheus_metrics['error_rate'].labels(
                    integration=name
                ).set(error_rate)
                
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                
                # Update error metrics
                metrics = self.integration_metrics[name]
                metrics.error_count += 1
                metrics.health_status = IntegrationHealth.UNHEALTHY
                metrics.last_error = datetime.now()
                
                self.prometheus_metrics['request_counter'].labels(
                    integration=name, status='error'
                ).inc()
                self.prometheus_metrics['health_gauge'].labels(
                    integration=name
                ).set(0)
            
            # Wait for next check
            await asyncio.sleep(health_check.interval)
    
    async def _monitor_system_metrics(self) -> None:
        """Monitor system-level metrics."""
        while not self._shutdown_event.is_set():
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_metrics['cpu_usage'].append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_metrics['memory_usage'].append(memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.system_metrics['disk_usage'].append(disk_percent)
                
                # Network I/O
                network = psutil.net_io_counters()
                network_total = network.bytes_sent + network.bytes_recv
                self.system_metrics['network_io'].append(network_total)
                
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
            
            await asyncio.sleep(30)  # Monitor every 30 seconds
    
    async def _process_alerts(self) -> None:
        """Process alert rules and trigger notifications."""
        while not self._shutdown_event.is_set():
            try:
                for rule_name, rule in self.alert_rules.items():
                    if not rule.enabled:
                        continue
                    
                    # Evaluate alert condition
                    if self._evaluate_alert_condition(rule):
                        alert_key = f"{rule_name}_{rule.condition}"
                        
                        if alert_key not in self.active_alerts:
                            # New alert
                            alert = {
                                'rule_name': rule_name,
                                'condition': rule.condition,
                                'severity': rule.severity,
                                'started_at': datetime.now(),
                                'notified': False
                            }
                            self.active_alerts[alert_key] = alert
                            
                            # Send notification
                            await self._send_alert_notification(alert, rule)
                            alert['notified'] = True
                    else:
                        # Check if alert should be resolved
                        alert_key = f"{rule_name}_{rule.condition}"
                        if alert_key in self.active_alerts:
                            alert = self.active_alerts[alert_key]
                            duration = datetime.now() - alert['started_at']
                            
                            if duration >= rule.duration:
                                # Resolve alert
                                await self._send_alert_resolution(alert, rule)
                                del self.active_alerts[alert_key]
                
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
            
            await asyncio.sleep(10)  # Check alerts every 10 seconds
    
    def _evaluate_alert_condition(self, rule: AlertRule) -> bool:
        """Evaluate alert condition."""
        try:
            # Create evaluation context
            context = {
                'metrics': self.integration_metrics,
                'system': self.system_metrics,
                'threshold': rule.threshold
            }
            
            # Evaluate condition
            return eval(rule.condition, {"__builtins__": {}}, context)
        except Exception as e:
            self.logger.error(f"Alert condition evaluation error: {e}")
            return False
    
    async def _send_alert_notification(self, alert -> None: Dict[str, Any], rule -> None: AlertRule) -> None:
        """Send alert notification."""
        self.logger.warning(f"ALERT: {alert['rule_name']} - {alert['condition']}")
        
        # Here you would integrate with notification services
        # (email, Slack, PagerDuty, etc.)
        notification_data = {
            'title': f"Integration Alert: {alert['rule_name']}",
            'message': f"Condition: {alert['condition']}",
            'severity': alert['severity'],
            'timestamp': alert['started_at'].isoformat()
        }
        
        # Send to configured channels
        for channel in rule.channels:
            await self._send_to_channel(channel, notification_data)
    
    async def _send_alert_resolution(self, alert -> None: Dict[str, Any], rule -> None: AlertRule) -> None:
        """Send alert resolution notification."""
        self.logger.info(f"RESOLVED: {alert['rule_name']} - {alert['condition']}")
        
        notification_data = {
            'title': f"Integration Alert Resolved: {alert['rule_name']}",
            'message': f"Condition resolved: {alert['condition']}",
            'severity': 'info',
            'timestamp': datetime.now().isoformat()
        }
        
        for channel in rule.channels:
            await self._send_to_channel(channel, notification_data)
    
    async def _send_to_channel(self, channel -> None: str, data -> None: Dict[str, Any]) -> None:
        """Send notification to specific channel."""
        # Implement channel-specific notification logic
        # This is a placeholder for actual implementation
        self.logger.info(f"Sending notification to {channel}: {data}")
    
    async def _analyze_performance(self) -> None:
        """Analyze performance patterns and detect anomalies."""
        while not self._shutdown_event.is_set():
            try:
                for name, metrics in self.integration_metrics.items():
                    if len(metrics.response_times) >= 10:
                        # Calculate performance statistics
                        response_times = list(metrics.response_times)
                        avg_response_time = statistics.mean(response_times)
                        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                        
                        # Update baselines
                        if name not in self.performance_baselines:
                            self.performance_baselines[name] = {
                                'avg_response_time': avg_response_time,
                                'p95_response_time': p95_response_time
                            }
                        else:
                            # Detect anomalies
                            baseline = self.performance_baselines[name]
                            if (avg_response_time > baseline['avg_response_time'] * 1.5 or
                                p95_response_time > baseline['p95_response_time'] * 2.0):
                                self.logger.warning(
                                    f"Performance anomaly detected for {name}: "
                                    f"avg={avg_response_time:.3f}s, p95={p95_response_time:.3f}s"
                                )
                
            except Exception as e:
                self.logger.error(f"Performance analysis error: {e}")
            
            await asyncio.sleep(300)  # Analyze every 5 minutes
    
    def get_integration_status(self, integration_name: str) -> Dict[str, Any]:
        """Get detailed status for specific integration."""
        if integration_name not in self.integration_metrics:
            return {"error": "Integration not found"}
        
        metrics = self.integration_metrics[integration_name]
        response_times = list(metrics.response_times)
        
        status = {
            'name': integration_name,
            'health_status': metrics.health_status.value,
            'request_count': metrics.request_count,
            'error_count': metrics.error_count,
            'error_rate': (metrics.error_count / max(metrics.request_count, 1)) * 100,
            'last_success': metrics.last_success.isoformat() if metrics.last_success else None,
            'last_error': metrics.last_error.isoformat() if metrics.last_error else None,
            'uptime_percentage': metrics.uptime_percentage
        }
        
        if response_times:
            status.update({
                'avg_response_time': statistics.mean(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
            })
        
        return status
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system-level status."""
        status = {}
        
        for metric_name, values in self.system_metrics.items():
            if values:
                status[metric_name] = {
                    'current': values[-1],
                    'average': statistics.mean(values),
                    'max': max(values),
                    'min': min(values)
                }
        
        return status
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of active alerts."""
        return {
            'active_alerts': len(self.active_alerts),
            'alert_details': [
                {
                    'rule_name': alert['rule_name'],
                    'condition': alert['condition'],
                    'severity': alert['severity'],
                    'duration': (datetime.now() - alert['started_at']).total_seconds(),
                    'notified': alert['notified']
                }
                for alert in self.active_alerts.values()
            ]
        }
    
    def export_metrics(self, format_type: str = "prometheus") -> str:
        """Export metrics in specified format."""
        if format_type == "prometheus":
            from prometheus_client import generate_latest
            return generate_latest(self.registry).decode('utf-8')
        elif format_type == "json":
            metrics_data = {
                'integrations': {
                    name: self.get_integration_status(name)
                    for name in self.integration_metrics.keys()
                },
                'system': self.get_system_status(),
                'alerts': self.get_alert_summary()
            }
            return json.dumps(metrics_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")


# Example usage and configuration
if __name__ == "__main__":
    # Example monitoring configuration
    monitoring = IntegrationMonitoring()
    
    # Add health checks
    monitoring.add_health_check(HealthCheck(
        name="openai_api",
        endpoint="https://api.openai.com/v1/models",
        headers={"Authorization": "Bearer your-api-key"},
        timeout=10.0,
        interval=60.0
    ))
    
    # Add alert rules
    monitoring.add_alert_rule(AlertRule(
        name="high_error_rate",
        condition="metrics['openai_api'].error_count / max(metrics['openai_api'].request_count, 1) > threshold",
        threshold=0.1,  # 10% error rate
        duration=timedelta(minutes=5),
        severity="error",
        channels=["slack", "email"]
    ))
    
    async def main() -> None:
        await monitoring.start_monitoring()
        # Keep running
        await asyncio.sleep(3600)  # Run for 1 hour
        await monitoring.stop_monitoring()
    
    asyncio.run(main())