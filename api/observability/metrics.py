"""Enterprise Metrics Collection System

Advanced metrics collection and monitoring infrastructure for comprehensive
system and business metrics tracking in the IA Influencer platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import time
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import json
import logging


class MetricType(Enum):
    """Metric type definitions."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    BUSINESS = "business"


@dataclass
class MetricPoint:
    """Individual metric data point."""    timestamp: datetime
    value: float
    labels: Dict[str, str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'labels': self.labels or {}
        }



class MetricsCollector:
    """Enhanced metrics collector with enterprise features."""    
    def __init__(self, retention_hours: int = 24, service_name: str = "ia-influencer"):
        self.retention_hours = retention_hours
        self.service_name = service_name
        self.metrics_data = defaultdict(lambda: deque(maxlen=10000))
        self.counters = defaultdict(float)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self._lock = threading.Lock()
        
        # Business metrics tracking
        self.business_metrics = defaultdict(float)
        self.content_metrics = defaultdict(int)
        self.user_metrics = defaultdict(int)
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning': 1000,  # 1s
            'response_time_critical': 5000,  # 5s
            'error_rate_warning': 0.05,     # 5%
            'error_rate_critical': 0.10     # 10%
        }

    def increment_counter(self, name: str, value: float = 1, labels: Optional[Dict] = None):
        """Increment a counter metric with labels support."""        with self._lock:
            metric_key = self._build_key(name, labels)
            self.counters[metric_key] += value
            self._record_time_series(metric_key, self.counters[metric_key], labels)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict] = None):
        """Set a gauge metric with labels support."""        with self._lock:
            metric_key = self._build_key(name, labels)
            self.gauges[metric_key] = value
            self._record_time_series(metric_key, value, labels)

    def record_histogram(self, name: str, value: float, labels: Optional[Dict] = None):
        """Record a histogram metric with labels support."""        with self._lock:
            metric_key = self._build_key(name, labels)
            self.histograms[metric_key].append(value)
            
            # Keep only recent values to prevent memory bloat
            if len(self.histograms[metric_key]) > 1000:
                self.histograms[metric_key] = self.histograms[metric_key][-1000:]
            
            self._record_time_series(metric_key, value, labels)

    def record_business_metric(self, metric_name: str, value: float, user_id: Optional[str] = None):
        """Record business-specific metrics."""        with self._lock:
            self.business_metrics[metric_name] += value
            
            # Track user-specific metrics if provided
            if user_id:
                self.user_metrics[f"{metric_name}_by_user_{user_id}"] += value
            
            self._record_time_series(f"business.{metric_name}", value, {"user_id": user_id})

    def record_content_event(self, event_type: str, content_type: str, user_id: str, metadata: Optional[Dict] = None):
        """Record content processing events."""        labels = {
            "event_type": event_type,
            "content_type": content_type,
            "user_id": user_id
        }
        if metadata:
            labels.update(metadata)
        
        with self._lock:
            self.increment_counter("content.events", 1, labels)
            self.content_metrics[f"{event_type}_{content_type}"] += 1

    def record_ai_operation(self, model_name: str, operation: str, duration_ms: float, success: bool, input_size: int = 0):
        """Record AI operation metrics."""        labels = {
            "model": model_name,
            "operation": operation,
            "success": str(success)
        }
        
        with self._lock:
            self.increment_counter("ai.operations", 1, labels)
            self.record_histogram("ai.operation_duration", duration_ms, labels)
            
            if input_size > 0:
                self.record_histogram("ai.input_size", input_size, labels)
            
            if success:
                self.increment_counter("ai.operations.success", 1, labels)
            else:
                self.increment_counter("ai.operations.error", 1, labels)

    def record_protection_scan(self, scan_type: str, duration_ms: float, items_scanned: int, violations_found: int):
        """Record content protection scan metrics."""        labels = {"scan_type": scan_type}
        
        with self._lock:
            self.increment_counter("protection.scans", 1, labels)
            self.record_histogram("protection.scan_duration", duration_ms, labels)
            self.record_histogram("protection.items_scanned", items_scanned, labels)
            self.increment_counter("protection.violations_found", violations_found, labels)

    def record_collaboration_match(self, match_type: str, duration_ms: float, matches_found: int, success: bool):
        """Record collaboration matching metrics."""        labels = {
            "match_type": match_type,
            "success": str(success)
        }
        
        with self._lock:
            self.increment_counter("collaboration.matches", 1, labels)
            self.record_histogram("collaboration.match_duration", duration_ms, labels)
            self.record_histogram("collaboration.matches_found", matches_found, labels)

    def time_operation(self, name: str, labels: Optional[Dict] = None):
        """Context manager to time operations with enhanced features."""        return TimingContext(self, name, labels)

    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary."""        with self._lock:
            current_time = datetime.utcnow()
            
            return {
                "service_name": self.service_name,
                "timestamp": current_time.isoformat(),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": self._get_histogram_statistics(),
                "business_metrics": dict(self.business_metrics),
                "content_metrics": dict(self.content_metrics),
                "user_metrics": dict(self.user_metrics),
                "retention_hours": self.retention_hours,
                "total_data_points": sum(len(series) for series in self.metrics_data.values())
            }

    def _get_histogram_statistics(self) -> Dict:
        """Calculate statistics for all histograms."""        stats = {}
        for name, values in self.histograms.items():
            if values:
                stats[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "p50": self._calculate_percentile(values, 0.50),
                    "p90": self._calculate_percentile(values, 0.90),
                    "p95": self._calculate_percentile(values, 0.95),
                    "p99": self._calculate_percentile(values, 0.99)
                }
        return stats

    def get_content_metrics(self) -> Dict:
        """Get detailed content processing metrics."""        with self._lock:
            return {
                "uploads_total": self.counters.get("content.events:event_type=upload", 0),
                "uploads_by_type": {
                    "audio": self.content_metrics.get("upload_audio", 0),
                    "video": self.content_metrics.get("upload_video", 0),
                    "image": self.content_metrics.get("upload_image", 0),
                    "text": self.content_metrics.get("upload_text", 0),
                },
                "protection_scans": self.counters.get("protection.scans", 0),
                "violations_detected": self.counters.get("protection.violations_found", 0),
                "ai_operations": self.counters.get("ai.operations", 0),
                "ai_success_rate": self._calculate_success_rate("ai.operations"),
                "collaboration_matches": self.counters.get("collaboration.matches", 0),
                "processing_times": {
                    "ai_avg_ms": self._get_histogram_avg("ai.operation_duration"),
                    "protection_avg_ms": self._get_histogram_avg("protection.scan_duration"),
                    "collaboration_avg_ms": self._get_histogram_avg("collaboration.match_duration")
                }
            }

    def get_system_metrics(self) -> Dict:
        """Get system performance metrics."""        with self._lock:
            return {
                "requests_total": self.counters.get("http.requests", 0),
                "requests_by_status": {
                    "2xx": self.counters.get("http.requests:status_code=2xx", 0),
                    "4xx": self.counters.get("http.requests:status_code=4xx", 0),
                    "5xx": self.counters.get("http.requests:status_code=5xx", 0),
                },
                "response_times": {
                    "avg_ms": self._get_histogram_avg("http.response_time"),
                    "p95_ms": self._get_histogram_percentile("http.response_time", 0.95),
                    "p99_ms": self._get_histogram_percentile("http.response_time", 0.99)
                },
                "error_rate": self._calculate_error_rate(),
                "database_metrics": {
                    "connections": self.gauges.get("db.connections", 0),
                    "query_avg_ms": self._get_histogram_avg("db.query_time"),
                    "slow_queries": self.counters.get("db.slow_queries", 0)
                },
                "cache_metrics": {
                    "hit_rate": self._calculate_cache_hit_rate(),
                    "memory_usage_mb": self.gauges.get("cache.memory_mb", 0)
                }
            }

    def get_business_metrics(self) -> Dict:
        """Get business-specific metrics."""        with self._lock:
            return {
                "revenue_generated": self.business_metrics.get("revenue", 0.0),
                "content_monetized": self.business_metrics.get("content_monetized", 0.0),
                "protection_value": self.business_metrics.get("protection_value", 0.0),
                "collaboration_revenue": self.business_metrics.get("collaboration_revenue", 0.0),
                "active_users": len([k for k in self.user_metrics.keys() if "upload_by_user" in k]),
                "top_content_types": self._get_top_content_types(),
                "performance_sla": {
                    "upload_sla_compliance": self._calculate_sla_compliance("content.upload_time", 5000),
                    "ai_processing_sla": self._calculate_sla_compliance("ai.operation_duration", 30000),
                    "protection_sla": self._calculate_sla_compliance("protection.scan_duration", 60000)
                }
            }

    def _calculate_success_rate(self, operation_name: str) -> float:
        """Calculate success rate for an operation."""        total = self.counters.get(operation_name, 0)
        success = self.counters.get(f"{operation_name}.success", 0)
        return (success / total * 100) if total > 0 else 100.0

    def _calculate_error_rate(self) -> float:
        """Calculate overall error rate."""        total_requests = self.counters.get("http.requests", 0)
        error_requests = (
            self.counters.get("http.requests:status_code=4xx", 0) +
            self.counters.get("http.requests:status_code=5xx", 0)
        )
        return (error_requests / total_requests * 100) if total_requests > 0 else 0.0

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""        hits = self.counters.get("cache.hits", 0)
        total = hits + self.counters.get("cache.misses", 0)
        return (hits / total * 100) if total > 0 else 0.0

    def _get_top_content_types(self) -> List[Dict]:
        """Get top content types by upload count."""        content_types = {}
        for key, value in self.content_metrics.items():
            if "upload_" in key:
                content_type = key.replace("upload_", "")
                content_types[content_type] = value
        
        return [
            {"type": content_type, "count": count}
            for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True)
        ]

    def _calculate_sla_compliance(self, metric_name: str, threshold_ms: float) -> float:
        """Calculate SLA compliance percentage."""        values = self.histograms.get(metric_name, [])
        if not values:
            return 100.0
        
        compliant_count = sum(1 for v in values if v <= threshold_ms)
        return (compliant_count / len(values) * 100)

    def cleanup_old_metrics(self):
        """Clean up old metric data points beyond retention period."""        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        with self._lock:
            for metric_name, time_series in self.metrics_data.items():
                while time_series and time_series[0].timestamp < cutoff_time:
                    time_series.popleft()

    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format with enhanced metadata."""        lines = []
        
        # Add service info
        lines.append(f"# HELP service_info Service information")
        lines.append(f"# TYPE service_info gauge")
        lines.append(f'service_info{{service="{self.service_name}",version="1.0"}} 1')
        lines.append("")
        
        # Counters
        for name, value in self.counters.items():
            clean_name = self._clean_metric_name(name)
            labels = self._extract_labels_from_key(name)
            label_str = self._format_prometheus_labels(labels)
            
            lines.append(f"# TYPE {clean_name} counter")
            lines.append(f"{clean_name}{label_str} {value}")
        
        # Gauges
        for name, value in self.gauges.items():
            clean_name = self._clean_metric_name(name)
            labels = self._extract_labels_from_key(name)
            label_str = self._format_prometheus_labels(labels)
            
            lines.append(f"# TYPE {clean_name} gauge")
            lines.append(f"{clean_name}{label_str} {value}")
        
        # Histograms (simplified as summaries)
        for name, values in self.histograms.items():
            if values:
                clean_name = self._clean_metric_name(name)
                labels = self._extract_labels_from_key(name)
                label_str = self._format_prometheus_labels(labels)
                
                lines.append(f"# TYPE {clean_name} summary")
                lines.append(f"{clean_name}_count{label_str} {len(values)}")
                lines.append(f"{clean_name}_sum{label_str} {sum(values)}")
                
                # Add quantiles
                sorted_values = sorted(values)
                quantiles = [0.5, 0.9, 0.95, 0.99]
                for q in quantiles:
                    q_value = self._calculate_percentile(sorted_values, q)
                    q_labels = labels.copy() if labels else {}
                    q_labels["quantile"] = str(q)
                    q_label_str = self._format_prometheus_labels(q_labels)
                    lines.append(f"{clean_name}{q_label_str} {q_value}")
        
        return "\n".join(lines)

    def _clean_metric_name(self, name: str) -> str:
        """Clean metric name for Prometheus format."""        # Remove labels from name and clean
        base_name = name.split(":")[0] if ":" in name else name
        return base_name.replace("-", "_").replace(".", "_").replace(" ", "_")

    def _extract_labels_from_key(self, key: str) -> Optional[Dict[str, str]]:
        """Extract labels from metric key."""        if ":" not in key:
            return None
        
        labels = {}
        parts = key.split(":", 1)[1].split(":")
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                labels[k] = v
        
        return labels if labels else None

    def _format_prometheus_labels(self, labels: Optional[Dict[str, str]]) -> str:
        """Format labels for Prometheus."""        if not labels:
            return ""
        
        label_pairs = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(label_pairs) + "}"

    def _build_key(self, name: str, labels: Optional[Dict] = None) -> str:
        """Build metric key with labels."""        if not labels:
            return name
        
        label_str = ":".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}"

    def _record_time_series(self, metric_key: str, value: float, labels: Optional[Dict] = None):
        """Record time series data point with enhanced metadata."""        data_point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels
        )
        self.metrics_data[metric_key].append(data_point)

    def _get_histogram_avg(self, name: str) -> float:
        """Get average value from histogram."""        values = self.histograms.get(name, [])
        return sum(values) / len(values) if values else 0.0

    def _get_histogram_percentile(self, name: str, percentile: float) -> float:
        """Get percentile value from histogram."""        values = sorted(self.histograms.get(name, []))
        return self._calculate_percentile(values, percentile)

    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""        if not values:
            return 0.0
        
        index = int(len(values) * percentile)
        return values[min(index, len(values) - 1)]


class ContentMetricsCollector:
    """Specialized metrics collector for content processing operations."""    
    def __init__(self, base_collector: MetricsCollector):
        self.base_collector = base_collector
        
        # Content-specific tracking
        self.upload_sizes = deque(maxlen=1000)
        self.processing_durations = defaultdict(lambda: deque(maxlen=1000))
        self.content_by_user = defaultdict(int)
        
    def record_upload(self, user_id: str, content_type: str, file_size: int, success: bool, duration_ms: float):
        """Record content upload event."""        labels = {
            "content_type": content_type,
            "success": str(success),
            "user_id": user_id
        }
        
        self.base_collector.record_content_event("upload", content_type, user_id, {"file_size": file_size})
        self.base_collector.record_histogram("content.upload_duration", duration_ms, labels)
        self.base_collector.record_histogram("content.file_size", file_size, labels)
        
        # Track upload sizes and user activity
        self.upload_sizes.append(file_size)
        self.content_by_user[user_id] += 1
        
        if success:
            self.base_collector.increment_counter("content.uploads.success", 1, labels)
            self.base_collector.record_business_metric("successful_uploads", 1, user_id)
        else:
            self.base_collector.increment_counter("content.uploads.failed", 1, labels)

    def record_processing(self, content_id: str, processing_type: str, duration_ms: float, success: bool, metadata: Optional[Dict] = None):
        """Record content processing event."""        labels = {
            "processing_type": processing_type,
            "success": str(success)
        }
        if metadata:
            labels.update(metadata)
        
        self.base_collector.record_histogram(f"content.processing.{processing_type}", duration_ms, labels)
        self.processing_durations[processing_type].append(duration_ms)
        
        if success:
            self.base_collector.increment_counter(f"content.processing.{processing_type}.success", 1)
        else:
            self.base_collector.increment_counter(f"content.processing.{processing_type}.failed", 1)

    def get_content_insights(self) -> Dict:
        """Get content processing insights."""        return {
            "average_upload_size_mb": sum(self.upload_sizes) / len(self.upload_sizes) / (1024*1024) if self.upload_sizes else 0,
            "total_unique_users": len(self.content_by_user),
            "most_active_users": sorted(self.content_by_user.items(), key=lambda x: x[1], reverse=True)[:10],
            "processing_performance": {
                processing_type: {
                    "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                    "total_processed": len(durations)
                }
                for processing_type, durations in self.processing_durations.items()
            }
        }


class AIMetricsCollector:
    """Specialized metrics collector for AI operations."""    
    def __init__(self, base_collector: MetricsCollector):
        self.base_collector = base_collector
        
        # AI-specific tracking
        self.model_performance = defaultdict(lambda: {"calls": 0, "total_duration": 0, "errors": 0})
        self.inference_sizes = defaultdict(list)
        
    def record_inference(self, model_name: str, operation: str, duration_ms: float, success: bool, 
                        input_size: int = 0, accuracy_score: Optional[float] = None):
        """Record AI inference event."""        self.base_collector.record_ai_operation(model_name, operation, duration_ms, success, input_size)
        
        # Track model-specific performance
        perf = self.model_performance[model_name]
        perf["calls"] += 1
        perf["total_duration"] += duration_ms
        if not success:
            perf["errors"] += 1
        
        if input_size > 0:
            self.inference_sizes[model_name].append(input_size)
        
        if accuracy_score:
            self.base_collector.record_histogram(f"ai.accuracy.{model_name}", accuracy_score, {"operation": operation})

    def get_ai_insights(self) -> Dict:
        """Get AI performance insights."""        insights = {}
        
        for model_name, perf in self.model_performance.items():
            avg_duration = perf["total_duration"] / perf["calls"] if perf["calls"] > 0 else 0
            error_rate = perf["errors"] / perf["calls"] if perf["calls"] > 0 else 0
            
            avg_input_size = 0
            if model_name in self.inference_sizes and self.inference_sizes[model_name]:
                avg_input_size = sum(self.inference_sizes[model_name]) / len(self.inference_sizes[model_name])
            
            insights[model_name] = {
                "total_calls": perf["calls"],
                "avg_duration_ms": round(avg_duration, 2),
                "error_rate": round(error_rate * 100, 2),
                "avg_input_size": round(avg_input_size, 2),
                "throughput_per_hour": perf["calls"]  # Assuming 1-hour window
            }
        
        return insights


class TimingContext:
    """Enhanced context manager for timing operations."""    
    def __init__(self, collector: MetricsCollector, name: str, labels: Optional[Dict] = None):
        self.collector = collector
        self.name = name
        self.labels = labels or {}
        self.start_time = None
        self.success = True
        self.metadata = {}

    def add_label(self, key: str, value: Any):
        """Add a label to the timing context."""        self.labels[key] = str(value)

    def add_metadata(self, key: str, value: Any):
        """Add metadata to be recorded with the timing."""        self.metadata[key] = value

    def set_success(self, success: bool):
        """Set the success status of the operation."""        self.success = success

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000  # Convert to milliseconds
            
            # Add success label
            self.labels["success"] = str(self.success and exc_type is None)
            
            # Record the timing
            self.collector.record_histogram(self.name, duration, self.labels)
            
            # If there was an exception, mark as error
            if exc_type is not None:
                self.collector.increment_counter(f"{self.name}.errors", 1, self.labels)
            else:
                self.collector.increment_counter(f"{self.name}.success", 1, self.labels)
