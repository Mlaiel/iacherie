"""Metrics Collection Utilities
Enterprise-grade metrics collection and aggregation for Ainflue Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Represents a single metric data point"""
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: float
    unit: str = ""


class MetricsCollector:
    """
    Enterprise-grade metrics collection system with buffering, 
    aggregation, and export capabilities.
    """
    
    def __init__(self, buffer_size: int = 10000, flush_interval: int = 60):
        """Initialize metrics collector
        
        Args:
            buffer_size: Maximum number of metrics to buffer before flushing
            flush_interval: Interval in seconds to auto-flush metrics
        """
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.metrics_buffer: deque = deque(maxlen=buffer_size)
        self.aggregated_metrics: Dict[str, Dict] = defaultdict(dict)
        self.exporters: List[Callable] = []
        self.running = False
        self.lock = threading.Lock()
        
        # Start background flush thread
        self._start_flush_thread()
        
        logger.info(f"MetricsCollector initialized with buffer_size={buffer_size}, flush_interval={flush_interval}")
    
    def _start_flush_thread(self):
        """Start background thread for periodic metric flushing"""
        def flush_worker():
            while self.running:
                time.sleep(self.flush_interval)
                if self.running:
                    self.flush_metrics()
        
        self.running = True
        self.flush_thread = threading.Thread(target=flush_worker, daemon=True)
        self.flush_thread.start()
    
    def record_counter(self, name: str, value: float = 1, tags: Optional[Dict[str, str]] = None):
        """Record a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            tags=tags or {},
            timestamp=time.time(),
            unit="count"
        )
        self._add_metric(metric)
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a gauge metric"""
        metric = Metric(
            name=name,
            value=value,
            tags=tags or {},
            timestamp=time.time(),
            unit="value"
        )
        self._add_metric(metric)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram metric"""
        metric = Metric(
            name=name,
            value=value,
            tags=tags or {},
            timestamp=time.time(),
            unit="duration"
        )
        self._add_metric(metric)
    
    def record_timer(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record a timer metric"""
        metric = Metric(
            name=name,
            value=duration,
            tags=tags or {},
            timestamp=time.time(),
            unit="seconds"
        )
        self._add_metric(metric)
    
    def _add_metric(self, metric: Metric):
        """Add metric to buffer thread-safely"""
        with self.lock:
            self.metrics_buffer.append(metric)
            
            # Auto-flush if buffer is full
            if len(self.metrics_buffer) >= self.buffer_size:
                self.flush_metrics()
    
    def flush_metrics(self):
        """Flush buffered metrics to exporters"""
        with self.lock:
            if not self.metrics_buffer:
                return
            
            # Copy and clear buffer
            metrics_to_flush = list(self.metrics_buffer)
            self.metrics_buffer.clear()
        
        # Aggregate metrics
        self._aggregate_metrics(metrics_to_flush)
        
        # Export to all registered exporters
        for exporter in self.exporters:
            try:
                exporter(metrics_to_flush)
            except Exception as e:
                logger.error(f"Error in metric exporter: {e}")
    
    def _aggregate_metrics(self, metrics: List[Metric]):
        """Aggregate metrics for internal storage"""
        for metric in metrics:
            key = f"{metric.name}:{':'.join(f'{k}={v}' for k, v in metric.tags.items())}"
            
            if key not in self.aggregated_metrics:
                self.aggregated_metrics[key] = {
                    "name": metric.name,
                    "tags": metric.tags,
                    "count": 0,
                    "sum": 0,
                    "min": float('inf'),
                    "max": float('-inf'),
                    "last_value": 0,
                    "last_timestamp": 0
                }
            
            agg = self.aggregated_metrics[key]
            agg["count"] += 1
            agg["sum"] += metric.value
            agg["min"] = min(agg["min"], metric.value)
            agg["max"] = max(agg["max"], metric.value)
            agg["last_value"] = metric.value
            agg["last_timestamp"] = metric.timestamp
    
    def add_exporter(self, exporter: Callable[[List[Metric]], None]):
        """Add metric exporter function"""
        self.exporters.append(exporter)
        logger.info(f"Added metric exporter: {exporter.__name__}")
    
    def get_aggregated_metrics(self) -> Dict[str, Dict]:
        """Get current aggregated metrics"""
        with self.lock:
            return dict(self.aggregated_metrics)
    
    def get_metric_summary(self, name: str) -> Optional[Dict]:
        """Get summary for specific metric"""
        for key, data in self.aggregated_metrics.items():
            if data["name"] == name:
                avg = data["sum"] / data["count"] if data["count"] > 0 else 0
                return {
                    "name": name,
                    "count": data["count"],
                    "sum": data["sum"],
                    "average": avg,
                    "min": data["min"] if data["min"] != float('inf') else 0,
                    "max": data["max"] if data["max"] != float('-inf') else 0,
                    "last_value": data["last_value"],
                    "last_timestamp": data["last_timestamp"]
                }
        return None
    
    def reset_metrics(self):
        """Reset all aggregated metrics"""
        with self.lock:
            self.aggregated_metrics.clear()
            self.metrics_buffer.clear()
        logger.info("All metrics have been reset")
    
    def stop(self):
        """Stop the metrics collector"""
        self.running = False
        if hasattr(self, 'flush_thread'):
            self.flush_thread.join(timeout=5)
        
        # Final flush
        self.flush_metrics()
        logger.info("MetricsCollector stopped")


class PrometheusExporter:
    """Prometheus metrics exporter"""
    
    def __init__(self, namespace: str = "ainflue"):
        self.namespace = namespace
    
    def __call__(self, metrics: List[Metric]):
        """Export metrics in Prometheus format"""
        prometheus_metrics = []
        
        for metric in metrics:
            # Convert to Prometheus format
            metric_name = f"{self.namespace}_{metric.name.replace('-', '_')}"
            labels = ','.join(f'{k}="{v}"' for k, v in metric.tags.items()) if metric.tags else ""
            
            if labels:
                line = f"{metric_name}{{{labels}}} {metric.value} {int(metric.timestamp * 1000)}"
            else:
                line = f"{metric_name} {metric.value} {int(metric.timestamp * 1000)}"
            
            prometheus_metrics.append(line)
        
        # In a real implementation, this would send to Prometheus
        logger.debug(f"Exported {len(prometheus_metrics)} metrics to Prometheus")


class JSONExporter:
    """JSON metrics exporter"""
    
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
    
    def __call__(self, metrics: List[Metric]):
        """Export metrics as JSON"""
        import json
        
        json_metrics = []
        for metric in metrics:
            json_metrics.append({
                "name": metric.name,
                "value": metric.value,
                "tags": metric.tags,
                "timestamp": metric.timestamp,
                "unit": metric.unit
            })
        
        if self.file_path:
            with open(self.file_path, 'a') as f:
                for metric in json_metrics:
                    f.write(json.dumps(metric) + '\n')
        else:
            logger.debug(f"Exported {len(json_metrics)} metrics as JSON")


# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None


def get_global_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def record_counter(name: str, value: float = 1, tags: Optional[Dict[str, str]] = None):
    """Record counter using global collector"""
    get_global_collector().record_counter(name, value, tags)


def record_gauge(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record gauge using global collector"""
    get_global_collector().record_gauge(name, value, tags)


def record_timer(name: str, duration: float, tags: Optional[Dict[str, str]] = None):
    """Record timer using global collector"""
    get_global_collector().record_timer(name, duration, tags)