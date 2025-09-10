"""Cache Manager - Integration Response Caching
===========================================

High-performance caching system for integration responses.
Provides multi-level caching with TTL, invalidation, and smart prefetching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
import pickle
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import aioredis
import lz4.frame


class CacheLevel(Enum):
    """Cache levels."""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"


class CacheStrategy(Enum):
    """Cache strategies."""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    TTL = "ttl"              # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"


@dataclass
class CacheConfig:
    """Cache configuration."""
    integration_name: str
    enabled: bool = True
    default_ttl: int = 3600          # 1 hour in seconds
    max_memory_size: int = 1000       # Maximum items in memory
    max_disk_size: int = 10000        # Maximum items on disk
    compression_enabled: bool = True
    strategy: CacheStrategy = CacheStrategy.LRU
    write_strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH
    prefetch_enabled: bool = False
    prefetch_threshold: float = 0.8   # Prefetch when cache hit ratio drops below this
    invalidation_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    """Cache entry."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    invalidations: int = 0
    total_requests: int = 0
    hit_ratio: float = 0.0
    memory_usage_bytes: int = 0
    disk_usage_bytes: int = 0
    average_response_time: float = 0.0


class CacheManager:
    """High-performance caching system for integration responses.
    
    Provides multi-level caching with intelligent eviction policies,
    compression, and automatic prefetching for optimal performance.
    """
    
    def __init__(self, redis_url: Optional[str] = None, disk_path: str = "/tmp/ainflue_cache"):
        """Initialize cache manager."""
        self.logger = logging.getLogger(__name__)
        
        # Cache configurations by integration
        self.configs: Dict[str, CacheConfig] = {}
        
        # Memory cache (L1)
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # Redis client for distributed cache (L2)
        self.redis_client: Optional[aioredis.Redis] = None
        self.redis_url = redis_url
        
        # Disk cache path (L3)
        self.disk_path = disk_path
        
        # Cache statistics
        self.stats: Dict[str, CacheStats] = {}
        
        # LRU tracking
        self.access_order: List[str] = []
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.prefetch_task: Optional[asyncio.Task] = None
        
        # Global settings
        self.compression_threshold = 1024  # Compress if larger than 1KB
        self.cleanup_interval = 300        # 5 minutes
        self.prefetch_interval = 600       # 10 minutes
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    async def initialize(self) -> None:
        """Initialize cache manager components."""
        # Initialize Redis if URL provided
        if self.redis_url:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                self.logger.info("Redis cache backend connected")
            except Exception as e:
                self.logger.warning(f"Redis connection failed, using local cache only: {str(e)}")
        
        # Create disk cache directory
        import os
        os.makedirs(self.disk_path, exist_ok=True)
        
        # Start background tasks
        await self._start_background_tasks()
        
        self.logger.info("Cache manager initialized successfully")
    
    def _initialize_default_configs(self) -> None:
        """Initialize default cache configurations."""
        default_configs = [
            # High-cache social media platforms
            CacheConfig(
                integration_name="youtube",
                default_ttl=1800,  # 30 minutes
                max_memory_size=2000,
                prefetch_enabled=True,
                invalidation_patterns=["video_*", "channel_*"]
            ),
            CacheConfig(
                integration_name="instagram",
                default_ttl=900,   # 15 minutes
                max_memory_size=1500,
                prefetch_enabled=True,
                invalidation_patterns=["media_*", "user_*"]
            ),
            CacheConfig(
                integration_name="tiktok",
                default_ttl=600,   # 10 minutes
                max_memory_size=1000,
                prefetch_enabled=True
            ),
            CacheConfig(
                integration_name="spotify",
                default_ttl=3600,  # 1 hour
                max_memory_size=1500,
                prefetch_enabled=True,
                invalidation_patterns=["track_*", "artist_*", "playlist_*"]
            ),
            
            # AI services - shorter TTL due to dynamic nature
            CacheConfig(
                integration_name="openai",
                default_ttl=300,   # 5 minutes
                max_memory_size=500,
                compression_enabled=True,
                prefetch_enabled=False  # AI responses are usually unique
            ),
            CacheConfig(
                integration_name="anthropic",
                default_ttl=300,   # 5 minutes
                max_memory_size=500,
                compression_enabled=True,
                prefetch_enabled=False
            ),
            
            # Payment gateways - very short TTL for security
            CacheConfig(
                integration_name="stripe",
                default_ttl=60,    # 1 minute
                max_memory_size=200,
                compression_enabled=False,
                prefetch_enabled=False
            ),
            CacheConfig(
                integration_name="paypal",
                default_ttl=60,    # 1 minute
                max_memory_size=200,
                compression_enabled=False,
                prefetch_enabled=False
            ),
            
            # Cloud providers - medium TTL
            CacheConfig(
                integration_name="aws",
                default_ttl=1800,  # 30 minutes
                max_memory_size=1000,
                compression_enabled=True,
                prefetch_enabled=True
            ),
            CacheConfig(
                integration_name="gcp",
                default_ttl=1800,  # 30 minutes
                max_memory_size=1000,
                compression_enabled=True,
                prefetch_enabled=True
            ),
        ]
        
        for config in default_configs:
            self.configs[config.integration_name] = config
            self.stats[config.integration_name] = CacheStats()
    
    async def get(
        self,
        integration_name: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get value from cache with multi-level lookup."""
        start_time = time.time()
        
        try:
            if integration_name not in self.configs:
                await self._initialize_integration_cache(integration_name)
            
            config = self.configs[integration_name]
            stats = self.stats[integration_name]
            
            if not config.enabled:
                stats.misses += 1
                return default
            
            full_key = self._generate_cache_key(integration_name, key)
            
            # Try L1 cache (memory) first
            entry = await self._get_from_memory(full_key)
            if entry and not self._is_expired(entry):
                await self._update_access_stats(entry)
                stats.hits += 1
                self._update_response_time(stats, time.time() - start_time)
                return entry.value
            
            # Try L2 cache (Redis) if available
            if self.redis_client:
                entry = await self._get_from_redis(full_key)
                if entry and not self._is_expired(entry):
                    # Store in L1 for faster future access
                    await self._store_in_memory(full_key, entry)
                    await self._update_access_stats(entry)
                    stats.hits += 1
                    self._update_response_time(stats, time.time() - start_time)
                    return entry.value
            
            # Try L3 cache (disk)
            entry = await self._get_from_disk(full_key)
            if entry and not self._is_expired(entry):
                # Store in higher levels for faster future access
                await self._store_in_memory(full_key, entry)
                if self.redis_client:
                    await self._store_in_redis(full_key, entry)
                await self._update_access_stats(entry)
                stats.hits += 1
                self._update_response_time(stats, time.time() - start_time)
                return entry.value
            
            # Cache miss
            stats.misses += 1
            self._update_response_time(stats, time.time() - start_time)
            return default
            
        except Exception as e:
            self.logger.error(f"Cache get error for {integration_name}:{key}: {str(e)}")
            return default
        finally:
            self.stats[integration_name].total_requests += 1
            self._update_hit_ratio(integration_name)
    
    async def set(
        self,
        integration_name: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with multi-level storage."""
        try:
            if integration_name not in self.configs:
                await self._initialize_integration_cache(integration_name)
            
            config = self.configs[integration_name]
            
            if not config.enabled:
                return False
            
            full_key = self._generate_cache_key(integration_name, key)
            effective_ttl = ttl or config.default_ttl
            
            # Create cache entry
            entry = CacheEntry(
                key=full_key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=effective_ttl) if effective_ttl > 0 else None,
                size_bytes=self._calculate_size(value)
            )
            
            # Apply write strategy
            if config.write_strategy == CacheStrategy.WRITE_THROUGH:
                # Write to all levels
                await self._store_in_memory(full_key, entry)
                if self.redis_client:
                    await self._store_in_redis(full_key, entry)
                await self._store_in_disk(full_key, entry)
                
            elif config.write_strategy == CacheStrategy.WRITE_BACK:
                # Write to memory first, background write to other levels
                await self._store_in_memory(full_key, entry)
                asyncio.create_task(self._background_write(full_key, entry))
                
            elif config.write_strategy == CacheStrategy.WRITE_AROUND:
                # Skip cache, write directly to storage
                await self._store_in_disk(full_key, entry)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error for {integration_name}:{key}: {str(e)}")
            return False
    
    async def delete(self, integration_name: str, key: str) -> bool:
        """Delete value from all cache levels."""
        try:
            full_key = self._generate_cache_key(integration_name, key)
            
            # Remove from all levels
            await self._delete_from_memory(full_key)
            if self.redis_client:
                await self._delete_from_redis(full_key)
            await self._delete_from_disk(full_key)
            
            if integration_name in self.stats:
                self.stats[integration_name].invalidations += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache delete error for {integration_name}:{key}: {str(e)}")
            return False
    
    async def invalidate_pattern(self, integration_name: str, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            invalidated_count = 0
            
            # Get all keys matching pattern
            matching_keys = await self._find_keys_by_pattern(integration_name, pattern)
            
            # Delete matching keys
            for key in matching_keys:
                await self.delete(integration_name, key)
                invalidated_count += 1
            
            self.logger.info(f"Invalidated {invalidated_count} cache entries for pattern {pattern}")
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Cache pattern invalidation error: {str(e)}")
            return 0
    
    async def clear_integration_cache(self, integration_name: str) -> bool:
        """Clear all cache entries for integration."""
        try:
            # Find all keys for integration
            prefix = f"cache:{integration_name}:"
            
            # Clear from memory
            keys_to_remove = [key for key in self.memory_cache.keys() if key.startswith(prefix)]
            for key in keys_to_remove:
                await self._delete_from_memory(key)
            
            # Clear from Redis
            if self.redis_client:
                async for key in self.redis_client.scan_iter(match=f"{prefix}*"):
                    await self.redis_client.delete(key)
            
            # Clear from disk
            import os
            import glob
            disk_pattern = os.path.join(self.disk_path, f"{integration_name}_*.cache")
            for file_path in glob.glob(disk_pattern):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            
            # Reset stats
            if integration_name in self.stats:
                self.stats[integration_name] = CacheStats()
            
            self.logger.info(f"Cleared all cache entries for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing cache for {integration_name}: {str(e)}")
            return False
    
    async def cache_response(
        self,
        integration_name: str,
        endpoint: str,
        response_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache API response data."""
        try:
            # Generate cache key from endpoint and parameters
            cache_key = self._generate_response_cache_key(endpoint, response_data.get("params", {}))
            
            # Extract cacheable data
            cacheable_data = {
                "data": response_data.get("data"),
                "headers": response_data.get("headers", {}),
                "status_code": response_data.get("status_code"),
                "cached_at": datetime.utcnow().isoformat()
            }
            
            return await self.set(integration_name, cache_key, cacheable_data, ttl)
            
        except Exception as e:
            self.logger.error(f"Error caching response: {str(e)}")
            return False
    
    async def get_cached_response(
        self,
        integration_name: str,
        endpoint: str,
        params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached API response."""
        try:
            cache_key = self._generate_response_cache_key(endpoint, params or {})
            return await self.get(integration_name, cache_key)
            
        except Exception as e:
            self.logger.error(f"Error getting cached response: {str(e)}")
            return None
    
    async def get_cache_stats(self, integration_name: str) -> Dict[str, Any]:
        """Get cache statistics for integration."""
        if integration_name not in self.stats:
            return {"error": "Integration not found"}
        
        stats = self.stats[integration_name]
        config = self.configs.get(integration_name, CacheConfig(integration_name))
        
        # Calculate memory usage for this integration
        integration_memory_usage = sum(
            entry.size_bytes for key, entry in self.memory_cache.items()
            if key.startswith(f"cache:{integration_name}:")
        )
        
        return {
            "integration_name": integration_name,
            "enabled": config.enabled,
            "statistics": {
                "hits": stats.hits,
                "misses": stats.misses,
                "total_requests": stats.total_requests,
                "hit_ratio": round(stats.hit_ratio, 3),
                "evictions": stats.evictions,
                "invalidations": stats.invalidations,
                "average_response_time": round(stats.average_response_time, 3)
            },
            "memory_usage": {
                "bytes": integration_memory_usage,
                "entries": len([k for k in self.memory_cache.keys() if k.startswith(f"cache:{integration_name}:")])
            },
            "configuration": {
                "default_ttl": config.default_ttl,
                "max_memory_size": config.max_memory_size,
                "compression_enabled": config.compression_enabled,
                "strategy": config.strategy.value,
                "prefetch_enabled": config.prefetch_enabled
            }
        }
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global cache statistics."""
        total_hits = sum(stats.hits for stats in self.stats.values())
        total_misses = sum(stats.misses for stats in self.stats.values())
        total_requests = total_hits + total_misses
        global_hit_ratio = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        total_memory_usage = sum(entry.size_bytes for entry in self.memory_cache.values())
        total_memory_entries = len(self.memory_cache)
        
        return {
            "global_statistics": {
                "total_hits": total_hits,
                "total_misses": total_misses,
                "total_requests": total_requests,
                "global_hit_ratio": round(global_hit_ratio, 2),
                "total_evictions": sum(stats.evictions for stats in self.stats.values()),
                "total_invalidations": sum(stats.invalidations for stats in self.stats.values())
            },
            "memory_cache": {
                "total_entries": total_memory_entries,
                "total_size_bytes": total_memory_usage,
                "average_entry_size": round(total_memory_usage / total_memory_entries, 2) if total_memory_entries > 0 else 0
            },
            "integrations": len(self.configs),
            "redis_connected": self.redis_client is not None,
            "background_tasks_running": {
                "cleanup": self.cleanup_task is not None and not self.cleanup_task.done(),
                "prefetch": self.prefetch_task is not None and not self.prefetch_task.done()
            }
        }
    
    async def _initialize_integration_cache(self, integration_name: str) -> None:
        """Initialize cache for new integration."""
        if integration_name not in self.configs:
            self.configs[integration_name] = CacheConfig(integration_name=integration_name)
        
        if integration_name not in self.stats:
            self.stats[integration_name] = CacheStats()
    
    def _generate_cache_key(self, integration_name: str, key: str) -> str:
        """Generate standardized cache key."""
        return f"cache:{integration_name}:{key}"
    
    def _generate_response_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for API responses."""
        # Create deterministic key from endpoint and params
        param_string = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
        safe_endpoint = endpoint.replace("/", "_").replace("?", "_")
        return f"response_{safe_endpoint}_{param_hash}"
    
    async def _get_from_memory(self, key: str) -> Optional[CacheEntry]:
        """Get entry from memory cache."""
        return self.memory_cache.get(key)
    
    async def _store_in_memory(self, key: str, entry: CacheEntry) -> None:
        """Store entry in memory cache with LRU eviction."""
        config_name = key.split(":")[1] if ":" in key else "default"
        config = self.configs.get(config_name, CacheConfig(config_name))
        
        # Check if we need to evict
        if len(self.memory_cache) >= config.max_memory_size:
            await self._evict_memory_entries(config_name, 1)
        
        self.memory_cache[key] = entry
        
        # Update LRU order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    async def _delete_from_memory(self, key: str) -> None:
        """Delete entry from memory cache."""
        self.memory_cache.pop(key, None)
        if key in self.access_order:
            self.access_order.remove(key)
    
    async def _get_from_redis(self, key: str) -> Optional[CacheEntry]:
        """Get entry from Redis cache."""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Redis get error: {str(e)}")
        
        return None
    
    async def _store_in_redis(self, key: str, entry: CacheEntry) -> None:
        """Store entry in Redis cache."""
        if not self.redis_client:
            return
        
        try:
            ttl = int((entry.expires_at - datetime.utcnow()).total_seconds()) if entry.expires_at else 3600
            if ttl > 0:
                serialized_data = pickle.dumps(entry)
                await self.redis_client.setex(key, ttl, serialized_data)
        except Exception as e:
            self.logger.error(f"Redis store error: {str(e)}")
    
    async def _delete_from_redis(self, key: str) -> None:
        """Delete entry from Redis cache."""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                self.logger.error(f"Redis delete error: {str(e)}")
    
    async def _get_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Get entry from disk cache."""
        try:
            import os
            file_path = os.path.join(self.disk_path, f"{key.replace(':', '_')}.cache")
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    if data.startswith(b'LZ4'):  # Compressed
                        data = lz4.frame.decompress(data[3:])
                    return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Disk cache get error: {str(e)}")
        
        return None
    
    async def _store_in_disk(self, key: str, entry: CacheEntry) -> None:
        """Store entry in disk cache."""
        try:
            import os
            file_path = os.path.join(self.disk_path, f"{key.replace(':', '_')}.cache")
            
            data = pickle.dumps(entry)
            
            # Compress if configured and data is large enough
            config_name = key.split(":")[1] if ":" in key else "default"
            config = self.configs.get(config_name, CacheConfig(config_name))
            
            if config.compression_enabled and len(data) > self.compression_threshold:
                data = b'LZ4' + lz4.frame.compress(data)
                entry.compressed = True
            
            with open(file_path, 'wb') as f:
                f.write(data)
                
        except Exception as e:
            self.logger.error(f"Disk cache store error: {str(e)}")
    
    async def _delete_from_disk(self, key: str) -> None:
        """Delete entry from disk cache."""
        try:
            import os
            file_path = os.path.join(self.disk_path, f"{key.replace(':', '_')}.cache")
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.error(f"Disk cache delete error: {str(e)}")
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if not entry.expires_at:
            return False
        return datetime.utcnow() > entry.expires_at
    
    async def _update_access_stats(self, entry: CacheEntry) -> None:
        """Update access statistics for cache entry."""
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return len(str(value).encode())
    
    def _update_response_time(self, stats: CacheStats, response_time: float) -> None:
        """Update average response time."""
        alpha = 0.1  # Exponential smoothing factor
        stats.average_response_time = (
            alpha * response_time + (1 - alpha) * stats.average_response_time
        )
    
    def _update_hit_ratio(self, integration_name: str) -> None:
        """Update cache hit ratio."""
        stats = self.stats[integration_name]
        if stats.total_requests > 0:
            stats.hit_ratio = (stats.hits / stats.total_requests) * 100
    
    async def _evict_memory_entries(self, integration_name: str, count: int) -> None:
        """Evict entries from memory cache."""
        config = self.configs[integration_name]
        evicted = 0
        
        if config.strategy == CacheStrategy.LRU:
            # Remove least recently used entries
            while evicted < count and self.access_order:
                key_to_evict = self.access_order[0]
                if key_to_evict.startswith(f"cache:{integration_name}:"):
                    await self._delete_from_memory(key_to_evict)
                    self.stats[integration_name].evictions += 1
                    evicted += 1
                else:
                    self.access_order.pop(0)
    
    async def _find_keys_by_pattern(self, integration_name: str, pattern: str) -> List[str]:
        """Find cache keys matching pattern."""
        matching_keys = []
        prefix = f"cache:{integration_name}:"
        
        import re
        regex_pattern = pattern.replace("*", ".*")
        
        # Search memory cache
        for key in self.memory_cache.keys():
            if key.startswith(prefix):
                cache_key = key[len(prefix):]
                if re.match(regex_pattern, cache_key):
                    matching_keys.append(cache_key)
        
        return matching_keys
    
    async def _background_write(self, key: str, entry: CacheEntry) -> None:
        """Background write for write-back strategy."""
        try:
            if self.redis_client:
                await self._store_in_redis(key, entry)
            await self._store_in_disk(key, entry)
        except Exception as e:
            self.logger.error(f"Background write error: {str(e)}")
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
        self.prefetch_task = asyncio.create_task(self._prefetch_popular_data())
    
    async def _cleanup_expired_entries(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean memory cache
                expired_keys = [
                    key for key, entry in self.memory_cache.items()
                    if self._is_expired(entry)
                ]
                
                for key in expired_keys:
                    await self._delete_from_memory(key)
                
                if expired_keys:
                    self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cache cleanup error: {str(e)}")
    
    async def _prefetch_popular_data(self) -> None:
        """Background task to prefetch popular data."""
        while True:
            try:
                await asyncio.sleep(self.prefetch_interval)
                
                # Implement prefetching logic based on access patterns
                # This would analyze frequently accessed keys and pre-load them
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cache prefetch error: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown cache manager."""
        self.logger.info("Shutting down cache manager...")
        
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.prefetch_task:
            self.prefetch_task.cancel()
        
        # Wait for tasks to complete
        tasks = [task for task in [self.cleanup_task, self.prefetch_task] if task]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Clear memory cache
        self.memory_cache.clear()
        self.access_order.clear()
        
        self.logger.info("Cache manager shutdown complete")