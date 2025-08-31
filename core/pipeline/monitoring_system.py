"""Monitoring System

Ultra-advanced monitoring and observability system for pipeline executions
with real-time metrics, intelligent alerting, and comprehensive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Data Collection → Metrics Processing → Alerting → Analytics → Insights → Optimization
"""
import asyncio
import logging
import time
import json
import uuid
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics
import psutil
import aiohttp
import websockets

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SET = "set"


class AlertLevel(Enum):
    """Alert levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class MonitoringStatus(Enum):
    """Monitoring status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Metric data structure"""
    name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    value: Union[int, float] = 0
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Additional metadata
    unit: str = ""
    description: str = ""
    source: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "labels": self.labels,
            "unit": self.unit,
            "description": self.description,
            "source": self.source
        }


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str = ""
    name: str = ""
    level: AlertLevel = AlertLevel.WARNING
    status: AlertStatus = AlertStatus.ACTIVE
    message: str = ""
    description: str = ""
    
    # Alert conditions
    metric_name: str = ""
    condition: str = ""
    threshold: Union[int, float] = 0
    current_value: Union[int, float] = 0
    
    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    # Context
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Actions
    actions_taken: List[str] = field(default_factory=list)
    escalation_level: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "level": self.level.value,
            "status": self.status.value,
            "message": self.message,
            "description": self.description,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "tags": self.tags,
            "metadata": self.metadata,
            "actions_taken": self.actions_taken,
            "escalation_level": self.escalation_level
        }


@dataclass
class HealthCheck:
    """Health check result"""
    component: str = ""
    status: MonitoringStatus = MonitoringStatus.HEALTHY
    message: str = ""
    response_time: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)
    
    # Health metrics
    success_rate: float = 1.0
    average_response_time: float = 0.0
    error_count: int = 0
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check to dictionary"""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "response_time": self.response_time,
            "last_check": self.last_check.isoformat(),
            "success_rate": self.success_rate,
            "average_response_time": self.average_response_time,
            "error_count": self.error_count,
            "metadata": self.metadata,
            "dependencies": self.dependencies
        }


class MetricCollector:
    """Advanced metric collection system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetricCollector")
        
        # Metric storage
        self.metrics: deque = deque(maxlen=config.get("max_metrics", 100000))
        self.metric_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time metrics
        self.real_time_metrics: Dict[str, Metric] = {}
        
        # Collection tasks
        self.collection_tasks: Dict[str, asyncio.Task] = {}
        self.collection_active = False
        
        # Custom collectors
        self.custom_collectors: Dict[str, Callable] = {}
        
        # Start automatic collection
        if config.get("auto_collection", True):
            self._start_collection()
    
    def _start_collection(self):
        """Start metric collection"""
        self.collection_active = True
        
        # Start system metrics collection
        self.collection_tasks["system"] = asyncio.create_task(
            self._collect_system_metrics()
        )
        
        # Start application metrics collection
        self.collection_tasks["application"] = asyncio.create_task(
            self._collect_application_metrics()
        )
        
        # Start custom metrics collection
        self.collection_tasks["custom"] = asyncio.create_task(
            self._collect_custom_metrics()
        )
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        collection_interval = self.config.get("system_collection_interval", 5.0)
        
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                
                self._record_metric(Metric(
                    name="system.cpu.usage",
                    metric_type=MetricType.GAUGE,
                    value=cpu_percent,
                    timestamp=timestamp,
                    unit="percent",
                    description="CPU usage percentage",
                    source="system"
                ))
                
                self._record_metric(Metric(
                    name="system.cpu.count",
                    metric_type=MetricType.GAUGE,
                    value=cpu_count,
                    timestamp=timestamp,
                    unit="cores",
                    description="Number of CPU cores",
                    source="system"
                ))
                
                # Memory metrics
                memory = psutil.virtual_memory()
                
                self._record_metric(Metric(
                    name="system.memory.usage",
                    metric_type=MetricType.GAUGE,
                    value=memory.percent,
                    timestamp=timestamp,
                    unit="percent",
                    description="Memory usage percentage",
                    source="system"
                ))
                
                self._record_metric(Metric(
                    name="system.memory.available",
                    metric_type=MetricType.GAUGE,
                    value=memory.available / (1024**3),  # GB
                    timestamp=timestamp,
                    unit="GB",
                    description="Available memory",
                    source="system"
                ))
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                
                self._record_metric(Metric(
                    name="system.disk.usage",
                    metric_type=MetricType.GAUGE,
                    value=(disk.used / disk.total) * 100,
                    timestamp=timestamp,
                    unit="percent",
                    description="Disk usage percentage",
                    source="system"
                ))
                
                self._record_metric(Metric(
                    name="system.disk.free",
                    metric_type=MetricType.GAUGE,
                    value=disk.free / (1024**3),  # GB
                    timestamp=timestamp,
                    unit="GB",
                    description="Free disk space",
                    source="system"
                ))
                
                # Network metrics
                network = psutil.net_io_counters()
                
                self._record_metric(Metric(
                    name="system.network.bytes_sent",
                    metric_type=MetricType.COUNTER,
                    value=network.bytes_sent,
                    timestamp=timestamp,
                    unit="bytes",
                    description="Network bytes sent",
                    source="system"
                ))
                
                self._record_metric(Metric(
                    name="system.network.bytes_recv",
                    metric_type=MetricType.COUNTER,
                    value=network.bytes_recv,
                    timestamp=timestamp,
                    unit="bytes",
                    description="Network bytes received",
                    source="system"
                ))
                
                await asyncio.sleep(collection_interval)
                
            except Exception as e:
                self.logger.error(f"System metrics collection error: {e}")
                await asyncio.sleep(collection_interval * 2)
    
    async def _collect_application_metrics(self):
        """Collect application-level metrics"""
        collection_interval = self.config.get("app_collection_interval", 10.0)
        
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # Pipeline metrics (simulated)
                self._record_metric(Metric(
                    name="pipeline.executions.total",
                    metric_type=MetricType.COUNTER,
                    value=self._get_pipeline_executions_count(),
                    timestamp=timestamp,
                    unit="count",
                    description="Total pipeline executions",
                    source="application"
                ))
                
                self._record_metric(Metric(
                    name="pipeline.executions.success_rate",
                    metric_type=MetricType.GAUGE,
                    value=self._get_pipeline_success_rate(),
                    timestamp=timestamp,
                    unit="percent",
                    description="Pipeline success rate",
                    source="application"
                ))
                
                self._record_metric(Metric(
                    name="pipeline.executions.avg_duration",
                    metric_type=MetricType.GAUGE,
                    value=self._get_average_execution_duration(),
                    timestamp=timestamp,
                    unit="seconds",
                    description="Average pipeline execution duration",
                    source="application"
                ))
                
                # Content processing metrics
                self._record_metric(Metric(
                    name="content.processed.total",
                    metric_type=MetricType.COUNTER,
                    value=self._get_content_processed_count(),
                    timestamp=timestamp,
                    unit="count",
                    description="Total content items processed",
                    source="application"
                ))
                
                self._record_metric(Metric(
                    name="content.processing.queue_size",
                    metric_type=MetricType.GAUGE,
                    value=self._get_processing_queue_size(),
                    timestamp=timestamp,
                    unit="items",
                    description="Content processing queue size",
                    source="application"
                ))
                
                # AI analysis metrics
                self._record_metric(Metric(
                    name="ai.analysis.requests",
                    metric_type=MetricType.COUNTER,
                    value=self._get_ai_analysis_requests(),
                    timestamp=timestamp,
                    unit="count",
                    description="AI analysis requests",
                    source="application"
                ))
                
                self._record_metric(Metric(
                    name="ai.analysis.accuracy",
                    metric_type=MetricType.GAUGE,
                    value=self._get_ai_analysis_accuracy(),
                    timestamp=timestamp,
                    unit="percent",
                    description="AI analysis accuracy",
                    source="application"
                ))
                
                await asyncio.sleep(collection_interval)
                
            except Exception as e:
                self.logger.error(f"Application metrics collection error: {e}")
                await asyncio.sleep(collection_interval * 2)
    
    async def _collect_custom_metrics(self):
        """Collect custom metrics"""
        collection_interval = self.config.get("custom_collection_interval", 30.0)
        
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # Execute custom collectors
                for name, collector in self.custom_collectors.items():
                    try:
                        metrics = await self._execute_collector(collector, timestamp)
                        for metric in metrics:
                            self._record_metric(metric)
                    except Exception as e:
                        self.logger.error(f"Custom collector '{name}' failed: {e}")
                
                await asyncio.sleep(collection_interval)
                
            except Exception as e:
                self.logger.error(f"Custom metrics collection error: {e}")
                await asyncio.sleep(collection_interval * 2)
    
    async def _execute_collector(self, collector: Callable, timestamp: datetime) -> List[Metric]:
        """Execute custom metric collector"""
        if asyncio.iscoroutinefunction(collector):
            return await collector(timestamp)
        else:
            return collector(timestamp)
    
    def _record_metric(self, metric: Metric):
        """Record a metric"""
        # Add to main storage
        self.metrics.append(metric)
        
        # Add to metric-specific buffer
        self.metric_buffer[metric.name].append(metric)
        
        # Update real-time metrics
        self.real_time_metrics[metric.name] = metric
        
        # Log high-level metrics
        if metric.name.endswith('.total') or metric.name.endswith('.usage'):
            self.logger.debug(f"Metric recorded: {metric.name} = {metric.value} {metric.unit}")
    
    # Simulated metric getters (replace with actual implementations)
    def _get_pipeline_executions_count(self) -> int:
        """Get pipeline executions count"""
        import random
        return random.randint(1000, 5000)
    
    def _get_pipeline_success_rate(self) -> float:
        """Get pipeline success rate"""
        import random
        return random.uniform(85.0, 99.5)
    
    def _get_average_execution_duration(self) -> float:
        """Get average execution duration"""
        import random
        return random.uniform(15.0, 45.0)
    
    def _get_content_processed_count(self) -> int:
        """Get content processed count"""
        import random
        return random.randint(500, 2000)
    
    def _get_processing_queue_size(self) -> int:
        """Get processing queue size"""
        import random
        return random.randint(0, 100)
    
    def _get_ai_analysis_requests(self) -> int:
        """Get AI analysis requests"""
        import random
        return random.randint(100, 500)
    
    def _get_ai_analysis_accuracy(self) -> float:
        """Get AI analysis accuracy"""
        import random
        return random.uniform(90.0, 98.5)
    
    def record_metric(self, metric: Metric):
        """Public method to record a metric"""
        self._record_metric(metric)
    
    def get_metrics(self, metric_name: Optional[str] = None, limit: int = 1000) -> List[Metric]:
        """Get metrics"""
        if metric_name:
            return list(self.metric_buffer[metric_name])[-limit:]
        else:
            return list(self.metrics)[-limit:]
    
    def get_real_time_metrics(self) -> Dict[str, Metric]:
        """Get real-time metrics"""
        return self.real_time_metrics.copy()
    
    def add_custom_collector(self, name: str, collector: Callable):
        """Add custom metric collector"""
        self.custom_collectors[name] = collector
        self.logger.info(f"Added custom collector: {name}")
    
    def remove_custom_collector(self, name: str):
        """Remove custom metric collector"""
        if name in self.custom_collectors:
            del self.custom_collectors[name]
            self.logger.info(f"Removed custom collector: {name}")
    
    def stop_collection(self):
        """Stop metric collection"""
        self.collection_active = False
        for task in self.collection_tasks.values():
            task.cancel()
        self.collection_tasks.clear()


class AlertManager:
    """Advanced alerting system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AlertManager")
        
        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=config.get("max_alert_history", 10000))
        
        # Alert rules
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Notification channels
        self.notification_channels: Dict[str, Callable] = {}
        
        # Alert processing
        self.alert_processor_task: Optional[asyncio.Task] = None
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        self.processing_active = False
        
        # Initialize default alert rules
        self._initialize_default_rules()
        
        # Start alert processing
        self._start_alert_processing()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        self.alert_rules = {
            "high_cpu_usage": {
                "metric": "system.cpu.usage",
                "condition": ">",
                "threshold": 85.0,
                "level": AlertLevel.WARNING,
                "duration": 300,  # 5 minutes
                "description": "High CPU usage detected"
            },
            "critical_cpu_usage": {
                "metric": "system.cpu.usage",
                "condition": ">",
                "threshold": 95.0,
                "level": AlertLevel.CRITICAL,
                "duration": 60,  # 1 minute
                "description": "Critical CPU usage detected"
            },
            "high_memory_usage": {
                "metric": "system.memory.usage",
                "condition": ">",
                "threshold": 80.0,
                "level": AlertLevel.WARNING,
                "duration": 300,
                "description": "High memory usage detected"
            },
            "critical_memory_usage": {
                "metric": "system.memory.usage",
                "condition": ">",
                "threshold": 95.0,
                "level": AlertLevel.CRITICAL,
                "duration": 60,
                "description": "Critical memory usage detected"
            },
            "low_disk_space": {
                "metric": "system.disk.free",
                "condition": "<",
                "threshold": 10.0,
                "level": AlertLevel.WARNING,
                "duration": 0,
                "description": "Low disk space detected"
            },
            "pipeline_failure_rate": {
                "metric": "pipeline.executions.success_rate",
                "condition": "<",
                "threshold": 90.0,
                "level": AlertLevel.ERROR,
                "duration": 600,  # 10 minutes
                "description": "Pipeline failure rate is high"
            }
        }
    
    def _start_alert_processing(self):
        """Start alert processing"""
        self.processing_active = True
        self.alert_processor_task = asyncio.create_task(self._process_alerts())
    
    async def _process_alerts(self):
        """Process alert queue"""
        while self.processing_active:
            try:
                # Get metric from queue
                metric = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                
                # Check metric against alert rules
                await self._check_alert_rules(metric)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
                await asyncio.sleep(1.0)
    
    async def _check_alert_rules(self, metric: Metric):
        """Check metric against alert rules"""
        for rule_name, rule in self.alert_rules.items():
            if rule["metric"] == metric.name:
                await self._evaluate_rule(rule_name, rule, metric)
    
    async def _evaluate_rule(self, rule_name: str, rule: Dict[str, Any], metric: Metric):
        """Evaluate alert rule"""
        condition = rule["condition"]
        threshold = rule["threshold"]
        current_value = metric.value
        
        # Check condition
        triggered = False
        if condition == ">":
            triggered = current_value > threshold
        elif condition == "<":
            triggered = current_value < threshold
        elif condition == ">=":
            triggered = current_value >= threshold
        elif condition == "<=":
            triggered = current_value <= threshold
        elif condition == "==":
            triggered = current_value == threshold
        elif condition == "!=":
            triggered = current_value != threshold
        
        alert_id = f"alert_{rule_name}_{metric.name}"
        
        if triggered:
            # Check if alert already exists
            if alert_id in self.active_alerts:
                # Update existing alert
                alert = self.active_alerts[alert_id]
                alert.current_value = current_value
            else:
                # Create new alert
                alert = Alert(
                    alert_id=alert_id,
                    name=rule_name,
                    level=rule["level"],
                    message=f"{rule['description']}: {current_value} {condition} {threshold}",
                    description=rule["description"],
                    metric_name=metric.name,
                    condition=f"{condition} {threshold}",
                    threshold=threshold,
                    current_value=current_value,
                    tags=metric.tags.copy(),
                    metadata={
                        "rule": rule_name,
                        "metric_source": metric.source,
                        "metric_unit": metric.unit
                    }
                )
                
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                
                # Send notification
                await self._send_alert_notification(alert)
                
                self.logger.warning(f"Alert triggered: {alert.name} - {alert.message}")
        
        else:
            # Check if alert should be resolved
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                # Send resolution notification
                await self._send_resolution_notification(alert)
                
                self.logger.info(f"Alert resolved: {alert.name}")
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        for channel_name, channel in self.notification_channels.items():
            try:
                if asyncio.iscoroutinefunction(channel):
                    await channel(alert)
                else:
                    channel(alert)
            except Exception as e:
                self.logger.error(f"Failed to send alert to {channel_name}: {e}")
    
    async def _send_resolution_notification(self, alert: Alert):
        """Send alert resolution notification"""
        for channel_name, channel in self.notification_channels.items():
            try:
                if asyncio.iscoroutinefunction(channel):
                    await channel(alert)
                else:
                    channel(alert)
            except Exception as e:
                self.logger.error(f"Failed to send resolution to {channel_name}: {e}")
    
    async def process_metric(self, metric: Metric):
        """Process metric for alerting"""
        await self.alert_queue.put(metric)
    
    def add_alert_rule(self, name: str, rule: Dict[str, Any]):
        """Add alert rule"""
        self.alert_rules[name] = rule
        self.logger.info(f"Added alert rule: {name}")
    
    def remove_alert_rule(self, name: str):
        """Remove alert rule"""
        if name in self.alert_rules:
            del self.alert_rules[name]
            self.logger.info(f"Removed alert rule: {name}")
    
    def add_notification_channel(self, name: str, channel: Callable):
        """Add notification channel"""
        self.notification_channels[name] = channel
        self.logger.info(f"Added notification channel: {name}")
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            self.logger.info(f"Alert acknowledged: {alert.name}")
    
    def silence_alert(self, alert_id: str, duration: int = 3600):
        """Silence alert for specified duration"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SILENCED
            # Note: In a real implementation, you'd set a timer to unsilence
            self.logger.info(f"Alert silenced for {duration} seconds: {alert.name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return list(self.alert_history)[-limit:]
    
    def stop_processing(self):
        """Stop alert processing"""
        self.processing_active = False
        if self.alert_processor_task:
            self.alert_processor_task.cancel()


class HealthMonitor:
    """Advanced health monitoring system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.HealthMonitor")
        
        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_check_functions: Dict[str, Callable] = {}
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.monitoring_active = False
        
        # Initialize default health checks
        self._initialize_default_health_checks()
        
        # Start health monitoring
        if config.get("enabled", True):
            self._start_health_monitoring()
    
    def _initialize_default_health_checks(self):
        """Initialize default health checks"""
        self.health_check_functions = {
            "system": self._check_system_health,
            "database": self._check_database_health,
            "cache": self._check_cache_health,
            "ai_services": self._check_ai_services_health,
            "content_pipeline": self._check_content_pipeline_health
        }
    
    def _start_health_monitoring(self):
        """Start health monitoring"""
        self.monitoring_active = True
        
        # Start health check tasks
        for component, check_func in self.health_check_functions.items():
            self.monitoring_tasks[component] = asyncio.create_task(
                self._monitor_component_health(component, check_func)
            )
    
    async def _monitor_component_health(self, component: str, check_func: Callable):
        """Monitor component health"""
        check_interval = self.config.get("check_interval", 60.0)
        
        while self.monitoring_active:
            try:
                start_time = time.time()
                
                # Execute health check
                if asyncio.iscoroutinefunction(check_func):
                    health_check = await check_func()
                else:
                    health_check = check_func()
                
                # Calculate response time
                response_time = time.time() - start_time
                health_check.response_time = response_time
                health_check.last_check = datetime.now()
                
                # Update health check
                self.health_checks[component] = health_check
                
                # Log health status changes
                if health_check.status != MonitoringStatus.HEALTHY:
                    self.logger.warning(f"Health check failed for {component}: {health_check.message}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Health check error for {component}: {e}")
                
                # Create error health check
                error_health_check = HealthCheck(
                    component=component,
                    status=MonitoringStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    response_time=0.0,
                    error_count=1
                )
                self.health_checks[component] = error_health_check
                
                await asyncio.sleep(check_interval * 2)
    
    async def _check_system_health(self) -> HealthCheck:
        """Check system health"""
        try:
            # Check system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status
            status = MonitoringStatus.HEALTHY
            message = "System is healthy"
            
            if cpu_percent > 90 or memory.percent > 90 or (disk.used / disk.total) > 0.95:
                status = MonitoringStatus.CRITICAL
                message = "System resources critically high"
            elif cpu_percent > 80 or memory.percent > 80 or (disk.used / disk.total) > 0.85:
                status = MonitoringStatus.DEGRADED
                message = "System resources high"
            
            return HealthCheck(
                component="system",
                status=status,
                message=message,
                metadata={
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": (disk.used / disk.total) * 100
                }
            )
            
        except Exception as e:
            return HealthCheck(
                component="system",
                status=MonitoringStatus.CRITICAL,
                message=f"System health check failed: {str(e)}"
            )
    
    async def _check_database_health(self) -> HealthCheck:
        """Check database health"""
        try:
            # Simulate database check
            await asyncio.sleep(0.1)  # Simulate DB query
            
            # In real implementation, check actual database connectivity
            
            return HealthCheck(
                component="database",
                status=MonitoringStatus.HEALTHY,
                message="Database is accessible",
                metadata={
                    "connection_pool_size": 10,
                    "active_connections": 5
                }
            )
            
        except Exception as e:
            return HealthCheck(
                component="database",
                status=MonitoringStatus.CRITICAL,
                message=f"Database health check failed: {str(e)}"
            )
    
    async def _check_cache_health(self) -> HealthCheck:
        """Check cache health"""
        try:
            # Simulate cache check
            await asyncio.sleep(0.05)  # Simulate cache ping
            
            return HealthCheck(
                component="cache",
                status=MonitoringStatus.HEALTHY,
                message="Cache is responding",
                metadata={
                    "hit_rate": 85.5,
                    "memory_usage": 45.2
                }
            )
            
        except Exception as e:
            return HealthCheck(
                component="cache",
                status=MonitoringStatus.CRITICAL,
                message=f"Cache health check failed: {str(e)}"
            )
    
    async def _check_ai_services_health(self) -> HealthCheck:
        """Check AI services health"""
        try:
            # Simulate AI services check
            await asyncio.sleep(0.2)  # Simulate AI service ping
            
            return HealthCheck(
                component="ai_services",
                status=MonitoringStatus.HEALTHY,
                message="AI services are operational",
                metadata={
                    "model_accuracy": 94.2,
                    "processing_queue": 12
                }
            )
            
        except Exception as e:
            return HealthCheck(
                component="ai_services",
                status=MonitoringStatus.CRITICAL,
                message=f"AI services health check failed: {str(e)}"
            )
    
    async def _check_content_pipeline_health(self) -> HealthCheck:
        """Check content pipeline health"""
        try:
            # Simulate pipeline check
            await asyncio.sleep(0.15)  # Simulate pipeline status check
            
            return HealthCheck(
                component="content_pipeline",
                status=MonitoringStatus.HEALTHY,
                message="Content pipeline is processing",
                metadata={
                    "queue_size": 25,
                    "processing_rate": 120.5
                }
            )
            
        except Exception as e:
            return HealthCheck(
                component="content_pipeline",
                status=MonitoringStatus.CRITICAL,
                message=f"Content pipeline health check failed: {str(e)}"
            )
    
    def add_health_check(self, component: str, check_func: Callable):
        """Add custom health check"""
        self.health_check_functions[component] = check_func
        
        if self.monitoring_active:
            self.monitoring_tasks[component] = asyncio.create_task(
                self._monitor_component_health(component, check_func)
            )
        
        self.logger.info(f"Added health check for: {component}")
    
    def get_health_status(self) -> Dict[str, HealthCheck]:
        """Get health status for all components"""
        return self.health_checks.copy()
    
    def get_overall_health(self) -> MonitoringStatus:
        """Get overall system health"""
        if not self.health_checks:
            return MonitoringStatus.UNHEALTHY
        
        critical_count = sum(1 for hc in self.health_checks.values() 
                           if hc.status == MonitoringStatus.CRITICAL)
        
        degraded_count = sum(1 for hc in self.health_checks.values() 
                           if hc.status == MonitoringStatus.DEGRADED)
        
        if critical_count > 0:
            return MonitoringStatus.CRITICAL
        elif degraded_count > len(self.health_checks) / 2:
            return MonitoringStatus.DEGRADED
        elif degraded_count > 0:
            return MonitoringStatus.DEGRADED
        else:
            return MonitoringStatus.HEALTHY
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        for task in self.monitoring_tasks.values():
            task.cancel()
        self.monitoring_tasks.clear()


class MonitoringSystem:
    """
    Ultra-advanced monitoring and observability system for pipeline executions
    with real-time metrics, intelligent alerting, and comprehensive analytics.
    
    Features:
    - Comprehensive metric collection (system, application, custom)
    - Real-time monitoring and alerting
    - Health checks and dependency monitoring
    - Performance analytics and trend analysis
    - Multi-channel notifications
    - Historical data analysis
    - Predictive monitoring capabilities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core components
        self.metric_collector = MetricCollector(self.config.get("metrics", {}))
        self.alert_manager = AlertManager(self.config.get("alerts", {}))
        self.health_monitor = HealthMonitor(self.config.get("health", {}))
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Analytics
        self.analytics_data: Dict[str, Any] = {}
        self.trend_analysis: Dict[str, Any] = {}
        
        # WebSocket connections for real-time updates
        self.websocket_connections: set = set()
        
        # Initialize default notification channels
        self._initialize_notification_channels()
        
        # Start monitoring
        if self.config.get("auto_start", True):
            self.start_monitoring()
        
        self.logger.info("Monitoring System initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "auto_start": True,
            "metrics": {
                "auto_collection": True,
                "max_metrics": 100000,
                "system_collection_interval": 5.0,
                "app_collection_interval": 10.0,
                "custom_collection_interval": 30.0
            },
            "alerts": {
                "max_alert_history": 10000,
                "notification_channels": ["console", "webhook"]
            },
            "health": {
                "enabled": True,
                "check_interval": 60.0
            },
            "analytics": {
                "enabled": True,
                "analysis_interval": 300.0,  # 5 minutes
                "trend_detection": True
            },
            "websocket": {
                "enabled": True,
                "port": 8765,
                "real_time_updates": True
            }
        }
    
    def _initialize_notification_channels(self):
        """Initialize notification channels"""
        # Console notification channel
        self.alert_manager.add_notification_channel(
            "console", self._console_notification
        )
        
        # Webhook notification channel
        self.alert_manager.add_notification_channel(
            "webhook", self._webhook_notification
        )
        
        # Email notification channel (placeholder)
        self.alert_manager.add_notification_channel(
            "email", self._email_notification
        )
    
    async def _console_notification(self, alert: Alert):
        """Console notification channel"""
        level_colors = {
            AlertLevel.INFO: "\033[94m",      # Blue
            AlertLevel.WARNING: "\033[93m",   # Yellow
            AlertLevel.ERROR: "\033[91m",     # Red
            AlertLevel.CRITICAL: "\033[95m"   # Magenta
        }
        
        reset_color = "\033[0m"
        color = level_colors.get(alert.level, "")
        
        message = f"{color}[{alert.level.value.upper()}] {alert.name}: {alert.message}{reset_color}"
        print(message)
        
        # Also log to logger
        if alert.level == AlertLevel.CRITICAL:
            self.logger.critical(f"ALERT: {alert.name} - {alert.message}")
        elif alert.level == AlertLevel.ERROR:
            self.logger.error(f"ALERT: {alert.name} - {alert.message}")
        elif alert.level == AlertLevel.WARNING:
            self.logger.warning(f"ALERT: {alert.name} - {alert.message}")
        else:
            self.logger.info(f"ALERT: {alert.name} - {alert.message}")
    
    async def _webhook_notification(self, alert: Alert):
        """Webhook notification channel"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return
        
        try:
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.now().isoformat(),
                "system": "IA-Influencer-Agent-Monitoring"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        self.logger.error(f"Webhook notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Webhook notification error: {e}")
    
    async def _email_notification(self, alert: Alert):
        """Email notification channel (placeholder)"""
        # Placeholder for email notification
        # In real implementation, integrate with email service
        self.logger.info(f"Email notification (placeholder): {alert.name}")
    
    def start_monitoring(self):
        """Start monitoring system"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Start WebSocket server if enabled
        if self.config.get("websocket", {}).get("enabled", True):
            self._start_websocket_server()
        
        self.logger.info("Monitoring system started")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        analytics_interval = self.config.get("analytics", {}).get("analysis_interval", 300.0)
        last_analytics = time.time()
        
        while self.monitoring_active:
            try:
                # Process metrics for alerting
                real_time_metrics = self.metric_collector.get_real_time_metrics()
                
                for metric in real_time_metrics.values():
                    await self.alert_manager.process_metric(metric)
                
                # Update analytics periodically
                current_time = time.time()
                if current_time - last_analytics >= analytics_interval:
                    await self._update_analytics()
                    last_analytics = current_time
                
                # Send real-time updates via WebSocket
                if self.websocket_connections:
                    await self._broadcast_real_time_updates()
                
                await asyncio.sleep(1.0)  # Main loop frequency
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5.0)
    
    async def _update_analytics(self):
        """Update analytics data"""
        try:
            # Get metrics for analysis
            metrics = self.metric_collector.get_metrics(limit=10000)
            health_status = self.health_monitor.get_health_status()
            alert_history = self.alert_manager.get_alert_history(limit=1000)
            
            # Calculate analytics
            self.analytics_data = {
                "metrics_summary": self._calculate_metrics_summary(metrics),
                "health_summary": self._calculate_health_summary(health_status),
                "alert_summary": self._calculate_alert_summary(alert_history),
                "performance_trends": self._calculate_performance_trends(metrics),
                "system_overview": self._calculate_system_overview(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Update trend analysis if enabled
            if self.config.get("analytics", {}).get("trend_detection", True):
                self.trend_analysis = self._analyze_trends(metrics)
            
        except Exception as e:
            self.logger.error(f"Analytics update error: {e}")
    
    def _calculate_metrics_summary(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Calculate metrics summary"""
        if not metrics:
            return {}
        
        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics[-1000:]:  # Last 1000 metrics
            metric_groups[metric.name].append(metric.value)
        
        summary = {}
        for name, values in metric_groups.items():
            if values:
                summary[name] = {
                    "count": len(values),
                    "latest": values[-1],
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": "increasing" if len(values) > 1 and values[-1] > values[0] else "stable"
                }
        
        return summary
    
    def _calculate_health_summary(self, health_status: Dict[str, HealthCheck]) -> Dict[str, Any]:
        """Calculate health summary"""
        if not health_status:
            return {}
        
        status_counts = defaultdict(int)
        total_response_time = 0
        
        for health_check in health_status.values():
            status_counts[health_check.status.value] += 1
            total_response_time += health_check.response_time
        
        return {
            "total_components": len(health_status),
            "healthy": status_counts.get("healthy", 0),
            "degraded": status_counts.get("degraded", 0),
            "unhealthy": status_counts.get("unhealthy", 0),
            "critical": status_counts.get("critical", 0),
            "average_response_time": total_response_time / max(len(health_status), 1),
            "overall_status": self.health_monitor.get_overall_health().value
        }
    
    def _calculate_alert_summary(self, alert_history: List[Alert]) -> Dict[str, Any]:
        """Calculate alert summary"""
        if not alert_history:
            return {}
        
        level_counts = defaultdict(int)
        status_counts = defaultdict(int)
        
        for alert in alert_history[-100:]:  # Last 100 alerts
            level_counts[alert.level.value] += 1
            status_counts[alert.status.value] += 1
        
        return {
            "total_alerts": len(alert_history),
            "by_level": dict(level_counts),
            "by_status": dict(status_counts),
            "active_alerts": len(self.alert_manager.get_active_alerts())
        }
    
    def _calculate_performance_trends(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Calculate performance trends"""
        trends = {}
        
        # Group metrics by name for trend analysis
        metric_groups = defaultdict(list)
        for metric in metrics[-500:]:  # Last 500 metrics
            metric_groups[metric.name].append({
                "value": metric.value,
                "timestamp": metric.timestamp
            })
        
        for name, data in metric_groups.items():
            if len(data) > 10:  # Need sufficient data for trend analysis
                values = [d["value"] for d in data]
                
                # Simple trend calculation
                if len(values) > 1:
                    recent_avg = statistics.mean(values[-5:])
                    overall_avg = statistics.mean(values)
                    
                    if recent_avg > overall_avg * 1.1:
                        trend = "increasing"
                    elif recent_avg < overall_avg * 0.9:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                    
                    trends[name] = {
                        "trend": trend,
                        "recent_average": recent_avg,
                        "overall_average": overall_avg,
                        "change_percentage": ((recent_avg - overall_avg) / overall_avg) * 100
                    }
        
        return trends
    
    def _calculate_system_overview(self) -> Dict[str, Any]:
        """Calculate system overview"""
        real_time_metrics = self.metric_collector.get_real_time_metrics()
        
        overview = {
            "monitoring_uptime": time.time() - getattr(self, '_start_time', time.time()),
            "total_metrics_collected": len(self.metric_collector.metrics),
            "real_time_metrics_count": len(real_time_metrics),
            "active_alerts": len(self.alert_manager.get_active_alerts()),
            "websocket_connections": len(self.websocket_connections),
            "system_status": "operational"
        }
        
        return overview
    
    def _analyze_trends(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze performance trends"""
        # Placeholder for advanced trend analysis
        # In real implementation, use machine learning models
        
        return {
            "trend_analysis_enabled": True,
            "analysis_timestamp": datetime.now().isoformat(),
            "trends_detected": [],
            "anomalies_detected": [],
            "predictions": {}
        }
    
    def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        # Placeholder for WebSocket server
        # In real implementation, start actual WebSocket server
        self.logger.info("WebSocket server started (placeholder)")
    
    async def _broadcast_real_time_updates(self):
        """Broadcast real-time updates to WebSocket clients"""
        if not self.websocket_connections:
            return
        
        try:
            update_data = {
                "type": "real_time_update",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    name: metric.to_dict() 
                    for name, metric in self.metric_collector.get_real_time_metrics().items()
                },
                "alerts": [alert.to_dict() for alert in self.alert_manager.get_active_alerts()],
                "health": {
                    name: health.to_dict() 
                    for name, health in self.health_monitor.get_health_status().items()
                }
            }
            
            # In real implementation, broadcast to WebSocket connections
            self.logger.debug(f"Broadcasting update to {len(self.websocket_connections)} connections")
            
        except Exception as e:
            self.logger.error(f"Broadcast error: {e}")
    
    # Public API methods
    def record_metric(self, metric: Metric):
        """Record a custom metric"""
        self.metric_collector.record_metric(metric)
    
    def add_custom_metric_collector(self, name: str, collector: Callable):
        """Add custom metric collector"""
        self.metric_collector.add_custom_collector(name, collector)
    
    def add_health_check(self, component: str, check_func: Callable):
        """Add custom health check"""
        self.health_monitor.add_health_check(component, check_func)
    
    def add_alert_rule(self, name: str, rule: Dict[str, Any]):
        """Add custom alert rule"""
        self.alert_manager.add_alert_rule(name, rule)
    
    def add_notification_channel(self, name: str, channel: Callable):
        """Add custom notification channel"""
        self.alert_manager.add_notification_channel(name, channel)
    
    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""
        return {
            "real_time_metrics": {
                name: metric.to_dict() 
                for name, metric in self.metric_collector.get_real_time_metrics().items()
            },
            "active_alerts": [alert.to_dict() for alert in self.alert_manager.get_active_alerts()],
            "health_status": {
                name: health.to_dict() 
                for name, health in self.health_monitor.get_health_status().items()
            },
            "analytics": self.analytics_data,
            "trend_analysis": self.trend_analysis,
            "system_overview": self.analytics_data.get("system_overview", {})
        }
    
    def get_metrics_history(self, metric_name: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get metrics history"""
        metrics = self.metric_collector.get_metrics(metric_name, limit)
        return [metric.to_dict() for metric in metrics]
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert"""
        self.alert_manager.acknowledge_alert(alert_id)
    
    def silence_alert(self, alert_id: str, duration: int = 3600):
        """Silence alert"""
        self.alert_manager.silence_alert(alert_id, duration)
    
    async def shutdown(self):
        """Shutdown monitoring system"""
        self.logger.info("Shutting down monitoring system")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        # Stop components
        self.metric_collector.stop_collection()
        self.alert_manager.stop_processing()
        self.health_monitor.stop_monitoring()
        
        # Close WebSocket connections
        self.websocket_connections.clear()
        
        self.logger.info("Monitoring system shutdown complete")
