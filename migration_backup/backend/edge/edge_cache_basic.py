"""Edge Cache System
==================

Advanced caching system for edge computing infrastructure,
providing intelligent content caching, cache invalidation, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
import pickle
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, asdict, field
import json
import uuid
from collections import defaultdict, OrderedDict
import threading
import weakref

logger = logging.getLogger(__name__)


class CacheStrategy(str, Enum):
    """Cache replacement strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive strategy
    PREDICTIVE = "predictive"  # Predictive caching


class CacheType(str, Enum):
    """Types of cache storage."""
    MEMORY = "memory"
    DISK = "disk"
    HYBRID = "hybrid"
    DISTRIBUTED = "distributed"


class CacheLevel(str, Enum):
    """Cache hierarchy levels."""
    L1 = "l1"  # Local memory cache
    L2 = "l2"  # Local disk cache
    L3 = "l3"  # Regional cache
    CDN = "cdn"  # Content Delivery Network


class InvalidationStrategy(str, Enum):
    """Cache invalidation strategies."""
    TTL_BASED = "ttl_based"
    TAG_BASED = "tag_based"
    DEPENDENCY_BASED = "dependency_based"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"


@dataclass
class CacheItem:
    """Cache item with metadata."""
    key: str
    value: Any
    size: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compressed: bool = False
    
    def is_expired(self) -> bool:
        """Check if cache item is expired."""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).seconds > self.ttl
    
    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    capacity: int = 0
    hit_ratio: float = 0.0
    memory_usage: int = 0
    disk_usage: int = 0


@dataclass
class CachePrefetchRequest:
    """Cache prefetch request."""
    keys: List[str]
    priority: int = 1
    ttl: Optional[int] = None
    requester: str = "system"


class EdgeCache:
    """Advanced edge cache system with intelligent caching strategies."""
    
    def __init__(self,
                 max_memory_size: int = 1024 * 1024 * 1024,  # 1GB
                 max_disk_size: int = 10 * 1024 * 1024 * 1024,  # 10GB
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 default_ttl: int = 3600,
                 compression_threshold: int = 1024):
        
        self.max_memory_size = max_memory_size
        self.max_disk_size = max_disk_size
        self.strategy = strategy
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        
        # Cache storage
        self.memory_cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.disk_cache: Dict[str, str] = {}  # key -> file_path mapping
        
        # Cache statistics
        self.stats = CacheStats(capacity=max_memory_size)
        
        # Access patterns for adaptive caching
        self.access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.popularity_scores: Dict[str, float] = defaultdict(float)
        
        # Invalidation tracking
        self.tag_to_keys: Dict[str, set] = defaultdict(set)
        self.dependency_graph: Dict[str, set] = defaultdict(set)
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.prefetch_task: Optional[asyncio.Task] = None
        self.analytics_task: Optional[asyncio.Task] = None
        
        # Prefetch queue
        self.prefetch_queue: asyncio.Queue = asyncio.Queue()
        
        # Thread-safe operations
        self._cache_lock = threading.RLock()
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.info(f"EdgeCache initialized with strategy: {strategy}")
    
    async def start(self):
        """Start the cache system and background tasks."""
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.prefetch_task = asyncio.create_task(self._prefetch_loop())
        self.analytics_task = asyncio.create_task(self._analytics_loop())
        
        logger.info("Edge cache system started")
    
    async def stop(self):
        """Stop the cache system and background tasks."""
        # Cancel background tasks
        tasks = [self.cleanup_task, self.prefetch_task, self.analytics_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Edge cache system stopped")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._cache_lock:
            # Check memory cache first
            if key in self.memory_cache:
                item = self.memory_cache[key]
                
                # Check if expired
                if item.is_expired():
                    await self._evict_item(key)
                    self.stats.misses += 1
                    return default
                
                # Update access stats and move to end (LRU)
                item.update_access()
                self.memory_cache.move_to_end(key)
                self.stats.hits += 1
                
                # Update access patterns
                await self._update_access_pattern(key)
                
                # Decompress if needed
                value = item.value
                if item.compressed and isinstance(value, bytes):
                    value = pickle.loads(gzip.decompress(value))
                
                # Trigger cache hit event
                await self._trigger_event("cache_hit", {"key": key, "value": value})
                
                return value
            
            # Check disk cache
            if key in self.disk_cache:
                try:
                    value = await self._load_from_disk(key)
                    if value is not None:
                        # Promote to memory cache
                        await self._promote_to_memory(key, value)
                        self.stats.hits += 1
                        await self._update_access_pattern(key)
                        return value
                except Exception as e:
                    logger.error(f"Failed to load from disk cache: {e}")
            
            # Cache miss
            self.stats.misses += 1
            await self._trigger_event("cache_miss", {"key": key})
            return default
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  tags: Optional[List[str]] = None,
                  dependencies: Optional[List[str]] = None,
                  force_disk: bool = False) -> bool:
        """Set value in cache."""
        
        try:
            with self._cache_lock:
                # Serialize and optionally compress value
                serialized_value, size, compressed = await self._serialize_value(value)
                
                # Create cache item
                item = CacheItem(
                    key=key,
                    value=serialized_value,
                    size=size,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    ttl=ttl or self.default_ttl,
                    tags=tags or [],
                    dependencies=dependencies or [],
                    compressed=compressed
                )
                
                # Update tag mappings
                for tag in item.tags:
                    self.tag_to_keys[tag].add(key)
                
                # Update dependency graph
                for dep in item.dependencies:
                    self.dependency_graph[dep].add(key)
                
                # Determine cache level based on size and strategy
                if force_disk or size > self.max_memory_size // 10:  # Large items go to disk
                    success = await self._store_to_disk(key, item)
                else:
                    success = await self._store_to_memory(key, item)
                
                if success:
                    await self._trigger_event("cache_set", {"key": key, "size": size})
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to set cache item {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete item from cache."""
        with self._cache_lock:
            deleted = False
            
            # Remove from memory cache
            if key in self.memory_cache:
                await self._evict_item(key)
                deleted = True
            
            # Remove from disk cache
            if key in self.disk_cache:
                await self._remove_from_disk(key)
                deleted = True
            
            if deleted:
                await self._trigger_event("cache_delete", {"key": key})
            
            return deleted
    
    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache items with a specific tag."""
        invalidated_count = 0
        
        if tag in self.tag_to_keys:
            keys_to_invalidate = list(self.tag_to_keys[tag])
            
            for key in keys_to_invalidate:
                if await self.delete(key):
                    invalidated_count += 1
            
            # Clean up tag mapping
            del self.tag_to_keys[tag]
        
        logger.info(f"Invalidated {invalidated_count} items with tag: {tag}")
        return invalidated_count
    
    async def invalidate_by_dependency(self, dependency: str) -> int:
        """Invalidate all cache items that depend on a specific dependency."""
        invalidated_count = 0
        
        if dependency in self.dependency_graph:
            keys_to_invalidate = list(self.dependency_graph[dependency])
            
            for key in keys_to_invalidate:
                if await self.delete(key):
                    invalidated_count += 1
            
            # Clean up dependency graph
            del self.dependency_graph[dependency]
        
        logger.info(f"Invalidated {invalidated_count} items dependent on: {dependency}")
        return invalidated_count
    
    async def clear(self) -> bool:
        """Clear all cache items."""
        try:
            with self._cache_lock:
                # Clear memory cache
                self.memory_cache.clear()
                
                # Clear disk cache
                for key in list(self.disk_cache.keys()):
                    await self._remove_from_disk(key)
                
                # Reset statistics
                self.stats = CacheStats(capacity=self.max_memory_size)
                
                # Clear tracking structures
                self.access_patterns.clear()
                self.popularity_scores.clear()
                self.tag_to_keys.clear()
                self.dependency_graph.clear()
                
                await self._trigger_event("cache_clear", {})
                
                logger.info("Cache cleared")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    async def prefetch(self, keys: List[str], priority: int = 1) -> bool:
        """Request prefetching of specific keys."""
        try:
            prefetch_request = CachePrefetchRequest(
                keys=keys,
                priority=priority,
                requester="manual"
            )
            
            await self.prefetch_queue.put(prefetch_request)
            logger.info(f"Queued prefetch request for {len(keys)} keys")
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue prefetch request: {e}")
            return False
    
    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._cache_lock:
            # Update hit ratio
            total_requests = self.stats.hits + self.stats.misses
            if total_requests > 0:
                self.stats.hit_ratio = self.stats.hits / total_requests
            
            # Update size information
            self.stats.size = len(self.memory_cache)
            self.stats.memory_usage = sum(item.size for item in self.memory_cache.values())
            self.stats.disk_usage = len(self.disk_cache)  # Simplified
            
            return self.stats
    
    async def get_popular_keys(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get most popular cache keys."""
        sorted_keys = sorted(
            self.popularity_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_keys[:limit]
    
    async def optimize(self) -> Dict[str, Any]:
        """Optimize cache configuration based on usage patterns."""
        optimization_results = {
            "actions_taken": [],
            "metrics_improved": {},
            "recommendations": []
        }
        
        try:
            # Analyze access patterns
            hot_keys = await self.get_popular_keys(100)
            
            # Promote frequently accessed items to memory
            promoted = 0
            for key, score in hot_keys:
                if key in self.disk_cache and key not in self.memory_cache:
                    value = await self._load_from_disk(key)
                    if value and await self._promote_to_memory(key, value):
                        promoted += 1
            
            if promoted > 0:
                optimization_results["actions_taken"].append(f"Promoted {promoted} items to memory")
            
            # Adjust cache sizes based on hit ratios
            current_stats = await self.get_stats()
            if current_stats.hit_ratio < 0.7:  # Low hit ratio
                optimization_results["recommendations"].append("Consider increasing cache size")
            
            if current_stats.memory_usage > self.max_memory_size * 0.9:  # High memory usage
                optimization_results["recommendations"].append("Consider implementing more aggressive eviction")
            
            logger.info(f"Cache optimization completed: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return optimization_results
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler for cache events."""
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove event handler for cache events."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    # Private methods
    
    async def _serialize_value(self, value: Any) -> Tuple[bytes, int, bool]:
        """Serialize and optionally compress value."""
        # Serialize the value
        serialized = pickle.dumps(value)
        original_size = len(serialized)
        
        # Compress if above threshold
        compressed = False
        if original_size > self.compression_threshold:
            compressed_data = gzip.compress(serialized)
            if len(compressed_data) < original_size * 0.8:  # Only use if significant compression
                serialized = compressed_data
                compressed = True
        
        return serialized, len(serialized), compressed
    
    async def _store_to_memory(self, key: str, item: CacheItem) -> bool:
        """Store item in memory cache."""
        try:
            # Check if we need to evict items
            while (self.stats.memory_usage + item.size > self.max_memory_size and 
                   len(self.memory_cache) > 0):
                await self._evict_least_valuable()
            
            # Store item
            self.memory_cache[key] = item
            self.stats.memory_usage += item.size
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store item to memory cache: {e}")
            return False
    
    async def _store_to_disk(self, key: str, item: CacheItem) -> bool:
        """Store item in disk cache."""
        try:
            # For now, we'll simulate disk storage
            # In a real implementation, this would write to actual disk
            self.disk_cache[key] = f"disk_path_{key}"
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store item to disk cache: {e}")
            return False
    
    async def _load_from_disk(self, key: str) -> Optional[Any]:
        """Load item from disk cache."""
        try:
            if key not in self.disk_cache:
                return None
            
            # Simulate disk loading
            # In a real implementation, this would read from actual disk
            return f"disk_value_{key}"
            
        except Exception as e:
            logger.error(f"Failed to load item from disk cache: {e}")
            return None
    
    async def _remove_from_disk(self, key: str) -> bool:
        """Remove item from disk cache."""
        try:
            if key in self.disk_cache:
                # Simulate disk removal
                # In a real implementation, this would delete the actual file
                del self.disk_cache[key]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove item from disk cache: {e}")
            return False
    
    async def _promote_to_memory(self, key: str, value: Any) -> bool:
        """Promote disk-cached item to memory cache."""
        try:
            serialized_value, size, compressed = await self._serialize_value(value)
            
            item = CacheItem(
                key=key,
                value=serialized_value,
                size=size,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                compressed=compressed
            )
            
            return await self._store_to_memory(key, item)
            
        except Exception as e:
            logger.error(f"Failed to promote item to memory: {e}")
            return False
    
    async def _evict_item(self, key: str):
        """Evict specific item from memory cache."""
        if key in self.memory_cache:
            item = self.memory_cache[key]
            del self.memory_cache[key]
            self.stats.memory_usage -= item.size
            self.stats.evictions += 1
    
    async def _evict_least_valuable(self):
        """Evict least valuable item based on current strategy."""
        if not self.memory_cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used (first item in OrderedDict)
            key = next(iter(self.memory_cache))
            await self._evict_item(key)
            
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            min_key = min(self.memory_cache.keys(), 
                         key=lambda k: self.memory_cache[k].access_count)
            await self._evict_item(min_key)
            
        elif self.strategy == CacheStrategy.FIFO:
            # Remove oldest item
            min_key = min(self.memory_cache.keys(), 
                         key=lambda k: self.memory_cache[k].created_at)
            await self._evict_item(min_key)
            
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired items first, then oldest
            expired_keys = [k for k, v in self.memory_cache.items() if v.is_expired()]
            if expired_keys:
                await self._evict_item(expired_keys[0])
            else:
                min_key = min(self.memory_cache.keys(), 
                             key=lambda k: self.memory_cache[k].created_at)
                await self._evict_item(min_key)
                
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Use popularity score for eviction
            min_key = min(self.memory_cache.keys(), 
                         key=lambda k: self.popularity_scores.get(k, 0))
            await self._evict_item(min_key)
            
        else:  # Default to LRU
            key = next(iter(self.memory_cache))
            await self._evict_item(key)
    
    async def _update_access_pattern(self, key: str):
        """Update access pattern for adaptive caching."""
        now = datetime.now()
        self.access_patterns[key].append(now)
        
        # Keep only recent accesses (last hour)
        cutoff_time = now - timedelta(hours=1)
        self.access_patterns[key] = [
            access_time for access_time in self.access_patterns[key]
            if access_time > cutoff_time
        ]
        
        # Update popularity score
        recent_accesses = len(self.access_patterns[key])
        time_decay = 0.9 ** ((now - self.access_patterns[key][-1]).seconds / 3600)  # Decay over time
        self.popularity_scores[key] = recent_accesses * time_decay
    
    async def _cleanup_loop(self):
        """Background cleanup task."""
        while True:
            try:
                await self._cleanup_expired_items()
                await asyncio.sleep(60)  # Run every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _prefetch_loop(self):
        """Background prefetch task."""
        while True:
            try:
                # Wait for prefetch requests
                request = await self.prefetch_queue.get()
                await self._process_prefetch_request(request)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in prefetch loop: {e}")
    
    async def _analytics_loop(self):
        """Background analytics task."""
        while True:
            try:
                await self._analyze_access_patterns()
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_expired_items(self):
        """Clean up expired cache items."""
        expired_keys = []
        
        with self._cache_lock:
            for key, item in self.memory_cache.items():
                if item.is_expired():
                    expired_keys.append(key)
        
        for key in expired_keys:
            await self._evict_item(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
    
    async def _process_prefetch_request(self, request: CachePrefetchRequest):
        """Process a prefetch request."""
        logger.info(f"Processing prefetch request for {len(request.keys)} keys")
        
        # For now, this is a placeholder
        # In a real implementation, this would fetch data from the origin
        for key in request.keys:
            if key not in self.memory_cache and key not in self.disk_cache:
                # Simulate fetching data
                dummy_value = f"prefetched_value_{key}"
                await self.set(key, dummy_value, ttl=request.ttl)
    
    async def _analyze_access_patterns(self):
        """Analyze access patterns for optimization."""
        # Clean up old access patterns
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        keys_to_remove = []
        for key, accesses in self.access_patterns.items():
            # Remove old accesses
            recent_accesses = [a for a in accesses if a > cutoff_time]
            
            if recent_accesses:
                self.access_patterns[key] = recent_accesses
            else:
                keys_to_remove.append(key)
        
        # Clean up empty patterns
        for key in keys_to_remove:
            del self.access_patterns[key]
            if key in self.popularity_scores:
                del self.popularity_scores[key]
    
    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger cache event handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")


def create_edge_cache(
    max_memory_size: int = 1024 * 1024 * 1024,  # 1GB
    max_disk_size: int = 10 * 1024 * 1024 * 1024,  # 10GB
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
    default_ttl: int = 3600
) -> EdgeCache:
    """Create and configure an edge cache instance."""
    return EdgeCache(
        max_memory_size=max_memory_size,
        max_disk_size=max_disk_size,
        strategy=strategy,
        default_ttl=default_ttl
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_cache():
        """Test the edge cache system."""
        cache = create_edge_cache(max_memory_size=1024*1024)  # 1MB for testing
        
        # Start cache
        await cache.start()
        
        # Test basic operations
        await cache.set("key1", "value1", ttl=60)
        await cache.set("key2", {"data": "complex_value"}, tags=["tag1", "tag2"])
        
        # Test retrieval
        value1 = await cache.get("key1")
        value2 = await cache.get("key2")
        
        print(f"Retrieved: {value1}, {value2}")
        
        # Test statistics
        stats = await cache.get_stats()
        print(f"Cache stats: {stats.hits} hits, {stats.misses} misses, hit ratio: {stats.hit_ratio:.2f}")
        
        # Test tag-based invalidation
        invalidated = await cache.invalidate_by_tag("tag1")
        print(f"Invalidated {invalidated} items with tag1")
        
        # Test optimization
        optimization_results = await cache.optimize()
        print(f"Optimization results: {optimization_results}")
        
        # Stop cache
        await cache.stop()
    
    # Run test
    asyncio.run(test_cache())