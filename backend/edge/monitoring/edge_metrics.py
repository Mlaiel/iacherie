"""Edge Metrics Collection System
==============================

Advanced metrics collection system for edge computing nodes,
providing real-time metric gathering, aggregation, and analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from collections import defaultdict, deque
import statistics
import threading

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of edge metrics."""
    # Performance metrics
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    
    # Resource metrics
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    GPU_USAGE = "gpu_usage"
    
    # Network metrics
    BANDWIDTH_UTILIZATION = "bandwidth_utilization"
    PACKET_LOSS = "packet_loss"
    JITTER = "jitter"
    CONNECTION_COUNT = "connection_count"
    
    # Application metrics
    REQUEST_COUNT = "request_count"
    ACTIVE_SESSIONS = "active_sessions"
    CACHE_HIT_RATIO = "cache_hit_ratio"
    QUEUE_DEPTH = "queue_depth"
    
    # Business metrics
    USER_COUNT = "user_count"
    REVENUE_PER_MINUTE = "revenue_per_minute"
    CONVERSION_RATE = "conversion_rate"
    SERVICE_AVAILABILITY = "service_availability"


class MetricLevel(str, Enum):
    """Metric collection levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    DEBUG = "debug"


class AggregationType(str, Enum):
    """Metric aggregation types."""
    AVERAGE = "average"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_50 = "p50"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    RATE = "rate"
    DELTA = "delta"


@dataclass
class EdgeMetric:
    """Individual edge metric data point."""
    metric_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    source: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    level: MetricLevel = MetricLevel.NORMAL
    unit: str = ""


@dataclass
class MetricAggregation:
    """Aggregated metric data."""
    metric_type: MetricType
    aggregation_type: AggregationType
    value: float
    start_time: datetime
    end_time: datetime
    sample_count: int
    source: str
    tags: Dict[str, str] = field(default_factory=dict)


class EdgeMetricsCollector:
    """Advanced edge metrics collection system."""
    
    def __init__(self,
                 collection_interval: float = 1.0,
                 retention_period: int = 86400,  # 24 hours
                 max_metrics_per_type: int = 10000):
        
        self.collection_interval = collection_interval
        self.retention_period = retention_period
        self.max_metrics_per_type = max_metrics_per_type
        
        # Metrics storage
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_type))
        self.aggregated_metrics: Dict[str, List[MetricAggregation]] = defaultdict(list)
        
        # Collection configuration
        self.metric_collectors: Dict[MetricType, Callable] = {}
        self.custom_collectors: Dict[str, Callable] = {}
        
        # Background tasks
        self.collection_task: Optional[asyncio.Task] = None
        self.aggregation_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Event handlers
        self.metric_handlers: List[Callable] = []
        self.alert_handlers: List[Callable] = []
        
        # Thread safety
        self._collection_lock = threading.RLock()
        
        # Control flags
        self.running = False
        
        # Initialize built-in collectors
        self._initialize_collectors()
        
        logger.info("EdgeMetricsCollector initialized")
    
    async def start(self):
        """Start the metrics collection system."""
        if self.running:
            logger.warning("Metrics collector already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.collection_task = asyncio.create_task(self._collection_loop())
        self.aggregation_task = asyncio.create_task(self._aggregation_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Edge metrics collection started")
    
    async def stop(self):
        """Stop the metrics collection system."""
        self.running = False
        
        # Cancel background tasks
        tasks = [self.collection_task, self.aggregation_task, self.cleanup_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Edge metrics collection stopped")
    
    async def collect_metric(self, metric: EdgeMetric):
        """Collect a single metric."""
        with self._collection_lock:
            try:
                # Store raw metric
                metric_key = f"{metric.source}_{metric.metric_type.value}"
                self.raw_metrics[metric_key].append(metric)
                
                # Trigger metric handlers
                for handler in self.metric_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(metric)
                        else:
                            handler(metric)
                    except Exception as e:
                        logger.error(f"Error in metric handler: {e}")
                
                logger.debug(f"Collected metric: {metric.metric_type.value} = {metric.value}")
                
            except Exception as e:
                logger.error(f"Failed to collect metric: {e}")
    
    async def get_metrics(self,
                         metric_type: Optional[MetricType] = None,
                         source: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         limit: Optional[int] = None) -> List[EdgeMetric]:
        """Get collected metrics with optional filtering."""
        
        metrics = []
        
        with self._collection_lock:
            for metric_key, metric_deque in self.raw_metrics.items():
                for metric in metric_deque:
                    # Apply filters
                    if metric_type and metric.metric_type != metric_type:
                        continue
                    if source and metric.source != source:
                        continue
                    if start_time and metric.timestamp < start_time:
                        continue
                    if end_time and metric.timestamp > end_time:
                        continue
                    
                    metrics.append(metric)
        
        # Sort by timestamp
        metrics.sort(key=lambda m: m.timestamp)
        
        # Apply limit
        if limit:
            metrics = metrics[-limit:]
        
        return metrics
    
    async def get_aggregated_metrics(self,
                                   metric_type: MetricType,
                                   aggregation_type: AggregationType,
                                   time_window: timedelta = timedelta(minutes=5),
                                   source: Optional[str] = None) -> List[MetricAggregation]:
        """Get aggregated metrics for a specific type and time window."""
        
        end_time = datetime.now()
        start_time = end_time - time_window
        
        # Get raw metrics for the time window
        raw_metrics = await self.get_metrics(
            metric_type=metric_type,
            source=source,
            start_time=start_time,
            end_time=end_time
        )
        
        if not raw_metrics:
            return []
        
        # Group by source if not specified
        if source:
            grouped_metrics = {source: raw_metrics}
        else:
            grouped_metrics = defaultdict(list)
            for metric in raw_metrics:
                grouped_metrics[metric.source].append(metric)
        
        # Calculate aggregations
        aggregations = []
        for src, metrics in grouped_metrics.items():
            if not metrics:
                continue
            
            values = [m.value for m in metrics]
            aggregated_value = await self._calculate_aggregation(values, aggregation_type)
            
            aggregation = MetricAggregation(
                metric_type=metric_type,
                aggregation_type=aggregation_type,
                value=aggregated_value,
                start_time=start_time,
                end_time=end_time,
                sample_count=len(values),
                source=src,
                tags=metrics[0].tags if metrics else {}
            )
            
            aggregations.append(aggregation)
        
        return aggregations
    
    async def get_metric_statistics(self,
                                   metric_type: MetricType,
                                   time_window: timedelta = timedelta(minutes=15),
                                   source: Optional[str] = None) -> Dict[str, float]:
        """Get comprehensive statistics for a metric type."""
        
        metrics = await self.get_metrics(
            metric_type=metric_type,
            source=source,
            start_time=datetime.now() - time_window
        )
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        stats = {
            'count': len(values),
            'mean': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'sum': sum(values)
        }
        
        if len(values) > 1:
            stats['stdev'] = statistics.stdev(values)
            stats['median'] = statistics.median(values)
        
        # Calculate percentiles
        if len(values) >= 2:
            sorted_values = sorted(values)
            stats['p50'] = self._percentile(sorted_values, 50)
            stats['p95'] = self._percentile(sorted_values, 95)
            stats['p99'] = self._percentile(sorted_values, 99)
        
        return stats
    
    async def register_custom_collector(self, name: str, collector_func: Callable):
        """Register a custom metric collector function."""
        self.custom_collectors[name] = collector_func
        logger.info(f"Registered custom collector: {name}")
    
    def add_metric_handler(self, handler: Callable):
        """Add a metric event handler."""
        self.metric_handlers.append(handler)
    
    def remove_metric_handler(self, handler: Callable):
        """Remove a metric event handler."""
        try:
            self.metric_handlers.remove(handler)
        except ValueError:
            pass
    
    async def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format."""
        
        all_metrics = []
        
        with self._collection_lock:
            for metric_deque in self.raw_metrics.values():
                all_metrics.extend(list(metric_deque))
        
        if format_type.lower() == "json":
            # Convert to JSON serializable format
            json_metrics = []
            for metric in all_metrics:
                json_metrics.append({
                    'metric_id': metric.metric_id,
                    'metric_type': metric.metric_type.value,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'source': metric.source,
                    'tags': metric.tags,
                    'metadata': metric.metadata,
                    'level': metric.level.value,
                    'unit': metric.unit
                })
            
            return json.dumps(json_metrics, indent=2)
        
        elif format_type.lower() == "prometheus":
            # Convert to Prometheus format
            prometheus_lines = []
            metric_groups = defaultdict(list)
            
            # Group metrics by type
            for metric in all_metrics:
                metric_groups[metric.metric_type].append(metric)
            
            for metric_type, metrics in metric_groups.items():
                for metric in metrics:
                    tags_str = ','.join([f'{k}="{v}"' for k, v in metric.tags.items()])
                    line = f'{metric_type.value}{{{tags_str}}} {metric.value} {int(metric.timestamp.timestamp() * 1000)}'
                    prometheus_lines.append(line)
            
            return '\n'.join(prometheus_lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    # Private methods
    
    def _initialize_collectors(self):
        """Initialize built-in metric collectors."""
        self.metric_collectors = {
            MetricType.CPU_USAGE: self._collect_cpu_usage,
            MetricType.MEMORY_USAGE: self._collect_memory_usage,
            MetricType.DISK_USAGE: self._collect_disk_usage,
            MetricType.NETWORK_IO: self._collect_network_io,
            MetricType.LATENCY: self._collect_latency,
            MetricType.THROUGHPUT: self._collect_throughput
        }
    
    async def _collection_loop(self):
        """Main collection loop."""
        while self.running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect custom metrics
                await self._collect_custom_metrics()
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _aggregation_loop(self):
        """Background aggregation loop."""
        while self.running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(60)  # Aggregate every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self.running:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _collect_system_metrics(self):
        """Collect built-in system metrics."""
        timestamp = datetime.now()
        source = "system"
        
        for metric_type, collector in self.metric_collectors.items():
            try:
                value = await collector()
                
                metric = EdgeMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=metric_type,
                    value=value,
                    timestamp=timestamp,
                    source=source,
                    tags={"node": "local", "type": "system"},
                    level=MetricLevel.NORMAL
                )
                
                await self.collect_metric(metric)
                
            except Exception as e:
                logger.error(f"Failed to collect {metric_type.value}: {e}")
    
    async def _collect_custom_metrics(self):
        """Collect custom metrics."""
        timestamp = datetime.now()
        
        for name, collector in self.custom_collectors.items():
            try:
                result = await collector() if asyncio.iscoroutinefunction(collector) else collector()
                
                if isinstance(result, dict):
                    # Multiple metrics from one collector
                    for metric_name, value in result.items():
                        metric = EdgeMetric(
                            metric_id=str(uuid.uuid4()),
                            metric_type=MetricType(metric_name) if metric_name in MetricType.__members__.values() else MetricType.REQUEST_COUNT,
                            value=float(value),
                            timestamp=timestamp,
                            source=name,
                            tags={"collector": name, "type": "custom"},
                            level=MetricLevel.NORMAL
                        )
                        await self.collect_metric(metric)
                else:
                    # Single metric value
                    metric = EdgeMetric(
                        metric_id=str(uuid.uuid4()),
                        metric_type=MetricType.REQUEST_COUNT,  # Default type
                        value=float(result),
                        timestamp=timestamp,
                        source=name,
                        tags={"collector": name, "type": "custom"},
                        level=MetricLevel.NORMAL
                    )
                    await self.collect_metric(metric)
                    
            except Exception as e:
                logger.error(f"Failed to collect custom metric {name}: {e}")
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for storage efficiency."""
        current_time = datetime.now()
        
        # Get metrics from the last hour
        start_time = current_time - timedelta(hours=1)
        
        for metric_type in MetricType:
            try:
                # Get aggregations for different time windows
                for agg_type in [AggregationType.AVERAGE, AggregationType.MAX, AggregationType.MIN]:
                    aggregations = await self.get_aggregated_metrics(
                        metric_type=metric_type,
                        aggregation_type=agg_type,
                        time_window=timedelta(minutes=5)
                    )
                    
                    # Store aggregations
                    agg_key = f"{metric_type.value}_{agg_type.value}"
                    self.aggregated_metrics[agg_key].extend(aggregations)
                    
                    # Keep only recent aggregations
                    cutoff_time = current_time - timedelta(hours=24)
                    self.aggregated_metrics[agg_key] = [
                        agg for agg in self.aggregated_metrics[agg_key]
                        if agg.end_time > cutoff_time
                    ]
                    
            except Exception as e:
                logger.error(f"Failed to aggregate {metric_type.value}: {e}")
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics to manage memory usage."""
        cutoff_time = datetime.now() - timedelta(seconds=self.retention_period)
        
        with self._collection_lock:
            for metric_key in list(self.raw_metrics.keys()):
                metric_deque = self.raw_metrics[metric_key]
                
                # Remove old metrics
                while metric_deque and metric_deque[0].timestamp < cutoff_time:
                    metric_deque.popleft()
                
                # Remove empty deques
                if not metric_deque:
                    del self.raw_metrics[metric_key]
        
        logger.debug("Cleaned up old metrics")
    
    async def _calculate_aggregation(self, values: List[float], aggregation_type: AggregationType) -> float:
        """Calculate aggregated value based on type."""
        if not values:
            return 0.0
        
        if aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(values)
        elif aggregation_type == AggregationType.SUM:
            return sum(values)
        elif aggregation_type == AggregationType.MIN:
            return min(values)
        elif aggregation_type == AggregationType.MAX:
            return max(values)
        elif aggregation_type == AggregationType.COUNT:
            return len(values)
        elif aggregation_type == AggregationType.PERCENTILE_50:
            return self._percentile(sorted(values), 50)
        elif aggregation_type == AggregationType.PERCENTILE_95:
            return self._percentile(sorted(values), 95)
        elif aggregation_type == AggregationType.PERCENTILE_99:
            return self._percentile(sorted(values), 99)
        else:
            return statistics.mean(values)  # Default to average
    
    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not sorted_values:
            return 0.0
        
        index = (len(sorted_values) - 1) * percentile / 100
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        
        if lower_index == upper_index:
            return sorted_values[lower_index]
        
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    # Built-in metric collectors
    
    async def _collect_cpu_usage(self) -> float:
        """Collect CPU usage percentage."""
        return psutil.cpu_percent(interval=None)
    
    async def _collect_memory_usage(self) -> float:
        """Collect memory usage percentage."""
        memory = psutil.virtual_memory()
        return memory.percent
    
    async def _collect_disk_usage(self) -> float:
        """Collect disk usage percentage."""
        disk = psutil.disk_usage('/')
        return (disk.used / disk.total) * 100
    
    async def _collect_network_io(self) -> float:
        """Collect network I/O rate."""
        net_io = psutil.net_io_counters()
        return net_io.bytes_sent + net_io.bytes_recv
    
    async def _collect_latency(self) -> float:
        """Collect application latency (placeholder)."""
        # This would be implemented based on actual application metrics
        return 1.5  # Placeholder latency in milliseconds
    
    async def _collect_throughput(self) -> float:
        """Collect application throughput (placeholder)."""
        # This would be implemented based on actual application metrics
        return 1000.0  # Placeholder throughput in requests per second


def create_edge_metrics_collector(
    collection_interval: float = 1.0,
    retention_period: int = 86400,
    max_metrics_per_type: int = 10000
) -> EdgeMetricsCollector:
    """Create and configure an edge metrics collector instance."""
    return EdgeMetricsCollector(
        collection_interval=collection_interval,
        retention_period=retention_period,
        max_metrics_per_type=max_metrics_per_type
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_metrics_collector():
        """Test the metrics collector."""
        collector = create_edge_metrics_collector(collection_interval=2.0)
        
        # Start collector
        await collector.start()
        
        # Let it collect some metrics
        await asyncio.sleep(10)
        
        # Get metrics
        cpu_metrics = await collector.get_metrics(MetricType.CPU_USAGE, limit=5)
        print(f"Collected {len(cpu_metrics)} CPU metrics")
        
        # Get statistics
        stats = await collector.get_metric_statistics(MetricType.CPU_USAGE)
        print(f"CPU stats: {stats}")
        
        # Export metrics
        json_export = await collector.export_metrics("json")
        print(f"Exported {len(json_export.split('\n'))} lines of JSON")
        
        # Stop collector
        await collector.stop()
    
    # Run test
    asyncio.run(test_metrics_collector())