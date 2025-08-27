"""
High-Performance Fingerprint Cache Manager

Advanced caching system for fingerprint data with multi-level caching,
intelligent invalidation, and enterprise-grade performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import json
import hashlib
import logging
import pickle
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum

import redis.asyncio as redis
from redis.asyncio import Redis
import numpy as np

from backend.core.config import settings
from backend.core.exceptions import CacheError, ValidationError
from backend.ai.content_protection.models import ContentFingerprint
from backend.utils.performance import PerformanceMonitor
from backend.utils.compression import CompressionManager
from backend.utils.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels for different data types"""
    L1_MEMORY = "l1_memory"      # In-memory cache for hot data
    L2_REDIS = "l2_redis"        # Redis cache for warm data
    L3_DISK = "l3_disk"          # Disk cache for cold data


class CacheStrategy(Enum):
    """Cache strategies for different access patterns"""
    LRU = "lru"                  # Least Recently Used
    LFU = "lfu"                  # Least Frequently Used
    TTL = "ttl"                  # Time To Live
    ADAPTIVE = "adaptive"        # Adaptive based on access patterns


@dataclass
class CacheConfiguration:
    """Configuration for cache behavior"""
    # Memory cache settings
    memory_cache_size: int = 1000           # Max items in L1 cache
    memory_ttl: int = 300                   # 5 minutes
    
    # Redis cache settings
    redis_ttl: int = 3600                   # 1 hour
    redis_max_size: int = 100000            # Max items in Redis
    
    # Disk cache settings
    disk_cache_enabled: bool = False
    disk_ttl: int = 86400                   # 24 hours
    disk_cache_path: str = "/tmp/fingerprint_cache"
    
    # Performance settings
    compression_enabled: bool = True
    encryption_enabled: bool = True
    batch_operations: bool = True
    prefetch_enabled: bool = True
    
    # Cache strategies
    l1_strategy: CacheStrategy = CacheStrategy.LRU
    l2_strategy: CacheStrategy = CacheStrategy.TTL
    
    # Invalidation settings
    auto_invalidation: bool = True
    dependency_tracking: bool = True


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    
    total_gets: int = 0
    total_sets: int = 0
    total_deletes: int = 0
    
    average_get_time: float = 0.0
    average_set_time: float = 0.0
    
    compression_ratio: float = 0.0
    cache_size_bytes: int = 0
    
    def hit_rate(self) -> float:
        """Calculate overall hit rate"""
        total_hits = self.l1_hits + self.l2_hits + self.l3_hits
        total_requests = total_hits + self.l1_misses + self.l2_misses + self.l3_misses
        return total_hits / total_requests if total_requests > 0 else 0.0
    
    def l1_hit_rate(self) -> float:
        """Calculate L1 cache hit rate"""
        total_l1 = self.l1_hits + self.l1_misses
        return self.l1_hits / total_l1 if total_l1 > 0 else 0.0


class MemoryCache:
    """High-performance in-memory cache with LRU/LFU support"""
    
    def __init__(self, max_size: int, strategy: CacheStrategy, ttl: int = 300):
        self.max_size = max_size
        self.strategy = strategy
        self.ttl = ttl
        
        # Storage
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._access_order: List[str] = []
        
        # Metrics
        self.hits = 0
        self.misses = 0
        
        self.logger = logging.getLogger(f"{__name__}.MemoryCache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from memory cache"""
        try:
            # Check if key exists and not expired
            if key not in self._cache:
                self.misses += 1
                return None
            
            # Check TTL
            if time.time() - self._timestamps[key] > self.ttl:
                self._remove_key(key)
                self.misses += 1
                return None
            
            # Update access patterns
            self._update_access(key)
            self.hits += 1
            
            return self._cache[key]
            
        except Exception as e:
            self.logger.error(f"Memory cache get failed for key {key}: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """Set item in memory cache"""
        try:
            # Check if we need to evict
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_item()
            
            # Store item
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._access_counts[key] = 1
            
            # Update access order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Memory cache set failed for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from memory cache"""
        try:
            if key in self._cache:
                self._remove_key(key)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Memory cache delete failed for key {key}: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all items from memory cache"""
        self._cache.clear()
        self._timestamps.clear()
        self._access_counts.clear()
        self._access_order.clear()
    
    def _update_access(self, key: str) -> None:
        """Update access patterns for cache strategy"""
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
        
        if self.strategy == CacheStrategy.LRU:
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
    
    def _evict_item(self) -> None:
        """Evict item based on cache strategy"""
        if not self._cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            key_to_remove = self._access_order[0]
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            key_to_remove = min(self._access_counts.keys(), key=lambda k: self._access_counts[k])
        else:
            # Default to LRU
            key_to_remove = self._access_order[0]
        
        self._remove_key(key_to_remove)
    
    def _remove_key(self, key: str) -> None:
        """Remove key from all data structures"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._access_counts.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)
    
    def hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class RedisCache:
    """High-performance Redis cache with advanced features"""
    
    def __init__(self, redis_client: Redis, config: CacheConfiguration):
        self.redis = redis_client
        self.config = config
        self.compression_manager = CompressionManager()
        self.encryption_manager = EncryptionManager()
        self.logger = logging.getLogger(f"{__name__}.RedisCache")
        
        # Key prefixes
        self.fingerprint_prefix = "fp:"
        self.match_prefix = "match:"
        self.metadata_prefix = "meta:"
        self.index_prefix = "idx:"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from Redis cache"""
        try:
            # Get data from Redis
            data = await self.redis.get(self._make_key(key))
            
            if data is None:
                return None
            
            # Decrypt if enabled
            if self.config.encryption_enabled:
                data = await self.encryption_manager.decrypt_data(data)
            
            # Decompress if enabled
            if self.config.compression_enabled:
                data = await self.compression_manager.decompress(data)
            
            # Deserialize
            return pickle.loads(data)
            
        except Exception as e:
            self.logger.error(f"Redis cache get failed for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set item in Redis cache"""
        try:
            # Serialize data
            data = pickle.dumps(value)
            
            # Compress if enabled
            if self.config.compression_enabled:
                data = await self.compression_manager.compress(data)
            
            # Encrypt if enabled
            if self.config.encryption_enabled:
                data = await self.encryption_manager.encrypt_data(data)
            
            # Set TTL
            ttl = ttl or self.config.redis_ttl
            
            # Store in Redis
            redis_key = self._make_key(key)
            await self.redis.setex(redis_key, ttl, data)
            
            # Store tags for invalidation
            if tags and self.config.dependency_tracking:
                await self._store_tags(key, tags)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Redis cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete item from Redis cache"""
        try:
            redis_key = self._make_key(key)
            result = await self.redis.delete(redis_key)
            
            # Remove tags
            if self.config.dependency_tracking:
                await self._remove_tags(key)
            
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Redis cache delete failed for key {key}: {e}")
            return False
    
    async def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple items from Redis cache"""
        try:
            redis_keys = [self._make_key(key) for key in keys]
            data_list = await self.redis.mget(redis_keys)
            
            results = []
            for data in data_list:
                if data is None:
                    results.append(None)
                    continue
                
                try:
                    # Decrypt and decompress
                    if self.config.encryption_enabled:
                        data = await self.encryption_manager.decrypt_data(data)
                    
                    if self.config.compression_enabled:
                        data = await self.compression_manager.decompress(data)
                    
                    # Deserialize
                    results.append(pickle.loads(data))
                    
                except Exception as e:
                    self.logger.warning(f"Failed to deserialize cached data: {e}")
                    results.append(None)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Redis cache mget failed: {e}")
            return [None] * len(keys)
    
    async def mset(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple items in Redis cache"""
        try:
            if not items:
                return True
            
            # Prepare data
            redis_items = {}
            ttl = ttl or self.config.redis_ttl
            
            for key, value in items.items():
                # Serialize
                data = pickle.dumps(value)
                
                # Compress and encrypt
                if self.config.compression_enabled:
                    data = await self.compression_manager.compress(data)
                
                if self.config.encryption_enabled:
                    data = await self.encryption_manager.encrypt_data(data)
                
                redis_items[self._make_key(key)] = data
            
            # Use pipeline for better performance
            async with self.redis.pipeline() as pipe:
                await pipe.mset(redis_items)
                
                # Set TTL for each key
                for redis_key in redis_items.keys():
                    await pipe.expire(redis_key, ttl)
                
                await pipe.execute()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Redis cache mset failed: {e}")
            return False
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        try:
            if not self.config.dependency_tracking:
                return 0
            
            keys_to_delete = set()
            
            for tag in tags:
                tag_key = f"tag:{tag}"
                tagged_keys = await self.redis.smembers(tag_key)
                
                for key in tagged_keys:
                    if isinstance(key, bytes):
                        key = key.decode()
                    keys_to_delete.add(key)
            
            if keys_to_delete:
                deleted_count = await self.redis.delete(*keys_to_delete)
                
                # Clean up tag sets
                for tag in tags:
                    await self.redis.delete(f"tag:{tag}")
                
                return deleted_count
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Cache invalidation by tags failed: {e}")
            return 0
    
    async def _store_tags(self, key: str, tags: List[str]) -> None:
        """Store tags for a cache key"""
        try:
            redis_key = self._make_key(key)
            
            async with self.redis.pipeline() as pipe:
                for tag in tags:
                    tag_key = f"tag:{tag}"
                    await pipe.sadd(tag_key, redis_key)
                    await pipe.expire(tag_key, self.config.redis_ttl)
                
                await pipe.execute()
                
        except Exception as e:
            self.logger.error(f"Failed to store tags for key {key}: {e}")
    
    async def _remove_tags(self, key: str) -> None:
        """Remove tags for a cache key"""
        try:
            redis_key = self._make_key(key)
            
            # Find all tag sets containing this key
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match="tag:*", count=100)
                
                for tag_key in keys:
                    await self.redis.srem(tag_key, redis_key)
                
                if cursor == 0:
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to remove tags for key {key}: {e}")
    
    def _make_key(self, key: str) -> str:
        """Create Redis key with prefix"""
        return f"{self.fingerprint_prefix}{key}"
    
    async def size(self) -> int:
        """Get approximate cache size"""
        try:
            info = await self.redis.info('memory')
            return info.get('used_memory', 0)
        except Exception:
            return 0


class FingerprintCacheManager:
    """
    Comprehensive fingerprint cache manager with multi-level caching,
    intelligent invalidation, and enterprise-grade performance optimization.
    """
    
    def __init__(self, redis_client: Redis, config: Optional[CacheConfiguration] = None):
        self.config = config or CacheConfiguration()
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize cache levels
        self.l1_cache = MemoryCache(
            self.config.memory_cache_size,
            self.config.l1_strategy,
            self.config.memory_ttl
        )
        
        self.l2_cache = RedisCache(redis_client, self.config)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.metrics = CacheMetrics()
        
        # Cache warming
        self._warming_tasks: Set[str] = set()
    
    async def get_fingerprint(
        self,
        fingerprint_id: str,
        include_vectors: bool = False
    ) -> Optional[ContentFingerprint]:
        """
        Get fingerprint from cache with multi-level lookup
        
        Args:
            fingerprint_id: Fingerprint identifier
            include_vectors: Whether to include vector data
            
        Returns:
            ContentFingerprint object or None
        """
        start_time = time.time()
        cache_key = self._make_cache_key("fingerprint", fingerprint_id, include_vectors)
        
        try:
            self.metrics.total_gets += 1
            
            # L1 (Memory) cache lookup
            result = self.l1_cache.get(cache_key)
            if result is not None:
                self.metrics.l1_hits += 1
                self._update_average_time("get", start_time)
                return result
            
            self.metrics.l1_misses += 1
            
            # L2 (Redis) cache lookup
            result = await self.l2_cache.get(cache_key)
            if result is not None:
                self.metrics.l2_hits += 1
                
                # Promote to L1 cache
                self.l1_cache.set(cache_key, result)
                
                self._update_average_time("get", start_time)
                return result
            
            self.metrics.l2_misses += 1
            self._update_average_time("get", start_time)
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get failed for fingerprint {fingerprint_id}: {e}")
            self._update_average_time("get", start_time)
            return None
    
    async def set_fingerprint(
        self,
        fingerprint: ContentFingerprint,
        include_vectors: bool = False,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Store fingerprint in cache with multi-level storage
        
        Args:
            fingerprint: ContentFingerprint object
            include_vectors: Whether vectors are included
            ttl: Time to live (seconds)
            tags: Cache tags for invalidation
            
        Returns:
            True if stored successfully
        """
        start_time = time.time()
        
        try:
            self.metrics.total_sets += 1
            
            fingerprint_id = fingerprint.fingerprint_id
            cache_key = self._make_cache_key("fingerprint", fingerprint_id, include_vectors)
            
            # Generate cache tags
            if tags is None:
                tags = self._generate_fingerprint_tags(fingerprint)
            
            # Store in L1 cache
            l1_success = self.l1_cache.set(cache_key, fingerprint)
            
            # Store in L2 cache
            l2_success = await self.l2_cache.set(cache_key, fingerprint, ttl, tags)
            
            self._update_average_time("set", start_time)
            
            return l1_success and l2_success
            
        except Exception as e:
            self.logger.error(f"Cache set failed for fingerprint {fingerprint.fingerprint_id}: {e}")
            self._update_average_time("set", start_time)
            return False
    
    async def get_match_results(
        self,
        query_hash: str,
        content_type: Optional[str] = None
    ) -> Optional[List[Any]]:
        """Get cached match results"""
        cache_key = self._make_cache_key("match", query_hash, content_type)
        
        # Try L1 first
        result = self.l1_cache.get(cache_key)
        if result is not None:
            self.metrics.l1_hits += 1
            return result
        
        # Try L2
        result = await self.l2_cache.get(cache_key)
        if result is not None:
            self.metrics.l2_hits += 1
            # Promote to L1
            self.l1_cache.set(cache_key, result)
        else:
            self.metrics.l2_misses += 1
        
        return result
    
    async def set_match_results(
        self,
        query_hash: str,
        match_results: List[Any],
        content_type: Optional[str] = None,
        ttl: int = 1800  # 30 minutes default
    ) -> bool:
        """Store match results in cache"""
        cache_key = self._make_cache_key("match", query_hash, content_type)
        tags = ["matches", f"content_type:{content_type}"] if content_type else ["matches"]
        
        # Store in both levels
        self.l1_cache.set(cache_key, match_results)
        return await self.l2_cache.set(cache_key, match_results, ttl, tags)
    
    async def invalidate_fingerprint(self, fingerprint_id: str) -> bool:
        """Invalidate all cache entries for a fingerprint"""
        try:
            # Remove from L1 cache
            l1_deleted = False
            for include_vectors in [True, False]:
                cache_key = self._make_cache_key("fingerprint", fingerprint_id, include_vectors)
                if self.l1_cache.delete(cache_key):
                    l1_deleted = True
            
            # Invalidate by tags in L2 cache
            tags = [f"fingerprint_id:{fingerprint_id}"]
            l2_deleted = await self.l2_cache.invalidate_by_tags(tags)
            
            self.logger.debug(f"Invalidated fingerprint {fingerprint_id} from cache")
            return l1_deleted or l2_deleted > 0
            
        except Exception as e:
            self.logger.error(f"Cache invalidation failed for fingerprint {fingerprint_id}: {e}")
            return False
    
    async def invalidate_by_content_type(self, content_type: str) -> int:
        """Invalidate all cache entries for a content type"""
        try:
            # Clear L1 cache (no tag support, so clear all)
            self.l1_cache.clear()
            
            # Invalidate by tags in L2 cache
            tags = [f"content_type:{content_type}"]
            deleted_count = await self.l2_cache.invalidate_by_tags(tags)
            
            self.logger.info(f"Invalidated {deleted_count} entries for content_type {content_type}")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Content type invalidation failed: {e}")
            return 0
    
    async def invalidate_by_user(self, user_id: str) -> int:
        """Invalidate all cache entries for a user"""
        try:
            # Clear L1 cache
            self.l1_cache.clear()
            
            # Invalidate by tags in L2 cache
            tags = [f"user_id:{user_id}"]
            deleted_count = await self.l2_cache.invalidate_by_tags(tags)
            
            self.logger.info(f"Invalidated {deleted_count} entries for user {user_id}")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"User invalidation failed: {e}")
            return 0
    
    async def warm_cache(
        self,
        fingerprint_ids: List[str],
        batch_size: int = 50
    ) -> int:
        """Warm cache with specified fingerprints"""
        try:
            warmed_count = 0
            
            # Process in batches
            for i in range(0, len(fingerprint_ids), batch_size):
                batch = fingerprint_ids[i:i + batch_size]
                
                # Warm batch in parallel
                tasks = []
                for fingerprint_id in batch:
                    if fingerprint_id not in self._warming_tasks:
                        self._warming_tasks.add(fingerprint_id)
                        task = self._warm_fingerprint(fingerprint_id)
                        tasks.append(task)
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    warmed_count += sum(1 for r in results if r is True)
                
                # Remove from warming tasks
                for fingerprint_id in batch:
                    self._warming_tasks.discard(fingerprint_id)
            
            self.logger.info(f"Warmed cache for {warmed_count} fingerprints")
            return warmed_count
            
        except Exception as e:
            self.logger.error(f"Cache warming failed: {e}")
            return 0
    
    async def _warm_fingerprint(self, fingerprint_id: str) -> bool:
        """Warm cache for a single fingerprint"""
        try:
            # This would typically fetch from database and store in cache
            # For now, we'll simulate the warming process
            
            # Check if already in cache
            cached = await self.get_fingerprint(fingerprint_id)
            if cached is not None:
                return True
            
            # Would fetch from database here
            # fingerprint = await self.database.get_fingerprint(fingerprint_id)
            # if fingerprint:
            #     await self.set_fingerprint(fingerprint)
            #     return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Fingerprint warming failed for {fingerprint_id}: {e}")
            return False
    
    async def clear_all_caches(self) -> bool:
        """Clear all cache levels"""
        try:
            # Clear L1 cache
            self.l1_cache.clear()
            
            # Clear L2 cache (Redis)
            await self.redis_client.flushdb()
            
            self.logger.info("Cleared all cache levels")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache clearing failed: {e}")
            return False
    
    def get_cache_metrics(self) -> CacheMetrics:
        """Get comprehensive cache metrics"""
        # Update L1 metrics
        self.metrics.l1_hits = self.l1_cache.hits
        self.metrics.l1_misses = self.l1_cache.misses
        
        return self.metrics
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get detailed cache statistics"""
        try:
            metrics = self.get_cache_metrics()
            
            l1_size = self.l1_cache.size()
            l2_size = await self.l2_cache.size()
            
            return {
                "hit_rates": {
                    "overall": metrics.hit_rate(),
                    "l1": metrics.l1_hit_rate(),
                    "l2": (metrics.l2_hits / (metrics.l2_hits + metrics.l2_misses)) if (metrics.l2_hits + metrics.l2_misses) > 0 else 0.0
                },
                "cache_sizes": {
                    "l1_items": l1_size,
                    "l1_max": self.config.memory_cache_size,
                    "l2_bytes": l2_size,
                    "l2_max": self.config.redis_max_size
                },
                "performance": {
                    "average_get_time": metrics.average_get_time,
                    "average_set_time": metrics.average_set_time,
                    "total_operations": metrics.total_gets + metrics.total_sets + metrics.total_deletes
                },
                "operations": {
                    "gets": metrics.total_gets,
                    "sets": metrics.total_sets,
                    "deletes": metrics.total_deletes
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cache statistics: {e}")
            return {"error": str(e)}
    
    def _make_cache_key(self, prefix: str, key: str, suffix: Any = None) -> str:
        """Generate cache key with consistent format"""
        parts = [prefix, key]
        if suffix is not None:
            parts.append(str(suffix))
        
        cache_key = ":".join(parts)
        
        # Hash if too long
        if len(cache_key) > 250:
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        return cache_key
    
    def _generate_fingerprint_tags(self, fingerprint: ContentFingerprint) -> List[str]:
        """Generate cache tags for a fingerprint"""
        tags = [
            f"fingerprint_id:{fingerprint.fingerprint_id}",
            f"content_id:{fingerprint.content_id}",
            f"content_type:{fingerprint.content_type}",
            f"fingerprint_type:{fingerprint.fingerprint_type}"
        ]
        
        # Add user tag from metadata
        if fingerprint.metadata and 'user_id' in fingerprint.metadata:
            tags.append(f"user_id:{fingerprint.metadata['user_id']}")
        
        return tags
    
    def _update_average_time(self, operation: str, start_time: float) -> None:
        """Update average operation time"""
        elapsed = time.time() - start_time
        
        if operation == "get":
            # Simple moving average
            if self.metrics.total_gets == 1:
                self.metrics.average_get_time = elapsed
            else:
                self.metrics.average_get_time = (
                    (self.metrics.average_get_time * (self.metrics.total_gets - 1) + elapsed) 
                    / self.metrics.total_gets
                )
        elif operation == "set":
            if self.metrics.total_sets == 1:
                self.metrics.average_set_time = elapsed
            else:
                self.metrics.average_set_time = (
                    (self.metrics.average_set_time * (self.metrics.total_sets - 1) + elapsed) 
                    / self.metrics.total_sets
                )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache components"""
        try:
            health = {
                "status": "healthy",
                "components": {},
                "metrics": {}
            }
            
            # Test L1 cache
            test_key = "health_check_test"
            test_value = {"test": True, "timestamp": time.time()}
            
            if self.l1_cache.set(test_key, test_value):
                retrieved = self.l1_cache.get(test_key)
                if retrieved == test_value:
                    health["components"]["l1_cache"] = "healthy"
                else:
                    health["components"]["l1_cache"] = "unhealthy"
                    health["status"] = "degraded"
            else:
                health["components"]["l1_cache"] = "unhealthy"
                health["status"] = "degraded"
            
            # Test L2 cache (Redis)
            try:
                await self.redis_client.ping()
                redis_set = await self.l2_cache.set(test_key, test_value, 60)
                redis_get = await self.l2_cache.get(test_key)
                
                if redis_set and redis_get == test_value:
                    health["components"]["l2_cache"] = "healthy"
                else:
                    health["components"]["l2_cache"] = "unhealthy"
                    health["status"] = "degraded"
                    
            except Exception as e:
                health["components"]["l2_cache"] = f"unhealthy: {e}"
                health["status"] = "degraded"
            
            # Add metrics
            health["metrics"] = await self.get_cache_statistics()
            
            # Cleanup test data
            self.l1_cache.delete(test_key)
            await self.l2_cache.delete(test_key)
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
