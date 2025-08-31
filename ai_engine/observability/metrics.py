"""
Metrics Collection and Management System

Comprehensive metrics system for the IA Influencer platform providing
real-time metrics collection, aggregation, and analysis capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import time
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import json
import statistics
import logging
import weakref

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics following Prometheus conventions"""
    COUNTER = "counter"         # Monotonically increasing value
    GAUGE = "gauge"            # Current value that can go up/down
    HISTOGRAM = "histogram"    # Distribution of values with buckets
    SUMMARY = "summary"        # Sample observations with quantiles
    RATE = "rate"              # Rate of change over time


class MetricUnit(Enum):
    """Standard metric units"""
    # Time units
    NANOSECONDS = "nanoseconds"
    MICROSECONDS = "microseconds"
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    
    # Size units
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"
    
    # Count units
    COUNT = "count"
    REQUESTS = "requests"
    OPERATIONS = "operations"
    ERRORS = "errors"
    
    # Percentage
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    
    # Business units
    USERS = "users"
    CREATORS = "creators"
    CONTENT_ITEMS = "content_items"
    REVENUE = "revenue"


@dataclass
class MetricSample:
    """Individual metric sample/measurement"""
    timestamp: datetime
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'labels': self.labels
        }


@dataclass
class MetricDefinition:
    """Metric definition with metadata"""
    name: str
    metric_type: MetricType
    unit: MetricUnit
    description: str
    help_text: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    
    # Histogram/Summary specific
    buckets: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None
    
    # Retention and aggregation
    retention_period: timedelta = field(default_factory=lambda: timedelta(hours=24))
    aggregation_intervals: List[int] = field(default_factory=lambda: [60, 300, 3600])  # 1m, 5m, 1h
    
    def __post_init__(self):
        # Set default buckets for histograms
        if self.metric_type == MetricType.HISTOGRAM and not self.buckets:
            self.buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        
        # Set default quantiles for summaries
        if self.metric_type == MetricType.SUMMARY and not self.quantiles:
            self.quantiles = [0.5, 0.9, 0.95, 0.99]


class Counter:
    """Counter metric implementation"""
    
    def __init__(self, definition: MetricDefinition):
        self.definition = definition
        self._value = 0.0
        self._lock = threading.Lock()
        self.samples: deque = deque(maxlen=10000)
    
    def inc(self, amount: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None):
        """Increment counter"""
        if amount < 0:
            raise ValueError("Counter can only be incremented by non-negative values")
        
        with self._lock:
            self._value += amount
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=self._value,
                labels=labels or {}
            )
            self.samples.append(sample)
    
    def get_value(self) -> float:
        """Get current counter value"""



        return self._value
    
    def get_samples(self, since: Optional[datetime] = None) -> List[MetricSample]:
        """Get samples since specified time"""
        if since is None:
            return list(self.samples)
        
        return [s for s in self.samples if s.timestamp >= since]


class Gauge:
    """Gauge metric implementation"""
    
    def __init__(self, definition: MetricDefinition):
        self.definition = definition
        self._value = 0.0
        self._lock = threading.Lock()
        self.samples: deque = deque(maxlen=10000)
    
    def set(self, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Set gauge value"""
        with self._lock:
            self._value = float(value)
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=self._value,
                labels=labels or {}
            )
            self.samples.append(sample)
    
    def inc(self, amount: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None):
        """Increment gauge"""
        with self._lock:
            self._value += amount
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=self._value,
                labels=labels or {}
            )
            self.samples.append(sample)
    
    def dec(self, amount: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None):
        """Decrement gauge"""
        with self._lock:
            self._value -= amount
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=self._value,
                labels=labels or {}
            )
            self.samples.append(sample)
    
    def get_value(self) -> float:
        """Get current gauge value"""



        return self._value
    
    def get_samples(self, since: Optional[datetime] = None) -> List[MetricSample]:
        """Get samples since specified time"""
        if since is None:
            return list(self.samples)
        
        return [s for s in self.samples if s.timestamp >= since]


class Histogram:
    """Histogram metric implementation"""
    
    def __init__(self, definition: MetricDefinition):
        self.definition = definition
        self.buckets = definition.buckets or []
        self._bucket_counts = {bucket: 0 for bucket in self.buckets}
        self._bucket_counts['inf'] = 0  # +Inf bucket
        self._sum = 0.0
        self._count = 0
        self._lock = threading.Lock()
        self.samples: deque = deque(maxlen=10000)
    
    def observe(self, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Observe a value"""
        value = float(value)
        
        with self._lock:
            # Update sum and count
            self._sum += value
            self._count += 1
            
            # Update buckets
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1
            
            # Always update +Inf bucket
            self._bucket_counts['inf'] += 1
            
            # Store sample
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=value,
                labels=labels or {}
            )
            self.samples.append(sample)
    
    def get_bucket_counts(self) -> Dict[Union[float, str], int]:
        """Get bucket counts"""



        return self._bucket_counts.copy()
    
    def get_sum(self) -> float:
        """Get sum of all observed values"""



        return self._sum
    
    def get_count(self) -> int:
        """Get count of all observations"""



        return self._count
    
    def get_quantile(self, quantile: float) -> Optional[float]:
        """Calculate quantile from histogram data"""
        if not self.samples:
            return None
        
        values = sorted([s.value for s in self.samples])
        index = int(len(values) * quantile)
        return values[min(index, len(values) - 1)]
    
    def get_samples(self, since: Optional[datetime] = None) -> List[MetricSample]:
        """Get samples since specified time"""
        if since is None:
            return list(self.samples)
        
        return [s for s in self.samples if s.timestamp >= since]


class Summary:
    """Summary metric implementation"""
    
    def __init__(self, definition: MetricDefinition):
        self.definition = definition
        self.quantiles = definition.quantiles or []
        self._sum = 0.0
        self._count = 0
        self._lock = threading.Lock()
        self.samples: deque = deque(maxlen=10000)
    
    def observe(self, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Observe a value"""
        value = float(value)
        
        with self._lock:
            self._sum += value
            self._count += 1
            
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=value,
                labels=labels or {}
            )
            self.samples.append(sample)
    
    def get_sum(self) -> float:
        """Get sum of all observed values"""



        return self._sum
    
    def get_count(self) -> int:
        """Get count of all observations"""



        return self._count
    
    def get_quantiles(self) -> Dict[float, float]:
        """Calculate quantiles"""
        if not self.samples:
            return {}
        
        values = sorted([s.value for s in self.samples])
        quantiles = {}
        
        for q in self.quantiles:
            index = int(len(values) * q)
            quantiles[q] = values[min(index, len(values) - 1)]
        
        return quantiles
    
    def get_samples(self, since: Optional[datetime] = None) -> List[MetricSample]:
        """Get samples since specified time"""
        if since is None:
            return list(self.samples)
        
        return [s for s in self.samples if s.timestamp >= since]


class MetricsCollector:
    """
    Main metrics collector managing all metric types
    
    Features:
    - Multiple metric type support
    - Automatic aggregation
    - Time-based retention
    - Label-based filtering
    - Export to various backends
    - Performance optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics collector"""
        self.config = config or {}
        
        # Collector configuration
        self.namespace = self.config.get('namespace', 'ia_influencer')
        self.collection_interval = self.config.get('collection_interval', 60)  # seconds
        self.retention_period = self.config.get('retention_period', 86400)  # 24 hours
        
        # Metrics storage
        self.metrics: Dict[str, Union[Counter, Gauge, Histogram, Summary]] = {}
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        
        # Aggregation
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}
        self.last_aggregation = datetime.now(timezone.utc)
        
        # Background processing
        self.is_collecting = False
        self.collection_task = None
        self.cleanup_task = None
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Exporters
        self.exporters: List[Any] = []
    
    def register_metric(self, definition: MetricDefinition) -> Union[Counter, Gauge, Histogram, Summary]:
        """Register a new metric"""
        
        with self._lock:
            metric_name = f"{self.namespace}_{definition.name}"
            
            if metric_name in self.metrics:
                return self.metrics[metric_name]
            
            # Create metric instance based on type
            if definition.metric_type == MetricType.COUNTER:
                metric = Counter(definition)
            elif definition.metric_type == MetricType.GAUGE:
                metric = Gauge(definition)
            elif definition.metric_type == MetricType.HISTOGRAM:
                metric = Histogram(definition)
            elif definition.metric_type == MetricType.SUMMARY:
                metric = Summary(definition)
            else:
                raise ValueError(f"Unsupported metric type: {definition.metric_type}")
            
            self.metrics[metric_name] = metric
            self.metric_definitions[metric_name] = definition
            
            logger.debug(f"Registered metric: {metric_name} ({definition.metric_type.value})")
            return metric
    
    def counter(self, name: str, description: str, labels: Optional[List[str]] = None) -> Counter:
        """Create or get a counter metric"""
        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description=description,
            labels=labels or []
        )
        return self.register_metric(definition)
    
    def gauge(self, name: str, description: str, unit: MetricUnit = MetricUnit.COUNT,
             labels: Optional[List[str]] = None) -> Gauge:
        """Create or get a gauge metric"""
        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.GAUGE,
            unit=unit,
            description=description,
            labels=labels or []
        )
        return self.register_metric(definition)
    
    def histogram(self, name: str, description: str, unit: MetricUnit = MetricUnit.SECONDS,
                 buckets: Optional[List[float]] = None, labels: Optional[List[str]] = None) -> Histogram:
        """Create or get a histogram metric"""
        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.HISTOGRAM,
            unit=unit,
            description=description,
            buckets=buckets,
            labels=labels or []
        )
        return self.register_metric(definition)
    
    def summary(self, name: str, description: str, unit: MetricUnit = MetricUnit.SECONDS,
               quantiles: Optional[List[float]] = None, labels: Optional[List[str]] = None) -> Summary:
        """Create or get a summary metric"""
        definition = MetricDefinition(
            name=name,
            metric_type=MetricType.SUMMARY,
            unit=unit,
            description=description,
            quantiles=quantiles,
            labels=labels or []
        )
        return self.register_metric(definition)
    
    def get_metric(self, name: str) -> Optional[Union[Counter, Gauge, Histogram, Summary]]:
        """Get metric by name"""
        metric_name = f"{self.namespace}_{name}"
        return self.metrics.get(metric_name)
    
    def get_all_metrics(self) -> Dict[str, Union[Counter, Gauge, Histogram, Summary]]:
        """Get all metrics"""



        return self.metrics.copy()
    
    async def start_collection(self):
        """Start metrics collection background tasks"""



        try:
            logger.info("Starting metrics collection")
            self.is_collecting = True
            
            # Start collection and cleanup tasks
            self.collection_task = asyncio.create_task(self._collection_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
        except Exception as e:
            logger.error(f"Failed to start metrics collection: {str(e)}")
    
    async def stop_collection(self):
        """Stop metrics collection background tasks"""



        try:
            logger.info("Stopping metrics collection")
            self.is_collecting = False
            
            if self.collection_task:
                self.collection_task.cancel()
            
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
        except Exception as e:
            logger.error(f"Failed to stop metrics collection: {str(e)}")
    
    async def _collection_loop(self):
        """Main collection loop for aggregation and export"""
        while self.is_collecting:
            try:
                # Perform aggregation
                await self._aggregate_metrics()
                
                # Export metrics if exporters are configured
                if self.exporters:
                    await self._export_metrics()
                
                # Wait for next collection interval
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _cleanup_loop(self):
        """Cleanup loop for removing old metrics data"""
        while self.is_collecting:
            try:
                await self._cleanup_old_data()
                
                # Run cleanup every hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics cleanup loop: {str(e)}")
                await asyncio.sleep(300)  # 5 minutes pause on error
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for different time intervals"""



        try:
            current_time = datetime.now(timezone.utc)
            aggregation_window = current_time - self.last_aggregation
            
            for metric_name, metric in self.metrics.items():
                definition = self.metric_definitions.get(metric_name)
                if not definition:
                    continue
                
                # Get samples from aggregation window
                samples = metric.get_samples(since=self.last_aggregation)
                if not samples:
                    continue
                
                # Aggregate based on intervals defined in metric definition
                for interval in definition.aggregation_intervals:
                    interval_key = f"{metric_name}_{interval}s"
                    
                    # Calculate aggregated values
                    aggregated_data = self._calculate_aggregation(samples, interval, definition.metric_type)
                    
                    if interval_key not in self.aggregated_metrics:
                        self.aggregated_metrics[interval_key] = {}
                    
                    self.aggregated_metrics[interval_key][current_time.isoformat()] = aggregated_data
            
            self.last_aggregation = current_time
            
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {str(e)}")
    
    def _calculate_aggregation(self, samples: List[MetricSample], 
                              interval_seconds: int, metric_type: MetricType) -> Dict[str, Any]:
        """Calculate aggregation for samples within an interval"""
        
        if not samples:
            return {}
        
        values = [s.value for s in samples]
        
        if metric_type == MetricType.COUNTER:
            # For counters, we want the increase over the interval
            return {
                'increase': values[-1] - values[0] if len(values) > 1 else values[0],
                'rate': (values[-1] - values[0]) / interval_seconds if len(values) > 1 and interval_seconds > 0 else 0,
                'sample_count': len(samples)
            }
        
        elif metric_type == MetricType.GAUGE:
            return {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'last': values[-1],
                'sample_count': len(samples)
            }
        
        elif metric_type in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
            return {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'sum': sum(values),
                'count': len(values),
                'p50': statistics.median(values),
                'p95': self._calculate_percentile(sorted(values), 0.95),
                'p99': self._calculate_percentile(sorted(values), 0.99),
                'sample_count': len(samples)
            }
        
        return {}
    
    def _calculate_percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile from sorted values"""
        if not sorted_values:
            return 0.0
        
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    async def _cleanup_old_data(self):
        """Clean up old metrics data"""



        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.retention_period)
            
            # Clean up metric samples
            for metric in self.metrics.values():
                if hasattr(metric, 'samples'):
                    # Filter samples to keep only recent ones
                    recent_samples = deque(
                        [s for s in metric.samples if s.timestamp >= cutoff_time],
                        maxlen=metric.samples.maxlen
                    )
                    metric.samples = recent_samples
            
            # Clean up aggregated metrics
            for interval_key in list(self.aggregated_metrics.keys()):
                interval_data = self.aggregated_metrics[interval_key]
                recent_data = {
                    timestamp: data for timestamp, data in interval_data.items()
                    if datetime.fromisoformat(timestamp.replace('Z', '+00:00')) >= cutoff_time
                }
                self.aggregated_metrics[interval_key] = recent_data
            
            logger.debug(f"Cleaned up metrics data older than {cutoff_time}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics data: {str(e)}")
    
    async def _export_metrics(self):
        """Export metrics to configured backends"""



        try:
            # Prepare metrics data for export
            metrics_data = await self._prepare_export_data()
            
            # Export to all configured exporters
            for exporter in self.exporters:
                try:
                    await self._export_to_backend(exporter, metrics_data)
                except Exception as e:
                    logger.error(f"Failed to export to {type(exporter).__name__}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to export metrics: {str(e)}")
    
    async def _prepare_export_data(self) -> Dict[str, Any]:
        """Prepare metrics data for export"""
        export_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'namespace': self.namespace,
            'metrics': {},
            'aggregated_metrics': self.aggregated_metrics
        }
        
        # Include current metric values
        for metric_name, metric in self.metrics.items():
            metric_info = {
                'type': self.metric_definitions[metric_name].metric_type.value,
                'unit': self.metric_definitions[metric_name].unit.value,
                'description': self.metric_definitions[metric_name].description
            }
            
            if isinstance(metric, Counter):
                metric_info['value'] = metric.get_value()
            elif isinstance(metric, Gauge):
                metric_info['value'] = metric.get_value()
            elif isinstance(metric, Histogram):
                metric_info.update({
                    'sum': metric.get_sum(),
                    'count': metric.get_count(),
                    'buckets': metric.get_bucket_counts()
                })
            elif isinstance(metric, Summary):
                metric_info.update({
                    'sum': metric.get_sum(),
                    'count': metric.get_count(),
                    'quantiles': metric.get_quantiles()
                })
            
            export_data['metrics'][metric_name] = metric_info
        
        return export_data
    
    async def _export_to_backend(self, exporter: Any, data: Dict[str, Any]):
        """Export data to specific backend"""
        # This would be implemented based on specific exporter type
        # (Prometheus, InfluxDB, CloudWatch, etc.)
        pass
    
    def add_exporter(self, exporter: Any):
        """Add metrics exporter"""
        self.exporters.append(exporter)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'total_metrics': len(self.metrics),
            'metrics_by_type': {},
            'recent_activity': {},
            'aggregation_status': {
                'last_aggregation': self.last_aggregation.isoformat(),
                'aggregated_intervals': len(self.aggregated_metrics)
            }
        }
        
        # Count metrics by type
        for metric_name, definition in self.metric_definitions.items():
            metric_type = definition.metric_type.value
            if metric_type not in summary['metrics_by_type']:
                summary['metrics_by_type'][metric_type] = 0
            summary['metrics_by_type'][metric_type] += 1
        
        # Get recent activity (last 5 minutes)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
        for metric_name, metric in self.metrics.items():
            recent_samples = metric.get_samples(since=recent_cutoff)
            if recent_samples:
                summary['recent_activity'][metric_name] = len(recent_samples)
        
        return summary


class MetricsAggregator:
    """
    Advanced metrics aggregator for multi-dimensional analysis
    and real-time processing of metric streams.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics aggregator"""
        self.config = config or {}
        
        # Aggregation configuration
        self.aggregation_windows = self.config.get('windows', [60, 300, 900, 3600])  # 1m, 5m, 15m, 1h
        self.max_series = self.config.get('max_series', 10000)
        self.retention_factor = self.config.get('retention_factor', 0.8)
        
        # Storage for aggregated data
        self.aggregated_data: Dict[str, Dict[int, Dict[str, Any]]] = defaultdict(lambda: defaultdict(dict))
        self.series_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Processing state
        self.last_processed = {}
        self.processing_lock = threading.Lock()
    
    async def aggregate_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate metrics across different time windows"""



        
        try:
            timestamp = datetime.now(timezone.utc)
            
            aggregation_results = {
                'timestamp': timestamp.isoformat(),
                'windows': {},
                'series_count': 0,
                'processing_stats': {}
            }
            
            # Process each aggregation window
            for window_seconds in self.aggregation_windows:
                window_results = await self._aggregate_window(metrics_data, window_seconds, timestamp)
                aggregation_results['windows'][f"{window_seconds}s"] = window_results
            
            # Calculate series count
            aggregation_results['series_count'] = len(self.series_metadata)
            
            # Add processing statistics
            aggregation_results['processing_stats'] = {
                'processed_at': timestamp.isoformat(),
                'total_series': len(self.series_metadata),
                'active_windows': len(self.aggregation_windows)
            }
            
            return aggregation_results
            
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {str(e)}")
            return {}
    
    async def _aggregate_window(self, metrics_data: Dict[str, Any], 
                               window_seconds: int, timestamp: datetime) -> Dict[str, Any]:
        """Aggregate metrics for a specific time window"""
        
        window_results = {
            'window_seconds': window_seconds,
            'aggregated_metrics': {},
            'summary_stats': {}
        }
        
        # Calculate window boundaries
        window_start = timestamp.replace(second=0, microsecond=0)
        window_start = window_start.replace(
            minute=(window_start.minute // (window_seconds // 60)) * (window_seconds // 60)
        )
        
        try:
            # Aggregate each metric
            for metric_name, metric_info in metrics_data.get('metrics', {}).items():
                aggregated_metric = await self._aggregate_metric_for_window(
                    metric_name, metric_info, window_seconds, window_start
                )
                window_results['aggregated_metrics'][metric_name] = aggregated_metric
            
            # Calculate summary statistics
            window_results['summary_stats'] = self._calculate_window_stats(
                window_results['aggregated_metrics']
            )
            
        except Exception as e:
            logger.error(f"Failed to aggregate window {window_seconds}s: {str(e)}")
        
        return window_results
    
    async def _aggregate_metric_for_window(self, metric_name: str, metric_info: Dict[str, Any],
                                         window_seconds: int, window_start: datetime) -> Dict[str, Any]:
        """Aggregate a single metric for a time window"""
        
        metric_type = metric_info.get('type')
        
        if metric_type == 'counter':
            return await self._aggregate_counter(metric_name, metric_info, window_seconds, window_start)
        elif metric_type == 'gauge':
            return await self._aggregate_gauge(metric_name, metric_info, window_seconds, window_start)
        elif metric_type in ['histogram', 'summary']:
            return await self._aggregate_distribution(metric_name, metric_info, window_seconds, window_start)
        
        return {}
    
    async def _aggregate_counter(self, metric_name: str, metric_info: Dict[str, Any],
                               window_seconds: int, window_start: datetime) -> Dict[str, Any]:
        """Aggregate counter metric"""
        
        current_value = metric_info.get('value', 0)
        series_key = f"{metric_name}_{window_seconds}"
        
        # Get previous value for rate calculation
        previous_data = self.aggregated_data[series_key].get(
            int(window_start.timestamp()) - window_seconds, {}
        )
        previous_value = previous_data.get('value', 0)
        
        # Calculate rate
        rate = (current_value - previous_value) / window_seconds if window_seconds > 0 else 0
        
        aggregated = {
            'value': current_value,
            'increase': current_value - previous_value,
            'rate': rate,
            'window_seconds': window_seconds
        }
        
        # Store aggregated data
        self.aggregated_data[series_key][int(window_start.timestamp())] = aggregated
        
        return aggregated
    
    async def _aggregate_gauge(self, metric_name: str, metric_info: Dict[str, Any],
                             window_seconds: int, window_start: datetime) -> Dict[str, Any]:
        """Aggregate gauge metric"""
        
        current_value = metric_info.get('value', 0)
        series_key = f"{metric_name}_{window_seconds}"
        
        # For gauges, we track changes and averages over the window
        window_data = []
        
        # Collect values from the window
        for ts, data in self.aggregated_data[series_key].items():
            window_ts = datetime.fromtimestamp(ts, tz=timezone.utc)
            if window_start <= window_ts < window_start + timedelta(seconds=window_seconds):
                window_data.append(data.get('value', 0))
        
        # Add current value
        window_data.append(current_value)
        
        aggregated = {
            'value': current_value,
            'min': min(window_data) if window_data else current_value,
            'max': max(window_data) if window_data else current_value,
            'avg': sum(window_data) / len(window_data) if window_data else current_value,
            'samples': len(window_data),
            'window_seconds': window_seconds
        }
        
        # Store aggregated data
        self.aggregated_data[series_key][int(window_start.timestamp())] = aggregated
        
        return aggregated
    
    async def _aggregate_distribution(self, metric_name: str, metric_info: Dict[str, Any],
                                    window_seconds: int, window_start: datetime) -> Dict[str, Any]:
        """Aggregate histogram/summary metric"""
        
        series_key = f"{metric_name}_{window_seconds}"
        
        aggregated = {
            'sum': metric_info.get('sum', 0),
            'count': metric_info.get('count', 0),
            'avg': metric_info.get('sum', 0) / max(metric_info.get('count', 1), 1),
            'window_seconds': window_seconds
        }
        
        # Add quantiles if available
        if 'quantiles' in metric_info:
            aggregated['quantiles'] = metric_info['quantiles']
        
        # Add bucket data if available
        if 'buckets' in metric_info:
            aggregated['buckets'] = metric_info['buckets']
        
        # Store aggregated data
        self.aggregated_data[series_key][int(window_start.timestamp())] = aggregated
        
        return aggregated
    
    def _calculate_window_stats(self, aggregated_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for a window"""
        
        stats = {
            'total_metrics': len(aggregated_metrics),
            'metric_types': {},
            'value_ranges': {}
        }
        
        for metric_name, metric_data in aggregated_metrics.items():
            # Count metric types (inferred from data structure)
            if 'rate' in metric_data:
                metric_type = 'counter'
            elif 'avg' in metric_data and 'min' in metric_data:
                metric_type = 'gauge'
            elif 'quantiles' in metric_data or 'buckets' in metric_data:
                metric_type = 'distribution'
            else:
                metric_type = 'unknown'
            
            if metric_type not in stats['metric_types']:
                stats['metric_types'][metric_type] = 0
            stats['metric_types'][metric_type] += 1
            
            # Track value ranges
            value = metric_data.get('value') or metric_data.get('avg', 0)
            if 'min_value' not in stats['value_ranges'] or value < stats['value_ranges']['min_value']:
                stats['value_ranges']['min_value'] = value
            if 'max_value' not in stats['value_ranges'] or value > stats['value_ranges']['max_value']:
                stats['value_ranges']['max_value'] = value
        
        return stats
    
    def get_aggregated_data(self, metric_name: str, window_seconds: int,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get aggregated data for a specific metric and window"""
        
        series_key = f"{metric_name}_{window_seconds}"
        series_data = self.aggregated_data.get(series_key, {})
        
        if not series_data:
            return []
        
        # Filter by time range if specified
        filtered_data = []
        for timestamp, data in sorted(series_data.items()):
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            
            if start_time and dt < start_time:
                continue
            if end_time and dt > end_time:
                break
            
            data_point = data.copy()
            data_point['timestamp'] = dt.isoformat()
            filtered_data.append(data_point)
        
        return filtered_data
    
    def cleanup_old_data(self, retention_hours: int = 24):
        """Clean up old aggregated data"""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=retention_hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        with self.processing_lock:
            for series_key in list(self.aggregated_data.keys()):
                series_data = self.aggregated_data[series_key]
                
                # Remove old data points
                old_timestamps = [ts for ts in series_data.keys() if ts < cutoff_timestamp]
                for ts in old_timestamps:
                    del series_data[ts]
                
                # Remove empty series
                if not series_data:
                    del self.aggregated_data[series_key]


class MetricsAnalyzer:
    """
    Advanced metrics analyzer for anomaly detection,
    trend analysis, and performance insights.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics analyzer"""
        self.config = config or {}
        
        # Analysis configuration
        self.anomaly_threshold = self.config.get('anomaly_threshold', 2.0)  # Standard deviations
        self.trend_window = self.config.get('trend_window', 3600)  # 1 hour in seconds
        self.min_samples = self.config.get('min_samples', 10)
        
        # Analysis state
        self.analysis_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.baselines: Dict[str, Dict[str, float]] = {}
    
    async def analyze_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive metrics analysis"""



        
        try:
            analysis_results = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'anomalies': [],
                'trends': [],
                'performance_insights': [],
                'recommendations': []
            }
            
            # Anomaly detection
            anomalies = await self._detect_anomalies(metrics_data)
            analysis_results['anomalies'] = anomalies
            
            # Trend analysis
            trends = await self._analyze_trends(metrics_data)
            analysis_results['trends'] = trends
            
            # Performance insights
            insights = await self._generate_performance_insights(metrics_data)
            analysis_results['performance_insights'] = insights
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(analysis_results)
            analysis_results['recommendations'] = recommendations
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {str(e)}")
            return {}
    
    async def _detect_anomalies(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics data"""
        
        anomalies = []
        
        try:
            for metric_name, metric_info in metrics_data.get('metrics', {}).items():
                # Get current value
                current_value = self._extract_metric_value(metric_info)
                if current_value is None:
                    continue
                
                # Get historical data for baseline
                baseline = self._get_or_calculate_baseline(metric_name, current_value)
                
                if baseline:
                    # Check for anomalies
                    anomaly = self._check_anomaly(metric_name, current_value, baseline)
                    if anomaly:
                        anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {str(e)}")
            return []
    
    def _extract_metric_value(self, metric_info: Dict[str, Any]) -> Optional[float]:
        """Extract numeric value from metric info"""
        
        # Try different value fields based on metric type
        for field in ['value', 'avg', 'sum', 'rate']:
            if field in metric_info:
                return float(metric_info[field])
        
        return None
    
    def _get_or_calculate_baseline(self, metric_name: str, current_value: float) -> Optional[Dict[str, float]]:
        """Get or calculate baseline statistics for a metric"""
        
        if metric_name not in self.baselines:
            # Initialize baseline with current value
            self.baselines[metric_name] = {
                'mean': current_value,
                'std': 0.0,
                'min': current_value,
                'max': current_value,
                'count': 1,
                'values': deque([current_value], maxlen=1000)
            }
            return None
        
        baseline = self.baselines[metric_name]
        
        # Add current value to baseline
        baseline['values'].append(current_value)
        baseline['count'] += 1
        
        # Recalculate statistics
        values = list(baseline['values'])
        baseline['mean'] = sum(values) / len(values)
        baseline['min'] = min(values)
        baseline['max'] = max(values)
        
        # Calculate standard deviation
        if len(values) > 1:
            variance = sum((x - baseline['mean']) ** 2 for x in values) / len(values)
            baseline['std'] = variance ** 0.5
        
        return baseline
    
    def _check_anomaly(self, metric_name: str, current_value: float, 
                      baseline: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Check if current value is anomalous"""
        
        if baseline['count'] < self.min_samples:
            return None
        
        if baseline['std'] == 0:
            return None
        
        # Calculate z-score
        z_score = abs(current_value - baseline['mean']) / baseline['std']
        
        if z_score > self.anomaly_threshold:
            severity = 'high' if z_score > self.anomaly_threshold * 2 else 'medium'
            
            return {
                'type': 'statistical_anomaly',
                'metric_name': metric_name,
                'current_value': current_value,
                'expected_value': baseline['mean'],
                'z_score': z_score,
                'severity': severity,
                'threshold': self.anomaly_threshold,
                'baseline_samples': baseline['count']
            }
        
        return None
    
    async def _analyze_trends(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze trends in metrics data"""
        
        trends = []
        
        try:
            # This would analyze historical data to identify trends
            # For now, we'll provide a basic implementation
            
            for metric_name, metric_info in metrics_data.get('metrics', {}).items():
                baseline = self.baselines.get(metric_name)
                if not baseline or baseline['count'] < 20:  # Need sufficient samples
                    continue
                
                # Analyze recent trend
                recent_values = list(baseline['values'])[-10:]  # Last 10 values
                if len(recent_values) >= 5:
                    trend_direction = self._calculate_trend_direction(recent_values)
                    trend_strength = self._calculate_trend_strength(recent_values)
                    
                    if abs(trend_strength) > 0.5:  # Significant trend
                        trends.append({
                            'metric_name': metric_name,
                            'direction': trend_direction,
                            'strength': trend_strength,
                            'recent_change_percent': ((recent_values[-1] - recent_values[0]) / 
                                                    max(abs(recent_values[0]), 1e-6)) * 100,
                            'samples_analyzed': len(recent_values)
                        })
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {str(e)}")
            return []
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return 'stable'
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.05:  # 5% increase
            return 'increasing'
        elif second_avg < first_avg * 0.95:  # 5% decrease
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength (-1 to 1)"""
        if len(values) < 3:
            return 0.0
        
        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))
        
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalize slope to [-1, 1] range
        max_value = max(abs(v) for v in values)
        if max_value > 0:
            normalized_slope = slope / max_value
            return max(-1.0, min(1.0, normalized_slope))
        
        return 0.0
    
    async def _generate_performance_insights(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance insights from metrics"""
        
        insights = []
        
        try:
            # Analyze response time metrics
            response_time_metrics = [
                name for name in metrics_data.get('metrics', {}).keys()
                if 'response_time' in name.lower() or 'latency' in name.lower() or 'duration' in name.lower()
            ]
            
            for metric_name in response_time_metrics:
                metric_info = metrics_data['metrics'][metric_name]
                current_value = self._extract_metric_value(metric_info)
                
                if current_value is not None:
                    if current_value > 1000:  # More than 1 second
                        insights.append({
                            'type': 'performance_concern',
                            'metric_name': metric_name,
                            'current_value': current_value,
                            'threshold': 1000,
                            'message': f'High response time detected: {current_value:.2f}ms',
                            'impact': 'user_experience'
                        })
            
            # Analyze error rate metrics
            error_metrics = [
                name for name in metrics_data.get('metrics', {}).keys()
                if 'error' in name.lower() or 'failure' in name.lower()
            ]
            
            for metric_name in error_metrics:
                metric_info = metrics_data['metrics'][metric_name]
                current_value = self._extract_metric_value(metric_info)
                
                if current_value is not None and current_value > 0:
                    insights.append({
                        'type': 'error_detection',
                        'metric_name': metric_name,
                        'current_value': current_value,
                        'message': f'Errors detected: {current_value}',
                        'impact': 'reliability'
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate performance insights: {str(e)}")
            return []
    
    async def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis results"""
        
        recommendations = []
        
        try:
            # Recommendations based on anomalies
            anomalies = analysis_results.get('anomalies', [])
            high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
            
            if high_severity_anomalies:
                recommendations.append({
                    'type': 'anomaly_investigation',
                    'priority': 'high',
                    'message': f'Investigate {len(high_severity_anomalies)} high-severity anomalies',
                    'action': 'investigate_anomalies',
                    'affected_metrics': [a['metric_name'] for a in high_severity_anomalies]
                })
            
            # Recommendations based on trends
            trends = analysis_results.get('trends', [])
            concerning_trends = [t for t in trends if 
                               t.get('direction') in ['increasing', 'decreasing'] and 
                               abs(t.get('strength', 0)) > 0.7]
            
            if concerning_trends:
                recommendations.append({
                    'type': 'trend_monitoring',
                    'priority': 'medium',
                    'message': f'Monitor {len(concerning_trends)} metrics with strong trends',
                    'action': 'monitor_trends',
                    'affected_metrics': [t['metric_name'] for t in concerning_trends]
                })
            
            # Recommendations based on performance insights
            performance_issues = analysis_results.get('performance_insights', [])
            critical_performance = [p for p in performance_issues if 
                                  p.get('type') == 'performance_concern']
            
            if critical_performance:
                recommendations.append({
                    'type': 'performance_optimization',
                    'priority': 'high',
                    'message': f'Optimize performance for {len(critical_performance)} slow operations',
                    'action': 'optimize_performance',
                    'affected_metrics': [p['metric_name'] for p in critical_performance]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return []


# Business-specific metrics classes
class CustomMetrics:
    """Custom metrics for IA Influencer platform specific use cases"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        
        # Content metrics
        self.content_uploads = collector.counter(
            "content_uploads_total",
            "Total number of content uploads",
            labels=["content_type", "creator_id"]
        )
        
        self.content_protection_time = collector.histogram(
            "content_protection_duration",
            "Time taken to protect content",
            unit=MetricUnit.MILLISECONDS,
            labels=["content_type", "protection_method"]
        )
        
        # AI model metrics
        self.model_inference_time = collector.histogram(
            "ai_model_inference_duration",
            "AI model inference time",
            unit=MetricUnit.MILLISECONDS,
            labels=["model_name", "model_version"]
        )
        
        self.model_accuracy = collector.gauge(
            "ai_model_accuracy",
            "Current model accuracy score",
            unit=MetricUnit.RATIO,
            labels=["model_name"]
        )


class BusinessMetrics:
    """Business-specific metrics for platform success tracking"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        
        # User engagement metrics
        self.active_creators = collector.gauge(
            "active_creators",
            "Number of active content creators",
            unit=MetricUnit.USERS
        )
        
        self.content_views = collector.counter(
            "content_views_total",
            "Total content views",
            labels=["content_type", "platform"]
        )
        
        # Revenue metrics
        self.revenue_generated = collector.counter(
            "revenue_generated_total",
            "Total revenue generated",
            labels=["revenue_source", "creator_tier"]
        )
        
        # Collaboration metrics
        self.collaborations_formed = collector.counter(
            "collaborations_formed_total",
            "Total collaborations formed through matching",
            labels=["collaboration_type"]
        )


class TechnicalMetrics:
    """Technical metrics for infrastructure and performance monitoring"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        
        # Infrastructure metrics
        self.cpu_usage = collector.gauge(
            "cpu_usage_percent",
            "CPU usage percentage",
            unit=MetricUnit.PERCENTAGE,
            labels=["service", "instance"]
        )
        
        self.memory_usage = collector.gauge(
            "memory_usage_bytes",
            "Memory usage in bytes",
            unit=MetricUnit.BYTES,
            labels=["service", "instance"]
        )
        
        # Database metrics
        self.db_query_time = collector.histogram(
            "database_query_duration",
            "Database query execution time",
            unit=MetricUnit.MILLISECONDS,
            labels=["query_type", "table"]
        )
        
        self.db_connections = collector.gauge(
            "database_connections_active",
            "Active database connections",
            unit=MetricUnit.COUNT,
            labels=["database"]
        )
