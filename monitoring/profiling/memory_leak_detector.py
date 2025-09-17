"""🔍 Memory Leak Detector
=======================

Advanced memory leak detection system for the Ainflue Creator Economy platform.
Monitors memory allocation patterns, detects leaks, and provides automated cleanup.

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
import gc
import logging
import threading
import time
import tracemalloc
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import weakref
import sys

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class LeakType(Enum):
    """Types of memory leaks"""
    GRADUAL_LEAK = "gradual_leak"
    SUDDEN_SPIKE = "sudden_spike"
    CYCLIC_REFERENCE = "cyclic_reference"
    UNCLOSED_RESOURCE = "unclosed_resource"
    CACHE_BLOAT = "cache_bloat"
    EVENT_LISTENER_LEAK = "event_listener_leak"
    THREAD_LEAK = "thread_leak"
    FILE_HANDLE_LEAK = "file_handle_leak"


class MemoryComponent(Enum):
    """Memory components to monitor"""
    HEAP = "heap"
    STACK = "stack"
    CACHE = "cache"
    BUFFER = "buffer"
    THREAD_LOCAL = "thread_local"
    GLOBAL_VARS = "global_vars"
    EXTERNAL_LIBS = "external_libs"


class LeakSeverity(Enum):
    """Memory leak severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemoryAllocation:
    """Memory allocation record"""
    allocation_id: str
    size_bytes: int
    filename: str
    line_number: int
    function_name: str
    
    # Object information
    object_type: str
    object_repr: Optional[str] = None
    
    # Timing
    allocated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    
    # Tracking
    reference_count: int = 1
    is_tracked: bool = True
    
    # Tags for categorization
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""
    snapshot_id: str
    timestamp: datetime
    
    # Memory usage
    total_memory_mb: float
    heap_memory_mb: float
    stack_memory_mb: float
    
    # Object counts
    total_objects: int
    new_objects: int
    released_objects: int
    
    # Top allocations
    top_allocations: List[MemoryAllocation]
    
    # Garbage collection stats
    gc_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryLeak:
    """Detected memory leak"""
    leak_id: str
    leak_type: LeakType
    component: MemoryComponent
    severity: LeakSeverity
    
    # Leak characteristics
    description: str
    growth_rate_mb_per_hour: float
    total_leaked_mb: float
    
    # Source information
    source_file: str
    source_function: str
    source_line: int
    
    # Object details
    leaked_objects: List[str]
    object_types: Dict[str, int]
    
    # Detection details
    detection_confidence: float  # 0-1
    first_detected: datetime
    last_detected: datetime
    
    # Impact analysis
    performance_impact: Dict[str, float]
    stability_risk: str  # low, medium, high, critical
    
    # Recommendations
    fix_recommendations: List[str]
    prevention_strategies: List[str]
    
    # Cleanup
    auto_cleanup_possible: bool = False
    cleanup_performed: bool = False
    cleanup_timestamp: Optional[datetime] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ObjectTracker:
    """Object lifecycle tracker"""
    object_id: str
    object_type: str
    creation_time: datetime
    
    # Reference tracking
    reference_count: int = 1
    weak_references: Set[weakref.ref] = field(default_factory=set)
    
    # Access patterns
    access_count: int = 0
    last_access: Optional[datetime] = None
    
    # Memory usage
    estimated_size_bytes: int = 0
    
    # Lifecycle flags
    is_alive: bool = True
    marked_for_cleanup: bool = False


class MemoryLeakDetector:
    """Advanced memory leak detection system"""
    
    def __init__(self,
                 monitoring_interval_seconds: float = 30.0,
                 snapshot_interval_seconds: float = 300.0,
                 max_snapshots: int = 100,
                 enable_object_tracking: bool = True,
                 enable_auto_cleanup: bool = False,
                 leak_threshold_mb: float = 10.0):
        """
        Initialize memory leak detector
        
        Args:
            monitoring_interval_seconds: Monitoring interval
            snapshot_interval_seconds: Memory snapshot interval
            max_snapshots: Maximum number of snapshots to keep
            enable_object_tracking: Enable detailed object tracking
            enable_auto_cleanup: Enable automatic cleanup of detected leaks
            leak_threshold_mb: Threshold for leak detection in MB
        """
        self.monitoring_interval = monitoring_interval_seconds
        self.snapshot_interval = snapshot_interval_seconds
        self.max_snapshots = max_snapshots
        self.enable_object_tracking = enable_object_tracking
        self.enable_auto_cleanup = enable_auto_cleanup
        self.leak_threshold_mb = leak_threshold_mb
        
        # Memory tracking
        self.memory_snapshots: deque = deque(maxlen=max_snapshots)
        self.current_allocations: Dict[str, MemoryAllocation] = {}
        self.detected_leaks: List[MemoryLeak] = []
        
        # Object tracking
        self.tracked_objects: Dict[str, ObjectTracker] = {}
        self.object_creation_patterns: Dict[str, List[datetime]] = defaultdict(list)
        
        # Leak detection state
        self.baseline_memory_mb: Optional[float] = None
        self.memory_trend: List[float] = []
        self.gc_forced_count: int = 0
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.snapshot_task: Optional[asyncio.Task] = None
        
        # Tracemalloc state
        self.tracemalloc_enabled = False
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("MemoryLeakDetector initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'memory_usage_mb': Gauge(
                'ainflue_memory_usage_mb',
                'Memory usage in MB',
                ['component', 'type']
            ),
            'memory_leaks_detected': Counter(
                'ainflue_memory_leaks_detected_total',
                'Total memory leaks detected',
                ['leak_type', 'severity']
            ),
            'memory_objects_tracked': Gauge(
                'ainflue_memory_objects_tracked',
                'Number of tracked objects',
                ['object_type']
            ),
            'memory_gc_collections': Counter(
                'ainflue_memory_gc_collections_total',
                'Total garbage collections performed',
                ['generation']
            ),
            'memory_leak_cleanup': Counter(
                'ainflue_memory_leak_cleanup_total',
                'Total memory leak cleanups performed',
                ['leak_type', 'success']
            )
        }
    
    async def start_monitoring(self):
        """Start memory leak monitoring"""
        if self.is_monitoring:
            logger.warning("Memory leak monitoring already running")
            return
        
        # Enable tracemalloc
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self.tracemalloc_enabled = True
            logger.info("Tracemalloc enabled for memory tracking")
        
        self.is_monitoring = True
        
        # Start monitoring tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.snapshot_task = asyncio.create_task(self._snapshot_loop())
        
        # Take initial baseline
        await self._take_memory_snapshot()
        
        logger.info("Memory leak monitoring started")
    
    async def stop_monitoring(self):
        """Stop memory leak monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        # Cancel tasks
        for task in [self.monitoring_task, self.snapshot_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Disable tracemalloc if we enabled it
        if self.tracemalloc_enabled and tracemalloc.is_tracing():
            tracemalloc.stop()
            self.tracemalloc_enabled = False
        
        logger.info("Memory leak monitoring stopped")
    
    async def track_object(self, obj: Any, object_type: str, tags: Optional[Dict[str, str]] = None):
        """Track an object for memory leak detection"""
        if not self.enable_object_tracking:
            return
        
        try:
            object_id = f"{object_type}_{id(obj)}"
            
            tracker = ObjectTracker(
                object_id=object_id,
                object_type=object_type,
                creation_time=datetime.utcnow(),
                estimated_size_bytes=sys.getsizeof(obj)
            )
            
            # Create weak reference to avoid keeping object alive
            def cleanup_callback(ref):
                self._object_cleanup_callback(object_id)
            
            weak_ref = weakref.ref(obj, cleanup_callback)
            tracker.weak_references.add(weak_ref)
            
            with self._lock:
                self.tracked_objects[object_id] = tracker
                self.object_creation_patterns[object_type].append(datetime.utcnow())
            
            # Update Prometheus metrics
            self.prometheus_metrics['memory_objects_tracked'].labels(
                object_type=object_type
            ).inc()
            
        except Exception as e:
            logger.warning(f"Failed to track object {object_type}: {e}")
    
    def _object_cleanup_callback(self, object_id: str):
        """Callback when tracked object is garbage collected"""
        with self._lock:
            if object_id in self.tracked_objects:
                tracker = self.tracked_objects[object_id]
                tracker.is_alive = False
                
                # Update Prometheus metrics
                self.prometheus_metrics['memory_objects_tracked'].labels(
                    object_type=tracker.object_type
                ).dec()
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Analyze memory trends
                await self._analyze_memory_trends()
                
                # Detect memory leaks
                await self._detect_memory_leaks()
                
                # Perform cleanup if enabled
                if self.enable_auto_cleanup:
                    await self._perform_automatic_cleanup()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _snapshot_loop(self):
        """Background snapshot loop"""
        while self.is_monitoring:
            try:
                await self._take_memory_snapshot()
                await asyncio.sleep(self.snapshot_interval)
                
            except Exception as e:
                logger.error(f"Error in snapshot loop: {e}")
                await asyncio.sleep(self.snapshot_interval)
    
    async def _take_memory_snapshot(self):
        """Take a memory usage snapshot"""
        try:
            import psutil
            
            # Get current process
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Get tracemalloc statistics
            top_allocations = []
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                
                # Get top allocations
                stats = tracemalloc.take_snapshot().statistics('lineno')
                for index, stat in enumerate(stats[:10]):  # Top 10
                    allocation = MemoryAllocation(
                        allocation_id=f"alloc_{index}_{int(time.time())}",
                        size_bytes=stat.size,
                        filename=stat.traceback.format()[0].split(',')[0],
                        line_number=0,  # Simplified
                        function_name="unknown",
                        object_type="memory_block"
                    )
                    top_allocations.append(allocation)
            
            # Get garbage collection stats
            gc_stats = {
                "collections": gc.get_stats(),
                "count": gc.get_count(),
                "threshold": gc.get_threshold()
            }
            
            # Create snapshot
            snapshot = MemorySnapshot(
                snapshot_id=f"snapshot_{int(time.time())}",
                timestamp=datetime.utcnow(),
                total_memory_mb=memory_info.rss / (1024 * 1024),
                heap_memory_mb=memory_info.rss / (1024 * 1024),  # Simplified
                stack_memory_mb=0.0,  # Simplified
                total_objects=len(gc.get_objects()),
                new_objects=0,  # Would be calculated from previous snapshot
                released_objects=0,  # Would be calculated from previous snapshot
                top_allocations=top_allocations,
                gc_stats=gc_stats
            )
            
            # Store snapshot
            with self._lock:
                self.memory_snapshots.append(snapshot)
                
                # Update memory trend
                self.memory_trend.append(snapshot.total_memory_mb)
                if len(self.memory_trend) > 100:  # Keep last 100 points
                    self.memory_trend = self.memory_trend[-100:]
                
                # Set baseline if not set
                if self.baseline_memory_mb is None:
                    self.baseline_memory_mb = snapshot.total_memory_mb
            
            # Update Prometheus metrics
            self.prometheus_metrics['memory_usage_mb'].labels(
                component='system',
                type='total'
            ).set(snapshot.total_memory_mb)
            
            self.prometheus_metrics['memory_usage_mb'].labels(
                component='system',
                type='heap'
            ).set(snapshot.heap_memory_mb)
            
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
        except Exception as e:
            logger.error(f"Error taking memory snapshot: {e}")
    
    async def _analyze_memory_trends(self):
        """Analyze memory usage trends"""
        if len(self.memory_trend) < 10:  # Need enough data points
            return
        
        try:
            # Calculate trend
            recent_trend = self.memory_trend[-10:]  # Last 10 points
            
            # Simple linear regression
            n = len(recent_trend)
            x_vals = list(range(n))
            y_vals = recent_trend
            
            x_mean = sum(x_vals) / n
            y_mean = sum(y_vals) / n
            
            numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
            denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                
                # Check for concerning trends
                if slope > 1.0:  # Memory increasing > 1MB per interval
                    logger.warning(f"Memory trend shows increasing usage: {slope:.2f} MB per interval")
                
                # Calculate growth rate
                if len(self.memory_trend) >= 2:
                    current_memory = self.memory_trend[-1]
                    previous_memory = self.memory_trend[-2]
                    
                    if self.baseline_memory_mb:
                        growth_from_baseline = current_memory - self.baseline_memory_mb
                        
                        if growth_from_baseline > self.leak_threshold_mb:
                            logger.warning(f"Memory usage increased by {growth_from_baseline:.2f} MB from baseline")
        
        except Exception as e:
            logger.error(f"Error analyzing memory trends: {e}")
    
    async def _detect_memory_leaks(self):
        """Detect memory leaks based on patterns"""
        if len(self.memory_snapshots) < 3:  # Need at least 3 snapshots
            return
        
        try:
            recent_snapshots = list(self.memory_snapshots)[-3:]
            
            # Check for gradual memory leak
            memory_values = [s.total_memory_mb for s in recent_snapshots]
            
            if all(memory_values[i] < memory_values[i+1] for i in range(len(memory_values)-1)):
                # Memory consistently increasing
                growth_rate = (memory_values[-1] - memory_values[0]) / len(memory_values)
                
                if growth_rate > 0.5:  # > 0.5 MB per snapshot
                    leak = MemoryLeak(
                        leak_id=f"leak_{int(time.time())}",
                        leak_type=LeakType.GRADUAL_LEAK,
                        component=MemoryComponent.HEAP,
                        severity=self._calculate_leak_severity(growth_rate),
                        description=f"Gradual memory leak detected: {growth_rate:.2f} MB growth per snapshot",
                        growth_rate_mb_per_hour=growth_rate * (3600 / self.snapshot_interval),
                        total_leaked_mb=memory_values[-1] - memory_values[0],
                        source_file="unknown",
                        source_function="unknown",
                        source_line=0,
                        leaked_objects=[],
                        object_types={},
                        detection_confidence=0.8,
                        first_detected=recent_snapshots[0].timestamp,
                        last_detected=recent_snapshots[-1].timestamp,
                        performance_impact={"memory_pressure": growth_rate},
                        stability_risk="medium",
                        fix_recommendations=[
                            "Review recent code changes for unclosed resources",
                            "Check for circular references",
                            "Monitor object creation patterns",
                            "Consider forced garbage collection"
                        ],
                        prevention_strategies=[
                            "Implement proper resource cleanup",
                            "Use context managers for resource handling",
                            "Regular memory profiling",
                            "Code review focus on resource management"
                        ],
                        auto_cleanup_possible=True
                    )
                    
                    self.detected_leaks.append(leak)
                    
                    # Update Prometheus metrics
                    self.prometheus_metrics['memory_leaks_detected'].labels(
                        leak_type=leak.leak_type.value,
                        severity=leak.severity.value
                    ).inc()
                    
                    logger.warning(f"Memory leak detected: {leak.description}")
            
            # Check for object count leaks
            await self._detect_object_leaks()
            
        except Exception as e:
            logger.error(f"Error detecting memory leaks: {e}")
    
    async def _detect_object_leaks(self):
        """Detect object-specific memory leaks"""
        if not self.enable_object_tracking:
            return
        
        try:
            current_time = datetime.utcnow()
            
            # Group objects by type
            object_counts = defaultdict(int)
            old_objects = defaultdict(list)
            
            with self._lock:
                for obj_id, tracker in self.tracked_objects.items():
                    if tracker.is_alive:
                        object_counts[tracker.object_type] += 1
                        
                        # Check for old objects that haven't been accessed
                        if tracker.last_access:
                            age = current_time - tracker.last_access
                            if age > timedelta(hours=1):  # Object not accessed for 1 hour
                                old_objects[tracker.object_type].append(obj_id)
            
            # Check for excessive object counts
            for object_type, count in object_counts.items():
                if count > 1000:  # Threshold for suspicious object count
                    leak = MemoryLeak(
                        leak_id=f"object_leak_{int(time.time())}",
                        leak_type=LeakType.CACHE_BLOAT,
                        component=MemoryComponent.CACHE,
                        severity=LeakSeverity.MEDIUM,
                        description=f"Excessive {object_type} objects: {count}",
                        growth_rate_mb_per_hour=0.0,  # Would be calculated
                        total_leaked_mb=0.0,  # Would be calculated
                        source_file="unknown",
                        source_function="unknown",
                        source_line=0,
                        leaked_objects=old_objects.get(object_type, []),
                        object_types={object_type: count},
                        detection_confidence=0.7,
                        first_detected=current_time,
                        last_detected=current_time,
                        performance_impact={"object_count": count},
                        stability_risk="medium",
                        fix_recommendations=[
                            f"Review {object_type} lifecycle management",
                            "Implement object pooling",
                            "Add cleanup mechanisms",
                            "Set object count limits"
                        ],
                        prevention_strategies=[
                            "Implement proper object cleanup",
                            "Use weak references where appropriate",
                            "Monitor object creation patterns",
                            "Regular object audits"
                        ],
                        auto_cleanup_possible=len(old_objects.get(object_type, [])) > 0
                    )
                    
                    self.detected_leaks.append(leak)
                    logger.warning(f"Object leak detected: {leak.description}")
        
        except Exception as e:
            logger.error(f"Error detecting object leaks: {e}")
    
    def _calculate_leak_severity(self, growth_rate_mb: float) -> LeakSeverity:
        """Calculate leak severity based on growth rate"""
        if growth_rate_mb < 1.0:
            return LeakSeverity.LOW
        elif growth_rate_mb < 5.0:
            return LeakSeverity.MEDIUM
        elif growth_rate_mb < 20.0:
            return LeakSeverity.HIGH
        else:
            return LeakSeverity.CRITICAL
    
    async def _perform_automatic_cleanup(self):
        """Perform automatic cleanup of detected leaks"""
        for leak in self.detected_leaks:
            if leak.auto_cleanup_possible and not leak.cleanup_performed:
                try:
                    success = await self._cleanup_leak(leak)
                    
                    leak.cleanup_performed = True
                    leak.cleanup_timestamp = datetime.utcnow()
                    
                    # Update Prometheus metrics
                    self.prometheus_metrics['memory_leak_cleanup'].labels(
                        leak_type=leak.leak_type.value,
                        success=str(success).lower()
                    ).inc()
                    
                    if success:
                        logger.info(f"Successfully cleaned up leak: {leak.leak_id}")
                    else:
                        logger.warning(f"Failed to clean up leak: {leak.leak_id}")
                
                except Exception as e:
                    logger.error(f"Error during automatic cleanup of leak {leak.leak_id}: {e}")
    
    async def _cleanup_leak(self, leak: MemoryLeak) -> bool:
        """Clean up a specific memory leak"""
        try:
            if leak.leak_type == LeakType.GRADUAL_LEAK:
                # Force garbage collection
                collected = gc.collect()
                self.gc_forced_count += 1
                
                # Update GC metrics
                for generation in range(3):
                    self.prometheus_metrics['memory_gc_collections'].labels(
                        generation=str(generation)
                    ).inc()
                
                logger.info(f"Forced garbage collection, collected {collected} objects")
                return collected > 0
            
            elif leak.leak_type == LeakType.CACHE_BLOAT:
                # Clean up old objects
                cleaned_count = 0
                
                with self._lock:
                    for obj_id in leak.leaked_objects:
                        if obj_id in self.tracked_objects:
                            tracker = self.tracked_objects[obj_id]
                            tracker.marked_for_cleanup = True
                            cleaned_count += 1
                
                logger.info(f"Marked {cleaned_count} objects for cleanup")
                return cleaned_count > 0
            
            return False
            
        except Exception as e:
            logger.error(f"Error cleaning up leak {leak.leak_id}: {e}")
            return False
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=24)  # Keep 24 hours of data
        
        # Clean up old leaks
        self.detected_leaks = [
            leak for leak in self.detected_leaks
            if leak.timestamp > cutoff_time
        ]
        
        # Clean up old object trackers
        with self._lock:
            old_trackers = [
                obj_id for obj_id, tracker in self.tracked_objects.items()
                if not tracker.is_alive and tracker.creation_time < cutoff_time
            ]
            
            for obj_id in old_trackers:
                del self.tracked_objects[obj_id]
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics"""
        try:
            # Collect statistics before
            before_count = len(gc.get_objects())
            
            # Force collection
            collected = gc.collect()
            self.gc_forced_count += 1
            
            # Collect statistics after
            after_count = len(gc.get_objects())
            
            stats = {
                "objects_before": before_count,
                "objects_after": after_count,
                "objects_collected": collected,
                "objects_freed": before_count - after_count
            }
            
            logger.info(f"Forced garbage collection: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error during forced garbage collection: {e}")
            return {}
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report"""
        try:
            with self._lock:
                # Get current snapshot
                current_snapshot = self.memory_snapshots[-1] if self.memory_snapshots else None
                
                # Calculate trends
                memory_trend_summary = {}
                if len(self.memory_trend) >= 2:
                    current_memory = self.memory_trend[-1]
                    previous_memory = self.memory_trend[-2]
                    change = current_memory - previous_memory
                    
                    memory_trend_summary = {
                        "current_mb": current_memory,
                        "previous_mb": previous_memory,
                        "change_mb": change,
                        "trend": "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
                    }
                
                # Get object tracking summary
                object_summary = {}
                if self.enable_object_tracking:
                    alive_objects = defaultdict(int)
                    for tracker in self.tracked_objects.values():
                        if tracker.is_alive:
                            alive_objects[tracker.object_type] += 1
                    
                    object_summary = {
                        "total_tracked": len(self.tracked_objects),
                        "alive_objects": sum(alive_objects.values()),
                        "by_type": dict(alive_objects)
                    }
                
                return {
                    "current_snapshot": {
                        "timestamp": current_snapshot.timestamp.isoformat() if current_snapshot else None,
                        "total_memory_mb": current_snapshot.total_memory_mb if current_snapshot else 0,
                        "total_objects": current_snapshot.total_objects if current_snapshot else 0
                    } if current_snapshot else None,
                    "memory_trend": memory_trend_summary,
                    "baseline_memory_mb": self.baseline_memory_mb,
                    "detected_leaks": [
                        {
                            "id": leak.leak_id,
                            "type": leak.leak_type.value,
                            "severity": leak.severity.value,
                            "description": leak.description,
                            "growth_rate_mb_per_hour": leak.growth_rate_mb_per_hour,
                            "total_leaked_mb": leak.total_leaked_mb,
                            "first_detected": leak.first_detected.isoformat(),
                            "cleanup_performed": leak.cleanup_performed,
                            "recommendations": leak.fix_recommendations
                        }
                        for leak in self.detected_leaks
                    ],
                    "object_tracking": object_summary,
                    "gc_stats": {
                        "forced_collections": self.gc_forced_count,
                        "current_count": gc.get_count(),
                        "current_threshold": gc.get_threshold()
                    },
                    "monitoring_stats": {
                        "snapshots_taken": len(self.memory_snapshots),
                        "monitoring_active": self.is_monitoring,
                        "tracemalloc_enabled": tracemalloc.is_tracing()
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error generating memory report: {e}")
            return {"error": str(e)}


def create_memory_leak_detector(
    monitoring_interval_seconds: float = 30.0,
    snapshot_interval_seconds: float = 300.0,
    enable_object_tracking: bool = True,
    enable_auto_cleanup: bool = False,
    leak_threshold_mb: float = 10.0,
    start_monitoring: bool = False
) -> MemoryLeakDetector:
    """
    Factory function to create memory leak detector
    
    Args:
        monitoring_interval_seconds: Monitoring interval
        snapshot_interval_seconds: Memory snapshot interval
        enable_object_tracking: Enable detailed object tracking
        enable_auto_cleanup: Enable automatic cleanup
        leak_threshold_mb: Threshold for leak detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        MemoryLeakDetector: Configured memory leak detector instance
    """
    detector = MemoryLeakDetector(
        monitoring_interval_seconds=monitoring_interval_seconds,
        snapshot_interval_seconds=snapshot_interval_seconds,
        enable_object_tracking=enable_object_tracking,
        enable_auto_cleanup=enable_auto_cleanup,
        leak_threshold_mb=leak_threshold_mb
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(detector.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return detector


# Example usage for Creator Economy platform
async def example_memory_leak_detection():
    """Example of memory leak detection for Creator Economy"""
    detector = create_memory_leak_detector(
        monitoring_interval_seconds=5.0,
        snapshot_interval_seconds=10.0,
        enable_object_tracking=True,
        enable_auto_cleanup=True,
        start_monitoring=True
    )
    
    # Simulate object creation and potential leaks
    objects = []
    
    for i in range(100):
        # Create objects that might leak
        obj = {"data": f"content_{i}", "size": list(range(1000))}
        objects.append(obj)
        
        # Track some objects
        if i % 10 == 0:
            await detector.track_object(obj, "content_cache", {"creator_id": f"creator_{i//10}"})
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
    
    # Wait for monitoring to detect patterns
    await asyncio.sleep(15)
    
    # Get memory report
    report = detector.get_memory_report()
    
    print("Memory leak detection report:")
    print(f"- Current memory: {report['current_snapshot']['total_memory_mb']:.2f} MB" if report['current_snapshot'] else "- No snapshot available")
    print(f"- Baseline memory: {report['baseline_memory_mb']:.2f} MB" if report['baseline_memory_mb'] else "- No baseline set")
    print(f"- Detected leaks: {len(report['detected_leaks'])}")
    print(f"- Tracked objects: {report['object_tracking']['total_tracked']}" if 'object_tracking' in report else "- Object tracking disabled")
    print(f"- Forced GC count: {report['gc_stats']['forced_collections']}")
    
    print("\nDetected leaks:")
    for leak in report['detected_leaks']:
        print(f"- {leak['type']} ({leak['severity']}): {leak['description']}")
        print(f"  Growth rate: {leak['growth_rate_mb_per_hour']:.2f} MB/hour")
        print(f"  Cleanup performed: {leak['cleanup_performed']}")
    
    # Force garbage collection
    gc_stats = detector.force_garbage_collection()
    print(f"\nForced garbage collection: {gc_stats}")
    
    await detector.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_memory_leak_detection())