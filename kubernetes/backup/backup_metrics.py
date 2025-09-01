"""Backup Metrics and Performance Monitoring for IA Influencer Agent Platform.

Provides comprehensive metrics collection, performance monitoring, and
analytics for backup operations with Prometheus integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution is strictly prohibited and will result
in immediate legal action under German and international law.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from collections import defaultdict, deque

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = Info = CollectorRegistry = None

from ...core.monitoring import BaseMetrics
from ...core.exceptions import MetricsError


class MetricType(Enum):
    """
Metric type enumeration."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    INFO = "info"


class BackupOperationType(Enum):
    """Backup operation type enumeration."""

    FULL_BACKUP = "full_backup"
    INCREMENTAL_BACKUP = "incremental_backup"
    CONTENT_BACKUP = "content_backup"
    USER_BACKUP = "user_backup"
    SYSTEM_BACKUP = "system_backup"
    RESTORE = "restore"
    VERIFICATION = "verification"


@dataclass
class MetricValue:
    """Metric value with metadata."""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""


@dataclass
class OperationMetrics:
    """Operation-specific metrics."""
    operation_id: str
    operation_type: BackupOperationType
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    bytes_processed: int = 0
    files_processed: int = 0
    success: bool = False
    error_message: Optional[str] = None
    progress_percent: float = 0.0
    throughput_mbps: float = 0.0


class BackupMetrics:
    """
    Comprehensive backup metrics collection and monitoring system.
    
    Provides real-time metrics collection, Prometheus integration,
    performance analytics, and operational insights.
    """
    def __init__(self, enable_prometheus: bool = True):
        """
        Initialize backup metrics system.
        
        Args:
            enable_prometheus: Enable Prometheus metrics export
        """
        self.logger = logging.getLogger(__name__)
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        
        # Metrics storage
        self.custom_metrics: Dict[str, MetricValue] = {}
        self.operation_metrics: Dict[str, OperationMetrics] = {}
        self.historical_metrics: deque = deque(maxlen=10000)
        
        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds: Dict[str, float] = {}
        
        # Thread safety
        self._metrics_lock = threading.RLock()
        
        # Initialize Prometheus metrics if available
        if self.enable_prometheus:
            self._init_prometheus_metrics()
        
        # Start metrics collection background task
        self._metrics_task = None
        self._start_metrics_collection()

    def _init_prometheus_metrics(self) -> None:
        """
Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            self.logger.warning("Prometheus client not available")
            return
        
        try:
            # Create custom registry
            self.registry = CollectorRegistry()
            
            # Backup operation metrics
            self.backup_operations_total = Counter(
                'backup_operations_total',
                'Total number of backup operations',
                ['operation_type', 'status'],
                registry=self.registry
            )
            
            self.backup_duration_seconds = Histogram(
                'backup_duration_seconds',
                'Backup operation duration in seconds',
                ['operation_type'],
                buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200],
                registry=self.registry
            )
            
            self.backup_bytes_processed = Counter(
                'backup_bytes_processed_total',
                'Total bytes processed in backup operations',
                ['operation_type'],
                registry=self.registry
            )
            
            self.backup_files_processed = Counter(
                'backup_files_processed_total',
                'Total files processed in backup operations',
                ['operation_type'],
                registry=self.registry
            )
            
            # Storage metrics
            self.backup_storage_used_bytes = Gauge(
                'backup_storage_used_bytes',
                'Current backup storage usage in bytes',
                ['storage_backend'],
                registry=self.registry
            )
            
            self.backup_storage_available_bytes = Gauge(
                'backup_storage_available_bytes',
                'Available backup storage in bytes',
                ['storage_backend'],
                registry=self.registry
            )
            
            # Performance metrics
            self.backup_throughput_mbps = Gauge(
                'backup_throughput_mbps',
                'Current backup throughput in MB/s',
                ['operation_type'],
                registry=self.registry
            )
            
            self.backup_compression_ratio = Gauge(
                'backup_compression_ratio',
                'Backup compression ratio',
                ['operation_type'],
                registry=self.registry
            )
            
            # System metrics
            self.backup_active_operations = Gauge(
                'backup_active_operations',
                'Number of currently active backup operations',
                registry=self.registry
            )
            
            self.backup_queue_size = Gauge(
                'backup_queue_size',
                'Number of backup operations in queue',
                registry=self.registry
            )
            
            # Error metrics
            self.backup_errors_total = Counter(
                'backup_errors_total',
                'Total number of backup errors',
                ['error_type', 'operation_type'],
                registry=self.registry
            )
            
            # Restoration metrics
            self.restore_operations_total = Counter(
                'restore_operations_total',
                'Total number of restore operations',
                ['restore_type', 'status'],
                registry=self.registry
            )
            
            self.restore_duration_seconds = Histogram(
                'restore_duration_seconds',
                'Restore operation duration in seconds',
                ['restore_type'],
                buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200],
                registry=self.registry
            )
            
            # Validation metrics
            self.backup_validation_total = Counter(
                'backup_validation_total',
                'Total number of backup validations',
                ['validation_type', 'status'],
                registry=self.registry
            )
            
            self.backup_integrity_score = Gauge(
                'backup_integrity_score',
                'Backup integrity score (0-1)',
                ['backup_id'],
                registry=self.registry
            )
            
            self.logger.info("Prometheus metrics initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Prometheus metrics: {e}")
            self.enable_prometheus = False

    def record_backup_operation(
        self,
        operation_id: str,
        operation_type: BackupOperationType,
        duration_seconds: float,
        bytes_processed: int,
        files_processed: int,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Record backup operation metrics.
        
        Args:
            operation_id: Operation identifier
            operation_type: Type of backup operation
            duration_seconds: Operation duration
            bytes_processed: Bytes processed
            files_processed: Files processed
            success: Operation success status
            error_message: Error message if failed
        """
        with self._metrics_lock:
            # Create operation metrics
            metrics = OperationMetrics(
                operation_id=operation_id,
                operation_type=operation_type,
                started_at=datetime.now() - timedelta(seconds=duration_seconds),
                completed_at=datetime.now(),
                duration_seconds=duration_seconds,
                bytes_processed=bytes_processed,
                files_processed=files_processed,
                success=success,
                error_message=error_message,
                progress_percent=100.0 if success else 0.0,
                throughput_mbps=self._calculate_throughput(bytes_processed, duration_seconds)
            )
            
            self.operation_metrics[operation_id] = metrics
            self.historical_metrics.append(metrics)
            
            # Update Prometheus metrics
            if self.enable_prometheus:
                self._update_prometheus_metrics(metrics)
            
            # Update performance history
            self._update_performance_history(metrics)
            
            self.logger.info(
                f"Recorded backup operation: {operation_id} "
                f"({operation_type.value}) - {'Success' if success else 'Failed'}"
            )

    def start_operation_tracking(
        self,
        operation_id: str,
        operation_type: BackupOperationType
    ) -> None:
        """
        Start tracking a backup operation.
        
        Args:
            operation_id: Operation identifier
            operation_type: Type of backup operation
        """
        with self._metrics_lock:
            metrics = OperationMetrics(
                operation_id=operation_id,
                operation_type=operation_type,
                started_at=datetime.now()
            )
            
            self.operation_metrics[operation_id] = metrics
            
            # Update active operations count
            if self.enable_prometheus:
                self.backup_active_operations.inc()

    def update_operation_progress(
        self,
        operation_id: str,
        progress_percent: float,
        bytes_processed: int = 0,
        files_processed: int = 0
    ) -> None:
        """
        Update operation progress.
        
        Args:
            operation_id: Operation identifier
            progress_percent: Progress percentage (0-100)
            bytes_processed: Bytes processed so far
            files_processed: Files processed so far
        """
        with self._metrics_lock:
            if operation_id in self.operation_metrics:
                metrics = self.operation_metrics[operation_id]
                metrics.progress_percent = progress_percent
                metrics.bytes_processed = bytes_processed
                metrics.files_processed = files_processed
                
                # Calculate current throughput
                elapsed_seconds = (datetime.now() - metrics.started_at).total_seconds()
                if elapsed_seconds > 0:
                    metrics.throughput_mbps = self._calculate_throughput(
                        bytes_processed, elapsed_seconds
                    )
                
                # Update Prometheus gauge
                if self.enable_prometheus:
                    self.backup_throughput_mbps.labels(
                        operation_type=metrics.operation_type.value
                    ).set(metrics.throughput_mbps)

    def complete_operation(
        self,
        operation_id: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Complete operation tracking.
        
        Args:
            operation_id: Operation identifier
            success: Operation success status
            error_message: Error message if failed
        """
        with self._metrics_lock:
            if operation_id in self.operation_metrics:
                metrics = self.operation_metrics[operation_id]
                metrics.completed_at = datetime.now()
                metrics.success = success
                metrics.error_message = error_message
                metrics.duration_seconds = (
                    metrics.completed_at - metrics.started_at
                ).total_seconds()
                
                # Final throughput calculation
                if metrics.duration_seconds > 0:
                    metrics.throughput_mbps = self._calculate_throughput(
                        metrics.bytes_processed, metrics.duration_seconds
                    )
                
                # Update Prometheus metrics
                if self.enable_prometheus:
                    self._update_prometheus_metrics(metrics)
                    self.backup_active_operations.dec()
                
                # Archive metrics
                self.historical_metrics.append(metrics)
                
                self.logger.info(f"Completed operation tracking: {operation_id}")

    def record_storage_metrics(
        self,
        storage_backend: str,
        used_bytes: int,
        available_bytes: int
    ) -> None:
        """
        Record storage usage metrics.
        
        Args:
            storage_backend: Storage backend name
            used_bytes: Used storage in bytes
            available_bytes: Available storage in bytes
        """
        with self._metrics_lock:
            if self.enable_prometheus:
                self.backup_storage_used_bytes.labels(
                    storage_backend=storage_backend
                ).set(used_bytes)
                
                self.backup_storage_available_bytes.labels(
                    storage_backend=storage_backend
                ).set(available_bytes)
            
            # Store custom metrics
            self.custom_metrics[f"storage_used_{storage_backend}"] = MetricValue(
                name="storage_used",
                value=used_bytes,
                labels={"storage_backend": storage_backend},
                description="Used storage in bytes"
            )
            
            self.custom_metrics[f"storage_available_{storage_backend}"] = MetricValue(
                name="storage_available",
                value=available_bytes,
                labels={"storage_backend": storage_backend},
                description="Available storage in bytes"
            )

    def record_error(
        self,
        error_type: str,
        operation_type: BackupOperationType,
        error_message: str
    ) -> None:
        """
        Record backup error.
        
        Args:
            error_type: Type of error
            operation_type: Backup operation type
            error_message: Error message
        """
        with self._metrics_lock:
            if self.enable_prometheus:
                self.backup_errors_total.labels(
                    error_type=error_type,
                    operation_type=operation_type.value
                ).inc()
            
            # Store error in custom metrics
            error_key = f"error_{error_type}_{operation_type.value}_{int(time.time())}"
            self.custom_metrics[error_key] = MetricValue(
                name="backup_error",
                value=1,
                labels={
                    "error_type": error_type,
                    "operation_type": operation_type.value,
                    "message": error_message
                },
                description="Backup error occurrence"
            )
            
            self.logger.warning(f"Recorded backup error: {error_type} - {error_message}")

    def get_operation_statistics(
        self,
        operation_type: Optional[BackupOperationType] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get operation statistics.
        
        Args:
            operation_type: Filter by operation type
            time_window_hours: Time window for statistics
            
        Returns:
            Operation statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Filter operations by time and type
        filtered_ops = [
            op for op in self.historical_metrics
            if op.started_at >= cutoff_time and
            (operation_type is None or op.operation_type == operation_type)
        ]
        
        if not filtered_ops:
            return {
                "total_operations": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "total_bytes_processed": 0,
                "total_files_processed": 0,
                "average_throughput": 0.0
            }
        
        # Calculate statistics
        total_ops = len(filtered_ops)
        successful_ops = sum(1 for op in filtered_ops if op.success)
        success_rate = successful_ops / total_ops if total_ops > 0 else 0
        
        durations = [op.duration_seconds for op in filtered_ops if op.duration_seconds > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        total_bytes = sum(op.bytes_processed for op in filtered_ops)
        total_files = sum(op.files_processed for op in filtered_ops)
        
        throughputs = [op.throughput_mbps for op in filtered_ops if op.throughput_mbps > 0]
        avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 0
        
        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "failed_operations": total_ops - successful_ops,
            "success_rate": success_rate,
            "average_duration": avg_duration,
            "max_duration": max(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "total_bytes_processed": total_bytes,
            "total_files_processed": total_files,
            "average_throughput": avg_throughput,
            "max_throughput": max(throughputs) if throughputs else 0,
            "time_window_hours": time_window_hours
        }

    def get_performance_trends(
        self,
        metric_name: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get performance trends for specific metric.
        
        Args:
            metric_name: Name of the metric
            time_window_hours: Time window for trends
            
        Returns:
            Performance trend data
        """
        if metric_name not in self.performance_history:
            return {"error": f"Metric {metric_name} not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        history = self.performance_history[metric_name]
        
        # Filter by time window
        recent_values = [
            (timestamp, value) for timestamp, value in history
            if timestamp >= cutoff_time
        ]
        
        if not recent_values:
            return {"error": "No data in time window"}
        
        values = [value for _, value in recent_values]
        
        return {
            "metric_name": metric_name,
            "data_points": len(values),
            "current_value": values[-1] if values else 0,
            "average": sum(values) / len(values),
            "maximum": max(values),
            "minimum": min(values),
            "trend": self._calculate_trend(values),
            "time_window_hours": time_window_hours
        }

    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics
        """
        if not self.enable_prometheus:
            return "# Prometheus metrics not enabled"
        
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to export Prometheus metrics: {e}")
            return f"# Error exporting metrics: {e}"

    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get backup system health summary.
        
        Returns:
            Health summary
        """
        recent_stats = self.get_operation_statistics(time_window_hours=1)
        
        # Calculate health score
        health_score = self._calculate_health_score(recent_stats)
        
        # Get active operations
        active_ops = [
            op for op in self.operation_metrics.values()
            if op.completed_at is None
        ]
        
        return {
            "health_score": health_score,
            "status": self._get_health_status(health_score),
            "active_operations": len(active_ops),
            "recent_success_rate": recent_stats.get("success_rate", 0),
            "average_throughput": recent_stats.get("average_throughput", 0),
            "total_operations_24h": self.get_operation_statistics(time_window_hours=24).get("total_operations", 0),
            "last_updated": datetime.now().isoformat()
        }

    def _calculate_throughput(self, bytes_processed: int, duration_seconds: float) -> float:
        """Calculate throughput in MB/s."""
        if duration_seconds <= 0:
            return 0.0
        
        megabytes = bytes_processed / (1024 * 1024)
        return megabytes / duration_seconds

    def _update_prometheus_metrics(self, metrics: OperationMetrics) -> None:
        """
Update Prometheus metrics with operation data."""
        if not self.enable_prometheus:
            return
        
        try:
            operation_type = metrics.operation_type.value
            status = "success" if metrics.success else "failure"
            
            # Update counters
            self.backup_operations_total.labels(
                operation_type=operation_type,
                status=status
            ).inc()
            
            self.backup_bytes_processed.labels(
                operation_type=operation_type
            ).inc(metrics.bytes_processed)
            
            self.backup_files_processed.labels(
                operation_type=operation_type
            ).inc(metrics.files_processed)
            
            # Update histograms
            self.backup_duration_seconds.labels(
                operation_type=operation_type
            ).observe(metrics.duration_seconds)
            
            # Update gauges
            self.backup_throughput_mbps.labels(
                operation_type=operation_type
            ).set(metrics.throughput_mbps)
            
        except Exception as e:
            self.logger.error(f"Failed to update Prometheus metrics: {e}")

    def _update_performance_history(self, metrics: OperationMetrics) -> None:
        """Update performance history with operation metrics."""
        timestamp = metrics.completed_at or datetime.now()
        
        # Store various performance metrics
        self.performance_history["duration"].append((timestamp, metrics.duration_seconds))
        self.performance_history["throughput"].append((timestamp, metrics.throughput_mbps))
        self.performance_history["bytes_processed"].append((timestamp, metrics.bytes_processed))
        self.performance_history["files_processed"].append((timestamp, metrics.files_processed))

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        change_percent = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"

    def _calculate_health_score(self, stats: Dict[str, Any]) -> float:
        """Calculate overall health score (0-1)."""
        success_rate = stats.get("success_rate", 0)
        throughput = stats.get("average_throughput", 0)
        
        # Base score from success rate
        score = success_rate
        
        # Adjust for throughput (normalized to expected range)
        expected_throughput = 10.0  # MB/s
        throughput_factor = min(throughput / expected_throughput, 1.0)
        score = (score * 0.8) + (throughput_factor * 0.2)
        
        return min(score, 1.0)

    def _get_health_status(self, health_score: float) -> str:
        """Get health status from score."""
        if health_score >= 0.9:
            return "excellent"
        elif health_score >= 0.7:
            return "good"
        elif health_score >= 0.5:
            return "fair"
        elif health_score >= 0.3:
            return "poor"
        else:
            return "critical"

    def _start_metrics_collection(self) -> None:
        """Start background metrics collection task."""
        if self._metrics_task is None:
            self._metrics_task = threading.Thread(
                target=self._metrics_collection_loop,
                daemon=True
            )
            self._metrics_task.start()

    def _metrics_collection_loop(self) -> None:
        """
Background metrics collection loop."""
        while True:
            try:
                # Perform periodic metrics collection
                self._collect_system_metrics()
                time.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(60)

    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        # Update queue size
        if self.enable_prometheus:
            queue_size = len([
                op for op in self.operation_metrics.values()
                if op.completed_at is None
            ])
            self.backup_queue_size.set(queue_size)


# Global metrics instance
backup_metrics = BackupMetrics()


def get_backup_metrics() -> BackupMetrics:
    """
Get global backup metrics instance."""
    return backup_metrics


def record_operation_metrics(
    operation_id: str,
    operation_type: str,
    duration_seconds: float,
    bytes_processed: int,
    success: bool
) -> None:
    """
Convenience function to record operation metrics."""
    backup_metrics.record_backup_operation(
        operation_id=operation_id,
        operation_type=BackupOperationType(operation_type),
        duration_seconds=duration_seconds,
        bytes_processed=bytes_processed,
        files_processed=0,
        success=success
    )
