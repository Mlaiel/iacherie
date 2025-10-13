#!/usr/bin/env python3
"""
📊 UNIFIED MONITORING SERVICE - Enterprise Infrastructure Monitoring
===================================================================

Comprehensive unified monitoring service consolidating:
- System monitoring and alerting
- Resource monitoring (CPU, memory, disk, network)
- Metrics aggregation and analytics
- Real-time health checks and performance tracking

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
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
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


class MonitoringLevel(Enum):
    """Monitoring level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ResourceType(Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    CONTAINER = "container"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    CUSTOM = "custom"


class AlertLevel(Enum):
    """Alert level enumeration."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Metric type enumeration."""
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enabled: bool = True
    interval: int = 30
    retention_period: int = 86400
    alert_enabled: bool = True
    metrics_enabled: bool = True
    health_check_enabled: bool = True
    resource_monitoring_enabled: bool = True
    
    # Thresholds
    cpu_warning_threshold: float = 70.0
    cpu_critical_threshold: float = 90.0
    memory_warning_threshold: float = 80.0
    memory_critical_threshold: float = 95.0
    disk_warning_threshold: float = 85.0
    disk_critical_threshold: float = 95.0
    
    # Network thresholds
    network_warning_threshold: float = 1000.0  # MB/s
    network_critical_threshold: float = 2000.0  # MB/s
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Prometheus configuration
    prometheus_port: int = 8000
    prometheus_enabled: bool = True


@dataclass
class ResourceMetric:
    """Resource metric data structure."""
    resource_type: ResourceType
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    alert_level: Optional[AlertLevel] = None


@dataclass
class SystemAlert:
    """System alert data structure."""
    id: str
    level: AlertLevel
    message: str
    component: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    service_name: str
    status: str
    response_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class MetricPoint:
    """Individual metric point."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


class UnifiedMonitoringService:
    """
    Unified monitoring service consolidating system monitoring, resource monitoring, 
    and metrics aggregation into a single comprehensive service.
    """
    
    def __init__(self, config: MonitoringConfig = None):
        """Initialize unified monitoring service."""
        self.config = config or MonitoringConfig()
        self.logger = logger.bind(service="unified_monitoring")
        
        # State management
        self.is_running = False
        self.metrics_cache = defaultdict(deque)
        self.alerts_cache = deque(maxlen=1000)
        self.health_status = {}
        
        # Monitoring data
        self.system_metrics = {}
        self.resource_metrics = {}
        self.custom_metrics = {}
        
        # Redis client
        self.redis_client = None
        
        # Prometheus metrics
        self.prometheus_registry = CollectorRegistry()
        self.prometheus_metrics = {}
        
        # Monitoring tasks
        self.monitoring_tasks = []
        
        # Alert handlers
        self.alert_handlers = []
        
        # Thresholds and rules
        self.monitoring_rules = {}
        
        self.logger.info("Unified monitoring service initialized", config=asdict(self.config))
    
    async def start(self):
        """Start the unified monitoring service."""
        if self.is_running:
            self.logger.warning("Monitoring service is already running")
            return
        
        try:
            # Initialize Redis connection
            if self.config.redis_host:
                await self._initialize_redis()
            
            # Initialize Prometheus metrics
            if self.config.prometheus_enabled:
                self._initialize_prometheus_metrics()
            
            # Initialize monitoring rules
            self._initialize_monitoring_rules()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            self.is_running = True
            self.logger.info("Unified monitoring service started successfully")
            
        except Exception as e:
            self.logger.error("Failed to start monitoring service", error=str(e))
            raise
    
    async def stop(self):
        """Stop the unified monitoring service."""
        if not self.is_running:
            self.logger.warning("Monitoring service is not running")
            return
        
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            self.is_running = False
            self.logger.info("Unified monitoring service stopped successfully")
            
        except Exception as e:
            self.logger.error("Error stopping monitoring service", error=str(e))
    
    async def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            self.logger.info("Redis connection established")
            
        except Exception as e:
            self.logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        try:
            # System metrics
            self.prometheus_metrics['cpu_usage'] = Gauge(
                'system_cpu_usage_percent', 
                'CPU usage percentage',
                registry=self.prometheus_registry
            )
            
            self.prometheus_metrics['memory_usage'] = Gauge(
                'system_memory_usage_percent',
                'Memory usage percentage',
                registry=self.prometheus_registry
            )
            
            self.prometheus_metrics['disk_usage'] = Gauge(
                'system_disk_usage_percent',
                'Disk usage percentage',
                ['mount_point'],
                registry=self.prometheus_registry
            )
            
            self.prometheus_metrics['network_bytes_sent'] = Counter(
                'system_network_bytes_sent_total',
                'Network bytes sent',
                ['interface'],
                registry=self.prometheus_registry
            )
            
            self.prometheus_metrics['network_bytes_recv'] = Counter(
                'system_network_bytes_recv_total',
                'Network bytes received',
                ['interface'],
                registry=self.prometheus_registry
            )
            
            # Service health metrics
            self.prometheus_metrics['service_health'] = Gauge(
                'service_health_status',
                'Service health status (1=healthy, 0=unhealthy)',
                ['service_name'],
                registry=self.prometheus_registry
            )
            
            # Response time metrics
            self.prometheus_metrics['response_time'] = Histogram(
                'service_response_time_seconds',
                'Service response time in seconds',
                ['service_name'],
                registry=self.prometheus_registry
            )
            
            # Alert metrics
            self.prometheus_metrics['alerts_total'] = Counter(
                'monitoring_alerts_total',
                'Total number of alerts',
                ['level', 'component'],
                registry=self.prometheus_registry
            )
            
            self.logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize Prometheus metrics", error=str(e))
            raise
    
    def _initialize_monitoring_rules(self):
        """Initialize monitoring rules and thresholds."""
        self.monitoring_rules = {
            'cpu_usage': {
                'warning': self.config.cpu_warning_threshold,
                'critical': self.config.cpu_critical_threshold
            },
            'memory_usage': {
                'warning': self.config.memory_warning_threshold,
                'critical': self.config.memory_critical_threshold
            },
            'disk_usage': {
                'warning': self.config.disk_warning_threshold,
                'critical': self.config.disk_critical_threshold
            },
            'network_usage': {
                'warning': self.config.network_warning_threshold,
                'critical': self.config.network_critical_threshold
            }
        }
        
        self.logger.info("Monitoring rules initialized", rules=self.monitoring_rules)
    
    async def _start_monitoring_tasks(self):
        """Start all monitoring tasks."""
        try:
            # System monitoring task
            self.monitoring_tasks.append(
                asyncio.create_task(self._system_monitoring_loop())
            )
            
            # Resource monitoring task
            self.monitoring_tasks.append(
                asyncio.create_task(self._resource_monitoring_loop())
            )
            
            # Health check task
            if self.config.health_check_enabled:
                self.monitoring_tasks.append(
                    asyncio.create_task(self._health_check_loop())
                )
            
            # Metrics aggregation task
            if self.config.metrics_enabled:
                self.monitoring_tasks.append(
                    asyncio.create_task(self._metrics_aggregation_loop())
                )
            
            # Alert processing task
            if self.config.alert_enabled:
                self.monitoring_tasks.append(
                    asyncio.create_task(self._alert_processing_loop())
                )
            
            self.logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")
            
        except Exception as e:
            self.logger.error("Failed to start monitoring tasks", error=str(e))
            raise
    
    async def _system_monitoring_loop(self):
        """Main system monitoring loop."""
        while self.is_running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.config.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in system monitoring loop", error=str(e))
                await asyncio.sleep(5)
    
    async def _resource_monitoring_loop(self):
        """Resource monitoring loop."""
        while self.is_running:
            try:
                await self._collect_resource_metrics()
                await asyncio.sleep(self.config.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in resource monitoring loop", error=str(e))
                await asyncio.sleep(5)
    
    async def _health_check_loop(self):
        """Health check monitoring loop."""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in health check loop", error=str(e))
                await asyncio.sleep(5)
    
    async def _metrics_aggregation_loop(self):
        """Metrics aggregation loop."""
        while self.is_running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(60)  # Aggregate every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in metrics aggregation loop", error=str(e))
                await asyncio.sleep(5)
    
    async def _alert_processing_loop(self):
        """Alert processing loop."""
        while self.is_running:
            try:
                await self._process_alerts()
                await asyncio.sleep(10)  # Process alerts every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in alert processing loop", error=str(e))
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_metrics = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_metrics[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except PermissionError:
                    continue
            
            # Network metrics
            network = psutil.net_io_counters()
            network_per_interface = psutil.net_io_counters(pernic=True)
            
            # Update system metrics
            self.system_metrics.update({
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': disk_metrics,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                    'per_interface': network_per_interface
                },
                'timestamp': timestamp
            })
            
            # Update Prometheus metrics
            if self.config.prometheus_enabled:
                self._update_prometheus_metrics()
            
            # Check for alerts
            await self._check_system_alerts()
            
            # Store metrics in cache
            self._store_metrics_in_cache('system', self.system_metrics)
            
            self.logger.debug("System metrics collected", 
                            cpu_percent=cpu_percent,
                            memory_percent=memory.percent)
            
        except Exception as e:
            self.logger.error("Error collecting system metrics", error=str(e))
    
    async def _collect_resource_metrics(self):
        """Collect resource-specific metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # Process metrics
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 1.0 or proc_info['memory_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = timestamp - boot_time
            
            # Temperature sensors (if available)
            temperature_metrics = {}
            try:
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    temperature_metrics[name] = [
                        {'label': entry.label or 'temp', 'current': entry.current}
                        for entry in entries
                    ]
            except AttributeError:
                pass
            
            # Update resource metrics
            self.resource_metrics.update({
                'processes': processes,
                'uptime': uptime.total_seconds(),
                'boot_time': boot_time,
                'temperature': temperature_metrics,
                'timestamp': timestamp
            })
            
            # Store metrics in cache
            self._store_metrics_in_cache('resource', self.resource_metrics)
            
            self.logger.debug("Resource metrics collected",
                            process_count=len(processes),
                            uptime_hours=uptime.total_seconds() / 3600)
            
        except Exception as e:
            self.logger.error("Error collecting resource metrics", error=str(e))
    
    async def _perform_health_checks(self):
        """Perform health checks on services."""
        try:
            # Define health check endpoints
            health_endpoints = [
                {'name': 'api_gateway', 'url': 'http://localhost:8000/health'},
                {'name': 'database', 'url': 'http://localhost:5432/health'},
                {'name': 'redis', 'url': 'http://localhost:6379/health'},
                {'name': 'elasticsearch', 'url': 'http://localhost:9200/_cluster/health'},
            ]
            
            health_results = {}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                for endpoint in health_endpoints:
                    try:
                        start_time = time.time()
                        async with session.get(endpoint['url']) as response:
                            response_time = time.time() - start_time
                            
                            health_result = HealthCheckResult(
                                service_name=endpoint['name'],
                                status='healthy' if response.status == 200 else 'unhealthy',
                                response_time=response_time,
                                details={'status_code': response.status}
                            )
                            
                            health_results[endpoint['name']] = health_result
                            
                            # Update Prometheus metrics
                            if self.config.prometheus_enabled:
                                self.prometheus_metrics['service_health'].labels(
                                    service_name=endpoint['name']
                                ).set(1 if response.status == 200 else 0)
                                
                                self.prometheus_metrics['response_time'].labels(
                                    service_name=endpoint['name']
                                ).observe(response_time)
                    
                    except Exception as e:
                        health_result = HealthCheckResult(
                            service_name=endpoint['name'],
                            status='unhealthy',
                            response_time=0,
                            error=str(e)
                        )
                        
                        health_results[endpoint['name']] = health_result
                        
                        # Update Prometheus metrics
                        if self.config.prometheus_enabled:
                            self.prometheus_metrics['service_health'].labels(
                                service_name=endpoint['name']
                            ).set(0)
            
            self.health_status = health_results
            
            # Store health status in cache
            self._store_metrics_in_cache('health', health_results)
            
            self.logger.debug("Health checks completed",
                            healthy_services=sum(1 for r in health_results.values() if r.status == 'healthy'),
                            total_services=len(health_results))
            
        except Exception as e:
            self.logger.error("Error performing health checks", error=str(e))
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for reporting and analytics."""
        try:
            # Calculate aggregated metrics for the last hour
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            aggregated_metrics = {
                'system': self._aggregate_system_metrics(start_time, end_time),
                'resource': self._aggregate_resource_metrics(start_time, end_time),
                'health': self._aggregate_health_metrics(start_time, end_time),
                'alerts': self._aggregate_alert_metrics(start_time, end_time),
                'timestamp': end_time
            }
            
            # Store aggregated metrics
            if self.redis_client:
                await self.redis_client.setex(
                    f"monitoring:aggregated:{int(end_time.timestamp())}",
                    3600,  # 1 hour TTL
                    json.dumps(aggregated_metrics, default=str)
                )
            
            self.logger.debug("Metrics aggregated", 
                            period_hours=1,
                            end_time=end_time)
            
        except Exception as e:
            self.logger.error("Error aggregating metrics", error=str(e))
    
    def _aggregate_system_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Aggregate system metrics for the given time period."""
        # Get cached metrics for the period
        cached_metrics = self._get_cached_metrics('system', start_time, end_time)
        
        if not cached_metrics:
            return {}
        
        # Calculate aggregations
        cpu_values = [m.get('cpu', {}).get('percent', 0) for m in cached_metrics]
        memory_values = [m.get('memory', {}).get('percent', 0) for m in cached_metrics]
        
        return {
            'cpu': {
                'avg': statistics.mean(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0,
                'std': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            },
            'memory': {
                'avg': statistics.mean(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'min': min(memory_values) if memory_values else 0,
                'std': statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            'sample_count': len(cached_metrics)
        }
    
    def _aggregate_resource_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Aggregate resource metrics for the given time period."""
        cached_metrics = self._get_cached_metrics('resource', start_time, end_time)
        
        if not cached_metrics:
            return {}
        
        return {
            'avg_process_count': statistics.mean([
                len(m.get('processes', [])) for m in cached_metrics
            ]) if cached_metrics else 0,
            'sample_count': len(cached_metrics)
        }
    
    def _aggregate_health_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Aggregate health metrics for the given time period."""
        cached_metrics = self._get_cached_metrics('health', start_time, end_time)
        
        if not cached_metrics:
            return {}
        
        # Calculate uptime percentages
        service_uptimes = defaultdict(list)
        
        for metrics in cached_metrics:
            for service_name, health_result in metrics.items():
                if hasattr(health_result, 'status'):
                    service_uptimes[service_name].append(
                        1 if health_result.status == 'healthy' else 0
                    )
        
        uptime_stats = {}
        for service_name, statuses in service_uptimes.items():
            uptime_stats[service_name] = {
                'uptime_percentage': (sum(statuses) / len(statuses)) * 100 if statuses else 0,
                'total_checks': len(statuses)
            }
        
        return {
            'service_uptimes': uptime_stats,
            'sample_count': len(cached_metrics)
        }
    
    def _aggregate_alert_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Aggregate alert metrics for the given time period."""
        period_alerts = [
            alert for alert in self.alerts_cache 
            if start_time <= alert.timestamp <= end_time
        ]
        
        alert_counts = defaultdict(int)
        for alert in period_alerts:
            alert_counts[alert.level.value] += 1
        
        return {
            'total_alerts': len(period_alerts),
            'by_level': dict(alert_counts)
        }
    
    async def _process_alerts(self):
        """Process pending alerts."""
        try:
            # Process recent alerts that haven't been handled
            recent_alerts = [
                alert for alert in self.alerts_cache 
                if not alert.resolved and 
                (datetime.utcnow() - alert.timestamp).total_seconds() < 300  # Last 5 minutes
            ]
            
            for alert in recent_alerts:
                await self._handle_alert(alert)
            
            self.logger.debug("Alerts processed", alert_count=len(recent_alerts))
            
        except Exception as e:
            self.logger.error("Error processing alerts", error=str(e))
    
    async def _handle_alert(self, alert: SystemAlert):
        """Handle a specific alert."""
        try:
            # Log the alert
            self.logger.warning("Alert triggered",
                              alert_id=alert.id,
                              level=alert.level.value,
                              component=alert.component,
                              message=alert.message)
            
            # Update Prometheus metrics
            if self.config.prometheus_enabled:
                self.prometheus_metrics['alerts_total'].labels(
                    level=alert.level.value,
                    component=alert.component
                ).inc()
            
            # Send notifications (implement based on requirements)
            await self._send_alert_notification(alert)
            
            # Store alert in Redis
            if self.redis_client:
                await self.redis_client.lpush(
                    "monitoring:alerts",
                    json.dumps(asdict(alert), default=str)
                )
                
                # Keep only last 1000 alerts
                await self.redis_client.ltrim("monitoring:alerts", 0, 999)
            
        except Exception as e:
            self.logger.error("Error handling alert", 
                            alert_id=alert.id, 
                            error=str(e))
    
    async def _send_alert_notification(self, alert: SystemAlert):
        """Send alert notification (placeholder for implementation)."""
        # Implement notification logic (email, Slack, etc.)
        pass
    
    async def _check_system_alerts(self):
        """Check system metrics against alert thresholds."""
        try:
            alerts = []
            
            # Check CPU usage
            cpu_percent = self.system_metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent >= self.config.cpu_critical_threshold:
                alerts.append(SystemAlert(
                    id=f"cpu_critical_{int(time.time())}",
                    level=AlertLevel.CRITICAL,
                    message=f"CPU usage critical: {cpu_percent:.1f}%",
                    component="system",
                    metadata={'cpu_percent': cpu_percent}
                ))
            elif cpu_percent >= self.config.cpu_warning_threshold:
                alerts.append(SystemAlert(
                    id=f"cpu_warning_{int(time.time())}",
                    level=AlertLevel.WARNING,
                    message=f"CPU usage high: {cpu_percent:.1f}%",
                    component="system",
                    metadata={'cpu_percent': cpu_percent}
                ))
            
            # Check memory usage
            memory_percent = self.system_metrics.get('memory', {}).get('percent', 0)
            if memory_percent >= self.config.memory_critical_threshold:
                alerts.append(SystemAlert(
                    id=f"memory_critical_{int(time.time())}",
                    level=AlertLevel.CRITICAL,
                    message=f"Memory usage critical: {memory_percent:.1f}%",
                    component="system",
                    metadata={'memory_percent': memory_percent}
                ))
            elif memory_percent >= self.config.memory_warning_threshold:
                alerts.append(SystemAlert(
                    id=f"memory_warning_{int(time.time())}",
                    level=AlertLevel.WARNING,
                    message=f"Memory usage high: {memory_percent:.1f}%",
                    component="system",
                    metadata={'memory_percent': memory_percent}
                ))
            
            # Check disk usage
            for mount_point, disk_info in self.system_metrics.get('disk', {}).items():
                disk_percent = disk_info.get('percent', 0)
                if disk_percent >= self.config.disk_critical_threshold:
                    alerts.append(SystemAlert(
                        id=f"disk_critical_{mount_point}_{int(time.time())}",
                        level=AlertLevel.CRITICAL,
                        message=f"Disk usage critical on {mount_point}: {disk_percent:.1f}%",
                        component="storage",
                        metadata={'mount_point': mount_point, 'disk_percent': disk_percent}
                    ))
                elif disk_percent >= self.config.disk_warning_threshold:
                    alerts.append(SystemAlert(
                        id=f"disk_warning_{mount_point}_{int(time.time())}",
                        level=AlertLevel.WARNING,
                        message=f"Disk usage high on {mount_point}: {disk_percent:.1f}%",
                        component="storage",
                        metadata={'mount_point': mount_point, 'disk_percent': disk_percent}
                    ))
            
            # Add alerts to cache
            for alert in alerts:
                self.alerts_cache.append(alert)
            
            if alerts:
                self.logger.info(f"Generated {len(alerts)} system alerts")
            
        except Exception as e:
            self.logger.error("Error checking system alerts", error=str(e))
    
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics with current values."""
        try:
            # Update CPU metrics
            cpu_percent = self.system_metrics.get('cpu', {}).get('percent', 0)
            self.prometheus_metrics['cpu_usage'].set(cpu_percent)
            
            # Update memory metrics
            memory_percent = self.system_metrics.get('memory', {}).get('percent', 0)
            self.prometheus_metrics['memory_usage'].set(memory_percent)
            
            # Update disk metrics
            for mount_point, disk_info in self.system_metrics.get('disk', {}).items():
                self.prometheus_metrics['disk_usage'].labels(
                    mount_point=mount_point
                ).set(disk_info.get('percent', 0))
            
            # Update network metrics
            network_info = self.system_metrics.get('network', {})
            for interface, stats in network_info.get('per_interface', {}).items():
                self.prometheus_metrics['network_bytes_sent'].labels(
                    interface=interface
                ).inc(stats.bytes_sent)
                
                self.prometheus_metrics['network_bytes_recv'].labels(
                    interface=interface
                ).inc(stats.bytes_recv)
            
        except Exception as e:
            self.logger.error("Error updating Prometheus metrics", error=str(e))
    
    def _store_metrics_in_cache(self, metric_type: str, metrics: Dict[str, Any]):
        """Store metrics in memory cache."""
        try:
            # Add timestamp if not present
            if 'timestamp' not in metrics:
                metrics['timestamp'] = datetime.utcnow()
            
            # Store in cache with size limit
            cache_key = metric_type
            self.metrics_cache[cache_key].append(metrics)
            
            # Keep only last 1000 entries
            if len(self.metrics_cache[cache_key]) > 1000:
                self.metrics_cache[cache_key].popleft()
            
            # Store in Redis if available
            if self.redis_client:
                asyncio.create_task(self._store_metrics_in_redis(metric_type, metrics))
            
        except Exception as e:
            self.logger.error("Error storing metrics in cache", 
                            metric_type=metric_type, 
                            error=str(e))
    
    async def _store_metrics_in_redis(self, metric_type: str, metrics: Dict[str, Any]):
        """Store metrics in Redis."""
        try:
            key = f"monitoring:{metric_type}:{int(time.time())}"
            await self.redis_client.setex(
                key,
                self.config.retention_period,
                json.dumps(metrics, default=str)
            )
        except Exception as e:
            self.logger.error("Error storing metrics in Redis", 
                            metric_type=metric_type, 
                            error=str(e))
    
    def _get_cached_metrics(self, metric_type: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get cached metrics for a time period."""
        cached_metrics = self.metrics_cache.get(metric_type, [])
        return [
            metrics for metrics in cached_metrics
            if start_time <= metrics.get('timestamp', datetime.min) <= end_time
        ]
    
    # Public API methods
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'system_metrics': self.system_metrics,
            'resource_metrics': self.resource_metrics,
            'health_status': {
                name: asdict(status) if hasattr(status, '__dict__') else status
                for name, status in self.health_status.items()
            },
            'alerts_count': len(self.alerts_cache),
            'is_running': self.is_running,
            'uptime': (datetime.utcnow() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
        }
    
    async def get_metrics_history(self, metric_type: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for the specified period."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        return self._get_cached_metrics(metric_type, start_time, end_time)
    
    async def get_alerts(self, level: AlertLevel = None, resolved: bool = None) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering."""
        alerts = list(self.alerts_cache)
        
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]
        
        return [asdict(alert) for alert in alerts]
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert by ID."""
        for alert in self.alerts_cache:
            if alert.id == alert_id:
                alert.resolved = True
                self.logger.info("Alert resolved", alert_id=alert_id)
                return True
        
        return False
    
    async def add_custom_metric(self, metric: MetricPoint):
        """Add a custom metric."""
        metric_key = f"custom_{metric.name}"
        
        if metric_key not in self.custom_metrics:
            self.custom_metrics[metric_key] = deque(maxlen=1000)
        
        self.custom_metrics[metric_key].append(asdict(metric))
        
        self.logger.debug("Custom metric added", metric_name=metric.name, value=metric.value)
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.config.prometheus_enabled:
            return ""
        
        return generate_latest(self.prometheus_registry).decode('utf-8')
    
    async def register_alert_handler(self, handler: Callable[[SystemAlert], None]):
        """Register an alert handler function."""
        self.alert_handlers.append(handler)
        self.logger.info("Alert handler registered")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the monitoring service itself."""
        return {
            'status': 'healthy' if self.is_running else 'unhealthy',
            'uptime': time.time() - (time.time() if self.is_running else 0),
            'active_tasks': len([task for task in self.monitoring_tasks if not task.done()]),
            'redis_connected': self.redis_client is not None,
            'prometheus_enabled': self.config.prometheus_enabled,
            'metrics_cache_size': sum(len(cache) for cache in self.metrics_cache.values()),
            'alerts_cache_size': len(self.alerts_cache)
        }


# Service factory and configuration
async def create_unified_monitoring_service(config: Dict[str, Any] = None) -> UnifiedMonitoringService:
    """Create and configure a unified monitoring service."""
    monitoring_config = MonitoringConfig(**(config or {}))
    service = UnifiedMonitoringService(monitoring_config)
    return service


# Main execution
if __name__ == "__main__":
    async def main():
        """Main execution function."""
        # Create monitoring service
        service = await create_unified_monitoring_service()
        
        try:
            # Start the service
            await service.start()
            
            # Run indefinitely
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down monitoring service")
        finally:
            await service.stop()
    
    # Run the service
    asyncio.run(main())