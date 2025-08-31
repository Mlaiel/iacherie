"""
Cache Management Utilities for IA Influencer Agent Platform
Advanced caching, memory optimization, and performance monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import redis
import json
import pickle
import asyncio
import time
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from collections import defaultdict, OrderedDict
import threading
import psutil
import gc

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    REFRESH_AHEAD = "refresh_ahead"


class CacheLevel(Enum):
    """Cache level enumeration"""
    L1_MEMORY = "l1_memory"  # In-memory cache
    L2_REDIS = "l2_redis"    # Redis cache
    L3_DATABASE = "l3_database"  # Database cache


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    avg_access_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 1
    ttl: Optional[int] = None
    size: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return (datetime.utcnow() - self.created_at).seconds > self.ttl


class MemoryOptimizer:
    """Advanced memory optimization and monitoring"""
    
    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.memory_warnings = []
        self.optimization_history = []
        
    def monitor_memory_usage(self) -> Dict[str, Any]:
        """Monitor current memory usage"""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        memory_info = {
            'total_memory_gb': round(memory.total / (1024**3), 2),
            'available_memory_gb': round(memory.available / (1024**3), 2),
            'used_memory_percent': memory.percent,
            'process_memory_mb': round(process.memory_info().rss / (1024**2), 2),
            'process_memory_percent': process.memory_percent(),
            'memory_threshold_exceeded': memory.percent > self.max_memory_percent
        }
        
        if memory_info['memory_threshold_exceeded']:
            self._trigger_memory_optimization()
            
        return memory_info
    
    def _trigger_memory_optimization(self):
        """Trigger memory optimization procedures"""
        logger.warning(f"Memory usage exceeded {self.max_memory_percent}%, triggering optimization")
        
        optimization_result = {
            'timestamp': datetime.utcnow(),
            'pre_optimization_memory': psutil.virtual_memory().percent,
            'actions_taken': []
        }
        
        # Force garbage collection
        gc.collect()
        optimization_result['actions_taken'].append('garbage_collection')
        
        # Clear unnecessary caches
        self._clear_low_priority_caches()
        optimization_result['actions_taken'].append('cache_cleanup')
        
        optimization_result['post_optimization_memory'] = psutil.virtual_memory().percent
        self.optimization_history.append(optimization_result)
        
    def _clear_low_priority_caches(self):
        """Clear low priority cache entries"""
        # This would integrate with the cache manager
        # to clear least recently used or expired entries
        pass
    
    def optimize_data_structures(self, data: Any) -> Any:
        """Optimize data structures for memory efficiency"""
        if isinstance(data, dict):
            # Convert to more memory-efficient structure if large
            if len(data) > 1000:
                return self._optimize_large_dict(data)
        elif isinstance(data, list):
            if len(data) > 10000:
                return self._optimize_large_list(data)
        
        return data
    
    def _optimize_large_dict(self, data: dict) -> dict:
        """Optimize large dictionary structures"""
        # Remove None values and empty collections
        optimized = {
            k: v for k, v in data.items() 
            if v is not None and (not isinstance(v, (list, dict)) or v)
        }
        return optimized
    
    def _optimize_large_list(self, data: list) -> list:
        """Optimize large list structures"""
        # Remove None values and duplicates while preserving order
        seen = set()
        optimized = []
        for item in data:
            if item is not None and item not in seen:
                optimized.append(item)
                seen.add(item)
        return optimized


class RedisHandler:
    """Advanced Redis cache handler with clustering support"""
    
    def __init__(self, 
                 host: str = 'localhost', 
                 port: int = 6379, 
                 db: int = 0,
                 password: Optional[str] = None,
                 cluster_mode: bool = False):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.cluster_mode = cluster_mode
        self.connection_pool = None
        self.client = None
        self._connect()
        
    def _connect(self):
        """Establish Redis connection"""



        try:
            if self.cluster_mode:
                # Redis Cluster configuration
                from rediscluster import RedisCluster
                startup_nodes = [{"host": self.host, "port": self.port}]
                self.client = RedisCluster(
                    startup_nodes=startup_nodes,
                    decode_responses=True,
                    password=self.password
                )
            else:
                # Single Redis instance
                self.connection_pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                    max_connections=50
                )
                self.client = redis.Redis(connection_pool=self.connection_pool)
                
            # Test connection
            self.client.ping()
            logger.info(f"Redis connection established: {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""



        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return pickle.loads(value.encode('latin-1'))
                
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""



        try:
            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = pickle.dumps(value).decode('latin-1')
            
            # Set with TTL if provided
            if ttl:
                result = self.client.setex(key, ttl, serialized_value)
            else:
                result = self.client.set(key, serialized_value)
                
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""



        try:
            result = self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""



        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {str(e)}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get Redis server information"""



        try:
            info = self.client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {str(e)}")
            return {}


class CacheManager:
    """Comprehensive multi-level cache management system"""
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 default_ttl: int = 3600,
                 max_memory_entries: int = 10000):
        self.default_ttl = default_ttl
        self.max_memory_entries = max_memory_entries
        
        # Multi-level cache storage
        self.l1_cache = OrderedDict()  # Memory cache
        self.l2_redis = None  # Redis cache
        
        # Cache statistics
        self.stats = {
            CacheLevel.L1_MEMORY: CacheStats(),
            CacheLevel.L2_REDIS: CacheStats()
        }
        
        # Initialize Redis if config provided
        if redis_config:
            try:
                self.l2_redis = RedisHandler(**redis_config)
            except Exception as e:
                logger.warning(f"Redis initialization failed: {str(e)}")
        
        # Memory optimizer
        self.memory_optimizer = MemoryOptimizer()
        
        # Cache strategies
        self.strategies = {
            CacheStrategy.LRU: self._lru_eviction,
            CacheStrategy.LFU: self._lfu_eviction,
            CacheStrategy.FIFO: self._fifo_eviction
        }
        
        # Background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        def cleanup_task():
            while True:
                try:
                    self._cleanup_expired_entries()
                    self._update_memory_stats()
                    time.sleep(300)  # Run every 5 minutes
                except Exception as e:
                    logger.error(f"Cleanup task error: {str(e)}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from multi-level cache"""
        start_time = time.time()
        
        try:
            # Check L1 memory cache first
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if not entry.is_expired:
                    # Update access information
                    entry.accessed_at = datetime.utcnow()
                    entry.access_count += 1
                    # Move to end (LRU)
                    self.l1_cache.move_to_end(key)
                    
                    self.stats[CacheLevel.L1_MEMORY].hits += 1
                    return entry.value
                else:
                    # Remove expired entry
                    del self.l1_cache[key]
            
            # Check L2 Redis cache
            if self.l2_redis:
                redis_value = await self.l2_redis.get(key)
                if redis_value is not None:
                    # Store in L1 cache for faster future access
                    await self._store_l1(key, redis_value)
                    
                    self.stats[CacheLevel.L2_REDIS].hits += 1
                    return redis_value
                else:
                    self.stats[CacheLevel.L2_REDIS].misses += 1
            
            # Cache miss
            self.stats[CacheLevel.L1_MEMORY].misses += 1
            return default
            
        finally:
            # Update access time statistics
            access_time = time.time() - start_time
            for level_stats in self.stats.values():
                level_stats.avg_access_time = (
                    level_stats.avg_access_time * 0.9 + access_time * 0.1
                )
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  strategy: CacheStrategy = CacheStrategy.LRU) -> bool:
        """Set value in multi-level cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            # Store in L1 memory cache
            await self._store_l1(key, value, ttl)
            
            # Store in L2 Redis cache
            if self.l2_redis:
                await self.l2_redis.set(key, value, ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache SET error for key {key}: {str(e)}")
            return False
    
    async def _store_l1(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in L1 memory cache"""
        # Check if we need to evict entries
        if len(self.l1_cache) >= self.max_memory_entries:
            await self._evict_entries(1)
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl,
            size=self._calculate_size(value)
        )
        
        self.l1_cache[key] = entry
        self.l1_cache.move_to_end(key)  # For LRU
        
        # Update memory usage
        self.stats[CacheLevel.L1_MEMORY].memory_usage += entry.size
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        deleted = False
        
        # Delete from L1
        if key in self.l1_cache:
            entry = self.l1_cache.pop(key)
            self.stats[CacheLevel.L1_MEMORY].memory_usage -= entry.size
            deleted = True
        
        # Delete from L2
        if self.l2_redis:
            redis_deleted = await self.l2_redis.delete(key)
            deleted = deleted or redis_deleted
        
        return deleted
    
    async def clear(self, pattern: Optional[str] = None):
        """Clear cache entries matching pattern"""
        if pattern is None:
            # Clear all
            self.l1_cache.clear()
            self.stats[CacheLevel.L1_MEMORY].memory_usage = 0
        else:
            # Clear by pattern (simplified)
            keys_to_delete = [k for k in self.l1_cache.keys() if pattern in k]
            for key in keys_to_delete:
                await self.delete(key)
    
    async def _evict_entries(self, count: int):
        """Evict entries using configured strategy"""
        evicted = 0
        
        while evicted < count and self.l1_cache:
            # Default LRU eviction
            key, entry = self.l1_cache.popitem(last=False)
            self.stats[CacheLevel.L1_MEMORY].memory_usage -= entry.size
            self.stats[CacheLevel.L1_MEMORY].evictions += 1
            evicted += 1
    
    def _lru_eviction(self) -> str:
        """LRU eviction strategy"""



        return next(iter(self.l1_cache))
    
    def _lfu_eviction(self) -> str:
        """LFU eviction strategy"""



        return min(self.l1_cache.keys(), 
                  key=lambda k: self.l1_cache[k].access_count)
    
    def _fifo_eviction(self) -> str:
        """FIFO eviction strategy"""



        return min(self.l1_cache.keys(), 
                  key=lambda k: self.l1_cache[k].created_at)
    
    def _cleanup_expired_entries(self):
        """Remove expired entries from L1 cache"""
        expired_keys = [
            key for key, entry in self.l1_cache.items() 
            if entry.is_expired
        ]
        
        for key in expired_keys:
            entry = self.l1_cache.pop(key)
            self.stats[CacheLevel.L1_MEMORY].memory_usage -= entry.size
            self.stats[CacheLevel.L1_MEMORY].evictions += 1
    
    def _update_memory_stats(self):
        """Update memory usage statistics"""
        total_size = sum(entry.size for entry in self.l1_cache.values())
        self.stats[CacheLevel.L1_MEMORY].memory_usage = total_size
        
        # Update last updated timestamp
        for stats in self.stats.values():
            stats.last_updated = datetime.utcnow()
    
    def _calculate_size(self, obj: Any) -> int:
        """Calculate approximate size of object in bytes"""



        try:
            return len(pickle.dumps(obj))
        except Exception:
            # Fallback estimation
            if isinstance(obj, str):
                return len(obj.encode('utf-8'))
            elif isinstance(obj, (int, float)):
                return 8
            elif isinstance(obj, dict):
                return sum(self._calculate_size(k) + self._calculate_size(v) 
                          for k, v in obj.items())
            elif isinstance(obj, list):
                return sum(self._calculate_size(item) for item in obj)
            else:
                return 64  # Default estimate
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive cache statistics"""
        stats_dict = {}
        
        for level, stats in self.stats.items():
            stats_dict[level.value] = {
                'hits': stats.hits,
                'misses': stats.misses,
                'hit_ratio': stats.hit_ratio,
                'evictions': stats.evictions,
                'memory_usage_mb': round(stats.memory_usage / (1024 * 1024), 2),
                'avg_access_time_ms': round(stats.avg_access_time * 1000, 2),
                'last_updated': stats.last_updated.isoformat()
            }
        
        # Add L1 specific stats
        stats_dict['l1_memory']['entry_count'] = len(self.l1_cache)
        stats_dict['l1_memory']['max_entries'] = self.max_memory_entries
        stats_dict['l1_memory']['memory_utilization'] = round(
            (len(self.l1_cache) / self.max_memory_entries) * 100, 2
        )
        
        # Add Redis stats if available
        if self.l2_redis:
            redis_info = self.l2_redis.get_info()
            stats_dict['l2_redis'].update(redis_info)
        
        return stats_dict


class PerformanceMonitor:
    """Performance monitoring and optimization for cache operations"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.performance_history = []
        self.alert_thresholds = {
            'hit_ratio_min': 0.8,
            'avg_access_time_max': 0.01,  # 10ms
            'memory_usage_max': 0.8  # 80% of max
        }
    
    def monitor_performance(self) -> Dict[str, Any]:
        """Monitor cache performance and generate alerts"""
        stats = self.cache_manager.get_stats()
        alerts = []
        recommendations = []
        
        for level, level_stats in stats.items():
            # Check hit ratio
            if level_stats['hit_ratio'] < self.alert_thresholds['hit_ratio_min']:
                alerts.append(f"Low hit ratio in {level}: {level_stats['hit_ratio']:.2%}")
                recommendations.append(f"Increase cache size or TTL for {level}")
            
            # Check access time
            if level_stats['avg_access_time_ms'] > self.alert_thresholds['avg_access_time_max'] * 1000:
                alerts.append(f"High access time in {level}: {level_stats['avg_access_time_ms']:.2f}ms")
                recommendations.append(f"Optimize data serialization for {level}")
            
            # Check memory usage (L1 only)
            if level == 'l1_memory':
                if level_stats['memory_utilization'] > self.alert_thresholds['memory_usage_max'] * 100:
                    alerts.append(f"High memory usage: {level_stats['memory_utilization']:.1f}%")
                    recommendations.append("Increase max_memory_entries or implement more aggressive eviction")
        
        performance_report = {
            'timestamp': datetime.utcnow(),
            'stats': stats,
            'alerts': alerts,
            'recommendations': recommendations,
            'overall_health': 'good' if not alerts else 'warning' if len(alerts) < 3 else 'critical'
        }
        
        self.performance_history.append(performance_report)
        
        # Keep only last 100 reports
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
        
        return performance_report
    
    def get_performance_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over specified period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_reports = [
            report for report in self.performance_history
            if report['timestamp'] >= cutoff_time
        ]
        
        if not recent_reports:
            return {'status': 'insufficient_data'}
        
        # Calculate trends
        l1_hit_ratios = [r['stats']['l1_memory']['hit_ratio'] for r in recent_reports]
        l1_access_times = [r['stats']['l1_memory']['avg_access_time_ms'] for r in recent_reports]
        
        return {
            'period_hours': hours,
            'report_count': len(recent_reports),
            'hit_ratio_trend': {
                'current': l1_hit_ratios[-1] if l1_hit_ratios else 0,
                'average': sum(l1_hit_ratios) / len(l1_hit_ratios) if l1_hit_ratios else 0,
                'min': min(l1_hit_ratios) if l1_hit_ratios else 0,
                'max': max(l1_hit_ratios) if l1_hit_ratios else 0
            },
            'access_time_trend': {
                'current': l1_access_times[-1] if l1_access_times else 0,
                'average': sum(l1_access_times) / len(l1_access_times) if l1_access_times else 0,
                'min': min(l1_access_times) if l1_access_times else 0,
                'max': max(l1_access_times) if l1_access_times else 0
            }
        }


def cache_decorator(ttl: int = 3600, key_prefix: str = "", cache_manager: Optional[CacheManager] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            if cache_manager:
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if cache_manager:
                await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, create simple key-based caching
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Simple in-memory cache for sync functions
            if not hasattr(sync_wrapper, '_cache'):
                sync_wrapper._cache = {}
            
            if cache_key in sync_wrapper._cache:
                entry_time, cached_result = sync_wrapper._cache[cache_key]
                if time.time() - entry_time < ttl:
                    return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            sync_wrapper._cache[cache_key] = (time.time(), result)
            
            # Clean old entries
            current_time = time.time()
            sync_wrapper._cache = {
                k: v for k, v in sync_wrapper._cache.items()
                if current_time - v[0] < ttl
            }
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
