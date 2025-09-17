"""⚡ Storage I/O Profiling System
================================

Advanced storage I/O performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for disk operations, cloud storage, and file system performance.

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
import psutil
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Try to import boto3 for S3 profiling
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    logger.warning("boto3 not available, S3 profiling disabled")

# Try to import azure storage for Azure profiling
try:
    from azure.storage.blob import BlobServiceClient
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False

# Try to import google cloud storage
try:
    from google.cloud import storage as gcs
    HAS_GCS = True
except ImportError:
    HAS_GCS = False


class StorageType(Enum):
    """Types of storage systems"""
    LOCAL_DISK = "local_disk"
    NETWORK_STORAGE = "network_storage"
    S3_COMPATIBLE = "s3_compatible"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    REDIS_STORAGE = "redis_storage"
    DATABASE_STORAGE = "database_storage"


class IOOperation(Enum):
    """Types of I/O operations"""
    READ = "read"
    WRITE = "write" 
    DELETE = "delete"
    LIST = "list"
    COPY = "copy"
    MOVE = "move"
    SYNC = "sync"
    BACKUP = "backup"


class StorageMetrics(Enum):
    """Storage performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    IOPS = "iops"
    BANDWIDTH = "bandwidth"
    QUEUE_DEPTH = "queue_depth"
    ERROR_RATE = "error_rate"


@dataclass
class StorageMetadata:
    """Metadata for storage operations"""
    file_path: str
    file_size: int
    operation: IOOperation
    storage_type: StorageType
    content_type: Optional[str] = None
    compression: Optional[str] = None
    encryption: bool = False
    cache_hit: bool = False


@dataclass
class IOMetrics:
    """Storage I/O performance metrics"""
    operation_id: str
    storage_type: StorageType
    operation: IOOperation
    file_size: int
    latency_ms: float
    throughput_mbps: float
    iops: float
    bandwidth_usage: float
    queue_depth: int
    error_count: int
    cache_hit_rate: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageBottleneck:
    """Storage bottleneck information"""
    bottleneck_type: str
    severity: str
    storage_type: StorageType
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class StorageIOProfiler:
    """
    Storage I/O performance profiler for Creator Economy content storage
    """
    
    def __init__(self, 
                 monitoring_interval: float = 1.0,
                 max_history_size: int = 50000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.io_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.current_operations: Dict[str, Dict] = {}
        
        # Performance thresholds
        self.thresholds = {
            'slow_io_threshold': 1000.0,  # 1 second
            'high_latency_threshold': 500.0,  # 500ms
            'low_throughput_threshold': 10.0,  # 10 MB/s
            'high_error_rate_threshold': 5.0,  # 5%
            'queue_depth_threshold': 50
        }
        
        # Storage clients cache
        self.storage_clients = {}
        self._init_storage_clients()
        
        logger.info("StorageIOProfiler initialized")

    def _init_storage_clients(self):
        """Initialize storage clients"""
        try:
            # Initialize S3 client if available
            if HAS_BOTO3:
                self.storage_clients['s3'] = boto3.client('s3')
            
            # Initialize Azure client if available
            if HAS_AZURE:
                # Placeholder - would need connection string
                pass
            
            # Initialize GCS client if available  
            if HAS_GCS:
                # Placeholder - would need credentials
                pass
                
        except Exception as e:
            logger.warning(f"Error initializing storage clients: {e}")

    def start_monitoring(self):
        """Start background storage monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Storage I/O monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Storage I/O monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_system_io_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in storage monitoring loop: {e}")

    def _collect_system_io_metrics(self):
        """Collect system-wide I/O metrics"""
        try:
            # Get disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics = IOMetrics(
                    operation_id=f"system_io_{int(time.time())}",
                    storage_type=StorageType.LOCAL_DISK,
                    operation=IOOperation.READ,  # Mixed operation
                    file_size=0,
                    latency_ms=0.0,
                    throughput_mbps=0.0,
                    iops=disk_io.read_count + disk_io.write_count,
                    bandwidth_usage=(disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024,
                    queue_depth=0,
                    error_count=0,
                    cache_hit_rate=0.0,
                    timestamp=datetime.utcnow(),
                    metadata={
                        'read_count': disk_io.read_count,
                        'write_count': disk_io.write_count,
                        'read_bytes': disk_io.read_bytes,
                        'write_bytes': disk_io.write_bytes,
                        'read_time': disk_io.read_time,
                        'write_time': disk_io.write_time
                    }
                )
                self.io_metrics_history.append(metrics)
                
        except Exception as e:
            logger.error(f"Error collecting system I/O metrics: {e}")

    def profile_file_operation(self, 
                             file_path: str,
                             operation: IOOperation,
                             storage_type: StorageType = StorageType.LOCAL_DISK,
                             **kwargs) -> IOMetrics:
        """
        Profile a file operation
        
        Args:
            file_path: Path to the file
            operation: Type of operation
            storage_type: Type of storage system
            **kwargs: Additional operation parameters
            
        Returns:
            IOMetrics with profiling results
        """
        operation_id = f"{operation.value}_{file_path}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Get file size if applicable
            file_size = 0
            if operation in [IOOperation.READ, IOOperation.WRITE, IOOperation.COPY]:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                except:
                    pass
            
            # Track operation start
            self.current_operations[operation_id] = {
                'start_time': start_time,
                'file_path': file_path,
                'operation': operation,
                'storage_type': storage_type
            }
            
            # Perform the actual operation profiling
            if storage_type == StorageType.LOCAL_DISK:
                result = self._profile_local_operation(file_path, operation, **kwargs)
            elif storage_type == StorageType.S3_COMPATIBLE:
                result = self._profile_s3_operation(file_path, operation, **kwargs)
            else:
                result = self._profile_generic_operation(file_path, operation, **kwargs)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Calculate throughput
            throughput_mbps = 0.0
            if file_size > 0 and latency_ms > 0:
                throughput_mbps = (file_size / 1024 / 1024) / (latency_ms / 1000)
            
            # Create metrics
            metrics = IOMetrics(
                operation_id=operation_id,
                storage_type=storage_type,
                operation=operation,
                file_size=file_size,
                latency_ms=latency_ms,
                throughput_mbps=throughput_mbps,
                iops=1.0 / (latency_ms / 1000) if latency_ms > 0 else 0.0,
                bandwidth_usage=throughput_mbps,
                queue_depth=len(self.current_operations),
                error_count=1 if result.get('error') else 0,
                cache_hit_rate=result.get('cache_hit_rate', 0.0),
                timestamp=datetime.utcnow(),
                metadata=result
            )
            
            # Store metrics
            self.io_metrics_history.append(metrics)
            
            # Check for bottlenecks
            self._analyze_bottlenecks(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error profiling storage operation: {e}")
            raise
        finally:
            # Remove from current operations
            self.current_operations.pop(operation_id, None)

    def _profile_local_operation(self, file_path: str, operation: IOOperation, **kwargs) -> Dict:
        """Profile local disk operation"""
        result = {'error': False}
        
        try:
            if operation == IOOperation.READ:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        result['bytes_read'] = len(data)
                else:
                    result['error'] = True
                    
            elif operation == IOOperation.WRITE:
                data = kwargs.get('data', b'')
                with open(file_path, 'wb') as f:
                    f.write(data)
                    result['bytes_written'] = len(data)
                    
            elif operation == IOOperation.DELETE:
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    result['error'] = True
                    
            elif operation == IOOperation.LIST:
                if os.path.isdir(file_path):
                    files = os.listdir(file_path)
                    result['files_count'] = len(files)
                else:
                    result['error'] = True
                    
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
            
        return result

    def _profile_s3_operation(self, file_path: str, operation: IOOperation, **kwargs) -> Dict:
        """Profile S3 operation"""
        result = {'error': False}
        
        if not HAS_BOTO3 or 's3' not in self.storage_clients:
            result['error'] = True
            result['error_message'] = "S3 client not available"
            return result
            
        try:
            s3_client = self.storage_clients['s3']
            bucket = kwargs.get('bucket')
            key = kwargs.get('key', file_path)
            
            if not bucket:
                result['error'] = True
                result['error_message'] = "Bucket not specified"
                return result
            
            if operation == IOOperation.READ:
                response = s3_client.get_object(Bucket=bucket, Key=key)
                data = response['Body'].read()
                result['bytes_read'] = len(data)
                
            elif operation == IOOperation.WRITE:
                data = kwargs.get('data', b'')
                s3_client.put_object(Bucket=bucket, Key=key, Body=data)
                result['bytes_written'] = len(data)
                
            elif operation == IOOperation.DELETE:
                s3_client.delete_object(Bucket=bucket, Key=key)
                
            elif operation == IOOperation.LIST:
                response = s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
                result['objects_count'] = response.get('KeyCount', 0)
                
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
            
        return result

    def _profile_generic_operation(self, file_path: str, operation: IOOperation, **kwargs) -> Dict:
        """Profile generic storage operation"""
        return {'error': False, 'operation_type': 'generic'}

    def _analyze_bottlenecks(self, metrics: IOMetrics):
        """Analyze storage bottlenecks"""
        bottlenecks = []
        
        # Check latency
        if metrics.latency_ms > self.thresholds['slow_io_threshold']:
            bottlenecks.append(StorageBottleneck(
                bottleneck_type="high_latency",
                severity="high" if metrics.latency_ms > 2000 else "medium",
                storage_type=metrics.storage_type,
                description=f"Storage operation latency too high: {metrics.latency_ms:.1f}ms",
                impact="Affects content upload/download performance",
                recommendations=[
                    "Check storage infrastructure",
                    "Consider caching strategy",
                    "Optimize file sizes",
                    "Use compression"
                ],
                detected_at=datetime.utcnow(),
                metrics={'latency_ms': metrics.latency_ms}
            ))
        
        # Check throughput
        if metrics.throughput_mbps < self.thresholds['low_throughput_threshold']:
            bottlenecks.append(StorageBottleneck(
                bottleneck_type="low_throughput",
                severity="medium",
                storage_type=metrics.storage_type,
                description=f"Storage throughput too low: {metrics.throughput_mbps:.1f}MB/s",
                impact="Slow content processing and delivery",
                recommendations=[
                    "Upgrade storage infrastructure",
                    "Implement parallel uploads",
                    "Use CDN for content delivery",
                    "Optimize network configuration"
                ],
                detected_at=datetime.utcnow(),
                metrics={'throughput_mbps': metrics.throughput_mbps}
            ))
        
        # Check queue depth
        if metrics.queue_depth > self.thresholds['queue_depth_threshold']:
            bottlenecks.append(StorageBottleneck(
                bottleneck_type="high_queue_depth",
                severity="high",
                storage_type=metrics.storage_type,
                description=f"Storage queue depth too high: {metrics.queue_depth}",
                impact="Storage operations backing up",
                recommendations=[
                    "Scale storage workers",
                    "Implement queue management",
                    "Optimize operation batching",
                    "Add load balancing"
                ],
                detected_at=datetime.utcnow(),
                metrics={'queue_depth': metrics.queue_depth}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get storage performance summary"""
        if not self.io_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.io_metrics_history)[-1000:]  # Last 1000 operations
        
        # Calculate statistics
        latencies = [m.latency_ms for m in recent_metrics]
        throughputs = [m.throughput_mbps for m in recent_metrics if m.throughput_mbps > 0]
        error_count = sum(1 for m in recent_metrics if m.error_count > 0)
        
        return {
            "summary": {
                "total_operations": len(recent_metrics),
                "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
                "p95_latency_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0,
                "avg_throughput_mbps": statistics.mean(throughputs) if throughputs else 0,
                "error_rate": (error_count / len(recent_metrics)) * 100,
                "active_operations": len(self.current_operations)
            },
            "by_storage_type": self._get_metrics_by_storage_type(),
            "by_operation": self._get_metrics_by_operation(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_optimization_recommendations()
        }

    def _get_metrics_by_storage_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by storage type"""
        metrics_by_type = defaultdict(list)
        
        for metrics in list(self.io_metrics_history)[-1000:]:
            metrics_by_type[metrics.storage_type.value].append(metrics)
        
        result = {}
        for storage_type, metrics_list in metrics_by_type.items():
            latencies = [m.latency_ms for m in metrics_list]
            throughputs = [m.throughput_mbps for m in metrics_list if m.throughput_mbps > 0]
            
            result[storage_type] = {
                "operations": len(metrics_list),
                "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
                "avg_throughput_mbps": statistics.mean(throughputs) if throughputs else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_operation(self) -> Dict[str, Dict]:
        """Get metrics grouped by operation type"""
        metrics_by_op = defaultdict(list)
        
        for metrics in list(self.io_metrics_history)[-1000:]:
            metrics_by_op[metrics.operation.value].append(metrics)
        
        result = {}
        for operation, metrics_list in metrics_by_op.items():
            latencies = [m.latency_ms for m in metrics_list]
            throughputs = [m.throughput_mbps for m in metrics_list if m.throughput_mbps > 0]
            
            result[operation] = {
                "operations": len(metrics_list),
                "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
                "avg_throughput_mbps": statistics.mean(throughputs) if throughputs else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        if not self.io_metrics_history:
            return ["Start profiling storage operations to get recommendations"]
        
        recent_metrics = list(self.io_metrics_history)[-100:]
        avg_latency = statistics.mean([m.latency_ms for m in recent_metrics])
        avg_throughput = statistics.mean([m.throughput_mbps for m in recent_metrics if m.throughput_mbps > 0])
        error_rate = (sum(1 for m in recent_metrics if m.error_count > 0) / len(recent_metrics)) * 100
        
        if avg_latency > 500:
            recommendations.append("High latency detected - consider caching strategy")
        if avg_throughput < 50:
            recommendations.append("Low throughput - consider storage infrastructure upgrade")
        if error_rate > 1:
            recommendations.append("High error rate - check storage health and connectivity")
        if len(self.current_operations) > 20:
            recommendations.append("High concurrent operations - consider scaling storage workers")
        
        if not recommendations:
            recommendations.append("Storage performance is optimal")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[StorageBottleneck]:
        """Get recent storage bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def export_metrics(self, format: str = "json") -> str:
        """Export storage metrics"""
        data = {
            "storage_io_metrics": [
                {
                    "operation_id": m.operation_id,
                    "storage_type": m.storage_type.value,
                    "operation": m.operation.value,
                    "file_size": m.file_size,
                    "latency_ms": m.latency_ms,
                    "throughput_mbps": m.throughput_mbps,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.io_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "storage_type": b.storage_type.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ]
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_storage_io_profiler(monitoring_interval: float = 1.0,
                             max_history_size: int = 50000,
                             start_monitoring: bool = True) -> StorageIOProfiler:
    """
    Create and configure a storage I/O profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured StorageIOProfiler instance
    """
    profiler = StorageIOProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_storage_io_profiler()
    
    try:
        # Example: Profile a file read operation
        import tempfile
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content for storage profiling")
            test_file = f.name
        
        # Profile read operation
        metrics = profiler.profile_file_operation(
            test_file, 
            IOOperation.READ,
            StorageType.LOCAL_DISK
        )
        
        print(f"Read operation latency: {metrics.latency_ms:.2f}ms")
        print(f"Throughput: {metrics.throughput_mbps:.2f}MB/s")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"Performance summary: {json.dumps(summary, indent=2)}")
        
        # Clean up
        os.unlink(test_file)
        
    finally:
        profiler.stop_monitoring()