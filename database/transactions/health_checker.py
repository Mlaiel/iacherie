"""Health Checker - Transaction System Health Monitoring

Enterprise-grade health monitoring system providing comprehensive health checks,
performance monitoring, and system diagnostics for the IA Influencer platform's
transaction infrastructure with creator economy specific metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import asyncio
import psutil
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
from collections import deque, defaultdict
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading
import socket
import subprocess
import platform
import gc

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""    HEALTHY = "HEALTHY"         # All systems operating normally
    WARNING = "WARNING"         # Some issues detected but system functional
    CRITICAL = "CRITICAL"       # Critical issues requiring immediate attention
    DEGRADED = "DEGRADED"       # System performance degraded
    FAILED = "FAILED"           # System failure detected
    UNKNOWN = "UNKNOWN"         # Health status cannot be determined


class MetricType(Enum):
    """Types of health metrics"""    COUNTER = "COUNTER"         # Monotonically increasing value
    GAUGE = "GAUGE"             # Current value
    HISTOGRAM = "HISTOGRAM"     # Distribution of values
    TIMER = "TIMER"             # Time measurements
    PERCENTAGE = "PERCENTAGE"   # Percentage values (0-100)


@dataclass
class HealthMetric:
    """Individual health metric"""    name: str
    value: float
    metric_type: MetricType
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: Dict[str, str] = field(default_factory=dict)
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    @property
    def status(self) -> HealthStatus:
        """Determine health status based on thresholds"""        if self.threshold_critical is not None and self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.threshold_warning is not None and self.value >= self.threshold_warning:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'name': self.name,
            'value': self.value,
            'metric_type': self.metric_type.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'threshold_warning': self.threshold_warning,
            'threshold_critical': self.threshold_critical,
            'status': self.status.value,
        }


@dataclass
class HealthCheckResult:
    """Result of a health check"""    check_name: str
    status: HealthStatus
    message: str
    metrics: List[HealthMetric] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration: float = 0.0  # Check duration in seconds
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'check_name': self.check_name,
            'status': self.status.value,
            'message': self.message,
            'metrics': [metric.to_dict() for metric in self.metrics],
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'error': self.error,
            'details': self.details,
        }


@dataclass
class SystemHealthReport:
    """Comprehensive system health report"""    overall_status: HealthStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    check_results: List[HealthCheckResult] = field(default_factory=list)
    summary_metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    uptime: float = 0.0
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'overall_status': self.overall_status.value,
            'timestamp': self.timestamp.isoformat(),
            'check_results': [result.to_dict() for result in self.check_results],
            'summary_metrics': self.summary_metrics,
            'recommendations': self.recommendations,
            'uptime': self.uptime,
            'version': self.version,
        }


class MetricsCollector:
    """Metrics collection and aggregation system"""    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.RLock()
        
    def record_metric(self, metric: HealthMetric) -> None:
        """Record a metric value"""        with self.lock:
            self.metrics_history[metric.name].append({
                'value': metric.value,
                'timestamp': metric.timestamp,
                'labels': metric.labels.copy(),
            })
    
    def get_metric_history(self, metric_name: str, duration: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Get metric history for specified duration"""        with self.lock:
            history = list(self.metrics_history[metric_name])
            
            if duration:
                cutoff = datetime.now(timezone.utc) - duration
                history = [
                    entry for entry in history
                    if entry['timestamp'] >= cutoff
                ]
            
            return history
    
    def get_metric_statistics(self, metric_name: str, duration: Optional[timedelta] = None) -> Dict[str, float]:
        """Get statistical analysis of metric"""        history = self.get_metric_history(metric_name, duration)
        
        if not history:
            return {}
        
        values = [entry['value'] for entry in history]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'p95': statistics.quantiles(values, n=20)[18] if len(values) > 1 else values[0],
            'p99': statistics.quantiles(values, n=100)[98] if len(values) > 1 else values[0],
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""        with self.lock:
            all_metrics = {}
            
            for metric_name, history in self.metrics_history.items():
                if history:
                    latest = history[-1]
                    stats = self.get_metric_statistics(metric_name, timedelta(minutes=5))
                    
                    all_metrics[metric_name] = {
                        'current_value': latest['value'],
                        'last_updated': latest['timestamp'].isoformat(),
                        'labels': latest['labels'],
                        'statistics': stats,
                    }
            
            return all_metrics


class TransactionHealthChecker:
    """    Comprehensive transaction system health checker
    
    Features:
    - Real-time system monitoring
    - Performance metrics collection
    - Creator economy specific health checks
    - Predictive health analysis
    - Automated recommendations
    - Historical trend analysis
    - Resource utilization monitoring
    - Business metrics tracking
    """    
    def __init__(
        self,
        check_interval: float = 30.0,
        metrics_retention: int = 10000,
        enable_system_monitoring: bool = True
    ):
        self.check_interval = check_interval
        self.metrics_retention = metrics_retention
        self.enable_system_monitoring = enable_system_monitoring
        
        # Core components
        self.metrics_collector = MetricsCollector(metrics_retention)
        
        # Health checks registry
        self.health_checks: Dict[str, Callable] = {}
        self.check_results_history: deque = deque(maxlen=100)
        
        # System monitoring
        self.system_start_time = time.time()
        self.last_health_report: Optional[SystemHealthReport] = None
        
        # Performance tracking
        self.performance_thresholds = {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'transaction_throughput': {'warning': 100.0, 'critical': 50.0},  # transactions per second
            'error_rate': {'warning': 5.0, 'critical': 10.0},  # percentage
            'response_time': {'warning': 1000.0, 'critical': 3000.0},  # milliseconds
        }
        
        # Business metrics tracking
        self.business_metrics = {
            'active_creators': 0,
            'content_processed': 0,
            'revenue_generated': 0.0,
            'violations_detected': 0,
            'collaborations_matched': 0,
        }
        
        # Background monitoring
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._monitoring = True
        
        # Register default health checks
        self._register_default_checks()
        
        # Start monitoring tasks
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._metrics_collection_loop())
        
        logger.info("TransactionHealthChecker initialized with interval: %.1fs", check_interval)
    
    def register_health_check(self, name: str, check_function: Callable) -> None:
        """Register a custom health check function"""        self.health_checks[name] = check_function
        logger.debug("Registered health check: %s", name)
    
    def record_business_metric(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record business metric"""        metric = HealthMetric(
            name=f"business.{metric_name}",
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc)
        )
        
        self.metrics_collector.record_metric(metric)
        
        # Update business metrics cache
        if metric_name in self.business_metrics:
            self.business_metrics[metric_name] = value
    
    def record_transaction_metric(
        self,
        transaction_id: str,
        metric_name: str,
        value: float,
        creator_id: Optional[str] = None
    ) -> None:
        """Record transaction-specific metric"""        labels = {'transaction_id': transaction_id}
        if creator_id:
            labels['creator_id'] = creator_id
        
        metric = HealthMetric(
            name=f"transaction.{metric_name}",
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels,
            timestamp=datetime.now(timezone.utc)
        )
        
        self.metrics_collector.record_metric(metric)
    
    async def run_health_check(self, check_name: str) -> HealthCheckResult:
        """Run specific health check"""        if check_name not in self.health_checks:
            return HealthCheckResult(
                check_name=check_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{check_name}' not found",
                error="Health check not registered"
            )
        
        start_time = time.time()
        
        try:
            check_function = self.health_checks[check_name]
            
            # Run check function
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, check_function
                )
            
            if isinstance(result, HealthCheckResult):
                result.duration = time.time() - start_time
                return result
            else:
                # Convert simple result to HealthCheckResult
                return HealthCheckResult(
                    check_name=check_name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.FAILED,
                    message=f"Check '{check_name}' {'passed' if result else 'failed'}",
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            logger.error("Health check '%s' failed: %s", check_name, str(e))
            return HealthCheckResult(
                check_name=check_name,
                status=HealthStatus.FAILED,
                message=f"Health check failed: {str(e)}",
                error=str(e),
                duration=time.time() - start_time
            )
    
    async def run_all_health_checks(self) -> SystemHealthReport:
        """Run all registered health checks"""        start_time = time.time()
        check_results = []
        
        # Run all health checks
        for check_name in self.health_checks:
            result = await self.run_health_check(check_name)
            check_results.append(result)
        
        # Determine overall status
        overall_status = self._determine_overall_status(check_results)
        
        # Generate summary metrics
        summary_metrics = self._generate_summary_metrics(check_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(check_results)
        
        # Create health report
        report = SystemHealthReport(
            overall_status=overall_status,
            check_results=check_results,
            summary_metrics=summary_metrics,
            recommendations=recommendations,
            uptime=time.time() - self.system_start_time
        )
        
        # Store report
        self.last_health_report = report
        self.check_results_history.append(report)
        
        logger.info("Health check completed: %s (duration=%.3fs, checks=%d)",
                   overall_status.value, time.time() - start_time, len(check_results))
        
        return report
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""        
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime': time.time() - self.system_start_time,
            'last_health_status': self.last_health_report.overall_status.value if self.last_health_report else 'UNKNOWN',
        }
        
        # Add system metrics
        if self.enable_system_monitoring:
            metrics.update(await self._collect_system_metrics())
        
        # Add business metrics
        metrics['business_metrics'] = self.business_metrics.copy()
        
        # Add performance metrics
        metrics['performance_metrics'] = self._collect_performance_metrics()
        
        # Add historical trends
        metrics['trends'] = self._calculate_trends()
        
        return metrics
    
    async def get_creator_health_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get health metrics specific to a creator"""        
        creator_metrics = {
            'creator_id': creator_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {},
        }
        
        # Get creator-specific metrics from history
        all_metrics = self.metrics_collector.get_all_metrics()
        
        for metric_name, metric_data in all_metrics.items():
            labels = metric_data.get('labels', {})
            if labels.get('creator_id') == creator_id:
                creator_metrics['metrics'][metric_name] = metric_data
        
        # Calculate creator-specific health score
        creator_metrics['health_score'] = self._calculate_creator_health_score(creator_id)
        
        return creator_metrics
    
    async def get_content_protection_health(self) -> Dict[str, Any]:
        """Get content protection system health metrics"""        
        protection_metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {},
        }
        
        # Get content protection specific metrics
        all_metrics = self.metrics_collector.get_all_metrics()
        
        for metric_name, metric_data in all_metrics.items():
            if 'content_protection' in metric_name or 'fingerprint' in metric_name:
                protection_metrics['metrics'][metric_name] = metric_data
        
        # Calculate protection effectiveness
        protection_metrics['effectiveness_score'] = self._calculate_protection_effectiveness()
        
        return protection_metrics
    
    async def get_revenue_system_health(self) -> Dict[str, Any]:
        """Get revenue system health metrics"""        
        revenue_metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {},
        }
        
        # Get revenue-specific metrics
        all_metrics = self.metrics_collector.get_all_metrics()
        
        for metric_name, metric_data in all_metrics.items():
            if 'revenue' in metric_name or 'payment' in metric_name or 'monetization' in metric_name:
                revenue_metrics['metrics'][metric_name] = metric_data
        
        # Calculate revenue system reliability
        revenue_metrics['reliability_score'] = self._calculate_revenue_reliability()
        
        return revenue_metrics
    
    def _register_default_checks(self) -> None:
        """Register default health checks"""        
        self.health_checks.update({
            'system_resources': self._check_system_resources,
            'database_connectivity': self._check_database_connectivity,
            'transaction_coordinator': self._check_transaction_coordinator,
            'memory_usage': self._check_memory_usage,
            'disk_space': self._check_disk_space,
            'network_connectivity': self._check_network_connectivity,
            'creator_system': self._check_creator_system,
            'content_protection': self._check_content_protection,
            'revenue_system': self._check_revenue_system,
            'performance_metrics': self._check_performance_metrics,
        })
    
    async def _check_system_resources(self) -> HealthCheckResult:
        """Check system resource utilization"""        
        metrics = []
        status = HealthStatus.HEALTHY
        messages = []
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metric = HealthMetric(
                name="system.cpu_usage",
                value=cpu_percent,
                metric_type=MetricType.PERCENTAGE,
                unit="%",
                threshold_warning=self.performance_thresholds['cpu_usage']['warning'],
                threshold_critical=self.performance_thresholds['cpu_usage']['critical']
            )
            metrics.append(cpu_metric)
            
            if cpu_metric.status != HealthStatus.HEALTHY:
                status = max(status, cpu_metric.status, key=lambda x: x.value)
                messages.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_metric = HealthMetric(
                name="system.memory_usage",
                value=memory.percent,
                metric_type=MetricType.PERCENTAGE,
                unit="%",
                threshold_warning=self.performance_thresholds['memory_usage']['warning'],
                threshold_critical=self.performance_thresholds['memory_usage']['critical']
            )
            metrics.append(memory_metric)
            
            if memory_metric.status != HealthStatus.HEALTHY:
                status = max(status, memory_metric.status, key=lambda x: x.value)
                messages.append(f"High memory usage: {memory.percent:.1f}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_metric = HealthMetric(
                name="system.disk_usage",
                value=disk_percent,
                metric_type=MetricType.PERCENTAGE,
                unit="%",
                threshold_warning=self.performance_thresholds['disk_usage']['warning'],
                threshold_critical=self.performance_thresholds['disk_usage']['critical']
            )
            metrics.append(disk_metric)
            
            if disk_metric.status != HealthStatus.HEALTHY:
                status = max(status, disk_metric.status, key=lambda x: x.value)
                messages.append(f"High disk usage: {disk_percent:.1f}%")
            
            # Load average (Unix systems)
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()[0]  # 1-minute load average
                cpu_count = psutil.cpu_count()
                load_percent = (load_avg / cpu_count) * 100
                
                load_metric = HealthMetric(
                    name="system.load_average",
                    value=load_percent,
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    threshold_warning=80.0,
                    threshold_critical=120.0
                )
                metrics.append(load_metric)
                
                if load_metric.status != HealthStatus.HEALTHY:
                    status = max(status, load_metric.status, key=lambda x: x.value)
                    messages.append(f"High load average: {load_avg:.2f}")
            
            message = "System resources healthy" if status == HealthStatus.HEALTHY else "; ".join(messages)
            
            return HealthCheckResult(
                check_name="system_resources",
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="system_resources",
                status=HealthStatus.FAILED,
                message=f"Failed to check system resources: {str(e)}",
                error=str(e)
            )
    
    async def _check_database_connectivity(self) -> HealthCheckResult:
        """Check database connectivity and performance"""        
        try:
            start_time = time.time()
            
            # Mock database connectivity check
            # In a real implementation, this would test actual database connections
            await asyncio.sleep(0.01)  # Simulate database query
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            metrics = [
                HealthMetric(
                    name="database.response_time",
                    value=response_time,
                    metric_type=MetricType.TIMER,
                    unit="ms",
                    threshold_warning=100.0,
                    threshold_critical=500.0
                ),
                HealthMetric(
                    name="database.connections_active",
                    value=10,  # Mock value
                    metric_type=MetricType.GAUGE,
                    unit="connections",
                    threshold_warning=50,
                    threshold_critical=80
                )
            ]
            
            status = HealthStatus.HEALTHY
            if response_time > 500:
                status = HealthStatus.CRITICAL
            elif response_time > 100:
                status = HealthStatus.WARNING
            
            return HealthCheckResult(
                check_name="database_connectivity",
                status=status,
                message=f"Database responsive in {response_time:.1f}ms",
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="database_connectivity",
                status=HealthStatus.FAILED,
                message=f"Database connectivity failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_transaction_coordinator(self) -> HealthCheckResult:
        """Check transaction coordinator health"""        
        try:
            # Mock transaction coordinator metrics
            active_transactions = 25  # Mock value
            throughput = 150.0  # transactions per second
            error_rate = 2.5  # percentage
            
            metrics = [
                HealthMetric(
                    name="transaction.active_count",
                    value=active_transactions,
                    metric_type=MetricType.GAUGE,
                    unit="transactions",
                    threshold_warning=100,
                    threshold_critical=200
                ),
                HealthMetric(
                    name="transaction.throughput",
                    value=throughput,
                    metric_type=MetricType.GAUGE,
                    unit="tx/sec",
                    threshold_warning=self.performance_thresholds['transaction_throughput']['warning'],
                    threshold_critical=self.performance_thresholds['transaction_throughput']['critical']
                ),
                HealthMetric(
                    name="transaction.error_rate",
                    value=error_rate,
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    threshold_warning=self.performance_thresholds['error_rate']['warning'],
                    threshold_critical=self.performance_thresholds['error_rate']['critical']
                )
            ]
            
            status = HealthStatus.HEALTHY
            messages = []
            
            for metric in metrics:
                if metric.status != HealthStatus.HEALTHY:
                    status = max(status, metric.status, key=lambda x: x.value)
                    messages.append(f"{metric.name}: {metric.value}")
            
            message = "Transaction coordinator healthy" if status == HealthStatus.HEALTHY else "; ".join(messages)
            
            return HealthCheckResult(
                check_name="transaction_coordinator",
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="transaction_coordinator",
                status=HealthStatus.FAILED,
                message=f"Transaction coordinator check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_memory_usage(self) -> HealthCheckResult:
        """Check detailed memory usage"""        
        try:
            # Process memory info
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Python garbage collection stats
            gc_stats = gc.get_stats()
            gc_count = sum(stat['collections'] for stat in gc_stats)
            
            metrics = [
                HealthMetric(
                    name="memory.process_rss",
                    value=memory_info.rss / 1024 / 1024,  # Convert to MB
                    metric_type=MetricType.GAUGE,
                    unit="MB"
                ),
                HealthMetric(
                    name="memory.process_vms",
                    value=memory_info.vms / 1024 / 1024,  # Convert to MB
                    metric_type=MetricType.GAUGE,
                    unit="MB"
                ),
                HealthMetric(
                    name="memory.process_percent",
                    value=memory_percent,
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    threshold_warning=50.0,
                    threshold_critical=80.0
                ),
                HealthMetric(
                    name="memory.gc_collections",
                    value=gc_count,
                    metric_type=MetricType.COUNTER,
                    unit="collections"
                )
            ]
            
            status = HealthStatus.HEALTHY
            if memory_percent > 80:
                status = HealthStatus.CRITICAL
            elif memory_percent > 50:
                status = HealthStatus.WARNING
            
            return HealthCheckResult(
                check_name="memory_usage",
                status=status,
                message=f"Process memory usage: {memory_percent:.1f}%",
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="memory_usage",
                status=HealthStatus.FAILED,
                message=f"Memory usage check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_disk_space(self) -> HealthCheckResult:
        """Check disk space across mounted filesystems"""        
        try:
            metrics = []
            status = HealthStatus.HEALTHY
            messages = []
            
            # Check all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    usage_percent = (usage.used / usage.total) * 100
                    
                    metric = HealthMetric(
                        name=f"disk.usage_{partition.device.replace('/', '_')}",
                        value=usage_percent,
                        metric_type=MetricType.PERCENTAGE,
                        unit="%",
                        labels={'mountpoint': partition.mountpoint, 'device': partition.device},
                        threshold_warning=85.0,
                        threshold_critical=95.0
                    )
                    metrics.append(metric)
                    
                    if metric.status != HealthStatus.HEALTHY:
                        status = max(status, metric.status, key=lambda x: x.value)
                        messages.append(f"{partition.mountpoint}: {usage_percent:.1f}%")
                        
                except PermissionError:
                    # Skip inaccessible partitions
                    continue
            
            message = "Disk space healthy" if status == HealthStatus.HEALTHY else "; ".join(messages)
            
            return HealthCheckResult(
                check_name="disk_space",
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="disk_space",
                status=HealthStatus.FAILED,
                message=f"Disk space check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_network_connectivity(self) -> HealthCheckResult:
        """Check network connectivity"""        
        try:
            # Test network connectivity by checking socket creation
            start_time = time.time()
            
            # Test local connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', 80))  # Test local connection
            sock.close()
            
            response_time = (time.time() - start_time) * 1000
            
            # Get network I/O stats
            net_io = psutil.net_io_counters()
            
            metrics = [
                HealthMetric(
                    name="network.connectivity_time",
                    value=response_time,
                    metric_type=MetricType.TIMER,
                    unit="ms"
                ),
                HealthMetric(
                    name="network.bytes_sent",
                    value=net_io.bytes_sent,
                    metric_type=MetricType.COUNTER,
                    unit="bytes"
                ),
                HealthMetric(
                    name="network.bytes_received",
                    value=net_io.bytes_recv,
                    metric_type=MetricType.COUNTER,
                    unit="bytes"
                ),
                HealthMetric(
                    name="network.packets_sent",
                    value=net_io.packets_sent,
                    metric_type=MetricType.COUNTER,
                    unit="packets"
                ),
                HealthMetric(
                    name="network.packets_received",
                    value=net_io.packets_recv,
                    metric_type=MetricType.COUNTER,
                    unit="packets"
                )
            ]
            
            status = HealthStatus.HEALTHY if result == 0 else HealthStatus.WARNING
            message = "Network connectivity OK" if result == 0 else "Network connectivity issues detected"
            
            return HealthCheckResult(
                check_name="network_connectivity",
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="network_connectivity",
                status=HealthStatus.FAILED,
                message=f"Network connectivity check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_creator_system(self) -> HealthCheckResult:
        """Check creator economy system health"""        
        try:
            # Mock creator system metrics
            active_creators = self.business_metrics.get('active_creators', 0)
            content_processed = self.business_metrics.get('content_processed', 0)
            collaborations = self.business_metrics.get('collaborations_matched', 0)
            
            metrics = [
                HealthMetric(
                    name="creator.active_count",
                    value=active_creators,
                    metric_type=MetricType.GAUGE,
                    unit="creators"
                ),
                HealthMetric(
                    name="creator.content_processed",
                    value=content_processed,
                    metric_type=MetricType.COUNTER,
                    unit="content_items"
                ),
                HealthMetric(
                    name="creator.collaborations_matched",
                    value=collaborations,
                    metric_type=MetricType.COUNTER,
                    unit="collaborations"
                )
            ]
            
            # Determine status based on activity levels
            status = HealthStatus.HEALTHY
            if active_creators == 0:
                status = HealthStatus.WARNING
            
            return HealthCheckResult(
                check_name="creator_system",
                status=status,
                message=f"Creator system: {active_creators} active creators, {content_processed} content processed",
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="creator_system",
                status=HealthStatus.FAILED,
                message=f"Creator system check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_content_protection(self) -> HealthCheckResult:
        """Check content protection system health"""        
        try:
            # Mock content protection metrics
            violations_detected = self.business_metrics.get('violations_detected', 0)
            protection_rate = 95.5  # Mock percentage
            fingerprint_speed = 150.0  # Mock fingerprints per second
            
            metrics = [
                HealthMetric(
                    name="protection.violations_detected",
                    value=violations_detected,
                    metric_type=MetricType.COUNTER,
                    unit="violations"
                ),
                HealthMetric(
                    name="protection.effectiveness_rate",
                    value=protection_rate,
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    threshold_warning=90.0,
                    threshold_critical=80.0
                ),
                HealthMetric(
                    name="protection.fingerprint_speed",
                    value=fingerprint_speed,
                    metric_type=MetricType.GAUGE,
                    unit="fp/sec",
                    threshold_warning=100.0,
                    threshold_critical=50.0
                )
            ]
            
            status = HealthStatus.HEALTHY
            if protection_rate < 80:
                status = HealthStatus.CRITICAL
            elif protection_rate < 90:
                status = HealthStatus.WARNING
            
            return HealthCheckResult(
                check_name="content_protection",
                status=status,
                message=f"Content protection: {protection_rate:.1f}% effectiveness, {violations_detected} violations detected",
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="content_protection",
                status=HealthStatus.FAILED,
                message=f"Content protection check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_revenue_system(self) -> HealthCheckResult:
        """Check revenue system health"""        
        try:
            # Mock revenue system metrics
            revenue_generated = self.business_metrics.get('revenue_generated', 0.0)
            payment_success_rate = 98.5  # Mock percentage
            processing_time = 2.5  # Mock seconds
            
            metrics = [
                HealthMetric(
                    name="revenue.total_generated",
                    value=revenue_generated,
                    metric_type=MetricType.COUNTER,
                    unit="EUR"
                ),
                HealthMetric(
                    name="revenue.payment_success_rate",
                    value=payment_success_rate,
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    threshold_warning=95.0,
                    threshold_critical=90.0
                ),
                HealthMetric(
                    name="revenue.processing_time",
                    value=processing_time,
                    metric_type=MetricType.TIMER,
                    unit="seconds",
                    threshold_warning=5.0,
                    threshold_critical=10.0
                )
            ]
            
            status = HealthStatus.HEALTHY
            if payment_success_rate < 90:
                status = HealthStatus.CRITICAL
            elif payment_success_rate < 95:
                status = HealthStatus.WARNING
            
            return HealthCheckResult(
                check_name="revenue_system",
                status=status,
                message=f"Revenue system: {payment_success_rate:.1f}% payment success rate, €{revenue_generated:.2f} generated",
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="revenue_system",
                status=HealthStatus.FAILED,
                message=f"Revenue system check failed: {str(e)}",
                error=str(e)
            )
    
    async def _check_performance_metrics(self) -> HealthCheckResult:
        """Check overall performance metrics"""        
        try:
            # Calculate recent performance statistics
            recent_stats = self._calculate_recent_performance()
            
            metrics = [
                HealthMetric(
                    name="performance.average_response_time",
                    value=recent_stats.get('avg_response_time', 0),
                    metric_type=MetricType.TIMER,
                    unit="ms",
                    threshold_warning=1000.0,
                    threshold_critical=3000.0
                ),
                HealthMetric(
                    name="performance.throughput",
                    value=recent_stats.get('throughput', 0),
                    metric_type=MetricType.GAUGE,
                    unit="ops/sec"
                ),
                HealthMetric(
                    name="performance.error_rate",
                    value=recent_stats.get('error_rate', 0),
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    threshold_warning=5.0,
                    threshold_critical=10.0
                )
            ]
            
            status = HealthStatus.HEALTHY
            for metric in metrics:
                if metric.status != HealthStatus.HEALTHY:
                    status = max(status, metric.status, key=lambda x: x.value)
            
            return HealthCheckResult(
                check_name="performance_metrics",
                status=status,
                message=f"Performance: {recent_stats.get('avg_response_time', 0):.1f}ms avg response time",
                metrics=metrics
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="performance_metrics",
                status=HealthStatus.FAILED,
                message=f"Performance metrics check failed: {str(e)}",
                error=str(e)
            )
    
    def _determine_overall_status(self, check_results: List[HealthCheckResult]) -> HealthStatus:
        """Determine overall system health status"""        
        if not check_results:
            return HealthStatus.UNKNOWN
        
        status_counts = defaultdict(int)
        for result in check_results:
            status_counts[result.status] += 1
        
        # Determine overall status based on individual check results
        if status_counts[HealthStatus.FAILED] > 0:
            return HealthStatus.FAILED
        elif status_counts[HealthStatus.CRITICAL] > 0:
            return HealthStatus.CRITICAL
        elif status_counts[HealthStatus.WARNING] > len(check_results) * 0.3:  # More than 30% warnings
            return HealthStatus.DEGRADED
        elif status_counts[HealthStatus.WARNING] > 0:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def _generate_summary_metrics(self, check_results: List[HealthCheckResult]) -> Dict[str, float]:
        """Generate summary metrics from check results"""        
        total_checks = len(check_results)
        healthy_checks = sum(1 for result in check_results if result.status == HealthStatus.HEALTHY)
        
        return {
            'total_checks': total_checks,
            'healthy_checks': healthy_checks,
            'health_percentage': (healthy_checks / total_checks * 100) if total_checks > 0 else 0,
            'average_check_duration': statistics.mean([result.duration for result in check_results]) if check_results else 0,
            'uptime_hours': (time.time() - self.system_start_time) / 3600,
        }
    
    def _generate_recommendations(self, check_results: List[HealthCheckResult]) -> List[str]:
        """Generate health recommendations based on check results"""        
        recommendations = []
        
        for result in check_results:
            if result.status == HealthStatus.CRITICAL:
                recommendations.append(f"CRITICAL: {result.check_name} - {result.message}")
            elif result.status == HealthStatus.WARNING:
                recommendations.append(f"WARNING: {result.check_name} - {result.message}")
            elif result.status == HealthStatus.FAILED:
                recommendations.append(f"FAILED: {result.check_name} - {result.message}")
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("System is healthy - no immediate action required")
        else:
            recommendations.append("Review and address the issues listed above")
            recommendations.append("Consider scaling resources if performance issues persist")
        
        return recommendations
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect detailed system metrics"""        
        try:
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            
            # Network information
            network_io = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None,
                    'usage_percent': psutil.cpu_percent(),
                },
                'memory': {
                    'total_gb': memory.total / 1024 / 1024 / 1024,
                    'available_gb': memory.available / 1024 / 1024 / 1024,
                    'used_percent': memory.percent,
                },
                'swap': {
                    'total_gb': swap.total / 1024 / 1024 / 1024,
                    'used_percent': swap.percent,
                },
                'disk': {
                    'total_gb': disk_usage.total / 1024 / 1024 / 1024,
                    'free_gb': disk_usage.free / 1024 / 1024 / 1024,
                    'used_percent': (disk_usage.used / disk_usage.total) * 100,
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_received': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_received': network_io.packets_recv,
                },
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'architecture': platform.architecture()[0],
                }
            }
            
        except Exception as e:
            logger.error("Error collecting system metrics: %s", str(e))
            return {}
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""        
        # Get recent performance statistics
        recent_stats = self._calculate_recent_performance()
        
        # Get metric statistics for key performance indicators
        metrics = {}
        for metric_name in ['transaction.throughput', 'transaction.error_rate', 'system.cpu_usage']:
            stats = self.metrics_collector.get_metric_statistics(metric_name, timedelta(minutes=5))
            if stats:
                metrics[metric_name] = stats
        
        return {
            'recent_performance': recent_stats,
            'metric_statistics': metrics,
        }
    
    def _calculate_recent_performance(self) -> Dict[str, float]:
        """Calculate recent performance statistics"""        
        # Mock performance calculations
        # In a real implementation, this would analyze actual metrics
        return {
            'avg_response_time': 150.0,  # milliseconds
            'throughput': 250.0,  # operations per second
            'error_rate': 1.5,  # percentage
            'availability': 99.95,  # percentage
        }
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate performance trends"""        
        trends = {}
        
        # Calculate trends for key metrics
        for metric_name in ['system.cpu_usage', 'system.memory_usage', 'transaction.throughput']:
            history = self.metrics_collector.get_metric_history(metric_name, timedelta(hours=1))
            
            if len(history) >= 2:
                recent_values = [entry['value'] for entry in history[-10:]]  # Last 10 values
                older_values = [entry['value'] for entry in history[-20:-10]]  # Previous 10 values
                
                if recent_values and older_values:
                    recent_avg = statistics.mean(recent_values)
                    older_avg = statistics.mean(older_values)
                    
                    if recent_avg > older_avg * 1.1:
                        trends[metric_name] = "INCREASING"
                    elif recent_avg < older_avg * 0.9:
                        trends[metric_name] = "DECREASING"
                    else:
                        trends[metric_name] = "STABLE"
                else:
                    trends[metric_name] = "UNKNOWN"
            else:
                trends[metric_name] = "INSUFFICIENT_DATA"
        
        return trends
    
    def _calculate_creator_health_score(self, creator_id: str) -> float:
        """Calculate health score for specific creator"""        
        # Mock health score calculation
        # In a real implementation, this would analyze creator-specific metrics
        return 85.5  # Mock score (0-100)
    
    def _calculate_protection_effectiveness(self) -> float:
        """Calculate content protection effectiveness score"""        
        # Mock effectiveness calculation
        return 92.3  # Mock score (0-100)
    
    def _calculate_revenue_reliability(self) -> float:
        """Calculate revenue system reliability score"""        
        # Mock reliability calculation
        return 97.8  # Mock score (0-100)
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""        
        while self._monitoring:
            try:
                # Run full health check
                await self.run_all_health_checks()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop: %s", str(e))
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""        
        while self._monitoring:
            try:
                # Collect and record system metrics
                if self.enable_system_monitoring:
                    system_metrics = await self._collect_system_metrics()
                    
                    # Record key system metrics
                    if 'cpu' in system_metrics:
                        self.record_business_metric('system_cpu_usage', system_metrics['cpu']['usage_percent'])
                    
                    if 'memory' in system_metrics:
                        self.record_business_metric('system_memory_usage', system_metrics['memory']['used_percent'])
                
                await asyncio.sleep(10)  # Collect metrics every 10 seconds
                
            except Exception as e:
                logger.error("Error in metrics collection loop: %s", str(e))
                await asyncio.sleep(5)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of health checker"""        logger.info("Shutting down TransactionHealthChecker...")
        
        self._monitoring = False
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("TransactionHealthChecker shutdown complete")


# Convenience functions for common health patterns
async def quick_health_check(health_checker: TransactionHealthChecker) -> bool:
    """Quick health check returning simple boolean"""    
    report = await health_checker.run_all_health_checks()
    return report.overall_status in [HealthStatus.HEALTHY, HealthStatus.WARNING]


async def get_system_status(health_checker: TransactionHealthChecker) -> Dict[str, str]:
    """Get simplified system status"""    
    report = await health_checker.run_all_health_checks()
    
    return {
        'status': report.overall_status.value,
        'message': f"{len([r for r in report.check_results if r.status == HealthStatus.HEALTHY])}/{len(report.check_results)} checks healthy",
        'uptime': f"{report.uptime/3600:.1f} hours",
        'last_check': report.timestamp.isoformat(),
    }


async def check_creator_health(health_checker: TransactionHealthChecker, creator_id: str) -> Dict[str, Any]:
    """Check health for specific creator"""    
    return await health_checker.get_creator_health_metrics(creator_id)
