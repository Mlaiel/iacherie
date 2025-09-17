"""🗄️ Storage I/O Performance Profiler
=====================================

Advanced storage and I/O performance profiling system for the Ainflue Creator Economy platform.
Monitors disk I/O, file system operations, S3/Cloud storage, and network storage performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import os
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import psutil
from pathlib import Path

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Types of storage systems"""
    LOCAL_DISK = "local_disk"
    SSD = "ssd"
    HDD = "hdd"
    NETWORK_STORAGE = "network_storage"
    S3_CLOUD = "s3_cloud"
    AZURE_BLOB = "azure_blob"
    GCP_STORAGE = "gcp_storage"
    CDN = "cdn"


class IOOperationType(Enum):
    """Types of I/O operations"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    COPY = "copy"
    MOVE = "move"
    SYNC = "sync"
    UPLOAD = "upload"
    DOWNLOAD = "download"


class StorageLocation(Enum):
    """Storage location categories"""
    CREATOR_CONTENT = "creator_content"
    USER_DATA = "user_data"
    SYSTEM_LOGS = "system_logs"
    CACHE_DATA = "cache_data"
    BACKUP_DATA = "backup_data"
    TEMP_FILES = "temp_files"
    ANALYTICS_DATA = "analytics_data"


@dataclass
class FileMetadata:
    """Metadata for file operations"""
    file_path: str
    file_size: int
    file_type: str
    content_type: Optional[str] = None
    creator_id: Optional[str] = None
    compression: Optional[str] = None
    encryption: bool = False
    access_pattern: str = "random"  # sequential, random, streaming


@dataclass
class StorageMetrics:
    """Storage performance metrics"""
    operation_id: str
    storage_type: StorageType
    operation_type: IOOperationType
    location: StorageLocation
    file_metadata: FileMetadata
    
    # Performance metrics
    latency_ms: float
    throughput_mbps: float
    iops: float
    
    # System metrics
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_usage_percent: float
    
    # Network metrics (for cloud storage)
    network_latency_ms: Optional[float] = None
    bandwidth_utilization_percent: Optional[float] = None
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    retry_count: int = 0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StorageBottleneck:
    """Storage bottleneck detection"""
    bottleneck_id: str
    storage_type: StorageType
    location: StorageLocation
    
    # Bottleneck details
    bottleneck_type: str  # "high_latency", "low_throughput", "high_cpu", "disk_full"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class StorageIOProfiler:
    """Advanced storage I/O performance profiler"""
    
    def __init__(self, 
                 monitoring_interval: float = 1.0,
                 max_history_size: int = 10000,
                 enable_file_tracking: bool = True,
                 enable_cloud_monitoring: bool = True):
        """
        Initialize storage I/O profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_file_tracking: Enable detailed file operation tracking
            enable_cloud_monitoring: Enable cloud storage monitoring
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_file_tracking = enable_file_tracking
        self.enable_cloud_monitoring = enable_cloud_monitoring
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.current_operations: Dict[str, StorageMetrics] = {}
        self.bottlenecks: List[StorageBottleneck] = []
        
        # Performance thresholds
        self.thresholds = {
            'max_latency_ms': 1000.0,
            'min_throughput_mbps': 10.0,
            'max_cpu_usage': 80.0,
            'max_disk_usage': 85.0,
            'max_retry_count': 3
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("StorageIOProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'storage_operation_duration': Histogram(
                'ainflue_storage_operation_duration_seconds',
                'Duration of storage operations',
                ['storage_type', 'operation_type', 'location']
            ),
            'storage_throughput': Gauge(
                'ainflue_storage_throughput_mbps',
                'Storage throughput in MB/s',
                ['storage_type', 'location']
            ),
            'storage_latency': Gauge(
                'ainflue_storage_latency_ms',
                'Storage operation latency in ms',
                ['storage_type', 'operation_type']
            ),
            'storage_errors': Counter(
                'ainflue_storage_errors_total',
                'Total storage operation errors',
                ['storage_type', 'error_type']
            ),
            'storage_bottlenecks': Gauge(
                'ainflue_storage_bottlenecks_active',
                'Number of active storage bottlenecks',
                ['storage_type', 'severity']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous storage monitoring"""
        if self.is_monitoring:
            logger.warning("Storage monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Storage I/O monitoring started")
    
    async def stop_monitoring(self):
        """Stop storage monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Storage I/O monitoring stopped")
    
    async def profile_storage_operation(self,
                                      operation_type: IOOperationType,
                                      storage_type: StorageType,
                                      location: StorageLocation,
                                      file_metadata: FileMetadata,
                                      operation_func: Callable,
                                      *args, **kwargs) -> StorageMetrics:
        """
        Profile a storage operation
        
        Args:
            operation_type: Type of I/O operation
            storage_type: Type of storage system
            location: Storage location category
            file_metadata: File metadata
            operation_func: Function to execute and profile
            *args, **kwargs: Arguments for the operation function
        
        Returns:
            StorageMetrics: Detailed performance metrics
        """
        operation_id = f"{operation_type.value}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # Get initial system metrics
        initial_cpu = psutil.cpu_percent()
        initial_memory = psutil.virtual_memory()
        
        try:
            # Execute the operation
            result = await self._execute_operation(operation_func, *args, **kwargs)
            
            # Calculate performance metrics
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Calculate throughput
            throughput_mbps = 0.0
            if file_metadata.file_size > 0:
                throughput_mbps = (file_metadata.file_size / (1024 * 1024)) / (end_time - start_time)
            
            # Get final system metrics
            final_cpu = psutil.cpu_percent()
            final_memory = psutil.virtual_memory()
            
            # Calculate IOPS (simplified)
            iops = 1.0 / (end_time - start_time) if (end_time - start_time) > 0 else 0.0
            
            # Create metrics object
            metrics = StorageMetrics(
                operation_id=operation_id,
                storage_type=storage_type,
                operation_type=operation_type,
                location=location,
                file_metadata=file_metadata,
                latency_ms=latency_ms,
                throughput_mbps=throughput_mbps,
                iops=iops,
                cpu_usage_percent=(initial_cpu + final_cpu) / 2,
                memory_usage_mb=final_memory.used / (1024 * 1024),
                disk_usage_percent=psutil.disk_usage('/').percent,
                success=True
            )
            
            # Add network metrics for cloud storage
            if storage_type in [StorageType.S3_CLOUD, StorageType.AZURE_BLOB, StorageType.GCP_STORAGE]:
                metrics.network_latency_ms = await self._measure_network_latency()
                metrics.bandwidth_utilization_percent = await self._measure_bandwidth_utilization()
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            logger.debug(f"Storage operation profiled: {operation_id} - {latency_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle operation failure
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            metrics = StorageMetrics(
                operation_id=operation_id,
                storage_type=storage_type,
                operation_type=operation_type,
                location=location,
                file_metadata=file_metadata,
                latency_ms=latency_ms,
                throughput_mbps=0.0,
                iops=0.0,
                cpu_usage_percent=psutil.cpu_percent(),
                memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
                disk_usage_percent=psutil.disk_usage('/').percent,
                success=False,
                error_message=str(e)
            )
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['storage_errors'].labels(
                storage_type=storage_type.value,
                error_type=type(e).__name__
            ).inc()
            
            logger.error(f"Storage operation failed: {operation_id} - {e}")
            return metrics
    
    async def _execute_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute storage operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    async def _store_metrics(self, metrics: StorageMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.current_operations[metrics.operation_id] = metrics
    
    def _update_prometheus_metrics(self, metrics: StorageMetrics):
        """Update Prometheus metrics"""
        # Update operation duration
        self.prometheus_metrics['storage_operation_duration'].labels(
            storage_type=metrics.storage_type.value,
            operation_type=metrics.operation_type.value,
            location=metrics.location.value
        ).observe(metrics.latency_ms / 1000)
        
        # Update throughput
        self.prometheus_metrics['storage_throughput'].labels(
            storage_type=metrics.storage_type.value,
            location=metrics.location.value
        ).set(metrics.throughput_mbps)
        
        # Update latency
        self.prometheus_metrics['storage_latency'].labels(
            storage_type=metrics.storage_type.value,
            operation_type=metrics.operation_type.value
        ).set(metrics.latency_ms)
    
    async def _detect_bottlenecks(self, metrics: StorageMetrics):
        """Detect storage performance bottlenecks"""
        bottlenecks = []
        
        # High latency detection
        if metrics.latency_ms > self.thresholds['max_latency_ms']:
            bottleneck = StorageBottleneck(
                bottleneck_id=f"high_latency_{int(time.time())}",
                storage_type=metrics.storage_type,
                location=metrics.location,
                bottleneck_type="high_latency",
                severity="high" if metrics.latency_ms > self.thresholds['max_latency_ms'] * 2 else "medium",
                description=f"High latency detected: {metrics.latency_ms:.2f}ms",
                current_performance={"latency_ms": metrics.latency_ms},
                expected_performance={"latency_ms": self.thresholds['max_latency_ms']},
                impact_percentage=(metrics.latency_ms - self.thresholds['max_latency_ms']) / self.thresholds['max_latency_ms'] * 100,
                recommendations=[
                    "Consider caching frequently accessed files",
                    "Optimize file access patterns",
                    "Check disk health and fragmentation",
                    "Consider SSD upgrade for critical data"
                ],
                estimated_improvement={"latency_reduction_percent": 30.0}
            )
            bottlenecks.append(bottleneck)
        
        # Low throughput detection
        if metrics.throughput_mbps < self.thresholds['min_throughput_mbps']:
            bottleneck = StorageBottleneck(
                bottleneck_id=f"low_throughput_{int(time.time())}",
                storage_type=metrics.storage_type,
                location=metrics.location,
                bottleneck_type="low_throughput",
                severity="medium",
                description=f"Low throughput detected: {metrics.throughput_mbps:.2f} MB/s",
                current_performance={"throughput_mbps": metrics.throughput_mbps},
                expected_performance={"throughput_mbps": self.thresholds['min_throughput_mbps']},
                impact_percentage=(self.thresholds['min_throughput_mbps'] - metrics.throughput_mbps) / self.thresholds['min_throughput_mbps'] * 100,
                recommendations=[
                    "Optimize I/O operations batch size",
                    "Consider parallel processing for large files",
                    "Check network bandwidth for cloud storage",
                    "Review compression settings"
                ],
                estimated_improvement={"throughput_improvement_percent": 50.0}
            )
            bottlenecks.append(bottleneck)
        
        # High CPU usage detection
        if metrics.cpu_usage_percent > self.thresholds['max_cpu_usage']:
            bottleneck = StorageBottleneck(
                bottleneck_id=f"high_cpu_{int(time.time())}",
                storage_type=metrics.storage_type,
                location=metrics.location,
                bottleneck_type="high_cpu",
                severity="high",
                description=f"High CPU usage during I/O: {metrics.cpu_usage_percent:.1f}%",
                current_performance={"cpu_usage_percent": metrics.cpu_usage_percent},
                expected_performance={"cpu_usage_percent": self.thresholds['max_cpu_usage']},
                impact_percentage=(metrics.cpu_usage_percent - self.thresholds['max_cpu_usage']) / self.thresholds['max_cpu_usage'] * 100,
                recommendations=[
                    "Optimize file processing algorithms",
                    "Consider hardware acceleration",
                    "Reduce concurrent I/O operations",
                    "Profile CPU-intensive operations"
                ],
                estimated_improvement={"cpu_reduction_percent": 25.0}
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['storage_bottlenecks'].labels(
                storage_type=bottleneck.storage_type.value,
                severity=bottleneck.severity
            ).inc()
    
    async def _measure_network_latency(self) -> float:
        """Measure network latency for cloud operations"""
        # Simplified latency measurement
        start_time = time.time()
        try:
            # This would be replaced with actual network ping/test
            await asyncio.sleep(0.001)  # Simulated network call
            return (time.time() - start_time) * 1000
        except Exception:
            return 0.0
    
    async def _measure_bandwidth_utilization(self) -> float:
        """Measure bandwidth utilization"""
        # Simplified bandwidth measurement
        try:
            net_io = psutil.net_io_counters()
            if hasattr(net_io, 'bytes_sent') and hasattr(net_io, 'bytes_recv'):
                # This is a simplified calculation
                return min(95.0, (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024 * 100) * 100)
            return 0.0
        except Exception:
            return 0.0
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor system storage metrics
                await self._monitor_system_storage()
                
                # Monitor active operations
                await self._monitor_active_operations()
                
                # Clean up old bottlenecks
                await self._cleanup_old_bottlenecks()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in storage monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_system_storage(self):
        """Monitor overall system storage performance"""
        try:
            # Get disk usage
            disk_usage = psutil.disk_usage('/')
            
            # Get disk I/O stats
            disk_io = psutil.disk_io_counters()
            
            # Update Prometheus metrics
            self.prometheus_metrics['storage_latency'].labels(
                storage_type=StorageType.LOCAL_DISK.value,
                operation_type="system"
            ).set(disk_usage.percent)
            
        except Exception as e:
            logger.error(f"Error monitoring system storage: {e}")
    
    async def _monitor_active_operations(self):
        """Monitor currently active operations"""
        # This would monitor long-running operations
        pass
    
    async def _cleanup_old_bottlenecks(self):
        """Clean up old bottleneck records"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get storage performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 operations
        
        # Calculate averages
        avg_latency = statistics.mean([m.latency_ms for m in recent_metrics])
        avg_throughput = statistics.mean([m.throughput_mbps for m in recent_metrics])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        
        # Get storage type breakdown
        storage_breakdown = defaultdict(list)
        for metric in recent_metrics:
            storage_breakdown[metric.storage_type.value].append(metric)
        
        return {
            "overall_performance": {
                "average_latency_ms": avg_latency,
                "average_throughput_mbps": avg_throughput,
                "success_rate_percent": success_rate,
                "total_operations": len(recent_metrics)
            },
            "storage_breakdown": {
                storage_type: {
                    "count": len(metrics),
                    "avg_latency_ms": statistics.mean([m.latency_ms for m in metrics]),
                    "avg_throughput_mbps": statistics.mean([m.throughput_mbps for m in metrics])
                }
                for storage_type, metrics in storage_breakdown.items()
            },
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "storage_type": b.storage_type.value,
                "location": b.location.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]


class StorageProfiler:
    """Simplified storage profiler interface"""
    
    def __init__(self):
        self.profiler = StorageIOProfiler()
    
    async def start_monitoring(self):
        """Start storage monitoring"""
        return await self.profiler.start_monitoring()
    
    async def stop_monitoring(self):
        """Stop storage monitoring"""
        return await self.profiler.stop_monitoring()
    
    async def profile_file_operation(self, 
                                   operation_type: str,
                                   file_path: str,
                                   operation_func: Callable,
                                   *args, **kwargs):
        """Profile a file operation"""
        # Convert string to enum
        op_type = IOOperationType(operation_type.lower())
        
        # Determine storage type based on file path
        storage_type = self._determine_storage_type(file_path)
        
        # Determine location based on file path
        location = self._determine_location(file_path)
        
        # Create file metadata
        file_metadata = self._create_file_metadata(file_path)
        
        return await self.profiler.profile_storage_operation(
            op_type, storage_type, location, file_metadata, operation_func, *args, **kwargs
        )
    
    def _determine_storage_type(self, file_path: str) -> StorageType:
        """Determine storage type from file path"""
        if file_path.startswith(('s3://', 'https://s3')):
            return StorageType.S3_CLOUD
        elif file_path.startswith('https://'):
            return StorageType.CDN
        elif '/tmp/' in file_path:
            return StorageType.LOCAL_DISK
        else:
            return StorageType.LOCAL_DISK
    
    def _determine_location(self, file_path: str) -> StorageLocation:
        """Determine storage location from file path"""
        if 'creator' in file_path.lower():
            return StorageLocation.CREATOR_CONTENT
        elif 'cache' in file_path.lower():
            return StorageLocation.CACHE_DATA
        elif 'log' in file_path.lower():
            return StorageLocation.SYSTEM_LOGS
        elif 'tmp' in file_path.lower():
            return StorageLocation.TEMP_FILES
        else:
            return StorageLocation.USER_DATA
    
    def _create_file_metadata(self, file_path: str) -> FileMetadata:
        """Create file metadata from file path"""
        try:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_type = Path(file_path).suffix
            return FileMetadata(
                file_path=file_path,
                file_size=file_size,
                file_type=file_type
            )
        except Exception:
            return FileMetadata(
                file_path=file_path,
                file_size=0,
                file_type=""
            )


def create_storage_io_profiler(
    monitoring_interval: float = 1.0,
    enable_file_tracking: bool = True,
    enable_cloud_monitoring: bool = True,
    start_monitoring: bool = False
) -> StorageIOProfiler:
    """
    Factory function to create storage I/O profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_file_tracking: Enable detailed file operation tracking
        enable_cloud_monitoring: Enable cloud storage monitoring
        start_monitoring: Start monitoring immediately
    
    Returns:
        StorageIOProfiler: Configured storage profiler instance
    """
    profiler = StorageIOProfiler(
        monitoring_interval=monitoring_interval,
        enable_file_tracking=enable_file_tracking,
        enable_cloud_monitoring=enable_cloud_monitoring
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_creator_content_profiling():
    """Example of profiling creator content operations"""
    profiler = create_storage_io_profiler(start_monitoring=True)
    
    # Example: Profile video upload operation
    async def upload_video(file_path: str, destination: str):
        # Simulate video upload
        await asyncio.sleep(0.1)
        return f"Uploaded {file_path} to {destination}"
    
    file_metadata = FileMetadata(
        file_path="/tmp/creator_video.mp4",
        file_size=50 * 1024 * 1024,  # 50MB
        file_type=".mp4",
        content_type="video/mp4",
        creator_id="creator_123"
    )
    
    metrics = await profiler.profile_storage_operation(
        IOOperationType.UPLOAD,
        StorageType.S3_CLOUD,
        StorageLocation.CREATOR_CONTENT,
        file_metadata,
        upload_video,
        "/tmp/creator_video.mp4",
        "s3://ainflue-content/videos/"
    )
    
    print(f"Upload profiling completed:")
    print(f"- Latency: {metrics.latency_ms:.2f}ms")
    print(f"- Throughput: {metrics.throughput_mbps:.2f} MB/s")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_creator_content_profiling())