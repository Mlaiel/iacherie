"""Comprehensive metrics collection and monitoring for workflow system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
import time
import json
import asyncio
import logging


class MetricType(Enum):
    """Types of metrics collected."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class MetricLevel(Enum):
    """Metric importance levels."""    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Individual metric data point."""    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    level: MetricLevel = MetricLevel.INFO


@dataclass
class TimerContext:
    """Context manager for timing operations."""    name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metrics_collector: 'WorkflowMetrics' = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if self.metrics_collector:
            self.metrics_collector.record_timer(
                self.name, 
                duration, 
                tags=self.tags
            )


class WorkflowMetrics:
    """Comprehensive metrics collection for workflow operations."""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Storage for metrics
        self.metrics_storage = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.timers = defaultdict(list)
        
        # Aggregated metrics
        self.aggregated_metrics = {}
        self.aggregation_window = timedelta(minutes=5)
        self.last_aggregation = datetime.utcnow()
        
        # Performance tracking
        self.performance_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration
        self.retention_period = timedelta(hours=24)
        self.enable_aggregation = self.config.get("enable_aggregation", True)
        self.enable_performance_tracking = self.config.get("enable_performance_tracking", True)
        self.max_metrics_per_type = self.config.get("max_metrics_per_type", 10000)
        
        # Logger
        self.logger = logging.getLogger("workflow.metrics")
    
    def increment(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""        with self._lock:
            key = self._build_metric_key(metric_name, tags)
            self.counters[key] += value
            
            self._store_metric(Metric(
                name=metric_name,
                value=value,
                metric_type=MetricType.COUNTER,
                tags=tags or {}
            ))
    
    def decrement(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None):
        """Decrement a counter metric."""        self.increment(metric_name, -value, tags)
    
    def set_gauge(self, metric_name: str, value: Union[int, float], tags: Dict[str, str] = None):
        """Set a gauge metric value."""        with self._lock:
            key = self._build_metric_key(metric_name, tags)
            self.gauges[key] = value
            
            self._store_metric(Metric(
                name=metric_name,
                value=value,
                metric_type=MetricType.GAUGE,
                tags=tags or {}
            ))
    
    def record_histogram(self, metric_name: str, value: Union[int, float], tags: Dict[str, str] = None):
        """Record a value in a histogram."""        with self._lock:
            key = self._build_metric_key(metric_name, tags)
            self.histograms[key].append(value)
            
            # Maintain size limit
            if len(self.histograms[key]) > self.max_metrics_per_type:
                self.histograms[key] = self.histograms[key][-self.max_metrics_per_type//2:]
            
            self._store_metric(Metric(
                name=metric_name,
                value=value,
                metric_type=MetricType.HISTOGRAM,
                tags=tags or {}
            ))
    
    def record_timer(self, metric_name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timer metric."""        with self._lock:
            key = self._build_metric_key(metric_name, tags)
            self.timers[key].append(duration)
            
            # Maintain size limit
            if len(self.timers[key]) > self.max_metrics_per_type:
                self.timers[key] = self.timers[key][-self.max_metrics_per_type//2:]
            
            self._store_metric(Metric(
                name=metric_name,
                value=duration,
                metric_type=MetricType.TIMER,
                tags=tags or {}
            ))
    
    def timer(self, metric_name: str, tags: Dict[str, str] = None) -> TimerContext:
        """Create a timer context manager."""        return TimerContext(
            name=metric_name,
            tags=tags or {},
            metrics_collector=self
        )
    
    def record_workflow_execution(self, workflow_id: str, success: bool, duration: float, **kwargs):
        """Record workflow execution metrics."""        tags = {
            "workflow_id": workflow_id,
            "success": str(success).lower()
        }
        tags.update(kwargs.get("tags", {}))
        
        self.increment("workflow.executions.total", tags=tags)
        self.record_timer("workflow.execution.duration", duration, tags=tags)
        
        if success:
            self.increment("workflow.executions.success", tags=tags)
        else:
            self.increment("workflow.executions.failure", tags=tags)
    
    def record_pipeline_execution(self, pipeline_id: str, success: bool, duration: float, **kwargs):
        """Record pipeline execution metrics."""        tags = {
            "pipeline_id": pipeline_id,
            "success": str(success).lower()
        }
        tags.update(kwargs.get("tags", {}))
        
        self.increment("pipeline.executions.total", tags=tags)
        self.record_timer("pipeline.execution.duration", duration, tags=tags)
        
        if success:
            self.increment("pipeline.executions.success", tags=tags)
        else:
            self.increment("pipeline.executions.failure", tags=tags)
        
        # Record additional pipeline metrics
        steps_executed = kwargs.get("steps_executed", 0)
        steps_failed = kwargs.get("steps_failed", 0)
        
        self.record_histogram("pipeline.steps.executed", steps_executed, tags=tags)
        self.record_histogram("pipeline.steps.failed", steps_failed, tags=tags)
    
    def record_step_execution(self, pipeline_id: str, step_name: str, success: bool, duration: float, **kwargs):
        """Record pipeline step execution metrics."""        tags = {
            "pipeline_id": pipeline_id,
            "step_name": step_name,
            "success": str(success).lower()
        }
        tags.update(kwargs.get("tags", {}))
        
        self.increment("pipeline.step.executions.total", tags=tags)
        self.record_timer("pipeline.step.execution.duration", duration, tags=tags)
        
        if success:
            self.increment("pipeline.step.executions.success", tags=tags)
        else:
            self.increment("pipeline.step.executions.failure", tags=tags)
            
            error = kwargs.get("error")
            if error:
                error_tags = tags.copy()
                error_tags["error_type"] = type(error).__name__ if isinstance(error, Exception) else "unknown"
                self.increment("pipeline.step.errors", tags=error_tags)
    
    def record_scheduler_activity(self, task_id: str, activity: str, **kwargs):
        """Record scheduler activity metrics."""        tags = {
            "task_id": task_id,
            "activity": activity
        }
        tags.update(kwargs.get("tags", {}))
        
        self.increment(f"scheduler.{activity}", tags=tags)
        
        if activity == "task_executed":
            duration = kwargs.get("duration", 0)
            success = kwargs.get("success", False)
            
            self.record_timer("scheduler.task.execution.duration", duration, tags=tags)
            
            if success:
                self.increment("scheduler.task.executions.success", tags=tags)
            else:
                self.increment("scheduler.task.executions.failure", tags=tags)
    
    def record_automation_trigger(self, rule_id: str, trigger_type: str, success: bool, **kwargs):
        """Record automation trigger metrics."""        tags = {
            "rule_id": rule_id,
            "trigger_type": trigger_type,
            "success": str(success).lower()
        }
        tags.update(kwargs.get("tags", {}))
        
        self.increment("automation.triggers.total", tags=tags)
        
        if success:
            self.increment("automation.triggers.success", tags=tags)
        else:
            self.increment("automation.triggers.failure", tags=tags)
    
    def record_state_operation(self, state_id: str, operation: str, duration: float, **kwargs):
        """Record state management operation metrics."""        tags = {
            "state_id": state_id,
            "operation": operation
        }
        tags.update(kwargs.get("tags", {}))
        
        self.increment(f"state.{operation}.total", tags=tags)
        self.record_timer(f"state.{operation}.duration", duration, tags=tags)
        
        success = kwargs.get("success", True)
        if success:
            self.increment(f"state.{operation}.success", tags=tags)
        else:
            self.increment(f"state.{operation}.failure", tags=tags)
    
    def record_resource_usage(self, resource_type: str, usage: Union[int, float], **kwargs):
        """Record resource usage metrics."""        tags = {
            "resource_type": resource_type
        }
        tags.update(kwargs.get("tags", {}))
        
        self.set_gauge(f"resource.{resource_type}.usage", usage, tags=tags)
        
        # Track resource utilization
        capacity = kwargs.get("capacity")
        if capacity:
            utilization = (usage / capacity) * 100
            self.set_gauge(f"resource.{resource_type}.utilization", utilization, tags=tags)
    
    def get_metric_summary(self, metric_name: str, tags: Dict[str, str] = None) -> Dict[str, Any]:
        """Get summary statistics for a metric."""        with self._lock:
            key = self._build_metric_key(metric_name, tags)
            summary = {}
            
            # Counter metrics
            if key in self.counters:
                summary["counter"] = self.counters[key]
            
            # Gauge metrics
            if key in self.gauges:
                summary["gauge"] = self.gauges[key]
            
            # Histogram metrics
            if key in self.histograms and self.histograms[key]:
                values = self.histograms[key]
                summary["histogram"] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "p50": self._percentile(values, 50),
                    "p90": self._percentile(values, 90),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99)
                }
            
            # Timer metrics
            if key in self.timers and self.timers[key]:
                values = self.timers[key]
                summary["timer"] = {
                    "count": len(values),
                    "min_ms": min(values) * 1000,
                    "max_ms": max(values) * 1000,
                    "mean_ms": (sum(values) / len(values)) * 1000,
                    "p50_ms": self._percentile(values, 50) * 1000,
                    "p90_ms": self._percentile(values, 90) * 1000,
                    "p95_ms": self._percentile(values, 95) * 1000,
                    "p99_ms": self._percentile(values, 99) * 1000
                }
            
            return summary
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""        with self._lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {k: self._histogram_summary(v) for k, v in self.histograms.items()},
                "timers": {k: self._timer_summary(v) for k, v in self.timers.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow-specific metrics."""        workflow_metrics = {}
        
        for key, value in self.counters.items():
            if "workflow" in key:
                workflow_metrics[key] = value
        
        for key, value in self.timers.items():
            if "workflow" in key:
                workflow_metrics[key] = self._timer_summary(value)
        
        return workflow_metrics
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline-specific metrics."""        pipeline_metrics = {}
        
        for key, value in self.counters.items():
            if "pipeline" in key:
                pipeline_metrics[key] = value
        
        for key, value in self.timers.items():
            if "pipeline" in key:
                pipeline_metrics[key] = self._timer_summary(value)
        
        return pipeline_metrics
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format."""        metrics_data = self.get_all_metrics()
        
        if format_type == "json":
            return json.dumps(metrics_data, indent=2, default=str)
        elif format_type == "prometheus":
            return self._export_prometheus_format(metrics_data)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def clear_metrics(self, metric_type: str = None):
        """Clear metrics data."""        with self._lock:
            if metric_type is None or metric_type == "all":
                self.counters.clear()
                self.gauges.clear()
                self.histograms.clear()
                self.timers.clear()
                self.metrics_storage.clear()
            elif metric_type == "counters":
                self.counters.clear()
            elif metric_type == "gauges":
                self.gauges.clear()
            elif metric_type == "histograms":
                self.histograms.clear()
            elif metric_type == "timers":
                self.timers.clear()
    
    def cleanup_old_metrics(self):
        """Remove old metrics beyond retention period."""        with self._lock:
            cutoff_time = datetime.utcnow() - self.retention_period
            
            for metric_name, metrics_list in self.metrics_storage.items():
                self.metrics_storage[metric_name] = [
                    metric for metric in metrics_list
                    if metric.timestamp > cutoff_time
                ]
    
    async def start_background_tasks(self):
        """Start background metric aggregation and cleanup tasks."""        if self.enable_aggregation:
            asyncio.create_task(self._aggregation_task())
        
        asyncio.create_task(self._cleanup_task())
    
    async def _aggregation_task(self):
        """Background task for metric aggregation."""        while True:
            try:
                await asyncio.sleep(self.aggregation_window.total_seconds())
                self._aggregate_metrics()
            except Exception as e:
                self.logger.error(f"Error in metric aggregation task: {e}")
    
    async def _cleanup_task(self):
        """Background task for metric cleanup."""        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                self.cleanup_old_metrics()
            except Exception as e:
                self.logger.error(f"Error in metric cleanup task: {e}")
    
    def _aggregate_metrics(self):
        """Aggregate metrics over time window."""        with self._lock:
            now = datetime.utcnow()
            
            if now - self.last_aggregation < self.aggregation_window:
                return
            
            # Aggregate recent metrics
            for metric_name, metrics_list in self.metrics_storage.items():
                recent_metrics = [
                    metric for metric in metrics_list
                    if now - metric.timestamp <= self.aggregation_window
                ]
                
                if recent_metrics:
                    self.aggregated_metrics[metric_name] = self._calculate_aggregates(recent_metrics)
            
            self.last_aggregation = now
    
    def _calculate_aggregates(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Calculate aggregate statistics for metrics."""        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _store_metric(self, metric: Metric):
        """Store individual metric."""        self.metrics_storage[metric.name].append(metric)
        
        # Maintain storage limits
        if len(self.metrics_storage[metric.name]) > self.max_metrics_per_type:
            self.metrics_storage[metric.name] = (
                self.metrics_storage[metric.name][-self.max_metrics_per_type//2:]
            )
    
    def _build_metric_key(self, metric_name: str, tags: Dict[str, str] = None) -> str:
        """Build unique key for metric with tags."""        if not tags:
            return metric_name
        
        tag_string = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_name}#{tag_string}"
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = int(index)
            upper = lower + 1
            weight = index - lower
            
            if upper >= len(sorted_values):
                return sorted_values[lower]
            
            return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
    
    def _histogram_summary(self, values: List[float]) -> Dict[str, Any]:
        """Generate summary for histogram values."""        if not values:
            return {}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "p50": self._percentile(values, 50),
            "p90": self._percentile(values, 90),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99)
        }
    
    def _timer_summary(self, values: List[float]) -> Dict[str, Any]:
        """Generate summary for timer values."""        if not values:
            return {}
        
        return {
            "count": len(values),
            "min_ms": min(values) * 1000,
            "max_ms": max(values) * 1000,
            "mean_ms": (sum(values) / len(values)) * 1000,
            "p50_ms": self._percentile(values, 50) * 1000,
            "p90_ms": self._percentile(values, 90) * 1000,
            "p95_ms": self._percentile(values, 95) * 1000,
            "p99_ms": self._percentile(values, 99) * 1000
        }
    
    def _export_prometheus_format(self, metrics_data: Dict[str, Any]) -> str:
        """Export metrics in Prometheus format."""        prometheus_lines = []
        
        # Add help and type information
        prometheus_lines.append("# HELP workflow_metrics Workflow system metrics")
        prometheus_lines.append("# TYPE workflow_metrics gauge")
        
        # Export counters
        for key, value in metrics_data.get("counters", {}).items():
            metric_name = key.replace(".", "_").replace("#", "_")
            prometheus_lines.append(f'workflow_counter_{metric_name} {value}')
        
        # Export gauges
        for key, value in metrics_data.get("gauges", {}).items():
            metric_name = key.replace(".", "_").replace("#", "_")
            prometheus_lines.append(f'workflow_gauge_{metric_name} {value}')
        
        return "\n".join(prometheus_lines)
