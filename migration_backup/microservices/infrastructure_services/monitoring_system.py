"""
📊 Enterprise Monitoring & Observability System
🎖️ Multi-Expert Implementation: DevOps + Backend Senior + Microservices + ML Engineer

Complete observability stack with:
- Distributed tracing (Jaeger/Zipkin)
- Metrics collection (Prometheus)
- Centralized logging (ELK stack)
- Real-time alerting
- Performance analytics
- Business metrics
- SLI/SLO monitoring
- Anomaly detection with ML

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import yaml
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import httpx
import redis.asyncio as aioredis
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server, CollectorRegistry
import opentelemetry
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
import uuid
import psutil
import socket

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class SLIType(str, Enum):
    """Service Level Indicator types"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    SATURATION = "saturation"


@dataclass
class Alert:
    """Alert definition"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    service: str = ""
    metric_name: str = ""
    threshold: float = 0.0
    current_value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    runbook_url: Optional[str] = None


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str
    service: str
    sli_type: SLIType
    target_percentage: float  # e.g., 99.9
    time_window: int  # seconds
    error_budget: float = field(init=False)
    current_percentage: float = 0.0
    budget_remaining: float = 0.0
    
    def __post_init__(self):
        self.error_budget = 100 - self.target_percentage


@dataclass
class Trace:
    """Distributed trace"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: float = 0.0
    status: str = "ok"
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    service: str
    message: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    📊 Metrics Collector
    Collects and aggregates application metrics
    """
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics = {}
        self.custom_metrics = {}
        
        # Initialize default metrics
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Initialize default application metrics"""
        # Request metrics
        self.metrics['http_requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'service'],
            registry=self.registry
        )
        
        self.metrics['http_request_duration'] = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint', 'service'],
            registry=self.registry
        )
        
        # System metrics
        self.metrics['cpu_usage'] = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['service', 'instance'],
            registry=self.registry
        )
        
        self.metrics['memory_usage'] = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['service', 'instance'],
            registry=self.registry
        )
        
        self.metrics['active_connections'] = Gauge(
            'active_connections_total',
            'Active connections',
            ['service', 'instance'],
            registry=self.registry
        )
        
        # Business metrics
        self.metrics['content_processed'] = Counter(
            'content_processed_total',
            'Total content processed',
            ['content_type', 'service'],
            registry=self.registry
        )
        
        self.metrics['ai_inference_requests'] = Counter(
            'ai_inference_requests_total',
            'Total AI inference requests',
            ['model_type', 'service'],
            registry=self.registry
        )
        
        self.metrics['user_sessions'] = Gauge(
            'user_sessions_active',
            'Active user sessions',
            ['service'],
            registry=self.registry
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, 
                           duration: float, service: str):
        """Record HTTP request metrics"""
        self.metrics['http_requests_total'].labels(
            method=method, endpoint=endpoint, status_code=status_code, service=service
        ).inc()
        
        self.metrics['http_request_duration'].labels(
            method=method, endpoint=endpoint, service=service
        ).observe(duration)
    
    def record_system_metrics(self, service: str, instance: str):
        """Record system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics['cpu_usage'].labels(service=service, instance=instance).set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics['memory_usage'].labels(service=service, instance=instance).set(memory.used)
        
        # Network connections
        connections = len(psutil.net_connections())
        self.metrics['active_connections'].labels(service=service, instance=instance).set(connections)
    
    def record_business_metric(self, metric_name: str, value: float, labels: Dict[str, str]):
        """Record custom business metric"""
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if hasattr(metric, 'labels'):
                metric.labels(**labels).inc(value) if hasattr(metric, 'inc') else metric.labels(**labels).set(value)
            else:
                metric.inc(value) if hasattr(metric, 'inc') else metric.set(value)
    
    def create_custom_metric(self, name: str, description: str, metric_type: MetricType, 
                           labels: List[str] = None):
        """Create custom metric"""
        labels = labels or []
        
        if metric_type == MetricType.COUNTER:
            metric = Counter(name, description, labels, registry=self.registry)
        elif metric_type == MetricType.GAUGE:
            metric = Gauge(name, description, labels, registry=self.registry)
        elif metric_type == MetricType.HISTOGRAM:
            metric = Histogram(name, description, labels, registry=self.registry)
        elif metric_type == MetricType.SUMMARY:
            metric = Summary(name, description, labels, registry=self.registry)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")
        
        self.custom_metrics[name] = metric
        return metric


class DistributedTracer:
    """
    🔍 Distributed Tracing
    Manages distributed traces across microservices
    """
    
    def __init__(self, service_name: str, jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self.active_traces = {}
        self.completed_traces = deque(maxlen=1000)
        
        # Initialize OpenTelemetry
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        # Configure tracer provider
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        # Configure span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Get tracer
        self.tracer = trace.get_tracer(self.service_name)
    
    def start_trace(self, operation_name: str, parent_context=None) -> Trace:
        """Start a new trace"""
        with self.tracer.start_as_current_span(operation_name) as span:
            trace_id = format(span.get_span_context().trace_id, 'x')
            span_id = format(span.get_span_context().span_id, 'x')
            
            trace_obj = Trace(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                operation_name=operation_name,
                service_name=self.service_name,
                start_time=datetime.utcnow()
            )
            
            self.active_traces[span_id] = trace_obj
            return trace_obj
    
    def finish_trace(self, span_id: str, status: str = "ok", tags: Dict[str, Any] = None):
        """Finish a trace"""
        if span_id in self.active_traces:
            trace_obj = self.active_traces[span_id]
            trace_obj.end_time = datetime.utcnow()
            trace_obj.duration_ms = (trace_obj.end_time - trace_obj.start_time).total_seconds() * 1000
            trace_obj.status = status
            trace_obj.tags.update(tags or {})
            
            self.completed_traces.append(trace_obj)
            del self.active_traces[span_id]
    
    def add_trace_log(self, span_id: str, level: str, message: str, metadata: Dict[str, Any] = None):
        """Add log to trace"""
        if span_id in self.active_traces:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": message,
                "metadata": metadata or {}
            }
            self.active_traces[span_id].logs.append(log_entry)
    
    def get_trace_analytics(self) -> Dict[str, Any]:
        """Get trace analytics"""
        if not self.completed_traces:
            return {"message": "No traces available"}
        
        durations = [trace.duration_ms for trace in self.completed_traces]
        operations = defaultdict(list)
        
        for trace in self.completed_traces:
            operations[trace.operation_name].append(trace.duration_ms)
        
        return {
            "total_traces": len(self.completed_traces),
            "average_duration_ms": statistics.mean(durations),
            "p95_duration_ms": np.percentile(durations, 95),
            "p99_duration_ms": np.percentile(durations, 99),
            "operations": {
                op: {
                    "count": len(op_durations),
                    "avg_duration_ms": statistics.mean(op_durations),
                    "p95_duration_ms": np.percentile(op_durations, 95)
                }
                for op, op_durations in operations.items()
            }
        }


class LogAggregator:
    """
    📝 Log Aggregator
    Collects and processes structured logs
    """
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.log_buffer = deque(maxlen=10000)
        self.log_analytics = defaultdict(int)
    
    async def add_log(self, log_entry: LogEntry):
        """Add log entry"""
        self.log_buffer.append(log_entry)
        
        # Update analytics
        self.log_analytics[f"level_{log_entry.level}"] += 1
        self.log_analytics[f"service_{log_entry.service}"] += 1
        
        # Store in Redis for persistence
        log_data = {
            "timestamp": log_entry.timestamp.isoformat(),
            "level": log_entry.level,
            "service": log_entry.service,
            "message": log_entry.message,
            "trace_id": log_entry.trace_id,
            "span_id": log_entry.span_id,
            "user_id": log_entry.user_id,
            "request_id": log_entry.request_id,
            "metadata": json.dumps(log_entry.metadata)
        }
        
        await self.redis.lpush("logs", json.dumps(log_data))
        await self.redis.expire("logs", 86400 * 7)  # Keep logs for 7 days
    
    async def search_logs(self, query: str, service: Optional[str] = None, 
                         level: Optional[str] = None, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[LogEntry]:
        """Search logs with filters"""
        matching_logs = []
        
        for log_entry in self.log_buffer:
            # Apply filters
            if service and log_entry.service != service:
                continue
            if level and log_entry.level != level:
                continue
            if start_time and log_entry.timestamp < start_time:
                continue
            if end_time and log_entry.timestamp > end_time:
                continue
            if query and query.lower() not in log_entry.message.lower():
                continue
            
            matching_logs.append(log_entry)
        
        return matching_logs
    
    def get_log_analytics(self) -> Dict[str, Any]:
        """Get log analytics"""
        return {
            "total_logs": len(self.log_buffer),
            "analytics": dict(self.log_analytics),
            "recent_errors": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "service": log.service,
                    "message": log.message
                }
                for log in list(self.log_buffer)[-100:]
                if log.level in ["ERROR", "CRITICAL"]
            ][-10:]  # Last 10 errors
        }


class AlertManager:
    """
    🚨 Alert Manager
    Manages alerts and notifications
    """
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.active_alerts = {}
        self.alert_rules = {}
        self.notification_channels = []
    
    def add_alert_rule(self, rule_id: str, metric_name: str, condition: str, 
                      threshold: float, severity: AlertSeverity, service: str = "*"):
        """Add alert rule"""
        self.alert_rules[rule_id] = {
            "metric_name": metric_name,
            "condition": condition,  # >, <, >=, <=, ==, !=
            "threshold": threshold,
            "severity": severity,
            "service": service
        }
    
    def add_notification_channel(self, channel: Callable[[Alert], None]):
        """Add notification channel"""
        self.notification_channels.append(channel)
    
    async def evaluate_metric(self, metric_name: str, value: float, service: str, tags: Dict[str, str] = None):
        """Evaluate metric against alert rules"""
        for rule_id, rule in self.alert_rules.items():
            if rule["metric_name"] != metric_name:
                continue
            if rule["service"] != "*" and rule["service"] != service:
                continue
            
            # Evaluate condition
            triggered = False
            condition = rule["condition"]
            threshold = rule["threshold"]
            
            if condition == ">" and value > threshold:
                triggered = True
            elif condition == "<" and value < threshold:
                triggered = True
            elif condition == ">=" and value >= threshold:
                triggered = True
            elif condition == "<=" and value <= threshold:
                triggered = True
            elif condition == "==" and value == threshold:
                triggered = True
            elif condition == "!=" and value != threshold:
                triggered = True
            
            if triggered:
                await self._trigger_alert(rule_id, metric_name, value, threshold, service, rule["severity"], tags)
    
    async def _trigger_alert(self, rule_id: str, metric_name: str, current_value: float, 
                           threshold: float, service: str, severity: AlertSeverity, tags: Dict[str, str] = None):
        """Trigger an alert"""
        # Check if alert is already active
        alert_key = f"{rule_id}_{service}_{metric_name}"
        if alert_key in self.active_alerts:
            return  # Alert already active
        
        alert = Alert(
            title=f"Alert: {metric_name} threshold exceeded",
            description=f"Metric {metric_name} for service {service} has value {current_value}, exceeding threshold {threshold}",
            severity=severity,
            service=service,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            tags=tags or {}
        )
        
        self.active_alerts[alert_key] = alert
        
        # Store in Redis
        alert_data = asdict(alert)
        alert_data["timestamp"] = alert.timestamp.isoformat()
        await self.redis.setex(f"alert:{alert.alert_id}", 86400, json.dumps(alert_data))
        
        # Send notifications
        for channel in self.notification_channels:
            try:
                await channel(alert) if asyncio.iscoroutinefunction(channel) else channel(alert)
            except Exception as e:
                logger.error(f"Failed to send alert notification: {e}")
        
        logger.warning(f"Alert triggered: {alert.title}")
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        # Find and resolve alert
        for alert_key, alert in self.active_alerts.items():
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                
                # Update in Redis
                alert_data = asdict(alert)
                alert_data["timestamp"] = alert.timestamp.isoformat()
                alert_data["resolved_at"] = alert.resolved_at.isoformat()
                await self.redis.setex(f"alert:{alert.alert_id}", 86400, json.dumps(alert_data))
                
                del self.active_alerts[alert_key]
                logger.info(f"Alert resolved: {alert_id}")
                break
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())


class SLOMonitor:
    """
    📈 SLO Monitor
    Monitors Service Level Objectives
    """
    
    def __init__(self):
        self.slos = {}
        self.sli_data = defaultdict(deque)
    
    def add_slo(self, slo: SLO):
        """Add SLO to monitor"""
        self.slos[slo.slo_id] = slo
        logger.info(f"SLO added: {slo.name} ({slo.target_percentage}%)")
    
    def record_sli(self, slo_id: str, success: bool, value: float = None):
        """Record Service Level Indicator data"""
        if slo_id not in self.slos:
            return
        
        timestamp = time.time()
        sli_entry = {
            "timestamp": timestamp,
            "success": success,
            "value": value
        }
        
        self.sli_data[slo_id].append(sli_entry)
        
        # Keep only data within time window
        slo = self.slos[slo_id]
        cutoff_time = timestamp - slo.time_window
        
        while self.sli_data[slo_id] and self.sli_data[slo_id][0]["timestamp"] < cutoff_time:
            self.sli_data[slo_id].popleft()
    
    def calculate_slo_compliance(self, slo_id: str) -> Dict[str, float]:
        """Calculate SLO compliance"""
        if slo_id not in self.slos or not self.sli_data[slo_id]:
            return {"current_percentage": 0.0, "budget_remaining": 0.0}
        
        slo = self.slos[slo_id]
        data = self.sli_data[slo_id]
        
        if slo.sli_type == SLIType.AVAILABILITY:
            success_count = sum(1 for entry in data if entry["success"])
            total_count = len(data)
            current_percentage = (success_count / total_count) * 100 if total_count > 0 else 0
        
        elif slo.sli_type == SLIType.LATENCY:
            # For latency, success means below threshold
            threshold = slo.target_percentage  # Assuming target_percentage is latency threshold
            success_count = sum(1 for entry in data if entry["value"] and entry["value"] < threshold)
            total_count = len(data)
            current_percentage = (success_count / total_count) * 100 if total_count > 0 else 0
        
        elif slo.sli_type == SLIType.ERROR_RATE:
            error_count = sum(1 for entry in data if not entry["success"])
            total_count = len(data)
            error_rate = (error_count / total_count) * 100 if total_count > 0 else 0
            current_percentage = 100 - error_rate
        
        else:
            # Default calculation
            success_count = sum(1 for entry in data if entry["success"])
            total_count = len(data)
            current_percentage = (success_count / total_count) * 100 if total_count > 0 else 0
        
        # Calculate error budget remaining
        error_budget_used = max(0, slo.target_percentage - current_percentage)
        budget_remaining = max(0, slo.error_budget - error_budget_used)
        
        # Update SLO
        slo.current_percentage = current_percentage
        slo.budget_remaining = budget_remaining
        
        return {
            "current_percentage": current_percentage,
            "budget_remaining": budget_remaining,
            "error_budget_used": error_budget_used,
            "is_compliant": current_percentage >= slo.target_percentage
        }
    
    def get_slo_status(self) -> Dict[str, Any]:
        """Get status of all SLOs"""
        status = {}
        
        for slo_id, slo in self.slos.items():
            compliance = self.calculate_slo_compliance(slo_id)
            status[slo_id] = {
                "name": slo.name,
                "service": slo.service,
                "sli_type": slo.sli_type.value,
                "target_percentage": slo.target_percentage,
                "current_percentage": compliance["current_percentage"],
                "budget_remaining": compliance["budget_remaining"],
                "is_compliant": compliance["is_compliant"],
                "data_points": len(self.sli_data[slo_id])
            }
        
        return status


class AnomalyDetector:
    """
    🤖 ML-Powered Anomaly Detector
    Detects anomalies in metrics using machine learning
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.metric_history = defaultdict(deque)
        self.anomalies = deque(maxlen=1000)
    
    def add_metric_data(self, metric_name: str, value: float, timestamp: float = None):
        """Add metric data for anomaly detection"""
        timestamp = timestamp or time.time()
        self.metric_history[metric_name].append((timestamp, value))
        
        # Keep last 1000 data points
        if len(self.metric_history[metric_name]) > 1000:
            self.metric_history[metric_name].popleft()
    
    def train_model(self, metric_name: str):
        """Train anomaly detection model for metric"""
        if metric_name not in self.metric_history or len(self.metric_history[metric_name]) < 100:
            logger.warning(f"Not enough data to train model for {metric_name}")
            return
        
        # Prepare training data
        data = list(self.metric_history[metric_name])
        values = np.array([point[1] for point in data]).reshape(-1, 1)
        
        # Scale data
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(values)
        
        # Train isolation forest
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(scaled_values)
        
        # Store model and scaler
        self.models[metric_name] = model
        self.scalers[metric_name] = scaler
        
        logger.info(f"Anomaly detection model trained for {metric_name}")
    
    def detect_anomaly(self, metric_name: str, value: float) -> Tuple[bool, float]:
        """Detect if metric value is anomalous"""
        if metric_name not in self.models:
            return False, 0.0
        
        model = self.models[metric_name]
        scaler = self.scalers[metric_name]
        
        # Scale value
        scaled_value = scaler.transform([[value]])
        
        # Predict
        prediction = model.predict(scaled_value)[0]
        score = model.decision_function(scaled_value)[0]
        
        is_anomaly = prediction == -1
        
        if is_anomaly:
            anomaly = {
                "timestamp": time.time(),
                "metric_name": metric_name,
                "value": value,
                "score": abs(score)
            }
            self.anomalies.append(anomaly)
        
        return is_anomaly, abs(score)
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get anomaly detection summary"""
        return {
            "total_anomalies": len(self.anomalies),
            "metrics_monitored": list(self.models.keys()),
            "recent_anomalies": list(self.anomalies)[-10:] if self.anomalies else []
        }


class EnterpriseMonitoringSystem:
    """
    📊 Enterprise Monitoring & Observability System
    🎖️ Complete monitoring stack for microservices
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.metrics_collector = MetricsCollector()
        self.distributed_tracer = None
        self.log_aggregator = None
        self.alert_manager = None
        self.slo_monitor = SLOMonitor()
        self.anomaly_detector = AnomalyDetector()
        self.monitoring_tasks = []
        self.system_metrics = {}
    
    async def initialize(self, service_name: str = "ainflue-monitoring"):
        """Initialize monitoring system"""
        try:
            # Initialize Redis
            self.redis_client = aioredis.from_url(self.redis_url)
            
            # Initialize components
            self.distributed_tracer = DistributedTracer(service_name)
            self.log_aggregator = LogAggregator(self.redis_client)
            self.alert_manager = AlertManager(self.redis_client)
            
            # Setup default alert rules
            await self._setup_default_alerts()
            
            # Setup default SLOs
            self._setup_default_slos()
            
            # Start Prometheus metrics server
            start_http_server(8000, registry=self.metrics_collector.registry)
            
            # Start monitoring tasks
            self.monitoring_tasks = [
                asyncio.create_task(self._system_metrics_collector()),
                asyncio.create_task(self._anomaly_detection_trainer()),
                asyncio.create_task(self._slo_evaluator())
            ]
            
            logger.info("Enterprise Monitoring System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring system: {e}")
            raise
    
    async def _setup_default_alerts(self):
        """Setup default alert rules"""
        # CPU usage alert
        self.alert_manager.add_alert_rule(
            "high_cpu",
            "cpu_usage_percent",
            ">",
            80.0,
            AlertSeverity.WARNING
        )
        
        # Memory usage alert
        self.alert_manager.add_alert_rule(
            "high_memory",
            "memory_usage_bytes",
            ">",
            8 * 1024 * 1024 * 1024,  # 8GB
            AlertSeverity.WARNING
        )
        
        # HTTP error rate alert
        self.alert_manager.add_alert_rule(
            "high_error_rate",
            "http_error_rate",
            ">",
            5.0,  # 5%
            AlertSeverity.ERROR
        )
        
        # Response time alert
        self.alert_manager.add_alert_rule(
            "high_latency",
            "http_request_duration_p95",
            ">",
            1.0,  # 1 second
            AlertSeverity.WARNING
        )
        
        # Add notification channel
        self.alert_manager.add_notification_channel(self._log_alert_notification)
    
    def _setup_default_slos(self):
        """Setup default SLOs"""
        # API availability SLO
        api_availability_slo = SLO(
            slo_id="api_availability",
            name="API Availability",
            service="api-gateway",
            sli_type=SLIType.AVAILABILITY,
            target_percentage=99.9,
            time_window=3600  # 1 hour
        )
        self.slo_monitor.add_slo(api_availability_slo)
        
        # Response time SLO
        response_time_slo = SLO(
            slo_id="response_time",
            name="Response Time P95",
            service="api-gateway",
            sli_type=SLIType.LATENCY,
            target_percentage=500,  # 500ms
            time_window=3600
        )
        self.slo_monitor.add_slo(response_time_slo)
        
        # Error rate SLO
        error_rate_slo = SLO(
            slo_id="error_rate",
            name="Error Rate",
            service="*",
            sli_type=SLIType.ERROR_RATE,
            target_percentage=99.0,  # <1% error rate
            time_window=3600
        )
        self.slo_monitor.add_slo(error_rate_slo)
    
    async def _log_alert_notification(self, alert: Alert):
        """Log alert notification"""
        logger.warning(f"ALERT: {alert.title} - {alert.description}")
        
        # Could also send to Slack, email, PagerDuty, etc.
        notification_data = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "severity": alert.severity.value,
            "service": alert.service,
            "timestamp": alert.timestamp.isoformat()
        }
        
        await self.redis_client.lpush("alert_notifications", json.dumps(notification_data))
    
    async def _system_metrics_collector(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # Collect system metrics for all services
                services = ["api-gateway", "content-service", "ai-service", "auth-service"]
                
                for service in services:
                    instance = socket.gethostname()
                    self.metrics_collector.record_system_metrics(service, instance)
                    
                    # Get current CPU and memory for anomaly detection
                    cpu_percent = psutil.cpu_percent()
                    memory_percent = psutil.virtual_memory().percent
                    
                    self.anomaly_detector.add_metric_data(f"cpu_usage_{service}", cpu_percent)
                    self.anomaly_detector.add_metric_data(f"memory_usage_{service}", memory_percent)
                    
                    # Check for anomalies
                    cpu_anomaly, cpu_score = self.anomaly_detector.detect_anomaly(f"cpu_usage_{service}", cpu_percent)
                    memory_anomaly, memory_score = self.anomaly_detector.detect_anomaly(f"memory_usage_{service}", memory_percent)
                    
                    if cpu_anomaly:
                        await self.log_event("WARNING", service, f"CPU usage anomaly detected: {cpu_percent}% (score: {cpu_score:.2f})")
                    
                    if memory_anomaly:
                        await self.log_event("WARNING", service, f"Memory usage anomaly detected: {memory_percent}% (score: {memory_score:.2f})")
                    
                    # Evaluate against alert rules
                    await self.alert_manager.evaluate_metric("cpu_usage_percent", cpu_percent, service)
                    await self.alert_manager.evaluate_metric("memory_usage_bytes", psutil.virtual_memory().used, service)
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def _anomaly_detection_trainer(self):
        """Train anomaly detection models periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Train every hour
                
                # Train models for all metrics with enough data
                for metric_name in self.anomaly_detector.metric_history.keys():
                    self.anomaly_detector.train_model(metric_name)
                
            except Exception as e:
                logger.error(f"Error in anomaly detection training: {e}")
    
    async def _slo_evaluator(self):
        """Evaluate SLOs periodically"""
        while True:
            try:
                slo_status = self.slo_monitor.get_slo_status()
                
                for slo_id, status in slo_status.items():
                    if not status["is_compliant"]:
                        await self.log_event(
                            "ERROR",
                            status["service"],
                            f"SLO violation: {status['name']} - Current: {status['current_percentage']:.2f}%, Target: {status['target_percentage']}%"
                        )
                
                await asyncio.sleep(300)  # Evaluate every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in SLO evaluation: {e}")
                await asyncio.sleep(300)
    
    async def record_http_request(self, method: str, endpoint: str, status_code: int, 
                                duration_ms: float, service: str, trace_id: str = None):
        """Record HTTP request with full observability"""
        # Record metrics
        self.metrics_collector.record_http_request(method, endpoint, status_code, duration_ms / 1000, service)
        
        # Record SLI data
        is_success = 200 <= status_code < 400
        self.slo_monitor.record_sli("api_availability", is_success)
        self.slo_monitor.record_sli("response_time", duration_ms < 500, duration_ms)
        self.slo_monitor.record_sli("error_rate", is_success)
        
        # Log request
        await self.log_event(
            "INFO" if is_success else "ERROR",
            service,
            f"{method} {endpoint} - {status_code} - {duration_ms}ms",
            trace_id=trace_id,
            metadata={
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": duration_ms
            }
        )
        
        # Check for anomalies in response time
        self.anomaly_detector.add_metric_data(f"response_time_{service}", duration_ms)
        is_anomaly, score = self.anomaly_detector.detect_anomaly(f"response_time_{service}", duration_ms)
        
        if is_anomaly:
            await self.log_event(
                "WARNING",
                service,
                f"Response time anomaly detected: {duration_ms}ms (score: {score:.2f})",
                trace_id=trace_id
            )
        
        # Evaluate alerts
        if status_code >= 400:
            error_rate = await self._calculate_error_rate(service)
            await self.alert_manager.evaluate_metric("http_error_rate", error_rate, service)
        
        p95_latency = await self._calculate_p95_latency(service)
        await self.alert_manager.evaluate_metric("http_request_duration_p95", p95_latency, service)
    
    async def _calculate_error_rate(self, service: str) -> float:
        """Calculate error rate for service"""
        # This would typically query your metrics backend
        # For demo, return a mock value
        return 2.5  # 2.5%
    
    async def _calculate_p95_latency(self, service: str) -> float:
        """Calculate P95 latency for service"""
        # This would typically query your metrics backend
        # For demo, return a mock value
        return 0.8  # 800ms
    
    async def start_trace(self, operation_name: str, service: str = None) -> str:
        """Start distributed trace"""
        service = service or "unknown"
        tracer = DistributedTracer(service)
        trace = tracer.start_trace(operation_name)
        return trace.span_id
    
    async def finish_trace(self, span_id: str, status: str = "ok", tags: Dict[str, Any] = None):
        """Finish distributed trace"""
        if hasattr(self, '_active_tracers'):
            for tracer in self._active_tracers.values():
                if span_id in tracer.active_traces:
                    tracer.finish_trace(span_id, status, tags)
                    break
    
    async def log_event(self, level: str, service: str, message: str, 
                       trace_id: str = None, span_id: str = None, 
                       user_id: str = None, request_id: str = None,
                       metadata: Dict[str, Any] = None):
        """Log structured event"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            service=service,
            message=message,
            trace_id=trace_id,
            span_id=span_id,
            user_id=user_id,
            request_id=request_id,
            metadata=metadata or {}
        )
        
        await self.log_aggregator.add_log(log_entry)
    
    async def record_business_metric(self, metric_name: str, value: float, 
                                   service: str, labels: Dict[str, str] = None):
        """Record business metric"""
        labels = labels or {}
        labels["service"] = service
        
        self.metrics_collector.record_business_metric(metric_name, value, labels)
        
        # Add to anomaly detection
        self.anomaly_detector.add_metric_data(f"{metric_name}_{service}", value)
        is_anomaly, score = self.anomaly_detector.detect_anomaly(f"{metric_name}_{service}", value)
        
        if is_anomaly:
            await self.log_event(
                "WARNING",
                service,
                f"Business metric anomaly detected: {metric_name}={value} (score: {score:.2f})",
                metadata={"metric_name": metric_name, "value": value, "labels": labels}
            )
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        # Get metrics from all components
        trace_analytics = self.distributed_tracer.get_trace_analytics() if self.distributed_tracer else {}
        log_analytics = self.log_aggregator.get_log_analytics()
        active_alerts = self.alert_manager.get_active_alerts()
        slo_status = self.slo_monitor.get_slo_status()
        anomaly_summary = self.anomaly_detector.get_anomaly_summary()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections())
            },
            "traces": trace_analytics,
            "logs": log_analytics,
            "alerts": {
                "active_count": len(active_alerts),
                "critical_count": sum(1 for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL),
                "recent_alerts": [
                    {
                        "title": alert.title,
                        "severity": alert.severity.value,
                        "service": alert.service,
                        "timestamp": alert.timestamp.isoformat()
                    }
                    for alert in active_alerts[-5:]
                ]
            },
            "slos": slo_status,
            "anomalies": anomaly_summary,
            "services": {
                "total_services": len(set(log.service for log in self.log_aggregator.log_buffer)),
                "healthy_services": [],  # Would be calculated based on health checks
                "unhealthy_services": []
            }
        }
    
    async def export_monitoring_config(self) -> str:
        """Export monitoring configuration"""
        config = {
            "alert_rules": self.alert_manager.alert_rules,
            "slos": {
                slo_id: {
                    "name": slo.name,
                    "service": slo.service,
                    "sli_type": slo.sli_type.value,
                    "target_percentage": slo.target_percentage,
                    "time_window": slo.time_window
                }
                for slo_id, slo in self.slo_monitor.slos.items()
            },
            "custom_metrics": list(self.metrics_collector.custom_metrics.keys()),
            "monitoring_settings": {
                "collection_interval": 30,
                "retention_days": 7,
                "anomaly_detection_enabled": True
            }
        }
        
        return yaml.dump(config, default_flow_style=False)
    
    async def shutdown(self):
        """Shutdown monitoring system gracefully"""
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Enterprise Monitoring System shutdown complete")


# Example usage for Ainflue microservices
async def setup_ainflue_monitoring():
    """Setup Ainflue monitoring system"""
    monitoring = EnterpriseMonitoringSystem()
    await monitoring.initialize("ainflue-platform")
    
    # Create custom business metrics
    monitoring.metrics_collector.create_custom_metric(
        "ainflue_content_uploads",
        "Total content uploads to Ainflue platform",
        MetricType.COUNTER,
        ["content_type", "user_type"]
    )
    
    monitoring.metrics_collector.create_custom_metric(
        "ainflue_ai_processing_time",
        "AI processing time for content",
        MetricType.HISTOGRAM,
        ["model_type", "content_type"]
    )
    
    monitoring.metrics_collector.create_custom_metric(
        "ainflue_active_creators",
        "Number of active creators",
        MetricType.GAUGE,
        ["platform"]
    )
    
    return monitoring


if __name__ == "__main__":
    async def main():
        monitoring = await setup_ainflue_monitoring()
        
        # Simulate some monitoring data
        for i in range(10):
            # Simulate HTTP requests
            await monitoring.record_http_request(
                "POST", "/api/content/upload", 200, 250.0, "content-service"
            )
            
            await monitoring.record_http_request(
                "GET", "/api/ai/inference", 200, 800.0, "ai-service"
            )
            
            # Simulate business metrics
            await monitoring.record_business_metric(
                "ainflue_content_uploads", 1.0, "content-service",
                {"content_type": "video", "user_type": "creator"}
            )
            
            await asyncio.sleep(1)
        
        # Get dashboard data
        dashboard = await monitoring.get_monitoring_dashboard()
        print(json.dumps(dashboard, indent=2, default=str))
        
        # Export configuration
        config_yaml = await monitoring.export_monitoring_config()
        print("Monitoring Configuration:")
        print(config_yaml)
        
        # Keep running for demonstration
        try:
            while True:
                await asyncio.sleep(30)
                dashboard = await monitoring.get_monitoring_dashboard()
                print(f"Health: CPU {dashboard['system_health']['cpu_usage']:.1f}%, "
                      f"Memory {dashboard['system_health']['memory_usage']:.1f}%, "
                      f"Active Alerts: {dashboard['alerts']['active_count']}")
        except KeyboardInterrupt:
            await monitoring.shutdown()
    
    asyncio.run(main())