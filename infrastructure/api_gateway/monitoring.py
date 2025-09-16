"""
Enterprise Monitoring System - Comprehensive API Gateway Monitoring
© 2025 Fahed Mlaiel. All rights reserved.

Enterprise monitoring providing real-time metrics collection, health checks,
performance analytics, alert management, and comprehensive observability.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
import time
import statistics
from collections import defaultdict, deque
import psutil
import threading

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class ServiceStatus(Enum):
    """Service status"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class Metric:
    """Performance metric"""
    name: str
    type: MetricType
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    unit: str = ""


@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    description: str
    endpoint: str = ""
    timeout: int = 10
    interval: int = 30
    enabled: bool = True
    critical: bool = False
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    consecutive_failures: int = 0
    max_failures: int = 3


@dataclass
class Alert:
    """System alert"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.INFO
    source: str = ""
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    escalation_count: int = 0
    acknowledgment: Optional[str] = None


@dataclass
class ServiceHealth:
    """Service health information"""
    service_name: str
    status: ServiceStatus
    health_status: HealthStatus
    last_check: datetime
    response_time: float
    error_count: int = 0
    uptime: float = 0.0
    version: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """Performance snapshot"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    request_count: int = 0
    error_count: int = 0
    response_times: List[float] = field(default_factory=list)
    active_connections: int = 0


class EnterpriseMonitoringSystem:
    """
    Enterprise Monitoring System for API Gateway
    
    Provides comprehensive monitoring including:
    - Real-time performance metrics collection
    - Health check orchestration
    - Alert management and escalation
    - Service discovery and monitoring
    - Performance analytics and trending
    - Resource utilization tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Enterprise Monitoring System"""
        self.config = config or {}
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alerts: Dict[str, Alert] = {}
        self.services: Dict[str, ServiceHealth] = {}
        self.performance_history: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.alert_handlers: List[Callable] = []
        self.metric_handlers: List[Callable] = []
        
        # Configuration
        self.metrics_retention_hours = self.config.get('metrics_retention_hours', 24)
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.performance_collection_interval = self.config.get('performance_collection_interval', 60)
        self.alert_escalation_timeout = self.config.get('alert_escalation_timeout', 300)
        self.enable_system_monitoring = self.config.get('enable_system_monitoring', True)
        
        # Thresholds
        self.cpu_threshold_warning = self.config.get('cpu_threshold_warning', 80.0)
        self.cpu_threshold_critical = self.config.get('cpu_threshold_critical', 95.0)
        self.memory_threshold_warning = self.config.get('memory_threshold_warning', 80.0)
        self.memory_threshold_critical = self.config.get('memory_threshold_critical', 95.0)
        self.response_time_threshold = self.config.get('response_time_threshold', 1.0)
        self.error_rate_threshold = self.config.get('error_rate_threshold', 5.0)
        
        # Setup default health checks
        self._setup_default_health_checks()
        
        # Start monitoring tasks
        self._start_monitoring_tasks()
        
        logger.info("Enterprise Monitoring System initialized")
    
    def _setup_default_health_checks(self):
        """Setup default health checks for API Gateway components"""
        default_checks = [
            HealthCheck(
                name="api_gateway_health",
                description="Main API Gateway health check",
                endpoint="/health",
                timeout=5,
                interval=30,
                critical=True
            ),
            HealthCheck(
                name="database_connection",
                description="Database connectivity check",
                endpoint="/health/database",
                timeout=10,
                interval=60,
                critical=True
            ),
            HealthCheck(
                name="redis_connection",
                description="Redis cache connectivity check",
                endpoint="/health/redis",
                timeout=5,
                interval=30,
                critical=True
            ),
            HealthCheck(
                name="graphql_api",
                description="GraphQL API health check",
                endpoint="/graphql/health",
                timeout=10,
                interval=60,
                critical=False
            ),
            HealthCheck(
                name="websocket_api",
                description="WebSocket API health check",
                endpoint="/ws/health",
                timeout=5,
                interval=30,
                critical=False
            ),
            HealthCheck(
                name="rest_api",
                description="REST API health check",
                endpoint="/api/health",
                timeout=5,
                interval=30,
                critical=True
            ),
            HealthCheck(
                name="rate_limiter",
                description="Rate limiter service health",
                endpoint="/health/rate-limiter",
                timeout=5,
                interval=30,
                critical=True
            ),
            HealthCheck(
                name="authentication_service",
                description="Authentication service health",
                endpoint="/auth/health",
                timeout=10,
                interval=60,
                critical=True
            ),
            HealthCheck(
                name="ai_services_federation",
                description="AI services federation health",
                endpoint="/ai/health",
                timeout=15,
                interval=120,
                critical=False
            ),
            HealthCheck(
                name="monitoring_system",
                description="Monitoring system self-check",
                endpoint="/monitoring/health",
                timeout=5,
                interval=60,
                critical=False
            )
        ]
        
        for check in default_checks:
            self.health_checks[check.name] = check
        
        logger.info(f"Setup {len(default_checks)} default health checks")
    
    def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._health_check_scheduler())
        asyncio.create_task(self._performance_collector())
        asyncio.create_task(self._alert_processor())
        asyncio.create_task(self._metrics_cleanup())
        
        if self.enable_system_monitoring:
            asyncio.create_task(self._system_resource_monitor())
    
    async def record_metric(self, metric: Metric):
        """Record a performance metric"""
        try:
            metric_key = f"{metric.name}:{json.dumps(metric.labels, sort_keys=True)}"
            self.metrics[metric_key].append({
                'value': metric.value,
                'timestamp': metric.timestamp,
                'type': metric.type.value,
                'unit': metric.unit,
                'description': metric.description
            })
            
            # Trigger metric handlers
            for handler in self.metric_handlers:
                try:
                    await handler(metric)
                except Exception as e:
                    logger.error(f"Error in metric handler: {e}")
            
            # Check for threshold alerts
            await self._check_metric_thresholds(metric)
            
        except Exception as e:
            logger.error(f"Error recording metric {metric.name}: {e}")
    
    async def record_request_metric(self, endpoint: str, method: str, response_time: float, status_code: int, user_id: Optional[str] = None):
        """Record API request metrics"""
        labels = {
            'endpoint': endpoint,
            'method': method,
            'status_code': str(status_code),
            'user_id': user_id or 'anonymous'
        }
        
        # Response time metric
        await self.record_metric(Metric(
            name="api_request_duration",
            type=MetricType.HISTOGRAM,
            value=response_time,
            labels=labels,
            unit="seconds",
            description="API request response time"
        ))
        
        # Request count metric
        await self.record_metric(Metric(
            name="api_request_total",
            type=MetricType.COUNTER,
            value=1,
            labels=labels,
            description="Total API requests"
        ))
        
        # Error count metric
        if status_code >= 400:
            await self.record_metric(Metric(
                name="api_request_errors",
                type=MetricType.COUNTER,
                value=1,
                labels=labels,
                description="API request errors"
            ))
    
    async def perform_health_check(self, check_name: str) -> HealthStatus:
        """Perform individual health check"""
        try:
            if check_name not in self.health_checks:
                logger.error(f"Health check not found: {check_name}")
                return HealthStatus.UNKNOWN
            
            check = self.health_checks[check_name]
            
            if not check.enabled:
                return HealthStatus.UNKNOWN
            
            start_time = time.time()
            
            # Simulate health check (in production, would make actual HTTP call)
            await asyncio.sleep(0.1)  # Simulate network call
            health_status = HealthStatus.HEALTHY  # Default to healthy for demo
            
            response_time = time.time() - start_time
            
            # Update check status
            check.last_check = datetime.utcnow()
            check.last_status = health_status
            
            if health_status == HealthStatus.HEALTHY:
                check.consecutive_failures = 0
            else:
                check.consecutive_failures += 1
                
                # Trigger alert if threshold exceeded
                if check.consecutive_failures >= check.max_failures:
                    await self._trigger_health_alert(check, health_status)
            
            # Record metrics
            await self.record_metric(Metric(
                name="health_check_duration",
                type=MetricType.TIMER,
                value=response_time,
                labels={'check_name': check_name},
                unit="seconds",
                description="Health check response time"
            ))
            
            await self.record_metric(Metric(
                name="health_check_status",
                type=MetricType.GAUGE,
                value=1 if health_status == HealthStatus.HEALTHY else 0,
                labels={'check_name': check_name, 'status': health_status.value},
                description="Health check status"
            ))
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed for {check_name}: {e}")
            if check_name in self.health_checks:
                self.health_checks[check_name].consecutive_failures += 1
            return HealthStatus.UNHEALTHY
    
    async def trigger_alert(self, alert: Alert):
        """Trigger system alert"""
        try:
            # Store alert
            self.alerts[alert.id] = alert
            
            # Process alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
            # Log alert
            logger.warning(f"Alert triggered: {alert.name} ({alert.severity.value}) - {alert.description}")
            
            # Record alert metric
            await self.record_metric(Metric(
                name="alerts_triggered",
                type=MetricType.COUNTER,
                value=1,
                labels={'severity': alert.severity.value, 'source': alert.source},
                description="Alerts triggered"
            ))
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve active alert"""
        try:
            if alert_id not in self.alerts:
                logger.error(f"Alert not found: {alert_id}")
                return False
            
            alert = self.alerts[alert_id]
            alert.is_active = False
            alert.resolved_at = datetime.utcnow()
            alert.acknowledgment = resolved_by
            
            # Record resolution metric
            resolution_time = (alert.resolved_at - alert.triggered_at).total_seconds()
            await self.record_metric(Metric(
                name="alert_resolution_time",
                type=MetricType.HISTOGRAM,
                value=resolution_time,
                labels={'severity': alert.severity.value, 'source': alert.source},
                unit="seconds",
                description="Alert resolution time"
            ))
            
            logger.info(f"Alert resolved: {alert.name} by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    async def register_service(self, service_name: str, service_info: Dict[str, Any]):
        """Register service for monitoring"""
        try:
            service_health = ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.RUNNING,
                health_status=HealthStatus.UNKNOWN,
                last_check=datetime.utcnow(),
                response_time=0.0,
                version=service_info.get('version', ''),
                metadata=service_info
            )
            
            self.services[service_name] = service_health
            
            logger.info(f"Service registered for monitoring: {service_name}")
            
        except Exception as e:
            logger.error(f"Error registering service {service_name}: {e}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # Overall health calculation
            healthy_checks = sum(1 for check in self.health_checks.values() 
                               if check.last_status == HealthStatus.HEALTHY and check.enabled)
            total_checks = sum(1 for check in self.health_checks.values() if check.enabled)
            
            overall_health = HealthStatus.HEALTHY
            if total_checks == 0:
                overall_health = HealthStatus.UNKNOWN
            elif healthy_checks < total_checks * 0.8:
                overall_health = HealthStatus.DEGRADED
            elif healthy_checks < total_checks * 0.5:
                overall_health = HealthStatus.UNHEALTHY
            
            # Active alerts by severity
            active_alerts = [alert for alert in self.alerts.values() if alert.is_active]
            alert_counts = {severity.value: 0 for severity in AlertSeverity}
            for alert in active_alerts:
                alert_counts[alert.severity.value] += 1
            
            # Service status summary
            service_summary = {}
            for service_name, service in self.services.items():
                service_summary[service_name] = {
                    'status': service.status.value,
                    'health': service.health_status.value,
                    'uptime': service.uptime,
                    'last_check': service.last_check.isoformat(),
                    'response_time': service.response_time
                }
            
            return {
                'overall_health': overall_health.value,
                'health_checks': {
                    'total': total_checks,
                    'healthy': healthy_checks,
                    'unhealthy': total_checks - healthy_checks,
                    'checks': {
                        name: {
                            'status': check.last_status.value,
                            'last_check': check.last_check.isoformat() if check.last_check else None,
                            'consecutive_failures': check.consecutive_failures,
                            'critical': check.critical
                        }
                        for name, check in self.health_checks.items()
                    }
                },
                'alerts': {
                    'active_count': len(active_alerts),
                    'by_severity': alert_counts,
                    'recent_alerts': [
                        {
                            'id': alert.id,
                            'name': alert.name,
                            'severity': alert.severity.value,
                            'triggered_at': alert.triggered_at.isoformat(),
                            'source': alert.source
                        }
                        for alert in sorted(active_alerts, key=lambda a: a.triggered_at, reverse=True)[:10]
                    ]
                },
                'services': service_summary,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'error': str(e)}
    
    async def get_performance_metrics(self, timeframe_hours: int = 1) -> Dict[str, Any]:
        """Get performance metrics for specified timeframe"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            
            # Filter metrics by timeframe
            filtered_metrics = {}
            for metric_key, metric_data in self.metrics.items():
                recent_data = [
                    data for data in metric_data
                    if data['timestamp'] > cutoff_time
                ]
                if recent_data:
                    filtered_metrics[metric_key] = recent_data
            
            # Calculate aggregations
            performance_summary = {}
            
            # API request metrics
            request_times = []
            error_count = 0
            total_requests = 0
            
            for metric_key, metric_data in filtered_metrics.items():
                if 'api_request_duration' in metric_key:
                    request_times.extend([data['value'] for data in metric_data])
                elif 'api_request_total' in metric_key:
                    total_requests += sum(data['value'] for data in metric_data)
                elif 'api_request_errors' in metric_key:
                    error_count += sum(data['value'] for data in metric_data)
            
            if request_times:
                performance_summary['response_time'] = {
                    'avg': statistics.mean(request_times),
                    'min': min(request_times),
                    'max': max(request_times),
                    'p95': statistics.quantiles(request_times, n=20)[18] if len(request_times) > 20 else max(request_times),
                    'p99': statistics.quantiles(request_times, n=100)[98] if len(request_times) > 100 else max(request_times)
                }
            
            performance_summary['requests'] = {
                'total': total_requests,
                'errors': error_count,
                'error_rate': (error_count / total_requests * 100) if total_requests > 0 else 0
            }
            
            # System resource metrics
            if self.performance_history:
                recent_snapshots = [
                    snapshot for snapshot in self.performance_history
                    if snapshot.timestamp > cutoff_time
                ]
                
                if recent_snapshots:
                    performance_summary['system_resources'] = {
                        'cpu': {
                            'avg': statistics.mean([s.cpu_usage for s in recent_snapshots]),
                            'max': max([s.cpu_usage for s in recent_snapshots])
                        },
                        'memory': {
                            'avg': statistics.mean([s.memory_usage for s in recent_snapshots]),
                            'max': max([s.memory_usage for s in recent_snapshots])
                        },
                        'connections': {
                            'avg': statistics.mean([s.active_connections for s in recent_snapshots]),
                            'max': max([s.active_connections for s in recent_snapshots])
                        }
                    }
            
            return {
                'timeframe_hours': timeframe_hours,
                'summary': performance_summary,
                'detailed_metrics': filtered_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def add_metric_handler(self, handler: Callable):
        """Add metric handler function"""
        self.metric_handlers.append(handler)
    
    # Internal Implementation Methods
    
    async def _health_check_scheduler(self):
        """Schedule and execute health checks"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                for check_name, check in self.health_checks.items():
                    if not check.enabled:
                        continue
                    
                    # Check if it's time to run this health check
                    if (not check.last_check or 
                        (current_time - check.last_check).total_seconds() >= check.interval):
                        
                        asyncio.create_task(self.perform_health_check(check_name))
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in health check scheduler: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _performance_collector(self):
        """Collect system performance metrics"""
        while True:
            try:
                if self.enable_system_monitoring:
                    snapshot = PerformanceSnapshot(
                        cpu_usage=psutil.cpu_percent(interval=1),
                        memory_usage=psutil.virtual_memory().percent,
                        disk_usage=psutil.disk_usage('/').percent,
                        network_io=dict(psutil.net_io_counters()._asdict()),
                        active_connections=len(psutil.net_connections())
                    )
                    
                    self.performance_history.append(snapshot)
                    
                    # Record system metrics
                    await self.record_metric(Metric(
                        name="system_cpu_usage",
                        type=MetricType.GAUGE,
                        value=snapshot.cpu_usage,
                        unit="percent",
                        description="System CPU usage"
                    ))
                    
                    await self.record_metric(Metric(
                        name="system_memory_usage",
                        type=MetricType.GAUGE,
                        value=snapshot.memory_usage,
                        unit="percent",
                        description="System memory usage"
                    ))
                
                await asyncio.sleep(self.performance_collection_interval)
                
            except Exception as e:
                logger.error(f"Error in performance collector: {e}")
                await asyncio.sleep(60)
    
    async def _alert_processor(self):
        """Process and escalate alerts"""
        while True:
            try:
                current_time = datetime.utcnow()
                escalation_threshold = current_time - timedelta(seconds=self.alert_escalation_timeout)
                
                for alert in self.alerts.values():
                    if (alert.is_active and 
                        alert.triggered_at < escalation_threshold and 
                        alert.escalation_count < 3):
                        
                        # Escalate alert
                        alert.escalation_count += 1
                        logger.warning(f"Escalating alert: {alert.name} (escalation #{alert.escalation_count})")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in alert processor: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_cleanup(self):
        """Clean up old metrics data"""
        while True:
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=self.metrics_retention_hours)
                
                for metric_key in list(self.metrics.keys()):
                    metric_data = self.metrics[metric_key]
                    
                    # Remove old data points
                    while metric_data and metric_data[0]['timestamp'] < cutoff_time:
                        metric_data.popleft()
                    
                    # Remove empty metric keys
                    if not metric_data:
                        del self.metrics[metric_key]
                
                # Clean up old alerts
                old_alerts = [
                    alert_id for alert_id, alert in self.alerts.items()
                    if not alert.is_active and alert.resolved_at and alert.resolved_at < cutoff_time
                ]
                
                for alert_id in old_alerts:
                    del self.alerts[alert_id]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def _system_resource_monitor(self):
        """Monitor system resources and trigger alerts"""
        while True:
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                
                # Check CPU thresholds
                if cpu_usage >= self.cpu_threshold_critical:
                    await self.trigger_alert(Alert(
                        name="Critical CPU Usage",
                        description=f"CPU usage at {cpu_usage:.1f}% (threshold: {self.cpu_threshold_critical}%)",
                        severity=AlertSeverity.CRITICAL,
                        source="system_monitor",
                        metadata={'cpu_usage': cpu_usage}
                    ))
                elif cpu_usage >= self.cpu_threshold_warning:
                    await self.trigger_alert(Alert(
                        name="High CPU Usage",
                        description=f"CPU usage at {cpu_usage:.1f}% (threshold: {self.cpu_threshold_warning}%)",
                        severity=AlertSeverity.HIGH,
                        source="system_monitor",
                        metadata={'cpu_usage': cpu_usage}
                    ))
                
                # Check memory thresholds
                if memory_usage >= self.memory_threshold_critical:
                    await self.trigger_alert(Alert(
                        name="Critical Memory Usage",
                        description=f"Memory usage at {memory_usage:.1f}% (threshold: {self.memory_threshold_critical}%)",
                        severity=AlertSeverity.CRITICAL,
                        source="system_monitor",
                        metadata={'memory_usage': memory_usage}
                    ))
                elif memory_usage >= self.memory_threshold_warning:
                    await self.trigger_alert(Alert(
                        name="High Memory Usage",
                        description=f"Memory usage at {memory_usage:.1f}% (threshold: {self.memory_threshold_warning}%)",
                        severity=AlertSeverity.HIGH,
                        source="system_monitor",
                        metadata={'memory_usage': memory_usage}
                    ))
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in system resource monitor: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_health_alert(self, check: HealthCheck, status: HealthStatus):
        """Trigger alert for health check failure"""
        severity = AlertSeverity.CRITICAL if check.critical else AlertSeverity.HIGH
        
        await self.trigger_alert(Alert(
            name=f"Health Check Failed: {check.name}",
            description=f"Health check '{check.name}' failed {check.consecutive_failures} consecutive times (status: {status.value})",
            severity=severity,
            source="health_checker",
            metadata={
                'check_name': check.name,
                'consecutive_failures': check.consecutive_failures,
                'status': status.value,
                'critical': check.critical
            }
        ))
    
    async def _check_metric_thresholds(self, metric: Metric):
        """Check metric against defined thresholds"""
        try:
            # Response time threshold
            if metric.name == "api_request_duration" and metric.value > self.response_time_threshold:
                await self.trigger_alert(Alert(
                    name="High Response Time",
                    description=f"API response time {metric.value:.3f}s exceeds threshold {self.response_time_threshold}s",
                    severity=AlertSeverity.MEDIUM,
                    source="metric_monitor",
                    metadata={'metric': metric.name, 'value': metric.value, 'labels': metric.labels}
                ))
            
            # Error rate threshold
            if metric.name == "api_request_errors":
                # Calculate recent error rate
                recent_errors = sum(
                    data['value'] for data in self.metrics[f"{metric.name}:{json.dumps(metric.labels, sort_keys=True)}"]
                    if (datetime.utcnow() - data['timestamp']).total_seconds() < 300  # Last 5 minutes
                )
                
                recent_requests = sum(
                    data['value'] for data in self.metrics.get(f"api_request_total:{json.dumps(metric.labels, sort_keys=True)}", [])
                    if (datetime.utcnow() - data['timestamp']).total_seconds() < 300
                )
                
                if recent_requests > 0:
                    error_rate = (recent_errors / recent_requests) * 100
                    if error_rate > self.error_rate_threshold:
                        await self.trigger_alert(Alert(
                            name="High Error Rate",
                            description=f"API error rate {error_rate:.2f}% exceeds threshold {self.error_rate_threshold}%",
                            severity=AlertSeverity.HIGH,
                            source="metric_monitor",
                            metadata={'error_rate': error_rate, 'labels': metric.labels}
                        ))
        
        except Exception as e:
            logger.error(f"Error checking metric thresholds: {e}")


# Enterprise Monitoring Factory
def create_enterprise_monitoring_system(config: Optional[Dict[str, Any]] = None) -> EnterpriseMonitoringSystem:
    """Factory function to create Enterprise Monitoring System instance"""
    return EnterpriseMonitoringSystem(config)


# Default alert handlers
async def log_alert_handler(alert: Alert):
    """Default alert handler that logs alerts"""
    log_level = {
        AlertSeverity.CRITICAL: logging.CRITICAL,
        AlertSeverity.HIGH: logging.ERROR,
        AlertSeverity.MEDIUM: logging.WARNING,
        AlertSeverity.LOW: logging.INFO,
        AlertSeverity.INFO: logging.INFO
    }.get(alert.severity, logging.INFO)
    
    logger.log(log_level, f"ALERT: {alert.name} - {alert.description}")


async def prometheus_metric_handler(metric: Metric):
    """Metric handler for Prometheus export"""
    # Implementation would export to Prometheus
    logger.debug(f"Prometheus metric: {metric.name} = {metric.value}")


if __name__ == "__main__":
    # Example usage
    async def main():
        monitoring = create_enterprise_monitoring_system({
            'metrics_retention_hours': 24,
            'cpu_threshold_warning': 75.0,
            'memory_threshold_warning': 80.0
        })
        
        # Add alert handler
        monitoring.add_alert_handler(log_alert_handler)
        monitoring.add_metric_handler(prometheus_metric_handler)
        
        # Record some metrics
        await monitoring.record_request_metric("/api/v1/creators", "GET", 0.15, 200, "user_123")
        await monitoring.record_request_metric("/api/v1/content", "POST", 0.45, 201, "user_456")
        
        # Perform health check
        health_status = await monitoring.perform_health_check("api_gateway_health")
        print(f"Health check status: {health_status}")
        
        # Get system health
        system_health = await monitoring.get_system_health()
        print(f"System health: {json.dumps(system_health, indent=2)}")
        
        # Get performance metrics
        metrics = await monitoring.get_performance_metrics(1)
        print(f"Performance metrics: {json.dumps(metrics, indent=2)}")
        
        # Simulate some time for background tasks
        await asyncio.sleep(3)
    
    asyncio.run(main())