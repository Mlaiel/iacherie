"""⚡ Performance Profiling System
==============================

Advanced performance monitoring and optimization system for the Ainflue platform.
Provides real-time profiling, bottleneck detection, and optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import cProfile
import pstats
import io
import tracemalloc
import gc

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class ProfilerType(Enum):
    """
Types of profilers"""

    CPU = "cpu"
    MEMORY = "memory"
    ASYNC = "async"
    DATABASE = "database"
    NETWORK = "network"


class OptimizationLevel(Enum):
    """Optimization recommendation levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    profiler_type: Optional[ProfilerType] = None


@dataclass
class BottleneckReport:
    """
Performance bottleneck report"""
    function_name: str
    execution_time: float
    call_count: int
    memory_usage: float
    cpu_percentage: float
    optimization_level: OptimizationLevel
    recommendations: List[str]


class PerformanceProfiler:
    """
    Advanced performance profiling system
    
    Features:
    - Real-time CPU profiling
    - Memory usage tracking
    - Async function profiling
    - Database query analysis
    - Network call monitoring
    - Automatic bottleneck detection
    - Optimization recommendations
    """
    
    def __init__(self):
        """
Initialize performance profiler"""
        
        # Prometheus metrics
        self.cpu_usage = Gauge(
            'ainflue_cpu_usage_percentage',
            'CPU usage percentage',
            ['process', 'core']
        )
        
        self.memory_usage = Gauge(
            'ainflue_memory_usage_bytes',
            'Memory usage in bytes',
            ['type']  # rss, vms, shared, etc.
        )
        
        self.function_execution_time = Histogram(
            'ainflue_function_execution_seconds',
            'Function execution time',
            ['function_name', 'module'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf')]
        )
        
        self.gc_collections = Counter(
            'ainflue_gc_collections_total',
            'Total garbage collections',
            ['generation']
        )
        
        self.database_query_time = Histogram(
            'ainflue_database_query_seconds',
            'Database query execution time',
            ['query_type', 'table'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0, float('inf')]
        )
        
        # Profiling data storage
        self.performance_metrics: List[PerformanceMetric] = []
        self.bottleneck_reports: List[BottleneckReport] = []
        self.function_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.profiling_sessions: Dict[str, Any] = {}
        
        # Performance tracking
        self.memory_tracker = None
        self.cpu_profiler = None
        
        # Recent metrics for quick access
        self.recent_metrics = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'functions': deque(maxlen=1000)
        }
        
        logger.info("PerformanceProfiler initialized successfully")
    
    async def start_profiling(
        self,
        profiler_types: List[ProfilerType] = None,
        duration_seconds: Optional[int] = None
    ) -> str:
        """
        Start performance profiling session
        
        Args:
            profiler_types: Types of profilers to enable
            duration_seconds: Duration to run profiling (None = indefinite)
            
        Returns:
            Session ID
        """
        try:
            session_id = f"profile_{int(time.time())}"
            profiler_types = profiler_types or [ProfilerType.CPU, ProfilerType.MEMORY]
            
            session = {
                "session_id": session_id,
                "start_time": datetime.utcnow(),
                "profiler_types": profiler_types,
                "duration_seconds": duration_seconds,
                "active": True,
                "metrics": []
            }
            
            self.profiling_sessions[session_id] = session
            
            # Start memory tracking if requested
            if ProfilerType.MEMORY in profiler_types:
                tracemalloc.start()
                logger.info("Memory tracking started")
            
            # Start CPU profiling if requested
            if ProfilerType.CPU in profiler_types:
                self.cpu_profiler = cProfile.Profile()
                self.cpu_profiler.enable()
                logger.info("CPU profiling started")
            
            # Start real-time monitoring
            if not self.monitoring_active:
                await self._start_monitoring()
            
            logger.info(f"Profiling session {session_id} started with {profiler_types}")
            
            # Auto-stop after duration if specified
            if duration_seconds:
                asyncio.create_task(self._auto_stop_profiling(session_id, duration_seconds))
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting profiling: {e}")
            return ""
    
    async def stop_profiling(self, session_id: str) -> Dict[str, Any]:
        """
        Stop profiling session and generate report
        
        Args:
            session_id: Session to stop
            
        Returns:
            Profiling report
        """
        try:
            if session_id not in self.profiling_sessions:
                logger.warning(f"Session {session_id} not found")
                return {"error": "Session not found"}
            
            session = self.profiling_sessions[session_id]
            session["active"] = False
            session["end_time"] = datetime.utcnow()
            
            report = {
                "session_id": session_id,
                "duration": (session["end_time"] - session["start_time"]).total_seconds(),
                "profiler_types": [pt.value for pt in session["profiler_types"]],
                "summary": {},
                "bottlenecks": [],
                "recommendations": []
            }
            
            # Generate CPU profiling report
            if ProfilerType.CPU in session["profiler_types"] and self.cpu_profiler:
                cpu_report = await self._generate_cpu_report()
                report["summary"]["cpu"] = cpu_report
                self.cpu_profiler.disable()
                self.cpu_profiler = None
            
            # Generate memory profiling report
            if ProfilerType.MEMORY in session["profiler_types"]:
                memory_report = await self._generate_memory_report()
                report["summary"]["memory"] = memory_report
                tracemalloc.stop()
            
            # Detect bottlenecks
            bottlenecks = await self._detect_bottlenecks(session)
            report["bottlenecks"] = [
                {
                    "function": b.function_name,
                    "execution_time": b.execution_time,
                    "call_count": b.call_count,
                    "optimization_level": b.optimization_level.value,
                    "recommendations": b.recommendations
                }
                for b in bottlenecks
            ]
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(report)
            report["recommendations"] = recommendations
            
            # Store bottleneck reports
            self.bottleneck_reports.extend(bottlenecks)
            
            logger.info(f"Profiling session {session_id} completed")
            return report
            
        except Exception as e:
            logger.error(f"Error stopping profiling: {e}")
            return {"error": str(e)}
    
    async def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Profile a specific function execution
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Profiling data
        """
        try:
            function_name = f"{func.__module__}.{func.__name__}"
            
            # Start timing
            start_time = time.perf_counter()
            start_memory = self._get_memory_usage()
            
            # Enable CPU profiling for this function
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            finally:
                profiler.disable()
            
            # Calculate metrics
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Generate stats
            stats_buffer = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_buffer)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # Top 10 functions
            
            # Update Prometheus metrics
            self.function_execution_time.labels(
                function_name=function_name,
                module=func.__module__ or "unknown"
            ).observe(execution_time)
            
            # Store function statistics
            self.function_stats[function_name].update({
                "total_calls": self.function_stats[function_name].get("total_calls", 0) + 1,
                "total_time": self.function_stats[function_name].get("total_time", 0) + execution_time,
                "avg_time": self.function_stats[function_name].get("total_time", 0) / self.function_stats[function_name].get("total_calls", 1),
                "last_execution": execution_time,
                "memory_delta": memory_delta
            })
            
            # Add to recent metrics
            metric = PerformanceMetric(
                name=function_name,
                value=execution_time,
                unit="seconds",
                timestamp=datetime.utcnow(),
                context={"memory_delta": memory_delta, "call_count": 1},
                profiler_type=ProfilerType.CPU
            )
            
            self.performance_metrics.append(metric)
            self.recent_metrics['functions'].append(metric)
            
            profile_data = {
                "function_name": function_name,
                "execution_time": execution_time,
                "memory_delta": memory_delta,
                "cpu_stats": stats_buffer.getvalue(),
                "result": result if result is not None else "No return value"
            }
            
            logger.debug(f"Function {function_name} profiled: {execution_time:.4f}s")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error profiling function {func}: {e}")
            return {"error": str(e)}
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Update Prometheus metrics
            self.cpu_usage.labels(process="ainflue", core="total").set(cpu_percent)
            self.memory_usage.labels(type="rss").set(process_memory.rss)
            self.memory_usage.labels(type="vms").set(process_memory.vms)
            self.memory_usage.labels(type="system_total").set(memory.total)
            self.memory_usage.labels(type="system_available").set(memory.available)
            
            # GC statistics
            gc_stats = gc.get_stats()
            for i, stats in enumerate(gc_stats):
                self.gc_collections.labels(generation=str(i))._value._value = stats.get('collections', 0)
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_usage_percent": disk.percent
                },
                "process": {
                    "cpu_percent": process_cpu,
                    "memory_rss_mb": process_memory.rss / (1024**2),
                    "memory_vms_mb": process_memory.vms / (1024**2),
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files())
                },
                "python": {
                    "gc_collections": [stats.get('collections', 0) for stats in gc_stats],
                    "gc_collected": [stats.get('collected', 0) for stats in gc_stats],
                    "gc_uncollectable": [stats.get('uncollectable', 0) for stats in gc_stats]
                },
                "application": {
                    "active_sessions": len(self.profiling_sessions),
                    "total_metrics": len(self.performance_metrics),
                    "function_stats_count": len(self.function_stats)
                }
            }
            
            # Store metric
            metric = PerformanceMetric(
                name="system_cpu",
                value=cpu_percent,
                unit="percent",
                timestamp=datetime.utcnow(),
                context=metrics
            )
            self.recent_metrics['cpu'].append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {"error": str(e)}
    
    async def get_performance_report(self, period_hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            period_hours: Report period in hours
            
        Returns:
            Performance report
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=period_hours)
            
            # Filter metrics by time period
            period_metrics = [
                metric for metric in self.performance_metrics
                if start_time <= metric.timestamp <= end_time
            ]
            
            report = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": period_hours
                },
                "summary": await self._calculate_performance_summary(period_metrics),
                "top_functions": await self._get_top_functions_by_time(),
                "memory_analysis": await self._analyze_memory_usage(period_metrics),
                "bottlenecks": await self._get_recent_bottlenecks(),
                "trends": await self._calculate_performance_trends(period_metrics),
                "recommendations": await self._get_performance_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {"error": str(e)}
    
    async def _start_monitoring(self) -> None:
        """Start real-time performance monitoring"""
        try:
            self.monitoring_active = True
            
            def monitoring_loop():
                while self.monitoring_active:
                    try:
                        # Collect metrics
                        asyncio.create_task(self.get_real_time_metrics())
                        time.sleep(10)  # Collect every 10 seconds
                    except Exception as e:
                        logger.error(f"Error in monitoring loop: {e}")
                        time.sleep(5)
            
            self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("Real-time monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
    
    async def _auto_stop_profiling(self, session_id: str, duration_seconds: int) -> None:
        """Auto-stop profiling after specified duration"""
        await asyncio.sleep(duration_seconds)
        await self.stop_profiling(session_id)
    
    async def _generate_cpu_report(self) -> Dict[str, Any]:
        """
Generate CPU profiling report"""
        try:
            if not self.cpu_profiler:
                return {"error": "No CPU profiler active"}
            
            # Create stats from profiler
            stats_buffer = io.StringIO()
            stats = pstats.Stats(self.cpu_profiler, stream=stats_buffer)
            
            # Get top functions by cumulative time
            stats.sort_stats('cumulative')
            stats.print_stats(20)
            
            # Get top functions by total time
            top_functions = []
            for func, (calls, total_time, cumulative_time, *_) in stats.stats.items():
                filename, line, function_name = func
                top_functions.append({
                    "function": f"{filename}:{line}({function_name})",
                    "calls": calls,
                    "total_time": total_time,
                    "cumulative_time": cumulative_time,
                    "per_call": total_time / calls if calls > 0 else 0
                })
            
            # Sort by total time and take top 10
            top_functions.sort(key=lambda x: x["total_time"], reverse=True)
            
            return {
                "top_functions": top_functions[:10],
                "total_functions": len(stats.stats),
                "raw_stats": stats_buffer.getvalue()
            }
            
        except Exception as e:
            logger.error(f"Error generating CPU report: {e}")
            return {"error": str(e)}
    
    async def _generate_memory_report(self) -> Dict[str, Any]:
        """Generate memory profiling report"""
        try:
            if not tracemalloc.is_tracing():
                return {"error": "Memory tracking not active"}
            
            # Get memory statistics
            current, peak = tracemalloc.get_traced_memory()
            snapshot = tracemalloc.take_snapshot()
            
            # Get top memory consumers
            top_stats = snapshot.statistics('lineno')
            
            memory_hotspots = []
            for stat in top_stats[:10]:
                memory_hotspots.append({
                    "file": stat.traceback.format()[-1] if stat.traceback.format() else "unknown",
                    "size_mb": stat.size / (1024 * 1024),
                    "count": stat.count
                })
            
            return {
                "current_usage_mb": current / (1024 * 1024),
                "peak_usage_mb": peak / (1024 * 1024),
                "memory_hotspots": memory_hotspots,
                "total_traces": len(top_stats)
            }
            
        except Exception as e:
            logger.error(f"Error generating memory report: {e}")
            return {"error": str(e)}
    
    async def _detect_bottlenecks(self, session: Dict[str, Any]) -> List[BottleneckReport]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        try:
            # Analyze function statistics for bottlenecks
            for func_name, stats in self.function_stats.items():
                avg_time = stats.get("avg_time", 0)
                total_calls = stats.get("total_calls", 0)
                total_time = stats.get("total_time", 0)
                
                # Determine optimization level
                optimization_level = OptimizationLevel.LOW
                recommendations = []
                
                if avg_time > 1.0:  # Functions taking more than 1 second on average
                    optimization_level = OptimizationLevel.HIGH
                    recommendations.extend([
                        "Consider caching results if function is pure",
                        "Profile function internals for specific bottlenecks",
                        "Consider asynchronous execution if I/O bound"
                    ])
                elif avg_time > 0.1:  # Functions taking more than 100ms on average
                    optimization_level = OptimizationLevel.MEDIUM
                    recommendations.extend([
                        "Review algorithm complexity",
                        "Consider optimizing data structures"
                    ])
                
                if total_calls > 10000:  # Frequently called functions
                    optimization_level = max(optimization_level, OptimizationLevel.MEDIUM)
                    recommendations.append("Consider reducing call frequency or caching")
                
                if optimization_level != OptimizationLevel.LOW:
                    bottleneck = BottleneckReport(
                        function_name=func_name,
                        execution_time=avg_time,
                        call_count=total_calls,
                        memory_usage=stats.get("memory_delta", 0),
                        cpu_percentage=0,  # Would need more detailed CPU tracking
                        optimization_level=optimization_level,
                        recommendations=recommendations
                    )
                    bottlenecks.append(bottleneck)
            
            # Sort by optimization level and execution time
            bottlenecks.sort(
                key=lambda x: (x.optimization_level.value, x.execution_time),
                reverse=True
            )
            
            return bottlenecks[:10]  # Return top 10 bottlenecks
            
        except Exception as e:
            logger.error(f"Error detecting bottlenecks: {e}")
            return []
    
    async def _generate_optimization_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on profiling data"""
        recommendations = []
        
        try:
            # CPU-based recommendations
            cpu_summary = report.get("summary", {}).get("cpu", {})
            if cpu_summary:
                top_functions = cpu_summary.get("top_functions", [])
                if top_functions and top_functions[0].get("total_time", 0) > 1.0:
                    recommendations.append(
                        f"Optimize {top_functions[0].get('function', 'unknown')} - consuming most CPU time"
                    )
            
            # Memory-based recommendations
            memory_summary = report.get("summary", {}).get("memory", {})
            if memory_summary:
                peak_usage = memory_summary.get("peak_usage_mb", 0)
                if peak_usage > 1000:  # More than 1GB peak usage
                    recommendations.append("Consider implementing memory optimization strategies - peak usage exceeds 1GB")
            
            # Bottleneck-based recommendations
            bottlenecks = report.get("bottlenecks", [])
            high_priority_bottlenecks = [b for b in bottlenecks if b.get("optimization_level") == "high"]
            if high_priority_bottlenecks:
                recommendations.append(f"Address {len(high_priority_bottlenecks)} high-priority performance bottlenecks")
            
            # General recommendations
            if len(bottlenecks) > 5:
                recommendations.append("Consider implementing performance monitoring in production")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in bytes"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0
    
    async def _calculate_performance_summary(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """
Calculate performance summary from metrics"""
        if not metrics:
            return {}
        
        cpu_metrics = [m for m in metrics if m.profiler_type == ProfilerType.CPU]
        memory_metrics = [m for m in metrics if m.profiler_type == ProfilerType.MEMORY]
        
        summary = {
            "total_metrics": len(metrics),
            "period_start": min(m.timestamp for m in metrics).isoformat(),
            "period_end": max(m.timestamp for m in metrics).isoformat()
        }
        
        if cpu_metrics:
            cpu_values = [m.value for m in cpu_metrics]
            summary["cpu"] = {
                "avg_execution_time": statistics.mean(cpu_values),
                "max_execution_time": max(cpu_values),
                "total_functions_profiled": len(cpu_metrics)
            }
        
        return summary
    
    async def _get_top_functions_by_time(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top functions by execution time"""
        sorted_functions = sorted(
            self.function_stats.items(),
            key=lambda x: x[1].get("total_time", 0),
            reverse=True
        )
        
        return [
            {
                "function": func_name,
                "total_time": stats.get("total_time", 0),
                "total_calls": stats.get("total_calls", 0),
                "avg_time": stats.get("avg_time", 0)
            }
            for func_name, stats in sorted_functions[:limit]
        ]
    
    async def _analyze_memory_usage(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        # Simplified memory analysis
        return {
            "analysis_available": False,
            "reason": "Detailed memory analysis requires additional instrumentation"
        }
    
    async def _get_recent_bottlenecks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent bottleneck reports"""
        recent_bottlenecks = sorted(
            self.bottleneck_reports,
            key=lambda x: x.optimization_level.value,
            reverse=True
        )
        
        return [
            {
                "function": b.function_name,
                "optimization_level": b.optimization_level.value,
                "execution_time": b.execution_time,
                "recommendations": b.recommendations
            }
            for b in recent_bottlenecks[:limit]
        ]
    
    async def _calculate_performance_trends(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate performance trends"""
        # Simplified trend calculation
        return {
            "trends_available": False,
            "reason": "Trend analysis requires longer data collection period"
        }
    
    async def _get_performance_recommendations(self) -> List[str]:
        """Get general performance recommendations"""
        recommendations = []
        
        # Analyze current state
        if len(self.function_stats) > 100:
            recommendations.append("Large number of profiled functions - consider focusing on critical paths")
        
        high_time_functions = [
            name for name, stats in self.function_stats.items()
            if stats.get("avg_time", 0) > 0.5
        ]
        
        if high_time_functions:
            recommendations.append(f"Optimize {len(high_time_functions)} functions with high execution time")
        
        return recommendations
    
    def stop_monitoring(self) -> None:
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def get_profiler_stats(self) -> Dict[str, Any]:
        """Get profiler statistics"""
        return {
            "total_metrics": len(self.performance_metrics),
            "active_sessions": len([s for s in self.profiling_sessions.values() if s.get("active", False)]),
            "total_sessions": len(self.profiling_sessions),
            "function_stats_count": len(self.function_stats),
            "bottleneck_reports": len(self.bottleneck_reports),
            "monitoring_active": self.monitoring_active
        }


# Export classes
__all__ = [
    "PerformanceProfiler",
    "PerformanceMetric",
    "BottleneckReport",
    "ProfilerType",
    "OptimizationLevel"
]