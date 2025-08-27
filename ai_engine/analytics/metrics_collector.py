"""
Metrics Collector - Comprehensive Metrics Collection and Aggregation
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive metrics collection, aggregation, and storage
capabilities for the IA Influencer Agent platform.
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import statistics
import hashlib

logger = logging.getLogger(__name__)

class MetricCategory(Enum):
    """Categories of metrics"""
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    CONTENT = "content"
    USER = "user"
    SYSTEM = "system"
    BUSINESS = "business"
    QUALITY = "quality"
    SECURITY = "security"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"  # Always increases
    GAUGE = "gauge"     # Current value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"     # Duration measurements
    RATE = "rate"      # Events per time unit
    RATIO = "ratio"    # Percentage or fraction
    SET = "set"        # Unique values
    SUMMARY = "summary"  # Statistical summary

class AggregationMethod(Enum):
    """Methods for aggregating metrics"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"
    STDDEV = "stddev"
    RATE_PER_SECOND = "rate_per_second"
    RATE_PER_MINUTE = "rate_per_minute"
    UNIQUE_COUNT = "unique_count"

@dataclass
class MetricData:
    """Individual metric data point"""
    metric_name: str
    value: Union[int, float, str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    category: MetricCategory = MetricCategory.OPERATIONAL
    metric_type: MetricType = MetricType.GAUGE
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    unit: Optional[str] = None

@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    metric_name: str
    aggregation_method: AggregationMethod
    value: Union[int, float]
    time_window: Dict[str, datetime]
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricAlert:
    """Metric alert configuration"""
    alert_name: str
    metric_name: str
    condition: str  # e.g., "> 100", "< 0.5", "== 0"
    threshold_value: float
    time_window_minutes: int = 5
    severity: str = "warning"  # info, warning, critical
    callback: Optional[Callable] = None
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

class MetricBuffer:
    """Thread-safe buffer for storing metrics"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.total_added = 0
        self.total_dropped = 0
    
    def add(self, metric: MetricData) -> bool:
        """Add metric to buffer"""
        with self.lock:
            try:
                if len(self.buffer) >= self.max_size:
                    self.total_dropped += 1
                    self.buffer.popleft()  # Remove oldest if full
                
                self.buffer.append(metric)
                self.total_added += 1
                return True
            except Exception as e:
                logger.error(f"Failed to add metric to buffer: {e}")
                return False
    
    def get_all(self, clear: bool = True) -> List[MetricData]:
        """Get all metrics from buffer"""
        with self.lock:
            metrics = list(self.buffer)
            if clear:
                self.buffer.clear()
            return metrics
    
    def get_recent(self, seconds: int = 60) -> List[MetricData]:
        """Get metrics from last N seconds"""
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        with self.lock:
            return [m for m in self.buffer if m.timestamp >= cutoff]
    
    def size(self) -> int:
        """Get current buffer size"""
        with self.lock:
            return len(self.buffer)

class MetricsCollector:
    """Main metrics collection and aggregation engine"""
    
    def __init__(self, buffer_size: int = 50000, auto_flush_seconds: int = 60):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.buffer = MetricBuffer(buffer_size)
        self.auto_flush_seconds = auto_flush_seconds
        
        # Aggregated metrics storage
        self.aggregated_metrics = {}
        self.metric_history = defaultdict(list)
        
        # Alert system
        self.alerts = {}
        self.alert_callbacks = {}
        
        # Auto-flush thread
        self.running = True
        self.flush_thread = None
        if auto_flush_seconds > 0:
            self._start_auto_flush()
        
        # Metric definitions
        self.metric_definitions = {}
        self._initialize_standard_metrics()
        
        self.logger.info("MetricsCollector initialized successfully")
    
    def _initialize_standard_metrics(self):
        """Initialize standard metric definitions"""
        self.metric_definitions = {
            # Performance metrics
            "response_time": {
                "category": MetricCategory.PERFORMANCE,
                "type": MetricType.TIMER,
                "unit": "milliseconds",
                "description": "Response time for requests"
            },
            "cpu_usage": {
                "category": MetricCategory.SYSTEM,
                "type": MetricType.GAUGE,
                "unit": "percent",
                "description": "CPU usage percentage"
            },
            "memory_usage": {
                "category": MetricCategory.SYSTEM,
                "type": MetricType.GAUGE,
                "unit": "bytes",
                "description": "Memory usage in bytes"
            },
            
            # Engagement metrics
            "content_views": {
                "category": MetricCategory.ENGAGEMENT,
                "type": MetricType.COUNTER,
                "unit": "count",
                "description": "Number of content views"
            },
            "engagement_rate": {
                "category": MetricCategory.ENGAGEMENT,
                "type": MetricType.RATIO,
                "unit": "percent",
                "description": "Engagement rate percentage"
            },
            "user_interactions": {
                "category": MetricCategory.USER,
                "type": MetricType.COUNTER,
                "unit": "count",
                "description": "Number of user interactions"
            },
            
            # Business metrics
            "revenue": {
                "category": MetricCategory.BUSINESS,
                "type": MetricType.GAUGE,
                "unit": "currency",
                "description": "Revenue amount"
            },
            "conversion_rate": {
                "category": MetricCategory.BUSINESS,
                "type": MetricType.RATIO,
                "unit": "percent",
                "description": "Conversion rate percentage"
            },
            
            # Quality metrics
            "content_quality_score": {
                "category": MetricCategory.QUALITY,
                "type": MetricType.GAUGE,
                "unit": "score",
                "description": "Content quality score"
            },
            "error_rate": {
                "category": MetricCategory.QUALITY,
                "type": MetricType.RATIO,
                "unit": "percent",
                "description": "Error rate percentage"
            }
        }
    
    def _start_auto_flush(self):
        """Start auto-flush thread"""
        def auto_flush():
            while self.running:
                try:
                    time.sleep(self.auto_flush_seconds)
                    if self.running:
                        self.flush_metrics()
                except Exception as e:
                    self.logger.error(f"Auto-flush error: {e}")
        
        self.flush_thread = threading.Thread(target=auto_flush, daemon=True)
        self.flush_thread.start()
        self.logger.debug("Auto-flush thread started")
    
    def record_metric(self, metric_name: str, value: Union[int, float, str], 
                     tags: Optional[Dict[str, str]] = None,
                     category: Optional[MetricCategory] = None,
                     metric_type: Optional[MetricType] = None,
                     source: Optional[str] = None,
                     unit: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record a new metric"""
        try:
            # Get metric definition if exists
            definition = self.metric_definitions.get(metric_name, {})
            
            # Use provided values or defaults from definition
            final_category = category or definition.get('category', MetricCategory.OPERATIONAL)
            final_type = metric_type or definition.get('type', MetricType.GAUGE)
            final_unit = unit or definition.get('unit')
            
            metric = MetricData(
                metric_name=metric_name,
                value=value,
                tags=tags or {},
                category=final_category,
                metric_type=final_type,
                metadata=metadata or {},
                source=source,
                unit=final_unit
            )
            
            # Add to buffer
            success = self.buffer.add(metric)
            
            # Check alerts
            if success:
                self._check_alerts(metric)
            
            self.logger.debug(f"Recorded metric: {metric_name}={value}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}: {e}")
            return False
    
    def record_counter(self, name: str, increment: int = 1, 
                      tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a counter metric"""
        return self.record_metric(
            name, increment, tags, 
            MetricCategory.OPERATIONAL, MetricType.COUNTER
        )
    
    def record_gauge(self, name: str, value: Union[int, float], 
                    tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a gauge metric"""
        return self.record_metric(
            name, value, tags, 
            MetricCategory.OPERATIONAL, MetricType.GAUGE
        )
    
    def record_timer(self, name: str, duration_ms: float, 
                    tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a timer metric"""
        return self.record_metric(
            name, duration_ms, tags, 
            MetricCategory.PERFORMANCE, MetricType.TIMER, unit="milliseconds"
        )
    
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> 'TimerContext':
        """Start a timer context manager"""
        return TimerContext(self, name, tags)
    
    def _check_alerts(self, metric: MetricData):
        """Check if metric triggers any alerts"""
        try:
            for alert_name, alert in self.alerts.items():
                if not alert.enabled or alert.metric_name != metric.metric_name:
                    continue
                
                # Check if we should evaluate (avoid spam)
                now = datetime.utcnow()
                if (alert.last_triggered and 
                    (now - alert.last_triggered).total_seconds() < alert.time_window_minutes * 60):
                    continue
                
                # Evaluate condition
                try:
                    metric_value = float(metric.value)
                    condition_met = self._evaluate_condition(
                        metric_value, alert.condition, alert.threshold_value
                    )
                    
                    if condition_met:
                        alert.last_triggered = now
                        alert.trigger_count += 1
                        self._trigger_alert(alert, metric)
                        
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Could not evaluate alert {alert_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Alert checking failed: {e}")
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        try:
            if condition.startswith('>'):
                return value > threshold
            elif condition.startswith('<'):
                return value < threshold
            elif condition.startswith('=='):
                return abs(value - threshold) < 0.001  # Float equality
            elif condition.startswith('!='):
                return abs(value - threshold) > 0.001
            elif condition.startswith('>='):
                return value >= threshold
            elif condition.startswith('<='):
                return value <= threshold
            else:
                self.logger.warning(f"Unknown condition operator: {condition}")
                return False
        except Exception:
            return False
    
    def _trigger_alert(self, alert: MetricAlert, metric: MetricData):
        """Trigger an alert"""
        try:
            self.logger.warning(
                f"ALERT: {alert.alert_name} - {metric.metric_name}={metric.value} "
                f"({alert.condition} {alert.threshold_value})"
            )
            
            # Call callback if provided
            if alert.callback:
                try:
                    alert.callback(alert, metric)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to trigger alert: {e}")
    
    def add_alert(self, alert: MetricAlert) -> bool:
        """Add a new alert"""
        try:
            self.alerts[alert.alert_name] = alert
            self.logger.info(f"Added alert: {alert.alert_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add alert: {e}")
            return False
    
    def remove_alert(self, alert_name: str) -> bool:
        """Remove an alert"""
        try:
            if alert_name in self.alerts:
                del self.alerts[alert_name]
                self.logger.info(f"Removed alert: {alert_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove alert: {e}")
            return False
    
    def flush_metrics(self) -> int:
        """Flush buffered metrics and perform aggregation"""
        try:
            metrics = self.buffer.get_all(clear=True)
            if not metrics:
                return 0
            
            # Store in history
            for metric in metrics:
                self.metric_history[metric.metric_name].append(metric)
                
                # Keep only recent history (last 24 hours)
                cutoff = datetime.utcnow() - timedelta(hours=24)
                self.metric_history[metric.metric_name] = [
                    m for m in self.metric_history[metric.metric_name] 
                    if m.timestamp >= cutoff
                ]
            
            # Perform aggregations
            self._perform_aggregations(metrics)
            
            self.logger.debug(f"Flushed {len(metrics)} metrics")
            return len(metrics)
            
        except Exception as e:
            self.logger.error(f"Failed to flush metrics: {e}")
            return 0
    
    def _perform_aggregations(self, metrics: List[MetricData]):
        """Perform metric aggregations"""
        try:
            # Group metrics by name and time window
            now = datetime.utcnow()
            time_windows = [
                (timedelta(minutes=1), "1m"),
                (timedelta(minutes=5), "5m"),
                (timedelta(minutes=15), "15m"),
                (timedelta(hours=1), "1h"),
                (timedelta(hours=6), "6h"),
                (timedelta(days=1), "24h")
            ]
            
            for window_delta, window_name in time_windows:
                window_start = now - window_delta
                
                # Group metrics by name within this time window
                windowed_metrics = defaultdict(list)
                for metric in metrics:
                    if metric.timestamp >= window_start:
                        windowed_metrics[metric.metric_name].append(metric)
                
                # Calculate aggregations
                for metric_name, metric_list in windowed_metrics.items():
                    if not metric_list:
                        continue
                    
                    self._calculate_aggregations(
                        metric_name, metric_list, window_start, now, window_name
                    )
                    
        except Exception as e:
            self.logger.error(f"Aggregation failed: {e}")
    
    def _calculate_aggregations(self, metric_name: str, metrics: List[MetricData],
                              window_start: datetime, window_end: datetime,
                              window_name: str):
        """Calculate aggregations for a metric within a time window"""
        try:
            if not metrics:
                return
            
            # Extract numeric values
            numeric_values = []
            for metric in metrics:
                try:
                    numeric_values.append(float(metric.value))
                except (ValueError, TypeError):
                    continue
            
            if not numeric_values:
                return
            
            # Calculate various aggregations
            aggregations = {
                AggregationMethod.SUM: sum(numeric_values),
                AggregationMethod.AVERAGE: statistics.mean(numeric_values),
                AggregationMethod.MIN: min(numeric_values),
                AggregationMethod.MAX: max(numeric_values),
                AggregationMethod.COUNT: len(numeric_values),
            }
            
            # Additional aggregations if we have enough data
            if len(numeric_values) > 1:
                try:
                    aggregations[AggregationMethod.MEDIAN] = statistics.median(numeric_values)
                    aggregations[AggregationMethod.STDDEV] = statistics.stdev(numeric_values)
                except statistics.StatisticsError:
                    pass
            
            # Percentiles if we have enough data
            if len(numeric_values) >= 20:  # Minimum for meaningful percentiles
                sorted_values = sorted(numeric_values)
                try:
                    p95_idx = int(len(sorted_values) * 0.95)
                    p99_idx = int(len(sorted_values) * 0.99)
                    aggregations[AggregationMethod.PERCENTILE_95] = sorted_values[p95_idx]
                    aggregations[AggregationMethod.PERCENTILE_99] = sorted_values[p99_idx]
                except IndexError:
                    pass
            
            # Rate calculations
            window_seconds = (window_end - window_start).total_seconds()
            if window_seconds > 0:
                aggregations[AggregationMethod.RATE_PER_SECOND] = len(numeric_values) / window_seconds
                aggregations[AggregationMethod.RATE_PER_MINUTE] = (len(numeric_values) / window_seconds) * 60
            
            # Store aggregated metrics
            for method, value in aggregations.items():
                agg_key = f"{metric_name}_{window_name}_{method.value}"
                
                aggregated = AggregatedMetric(
                    metric_name=metric_name,
                    aggregation_method=method,
                    value=value,
                    time_window={
                        'start': window_start,
                        'end': window_end,
                        'window': window_name
                    },
                    sample_count=len(numeric_values),
                    confidence=min(1.0, len(numeric_values) / 100.0)  # Confidence based on sample size
                )
                
                self.aggregated_metrics[agg_key] = aggregated
            
        except Exception as e:
            self.logger.error(f"Failed to calculate aggregations for {metric_name}: {e}")
    
    def get_metric_value(self, metric_name: str, 
                        aggregation: AggregationMethod = AggregationMethod.AVERAGE,
                        window: str = "1h") -> Optional[float]:
        """Get aggregated metric value"""
        try:
            key = f"{metric_name}_{window}_{aggregation.value}"
            agg_metric = self.aggregated_metrics.get(key)
            return agg_metric.value if agg_metric else None
        except Exception as e:
            self.logger.error(f"Failed to get metric value: {e}")
            return None
    
    def get_metric_history(self, metric_name: str, 
                          hours_back: int = 24) -> List[MetricData]:
        """Get metric history"""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours_back)
            history = self.metric_history.get(metric_name, [])
            return [m for m in history if m.timestamp >= cutoff]
        except Exception as e:
            self.logger.error(f"Failed to get metric history: {e}")
            return []
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        try:
            buffer_stats = {
                "current_buffer_size": self.buffer.size(),
                "total_metrics_added": self.buffer.total_added,
                "total_metrics_dropped": self.buffer.total_dropped
            }
            
            aggregation_stats = {
                "total_aggregated_metrics": len(self.aggregated_metrics),
                "unique_metric_names": len(self.metric_history),
                "total_historical_points": sum(len(history) for history in self.metric_history.values())
            }
            
            alert_stats = {
                "total_alerts": len(self.alerts),
                "active_alerts": len([a for a in self.alerts.values() if a.enabled]),
                "total_alert_triggers": sum(a.trigger_count for a in self.alerts.values())
            }
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "buffer_stats": buffer_stats,
                "aggregation_stats": aggregation_stats,
                "alert_stats": alert_stats,
                "metric_definitions": len(self.metric_definitions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    def export_metrics(self, format_type: str = "json", 
                      include_raw: bool = False) -> Union[str, Dict[str, Any]]:
        """Export metrics data"""
        try:
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "summary": self.get_metrics_summary(),
                "aggregated_metrics": {}
            }
            
            # Export aggregated metrics
            for key, agg_metric in self.aggregated_metrics.items():
                export_data["aggregated_metrics"][key] = {
                    "metric_name": agg_metric.metric_name,
                    "aggregation_method": agg_metric.aggregation_method.value,
                    "value": agg_metric.value,
                    "sample_count": agg_metric.sample_count,
                    "confidence": agg_metric.confidence,
                    "time_window": {
                        "start": agg_metric.time_window['start'].isoformat(),
                        "end": agg_metric.time_window['end'].isoformat(),
                        "window": agg_metric.time_window['window']
                    }
                }
            
            # Include raw data if requested
            if include_raw:
                export_data["raw_metrics"] = {}
                for metric_name, history in self.metric_history.items():
                    export_data["raw_metrics"][metric_name] = [
                        {
                            "value": m.value,
                            "timestamp": m.timestamp.isoformat(),
                            "tags": m.tags,
                            "source": m.source
                        }
                        for m in history[-100:]  # Last 100 points only
                    ]
            
            if format_type.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                return export_data
                
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown the metrics collector"""
        try:
            self.logger.info("Shutting down MetricsCollector")
            self.running = False
            
            # Final flush
            self.flush_metrics()
            
            # Wait for flush thread
            if self.flush_thread and self.flush_thread.is_alive():
                self.flush_thread.join(timeout=5)
            
            self.logger.info("MetricsCollector shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

class TimerContext:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, name: str, 
                 tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_timer(self.name, duration_ms, self.tags)

# Export main classes
__all__ = [
    'MetricsCollector',
    'MetricData',
    'AggregatedMetric',
    'MetricAlert',
    'TimerContext',
    'MetricCategory',
    'MetricType',
    'AggregationMethod'
]

logger.info("Metrics collector module loaded successfully")
