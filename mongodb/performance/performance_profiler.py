"""MongoDB Performance Profiler
=============================

Real-time performance profiling and monitoring for MongoDB operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import time
import threading
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pymongo import MongoClient
from pymongo.collection import Collection
import psutil
import json

logger = logging.getLogger(__name__)

@dataclass
class OperationProfile:
    """Performance profile for a single operation."""
    operation_id: str
    collection_name: str
    operation_type: str
    query: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    execution_time_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    documents_processed: int
    bytes_transferred: int
    index_hits: int
    index_misses: int
    lock_time_ms: float
    wait_time_ms: float
    network_time_ms: float

@dataclass
class ProfilerMetrics:
    """Profiler performance metrics."""
    total_operations: int = 0
    avg_execution_time_ms: float = 0.0
    max_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float('inf')
    operations_per_second: float = 0.0
    avg_cpu_usage: float = 0.0
    avg_memory_usage_mb: float = 0.0
    total_documents_processed: int = 0
    total_bytes_transferred: int = 0
    cache_hit_ratio: float = 0.0
    slow_operations_count: int = 0

@dataclass
class SystemMetrics:
    """System-level performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    mongodb_connections: int
    mongodb_memory_mb: float

class PerformanceProfiler:
    """Real-time MongoDB performance profiler with system monitoring."""
    
    def __init__(self, client: MongoClient, sampling_interval: float = 1.0,
                 slow_threshold_ms: float = 100, max_profiles: int = 10000):
        """Initialize performance profiler.
        
        Args:
            client: MongoDB client instance
            sampling_interval: System metrics sampling interval in seconds
            slow_threshold_ms: Threshold for slow operation detection
            max_profiles: Maximum number of operation profiles to keep
        """
        self.client = client
        self.sampling_interval = sampling_interval
        self.slow_threshold_ms = slow_threshold_ms
        self.max_profiles = max_profiles
        
        # Operation tracking
        self._operation_profiles: deque = deque(maxlen=max_profiles)
        self._active_operations: Dict[str, Dict[str, Any]] = {}
        self._operation_lock = threading.RLock()
        
        # Metrics tracking
        self._metrics = ProfilerMetrics()
        self._system_metrics: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        
        # Monitoring threads
        self._monitoring_active = False
        self._system_monitor_thread = None
        self._metrics_calculator_thread = None
        
        # Performance callbacks
        self._slow_operation_callbacks: List[Callable] = []
        self._threshold_callbacks: List[Callable] = []
        
        # Baseline metrics for comparison
        self._baseline_metrics: Optional[ProfilerMetrics] = None
        
        # Profiler start time
        self._start_time = datetime.utcnow()
        
        # System process for monitoring
        self._process = psutil.Process()
    
    def start_profiling(self) -> None:
        """Start performance profiling."""
        if self._monitoring_active:
            logger.warning("Profiling already active")
            return
        
        self._monitoring_active = True
        
        # Start system monitoring thread
        self._system_monitor_thread = threading.Thread(
            target=self._system_monitor_loop,
            daemon=True
        )
        self._system_monitor_thread.start()
        
        # Start metrics calculation thread
        self._metrics_calculator_thread = threading.Thread(
            target=self._metrics_calculator_loop,
            daemon=True
        )
        self._metrics_calculator_thread.start()
        
        logger.info("Performance profiling started")
    
    def stop_profiling(self) -> None:
        """Stop performance profiling."""
        self._monitoring_active = False
        
        # Wait for threads to finish
        if self._system_monitor_thread:
            self._system_monitor_thread.join(timeout=5)
        if self._metrics_calculator_thread:
            self._metrics_calculator_thread.join(timeout=5)
        
        logger.info("Performance profiling stopped")
    
    def profile_operation(self, operation_func: Callable, *args, **kwargs) -> Any:
        """Profile a specific operation.
        
        Args:
            operation_func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Operation result
        """
        operation_id = self._generate_operation_id()
        
        # Extract operation details
        collection_name = "unknown"
        operation_type = operation_func.__name__
        query = {}
        
        # Try to extract collection and query information
        if args:
            if hasattr(args[0], 'name'):  # Collection object
                collection_name = args[0].name
            if len(args) > 1 and isinstance(args[1], dict):
                query = args[1]
        
        # Record operation start
        start_time = datetime.utcnow()
        start_cpu = psutil.cpu_percent()
        start_memory = self._process.memory_info().rss / 1024 / 1024  # MB
        
        with self._operation_lock:
            self._active_operations[operation_id] = {
                'collection_name': collection_name,
                'operation_type': operation_type,
                'query': query,
                'start_time': start_time,
                'start_cpu': start_cpu,
                'start_memory': start_memory
            }
        
        try:
            # Execute operation
            result = operation_func(*args, **kwargs)
            
            # Record operation completion
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() * 1000  # ms
            end_cpu = psutil.cpu_percent()
            end_memory = self._process.memory_info().rss / 1024 / 1024  # MB
            
            # Calculate metrics
            cpu_usage = (end_cpu + start_cpu) / 2
            memory_usage = (end_memory + start_memory) / 2
            
            # Create operation profile
            profile = OperationProfile(
                operation_id=operation_id,
                collection_name=collection_name,
                operation_type=operation_type,
                query=query,
                start_time=start_time,
                end_time=end_time,
                execution_time_ms=execution_time,
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_usage,
                documents_processed=self._estimate_documents_processed(result),
                bytes_transferred=self._estimate_bytes_transferred(result),
                index_hits=0,  # Would need MongoDB explain to get this
                index_misses=0,
                lock_time_ms=0,  # Would need MongoDB profiler data
                wait_time_ms=0,
                network_time_ms=0
            )
            
            # Store profile
            self._operation_profiles.append(profile)
            
            # Check for slow operation
            if execution_time >= self.slow_threshold_ms:
                self._handle_slow_operation(profile)
            
            # Remove from active operations
            with self._operation_lock:
                self._active_operations.pop(operation_id, None)
            
            return result
            
        except Exception as e:
            # Handle operation error
            with self._operation_lock:
                self._active_operations.pop(operation_id, None)
            
            logger.error(f"Profiled operation failed: {e}")
            raise
    
    def get_current_metrics(self) -> ProfilerMetrics:
        """Get current profiler metrics.
        
        Returns:
            Current performance metrics
        """
        return self._metrics
    
    def get_system_metrics(self, hours: int = 1) -> List[SystemMetrics]:
        """Get system metrics for specified time period.
        
        Args:
            hours: Number of hours of metrics to return
            
        Returns:
            List of system metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metric for metric in self._system_metrics
            if metric.timestamp >= cutoff_time
        ]
    
    def get_slow_operations(self, limit: int = 100) -> List[OperationProfile]:
        """Get slow operations.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of slow operations
        """
        slow_ops = [
            profile for profile in self._operation_profiles
            if profile.execution_time_ms >= self.slow_threshold_ms
        ]
        
        # Sort by execution time descending
        slow_ops.sort(key=lambda x: x.execution_time_ms, reverse=True)
        
        return slow_ops[:limit]
    
    def get_operation_patterns(self) -> Dict[str, Any]:
        """Analyze operation patterns.
        
        Returns:
            Operation pattern analysis
        """
        if not self._operation_profiles:
            return {}
        
        # Group by operation type
        operation_stats = defaultdict(list)
        for profile in self._operation_profiles:
            operation_stats[profile.operation_type].append(profile)
        
        # Calculate statistics for each operation type
        pattern_analysis = {}
        for op_type, profiles in operation_stats.items():
            execution_times = [p.execution_time_ms for p in profiles]
            
            pattern_analysis[op_type] = {
                'count': len(profiles),
                'avg_execution_time_ms': sum(execution_times) / len(execution_times),
                'max_execution_time_ms': max(execution_times),
                'min_execution_time_ms': min(execution_times),
                'slow_operations': len([p for p in profiles if p.execution_time_ms >= self.slow_threshold_ms]),
                'collections': list(set(p.collection_name for p in profiles))
            }
        
        return pattern_analysis
    
    def get_collection_performance(self, collection_name: str) -> Dict[str, Any]:
        """Get performance analysis for specific collection.
        
        Args:
            collection_name: Collection name to analyze
            
        Returns:
            Collection performance analysis
        """
        collection_profiles = [
            p for p in self._operation_profiles
            if p.collection_name == collection_name
        ]
        
        if not collection_profiles:
            return {"error": f"No operations found for collection '{collection_name}'"}
        
        execution_times = [p.execution_time_ms for p in collection_profiles]
        
        return {
            'collection_name': collection_name,
            'total_operations': len(collection_profiles),
            'avg_execution_time_ms': sum(execution_times) / len(execution_times),
            'max_execution_time_ms': max(execution_times),
            'min_execution_time_ms': min(execution_times),
            'slow_operations': len([p for p in collection_profiles if p.execution_time_ms >= self.slow_threshold_ms]),
            'operation_types': list(set(p.operation_type for p in collection_profiles)),
            'total_documents_processed': sum(p.documents_processed for p in collection_profiles),
            'total_bytes_transferred': sum(p.bytes_transferred for p in collection_profiles)
        }
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report.
        
        Args:
            hours: Hours of data to include in report
            
        Returns:
            Performance report
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_profiles = [
            p for p in self._operation_profiles
            if p.start_time >= cutoff_time
        ]
        
        if not recent_profiles:
            return {"error": "No operations in specified time period"}
        
        # Calculate summary statistics
        execution_times = [p.execution_time_ms for p in recent_profiles]
        
        # System metrics summary
        recent_system_metrics = self.get_system_metrics(hours)
        avg_cpu = sum(m.cpu_percent for m in recent_system_metrics) / len(recent_system_metrics) if recent_system_metrics else 0
        avg_memory = sum(m.memory_percent for m in recent_system_metrics) / len(recent_system_metrics) if recent_system_metrics else 0
        
        # Collection performance
        collections = set(p.collection_name for p in recent_profiles)
        collection_performance = {}
        for collection in collections:
            collection_performance[collection] = self.get_collection_performance(collection)
        
        report = {
            'report_period_hours': hours,
            'summary': {
                'total_operations': len(recent_profiles),
                'avg_execution_time_ms': sum(execution_times) / len(execution_times),
                'max_execution_time_ms': max(execution_times),
                'min_execution_time_ms': min(execution_times),
                'slow_operations': len([p for p in recent_profiles if p.execution_time_ms >= self.slow_threshold_ms]),
                'operations_per_second': len(recent_profiles) / (hours * 3600),
                'collections_accessed': len(collections)
            },
            'system_performance': {
                'avg_cpu_percent': avg_cpu,
                'avg_memory_percent': avg_memory,
                'peak_cpu_percent': max((m.cpu_percent for m in recent_system_metrics), default=0),
                'peak_memory_percent': max((m.memory_percent for m in recent_system_metrics), default=0)
            },
            'operation_patterns': self.get_operation_patterns(),
            'collection_performance': collection_performance,
            'slowest_operations': [
                {
                    'collection': p.collection_name,
                    'operation': p.operation_type,
                    'execution_time_ms': p.execution_time_ms,
                    'cpu_usage': p.cpu_usage_percent,
                    'memory_usage_mb': p.memory_usage_mb,
                    'query': p.query
                }
                for p in sorted(recent_profiles, key=lambda x: x.execution_time_ms, reverse=True)[:10]
            ]
        }
        
        return report
    
    def set_baseline(self) -> None:
        """Set current metrics as baseline for comparison."""
        self._baseline_metrics = self._metrics
        logger.info("Performance baseline set")
    
    def compare_to_baseline(self) -> Dict[str, Any]:
        """Compare current metrics to baseline.
        
        Returns:
            Comparison analysis
        """
        if not self._baseline_metrics:
            return {"error": "No baseline set"}
        
        current = self._metrics
        baseline = self._baseline_metrics
        
        def percentage_change(current_val, baseline_val):
            if baseline_val == 0:
                return 0
            return ((current_val - baseline_val) / baseline_val) * 100
        
        return {
            'execution_time_change_percent': percentage_change(
                current.avg_execution_time_ms, baseline.avg_execution_time_ms
            ),
            'throughput_change_percent': percentage_change(
                current.operations_per_second, baseline.operations_per_second
            ),
            'cpu_usage_change_percent': percentage_change(
                current.avg_cpu_usage, baseline.avg_cpu_usage
            ),
            'memory_usage_change_percent': percentage_change(
                current.avg_memory_usage_mb, baseline.avg_memory_usage_mb
            ),
            'cache_hit_ratio_change_percent': percentage_change(
                current.cache_hit_ratio, baseline.cache_hit_ratio
            ),
            'slow_operations_change_percent': percentage_change(
                current.slow_operations_count, baseline.slow_operations_count
            )
        }
    
    def register_slow_operation_callback(self, callback: Callable[[OperationProfile], None]) -> None:
        """Register callback for slow operation detection.
        
        Args:
            callback: Callback function to execute on slow operation
        """
        self._slow_operation_callbacks.append(callback)
    
    def register_threshold_callback(self, metric: str, threshold: float,
                                  callback: Callable[[str, float, float], None]) -> None:
        """Register callback for metric threshold violations.
        
        Args:
            metric: Metric name to monitor
            threshold: Threshold value
            callback: Callback function to execute
        """
        self._threshold_callbacks.append({
            'metric': metric,
            'threshold': threshold,
            'callback': callback
        })
    
    def export_profiles_to_json(self, filepath: str, hours: int = 24) -> None:
        """Export operation profiles to JSON file.
        
        Args:
            filepath: Output file path
            hours: Hours of data to export
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_profiles = [
            asdict(p) for p in self._operation_profiles
            if p.start_time >= cutoff_time
        ]
        
        # Convert datetime objects to strings
        for profile in recent_profiles:
            profile['start_time'] = profile['start_time'].isoformat()
            profile['end_time'] = profile['end_time'].isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(recent_profiles, f, indent=2, default=str)
        
        logger.info(f"Exported {len(recent_profiles)} profiles to {filepath}")
    
    def clear_profiles(self) -> None:
        """Clear all stored operation profiles."""
        self._operation_profiles.clear()
        self._system_metrics.clear()
        self._metrics = ProfilerMetrics()
        logger.info("Performance profiles cleared")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _estimate_documents_processed(self, result: Any) -> int:
        """Estimate number of documents processed based on result."""
        try:
            if hasattr(result, 'inserted_id'):
                return 1  # Insert operation
            elif hasattr(result, 'matched_count'):
                return result.matched_count  # Update operation
            elif hasattr(result, 'deleted_count'):
                return result.deleted_count  # Delete operation
            elif hasattr(result, '__iter__'):
                return len(list(result))  # Query result
            else:
                return 1  # Default
        except Exception:
            return 0
    
    def _estimate_bytes_transferred(self, result: Any) -> int:
        """Estimate bytes transferred based on result."""
        try:
            if result is None:
                return 0
            
            import sys
            return sys.getsizeof(result)
        except Exception:
            return 0
    
    def _handle_slow_operation(self, profile: OperationProfile) -> None:
        """Handle slow operation detection."""
        logger.warning(f"Slow operation detected: {profile.operation_type} on "
                      f"{profile.collection_name} took {profile.execution_time_ms:.1f}ms")
        
        # Execute callbacks
        for callback in self._slow_operation_callbacks:
            try:
                callback(profile)
            except Exception as e:
                logger.error(f"Slow operation callback error: {e}")
    
    def _system_monitor_loop(self) -> None:
        """System monitoring loop."""
        while self._monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                # MongoDB-specific metrics
                try:
                    server_status = self.client.admin.command("serverStatus")
                    mongodb_connections = server_status.get('connections', {}).get('current', 0)
                    mongodb_memory = server_status.get('mem', {}).get('resident', 0)
                except Exception:
                    mongodb_connections = 0
                    mongodb_memory = 0
                
                system_metrics = SystemMetrics(
                    timestamp=datetime.utcnow(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
                    disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
                    network_io_sent_mb=network_io.bytes_sent / 1024 / 1024 if network_io else 0,
                    network_io_recv_mb=network_io.bytes_recv / 1024 / 1024 if network_io else 0,
                    mongodb_connections=mongodb_connections,
                    mongodb_memory_mb=mongodb_memory
                )
                
                self._system_metrics.append(system_metrics)
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                time.sleep(5)  # Sleep longer on error
    
    def _metrics_calculator_loop(self) -> None:
        """Metrics calculation loop."""
        while self._monitoring_active:
            try:
                self._calculate_current_metrics()
                self._check_threshold_violations()
                time.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Metrics calculation error: {e}")
                time.sleep(5)
    
    def _calculate_current_metrics(self) -> None:
        """Calculate current performance metrics."""
        if not self._operation_profiles:
            return
        
        recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
        recent_profiles = [
            p for p in self._operation_profiles
            if p.start_time >= recent_cutoff
        ]
        
        if not recent_profiles:
            return
        
        execution_times = [p.execution_time_ms for p in recent_profiles]
        
        # Calculate metrics
        self._metrics.total_operations = len(self._operation_profiles)
        self._metrics.avg_execution_time_ms = sum(execution_times) / len(execution_times)
        self._metrics.max_execution_time_ms = max(execution_times)
        self._metrics.min_execution_time_ms = min(execution_times)
        self._metrics.operations_per_second = len(recent_profiles) / 300  # 5 minutes
        self._metrics.avg_cpu_usage = sum(p.cpu_usage_percent for p in recent_profiles) / len(recent_profiles)
        self._metrics.avg_memory_usage_mb = sum(p.memory_usage_mb for p in recent_profiles) / len(recent_profiles)
        self._metrics.total_documents_processed = sum(p.documents_processed for p in self._operation_profiles)
        self._metrics.total_bytes_transferred = sum(p.bytes_transferred for p in self._operation_profiles)
        self._metrics.slow_operations_count = len([p for p in recent_profiles if p.execution_time_ms >= self.slow_threshold_ms])
        
        # Calculate cache hit ratio (approximation)
        total_hits = sum(p.index_hits for p in recent_profiles)
        total_requests = total_hits + sum(p.index_misses for p in recent_profiles)
        self._metrics.cache_hit_ratio = (total_hits / total_requests * 100) if total_requests > 0 else 0
    
    def _check_threshold_violations(self) -> None:
        """Check for metric threshold violations."""
        current_metrics = asdict(self._metrics)
        
        for threshold_config in self._threshold_callbacks:
            metric_name = threshold_config['metric']
            threshold = threshold_config['threshold']
            callback = threshold_config['callback']
            
            if metric_name in current_metrics:
                current_value = current_metrics[metric_name]
                if current_value > threshold:
                    try:
                        callback(metric_name, current_value, threshold)
                    except Exception as e:
                        logger.error(f"Threshold callback error: {e}")

# Global profiler instance
_default_profiler: Optional[PerformanceProfiler] = None

def get_performance_profiler(client: MongoClient, **kwargs) -> PerformanceProfiler:
    """Get or create default performance profiler."""
    global _default_profiler
    if _default_profiler is None:
        _default_profiler = PerformanceProfiler(client, **kwargs)
    return _default_profiler

__all__ = [
    'PerformanceProfiler', 'OperationProfile', 'ProfilerMetrics', 'SystemMetrics',
    'get_performance_profiler'
]