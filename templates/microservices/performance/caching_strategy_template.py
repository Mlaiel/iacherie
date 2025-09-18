#!/usr/bin/env python3
"""
📊 CACHING STRATEGY TEMPLATE - ENTERPRISE PERFORMANCE OPTIMIZATION
==================================================================

Multi-layer caching strategy with Redis, Memcached, and in-memory optimization
for high-performance microservices with intelligent cache invalidation.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
🚨 UTILISATION COMMERCIALE INTERDITE SANS AUTORISATION ÉCRITE

🎯 EXPERTISE COMBINÉE:
- Performance Engineer: Cache optimization and strategies
- Backend Senior: Redis clustering and data structures  
- DevOps: Cache infrastructure and monitoring
- DBA: Cache invalidation and consistency patterns
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from datetime import datetime, timedelta
import redis.asyncio as redis
import aiomemcached
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategy types"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"

class CacheLayer(Enum):
    """Cache layer types"""
    L1_MEMORY = "l1_memory"      # In-process memory
    L2_REDIS = "l2_redis"        # Redis cluster
    L3_MEMCACHED = "l3_memcached" # Memcached cluster
    L4_DISK = "l4_disk"          # Disk-based cache

@dataclass
class CacheConfig:
    """Cache configuration"""
    strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    layers: List[CacheLayer] = field(default_factory=lambda: [CacheLayer.L1_MEMORY, CacheLayer.L2_REDIS])
    ttl_seconds: int = 3600
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    compression_enabled: bool = True
    encryption_enabled: bool = False
    replication_factor: int = 2
    consistency_level: str = "eventual"

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    error_count: int = 0
    total_requests: int = 0
    average_response_time_ms: float = 0.0
    memory_usage_bytes: int = 0

class CachingStrategyTemplate:
    """
    🚀 ENTERPRISE CACHING STRATEGY TEMPLATE
    
    Multi-layer caching system with intelligent strategies, automatic
    invalidation, performance monitoring, and high availability support.
    
    **Expertise Performance Engineer + Backend Senior + DevOps**
    """
    
    def __init__(self, config: CacheConfig):
        """Initialize caching strategy"""
        self.config = config
        self.metrics = CacheMetrics()
        self.cache_layers: Dict[CacheLayer, Any] = {}
        self.invalidation_callbacks: List[Callable] = []
        self.health_status = True
        
        # Initialize cache layers
        asyncio.create_task(self._initialize_cache_layers())
    
    async def _initialize_cache_layers(self):
        """Initialize configured cache layers"""
        try:
            for layer in self.config.layers:
                if layer == CacheLayer.L1_MEMORY:
                    self.cache_layers[layer] = MemoryCache(self.config.max_memory_size)
                elif layer == CacheLayer.L2_REDIS:
                    self.cache_layers[layer] = await self._create_redis_client()
                elif layer == CacheLayer.L3_MEMCACHED:
                    self.cache_layers[layer] = await self._create_memcached_client()
                elif layer == CacheLayer.L4_DISK:
                    self.cache_layers[layer] = DiskCache()
                    
            logger.info(f"✅ Initialized cache layers: {list(self.cache_layers.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Cache layer initialization failed: {e}")
            self.health_status = False
    
    async def _create_redis_client(self) -> redis.Redis:
        """Create Redis cluster client"""
        return redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={}
        )
    
    async def _create_memcached_client(self):
        """Create Memcached client"""
        return aiomemcached.Client('127.0.0.1', 11211)
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with multi-layer fallback"""
        start_time = time.time()
        
        try:
            # Try each cache layer in order
            for layer in self.config.layers:
                cache_client = self.cache_layers.get(layer)
                if not cache_client:
                    continue
                    
                try:
                    value = await self._get_from_layer(cache_client, layer, key)
                    if value is not None:
                        self.metrics.hit_count += 1
                        self._update_response_time(start_time)
                        
                        # Populate higher-priority layers
                        await self._populate_higher_layers(key, value, layer)
                        return value
                        
                except Exception as e:
                    logger.warning(f"Cache layer {layer} get failed: {e}")
                    self.metrics.error_count += 1
            
            # Cache miss
            self.metrics.miss_count += 1
            self._update_response_time(start_time)
            return default
            
        except Exception as e:
            logger.error(f"Cache get operation failed: {e}")
            self.metrics.error_count += 1
            return default
        finally:
            self.metrics.total_requests += 1
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache using configured strategy"""
        try:
            ttl = ttl or self.config.ttl_seconds
            
            if self.config.strategy == CacheStrategy.WRITE_THROUGH:
                return await self._write_through(key, value, ttl)
            elif self.config.strategy == CacheStrategy.WRITE_BEHIND:
                return await self._write_behind(key, value, ttl)
            elif self.config.strategy == CacheStrategy.WRITE_AROUND:
                return await self._write_around(key, value, ttl)
            else:  # CACHE_ASIDE
                return await self._cache_aside_set(key, value, ttl)
                
        except Exception as e:
            logger.error(f"Cache set operation failed: {e}")
            self.metrics.error_count += 1
            return False
    
    async def _write_through(self, key: str, value: Any, ttl: int) -> bool:
        """Write-through cache strategy"""
        success = True
        
        # Write to all cache layers simultaneously
        tasks = []
        for layer in self.config.layers:
            cache_client = self.cache_layers.get(layer)
            if cache_client:
                task = self._set_in_layer(cache_client, layer, key, value, ttl)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success = all(r is True for r in results if not isinstance(r, Exception))
        
        return success
    
    async def _write_behind(self, key: str, value: Any, ttl: int) -> bool:
        """Write-behind (lazy write) cache strategy"""
        # Write to fastest layer first
        primary_layer = self.config.layers[0] if self.config.layers else None
        if primary_layer:
            cache_client = self.cache_layers.get(primary_layer)
            if cache_client:
                await self._set_in_layer(cache_client, primary_layer, key, value, ttl)
        
        # Schedule background writes to other layers
        asyncio.create_task(self._background_write(key, value, ttl))
        return True
    
    async def _background_write(self, key: str, value: Any, ttl: int):
        """Background write to secondary cache layers"""
        for layer in self.config.layers[1:]:
            try:
                cache_client = self.cache_layers.get(layer)
                if cache_client:
                    await self._set_in_layer(cache_client, layer, key, value, ttl)
            except Exception as e:
                logger.warning(f"Background write to {layer} failed: {e}")
    
    async def _get_from_layer(self, client: Any, layer: CacheLayer, key: str) -> Any:
        """Get value from specific cache layer"""
        if layer == CacheLayer.L1_MEMORY:
            return client.get(key)
        elif layer == CacheLayer.L2_REDIS:
            value = await client.get(key)
            return json.loads(value) if value else None
        elif layer == CacheLayer.L3_MEMCACHED:
            return await client.get(key.encode())
        elif layer == CacheLayer.L4_DISK:
            return await client.get(key)
        
        return None
    
    async def _set_in_layer(self, client: Any, layer: CacheLayer, key: str, value: Any, ttl: int) -> bool:
        """Set value in specific cache layer"""
        try:
            if layer == CacheLayer.L1_MEMORY:
                return client.set(key, value, ttl)
            elif layer == CacheLayer.L2_REDIS:
                serialized = json.dumps(value)
                return await client.setex(key, ttl, serialized)
            elif layer == CacheLayer.L3_MEMCACHED:
                return await client.set(key.encode(), value, exptime=ttl)
            elif layer == CacheLayer.L4_DISK:
                return await client.set(key, value, ttl)
            
            return False
            
        except Exception as e:
            logger.error(f"Set operation failed for layer {layer}: {e}")
            return False
    
    async def invalidate(self, pattern: str = None, keys: List[str] = None):
        """Invalidate cache entries by pattern or specific keys"""
        try:
            if keys:
                # Invalidate specific keys
                for key in keys:
                    await self._invalidate_key(key)
            elif pattern:
                # Invalidate by pattern
                await self._invalidate_pattern(pattern)
                
            # Trigger invalidation callbacks
            for callback in self.invalidation_callbacks:
                try:
                    await callback(pattern, keys)
                except Exception as e:
                    logger.warning(f"Invalidation callback failed: {e}")
                    
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
    
    async def _invalidate_key(self, key: str):
        """Invalidate specific key from all layers"""
        for layer in self.config.layers:
            cache_client = self.cache_layers.get(layer)
            if cache_client:
                try:
                    if layer == CacheLayer.L1_MEMORY:
                        cache_client.delete(key)
                    elif layer == CacheLayer.L2_REDIS:
                        await cache_client.delete(key)
                    elif layer == CacheLayer.L3_MEMCACHED:
                        await cache_client.delete(key.encode())
                    elif layer == CacheLayer.L4_DISK:
                        await cache_client.delete(key)
                except Exception as e:
                    logger.warning(f"Key invalidation failed for layer {layer}: {e}")
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics"""
        if self.metrics.total_requests > 0:
            hit_rate = self.metrics.hit_count / self.metrics.total_requests
            self.metrics.hit_rate = hit_rate
        
        return self.metrics
    
    def _update_response_time(self, start_time: float):
        """Update average response time"""
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if self.metrics.total_requests == 0:
            self.metrics.average_response_time_ms = response_time
        else:
            # Calculate rolling average
            total_time = self.metrics.average_response_time_ms * self.metrics.total_requests
            self.metrics.average_response_time_ms = (total_time + response_time) / (self.metrics.total_requests + 1)

class MemoryCache:
    """In-memory LRU cache implementation"""
    
    def __init__(self, max_size: int):
        """Initialize memory cache"""
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.current_size = 0
    
    def get(self, key: str) -> Any:
        """Get value from memory cache"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in memory cache with LRU eviction"""
        try:
            # Check if eviction is needed
            if self.current_size >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = value
            self.access_times[key] = time.time()
            self.current_size += 1
            
            # Schedule TTL expiration
            asyncio.create_task(self._schedule_expiration(key, ttl))
            return True
            
        except Exception as e:
            logger.error(f"Memory cache set failed: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from memory cache"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
            self.current_size -= 1
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
            
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        self.delete(lru_key)
    
    async def _schedule_expiration(self, key: str, ttl: int):
        """Schedule key expiration"""
        await asyncio.sleep(ttl)
        self.delete(key)

class DiskCache:
    """Simple disk-based cache for large objects"""
    
    def __init__(self, cache_dir: str = "/tmp/cache"):
        """Initialize disk cache"""
        self.cache_dir = cache_dir
        import os
        os.makedirs(cache_dir, exist_ok=True)
    
    async def get(self, key: str) -> Any:
        """Get value from disk cache"""
        try:
            import os
            file_path = os.path.join(self.cache_dir, self._hash_key(key))
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Disk cache get failed: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in disk cache"""
        try:
            import os
            file_path = os.path.join(self.cache_dir, self._hash_key(key))
            with open(file_path, 'w') as f:
                json.dump(value, f)
            
            # Schedule cleanup after TTL
            asyncio.create_task(self._schedule_cleanup(file_path, ttl))
            return True
            
        except Exception as e:
            logger.error(f"Disk cache set failed: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from disk cache"""
        try:
            import os
            file_path = os.path.join(self.cache_dir, self._hash_key(key))
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Disk cache delete failed: {e}")
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    async def _schedule_cleanup(self, file_path: str, ttl: int):
        """Schedule file cleanup after TTL"""
        await asyncio.sleep(ttl)
        try:
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Disk cache cleanup failed: {e}")

# Cache strategy factory
def create_caching_strategy(strategy_type: CacheStrategy, **kwargs) -> CachingStrategyTemplate:
    """Factory function to create caching strategy instances"""
    config = CacheConfig(strategy=strategy_type, **kwargs)
    return CachingStrategyTemplate(config)