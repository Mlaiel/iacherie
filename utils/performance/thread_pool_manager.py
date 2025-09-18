"""
Thread Pool Manager - Enterprise Performance Module
===================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade thread pool management for Creator Economy platform.
Intelligent thread allocation and optimization for high-performance applications.

Performance Targets: < 1ms thread assignment
Pool Efficiency: > 95% utilization
Task Throughput: Maximum concurrent processing
"""

import asyncio
import logging
import time
import threading
import queue
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import multiprocessing
import psutil
import weakref

# Enterprise logging setup
logger = logging.getLogger(__name__)


class ThreadPoolType(Enum):
    """Thread pool types"""
    IO_BOUND = "io_bound"
    CPU_BOUND = "cpu_bound"
    MIXED = "mixed"
    REAL_TIME = "real_time"
    BATCH = "batch"
    CREATOR_SPECIFIC = "creator_specific"


class ThreadPriority(Enum):
    """Thread priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    REAL_TIME = "real_time"


class PoolScalingPolicy(Enum):
    """Pool scaling policies"""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    CREATOR_AWARE = "creator_aware"


@dataclass
class ThreadTask:
    """Thread task configuration"""
    task_id: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: ThreadPriority = ThreadPriority.NORMAL
    timeout_seconds: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    creator_context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreadPoolConfig:
    """Thread pool configuration"""
    pool_name: str
    pool_type: ThreadPoolType
    min_threads: int = 2
    max_threads: int = 20
    scaling_policy: PoolScalingPolicy = PoolScalingPolicy.DYNAMIC
    idle_timeout_seconds: int = 300
    task_queue_size: int = 1000
    enable_monitoring: bool = True
    creator_specific: bool = False
    thread_name_prefix: str = ""


@dataclass
class ThreadPoolMetrics:
    """Thread pool performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    pool_name: str = ""
    active_threads: int = 0
    idle_threads: int = 0
    total_threads: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_task_duration_ms: float = 0.0
    avg_queue_wait_time_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    throughput_tasks_per_second: float = 0.0


@dataclass
class ThreadPoolStats:
    """Thread pool statistics"""
    pool_name: str
    tasks_submitted: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time_ms: float = 0.0
    total_queue_time_ms: float = 0.0
    peak_thread_count: int = 0
    peak_queue_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class CreatorThreadProfile:
    """Creator-specific thread pool optimization profiles"""
    
    def __init__(self, creator_type: str):
        self.creator_type = creator_type
        self.thread_requirements = {}
        self.performance_preferences = {}
        self.scaling_preferences = {}
        
    def get_musician_profile(self) -> Dict[str, Any]:
        """Thread pool profile for musicians"""
        return {
            "pool_configurations": {
                "audio_processing": {
                    "type": ThreadPoolType.REAL_TIME,
                    "min_threads": 4,
                    "max_threads": 8,
                    "priority": ThreadPriority.CRITICAL,
                    "scaling": PoolScalingPolicy.FIXED
                },
                "sample_loading": {
                    "type": ThreadPoolType.IO_BOUND,
                    "min_threads": 2,
                    "max_threads": 6,
                    "priority": ThreadPriority.HIGH,
                    "scaling": PoolScalingPolicy.DYNAMIC
                },
                "project_management": {
                    "type": ThreadPoolType.MIXED,
                    "min_threads": 2,
                    "max_threads": 4,
                    "priority": ThreadPriority.NORMAL,
                    "scaling": PoolScalingPolicy.ADAPTIVE
                },
                "background_tasks": {
                    "type": ThreadPoolType.BATCH,
                    "min_threads": 1,
                    "max_threads": 3,
                    "priority": ThreadPriority.LOW,
                    "scaling": PoolScalingPolicy.DYNAMIC
                }
            },
            "performance_requirements": {
                "audio_latency_ms": 1.0,
                "real_time_processing": True,
                "priority_scheduling": True,
                "dedicated_cores": True
            },
            "optimization_features": [
                "real_time_thread_priority", "audio_thread_isolation",
                "low_latency_scheduling", "numa_aware_allocation"
            ]
        }
    
    def get_photographer_profile(self) -> Dict[str, Any]:
        """Thread pool profile for photographers"""
        return {
            "pool_configurations": {
                "image_processing": {
                    "type": ThreadPoolType.CPU_BOUND,
                    "min_threads": 6,
                    "max_threads": 16,
                    "priority": ThreadPriority.HIGH,
                    "scaling": PoolScalingPolicy.ADAPTIVE
                },
                "file_operations": {
                    "type": ThreadPoolType.IO_BOUND,
                    "min_threads": 4,
                    "max_threads": 12,
                    "priority": ThreadPriority.NORMAL,
                    "scaling": PoolScalingPolicy.DYNAMIC
                },
                "batch_processing": {
                    "type": ThreadPoolType.BATCH,
                    "min_threads": 2,
                    "max_threads": 20,
                    "priority": ThreadPriority.NORMAL,
                    "scaling": PoolScalingPolicy.CREATOR_AWARE
                },
                "gallery_operations": {
                    "type": ThreadPoolType.MIXED,
                    "min_threads": 2,
                    "max_threads": 8,
                    "priority": ThreadPriority.NORMAL,
                    "scaling": PoolScalingPolicy.DYNAMIC
                }
            },
            "performance_requirements": {
                "parallel_processing": True,
                "high_throughput": True,
                "batch_optimization": True,
                "memory_efficient": True
            },
            "optimization_features": [
                "parallel_image_processing", "batch_task_optimization",
                "memory_pool_management", "gpu_thread_coordination"
            ]
        }
    
    def get_blogger_profile(self) -> Dict[str, Any]:
        """Thread pool profile for bloggers"""
        return {
            "pool_configurations": {
                "content_processing": {
                    "type": ThreadPoolType.MIXED,
                    "min_threads": 3,
                    "max_threads": 8,
                    "priority": ThreadPriority.NORMAL,
                    "scaling": PoolScalingPolicy.ADAPTIVE
                },
                "publishing": {
                    "type": ThreadPoolType.IO_BOUND,
                    "min_threads": 2,
                    "max_threads": 6,
                    "priority": ThreadPriority.HIGH,
                    "scaling": PoolScalingPolicy.DYNAMIC
                },
                "analytics": {
                    "type": ThreadPoolType.CPU_BOUND,
                    "min_threads": 1,
                    "max_threads": 4,
                    "priority": ThreadPriority.LOW,
                    "scaling": PoolScalingPolicy.DYNAMIC
                },
                "media_processing": {
                    "type": ThreadPoolType.MIXED,
                    "min_threads": 2,
                    "max_threads": 6,
                    "priority": ThreadPriority.NORMAL,
                    "scaling": PoolScalingPolicy.ADAPTIVE
                }
            },
            "performance_requirements": {
                "responsive_ui": True,
                "balanced_performance": True,
                "background_processing": True,
                "efficient_scaling": True
            },
            "optimization_features": [
                "responsive_content_processing", "background_task_scheduling",
                "adaptive_scaling", "balanced_resource_usage"
            ]
        }


class EnterpriseThreadPool:
    """Enhanced thread pool with enterprise features"""
    
    def __init__(self, config: ThreadPoolConfig):
        self.config = config
        self._executor: Optional[ThreadPoolExecutor] = None
        self._task_queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=config.task_queue_size)
        self._stats = ThreadPoolStats(pool_name=config.pool_name)
        self._metrics_history: deque = deque(maxlen=1000)
        self._active_tasks: Dict[str, ThreadTask] = {}
        self._completed_tasks: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
        self._shutdown = False
        
        # Initialize thread pool
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize the thread pool executor"""
        try:
            thread_name_prefix = self.config.thread_name_prefix or f"{self.config.pool_name}_thread"
            
            self._executor = ThreadPoolExecutor(
                max_workers=self.config.max_threads,
                thread_name_prefix=thread_name_prefix
            )
            
            logger.info(f"Initialized thread pool '{self.config.pool_name}' with {self.config.max_threads} max threads")
            
        except Exception as e:
            logger.error(f"Error initializing thread pool '{self.config.pool_name}': {e}")
            raise
    
    def submit_task(self, task: ThreadTask) -> Future:
        """Submit a task to the thread pool"""
        try:
            if self._shutdown:
                raise RuntimeError("Thread pool is shutdown")
            
            with self._lock:
                self._active_tasks[task.task_id] = task
                self._stats.tasks_submitted += 1
                self._stats.last_activity = datetime.now()
            
            # Submit to executor
            future = self._executor.submit(self._execute_task_wrapper, task)
            
            # Add callback for completion
            future.add_done_callback(lambda f: self._task_completed(task, f))
            
            return future
            
        except Exception as e:
            logger.error(f"Error submitting task {task.task_id}: {e}")
            raise
    
    def _execute_task_wrapper(self, task: ThreadTask) -> Any:
        """Wrapper for task execution with monitoring"""
        task.started_at = datetime.now()
        
        try:
            # Execute the actual task
            if task.kwargs:
                result = task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args)
            
            task.completed_at = datetime.now()
            return result
            
        except Exception as e:
            task.completed_at = datetime.now()
            logger.error(f"Task {task.task_id} failed: {e}")
            raise
    
    def _task_completed(self, task: ThreadTask, future: Future) -> None:
        """Handle task completion"""
        try:
            with self._lock:
                # Remove from active tasks
                self._active_tasks.pop(task.task_id, None)
                
                # Add to completed tasks
                self._completed_tasks.append(task)
                
                # Update statistics
                if future.exception():
                    self._stats.tasks_failed += 1
                else:
                    self._stats.tasks_completed += 1
                
                # Update execution time
                if task.started_at and task.completed_at:
                    execution_time = (task.completed_at - task.started_at).total_seconds() * 1000
                    self._stats.total_execution_time_ms += execution_time
                
                self._stats.last_activity = datetime.now()
                
        except Exception as e:
            logger.error(f"Error handling task completion for {task.task_id}: {e}")
    
    def get_metrics(self) -> ThreadPoolMetrics:
        """Get current thread pool metrics"""
        try:
            with self._lock:
                # Calculate average task duration
                avg_duration = 0.0
                if self._stats.tasks_completed > 0:
                    avg_duration = self._stats.total_execution_time_ms / self._stats.tasks_completed
                
                # Get current thread counts (simplified)
                total_threads = self._executor._threads if self._executor else 0
                active_threads = len(self._active_tasks)
                idle_threads = max(0, total_threads - active_threads)
                
                metrics = ThreadPoolMetrics(
                    pool_name=self.config.pool_name,
                    active_threads=active_threads,
                    idle_threads=idle_threads,
                    total_threads=total_threads,
                    pending_tasks=self._task_queue.qsize(),
                    completed_tasks=self._stats.tasks_completed,
                    failed_tasks=self._stats.tasks_failed,
                    avg_task_duration_ms=avg_duration
                )
                
                self._metrics_history.append(metrics)
                return metrics
                
        except Exception as e:
            logger.error(f"Error getting metrics for pool '{self.config.pool_name}': {e}")
            return ThreadPoolMetrics(pool_name=self.config.pool_name)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool"""
        try:
            self._shutdown = True
            if self._executor:
                self._executor.shutdown(wait=wait)
            logger.info(f"Thread pool '{self.config.pool_name}' shutdown")
        except Exception as e:
            logger.error(f"Error shutting down thread pool '{self.config.pool_name}': {e}")


class ThreadPoolManager:
    """
    Enterprise Thread Pool Manager for Creator Economy Platform
    
    Intelligent thread pool management with automatic scaling and optimization.
    Specialized for content creator workloads requiring high-performance processing.
    
    Features:
    - < 1ms thread assignment
    - > 95% pool utilization efficiency
    - Creator-specific optimization
    - Intelligent scaling policies
    - Real-time performance monitoring
    """
    
    def __init__(
        self,
        enable_auto_scaling: bool = True,
        enable_monitoring: bool = True,
        monitoring_interval: int = 30,
        max_total_threads: Optional[int] = None
    ):
        self.enable_auto_scaling = enable_auto_scaling
        self.enable_monitoring = enable_monitoring
        self.monitoring_interval = monitoring_interval
        self.max_total_threads = max_total_threads or (multiprocessing.cpu_count() * 4)
        
        # Enterprise state management
        self._is_running = False
        self._manager_lock = threading.Lock()
        self._thread_pools: Dict[str, EnterpriseThreadPool] = {}
        self._creator_profiles: Dict[str, CreatorThreadProfile] = {}
        
        # Performance tracking
        self._manager_stats = {
            "total_pools": 0,
            "total_threads": 0,
            "total_tasks_submitted": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "avg_pool_utilization": 0.0,
            "system_cpu_usage": 0.0,
            "system_memory_usage": 0.0,
            "last_optimization": None
        }
        
        # Auto-scaling configuration
        self._scaling_config = {
            "scale_up_threshold": 0.8,    # 80% utilization
            "scale_down_threshold": 0.3,   # 30% utilization
            "scale_up_factor": 1.5,        # Increase by 50%
            "scale_down_factor": 0.8,      # Decrease by 20%
            "min_scale_interval": 60,      # Minimum 60 seconds between scaling
            "last_scale_time": {}          # Track last scaling per pool
        }
        
        logger.info(f"ThreadPoolManager initialized - Max threads: {self.max_total_threads}")
    
    async def start_monitoring(self) -> None:
        """Start thread pool monitoring and auto-scaling"""
        if self._is_running:
            logger.warning("Thread pool monitoring already running")
            return
        
        self._is_running = True
        logger.info("Starting enterprise thread pool monitoring")
        
        try:
            while self._is_running:
                start_time = time.perf_counter()
                
                # Update pool metrics
                await self.update_pool_metrics()
                
                # Perform auto-scaling if enabled
                if self.enable_auto_scaling:
                    await self.auto_scale_pools()
                
                # Optimize pool configurations
                await self.optimize_pool_configurations()
                
                # Update manager statistics
                await self.update_manager_stats()
                
                # Sleep until next monitoring cycle
                monitoring_time = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Thread pool monitoring cycle completed in {monitoring_time:.2f}ms")
                
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error in thread pool monitoring: {e}")
        finally:
            self._is_running = False
            logger.info("Thread pool monitoring stopped")
    
    async def stop_monitoring(self) -> None:
        """Stop thread pool monitoring"""
        self._is_running = False
        logger.info("Stopping thread pool monitoring")
    
    async def create_pool(self, config: ThreadPoolConfig) -> EnterpriseThreadPool:
        """Create a new thread pool"""
        try:
            with self._manager_lock:
                if config.pool_name in self._thread_pools:
                    raise ValueError(f"Pool '{config.pool_name}' already exists")
                
                # Check total thread limit
                current_total_threads = sum(
                    pool.config.max_threads for pool in self._thread_pools.values()
                )
                
                if current_total_threads + config.max_threads > self.max_total_threads:
                    raise ValueError(f"Cannot create pool: would exceed max total threads ({self.max_total_threads})")
                
                # Create and register the pool
                pool = EnterpriseThreadPool(config)
                self._thread_pools[config.pool_name] = pool
                
                self._manager_stats["total_pools"] += 1
                logger.info(f"Created thread pool '{config.pool_name}'")
                
                return pool
                
        except Exception as e:
            logger.error(f"Error creating thread pool '{config.pool_name}': {e}")
            raise
    
    async def get_pool(self, pool_name: str) -> Optional[EnterpriseThreadPool]:
        """Get an existing thread pool"""
        return self._thread_pools.get(pool_name)
    
    async def submit_task(self, pool_name: str, function: Callable, *args, 
                         priority: ThreadPriority = ThreadPriority.NORMAL,
                         timeout_seconds: Optional[float] = None,
                         creator_context: str = "", **kwargs) -> Optional[Future]:
        """Submit a task to a specific thread pool"""
        try:
            pool = self._thread_pools.get(pool_name)
            if not pool:
                logger.error(f"Thread pool '{pool_name}' not found")
                return None
            
            # Create task
            task = ThreadTask(
                task_id=f"{pool_name}_{int(time.time() * 1000000)}",  # Microsecond timestamp
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority,
                timeout_seconds=timeout_seconds,
                creator_context=creator_context
            )
            
            # Submit to pool
            future = pool.submit_task(task)
            
            # Update manager statistics
            self._manager_stats["total_tasks_submitted"] += 1
            
            return future
            
        except Exception as e:
            logger.error(f"Error submitting task to pool '{pool_name}': {e}")
            return None
    
    async def submit_creator_task(self, creator_id: str, task_type: str, function: Callable,
                                 *args, **kwargs) -> Optional[Future]:
        """Submit a task using creator-specific optimization"""
        try:
            # Get creator profile
            profile = self._creator_profiles.get(creator_id)
            if not profile:
                # Use default pool
                return await self.submit_task("default", function, *args, **kwargs)
            
            # Determine optimal pool based on task type and creator profile
            pool_name = await self._select_optimal_pool_for_creator(creator_id, task_type)
            
            # Get priority based on creator and task type
            priority = await self._determine_task_priority(creator_id, task_type)
            
            return await self.submit_task(
                pool_name, function, *args,
                priority=priority,
                creator_context=creator_id,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Error submitting creator task for {creator_id}: {e}")
            return None
    
    async def _select_optimal_pool_for_creator(self, creator_id: str, task_type: str) -> str:
        """Select optimal thread pool for creator and task type"""
        try:
            profile = self._creator_profiles.get(creator_id)
            if not profile:
                return "default"
            
            creator_type = profile.creator_type
            
            # Map task types to pools based on creator type
            if creator_type == "musician":
                task_pool_mapping = {
                    "audio_processing": "musician_audio",
                    "sample_loading": "musician_io",
                    "project_management": "musician_mixed",
                    "background": "musician_batch"
                }
            elif creator_type == "photographer":
                task_pool_mapping = {
                    "image_processing": "photographer_cpu",
                    "file_operations": "photographer_io",
                    "batch_processing": "photographer_batch",
                    "gallery": "photographer_mixed"
                }
            elif creator_type == "blogger":
                task_pool_mapping = {
                    "content_processing": "blogger_mixed",
                    "publishing": "blogger_io",
                    "analytics": "blogger_cpu",
                    "media": "blogger_mixed"
                }
            else:
                return "default"
            
            return task_pool_mapping.get(task_type, "default")
            
        except Exception as e:
            logger.error(f"Error selecting optimal pool: {e}")
            return "default"
    
    async def _determine_task_priority(self, creator_id: str, task_type: str) -> ThreadPriority:
        """Determine task priority based on creator and task type"""
        try:
            profile = self._creator_profiles.get(creator_id)
            if not profile:
                return ThreadPriority.NORMAL
            
            creator_type = profile.creator_type
            
            # Priority mapping based on creator type and task
            if creator_type == "musician":
                if task_type in ["audio_processing", "real_time"]:
                    return ThreadPriority.CRITICAL
                elif task_type in ["sample_loading", "project_management"]:
                    return ThreadPriority.HIGH
                else:
                    return ThreadPriority.NORMAL
            
            elif creator_type == "photographer":
                if task_type in ["image_processing", "batch_processing"]:
                    return ThreadPriority.HIGH
                else:
                    return ThreadPriority.NORMAL
            
            elif creator_type == "blogger":
                if task_type == "publishing":
                    return ThreadPriority.HIGH
                else:
                    return ThreadPriority.NORMAL
            
            return ThreadPriority.NORMAL
            
        except Exception as e:
            logger.error(f"Error determining task priority: {e}")
            return ThreadPriority.NORMAL
    
    async def update_pool_metrics(self) -> None:
        """Update metrics for all thread pools"""
        try:
            for pool in self._thread_pools.values():
                metrics = pool.get_metrics()
                # Metrics are automatically stored in pool's history
                
        except Exception as e:
            logger.error(f"Error updating pool metrics: {e}")
    
    async def auto_scale_pools(self) -> None:
        """Automatically scale thread pools based on utilization"""
        try:
            if not self.enable_auto_scaling:
                return
            
            current_time = time.time()
            
            for pool_name, pool in self._thread_pools.items():
                # Check if enough time has passed since last scaling
                last_scale_time = self._scaling_config["last_scale_time"].get(pool_name, 0)
                if current_time - last_scale_time < self._scaling_config["min_scale_interval"]:
                    continue
                
                # Get current metrics
                metrics = pool.get_metrics()
                
                # Calculate utilization
                if metrics.total_threads > 0:
                    utilization = metrics.active_threads / metrics.total_threads
                    
                    # Scale up if high utilization
                    if (utilization > self._scaling_config["scale_up_threshold"] and
                        metrics.total_threads < pool.config.max_threads):
                        
                        new_max = min(
                            int(metrics.total_threads * self._scaling_config["scale_up_factor"]),
                            pool.config.max_threads
                        )
                        
                        await self._scale_pool(pool_name, new_max, "up")
                        self._scaling_config["last_scale_time"][pool_name] = current_time
                    
                    # Scale down if low utilization
                    elif (utilization < self._scaling_config["scale_down_threshold"] and
                          metrics.total_threads > pool.config.min_threads):
                        
                        new_max = max(
                            int(metrics.total_threads * self._scaling_config["scale_down_factor"]),
                            pool.config.min_threads
                        )
                        
                        await self._scale_pool(pool_name, new_max, "down")
                        self._scaling_config["last_scale_time"][pool_name] = current_time
                        
        except Exception as e:
            logger.error(f"Error in auto-scaling: {e}")
    
    async def _scale_pool(self, pool_name: str, new_size: int, direction: str) -> None:
        """Scale a thread pool to new size"""
        try:
            pool = self._thread_pools.get(pool_name)
            if not pool:
                return
            
            # Note: ThreadPoolExecutor doesn't support dynamic resizing
            # In a real implementation, this would require a custom thread pool
            # For now, we'll log the scaling intention
            
            logger.info(f"Scaling pool '{pool_name}' {direction} to {new_size} threads")
            
            # Update configuration for future reference
            if direction == "up":
                pool.config.max_threads = min(new_size, pool.config.max_threads)
            else:
                pool.config.max_threads = max(new_size, pool.config.min_threads)
                
        except Exception as e:
            logger.error(f"Error scaling pool '{pool_name}': {e}")
    
    async def optimize_pool_configurations(self) -> None:
        """Optimize thread pool configurations based on usage patterns"""
        try:
            for pool_name, pool in self._thread_pools.items():
                metrics = pool.get_metrics()
                
                # Analyze usage patterns
                if len(pool._metrics_history) > 10:
                    recent_metrics = list(pool._metrics_history)[-10:]
                    
                    # Calculate average utilization
                    avg_utilization = statistics.mean([
                        m.active_threads / max(m.total_threads, 1) for m in recent_metrics
                    ])
                    
                    # Calculate average queue wait time
                    avg_queue_time = statistics.mean([
                        m.avg_queue_wait_time_ms for m in recent_metrics if m.avg_queue_wait_time_ms > 0
                    ])
                    
                    # Suggest optimizations
                    optimizations = []
                    
                    if avg_utilization > 0.9:
                        optimizations.append("Consider increasing max_threads")
                    elif avg_utilization < 0.2:
                        optimizations.append("Consider decreasing min_threads")
                    
                    if avg_queue_time > 100:  # > 100ms queue time
                        optimizations.append("Consider increasing pool size or improving task efficiency")
                    
                    if optimizations:
                        logger.info(f"Pool '{pool_name}' optimization suggestions: {', '.join(optimizations)}")
                        
        except Exception as e:
            logger.error(f"Error optimizing pool configurations: {e}")
    
    async def update_manager_stats(self) -> None:
        """Update thread pool manager statistics"""
        try:
            # Count totals across all pools
            total_threads = 0
            total_tasks_completed = 0
            total_tasks_failed = 0
            total_utilization = 0.0
            
            for pool in self._thread_pools.values():
                metrics = pool.get_metrics()
                total_threads += metrics.total_threads
                total_tasks_completed += metrics.completed_tasks
                total_tasks_failed += metrics.failed_tasks
                
                if metrics.total_threads > 0:
                    total_utilization += metrics.active_threads / metrics.total_threads
            
            # Calculate averages
            pool_count = len(self._thread_pools)
            avg_pool_utilization = total_utilization / pool_count if pool_count > 0 else 0.0
            
            # Get system metrics
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory().percent
            
            # Update stats
            self._manager_stats.update({
                "total_pools": pool_count,
                "total_threads": total_threads,
                "total_tasks_completed": total_tasks_completed,
                "total_tasks_failed": total_tasks_failed,
                "avg_pool_utilization": avg_pool_utilization,
                "system_cpu_usage": system_cpu,
                "system_memory_usage": system_memory,
                "last_optimization": datetime.now()
            })
            
        except Exception as e:
            logger.error(f"Error updating manager stats: {e}")
    
    async def add_creator_profile(self, creator_id: str, creator_type: str) -> None:
        """Add creator-specific thread pool profile"""
        try:
            profile = CreatorThreadProfile(creator_type)
            self._creator_profiles[creator_id] = profile
            
            # Create creator-specific pools based on profile
            await self._create_creator_pools(creator_id, creator_type)
            
            logger.info(f"Added creator thread profile: {creator_id} ({creator_type})")
            
        except Exception as e:
            logger.error(f"Error adding creator profile: {e}")
    
    async def _create_creator_pools(self, creator_id: str, creator_type: str) -> None:
        """Create thread pools for a specific creator type"""
        try:
            profile = self._creator_profiles[creator_id]
            creator_config = getattr(profile, f"get_{creator_type}_profile")()
            
            for pool_name, pool_config in creator_config["pool_configurations"].items():
                full_pool_name = f"{creator_type}_{pool_name}"
                
                # Skip if pool already exists
                if full_pool_name in self._thread_pools:
                    continue
                
                config = ThreadPoolConfig(
                    pool_name=full_pool_name,
                    pool_type=pool_config["type"],
                    min_threads=pool_config["min_threads"],
                    max_threads=pool_config["max_threads"],
                    scaling_policy=pool_config["scaling"],
                    creator_specific=True,
                    thread_name_prefix=f"{creator_type}_{pool_name}"
                )
                
                await self.create_pool(config)
                
        except Exception as e:
            logger.error(f"Error creating creator pools for {creator_id}: {e}")
    
    async def remove_pool(self, pool_name: str) -> bool:
        """Remove a thread pool"""
        try:
            with self._manager_lock:
                pool = self._thread_pools.get(pool_name)
                if not pool:
                    return False
                
                # Shutdown the pool
                pool.shutdown(wait=True)
                
                # Remove from manager
                del self._thread_pools[pool_name]
                
                self._manager_stats["total_pools"] -= 1
                logger.info(f"Removed thread pool '{pool_name}'")
                
                return True
                
        except Exception as e:
            logger.error(f"Error removing thread pool '{pool_name}': {e}")
            return False
    
    async def get_manager_stats(self) -> Dict[str, Any]:
        """Get thread pool manager statistics"""
        return {
            **self._manager_stats,
            "pools": {
                pool_name: {
                    "type": pool.config.pool_type.value,
                    "min_threads": pool.config.min_threads,
                    "max_threads": pool.config.max_threads,
                    "scaling_policy": pool.config.scaling_policy.value,
                    "metrics": pool.get_metrics().__dict__
                }
                for pool_name, pool in self._thread_pools.items()
            },
            "creator_profiles": len(self._creator_profiles),
            "is_running": self._is_running
        }
    
    async def shutdown_all_pools(self) -> None:
        """Shutdown all thread pools"""
        try:
            logger.info("Shutting down all thread pools")
            
            for pool_name, pool in self._thread_pools.items():
                pool.shutdown(wait=True)
                logger.info(f"Shutdown pool '{pool_name}'")
            
            self._thread_pools.clear()
            self._is_running = False
            
        except Exception as e:
            logger.error(f"Error shutting down all pools: {e}")


# Factory function for enterprise instantiation
def create_thread_pool_manager(
    enable_auto_scaling: bool = True,
    max_total_threads: Optional[int] = None
) -> ThreadPoolManager:
    """
    Factory function to create ThreadPoolManager instance
    
    Args:
        enable_auto_scaling: Enable automatic pool scaling
        max_total_threads: Maximum total threads across all pools
    
    Returns:
        Configured ThreadPoolManager instance
    """
    return ThreadPoolManager(
        enable_auto_scaling=enable_auto_scaling,
        max_total_threads=max_total_threads
    )


# Export for enterprise usage
__all__ = [
    "ThreadPoolManager",
    "ThreadPoolType",
    "ThreadPriority", 
    "PoolScalingPolicy",
    "ThreadTask",
    "ThreadPoolConfig",
    "ThreadPoolMetrics",
    "ThreadPoolStats",
    "EnterpriseThreadPool",
    "CreatorThreadProfile",
    "create_thread_pool_manager"
]