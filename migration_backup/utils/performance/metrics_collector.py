"""
Metrics Collector - Performance Utilities Level 3
=================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade metrics collection consolidating metrics.py + metrics_collector.py
Enhanced with Prometheus integration and real-time monitoring.

Performance: < 1ms per metric operation
Standards: Prometheus metrics, real-time collection, enterprise observability
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class MetricResult:
    """Result container for metrics operations."""
    success: bool
    result: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

class MetricsCollector:
    """Enterprise metrics collector with Prometheus integration."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics collector."""
        self.config = config or {}
        self._performance_threshold_ms = 1.0
        self._metrics_storage = defaultdict(deque)
        self._counters = defaultdict(int)
        self._gauges = defaultdict(float)
        self._histograms = defaultdict(list)
        self._lock = threading.Lock()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> MetricResult:
        """Increment a counter metric."""
        start_time = time.perf_counter()
        
        try:
            with self._lock:
                metric_key = f"{name}_{labels}" if labels else name
                self._counters[metric_key] += value
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return MetricResult(
                success=True,
                result=f"Counter {name} incremented by {value}",
                execution_time_ms=exec_time
            )
        except Exception as e:
            return MetricResult(success=False, errors=[str(e)])
    
    async def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> MetricResult:
        """Set a gauge metric value."""
        start_time = time.perf_counter()
        
        try:
            with self._lock:
                metric_key = f"{name}_{labels}" if labels else name
                self._gauges[metric_key] = value
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return MetricResult(
                success=True,
                result=f"Gauge {name} set to {value}",
                execution_time_ms=exec_time
            )
        except Exception as e:
            return MetricResult(success=False, errors=[str(e)])
    
    async def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> MetricResult:
        """Record a histogram value."""
        start_time = time.perf_counter()
        
        try:
            with self._lock:
                metric_key = f"{name}_{labels}" if labels else name
                self._histograms[metric_key].append(value)
                
                # Keep only last 1000 values for memory management
                if len(self._histograms[metric_key]) > 1000:
                    self._histograms[metric_key] = self._histograms[metric_key][-1000:]
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return MetricResult(
                success=True,
                result=f"Histogram {name} recorded value {value}",
                execution_time_ms=exec_time
            )
        except Exception as e:
            return MetricResult(success=False, errors=[str(e)])
    
    async def get_metrics_summary(self) -> MetricResult:
        """Get summary of all metrics."""
        try:
            with self._lock:
                summary = {
                    'counters': dict(self._counters),
                    'gauges': dict(self._gauges),
                    'histograms': {
                        name: {
                            'count': len(values),
                            'avg': sum(values) / len(values) if values else 0,
                            'min': min(values) if values else 0,
                            'max': max(values) if values else 0
                        }
                        for name, values in self._histograms.items()
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            return MetricResult(success=True, result=summary)
        except Exception as e:
            return MetricResult(success=False, errors=[str(e)])

class MetricsCollectorFactory:
    """Factory for creating metrics collector instances."""
    
    @staticmethod
    def create_collector(config: Optional[Dict[str, Any]] = None) -> MetricsCollector:
        return MetricsCollector(config)

# === ENHANCED ENTERPRISE METRICS UTILITIES ===
# Consolidated from standalone metrics_collector.py with enterprise features

# Optional dependencies with fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

@dataclass
class EnterpriseMetricData:
    """Enhanced metric data structure for enterprise monitoring"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    category: str = "general"
    severity: str = "info"  # info, warning, error, critical

class EnterpriseMetricsCollector:
    """Enhanced enterprise metrics collector with system monitoring and Prometheus integration
    
    DevOps Expert: Advanced monitoring with system metrics, Prometheus export, alerting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.collection_interval = self.config.get('collection_interval', 30)
        self.metrics_buffer: List[EnterpriseMetricData] = []
        self.system_collectors = {}
        self.is_running = False
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Prometheus metrics
        self._prometheus_enabled = self.config.get('prometheus_enabled', False)
        self._prometheus_metrics = {}
        
        if self._prometheus_enabled and PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self._prometheus_metrics = {
            'request_count': Counter('ainflue_requests_total', 'Total requests', ['method', 'endpoint']),
            'request_duration': Histogram('ainflue_request_duration_seconds', 'Request duration'),
            'memory_usage': Gauge('ainflue_memory_usage_bytes', 'Memory usage'),
            'cpu_usage': Gauge('ainflue_cpu_usage_percent', 'CPU usage percentage'),
            'active_connections': Gauge('ainflue_active_connections', 'Active connections')
        }
        
        # Start Prometheus HTTP server
        prometheus_port = self.config.get('prometheus_port', 8000)
        try:
            start_http_server(prometheus_port)
            self.logger.info(f"Prometheus metrics server started on port {prometheus_port}")
        except Exception as e:
            self.logger.warning(f"Failed to start Prometheus server: {e}")
    
    async def start_collection(self):
        """Start continuous metrics collection"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Register system collectors
        if PSUTIL_AVAILABLE:
            self.system_collectors['cpu'] = self._collect_cpu_metrics
            self.system_collectors['memory'] = self._collect_memory_metrics
            self.system_collectors['disk'] = self._collect_disk_metrics
            self.system_collectors['network'] = self._collect_network_metrics
        
        # Start collection loop
        asyncio.create_task(self._collection_loop())
        self.logger.info("Enterprise metrics collection started")
    
    async def stop_collection(self):
        """Stop metrics collection"""
        self.is_running = False
        self.logger.info("Enterprise metrics collection stopped")
    
    async def _collection_loop(self):
        """Main metrics collection loop"""
        while self.is_running:
            try:
                # Collect system metrics
                for collector_name, collector_func in self.system_collectors.items():
                    metrics = await collector_func()
                    with self._lock:
                        self.metrics_buffer.extend(metrics)
                
                # Clean old metrics (keep last 1000)
                with self._lock:
                    if len(self.metrics_buffer) > 1000:
                        self.metrics_buffer = self.metrics_buffer[-1000:]
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)  # Short delay on error
    
    async def _collect_cpu_metrics(self) -> List[EnterpriseMetricData]:
        """Collect CPU metrics"""
        metrics = []
        
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            now = datetime.now(timezone.utc)
            
            metrics.extend([
                EnterpriseMetricData("cpu_usage_percent", cpu_percent, now, unit="%", category="system"),
                EnterpriseMetricData("cpu_count", cpu_count, now, unit="cores", category="system"),
                EnterpriseMetricData("load_avg_1m", load_avg[0], now, unit="load", category="system"),
                EnterpriseMetricData("load_avg_5m", load_avg[1], now, unit="load", category="system"),
                EnterpriseMetricData("load_avg_15m", load_avg[2], now, unit="load", category="system")
            ])
            
            # Update Prometheus metrics
            if self._prometheus_enabled and 'cpu_usage' in self._prometheus_metrics:
                self._prometheus_metrics['cpu_usage'].set(cpu_percent)
            
        except Exception as e:
            self.logger.warning(f"CPU metrics collection failed: {e}")
        
        return metrics
    
    async def _collect_memory_metrics(self) -> List[EnterpriseMetricData]:
        """Collect memory metrics"""
        metrics = []
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            now = datetime.now(timezone.utc)
            
            metrics.extend([
                EnterpriseMetricData("memory_total", memory.total, now, unit="bytes", category="system"),
                EnterpriseMetricData("memory_available", memory.available, now, unit="bytes", category="system"),
                EnterpriseMetricData("memory_used", memory.used, now, unit="bytes", category="system"),
                EnterpriseMetricData("memory_percent", memory.percent, now, unit="%", category="system"),
                EnterpriseMetricData("swap_total", swap.total, now, unit="bytes", category="system"),
                EnterpriseMetricData("swap_used", swap.used, now, unit="bytes", category="system"),
                EnterpriseMetricData("swap_percent", swap.percent, now, unit="%", category="system")
            ])
            
            # Update Prometheus metrics
            if self._prometheus_enabled and 'memory_usage' in self._prometheus_metrics:
                self._prometheus_metrics['memory_usage'].set(memory.used)
            
        except Exception as e:
            self.logger.warning(f"Memory metrics collection failed: {e}")
        
        return metrics
    
    async def _collect_disk_metrics(self) -> List[EnterpriseMetricData]:
        """Collect disk I/O metrics"""
        metrics = []
        
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            now = datetime.now(timezone.utc)
            
            metrics.extend([
                EnterpriseMetricData("disk_total", disk_usage.total, now, unit="bytes", category="storage"),
                EnterpriseMetricData("disk_used", disk_usage.used, now, unit="bytes", category="storage"),
                EnterpriseMetricData("disk_free", disk_usage.free, now, unit="bytes", category="storage"),
                EnterpriseMetricData("disk_percent", disk_usage.percent, now, unit="%", category="storage")
            ])
            
            if disk_io:
                metrics.extend([
                    EnterpriseMetricData("disk_read_bytes", disk_io.read_bytes, now, unit="bytes", category="storage"),
                    EnterpriseMetricData("disk_write_bytes", disk_io.write_bytes, now, unit="bytes", category="storage"),
                    EnterpriseMetricData("disk_read_count", disk_io.read_count, now, unit="ops", category="storage"),
                    EnterpriseMetricData("disk_write_count", disk_io.write_count, now, unit="ops", category="storage")
                ])
            
        except Exception as e:
            self.logger.warning(f"Disk metrics collection failed: {e}")
        
        return metrics
    
    async def _collect_network_metrics(self) -> List[EnterpriseMetricData]:
        """Collect network I/O metrics"""
        metrics = []
        
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            now = datetime.now(timezone.utc)
            
            if net_io:
                metrics.extend([
                    EnterpriseMetricData("network_bytes_sent", net_io.bytes_sent, now, unit="bytes", category="network"),
                    EnterpriseMetricData("network_bytes_recv", net_io.bytes_recv, now, unit="bytes", category="network"),
                    EnterpriseMetricData("network_packets_sent", net_io.packets_sent, now, unit="packets", category="network"),
                    EnterpriseMetricData("network_packets_recv", net_io.packets_recv, now, unit="packets", category="network")
                ])
            
            metrics.append(
                EnterpriseMetricData("network_connections", net_connections, now, unit="connections", category="network")
            )
            
            # Update Prometheus metrics
            if self._prometheus_enabled and 'active_connections' in self._prometheus_metrics:
                self._prometheus_metrics['active_connections'].set(net_connections)
            
        except Exception as e:
            self.logger.warning(f"Network metrics collection failed: {e}")
        
        return metrics
    
    async def record_custom_metric(
        self, 
        name: str, 
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
        unit: str = "",
        category: str = "custom"
    ):
        """Record a custom metric"""
        metric = EnterpriseMetricData(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc),
            tags=tags or {},
            unit=unit,
            category=category
        )
        
        with self._lock:
            self.metrics_buffer.append(metric)
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self._lock:
            if not self.metrics_buffer:
                return {'message': 'No metrics available', 'count': 0}
            
            # Group metrics by category
            by_category = defaultdict(list)
            for metric in self.metrics_buffer:
                by_category[metric.category].append(metric)
            
            summary = {
                'total_metrics': len(self.metrics_buffer),
                'collection_time': datetime.now(timezone.utc).isoformat(),
                'categories': {}
            }
            
            for category, metrics in by_category.items():
                summary['categories'][category] = {
                    'count': len(metrics),
                    'latest_values': {
                        metric.name: metric.value 
                        for metric in metrics[-10:]  # Last 10 metrics per category
                    }
                }
            
            return summary
    
    async def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        with self._lock:
            if format_type == "json":
                return json.dumps([
                    {
                        'name': m.name,
                        'value': m.value,
                        'timestamp': m.timestamp.isoformat(),
                        'tags': m.tags,
                        'unit': m.unit,
                        'category': m.category
                    }
                    for m in self.metrics_buffer
                ], indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

# Export enhanced metrics utilities
__all__ = ['MetricsCollector', 'MetricsCollectorFactory', 'MetricResult',
           'EnterpriseMetricsCollector', 'EnterpriseMetricData']