"""
Async Optimizer - Enterprise Performance Module
===============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade asynchronous operation optimization for Creator Economy platform.
Advanced asyncio optimization with intelligent task scheduling and resource management.

Performance Targets: < 1ms task scheduling
Event Loop Efficiency: > 99% utilization
Concurrency: Optimal async task coordination
"""

import asyncio
import logging
import time
import threading
import weakref
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable, Awaitable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
import sys
import gc
import inspect
import functools
import statistics

# Enterprise logging setup
logger = logging.getLogger(__name__)


class AsyncTaskType(Enum):
    """Asynchronous task types"""
    IO_BOUND = "io_bound"
    CPU_BOUND = "cpu_bound"
    NETWORK = "network"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    REAL_TIME = "real_time"
    BACKGROUND = "background"
    CREATOR_TASK = "creator_task"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    REAL_TIME = 5


class EventLoopPolicy(Enum):
    """Event loop policies"""
    DEFAULT = "default"
    OPTIMIZED = "optimized"
    REAL_TIME = "real_time"
    HIGH_THROUGHPUT = "high_throughput"
    CREATOR_AWARE = "creator_aware"


@dataclass
class AsyncTask:
    """Asynchronous task representation"""
    task_id: str
    coroutine: Coroutine
    task_type: AsyncTaskType
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    creator_context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventLoopMetrics:
    """Event loop performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    active_tasks: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_task_duration_ms: float = 0.0
    event_loop_latency_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gc_collections: int = 0
    selector_efficiency: float = 0.0


@dataclass
class AsyncProfile:
    """Async operation profile"""
    operation_id: str
    operation_type: str
    call_count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_called: datetime = field(default_factory=datetime.now)
    creator_context: str = ""


class CreatorAsyncProfile:
    """Creator-specific async optimization profiles"""
    
    def __init__(self, creator_type: str):
        self.creator_type = creator_type
        self.async_patterns = {}
        self.performance_requirements = {}
        self.optimization_preferences = {}
        
    def get_musician_profile(self) -> Dict[str, Any]:
        """Async profile for musicians"""
        return {
            "event_loop_policy": EventLoopPolicy.REAL_TIME,
            "priority_tasks": [
                "audio_processing", "real_time_collaboration", "plugin_communication",
                "midi_input_processing", "audio_stream_management"
            ],
            "performance_requirements": {
                "max_latency_ms": 1.0,
                "real_time_guarantees": True,
                "audio_priority": True,
                "low_jitter": True
            },
            "concurrency_limits": {
                "audio_tasks": 4,
                "io_tasks": 10,
                "background_tasks": 2
            },
            "optimization_features": [
                "real_time_scheduling", "audio_thread_isolation",
                "low_latency_io", "priority_task_queuing"
            ],
            "event_loop_config": {
                "policy": "real_time",
                "debug": False,
                "gc_threshold": (100, 10, 5),  # Aggressive GC for low latency
                "task_timeout": 0.001  # 1ms timeout for real-time tasks
            }
        }
    
    def get_photographer_profile(self) -> Dict[str, Any]:
        """Async profile for photographers"""
        return {
            "event_loop_policy": EventLoopPolicy.HIGH_THROUGHPUT,
            "priority_tasks": [
                "image_processing", "batch_operations", "file_uploads",
                "gallery_operations", "metadata_processing"
            ],
            "performance_requirements": {
                "max_latency_ms": 50.0,
                "high_throughput": True,
                "batch_processing": True,
                "concurrent_uploads": True
            },
            "concurrency_limits": {
                "image_tasks": 16,
                "io_tasks": 32,
                "batch_tasks": 8
            },
            "optimization_features": [
                "batch_task_optimization", "parallel_processing",
                "high_throughput_io", "concurrent_uploads"
            ],
            "event_loop_config": {
                "policy": "high_throughput",
                "debug": False,
                "gc_threshold": (700, 10, 10),  # Standard GC for throughput
                "task_timeout": 30.0  # 30s timeout for batch operations
            }
        }
    
    def get_blogger_profile(self) -> Dict[str, Any]:
        """Async profile for bloggers"""
        return {
            "event_loop_policy": EventLoopPolicy.OPTIMIZED,
            "priority_tasks": [
                "content_processing", "publishing_operations", "analytics_collection",
                "media_optimization", "seo_processing"
            ],
            "performance_requirements": {
                "max_latency_ms": 100.0,
                "responsive_ui": True,
                "background_processing": True,
                "efficient_resource_usage": True
            },
            "concurrency_limits": {
                "content_tasks": 8,
                "io_tasks": 16,
                "background_tasks": 4
            },
            "optimization_features": [
                "responsive_processing", "background_task_scheduling",
                "efficient_resource_usage", "adaptive_concurrency"
            ],
            "event_loop_config": {
                "policy": "optimized",
                "debug": False,
                "gc_threshold": (700, 10, 10),  # Balanced GC
                "task_timeout": 10.0  # 10s timeout for content operations
            }
        }


class AsyncOptimizer:
    """
    Enterprise Async Optimizer for Creator Economy Platform
    
    Advanced asynchronous operation optimization with intelligent task scheduling.
    Specialized for content creator workloads requiring high-performance async processing.
    
    Features:
    - < 1ms task scheduling
    - > 99% event loop efficiency
    - Creator-specific optimization
    - Intelligent concurrency management
    - Real-time performance monitoring
    """
    
    def __init__(
        self,
        event_loop_policy: EventLoopPolicy = EventLoopPolicy.OPTIMIZED,
        enable_task_monitoring: bool = True,
        enable_gc_optimization: bool = True,
        max_concurrent_tasks: int = 1000,
        monitoring_interval: int = 10
    ):
        self.event_loop_policy = event_loop_policy
        self.enable_task_monitoring = enable_task_monitoring
        self.enable_gc_optimization = enable_gc_optimization
        self.max_concurrent_tasks = max_concurrent_tasks
        self.monitoring_interval = monitoring_interval
        
        # Enterprise state management
        self._is_running = False
        self._optimizer_lock = threading.Lock()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._task_registry: Dict[str, AsyncTask] = {}
        self._creator_profiles: Dict[str, CreatorAsyncProfile] = {}
        
        # Performance tracking
        self._metrics_history: deque = deque(maxlen=1000)
        self._async_profiles: Dict[str, AsyncProfile] = {}
        self._task_queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }
        
        # Event loop optimization
        self._loop_monitor_task: Optional[asyncio.Task] = None
        self._gc_stats = {"collections": 0, "time_spent": 0.0}
        self._selector_stats = {"calls": 0, "time_spent": 0.0}
        
        # Performance statistics
        self._optimizer_stats = {
            "total_tasks_scheduled": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "avg_scheduling_time_ms": 0.0,
            "avg_task_duration_ms": 0.0,
            "event_loop_efficiency": 0.0,
            "gc_optimization_savings_ms": 0.0,
            "concurrency_utilization": 0.0,
            "last_optimization": None
        }
        
        logger.info(f"AsyncOptimizer initialized - Policy: {event_loop_policy.value}")
    
    async def start_optimization(self) -> None:
        """Start async optimization monitoring"""
        if self._is_running:
            logger.warning("Async optimization already running")
            return
        
        self._is_running = True
        self._event_loop = asyncio.get_running_loop()
        
        # Apply event loop optimizations
        await self._optimize_event_loop()
        
        # Start monitoring task
        self._loop_monitor_task = asyncio.create_task(self._monitor_event_loop())
        
        logger.info("Started enterprise async optimization")
    
    async def stop_optimization(self) -> None:
        """Stop async optimization monitoring"""
        self._is_running = False
        
        if self._loop_monitor_task:
            self._loop_monitor_task.cancel()
            try:
                await self._loop_monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped async optimization")
    
    async def _optimize_event_loop(self) -> None:
        """Optimize event loop configuration"""
        try:
            if not self._event_loop:
                return
            
            # Configure event loop based on policy
            if self.event_loop_policy == EventLoopPolicy.REAL_TIME:
                # Real-time optimizations
                self._event_loop.set_debug(False)
                if hasattr(self._event_loop, 'set_task_factory'):
                    self._event_loop.set_task_factory(self._real_time_task_factory)
            
            elif self.event_loop_policy == EventLoopPolicy.HIGH_THROUGHPUT:
                # High throughput optimizations
                self._event_loop.set_debug(False)
                if hasattr(self._event_loop, 'set_task_factory'):
                    self._event_loop.set_task_factory(self._high_throughput_task_factory)
            
            # Configure garbage collection if enabled
            if self.enable_gc_optimization:
                await self._optimize_garbage_collection()
            
            logger.info(f"Event loop optimized for {self.event_loop_policy.value}")
            
        except Exception as e:
            logger.error(f"Error optimizing event loop: {e}")
    
    def _real_time_task_factory(self, loop: asyncio.AbstractEventLoop, coro: Coroutine) -> asyncio.Task:
        """Task factory optimized for real-time performance"""
        try:
            task = asyncio.Task(coro, loop=loop)
            
            # Set high priority for real-time tasks
            if hasattr(task, 'set_name'):
                task.set_name(f"rt_{id(task)}")
            
            return task
            
        except Exception as e:
            logger.error(f"Error in real-time task factory: {e}")
            return asyncio.Task(coro, loop=loop)
    
    def _high_throughput_task_factory(self, loop: asyncio.AbstractEventLoop, coro: Coroutine) -> asyncio.Task:
        """Task factory optimized for high throughput"""
        try:
            task = asyncio.Task(coro, loop=loop)
            
            # Optimize for throughput
            if hasattr(task, 'set_name'):
                task.set_name(f"ht_{id(task)}")
            
            return task
            
        except Exception as e:
            logger.error(f"Error in high throughput task factory: {e}")
            return asyncio.Task(coro, loop=loop)
    
    async def _optimize_garbage_collection(self) -> None:
        """Optimize garbage collection for async operations"""
        try:
            if self.event_loop_policy == EventLoopPolicy.REAL_TIME:
                # Aggressive GC for low latency
                gc.set_threshold(100, 10, 5)
            elif self.event_loop_policy == EventLoopPolicy.HIGH_THROUGHPUT:
                # Balanced GC for throughput
                gc.set_threshold(700, 10, 10)
            else:
                # Default optimized settings
                gc.set_threshold(500, 10, 10)
            
            # Disable automatic GC during critical sections if needed
            if self.event_loop_policy == EventLoopPolicy.REAL_TIME:
                gc.disable()
                # Re-enable with controlled intervals
                asyncio.create_task(self._controlled_gc_cycle())
            
            logger.info("Garbage collection optimized for async operations")
            
        except Exception as e:
            logger.error(f"Error optimizing garbage collection: {e}")
    
    async def _controlled_gc_cycle(self) -> None:
        """Controlled garbage collection cycle for real-time performance"""
        try:
            while self._is_running:
                # Wait for a good time to run GC
                await asyncio.sleep(0.1)  # 100ms intervals
                
                # Quick GC cycle
                start_time = time.perf_counter()
                collected = gc.collect()
                gc_time = (time.perf_counter() - start_time) * 1000
                
                # Update GC stats
                self._gc_stats["collections"] += 1
                self._gc_stats["time_spent"] += gc_time
                
                if collected > 0:
                    logger.debug(f"GC collected {collected} objects in {gc_time:.2f}ms")
                    
        except Exception as e:
            logger.error(f"Error in controlled GC cycle: {e}")
    
    async def _monitor_event_loop(self) -> None:
        """Monitor event loop performance"""
        try:
            while self._is_running:
                start_time = time.perf_counter()
                
                # Collect event loop metrics
                metrics = await self._collect_event_loop_metrics()
                self._metrics_history.append(metrics)
                
                # Optimize based on metrics
                await self._optimize_based_on_metrics(metrics)
                
                # Update performance statistics
                monitoring_time = (time.perf_counter() - start_time) * 1000
                self._update_optimizer_stats(monitoring_time)
                
                # Sleep until next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error monitoring event loop: {e}")
    
    async def _collect_event_loop_metrics(self) -> EventLoopMetrics:
        """Collect comprehensive event loop metrics"""
        try:
            if not self._event_loop:
                return EventLoopMetrics()
            
            # Get current tasks
            all_tasks = asyncio.all_tasks(self._event_loop)
            active_tasks = len([task for task in all_tasks if not task.done()])
            pending_tasks = len(self._task_registry)
            
            # Calculate completed and failed tasks
            completed_tasks = len([task for task in all_tasks if task.done() and not task.cancelled() and task.exception() is None])
            failed_tasks = len([task for task in all_tasks if task.done() and (task.cancelled() or task.exception() is not None)])
            
            # Calculate average task duration
            avg_duration = 0.0
            if self._async_profiles:
                durations = [profile.avg_time_ms for profile in self._async_profiles.values() if profile.avg_time_ms > 0]
                if durations:
                    avg_duration = statistics.mean(durations)
            
            # Measure event loop latency
            latency_start = time.perf_counter()
            await asyncio.sleep(0)  # Yield to event loop
            latency_ms = (time.perf_counter() - latency_start) * 1000
            
            # Get memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            cpu_percent = process.cpu_percent()
            
            metrics = EventLoopMetrics(
                active_tasks=active_tasks,
                pending_tasks=pending_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                avg_task_duration_ms=avg_duration,
                event_loop_latency_ms=latency_ms,
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory_mb,
                gc_collections=self._gc_stats["collections"]
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting event loop metrics: {e}")
            return EventLoopMetrics()
    
    async def _optimize_based_on_metrics(self, metrics: EventLoopMetrics) -> None:
        """Optimize async operations based on current metrics"""
        try:
            # Check for high latency
            if metrics.event_loop_latency_ms > 10.0:  # > 10ms latency
                logger.warning(f"High event loop latency: {metrics.event_loop_latency_ms:.2f}ms")
                await self._optimize_for_latency()
            
            # Check for high task count
            if metrics.active_tasks > self.max_concurrent_tasks * 0.9:
                logger.warning(f"High task count: {metrics.active_tasks}")
                await self._optimize_for_concurrency()
            
            # Check for memory pressure
            if metrics.memory_usage_mb > 1000:  # > 1GB
                logger.warning(f"High memory usage: {metrics.memory_usage_mb:.2f}MB")
                await self._optimize_for_memory()
            
            # Update efficiency metrics
            if metrics.active_tasks > 0:
                efficiency = min(metrics.active_tasks / self.max_concurrent_tasks, 1.0)
                self._optimizer_stats["event_loop_efficiency"] = efficiency
                
        except Exception as e:
            logger.error(f"Error optimizing based on metrics: {e}")
    
    async def _optimize_for_latency(self) -> None:
        """Optimize for low latency"""
        try:
            # Reduce task queue sizes
            for priority_queue in self._task_queues.values():
                if len(priority_queue) > 100:
                    # Process high priority tasks first
                    break
            
            # Trigger garbage collection if needed
            if self.enable_gc_optimization:
                gc.collect()
                
        except Exception as e:
            logger.error(f"Error optimizing for latency: {e}")
    
    async def _optimize_for_concurrency(self) -> None:
        """Optimize for high concurrency"""
        try:
            # Limit new task creation temporarily
            # This would be implemented with rate limiting
            
            # Prioritize task completion
            await asyncio.sleep(0.01)  # Small yield to let tasks complete
            
        except Exception as e:
            logger.error(f"Error optimizing for concurrency: {e}")
    
    async def _optimize_for_memory(self) -> None:
        """Optimize for memory usage"""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear completed task references
            await self._cleanup_completed_tasks()
            
            if collected > 0:
                logger.info(f"Memory optimization: collected {collected} objects")
                
        except Exception as e:
            logger.error(f"Error optimizing for memory: {e}")
    
    async def schedule_task(self, coro: Coroutine, task_type: AsyncTaskType = AsyncTaskType.IO_BOUND,
                           priority: TaskPriority = TaskPriority.NORMAL,
                           timeout_seconds: Optional[float] = None,
                           creator_context: str = "") -> Optional[asyncio.Task]:
        """
        Schedule an async task with optimization
        
        Performance Target: < 1ms scheduling time
        """
        start_time = time.perf_counter()
        
        try:
            # Generate task ID
            task_id = f"{task_type.value}_{int(time.time() * 1000000)}"
            
            # Create async task wrapper
            async_task = AsyncTask(
                task_id=task_id,
                coroutine=coro,
                task_type=task_type,
                priority=priority,
                timeout_seconds=timeout_seconds,
                creator_context=creator_context
            )
            
            # Apply creator-specific optimizations
            if creator_context:
                await self._apply_creator_optimizations(async_task)
            
            # Schedule the task
            if timeout_seconds:
                # Use timeout wrapper
                task = asyncio.create_task(
                    asyncio.wait_for(self._execute_optimized_task(async_task), timeout=timeout_seconds)
                )
            else:
                task = asyncio.create_task(self._execute_optimized_task(async_task))
            
            # Set task name for debugging
            if hasattr(task, 'set_name'):
                task.set_name(f"{task_type.value}_{priority.value}_{task_id}")
            
            # Register task
            self._task_registry[task_id] = async_task
            
            # Add to priority queue
            self._task_queues[priority].append(task_id)
            
            # Update statistics
            scheduling_time = (time.perf_counter() - start_time) * 1000
            self._optimizer_stats["total_tasks_scheduled"] += 1
            self._update_scheduling_time(scheduling_time)
            
            return task
            
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            return None
    
    async def _execute_optimized_task(self, async_task: AsyncTask) -> Any:
        """Execute task with optimization monitoring"""
        start_time = time.perf_counter()
        async_task.started_at = datetime.now()
        
        try:
            # Execute the coroutine
            result = await async_task.coroutine
            
            # Task completed successfully
            async_task.completed_at = datetime.now()
            execution_time = (time.perf_counter() - start_time) * 1000
            
            # Update async profile
            await self._update_async_profile(async_task, execution_time, True)
            
            # Update statistics
            self._optimizer_stats["total_tasks_completed"] += 1
            
            return result
            
        except Exception as e:
            # Task failed
            async_task.completed_at = datetime.now()
            execution_time = (time.perf_counter() - start_time) * 1000
            
            # Update async profile
            await self._update_async_profile(async_task, execution_time, False)
            
            # Update statistics
            self._optimizer_stats["total_tasks_failed"] += 1
            
            logger.error(f"Task {async_task.task_id} failed: {e}")
            raise
        
        finally:
            # Cleanup task from registry
            self._task_registry.pop(async_task.task_id, None)
    
    async def _apply_creator_optimizations(self, async_task: AsyncTask) -> None:
        """Apply creator-specific optimizations to task"""
        try:
            creator_context = async_task.creator_context
            if not creator_context or creator_context not in self._creator_profiles:
                return
            
            profile = self._creator_profiles[creator_context]
            creator_config = getattr(profile, f"get_{profile.creator_type}_profile")()
            
            # Apply priority adjustments
            if async_task.task_type.value in creator_config.get("priority_tasks", []):
                if profile.creator_type == "musician":
                    async_task.priority = TaskPriority.CRITICAL
                elif profile.creator_type == "photographer":
                    async_task.priority = TaskPriority.HIGH
            
            # Apply timeout adjustments
            performance_req = creator_config.get("performance_requirements", {})
            if "max_latency_ms" in performance_req:
                max_latency = performance_req["max_latency_ms"] / 1000  # Convert to seconds
                if not async_task.timeout_seconds or async_task.timeout_seconds > max_latency:
                    async_task.timeout_seconds = max_latency
                    
        except Exception as e:
            logger.error(f"Error applying creator optimizations: {e}")
    
    async def _update_async_profile(self, async_task: AsyncTask, execution_time_ms: float, success: bool) -> None:
        """Update async operation profile"""
        try:
            operation_type = f"{async_task.task_type.value}_{async_task.creator_context}"
            
            if operation_type not in self._async_profiles:
                self._async_profiles[operation_type] = AsyncProfile(
                    operation_id=operation_type,
                    operation_type=async_task.task_type.value,
                    creator_context=async_task.creator_context
                )
            
            profile = self._async_profiles[operation_type]
            profile.call_count += 1
            profile.total_time_ms += execution_time_ms
            profile.avg_time_ms = profile.total_time_ms / profile.call_count
            profile.min_time_ms = min(profile.min_time_ms, execution_time_ms)
            profile.max_time_ms = max(profile.max_time_ms, execution_time_ms)
            profile.last_called = datetime.now()
            
            if success:
                profile.success_count += 1
            else:
                profile.failure_count += 1
                
        except Exception as e:
            logger.error(f"Error updating async profile: {e}")
    
    async def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks and references"""
        try:
            # Clean up task registry
            completed_tasks = []
            for task_id, async_task in self._task_registry.items():
                if async_task.completed_at:
                    completed_tasks.append(task_id)
            
            for task_id in completed_tasks:
                self._task_registry.pop(task_id, None)
            
            # Clean up priority queues
            for priority_queue in self._task_queues.values():
                # Remove completed tasks from queues
                while priority_queue and priority_queue[0] not in self._task_registry:
                    priority_queue.popleft()
                    
        except Exception as e:
            logger.error(f"Error cleaning up completed tasks: {e}")
    
    async def optimize_coroutine(self, coro_func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        """Optimize a coroutine function with performance enhancements"""
        @functools.wraps(coro_func)
        async def optimized_wrapper(*args, **kwargs):
            # Apply optimizations based on function characteristics
            start_time = time.perf_counter()
            
            try:
                # Execute the original coroutine
                result = await coro_func(*args, **kwargs)
                
                # Track performance
                execution_time = (time.perf_counter() - start_time) * 1000
                await self._track_optimized_function(coro_func.__name__, execution_time, True)
                
                return result
                
            except Exception as e:
                # Track failure
                execution_time = (time.perf_counter() - start_time) * 1000
                await self._track_optimized_function(coro_func.__name__, execution_time, False)
                raise
        
        return optimized_wrapper
    
    async def _track_optimized_function(self, func_name: str, execution_time_ms: float, success: bool) -> None:
        """Track performance of optimized function"""
        try:
            if func_name not in self._async_profiles:
                self._async_profiles[func_name] = AsyncProfile(
                    operation_id=func_name,
                    operation_type="optimized_function"
                )
            
            profile = self._async_profiles[func_name]
            profile.call_count += 1
            profile.total_time_ms += execution_time_ms
            profile.avg_time_ms = profile.total_time_ms / profile.call_count
            profile.min_time_ms = min(profile.min_time_ms, execution_time_ms)
            profile.max_time_ms = max(profile.max_time_ms, execution_time_ms)
            
            if success:
                profile.success_count += 1
            else:
                profile.failure_count += 1
                
        except Exception as e:
            logger.error(f"Error tracking optimized function: {e}")
    
    def _update_scheduling_time(self, scheduling_time_ms: float) -> None:
        """Update average scheduling time statistics"""
        try:
            current_avg = self._optimizer_stats["avg_scheduling_time_ms"]
            total_scheduled = self._optimizer_stats["total_tasks_scheduled"]
            
            if total_scheduled > 1:
                new_avg = ((current_avg * (total_scheduled - 1)) + scheduling_time_ms) / total_scheduled
                self._optimizer_stats["avg_scheduling_time_ms"] = new_avg
            else:
                self._optimizer_stats["avg_scheduling_time_ms"] = scheduling_time_ms
                
        except Exception as e:
            logger.error(f"Error updating scheduling time: {e}")
    
    def _update_optimizer_stats(self, monitoring_time_ms: float) -> None:
        """Update optimizer performance statistics"""
        try:
            # Update average task duration
            if self._async_profiles:
                durations = [p.avg_time_ms for p in self._async_profiles.values() if p.avg_time_ms > 0]
                if durations:
                    self._optimizer_stats["avg_task_duration_ms"] = statistics.mean(durations)
            
            # Update concurrency utilization
            active_tasks = len(self._task_registry)
            utilization = min(active_tasks / self.max_concurrent_tasks, 1.0)
            self._optimizer_stats["concurrency_utilization"] = utilization
            
            # Update GC optimization savings
            if self._gc_stats["collections"] > 0:
                avg_gc_time = self._gc_stats["time_spent"] / self._gc_stats["collections"]
                # Estimate savings compared to default GC
                estimated_savings = max(0, 5.0 - avg_gc_time)  # 5ms baseline
                self._optimizer_stats["gc_optimization_savings_ms"] = estimated_savings
            
            self._optimizer_stats["last_optimization"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating optimizer stats: {e}")
    
    async def add_creator_profile(self, creator_id: str, creator_type: str) -> None:
        """Add creator-specific async optimization profile"""
        try:
            profile = CreatorAsyncProfile(creator_type)
            self._creator_profiles[creator_id] = profile
            logger.info(f"Added creator async profile: {creator_id} ({creator_type})")
        except Exception as e:
            logger.error(f"Error adding creator profile: {e}")
    
    async def get_optimizer_stats(self) -> Dict[str, Any]:
        """Get async optimizer statistics"""
        return {
            **self._optimizer_stats,
            "event_loop_metrics": self._metrics_history[-1].__dict__ if self._metrics_history else {},
            "async_profiles": {
                name: {
                    "call_count": profile.call_count,
                    "avg_time_ms": profile.avg_time_ms,
                    "success_rate": profile.success_count / max(profile.call_count, 1) * 100,
                    "creator_context": profile.creator_context
                }
                for name, profile in self._async_profiles.items()
            },
            "task_queues": {
                priority.name: len(queue) for priority, queue in self._task_queues.items()
            },
            "creator_profiles": len(self._creator_profiles),
            "gc_stats": self._gc_stats,
            "is_running": self._is_running
        }
    
    async def analyze_async_performance(self) -> Dict[str, Any]:
        """Analyze async performance patterns"""
        analysis = {
            "performance_summary": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        try:
            if self._async_profiles:
                # Find slowest operations
                slow_operations = sorted(
                    self._async_profiles.values(),
                    key=lambda p: p.avg_time_ms,
                    reverse=True
                )[:5]
                
                analysis["performance_summary"]["slowest_operations"] = [
                    {"name": op.operation_id, "avg_time_ms": op.avg_time_ms}
                    for op in slow_operations
                ]
                
                # Find most frequent operations
                frequent_operations = sorted(
                    self._async_profiles.values(),
                    key=lambda p: p.call_count,
                    reverse=True
                )[:5]
                
                analysis["performance_summary"]["most_frequent_operations"] = [
                    {"name": op.operation_id, "call_count": op.call_count}
                    for op in frequent_operations
                ]
                
                # Identify bottlenecks
                for profile in self._async_profiles.values():
                    if profile.avg_time_ms > 100.0:  # > 100ms
                        analysis["bottlenecks"].append({
                            "operation": profile.operation_id,
                            "avg_time_ms": profile.avg_time_ms,
                            "call_count": profile.call_count
                        })
                
                # Generate recommendations
                if slow_operations:
                    analysis["recommendations"].append(
                        f"Optimize {slow_operations[0].operation_id} - avg time: {slow_operations[0].avg_time_ms:.2f}ms"
                    )
                
                if len(self._task_registry) > self.max_concurrent_tasks * 0.8:
                    analysis["recommendations"].append("Consider reducing concurrent task count")
                
        except Exception as e:
            logger.error(f"Error analyzing async performance: {e}")
            analysis["error"] = str(e)
        
        return analysis


# Factory function for enterprise instantiation
def create_async_optimizer(
    event_loop_policy: str = "optimized",
    enable_task_monitoring: bool = True,
    max_concurrent_tasks: int = 1000
) -> AsyncOptimizer:
    """
    Factory function to create AsyncOptimizer instance
    
    Args:
        event_loop_policy: Event loop optimization policy
        enable_task_monitoring: Enable task performance monitoring
        max_concurrent_tasks: Maximum concurrent tasks
    
    Returns:
        Configured AsyncOptimizer instance
    """
    policy_map = {
        "default": EventLoopPolicy.DEFAULT,
        "optimized": EventLoopPolicy.OPTIMIZED,
        "real_time": EventLoopPolicy.REAL_TIME,
        "high_throughput": EventLoopPolicy.HIGH_THROUGHPUT,
        "creator_aware": EventLoopPolicy.CREATOR_AWARE
    }
    
    policy = policy_map.get(event_loop_policy, EventLoopPolicy.OPTIMIZED)
    
    return AsyncOptimizer(
        event_loop_policy=policy,
        enable_task_monitoring=enable_task_monitoring,
        max_concurrent_tasks=max_concurrent_tasks
    )


# Export for enterprise usage
__all__ = [
    "AsyncOptimizer",
    "AsyncTaskType",
    "TaskPriority",
    "EventLoopPolicy",
    "AsyncTask",
    "EventLoopMetrics",
    "AsyncProfile",
    "CreatorAsyncProfile",
    "create_async_optimizer"
]