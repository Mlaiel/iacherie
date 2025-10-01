"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

Application Profiler - Enterprise Performance Monitoring
Advanced Python application profiling for Creator Economy platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import cProfile
import pstats
import io
import gc
import sys
import tracemalloc
import threading
import psutil
import linecache
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import statistics
import functools
import inspect
from prometheus_client import Gauge, Counter, Histogram
import traceback
import memory_profiler
import py_spy
import subprocess
import json
import weakref

logger = logging.getLogger(__name__)

@dataclass
class FunctionProfileMetrics:
    """Function-level profiling metrics"""
    function_name: str
    module_name: str
    file_path: str
    line_number: int
    call_count: int
    total_time_seconds: float
    cumulative_time_seconds: float
    avg_time_per_call_ms: float
    memory_usage_mb: float
    memory_peak_mb: float
    cpu_percent: float
    timestamp: datetime

@dataclass
class MemoryLeakMetrics:
    """Memory leak detection metrics"""
    object_type: str
    instance_count: int
    memory_usage_mb: float
    growth_rate_mb_per_hour: float
    leak_severity: str  # low, medium, high, critical
    allocation_traceback: List[str]
    first_seen: datetime
    last_seen: datetime

@dataclass
class GarbageCollectionMetrics:
    """Garbage collection performance metrics"""
    generation: int
    collection_count: int
    collection_time_ms: float
    objects_collected: int
    objects_uncollectable: int
    memory_freed_mb: float
    gc_efficiency_percent: float
    timestamp: datetime

@dataclass
class ThreadContentionMetrics:
    """Thread contention monitoring metrics"""
    thread_id: int
    thread_name: str
    lock_type: str
    lock_name: str
    wait_time_ms: float
    acquisition_time_ms: float
    hold_time_ms: float
    contention_count: int
    deadlock_risk_score: float
    timestamp: datetime

@dataclass
class HotSpotMetrics:
    """Performance hotspot identification"""
    hotspot_type: str  # cpu, memory, io
    location: str  # function, line, module
    severity_score: float
    impact_percent: float
    optimization_suggestion: str
    code_sample: str
    call_stack: List[str]
    timestamp: datetime

@dataclass
class AsyncPerformanceMetrics:
    """Async/await performance metrics"""
    coroutine_name: str
    event_loop_id: str
    execution_time_ms: float
    await_time_ms: float
    callback_time_ms: float
    queue_time_ms: float
    context_switches: int
    blocking_calls: int
    timestamp: datetime

class ApplicationProfiler:
    """
    Enterprise-grade Python application profiler
    Provides function-level profiling, memory leak detection, and performance optimization
    """
    
    def __init__(self,
                 enable_memory_profiling: bool = True,
                 enable_cpu_profiling: bool = True,
                 enable_thread_monitoring: bool = True,
                 enable_async_monitoring: bool = True,
                 sampling_interval: float = 0.1,
                 memory_threshold_mb: float = 100.0):
        """
        Initialize application profiler
        
        Args:
            enable_memory_profiling: Enable memory profiling and leak detection
            enable_cpu_profiling: Enable CPU profiling
            enable_thread_monitoring: Enable thread contention monitoring
            enable_async_monitoring: Enable async/await performance monitoring
            sampling_interval: Profiling sampling interval in seconds
            memory_threshold_mb: Memory usage threshold for alerts (MB)
        """
        self.enable_memory_profiling = enable_memory_profiling
        self.enable_cpu_profiling = enable_cpu_profiling
        self.enable_thread_monitoring = enable_thread_monitoring
        self.enable_async_monitoring = enable_async_monitoring
        self.sampling_interval = sampling_interval
        self.memory_threshold_mb = memory_threshold_mb
        
        # Profiling state
        self.profiling_active = False
        self.cpu_profiler = None
        self.memory_tracker = None
        
        # Metrics storage
        self.function_profiles: deque = deque(maxlen=10000)
        self.memory_leaks: Dict[str, MemoryLeakMetrics] = {}
        self.gc_metrics: deque = deque(maxlen=1000)
        self.thread_contentions: deque = deque(maxlen=5000)
        self.hotspots: deque = deque(maxlen=1000)
        self.async_metrics: deque = deque(maxlen=5000)
        
        # Performance tracking
        self.function_stats: Dict[str, Dict] = defaultdict(lambda: {
            'call_count': 0,
            'total_time': 0.0,
            'peak_memory': 0.0,
            'last_profiled': None
        })
        
        # Memory tracking
        self.memory_snapshots: List[Any] = []
        self.memory_baselines: Dict[str, float] = {}
        self.object_tracking: Dict[type, List] = defaultdict(list)
        
        # Thread monitoring
        self.thread_locks: Dict[str, Dict] = {}
        self.lock_contentions: Dict[str, List] = defaultdict(list)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring tasks
        self._monitoring_tasks = []
        
        # Enable tracemalloc for memory profiling
        if self.enable_memory_profiling:
            tracemalloc.start()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.function_execution_time_histogram = Histogram(
            'application_function_execution_seconds',
            'Function execution time',
            ['function_name', 'module_name'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        )
        
        self.memory_usage_gauge = Gauge(
            'application_memory_usage_mb',
            'Application memory usage in MB',
            ['object_type']
        )
        
        self.memory_leak_severity_gauge = Gauge(
            'application_memory_leak_severity',
            'Memory leak severity score',
            ['object_type']
        )
        
        self.gc_collection_time_histogram = Histogram(
            'application_gc_collection_seconds',
            'Garbage collection time',
            ['generation']
        )
        
        self.thread_contention_time_histogram = Histogram(
            'application_thread_contention_seconds',
            'Thread contention time',
            ['lock_type']
        )
        
        self.hotspot_severity_gauge = Gauge(
            'application_hotspot_severity',
            'Performance hotspot severity score',
            ['hotspot_type', 'location']
        )
        
        self.async_await_time_histogram = Histogram(
            'application_async_await_seconds',
            'Async await time',
            ['coroutine_name']
        )
    
    def profile_function(self, include_memory: bool = True):
        """Decorator for function-level profiling"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._profile_function_call(func, args, kwargs, include_memory)
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._profile_async_function_call(func, args, kwargs, include_memory)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        
        return decorator
    
    def _profile_function_call(self, func: Callable, args: tuple, kwargs: dict, include_memory: bool) -> Any:
        """Profile synchronous function call"""
        function_name = f"{func.__module__}.{func.__qualname__}"
        
        # Memory baseline
        memory_before = 0
        if include_memory and self.enable_memory_profiling:
            gc.collect()  # Force garbage collection
            memory_before = psutil.Process().memory_info().rss / (1024 * 1024)
        
        # CPU profiling
        if self.enable_cpu_profiling:
            profiler = cProfile.Profile()
            profiler.enable()
        
        start_time = time.time()
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Stop CPU profiling
            if self.enable_cpu_profiling:
                profiler.disable()
                
                # Extract profiling stats
                stats_stream = io.StringIO()
                stats = pstats.Stats(profiler, stream=stats_stream)
                stats.sort_stats('cumulative')
                
                # Get function-specific stats
                for stat_key, stat_value in stats.stats.items():
                    if func.__name__ in str(stat_key):
                        call_count, total_time, cumulative_time = stat_value[:3]
                        break
                else:
                    call_count, total_time, cumulative_time = 1, execution_time, execution_time
            else:
                call_count, total_time, cumulative_time = 1, execution_time, execution_time
            
            # Memory measurement
            memory_after = 0
            memory_peak = 0
            if include_memory and self.enable_memory_profiling:
                memory_after = psutil.Process().memory_info().rss / (1024 * 1024)
                memory_peak = max(memory_before, memory_after)
            
            # Create metrics
            metrics = FunctionProfileMetrics(
                function_name=function_name,
                module_name=func.__module__,
                file_path=inspect.getfile(func),
                line_number=inspect.getsourcelines(func)[1],
                call_count=call_count,
                total_time_seconds=total_time,
                cumulative_time_seconds=cumulative_time,
                avg_time_per_call_ms=(total_time / call_count) * 1000,
                memory_usage_mb=memory_after - memory_before,
                memory_peak_mb=memory_peak,
                cpu_percent=0,  # Would need separate CPU monitoring
                timestamp=datetime.utcnow()
            )
            
            # Store metrics
            self.function_profiles.append(metrics)
            self._update_function_stats(function_name, metrics)
            
            # Update Prometheus metrics
            self.function_execution_time_histogram.labels(
                function_name=func.__name__,
                module_name=func.__module__
            ).observe(execution_time)
            
            if include_memory:
                self.memory_usage_gauge.labels(
                    object_type='function_call'
                ).set(memory_after - memory_before)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in profiled function {function_name}: {e}")
            raise
    
    async def _profile_async_function_call(self, func: Callable, args: tuple, kwargs: dict, include_memory: bool) -> Any:
        """Profile asynchronous function call"""
        function_name = f"{func.__module__}.{func.__qualname__}"
        
        # Get event loop info
        loop = asyncio.get_event_loop()
        loop_id = str(id(loop))
        
        start_time = time.time()
        await_start = None
        await_total = 0
        
        # Memory baseline
        memory_before = 0
        if include_memory and self.enable_memory_profiling:
            gc.collect()
            memory_before = psutil.Process().memory_info().rss / (1024 * 1024)
        
        try:
            # Execute async function
            result = await func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Create async metrics
            async_metrics = AsyncPerformanceMetrics(
                coroutine_name=function_name,
                event_loop_id=loop_id,
                execution_time_ms=execution_time * 1000,
                await_time_ms=await_total * 1000,
                callback_time_ms=0,  # Would need detailed loop monitoring
                queue_time_ms=0,     # Would need task queue monitoring
                context_switches=0,  # Would need OS-level monitoring
                blocking_calls=0,    # Would need call analysis
                timestamp=datetime.utcnow()
            )
            
            self.async_metrics.append(async_metrics)
            
            # Update Prometheus metrics
            self.async_await_time_histogram.labels(
                coroutine_name=func.__name__
            ).observe(execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in profiled async function {function_name}: {e}")
            raise
    
    def _update_function_stats(self, function_name: str, metrics: FunctionProfileMetrics):
        """Update function statistics"""
        stats = self.function_stats[function_name]
        stats['call_count'] += metrics.call_count
        stats['total_time'] += metrics.total_time_seconds
        stats['peak_memory'] = max(stats['peak_memory'], metrics.memory_peak_mb)
        stats['last_profiled'] = metrics.timestamp
    
    def start_memory_profiling(self):
        """Start memory profiling and leak detection"""
        if not self.enable_memory_profiling:
            return
        
        # Take initial memory snapshot
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            self.memory_snapshots.append(snapshot)
            
            # Establish baselines
            for trace in snapshot.traces:
                filename = trace.traceback.filename
                if filename not in self.memory_baselines:
                    self.memory_baselines[filename] = trace.size / (1024 * 1024)
        
        logger.info("Memory profiling started")
    
    def detect_memory_leaks(self) -> List[MemoryLeakMetrics]:
        """Detect memory leaks"""
        if not self.enable_memory_profiling or not tracemalloc.is_tracing():
            return []
        
        current_snapshot = tracemalloc.take_snapshot()
        self.memory_snapshots.append(current_snapshot)
        
        # Keep only recent snapshots
        if len(self.memory_snapshots) > 10:
            self.memory_snapshots = self.memory_snapshots[-10:]
        
        leaks = []
        
        if len(self.memory_snapshots) >= 2:
            # Compare with previous snapshot
            previous_snapshot = self.memory_snapshots[-2]
            top_stats = current_snapshot.compare_to(previous_snapshot, 'traceback')
            
            for stat in top_stats[:10]:  # Top 10 memory growers
                if stat.size_diff > 1024 * 1024:  # More than 1MB growth
                    
                    # Calculate growth rate
                    time_diff = (datetime.utcnow() - (datetime.utcnow() - timedelta(minutes=5))).total_seconds() / 3600  # hours
                    growth_rate = (stat.size_diff / (1024 * 1024)) / max(time_diff, 0.001)
                    
                    # Determine severity
                    if growth_rate > 100:  # 100MB/hour
                        severity = 'critical'
                    elif growth_rate > 50:  # 50MB/hour
                        severity = 'high'
                    elif growth_rate > 10:  # 10MB/hour
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    # Extract allocation traceback
                    traceback_lines = []
                    for frame in stat.traceback:
                        line = f"{frame.filename}:{frame.lineno}"
                        traceback_lines.append(line)
                    
                    object_type = self._identify_object_type(stat.traceback)
                    
                    leak_metrics = MemoryLeakMetrics(
                        object_type=object_type,
                        instance_count=stat.count,
                        memory_usage_mb=stat.size / (1024 * 1024),
                        growth_rate_mb_per_hour=growth_rate,
                        leak_severity=severity,
                        allocation_traceback=traceback_lines,
                        first_seen=datetime.utcnow() - timedelta(minutes=5),  # Approximation
                        last_seen=datetime.utcnow()
                    )
                    
                    leaks.append(leak_metrics)
                    
                    # Store in persistent tracking
                    self.memory_leaks[object_type] = leak_metrics
                    
                    # Update Prometheus metrics
                    severity_score = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}[severity]
                    self.memory_leak_severity_gauge.labels(
                        object_type=object_type
                    ).set(severity_score)
        
        return leaks
    
    def _identify_object_type(self, traceback) -> str:
        """Identify object type from allocation traceback"""
        for frame in traceback:
            filename = frame.filename
            
            # Look for common patterns
            if 'list' in filename or 'append' in str(frame):
                return 'list'
            elif 'dict' in filename:
                return 'dict'
            elif 'string' in filename or 'str' in filename:
                return 'string'
            elif 'tensor' in filename.lower():
                return 'tensor'
            elif 'numpy' in filename:
                return 'numpy_array'
            elif 'pandas' in filename:
                return 'dataframe'
        
        return 'unknown'
    
    def monitor_garbage_collection(self):
        """Monitor garbage collection performance"""
        gc_stats = gc.get_stats()
        
        for generation, stats in enumerate(gc_stats):
            collection_count = stats['collections']
            
            # Measure GC performance
            start_time = time.time()
            collected = gc.collect(generation)
            gc_time = (time.time() - start_time) * 1000
            
            # Calculate efficiency
            total_objects = len(gc.get_objects())
            efficiency = (collected / max(total_objects, 1)) * 100
            
            metrics = GarbageCollectionMetrics(
                generation=generation,
                collection_count=collection_count,
                collection_time_ms=gc_time,
                objects_collected=collected,
                objects_uncollectable=len(gc.garbage),
                memory_freed_mb=0,  # Would need memory measurement
                gc_efficiency_percent=efficiency,
                timestamp=datetime.utcnow()
            )
            
            self.gc_metrics.append(metrics)
            
            # Update Prometheus metrics
            self.gc_collection_time_histogram.labels(
                generation=str(generation)
            ).observe(gc_time / 1000)
    
    def identify_performance_hotspots(self) -> List[HotSpotMetrics]:
        """Identify performance hotspots"""
        hotspots = []
        
        # Analyze function profiles for CPU hotspots
        if len(self.function_profiles) >= 10:
            recent_profiles = list(self.function_profiles)[-100:]  # Last 100 calls
            
            # Group by function
            by_function = defaultdict(list)
            for profile in recent_profiles:
                by_function[profile.function_name].append(profile)
            
            # Find CPU hotspots
            for function_name, profiles in by_function.items():
                avg_time = statistics.mean([p.total_time_seconds for p in profiles])
                total_time = sum([p.total_time_seconds for p in profiles])
                
                if avg_time > 0.1 or total_time > 1.0:  # Significant CPU usage
                    severity_score = min(100, (avg_time * 1000) + (total_time * 10))
                    
                    # Get code sample
                    try:
                        file_path = profiles[0].file_path
                        line_num = profiles[0].line_number
                        code_sample = linecache.getline(file_path, line_num).strip()
                    except:
                        code_sample = "Unable to retrieve code"
                    
                    hotspot = HotSpotMetrics(
                        hotspot_type='cpu',
                        location=function_name,
                        severity_score=severity_score,
                        impact_percent=min(100, total_time * 10),
                        optimization_suggestion=self._generate_cpu_optimization_suggestion(profiles),
                        code_sample=code_sample,
                        call_stack=[function_name],
                        timestamp=datetime.utcnow()
                    )
                    
                    hotspots.append(hotspot)
                    
                    # Update Prometheus metrics
                    self.hotspot_severity_gauge.labels(
                        hotspot_type='cpu',
                        location=function_name.split('.')[-1]  # Just function name
                    ).set(severity_score)
        
        # Analyze memory hotspots
        for object_type, leak_metrics in self.memory_leaks.items():
            if leak_metrics.leak_severity in ['high', 'critical']:
                severity_score = 50 if leak_metrics.leak_severity == 'high' else 80
                
                hotspot = HotSpotMetrics(
                    hotspot_type='memory',
                    location=object_type,
                    severity_score=severity_score,
                    impact_percent=min(100, leak_metrics.growth_rate_mb_per_hour),
                    optimization_suggestion=self._generate_memory_optimization_suggestion(leak_metrics),
                    code_sample="",
                    call_stack=leak_metrics.allocation_traceback,
                    timestamp=datetime.utcnow()
                )
                
                hotspots.append(hotspot)
        
        self.hotspots.extend(hotspots)
        return hotspots
    
    def _generate_cpu_optimization_suggestion(self, profiles: List[FunctionProfileMetrics]) -> str:
        """Generate CPU optimization suggestion"""
        avg_time = statistics.mean([p.total_time_seconds for p in profiles])
        call_count = sum([p.call_count for p in profiles])
        
        if call_count > 1000 and avg_time > 0.01:
            return "High-frequency function with significant execution time. Consider caching results or optimizing algorithm."
        elif avg_time > 1.0:
            return "Long-running function. Consider async execution or breaking into smaller functions."
        elif call_count > 10000:
            return "Very high call frequency. Consider batch processing or result caching."
        else:
            return "General optimization: Profile internal operations and optimize data structures."
    
    def _generate_memory_optimization_suggestion(self, leak_metrics: MemoryLeakMetrics) -> str:
        """Generate memory optimization suggestion"""
        if leak_metrics.object_type == 'list':
            return "List growth detected. Consider using deque for append operations or implement size limits."
        elif leak_metrics.object_type == 'dict':
            return "Dictionary growth detected. Implement key expiration or use WeakKeyDictionary for caches."
        elif leak_metrics.object_type == 'string':
            return "String accumulation detected. Use StringIO or list join for string building."
        elif leak_metrics.object_type in ['tensor', 'numpy_array']:
            return "Array memory growth. Ensure proper cleanup and consider memory-mapped arrays for large datasets."
        else:
            return "Monitor object lifecycle and implement explicit cleanup or weak references."
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Function performance summary
        recent_profiles = [p for p in self.function_profiles if p.timestamp >= cutoff_time]
        
        if not recent_profiles:
            return {'message': 'No recent profiling data available'}
        
        # Top functions by execution time
        by_function = defaultdict(list)
        for profile in recent_profiles:
            by_function[profile.function_name].append(profile)
        
        top_functions = []
        for function_name, profiles in by_function.items():
            total_time = sum([p.total_time_seconds for p in profiles])
            avg_time = statistics.mean([p.total_time_seconds for p in profiles])
            call_count = sum([p.call_count for p in profiles])
            
            top_functions.append({
                'function': function_name,
                'total_time_seconds': total_time,
                'avg_time_seconds': avg_time,
                'call_count': call_count,
                'efficiency_score': min(100, 100 - (avg_time * 1000))
            })
        
        top_functions.sort(key=lambda x: x['total_time_seconds'], reverse=True)
        
        # Memory summary
        memory_summary = {
            'total_leaks_detected': len(self.memory_leaks),
            'critical_leaks': len([l for l in self.memory_leaks.values() if l.leak_severity == 'critical']),
            'high_leaks': len([l for l in self.memory_leaks.values() if l.leak_severity == 'high']),
            'total_growth_rate_mb_per_hour': sum([l.growth_rate_mb_per_hour for l in self.memory_leaks.values()])
        }
        
        # Hotspots summary
        recent_hotspots = [h for h in self.hotspots if h.timestamp >= cutoff_time]
        hotspots_by_type = defaultdict(list)
        for hotspot in recent_hotspots:
            hotspots_by_type[hotspot.hotspot_type].append(hotspot)
        
        return {
            'time_window_hours': hours,
            'total_function_calls': len(recent_profiles),
            'unique_functions': len(by_function),
            'top_functions': top_functions[:10],
            'memory_analysis': memory_summary,
            'hotspots_by_type': {
                hotspot_type: len(hotspots)
                for hotspot_type, hotspots in hotspots_by_type.items()
            },
            'performance_score': self._calculate_performance_score(recent_profiles, memory_summary)
        }
    
    def _calculate_performance_score(self, profiles: List[FunctionProfileMetrics], memory_summary: Dict) -> float:
        """Calculate overall performance score"""
        score = 100.0
        
        # CPU performance penalty
        if profiles:
            avg_execution_time = statistics.mean([p.total_time_seconds for p in profiles])
            score -= min(30, avg_execution_time * 1000)  # Max 30 point penalty
        
        # Memory leak penalty
        score -= memory_summary['critical_leaks'] * 20
        score -= memory_summary['high_leaks'] * 10
        
        # Growth rate penalty
        if memory_summary['total_growth_rate_mb_per_hour'] > 50:
            score -= 25
        elif memory_summary['total_growth_rate_mb_per_hour'] > 10:
            score -= 10
        
        return max(0.0, score)
    
    async def start_continuous_profiling(self):
        """Start continuous profiling"""
        if self.profiling_active:
            logger.warning("Profiling already active")
            return
        
        self.profiling_active = True
        
        # Start profiling tasks
        tasks = [
            self._memory_monitoring_loop(),
            self._gc_monitoring_loop(),
            self._hotspot_analysis_loop()
        ]
        
        self._monitoring_tasks = [asyncio.create_task(task) for task in tasks]
        
        self.start_memory_profiling()
        logger.info("Continuous application profiling started")
    
    async def stop_continuous_profiling(self):
        """Stop continuous profiling"""
        self.profiling_active = False
        
        for task in self._monitoring_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._monitoring_tasks.clear()
        logger.info("Continuous application profiling stopped")
    
    async def _memory_monitoring_loop(self):
        """Memory monitoring loop"""
        while self.profiling_active:
            try:
                self.detect_memory_leaks()
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _gc_monitoring_loop(self):
        """Garbage collection monitoring loop"""
        while self.profiling_active:
            try:
                self.monitor_garbage_collection()
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in GC monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _hotspot_analysis_loop(self):
        """Hotspot analysis loop"""
        while self.profiling_active:
            try:
                hotspots = self.identify_performance_hotspots()
                
                # Log critical hotspots
                for hotspot in hotspots:
                    if hotspot.severity_score > 70:
                        logger.warning(f"Performance hotspot detected: {hotspot.location} ({hotspot.hotspot_type})")
                
                await asyncio.sleep(180)  # Analyze every 3 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in hotspot analysis loop: {e}")
                await asyncio.sleep(180)