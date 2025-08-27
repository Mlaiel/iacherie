"""
🚀 Performance Optimization Engine for Content Fingerprinting
=============================================================

Advanced performance optimization system with GPU acceleration, 
intelligent caching, and dynamic resource allocation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import time
import gc
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
from enum import Enum
import threading
import queue
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import os

try:
    import torch
    import torch.nn as nn
    import torch.cuda
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

import numpy as np
from functools import lru_cache, wraps
import pickle
import hashlib
import redis

from .models import ContentType, ProcessingMetrics
from .utils import get_optimal_batch_size

logger = logging.getLogger(__name__)

class OptimizationLevel(str, Enum):
    """Performance optimization levels."""
    MINIMAL = "minimal"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"

class ResourceType(str, Enum):
    """System resource types."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    DISK = "disk"
    NETWORK = "network"

@dataclass
class ResourceProfile:
    """System resource profile for optimization."""
    cpu_cores: int
    cpu_frequency: float
    memory_total_gb: float
    memory_available_gb: float
    gpu_count: int
    gpu_memory_gb: float
    disk_type: str  # ssd, hdd, nvme
    disk_available_gb: float
    network_bandwidth_mbps: float

@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""
    level: OptimizationLevel = OptimizationLevel.BALANCED
    enable_gpu: bool = True
    enable_multiprocessing: bool = True
    enable_caching: bool = True
    cache_size_mb: int = 1024
    max_workers: Optional[int] = None
    batch_size_auto: bool = True
    memory_limit_gb: Optional[float] = None
    gpu_memory_fraction: float = 0.8
    prefetch_factor: int = 2
    enable_compression: bool = True
    enable_async_io: bool = True

class GPUAccelerator:
    """GPU acceleration utilities for fingerprinting operations."""
    
    def __init__(self):
        self.available = TORCH_AVAILABLE and torch.cuda.is_available()
        self.device_count = torch.cuda.device_count() if self.available else 0
        self.current_device = 0
        self.memory_pool = {}
        
        if self.available:
            self._initialize_gpu()
    
    def _initialize_gpu(self):
        """Initialize GPU environment for optimal performance."""
        try:
            # Set memory fraction
            torch.cuda.set_per_process_memory_fraction(0.8)
            
            # Enable cuDNN optimizations
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            
            # Set up memory pool for each GPU
            for i in range(self.device_count):
                with torch.cuda.device(i):
                    # Pre-allocate memory pool
                    self.memory_pool[i] = torch.cuda.memory.MemoryPool()
                    torch.cuda.memory.set_memory_pool(self.memory_pool[i])
            
            logger.info(f"GPU acceleration initialized with {self.device_count} devices")
            
        except Exception as e:
            logger.warning(f"GPU initialization failed: {e}")
            self.available = False
    
    def get_optimal_device(self) -> int:
        """Get the optimal GPU device based on memory availability."""
        if not self.available:
            return -1
        
        best_device = 0
        max_free_memory = 0
        
        for i in range(self.device_count):
            free_memory = torch.cuda.get_device_properties(i).total_memory - torch.cuda.memory_allocated(i)
            if free_memory > max_free_memory:
                max_free_memory = free_memory
                best_device = i
        
        return best_device
    
    def optimize_tensor_operations(self, tensor: torch.Tensor) -> torch.Tensor:
        """Optimize tensor for GPU operations."""
        if not self.available:
            return tensor
        
        device = self.get_optimal_device()
        
        # Move to GPU and optimize dtype
        if tensor.dtype == torch.float64:
            tensor = tensor.float()  # Use float32 for better performance
        
        return tensor.to(f'cuda:{device}', non_blocking=True)
    
    def batch_gpu_operation(self, data_list: List[torch.Tensor], 
                           operation: Callable) -> List[torch.Tensor]:
        """Perform batched GPU operations for efficiency."""
        if not self.available or not data_list:
            return [operation(item) for item in data_list]
        
        device = self.get_optimal_device()
        
        # Batch tensors for GPU processing
        batch_size = min(len(data_list), 32)  # Optimal batch size
        results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            
            # Move batch to GPU
            gpu_batch = [item.to(f'cuda:{device}', non_blocking=True) for item in batch]
            
            # Process batch
            with torch.cuda.device(device):
                batch_results = [operation(item) for item in gpu_batch]
            
            # Move results back to CPU if needed
            cpu_results = [result.cpu() if result.is_cuda else result for result in batch_results]
            results.extend(cpu_results)
        
        return results
    
    def clear_cache(self):
        """Clear GPU memory cache."""
        if self.available:
            torch.cuda.empty_cache()
            gc.collect()

class IntelligentCache:
    """Intelligent caching system with LRU eviction and compression."""
    
    def __init__(self, max_size_mb: int = 1024, compression: bool = True):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression = compression
        self.cache = OrderedDict()
        self.size_tracker = {}
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()
        
        # Optional Redis backend for distributed caching
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
            self.redis_client.ping()
        except:
            logger.debug("Redis not available, using in-memory cache only")
    
    def _serialize(self, obj: Any) -> bytes:
        """Serialize object with optional compression."""
        data = pickle.dumps(obj)
        
        if self.compression:
            import gzip
            data = gzip.compress(data)
        
        return data
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize object with optional decompression."""
        if self.compression:
            import gzip
            data = gzip.decompress(data)
        
        return pickle.loads(data)
    
    def _generate_key(self, key: str) -> str:
        """Generate cache key with hash for consistency."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        cache_key = self._generate_key(key)
        
        with self.lock:
            # Check local cache first
            if cache_key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(cache_key)
                self.cache[cache_key] = value
                self.hits += 1
                return self._deserialize(value)
            
            # Check Redis cache
            if self.redis_client:
                try:
                    redis_value = self.redis_client.get(f"fp_cache:{cache_key}")
                    if redis_value:
                        # Store in local cache too
                        self._put_local(cache_key, redis_value)
                        self.hits += 1
                        return self._deserialize(redis_value)
                except:
                    pass
            
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Put item in cache."""
        cache_key = self._generate_key(key)
        serialized_value = self._serialize(value)
        
        with self.lock:
            # Store in local cache
            self._put_local(cache_key, serialized_value)
            
            # Store in Redis cache
            if self.redis_client:
                try:
                    self.redis_client.setex(f"fp_cache:{cache_key}", ttl_seconds, serialized_value)
                except:
                    pass
    
    def _put_local(self, cache_key: str, serialized_value: bytes):
        """Put item in local cache with LRU eviction."""
        value_size = len(serialized_value)
        
        # Remove item if it already exists
        if cache_key in self.cache:
            old_size = self.size_tracker[cache_key]
            self.current_size -= old_size
            del self.cache[cache_key]
            del self.size_tracker[cache_key]
        
        # Evict items if necessary
        while self.current_size + value_size > self.max_size_bytes and self.cache:
            oldest_key = next(iter(self.cache))
            oldest_size = self.size_tracker[oldest_key]
            self.current_size -= oldest_size
            del self.cache[oldest_key]
            del self.size_tracker[oldest_key]
        
        # Add new item
        self.cache[cache_key] = serialized_value
        self.size_tracker[cache_key] = value_size
        self.current_size += value_size
    
    def clear(self):
        """Clear all cache."""
        with self.lock:
            self.cache.clear()
            self.size_tracker.clear()
            self.current_size = 0
        
        if self.redis_client:
            try:
                # Clear Redis keys with our prefix
                keys = self.redis_client.keys("fp_cache:*")
                if keys:
                    self.redis_client.delete(*keys)
            except:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'hits': self.hits,
            'misses': self.misses,
            'size_mb': self.current_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'items': len(self.cache)
        }

class MemoryManager:
    """Advanced memory management and optimization."""
    
    def __init__(self, memory_limit_gb: Optional[float] = None):
        self.memory_limit_bytes = (memory_limit_gb * 1024**3) if memory_limit_gb else None
        self.allocations = {}
        self.peak_usage = 0
        
    def track_allocation(self, name: str, size_bytes: int):
        """Track memory allocation."""
        self.allocations[name] = size_bytes
        total_usage = sum(self.allocations.values())
        
        if total_usage > self.peak_usage:
            self.peak_usage = total_usage
        
        # Check if we're approaching limits
        if self.memory_limit_bytes and total_usage > self.memory_limit_bytes * 0.9:
            logger.warning(f"Memory usage approaching limit: {total_usage / 1024**3:.2f}GB")
            self._trigger_cleanup()
    
    def _trigger_cleanup(self):
        """Trigger memory cleanup when approaching limits."""
        # Force garbage collection
        gc.collect()
        
        # Clear PyTorch cache if available
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Log memory status
        memory = psutil.virtual_memory()
        logger.info(f"Memory cleanup triggered. System: {memory.percent}% used")
    
    def get_optimal_chunk_size(self, total_size: int, available_memory: int) -> int:
        """Calculate optimal chunk size for processing large data."""
        # Use 50% of available memory for processing
        max_chunk_size = int(available_memory * 0.5)
        
        # Ensure at least 10 chunks for parallelism
        min_chunk_size = max(total_size // 10, 1024 * 1024)  # At least 1MB
        
        return min(max_chunk_size, max(min_chunk_size, total_size // 100))

class ProcessingPipeline:
    """Optimized processing pipeline with intelligent batching."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.gpu_accelerator = GPUAccelerator()
        self.cache = IntelligentCache(config.cache_size_mb, config.enable_compression)
        self.memory_manager = MemoryManager(config.memory_limit_gb)
        
        # Pipeline components
        self.preprocessors = []
        self.processors = []
        self.postprocessors = []
        
        # Execution pools
        self.thread_pool = None
        self.process_pool = None
        
    def add_preprocessor(self, func: Callable):
        """Add preprocessing function to pipeline."""
        self.preprocessors.append(func)
    
    def add_processor(self, func: Callable):
        """Add main processing function to pipeline."""
        self.processors.append(func)
    
    def add_postprocessor(self, func: Callable):
        """Add postprocessing function to pipeline."""
        self.postprocessors.append(func)
    
    async def process_batch(self, items: List[Any]) -> List[Any]:
        """Process batch of items through optimized pipeline."""
        if not items:
            return []
        
        # Initialize execution pools if needed
        if self.thread_pool is None:
            max_workers = self.config.max_workers or min(32, (os.cpu_count() or 1) + 4)
            self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        try:
            # Stage 1: Preprocessing
            preprocessed_items = await self._run_stage(items, self.preprocessors, "preprocessing")
            
            # Stage 2: Main processing
            processed_items = await self._run_stage(preprocessed_items, self.processors, "processing")
            
            # Stage 3: Postprocessing
            final_items = await self._run_stage(processed_items, self.postprocessors, "postprocessing")
            
            return final_items
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            raise
    
    async def _run_stage(self, items: List[Any], functions: List[Callable], stage_name: str) -> List[Any]:
        """Run pipeline stage with optimizations."""
        if not functions:
            return items
        
        stage_start = time.time()
        current_items = items
        
        for func in functions:
            # Check cache first
            if self.config.enable_caching:
                cached_results = []
                uncached_items = []
                
                for item in current_items:
                    cache_key = f"{func.__name__}_{hash(str(item))}"
                    cached_result = self.cache.get(cache_key)
                    
                    if cached_result is not None:
                        cached_results.append(cached_result)
                    else:
                        uncached_items.append((item, cache_key))
                
                # Process uncached items
                if uncached_items:
                    uncached_data = [item for item, _ in uncached_items]
                    new_results = await self._execute_function(func, uncached_data)
                    
                    # Cache new results
                    for (_, cache_key), result in zip(uncached_items, new_results):
                        self.cache.put(cache_key, result)
                    
                    # Combine cached and new results
                    current_items = cached_results + new_results
                else:
                    current_items = cached_results
            else:
                current_items = await self._execute_function(func, current_items)
        
        stage_time = time.time() - stage_start
        logger.debug(f"Pipeline stage '{stage_name}' completed in {stage_time:.3f}s")
        
        return current_items
    
    async def _execute_function(self, func: Callable, items: List[Any]) -> List[Any]:
        """Execute function with optimal parallelization."""
        if not items:
            return []
        
        # Determine execution strategy
        if len(items) == 1:
            # Single item - direct execution
            return [func(items[0])]
        
        elif len(items) <= 10:
            # Small batch - thread pool
            loop = asyncio.get_event_loop()
            futures = [loop.run_in_executor(self.thread_pool, func, item) for item in items]
            return await asyncio.gather(*futures)
        
        else:
            # Large batch - optimize based on function characteristics
            optimal_batch_size = get_optimal_batch_size(ContentType.AUDIO)  # Default
            
            results = []
            for i in range(0, len(items), optimal_batch_size):
                batch = items[i:i + optimal_batch_size]
                
                if hasattr(func, '_supports_batch') and func._supports_batch:
                    # Function supports batch processing
                    batch_result = func(batch)
                    results.extend(batch_result)
                else:
                    # Process items individually in parallel
                    loop = asyncio.get_event_loop()
                    futures = [loop.run_in_executor(self.thread_pool, func, item) for item in batch]
                    batch_results = await asyncio.gather(*futures)
                    results.extend(batch_results)
            
            return results
    
    def cleanup(self):
        """Cleanup pipeline resources."""
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.shutdown(wait=True)
        
        self.gpu_accelerator.clear_cache()
        self.cache.clear()

class PerformanceOptimizer:
    """
    Master performance optimization system for content fingerprinting.
    
    Features:
    - GPU acceleration and intelligent device selection
    - Multi-level caching with compression and distribution
    - Memory management and automatic cleanup
    - Adaptive batch sizing and resource allocation
    - Pipeline optimization with parallel execution
    - Real-time performance monitoring and adjustment
    """
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        
        # Core components
        self.gpu_accelerator = GPUAccelerator()
        self.cache = IntelligentCache(
            self.config.cache_size_mb,
            self.config.enable_compression
        )
        self.memory_manager = MemoryManager(self.config.memory_limit_gb)
        self.pipeline = ProcessingPipeline(self.config)
        
        # Performance tracking
        self.performance_history = []
        self.optimization_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'gpu_accelerated_ops': 0,
            'total_optimized_time': 0.0
        }
        
        # System profile
        self.resource_profile = self._detect_system_profile()
        
        logger.info(f"Performance optimizer initialized with {self.config.level.value} optimization")
    
    def _detect_system_profile(self) -> ResourceProfile:
        """Detect system capabilities for optimization."""
        # CPU information
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 2000.0
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024**3)
        memory_available = memory.available / (1024**3)
        
        # GPU information
        gpu_count = 0
        gpu_memory = 0.0
        if TORCH_AVAILABLE and torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            if gpu_count > 0:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        # Disk information
        disk_usage = psutil.disk_usage('/')
        disk_available = disk_usage.free / (1024**3)
        
        return ResourceProfile(
            cpu_cores=cpu_count,
            cpu_frequency=cpu_freq,
            memory_total_gb=memory_total,
            memory_available_gb=memory_available,
            gpu_count=gpu_count,
            gpu_memory_gb=gpu_memory,
            disk_type="unknown",
            disk_available_gb=disk_available,
            network_bandwidth_mbps=1000.0  # Default assumption
        )
    
    def optimize_for_content_type(self, content_type: ContentType) -> Dict[str, Any]:
        """Get optimized configuration for specific content type."""
        base_config = {
            'batch_size': get_optimal_batch_size(content_type, self.resource_profile.memory_available_gb),
            'use_gpu': self.gpu_accelerator.available,
            'cache_enabled': self.config.enable_caching,
            'parallel_workers': min(self.resource_profile.cpu_cores, 16)
        }
        
        # Content-specific optimizations
        if content_type == ContentType.AUDIO:
            base_config.update({
                'preprocessing_threads': 4,
                'feature_extraction_batch': 16,
                'gpu_acceleration': True
            })
        elif content_type == ContentType.VIDEO:
            base_config.update({
                'frame_batch_size': 8,
                'decode_threads': 2,
                'gpu_acceleration': True,
                'memory_aggressive': True
            })
        elif content_type == ContentType.IMAGE:
            base_config.update({
                'preprocessing_batch': 32,
                'resize_workers': 8,
                'gpu_acceleration': True
            })
        elif content_type == ContentType.TEXT:
            base_config.update({
                'tokenization_batch': 64,
                'embedding_batch': 32,
                'cpu_intensive': True
            })
        
        return base_config
    
    async def optimize_processing_function(self, func: Callable) -> Callable:
        """Wrap function with performance optimizations."""
        
        @wraps(func)
        async def optimized_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Generate cache key
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if self.config.enable_caching:
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    self.optimization_stats['cache_hits'] += 1
                    return cached_result
                else:
                    self.optimization_stats['cache_misses'] += 1
            
            # Execute function with optimizations
            try:
                # GPU optimization if applicable
                if (hasattr(func, '_gpu_compatible') and func._gpu_compatible and 
                    self.gpu_accelerator.available):
                    result = await self._gpu_optimized_execution(func, *args, **kwargs)
                    self.optimization_stats['gpu_accelerated_ops'] += 1
                else:
                    result = await self._cpu_optimized_execution(func, *args, **kwargs)
                
                # Cache result
                if self.config.enable_caching:
                    self.cache.put(cache_key, result)
                
                # Track performance
                execution_time = time.time() - start_time
                self.optimization_stats['total_optimized_time'] += execution_time
                
                return result
                
            except Exception as e:
                logger.error(f"Optimized execution failed for {func.__name__}: {e}")
                raise
        
        return optimized_wrapper
    
    async def _gpu_optimized_execution(self, func: Callable, *args, **kwargs):
        """Execute function with GPU optimizations."""
        device = self.gpu_accelerator.get_optimal_device()
        
        with torch.cuda.device(device):
            # Convert numpy arrays to GPU tensors if present
            gpu_args = []
            for arg in args:
                if isinstance(arg, np.ndarray):
                    tensor = torch.from_numpy(arg)
                    gpu_args.append(self.gpu_accelerator.optimize_tensor_operations(tensor))
                else:
                    gpu_args.append(arg)
            
            # Execute function
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, func, *gpu_args, **kwargs)
            
            # Convert result back to CPU if needed
            if isinstance(result, torch.Tensor) and result.is_cuda:
                result = result.cpu().numpy()
            
            return result
    
    async def _cpu_optimized_execution(self, func: Callable, *args, **kwargs):
        """Execute function with CPU optimizations."""
        loop = asyncio.get_event_loop()
        
        # Use thread pool for I/O bound operations
        if hasattr(func, '_io_bound') and func._io_bound:
            return await loop.run_in_executor(None, func, *args, **kwargs)
        
        # Use process pool for CPU intensive operations
        elif (hasattr(func, '_cpu_intensive') and func._cpu_intensive and 
              self.config.enable_multiprocessing):
            if not self.pipeline.process_pool:
                max_workers = min(self.resource_profile.cpu_cores, 8)
                self.pipeline.process_pool = ProcessPoolExecutor(max_workers=max_workers)
            
            return await loop.run_in_executor(self.pipeline.process_pool, func, *args, **kwargs)
        
        # Default execution
        else:
            return func(*args, **kwargs)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate optimization performance report."""
        cache_stats = self.cache.get_stats()
        
        return {
            'optimization_level': self.config.level.value,
            'system_profile': {
                'cpu_cores': self.resource_profile.cpu_cores,
                'memory_gb': self.resource_profile.memory_total_gb,
                'gpu_count': self.resource_profile.gpu_count,
                'gpu_memory_gb': self.resource_profile.gpu_memory_gb
            },
            'cache_performance': cache_stats,
            'gpu_utilization': {
                'available': self.gpu_accelerator.available,
                'accelerated_operations': self.optimization_stats['gpu_accelerated_ops']
            },
            'total_optimization_time': self.optimization_stats['total_optimized_time'],
            'recommendations': self._generate_optimization_recommendations()
        }
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on performance."""
        recommendations = []
        
        cache_stats = self.cache.get_stats()
        
        if cache_stats['hit_rate'] < 0.5:
            recommendations.append("Consider increasing cache size for better hit rates")
        
        if self.resource_profile.memory_available_gb < 4:
            recommendations.append("Low available memory - consider upgrading RAM")
        
        if not self.gpu_accelerator.available and self.resource_profile.cpu_cores < 8:
            recommendations.append("Consider GPU acceleration for improved performance")
        
        if self.optimization_stats['gpu_accelerated_ops'] == 0 and self.gpu_accelerator.available:
            recommendations.append("GPU available but not utilized - enable GPU acceleration")
        
        return recommendations
    
    async def cleanup(self):
        """Clean up optimization resources."""
        self.pipeline.cleanup()
        self.gpu_accelerator.clear_cache()
        self.cache.clear()

# Export main classes
__all__ = [
    'PerformanceOptimizer', 'OptimizationConfig', 'OptimizationLevel',
    'GPUAccelerator', 'IntelligentCache', 'MemoryManager', 'ProcessingPipeline',
    'ResourceProfile', 'ResourceType'
]
