"""
IA-Influencer Agent - Advanced Workflow Monitor

Enterprise-grade workflow monitoring system with real-time analytics and alerting.
Provides comprehensive monitoring capabilities for content creator workflows.

Key Features:
- Real-time workflow monitoring
- Performance analytics and metrics
- Intelligent alerting system
- Workflow health assessment
- Resource utilization tracking
- Anomaly detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import statistics
from collections import defaultdict, deque
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import io
import base64

from ..base import BaseAgent


class AlertSeverity(Enum):
    """Alert severity enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class WorkflowMetric:
    """Workflow metric data point."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    workflow_id: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Workflow alert."""
    id: str
    workflow_id: str
    title: str
    description: str
    severity: AlertSeverity
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    status: str = "active"  # active, acknowledged, resolved
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Workflow health check result."""
    workflow_id: str
    component: str
    status: HealthStatus
    message: str
    checked_at: datetime
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Workflow performance report."""
    workflow_id: str
    period_start: datetime
    period_end: datetime
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration: float
    p95_duration: float
    p99_duration: float
    throughput: float
    error_rate: float
    resource_utilization: Dict[str, float]
    trends: Dict[str, Any]
    recommendations: List[str]


class WorkflowMonitor(BaseAgent):
    """
    Advanced workflow monitoring system for content creator workflows.
    
    This monitor provides comprehensive observability with real-time metrics,
    alerting, health checks, and performance analytics.
    """

    def __init__(self, retention_days: int = 30):
        """Initialize the workflow monitor."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Core monitoring components
        self.retention_days = retention_days
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: Dict[str, Alert] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Monitoring state
        self.monitored_workflows: Set[str] = set()
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_channels: Dict[str, Callable] = {}
        
        # Performance tracking
        self.execution_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Anomaly detection
        self.anomaly_detectors: Dict[str, Any] = {}
        self.statistical_models: Dict[str, Any] = {}
        
        # Monitoring configuration
        self.monitoring_intervals = {
            'health_check': 30,  # seconds
            'metrics_collection': 5,  # seconds
            'alert_evaluation': 10,  # seconds
            'cleanup': 3600  # seconds (1 hour)
        }
        
        # Background tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start the workflow monitoring system."""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring is already active")
                return
            
            self.monitoring_active = True
            
            # Start monitoring tasks
            self.monitoring_tasks = [
                asyncio.create_task(self._metrics_collection_loop()),
                asyncio.create_task(self._health_check_loop()),
                asyncio.create_task(self._alert_evaluation_loop()),
                asyncio.create_task(self._cleanup_loop())
            ]
            
            self.logger.info("Workflow monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {str(e)}")
            raise

    async def stop_monitoring(self):
        """Stop the workflow monitoring system."""
        try:
            self.monitoring_active = False
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            self.monitoring_tasks.clear()
            
            self.logger.info("Workflow monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")

    async def register_workflow(
        self,
        workflow_id: str,
        alert_rules: Optional[Dict[str, Any]] = None
    ):
        """Register a workflow for monitoring."""
        try:
            self.monitored_workflows.add(workflow_id)
            
            # Set default alert rules if not provided
            if alert_rules:
                self.alert_rules[workflow_id] = alert_rules
            else:
                self.alert_rules[workflow_id] = self._get_default_alert_rules()
            
            # Initialize performance baseline
            self.performance_baselines[workflow_id] = {
                'avg_duration': 60.0,  # seconds
                'success_rate': 0.95,
                'throughput': 1.0,  # executions per minute
                'error_rate': 0.05
            }
            
            self.logger.info(f"Registered workflow for monitoring: {workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Error registering workflow {workflow_id}: {str(e)}")

    async def record_metric(
        self,
        workflow_id: str,
        metric_name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a workflow metric."""
        try:
            metric = WorkflowMetric(
                name=metric_name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.now(timezone.utc),
                workflow_id=workflow_id,
                tags=tags or {},
                metadata=metadata or {}
            )
            
            # Store metric
            metric_key = f"{workflow_id}:{metric_name}"
            self.metrics_buffer[metric_key].append(metric)
            
            # Update anomaly detection if enabled
            await self._update_anomaly_detection(metric_key, value)
            
        except Exception as e:
            self.logger.error(f"Error recording metric: {str(e)}")

    async def record_execution(
        self,
        workflow_id: str,
        execution_data: Dict[str, Any]
    ):
        """Record workflow execution data."""
        try:
            # Store execution data
            self.execution_history[workflow_id].append({
                **execution_data,
                'recorded_at': datetime.now(timezone.utc).isoformat()
            })
            
            # Limit history size
            if len(self.execution_history[workflow_id]) > 1000:
                self.execution_history[workflow_id] = self.execution_history[workflow_id][-1000:]
            
            # Record derived metrics
            if 'duration' in execution_data:
                await self.record_metric(
                    workflow_id,
                    'execution_duration',
                    execution_data['duration'],
                    MetricType.TIMER
                )
            
            if 'success' in execution_data:
                await self.record_metric(
                    workflow_id,
                    'execution_success',
                    1.0 if execution_data['success'] else 0.0,
                    MetricType.COUNTER
                )
            
            if 'resource_usage' in execution_data:
                for resource, usage in execution_data['resource_usage'].items():
                    await self.record_metric(
                        workflow_id,
                        f'resource_usage_{resource}',
                        usage,
                        MetricType.GAUGE
                    )
            
        except Exception as e:
            self.logger.error(f"Error recording execution: {str(e)}")

    async def create_alert(
        self,
        workflow_id: str,
        title: str,
        description: str,
        severity: AlertSeverity,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new alert."""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = Alert(
                id=alert_id,
                workflow_id=workflow_id,
                title=title,
                description=description,
                severity=severity,
                created_at=datetime.now(timezone.utc),
                metadata=metadata or {}
            )
            
            self.alerts[alert_id] = alert
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            self.logger.warning(f"Alert created: {title} ({alert_id})")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            return ""

    async def get_workflow_health(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive health status for a workflow."""
        try:
            # Get recent metrics
            recent_metrics = await self._get_recent_metrics(workflow_id, minutes=15)
            
            # Get recent executions
            recent_executions = self.execution_history.get(workflow_id, [])[-20:]
            
            # Calculate health metrics
            health_metrics = await self._calculate_health_metrics(
                workflow_id, recent_metrics, recent_executions
            )
            
            # Determine overall health status
            overall_status = await self._determine_health_status(health_metrics)
            
            # Get active alerts
            active_alerts = [
                alert for alert in self.alerts.values()
                if alert.workflow_id == workflow_id and alert.status == "active"
            ]
            
            return {
                'workflow_id': workflow_id,
                'overall_status': overall_status.value,
                'health_metrics': health_metrics,
                'active_alerts': len(active_alerts),
                'recent_executions': len(recent_executions),
                'last_execution': recent_executions[-1]['recorded_at'] if recent_executions else None,
                'performance_score': health_metrics.get('performance_score', 0.0),
                'recommendations': await self._get_health_recommendations(workflow_id, health_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting workflow health: {str(e)}")
            return {
                'workflow_id': workflow_id,
                'overall_status': HealthStatus.UNKNOWN.value,
                'error': str(e)
            }

    async def get_performance_report(
        self,
        workflow_id: str,
        period_hours: int = 24
    ) -> PerformanceReport:
        """Generate performance report for a workflow."""
        try:
            period_end = datetime.now(timezone.utc)
            period_start = period_end - timedelta(hours=period_hours)
            
            # Get executions in period
            all_executions = self.execution_history.get(workflow_id, [])
            period_executions = [
                ex for ex in all_executions
                if datetime.fromisoformat(ex['recorded_at'].replace('Z', '+00:00')) >= period_start
            ]
            
            # Calculate metrics
            total_executions = len(period_executions)
            successful_executions = sum(1 for ex in period_executions if ex.get('success', False))
            failed_executions = total_executions - successful_executions
            
            # Duration metrics
            durations = [ex.get('duration', 0) for ex in period_executions if 'duration' in ex]
            avg_duration = statistics.mean(durations) if durations else 0.0
            p95_duration = np.percentile(durations, 95) if durations else 0.0
            p99_duration = np.percentile(durations, 99) if durations else 0.0
            
            # Rates
            throughput = total_executions / period_hours if period_hours > 0 else 0.0
            error_rate = failed_executions / max(1, total_executions)
            
            # Resource utilization
            resource_utilization = await self._calculate_resource_utilization(
                workflow_id, period_start, period_end
            )
            
            # Trends
            trends = await self._calculate_performance_trends(workflow_id, period_executions)
            
            # Recommendations
            recommendations = await self._generate_performance_recommendations(
                workflow_id, {
                    'error_rate': error_rate,
                    'avg_duration': avg_duration,
                    'throughput': throughput,
                    'resource_utilization': resource_utilization
                }
            )
            
            return PerformanceReport(
                workflow_id=workflow_id,
                period_start=period_start,
                period_end=period_end,
                total_executions=total_executions,
                successful_executions=successful_executions,
                failed_executions=failed_executions,
                average_duration=avg_duration,
                p95_duration=p95_duration,
                p99_duration=p99_duration,
                throughput=throughput,
                error_rate=error_rate,
                resource_utilization=resource_utilization,
                trends=trends,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            raise

    async def _metrics_collection_loop(self):
        """Background task for metrics collection."""
        try:
            while self.monitoring_active:
                try:
                    # Collect system metrics for each workflow
                    for workflow_id in self.monitored_workflows:
                        await self._collect_workflow_metrics(workflow_id)
                    
                    await asyncio.sleep(self.monitoring_intervals['metrics_collection'])
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Metrics collection error: {str(e)}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"Fatal metrics collection error: {str(e)}")

    async def _health_check_loop(self):
        """Background task for health checks."""
        try:
            while self.monitoring_active:
                try:
                    # Perform health checks for each workflow
                    for workflow_id in self.monitored_workflows:
                        await self._perform_health_check(workflow_id)
                    
                    await asyncio.sleep(self.monitoring_intervals['health_check'])
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Health check error: {str(e)}")
                    await asyncio.sleep(10)
                    
        except Exception as e:
            self.logger.error(f"Fatal health check error: {str(e)}")

    async def _alert_evaluation_loop(self):
        """Background task for alert evaluation."""
        try:
            while self.monitoring_active:
                try:
                    # Evaluate alert rules for each workflow
                    for workflow_id in self.monitored_workflows:
                        await self._evaluate_alert_rules(workflow_id)
                    
                    await asyncio.sleep(self.monitoring_intervals['alert_evaluation'])
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Alert evaluation error: {str(e)}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"Fatal alert evaluation error: {str(e)}")

    async def _cleanup_loop(self):
        """Background task for data cleanup."""
        try:
            while self.monitoring_active:
                try:
                    await self._cleanup_old_data()
                    await asyncio.sleep(self.monitoring_intervals['cleanup'])
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Cleanup error: {str(e)}")
                    await asyncio.sleep(60)
                    
        except Exception as e:
            self.logger.error(f"Fatal cleanup error: {str(e)}")

    async def _collect_workflow_metrics(self, workflow_id: str):
        """Collect metrics for a specific workflow."""
        try:
            # Placeholder for system metrics collection
            # In a real implementation, this would collect various system metrics
            
            # Example metrics
            await self.record_metric(
                workflow_id,
                'system_cpu_usage',
                np.random.uniform(10, 80),  # Placeholder
                MetricType.GAUGE
            )
            
            await self.record_metric(
                workflow_id,
                'system_memory_usage',
                np.random.uniform(20, 90),  # Placeholder
                MetricType.GAUGE
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics for {workflow_id}: {str(e)}")

    async def _perform_health_check(self, workflow_id: str):
        """Perform health check for a workflow."""
        try:
            start_time = time.time()
            
            # Placeholder health check - would perform actual checks
            # Example: check database connectivity, external API availability, etc.
            
            # Simulate health check
            await asyncio.sleep(0.1)
            
            response_time = time.time() - start_time
            status = HealthStatus.HEALTHY  # Placeholder
            message = "Workflow is healthy"
            
            health_check = HealthCheck(
                workflow_id=workflow_id,
                component="workflow_engine",
                status=status,
                message=message,
                checked_at=datetime.now(timezone.utc),
                response_time=response_time
            )
            
            self.health_checks[f"{workflow_id}:workflow_engine"] = health_check
            
        except Exception as e:
            # Record failed health check
            health_check = HealthCheck(
                workflow_id=workflow_id,
                component="workflow_engine",
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                checked_at=datetime.now(timezone.utc),
                response_time=0.0
            )
            
            self.health_checks[f"{workflow_id}:workflow_engine"] = health_check
            self.logger.error(f"Health check failed for {workflow_id}: {str(e)}")

    async def _evaluate_alert_rules(self, workflow_id: str):
        """Evaluate alert rules for a workflow."""
        try:
            alert_rules = self.alert_rules.get(workflow_id, {})
            
            for rule_name, rule_config in alert_rules.items():
                await self._evaluate_single_alert_rule(workflow_id, rule_name, rule_config)
                
        except Exception as e:
            self.logger.error(f"Error evaluating alert rules for {workflow_id}: {str(e)}")

    async def _evaluate_single_alert_rule(
        self,
        workflow_id: str,
        rule_name: str,
        rule_config: Dict[str, Any]
    ):
        """Evaluate a single alert rule."""
        try:
            metric_name = rule_config.get('metric')
            threshold = rule_config.get('threshold')
            condition = rule_config.get('condition', 'greater_than')  # greater_than, less_than, equals
            severity = AlertSeverity(rule_config.get('severity', 'medium'))
            
            # Get recent metric values
            metric_key = f"{workflow_id}:{metric_name}"
            recent_metrics = list(self.metrics_buffer.get(metric_key, []))[-10:]
            
            if not recent_metrics:
                return
            
            # Check condition
            latest_value = recent_metrics[-1].value
            triggered = False
            
            if condition == 'greater_than' and latest_value > threshold:
                triggered = True
            elif condition == 'less_than' and latest_value < threshold:
                triggered = True
            elif condition == 'equals' and abs(latest_value - threshold) < 0.001:
                triggered = True
            
            if triggered:
                # Check if alert already exists for this rule
                existing_alert = None
                for alert in self.alerts.values():
                    if (alert.workflow_id == workflow_id and
                        alert.metadata.get('rule_name') == rule_name and
                        alert.status == 'active'):
                        existing_alert = alert
                        break
                
                if not existing_alert:
                    # Create new alert
                    await self.create_alert(
                        workflow_id=workflow_id,
                        title=f"Alert: {rule_name}",
                        description=f"Metric {metric_name} value {latest_value} {condition} threshold {threshold}",
                        severity=severity,
                        metadata={'rule_name': rule_name, 'metric_value': latest_value}
                    )
                    
        except Exception as e:
            self.logger.error(f"Error evaluating alert rule {rule_name}: {str(e)}")

    def _get_default_alert_rules(self) -> Dict[str, Any]:
        """Get default alert rules for a workflow."""
        return {
            'high_error_rate': {
                'metric': 'execution_success',
                'threshold': 0.8,
                'condition': 'less_than',
                'severity': 'high'
            },
            'long_execution_time': {
                'metric': 'execution_duration',
                'threshold': 300,  # 5 minutes
                'condition': 'greater_than',
                'severity': 'medium'
            },
            'high_cpu_usage': {
                'metric': 'system_cpu_usage',
                'threshold': 90,
                'condition': 'greater_than',
                'severity': 'medium'
            }
        }

    async def _get_recent_metrics(
        self,
        workflow_id: str,
        minutes: int = 15
    ) -> Dict[str, List[WorkflowMetric]]:
        """Get recent metrics for a workflow."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            recent_metrics = {}
            
            for metric_key, metrics in self.metrics_buffer.items():
                if metric_key.startswith(f"{workflow_id}:"):
                    metric_name = metric_key.split(":", 1)[1]
                    recent_metrics[metric_name] = [
                        metric for metric in metrics
                        if metric.timestamp >= cutoff_time
                    ]
            
            return recent_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting recent metrics: {str(e)}")
            return {}

    async def _calculate_health_metrics(
        self,
        workflow_id: str,
        recent_metrics: Dict[str, List[WorkflowMetric]],
        recent_executions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate health metrics for a workflow."""
        try:
            health_metrics = {}
            
            # Success rate
            if recent_executions:
                successful = sum(1 for ex in recent_executions if ex.get('success', False))
                health_metrics['success_rate'] = successful / len(recent_executions)
            else:
                health_metrics['success_rate'] = 1.0
            
            # Average response time
            durations = [ex.get('duration', 0) for ex in recent_executions if 'duration' in ex]
            if durations:
                health_metrics['avg_response_time'] = statistics.mean(durations)
            else:
                health_metrics['avg_response_time'] = 0.0
            
            # Resource utilization
            cpu_metrics = recent_metrics.get('system_cpu_usage', [])
            if cpu_metrics:
                health_metrics['cpu_utilization'] = statistics.mean(m.value for m in cpu_metrics)
            else:
                health_metrics['cpu_utilization'] = 0.0
            
            memory_metrics = recent_metrics.get('system_memory_usage', [])
            if memory_metrics:
                health_metrics['memory_utilization'] = statistics.mean(m.value for m in memory_metrics)
            else:
                health_metrics['memory_utilization'] = 0.0
            
            # Performance score (composite metric)
            performance_score = (
                health_metrics['success_rate'] * 0.4 +
                (1 - min(health_metrics['avg_response_time'] / 60, 1)) * 0.3 +
                (1 - health_metrics['cpu_utilization'] / 100) * 0.15 +
                (1 - health_metrics['memory_utilization'] / 100) * 0.15
            )
            health_metrics['performance_score'] = performance_score
            
            return health_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating health metrics: {str(e)}")
            return {'performance_score': 0.0}

    async def _determine_health_status(self, health_metrics: Dict[str, float]) -> HealthStatus:
        """Determine overall health status based on metrics."""
        try:
            performance_score = health_metrics.get('performance_score', 0.0)
            success_rate = health_metrics.get('success_rate', 0.0)
            
            if success_rate < 0.7 or performance_score < 0.5:
                return HealthStatus.CRITICAL
            elif success_rate < 0.9 or performance_score < 0.7:
                return HealthStatus.WARNING
            else:
                return HealthStatus.HEALTHY
                
        except Exception as e:
            self.logger.error(f"Error determining health status: {str(e)}")
            return HealthStatus.UNKNOWN

    async def _get_health_recommendations(
        self,
        workflow_id: str,
        health_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate health recommendations based on metrics."""
        try:
            recommendations = []
            
            # Success rate recommendations
            success_rate = health_metrics.get('success_rate', 1.0)
            if success_rate < 0.8:
                recommendations.append("Review error logs and fix failing workflow steps")
            
            # Response time recommendations
            avg_response_time = health_metrics.get('avg_response_time', 0.0)
            if avg_response_time > 120:  # 2 minutes
                recommendations.append("Optimize workflow execution time")
            
            # Resource utilization recommendations
            cpu_utilization = health_metrics.get('cpu_utilization', 0.0)
            if cpu_utilization > 80:
                recommendations.append("Consider scaling compute resources")
            
            memory_utilization = health_metrics.get('memory_utilization', 0.0)
            if memory_utilization > 85:
                recommendations.append("Increase memory allocation or optimize memory usage")
            
            # Performance score recommendations
            performance_score = health_metrics.get('performance_score', 0.0)
            if performance_score < 0.6:
                recommendations.append("Overall performance is poor - review all workflow components")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through configured channels."""
        try:
            for channel_name, notification_func in self.notification_channels.items():
                try:
                    await notification_func(alert)
                except Exception as e:
                    self.logger.error(f"Error sending notification via {channel_name}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {str(e)}")

    async def _update_anomaly_detection(self, metric_key: str, value: float):
        """Update anomaly detection models with new metric value."""
        try:
            # Simple anomaly detection using moving average and standard deviation
            if metric_key not in self.anomaly_detectors:
                self.anomaly_detectors[metric_key] = {
                    'values': deque(maxlen=100),
                    'mean': 0.0,
                    'std': 0.0
                }
            
            detector = self.anomaly_detectors[metric_key]
            detector['values'].append(value)
            
            if len(detector['values']) >= 10:
                values_array = np.array(detector['values'])
                detector['mean'] = np.mean(values_array)
                detector['std'] = np.std(values_array)
                
                # Check for anomaly (value outside 3 standard deviations)
                if abs(value - detector['mean']) > 3 * detector['std']:
                    # Anomaly detected
                    workflow_id = metric_key.split(':')[0]
                    metric_name = metric_key.split(':', 1)[1]
                    
                    await self.create_alert(
                        workflow_id=workflow_id,
                        title=f"Anomaly detected in {metric_name}",
                        description=f"Metric value {value} is {abs(value - detector['mean']) / detector['std']:.1f} standard deviations from mean",
                        severity=AlertSeverity.MEDIUM,
                        metadata={'metric_name': metric_name, 'anomaly_score': abs(value - detector['mean']) / detector['std']}
                    )
                    
        except Exception as e:
            self.logger.error(f"Error updating anomaly detection: {str(e)}")

    async def _calculate_resource_utilization(
        self,
        workflow_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, float]:
        """Calculate resource utilization for a period."""
        try:
            resource_utilization = {}
            
            # Get CPU utilization
            cpu_key = f"{workflow_id}:system_cpu_usage"
            cpu_metrics = [
                m for m in self.metrics_buffer.get(cpu_key, [])
                if period_start <= m.timestamp <= period_end
            ]
            if cpu_metrics:
                resource_utilization['cpu'] = statistics.mean(m.value for m in cpu_metrics)
            
            # Get memory utilization
            memory_key = f"{workflow_id}:system_memory_usage"
            memory_metrics = [
                m for m in self.metrics_buffer.get(memory_key, [])
                if period_start <= m.timestamp <= period_end
            ]
            if memory_metrics:
                resource_utilization['memory'] = statistics.mean(m.value for m in memory_metrics)
            
            return resource_utilization
            
        except Exception as e:
            self.logger.error(f"Error calculating resource utilization: {str(e)}")
            return {}

    async def _calculate_performance_trends(
        self,
        workflow_id: str,
        period_executions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate performance trends."""
        try:
            trends = {}
            
            if len(period_executions) < 2:
                return trends
            
            # Sort executions by time
            sorted_executions = sorted(
                period_executions,
                key=lambda x: x.get('recorded_at', '')
            )
            
            # Calculate duration trend
            durations = [ex.get('duration', 0) for ex in sorted_executions if 'duration' in ex]
            if len(durations) > 1:
                x = list(range(len(durations)))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, durations)
                trends['duration_trend'] = {
                    'slope': slope,
                    'direction': 'increasing' if slope > 0 else 'decreasing',
                    'correlation': r_value
                }
            
            # Calculate success rate trend
            success_rates = []
            window_size = max(1, len(sorted_executions) // 10)  # 10 windows
            for i in range(0, len(sorted_executions), window_size):
                window = sorted_executions[i:i+window_size]
                if window:
                    success_count = sum(1 for ex in window if ex.get('success', False))
                    success_rates.append(success_count / len(window))
            
            if len(success_rates) > 1:
                x = list(range(len(success_rates)))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, success_rates)
                trends['success_rate_trend'] = {
                    'slope': slope,
                    'direction': 'improving' if slope > 0 else 'degrading',
                    'correlation': r_value
                }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error calculating performance trends: {str(e)}")
            return {}

    async def _generate_performance_recommendations(
        self,
        workflow_id: str,
        performance_data: Dict[str, Any]
    ) -> List[str]:
        """Generate performance recommendations."""
        try:
            recommendations = []
            
            # Error rate recommendations
            error_rate = performance_data.get('error_rate', 0.0)
            if error_rate > 0.1:
                recommendations.append("High error rate detected - investigate and fix failing components")
            elif error_rate > 0.05:
                recommendations.append("Monitor error rate closely - consider preventive measures")
            
            # Duration recommendations
            avg_duration = performance_data.get('avg_duration', 0.0)
            baseline_duration = self.performance_baselines.get(workflow_id, {}).get('avg_duration', 60.0)
            if avg_duration > baseline_duration * 1.5:
                recommendations.append("Execution time significantly above baseline - optimize workflow steps")
            
            # Throughput recommendations
            throughput = performance_data.get('throughput', 0.0)
            baseline_throughput = self.performance_baselines.get(workflow_id, {}).get('throughput', 1.0)
            if throughput < baseline_throughput * 0.7:
                recommendations.append("Throughput below expectations - check for bottlenecks")
            
            # Resource utilization recommendations
            resource_utilization = performance_data.get('resource_utilization', {})
            cpu_usage = resource_utilization.get('cpu', 0.0)
            if cpu_usage > 85:
                recommendations.append("High CPU utilization - consider vertical or horizontal scaling")
            
            memory_usage = resource_utilization.get('memory', 0.0)
            if memory_usage > 80:
                recommendations.append("High memory utilization - optimize memory usage or increase allocation")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating performance recommendations: {str(e)}")
            return []

    async def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            
            # Clean up old metrics
            for metric_key, metrics in self.metrics_buffer.items():
                # Convert to list to avoid modifying deque during iteration
                current_metrics = list(metrics)
                metrics.clear()
                
                # Add back recent metrics
                for metric in current_metrics:
                    if metric.timestamp >= cutoff_time:
                        metrics.append(metric)
            
            # Clean up old alerts (keep resolved alerts for some time)
            alert_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            alerts_to_remove = []
            
            for alert_id, alert in self.alerts.items():
                if (alert.status == 'resolved' and
                    alert.resolved_at and
                    alert.resolved_at < alert_cutoff):
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.alerts[alert_id]
            
            # Clean up old execution history
            for workflow_id, executions in self.execution_history.items():
                filtered_executions = [
                    ex for ex in executions
                    if datetime.fromisoformat(ex['recorded_at'].replace('Z', '+00:00')) >= cutoff_time
                ]
                self.execution_history[workflow_id] = filtered_executions
            
            self.logger.info("Completed data cleanup")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")

    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring system statistics."""
        try:
            # Calculate metrics statistics
            total_metrics = sum(len(metrics) for metrics in self.metrics_buffer.values())
            
            # Calculate alert statistics
            active_alerts = sum(1 for alert in self.alerts.values() if alert.status == 'active')
            resolved_alerts = sum(1 for alert in self.alerts.values() if alert.status == 'resolved')
            
            return {
                'monitored_workflows': len(self.monitored_workflows),
                'total_metrics': total_metrics,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'health_checks': len(self.health_checks),
                'monitoring_active': self.monitoring_active,
                'retention_days': self.retention_days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring stats: {str(e)}")
            return {'error': str(e)}

    # Additional utility methods for external integration
    
    def add_notification_channel(self, name: str, notification_func: Callable):
        """Add a notification channel for alerts."""
        self.notification_channels[name] = notification_func

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        try:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = 'acknowledged'
                alert.acknowledged_at = datetime.now(timezone.utc)
                alert.acknowledged_by = acknowledged_by
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {str(e)}")
            return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        try:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = 'resolved'
                alert.resolved_at = datetime.now(timezone.utc)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")
            return False
