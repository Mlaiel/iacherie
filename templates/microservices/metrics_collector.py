"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Metrics Collector for IA Chérie Microservices Platform
===================================================

Enterprise-grade metrics collection and monitoring providing:
- Prometheus metrics integration
- Custom metrics definition and collection
- Performance monitoring and profiling
- Business metrics tracking
- Health metrics aggregation
- Time-series data management
- Alert threshold monitoring
- Dashboard data export
- Resource utilization tracking

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Monitoring Expert
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import json
import psutil
import threading

from pydantic import BaseModel, Field
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info, Enum as PrometheusEnum,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server, push_to_gateway
)
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    INFO = "info"
    ENUM = "enum"


class MetricConfig(BaseModel):
    """Metric configuration"""
    name: str = Field(..., description="Metric name")
    description: str = Field(..., description="Metric description")
    metric_type: MetricType = Field(..., description="Type of metric")
    labels: List[str] = Field(default_factory=list, description="Metric labels")
    buckets: Optional[List[float]] = Field(default=None, description="Histogram buckets")
    quantiles: Optional[Dict[float, float]] = Field(default=None, description="Summary quantiles")
    states: Optional[List[str]] = Field(default=None, description="Enum states")
    namespace: str = Field(default="microservice", description="Metric namespace")
    subsystem: str = Field(default="", description="Metric subsystem")


class MetricsCollectorConfig(BaseModel):
    """Metrics collector configuration"""
    service_name: str = Field(..., description="Service name")
    collect_interval: int = Field(default=15, description="Collection interval in seconds")
    enable_system_metrics: bool = Field(default=True, description="Enable system metrics collection")
    enable_business_metrics: bool = Field(default=True, description="Enable business metrics")
    enable_performance_metrics: bool = Field(default=True, description="Enable performance metrics")
    prometheus_port: int = Field(default=9090, description="Prometheus metrics port")
    pushgateway_url: Optional[str] = Field(default=None, description="Pushgateway URL")
    pushgateway_job: str = Field(default="microservice", description="Pushgateway job name")
    registry_namespace: str = Field(default="iacherie", description="Registry namespace")
    enable_redis_export: bool = Field(default=False, description="Enable Redis metrics export")
    redis_key_prefix: str = Field(default="metrics", description="Redis key prefix")
    retention_days: int = Field(default=7, description="Metrics retention in days")


class SystemMetrics(BaseModel):
    """System metrics model"""
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    open_files: int = 0
    threads_count: int = 0
    uptime_seconds: float = 0.0


class BusinessMetrics(BaseModel):
    """Business metrics model"""
    requests_total: int = 0
    requests_per_second: float = 0.0
    error_rate_percent: float = 0.0
    response_time_p50: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    active_users: int = 0
    concurrent_connections: int = 0


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    database_query_time: float = 0.0
    cache_hit_rate: float = 0.0
    queue_size: int = 0
    processing_time: float = 0.0
    throughput: float = 0.0
    latency_avg: float = 0.0
    gc_collections: int = 0
    gc_time: float = 0.0


class MetricsSnapshot(BaseModel):
    """Complete metrics snapshot"""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Snapshot timestamp")
    service_name: str = Field(..., description="Service name")
    system_metrics: SystemMetrics = Field(default_factory=SystemMetrics, description="System metrics")
    business_metrics: BusinessMetrics = Field(default_factory=BusinessMetrics, description="Business metrics")
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics, description="Performance metrics")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict, description="Custom metrics")


class MetricCollector(ABC):
    """Abstract metric collector"""
    
    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Collect metrics"""
        pass
    
    @abstractmethod
    def get_metric_configs(self) -> List[MetricConfig]:
        """Get metric configurations"""
        pass


class SystemMetricsCollector(MetricCollector):
    """System metrics collector"""
    
    def __init__(self, process_start_time: datetime):
        self.process_start_time = process_start_time
        self.process = psutil.Process()
    
    async def collect(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = self.process.cpu_percent()
            
            # Memory metrics
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # Disk usage
            disk_usage = psutil.disk_usage('/').percent
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # File descriptors
            num_fds = self.process.num_fds() if hasattr(self.process, 'num_fds') else 0
            
            # Thread count
            num_threads = self.process.num_threads()
            
            # Uptime
            uptime = (datetime.utcnow() - self.process_start_time).total_seconds()
            
            return {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_mb": memory_info.rss / 1024 / 1024,
                "memory_usage_percent": memory_percent,
                "disk_usage_percent": disk_usage,
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
                "open_files": num_fds,
                "threads_count": num_threads,
                "uptime_seconds": uptime
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return {}
    
    def get_metric_configs(self) -> List[MetricConfig]:
        """Get system metric configurations"""
        return [
            MetricConfig(
                name="cpu_usage_percent",
                description="CPU usage percentage",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="memory_usage_mb",
                description="Memory usage in MB",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="memory_usage_percent",
                description="Memory usage percentage",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="disk_usage_percent",
                description="Disk usage percentage",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="network_bytes_sent",
                description="Network bytes sent",
                metric_type=MetricType.COUNTER
            ),
            MetricConfig(
                name="network_bytes_recv",
                description="Network bytes received",
                metric_type=MetricType.COUNTER
            ),
            MetricConfig(
                name="open_files",
                description="Number of open file descriptors",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="threads_count",
                description="Number of threads",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="uptime_seconds",
                description="Service uptime in seconds",
                metric_type=MetricType.GAUGE
            )
        ]


class BusinessMetricsCollector(MetricCollector):
    """Business metrics collector"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_times: List[float] = []
        self.error_count = 0
        self.total_requests = 0
        self.active_connections = 0
        self.last_collection_time = time.time()
    
    async def collect(self) -> Dict[str, Any]:
        """Collect business metrics"""
        try:
            current_time = time.time()
            time_diff = current_time - self.last_collection_time
            
            # Calculate requests per second
            rps = self.total_requests / max(time_diff, 1)
            
            # Calculate error rate
            error_rate = (self.error_count / max(self.total_requests, 1)) * 100
            
            # Calculate response time percentiles
            if self.request_times:
                sorted_times = sorted(self.request_times)
                p50 = self._percentile(sorted_times, 50)
                p95 = self._percentile(sorted_times, 95)
                p99 = self._percentile(sorted_times, 99)
            else:
                p50 = p95 = p99 = 0.0
            
            # Reset counters
            self.last_collection_time = current_time
            
            return {
                "requests_total": self.total_requests,
                "requests_per_second": rps,
                "error_rate_percent": error_rate,
                "response_time_p50": p50,
                "response_time_p95": p95,
                "response_time_p99": p99,
                "active_users": 0,  # Would be calculated from active sessions
                "concurrent_connections": self.active_connections
            }
            
        except Exception as e:
            logger.error(f"Failed to collect business metrics: {str(e)}")
            return {}
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        k = (len(values) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f + 1 < len(values):
            return values[f] * (1 - c) + values[f + 1] * c
        else:
            return values[f]
    
    def record_request(self, response_time: float, success: bool = True):
        """Record request metrics"""
        self.total_requests += 1
        self.request_times.append(response_time)
        
        if not success:
            self.error_count += 1
        
        # Keep only last 1000 response times
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def set_active_connections(self, count: int):
        """Set active connections count"""
        self.active_connections = count
    
    def get_metric_configs(self) -> List[MetricConfig]:
        """Get business metric configurations"""
        return [
            MetricConfig(
                name="requests_total",
                description="Total number of requests",
                metric_type=MetricType.COUNTER
            ),
            MetricConfig(
                name="requests_per_second",
                description="Requests per second",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="error_rate_percent",
                description="Error rate percentage",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="response_time_p50",
                description="50th percentile response time",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="response_time_p95",
                description="95th percentile response time",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="response_time_p99",
                description="99th percentile response time",
                metric_type=MetricType.GAUGE
            ),
            MetricConfig(
                name="concurrent_connections",
                description="Number of concurrent connections",
                metric_type=MetricType.GAUGE
            )
        ]


class MetricsCollector:
    """
    Enterprise metrics collector for microservices
    
    Provides comprehensive metrics collection including:
    - Prometheus metrics integration and export
    - System resource monitoring
    - Business metrics tracking
    - Performance monitoring and profiling
    - Custom metrics definition and collection
    - Time-series data management
    - Alert threshold monitoring
    - Dashboard data export
    - Redis-based metrics persistence
    """
    
    def __init__(self, config: MetricsCollectorConfig):
        """Initialize metrics collector"""
        self.config = config
        
        # Prometheus registry
        self.registry = CollectorRegistry()
        
        # Metric collectors
        self.collectors: List[MetricCollector] = []
        self.prometheus_metrics: Dict[str, Any] = {}
        
        # Data storage
        self.redis_client: Optional[redis.Redis] = None
        self.metrics_history: List[MetricsSnapshot] = []
        
        # Collection control
        self.collection_task: Optional[asyncio.Task] = None
        self.is_collecting = False
        
        # Initialize collectors
        self._initialize_collectors()
        self._setup_prometheus_metrics()
        
        logger.info(f"Metrics collector initialized for service: {config.service_name}")
    
    def _initialize_collectors(self):
        """Initialize metric collectors"""
        process_start_time = datetime.utcnow()  # In real app, use actual start time
        
        if self.config.enable_system_metrics:
            self.collectors.append(SystemMetricsCollector(process_start_time))
        
        if self.config.enable_business_metrics:
            self.collectors.append(BusinessMetricsCollector(self.config.service_name))
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        for collector in self.collectors:
            for metric_config in collector.get_metric_configs():
                self._create_prometheus_metric(metric_config)
    
    def _create_prometheus_metric(self, config: MetricConfig):
        """Create Prometheus metric from configuration"""
        metric_name = f"{self.config.registry_namespace}_{config.namespace}_{config.name}"
        
        if config.subsystem:
            metric_name = f"{self.config.registry_namespace}_{config.namespace}_{config.subsystem}_{config.name}"
        
        try:
            if config.metric_type == MetricType.COUNTER:
                metric = Counter(
                    metric_name,
                    config.description,
                    labelnames=config.labels,
                    registry=self.registry
                )
            
            elif config.metric_type == MetricType.GAUGE:
                metric = Gauge(
                    metric_name,
                    config.description,
                    labelnames=config.labels,
                    registry=self.registry
                )
            
            elif config.metric_type == MetricType.HISTOGRAM:
                metric = Histogram(
                    metric_name,
                    config.description,
                    labelnames=config.labels,
                    buckets=config.buckets,
                    registry=self.registry
                )
            
            elif config.metric_type == MetricType.SUMMARY:
                metric = Summary(
                    metric_name,
                    config.description,
                    labelnames=config.labels,
                    registry=self.registry
                )
            
            elif config.metric_type == MetricType.INFO:
                metric = Info(
                    metric_name,
                    config.description,
                    labelnames=config.labels,
                    registry=self.registry
                )
            
            elif config.metric_type == MetricType.ENUM:
                metric = PrometheusEnum(
                    metric_name,
                    config.description,
                    labelnames=config.labels,
                    states=config.states or [],
                    registry=self.registry
                )
            
            else:
                logger.error(f"Unknown metric type: {config.metric_type}")
                return
            
            self.prometheus_metrics[config.name] = metric
            logger.debug(f"Created Prometheus metric: {metric_name}")
            
        except Exception as e:
            logger.error(f"Failed to create Prometheus metric {config.name}: {str(e)}")
    
    async def start_collection(self, redis_client: Optional[redis.Redis] = None):
        """Start metrics collection"""
        if self.is_collecting:
            logger.warning("Metrics collection already started")
            return
        
        self.redis_client = redis_client
        self.is_collecting = True
        
        # Start collection task
        self.collection_task = asyncio.create_task(self._collection_loop())
        
        # Start Prometheus HTTP server if configured
        if self.config.prometheus_port:
            try:
                start_http_server(self.config.prometheus_port, registry=self.registry)
                logger.info(f"Prometheus metrics server started on port {self.config.prometheus_port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus server: {str(e)}")
        
        logger.info("Metrics collection started")
    
    async def stop_collection(self):
        """Stop metrics collection"""
        if not self.is_collecting:
            return
        
        self.is_collecting = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Metrics collection stopped")
    
    async def _collection_loop(self):
        """Main collection loop"""
        while self.is_collecting:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.config.collect_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {str(e)}")
                await asyncio.sleep(5)  # Back off on error
    
    async def _collect_all_metrics(self):
        """Collect metrics from all collectors"""
        try:
            # Collect from all collectors
            collected_metrics = {}
            
            for collector in self.collectors:
                metrics = await collector.collect()
                collected_metrics.update(metrics)
            
            # Update Prometheus metrics
            await self._update_prometheus_metrics(collected_metrics)
            
            # Store metrics snapshot
            snapshot = MetricsSnapshot(
                service_name=self.config.service_name,
                system_metrics=SystemMetrics(**{k: v for k, v in collected_metrics.items() if k in SystemMetrics.__fields__}),
                business_metrics=BusinessMetrics(**{k: v for k, v in collected_metrics.items() if k in BusinessMetrics.__fields__}),
                performance_metrics=PerformanceMetrics(**{k: v for k, v in collected_metrics.items() if k in PerformanceMetrics.__fields__}),
                custom_metrics={k: v for k, v in collected_metrics.items() if k not in {**SystemMetrics.__fields__, **BusinessMetrics.__fields__, **PerformanceMetrics.__fields__}}
            )
            
            # Store snapshot
            await self._store_metrics_snapshot(snapshot)
            
            # Push to gateway if configured
            if self.config.pushgateway_url:
                await self._push_to_gateway()
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
    
    async def _update_prometheus_metrics(self, metrics: Dict[str, Any]):
        """Update Prometheus metrics with collected values"""
        for metric_name, value in metrics.items():
            if metric_name in self.prometheus_metrics:
                prometheus_metric = self.prometheus_metrics[metric_name]
                
                try:
                    if isinstance(prometheus_metric, (Counter, Gauge)):
                        if isinstance(prometheus_metric, Counter):
                            # For counters, set to current value or increment
                            prometheus_metric._value._value = value
                        else:
                            prometheus_metric.set(value)
                    
                    elif isinstance(prometheus_metric, (Histogram, Summary)):
                        # For histograms and summaries, observe the value
                        prometheus_metric.observe(value)
                    
                except Exception as e:
                    logger.error(f"Failed to update Prometheus metric {metric_name}: {str(e)}")
    
    async def _store_metrics_snapshot(self, snapshot: MetricsSnapshot):
        """Store metrics snapshot"""
        # Store in memory
        self.metrics_history.append(snapshot)
        
        # Keep only recent history
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.metrics_history = [
            s for s in self.metrics_history
            if s.timestamp >= cutoff_time
        ]
        
        # Store in Redis if available
        if self.config.enable_redis_export and self.redis_client:
            try:
                key = f"{self.config.redis_key_prefix}:{self.config.service_name}:{int(snapshot.timestamp.timestamp())}"
                await self.redis_client.setex(
                    key,
                    timedelta(days=self.config.retention_days).total_seconds(),
                    snapshot.json()
                )
            except Exception as e:
                logger.error(f"Failed to store metrics in Redis: {str(e)}")
    
    async def _push_to_gateway(self):
        """Push metrics to Pushgateway"""
        try:
            from prometheus_client.gateway import push_to_gateway
            
            push_to_gateway(
                self.config.pushgateway_url,
                job=self.config.pushgateway_job,
                registry=self.registry,
                grouping_key={'instance': self.config.service_name}
            )
            
        except Exception as e:
            logger.error(f"Failed to push metrics to gateway: {str(e)}")
    
    def record_request_metrics(self, method: str, endpoint: str, status_code: int, execution_time: float):
        """Record request metrics"""
        # Find business metrics collector
        for collector in self.collectors:
            if isinstance(collector, BusinessMetricsCollector):
                collector.record_request(execution_time, 200 <= status_code < 400)
                break
    
    def set_active_connections(self, count: int):
        """Set active connections count"""
        for collector in self.collectors:
            if isinstance(collector, BusinessMetricsCollector):
                collector.set_active_connections(count)
                break
    
    def add_custom_collector(self, collector: MetricCollector):
        """Add custom metric collector"""
        self.collectors.append(collector)
        
        # Setup Prometheus metrics for new collector
        for metric_config in collector.get_metric_configs():
            self._create_prometheus_metric(metric_config)
        
        logger.info(f"Added custom metric collector: {type(collector).__name__}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        if self.metrics_history:
            latest_snapshot = self.metrics_history[-1]
            return {
                "timestamp": latest_snapshot.timestamp.isoformat(),
                "system": latest_snapshot.system_metrics.dict(),
                "business": latest_snapshot.business_metrics.dict(),
                "performance": latest_snapshot.performance_metrics.dict(),
                "custom": latest_snapshot.custom_metrics
            }
        return {}
    
    async def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            {
                "timestamp": snapshot.timestamp.isoformat(),
                "system": snapshot.system_metrics.dict(),
                "business": snapshot.business_metrics.dict(),
                "performance": snapshot.performance_metrics.dict(),
                "custom": snapshot.custom_metrics
            }
            for snapshot in self.metrics_history
            if snapshot.timestamp >= cutoff_time
        ]
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in exposition format"""
        return generate_latest(self.registry).decode('utf-8')


def create_metrics_collector(
    service_name: str,
    collect_interval: int = 15,
    prometheus_port: int = 9090
) -> MetricsCollector:
    """Factory function to create metrics collector"""
    
    config = MetricsCollectorConfig(
        service_name=service_name,
        collect_interval=collect_interval,
        prometheus_port=prometheus_port,
        enable_system_metrics=True,
        enable_business_metrics=True,
        enable_performance_metrics=True
    )
    
    return MetricsCollector(config)