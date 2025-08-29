"""
Quality Metrics Collector - Enterprise Monitoring System

Advanced metrics collection and analysis system for comprehensive quality
monitoring across all content types and platform operations.

Business Logic:
Quality metrics collection → Real-time analysis → Performance tracking →
Quality insights → Automated reporting → Continuous improvement

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import csv
import io
import logging
import time
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of quality metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class MetricCategory(Enum):
    """Categories of quality metrics"""
    CONTENT_QUALITY = "content_quality"
    PERFORMANCE = "performance"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_HEALTH = "system_health"
    BUSINESS = "business"
    SECURITY = "security"
    COMPLIANCE = "compliance"


@dataclass
class MetricValue:
    """Individual metric value with metadata"""
    value: Union[float, int]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Definition of a quality metric"""
    name: str
    metric_type: MetricType
    category: MetricCategory
    description: str
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'category': self.category.value,
            'description': self.description,
            'unit': self.unit,
            'tags': self.tags,
            'thresholds': self.thresholds
        }


@dataclass
class MetricSummary:
    """Statistical summary of metric values"""
    count: int
    min_value: float
    max_value: float
    mean: float
    median: float
    std_dev: float
    percentile_95: float
    percentile_99: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'count': self.count,
            'min': self.min_value,
            'max': self.max_value,
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev,
            'p95': self.percentile_95,
            'p99': self.percentile_99
        }


class MetricStorage:
    """Thread-safe metric storage with retention policies"""
    
    def __init__(self, max_size: int = 10000, retention_hours: int = 24):
        self.max_size = max_size
        self.retention_hours = retention_hours
        self.data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_size))
        self.lock = threading.RLock()
        
    def store_metric(self, metric_name: str, value: MetricValue):
        """Store a metric value with automatic cleanup"""
        with self.lock:
            # Add new value
            self.data[metric_name].append(value)
            
            # Clean old data
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
            while (self.data[metric_name] and 
                   self.data[metric_name][0].timestamp < cutoff_time):
                self.data[metric_name].popleft()
    
    def get_metrics(self, metric_name: str, 
                   since: Optional[datetime] = None) -> List[MetricValue]:
        """Retrieve metric values with optional time filtering"""
        with self.lock:
            values = list(self.data[metric_name])
            
            if since:
                values = [v for v in values if v.timestamp >= since]
            
            return values
    
    def get_all_metric_names(self) -> List[str]:
        """Get all stored metric names"""
        with self.lock:
            return list(self.data.keys())
    
    def clear_metric(self, metric_name: str):
        """Clear all data for a specific metric"""
        with self.lock:
            if metric_name in self.data:
                self.data[metric_name].clear()
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self.lock:
            stats = {
                'total_metrics': len(self.data),
                'total_values': sum(len(values) for values in self.data.values()),
                'memory_usage_mb': self._estimate_memory_usage(),
                'oldest_timestamp': None,
                'newest_timestamp': None
            }
            
            # Find oldest and newest timestamps
            all_timestamps = []
            for values in self.data.values():
                if values:
                    all_timestamps.extend([v.timestamp for v in values])
            
            if all_timestamps:
                stats['oldest_timestamp'] = min(all_timestamps)
                stats['newest_timestamp'] = max(all_timestamps)
            
            return stats
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        # Rough estimation based on average object size
        total_objects = sum(len(values) for values in self.data.values())
        avg_object_size = 200  # bytes per MetricValue (estimated)
        return (total_objects * avg_object_size) / (1024 * 1024)


class QualityMetricsCollector:
    """Enterprise quality metrics collection and analysis system"""
    
    def __init__(self, storage_config: Optional[Dict[str, Any]] = None):
        self.storage = MetricStorage(
            max_size=storage_config.get('max_size', 10000) if storage_config else 10000,
            retention_hours=storage_config.get('retention_hours', 24) if storage_config else 24
        )
        self.definitions: Dict[str, MetricDefinition] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
    
    def _initialize_standard_metrics(self):
        """Initialize standard quality metrics"""
        standard_metrics = [
            # Content Quality Metrics
            MetricDefinition(
                name="content_quality_score",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.CONTENT_QUALITY,
                description="Overall content quality score (0-100)",
                unit="score",
                thresholds={"warning": 70.0, "critical": 50.0}
            ),
            MetricDefinition(
                name="content_validation_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.PERFORMANCE,
                description="Time taken for content validation",
                unit="milliseconds",
                thresholds={"warning": 5000.0, "critical": 10000.0}
            ),
            MetricDefinition(
                name="content_issues_count",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.CONTENT_QUALITY,
                description="Number of content quality issues found",
                unit="count"
            ),
            
            # Performance Metrics
            MetricDefinition(
                name="api_response_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.PERFORMANCE,
                description="API endpoint response time",
                unit="milliseconds",
                thresholds={"warning": 1000.0, "critical": 3000.0}
            ),
            MetricDefinition(
                name="throughput_requests_per_second",
                metric_type=MetricType.RATE,
                category=MetricCategory.PERFORMANCE,
                description="Request processing throughput",
                unit="requests/second"
            ),
            
            # System Health Metrics
            MetricDefinition(
                name="memory_usage_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM_HEALTH,
                description="System memory usage percentage",
                unit="percent",
                thresholds={"warning": 80.0, "critical": 95.0}
            ),
            MetricDefinition(
                name="cpu_usage_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM_HEALTH,
                description="System CPU usage percentage",
                unit="percent",
                thresholds={"warning": 80.0, "critical": 95.0}
            ),
            
            # Business Metrics
            MetricDefinition(
                name="monetization_readiness_score",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.BUSINESS,
                description="Content monetization readiness score",
                unit="score",
                thresholds={"warning": 60.0, "critical": 40.0}
            ),
            MetricDefinition(
                name="seo_optimization_score",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.BUSINESS,
                description="SEO optimization score for content",
                unit="score",
                thresholds={"warning": 70.0, "critical": 50.0}
            ),
            
            # Security Metrics
            MetricDefinition(
                name="security_scan_score",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SECURITY,
                description="Content security assessment score",
                unit="score",
                thresholds={"warning": 80.0, "critical": 60.0}
            ),
            MetricDefinition(
                name="compliance_violations",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.COMPLIANCE,
                description="Number of compliance violations detected",
                unit="count"
            )
        ]
        
        for metric_def in standard_metrics:
            self.register_metric(metric_def)
    
    def register_metric(self, definition: MetricDefinition):
        """Register a new metric definition"""
        self.definitions[definition.name] = definition
        logger.info(f"Registered metric: {definition.name}")
    
    def collect_metric(self, metric_name: str, value: Union[float, int],
                      tags: Optional[Dict[str, str]] = None,
                      metadata: Optional[Dict[str, Any]] = None):
        """Collect a metric value"""
        if metric_name not in self.definitions:
            logger.warning(f"Unknown metric: {metric_name}")
            return
        
        metric_value = MetricValue(
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.storage.store_metric(metric_name, metric_value)
        
        # Check thresholds
        self._check_thresholds(metric_name, value)
    
    def _check_thresholds(self, metric_name: str, value: Union[float, int]):
        """Check if metric value exceeds defined thresholds"""
        definition = self.definitions[metric_name]
        
        if 'critical' in definition.thresholds:
            threshold = definition.thresholds['critical']
            if (definition.metric_type in [MetricType.GAUGE, MetricType.TIMER] and 
                value >= threshold):
                logger.critical(f"CRITICAL threshold exceeded for {metric_name}: {value} >= {threshold}")
        
        if 'warning' in definition.thresholds:
            threshold = definition.thresholds['warning']
            if (definition.metric_type in [MetricType.GAUGE, MetricType.TIMER] and 
                value >= threshold):
                logger.warning(f"WARNING threshold exceeded for {metric_name}: {value} >= {threshold}")
    
    def get_metric_summary(self, metric_name: str,
                          since: Optional[datetime] = None) -> Optional[MetricSummary]:
        """Get statistical summary of a metric"""
        values = self.storage.get_metrics(metric_name, since)
        
        if not values:
            return None
        
        numeric_values = [v.value for v in values]
        
        try:
            return MetricSummary(
                count=len(numeric_values),
                min_value=min(numeric_values),
                max_value=max(numeric_values),
                mean=statistics.mean(numeric_values),
                median=statistics.median(numeric_values),
                std_dev=statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0,
                percentile_95=self._percentile(numeric_values, 95),
                percentile_99=self._percentile(numeric_values, 99)
            )
        except Exception as e:
            logger.error(f"Error calculating metric summary for {metric_name}: {e}")
            return None
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            if upper_index >= len(sorted_values):
                return sorted_values[lower_index]
            
            lower_value = sorted_values[lower_index]
            upper_value = sorted_values[upper_index]
            fraction = index - lower_index
            
            return lower_value + fraction * (upper_value - lower_value)
    
    def get_metrics_by_category(self, category: MetricCategory,
                               since: Optional[datetime] = None) -> Dict[str, MetricSummary]:
        """Get all metrics summaries for a specific category"""
        category_metrics = {
            name: definition for name, definition in self.definitions.items()
            if definition.category == category
        }
        
        summaries = {}
        for metric_name in category_metrics:
            summary = self.get_metric_summary(metric_name, since)
            if summary:
                summaries[metric_name] = summary
        
        return summaries
    
    def get_dashboard_data(self, time_range_hours: int = 1) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        since = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
        
        dashboard_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'time_range_hours': time_range_hours,
            'categories': {}
        }
        
        for category in MetricCategory:
            category_data = self.get_metrics_by_category(category, since)
            if category_data:
                dashboard_data['categories'][category.value] = {
                    metric_name: summary.to_dict()
                    for metric_name, summary in category_data.items()
                }
        
        # Add storage statistics
        dashboard_data['storage_stats'] = self.storage.get_storage_stats()
        
        return dashboard_data
    
    def export_metrics(self, format_type: str = "json",
                      since: Optional[datetime] = None) -> str:
        """Export metrics in specified format"""
        if format_type.lower() not in ['json', 'csv']:
            raise ValueError("Supported formats: json, csv")
        
        export_data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {}
        }
        
        for metric_name in self.definitions:
            values = self.storage.get_metrics(metric_name, since)
            export_data['metrics'][metric_name] = {
                'definition': self.definitions[metric_name].to_dict(),
                'values': [
                    {
                        'value': v.value,
                        'timestamp': v.timestamp.isoformat(),
                        'tags': v.tags,
                        'metadata': v.metadata
                    }
                    for v in values
                ]
            }
        
        if format_type.lower() == 'json':
            return json.dumps(export_data, indent=2)
        elif format_type.lower() == 'csv':
            return self._export_to_csv(export_data)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_to_csv(self, export_data: Dict[str, Any]) -> str:
        """Export metrics data to CSV format"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'timestamp', 'metric_name', 'metric_type', 'value', 
                'tags', 'dimensions', 'metadata'
            ])
            
            # Export summary metrics
            for metric_name, metric_data in export_data.get('summary', {}).items():
                if isinstance(metric_data, dict):
                    for sub_metric, value in metric_data.items():
                        writer.writerow([
                            export_data.get('timestamp', ''),
                            f"{metric_name}_{sub_metric}",
                            'summary',
                            value,
                            '',  # tags
                            '',  # dimensions
                            ''   # metadata
                        ])
                else:
                    writer.writerow([
                        export_data.get('timestamp', ''),
                        metric_name,
                        'summary',
                        metric_data,
                        '',  # tags
                        '',  # dimensions
                        ''   # metadata
                    ])
            
            # Export detailed metrics
            for metric_name, metric_info in export_data.get('metrics', {}).items():
                if isinstance(metric_info, dict):
                    metric_type = metric_info.get('type', 'unknown')
                    
                    # Export values based on metric type
                    if metric_type == 'counter':
                        writer.writerow([
                            export_data.get('timestamp', ''),
                            metric_name,
                            metric_type,
                            metric_info.get('value', 0),
                            json.dumps(metric_info.get('tags', {})),
                            '',
                            json.dumps(metric_info.get('metadata', {}))
                        ])
                    
                    elif metric_type == 'gauge':
                        current_value = metric_info.get('current_value', 0)
                        writer.writerow([
                            export_data.get('timestamp', ''),
                            metric_name,
                            metric_type,
                            current_value,
                            json.dumps(metric_info.get('tags', {})),
                            '',
                            json.dumps(metric_info.get('metadata', {}))
                        ])
                    
                    elif metric_type == 'histogram':
                        # Export histogram statistics
                        stats = metric_info.get('statistics', {})
                        for stat_name, stat_value in stats.items():
                            writer.writerow([
                                export_data.get('timestamp', ''),
                                f"{metric_name}_{stat_name}",
                                f"{metric_type}_stat",
                                stat_value,
                                json.dumps(metric_info.get('tags', {})),
                                '',
                                json.dumps(metric_info.get('metadata', {}))
                            ])
                        
                        # Export bucket data if available
                        buckets = metric_info.get('buckets', {})
                        for bucket_range, count in buckets.items():
                            writer.writerow([
                                export_data.get('timestamp', ''),
                                f"{metric_name}_bucket_{bucket_range}",
                                f"{metric_type}_bucket",
                                count,
                                json.dumps(metric_info.get('tags', {})),
                                bucket_range,
                                json.dumps(metric_info.get('metadata', {}))
                            ])
            
            # Export time series data if available
            for metric_name, time_series in export_data.get('time_series', {}).items():
                if isinstance(time_series, list):
                    for data_point in time_series:
                        if isinstance(data_point, dict):
                            writer.writerow([
                                data_point.get('timestamp', ''),
                                metric_name,
                                'time_series',
                                data_point.get('value', 0),
                                json.dumps(data_point.get('tags', {})),
                                '',
                                json.dumps(data_point.get('metadata', {}))
                            ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise ValueError(f"CSV export failed: {e}")
        finally:
            output.close()
    
    async def collect_metric_async(self, metric_name: str, value: Union[float, int],
                                  tags: Optional[Dict[str, str]] = None,
                                  metadata: Optional[Dict[str, Any]] = None):
        """Asynchronously collect a metric value"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor, self.collect_metric, metric_name, value, tags, metadata
        )
    
    def batch_collect_metrics(self, metrics: List[Dict[str, Any]]):
        """Collect multiple metrics in batch"""
        for metric_data in metrics:
            self.collect_metric(
                metric_data['name'],
                metric_data['value'],
                metric_data.get('tags'),
                metric_data.get('metadata')
            )
    
    def clear_all_metrics(self):
        """Clear all stored metric data"""
        for metric_name in self.definitions:
            self.storage.clear_metric(metric_name)
        logger.info("All metric data cleared")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status based on metrics"""
        health_status = {
            'overall_status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'categories': {},
            'alerts': []
        }
        
        # Check each category for health issues
        for category in MetricCategory:
            category_metrics = self.get_metrics_by_category(category)
            category_status = 'healthy'
            
            for metric_name, summary in category_metrics.items():
                definition = self.definitions[metric_name]
                
                # Check critical thresholds
                if 'critical' in definition.thresholds:
                    threshold = definition.thresholds['critical']
                    if summary.mean >= threshold:
                        category_status = 'critical'
                        health_status['alerts'].append({
                            'level': 'critical',
                            'metric': metric_name,
                            'value': summary.mean,
                            'threshold': threshold
                        })
                
                # Check warning thresholds
                elif 'warning' in definition.thresholds:
                    threshold = definition.thresholds['warning']
                    if summary.mean >= threshold:
                        if category_status == 'healthy':
                            category_status = 'warning'
                        health_status['alerts'].append({
                            'level': 'warning',
                            'metric': metric_name,
                            'value': summary.mean,
                            'threshold': threshold
                        })
            
            health_status['categories'][category.value] = category_status
            
            # Update overall status
            if category_status == 'critical':
                health_status['overall_status'] = 'critical'
            elif category_status == 'warning' and health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
        
        return health_status
    
    def shutdown(self):
        """Gracefully shutdown the metrics collector"""
        self.executor.shutdown(wait=True)
        logger.info("Quality metrics collector shutdown complete")
