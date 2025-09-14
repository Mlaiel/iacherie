"""
Application Monitoring Service - Enterprise DevOps Monitoring
============================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: DevOps Engineer & Backend Senior
**Module**: Security & Monitoring Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Comprehensive application monitoring with real-time metrics collection,
performance analysis, alerting, and observability for enterprise applications.
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import statistics


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(Enum):
    """Application health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Metric data structure"""
    name: str
    metric_type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = ""


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    metric_name: str
    threshold: float
    current_value: float
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    is_resolved: bool = False


@dataclass
class HealthCheck:
    """Health check configuration"""
    name: str
    endpoint: str
    timeout: int = 5
    interval: int = 30
    expected_status: int = 200
    enabled: bool = True


class ApplicationMonitoringService:
    """
    Enterprise Application Monitoring Service
    
    Comprehensive monitoring with:
    - Real-time metrics collection and aggregation
    - Performance monitoring and analysis
    - Health checks and service discovery
    - Alerting and notification system
    - Resource usage monitoring
    - Business metrics tracking
    - Custom metrics and dashboards
    """

    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Prometheus metrics registry
        self.registry = CollectorRegistry()
        
        # Core metrics
        self.request_counter = Counter(
            'app_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'app_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'app_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'app_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'app_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        # Monitoring state
        self.metrics_buffer: List[Metric] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Configuration
        self.alert_thresholds = {
            "response_time_p95": 1.0,  # seconds
            "error_rate": 0.05,        # 5%
            "memory_usage": 0.85,      # 85%
            "cpu_usage": 0.80,         # 80%
            "disk_usage": 0.90         # 90%
        }
        
        # Metrics storage
        self.metrics_history: Dict[str, List[float]] = {}
        self.performance_baselines: Dict[str, float] = {}
        
        # Business metrics
        self.business_metrics = {
            "total_users": 0,
            "active_sessions": 0,
            "revenue_per_hour": 0.0,
            "conversion_rate": 0.0
        }
        
        self.logger.info("Application Monitoring Service initialized")

    async def initialize(self) -> None:
        """Initialize monitoring service with Redis connection"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Load existing configuration
            await self._load_monitoring_config()
            
            # Initialize default health checks
            self._initialize_default_health_checks()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            self.logger.info("Application Monitoring Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Application Monitoring: {e}")
            raise

    def _initialize_default_health_checks(self) -> None:
        """Initialize default health checks for common services"""
        
        default_checks = [
            HealthCheck(
                name="database_health",
                endpoint="/health/database",
                timeout=5,
                interval=30
            ),
            HealthCheck(
                name="redis_health",
                endpoint="/health/redis",
                timeout=3,
                interval=30
            ),
            HealthCheck(
                name="api_health",
                endpoint="/health/api",
                timeout=5,
                interval=60
            ),
            HealthCheck(
                name="external_services",
                endpoint="/health/external",
                timeout=10,
                interval=120
            )
        ]
        
        for check in default_checks:
            self.health_checks[check.name] = check

    async def _start_monitoring_tasks(self) -> None:
        """Start background monitoring tasks"""
        
        # System metrics collection
        self.monitoring_tasks.append(
            asyncio.create_task(self._collect_system_metrics())
        )
        
        # Health checks
        self.monitoring_tasks.append(
            asyncio.create_task(self._run_health_checks())
        )
        
        # Alert processing
        self.monitoring_tasks.append(
            asyncio.create_task(self._process_alerts())
        )
        
        # Metrics aggregation
        self.monitoring_tasks.append(
            asyncio.create_task(self._aggregate_metrics())
        )
        
        # Performance analysis
        self.monitoring_tasks.append(
            asyncio.create_task(self._analyze_performance())
        )
        
        self.logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")

    async def record_metric(self, metric -> None: Metric) -> None:
        """Record a custom metric"""
        
        try:
            # Update Prometheus metrics
            if metric.metric_type == MetricType.COUNTER:
                self.request_counter.labels(**metric.labels).inc(metric.value)
            elif metric.metric_type == MetricType.GAUGE:
                if metric.name == "memory_usage":
                    self.memory_usage.set(metric.value)
                elif metric.name == "cpu_usage":
                    self.cpu_usage.set(metric.value)
                elif metric.name == "active_connections":
                    self.active_connections.set(metric.value)
            elif metric.metric_type == MetricType.HISTOGRAM:
                if "duration" in metric.name:
                    self.request_duration.labels(**metric.labels).observe(metric.value)
            
            # Store metric in buffer
            self.metrics_buffer.append(metric)
            
            # Store in Redis for persistence
            await self._store_metric(metric)
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            self.logger.debug(f"Recorded metric: {metric.name} = {metric.value}")
            
        except Exception as e:
            self.logger.error(f"Error recording metric {metric.name}: {e}")

    async def record_request(self, method -> None: str, endpoint -> None: str, 
                           status_code -> None: int, duration -> None: float) -> None:
        """Record HTTP request metrics"""
        
        # Record request count
        await self.record_metric(Metric(
            name="http_requests_total",
            metric_type=MetricType.COUNTER,
            value=1,
            labels={
                "method": method,
                "endpoint": endpoint,
                "status": str(status_code)
            }
        ))
        
        # Record request duration
        await self.record_metric(Metric(
            name="http_request_duration",
            metric_type=MetricType.HISTOGRAM,
            value=duration,
            labels={
                "method": method,
                "endpoint": endpoint
            }
        ))

    async def record_business_metric(self, metric_name -> None: str, value -> None: float, 
                                   labels -> None: Optional[Dict[str, str]] = None) -> None:
        """Record business-specific metrics"""
        
        if labels is None:
            labels = {}
        
        metric = Metric(
            name=f"business_{metric_name}",
            metric_type=MetricType.GAUGE,
            value=value,
            labels=labels,
            description=f"Business metric: {metric_name}"
        )
        
        await self.record_metric(metric)
        
        # Update business metrics cache
        self.business_metrics[metric_name] = value

    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics continuously"""
        
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                await self.record_metric(Metric(
                    name="cpu_usage",
                    metric_type=MetricType.GAUGE,
                    value=cpu_percent / 100.0
                ))
                
                # Memory usage
                memory = psutil.virtual_memory()
                await self.record_metric(Metric(
                    name="memory_usage",
                    metric_type=MetricType.GAUGE,
                    value=memory.used
                ))
                
                await self.record_metric(Metric(
                    name="memory_usage_percent",
                    metric_type=MetricType.GAUGE,
                    value=memory.percent / 100.0
                ))
                
                # Disk usage
                disk = psutil.disk_usage('/')
                await self.record_metric(Metric(
                    name="disk_usage_percent",
                    metric_type=MetricType.GAUGE,
                    value=(disk.used / disk.total)
                ))
                
                # Network I/O
                network = psutil.net_io_counters()
                await self.record_metric(Metric(
                    name="network_bytes_sent",
                    metric_type=MetricType.COUNTER,
                    value=network.bytes_sent
                ))
                
                await self.record_metric(Metric(
                    name="network_bytes_received",
                    metric_type=MetricType.COUNTER,
                    value=network.bytes_recv
                ))
                
                # Process count
                process_count = len(psutil.pids())
                await self.record_metric(Metric(
                    name="process_count",
                    metric_type=MetricType.GAUGE,
                    value=process_count
                ))
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)

    async def _run_health_checks(self) -> None:
        """Run health checks continuously"""
        
        while True:
            try:
                for check_name, health_check in self.health_checks.items():
                    if not health_check.enabled:
                        continue
                    
                    # Perform health check
                    result = await self._perform_health_check(health_check)
                    
                    # Record health check result
                    await self.record_metric(Metric(
                        name="health_check_status",
                        metric_type=MetricType.GAUGE,
                        value=1.0 if result["is_healthy"] else 0.0,
                        labels={
                            "check_name": check_name,
                            "endpoint": health_check.endpoint
                        }
                    ))
                    
                    # Record response time
                    await self.record_metric(Metric(
                        name="health_check_duration",
                        metric_type=MetricType.HISTOGRAM,
                        value=result["response_time"],
                        labels={
                            "check_name": check_name,
                            "endpoint": health_check.endpoint
                        }
                    ))
                    
                    # Store health check result
                    await self._store_health_check_result(check_name, result)
                
                await asyncio.sleep(30)  # Run checks every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error running health checks: {e}")
                await asyncio.sleep(60)

    async def _perform_health_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Perform individual health check"""
        
        start_time = time.time()
        result = {
            "is_healthy": False,
            "response_time": 0.0,
            "status_code": 0,
            "error": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=health_check.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://localhost:8000{health_check.endpoint}") as response:
                    result["status_code"] = response.status
                    result["response_time"] = time.time() - start_time
                    result["is_healthy"] = response.status == health_check.expected_status
                    
        except asyncio.TimeoutError:
            result["response_time"] = time.time() - start_time
            result["error"] = "Timeout"
        except Exception as e:
            result["response_time"] = time.time() - start_time
            result["error"] = str(e)
        
        return result

    async def _process_alerts(self) -> None:
        """Process and manage alerts"""
        
        while True:
            try:
                # Check for resolved alerts
                for alert_id, alert in list(self.active_alerts.items()):
                    if await self._is_alert_resolved(alert):
                        alert.is_resolved = True
                        alert.resolved_at = datetime.utcnow()
                        
                        # Send resolution notification
                        await self._send_alert_notification(alert, "resolved")
                        
                        # Move to resolved alerts
                        await self._archive_resolved_alert(alert)
                        del self.active_alerts[alert_id]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(120)

    async def _aggregate_metrics(self) -> None:
        """Aggregate metrics for analysis and storage"""
        
        while True:
            try:
                if len(self.metrics_buffer) > 100:
                    # Process metrics buffer
                    metrics_to_process = self.metrics_buffer[:100]
                    self.metrics_buffer = self.metrics_buffer[100:]
                    
                    # Group metrics by name
                    grouped_metrics = {}
                    for metric in metrics_to_process:
                        if metric.name not in grouped_metrics:
                            grouped_metrics[metric.name] = []
                        grouped_metrics[metric.name].append(metric.value)
                    
                    # Calculate aggregations
                    for metric_name, values in grouped_metrics.items():
                        if values:
                            aggregations = {
                                "count": len(values),
                                "sum": sum(values),
                                "avg": statistics.mean(values),
                                "min": min(values),
                                "max": max(values),
                                "p50": statistics.median(values),
                                "p95": self._calculate_percentile(values, 95),
                                "p99": self._calculate_percentile(values, 99)
                            }
                            
                            # Store aggregations
                            await self._store_metric_aggregations(metric_name, aggregations)
                
                await asyncio.sleep(30)  # Aggregate every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error aggregating metrics: {e}")
                await asyncio.sleep(60)

    async def _analyze_performance(self) -> None:
        """Analyze performance trends and anomalies"""
        
        while True:
            try:
                # Analyze response times
                await self._analyze_response_times()
                
                # Analyze error rates
                await self._analyze_error_rates()
                
                # Analyze resource usage trends
                await self._analyze_resource_usage()
                
                # Update performance baselines
                await self._update_performance_baselines()
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error analyzing performance: {e}")
                await asyncio.sleep(600)

    async def _check_metric_alerts(self, metric -> None: Metric) -> None:
        """Check if metric triggers any alerts"""
        
        try:
            alert_rules = {
                "cpu_usage": {
                    "threshold": self.alert_thresholds["cpu_usage"],
                    "operator": "gt",
                    "severity": AlertSeverity.WARNING
                },
                "memory_usage_percent": {
                    "threshold": self.alert_thresholds["memory_usage"],
                    "operator": "gt",
                    "severity": AlertSeverity.WARNING
                },
                "disk_usage_percent": {
                    "threshold": self.alert_thresholds["disk_usage"],
                    "operator": "gt",
                    "severity": AlertSeverity.CRITICAL
                },
                "health_check_status": {
                    "threshold": 1.0,
                    "operator": "lt",
                    "severity": AlertSeverity.ERROR
                }
            }
            
            if metric.name in alert_rules:
                rule = alert_rules[metric.name]
                
                should_alert = False
                if rule["operator"] == "gt" and metric.value > rule["threshold"]:
                    should_alert = True
                elif rule["operator"] == "lt" and metric.value < rule["threshold"]:
                    should_alert = True
                
                if should_alert:
                    alert_id = f"alert_{metric.name}_{int(time.time())}"
                    
                    alert = Alert(
                        alert_id=alert_id,
                        name=f"{metric.name.replace('_', ' ').title()} Alert",
                        severity=rule["severity"],
                        message=f"{metric.name} is {metric.value}, threshold: {rule['threshold']}",
                        metric_name=metric.name,
                        threshold=rule["threshold"],
                        current_value=metric.value
                    )
                    
                    # Check if similar alert is already active
                    existing_alert = None
                    for existing_id, existing in self.active_alerts.items():
                        if existing.metric_name == metric.name and not existing.is_resolved:
                            existing_alert = existing
                            break
                    
                    if not existing_alert:
                        self.active_alerts[alert_id] = alert
                        await self._send_alert_notification(alert, "triggered")
                        
                        self.logger.warning(f"Alert triggered: {alert.name}")
        
        except Exception as e:
            self.logger.error(f"Error checking metric alerts: {e}")

    async def _send_alert_notification(self, alert -> None: Alert, action -> None: str) -> None:
        """Send alert notification"""
        
        notification_data = {
            "alert_id": alert.alert_id,
            "name": alert.name,
            "severity": alert.severity.value,
            "message": alert.message,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "action": action,  # triggered, resolved
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store notification for processing by notification service
        await self.redis_client.lpush(
            f"alert_notifications:{alert.severity.value}",
            json.dumps(notification_data)
        )
        
        self.logger.info(f"Alert notification sent: {action} - {alert.alert_id}")

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            
            if upper_index < len(sorted_values):
                return (sorted_values[lower_index] * (1 - weight) + 
                       sorted_values[upper_index] * weight)
            else:
                return sorted_values[lower_index]

    async def _store_metric(self, metric -> None: Metric) -> None:
        """Store metric in Redis"""
        
        metric_data = {
            "name": metric.name,
            "type": metric.metric_type.value,
            "value": metric.value,
            "labels": metric.labels,
            "timestamp": metric.timestamp.isoformat(),
            "description": metric.description
        }
        
        # Store individual metric
        await self.redis_client.lpush(
            f"metrics:{metric.name}",
            json.dumps(metric_data)
        )
        
        # Keep only last 1000 metrics per type
        await self.redis_client.ltrim(f"metrics:{metric.name}", 0, 999)
        
        # Store in time series
        timestamp = int(metric.timestamp.timestamp())
        await self.redis_client.zadd(
            f"timeseries:{metric.name}",
            {json.dumps(metric_data): timestamp}
        )
        
        # Keep only last 24 hours of time series data
        cutoff_time = timestamp - 86400
        await self.redis_client.zremrangebyscore(
            f"timeseries:{metric.name}",
            0,
            cutoff_time
        )

    async def _store_metric_aggregations(self, metric_name -> None: str, aggregations -> None: Dict[str, float]) -> None:
        """Store metric aggregations"""
        
        aggregation_data = {
            "metric_name": metric_name,
            "aggregations": aggregations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(
            f"metric_agg:{metric_name}",
            3600,  # 1 hour TTL
            json.dumps(aggregation_data)
        )

    async def _store_health_check_result(self, check_name -> None: str, result -> None: Dict[str, Any]) -> None:
        """Store health check result"""
        
        await self.redis_client.lpush(
            f"health_checks:{check_name}",
            json.dumps(result)
        )
        
        # Keep only last 100 results
        await self.redis_client.ltrim(f"health_checks:{check_name}", 0, 99)

    async def _is_alert_resolved(self, alert: Alert) -> bool:
        """Check if alert condition is resolved"""
        
        # Get recent metrics for the alert
        recent_metrics = await self.redis_client.lrange(
            f"metrics:{alert.metric_name}", 0, 4
        )
        
        if not recent_metrics:
            return False
        
        # Check if last 5 metrics are below threshold
        below_threshold_count = 0
        for metric_json in recent_metrics:
            metric_data = json.loads(metric_json)
            
            if alert.metric_name in ["cpu_usage", "memory_usage_percent", "disk_usage_percent"]:
                if metric_data["value"] < alert.threshold:
                    below_threshold_count += 1
            elif alert.metric_name == "health_check_status":
                if metric_data["value"] >= alert.threshold:
                    below_threshold_count += 1
        
        return below_threshold_count >= 3  # 3 out of 5 metrics below threshold

    async def _archive_resolved_alert(self, alert -> None: Alert) -> None:
        """Archive resolved alert"""
        
        alert_data = {
            "alert_id": alert.alert_id,
            "name": alert.name,
            "severity": alert.severity.value,
            "message": alert.message,
            "metric_name": alert.metric_name,
            "threshold": alert.threshold,
            "current_value": alert.current_value,
            "triggered_at": alert.triggered_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "is_resolved": alert.is_resolved
        }
        
        await self.redis_client.lpush("resolved_alerts", json.dumps(alert_data))
        
        # Keep only last 500 resolved alerts
        await self.redis_client.ltrim("resolved_alerts", 0, 499)

    async def _analyze_response_times(self) -> None:
        """Analyze response time trends"""
        
        try:
            # Get response time metrics
            response_metrics = await self.redis_client.lrange(
                "metrics:http_request_duration", 0, 99
            )
            
            if response_metrics:
                values = []
                for metric_json in response_metrics:
                    metric_data = json.loads(metric_json)
                    values.append(metric_data["value"])
                
                if values:
                    p95_response_time = self._calculate_percentile(values, 95)
                    
                    # Check if P95 response time exceeds threshold
                    if p95_response_time > self.alert_thresholds["response_time_p95"]:
                        await self.record_metric(Metric(
                            name="response_time_alert",
                            metric_type=MetricType.GAUGE,
                            value=p95_response_time,
                            description="P95 response time exceeds threshold"
                        ))
        
        except Exception as e:
            self.logger.error(f"Error analyzing response times: {e}")

    async def _analyze_error_rates(self) -> None:
        """Analyze error rate trends"""
        
        try:
            # Get request metrics with status codes
            request_metrics = await self.redis_client.lrange(
                "metrics:http_requests_total", 0, 199
            )
            
            if request_metrics:
                total_requests = 0
                error_requests = 0
                
                for metric_json in request_metrics:
                    metric_data = json.loads(metric_json)
                    if "status" in metric_data["labels"]:
                        status = metric_data["labels"]["status"]
                        total_requests += 1
                        
                        if status.startswith("4") or status.startswith("5"):
                            error_requests += 1
                
                if total_requests > 0:
                    error_rate = error_requests / total_requests
                    
                    await self.record_metric(Metric(
                        name="error_rate",
                        metric_type=MetricType.GAUGE,
                        value=error_rate,
                        description="Current error rate"
                    ))
        
        except Exception as e:
            self.logger.error(f"Error analyzing error rates: {e}")

    async def _analyze_resource_usage(self) -> None:
        """Analyze resource usage trends"""
        
        try:
            # Analyze CPU usage trend
            cpu_metrics = await self.redis_client.lrange("metrics:cpu_usage", 0, 19)
            if cpu_metrics:
                cpu_values = [json.loads(m)["value"] for m in cpu_metrics]
                cpu_trend = self._calculate_trend(cpu_values)
                
                await self.record_metric(Metric(
                    name="cpu_usage_trend",
                    metric_type=MetricType.GAUGE,
                    value=cpu_trend,
                    description="CPU usage trend indicator"
                ))
            
            # Analyze memory usage trend
            memory_metrics = await self.redis_client.lrange("metrics:memory_usage_percent", 0, 19)
            if memory_metrics:
                memory_values = [json.loads(m)["value"] for m in memory_metrics]
                memory_trend = self._calculate_trend(memory_values)
                
                await self.record_metric(Metric(
                    name="memory_usage_trend",
                    metric_type=MetricType.GAUGE,
                    value=memory_trend,
                    description="Memory usage trend indicator"
                ))
        
        except Exception as e:
            self.logger.error(f"Error analyzing resource usage: {e}")

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend indicator (-1 to 1, where 1 is strongly increasing)"""
        
        if len(values) < 3:
            return 0.0
        
        # Simple linear regression to calculate trend
        n = len(values)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalize slope to -1 to 1 range
        return max(-1.0, min(1.0, slope))

    async def _update_performance_baselines(self) -> None:
        """Update performance baselines based on historical data"""
        
        try:
            baseline_metrics = ["cpu_usage", "memory_usage_percent", "http_request_duration"]
            
            for metric_name in baseline_metrics:
                # Get last 100 metrics
                metrics = await self.redis_client.lrange(f"metrics:{metric_name}", 0, 99)
                
                if metrics:
                    values = [json.loads(m)["value"] for m in metrics]
                    
                    # Calculate baseline as median of historical values
                    baseline = statistics.median(values)
                    self.performance_baselines[metric_name] = baseline
                    
                    # Store baseline
                    await self.redis_client.setex(
                        f"baseline:{metric_name}",
                        86400,  # 24 hours
                        str(baseline)
                    )
        
        except Exception as e:
            self.logger.error(f"Error updating performance baselines: {e}")

    async def _load_monitoring_config(self) -> None:
        """Load monitoring configuration from Redis"""
        
        try:
            # Load alert thresholds
            thresholds_data = await self.redis_client.get("alert_thresholds")
            if thresholds_data:
                self.alert_thresholds.update(json.loads(thresholds_data))
            
            # Load health checks
            health_checks_data = await self.redis_client.get("health_checks_config")
            if health_checks_data:
                checks_dict = json.loads(health_checks_data)
                for name, config in checks_dict.items():
                    self.health_checks[name] = HealthCheck(**config)
            
            self.logger.info("Monitoring configuration loaded")
            
        except Exception as e:
            self.logger.warning(f"Could not load monitoring config: {e}")

    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        
        # Get system metrics summary
        system_metrics = {}
        for metric_name in ["cpu_usage", "memory_usage_percent", "disk_usage_percent"]:
            latest_metric = await self.redis_client.lrange(f"metrics:{metric_name}", 0, 0)
            if latest_metric:
                metric_data = json.loads(latest_metric[0])
                system_metrics[metric_name] = metric_data["value"]
        
        # Get active alerts
        active_alerts_data = []
        for alert in self.active_alerts.values():
            active_alerts_data.append({
                "alert_id": alert.alert_id,
                "name": alert.name,
                "severity": alert.severity.value,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat()
            })
        
        # Get health check status
        health_status = {}
        for check_name in self.health_checks.keys():
            latest_result = await self.redis_client.lrange(f"health_checks:{check_name}", 0, 0)
            if latest_result:
                result_data = json.loads(latest_result[0])
                health_status[check_name] = result_data["is_healthy"]
        
        # Get recent metrics aggregations
        metric_aggregations = {}
        for metric_name in ["http_request_duration", "http_requests_total"]:
            agg_data = await self.redis_client.get(f"metric_agg:{metric_name}")
            if agg_data:
                metric_aggregations[metric_name] = json.loads(agg_data)["aggregations"]
        
        return {
            "system_metrics": system_metrics,
            "active_alerts": active_alerts_data,
            "health_status": health_status,
            "metric_aggregations": metric_aggregations,
            "business_metrics": self.business_metrics,
            "performance_baselines": self.performance_baselines,
            "monitoring_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def get_metrics_export(self) -> str:
        """Export metrics in Prometheus format"""
        
        return generate_latest(self.registry).decode('utf-8')

    async def shutdown(self) -> None:
        """Shutdown monitoring service gracefully"""
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Application Monitoring Service shutdown completed")


# Example usage
async def main() -> None:
    """Example usage of Application Monitoring Service"""
    
    monitoring = ApplicationMonitoringService()
    await monitoring.initialize()
    
    try:
        # Example metrics recording
        await monitoring.record_request("GET", "/api/users", 200, 0.15)
        await monitoring.record_business_metric("active_users", 1250)
        
        # Example custom metric
        await monitoring.record_metric(Metric(
            name="custom_processing_time",
            metric_type=MetricType.HISTOGRAM,
            value=0.85,
            labels={"service": "content_processor"}
        ))
        
        # Get dashboard
        dashboard = await monitoring.get_monitoring_dashboard()
        print(f"Monitoring dashboard: {dashboard}")
        
        # Get Prometheus metrics
        metrics_export = await monitoring.get_metrics_export()
        print(f"Prometheus metrics: {metrics_export}")
        
        # Let monitoring run for a bit
        await asyncio.sleep(5)
        
    finally:
        await monitoring.shutdown()


if __name__ == "__main__":
    asyncio.run(main())