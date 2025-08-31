"""System Monitoring

Real-time monitoring system for the IA Influencer platform infrastructure,
AI models, and business operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


class MonitoringLevel(Enum):
    """Monitoring intensity levels"""    MINIMAL = "minimal"      # Basic health checks
    STANDARD = "standard"    # Regular monitoring
    DETAILED = "detailed"    # Comprehensive monitoring
    DEBUG = "debug"          # Extensive debugging info


class MetricType(Enum):
    """Types of metrics"""    COUNTER = "counter"      # Always increasing value
    GAUGE = "gauge"          # Current value that can go up/down
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"      # Sample observations


class HealthStatus(Enum):
    """Health status levels"""    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"


@dataclass
class Metric:
    """Individual metric definition"""    name: str
    metric_type: MetricType
    value: Union[int, float]
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}


@dataclass
class SystemHealth:
    """Overall system health status"""    status: HealthStatus
    components: Dict[str, HealthStatus]
    metrics: Dict[str, Metric]
    issues: List[str]
    recommendations: List[str]
    last_check: datetime
    uptime_seconds: float
    
    def __post_init__(self):
        if not hasattr(self, 'issues'):
            self.issues = []
        if not hasattr(self, 'recommendations'):
            self.recommendations = []


class SystemMonitor:
    """    Comprehensive system monitoring
    
    Features:
    - Real-time system metrics collection
    - Resource utilization tracking
    - Performance monitoring
    - Health status assessment
    - Automatic anomaly detection
    - Alert generation
    - Historical data storage
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize system monitor"""        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Monitoring configuration
        self.monitoring_level = MonitoringLevel(self.config.get('level', 'standard'))
        self.collection_interval = self.config.get('collection_interval', 30)  # seconds
        self.retention_period = self.config.get('retention_period', 86400)  # 24 hours
        
        # Metrics storage
        self.metrics_history: Dict[str, List[Metric]] = {}
        self.current_metrics: Dict[str, Metric] = {}
        
        # Health tracking
        self.component_health: Dict[str, HealthStatus] = {}
        self.health_history: List[SystemHealth] = []
        
        # Thresholds and alerts
        self.thresholds = self.config.get('thresholds', {
            'cpu_usage_warning': 70.0,
            'cpu_usage_critical': 90.0,
            'memory_usage_warning': 80.0,
            'memory_usage_critical': 95.0,
            'disk_usage_warning': 85.0,
            'disk_usage_critical': 95.0,
            'response_time_warning': 1000.0,  # ms
            'response_time_critical': 5000.0,  # ms
        })
        
        # Monitoring state
        self.is_monitoring = False
        self.start_time = datetime.utcnow()
        self.monitoring_task = None
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
    
    async def start_monitoring(self) -> bool:
        """Start the monitoring system"""        try:
            self.logger.info("Starting system monitoring...")
            
            # Initialize monitoring components
            await self._initialize_monitoring()
            
            # Start collection loop
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("System monitoring started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            return False
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""        try:
            self.logger.info("Stopping system monitoring...")
            
            self.is_monitoring = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("System monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")
    
    async def get_current_metrics(self) -> Dict[str, Metric]:
        """Get current system metrics"""        try:
            metrics = {}
            
            # System metrics
            system_metrics = await self._collect_system_metrics()
            metrics.update(system_metrics)
            
            # Process metrics
            if self.monitoring_level in [MonitoringLevel.DETAILED, MonitoringLevel.DEBUG]:
                process_metrics = await self._collect_process_metrics()
                metrics.update(process_metrics)
            
            # Network metrics
            network_metrics = await self._collect_network_metrics()
            metrics.update(network_metrics)
            
            # Disk metrics
            disk_metrics = await self._collect_disk_metrics()
            metrics.update(disk_metrics)
            
            # Update current metrics
            self.current_metrics = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {str(e)}")
            return {}
    
    async def get_system_health(self) -> SystemHealth:
        """Get current system health status"""        try:
            # Collect current metrics
            metrics = await self.get_current_metrics()
            
            # Assess component health
            component_health = await self._assess_component_health(metrics)
            
            # Determine overall health
            overall_status = self._determine_overall_health(component_health)
            
            # Identify issues and recommendations
            issues = await self._identify_issues(metrics, component_health)
            recommendations = await self._generate_recommendations(issues, metrics)
            
            # Calculate uptime
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            health = SystemHealth(
                status=overall_status,
                components=component_health,
                metrics=metrics,
                issues=issues,
                recommendations=recommendations,
                last_check=datetime.utcnow(),
                uptime_seconds=uptime
            )
            
            # Store health history
            self.health_history.append(health)
            
            # Maintain history size
            if len(self.health_history) > 1000:
                self.health_history = self.health_history[-1000:]
            
            return health
            
        except Exception as e:
            self.logger.error(f"Failed to assess system health: {str(e)}")
            return SystemHealth(
                status=HealthStatus.UNKNOWN,
                components={},
                metrics={},
                issues=[f"Health assessment failed: {str(e)}"],
                recommendations=["Check system monitor logs"],
                last_check=datetime.utcnow(),
                uptime_seconds=0.0
            )
    
    async def get_metrics_history(
        self,
        metric_name: str,
        time_range_minutes: int = 60
    ) -> List[Metric]:
        """Get historical data for a specific metric"""        try:
            if metric_name not in self.metrics_history:
                return []
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
            
            return [
                metric for metric in self.metrics_history[metric_name]
                if metric.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics history: {str(e)}")
            return []
    
    async def add_alert_callback(self, callback: Callable):
        """Add callback for alert notifications"""        self.alert_callbacks.append(callback)
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary and statistics"""        try:
            current_metrics = self.current_metrics
            
            if not current_metrics:
                return {"error": "No metrics available"}
            
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_hours": (datetime.utcnow() - self.start_time).total_seconds() / 3600,
                "metrics_collected": len(current_metrics),
                "monitoring_level": self.monitoring_level.value,
            }
            
            # System performance
            if "cpu_usage" in current_metrics:
                summary["cpu_usage_percent"] = current_metrics["cpu_usage"].value
            
            if "memory_usage" in current_metrics:
                summary["memory_usage_percent"] = current_metrics["memory_usage"].value
            
            if "disk_usage" in current_metrics:
                summary["disk_usage_percent"] = current_metrics["disk_usage"].value
            
            # Performance trends (if history available)
            if self.health_history:
                recent_health = self.health_history[-10:]  # Last 10 checks
                healthy_count = sum(1 for h in recent_health if h.status == HealthStatus.HEALTHY)
                summary["health_stability_percent"] = (healthy_count / len(recent_health)) * 100
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance summary: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _initialize_monitoring(self):
        """Initialize monitoring components"""        # Set up initial component health
        self.component_health = {
            "cpu": HealthStatus.HEALTHY,
            "memory": HealthStatus.HEALTHY,
            "disk": HealthStatus.HEALTHY,
            "network": HealthStatus.HEALTHY,
            "processes": HealthStatus.HEALTHY
        }
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = await self.get_current_metrics()
                
                # Store metrics history
                await self._store_metrics_history(metrics)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self) -> Dict[str, Metric]:
        """Collect basic system metrics"""        metrics = {}
        now = datetime.utcnow()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage"] = Metric(
                name="cpu_usage",
                metric_type=MetricType.GAUGE,
                value=cpu_percent,
                unit="percent",
                timestamp=now,
                description="CPU utilization percentage"
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = Metric(
                name="memory_usage",
                metric_type=MetricType.GAUGE,
                value=memory.percent,
                unit="percent",
                timestamp=now,
                description="Memory utilization percentage"
            )
            
            metrics["memory_available_gb"] = Metric(
                name="memory_available_gb",
                metric_type=MetricType.GAUGE,
                value=memory.available / (1024**3),
                unit="GB",
                timestamp=now,
                description="Available memory in GB"
            )
            
            # Load average (Unix systems)
            try:
                load_avg = psutil.getloadavg()
                metrics["load_average_1m"] = Metric(
                    name="load_average_1m",
                    metric_type=MetricType.GAUGE,
                    value=load_avg[0],
                    unit="",
                    timestamp=now,
                    description="1-minute load average"
                )
            except (AttributeError, OSError):
                # Not available on all platforms
                pass
            
        except Exception as e:
            self.logger.warning(f"Failed to collect some system metrics: {str(e)}")
        
        return metrics
    
    async def _collect_process_metrics(self) -> Dict[str, Metric]:
        """Collect process-specific metrics"""        metrics = {}
        now = datetime.utcnow()
        
        try:
            # Current process info
            current_process = psutil.Process()
            
            # Process CPU usage
            metrics["process_cpu_percent"] = Metric(
                name="process_cpu_percent",
                metric_type=MetricType.GAUGE,
                value=current_process.cpu_percent(),
                unit="percent",
                timestamp=now,
                description="Current process CPU usage"
            )
            
            # Process memory usage
            memory_info = current_process.memory_info()
            metrics["process_memory_rss_mb"] = Metric(
                name="process_memory_rss_mb",
                metric_type=MetricType.GAUGE,
                value=memory_info.rss / (1024**2),
                unit="MB",
                timestamp=now,
                description="Process resident memory in MB"
            )
            
            # Number of threads
            metrics["process_threads"] = Metric(
                name="process_threads",
                metric_type=MetricType.GAUGE,
                value=current_process.num_threads(),
                unit="count",
                timestamp=now,
                description="Number of process threads"
            )
            
            # File descriptors (Unix)
            try:
                metrics["process_file_descriptors"] = Metric(
                    name="process_file_descriptors",
                    metric_type=MetricType.GAUGE,
                    value=current_process.num_fds(),
                    unit="count",
                    timestamp=now,
                    description="Number of open file descriptors"
                )
            except (AttributeError, OSError):
                pass
            
        except Exception as e:
            self.logger.warning(f"Failed to collect process metrics: {str(e)}")
        
        return metrics
    
    async def _collect_network_metrics(self) -> Dict[str, Metric]:
        """Collect network metrics"""        metrics = {}
        now = datetime.utcnow()
        
        try:
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            
            metrics["network_bytes_sent"] = Metric(
                name="network_bytes_sent",
                metric_type=MetricType.COUNTER,
                value=net_io.bytes_sent,
                unit="bytes",
                timestamp=now,
                description="Total bytes sent over network"
            )
            
            metrics["network_bytes_recv"] = Metric(
                name="network_bytes_recv",
                metric_type=MetricType.COUNTER,
                value=net_io.bytes_recv,
                unit="bytes",
                timestamp=now,
                description="Total bytes received over network"
            )
            
            # Connection count
            connections = psutil.net_connections()
            metrics["network_connections"] = Metric(
                name="network_connections",
                metric_type=MetricType.GAUGE,
                value=len(connections),
                unit="count",
                timestamp=now,
                description="Number of network connections"
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to collect network metrics: {str(e)}")
        
        return metrics
    
    async def _collect_disk_metrics(self) -> Dict[str, Metric]:
        """Collect disk metrics"""        metrics = {}
        now = datetime.utcnow()
        
        try:
            # Disk usage for root partition
            disk_usage = psutil.disk_usage('/')
            
            metrics["disk_usage"] = Metric(
                name="disk_usage",
                metric_type=MetricType.GAUGE,
                value=(disk_usage.used / disk_usage.total) * 100,
                unit="percent",
                timestamp=now,
                description="Disk usage percentage"
            )
            
            metrics["disk_free_gb"] = Metric(
                name="disk_free_gb",
                metric_type=MetricType.GAUGE,
                value=disk_usage.free / (1024**3),
                unit="GB",
                timestamp=now,
                description="Free disk space in GB"
            )
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics["disk_read_bytes"] = Metric(
                    name="disk_read_bytes",
                    metric_type=MetricType.COUNTER,
                    value=disk_io.read_bytes,
                    unit="bytes",
                    timestamp=now,
                    description="Total bytes read from disk"
                )
                
                metrics["disk_write_bytes"] = Metric(
                    name="disk_write_bytes",
                    metric_type=MetricType.COUNTER,
                    value=disk_io.write_bytes,
                    unit="bytes",
                    timestamp=now,
                    description="Total bytes written to disk"
                )
            
        except Exception as e:
            self.logger.warning(f"Failed to collect disk metrics: {str(e)}")
        
        return metrics
    
    async def _store_metrics_history(self, metrics: Dict[str, Metric]):
        """Store metrics in history"""        for metric_name, metric in metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []
            
            self.metrics_history[metric_name].append(metric)
            
            # Maintain history size
            max_history_size = 1000
            if len(self.metrics_history[metric_name]) > max_history_size:
                self.metrics_history[metric_name] = self.metrics_history[metric_name][-max_history_size:]
    
    async def _assess_component_health(self, metrics: Dict[str, Metric]) -> Dict[str, HealthStatus]:
        """Assess health of individual components"""        component_health = {}
        
        # CPU health
        if "cpu_usage" in metrics:
            cpu_usage = metrics["cpu_usage"].value
            if cpu_usage >= self.thresholds['cpu_usage_critical']:
                component_health["cpu"] = HealthStatus.CRITICAL
            elif cpu_usage >= self.thresholds['cpu_usage_warning']:
                component_health["cpu"] = HealthStatus.WARNING
            else:
                component_health["cpu"] = HealthStatus.HEALTHY
        
        # Memory health
        if "memory_usage" in metrics:
            memory_usage = metrics["memory_usage"].value
            if memory_usage >= self.thresholds['memory_usage_critical']:
                component_health["memory"] = HealthStatus.CRITICAL
            elif memory_usage >= self.thresholds['memory_usage_warning']:
                component_health["memory"] = HealthStatus.WARNING
            else:
                component_health["memory"] = HealthStatus.HEALTHY
        
        # Disk health
        if "disk_usage" in metrics:
            disk_usage = metrics["disk_usage"].value
            if disk_usage >= self.thresholds['disk_usage_critical']:
                component_health["disk"] = HealthStatus.CRITICAL
            elif disk_usage >= self.thresholds['disk_usage_warning']:
                component_health["disk"] = HealthStatus.WARNING
            else:
                component_health["disk"] = HealthStatus.HEALTHY
        
        # Network health (basic check)
        component_health["network"] = HealthStatus.HEALTHY
        
        return component_health
    
    def _determine_overall_health(self, component_health: Dict[str, HealthStatus]) -> HealthStatus:
        """Determine overall system health"""        if not component_health:
            return HealthStatus.UNKNOWN
        
        health_values = list(component_health.values())
        
        if HealthStatus.CRITICAL in health_values:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in health_values:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in health_values):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.DEGRADED
    
    async def _identify_issues(
        self,
        metrics: Dict[str, Metric],
        component_health: Dict[str, HealthStatus]
    ) -> List[str]:
        """Identify current system issues"""        issues = []
        
        for component, health in component_health.items():
            if health == HealthStatus.CRITICAL:
                issues.append(f"Critical: {component} performance is severely degraded")
            elif health == HealthStatus.WARNING:
                issues.append(f"Warning: {component} performance is degraded")
        
        return issues
    
    async def _generate_recommendations(
        self,
        issues: List[str],
        metrics: Dict[str, Metric]
    ) -> List[str]:
        """Generate recommendations based on issues"""        recommendations = []
        
        # CPU recommendations
        if "cpu_usage" in metrics and metrics["cpu_usage"].value > 80:
            recommendations.append("Consider optimizing CPU-intensive processes or scaling resources")
        
        # Memory recommendations
        if "memory_usage" in metrics and metrics["memory_usage"].value > 85:
            recommendations.append("Consider increasing memory allocation or optimizing memory usage")
        
        # Disk recommendations
        if "disk_usage" in metrics and metrics["disk_usage"].value > 90:
            recommendations.append("Clean up disk space or provision additional storage")
        
        if not recommendations:
            recommendations.append("System is performing within normal parameters")
        
        return recommendations
    
    async def _check_alerts(self, metrics: Dict[str, Metric]):
        """Check for alert conditions and trigger notifications"""        alerts = []
        
        # Check each metric against thresholds
        for metric_name, metric in metrics.items():
            if metric_name == "cpu_usage" and metric.value >= self.thresholds['cpu_usage_critical']:
                alerts.append({
                    "level": "critical",
                    "component": "cpu",
                    "message": f"CPU usage is {metric.value:.1f}%",
                    "metric": metric
                })
            elif metric_name == "memory_usage" and metric.value >= self.thresholds['memory_usage_critical']:
                alerts.append({
                    "level": "critical",
                    "component": "memory",
                    "message": f"Memory usage is {metric.value:.1f}%",
                    "metric": metric
                })
        
        # Trigger alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old metrics data"""        cutoff_time = datetime.utcnow() - timedelta(seconds=self.retention_period)
        
        for metric_name in list(self.metrics_history.keys()):
            self.metrics_history[metric_name] = [
                metric for metric in self.metrics_history[metric_name]
                if metric.timestamp >= cutoff_time
            ]
            
            # Remove empty entries
            if not self.metrics_history[metric_name]:
                del self.metrics_history[metric_name]


class PerformanceMonitor:
    """Monitor application performance metrics"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.response_times: List[float] = []
        self.error_counts: Dict[str, int] = {}
        self.request_counts: Dict[str, int] = {}
    
    async def record_request(self, endpoint: str, response_time_ms: float, status_code: int):
        """Record a request for performance tracking"""        # Record response time
        self.response_times.append(response_time_ms)
        
        # Maintain response time history size
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Count requests
        if endpoint not in self.request_counts:
            self.request_counts[endpoint] = 0
        self.request_counts[endpoint] += 1
        
        # Count errors
        if status_code >= 400:
            if endpoint not in self.error_counts:
                self.error_counts[endpoint] = 0
            self.error_counts[endpoint] += 1
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""        if not self.response_times:
            return {"error": "No performance data available"}
        
        return {
            "avg_response_time_ms": sum(self.response_times) / len(self.response_times),
            "min_response_time_ms": min(self.response_times),
            "max_response_time_ms": max(self.response_times),
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "error_rate_percent": (sum(self.error_counts.values()) / sum(self.request_counts.values())) * 100 if self.request_counts else 0,
            "endpoints": dict(self.request_counts)
        }


class ResourceMonitor:
    """Monitor resource usage and allocation"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    async def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_usage_per_core": psutil.cpu_percent(percpu=True),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "disk_total_gb": psutil.disk_usage('/').total / (1024**3),
                "disk_free_gb": psutil.disk_usage('/').free / (1024**3),
                "network_connections": len(psutil.net_connections()),
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {str(e)}")
            return {"error": str(e)}
