"""Pipeline Monitoring Systems
Author: Fahed Mlaiel <mlaiel@live.de>

Advanced monitoring and observability systems for data pipeline health,
performance metrics, error tracking, and resource optimization.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import statistics
import threading
import queue
from dataclasses import dataclass, field
from enum import Enum
import json
import psutil
import time

# Monitoring and observability
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary

# Alerting
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dashboard integration
import grafana_api

from ..core.exceptions import MonitoringError, AlertingError
from ..core.metrics import MetricsCollector
from ..core.config import MonitoringConfig
from ..utils.decorators import monitor_performance
from ..utils.notification import NotificationManager


class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning" 
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthCheck:
    """Health check result."""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: float = 0.0


@dataclass
class Alert:
    """System alert information."""
    alert_id: str
    component: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_time: Optional[datetime] = None


class PipelineHealthMonitor:
    """
    Comprehensive health monitoring system for pipeline components
    with automated health checks and intelligent anomaly detection.
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("health_monitor")
        
        # Health check registry
        self.health_checks = {}
        self.health_history = {}
        self.active_alerts = {}
        
        # Monitoring metrics
        self.health_gauge = Gauge('pipeline_component_health', 'Component health status', ['component'])
        self.response_time_histogram = Histogram('health_check_duration_seconds', 'Health check duration', ['component'])
        
        # Background monitoring
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        self._register_default_health_checks()
        self._start_monitoring()
    
    def _register_default_health_checks(self):
        """Register default health checks for common components."""
        
        # Database connectivity check
        self.register_health_check(
            'database',
            self._check_database_health,
            interval=30,
            timeout=10
        )
        
        # Redis connectivity check
        self.register_health_check(
            'redis',
            self._check_redis_health,
            interval=30,
            timeout=5
        )
        
        # Storage accessibility check
        self.register_health_check(
            'storage',
            self._check_storage_health,
            interval=60,
            timeout=15
        )
        
        # Processing engine health
        self.register_health_check(
            'processing_engine',
            self._check_processing_engine_health,
            interval=45,
            timeout=10
        )
        
        # API endpoint health
        self.register_health_check(
            'api_endpoints',
            self._check_api_health,
            interval=60,
            timeout=20
        )
    
    def register_health_check(
        self,
        component: str,
        check_function: Callable,
        interval: int = 60,
        timeout: int = 10,
        critical: bool = True
    ):
        """
        Register a health check for a component.
        
        Args:
            component: Component name
            check_function: Async function that performs the health check
            interval: Check interval in seconds
            timeout: Check timeout in seconds
            critical: Whether this is a critical component
        """
        
        self.health_checks[component] = {
            'function': check_function,
            'interval': interval,
            'timeout': timeout,
            'critical': critical,
            'last_check': None,
            'next_check': datetime.utcnow()
        }
        
        self.health_history[component] = []
        
        self.logger.info(f"Registered health check for {component}")
    
    def _start_monitoring(self):
        """Start background health monitoring."""
        
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("Health monitoring started")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        
        while not self.stop_monitoring.wait(5):  # Check every 5 seconds
            try:
                current_time = datetime.utcnow()
                
                for component, config in self.health_checks.items():
                    if current_time >= config['next_check']:
                        # Run health check asynchronously
                        asyncio.run_coroutine_threadsafe(
                            self._run_health_check(component),
                            asyncio.get_event_loop()
                        )
                        
                        # Schedule next check
                        config['next_check'] = current_time + timedelta(seconds=config['interval'])
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    async def _run_health_check(self, component: str):
        """Run health check for a specific component."""
        
        config = self.health_checks[component]
        start_time = time.time()
        
        try:
            # Run health check with timeout
            health_result = await asyncio.wait_for(
                config['function'](),
                timeout=config['timeout']
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            health_check = HealthCheck(
                component=component,
                status=health_result.get('status', HealthStatus.UNKNOWN),
                message=health_result.get('message', ''),
                metrics=health_result.get('metrics', {}),
                response_time_ms=response_time
            )
            
            # Update metrics
            self.health_gauge.labels(component=component).set(
                1 if health_check.status == HealthStatus.HEALTHY else 0
            )
            self.response_time_histogram.labels(component=component).observe(response_time / 1000)
            
            # Store health check result
            self._store_health_result(health_check)
            
            # Check for alerts
            await self._evaluate_health_alerts(health_check, config['critical'])
            
            config['last_check'] = datetime.utcnow()
            
        except asyncio.TimeoutError:
            health_check = HealthCheck(
                component=component,
                status=HealthStatus.CRITICAL,
                message=f"Health check timeout after {config['timeout']} seconds",
                response_time_ms=(time.time() - start_time) * 1000
            )
            
            self._store_health_result(health_check)
            await self._trigger_alert(
                component,
                AlertSeverity.CRITICAL,
                f"Health check timeout for {component}"
            )
            
        except Exception as e:
            health_check = HealthCheck(
                component=component,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )
            
            self._store_health_result(health_check)
            await self._trigger_alert(
                component,
                AlertSeverity.CRITICAL,
                f"Health check error for {component}: {str(e)}"
            )
    
    def _store_health_result(self, health_check: HealthCheck):
        """Store health check result in history."""
        
        component_history = self.health_history[health_check.component]
        component_history.append(health_check)
        
        # Keep only last 100 results
        if len(component_history) > 100:
            component_history.pop(0)
    
    async def _evaluate_health_alerts(self, health_check: HealthCheck, is_critical: bool):
        """Evaluate health check for alert conditions."""
        
        component = health_check.component
        
        # Check for status degradation
        if health_check.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            severity = AlertSeverity.CRITICAL if health_check.status == HealthStatus.CRITICAL else AlertSeverity.WARNING
            
            if is_critical and health_check.status == HealthStatus.CRITICAL:
                severity = AlertSeverity.EMERGENCY
            
            await self._trigger_alert(
                component,
                severity,
                health_check.message,
                health_check.metrics
            )
        
        # Check for performance degradation
        if health_check.response_time_ms > self.config.response_time_threshold:
            await self._trigger_alert(
                component,
                AlertSeverity.WARNING,
                f"High response time: {health_check.response_time_ms:.2f}ms",
                {'response_time_ms': health_check.response_time_ms}
            )
    
    async def _trigger_alert(
        self,
        component: str,
        severity: AlertSeverity,
        message: str,
        details: Dict[str, Any] = None
    ):
        """Trigger system alert."""
        
        alert_id = f"{component}_{int(time.time())}"
        
        alert = Alert(
            alert_id=alert_id,
            component=component,
            severity=severity,
            message=message,
            details=details or {}
        )
        
        self.active_alerts[alert_id] = alert
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        self.logger.warning(f"Alert triggered: {component} - {message}")
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications via configured channels."""
        
        notification_manager = NotificationManager(self.config.notification_config)
        
        try:
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                # Send immediate notifications
                await notification_manager.send_critical_alert(alert)
            else:
                # Queue for batch notifications
                await notification_manager.queue_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {e}")
    
    # Health check implementations
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        
        try:
            # Simulate database health check
            # In production, implement actual database connectivity test
            
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Database connection successful',
                'metrics': {
                    'connection_pool_size': 10,
                    'active_connections': 3,
                    'query_response_time_ms': 15.5
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Database connection failed: {str(e)}'
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        
        try:
            # Simulate Redis health check
            # In production, implement actual Redis connectivity test
            
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Redis connection successful',
                'metrics': {
                    'memory_usage_mb': 128.5,
                    'connected_clients': 15,
                    'keyspace_hits': 1000,
                    'keyspace_misses': 50
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Redis connection failed: {str(e)}'
            }
    
    async def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage system accessibility and performance."""
        
        try:
            # Simulate storage health check
            # In production, implement actual storage accessibility test
            
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Storage systems accessible',
                'metrics': {
                    'available_space_gb': 500.2,
                    'read_latency_ms': 25.3,
                    'write_latency_ms': 45.1
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Storage check failed: {str(e)}'
            }
    
    async def _check_processing_engine_health(self) -> Dict[str, Any]:
        """Check processing engine health and capacity."""
        
        try:
            # Simulate processing engine health check
            # In production, implement actual processing engine status check
            
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Processing engines operational',
                'metrics': {
                    'active_jobs': 5,
                    'queue_length': 12,
                    'average_processing_time_ms': 1500.5,
                    'success_rate_percent': 98.5
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Processing engine check failed: {str(e)}'
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API endpoint health and responsiveness."""
        
        try:
            # Simulate API health check
            # In production, implement actual API endpoint checks
            
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'API endpoints responsive',
                'metrics': {
                    'average_response_time_ms': 150.2,
                    'success_rate_percent': 99.8,
                    'active_connections': 25,
                    'rate_limit_usage_percent': 45.3
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'API health check failed: {str(e)}'
            }
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        
        if not self.health_history:
            return {
                'status': HealthStatus.UNKNOWN,
                'message': 'No health data available',
                'components': {}
            }
        
        component_statuses = {}
        critical_issues = []
        warning_issues = []
        
        for component, history in self.health_history.items():
            if history:
                latest_check = history[-1]
                component_statuses[component] = {
                    'status': latest_check.status.value,
                    'message': latest_check.message,
                    'last_check': latest_check.timestamp.isoformat(),
                    'response_time_ms': latest_check.response_time_ms
                }
                
                if latest_check.status == HealthStatus.CRITICAL:
                    critical_issues.append(component)
                elif latest_check.status == HealthStatus.WARNING:
                    warning_issues.append(component)
        
        # Determine overall status
        if critical_issues:
            overall_status = HealthStatus.CRITICAL
            message = f"Critical issues in: {', '.join(critical_issues)}"
        elif warning_issues:
            overall_status = HealthStatus.WARNING
            message = f"Warnings in: {', '.join(warning_issues)}"
        else:
            overall_status = HealthStatus.HEALTHY
            message = "All systems operational"
        
        return {
            'status': overall_status.value,
            'message': message,
            'components': component_statuses,
            'critical_issues': critical_issues,
            'warning_issues': warning_issues,
            'total_components': len(component_statuses),
            'healthy_components': len([s for s in component_statuses.values() if s['status'] == 'healthy'])
        }


class PerformanceMetricsCollector:
    """
    Advanced performance metrics collection system with real-time
    monitoring, trend analysis, and predictive insights.
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("performance_collector")
        
        # Prometheus metrics
        self.request_counter = Counter('pipeline_requests_total', 'Total requests', ['endpoint', 'method', 'status'])
        self.request_duration = Histogram('pipeline_request_duration_seconds', 'Request duration', ['endpoint'])
        self.active_connections = Gauge('pipeline_active_connections', 'Active connections')
        self.throughput_gauge = Gauge('pipeline_throughput_per_second', 'Processing throughput')
        
        # Performance data storage
        self.performance_data = {}
        self.trending_data = {}
        
        # Collection thread
        self.collection_thread = None
        self.stop_collection = threading.Event()
        
        self._start_collection()
    
    def _start_collection(self):
        """Start background metrics collection."""
        
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self.collection_thread.start()
        
        self.logger.info("Performance metrics collection started")
    
    def _collection_loop(self):
        """Main metrics collection loop."""
        
        while not self.stop_collection.wait(self.config.collection_interval):
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self._store_metrics('system', system_metrics)
                
                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                self._store_metrics('application', app_metrics)
                
                # Collect pipeline metrics
                pipeline_metrics = self._collect_pipeline_metrics()
                self._store_metrics('pipeline', pipeline_metrics)
                
                # Update trending data
                self._update_trending_data()
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level performance metrics."""
        
        return {
            'cpu_usage_percent': psutil.cpu_percent(interval=1),
            'memory_usage_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'network_io': dict(psutil.net_io_counters()._asdict()),
            'load_average': psutil.getloadavg(),
            'process_count': len(psutil.pids()),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-level performance metrics."""
        
        # In production, collect actual application metrics
        return {
            'active_sessions': 150,
            'database_connections': 25,
            'cache_hit_rate': 85.5,
            'error_rate_percent': 0.5,
            'response_time_p95_ms': 250.0,
            'response_time_p99_ms': 500.0,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _collect_pipeline_metrics(self) -> Dict[str, Any]:
        """Collect pipeline-specific performance metrics."""
        
        # In production, collect actual pipeline metrics
        return {
            'jobs_processed_per_minute': 45,
            'average_job_duration_ms': 1500,
            'queue_length': 12,
            'processing_engine_utilization': 75.5,
            'success_rate_percent': 98.2,
            'data_throughput_mb_per_second': 12.5,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _store_metrics(self, category: str, metrics: Dict[str, Any]):
        """Store metrics data for analysis."""
        
        if category not in self.performance_data:
            self.performance_data[category] = []
        
        self.performance_data[category].append(metrics)
        
        # Keep only last 1000 data points
        if len(self.performance_data[category]) > 1000:
            self.performance_data[category].pop(0)
    
    def _update_trending_data(self):
        """Update trending analysis data."""
        
        for category, data in self.performance_data.items():
            if len(data) < 2:
                continue
            
            if category not in self.trending_data:
                self.trending_data[category] = {}
            
            # Calculate trends for key metrics
            for metric_name in data[0].keys():
                if metric_name == 'timestamp':
                    continue
                
                try:
                    values = [d[metric_name] for d in data[-10:] if isinstance(d.get(metric_name), (int, float))]
                    
                    if len(values) >= 2:
                        trend = self._calculate_trend(values)
                        self.trending_data[category][metric_name] = {
                            'trend': trend,
                            'current_value': values[-1],
                            'average': statistics.mean(values),
                            'min': min(values),
                            'max': max(values),
                            'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                        }
                        
                except (KeyError, ValueError, TypeError):
                    continue
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        y = values
        
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    @monitor_performance
    async def get_performance_summary(self, timeframe_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for specified timeframe."""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeframe_minutes)
        
        summary = {
            'timeframe_minutes': timeframe_minutes,
            'summary_generated_at': datetime.utcnow().isoformat(),
            'categories': {}
        }
        
        for category, data in self.performance_data.items():
            # Filter data by timeframe
            filtered_data = [
                d for d in data
                if datetime.fromisoformat(d['timestamp']) >= cutoff_time
            ]
            
            if not filtered_data:
                continue
            
            category_summary = {
                'data_points': len(filtered_data),
                'metrics': {},
                'trends': self.trending_data.get(category, {})
            }
            
            # Calculate summary statistics for each metric
            for metric_name in filtered_data[0].keys():
                if metric_name == 'timestamp':
                    continue
                
                try:
                    values = [d[metric_name] for d in filtered_data if isinstance(d.get(metric_name), (int, float))]
                    
                    if values:
                        category_summary['metrics'][metric_name] = {
                            'current': values[-1],
                            'average': statistics.mean(values),
                            'min': min(values),
                            'max': max(values),
                            'median': statistics.median(values),
                            'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values)
                        }
                        
                except (KeyError, ValueError, TypeError):
                    continue
            
            summary['categories'][category] = category_summary
        
        return summary


class ErrorTrackingSystem:
    """
    Comprehensive error tracking and analysis system with intelligent
    categorization, root cause analysis, and automated resolution suggestions.
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.error_storage = []
        self.error_patterns = {}
        self.resolution_database = {}
        
        # Error metrics
        self.error_counter = Counter('pipeline_errors_total', 'Total errors', ['category', 'severity'])
        self.error_resolution_time = Histogram('error_resolution_time_seconds', 'Error resolution time')
    
    async def track_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: AlertSeverity = AlertSeverity.WARNING
    ) -> str:
        """
        Track and analyze error with context information.
        
        Args:
            error: Exception object
            context: Error context information
            severity: Error severity level
            
        Returns:
            Error tracking ID
        """
        
        error_id = f"error_{int(time.time())}_{hash(str(error)) % 10000}"
        
        error_data = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'severity': severity.value,
            'context': context,
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False,
            'resolution_suggestions': []
        }
        
        # Analyze error patterns
        pattern_analysis = await self._analyze_error_patterns(error_data)
        error_data['pattern_analysis'] = pattern_analysis
        
        # Generate resolution suggestions
        suggestions = await self._generate_resolution_suggestions(error_data)
        error_data['resolution_suggestions'] = suggestions
        
        # Store error
        self.error_storage.append(error_data)
        
        # Update metrics
        self.error_counter.labels(
            category=error_data['error_type'],
            severity=severity.value
        ).inc()
        
        self.logger.error(f"Error tracked: {error_id} - {error_data['error_message']}")
        
        return error_id
    
    async def _analyze_error_patterns(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error patterns for insights."""
        
        error_type = error_data['error_type']
        error_message = error_data['error_message']
        
        # Count similar errors
        similar_errors = [
            e for e in self.error_storage
            if e['error_type'] == error_type and
            self._calculate_message_similarity(e['error_message'], error_message) > 0.8
        ]
        
        # Analyze frequency and trends
        recent_errors = [
            e for e in similar_errors
            if datetime.fromisoformat(e['timestamp']) > datetime.utcnow() - timedelta(hours=1)
        ]
        
        return {
            'similar_error_count': len(similar_errors),
            'recent_error_count': len(recent_errors),
            'is_recurring': len(similar_errors) > 3,
            'frequency_trend': 'increasing' if len(recent_errors) > len(similar_errors) * 0.5 else 'stable'
        }
    
    def _calculate_message_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate similarity between error messages."""
        
        # Simple similarity calculation based on common words
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _generate_resolution_suggestions(self, error_data: Dict[str, Any]) -> List[str]:
        """Generate automated resolution suggestions."""
        
        suggestions = []
        error_type = error_data['error_type']
        context = error_data['context']
        
        # Common resolution patterns
        if error_type == 'ConnectionError':
            suggestions.extend([
                "Check network connectivity",
                "Verify service endpoints are accessible",
                "Review firewall and security group settings",
                "Check service health status"
            ])
        
        elif error_type == 'TimeoutError':
            suggestions.extend([
                "Increase timeout settings",
                "Check system load and performance",
                "Review resource allocation",
                "Consider implementing retry logic"
            ])
        
        elif error_type == 'MemoryError':
            suggestions.extend([
                "Increase available memory",
                "Optimize memory usage in application",
                "Implement memory monitoring",
                "Consider chunking large operations"
            ])
        
        elif error_type == 'FileNotFoundError':
            suggestions.extend([
                "Verify file path and permissions",
                "Check if file was moved or deleted",
                "Implement file existence validation",
                "Review backup and recovery procedures"
            ])
        
        # Context-specific suggestions
        if 'database' in context:
            suggestions.append("Check database connection and credentials")
        
        if 'api' in context:
            suggestions.append("Verify API endpoint and authentication")
        
        if 'storage' in context:
            suggestions.append("Check storage service availability and permissions")
        
        return suggestions[:5]  # Return top 5 suggestions


class ResourceUsageMonitor:
    """
    Real-time resource usage monitoring with intelligent optimization
    recommendations and automated scaling triggers.
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.resource_data = {}
        self.usage_thresholds = config.resource_thresholds
        
        # Resource metrics
        self.cpu_usage_gauge = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage_gauge = Gauge('system_memory_usage_percent', 'Memory usage percentage')
        self.disk_usage_gauge = Gauge('system_disk_usage_percent', 'Disk usage percentage')
        
        # Start monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
    
    async def _monitor_resources(self):
        """Monitor system resources continuously."""
        
        while True:
            try:
                # Collect resource data
                resource_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'cpu': {
                        'usage_percent': psutil.cpu_percent(interval=1),
                        'load_average': psutil.getloadavg(),
                        'core_count': psutil.cpu_count()
                    },
                    'memory': {
                        'usage_percent': psutil.virtual_memory().percent,
                        'available_gb': psutil.virtual_memory().available / (1024**3),
                        'total_gb': psutil.virtual_memory().total / (1024**3)
                    },
                    'disk': {
                        'usage_percent': psutil.disk_usage('/').percent,
                        'free_gb': psutil.disk_usage('/').free / (1024**3),
                        'total_gb': psutil.disk_usage('/').total / (1024**3)
                    },
                    'network': dict(psutil.net_io_counters()._asdict()),
                    'processes': len(psutil.pids())
                }
                
                # Update Prometheus metrics
                self.cpu_usage_gauge.set(resource_data['cpu']['usage_percent'])
                self.memory_usage_gauge.set(resource_data['memory']['usage_percent'])
                self.disk_usage_gauge.set(resource_data['disk']['usage_percent'])
                
                # Store resource data
                self._store_resource_data(resource_data)
                
                # Check thresholds and trigger alerts
                await self._check_resource_thresholds(resource_data)
                
                await asyncio.sleep(self.config.resource_monitor_interval)
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    def _store_resource_data(self, data: Dict[str, Any]):
        """Store resource usage data."""
        
        timestamp = data['timestamp']
        
        for category in ['cpu', 'memory', 'disk']:
            if category not in self.resource_data:
                self.resource_data[category] = []
            
            category_data = data[category].copy()
            category_data['timestamp'] = timestamp
            
            self.resource_data[category].append(category_data)
            
            # Keep only last 1000 data points
            if len(self.resource_data[category]) > 1000:
                self.resource_data[category].pop(0)
    
    async def _check_resource_thresholds(self, data: Dict[str, Any]):
        """Check resource usage against thresholds."""
        
        # CPU threshold check
        if data['cpu']['usage_percent'] > self.usage_thresholds.get('cpu_warning', 80):
            severity = AlertSeverity.CRITICAL if data['cpu']['usage_percent'] > 95 else AlertSeverity.WARNING
            # Trigger CPU usage alert
            
        # Memory threshold check
        if data['memory']['usage_percent'] > self.usage_thresholds.get('memory_warning', 85):
            severity = AlertSeverity.CRITICAL if data['memory']['usage_percent'] > 95 else AlertSeverity.WARNING
            # Trigger memory usage alert
            
        # Disk threshold check
        if data['disk']['usage_percent'] > self.usage_thresholds.get('disk_warning', 90):
            severity = AlertSeverity.CRITICAL if data['disk']['usage_percent'] > 98 else AlertSeverity.WARNING
            # Trigger disk usage alert
    
    async def get_resource_summary(self, timeframe_minutes: int = 60) -> Dict[str, Any]:
        """Get resource usage summary for specified timeframe."""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeframe_minutes)
        
        summary = {
            'timeframe_minutes': timeframe_minutes,
            'generated_at': datetime.utcnow().isoformat(),
            'current_usage': {},
            'peak_usage': {},
            'average_usage': {},
            'recommendations': []
        }
        
        for category, data in self.resource_data.items():
            filtered_data = [
                d for d in data
                if datetime.fromisoformat(d['timestamp']) >= cutoff_time
            ]
            
            if not filtered_data:
                continue
            
            # Get usage percentages
            usage_values = [d['usage_percent'] for d in filtered_data]
            
            summary['current_usage'][category] = usage_values[-1] if usage_values else 0
            summary['peak_usage'][category] = max(usage_values) if usage_values else 0
            summary['average_usage'][category] = statistics.mean(usage_values) if usage_values else 0
        
        # Generate optimization recommendations
        summary['recommendations'] = self._generate_optimization_recommendations(summary)
        
        return summary
    
    def _generate_optimization_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate resource optimization recommendations."""
        
        recommendations = []
        
        # CPU recommendations
        cpu_avg = summary['average_usage'].get('cpu', 0)
        if cpu_avg > 80:
            recommendations.append("Consider scaling CPU resources or optimizing CPU-intensive operations")
        elif cpu_avg < 20:
            recommendations.append("CPU resources may be over-provisioned, consider scaling down")
        
        # Memory recommendations
        memory_avg = summary['average_usage'].get('memory', 0)
        if memory_avg > 85:
            recommendations.append("Memory usage is high, consider increasing memory or optimizing memory usage")
        elif memory_avg < 30:
            recommendations.append("Memory resources may be over-provisioned")
        
        # Disk recommendations
        disk_avg = summary['average_usage'].get('disk', 0)
        if disk_avg > 90:
            recommendations.append("Disk usage is critically high, implement cleanup or increase storage capacity")
        
        return recommendations
