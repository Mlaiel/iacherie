"""⚡ Memory Leak Detection System
===============================

Advanced memory leak detection and analysis for the Ainflue Creator Platform.
Provides comprehensive memory profiling, leak pattern detection, and automated prevention.

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

import gc
import logging
import time
import threading
import tracemalloc
import weakref
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import psutil
import sys

logger = logging.getLogger(__name__)

# Try to import memory profiling libraries
try:
    import objgraph
    HAS_OBJGRAPH = True
except ImportError:
    HAS_OBJGRAPH = False
    logger.warning("objgraph not available, advanced object tracking disabled")

try:
    from pympler import tracker, muppy, summary
    HAS_PYMPLER = True
except ImportError:
    HAS_PYMPLER = False
    logger.warning("pympler not available, some memory analysis features disabled")


class LeakType(Enum):
    """Types of memory leaks"""
    REFERENCE_CYCLE = "reference_cycle"
    UNCLOSED_RESOURCE = "unclosed_resource"
    CACHE_OVERFLOW = "cache_overflow"
    EVENT_LISTENER = "event_listener"
    THREAD_LOCAL = "thread_local"
    CLOSURE_CAPTURE = "closure_capture"
    GLOBAL_ACCUMULATION = "global_accumulation"
    OBJECT_GROWTH = "object_growth"


class LeakSeverity(Enum):
    """Severity levels for memory leaks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemorySnapshot:
    """Memory snapshot at a point in time"""
    timestamp: datetime
    total_memory_mb: float
    available_memory_mb: float
    memory_percent: float
    process_memory_mb: float
    object_counts: Dict[str, int] = field(default_factory=dict)
    top_allocations: List[Tuple[str, int]] = field(default_factory=list)
    gc_stats: Dict[str, int] = field(default_factory=dict)


@dataclass
class MemoryLeak:
    """Memory leak detection result"""
    leak_id: str
    leak_type: LeakType
    severity: LeakSeverity
    description: str
    location: str
    growth_rate_mb_per_hour: float
    total_leaked_mb: float
    object_type: str
    reference_count: int
    first_detected: datetime
    last_seen: datetime
    stack_trace: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObjectTrackingInfo:
    """Information about tracked objects"""
    object_type: str
    count: int
    size_bytes: int
    growth_rate: float
    creation_locations: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class MemoryLeakDetector:
    """
    Memory leak detection and analysis system for Creator Economy platform
    """
    
    def __init__(self, 
                 monitoring_interval: float = 60.0,
                 snapshot_retention_hours: int = 24,
                 leak_detection_threshold_mb: float = 10.0):
        self.monitoring_interval = monitoring_interval
        self.snapshot_retention_hours = snapshot_retention_hours
        self.leak_detection_threshold_mb = leak_detection_threshold_mb
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Memory tracking
        self.memory_snapshots: deque = deque(maxlen=int(snapshot_retention_hours * 60 / monitoring_interval))
        self.detected_leaks: Dict[str, MemoryLeak] = {}
        self.object_tracking: Dict[str, ObjectTrackingInfo] = {}
        self.weak_references: Set[weakref.ref] = set()
        
        # Tracemalloc for detailed tracking
        self.tracemalloc_enabled = False
        self.allocation_traces: Dict[str, List] = defaultdict(list)
        
        # Growth patterns
        self.memory_growth_patterns: Dict[str, List[float]] = defaultdict(list)
        self.object_growth_patterns: Dict[str, List[int]] = defaultdict(list)
        
        # Thresholds and configurations
        self.thresholds = {
            'memory_growth_rate_mb_per_hour': 50.0,    # 50MB/hour
            'object_growth_rate_per_hour': 1000,       # 1000 objects/hour
            'memory_usage_critical': 90.0,             # 90%
            'gc_collection_threshold': 100,            # Collections per hour
            'reference_cycle_threshold': 50            # Circular references
        }
        
        # Prevention mechanisms
        self.auto_gc_enabled = True
        self.leak_prevention_callbacks: List[Callable] = []
        
        # Initialize tracking
        self._initialize_tracking()
        
        logger.info("MemoryLeakDetector initialized")

    def _initialize_tracking(self):
        """Initialize memory tracking systems"""
        try:
            # Enable tracemalloc for detailed allocation tracking
            if not tracemalloc.is_tracing():
                tracemalloc.start()
                self.tracemalloc_enabled = True
                logger.info("Tracemalloc enabled for detailed memory tracking")
            
            # Set up garbage collection monitoring
            gc.set_debug(gc.DEBUG_STATS)
            
            # Create initial memory snapshot
            self._take_memory_snapshot()
            
        except Exception as e:
            logger.error(f"Error initializing memory tracking: {e}")

    def start_monitoring(self):
        """Start background memory leak monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Memory leak monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        if self.tracemalloc_enabled:
            tracemalloc.stop()
            self.tracemalloc_enabled = False
        
        logger.info("Memory leak monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Take memory snapshot
                snapshot = self._take_memory_snapshot()
                
                # Analyze for leaks
                if len(self.memory_snapshots) >= 3:  # Need at least 3 snapshots
                    self._analyze_memory_leaks()
                
                # Check object growth
                self._check_object_growth()
                
                # Run garbage collection if needed
                if self.auto_gc_enabled:
                    self._conditional_garbage_collection()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")

    def _take_memory_snapshot(self) -> MemorySnapshot:
        """Take a comprehensive memory snapshot"""
        try:
            # System memory info
            memory_info = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Object counts
            object_counts = {}
            if HAS_OBJGRAPH:
                # Get top object types
                top_types = objgraph.most_common_types(limit=20)
                object_counts = dict(top_types)
            else:
                # Fallback to basic object counting
                object_counts = {
                    'total_objects': len(gc.get_objects()),
                    'dict': len([obj for obj in gc.get_objects() if isinstance(obj, dict)]),
                    'list': len([obj for obj in gc.get_objects() if isinstance(obj, list)]),
                    'tuple': len([obj for obj in gc.get_objects() if isinstance(obj, tuple)])
                }
            
            # Allocation tracking
            top_allocations = []
            if self.tracemalloc_enabled:
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')[:10]
                top_allocations = [
                    (str(stat.traceback), stat.size)
                    for stat in top_stats
                ]
            
            # Garbage collection stats
            gc_stats = {
                'collections_0': gc.get_count()[0],
                'collections_1': gc.get_count()[1],
                'collections_2': gc.get_count()[2],
                'uncollectable': len(gc.garbage)
            }
            
            snapshot = MemorySnapshot(
                timestamp=datetime.utcnow(),
                total_memory_mb=memory_info.total / 1024 / 1024,
                available_memory_mb=memory_info.available / 1024 / 1024,
                memory_percent=memory_info.percent,
                process_memory_mb=process_memory.rss / 1024 / 1024,
                object_counts=object_counts,
                top_allocations=top_allocations,
                gc_stats=gc_stats
            )
            
            self.memory_snapshots.append(snapshot)
            return snapshot
            
        except Exception as e:
            logger.error(f"Error taking memory snapshot: {e}")
            return MemorySnapshot(
                timestamp=datetime.utcnow(),
                total_memory_mb=0.0,
                available_memory_mb=0.0,
                memory_percent=0.0,
                process_memory_mb=0.0
            )

    def _analyze_memory_leaks(self):
        """Analyze memory snapshots for leak patterns"""
        try:
            if len(self.memory_snapshots) < 3:
                return
            
            recent_snapshots = list(self.memory_snapshots)[-10:]  # Last 10 snapshots
            
            # Analyze memory growth
            self._analyze_memory_growth(recent_snapshots)
            
            # Analyze object growth
            self._analyze_object_growth(recent_snapshots)
            
            # Detect reference cycles
            self._detect_reference_cycles()
            
            # Check for resource leaks
            self._check_resource_leaks()
            
        except Exception as e:
            logger.error(f"Error analyzing memory leaks: {e}")

    def _analyze_memory_growth(self, snapshots: List[MemorySnapshot]):
        """Analyze memory growth patterns"""
        if len(snapshots) < 3:
            return
        
        # Calculate memory growth rate
        memory_values = [s.process_memory_mb for s in snapshots]
        time_diffs = [(snapshots[i].timestamp - snapshots[i-1].timestamp).total_seconds() / 3600 
                     for i in range(1, len(snapshots))]
        
        if time_diffs:
            memory_diffs = [memory_values[i] - memory_values[i-1] for i in range(1, len(memory_values))]
            growth_rates = [diff / time_diff for diff, time_diff in zip(memory_diffs, time_diffs) if time_diff > 0]
            
            if growth_rates:
                avg_growth_rate = statistics.mean(growth_rates)
                
                if avg_growth_rate > self.thresholds['memory_growth_rate_mb_per_hour']:
                    leak_id = f"memory_growth_{int(time.time())}"
                    
                    if leak_id not in self.detected_leaks:
                        leak = MemoryLeak(
                            leak_id=leak_id,
                            leak_type=LeakType.OBJECT_GROWTH,
                            severity=self._calculate_leak_severity(avg_growth_rate),
                            description=f"Continuous memory growth detected: {avg_growth_rate:.2f}MB/hour",
                            location="system_wide",
                            growth_rate_mb_per_hour=avg_growth_rate,
                            total_leaked_mb=sum(memory_diffs) if memory_diffs else 0,
                            object_type="mixed",
                            reference_count=0,
                            first_detected=datetime.utcnow(),
                            last_seen=datetime.utcnow(),
                            recommendations=[
                                "Profile object allocations",
                                "Check for memory leaks in loops",
                                "Review cache implementations",
                                "Monitor garbage collection"
                            ]
                        )
                        
                        self.detected_leaks[leak_id] = leak
                        logger.warning(f"Memory leak detected: {leak.description}")

    def _analyze_object_growth(self, snapshots: List[MemorySnapshot]):
        """Analyze object count growth patterns"""
        if len(snapshots) < 3:
            return
        
        # Track object type growth
        for object_type in snapshots[0].object_counts.keys():
            counts = []
            for snapshot in snapshots:
                if object_type in snapshot.object_counts:
                    counts.append(snapshot.object_counts[object_type])
            
            if len(counts) >= 3:
                # Calculate growth rate
                growth_diffs = [counts[i] - counts[i-1] for i in range(1, len(counts))]
                avg_growth = statistics.mean(growth_diffs) if growth_diffs else 0
                
                # Convert to hourly rate
                time_diff_hours = (snapshots[-1].timestamp - snapshots[0].timestamp).total_seconds() / 3600
                hourly_growth = (avg_growth / max(1, time_diff_hours / len(growth_diffs))) if time_diff_hours > 0 else 0
                
                if hourly_growth > self.thresholds['object_growth_rate_per_hour']:
                    leak_id = f"object_growth_{object_type}_{int(time.time())}"
                    
                    if leak_id not in self.detected_leaks:
                        leak = MemoryLeak(
                            leak_id=leak_id,
                            leak_type=LeakType.OBJECT_GROWTH,
                            severity=self._calculate_object_growth_severity(hourly_growth),
                            description=f"Excessive {object_type} object growth: {hourly_growth:.0f}/hour",
                            location="object_allocation",
                            growth_rate_mb_per_hour=0.0,  # Would need object size info
                            total_leaked_mb=0.0,
                            object_type=object_type,
                            reference_count=counts[-1] if counts else 0,
                            first_detected=datetime.utcnow(),
                            last_seen=datetime.utcnow(),
                            recommendations=[
                                f"Review {object_type} object lifecycle",
                                "Check for proper cleanup",
                                "Implement object pooling",
                                "Monitor reference management"
                            ]
                        )
                        
                        self.detected_leaks[leak_id] = leak
                        logger.warning(f"Object growth leak detected: {leak.description}")

    def _detect_reference_cycles(self):
        """Detect reference cycles that prevent garbage collection"""
        try:
            # Force garbage collection and check uncollectable objects
            collected = gc.collect()
            uncollectable = len(gc.garbage)
            
            if uncollectable > self.thresholds['reference_cycle_threshold']:
                leak_id = f"reference_cycle_{int(time.time())}"
                
                if leak_id not in self.detected_leaks:
                    # Analyze garbage objects
                    garbage_types = defaultdict(int)
                    for obj in gc.garbage:
                        garbage_types[type(obj).__name__] += 1
                    
                    leak = MemoryLeak(
                        leak_id=leak_id,
                        leak_type=LeakType.REFERENCE_CYCLE,
                        severity=LeakSeverity.HIGH,
                        description=f"Reference cycles detected: {uncollectable} uncollectable objects",
                        location="reference_management",
                        growth_rate_mb_per_hour=0.0,
                        total_leaked_mb=0.0,
                        object_type=max(garbage_types.items(), key=lambda x: x[1])[0] if garbage_types else "unknown",
                        reference_count=uncollectable,
                        first_detected=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        recommendations=[
                            "Review circular references",
                            "Use weak references where appropriate",
                            "Implement proper cleanup methods",
                            "Check parent-child relationships"
                        ],
                        metadata={'garbage_types': dict(garbage_types)}
                    )
                    
                    self.detected_leaks[leak_id] = leak
                    logger.warning(f"Reference cycle leak detected: {leak.description}")
                    
        except Exception as e:
            logger.error(f"Error detecting reference cycles: {e}")

    def _check_resource_leaks(self):
        """Check for unclosed resources"""
        try:
            # Check open file descriptors
            process = psutil.Process()
            open_files = len(process.open_files())
            
            # Store file descriptor count for trend analysis
            self.memory_growth_patterns['open_files'].append(open_files)
            
            # Keep only recent data
            if len(self.memory_growth_patterns['open_files']) > 100:
                self.memory_growth_patterns['open_files'] = self.memory_growth_patterns['open_files'][-50:]
            
            # Check for growth in file descriptors
            if len(self.memory_growth_patterns['open_files']) >= 10:
                recent_counts = self.memory_growth_patterns['open_files'][-10:]
                if recent_counts[-1] > recent_counts[0] * 1.5:  # 50% increase
                    leak_id = f"resource_leak_files_{int(time.time())}"
                    
                    if leak_id not in self.detected_leaks:
                        leak = MemoryLeak(
                            leak_id=leak_id,
                            leak_type=LeakType.UNCLOSED_RESOURCE,
                            severity=LeakSeverity.MEDIUM,
                            description=f"File descriptor leak detected: {open_files} open files",
                            location="file_handling",
                            growth_rate_mb_per_hour=0.0,
                            total_leaked_mb=0.0,
                            object_type="file_descriptor",
                            reference_count=open_files,
                            first_detected=datetime.utcnow(),
                            last_seen=datetime.utcnow(),
                            recommendations=[
                                "Use context managers for file operations",
                                "Ensure proper file closing",
                                "Review file handling code",
                                "Implement resource pooling"
                            ]
                        )
                        
                        self.detected_leaks[leak_id] = leak
                        logger.warning(f"Resource leak detected: {leak.description}")
                        
        except Exception as e:
            logger.error(f"Error checking resource leaks: {e}")

    def _check_object_growth(self):
        """Check for unusual object growth"""
        try:
            if HAS_OBJGRAPH:
                # Track specific object types
                for obj_type in ['dict', 'list', 'tuple', 'function', 'method']:
                    count = objgraph.count(obj_type)
                    
                    if obj_type not in self.object_tracking:
                        self.object_tracking[obj_type] = ObjectTrackingInfo(
                            object_type=obj_type,
                            count=count,
                            size_bytes=0,
                            growth_rate=0.0
                        )
                    else:
                        tracking_info = self.object_tracking[obj_type]
                        previous_count = tracking_info.count
                        time_diff = (datetime.utcnow() - tracking_info.last_updated).total_seconds() / 3600
                        
                        if time_diff > 0:
                            growth_rate = (count - previous_count) / time_diff
                            tracking_info.count = count
                            tracking_info.growth_rate = growth_rate
                            tracking_info.last_updated = datetime.utcnow()
                            
        except Exception as e:
            logger.error(f"Error checking object growth: {e}")

    def _conditional_garbage_collection(self):
        """Run garbage collection based on conditions"""
        try:
            # Get current memory usage
            memory_percent = psutil.virtual_memory().percent
            
            # Force GC if memory usage is high
            if memory_percent > self.thresholds['memory_usage_critical']:
                before_objects = len(gc.get_objects())
                collected = gc.collect()
                after_objects = len(gc.get_objects())
                
                if collected > 0:
                    logger.info(f"Garbage collection freed {collected} objects "
                              f"(before: {before_objects}, after: {after_objects})")
                    
        except Exception as e:
            logger.error(f"Error in conditional garbage collection: {e}")

    def _cleanup_old_data(self):
        """Clean up old tracking data"""
        try:
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=self.snapshot_retention_hours)
            
            # Clean up old leaks that haven't been seen recently
            stale_leaks = []
            for leak_id, leak in self.detected_leaks.items():
                if leak.last_seen < cutoff_time:
                    stale_leaks.append(leak_id)
            
            for leak_id in stale_leaks:
                del self.detected_leaks[leak_id]
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    def _calculate_leak_severity(self, growth_rate_mb_per_hour: float) -> LeakSeverity:
        """Calculate leak severity based on growth rate"""
        if growth_rate_mb_per_hour > 200:
            return LeakSeverity.CRITICAL
        elif growth_rate_mb_per_hour > 100:
            return LeakSeverity.HIGH
        elif growth_rate_mb_per_hour > 50:
            return LeakSeverity.MEDIUM
        else:
            return LeakSeverity.LOW

    def _calculate_object_growth_severity(self, growth_rate_per_hour: float) -> LeakSeverity:
        """Calculate object growth severity"""
        if growth_rate_per_hour > 10000:
            return LeakSeverity.CRITICAL
        elif growth_rate_per_hour > 5000:
            return LeakSeverity.HIGH
        elif growth_rate_per_hour > 1000:
            return LeakSeverity.MEDIUM
        else:
            return LeakSeverity.LOW

    def track_object_reference(self, obj: Any, identifier: str = None):
        """Track an object reference for leak detection"""
        try:
            def cleanup_callback(ref):
                self.weak_references.discard(ref)
            
            weak_ref = weakref.ref(obj, cleanup_callback)
            self.weak_references.add(weak_ref)
            
            if identifier and HAS_OBJGRAPH:
                # Track object creation location
                self.allocation_traces[identifier].append({
                    'timestamp': datetime.utcnow(),
                    'object_type': type(obj).__name__,
                    'stack_trace': tracemalloc.get_traceback_limit()
                })
                
        except Exception as e:
            logger.error(f"Error tracking object reference: {e}")

    def add_leak_prevention_callback(self, callback: Callable):
        """Add a callback for leak prevention"""
        self.leak_prevention_callbacks.append(callback)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get memory leak detection performance summary"""
        if not self.memory_snapshots:
            return {"error": "No memory snapshots available"}
        
        latest_snapshot = self.memory_snapshots[-1]
        
        # Calculate trends
        if len(self.memory_snapshots) >= 2:
            memory_trend = latest_snapshot.process_memory_mb - self.memory_snapshots[-2].process_memory_mb
        else:
            memory_trend = 0.0
        
        return {
            "memory_status": {
                "current_memory_mb": latest_snapshot.process_memory_mb,
                "memory_usage_percent": latest_snapshot.memory_percent,
                "memory_trend_mb": memory_trend,
                "total_snapshots": len(self.memory_snapshots)
            },
            "leak_detection": {
                "total_leaks_detected": len(self.detected_leaks),
                "critical_leaks": len([l for l in self.detected_leaks.values() if l.severity == LeakSeverity.CRITICAL]),
                "high_leaks": len([l for l in self.detected_leaks.values() if l.severity == LeakSeverity.HIGH]),
                "leak_types": {
                    leak_type.value: len([l for l in self.detected_leaks.values() if l.leak_type == leak_type])
                    for leak_type in LeakType
                }
            },
            "object_tracking": {
                "tracked_object_types": len(self.object_tracking),
                "weak_references": len(self.weak_references),
                "high_growth_objects": len([t for t in self.object_tracking.values() if t.growth_rate > 1000])
            },
            "garbage_collection": {
                "total_objects": len(gc.get_objects()),
                "uncollectable_objects": len(gc.garbage),
                "gc_counts": gc.get_count(),
                "auto_gc_enabled": self.auto_gc_enabled
            },
            "recommendations": self._get_leak_prevention_recommendations()
        }

    def _get_leak_prevention_recommendations(self) -> List[str]:
        """Get memory leak prevention recommendations"""
        recommendations = []
        
        if not self.memory_snapshots:
            return ["Start memory monitoring to get recommendations"]
        
        # Check current status
        latest_snapshot = self.memory_snapshots[-1]
        critical_leaks = [l for l in self.detected_leaks.values() if l.severity == LeakSeverity.CRITICAL]
        high_growth_objects = [t for t in self.object_tracking.values() if t.growth_rate > 1000]
        
        if latest_snapshot.memory_percent > 85:
            recommendations.append("High memory usage - investigate memory consumption")
        
        if critical_leaks:
            recommendations.append(f"Critical memory leaks detected ({len(critical_leaks)}) - immediate action required")
        
        if high_growth_objects:
            recommendations.append(f"High object growth detected for {len(high_growth_objects)} types - review object lifecycle")
        
        if len(gc.garbage) > 50:
            recommendations.append("Reference cycles detected - review circular references")
        
        if not recommendations:
            recommendations.append("Memory usage is within normal parameters")
        
        return recommendations

    def get_detected_leaks(self) -> List[MemoryLeak]:
        """Get all detected memory leaks"""
        return list(self.detected_leaks.values())

    def get_memory_trend(self, hours: int = 1) -> Dict[str, List[float]]:
        """Get memory trend data for the specified period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_snapshots = [s for s in self.memory_snapshots if s.timestamp >= cutoff_time]
        
        return {
            'timestamps': [s.timestamp.isoformat() for s in recent_snapshots],
            'memory_usage_mb': [s.process_memory_mb for s in recent_snapshots],
            'memory_percent': [s.memory_percent for s in recent_snapshots],
            'object_counts': {
                obj_type: [s.object_counts.get(obj_type, 0) for s in recent_snapshots]
                for obj_type in ['dict', 'list', 'tuple'] if recent_snapshots
            }
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export memory leak detection metrics"""
        data = {
            "memory_snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "memory_mb": s.process_memory_mb,
                    "memory_percent": s.memory_percent,
                    "object_counts": s.object_counts
                }
                for s in list(self.memory_snapshots)[-50:]  # Last 50 snapshots
            ],
            "detected_leaks": [
                {
                    "leak_id": leak.leak_id,
                    "leak_type": leak.leak_type.value,
                    "severity": leak.severity.value,
                    "description": leak.description,
                    "growth_rate_mb_per_hour": leak.growth_rate_mb_per_hour,
                    "first_detected": leak.first_detected.isoformat(),
                    "last_seen": leak.last_seen.isoformat()
                }
                for leak in self.detected_leaks.values()
            ],
            "object_tracking": {
                obj_type: {
                    "count": info.count,
                    "growth_rate": info.growth_rate,
                    "last_updated": info.last_updated.isoformat()
                }
                for obj_type, info in self.object_tracking.items()
            }
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_memory_leak_detector(monitoring_interval: float = 60.0,
                               snapshot_retention_hours: int = 24,
                               leak_detection_threshold_mb: float = 10.0,
                               start_monitoring: bool = True) -> MemoryLeakDetector:
    """
    Create and configure a memory leak detector
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        snapshot_retention_hours: How long to retain snapshots
        leak_detection_threshold_mb: Threshold for leak detection
        start_monitoring: Start background monitoring
        
    Returns:
        Configured MemoryLeakDetector instance
    """
    detector = MemoryLeakDetector(
        monitoring_interval=monitoring_interval,
        snapshot_retention_hours=snapshot_retention_hours,
        leak_detection_threshold_mb=leak_detection_threshold_mb
    )
    
    if start_monitoring:
        detector.start_monitoring()
    
    return detector


# Main execution
if __name__ == "__main__":
    # Example usage
    detector = create_memory_leak_detector(monitoring_interval=10.0)  # 10 second intervals for demo
    
    try:
        print("Memory leak detector started...")
        print("Creating some objects to demonstrate tracking...")
        
        # Simulate potential memory leaks
        leaked_objects = []
        for i in range(1000):
            # Create objects that might leak
            obj = {'data': list(range(100)), 'id': i}
            leaked_objects.append(obj)
            
            # Track some objects
            if i % 100 == 0:
                detector.track_object_reference(obj, f"test_object_{i}")
        
        # Wait for some monitoring cycles
        time.sleep(30)
        
        # Get performance summary
        summary = detector.get_performance_summary()
        print(f"Memory leak detection summary: {json.dumps(summary, indent=2)}")
        
        # Get detected leaks
        leaks = detector.get_detected_leaks()
        if leaks:
            print(f"Detected {len(leaks)} potential memory leaks:")
            for leak in leaks:
                print(f"- {leak.description} (Severity: {leak.severity.value})")
        else:
            print("No memory leaks detected")
        
    finally:
        detector.stop_monitoring()