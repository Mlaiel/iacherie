"""IA Influencer Agent - Advanced Indexing Optimization
====================================================

Enterprise-grade optimization system for indexing performance,
resource management, auto-scaling, and intelligent caching strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""
import asyncio
import logging
import time
import psutil
import numpy as np
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from enum import Enum
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from redis.asyncio import Redis
import json
import pickle
from functools import wraps, lru_cache
import hashlib

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategy types"""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    BALANCED = "balanced"


class CacheStrategy(Enum):
    """Cache strategy types"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"


@dataclass
class OptimizationConfig:
    """Configuration for optimization settings"""
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    max_workers: int = multiprocessing.cpu_count()
    batch_size: int = 100
    cache_size_mb: int = 512
    cache_ttl_seconds: int = 3600
    auto_scaling_enabled: bool = True
    performance_threshold: float = 0.8
    memory_threshold: float = 0.85
    enable_prefetching: bool = True
    compression_enabled: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    throughput: float
    latency_ms: float
    cache_hit_rate: float
    queue_depth: int
    active_workers: int
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Result of optimization operation"""
    strategy_applied: str
    performance_improvement: float
    resource_savings: Dict[str, float]
    recommendations: List[str]
    metrics_before: PerformanceMetrics
    metrics_after: PerformanceMetrics


class IntelligentCache:
    """Advanced caching system with multiple strategies"""
    
    def __init__(self, config: OptimizationConfig, redis_client: Redis):
        self.config = config
        self.redis_client = redis_client
        self.local_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size_mb": 0
        }
        self.access_patterns = defaultdict(list)
        self.predictive_model = None
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with intelligent strategy"""
        try:
            # Check local cache first
            if key in self.local_cache:
                self.cache_stats["hits"] += 1
                self._update_access_pattern(key)
                return self.local_cache[key]["data"]
            
            # Check Redis cache
            cached_data = await self.redis_client.get(f"cache:{key}")
            if cached_data:
                try:
                    data = pickle.loads(cached_data)
                    # Promote to local cache if frequently accessed
                    if self._should_promote_to_local(key):
                        await self._store_local(key, data)
                    self.cache_stats["hits"] += 1
                    self._update_access_pattern(key)
                    return data
                except:
                    pass
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = None, 
        priority: int = 1
    ):
        """Set value in cache with intelligent placement"""
        try:
            ttl = ttl or self.config.cache_ttl_seconds
            
            # Serialize data
            serialized_data = pickle.dumps(value)
            data_size = len(serialized_data)
            
            # Store in Redis with TTL
            await self.redis_client.setex(
                f"cache:{key}", 
                ttl, 
                serialized_data
            )
            
            # Store in local cache if conditions are met
            if self._should_store_local(key, data_size, priority):
                await self._store_local(key, value, ttl)
            
            # Update cache statistics
            self.cache_stats["size_mb"] += data_size / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    async def _store_local(self, key: str, value: Any, ttl: int = None):
        """Store data in local cache with eviction policy"""
        try:
            current_time = time.time()
            
            # Check if we need to evict
            await self._evict_if_needed()
            
            self.local_cache[key] = {
                "data": value,
                "timestamp": current_time,
                "ttl": ttl,
                "access_count": 1,
                "last_access": current_time
            }
            
        except Exception as e:
            logger.error(f"Local cache store error for key {key}: {e}")
    
    async def _evict_if_needed(self):
        """Evict cache entries based on strategy"""
        try:
            # Calculate current cache size
            current_size = sum(
                len(pickle.dumps(entry["data"])) 
                for entry in self.local_cache.values()
            ) / (1024 * 1024)
            
            max_size = self.config.cache_size_mb
            
            if current_size > max_size:
                entries_to_evict = []
                
                if self.config.cache_strategy == CacheStrategy.LRU:
                    # Evict least recently used
                    sorted_entries = sorted(
                        self.local_cache.items(),
                        key=lambda x: x[1]["last_access"]
                    )
                    entries_to_evict = [key for key, _ in sorted_entries[:len(sorted_entries)//4]]
                
                elif self.config.cache_strategy == CacheStrategy.LFU:
                    # Evict least frequently used
                    sorted_entries = sorted(
                        self.local_cache.items(),
                        key=lambda x: x[1]["access_count"]
                    )
                    entries_to_evict = [key for key, _ in sorted_entries[:len(sorted_entries)//4]]
                
                elif self.config.cache_strategy == CacheStrategy.TTL:
                    # Evict expired entries
                    current_time = time.time()
                    for key, entry in self.local_cache.items():
                        if entry["ttl"] and (current_time - entry["timestamp"]) > entry["ttl"]:
                            entries_to_evict.append(key)
                
                # Perform eviction
                for key in entries_to_evict:
                    if key in self.local_cache:
                        del self.local_cache[key]
                        self.cache_stats["evictions"] += 1
                
        except Exception as e:
            logger.error(f"Cache eviction error: {e}")
    
    def _update_access_pattern(self, key: str):
        """Update access patterns for predictive caching"""
        current_time = time.time()
        self.access_patterns[key].append(current_time)
        
        # Keep only recent access patterns
        cutoff_time = current_time - 3600  # Last hour
        self.access_patterns[key] = [
            t for t in self.access_patterns[key] if t > cutoff_time
        ]
        
        # Update local cache access info
        if key in self.local_cache:
            self.local_cache[key]["access_count"] += 1
            self.local_cache[key]["last_access"] = current_time
    
    def _should_promote_to_local(self, key: str) -> bool:
        """Determine if key should be promoted to local cache"""
        access_history = self.access_patterns.get(key, [])
        
        # Promote if frequently accessed
        if len(access_history) >= 3:
            return True
        
        # Promote if accessed recently
        if access_history and (time.time() - access_history[-1]) < 300:  # 5 minutes
            return True
        
        return False
    
    def _should_store_local(self, key: str, data_size: int, priority: int) -> bool:
        """Determine if data should be stored in local cache"""
        # Don't store large objects locally
        if data_size > 1024 * 1024:  # 1MB
            return False
        
        # Store high priority items
        if priority >= 3:
            return True
        
        # Store frequently accessed items
        access_history = self.access_patterns.get(key, [])
        if len(access_history) >= 2:
            return True
        
        return False
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "local_cache_size": len(self.local_cache),
            "local_cache_size_mb": sum(
                len(pickle.dumps(entry["data"])) 
                for entry in self.local_cache.values()
            ) / (1024 * 1024),
            "evictions": self.cache_stats["evictions"],
            "most_accessed_keys": self._get_most_accessed_keys()
        }
    
    def _get_most_accessed_keys(self) -> List[Tuple[str, int]]:
        """Get most frequently accessed cache keys"""
        key_access_counts = [
            (key, len(access_list)) 
            for key, access_list in self.access_patterns.items()
        ]
        return sorted(key_access_counts, key=lambda x: x[1], reverse=True)[:10]


class WorkloadBalancer:
    """Intelligent workload balancing and auto-scaling"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.worker_pool = None
        self.active_workers = 0
        self.queue = asyncio.Queue()
        self.performance_history = deque(maxlen=100)
        self.load_threshold = 0.8
        self.scale_up_cooldown = 60  # seconds
        self.scale_down_cooldown = 300  # seconds
        self.last_scale_action = 0
        
    async def initialize(self):
        """Initialize workload balancer"""
        try:
            self.worker_pool = ThreadPoolExecutor(max_workers=self.config.max_workers)
            logger.info(f"WorkloadBalancer initialized with {self.config.max_workers} workers")
            
        except Exception as e:
            logger.error(f"Failed to initialize WorkloadBalancer: {e}")
            raise
    
    async def submit_task(
        self, 
        func: Callable, 
        *args, 
        priority: int = 1,
        **kwargs
    ) -> asyncio.Future:
        """Submit task with intelligent scheduling"""
        try:
            # Create task wrapper with monitoring
            wrapped_task = self._wrap_task(func, *args, **kwargs)
            
            # Submit to thread pool
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(self.worker_pool, wrapped_task)
            
            # Monitor performance
            await self._monitor_performance()
            
            return future
            
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise
    
    def _wrap_task(self, func: Callable, *args, **kwargs) -> Callable:
        """Wrap task with performance monitoring"""
        def wrapper():
            start_time = time.time()
            start_cpu = psutil.cpu_percent()
            start_memory = psutil.virtual_memory().percent
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                result = None
                success = False
            
            end_time = time.time()
            end_cpu = psutil.cpu_percent()
            end_memory = psutil.virtual_memory().percent
            
            # Record performance metrics
            metrics = {
                "execution_time": end_time - start_time,
                "cpu_delta": end_cpu - start_cpu,
                "memory_delta": end_memory - start_memory,
                "success": success,
                "timestamp": end_time
            }
            
            self.performance_history.append(metrics)
            
            return result
        
        return wrapper
    
    async def _monitor_performance(self):
        """Monitor performance and trigger auto-scaling if needed"""
        try:
            if not self.config.auto_scaling_enabled:
                return
            
            current_time = time.time()
            
            # Check cooldown period
            if current_time - self.last_scale_action < self.scale_up_cooldown:
                return
            
            # Calculate current load
            current_load = self._calculate_current_load()
            
            # Scale up if needed
            if current_load > self.load_threshold and self.active_workers < self.config.max_workers * 2:
                await self._scale_up()
            
            # Scale down if needed
            elif (current_load < 0.3 and 
                  self.active_workers > self.config.max_workers // 2 and
                  current_time - self.last_scale_action > self.scale_down_cooldown):
                await self._scale_down()
                
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
    
    def _calculate_current_load(self) -> float:
        """Calculate current system load"""
        try:
            # CPU load
            cpu_load = psutil.cpu_percent() / 100.0
            
            # Memory load
            memory_load = psutil.virtual_memory().percent / 100.0
            
            # Queue load (if available)
            queue_load = min(self.queue.qsize() / (self.config.max_workers * 2), 1.0)
            
            # Worker utilization
            worker_load = self.active_workers / self.config.max_workers
            
            # Weighted average
            total_load = (cpu_load * 0.3 + memory_load * 0.2 + 
                         queue_load * 0.3 + worker_load * 0.2)
            
            return total_load
            
        except Exception as e:
            logger.error(f"Load calculation error: {e}")
            return 0.5
    
    async def _scale_up(self):
        """Scale up worker pool"""
        try:
            new_max_workers = min(
                self.config.max_workers * 2,
                multiprocessing.cpu_count() * 4
            )
            
            if new_max_workers > self.worker_pool._max_workers:
                self.worker_pool._max_workers = new_max_workers
                self.last_scale_action = time.time()
                
                logger.info(f"Scaled up to {new_max_workers} workers")
                
        except Exception as e:
            logger.error(f"Scale up error: {e}")
    
    async def _scale_down(self):
        """Scale down worker pool"""
        try:
            new_max_workers = max(
                self.config.max_workers // 2,
                multiprocessing.cpu_count()
            )
            
            if new_max_workers < self.worker_pool._max_workers:
                self.worker_pool._max_workers = new_max_workers
                self.last_scale_action = time.time()
                
                logger.info(f"Scaled down to {new_max_workers} workers")
                
        except Exception as e:
            logger.error(f"Scale down error: {e}")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            recent_metrics = list(self.performance_history)[-10:]
            
            if not recent_metrics:
                return {"status": "no_data"}
            
            avg_execution_time = np.mean([m["execution_time"] for m in recent_metrics])
            success_rate = np.mean([m["success"] for m in recent_metrics]) * 100
            current_load = self._calculate_current_load()
            
            return {
                "active_workers": self.active_workers,
                "max_workers": self.worker_pool._max_workers,
                "queue_size": self.queue.qsize(),
                "average_execution_time": avg_execution_time,
                "success_rate": success_rate,
                "current_load": current_load,
                "total_tasks_processed": len(self.performance_history)
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"status": "error"}


class BatchProcessor:
    """Intelligent batch processing optimization"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.pending_batches = defaultdict(list)
        self.batch_timers = {}
        self.processing_stats = defaultdict(list)
        
    async def add_to_batch(
        self, 
        batch_type: str, 
        item: Any, 
        callback: Callable = None
    ):
        """Add item to batch with intelligent batching"""
        try:
            self.pending_batches[batch_type].append({
                "item": item,
                "callback": callback,
                "timestamp": time.time()
            })
            
            # Check if batch should be processed
            if await self._should_process_batch(batch_type):
                await self._process_batch(batch_type)
                
        except Exception as e:
            logger.error(f"Failed to add item to batch {batch_type}: {e}")
    
    async def _should_process_batch(self, batch_type: str) -> bool:
        """Determine if batch should be processed now"""
        batch = self.pending_batches[batch_type]
        
        # Process if batch is full
        if len(batch) >= self.config.batch_size:
            return True
        
        # Process if oldest item is too old
        if batch:
            oldest_timestamp = min(item["timestamp"] for item in batch)
            if time.time() - oldest_timestamp > 30:  # 30 seconds
                return True
        
        # Process based on system load
        current_load = psutil.cpu_percent() / 100.0
        if current_load < 0.5 and len(batch) >= self.config.batch_size // 2:
            return True
        
        return False
    
    async def _process_batch(self, batch_type: str):
        """Process accumulated batch"""
        try:
            batch = self.pending_batches[batch_type]
            if not batch:
                return
            
            start_time = time.time()
            
            # Extract items and callbacks
            items = [entry["item"] for entry in batch]
            callbacks = [entry["callback"] for entry in batch if entry["callback"]]
            
            # Clear the batch
            self.pending_batches[batch_type] = []
            
            # Process batch based on type
            if batch_type == "indexing":
                await self._process_indexing_batch(items, callbacks)
            elif batch_type == "search":
                await self._process_search_batch(items, callbacks)
            elif batch_type == "fingerprinting":
                await self._process_fingerprinting_batch(items, callbacks)
            
            # Record processing statistics
            processing_time = time.time() - start_time
            self.processing_stats[batch_type].append({
                "batch_size": len(items),
                "processing_time": processing_time,
                "throughput": len(items) / processing_time,
                "timestamp": time.time()
            })
            
            logger.info(f"Processed {batch_type} batch: {len(items)} items in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to process batch {batch_type}: {e}")
    
    async def _process_indexing_batch(self, items: List[Any], callbacks: List[Callable]):
        """Process indexing batch"""
        # Implementation would depend on specific indexing logic
        for i, item in enumerate(items):
            try:
                # Process item
                result = await self._process_indexing_item(item)
                
                # Execute callback if provided
                if i < len(callbacks) and callbacks[i]:
                    callbacks[i](result)
                    
            except Exception as e:
                logger.error(f"Failed to process indexing item: {e}")
    
    async def _process_search_batch(self, items: List[Any], callbacks: List[Callable]):
        """Process search batch"""
        # Implementation would depend on specific search logic
        for i, item in enumerate(items):
            try:
                # Process item
                result = await self._process_search_item(item)
                
                # Execute callback if provided
                if i < len(callbacks) and callbacks[i]:
                    callbacks[i](result)
                    
            except Exception as e:
                logger.error(f"Failed to process search item: {e}")
    
    async def _process_fingerprinting_batch(self, items: List[Any], callbacks: List[Callable]):
        """Process fingerprinting batch"""
        # Implementation would depend on specific fingerprinting logic
        for i, item in enumerate(items):
            try:
                # Process item
                result = await self._process_fingerprinting_item(item)
                
                # Execute callback if provided
                if i < len(callbacks) and callbacks[i]:
                    callbacks[i](result)
                    
            except Exception as e:
                logger.error(f"Failed to process fingerprinting item: {e}")
    
    async def _process_indexing_item(self, item: Any) -> Any:
        """Process individual indexing item"""
        # Placeholder - would be implemented based on specific requirements
        await asyncio.sleep(0.1)  # Simulate processing
        return {"status": "indexed", "item_id": str(item)}
    
    async def _process_search_item(self, item: Any) -> Any:
        """Process individual search item"""
        # Placeholder - would be implemented based on specific requirements
        await asyncio.sleep(0.05)  # Simulate processing
        return {"status": "searched", "results": []}
    
    async def _process_fingerprinting_item(self, item: Any) -> Any:
        """Process individual fingerprinting item"""
        # Placeholder - would be implemented based on specific requirements
        await asyncio.sleep(0.2)  # Simulate processing
        return {"status": "fingerprinted", "hash": "abc123"}
    
    async def get_batch_statistics(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        try:
            stats = {}
            
            for batch_type, batch_stats in self.processing_stats.items():
                if batch_stats:
                    recent_stats = batch_stats[-10:]  # Last 10 batches
                    
                    stats[batch_type] = {
                        "total_batches": len(batch_stats),
                        "average_batch_size": np.mean([s["batch_size"] for s in recent_stats]),
                        "average_processing_time": np.mean([s["processing_time"] for s in recent_stats]),
                        "average_throughput": np.mean([s["throughput"] for s in recent_stats]),
                        "pending_items": len(self.pending_batches[batch_type])
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get batch statistics: {e}")
            return {}


class OptimizationEngine:
    """Main optimization engine coordinating all optimization strategies"""
    
    def __init__(self, config: OptimizationConfig, redis_url: str):
        self.config = config
        self.redis_client = None
        self.cache = None
        self.workload_balancer = None
        self.batch_processor = None
        self.optimization_history = deque(maxlen=100)
        
    async def initialize(self):
        """Initialize optimization engine"""
        try:
            # Initialize Redis client
            self.redis_client = Redis.from_url(redis_url)
            await self.redis_client.ping()
            
            # Initialize components
            self.cache = IntelligentCache(self.config, self.redis_client)
            self.workload_balancer = WorkloadBalancer(self.config)
            self.batch_processor = BatchProcessor(self.config)
            
            await self.workload_balancer.initialize()
            
            logger.info("OptimizationEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OptimizationEngine: {e}")
            raise
    
    async def optimize_performance(self) -> OptimizationResult:
        """Perform comprehensive performance optimization"""
        try:
            # Collect baseline metrics
            metrics_before = await self._collect_performance_metrics()
            
            # Apply optimization strategies based on config
            optimizations_applied = []
            
            if self.config.strategy in [OptimizationStrategy.PERFORMANCE, OptimizationStrategy.BALANCED]:
                await self._optimize_cpu_usage()
                optimizations_applied.append("cpu_optimization")
                
            if self.config.strategy in [OptimizationStrategy.MEMORY, OptimizationStrategy.BALANCED]:
                await self._optimize_memory_usage()
                optimizations_applied.append("memory_optimization")
                
            if self.config.strategy in [OptimizationStrategy.THROUGHPUT, OptimizationStrategy.BALANCED]:
                await self._optimize_throughput()
                optimizations_applied.append("throughput_optimization")
                
            if self.config.strategy in [OptimizationStrategy.LATENCY, OptimizationStrategy.BALANCED]:
                await self._optimize_latency()
                optimizations_applied.append("latency_optimization")
            
            # Collect post-optimization metrics
            await asyncio.sleep(5)  # Allow time for optimizations to take effect
            metrics_after = await self._collect_performance_metrics()
            
            # Calculate improvements
            performance_improvement = self._calculate_improvement(metrics_before, metrics_after)
            resource_savings = self._calculate_resource_savings(metrics_before, metrics_after)
            recommendations = await self._generate_recommendations(metrics_after)
            
            result = OptimizationResult(
                strategy_applied=", ".join(optimizations_applied),
                performance_improvement=performance_improvement,
                resource_savings=resource_savings,
                recommendations=recommendations,
                metrics_before=metrics_before,
                metrics_after=metrics_after
            )
            
            self.optimization_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize performance: {e}")
            raise
    
    async def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        try:
            cpu_usage = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            
            # GPU usage (if available)
            gpu_usage = 0.0
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_usage = gpus[0].load * 100
            except:
                pass
            
            # Cache hit rate
            cache_stats = await self.cache.get_cache_statistics()
            cache_hit_rate = cache_stats.get("hit_rate", 0.0)
            
            # Workload metrics
            workload_metrics = await self.workload_balancer.get_performance_metrics()
            
            return PerformanceMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                gpu_usage=gpu_usage,
                throughput=workload_metrics.get("total_tasks_processed", 0),
                latency_ms=workload_metrics.get("average_execution_time", 0) * 1000,
                cache_hit_rate=cache_hit_rate,
                queue_depth=workload_metrics.get("queue_size", 0),
                active_workers=workload_metrics.get("active_workers", 0),
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return PerformanceMetrics(
                cpu_usage=0, memory_usage=0, gpu_usage=0,
                throughput=0, latency_ms=0, cache_hit_rate=0,
                queue_depth=0, active_workers=0,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        try:
            # Adjust worker pool size based on CPU usage
            current_cpu = psutil.cpu_percent()
            
            if current_cpu > 90:
                # Scale down workers
                await self.workload_balancer._scale_down()
                logger.info("Scaled down workers due to high CPU usage")
                
            elif current_cpu < 50:
                # Scale up workers if needed
                await self.workload_balancer._scale_up()
                logger.info("Scaled up workers due to low CPU usage")
                
        except Exception as e:
            logger.error(f"CPU optimization error: {e}")
    
    async def _optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            memory_info = psutil.virtual_memory()
            
            if memory_info.percent > 85:
                # Aggressive cache cleanup
                await self.cache._evict_if_needed()
                
                # Reduce batch sizes
                self.config.batch_size = max(self.config.batch_size // 2, 10)
                
                logger.info("Applied memory optimization due to high usage")
                
        except Exception as e:
            logger.error(f"Memory optimization error: {e}")
    
    async def _optimize_throughput(self):
        """Optimize throughput"""
        try:
            # Increase batch sizes if system can handle it
            current_load = psutil.cpu_percent() / 100.0
            
            if current_load < 0.7:
                self.config.batch_size = min(self.config.batch_size * 2, 500)
                logger.info("Increased batch size to improve throughput")
                
        except Exception as e:
            logger.error(f"Throughput optimization error: {e}")
    
    async def _optimize_latency(self):
        """Optimize latency"""
        try:
            # Reduce batch sizes for lower latency
            self.config.batch_size = max(self.config.batch_size // 2, 5)
            
            # Enable more aggressive caching
            self.config.cache_ttl_seconds = 7200  # 2 hours
            
            logger.info("Applied latency optimizations")
            
        except Exception as e:
            logger.error(f"Latency optimization error: {e}")
    
    def _calculate_improvement(
        self, 
        before: PerformanceMetrics, 
        after: PerformanceMetrics
    ) -> float:
        """Calculate overall performance improvement percentage"""
        try:
            improvements = []
            
            # CPU improvement (lower is better)
            if before.cpu_usage > 0:
                cpu_improvement = (before.cpu_usage - after.cpu_usage) / before.cpu_usage
                improvements.append(cpu_improvement)
            
            # Memory improvement (lower is better)
            if before.memory_usage > 0:
                memory_improvement = (before.memory_usage - after.memory_usage) / before.memory_usage
                improvements.append(memory_improvement)
            
            # Latency improvement (lower is better)
            if before.latency_ms > 0:
                latency_improvement = (before.latency_ms - after.latency_ms) / before.latency_ms
                improvements.append(latency_improvement)
            
            # Cache hit rate improvement (higher is better)
            cache_improvement = after.cache_hit_rate - before.cache_hit_rate
            improvements.append(cache_improvement)
            
            return np.mean(improvements) * 100 if improvements else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate improvement: {e}")
            return 0.0
    
    def _calculate_resource_savings(
        self, 
        before: PerformanceMetrics, 
        after: PerformanceMetrics
    ) -> Dict[str, float]:
        """Calculate resource savings"""
        try:
            return {
                "cpu_savings_percent": max(0, before.cpu_usage - after.cpu_usage),
                "memory_savings_percent": max(0, before.memory_usage - after.memory_usage),
                "latency_reduction_ms": max(0, before.latency_ms - after.latency_ms),
                "cache_improvement_percent": max(0, (after.cache_hit_rate - before.cache_hit_rate) * 100)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate resource savings: {e}")
            return {}
    
    async def _generate_recommendations(
        self, 
        metrics: PerformanceMetrics
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        try:
            if metrics.cpu_usage > 85:
                recommendations.append("Consider scaling horizontally or optimizing CPU-intensive operations")
            
            if metrics.memory_usage > 80:
                recommendations.append("Implement more aggressive memory management or increase available RAM")
            
            if metrics.cache_hit_rate < 0.7:
                recommendations.append("Optimize caching strategy or increase cache size")
            
            if metrics.queue_depth > metrics.active_workers * 10:
                recommendations.append("Increase worker pool size or optimize task processing")
            
            if metrics.latency_ms > 1000:
                recommendations.append("Optimize processing algorithms or implement request prioritization")
            
            if not recommendations:
                recommendations.append("System performance is optimal")
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
