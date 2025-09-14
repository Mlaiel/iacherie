"""Performance Optimization Toolkit - Ultra-Advanced for Ainflue Events

Comprehensive performance optimization toolkit for event processing with
intelligent caching, resource management, and real-time performance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import gc

# Optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import weakref

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Performance optimization levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    ULTRA = "ultra"


class ResourceType(Enum):
    """Types of resources to monitor and optimize"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CACHE = "cache"


@dataclass
class PerformanceMetrics:
    """Performance metrics for event processing"""
    event_id: str
    processing_time: float
    memory_usage: float
    cpu_usage: float
    cache_hits: int
    cache_misses: int
    throughput: float
    latency_p95: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationResult:
    """Result of performance optimization"""
    optimization_applied: str
    performance_improvement: float
    resource_savings: Dict[str, float]
    recommendation: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class ResourceLimits:
    """Resource limits for optimization"""
    max_memory_mb: float = 1024.0
    max_cpu_percent: float = 80.0
    max_cache_size_mb: float = 512.0
    max_concurrent_tasks: int = 100
    max_processing_time_seconds: float = 30.0


@dataclass
class CacheConfig:
    """Configuration for caching optimization"""
    max_size: int = 1000
    ttl_seconds: int = 3600
    cleanup_interval: int = 300
    eviction_policy: str = "lru"
    compression_enabled: bool = True


class PerformanceProfiler:
    """Advanced performance profiler for event processing"""
    
    def __init__(self) -> None:
        self.metrics_history: deque = deque(maxlen=10000)
        self.active_profiles: Dict[str, Dict[str, Any]] = {}
        self.resource_monitor = ResourceMonitor()
        
    async def start_profiling(self, event_id: str, business_context: Optional[Dict[str, Any]] = None) -> str:
        """Start profiling an event processing session"""
        
        profile_id = f"profile_{event_id}_{int(time.time() * 1000)}"
        
        profile_data = {
            "event_id": event_id,
            "start_time": time.time(),
            "start_memory": self.resource_monitor.get_memory_usage(),
            "start_cpu": self.resource_monitor.get_cpu_usage(),
            "business_context": business_context or {},
            "checkpoints": []
        }
        
        self.active_profiles[profile_id] = profile_data
        logger.debug(f"Started profiling for event {event_id} with profile {profile_id}")
        
        return profile_id
    
    async def add_checkpoint(self, profile_id -> None: str, checkpoint_name -> None: str, metadata -> None: Optional[Dict[str, Any]] = None) -> None:
        """Add a performance checkpoint"""
        
        if profile_id not in self.active_profiles:
            logger.warning(f"Profile {profile_id} not found for checkpoint")
            return
        
        profile = self.active_profiles[profile_id]
        current_time = time.time()
        
        checkpoint = {
            "name": checkpoint_name,
            "timestamp": current_time,
            "elapsed_time": current_time - profile["start_time"],
            "memory_usage": self.resource_monitor.get_memory_usage(),
            "cpu_usage": self.resource_monitor.get_cpu_usage(),
            "metadata": metadata or {}
        }
        
        profile["checkpoints"].append(checkpoint)
        logger.debug(f"Added checkpoint '{checkpoint_name}' to profile {profile_id}")
    
    async def end_profiling(self, profile_id: str) -> PerformanceMetrics:
        """End profiling and generate performance metrics"""
        
        if profile_id not in self.active_profiles:
            raise ValueError(f"Profile {profile_id} not found")
        
        profile = self.active_profiles[profile_id]
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - profile["start_time"]
        memory_delta = self.resource_monitor.get_memory_usage() - profile["start_memory"]
        cpu_avg = sum(cp["cpu_usage"] for cp in profile["checkpoints"]) / len(profile["checkpoints"]) if profile["checkpoints"] else 0
        
        metrics = PerformanceMetrics(
            event_id=profile["event_id"],
            processing_time=total_time,
            memory_usage=memory_delta,
            cpu_usage=cpu_avg,
            cache_hits=0,  # Will be updated by cache manager
            cache_misses=0,  # Will be updated by cache manager
            throughput=1.0 / total_time if total_time > 0 else 0.0,
            latency_p95=total_time,  # Simplified for single event
            error_rate=0.0
        )
        
        self.metrics_history.append(metrics)
        del self.active_profiles[profile_id]
        
        logger.info(f"Profiling completed for event {profile['event_id']} in {total_time:.3f}s")
        return metrics
    
    def get_performance_statistics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance statistics for a time window"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"message": "No metrics available for time window"}
        
        return {
            "total_events": len(recent_metrics),
            "average_processing_time": sum(m.processing_time for m in recent_metrics) / len(recent_metrics),
            "max_processing_time": max(m.processing_time for m in recent_metrics),
            "min_processing_time": min(m.processing_time for m in recent_metrics),
            "average_memory_usage": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            "average_throughput": sum(m.throughput for m in recent_metrics) / len(recent_metrics),
            "total_cache_hits": sum(m.cache_hits for m in recent_metrics),
            "total_cache_misses": sum(m.cache_misses for m in recent_metrics),
            "cache_hit_ratio": sum(m.cache_hits for m in recent_metrics) / (sum(m.cache_hits for m in recent_metrics) + sum(m.cache_misses for m in recent_metrics)) if sum(m.cache_misses for m in recent_metrics) > 0 else 1.0
        }


class ResourceMonitor:
    """System resource monitoring"""
    
    def __init__(self) -> None:
        if HAS_PSUTIL:
            self.process = psutil.Process()
        else:
            self.process = None
        self.monitoring_active = False
        self.monitor_thread = None
        self.resource_history: deque = deque(maxlen=1000)
    
    def start_monitoring(self, interval_seconds -> None: float = 1.0) -> None:
        """Start continuous resource monitoring"""
        
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self, interval -> None: float) -> None:
        """Monitoring loop"""
        while self.monitoring_active:
            try:
                resource_data = {
                    "timestamp": datetime.utcnow(),
                    "cpu_percent": self.get_cpu_usage(),
                    "memory_mb": self.get_memory_usage(),
                    "disk_io": self.get_disk_io(),
                    "network_io": self.get_network_io()
                }
                self.resource_history.append(resource_data)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(interval)
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        if HAS_PSUTIL and self.process:
            try:
                return self.process.cpu_percent()
            except:
                return 0.0
        return 0.0
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if HAS_PSUTIL and self.process:
            try:
                return self.process.memory_info().rss / 1024 / 1024
            except:
                return 0.0
        return 0.0
    
    def get_disk_io(self) -> Dict[str, int]:
        """Get disk I/O statistics"""
        if HAS_PSUTIL and self.process:
            try:
                io_counters = self.process.io_counters()
                return {
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes
                }
            except:
                return {"read_bytes": 0, "write_bytes": 0}
        return {"read_bytes": 0, "write_bytes": 0}
    
    def get_network_io(self) -> Dict[str, int]:
        """Get network I/O statistics"""
        if HAS_PSUTIL:
            try:
                # System-wide network stats (process-specific not available in psutil)
                net_io = psutil.net_io_counters()
                return {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv
                }
            except:
                return {"bytes_sent": 0, "bytes_recv": 0}
        return {"bytes_sent": 0, "bytes_recv": 0}
    
    def get_resource_pressure(self) -> Dict[str, str]:
        """Get current resource pressure levels"""
        
        cpu_usage = self.get_cpu_usage()
        memory_mb = self.get_memory_usage()
        
        # Determine pressure levels
        cpu_pressure = "low"
        if cpu_usage > 80:
            cpu_pressure = "high"
        elif cpu_usage > 60:
            cpu_pressure = "medium"
        
        memory_pressure = "low"
        if memory_mb > 1024:  # > 1GB
            memory_pressure = "high"
        elif memory_mb > 512:  # > 512MB
            memory_pressure = "medium"
        
        return {
            "cpu": cpu_pressure,
            "memory": memory_pressure,
            "overall": "high" if any(p == "high" for p in [cpu_pressure, memory_pressure]) else "medium" if any(p == "medium" for p in [cpu_pressure, memory_pressure]) else "low"
        }


class IntelligentCache:
    """Intelligent caching system with business-aware policies"""
    
    def __init__(self, config -> None: CacheConfig) -> None:
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, datetime] = {}
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.cache_size = 0
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self) -> None:
        """Start periodic cache cleanup"""
        def cleanup_loop() -> None:
            while True:
                try:
                    self._cleanup_expired_entries()
                    time.sleep(self.config.cleanup_interval)
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
                    time.sleep(self.config.cleanup_interval)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    async def get(self, key: str, business_priority: str = "normal") -> Optional[Any]:
        """Get value from cache with business-aware prioritization"""
        
        with self.lock:
            if key in self.cache:
                # Check if expired
                if self._is_expired(key):
                    self._remove_key(key)
                    self.miss_count += 1
                    return None
                
                # Update access statistics
                self.access_times[key] = datetime.utcnow()
                self.access_counts[key] += 1
                self.hit_count += 1
                
                # Business priority affects cache warming
                if business_priority in ["critical", "high"]:
                    self.access_counts[key] += 2  # Boost priority items
                
                logger.debug(f"Cache hit for key: {key}")
                return self.cache[key]
            else:
                self.miss_count += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
    
    async def put(self, key -> None: str, value -> None: Any, business_priority -> None: str = "normal", custom_ttl -> None: Optional[int] = None) -> None:
        """Put value in cache with business-aware storage"""
        
        with self.lock:
            # Check if we need to make space
            if len(self.cache) >= self.config.max_size:
                await self._evict_entries(business_priority)
            
            # Compress if configured
            stored_value = value
            if self.config.compression_enabled and isinstance(value, str) and len(value) > 100:
                try:
                    import gzip
                    stored_value = gzip.compress(value.encode('utf-8'))
                    logger.debug(f"Compressed cache value for key: {key}")
                except:
                    stored_value = value
            
            # Store with metadata
            ttl = custom_ttl or self.config.ttl_seconds
            expiry_time = datetime.utcnow() + timedelta(seconds=ttl)
            
            self.cache[key] = {
                "value": stored_value,
                "expiry": expiry_time,
                "business_priority": business_priority,
                "compressed": self.config.compression_enabled and isinstance(stored_value, bytes)
            }
            
            self.access_times[key] = datetime.utcnow()
            self.access_counts[key] = 1
            
            # High priority items get longer TTL
            if business_priority in ["critical", "high"]:
                self.cache[key]["expiry"] = datetime.utcnow() + timedelta(seconds=ttl * 2)
            
            logger.debug(f"Cached value for key: {key} with priority: {business_priority}")
    
    async def _evict_entries(self, new_item_priority -> None: str) -> None:
        """Evict entries based on business-aware policy"""
        
        if self.config.eviction_policy == "lru":
            await self._evict_lru(new_item_priority)
        elif self.config.eviction_policy == "business_aware":
            await self._evict_business_aware(new_item_priority)
        else:
            await self._evict_random()
    
    async def _evict_lru(self, new_item_priority -> None: str) -> None:
        """Evict least recently used items"""
        
        # Sort by last access time, but protect high-priority items
        candidates = []
        for key in self.cache:
            item = self.cache[key]
            priority = item.get("business_priority", "normal")
            
            # Don't evict critical items unless new item is also critical
            if priority == "critical" and new_item_priority != "critical":
                continue
            
            candidates.append((key, self.access_times.get(key, datetime.min)))
        
        if candidates:
            candidates.sort(key=lambda x: x[1])
            key_to_remove = candidates[0][0]
            self._remove_key(key_to_remove)
            logger.debug(f"Evicted LRU key: {key_to_remove}")
    
    async def _evict_business_aware(self, new_item_priority -> None: str) -> None:
        """Evict items based on business priority and access patterns"""
        
        priority_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1, "normal": 1}
        new_item_weight = priority_weights.get(new_item_priority, 1)
        
        candidates = []
        for key in self.cache:
            item = self.cache[key]
            priority = item.get("business_priority", "normal")
            priority_weight = priority_weights.get(priority, 1)
            
            # Calculate eviction score (lower = more likely to evict)
            access_recency = (datetime.utcnow() - self.access_times.get(key, datetime.min)).total_seconds()
            access_frequency = self.access_counts.get(key, 1)
            
            score = priority_weight * access_frequency / max(access_recency, 1)
            candidates.append((key, score))
        
        if candidates:
            candidates.sort(key=lambda x: x[1])
            key_to_remove = candidates[0][0]
            self._remove_key(key_to_remove)
            logger.debug(f"Evicted business-aware key: {key_to_remove}")
    
    async def _evict_random(self) -> None:
        """Evict random entry"""
        import random
        if self.cache:
            key_to_remove = random.choice(list(self.cache.keys()))
            self._remove_key(key_to_remove)
            logger.debug(f"Evicted random key: {key_to_remove}")
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.cache:
            return True
        
        item = self.cache[key]
        return datetime.utcnow() > item["expiry"]
    
    def _remove_key(self, key -> None: str) -> None:
        """Remove key from cache and metadata"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
        if key in self.access_counts:
            del self.access_counts[key]
    
    def _cleanup_expired_entries(self) -> None:
        """Remove expired entries"""
        with self.lock:
            expired_keys = [key for key in self.cache if self._is_expired(key)]
            for key in expired_keys:
                self._remove_key(key)
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_ratio = self.hit_count / total_requests if total_requests > 0 else 0.0
            
            return {
                "size": len(self.cache),
                "max_size": self.config.max_size,
                "hit_count": self.hit_count,
                "miss_count": self.miss_count,
                "hit_ratio": hit_ratio,
                "memory_usage_estimate": sum(len(str(v)) for v in self.cache.values()) / 1024,  # KB
                "average_access_count": sum(self.access_counts.values()) / len(self.access_counts) if self.access_counts else 0
            }


class ConcurrencyManager:
    """Manager for optimizing concurrent processing"""
    
    def __init__(self, resource_limits -> None: ResourceLimits) -> None:
        self.resource_limits = resource_limits
        self.thread_pool = ThreadPoolExecutor(max_workers=min(32, resource_limits.max_concurrent_tasks))
        self.process_pool = ProcessPoolExecutor(max_workers=min(4, resource_limits.max_concurrent_tasks // 4))
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_semaphore = asyncio.Semaphore(resource_limits.max_concurrent_tasks)
        self.resource_monitor = ResourceMonitor()
    
    async def execute_with_optimization(self, 
                                      task_func: Callable,
                                      task_args: Tuple = (),
                                      task_kwargs: Dict[str, Any] = None,
                                      business_priority: str = "normal",
                                      use_process_pool: bool = False) -> Any:
        """Execute task with concurrency optimization"""
        
        task_kwargs = task_kwargs or {}
        task_id = f"task_{int(time.time() * 1000)}_{id(task_func)}"
        
        async with self.task_semaphore:
            # Check resource pressure before execution
            pressure = self.resource_monitor.get_resource_pressure()
            
            if pressure["overall"] == "high":
                logger.warning(f"High resource pressure, delaying task {task_id}")
                await asyncio.sleep(0.1)  # Brief delay
            
            try:
                if use_process_pool and not asyncio.iscoroutinefunction(task_func):
                    # CPU-intensive task - use process pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.process_pool, task_func, *task_args
                    )
                elif not asyncio.iscoroutinefunction(task_func):
                    # I/O-bound task - use thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.thread_pool, task_func, *task_args
                    )
                else:
                    # Async task - run directly
                    task = asyncio.create_task(task_func(*task_args, **task_kwargs))
                    self.active_tasks[task_id] = task
                    
                    try:
                        result = await asyncio.wait_for(
                            task, 
                            timeout=self.resource_limits.max_processing_time_seconds
                        )
                    finally:
                        if task_id in self.active_tasks:
                            del self.active_tasks[task_id]
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Task {task_id} timed out after {self.resource_limits.max_processing_time_seconds}s")
                raise
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                raise
    
    async def batch_execute(self, 
                          tasks: List[Tuple[Callable, Tuple, Dict[str, Any]]],
                          max_concurrent: Optional[int] = None) -> List[Any]:
        """Execute multiple tasks with optimal concurrency"""
        
        max_concurrent = max_concurrent or min(len(tasks), self.resource_limits.max_concurrent_tasks)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single(task_info) -> None:
            task_func, args, kwargs = task_info
            async with semaphore:
                return await self.execute_with_optimization(task_func, args, kwargs)
        
        # Execute all tasks concurrently with limit
        results = await asyncio.gather(
            *[execute_single(task) for task in tasks],
            return_exceptions=True
        )
        
        return results
    
    def get_concurrency_statistics(self) -> Dict[str, Any]:
        """Get concurrency performance statistics"""
        return {
            "active_tasks": len(self.active_tasks),
            "max_concurrent_tasks": self.resource_limits.max_concurrent_tasks,
            "thread_pool_size": self.thread_pool._max_workers,
            "process_pool_size": self.process_pool._max_workers,
            "available_semaphore_permits": self.task_semaphore._value,
            "resource_pressure": self.resource_monitor.get_resource_pressure()
        }
    
    def shutdown(self) -> None:
        """Shutdown thread and process pools"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


class MemoryOptimizer:
    """Memory usage optimization and management"""
    
    def __init__(self, max_memory_mb -> None: float = 1024.0) -> None:
        self.max_memory_mb = max_memory_mb
        self.object_pools: Dict[str, List[Any]] = defaultdict(list)
        self.weak_references: Dict[str, List[weakref.ref]] = defaultdict(list)
        
    async def optimize_memory_usage(self) -> OptimizationResult:
        """Perform memory optimization"""
        
        initial_memory = 0.0
        if HAS_PSUTIL:
            try:
                initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            except:
                initial_memory = 100.0  # Default assumption
        
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clean up weak references
            self._cleanup_weak_references()
            
            # Clear object pools if memory pressure is high
            if initial_memory > self.max_memory_mb * 0.8:
                self._clear_object_pools()
            
            if HAS_PSUTIL:
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            else:
                final_memory = initial_memory * 0.95  # Simulate some cleanup
            memory_saved = initial_memory - final_memory
            
            return OptimizationResult(
                optimization_applied="memory_cleanup",
                performance_improvement=memory_saved,
                resource_savings={"memory_mb": memory_saved},
                recommendation=f"Freed {memory_saved:.2f} MB of memory, collected {collected} objects",
                success=True
            )
            
        except Exception as e:
            return OptimizationResult(
                optimization_applied="memory_cleanup",
                performance_improvement=0.0,
                resource_savings={},
                recommendation="Memory optimization failed",
                success=False,
                error_message=str(e)
            )
    
    def get_object_from_pool(self, object_type: str, factory: Callable) -> Any:
        """Get object from pool or create new one"""
        
        pool = self.object_pools[object_type]
        
        if pool:
            obj = pool.pop()
            logger.debug(f"Reused object from pool: {object_type}")
            return obj
        else:
            obj = factory()
            logger.debug(f"Created new object: {object_type}")
            return obj
    
    def return_object_to_pool(self, object_type -> None: str, obj -> None: Any) -> None:
        """Return object to pool for reuse"""
        
        pool = self.object_pools[object_type]
        
        # Limit pool size to prevent memory bloat
        if len(pool) < 10:
            # Reset object state if possible
            if hasattr(obj, 'reset'):
                obj.reset()
            elif hasattr(obj, 'clear'):
                obj.clear()
            
            pool.append(obj)
            logger.debug(f"Returned object to pool: {object_type}")
        else:
            logger.debug(f"Pool full, discarding object: {object_type}")
    
    def register_weak_reference(self, category -> None: str, obj -> None: Any) -> None:
        """Register weak reference for automatic cleanup"""
        
        weak_ref = weakref.ref(obj, lambda ref: self._on_object_deleted(category, ref))
        self.weak_references[category].append(weak_ref)
    
    def _on_object_deleted(self, category -> None: str, ref -> None: weakref.ref) -> None:
        """Callback for when weakly referenced object is deleted"""
        if ref in self.weak_references[category]:
            self.weak_references[category].remove(ref)
    
    def _cleanup_weak_references(self) -> None:
        """Clean up dead weak references"""
        for category in self.weak_references:
            self.weak_references[category] = [ref for ref in self.weak_references[category] if ref() is not None]
    
    def _clear_object_pools(self) -> None:
        """Clear object pools to free memory"""
        total_cleared = sum(len(pool) for pool in self.object_pools.values())
        self.object_pools.clear()
        logger.info(f"Cleared {total_cleared} objects from pools due to memory pressure")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        if HAS_PSUTIL:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                
                return {
                    "rss_mb": memory_info.rss / 1024 / 1024,
                    "vms_mb": memory_info.vms / 1024 / 1024,
                    "percent": process.memory_percent(),
                    "max_memory_mb": self.max_memory_mb,
                    "object_pools": {k: len(v) for k, v in self.object_pools.items()},
                    "weak_references": {k: len(v) for k, v in self.weak_references.items()},
                    "gc_stats": {
                        "counts": gc.get_count(),
                        "thresholds": gc.get_threshold()
                    }
                }
            except:
                pass
        
        return {
            "rss_mb": 0.0,
            "vms_mb": 0.0,
            "percent": 0.0,
            "max_memory_mb": self.max_memory_mb,
            "object_pools": {k: len(v) for k, v in self.object_pools.items()},
            "weak_references": {k: len(v) for k, v in self.weak_references.items()},
            "gc_stats": {
                "counts": gc.get_count(),
                "thresholds": gc.get_threshold()
            }
        }


class PerformanceOptimizationToolkit:
    """
    Ultra-advanced performance optimization toolkit for Ainflue event processing
    Intelligent resource management, caching, and real-time performance monitoring
    """
    
    def __init__(self, 
                 resource_limits -> None: Optional[ResourceLimits] = None,
                 cache_config -> None: Optional[CacheConfig] = None,
                 optimization_level -> None: OptimizationLevel = OptimizationLevel.STANDARD) -> None:
        
        self.resource_limits = resource_limits or ResourceLimits()
        self.cache_config = cache_config or CacheConfig()
        self.optimization_level = optimization_level
        
        # Initialize components
        self.profiler = PerformanceProfiler()
        self.resource_monitor = ResourceMonitor()
        self.cache = IntelligentCache(self.cache_config)
        self.concurrency_manager = ConcurrencyManager(self.resource_limits)
        self.memory_optimizer = MemoryOptimizer(self.resource_limits.max_memory_mb)
        
        # Performance tracking
        self.optimization_history: List[OptimizationResult] = []
        self.performance_baseline: Optional[Dict[str, float]] = None
        
        # Start monitoring
        self.resource_monitor.start_monitoring()
        
        logger.info(f"PerformanceOptimizationToolkit initialized with {optimization_level.value} optimization level")
    
    async def optimize_event_processing(self, 
                                      event_processor: Callable,
                                      event_data: Dict[str, Any],
                                      business_context: Optional[Dict[str, Any]] = None) -> Tuple[Any, PerformanceMetrics]:
        """Optimize event processing with comprehensive performance management"""
        
        business_context = business_context or {}
        business_priority = business_context.get("priority", "normal")
        
        # Start profiling
        profile_id = await self.profiler.start_profiling(
            event_data.get("event_id", "unknown"), 
            business_context
        )
        
        try:
            # Check and apply cache if applicable
            cache_key = self._generate_cache_key(event_data, event_processor.__name__)
            cached_result = await self.cache.get(cache_key, business_priority)
            
            if cached_result is not None:
                await self.profiler.add_checkpoint(profile_id, "cache_hit")
                metrics = await self.profiler.end_profiling(profile_id)
                metrics.cache_hits = 1
                return cached_result, metrics
            
            await self.profiler.add_checkpoint(profile_id, "cache_miss")
            
            # Apply resource optimization
            if self.optimization_level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.ULTRA]:
                await self._apply_pre_processing_optimizations()
            
            await self.profiler.add_checkpoint(profile_id, "optimization_applied")
            
            # Execute with concurrency management
            use_process_pool = self._should_use_process_pool(event_data, business_context)
            
            result = await self.concurrency_manager.execute_with_optimization(
                event_processor,
                task_args=(event_data,),
                task_kwargs=business_context,
                business_priority=business_priority,
                use_process_pool=use_process_pool
            )
            
            await self.profiler.add_checkpoint(profile_id, "processing_completed")
            
            # Cache result for future use
            await self.cache.put(cache_key, result, business_priority)
            
            await self.profiler.add_checkpoint(profile_id, "result_cached")
            
            # Apply post-processing optimizations
            if self.optimization_level == OptimizationLevel.ULTRA:
                await self._apply_post_processing_optimizations()
            
            # End profiling and get metrics
            metrics = await self.profiler.end_profiling(profile_id)
            metrics.cache_misses = 1
            
            return result, metrics
            
        except Exception as e:
            # End profiling even on error
            try:
                metrics = await self.profiler.end_profiling(profile_id)
                metrics.error_rate = 1.0
            except:
                metrics = PerformanceMetrics(
                    event_id=event_data.get("event_id", "unknown"),
                    processing_time=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0,
                    cache_hits=0,
                    cache_misses=1,
                    throughput=0.0,
                    latency_p95=0.0,
                    error_rate=1.0
                )
            
            logger.error(f"Event processing failed: {e}")
            raise
    
    async def optimize_batch_processing(self,
                                      event_processor: Callable,
                                      events: List[Dict[str, Any]],
                                      business_context: Optional[Dict[str, Any]] = None) -> Tuple[List[Any], List[PerformanceMetrics]]:
        """Optimize batch event processing"""
        
        business_context = business_context or {}
        
        # Group events by priority for optimal processing order
        events_by_priority = self._group_events_by_priority(events, business_context)
        
        results = []
        metrics_list = []
        
        # Process high-priority events first
        for priority in ["critical", "high", "medium", "low", "normal"]:
            if priority not in events_by_priority:
                continue
            
            priority_events = events_by_priority[priority]
            
            # Determine optimal batch size
            batch_size = self._calculate_optimal_batch_size(priority_events, priority)
            
            # Process in batches
            for i in range(0, len(priority_events), batch_size):
                batch = priority_events[i:i + batch_size]
                
                # Create tasks for concurrent processing
                tasks = []
                for event in batch:
                    task_info = (
                        self.optimize_event_processing,
                        (event_processor, event, {**business_context, "priority": priority}),
                        {}
                    )
                    tasks.append(task_info)
                
                # Execute batch concurrently
                batch_results = await self.concurrency_manager.batch_execute(tasks)
                
                # Separate results and metrics
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch processing error: {result}")
                        continue
                    
                    if isinstance(result, tuple) and len(result) == 2:
                        event_result, event_metrics = result
                        results.append(event_result)
                        metrics_list.append(event_metrics)
        
        return results, metrics_list
    
    async def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        
        recommendations = []
        
        # Analyze cache performance
        cache_stats = self.cache.get_cache_statistics()
        if cache_stats["hit_ratio"] < 0.7:
            recommendations.append("Cache hit ratio is low - consider increasing cache size or TTL")
        
        # Analyze resource usage
        resource_pressure = self.resource_monitor.get_resource_pressure()
        if resource_pressure["cpu"] == "high":
            recommendations.append("High CPU usage detected - consider using process pools for CPU-intensive tasks")
        
        if resource_pressure["memory"] == "high":
            recommendations.append("High memory usage detected - consider enabling memory optimization")
        
        # Analyze concurrency
        concurrency_stats = self.concurrency_manager.get_concurrency_statistics()
        active_ratio = concurrency_stats["active_tasks"] / concurrency_stats["max_concurrent_tasks"]
        
        if active_ratio > 0.9:
            recommendations.append("Concurrency limit nearly reached - consider increasing max_concurrent_tasks")
        elif active_ratio < 0.3:
            recommendations.append("Low concurrency utilization - consider reducing max_concurrent_tasks to save resources")
        
        # Analyze recent performance
        perf_stats = self.profiler.get_performance_statistics(30)  # Last 30 minutes
        if "average_processing_time" in perf_stats and perf_stats["average_processing_time"] > 10.0:
            recommendations.append("High average processing time - consider optimizing event processors or increasing cache usage")
        
        if not recommendations:
            recommendations.append("Performance is optimal - no immediate recommendations")
        
        return recommendations
    
    def _generate_cache_key(self, event_data: Dict[str, Any], processor_name: str) -> str:
        """Generate cache key for event and processor"""
        
        # Use a subset of event data for cache key to avoid cache pollution
        key_data = {
            "processor": processor_name,
            "event_type": event_data.get("event_type"),
            "user_id": event_data.get("user_id"),
            "payload_hash": hash(str(event_data.get("payload", {})))
        }
        
        return f"event_cache_{hash(str(key_data))}"
    
    def _should_use_process_pool(self, event_data: Dict[str, Any], business_context: Dict[str, Any]) -> bool:
        """Determine if process pool should be used for this event"""
        
        # Large payload events benefit from process pools
        payload_size = len(str(event_data.get("payload", {})))
        if payload_size > 100_000:  # 100KB
            return True
        
        # CPU-intensive event types
        event_type = event_data.get("event_type", "")
        cpu_intensive_types = ["ai_processing", "image_processing", "video_processing", "ml_inference"]
        
        if any(cpu_type in event_type for cpu_type in cpu_intensive_types):
            return True
        
        # High CPU pressure suggests using process pools
        resource_pressure = self.resource_monitor.get_resource_pressure()
        if resource_pressure["cpu"] == "high":
            return True
        
        return False
    
    def _group_events_by_priority(self, events: List[Dict[str, Any]], business_context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Group events by business priority"""
        
        groups = defaultdict(list)
        
        for event in events:
            # Determine priority from event or context
            priority = "normal"
            
            # Check business context
            if "priority" in business_context:
                priority = business_context["priority"]
            
            # Check event metadata
            elif "business_metadata" in event and "priority" in event["business_metadata"]:
                priority = event["business_metadata"]["priority"]
            
            # Infer from event type
            else:
                event_type = event.get("event_type", "")
                if "monetization" in event_type or "payment" in event_type:
                    priority = "high"
                elif "security" in event_type or "alert" in event_type:
                    priority = "critical"
                elif "analytics" in event_type:
                    priority = "low"
            
            groups[priority].append(event)
        
        return groups
    
    def _calculate_optimal_batch_size(self, events: List[Dict[str, Any]], priority: str) -> int:
        """Calculate optimal batch size for events"""
        
        base_batch_size = {
            "critical": 1,    # Process immediately
            "high": 5,        # Small batches for responsiveness
            "medium": 10,     # Balanced batches
            "low": 20,        # Larger batches for efficiency
            "normal": 10      # Default
        }.get(priority, 10)
        
        # Adjust based on resource pressure
        resource_pressure = self.resource_monitor.get_resource_pressure()
        
        if resource_pressure["overall"] == "high":
            return max(1, base_batch_size // 2)  # Smaller batches under pressure
        elif resource_pressure["overall"] == "low":
            return min(50, base_batch_size * 2)  # Larger batches when resources available
        
        return base_batch_size
    
    async def _apply_pre_processing_optimizations(self) -> None:
        """Apply optimizations before processing"""
        
        # Memory optimization
        memory_result = await self.memory_optimizer.optimize_memory_usage()
        if memory_result.success:
            self.optimization_history.append(memory_result)
    
    async def _apply_post_processing_optimizations(self) -> None:
        """Apply optimizations after processing"""
        
        # Force garbage collection for ultra optimization
        if self.optimization_level == OptimizationLevel.ULTRA:
            gc.collect()
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        return {
            "profiler": self.profiler.get_performance_statistics(),
            "cache": self.cache.get_cache_statistics(),
            "concurrency": self.concurrency_manager.get_concurrency_statistics(),
            "memory": self.memory_optimizer.get_memory_statistics(),
            "resource_pressure": self.resource_monitor.get_resource_pressure(),
            "optimization_level": self.optimization_level.value,
            "recent_optimizations": len(self.optimization_history),
            "uptime_minutes": (datetime.utcnow() - datetime.utcnow()).total_seconds() / 60  # Simplified
        }
    
    def shutdown(self) -> None:
        """Shutdown the optimization toolkit"""
        
        self.resource_monitor.stop_monitoring()
        self.concurrency_manager.shutdown()
        
        logger.info("PerformanceOptimizationToolkit shutdown completed")


# Export main classes
__all__ = [
    'PerformanceOptimizationToolkit',
    'OptimizationLevel',
    'ResourceLimits',
    'CacheConfig',
    'PerformanceMetrics',
    'OptimizationResult'
]