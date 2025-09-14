#!/usr/bin/env python3
"""
📊 MONITORING SERVICE
====================

Advanced real-time system monitoring and alerting service for the Ainflue platform.
Handles system metrics, performance monitoring, health checks, and intelligent alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import socket
import threading
from collections import deque, defaultdict
import statistics
import redis.asyncio as redis
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MonitorType(Enum):
    """Monitor type enumeration"""
    SYSTEM = "system"
    APPLICATION = "application"
    NETWORK = "network"
    DATABASE = "database"
    CUSTOM = "custom"

class MetricType(Enum):
    """Metric type enumeration"""
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    severity: AlertSeverity
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class MonitorCheck:
    """Monitor check definition"""
    id: str
    name: str
    monitor_type: MonitorType
    check_function: str
    threshold: float
    comparison: str  # >, <, >=, <=, ==, !=
    enabled: bool = True
    interval: int = 60  # seconds
    timeout: int = 30
    last_check: Optional[datetime] = None
    last_value: Optional[float] = None
    alert_threshold: int = 3  # consecutive failures before alert

@dataclass
class SystemMetrics:
    """System metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int
    memory_used: int
    disk_percent: float
    disk_free: int
    disk_used: int
    network_sent: int
    network_recv: int
    load_average: List[float]
    process_count: int
    uptime: float

@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    timestamp: datetime
    response_time: float
    request_count: int
    error_count: int
    active_connections: int
    queue_size: int
    cache_hit_rate: float
    throughput: float

class MetricsCollector:
    """System and application metrics collector"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        self.cpu_gauge = Gauge('system_cpu_percent', 'CPU usage percentage', registry=self.registry)
        self.memory_gauge = Gauge('system_memory_percent', 'Memory usage percentage', registry=self.registry)
        self.disk_gauge = Gauge('system_disk_percent', 'Disk usage percentage', registry=self.registry)
        self.network_sent_counter = Counter('system_network_sent_bytes', 'Network bytes sent', registry=self.registry)
        self.network_recv_counter = Counter('system_network_recv_bytes', 'Network bytes received', registry=self.registry)
        self.request_counter = Counter('app_requests_total', 'Total application requests', registry=self.registry)
        self.response_time_histogram = Histogram('app_response_time_seconds', 'Response time histogram', registry=self.registry)
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Load average
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            # Process count
            process_count = len(psutil.pids())
            
            # System uptime
            uptime = time.time() - psutil.boot_time()
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available=memory.available,
                memory_used=memory.used,
                disk_percent=disk.percent,
                disk_free=disk.free,
                disk_used=disk.used,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                load_average=list(load_avg),
                process_count=process_count,
                uptime=uptime
            )
            
            # Update Prometheus metrics
            self.cpu_gauge.set(cpu_percent)
            self.memory_gauge.set(memory.percent)
            self.disk_gauge.set(disk.percent)
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
            raise
    
    def collect_application_metrics(self, app_stats: Dict[str, Any] = None) -> ApplicationMetrics:
        """Collect application-specific metrics"""
        try:
            app_stats = app_stats or {}
            
            metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                response_time=app_stats.get('response_time', 0.0),
                request_count=app_stats.get('request_count', 0),
                error_count=app_stats.get('error_count', 0),
                active_connections=app_stats.get('active_connections', 0),
                queue_size=app_stats.get('queue_size', 0),
                cache_hit_rate=app_stats.get('cache_hit_rate', 0.0),
                throughput=app_stats.get('throughput', 0.0)
            )
            
            # Update Prometheus metrics
            self.request_counter.inc(metrics.request_count)
            self.response_time_histogram.observe(metrics.response_time)
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to collect application metrics", error=str(e))
            raise
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')

class AlertManager:
    """Alert management and notification system"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_handlers: List[Callable] = []
        self.alert_history: deque = deque(maxlen=1000)
        
    def add_notification_handler(self, handler: Callable):
        """Add a notification handler"""
        self.notification_handlers.append(handler)
        logger.info("Added notification handler", handler=handler.__name__)
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule"""
        self.alert_rules.append(rule)
        logger.info("Added alert rule", rule=rule)
    
    async def check_alert_rules(self, metrics: Dict[str, Any]):
        """Check metrics against alert rules"""
        for rule in self.alert_rules:
            try:
                metric_name = rule['metric']
                threshold = rule['threshold']
                comparison = rule['comparison']
                severity = AlertSeverity(rule['severity'])
                
                if metric_name in metrics:
                    value = metrics[metric_name]
                    
                    # Evaluate condition
                    triggered = False
                    if comparison == '>':
                        triggered = value > threshold
                    elif comparison == '<':
                        triggered = value < threshold
                    elif comparison == '>=':
                        triggered = value >= threshold
                    elif comparison == '<=':
                        triggered = value <= threshold
                    elif comparison == '==':
                        triggered = value == threshold
                    elif comparison == '!=':
                        triggered = value != threshold
                    
                    if triggered:
                        await self.create_alert(
                            name=rule['name'],
                            severity=severity,
                            message=f"{rule['message']} (value: {value}, threshold: {threshold})",
                            source=rule.get('source', 'monitoring'),
                            metadata={'metric': metric_name, 'value': value, 'threshold': threshold}
                        )
                        
            except Exception as e:
                logger.error("Error checking alert rule", rule=rule, error=str(e))
    
    async def create_alert(self, name: str, severity: AlertSeverity, message: str, 
                          source: str = "monitoring", metadata: Dict[str, Any] = None):
        """Create a new alert"""
        alert_id = f"alert_{int(time.time())}_{hash(name) % 10000}"
        
        alert = Alert(
            id=alert_id,
            name=name,
            severity=severity,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        logger.warning("Alert created", alert_id=alert_id, name=name, severity=severity.value)
        return alert_id
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            
            await self._send_notifications(self.alerts[alert_id], resolved=True)
            logger.info("Alert resolved", alert_id=alert_id)
            return True
        return False
    
    async def _send_notifications(self, alert: Alert, resolved: bool = False):
        """Send alert notifications"""
        for handler in self.notification_handlers:
            try:
                await handler(alert, resolved)
            except Exception as e:
                logger.error("Notification handler failed", handler=handler.__name__, error=str(e))
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        active_alerts = self.get_active_alerts()
        
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active_alerts),
            'critical_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            'error_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.ERROR]),
            'warning_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.WARNING]),
            'info_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.INFO])
        }

class HealthChecker:
    """Health check system for services and endpoints"""
    
    def __init__(self):
        self.health_checks: Dict[str, MonitorCheck] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)
        
    def add_health_check(self, check: MonitorCheck):
        """Add a health check"""
        self.health_checks[check.id] = check
        logger.info("Added health check", check_id=check.id, name=check.name)
    
    async def check_http_endpoint(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """Check HTTP endpoint health"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    
                    return {
                        'status': 'healthy' if response.status < 400 else 'unhealthy',
                        'status_code': response.status,
                        'response_time': response_time,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_tcp_port(self, host: str, port: int, timeout: int = 10) -> Dict[str, Any]:
        """Check TCP port connectivity"""
        try:
            start_time = time.time()
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout
            )
            
            writer.close()
            await writer.wait_closed()
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_database_connection(self, connection_string: str) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # This is a simplified example - implement based on your database type
            start_time = time.time()
            
            # Simulate database check
            await asyncio.sleep(0.1)
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all configured health checks"""
        results = {}
        
        for check_id, check in self.health_checks.items():
            try:
                if check.check_function == 'http_endpoint':
                    result = await self.check_http_endpoint(check.id, check.timeout)
                elif check.check_function == 'tcp_port':
                    host, port = check.id.split(':')
                    result = await self.check_tcp_port(host, int(port), check.timeout)
                elif check.check_function == 'database':
                    result = await self.check_database_connection(check.id)
                else:
                    result = {'status': 'unknown', 'error': 'Unknown check function'}
                
                # Update failure count
                if result['status'] == 'unhealthy':
                    self.failure_counts[check_id] += 1
                else:
                    self.failure_counts[check_id] = 0
                
                results[check_id] = result
                
            except Exception as e:
                logger.error("Health check failed", check_id=check_id, error=str(e))
                results[check_id] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results

class MonitoringService:
    """Advanced real-time system monitoring and alerting service"""
    
    def __init__(self):
        self.service_name = "MonitoringService"
        self.version = "1.0.0"
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_checker = HealthChecker()
        self.redis_client: Optional[redis.Redis] = None
        self.monitoring_enabled = True
        self.collection_interval = 30  # seconds
        self.metrics_history: deque = deque(maxlen=1000)
        self.monitoring_tasks: List[asyncio.Task] = []
        
        logger.info("Monitoring service initialized", service=self.service_name, version=self.version)
    
    async def initialize(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the monitoring service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Setup default alert rules
            self._setup_default_alert_rules()
            
            # Setup default notification handlers
            self._setup_default_notification_handlers()
            
            # Setup default health checks
            self._setup_default_health_checks()
            
            logger.info("Monitoring service initialized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to initialize monitoring service", error=str(e))
            return False
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        default_rules = [
            {
                'name': 'High CPU Usage',
                'metric': 'cpu_percent',
                'threshold': 80.0,
                'comparison': '>',
                'severity': 'warning',
                'message': 'CPU usage is above 80%',
                'source': 'system'
            },
            {
                'name': 'Critical CPU Usage',
                'metric': 'cpu_percent',
                'threshold': 95.0,
                'comparison': '>',
                'severity': 'critical',
                'message': 'CPU usage is critically high',
                'source': 'system'
            },
            {
                'name': 'High Memory Usage',
                'metric': 'memory_percent',
                'threshold': 85.0,
                'comparison': '>',
                'severity': 'warning',
                'message': 'Memory usage is above 85%',
                'source': 'system'
            },
            {
                'name': 'High Disk Usage',
                'metric': 'disk_percent',
                'threshold': 90.0,
                'comparison': '>',
                'severity': 'error',
                'message': 'Disk usage is above 90%',
                'source': 'system'
            }
        ]
        
        for rule in default_rules:
            self.alert_manager.add_alert_rule(rule)
    
    def _setup_default_notification_handlers(self):
        """Setup default notification handlers"""
        
        async def log_notification_handler(alert: Alert, resolved: bool = False):
            """Log-based notification handler"""
            if resolved:
                logger.info("Alert resolved", alert_id=alert.id, name=alert.name)
            else:
                logger.warning("Alert triggered", 
                             alert_id=alert.id, 
                             name=alert.name, 
                             severity=alert.severity.value,
                             message=alert.message)
        
        async def redis_notification_handler(alert: Alert, resolved: bool = False):
            """Redis-based notification handler"""
            if self.redis_client:
                try:
                    alert_data = {
                        'id': alert.id,
                        'name': alert.name,
                        'severity': alert.severity.value,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat(),
                        'resolved': resolved
                    }
                    
                    # Publish to Redis channel
                    await self.redis_client.publish('monitoring:alerts', json.dumps(alert_data))
                    
                    # Store in Redis list
                    await self.redis_client.lpush('monitoring:alert_history', json.dumps(alert_data))
                    await self.redis_client.ltrim('monitoring:alert_history', 0, 999)  # Keep last 1000
                    
                except Exception as e:
                    logger.error("Redis notification failed", error=str(e))
        
        self.alert_manager.add_notification_handler(log_notification_handler)
        self.alert_manager.add_notification_handler(redis_notification_handler)
    
    def _setup_default_health_checks(self):
        """Setup default health checks"""
        # Add Redis health check
        redis_check = MonitorCheck(
            id="redis://localhost:6379",
            name="Redis Health Check",
            monitor_type=MonitorType.DATABASE,
            check_function="tcp_port",
            threshold=0,
            comparison=">",
            interval=60
        )
        self.health_checker.add_health_check(redis_check)
        
        # Add localhost HTTP check
        http_check = MonitorCheck(
            id="http://localhost:8000/health",
            name="Application Health Check",
            monitor_type=MonitorType.APPLICATION,
            check_function="http_endpoint",
            threshold=0,
            comparison=">",
            interval=30
        )
        self.health_checker.add_health_check(http_check)
    
    async def start_monitoring(self):
        """Start the monitoring loops"""
        self.monitoring_enabled = True
        
        # Start metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self.monitoring_tasks.append(metrics_task)
        
        # Start health check task
        health_task = asyncio.create_task(self._health_check_loop())
        self.monitoring_tasks.append(health_task)
        
        # Start alert processing task
        alert_task = asyncio.create_task(self._alert_processing_loop())
        self.monitoring_tasks.append(alert_task)
        
        logger.info("Monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring loops"""
        self.monitoring_enabled = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Monitoring stopped")
    
    async def _metrics_collection_loop(self):
        """Main metrics collection loop"""
        while self.monitoring_enabled:
            try:
                # Collect system metrics
                system_metrics = self.metrics_collector.collect_system_metrics()
                
                # Collect application metrics (placeholder data)
                app_metrics = self.metrics_collector.collect_application_metrics()
                
                # Store metrics
                metrics_data = {
                    'timestamp': datetime.now().isoformat(),
                    'system': asdict(system_metrics),
                    'application': asdict(app_metrics)
                }
                
                self.metrics_history.append(metrics_data)
                
                # Store in Redis
                if self.redis_client:
                    await self.redis_client.lpush('monitoring:metrics', json.dumps(metrics_data))
                    await self.redis_client.ltrim('monitoring:metrics', 0, 999)  # Keep last 1000
                
                # Check alert rules
                all_metrics = {**asdict(system_metrics), **asdict(app_metrics)}
                await self.alert_manager.check_alert_rules(all_metrics)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error("Error in metrics collection loop", error=str(e))
                await asyncio.sleep(10)
    
    async def _health_check_loop(self):
        """Health check loop"""
        while self.monitoring_enabled:
            try:
                health_results = await self.health_checker.run_all_checks()
                
                # Store health check results
                if self.redis_client:
                    health_data = {
                        'timestamp': datetime.now().isoformat(),
                        'checks': health_results
                    }
                    await self.redis_client.set('monitoring:health', json.dumps(health_data))
                
                # Check for unhealthy services
                for check_id, result in health_results.items():
                    if result['status'] == 'unhealthy':
                        failure_count = self.health_checker.failure_counts[check_id]
                        check = self.health_checker.health_checks[check_id]
                        
                        if failure_count >= check.alert_threshold:
                            await self.alert_manager.create_alert(
                                name=f"Health Check Failed: {check.name}",
                                severity=AlertSeverity.ERROR,
                                message=f"Health check has failed {failure_count} consecutive times",
                                source="health_check",
                                metadata={'check_id': check_id, 'failure_count': failure_count}
                            )
                
                await asyncio.sleep(60)  # Health checks every minute
                
            except Exception as e:
                logger.error("Error in health check loop", error=str(e))
                await asyncio.sleep(10)
    
    async def _alert_processing_loop(self):
        """Alert processing and cleanup loop"""
        while self.monitoring_enabled:
            try:
                # Auto-resolve old alerts (example: resolve info alerts after 1 hour)
                current_time = datetime.now()
                for alert in self.alert_manager.alerts.values():
                    if (not alert.resolved and 
                        alert.severity == AlertSeverity.INFO and
                        current_time - alert.timestamp > timedelta(hours=1)):
                        await self.alert_manager.resolve_alert(alert.id)
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error("Error in alert processing loop", error=str(e))
                await asyncio.sleep(60)
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system and application metrics"""
        try:
            system_metrics = self.metrics_collector.collect_system_metrics()
            app_metrics = self.metrics_collector.collect_application_metrics()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': asdict(system_metrics),
                'application': asdict(app_metrics)
            }
        except Exception as e:
            logger.error("Failed to get current metrics", error=str(e))
            return {}
    
    async def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics history"""
        return list(self.metrics_history)[-limit:]
    
    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics"""
        return self.metrics_collector.get_prometheus_metrics()
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get monitoring service health status"""
        alert_summary = self.alert_manager.get_alert_summary()
        
        return {
            'service': self.service_name,
            'version': self.version,
            'status': 'healthy' if self.monitoring_enabled else 'stopped',
            'metrics_collected': len(self.metrics_history),
            'collection_interval': self.collection_interval,
            'alerts': alert_summary,
            'health_checks': len(self.health_checker.health_checks),
            'redis_connected': self.redis_client is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    async def create_custom_alert(self, name: str, severity: str, message: str, 
                                 metadata: Dict[str, Any] = None) -> str:
        """Create a custom alert"""
        return await self.alert_manager.create_alert(
            name=name,
            severity=AlertSeverity(severity),
            message=message,
            source="custom",
            metadata=metadata
        )
    
    def add_custom_health_check(self, check: MonitorCheck):
        """Add a custom health check"""
        self.health_checker.add_health_check(check)
    
    def add_custom_alert_rule(self, rule: Dict[str, Any]):
        """Add a custom alert rule"""
        self.alert_manager.add_alert_rule(rule)

# Service instance
monitoring_service = MonitoringService()

# Example usage
async def main():
    """Example usage of the monitoring service"""
    try:
        # Initialize service
        await monitoring_service.initialize()
        
        # Start monitoring
        await monitoring_service.start_monitoring()
        
        # Let it run for a while
        await asyncio.sleep(60)
        
        # Get current metrics
        metrics = await monitoring_service.get_current_metrics()
        print(f"Current metrics: {json.dumps(metrics, indent=2)}")
        
        # Get service health
        health = await monitoring_service.get_service_health()
        print(f"Service health: {json.dumps(health, indent=2)}")
        
        # Get Prometheus metrics
        prometheus_metrics = await monitoring_service.get_prometheus_metrics()
        print(f"Prometheus metrics:\n{prometheus_metrics}")
        
        # Create custom alert
        alert_id = await monitoring_service.create_custom_alert(
            name="Test Alert",
            severity="warning",
            message="This is a test alert",
            metadata={"test": True}
        )
        print(f"Created custom alert: {alert_id}")
        
    except Exception as e:
        logger.error("Error in main", error=str(e))
    finally:
        await monitoring_service.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())