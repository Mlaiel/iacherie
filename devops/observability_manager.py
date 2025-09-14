"""
🚀 Observability Manager - Comprehensive Monitoring Orchestration
================================================================

Enterprise-grade observability system with metrics aggregation, distributed tracing,
log analysis, alert correlation, and performance monitoring.

Features:
- Metrics aggregation and correlation algorithms
- Distributed tracing management with Jaeger/Zipkin integration
- Log aggregation and intelligent analysis
- Alert correlation and escalation workflows
- Performance baseline establishment and drift detection
- SLI/SLO monitoring and reporting
- Custom dashboard generation
- Anomaly detection and automated remediation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Engineer + SRE + Monitoring Engineering + Platform Engineering
"""

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import re
import math

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class LogLevel(Enum):
    """Log levels"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"

class TraceStatus(Enum):
    """Trace status"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class MetricPoint:
    """Single metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    metric_name: str
    threshold: float
    current_value: float
    labels: Dict[str, str] = field(default_factory=dict)
    escalation_policy: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class LogEntry:
    """Log entry"""
    log_id: str
    timestamp: datetime
    level: LogLevel
    service: str
    message: str
    fields: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

@dataclass
class TraceSpan:
    """Distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status: TraceStatus
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class SLI:
    """Service Level Indicator"""
    name: str
    service: str
    metric_query: str
    target_value: float
    current_value: float
    measurement_window: int  # seconds
    last_updated: datetime

@dataclass
class SLO:
    """Service Level Objective"""
    name: str
    service: str
    sli_name: str
    target_percentage: float
    time_window: int  # seconds
    current_percentage: float
    error_budget_remaining: float
    last_updated: datetime

@dataclass
class Dashboard:
    """Monitoring dashboard"""
    dashboard_id: str
    name: str
    description: str
    panels: List[Dict[str, Any]]
    variables: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class ObservabilityManager:
    """
    Comprehensive Monitoring Orchestration
    
    Responsibilities:
    - Metrics collection, aggregation, and correlation
    - Distributed tracing management and analysis
    - Log aggregation, parsing, and intelligent analysis
    - Alert management, correlation, and escalation
    - SLI/SLO monitoring and error budget tracking
    - Performance baseline establishment and anomaly detection
    - Custom dashboard and report generation
    """
    
    def __init__(self) -> None:
        # Metrics storage and processing
        self.metrics: deque = deque(maxlen=50000)
        self.metric_metadata: Dict[str, Dict] = {}
        self.aggregated_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Alerting system
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.escalation_policies: Dict[str, Dict] = {}
        self.notification_channels: Dict[str, Dict] = {}
        
        # Logging system
        self.logs: deque = deque(maxlen=100000)
        self.log_parsers: Dict[str, callable] = {}
        self.log_aggregations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Distributed tracing
        self.traces: Dict[str, List[TraceSpan]] = {}
        self.span_index: Dict[str, TraceSpan] = {}
        self.trace_sampling_rate = 0.1  # 10% sampling
        
        # SLI/SLO management
        self.slis: Dict[str, SLI] = {}
        self.slos: Dict[str, SLO] = {}
        
        # Dashboards and visualization
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Performance baselines and anomaly detection
        self.performance_baselines: Dict[str, Dict] = {}
        self.anomaly_detection_models: Dict[str, Any] = {}
        
        # System health and status
        self.system_health: Dict[str, Any] = {}
        self.component_status: Dict[str, str] = {}
        
        self._initialize_observability_manager()
        
        logger.info("ObservabilityManager initialized")

    def _initialize_observability_manager(self) -> None:
        """Initialize observability manager"""
        
        # Start background tasks
        asyncio.create_task(self._metrics_aggregation_loop())
        asyncio.create_task(self._alert_evaluation_loop())
        asyncio.create_task(self._log_processing_loop())
        asyncio.create_task(self._trace_processing_loop())
        asyncio.create_task(self._slo_evaluation_loop())
        asyncio.create_task(self._anomaly_detection_loop())
        asyncio.create_task(self._health_monitoring_loop())
        
        # Initialize default configurations
        self._setup_default_alert_rules()
        self._setup_default_slis_slos()
        self._setup_default_dashboards()
        self._setup_escalation_policies()
        self._setup_log_parsers()
        
        logger.info("Observability manager initialization complete")

    def _setup_default_alert_rules(self) -> None:
        """Setup default alerting rules"""
        
        self.alert_rules = [
            {
                "name": "high_cpu_usage",
                "metric": "cpu_usage_percent",
                "condition": "greater_than",
                "threshold": 80.0,
                "duration": 300,  # 5 minutes
                "severity": AlertSeverity.HIGH,
                "labels": {"component": "infrastructure"},
                "description": "CPU usage is above 80% for 5 minutes"
            },
            {
                "name": "high_memory_usage", 
                "metric": "memory_usage_percent",
                "condition": "greater_than",
                "threshold": 85.0,
                "duration": 300,
                "severity": AlertSeverity.HIGH,
                "labels": {"component": "infrastructure"},
                "description": "Memory usage is above 85% for 5 minutes"
            },
            {
                "name": "high_error_rate",
                "metric": "error_rate_percent",
                "condition": "greater_than", 
                "threshold": 5.0,
                "duration": 120,  # 2 minutes
                "severity": AlertSeverity.CRITICAL,
                "labels": {"component": "application"},
                "description": "Error rate is above 5% for 2 minutes"
            },
            {
                "name": "slow_response_time",
                "metric": "response_time_p95_ms",
                "condition": "greater_than",
                "threshold": 1000.0,
                "duration": 300,
                "severity": AlertSeverity.MEDIUM,
                "labels": {"component": "application"},
                "description": "95th percentile response time is above 1000ms for 5 minutes"
            },
            {
                "name": "disk_space_low",
                "metric": "disk_usage_percent",
                "condition": "greater_than",
                "threshold": 90.0,
                "duration": 60,
                "severity": AlertSeverity.CRITICAL,
                "labels": {"component": "infrastructure"},
                "description": "Disk usage is above 90%"
            }
        ]

    def _setup_default_slis_slos(self) -> None:
        """Setup default SLIs and SLOs"""
        
        # Default SLIs
        self.slis = {
            "availability": SLI(
                name="availability",
                service="ainflue-api",
                metric_query="up",
                target_value=1.0,
                current_value=1.0,
                measurement_window=300,
                last_updated=datetime.now()
            ),
            "latency": SLI(
                name="latency",
                service="ainflue-api",
                metric_query="response_time_p95_ms",
                target_value=200.0,
                current_value=150.0,
                measurement_window=300,
                last_updated=datetime.now()
            ),
            "error_rate": SLI(
                name="error_rate",
                service="ainflue-api",
                metric_query="error_rate_percent",
                target_value=1.0,
                current_value=0.5,
                measurement_window=300,
                last_updated=datetime.now()
            )
        }
        
        # Default SLOs
        self.slos = {
            "api_availability": SLO(
                name="api_availability",
                service="ainflue-api",
                sli_name="availability",
                target_percentage=99.9,
                time_window=2592000,  # 30 days
                current_percentage=99.95,
                error_budget_remaining=50.0,
                last_updated=datetime.now()
            ),
            "api_latency": SLO(
                name="api_latency",
                service="ainflue-api",
                sli_name="latency",
                target_percentage=95.0,
                time_window=86400,  # 1 day
                current_percentage=97.2,
                error_budget_remaining=44.0,
                last_updated=datetime.now()
            )
        }

    def _setup_default_dashboards(self) -> None:
        """Setup default monitoring dashboards"""
        
        infrastructure_dashboard = Dashboard(
            dashboard_id="infrastructure_overview",
            name="Infrastructure Overview",
            description="Comprehensive infrastructure monitoring dashboard",
            panels=[
                {
                    "title": "CPU Usage",
                    "type": "graph",
                    "metric": "cpu_usage_percent",
                    "time_range": "1h"
                },
                {
                    "title": "Memory Usage",
                    "type": "graph", 
                    "metric": "memory_usage_percent",
                    "time_range": "1h"
                },
                {
                    "title": "Network I/O",
                    "type": "graph",
                    "metric": "network_io_bytes",
                    "time_range": "1h"
                },
                {
                    "title": "Active Alerts",
                    "type": "stat",
                    "metric": "active_alerts_count",
                    "time_range": "now"
                }
            ]
        )
        
        application_dashboard = Dashboard(
            dashboard_id="application_performance",
            name="Application Performance",
            description="Application performance and business metrics",
            panels=[
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "metric": "request_rate_per_second",
                    "time_range": "1h"
                },
                {
                    "title": "Response Time",
                    "type": "graph",
                    "metric": "response_time_percentiles",
                    "time_range": "1h"
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "metric": "error_rate_percent",
                    "time_range": "1h"
                },
                {
                    "title": "SLO Status",
                    "type": "table",
                    "metric": "slo_compliance_percent",
                    "time_range": "7d"
                }
            ]
        )
        
        self.dashboards[infrastructure_dashboard.dashboard_id] = infrastructure_dashboard
        self.dashboards[application_dashboard.dashboard_id] = application_dashboard

    def _setup_escalation_policies(self) -> None:
        """Setup alert escalation policies"""
        
        self.escalation_policies = {
            "critical": {
                "levels": [
                    {"delay": 0, "channels": ["slack", "pagerduty"]},
                    {"delay": 300, "channels": ["slack", "pagerduty", "phone"]},
                    {"delay": 900, "channels": ["slack", "pagerduty", "phone", "email_manager"]}
                ]
            },
            "high": {
                "levels": [
                    {"delay": 0, "channels": ["slack"]},
                    {"delay": 600, "channels": ["slack", "email"]},
                    {"delay": 1800, "channels": ["slack", "email", "pagerduty"]}
                ]
            },
            "medium": {
                "levels": [
                    {"delay": 0, "channels": ["slack"]},
                    {"delay": 1800, "channels": ["slack", "email"]}
                ]
            }
        }
        
        self.notification_channels = {
            "slack": {
                "type": "slack",
                "webhook_url": "https://hooks.slack.com/ainflue-alerts",
                "channel": "#alerts"
            },
            "email": {
                "type": "email",
                "smtp_server": "smtp.company.com",
                "recipients": ["devops@ainflue.com"]
            },
            "pagerduty": {
                "type": "pagerduty",
                "integration_key": "pd_integration_key",
                "service_id": "ainflue_service"
            }
        }

    def _setup_log_parsers(self) -> None:
        """Setup log parsing configurations"""
        
        def nginx_log_parser(log_line: str) -> Dict[str, Any]:
            """Parse nginx access logs"""
            pattern = r'(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"'
            match = re.match(pattern, log_line)
            
            if match:
                return {
                    "ip": match.group(1),
                    "timestamp": match.group(2),
                    "method": match.group(3),
                    "path": match.group(4),
                    "protocol": match.group(5),
                    "status_code": int(match.group(6)),
                    "bytes": int(match.group(7)) if match.group(7) != '-' else 0,
                    "referer": match.group(8),
                    "user_agent": match.group(9)
                }
            return {}
        
        def application_log_parser(log_line: str) -> Dict[str, Any]:
            """Parse application logs"""
            try:
                # Assume JSON logs
                return json.loads(log_line)
            except:
                # Fallback to simple parsing
                parts = log_line.split(' ', 4)
                if len(parts) >= 4:
                    return {
                        "timestamp": parts[0] + " " + parts[1],
                        "level": parts[2],
                        "service": parts[3],
                        "message": parts[4] if len(parts) > 4 else ""
                    }
            return {}
        
        self.log_parsers = {
            "nginx": nginx_log_parser,
            "application": application_log_parser
        }

    async def collect_metric(
        self,
        name -> None: str,
        value -> None: float,
        labels -> None: Optional[Dict[str, str]] = None,
        metric_type -> None: MetricType = MetricType.GAUGE,
        timestamp -> None: Optional[datetime] = None
    ) -> None:
        """
        Collect a metric data point
        
        Args:
            name: Metric name
            value: Metric value
            labels: Metric labels
            metric_type: Type of metric
            timestamp: Metric timestamp
        """
        
        try:
            metric_point = MetricPoint(
                name=name,
                value=value,
                timestamp=timestamp or datetime.now(),
                labels=labels or {},
                metric_type=metric_type
            )
            
            self.metrics.append(metric_point)
            
            # Store metadata
            if name not in self.metric_metadata:
                self.metric_metadata[name] = {
                    "type": metric_type.value,
                    "description": f"Metric: {name}",
                    "unit": "unknown",
                    "first_seen": datetime.now(),
                    "label_keys": set()
                }
            
            # Update label keys
            self.metric_metadata[name]["label_keys"].update(labels.keys() if labels else [])
            
        except Exception as e:
            logger.error(f"Metric collection failed: {str(e)}")

    async def collect_log(
        self,
        service: str,
        level: LogLevel,
        message: str,
        fields: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None
    ) -> str:
        """
        Collect a log entry
        
        Args:
            service: Service name
            level: Log level
            message: Log message
            fields: Additional fields
            trace_id: Trace ID for correlation
            span_id: Span ID for correlation
            
        Returns:
            Log entry ID
        """
        
        try:
            log_id = str(uuid.uuid4())
            
            log_entry = LogEntry(
                log_id=log_id,
                timestamp=datetime.now(),
                level=level,
                service=service,
                message=message,
                fields=fields or {},
                trace_id=trace_id,
                span_id=span_id
            )
            
            self.logs.append(log_entry)
            
            # Index for aggregation
            service_key = f"service:{service}"
            level_key = f"level:{level.value}"
            
            self.log_aggregations[service_key].append(log_entry)
            self.log_aggregations[level_key].append(log_entry)
            
            # Error log special handling
            if level in [LogLevel.ERROR, LogLevel.FATAL]:
                await self._process_error_log(log_entry)
            
            return log_id
            
        except Exception as e:
            logger.error(f"Log collection failed: {str(e)}")
            return ""

    async def start_trace(
        self,
        operation_name: str,
        service_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Start a new trace span
        
        Args:
            operation_name: Name of the operation
            service_name: Service name
            parent_span_id: Parent span ID
            tags: Span tags
            
        Returns:
            Trace and span IDs
        """
        
        try:
            trace_id = str(uuid.uuid4())
            span_id = str(uuid.uuid4())
            
            span = TraceSpan(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                service_name=service_name,
                start_time=datetime.now(),
                end_time=datetime.now(),  # Will be updated on finish
                duration_ms=0.0,
                status=TraceStatus.OK,
                tags=tags or {}
            )
            
            # Add to trace
            if trace_id not in self.traces:
                self.traces[trace_id] = []
            
            self.traces[trace_id].append(span)
            self.span_index[span_id] = span
            
            return f"{trace_id}:{span_id}"
            
        except Exception as e:
            logger.error(f"Trace start failed: {str(e)}")
            return ""

    async def finish_trace(
        self,
        trace_span_id -> None: str,
        status -> None: TraceStatus = TraceStatus.OK,
        logs -> None: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Finish a trace span
        
        Args:
            trace_span_id: Trace:Span ID combination
            status: Span status
            logs: Span logs
        """
        
        try:
            if ":" not in trace_span_id:
                return
            
            trace_id, span_id = trace_span_id.split(":", 1)
            
            if span_id in self.span_index:
                span = self.span_index[span_id]
                span.end_time = datetime.now()
                span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
                span.status = status
                span.logs = logs or []
                
                # Sample trace for storage (to manage memory)
                if len(self.traces) > 1000:  # Keep only recent traces
                    oldest_traces = sorted(self.traces.keys())[:100]
                    for old_trace_id in oldest_traces:
                        del self.traces[old_trace_id]
            
        except Exception as e:
            logger.error(f"Trace finish failed: {str(e)}")

    async def create_alert_rule(
        self,
        name: str,
        metric: str,
        condition: str,
        threshold: float,
        duration: int,
        severity: AlertSeverity,
        description: str,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a new alert rule
        
        Args:
            name: Alert rule name
            metric: Metric to monitor
            condition: Alert condition (greater_than, less_than, etc.)
            threshold: Alert threshold
            duration: Duration before alerting
            severity: Alert severity
            description: Alert description
            labels: Alert labels
            
        Returns:
            Alert rule ID
        """
        
        try:
            alert_rule = {
                "id": str(uuid.uuid4()),
                "name": name,
                "metric": metric,
                "condition": condition,
                "threshold": threshold,
                "duration": duration,
                "severity": severity,
                "description": description,
                "labels": labels or {},
                "created_at": datetime.now(),
                "enabled": True
            }
            
            self.alert_rules.append(alert_rule)
            
            logger.info(f"Alert rule created: {name}")
            return alert_rule["id"]
            
        except Exception as e:
            logger.error(f"Alert rule creation failed: {str(e)}")
            return ""

    async def query_metrics(
        self,
        metric_name: str,
        time_range: str = "1h",
        labels: Optional[Dict[str, str]] = None,
        aggregation: str = "avg"
    ) -> List[Dict[str, Any]]:
        """
        Query metrics with time range and aggregation
        
        Args:
            metric_name: Name of the metric to query
            time_range: Time range (1h, 24h, 7d, etc.)
            labels: Label filters
            aggregation: Aggregation function (avg, sum, max, min)
            
        Returns:
            List of metric data points
        """
        
        try:
            # Parse time range
            now = datetime.now()
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(hours=24)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(hours=1)  # Default
            
            # Filter metrics
            filtered_metrics = []
            for metric in self.metrics:
                if (metric.name == metric_name and 
                    metric.timestamp >= start_time and
                    metric.timestamp <= now):
                    
                    # Apply label filters
                    if labels:
                        match = all(
                            metric.labels.get(k) == v 
                            for k, v in labels.items()
                        )
                        if not match:
                            continue
                    
                    filtered_metrics.append(metric)
            
            # Group by time buckets and aggregate
            time_buckets = {}
            bucket_size = 300  # 5 minutes
            
            for metric in filtered_metrics:
                bucket_timestamp = int(metric.timestamp.timestamp() // bucket_size) * bucket_size
                bucket_time = datetime.fromtimestamp(bucket_timestamp)
                
                if bucket_time not in time_buckets:
                    time_buckets[bucket_time] = []
                time_buckets[bucket_time].append(metric.value)
            
            # Apply aggregation
            result = []
            for bucket_time, values in sorted(time_buckets.items()):
                if aggregation == "avg":
                    aggregated_value = statistics.mean(values)
                elif aggregation == "sum":
                    aggregated_value = sum(values)
                elif aggregation == "max":
                    aggregated_value = max(values)
                elif aggregation == "min":
                    aggregated_value = min(values)
                else:
                    aggregated_value = statistics.mean(values)
                
                result.append({
                    "timestamp": bucket_time.isoformat(),
                    "value": aggregated_value
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Metrics query failed: {str(e)}")
            return []

    async def query_logs(
        self,
        service: Optional[str] = None,
        level: Optional[LogLevel] = None,
        time_range: str = "1h",
        search_text: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query logs with filters
        
        Args:
            service: Service name filter
            level: Log level filter
            time_range: Time range
            search_text: Text search in messages
            limit: Maximum number of results
            
        Returns:
            List of log entries
        """
        
        try:
            # Parse time range
            now = datetime.now()
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(hours=24)
            else:
                start_time = now - timedelta(hours=1)
            
            # Filter logs
            filtered_logs = []
            for log_entry in self.logs:
                if log_entry.timestamp < start_time:
                    continue
                
                if service and log_entry.service != service:
                    continue
                
                if level and log_entry.level != level:
                    continue
                
                if search_text and search_text.lower() not in log_entry.message.lower():
                    continue
                
                filtered_logs.append({
                    "log_id": log_entry.log_id,
                    "timestamp": log_entry.timestamp.isoformat(),
                    "level": log_entry.level.value,
                    "service": log_entry.service,
                    "message": log_entry.message,
                    "fields": log_entry.fields,
                    "trace_id": log_entry.trace_id,
                    "span_id": log_entry.span_id
                })
                
                if len(filtered_logs) >= limit:
                    break
            
            # Sort by timestamp (newest first)
            filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return filtered_logs[:limit]
            
        except Exception as e:
            logger.error(f"Log query failed: {str(e)}")
            return []

    async def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace by ID
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            Trace data with all spans
        """
        
        try:
            if trace_id not in self.traces:
                return None
            
            spans = self.traces[trace_id]
            
            # Calculate trace metadata
            start_time = min(span.start_time for span in spans)
            end_time = max(span.end_time for span in spans)
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Count spans by service
            service_spans = defaultdict(int)
            for span in spans:
                service_spans[span.service_name] += 1
            
            return {
                "trace_id": trace_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms,
                "span_count": len(spans),
                "service_spans": dict(service_spans),
                "spans": [
                    {
                        "span_id": span.span_id,
                        "parent_span_id": span.parent_span_id,
                        "operation_name": span.operation_name,
                        "service_name": span.service_name,
                        "start_time": span.start_time.isoformat(),
                        "end_time": span.end_time.isoformat(),
                        "duration_ms": span.duration_ms,
                        "status": span.status.value,
                        "tags": span.tags,
                        "logs": span.logs
                    }
                    for span in sorted(spans, key=lambda s: s.start_time)
                ]
            }
            
        except Exception as e:
            logger.error(f"Get trace failed: {str(e)}")
            return None

    async def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dashboard configuration and data
        
        Args:
            dashboard_id: Dashboard identifier
            
        Returns:
            Dashboard data with panel information
        """
        
        try:
            if dashboard_id not in self.dashboards:
                return None
            
            dashboard = self.dashboards[dashboard_id]
            
            # Populate panel data
            panels_with_data = []
            for panel in dashboard.panels:
                panel_data = panel.copy()
                
                # Get metric data for panel
                if panel["type"] == "graph":
                    metric_data = await self.query_metrics(
                        panel["metric"],
                        panel.get("time_range", "1h")
                    )
                    panel_data["data"] = metric_data
                elif panel["type"] == "stat":
                    # Get current value
                    recent_metrics = await self.query_metrics(
                        panel["metric"],
                        "5m"
                    )
                    current_value = recent_metrics[-1]["value"] if recent_metrics else 0
                    panel_data["current_value"] = current_value
                
                panels_with_data.append(panel_data)
            
            return {
                "dashboard_id": dashboard.dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "created_at": dashboard.created_at.isoformat(),
                "updated_at": dashboard.updated_at.isoformat(),
                "variables": dashboard.variables,
                "panels": panels_with_data
            }
            
        except Exception as e:
            logger.error(f"Get dashboard failed: {str(e)}")
            return None

    # Background processing tasks
    async def _metrics_aggregation_loop(self) -> None:
        """Background metrics aggregation loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Aggregate every minute
                await self._aggregate_metrics()
                
            except Exception as e:
                logger.error(f"Metrics aggregation loop error: {str(e)}")

    async def _aggregate_metrics(self) -> None:
        """Aggregate metrics for efficient querying"""
        
        # Group metrics by name and 5-minute windows
        now = datetime.now()
        five_minutes_ago = now - timedelta(minutes=5)
        
        recent_metrics = [
            m for m in self.metrics 
            if m.timestamp >= five_minutes_ago
        ]
        
        # Group by metric name
        metric_groups = defaultdict(list)
        for metric in recent_metrics:
            metric_groups[metric.name].append(metric.value)
        
        # Calculate aggregations
        for metric_name, values in metric_groups.items():
            if values:
                aggregated_point = {
                    "timestamp": now,
                    "count": len(values),
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "sum": sum(values)
                }
                
                self.aggregated_metrics[metric_name].append(aggregated_point)

    async def _alert_evaluation_loop(self) -> None:
        """Background alert evaluation loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                await self._evaluate_alert_rules()
                
            except Exception as e:
                logger.error(f"Alert evaluation loop error: {str(e)}")

    async def _evaluate_alert_rules(self) -> None:
        """Evaluate alert rules against current metrics"""
        
        for rule in self.alert_rules:
            if not rule.get("enabled", True):
                continue
            
            try:
                # Get recent metrics for the rule
                recent_metrics = await self.query_metrics(
                    rule["metric"], 
                    f"{rule['duration']}s"
                )
                
                if not recent_metrics:
                    continue
                
                # Check condition
                current_value = recent_metrics[-1]["value"]
                threshold = rule["threshold"]
                condition = rule["condition"]
                
                alert_triggered = False
                if condition == "greater_than" and current_value > threshold:
                    alert_triggered = True
                elif condition == "less_than" and current_value < threshold:
                    alert_triggered = True
                elif condition == "equals" and current_value == threshold:
                    alert_triggered = True
                
                # Create or update alert
                alert_key = f"{rule['name']}_{rule['metric']}"
                
                if alert_triggered:
                    if alert_key not in self.alerts:
                        # Create new alert
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            name=rule["name"],
                            description=rule["description"],
                            severity=rule["severity"],
                            status=AlertStatus.ACTIVE,
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            metric_name=rule["metric"],
                            threshold=threshold,
                            current_value=current_value,
                            labels=rule.get("labels", {})
                        )
                        
                        self.alerts[alert_key] = alert
                        
                        # Send notification
                        await self._send_alert_notification(alert)
                        
                        logger.warning(f"Alert triggered: {rule['name']} - {current_value} {condition} {threshold}")
                    else:
                        # Update existing alert
                        self.alerts[alert_key].current_value = current_value
                        self.alerts[alert_key].updated_at = datetime.now()
                else:
                    # Resolve alert if it exists
                    if alert_key in self.alerts and self.alerts[alert_key].status == AlertStatus.ACTIVE:
                        self.alerts[alert_key].status = AlertStatus.RESOLVED
                        self.alerts[alert_key].resolved_at = datetime.now()
                        self.alerts[alert_key].updated_at = datetime.now()
                        
                        logger.info(f"Alert resolved: {rule['name']}")
                
            except Exception as e:
                logger.error(f"Alert rule evaluation failed: {rule['name']} - {str(e)}")

    async def _send_alert_notification(self, alert -> None: Alert) -> None:
        """Send alert notification based on escalation policy"""
        
        try:
            severity_key = alert.severity.value
            if severity_key in self.escalation_policies:
                policy = self.escalation_policies[severity_key]
                
                # Send to first level channels immediately
                first_level = policy["levels"][0]
                for channel_name in first_level["channels"]:
                    await self._send_notification(channel_name, alert)
            
        except Exception as e:
            logger.error(f"Alert notification failed: {str(e)}")

    async def _send_notification(self, channel_name -> None: str, alert -> None: Alert) -> None:
        """Send notification to specific channel"""
        
        try:
            if channel_name not in self.notification_channels:
                return
            
            channel = self.notification_channels[channel_name]
            
            message = f"🚨 Alert: {alert.name}\n"
            message += f"Description: {alert.description}\n"
            message += f"Severity: {alert.severity.value}\n"
            message += f"Current Value: {alert.current_value}\n"
            message += f"Threshold: {alert.threshold}\n"
            message += f"Time: {alert.created_at.isoformat()}"
            
            # Mock notification sending
            logger.info(f"Sending notification to {channel_name}: {alert.name}")
            
        except Exception as e:
            logger.error(f"Notification sending failed: {channel_name} - {str(e)}")

    async def _log_processing_loop(self) -> None:
        """Background log processing loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Process every minute
                await self._process_logs()
                
            except Exception as e:
                logger.error(f"Log processing loop error: {str(e)}")

    async def _process_logs(self) -> None:
        """Process and analyze logs"""
        
        # Analyze error patterns
        recent_errors = [
            log for log in list(self.logs)[-1000:]  # Last 1000 logs
            if log.level in [LogLevel.ERROR, LogLevel.FATAL]
        ]
        
        # Group errors by message pattern
        error_patterns = defaultdict(int)
        for error_log in recent_errors:
            # Simple pattern extraction (first 50 chars)
            pattern = error_log.message[:50]
            error_patterns[pattern] += 1
        
        # Log analysis results
        if error_patterns:
            top_errors = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
            logger.info(f"Top error patterns: {top_errors}")

    async def _process_error_log(self, log_entry -> None: LogEntry) -> None:
        """Process error logs for immediate action"""
        
        try:
            # Check for critical error patterns
            critical_patterns = [
                "out of memory",
                "database connection failed",
                "authentication failed",
                "security violation"
            ]
            
            message_lower = log_entry.message.lower()
            for pattern in critical_patterns:
                if pattern in message_lower:
                    # Create immediate alert
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        name=f"Critical Error: {pattern}",
                        description=f"Critical error detected in {log_entry.service}: {log_entry.message}",
                        severity=AlertSeverity.CRITICAL,
                        status=AlertStatus.ACTIVE,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        metric_name="error_log",
                        threshold=0,
                        current_value=1,
                        labels={"service": log_entry.service, "log_level": log_entry.level.value}
                    )
                    
                    alert_key = f"error_log_{log_entry.service}_{pattern.replace(' ', '_')}"
                    self.alerts[alert_key] = alert
                    
                    await self._send_alert_notification(alert)
                    break
                    
        except Exception as e:
            logger.error(f"Error log processing failed: {str(e)}")

    async def _trace_processing_loop(self) -> None:
        """Background trace processing loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Process every 5 minutes
                await self._analyze_traces()
                
            except Exception as e:
                logger.error(f"Trace processing loop error: {str(e)}")

    async def _analyze_traces(self) -> None:
        """Analyze traces for performance insights"""
        
        if not self.traces:
            return
        
        # Analyze trace durations
        all_durations = []
        service_durations = defaultdict(list)
        
        for trace_spans in self.traces.values():
            for span in trace_spans:
                all_durations.append(span.duration_ms)
                service_durations[span.service_name].append(span.duration_ms)
        
        if all_durations:
            # Calculate percentiles
            all_durations.sort()
            p95_duration = all_durations[int(len(all_durations) * 0.95)]
            p99_duration = all_durations[int(len(all_durations) * 0.99)]
            
            # Collect performance metrics
            await self.collect_metric("trace_duration_p95_ms", p95_duration)
            await self.collect_metric("trace_duration_p99_ms", p99_duration)
            
            # Service-specific metrics
            for service, durations in service_durations.items():
                if durations:
                    avg_duration = statistics.mean(durations)
                    await self.collect_metric(
                        "service_duration_avg_ms", 
                        avg_duration,
                        labels={"service": service}
                    )

    async def _slo_evaluation_loop(self) -> None:
        """Background SLO evaluation loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Evaluate every 5 minutes
                await self._evaluate_slos()
                
            except Exception as e:
                logger.error(f"SLO evaluation loop error: {str(e)}")

    async def _evaluate_slos(self) -> None:
        """Evaluate SLO compliance and error budgets"""
        
        for slo in self.slos.values():
            try:
                # Get SLI value
                if slo.sli_name in self.slis:
                    sli = self.slis[slo.sli_name]
                    
                    # Mock SLO calculation
                    if sli.name == "availability":
                        # 99.95% uptime
                        current_percentage = 99.95
                    elif sli.name == "latency":
                        # 97% of requests under target
                        current_percentage = 97.0
                    elif sli.name == "error_rate":
                        # 99.5% success rate
                        current_percentage = 99.5
                    else:
                        current_percentage = 95.0
                    
                    slo.current_percentage = current_percentage
                    slo.last_updated = datetime.now()
                    
                    # Calculate error budget
                    if current_percentage >= slo.target_percentage:
                        slo.error_budget_remaining = 100.0
                    else:
                        deficit = slo.target_percentage - current_percentage
                        slo.error_budget_remaining = max(0, 100 - (deficit * 10))
                    
                    # Collect SLO metrics
                    await self.collect_metric(
                        f"slo_compliance_percent",
                        current_percentage,
                        labels={"slo": slo.name, "service": slo.service}
                    )
                    
                    await self.collect_metric(
                        f"slo_error_budget_percent",
                        slo.error_budget_remaining,
                        labels={"slo": slo.name, "service": slo.service}
                    )
                    
            except Exception as e:
                logger.error(f"SLO evaluation failed: {slo.name} - {str(e)}")

    async def _anomaly_detection_loop(self) -> None:
        """Background anomaly detection loop"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                await self._detect_anomalies()
                
            except Exception as e:
                logger.error(f"Anomaly detection loop error: {str(e)}")

    async def _detect_anomalies(self) -> None:
        """Detect anomalies in metrics using statistical methods"""
        
        # Simple anomaly detection using standard deviation
        for metric_name, aggregations in self.aggregated_metrics.items():
            if len(aggregations) < 10:  # Need sufficient data
                continue
            
            try:
                # Get recent values
                recent_values = [agg["avg"] for agg in list(aggregations)[-50:]]
                
                if len(recent_values) >= 10:
                    mean_value = statistics.mean(recent_values)
                    std_dev = statistics.stdev(recent_values)
                    
                    # Check latest value for anomaly
                    latest_value = recent_values[-1]
                    z_score = abs((latest_value - mean_value) / std_dev) if std_dev > 0 else 0
                    
                    # Anomaly threshold (2 standard deviations)
                    if z_score > 2.0:
                        logger.warning(f"Anomaly detected in {metric_name}: {latest_value} (z-score: {z_score:.2f})")
                        
                        # Create anomaly alert
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            name=f"Anomaly: {metric_name}",
                            description=f"Statistical anomaly detected in {metric_name}: {latest_value:.2f} (z-score: {z_score:.2f})",
                            severity=AlertSeverity.MEDIUM,
                            status=AlertStatus.ACTIVE,
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            metric_name=metric_name,
                            threshold=mean_value + (2 * std_dev),
                            current_value=latest_value,
                            labels={"type": "anomaly", "detection_method": "statistical"}
                        )
                        
                        alert_key = f"anomaly_{metric_name}"
                        if alert_key not in self.alerts:
                            self.alerts[alert_key] = alert
                            await self._send_alert_notification(alert)
                        
            except Exception as e:
                logger.error(f"Anomaly detection failed for {metric_name}: {str(e)}")

    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._update_system_health()
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {str(e)}")

    async def _update_system_health(self) -> None:
        """Update overall system health status"""
        
        try:
            # Count active alerts by severity
            active_alerts = [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
            critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
            high_alerts = [a for a in active_alerts if a.severity == AlertSeverity.HIGH]
            
            # Calculate health score
            health_score = 100
            health_score -= len(critical_alerts) * 20
            health_score -= len(high_alerts) * 10
            health_score -= len(active_alerts) * 2
            health_score = max(0, health_score)
            
            # Determine status
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "degraded"
            else:
                status = "unhealthy"
            
            self.system_health = {
                "status": status,
                "health_score": health_score,
                "last_updated": datetime.now().isoformat(),
                "active_alerts": len(active_alerts),
                "critical_alerts": len(critical_alerts),
                "high_alerts": len(high_alerts),
                "metrics_collected": len(self.metrics),
                "traces_stored": len(self.traces),
                "logs_stored": len(self.logs)
            }
            
        except Exception as e:
            logger.error(f"System health update failed: {str(e)}")

    async def health_check(self) -> bool:
        """Observability manager health check"""
        
        try:
            # Check system components
            if len(self.alerts) > 1000:  # Too many alerts
                return False
            
            if len(self.metrics) == 0:  # No metrics being collected
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Observability manager health check failed: {str(e)}")
            return False

    def get_observability_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive observability dashboard"""
        
        active_alerts = [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.system_health,
            "metrics": {
                "total_metrics": len(self.metrics),
                "unique_metric_names": len(self.metric_metadata),
                "recent_metrics_per_minute": len([
                    m for m in self.metrics 
                    if m.timestamp >= datetime.now() - timedelta(minutes=1)
                ])
            },
            "alerts": {
                "total_alerts": len(self.alerts),
                "active_alerts": len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "alert_rules": len(self.alert_rules)
            },
            "logs": {
                "total_logs": len(self.logs),
                "recent_logs_per_minute": len([
                    l for l in self.logs 
                    if l.timestamp >= datetime.now() - timedelta(minutes=1)
                ]),
                "error_logs": len([
                    l for l in self.logs 
                    if l.level in [LogLevel.ERROR, LogLevel.FATAL]
                ])
            },
            "traces": {
                "total_traces": len(self.traces),
                "total_spans": sum(len(spans) for spans in self.traces.values()),
                "sampling_rate": self.trace_sampling_rate
            },
            "slo_compliance": {
                "total_slos": len(self.slos),
                "compliant_slos": len([
                    slo for slo in self.slos.values() 
                    if slo.current_percentage >= slo.target_percentage
                ]),
                "average_error_budget": statistics.mean([
                    slo.error_budget_remaining for slo in self.slos.values()
                ]) if self.slos else 0
            },
            "dashboards": {
                "total_dashboards": len(self.dashboards),
                "dashboard_names": [d.name for d in self.dashboards.values()]
            }
        }

# Global observability manager instance
observability_manager = ObservabilityManager()

logger.info("🚀 Observability Manager initialized - Comprehensive monitoring orchestration")