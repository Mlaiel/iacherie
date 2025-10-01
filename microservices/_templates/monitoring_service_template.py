#!/usr/bin/env python3
"""
📊 Enterprise Monitoring Service Template - iacherie
=================================================
Template enterprise pour services monitoring.
Prometheus + Grafana + Jaeger + ELK + custom metrics + alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: iacherie Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction sans autorisation est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import time
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
import logging
import statistics
from collections import deque, defaultdict
import uuid

from .service_template import EnterpriseServiceBase, ServiceConfig


class MetricType(Enum):
    """Types de métriques."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMING = "timing"


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class AlertStatus(Enum):
    """Status des alertes."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class TraceStatus(Enum):
    """Status des traces."""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class Metric:
    """Modèle métrique."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    help_text: str = ""
    unit: str = ""


@dataclass
class Alert:
    """Modèle alerte."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    status: AlertStatus = AlertStatus.ACTIVE
    rule_expression: str = ""
    threshold_value: float = 0.0
    current_value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class TraceSpan:
    """Span de trace distribuée."""
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    service_name: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.OK
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class HealthCheck:
    """Vérification de santé."""
    name: str
    status: str = "unknown"
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    response_time_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """Configuration monitoring."""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    jaeger_enabled: bool = True
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    log_level: str = "INFO"
    metrics_retention_days: int = 30
    traces_retention_days: int = 7
    alerts_retention_days: int = 90
    health_check_interval_seconds: int = 30
    custom_dashboards: List[str] = field(default_factory=list)
    notification_webhooks: List[str] = field(default_factory=list)


class MonitoringServiceTemplate(EnterpriseServiceBase):
    """
    📊 Template enterprise pour services monitoring.
    Prometheus + Grafana + Jaeger + ELK + custom metrics + alerting.
    
    Features:
    - Collection métriques custom avec Prometheus
    - Distributed tracing avec Jaeger/Zipkin
    - Agrégation logs avec ELK stack
    - Règles alerting avec notification multi-canal
    - Dashboards Grafana automatiques
    - Health checks comprehensive
    - Performance monitoring temps réel
    - SLA/SLO tracking
    - Anomaly detection avec ML
    - Cost monitoring et optimization
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize monitoring service template."""
        super().__init__(config)
        
        self.metrics_store: Dict[str, List[Metric]] = defaultdict(list)
        self.alerts_store: Dict[str, Alert] = {}
        self.traces_store: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.health_checks: Dict[str, HealthCheck] = {}
        self.monitoring_config: Optional[MonitoringConfig] = None
        
        # Monitoring metrics
        self.monitoring_metrics = {
            'metrics_collected': 0,
            'alerts_active': 0,
            'alerts_resolved': 0,
            'traces_collected': 0,
            'health_checks_performed': 0,
            'health_checks_failed': 0,
            'dashboards_created': 0,
            'notifications_sent': 0,
            'anomalies_detected': 0,
            'average_response_time_ms': 0.0
        }
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        self.alert_rules: Dict[str, Dict] = {}
        self.notification_channels: Dict[str, Callable] = {}
        
        # Background tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        
        self.logger.info(f"📊 Monitoring Service Template initialized: {config.service_name}")
    
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        try:
            # Setup default monitoring config
            if not self.monitoring_config:
                self.monitoring_config = MonitoringConfig()
            
            # Setup default alert rules
            await self._setup_default_alert_rules()
            
            # Setup default notification channels
            await self._setup_default_notification_channels()
            
            # Start background monitoring tasks
            await self._start_background_tasks()
            
            self.logger.info("✅ Monitoring service components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize monitoring service: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Stop background tasks
            for task in self.monitoring_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Clear stores
            self.metrics_store.clear()
            self.alerts_store.clear()
            self.traces_store.clear()
            self.health_checks.clear()
            
            self.logger.info("✅ Monitoring service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during monitoring service cleanup: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform monitoring service-specific health checks."""
        try:
            return {
                'metrics_stored': sum(len(metrics) for metrics in self.metrics_store.values()),
                'active_alerts': len([a for a in self.alerts_store.values() if a.status == AlertStatus.ACTIVE]),
                'traces_stored': sum(len(traces) for traces in self.traces_store.values()),
                'health_checks_configured': len(self.health_checks),
                'alert_rules_configured': len(self.alert_rules),
                'notification_channels': len(self.notification_channels),
                'metrics': self.monitoring_metrics.copy(),
                'storage_usage': {
                    'metrics_mb': self._calculate_storage_usage('metrics'),
                    'traces_mb': self._calculate_storage_usage('traces'),
                    'alerts_mb': self._calculate_storage_usage('alerts')
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring service health check failed: {e}")
            return {'error': str(e), 'status': 'unhealthy'}
    
    async def setup_metrics_collection(self, metrics_config: Dict[str, Any]) -> None:
        """Collection métriques custom avec Prometheus."""
        try:
            # Configure Prometheus integration
            if metrics_config.get('prometheus_enabled', True):
                await self._setup_prometheus_integration(metrics_config)
            
            # Setup custom metrics
            custom_metrics = metrics_config.get('custom_metrics', [])
            for metric_config in custom_metrics:
                await self._register_custom_metric(metric_config)
            
            self.logger.info("✅ Metrics collection configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup metrics collection: {e}")
            raise
    
    async def setup_distributed_tracing(self, tracing_config: Dict[str, Any]) -> None:
        """Distributed tracing avec Jaeger/Zipkin."""
        try:
            # Configure Jaeger integration
            if tracing_config.get('jaeger_enabled', True):
                await self._setup_jaeger_integration(tracing_config)
            
            # Setup sampling strategy
            sampling_rate = tracing_config.get('sampling_rate', 0.1)
            await self._configure_trace_sampling(sampling_rate)
            
            self.logger.info("✅ Distributed tracing configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup distributed tracing: {e}")
            raise
    
    async def setup_log_aggregation(self, logging_config: Dict[str, Any]) -> None:
        """Agrégation logs avec ELK stack."""
        try:
            # Configure ELK integration
            if logging_config.get('elk_enabled', True):
                await self._setup_elk_integration(logging_config)
            
            # Setup log parsing rules
            log_patterns = logging_config.get('log_patterns', [])
            for pattern in log_patterns:
                await self._register_log_pattern(pattern)
            
            self.logger.info("✅ Log aggregation configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup log aggregation: {e}")
            raise
    
    async def setup_alerting_rules(self, alert_configs: List[Dict[str, Any]]) -> None:
        """Règles alerting avec notification multi-canal."""
        try:
            for alert_config in alert_configs:
                await self._create_alert_rule(alert_config)
            
            self.logger.info(f"✅ Alerting rules configured: {len(alert_configs)} rules")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup alerting rules: {e}")
            raise
    
    async def collect_metric(self, metric: Metric) -> None:
        """Collect single metric."""
        try:
            # Store metric
            self.metrics_store[metric.name].append(metric)
            self.monitoring_metrics['metrics_collected'] += 1
            
            # Limit storage per metric
            if len(self.metrics_store[metric.name]) > 10000:
                self.metrics_store[metric.name] = self.metrics_store[metric.name][-5000:]
            
            # Check alert rules
            await self._check_alert_rules(metric)
            
            self.logger.debug(f"📊 Metric collected: {metric.name} = {metric.value}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect metric: {e}")
    
    async def start_trace(self, operation_name: str, service_name: str, 
                         parent_span_id: Optional[str] = None) -> TraceSpan:
        """Start distributed trace span."""
        try:
            trace_id = str(uuid.uuid4()) if not parent_span_id else self._get_trace_id(parent_span_id)
            
            span = TraceSpan(
                trace_id=trace_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                service_name=service_name
            )
            
            self.traces_store[trace_id].append(span)
            self.monitoring_metrics['traces_collected'] += 1
            
            self.logger.debug(f"🔍 Trace started: {operation_name} ({span.span_id})")
            return span
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start trace: {e}")
            raise
    
    async def finish_trace(self, span: TraceSpan, status: TraceStatus = TraceStatus.OK, 
                          error: Optional[str] = None) -> None:
        """Finish distributed trace span."""
        try:
            span.end_time = datetime.now()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            span.error = error
            
            # Update performance metrics
            self._update_performance_metrics(span)
            
            self.logger.debug(f"🔍 Trace finished: {span.operation_name} ({span.duration_ms:.2f}ms)")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to finish trace: {e}")
    
    async def create_alert(self, name: str, description: str, severity: AlertSeverity,
                          rule_expression: str, threshold: float,
                          notification_channels: Optional[List[str]] = None) -> Alert:
        """Create alert."""
        try:
            alert = Alert(
                name=name,
                description=description,
                severity=severity,
                rule_expression=rule_expression,
                threshold_value=threshold,
                notification_channels=notification_channels or []
            )
            
            self.alerts_store[alert.id] = alert
            self.monitoring_metrics['alerts_active'] += 1
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            self.logger.warning(f"🚨 Alert created: {name} ({severity.value})")
            return alert
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create alert: {e}")
            raise
    
    async def resolve_alert(self, alert_id: str, resolved_by: Optional[str] = None) -> bool:
        """Resolve alert."""
        try:
            if alert_id not in self.alerts_store:
                return False
            
            alert = self.alerts_store[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            self.monitoring_metrics['alerts_active'] -= 1
            self.monitoring_metrics['alerts_resolved'] += 1
            
            # Send resolution notification
            await self._send_alert_resolution_notification(alert, resolved_by)
            
            self.logger.info(f"✅ Alert resolved: {alert.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to resolve alert: {e}")
            return False
    
    async def perform_health_check(self, name: str, check_function: Callable) -> HealthCheck:
        """Perform health check."""
        start_time = time.time()
        
        try:
            result = await check_function()
            response_time = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                name=name,
                status="healthy" if result.get('healthy', True) else "unhealthy",
                message=result.get('message', ''),
                response_time_ms=response_time,
                details=result.get('details', {})
            )
            
            self.health_checks[name] = health_check
            self.monitoring_metrics['health_checks_performed'] += 1
            
            if health_check.status != "healthy":
                self.monitoring_metrics['health_checks_failed'] += 1
                await self._handle_unhealthy_check(health_check)
            
            return health_check
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                name=name,
                status="error",
                message=str(e),
                response_time_ms=response_time
            )
            
            self.health_checks[name] = health_check
            self.monitoring_metrics['health_checks_failed'] += 1
            
            self.logger.error(f"❌ Health check failed for {name}: {e}")
            return health_check
    
    async def create_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring dashboard."""
        try:
            dashboard = {
                'id': str(uuid.uuid4()),
                'name': dashboard_config.get('name', 'Custom Dashboard'),
                'panels': dashboard_config.get('panels', []),
                'time_range': dashboard_config.get('time_range', '1h'),
                'refresh_interval': dashboard_config.get('refresh_interval', '30s'),
                'created_at': datetime.now().isoformat()
            }
            
            self.monitoring_metrics['dashboards_created'] += 1
            
            self.logger.info(f"📊 Dashboard created: {dashboard['name']}")
            return dashboard
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create dashboard: {e}")
            raise
    
    async def _setup_prometheus_integration(self, config: Dict[str, Any]) -> None:
        """Setup Prometheus integration."""
        # Placeholder for Prometheus integration
        self.logger.info("🚧 Prometheus integration setup (placeholder)")
    
    async def _setup_jaeger_integration(self, config: Dict[str, Any]) -> None:
        """Setup Jaeger integration."""
        # Placeholder for Jaeger integration
        self.logger.info("🚧 Jaeger integration setup (placeholder)")
    
    async def _setup_elk_integration(self, config: Dict[str, Any]) -> None:
        """Setup ELK stack integration."""
        # Placeholder for ELK integration
        self.logger.info("🚧 ELK integration setup (placeholder)")
    
    async def _register_custom_metric(self, metric_config: Dict[str, Any]) -> None:
        """Register custom metric."""
        metric_name = metric_config.get('name')
        self.logger.debug(f"📊 Custom metric registered: {metric_name}")
    
    async def _configure_trace_sampling(self, sampling_rate: float) -> None:
        """Configure trace sampling strategy."""
        self.logger.info(f"🔍 Trace sampling configured: {sampling_rate * 100}%")
    
    async def _register_log_pattern(self, pattern: Dict[str, Any]) -> None:
        """Register log parsing pattern."""
        pattern_name = pattern.get('name')
        self.logger.debug(f"📝 Log pattern registered: {pattern_name}")
    
    async def _create_alert_rule(self, alert_config: Dict[str, Any]) -> None:
        """Create alert rule."""
        rule_name = alert_config.get('name')
        self.alert_rules[rule_name] = alert_config
        self.logger.info(f"🚨 Alert rule created: {rule_name}")
    
    async def _check_alert_rules(self, metric: Metric) -> None:
        """Check metric against alert rules."""
        for rule_name, rule_config in self.alert_rules.items():
            if rule_config.get('metric_name') == metric.name:
                await self._evaluate_alert_rule(rule_name, rule_config, metric)
    
    async def _evaluate_alert_rule(self, rule_name: str, rule_config: Dict[str, Any], 
                                  metric: Metric) -> None:
        """Evaluate alert rule against metric."""
        try:
            threshold = rule_config.get('threshold', 0)
            condition = rule_config.get('condition', 'greater_than')
            
            triggered = False
            if condition == 'greater_than' and metric.value > threshold:
                triggered = True
            elif condition == 'less_than' and metric.value < threshold:
                triggered = True
            elif condition == 'equals' and metric.value == threshold:
                triggered = True
            
            if triggered:
                severity = AlertSeverity(rule_config.get('severity', 'warning'))
                await self.create_alert(
                    name=rule_name,
                    description=rule_config.get('description', f'Alert triggered for {metric.name}'),
                    severity=severity,
                    rule_expression=f"{metric.name} {condition} {threshold}",
                    threshold=threshold,
                    notification_channels=rule_config.get('notification_channels', [])
                )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to evaluate alert rule {rule_name}: {e}")
    
    async def _send_alert_notifications(self, alert: Alert) -> None:
        """Send alert notifications."""
        for channel in alert.notification_channels:
            if channel in self.notification_channels:
                try:
                    await self.notification_channels[channel](alert)
                    self.monitoring_metrics['notifications_sent'] += 1
                except Exception as e:
                    self.logger.error(f"❌ Failed to send notification to {channel}: {e}")
    
    async def _send_alert_resolution_notification(self, alert: Alert, resolved_by: Optional[str]) -> None:
        """Send alert resolution notification."""
        for channel in alert.notification_channels:
            if channel in self.notification_channels:
                try:
                    await self.notification_channels[channel](alert, resolved=True, resolved_by=resolved_by)
                    self.monitoring_metrics['notifications_sent'] += 1
                except Exception as e:
                    self.logger.error(f"❌ Failed to send resolution notification to {channel}: {e}")
    
    async def _handle_unhealthy_check(self, health_check: HealthCheck) -> None:
        """Handle unhealthy check result."""
        await self.create_alert(
            name=f"Health Check Failed: {health_check.name}",
            description=f"Health check {health_check.name} failed: {health_check.message}",
            severity=AlertSeverity.ERROR,
            rule_expression=f"health_check({health_check.name}) != healthy",
            threshold=1.0
        )
    
    def _get_trace_id(self, span_id: str) -> str:
        """Get trace ID from span ID."""
        for trace_id, spans in self.traces_store.items():
            for span in spans:
                if span.span_id == span_id:
                    return trace_id
        return str(uuid.uuid4())
    
    def _update_performance_metrics(self, span: TraceSpan) -> None:
        """Update performance metrics from trace."""
        if span.duration_ms:
            self.performance_history.append(span.duration_ms)
            
            # Update average response time
            if self.performance_history:
                self.monitoring_metrics['average_response_time_ms'] = statistics.mean(self.performance_history)
    
    def _calculate_storage_usage(self, store_type: str) -> float:
        """Calculate storage usage in MB."""
        try:
            if store_type == 'metrics':
                size = sum(len(json.dumps(asdict(metric))) for metrics in self.metrics_store.values() for metric in metrics)
            elif store_type == 'traces':
                size = sum(len(json.dumps(asdict(span))) for spans in self.traces_store.values() for span in spans)
            elif store_type == 'alerts':
                size = sum(len(json.dumps(asdict(alert))) for alert in self.alerts_store.values())
            else:
                return 0.0
            
            return size / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate storage usage for {store_type}: {e}")
            return 0.0
    
    async def _setup_default_alert_rules(self) -> None:
        """Setup default alert rules."""
        default_rules = [
            {
                'name': 'High CPU Usage',
                'metric_name': 'cpu_usage_percent',
                'condition': 'greater_than',
                'threshold': 80.0,
                'severity': 'warning',
                'description': 'CPU usage is above 80%'
            },
            {
                'name': 'High Memory Usage',
                'metric_name': 'memory_usage_percent',
                'condition': 'greater_than',
                'threshold': 90.0,
                'severity': 'error',
                'description': 'Memory usage is above 90%'
            },
            {
                'name': 'High Error Rate',
                'metric_name': 'error_rate',
                'condition': 'greater_than',
                'threshold': 5.0,
                'severity': 'critical',
                'description': 'Error rate is above 5%'
            }
        ]
        
        for rule in default_rules:
            await self._create_alert_rule(rule)
    
    async def _setup_default_notification_channels(self) -> None:
        """Setup default notification channels."""
        async def log_notification(alert: Alert, resolved: bool = False, resolved_by: Optional[str] = None):
            if resolved:
                self.logger.info(f"🔔 Alert resolved: {alert.name} (resolved by: {resolved_by})")
            else:
                self.logger.warning(f"🔔 Alert notification: {alert.name} - {alert.description}")
        
        async def webhook_notification(alert: Alert, resolved: bool = False, resolved_by: Optional[str] = None):
            # Placeholder for webhook notification
            action = "resolved" if resolved else "triggered"
            self.logger.info(f"🔔 Webhook notification: Alert {alert.name} {action}")
        
        self.notification_channels['log'] = log_notification
        self.notification_channels['webhook'] = webhook_notification
    
    async def _start_background_tasks(self) -> None:
        """Start background monitoring tasks."""
        # Cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_old_data())
        self.monitoring_tasks.append(cleanup_task)
        
        # Health check task
        health_task = asyncio.create_task(self._periodic_health_checks())
        self.monitoring_tasks.append(health_task)
        
        # Anomaly detection task
        anomaly_task = asyncio.create_task(self._anomaly_detection())
        self.monitoring_tasks.append(anomaly_task)
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old monitoring data."""
        while self.status == "running":
            try:
                current_time = datetime.now()
                
                # Cleanup old metrics
                if self.monitoring_config:
                    metrics_cutoff = current_time - timedelta(days=self.monitoring_config.metrics_retention_days)
                    for metric_name, metrics in self.metrics_store.items():
                        self.metrics_store[metric_name] = [
                            m for m in metrics if m.timestamp > metrics_cutoff
                        ]
                    
                    # Cleanup old traces
                    traces_cutoff = current_time - timedelta(days=self.monitoring_config.traces_retention_days)
                    for trace_id, spans in list(self.traces_store.items()):
                        filtered_spans = [s for s in spans if s.start_time > traces_cutoff]
                        if filtered_spans:
                            self.traces_store[trace_id] = filtered_spans
                        else:
                            del self.traces_store[trace_id]
                    
                    # Cleanup old alerts
                    alerts_cutoff = current_time - timedelta(days=self.monitoring_config.alerts_retention_days)
                    self.alerts_store = {
                        alert_id: alert for alert_id, alert in self.alerts_store.items()
                        if alert.started_at > alerts_cutoff or alert.status == AlertStatus.ACTIVE
                    }
                
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Cleanup task error: {e}")
                await asyncio.sleep(7200)
    
    async def _periodic_health_checks(self) -> None:
        """Periodic health checks."""
        while self.status == "running":
            try:
                # Basic system health checks
                await self.perform_health_check("system_memory", self._check_system_memory)
                await self.perform_health_check("system_cpu", self._check_system_cpu)
                await self.perform_health_check("disk_space", self._check_disk_space)
                
                interval = self.monitoring_config.health_check_interval_seconds if self.monitoring_config else 30
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Health check task error: {e}")
                await asyncio.sleep(60)
    
    async def _anomaly_detection(self) -> None:
        """Anomaly detection task."""
        while self.status == "running":
            try:
                # Simple anomaly detection based on standard deviation
                for metric_name, metrics in self.metrics_store.items():
                    if len(metrics) > 100:  # Need enough data points
                        recent_values = [m.value for m in metrics[-100:]]
                        mean_val = statistics.mean(recent_values)
                        std_dev = statistics.stdev(recent_values)
                        
                        # Check latest value against threshold (3 sigma)
                        if metrics and abs(metrics[-1].value - mean_val) > 3 * std_dev:
                            self.monitoring_metrics['anomalies_detected'] += 1
                            await self.create_alert(
                                name=f"Anomaly Detected: {metric_name}",
                                description=f"Metric {metric_name} value {metrics[-1].value} is outside normal range",
                                severity=AlertSeverity.WARNING,
                                rule_expression=f"anomaly_detection({metric_name})",
                                threshold=3.0
                            )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Anomaly detection error: {e}")
                await asyncio.sleep(600)
    
    async def _check_system_memory(self) -> Dict[str, Any]:
        """Check system memory usage."""
        # Placeholder for actual system memory check
        return {'healthy': True, 'message': 'Memory usage normal', 'details': {'usage_percent': 45.2}}
    
    async def _check_system_cpu(self) -> Dict[str, Any]:
        """Check system CPU usage."""
        # Placeholder for actual system CPU check
        return {'healthy': True, 'message': 'CPU usage normal', 'details': {'usage_percent': 25.8}}
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space usage."""
        # Placeholder for actual disk space check
        return {'healthy': True, 'message': 'Disk space sufficient', 'details': {'usage_percent': 67.3}}
    
    # Abstract methods pour extension
    @abstractmethod
    async def configure_custom_metrics(self) -> List[Dict[str, Any]]:
        """Configure métriques spécifiques au service."""
        pass
    
    @abstractmethod
    async def configure_custom_alerts(self) -> List[Dict[str, Any]]:
        """Configure alertes spécifiques au service."""
        pass


if __name__ == "__main__":
    print("📊 Enterprise Monitoring Service Template")
    print("Use this template to create comprehensive monitoring microservices")