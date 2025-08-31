"""Metrics Collector - Enterprise Metrics Collection & Aggregation System

This module provides comprehensive metrics collection, aggregation, and export
capabilities for monitoring and scaling decisions in the IA Influencer Agent platform.

Author: Fahed Mlaiel
Email: mlaiel@live.de
© 2025 All Rights Reserved
"""import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import statistics
from concurrent.futures import ThreadPoolExecutor

from ..base import BaseAgent
try:
    from core.exceptions import MetricsException
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    MetricsException = globals().get('MetricsException', Exception)
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.monitoring import get_metrics_client


class MetricType(Enum):
    """Types of metrics"""    COUNTER = "counter"
    GAUGE = "gauge" 
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"


class AggregationType(Enum):
    """Types of metric aggregation"""    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    MEDIAN = "median"
    STDDEV = "stddev"


@dataclass
class MetricPoint:
    """Individual metric data point"""    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetric:
    """Aggregated metric result"""    name: str
    aggregation_type: AggregationType
    value: float
    count: int
    start_time: datetime
    end_time: datetime
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Metric definition and configuration"""    name: str
    metric_type: MetricType
    description: str
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    retention_days: int = 7
    aggregation_intervals: List[int] = field(default_factory=lambda: [60, 300, 3600])  # 1m, 5m, 1h
    export_enabled: bool = True


class MetricsCollector(BaseAgent):
    """    Enterprise Metrics Collector
    
    Features:
    - Multi-source metrics collection
    - Real-time aggregation
    - Flexible export formats
    - Custom metric definitions
    - Time-series data management
    - Alert integration
    - Performance optimization
    - Batch processing support
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self.metrics_client = get_metrics_client()
        
        # Metrics storage
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100000))
        self.aggregated_metrics: Dict[str, Dict[int, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=10000))
        )
        
        # Metric definitions
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        
        # Collection configuration
        self.collection_interval = 30  # seconds
        self.aggregation_intervals = [60, 300, 3600, 86400]  # 1m, 5m, 1h, 1d
        self.max_metrics_per_batch = 1000
        
        # Collection state
        self.is_collecting = False
        self.collection_tasks: List[asyncio.Task] = []
        
        # Data sources
        self.data_sources: Dict[str, Callable] = {}
        self.custom_collectors: List[Callable] = []
        
        # Thread safety
        self.metrics_lock = threading.RLock()
        self.aggregation_lock = threading.RLock()
        
        # Performance tracking
        self.collector_stats = {
            "total_metrics_collected": 0,
            "collection_errors": 0,
            "last_collection_duration": 0.0,
            "aggregations_performed": 0,
            "export_operations": 0
        }
        
        # Export configuration
        self.export_handlers: Dict[str, Callable] = {}
        self.export_formats = ["prometheus", "json", "csv"]
        
        self.logger.info("MetricsCollector initialized successfully")

    async def start_collection(self):
        """Start metrics collection"""        try:
            if self.is_collecting:
                self.logger.warning("Metrics collection already active")
                return
            
            self.is_collecting = True
            
            # Initialize default metric definitions
            await self._initialize_default_metrics()
            
            # Initialize data sources
            await self._initialize_data_sources()
            
            # Start collection tasks
            self.collection_tasks = [
                asyncio.create_task(self._metrics_collection_loop()),
                asyncio.create_task(self._aggregation_loop()),
                asyncio.create_task(self._export_loop()),
                asyncio.create_task(self._cleanup_loop())
            ]
            
            self.logger.info("Metrics collection started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start metrics collection: {e}")
            self.is_collecting = False
            raise MetricsException(f"Collection startup failed: {e}")

    async def stop_collection(self):
        """Stop metrics collection"""        try:
            self.is_collecting = False
            
            # Cancel all collection tasks
            for task in self.collection_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self.collection_tasks:
                await asyncio.gather(*self.collection_tasks, return_exceptions=True)
            
            self.collection_tasks.clear()
            self.logger.info("Metrics collection stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping metrics collection: {e}")

    async def _metrics_collection_loop(self):
        """Main metrics collection loop"""        self.logger.info("Starting metrics collection loop")
        
        while self.is_collecting:
            try:
                start_time = time.time()
                
                # Collect from all data sources
                metrics_collected = await self._collect_all_metrics()
                
                # Store raw metrics
                await self._store_raw_metrics(metrics_collected)
                
                # Update collector stats
                collection_duration = time.time() - start_time
                self.collector_stats["last_collection_duration"] = collection_duration
                self.collector_stats["total_metrics_collected"] += len(metrics_collected)
                
                # Sleep for collection interval
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {e}")
                self.collector_stats["collection_errors"] += 1
                await asyncio.sleep(self.collection_interval)

    async def _aggregation_loop(self):
        """Metrics aggregation loop"""        while self.is_collecting:
            try:
                # Perform aggregation for each interval
                for interval in self.aggregation_intervals:
                    await self._perform_aggregation(interval)
                
                # Update stats
                self.collector_stats["aggregations_performed"] += 1
                
                # Sleep for aggregation interval (run every minute)
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in aggregation loop: {e}")
                await asyncio.sleep(60)

    async def _export_loop(self):
        """Metrics export loop"""        while self.is_collecting:
            try:
                # Export metrics to configured destinations
                await self._export_metrics()
                
                # Update stats
                self.collector_stats["export_operations"] += 1
                
                # Sleep for export interval (run every 5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in export loop: {e}")
                await asyncio.sleep(300)

    async def _cleanup_loop(self):
        """Metrics cleanup loop"""        while self.is_collecting:
            try:
                # Clean up old metrics
                await self._cleanup_old_metrics()
                
                # Sleep for cleanup interval (run every hour)
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)

    async def _collect_all_metrics(self) -> List[MetricPoint]:
        """Collect metrics from all configured sources"""        all_metrics = []
        
        try:
            # Collect from data sources
            for source_name, collector_func in self.data_sources.items():
                try:
                    source_metrics = await self._safe_collect(collector_func, source_name)
                    all_metrics.extend(source_metrics)
                except Exception as e:
                    self.logger.error(f"Error collecting from {source_name}: {e}")
            
            # Collect from custom collectors
            for collector_func in self.custom_collectors:
                try:
                    custom_metrics = await self._safe_collect(collector_func, "custom")
                    all_metrics.extend(custom_metrics)
                except Exception as e:
                    self.logger.error(f"Error in custom collector: {e}")
            
            return all_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting all metrics: {e}")
            return []

    async def _safe_collect(self, collector_func: Callable, source_name: str) -> List[MetricPoint]:
        """Safely execute a collector function"""        try:
            if asyncio.iscoroutinefunction(collector_func):
                result = await collector_func()
            else:
                result = collector_func()
            
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                # Convert dict to MetricPoint list
                return [
                    MetricPoint(
                        name=name,
                        value=value,
                        timestamp=datetime.now(),
                        tags={"source": source_name}
                    )
                    for name, value in result.items()
                ]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error in collector {source_name}: {e}")
            return []

    async def _store_raw_metrics(self, metrics: List[MetricPoint]):
        """Store raw metrics in memory"""        try:
            with self.metrics_lock:
                for metric in metrics:
                    self.raw_metrics[metric.name].append(metric)
            
            # Send to external metrics system if configured
            if self.metrics_client:
                for metric in metrics:
                    if metric.metric_type == MetricType.COUNTER:
                        self.metrics_client.increment(metric.name, metric.value, tags=metric.tags)
                    elif metric.metric_type == MetricType.GAUGE:
                        self.metrics_client.gauge(metric.name, metric.value, tags=metric.tags)
                    elif metric.metric_type == MetricType.HISTOGRAM:
                        self.metrics_client.histogram(metric.name, metric.value, tags=metric.tags)
                    elif metric.metric_type == MetricType.TIMER:
                        self.metrics_client.timing(metric.name, metric.value, tags=metric.tags)
                        
        except Exception as e:
            self.logger.error(f"Error storing raw metrics: {e}")

    async def _perform_aggregation(self, interval_seconds: int):
        """Perform aggregation for a specific time interval"""        try:
            current_time = datetime.now()
            start_time = current_time - timedelta(seconds=interval_seconds)
            
            with self.aggregation_lock:
                for metric_name, metric_points in self.raw_metrics.items():
                    # Filter metrics within the time window
                    recent_points = [
                        point for point in metric_points 
                        if point.timestamp >= start_time
                    ]
                    
                    if not recent_points:
                        continue
                    
                    # Get metric definition
                    metric_def = self.metric_definitions.get(metric_name)
                    if not metric_def:
                        continue
                    
                    # Perform aggregations
                    aggregated = await self._aggregate_metrics(
                        metric_name, recent_points, interval_seconds, start_time, current_time
                    )
                    
                    # Store aggregated metrics
                    for agg_metric in aggregated:
                        self.aggregated_metrics[metric_name][interval_seconds].append(agg_metric)
                        
        except Exception as e:
            self.logger.error(f"Error performing aggregation for {interval_seconds}s interval: {e}")

    async def _aggregate_metrics(self, metric_name: str, 
                                points: List[MetricPoint],
                                interval_seconds: int,
                                start_time: datetime,
                                end_time: datetime) -> List[AggregatedMetric]:
        """Aggregate a list of metric points"""        try:
            if not points:
                return []
            
            values = [point.value for point in points]
            aggregated_metrics = []
            
            # Common tags from all points
            common_tags = {}
            if points:
                common_tags = points[0].tags.copy()
            
            # Basic aggregations
            aggregations = {
                AggregationType.COUNT: len(values),
                AggregationType.SUM: sum(values),
                AggregationType.AVERAGE: statistics.mean(values),
                AggregationType.MIN: min(values),
                AggregationType.MAX: max(values)
            }
            
            # Advanced aggregations
            if len(values) > 1:
                try:
                    aggregations[AggregationType.MEDIAN] = statistics.median(values)
                    aggregations[AggregationType.STDDEV] = statistics.stdev(values)
                except:
                    pass
                
                # Percentiles
                try:
                    sorted_values = sorted(values)
                    p95_idx = int(len(sorted_values) * 0.95)
                    p99_idx = int(len(sorted_values) * 0.99)
                    
                    aggregations[AggregationType.PERCENTILE_95] = sorted_values[p95_idx]
                    aggregations[AggregationType.PERCENTILE_99] = sorted_values[p99_idx]
                except:
                    pass
            
            # Create aggregated metric objects
            for agg_type, value in aggregations.items():
                aggregated_metrics.append(
                    AggregatedMetric(
                        name=f"{metric_name}_{agg_type.value}",
                        aggregation_type=agg_type,
                        value=value,
                        count=len(values),
                        start_time=start_time,
                        end_time=end_time,
                        tags=common_tags
                    )
                )
            
            return aggregated_metrics
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics for {metric_name}: {e}")
            return []

    async def _export_metrics(self):
        """Export metrics to configured destinations"""        try:
            for format_name, handler in self.export_handlers.items():
                try:
                    await self._export_to_format(format_name, handler)
                except Exception as e:
                    self.logger.error(f"Error exporting to {format_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in metrics export: {e}")

    async def _export_to_format(self, format_name: str, handler: Callable):
        """Export metrics using specific format handler"""        try:
            # Prepare export data
            export_data = await self._prepare_export_data()
            
            # Call the handler
            if asyncio.iscoroutinefunction(handler):
                await handler(export_data)
            else:
                handler(export_data)
                
        except Exception as e:
            self.logger.error(f"Error exporting to {format_name}: {e}")

    async def _prepare_export_data(self) -> Dict[str, Any]:
        """Prepare data for export"""        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "raw_metrics": {},
                "aggregated_metrics": {},
                "metadata": {
                    "collector_stats": self.collector_stats,
                    "metric_definitions": {
                        name: {
                            "type": defn.metric_type.value,
                            "description": defn.description,
                            "unit": defn.unit
                        }
                        for name, defn in self.metric_definitions.items()
                    }
                }
            }
            
            # Add recent raw metrics (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            with self.metrics_lock:
                for metric_name, points in self.raw_metrics.items():
                    recent_points = [
                        {
                            "value": point.value,
                            "timestamp": point.timestamp.isoformat(),
                            "tags": point.tags
                        }
                        for point in points
                        if point.timestamp >= cutoff_time
                    ]
                    
                    if recent_points:
                        export_data["raw_metrics"][metric_name] = recent_points
            
            # Add aggregated metrics
            with self.aggregation_lock:
                for metric_name, intervals in self.aggregated_metrics.items():
                    export_data["aggregated_metrics"][metric_name] = {}
                    
                    for interval, agg_metrics in intervals.items():
                        if agg_metrics:
                            latest_agg = agg_metrics[-1]  # Get latest aggregation
                            export_data["aggregated_metrics"][metric_name][f"{interval}s"] = {
                                "value": latest_agg.value,
                                "aggregation_type": latest_agg.aggregation_type.value,
                                "count": latest_agg.count,
                                "start_time": latest_agg.start_time.isoformat(),
                                "end_time": latest_agg.end_time.isoformat()
                            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error preparing export data: {e}")
            return {}

    async def _cleanup_old_metrics(self):
        """Clean up old metrics data"""        try:
            current_time = datetime.now()
            
            with self.metrics_lock:
                for metric_name, points in self.raw_metrics.items():
                    metric_def = self.metric_definitions.get(metric_name)
                    retention_days = metric_def.retention_days if metric_def else 7
                    cutoff_time = current_time - timedelta(days=retention_days)
                    
                    # Remove old points
                    while points and points[0].timestamp < cutoff_time:
                        points.popleft()
            
            with self.aggregation_lock:
                for metric_name, intervals in self.aggregated_metrics.items():
                    for interval, agg_metrics in intervals.items():
                        # Keep aggregated metrics for longer (30 days)
                        cutoff_time = current_time - timedelta(days=30)
                        
                        while agg_metrics and agg_metrics[0].start_time < cutoff_time:
                            agg_metrics.popleft()
            
            self.logger.debug("Cleaned up old metrics data")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")

    async def _initialize_default_metrics(self):
        """Initialize default metric definitions"""        try:
            default_metrics = {
                "cpu_utilization": MetricDefinition(
                    name="cpu_utilization",
                    metric_type=MetricType.GAUGE,
                    description="CPU utilization percentage",
                    unit="percent"
                ),
                "memory_utilization": MetricDefinition(
                    name="memory_utilization",
                    metric_type=MetricType.GAUGE,
                    description="Memory utilization percentage",
                    unit="percent"
                ),
                "request_rate": MetricDefinition(
                    name="request_rate",
                    metric_type=MetricType.GAUGE,
                    description="Requests per second",
                    unit="requests/sec"
                ),
                "response_time": MetricDefinition(
                    name="response_time",
                    metric_type=MetricType.HISTOGRAM,
                    description="Average response time",
                    unit="milliseconds"
                ),
                "error_rate": MetricDefinition(
                    name="error_rate",
                    metric_type=MetricType.GAUGE,
                    description="Error rate percentage",
                    unit="percent"
                ),
                "queue_length": MetricDefinition(
                    name="queue_length",
                    metric_type=MetricType.GAUGE,
                    description="Queue length",
                    unit="items"
                ),
                "active_connections": MetricDefinition(
                    name="active_connections",
                    metric_type=MetricType.GAUGE,
                    description="Active connections count",
                    unit="connections"
                ),
                "disk_usage": MetricDefinition(
                    name="disk_usage",
                    metric_type=MetricType.GAUGE,
                    description="Disk usage percentage",
                    unit="percent"
                ),
                "network_io": MetricDefinition(
                    name="network_io",
                    metric_type=MetricType.GAUGE,
                    description="Network I/O bytes per second",
                    unit="bytes/sec"
                )
            }
            
            self.metric_definitions.update(default_metrics)
            
        except Exception as e:
            self.logger.error(f"Error initializing default metrics: {e}")

    async def _initialize_data_sources(self):
        """Initialize default data sources"""        try:
            # System metrics collector
            self.data_sources["system"] = self._collect_system_metrics
            
            # Application metrics collector
            self.data_sources["application"] = self._collect_application_metrics
            
            # Custom metrics collector
            self.data_sources["custom"] = self._collect_custom_metrics
            
        except Exception as e:
            self.logger.error(f"Error initializing data sources: {e}")

    async def _collect_system_metrics(self) -> List[MetricPoint]:
        """Collect system-level metrics"""        try:
            import psutil
            
            metrics = []
            timestamp = datetime.now()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(MetricPoint(
                name="cpu_utilization",
                value=cpu_percent,
                timestamp=timestamp,
                metric_type=MetricType.GAUGE,
                tags={"source": "system"}
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(MetricPoint(
                name="memory_utilization",
                value=memory.percent,
                timestamp=timestamp,
                metric_type=MetricType.GAUGE,
                tags={"source": "system"}
            ))
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics.append(MetricPoint(
                name="disk_usage",
                value=disk.percent,
                timestamp=timestamp,
                metric_type=MetricType.GAUGE,
                tags={"source": "system"}
            ))
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics.append(MetricPoint(
                name="network_io",
                value=network.bytes_sent + network.bytes_recv,
                timestamp=timestamp,
                metric_type=MetricType.GAUGE,
                tags={"source": "system", "direction": "total"}
            ))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return []

    async def _collect_application_metrics(self) -> List[MetricPoint]:
        """Collect application-level metrics"""        try:
            metrics = []
            timestamp = datetime.now()
            
            # Simulate application metrics
            metrics.extend([
                MetricPoint(
                    name="request_rate",
                    value=150.0,  # Simulated
                    timestamp=timestamp,
                    metric_type=MetricType.GAUGE,
                    tags={"source": "application"}
                ),
                MetricPoint(
                    name="response_time",
                    value=250.0,  # Simulated
                    timestamp=timestamp,
                    metric_type=MetricType.HISTOGRAM,
                    tags={"source": "application"}
                ),
                MetricPoint(
                    name="error_rate",
                    value=0.02,  # Simulated
                    timestamp=timestamp,
                    metric_type=MetricType.GAUGE,
                    tags={"source": "application"}
                ),
                MetricPoint(
                    name="active_connections",
                    value=75.0,  # Simulated
                    timestamp=timestamp,
                    metric_type=MetricType.GAUGE,
                    tags={"source": "application"}
                )
            ])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting application metrics: {e}")
            return []

    async def _collect_custom_metrics(self) -> List[MetricPoint]:
        """Collect custom metrics"""        try:
            metrics = []
            timestamp = datetime.now()
            
            # Custom business metrics
            metrics.extend([
                MetricPoint(
                    name="queue_length",
                    value=25.0,  # Simulated
                    timestamp=timestamp,
                    metric_type=MetricType.GAUGE,
                    tags={"source": "custom", "queue": "main"}
                )
            ])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting custom metrics: {e}")
            return []

    async def add_metric_definition(self, definition: MetricDefinition):
        """Add a new metric definition"""        try:
            self.metric_definitions[definition.name] = definition
            self.logger.info(f"Added metric definition: {definition.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding metric definition: {e}")
            raise MetricsException(f"Failed to add metric definition: {e}")

    async def add_custom_collector(self, collector_func: Callable):
        """Add a custom metrics collector function"""        try:
            self.custom_collectors.append(collector_func)
            self.logger.info(f"Added custom collector")
            
        except Exception as e:
            self.logger.error(f"Error adding custom collector: {e}")
            raise MetricsException(f"Failed to add custom collector: {e}")

    async def record_metric(self, name: str, value: float, 
                           metric_type: MetricType = MetricType.GAUGE,
                           tags: Optional[Dict[str, str]] = None):
        """Record a single metric point"""        try:
            metric_point = MetricPoint(
                name=name,
                value=value,
                timestamp=datetime.now(),
                metric_type=metric_type,
                tags=tags or {}
            )
            
            with self.metrics_lock:
                self.raw_metrics[name].append(metric_point)
            
            # Send to external metrics system
            if self.metrics_client:
                if metric_type == MetricType.COUNTER:
                    self.metrics_client.increment(name, value, tags=tags)
                elif metric_type == MetricType.GAUGE:
                    self.metrics_client.gauge(name, value, tags=tags)
                elif metric_type == MetricType.HISTOGRAM:
                    self.metrics_client.histogram(name, value, tags=tags)
                elif metric_type == MetricType.TIMER:
                    self.metrics_client.timing(name, value, tags=tags)
                    
        except Exception as e:
            self.logger.error(f"Error recording metric {name}: {e}")

    async def get_metric_data(self, metric_name: str, 
                             hours: int = 1) -> List[MetricPoint]:
        """Get raw metric data for a specific metric"""        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with self.metrics_lock:
                points = self.raw_metrics.get(metric_name, deque())
                return [point for point in points if point.timestamp >= cutoff_time]
                
        except Exception as e:
            self.logger.error(f"Error getting metric data for {metric_name}: {e}")
            return []

    async def get_aggregated_data(self, metric_name: str, 
                                 interval_seconds: int = 300,
                                 hours: int = 1) -> List[AggregatedMetric]:
        """Get aggregated metric data"""        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with self.aggregation_lock:
                agg_metrics = self.aggregated_metrics.get(metric_name, {}).get(interval_seconds, deque())
                return [agg for agg in agg_metrics if agg.start_time >= cutoff_time]
                
        except Exception as e:
            self.logger.error(f"Error getting aggregated data for {metric_name}: {e}")
            return []

    async def get_collector_status(self) -> Dict[str, Any]:
        """Get comprehensive collector status"""        try:
            return {
                "collecting": self.is_collecting,
                "active_tasks": len([task for task in self.collection_tasks if not task.done()]),
                "data_sources": list(self.data_sources.keys()),
                "custom_collectors": len(self.custom_collectors),
                "metric_definitions": len(self.metric_definitions),
                "raw_metrics": {name: len(points) for name, points in self.raw_metrics.items()},
                "aggregated_metrics": {
                    name: {interval: len(agg_list) for interval, agg_list in intervals.items()}
                    for name, intervals in self.aggregated_metrics.items()
                },
                "collector_stats": self.collector_stats,
                "export_handlers": list(self.export_handlers.keys())
            }
        except Exception as e:
            self.logger.error(f"Error getting collector status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for metrics collector"""        try:
            active_tasks = len([task for task in self.collection_tasks if not task.done()])
            collection_health = self.is_collecting and active_tasks > 0
            
            # Check if we're collecting metrics regularly
            last_collection_recent = (
                self.collector_stats["last_collection_duration"] > 0 and
                time.time() - self.collector_stats.get("last_collection_time", 0) < 120
            )
            
            return {
                "status": "healthy" if collection_health else "unhealthy",
                "collecting": self.is_collecting,
                "active_tasks": active_tasks,
                "total_tasks": len(self.collection_tasks),
                "metrics_collected": self.collector_stats["total_metrics_collected"],
                "collection_errors": self.collector_stats["collection_errors"],
                "last_collection_duration": self.collector_stats["last_collection_duration"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
