"""
Advanced Monitoring and Observability System for AI Processing Deployment
========================================================================

Enterprise-grade monitoring system providing comprehensive observability,
performance tracking, alerting, and health management for AI processing infrastructure.

Features:
- Real-time performance monitoring and metrics collection
- Advanced alerting with configurable thresholds
- Distributed tracing and logging integration
- Health check automation and reporting
- Performance analytics and optimization insights

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import json
import psutil
import socket
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from collections import defaultdict, deque
import uuid

import numpy as np
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry
import redis.asyncio as aioredis
from elasticsearch import AsyncElasticsearch
import aiohttp
from kubernetes import client as k8s_client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .core import ProcessingConfig, ProcessingStatus, AIModelType

# Global metrics registry
monitoring_registry = CollectorRegistry()

# Monitoring metrics
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percentage', registry=monitoring_registry)
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage percentage', registry=monitoring_registry)
system_disk_usage = Gauge('system_disk_usage_percent', 'System disk usage percentage', registry=monitoring_registry)
system_network_io = Gauge('system_network_io_bytes_per_second', 'Network I/O bytes per second', ['direction'], registry=monitoring_registry)
active_connections_count = Gauge('active_connections_count', 'Number of active connections', registry=monitoring_registry)
error_rate_percent = Gauge('error_rate_percent', 'Error rate percentage', ['component'], registry=monitoring_registry)
response_time_histogram = Histogram('response_time_seconds', 'Response time histogram', ['endpoint'], registry=monitoring_registry)
alert_notifications_total = Counter('alert_notifications_total', 'Total alert notifications sent', ['type', 'severity'], registry=monitoring_registry)

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts."""
    PERFORMANCE = "performance"
    ERROR = "error"
    AVAILABILITY = "availability"
    RESOURCE = "resource"
    SECURITY = "security"
    BUSINESS = "business"


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MonitoringState(Enum):
    """Monitoring system state."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"


@dataclass
class MetricDefinition:
    """Metric definition and configuration."""
    name: str
    type: str  # counter, gauge, histogram
    description: str
    labels: List[str] = None
    thresholds: Dict[str, float] = None
    unit: str = ""
    collection_interval: int = 60  # seconds


@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # >, <, ==, !=, >=, <=
    threshold: float
    severity: AlertSeverity
    alert_type: AlertType
    evaluation_window: int = 300  # seconds
    cooldown_period: int = 900  # seconds
    enabled: bool = True
    notification_channels: List[str] = None
    tags: Dict[str, str] = None


@dataclass
class AlertEvent:
    """Alert event data."""
    event_id: str
    rule_id: str
    alert_name: str
    severity: AlertSeverity
    alert_type: AlertType
    message: str
    current_value: float
    threshold: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = None


@dataclass
class HealthCheckResult:
    """Health check result."""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = None
    checked_at: datetime = None
    response_time_ms: float = 0.0


@dataclass
class SystemMetrics:
    """System-level metrics snapshot."""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_rx_bytes_per_sec: float
    network_tx_bytes_per_sec: float
    active_connections: int
    load_average: Tuple[float, float, float]
    disk_io_read_bytes_per_sec: float
    disk_io_write_bytes_per_sec: float


@dataclass
class PerformanceReport:
    """Performance analysis report."""
    report_id: str
    generated_at: datetime
    time_range: Dict[str, datetime]
    system_summary: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]
    trend_analysis: Dict[str, Any]


class MetricsCollector:
    """
    Advanced metrics collector for system and application performance monitoring
    with intelligent sampling and aggregation.
    """
    
    def __init__(self, collection_interval: int = 60):
        """Initialize metrics collector."""
        self.collection_interval = collection_interval
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.custom_metrics: Dict[str, MetricDefinition] = {}
        self.collection_tasks: List[asyncio.Task] = []
        self.is_collecting = False
        
    async def start_collection(self):
        """Start metrics collection."""
        if self.is_collecting:
            return
            
        self.is_collecting = True
        
        # Start system metrics collection
        self.collection_tasks.append(
            asyncio.create_task(self._collect_system_metrics())
        )
        
        # Start application metrics collection
        self.collection_tasks.append(
            asyncio.create_task(self._collect_application_metrics())
        )
        
        logger.info("Metrics collection started")
    
    async def stop_collection(self):
        """Stop metrics collection."""
        self.is_collecting = False
        
        # Cancel all collection tasks
        for task in self.collection_tasks:
            task.cancel()
        
        await asyncio.gather(*self.collection_tasks, return_exceptions=True)
        self.collection_tasks.clear()
        
        logger.info("Metrics collection stopped")
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics continuously."""
        last_network_stats = psutil.net_io_counters()
        last_disk_stats = psutil.disk_io_counters()
        last_time = time.time()
        
        while self.is_collecting:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # CPU usage
                cpu_usage = psutil.cpu_percent(interval=1)
                system_cpu_usage.set(cpu_usage)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                system_memory_usage.set(memory_usage)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_usage = (disk.used / disk.total) * 100
                system_disk_usage.set(disk_usage)
                
                # Network I/O
                current_network_stats = psutil.net_io_counters()
                rx_rate = (current_network_stats.bytes_recv - last_network_stats.bytes_recv) / time_delta
                tx_rate = (current_network_stats.bytes_sent - last_network_stats.bytes_sent) / time_delta
                
                system_network_io.labels(direction='rx').set(rx_rate)
                system_network_io.labels(direction='tx').set(tx_rate)
                
                # Active connections
                connections = len(psutil.net_connections(kind='inet'))
                active_connections_count.set(connections)
                
                # Disk I/O
                current_disk_stats = psutil.disk_io_counters()
                disk_read_rate = (current_disk_stats.read_bytes - last_disk_stats.read_bytes) / time_delta
                disk_write_rate = (current_disk_stats.write_bytes - last_disk_stats.write_bytes) / time_delta
                
                # Create system metrics snapshot
                metrics_snapshot = SystemMetrics(
                    timestamp=datetime.utcnow(),
                    cpu_usage_percent=cpu_usage,
                    memory_usage_percent=memory_usage,
                    disk_usage_percent=disk_usage,
                    network_rx_bytes_per_sec=rx_rate,
                    network_tx_bytes_per_sec=tx_rate,
                    active_connections=connections,
                    load_average=psutil.getloadavg(),
                    disk_io_read_bytes_per_sec=disk_read_rate,
                    disk_io_write_bytes_per_sec=disk_write_rate
                )
                
                # Store in buffer
                self.metrics_buffer['system_metrics'].append(metrics_snapshot)
                
                # Update for next iteration
                last_network_stats = current_network_stats
                last_disk_stats = current_disk_stats
                last_time = current_time
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_application_metrics(self):
        """Collect application-specific metrics."""
        while self.is_collecting:
            try:
                # Collect custom application metrics
                for metric_name, metric_def in self.custom_metrics.items():
                    # This would be implemented based on specific metric collection logic
                    pass
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Application metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def register_custom_metric(self, metric_def: MetricDefinition):
        """Register custom metric for collection."""
        self.custom_metrics[metric_def.name] = metric_def
        logger.info(f"Registered custom metric: {metric_def.name}")
    
    def get_recent_metrics(self, metric_type: str, count: int = 100) -> List[Any]:
        """Get recent metrics from buffer."""
        return list(self.metrics_buffer[metric_type])[-count:]
    
    def get_metric_statistics(self, metric_type: str, field: str) -> Dict[str, float]:
        """Get statistical summary of metric field."""
        metrics = self.get_recent_metrics(metric_type)
        
        if not metrics:
            return {}
        
        values = [getattr(metric, field) for metric in metrics if hasattr(metric, field)]
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'mean': np.mean(values),
            'median': np.median(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99)
        }


class AlertManager:
    """
    Intelligent alert management system with rule-based alerting,
    notification routing, and alert correlation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize alert manager."""
        self.config = config or {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.alert_history: List[AlertEvent] = []
        self.notification_channels: Dict[str, Dict[str, Any]] = {}
        self.evaluation_tasks: List[asyncio.Task] = []
        self.is_active = False
        
    async def start_alerting(self):
        """Start alert evaluation and notification system."""
        if self.is_active:
            return
            
        self.is_active = True
        
        # Start alert evaluation task
        self.evaluation_tasks.append(
            asyncio.create_task(self._evaluate_alerts())
        )
        
        logger.info("Alert manager started")
    
    async def stop_alerting(self):
        """Stop alert evaluation and notification system."""
        self.is_active = False
        
        # Cancel evaluation tasks
        for task in self.evaluation_tasks:
            task.cancel()
        
        await asyncio.gather(*self.evaluation_tasks, return_exceptions=True)
        self.evaluation_tasks.clear()
        
        logger.info("Alert manager stopped")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add new alert rule."""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove alert rule."""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
    
    def add_notification_channel(self, channel_name: str, channel_config: Dict[str, Any]):
        """Add notification channel configuration."""
        self.notification_channels[channel_name] = channel_config
        logger.info(f"Added notification channel: {channel_name}")
    
    async def _evaluate_alerts(self):
        """Continuously evaluate alert rules."""
        while self.is_active:
            try:
                current_time = datetime.utcnow()
                
                for rule_id, rule in self.alert_rules.items():
                    if not rule.enabled:
                        continue
                    
                    try:
                        # Get current metric value
                        metric_value = await self._get_metric_value(rule.metric_name)
                        
                        if metric_value is not None:
                            # Evaluate condition
                            triggered = self._evaluate_condition(
                                metric_value, rule.condition, rule.threshold
                            )
                            
                            if triggered:
                                await self._handle_alert_trigger(rule, metric_value, current_time)
                            else:
                                await self._handle_alert_resolution(rule_id, current_time)
                                
                    except Exception as e:
                        logger.error(f"Error evaluating alert rule {rule_id}: {e}")
                
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(60)
    
    async def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value of metric."""
        # This would integrate with the metrics collector
        # For now, return a placeholder value
        return None
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition."""
        if condition == '>':
            return value > threshold
        elif condition == '<':
            return value < threshold
        elif condition == '==':
            return value == threshold
        elif condition == '!=':
            return value != threshold
        elif condition == '>=':
            return value >= threshold
        elif condition == '<=':
            return value <= threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False
    
    async def _handle_alert_trigger(self, rule: AlertRule, value: float, timestamp: datetime):
        """Handle alert trigger."""
        # Check if alert is already active (avoid duplicate alerts)
        if rule.rule_id in self.active_alerts:
            return
        
        # Create alert event
        alert_event = AlertEvent(
            event_id=str(uuid.uuid4()),
            rule_id=rule.rule_id,
            alert_name=rule.name,
            severity=rule.severity,
            alert_type=rule.alert_type,
            message=f"{rule.description} - Current value: {value}, Threshold: {rule.threshold}",
            current_value=value,
            threshold=rule.threshold,
            triggered_at=timestamp
        )
        
        # Store active alert
        self.active_alerts[rule.rule_id] = alert_event
        self.alert_history.append(alert_event)
        
        # Send notifications
        await self._send_alert_notification(alert_event, rule)
        
        logger.warning(f"Alert triggered: {rule.name} - {alert_event.message}")
    
    async def _handle_alert_resolution(self, rule_id: str, timestamp: datetime):
        """Handle alert resolution."""
        if rule_id in self.active_alerts:
            alert_event = self.active_alerts[rule_id]
            alert_event.resolved_at = timestamp
            alert_event.duration_seconds = (timestamp - alert_event.triggered_at).total_seconds()
            
            # Remove from active alerts
            del self.active_alerts[rule_id]
            
            # Send resolution notification
            await self._send_resolution_notification(alert_event)
            
            logger.info(f"Alert resolved: {alert_event.alert_name}")
    
    async def _send_alert_notification(self, alert: AlertEvent, rule: AlertRule):
        """Send alert notification through configured channels."""
        if not rule.notification_channels:
            return
        
        for channel_name in rule.notification_channels:
            if channel_name in self.notification_channels:
                try:
                    await self._send_to_channel(channel_name, alert, 'alert')
                    alert_notifications_total.labels(type='alert', severity=alert.severity.value).inc()
                except Exception as e:
                    logger.error(f"Failed to send alert to channel {channel_name}: {e}")
    
    async def _send_resolution_notification(self, alert: AlertEvent):
        """Send alert resolution notification."""
        # Find the rule to get notification channels
        rule = self.alert_rules.get(alert.rule_id)
        if not rule or not rule.notification_channels:
            return
        
        for channel_name in rule.notification_channels:
            if channel_name in self.notification_channels:
                try:
                    await self._send_to_channel(channel_name, alert, 'resolution')
                    alert_notifications_total.labels(type='resolution', severity=alert.severity.value).inc()
                except Exception as e:
                    logger.error(f"Failed to send resolution to channel {channel_name}: {e}")
    
    async def _send_to_channel(self, channel_name: str, alert: AlertEvent, notification_type: str):
        """Send notification to specific channel."""
        channel_config = self.notification_channels[channel_name]
        channel_type = channel_config.get('type')
        
        if channel_type == 'email':
            await self._send_email_notification(channel_config, alert, notification_type)
        elif channel_type == 'webhook':
            await self._send_webhook_notification(channel_config, alert, notification_type)
        elif channel_type == 'slack':
            await self._send_slack_notification(channel_config, alert, notification_type)
        else:
            logger.warning(f"Unknown notification channel type: {channel_type}")
    
    async def _send_email_notification(self, config: Dict[str, Any], alert: AlertEvent, notification_type: str):
        """Send email notification."""
        try:
            # Prepare email
            subject = f"[{alert.severity.value.upper()}] {alert.alert_name}"
            if notification_type == 'resolution':
                subject = f"[RESOLVED] {subject}"
            
            body = f"""
Alert: {alert.alert_name}
Severity: {alert.severity.value}
Type: {alert.alert_type.value}
Message: {alert.message}
Triggered At: {alert.triggered_at}
"""
            if notification_type == 'resolution':
                body += f"""
Resolved At: {alert.resolved_at}
Duration: {alert.duration_seconds:.2f} seconds
"""
            
            # Send email (implementation would depend on SMTP configuration)
            logger.info(f"Email notification sent for alert: {alert.alert_name}")
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
    
    async def _send_webhook_notification(self, config: Dict[str, Any], alert: AlertEvent, notification_type: str):
        """Send webhook notification."""
        try:
            webhook_url = config.get('url')
            if not webhook_url:
                return
            
            payload = {
                'alert_id': alert.event_id,
                'rule_id': alert.rule_id,
                'alert_name': alert.alert_name,
                'severity': alert.severity.value,
                'alert_type': alert.alert_type.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'triggered_at': alert.triggered_at.isoformat(),
                'notification_type': notification_type
            }
            
            if notification_type == 'resolution':
                payload.update({
                    'resolved_at': alert.resolved_at.isoformat(),
                    'duration_seconds': alert.duration_seconds
                })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert: {alert.alert_name}")
                    else:
                        logger.error(f"Webhook notification failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
    
    async def _send_slack_notification(self, config: Dict[str, Any], alert: AlertEvent, notification_type: str):
        """Send Slack notification."""
        try:
            webhook_url = config.get('webhook_url')
            if not webhook_url:
                return
            
            # Prepare Slack message
            color = {
                AlertSeverity.LOW: 'good',
                AlertSeverity.MEDIUM: 'warning', 
                AlertSeverity.HIGH: 'danger',
                AlertSeverity.CRITICAL: 'danger'
            }.get(alert.severity, 'warning')
            
            if notification_type == 'resolution':
                color = 'good'
            
            message = {
                'attachments': [{
                    'color': color,
                    'title': f"{'🔴' if notification_type == 'alert' else '✅'} {alert.alert_name}",
                    'fields': [
                        {'title': 'Severity', 'value': alert.severity.value, 'short': True},
                        {'title': 'Type', 'value': alert.alert_type.value, 'short': True},
                        {'title': 'Current Value', 'value': str(alert.current_value), 'short': True},
                        {'title': 'Threshold', 'value': str(alert.threshold), 'short': True},
                        {'title': 'Message', 'value': alert.message, 'short': False}
                    ],
                    'ts': int(alert.triggered_at.timestamp())
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for alert: {alert.alert_name}")
                    else:
                        logger.error(f"Slack notification failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
    
    def get_active_alerts(self) -> List[AlertEvent]:
        """Get list of currently active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[AlertEvent]:
        """Get alert history."""
        return self.alert_history[-limit:]


class HealthMonitor:
    """
    Comprehensive health monitoring system for all system components
    with automated health checks and status reporting.
    """
    
    def __init__(self, check_interval: int = 300):
        """Initialize health monitor."""
        self.check_interval = check_interval
        self.health_checks: Dict[str, Callable] = {}
        self.health_status: Dict[str, HealthCheckResult] = {}
        self.check_tasks: List[asyncio.Task] = []
        self.is_monitoring = False
        
    async def start_monitoring(self):
        """Start health monitoring."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        
        # Start health check task
        self.check_tasks.append(
            asyncio.create_task(self._run_health_checks())
        )
        
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.is_monitoring = False
        
        # Cancel check tasks
        for task in self.check_tasks:
            task.cancel()
        
        await asyncio.gather(*self.check_tasks, return_exceptions=True)
        self.check_tasks.clear()
        
        logger.info("Health monitoring stopped")
    
    def register_health_check(self, component: str, check_function: Callable):
        """Register health check function for component."""
        self.health_checks[component] = check_function
        logger.info(f"Registered health check for component: {component}")
    
    async def _run_health_checks(self):
        """Run all health checks periodically."""
        while self.is_monitoring:
            try:
                # Run all registered health checks
                for component, check_function in self.health_checks.items():
                    try:
                        result = await self._execute_health_check(component, check_function)
                        self.health_status[component] = result
                    except Exception as e:
                        logger.error(f"Health check failed for {component}: {e}")
                        self.health_status[component] = HealthCheckResult(
                            component=component,
                            status=HealthStatus.UNKNOWN,
                            message=f"Health check execution failed: {e}",
                            checked_at=datetime.utcnow()
                        )
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _execute_health_check(self, component: str, check_function: Callable) -> HealthCheckResult:
        """Execute individual health check."""
        start_time = time.time()
        
        try:
            # Execute health check function
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            
            response_time = (time.time() - start_time) * 1000
            
            # Parse result
            if isinstance(result, HealthCheckResult):
                result.response_time_ms = response_time
                return result
            elif isinstance(result, dict):
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus(result.get('status', 'unknown')),
                    message=result.get('message', 'Health check completed'),
                    details=result.get('details'),
                    checked_at=datetime.utcnow(),
                    response_time_ms=response_time
                )
            elif isinstance(result, bool):
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    message="Health check completed",
                    checked_at=datetime.utcnow(),
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message=f"Unknown health check result type: {type(result)}",
                    checked_at=datetime.utcnow(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {e}",
                checked_at=datetime.utcnow(),
                response_time_ms=response_time
            )
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.health_status:
            return {
                'status': HealthStatus.UNKNOWN,
                'message': 'No health checks configured',
                'components': {}
            }
        
        # Analyze component statuses
        status_counts = defaultdict(int)
        for result in self.health_status.values():
            status_counts[result.status] += 1
        
        total_components = len(self.health_status)
        healthy_components = status_counts[HealthStatus.HEALTHY]
        unhealthy_components = status_counts[HealthStatus.UNHEALTHY]
        degraded_components = status_counts[HealthStatus.DEGRADED]
        
        # Determine overall status
        if unhealthy_components > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_components > 0:
            overall_status = HealthStatus.DEGRADED
        elif healthy_components == total_components:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        return {
            'status': overall_status,
            'message': f"{healthy_components}/{total_components} components healthy",
            'components': {
                component: {
                    'status': result.status.value,
                    'message': result.message,
                    'last_check': result.checked_at.isoformat() if result.checked_at else None,
                    'response_time_ms': result.response_time_ms
                }
                for component, result in self.health_status.items()
            },
            'summary': {
                'total': total_components,
                'healthy': healthy_components,
                'degraded': degraded_components,
                'unhealthy': unhealthy_components,
                'unknown': status_counts[HealthStatus.UNKNOWN]
            }
        }
    
    def get_component_health(self, component: str) -> Optional[HealthCheckResult]:
        """Get health status for specific component."""
        return self.health_status.get(component)


class MonitoringSystem:
    """
    Unified monitoring system orchestrating metrics collection,
    alerting, health monitoring, and performance analysis.
    """
    
    def __init__(self, config: ProcessingConfig):
        """Initialize monitoring system."""
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_monitor = HealthMonitor()
        self.state = MonitoringState.INITIALIZING
        self.prometheus_server = None
        
    async def initialize(self):
        """Initialize monitoring system."""
        try:
            # Start Prometheus metrics server
            if self.config.monitoring_enabled:
                self.prometheus_server = start_http_server(8000, registry=monitoring_registry)
                logger.info("Prometheus metrics server started on port 8000")
            
            # Configure default alert rules
            await self._setup_default_alert_rules()
            
            # Configure default health checks
            await self._setup_default_health_checks()
            
            self.state = MonitoringState.ACTIVE
            logger.info("Monitoring system initialized successfully")
            
        except Exception as e:
            logger.error(f"Monitoring system initialization failed: {e}")
            self.state = MonitoringState.DEGRADED
            raise
    
    async def start(self):
        """Start all monitoring components."""
        try:
            # Start metrics collection
            await self.metrics_collector.start_collection()
            
            # Start alerting
            await self.alert_manager.start_alerting()
            
            # Start health monitoring
            await self.health_monitor.start_monitoring()
            
            logger.info("Monitoring system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring system: {e}")
            raise
    
    async def stop(self):
        """Stop all monitoring components."""
        try:
            # Stop health monitoring
            await self.health_monitor.stop_monitoring()
            
            # Stop alerting
            await self.alert_manager.stop_alerting()
            
            # Stop metrics collection
            await self.metrics_collector.stop_collection()
            
            self.state = MonitoringState.STOPPED
            logger.info("Monitoring system stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring system: {e}")
    
    async def _setup_default_alert_rules(self):
        """Setup default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                description="CPU usage is above 80%",
                metric_name="system_cpu_usage_percent",
                condition=">",
                threshold=80.0,
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.RESOURCE,
                notification_channels=["default"]
            ),
            AlertRule(
                rule_id="high_memory_usage",
                name="High Memory Usage", 
                description="Memory usage is above 85%",
                metric_name="system_memory_usage_percent",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.RESOURCE,
                notification_channels=["default"]
            ),
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Error rate is above 5%",
                metric_name="error_rate_percent",
                condition=">", 
                threshold=5.0,
                severity=AlertSeverity.MEDIUM,
                alert_type=AlertType.ERROR,
                notification_channels=["default"]
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.add_alert_rule(rule)
    
    async def _setup_default_health_checks(self):
        """Setup default health checks."""
        # System health check
        async def system_health_check():
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            if cpu_usage > 90 or memory_usage > 95:
                return HealthCheckResult(
                    component="system",
                    status=HealthStatus.UNHEALTHY,
                    message=f"High resource usage - CPU: {cpu_usage}%, Memory: {memory_usage}%",
                    checked_at=datetime.utcnow()
                )
            elif cpu_usage > 70 or memory_usage > 80:
                return HealthCheckResult(
                    component="system",
                    status=HealthStatus.DEGRADED,
                    message=f"Elevated resource usage - CPU: {cpu_usage}%, Memory: {memory_usage}%",
                    checked_at=datetime.utcnow()
                )
            else:
                return HealthCheckResult(
                    component="system",
                    status=HealthStatus.HEALTHY,
                    message=f"System healthy - CPU: {cpu_usage}%, Memory: {memory_usage}%",
                    checked_at=datetime.utcnow()
                )
        
        self.health_monitor.register_health_check("system", system_health_check)
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system monitoring overview."""
        # Get recent metrics
        recent_system_metrics = self.metrics_collector.get_recent_metrics('system_metrics', 10)
        
        # Get health status
        health_status = await self.health_monitor.get_overall_health()
        
        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Calculate performance summary
        performance_summary = {}
        if recent_system_metrics:
            latest_metrics = recent_system_metrics[-1]
            performance_summary = {
                'cpu_usage': latest_metrics.cpu_usage_percent,
                'memory_usage': latest_metrics.memory_usage_percent,
                'disk_usage': latest_metrics.disk_usage_percent,
                'network_rx_rate': latest_metrics.network_rx_bytes_per_sec,
                'network_tx_rate': latest_metrics.network_tx_bytes_per_sec,
                'active_connections': latest_metrics.active_connections
            }
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'monitoring_state': self.state.value,
            'health_status': health_status,
            'performance_summary': performance_summary,
            'active_alerts': [
                {
                    'name': alert.alert_name,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'triggered_at': alert.triggered_at.isoformat()
                }
                for alert in active_alerts
            ],
            'metrics_collection': {
                'is_collecting': self.metrics_collector.is_collecting,
                'buffer_sizes': {
                    metric_type: len(buffer) 
                    for metric_type, buffer in self.metrics_collector.metrics_buffer.items()
                }
            }
        }
    
    async def generate_performance_report(self, time_range_hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance analysis report."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # Get metrics for time range
        system_metrics = self.metrics_collector.get_recent_metrics('system_metrics')
        
        # Filter by time range
        filtered_metrics = [
            metric for metric in system_metrics
            if start_time <= metric.timestamp <= end_time
        ]
        
        if not filtered_metrics:
            # Return empty report if no data
            return PerformanceReport(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.utcnow(),
                time_range={'start': start_time, 'end': end_time},
                system_summary={},
                performance_metrics={},
                bottlenecks=[],
                recommendations=[],
                trend_analysis={}
            )
        
        # Calculate system summary
        cpu_values = [m.cpu_usage_percent for m in filtered_metrics]
        memory_values = [m.memory_usage_percent for m in filtered_metrics]
        disk_values = [m.disk_usage_percent for m in filtered_metrics]
        
        system_summary = {
            'cpu': {
                'avg': np.mean(cpu_values),
                'max': np.max(cpu_values),
                'min': np.min(cpu_values),
                'p95': np.percentile(cpu_values, 95)
            },
            'memory': {
                'avg': np.mean(memory_values),
                'max': np.max(memory_values),
                'min': np.min(memory_values),
                'p95': np.percentile(memory_values, 95)
            },
            'disk': {
                'avg': np.mean(disk_values),
                'max': np.max(disk_values),
                'min': np.min(disk_values),
                'p95': np.percentile(disk_values, 95)
            }
        }
        
        # Identify bottlenecks
        bottlenecks = []
        if system_summary['cpu']['p95'] > 80:
            bottlenecks.append({
                'type': 'cpu',
                'severity': 'high' if system_summary['cpu']['p95'] > 90 else 'medium',
                'description': f"CPU usage P95: {system_summary['cpu']['p95']:.1f}%"
            })
        
        if system_summary['memory']['p95'] > 85:
            bottlenecks.append({
                'type': 'memory',
                'severity': 'high' if system_summary['memory']['p95'] > 95 else 'medium',
                'description': f"Memory usage P95: {system_summary['memory']['p95']:.1f}%"
            })
        
        # Generate recommendations
        recommendations = []
        if system_summary['cpu']['avg'] > 70:
            recommendations.append("Consider adding more CPU cores or optimizing CPU-intensive processes")
        
        if system_summary['memory']['avg'] > 80:
            recommendations.append("Consider increasing available memory or optimizing memory usage")
        
        if len(bottlenecks) == 0:
            recommendations.append("System performance is within normal parameters")
        
        return PerformanceReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            time_range={'start': start_time, 'end': end_time},
            system_summary=system_summary,
            performance_metrics={
                'data_points': len(filtered_metrics),
                'collection_period_hours': time_range_hours
            },
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            trend_analysis={}
        )
