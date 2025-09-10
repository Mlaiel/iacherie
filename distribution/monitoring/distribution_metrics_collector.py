"""
Distribution Metrics Collector for Ainflue Platform

This module provides comprehensive metrics collection for all distribution
activities with real-time aggregation and time-series storage.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"


class AggregationType(Enum):
    """Metric aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    RATE_PER_SECOND = "rate_per_second"


@dataclass
class MetricData:
    """Individual metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Aggregated metric data"""
    name: str
    aggregation_type: AggregationType
    value: Union[int, float]
    start_time: datetime
    end_time: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricThreshold:
    """Metric threshold for alerting"""
    metric_name: str
    threshold_value: float
    comparison: str  # gt, lt, eq, gte, lte
    duration_seconds: int
    alert_level: str
    enabled: bool = True


class DistributionMetricsCollector:
    """
    Comprehensive metrics collector for distribution platform
    
    Features:
    - Real-time metric collection and aggregation
    - Time-series data storage with configurable retention
    - Multi-dimensional tagging and metadata
    - Automatic threshold monitoring and alerting
    - Performance-optimized with async processing
    - Integration with Prometheus, InfluxDB, and custom backends
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_buffer = defaultdict(deque)
        self.aggregations = {}
        self.thresholds = {}
        self.collection_stats = {
            'total_metrics': 0,
            'metrics_per_second': 0,
            'last_collection_time': None,
            'buffer_size': 0
        }
        
        # Configuration
        self.buffer_size = self.config.get('buffer_size', 10000)
        self.flush_interval = self.config.get('flush_interval', 60)  # seconds
        self.retention_period = self.config.get('retention_period', 86400)  # 24 hours
        self.aggregation_intervals = self.config.get('aggregation_intervals', [60, 300, 3600])  # 1m, 5m, 1h
        
        # Storage backends
        self.storage_backends = []
        self.enable_prometheus = self.config.get('enable_prometheus', True)
        self.enable_influxdb = self.config.get('enable_influxdb', True)
        
        # Async processing
        self.collection_lock = threading.Lock()
        self.processing_enabled = True
        
        # Start background tasks
        self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background metric processing tasks"""
        
        # Start metric aggregation task
        asyncio.create_task(self._background_aggregation_task())
        
        # Start metric flushing task
        asyncio.create_task(self._background_flush_task())
        
        # Start cleanup task
        asyncio.create_task(self._background_cleanup_task())

    async def collect_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Collect a single metric data point
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            tags: Optional tags for multi-dimensional analysis
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            metric = MetricData(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.utcnow(),
                tags=tags or {},
                metadata=metadata or {}
            )
            
            # Add to buffer
            with self.collection_lock:
                self.metrics_buffer[name].append(metric)
                
                # Trim buffer if too large
                if len(self.metrics_buffer[name]) > self.buffer_size:
                    self.metrics_buffer[name].popleft()
                
                # Update collection stats
                self.collection_stats['total_metrics'] += 1
                self.collection_stats['last_collection_time'] = datetime.utcnow()
                self.collection_stats['buffer_size'] = sum(len(queue) for queue in self.metrics_buffer.values())
            
            # Check thresholds
            await self._check_thresholds(metric)
            
            return True
            
        except Exception as e:
            logger.error(f"Error collecting metric {name}: {e}")
            return False

    async def collect_distribution_metrics(self, distribution_data: Dict[str, Any]) -> bool:
        """Collect comprehensive distribution metrics from operation data"""
        
        try:
            content_id = distribution_data.get('content_id', 'unknown')
            platform = distribution_data.get('platform', 'unknown')
            user_id = distribution_data.get('user_id', 'unknown')
            
            # Common tags
            tags = {
                'content_id': content_id,
                'platform': platform,
                'user_id': user_id
            }
            
            # Distribution performance metrics
            if 'distribution_time_ms' in distribution_data:
                await self.collect_metric(
                    'distribution_time_ms',
                    distribution_data['distribution_time_ms'],
                    MetricType.TIMER,
                    tags=tags
                )
            
            # Engagement metrics
            engagement_metrics = distribution_data.get('engagement_metrics', {})
            for metric_name, value in engagement_metrics.items():
                await self.collect_metric(
                    f'engagement_{metric_name}',
                    value,
                    MetricType.GAUGE,
                    tags=tags
                )
            
            # Success/failure tracking
            if 'success' in distribution_data:
                await self.collect_metric(
                    'distribution_success',
                    1 if distribution_data['success'] else 0,
                    MetricType.COUNTER,
                    tags=tags
                )
            
            # Error tracking
            if 'error_code' in distribution_data:
                error_tags = {**tags, 'error_code': str(distribution_data['error_code'])}
                await self.collect_metric(
                    'distribution_errors',
                    1,
                    MetricType.COUNTER,
                    tags=error_tags
                )
            
            # API rate limit metrics
            if 'rate_limit_remaining' in distribution_data:
                await self.collect_metric(
                    'api_rate_limit_remaining',
                    distribution_data['rate_limit_remaining'],
                    MetricType.GAUGE,
                    tags={'platform': platform}
                )
            
            # Content quality metrics
            if 'quality_score' in distribution_data:
                await self.collect_metric(
                    'content_quality_score',
                    distribution_data['quality_score'],
                    MetricType.GAUGE,
                    tags=tags
                )
            
            # Viral potential metrics
            if 'viral_score' in distribution_data:
                await self.collect_metric(
                    'viral_potential_score',
                    distribution_data['viral_score'],
                    MetricType.GAUGE,
                    tags=tags
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error collecting distribution metrics: {e}")
            return False

    async def collect_performance_metrics(self, performance_data: Dict[str, Any]) -> bool:
        """Collect system performance metrics"""
        
        try:
            # CPU metrics
            if 'cpu_usage_percent' in performance_data:
                await self.collect_metric(
                    'system_cpu_usage_percent',
                    performance_data['cpu_usage_percent'],
                    MetricType.GAUGE
                )
            
            # Memory metrics
            if 'memory_usage_mb' in performance_data:
                await self.collect_metric(
                    'system_memory_usage_mb',
                    performance_data['memory_usage_mb'],
                    MetricType.GAUGE
                )
            
            # Database metrics
            db_metrics = performance_data.get('database_metrics', {})
            for db_name, metrics in db_metrics.items():
                tags = {'database': db_name}
                
                if 'connection_count' in metrics:
                    await self.collect_metric(
                        'db_connection_count',
                        metrics['connection_count'],
                        MetricType.GAUGE,
                        tags=tags
                    )
                
                if 'query_time_ms' in metrics:
                    await self.collect_metric(
                        'db_query_time_ms',
                        metrics['query_time_ms'],
                        MetricType.TIMER,
                        tags=tags
                    )
            
            # Cache metrics
            cache_metrics = performance_data.get('cache_metrics', {})
            for cache_name, metrics in cache_metrics.items():
                tags = {'cache': cache_name}
                
                if 'hit_rate' in metrics:
                    await self.collect_metric(
                        'cache_hit_rate',
                        metrics['hit_rate'],
                        MetricType.PERCENTAGE,
                        tags=tags
                    )
                
                if 'memory_usage_mb' in metrics:
                    await self.collect_metric(
                        'cache_memory_usage_mb',
                        metrics['memory_usage_mb'],
                        MetricType.GAUGE,
                        tags=tags
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return False

    async def get_metric_aggregation(
        self,
        metric_name: str,
        aggregation_type: AggregationType,
        start_time: datetime,
        end_time: datetime,
        tags: Dict[str, str] = None
    ) -> Optional[MetricAggregation]:
        """Get aggregated metric data for time range"""
        
        try:
            if metric_name not in self.metrics_buffer:
                return None
            
            # Filter metrics by time range and tags
            filtered_metrics = []
            for metric in self.metrics_buffer[metric_name]:
                if start_time <= metric.timestamp <= end_time:
                    if tags:
                        # Check if all required tags match
                        if all(metric.tags.get(k) == v for k, v in tags.items()):
                            filtered_metrics.append(metric)
                    else:
                        filtered_metrics.append(metric)
            
            if not filtered_metrics:
                return None
            
            # Calculate aggregation
            values = [m.value for m in filtered_metrics]
            
            if aggregation_type == AggregationType.SUM:
                result_value = sum(values)
            elif aggregation_type == AggregationType.AVERAGE:
                result_value = np.mean(values)
            elif aggregation_type == AggregationType.MIN:
                result_value = min(values)
            elif aggregation_type == AggregationType.MAX:
                result_value = max(values)
            elif aggregation_type == AggregationType.COUNT:
                result_value = len(values)
            elif aggregation_type == AggregationType.PERCENTILE:
                result_value = np.percentile(values, 95)  # Default to 95th percentile
            elif aggregation_type == AggregationType.RATE_PER_SECOND:
                duration = (end_time - start_time).total_seconds()
                result_value = len(values) / duration if duration > 0 else 0
            else:
                result_value = np.mean(values)  # Default to average
            
            return MetricAggregation(
                name=metric_name,
                aggregation_type=aggregation_type,
                value=result_value,
                start_time=start_time,
                end_time=end_time,
                sample_count=len(values),
                tags=tags or {}
            )
            
        except Exception as e:
            logger.error(f"Error getting metric aggregation: {e}")
            return None

    async def get_real_time_metrics(self, metric_names: List[str], window_minutes: int = 5) -> Dict[str, Dict[str, float]]:
        """Get real-time metrics for the last N minutes"""
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=window_minutes)
            
            result = {}
            
            for metric_name in metric_names:
                if metric_name not in self.metrics_buffer:
                    continue
                
                # Get recent metrics
                recent_metrics = [
                    m for m in self.metrics_buffer[metric_name]
                    if start_time <= m.timestamp <= end_time
                ]
                
                if not recent_metrics:
                    continue
                
                values = [m.value for m in recent_metrics]
                
                result[metric_name] = {
                    'current': values[-1] if values else 0,
                    'average': np.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values),
                    'rate_per_minute': len(values) / window_minutes
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}

    async def add_threshold(
        self,
        metric_name: str,
        threshold_value: float,
        comparison: str,
        duration_seconds: int = 60,
        alert_level: str = "warning"
    ) -> bool:
        """Add metric threshold for alerting"""
        
        try:
            threshold = MetricThreshold(
                metric_name=metric_name,
                threshold_value=threshold_value,
                comparison=comparison,
                duration_seconds=duration_seconds,
                alert_level=alert_level
            )
            
            if metric_name not in self.thresholds:
                self.thresholds[metric_name] = []
            
            self.thresholds[metric_name].append(threshold)
            
            logger.info(f"Added threshold for {metric_name}: {comparison} {threshold_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding threshold: {e}")
            return False

    async def _check_thresholds(self, metric: MetricData):
        """Check if metric value violates any thresholds"""
        
        try:
            if metric.name not in self.thresholds:
                return
            
            for threshold in self.thresholds[metric.name]:
                if not threshold.enabled:
                    continue
                
                violated = False
                
                if threshold.comparison == 'gt' and metric.value > threshold.threshold_value:
                    violated = True
                elif threshold.comparison == 'lt' and metric.value < threshold.threshold_value:
                    violated = True
                elif threshold.comparison == 'gte' and metric.value >= threshold.threshold_value:
                    violated = True
                elif threshold.comparison == 'lte' and metric.value <= threshold.threshold_value:
                    violated = True
                elif threshold.comparison == 'eq' and metric.value == threshold.threshold_value:
                    violated = True
                
                if violated:
                    # Check duration (simplified - would need more sophisticated tracking)
                    await self._trigger_threshold_alert(metric, threshold)
                    
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")

    async def _trigger_threshold_alert(self, metric: MetricData, threshold: MetricThreshold):
        """Trigger alert for threshold violation"""
        
        logger.warning(
            f"Threshold violation: {metric.name} = {metric.value} "
            f"{threshold.comparison} {threshold.threshold_value} "
            f"(alert level: {threshold.alert_level})"
        )
        
        # Here you would integrate with your alerting system
        # await self.alerting_system.send_alert(metric, threshold)

    async def _background_aggregation_task(self):
        """Background task for periodic metric aggregation"""
        
        while self.processing_enabled:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                current_time = datetime.utcnow()
                
                # Perform aggregations for each interval
                for interval_seconds in self.aggregation_intervals:
                    start_time = current_time - timedelta(seconds=interval_seconds)
                    
                    # Aggregate key metrics
                    key_metrics = [
                        'distribution_time_ms',
                        'engagement_likes',
                        'engagement_shares',
                        'distribution_success',
                        'system_cpu_usage_percent',
                        'system_memory_usage_mb'
                    ]
                    
                    for metric_name in key_metrics:
                        if metric_name in self.metrics_buffer:
                            aggregation = await self.get_metric_aggregation(
                                metric_name,
                                AggregationType.AVERAGE,
                                start_time,
                                current_time
                            )
                            
                            if aggregation:
                                # Store aggregation
                                aggregation_key = f"{metric_name}_{interval_seconds}s"
                                self.aggregations[aggregation_key] = aggregation
                
            except Exception as e:
                logger.error(f"Error in aggregation task: {e}")

    async def _background_flush_task(self):
        """Background task for flushing metrics to storage backends"""
        
        while self.processing_enabled:
            try:
                await asyncio.sleep(self.flush_interval)
                
                # Flush metrics to configured backends
                if self.enable_prometheus:
                    await self._flush_to_prometheus()
                
                if self.enable_influxdb:
                    await self._flush_to_influxdb()
                
                # Update metrics per second
                self._update_collection_rate()
                
            except Exception as e:
                logger.error(f"Error in flush task: {e}")

    async def _background_cleanup_task(self):
        """Background task for cleaning up old metrics"""
        
        while self.processing_enabled:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_time = datetime.utcnow() - timedelta(seconds=self.retention_period)
                
                with self.collection_lock:
                    for metric_name in list(self.metrics_buffer.keys()):
                        queue = self.metrics_buffer[metric_name]
                        
                        # Remove old metrics
                        while queue and queue[0].timestamp < cutoff_time:
                            queue.popleft()
                        
                        # Remove empty queues
                        if not queue:
                            del self.metrics_buffer[metric_name]
                
                logger.info("Completed metric cleanup task")
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def _flush_to_prometheus(self):
        """Flush metrics to Prometheus (placeholder)"""
        
        # This would integrate with prometheus_client library
        logger.debug("Flushing metrics to Prometheus")

    async def _flush_to_influxdb(self):
        """Flush metrics to InfluxDB (placeholder)"""
        
        # This would integrate with influxdb-client library
        logger.debug("Flushing metrics to InfluxDB")

    def _update_collection_rate(self):
        """Update metrics collection rate statistics"""
        
        current_time = time.time()
        
        if hasattr(self, '_last_rate_update'):
            time_diff = current_time - self._last_rate_update
            if time_diff > 0:
                metrics_diff = self.collection_stats['total_metrics'] - getattr(self, '_last_metric_count', 0)
                self.collection_stats['metrics_per_second'] = metrics_diff / time_diff
        
        self._last_rate_update = current_time
        self._last_metric_count = self.collection_stats['total_metrics']

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get metrics collection statistics"""
        
        with self.collection_lock:
            stats = self.collection_stats.copy()
            stats['buffer_sizes'] = {
                name: len(queue) for name, queue in self.metrics_buffer.items()
            }
            stats['unique_metrics'] = len(self.metrics_buffer)
            stats['total_buffer_size'] = sum(len(queue) for queue in self.metrics_buffer.values())
        
        return stats

    def export_metrics(self, format_type: str = 'json') -> str:
        """Export current metrics in specified format"""
        
        try:
            if format_type == 'json':
                export_data = {
                    'collection_stats': self.get_collection_stats(),
                    'recent_aggregations': {
                        k: {
                            'name': v.name,
                            'aggregation_type': v.aggregation_type.value,
                            'value': v.value,
                            'sample_count': v.sample_count,
                            'start_time': v.start_time.isoformat(),
                            'end_time': v.end_time.isoformat()
                        } for k, v in self.aggregations.items()
                    },
                    'active_thresholds': {
                        metric_name: [
                            {
                                'threshold_value': t.threshold_value,
                                'comparison': t.comparison,
                                'alert_level': t.alert_level,
                                'enabled': t.enabled
                            } for t in thresholds
                        ] for metric_name, thresholds in self.thresholds.items()
                    },
                    'exported_at': datetime.utcnow().isoformat()
                }
                
                return json.dumps(export_data, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return "{}"

    async def shutdown(self):
        """Gracefully shutdown metrics collector"""
        
        logger.info("Shutting down metrics collector...")
        
        self.processing_enabled = False
        
        # Final flush
        if self.enable_prometheus:
            await self._flush_to_prometheus()
        
        if self.enable_influxdb:
            await self._flush_to_influxdb()
        
        logger.info("Metrics collector shutdown complete")