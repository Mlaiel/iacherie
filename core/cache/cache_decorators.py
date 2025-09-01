"""Cache Decorators for IA Influencer Agent Platform
Comprehensive caching decorators and utilities for automatic cache management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
import functools
import inspect
import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class CacheMode(Enum):
    """
Cache operation modes"""

    READ_THROUGH = "read_through"
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"
    REFRESH_AHEAD = "refresh_ahead"

class InvalidationTrigger(Enum):
    """Cache invalidation triggers"""

    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    SIZE_BASED = "size_based"
    ACCESS_BASED = "access_based"
    DEPENDENCY_BASED = "dependency_based"

@dataclass
class CacheConfig:
    """Cache configuration for decorators"""
    ttl: Optional[int] = None
    namespace: str = "default"
    mode: CacheMode = CacheMode.READ_THROUGH
    invalidation_trigger: InvalidationTrigger = InvalidationTrigger.TIME_BASED
    max_size: Optional[int] = None
    serialize: bool = True
    compress: bool = False
    key_prefix: str = ""
    tags: List[str] = None
    dependency_keys: List[str] = None
    refresh_threshold: float = 0.8  # Refresh when 80% of TTL elapsed
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependency_keys is None:
            self.dependency_keys = []

class CacheDecoratorManager:
    """Manage cache decorators and their configurations"""
    
    def __init__(self):
        self.cache_instances = {}
        self.configurations = {}
        self.metrics = defaultdict(lambda: {
            'calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0,
            'cache_time': 0.0,
            'compute_time': 0.0
        })
        self._lock = threading.RLock()
        
        logger.info("CacheDecoratorManager initialized")
    
    def register_cache(self, name: str, cache_instance):
        """Register cache instance"""
        self.cache_instances[name] = cache_instance
    
    def get_cache(self, name: str = "default"):
        """Get cache instance by name"""
        return self.cache_instances.get(name)
    
    def update_metrics(self, func_name: str, hit: bool, cache_time: float, compute_time: float):
        """
Update cache metrics"""
        with self._lock:
            metrics = self.metrics[func_name]
            metrics['calls'] += 1
            if hit:
                metrics['cache_hits'] += 1
                metrics['cache_time'] += cache_time
            else:
                metrics['cache_misses'] += 1
                metrics['compute_time'] += compute_time
            metrics['total_time'] += cache_time + compute_time
    
    def get_metrics(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """
Get cache metrics"""
        with self._lock:
            if func_name:
                metrics = self.metrics.get(func_name, {})
                if metrics.get('calls', 0) > 0:
                    metrics['hit_rate'] = metrics['cache_hits'] / metrics['calls']
                    metrics['average_cache_time'] = metrics['cache_time'] / max(metrics['cache_hits'], 1)
                    metrics['average_compute_time'] = metrics['compute_time'] / max(metrics['cache_misses'], 1)
                return metrics
            else:
                return dict(self.metrics)

# Global decorator manager
_decorator_manager = CacheDecoratorManager()

def register_cache_instance(name: str, cache_instance):
    """
Register cache instance globally"""
    _decorator_manager.register_cache(name, cache_instance)

def get_cache_metrics(func_name: Optional[str] = None) -> Dict[str, Any]:
    """
Get cache metrics globally"""
    return _decorator_manager.get_metrics(func_name)

def _generate_cache_key(func: Callable, args: Tuple, kwargs: Dict[str, Any], config: CacheConfig) -> str:
    """
Generate cache key for function call"""
    # Build key components
    key_parts = []
    
    # Add namespace and prefix
    if config.namespace:
        key_parts.append(config.namespace)
    if config.key_prefix:
        key_parts.append(config.key_prefix)
    
    # Add function name
    key_parts.append(f"{func.__module__}.{func.__qualname__}")
    
    # Add arguments
    arg_hash = _hash_arguments(args, kwargs)
    key_parts.append(arg_hash)
    
    return ":".join(key_parts)

def _hash_arguments(args: Tuple, kwargs: Dict[str, Any]) -> str:
    """Generate hash for function arguments"""
    # Create a stable representation of arguments
    arg_repr = []
    
    # Process positional arguments
    for arg in args:
        arg_repr.append(_serialize_argument(arg))
    
    # Process keyword arguments (sorted for consistency)
    for key in sorted(kwargs.keys()):
        arg_repr.append(f"{key}={_serialize_argument(kwargs[key])}")
    
    # Generate hash
    arg_string = "|".join(arg_repr)
    return hashlib.md5(arg_string.encode()).hexdigest()

def _serialize_argument(arg: Any) -> str:
    """Serialize argument to string"""
    try:
        if hasattr(arg, '__dict__'):
            # Object with attributes
            return f"{type(arg).__name__}:{hash(str(arg.__dict__))}"
        elif hasattr(arg, '__iter__') and not isinstance(arg, (str, bytes)):
            # Iterable (list, tuple, set, etc.)
            return f"{type(arg).__name__}:{hash(str(sorted(str(item) for item in arg)))}"
        else:
            # Simple types
            return str(arg)
    except Exception:
        # Fallback for unhashable types
        return f"{type(arg).__name__}:{id(arg)}"

def cached(
    ttl: Optional[int] = None,
    namespace: str = "default",
    cache_name: str = "default",
    mode: CacheMode = CacheMode.READ_THROUGH,
    key_prefix: str = "",
    tags: Optional[List[str]] = None,
    dependency_keys: Optional[List[str]] = None,
    serialize: bool = True,
    compress: bool = False,
    refresh_threshold: float = 0.8
):
    """
    Cache decorator for function results
    
    Args:
        ttl: Time to live in seconds
        namespace: Cache namespace
        cache_name: Name of cache instance to use
        mode: Cache operation mode
        key_prefix: Prefix for cache keys
        tags: Tags for cache invalidation
        dependency_keys: Keys this cache depends on
        serialize: Whether to serialize the result
        compress: Whether to compress the cached data
        refresh_threshold: Threshold for refresh-ahead pattern
    """
    
    def decorator(func: Callable) -> Callable:
        config = CacheConfig(
            ttl=ttl,
            namespace=namespace,
            mode=mode,
            key_prefix=key_prefix,
            tags=tags or [],
            dependency_keys=dependency_keys or [],
            serialize=serialize,
            compress=compress,
            refresh_threshold=refresh_threshold
        )
        
        if asyncio.iscoroutinefunction(func):
            return _async_cached_wrapper(func, config, cache_name)
        else:
            return _sync_cached_wrapper(func, config, cache_name)
    
    return decorator

def _async_cached_wrapper(func: Callable, config: CacheConfig, cache_name: str) -> Callable:
    """
Async cache wrapper"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cache = _decorator_manager.get_cache(cache_name)
        if not cache:
            logger.warning(f"Cache '{cache_name}' not found, executing function directly")
            return await func(*args, **kwargs)
        
        # Generate cache key
        cache_key = _generate_cache_key(func, args, kwargs, config)
        func_name = f"{func.__module__}.{func.__qualname__}"
        
        start_time = time.time()
        
        try:
            # Try to get from cache
            cache_start = time.time()
            cached_result = await cache.get(cache_key)
            cache_time = time.time() - cache_start
            
            if cached_result is not None:
                # Cache hit
                _decorator_manager.update_metrics(func_name, True, cache_time, 0.0)
                
                # Check if refresh needed (refresh-ahead pattern)
                if config.mode == CacheMode.REFRESH_AHEAD and config.ttl:
                    if hasattr(cache, 'get_ttl'):
                        remaining_ttl = await cache.get_ttl(cache_key)
                        if remaining_ttl and remaining_ttl < config.ttl * (1 - config.refresh_threshold):
                            # Refresh in background
                            asyncio.create_task(_refresh_cache_async(func, args, kwargs, cache, cache_key, config))
                
                return _deserialize_result(cached_result, config)
            
            # Cache miss - compute result
            compute_start = time.time()
            result = await func(*args, **kwargs)
            compute_time = time.time() - compute_start
            
            # Store in cache
            if config.mode in [CacheMode.READ_THROUGH, CacheMode.WRITE_THROUGH]:
                serialized_result = _serialize_result(result, config)
                await cache.set(cache_key, serialized_result, ttl=config.ttl)
                
                # Set tags if supported
                if config.tags and hasattr(cache, 'tag'):
                    for tag in config.tags:
                        await cache.tag(cache_key, tag)
            
            _decorator_manager.update_metrics(func_name, False, cache_time, compute_time)
            return result
            
        except Exception as e:
            logger.error(f"Cache error for {func_name}: {e}")
            # Fallback to direct execution
            compute_start = time.time()
            result = await func(*args, **kwargs)
            compute_time = time.time() - compute_start
            _decorator_manager.update_metrics(func_name, False, 0.0, compute_time)
            return result
    
    return wrapper

def _sync_cached_wrapper(func: Callable, config: CacheConfig, cache_name: str) -> Callable:
    """Sync cache wrapper"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache = _decorator_manager.get_cache(cache_name)
        if not cache:
            logger.warning(f"Cache '{cache_name}' not found, executing function directly")
            return func(*args, **kwargs)
        
        # Generate cache key
        cache_key = _generate_cache_key(func, args, kwargs, config)
        func_name = f"{func.__module__}.{func.__qualname__}"
        
        start_time = time.time()
        
        try:
            # Try to get from cache (sync cache operations)
            cache_start = time.time()
            cached_result = None
            if hasattr(cache, 'get_sync'):
                cached_result = cache.get_sync(cache_key)
            elif hasattr(cache, 'get'):
                # For async caches, use asyncio.run (not recommended in production)
                try:
                    loop = asyncio.get_event_loop()
                    cached_result = loop.run_until_complete(cache.get(cache_key))
                except RuntimeError:
                    # No event loop running
                    cached_result = asyncio.run(cache.get(cache_key))
            
            cache_time = time.time() - cache_start
            
            if cached_result is not None:
                # Cache hit
                _decorator_manager.update_metrics(func_name, True, cache_time, 0.0)
                return _deserialize_result(cached_result, config)
            
            # Cache miss - compute result
            compute_start = time.time()
            result = func(*args, **kwargs)
            compute_time = time.time() - compute_start
            
            # Store in cache
            if config.mode in [CacheMode.READ_THROUGH, CacheMode.WRITE_THROUGH]:
                serialized_result = _serialize_result(result, config)
                if hasattr(cache, 'set_sync'):
                    cache.set_sync(cache_key, serialized_result, ttl=config.ttl)
                elif hasattr(cache, 'set'):
                    try:
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(cache.set(cache_key, serialized_result, ttl=config.ttl))
                    except RuntimeError:
                        asyncio.run(cache.set(cache_key, serialized_result, ttl=config.ttl))
            
            _decorator_manager.update_metrics(func_name, False, cache_time, compute_time)
            return result
            
        except Exception as e:
            logger.error(f"Cache error for {func_name}: {e}")
            # Fallback to direct execution
            compute_start = time.time()
            result = func(*args, **kwargs)
            compute_time = time.time() - compute_start
            _decorator_manager.update_metrics(func_name, False, 0.0, compute_time)
            return result
    
    return wrapper

async def _refresh_cache_async(func: Callable, args: Tuple, kwargs: Dict, cache, cache_key: str, config: CacheConfig):
    """Refresh cache entry in background"""
    try:
        result = await func(*args, **kwargs)
        serialized_result = _serialize_result(result, config)
        await cache.set(cache_key, serialized_result, ttl=config.ttl)
        logger.debug(f"Refreshed cache key: {cache_key}")
    except Exception as e:
        logger.error(f"Failed to refresh cache key {cache_key}: {e}")

def _serialize_result(result: Any, config: CacheConfig) -> Union[str, bytes, Any]:
    """Serialize result for caching"""
    if not config.serialize:
        return result
    
    try:
        if config.compress:
            import gzip
            serialized = json.dumps(result, default=str).encode()
            return gzip.compress(serialized)
        else:
            return json.dumps(result, default=str)
    except Exception as e:
        logger.warning(f"Failed to serialize result: {e}")
        return result

def _deserialize_result(cached_data: Union[str, bytes, Any], config: CacheConfig) -> Any:
    """Deserialize cached result"""
    if not config.serialize:
        return cached_data
    
    try:
        if config.compress:
            import gzip
            if isinstance(cached_data, bytes):
                decompressed = gzip.decompress(cached_data)
                return json.loads(decompressed.decode())
        else:
            if isinstance(cached_data, str):
                return json.loads(cached_data)
        
        return cached_data
    except Exception as e:
        logger.warning(f"Failed to deserialize cached data: {e}")
        return cached_data

def cache_invalidate(
    pattern: Optional[str] = None,
    tags: Optional[List[str]] = None,
    namespace: str = "default",
    cache_name: str = "default"
):
    """
    Decorator to invalidate cache entries after function execution
    
    Args:
        pattern: Key pattern to invalidate
        tags: Tags to invalidate
        namespace: Cache namespace
        cache_name: Name of cache instance to use
    """
    
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            return _async_invalidate_wrapper(func, pattern, tags, namespace, cache_name)
        else:
            return _sync_invalidate_wrapper(func, pattern, tags, namespace, cache_name)
    
    return decorator

def _async_invalidate_wrapper(func: Callable, pattern: Optional[str], tags: Optional[List[str]], namespace: str, cache_name: str) -> Callable:
    """
Async invalidation wrapper"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        
        cache = _decorator_manager.get_cache(cache_name)
        if cache:
            try:
                if pattern:
                    # Invalidate by pattern
                    full_pattern = f"{namespace}:{pattern}" if namespace != "default" else pattern
                    if hasattr(cache, 'delete_pattern'):
                        await cache.delete_pattern(full_pattern)
                
                if tags:
                    # Invalidate by tags
                    for tag in tags:
                        if hasattr(cache, 'invalidate_tag'):
                            await cache.invalidate_tag(tag)
                
            except Exception as e:
                logger.error(f"Cache invalidation error: {e}")
        
        return result
    
    return wrapper

def _sync_invalidate_wrapper(func: Callable, pattern: Optional[str], tags: Optional[List[str]], namespace: str, cache_name: str) -> Callable:
    """Sync invalidation wrapper"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        cache = _decorator_manager.get_cache(cache_name)
        if cache:
            try:
                if pattern:
                    # Invalidate by pattern
                    full_pattern = f"{namespace}:{pattern}" if namespace != "default" else pattern
                    if hasattr(cache, 'delete_pattern_sync'):
                        cache.delete_pattern_sync(full_pattern)
                    elif hasattr(cache, 'delete_pattern'):
                        try:
                            loop = asyncio.get_event_loop()
                            loop.run_until_complete(cache.delete_pattern(full_pattern))
                        except RuntimeError:
                            asyncio.run(cache.delete_pattern(full_pattern))
                
                if tags:
                    # Invalidate by tags
                    for tag in tags:
                        if hasattr(cache, 'invalidate_tag_sync'):
                            cache.invalidate_tag_sync(tag)
                        elif hasattr(cache, 'invalidate_tag'):
                            try:
                                loop = asyncio.get_event_loop()
                                loop.run_until_complete(cache.invalidate_tag(tag))
                            except RuntimeError:
                                asyncio.run(cache.invalidate_tag(tag))
                
            except Exception as e:
                logger.error(f"Cache invalidation error: {e}")
        
        return result
    
    return wrapper

def memoize(
    ttl: Optional[int] = None,
    max_size: Optional[int] = 1000,
    typed: bool = False
):
    """
    Simple memoization decorator using local memory
    
    Args:
        ttl: Time to live in seconds
        max_size: Maximum number of cached items
        typed: Whether to consider argument types in cache key
    """
    
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_info = {'hits': 0, 'misses': 0, 'maxsize': max_size, 'currsize': 0}
        lock = threading.RLock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = []
            key_parts.extend(args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            if typed:
                key_parts.extend(type(arg).__name__ for arg in args)
                key_parts.extend(type(v).__name__ for v in kwargs.values())
            
            cache_key = hash(tuple(str(part) for part in key_parts))
            
            with lock:
                # Check if cached
                if cache_key in cache:
                    cached_value, timestamp = cache[cache_key]
                    
                    # Check TTL
                    if ttl is None or (time.time() - timestamp) < ttl:
                        cache_info['hits'] += 1
                        return cached_value
                    else:
                        # Expired
                        del cache[cache_key]
                        cache_info['currsize'] -= 1
                
                # Cache miss
                cache_info['misses'] += 1
                result = func(*args, **kwargs)
                
                # Store in cache
                if max_size is None or cache_info['currsize'] < max_size:
                    cache[cache_key] = (result, time.time())
                    cache_info['currsize'] += 1
                elif max_size is not None and cache:
                    # Remove oldest entry (simple FIFO)
                    oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                    del cache[oldest_key]
                    cache[cache_key] = (result, time.time())
                
                return result
        
        # Add cache info methods
        def cache_info_func():
            with lock:
                return cache_info.copy()
        
        def cache_clear():
            with lock:
                cache.clear()
                cache_info['hits'] = cache_info['misses'] = 0
                cache_info['currsize'] = 0
        
        wrapper.cache_info = cache_info_func
        wrapper.cache_clear = cache_clear
        
        return wrapper
    
    return decorator

def cache_warmup(
    cache_name: str = "default",
    namespace: str = "default",
    batch_size: int = 100
):
    """
    Decorator for cache warmup functions
    
    Args:
        cache_name: Name of cache instance to use
        namespace: Cache namespace
        batch_size: Batch size for warmup operations
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache = _decorator_manager.get_cache(cache_name)
            if not cache:
                logger.warning(f"Cache '{cache_name}' not found for warmup")
                return []
            
            logger.info(f"Starting cache warmup with {func.__name__}")
            start_time = time.time()
            
            # Execute warmup function
            warmup_data = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            if not warmup_data:
                logger.warning("No warmup data returned")
                return []
            
            # Batch load into cache
            loaded_count = 0
            failed_count = 0
            
            for i in range(0, len(warmup_data), batch_size):
                batch = warmup_data[i:i + batch_size]
                
                for item in batch:
                    try:
                        key = item.get('key')
                        value = item.get('value')
                        ttl = item.get('ttl')
                        
                        if key and value is not None:
                            full_key = f"{namespace}:{key}" if namespace != "default" else key
                            
                            if asyncio.iscoroutinefunction(cache.set):
                                await cache.set(full_key, value, ttl=ttl)
                            else:
                                cache.set(full_key, value, ttl=ttl)
                            
                            loaded_count += 1
                    except Exception as e:
                        logger.error(f"Failed to load warmup item: {e}")
                        failed_count += 1
            
            elapsed_time = time.time() - start_time
            logger.info(f"Cache warmup completed: {loaded_count} items loaded, {failed_count} failed in {elapsed_time:.2f}s")
            
            return {
                'loaded_count': loaded_count,
                'failed_count': failed_count,
                'elapsed_time': elapsed_time,
                'items_per_second': loaded_count / elapsed_time if elapsed_time > 0 else 0
            }
        
        return wrapper
    
    return decorator

def rate_limited_cache(
    calls_per_second: int = 100,
    cache_name: str = "default"
):
    """
    Rate-limited cache decorator to prevent cache overload
    
    Args:
        calls_per_second: Maximum cache calls per second
        cache_name: Name of cache instance to use
    """
    
    def decorator(func: Callable) -> Callable:
        call_times = []
        lock = threading.RLock()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with lock:
                now = time.time()
                
                # Remove old timestamps
                call_times[:] = [t for t in call_times if now - t < 1.0]
                
                # Check rate limit
                if len(call_times) >= calls_per_second:
                    sleep_time = 1.0 - (now - call_times[0])
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                        now = time.time()
                        call_times[:] = [t for t in call_times if now - t < 1.0]
                
                call_times.append(now)
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def cache_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    cache_name: str = "default"
):
    """
    Circuit breaker pattern for cache operations
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Timeout before attempting to close circuit
        cache_name: Name of cache instance to use
    """
    
    def decorator(func: Callable) -> Callable:
        failure_count = 0
        last_failure_time = 0
        circuit_open = False
        lock = threading.RLock()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal failure_count, last_failure_time, circuit_open
            
            with lock:
                now = time.time()
                
                # Check if circuit should be closed
                if circuit_open and (now - last_failure_time) > recovery_timeout:
                    circuit_open = False
                    failure_count = 0
                    logger.info(f"Circuit breaker closed for {func.__name__}")
                
                # If circuit is open, skip cache operation
                if circuit_open:
                    logger.warning(f"Circuit breaker open for {func.__name__}, skipping cache")
                    return None
            
            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Reset failure count on success
                with lock:
                    failure_count = 0
                
                return result
                
            except Exception as e:
                with lock:
                    failure_count += 1
                    last_failure_time = time.time()
                    
                    if failure_count >= failure_threshold:
                        circuit_open = True
                        logger.error(f"Circuit breaker opened for {func.__name__} after {failure_count} failures")
                
                logger.error(f"Cache operation failed: {e}")
                raise
        
        return wrapper
    
    return decorator

# Utility functions for decorator management

def clear_cache_metrics():
    """Clear all cache metrics"""
    _decorator_manager.metrics.clear()

def get_cache_decorator_stats() -> Dict[str, Any]:
    """
Get comprehensive cache decorator statistics"""
    return {
        'registered_caches': list(_decorator_manager.cache_instances.keys()),
        'function_metrics': _decorator_manager.get_metrics(),
        'total_functions': len(_decorator_manager.metrics),
        'total_calls': sum(m.get('calls', 0) for m in _decorator_manager.metrics.values()),
        'total_cache_hits': sum(m.get('cache_hits', 0) for m in _decorator_manager.metrics.values()),
        'total_cache_misses': sum(m.get('cache_misses', 0) for m in _decorator_manager.metrics.values())
    }

def optimize_cache_decorators() -> Dict[str, Any]:
    """
Analyze and optimize cache decorator configurations"""
    metrics = _decorator_manager.get_metrics()
    recommendations = {}
    
    for func_name, stats in metrics.items():
        if stats.get('calls', 0) == 0:
            continue
        
        hit_rate = stats.get('hit_rate', 0.0)
        avg_cache_time = stats.get('average_cache_time', 0.0)
        avg_compute_time = stats.get('average_compute_time', 0.0)
        
        func_recommendations = []
        
        if hit_rate < 0.5:
            func_recommendations.append({
                'type': 'low_hit_rate',
                'message': f'Hit rate is {hit_rate:.2%}, consider increasing TTL or cache size',
                'action': 'increase_ttl'
            })
        
        if avg_cache_time > avg_compute_time * 0.5:
            func_recommendations.append({
                'type': 'cache_overhead',
                'message': f'Cache overhead is high ({avg_cache_time:.3f}s vs {avg_compute_time:.3f}s compute)',
                'action': 'optimize_serialization'
            })
        
        if hit_rate > 0.95 and avg_compute_time < 0.001:  # 1ms
            func_recommendations.append({
                'type': 'over_caching',
                'message': 'Function is very fast, caching may not be beneficial',
                'action': 'consider_removing_cache'
            })
        
        recommendations[func_name] = {
            'stats': stats,
            'recommendations': func_recommendations,
            'health_score': _calculate_cache_health_score(stats)
        }
    
    return recommendations

def _calculate_cache_health_score(stats: Dict[str, Any]) -> str:
    """
Calculate cache health score for a function"""
    hit_rate = stats.get('hit_rate', 0.0)
    calls = stats.get('calls', 0)
    
    if calls < 10:
        return 'insufficient_data'
    
    if hit_rate > 0.9:
        return 'excellent'
    elif hit_rate > 0.8:
        return 'good'
    elif hit_rate > 0.6:
        return 'fair'
    else:
        return 'poor'
