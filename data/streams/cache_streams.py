"""Cache Streams for IA Influencer Agent Platform
===========================================

Advanced caching system for streaming data with edge computing,
distributed cache management, and intelligent cache strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
import hashlib
import pickle
import gzip
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque, OrderedDict
import statistics

logger = logging.getLogger(__name__)


class CacheStrategy(str, Enum):
    """Cache strategy types"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    LIFO = "lifo"
    TTL = "ttl"
    ADAPTIVE = "adaptive"
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"


class CacheLevel(str, Enum):
    """Cache level hierarchy"""
    L1_MEMORY = "l1_memory"
    L2_SSD = "l2_ssd"
    L3_NETWORK = "l3_network"
    EDGE = "edge"
    CDN = "cdn"


class CacheOperation(str, Enum):
    """Cache operation types"""
    GET = "get"
    PUT = "put"
    DELETE = "delete"
    INVALIDATE = "invalidate"
    PREFETCH = "prefetch"
    EVICT = "evict"


class CacheEventType(str, Enum):
    """Cache event types"""
    HIT = "hit"
    MISS = "miss"
    EVICTION = "eviction"
    EXPIRATION = "expiration"
    INVALIDATION = "invalidation"
    PRELOAD = "preload"


class CompressionType(str, Enum):
    """Data compression types"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"


@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    compressed: bool = False
    tags: set = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        return (datetime.now(timezone.utc) - self.created_at).total_seconds() > self.ttl_seconds
    
    def update_access(self) -> None:
        """Update access statistics"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1


@dataclass
class CacheConfig:
    """Cache configuration"""
    cache_id: str
    strategy: CacheStrategy = CacheStrategy.LRU
    max_size_mb: int = 100
    max_entries: int = 10000
    default_ttl_seconds: int = 3600
    compression: CompressionType = CompressionType.NONE
    enable_persistence: bool = False
    persistence_path: str = "/tmp/cache"
    hit_ratio_threshold: float = 0.8
    enable_metrics: bool = True


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    cache_id: str
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    expirations: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    hit_ratio: float = 0.0
    average_response_time_ms: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EdgeNode:
    """Edge computing node configuration"""
    node_id: str
    location: str
    region: str
    capacity_mb: int = 1000
    latency_ms: float = 0.0
    bandwidth_mbps: float = 100.0
    status: str = "active"
    cache_hit_ratio: float = 0.0
    load_percentage: float = 0.0


@dataclass
class CacheEvent:
    """Cache event data structure"""
    event_id: str
    cache_id: str
    event_type: CacheEventType
    operation: CacheOperation
    key: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CacheStreams:
    """
    Advanced caching system for streaming data with edge computing,
    distributed cache management, and intelligent cache strategies.
    
    Features:
    - Multi-level cache hierarchy (L1, L2, L3, Edge, CDN)
    - Multiple eviction strategies (LRU, LFU, TTL, Adaptive)
    - Data compression and serialization
    - Edge computing and geographical distribution
    - Intelligent prefetching and preloading
    - Cache invalidation and consistency
    - Performance monitoring and optimization
    """
    
    def __init__(
        self,
        default_config -> None: Optional[CacheConfig] = None,
        enable_edge_computing -> None: bool = True,
        enable_distributed_cache -> None: bool = True
    ) -> None:
        # Configuration
        self.default_config = default_config or CacheConfig(cache_id="default")
        self.enable_edge_computing = enable_edge_computing
        self.enable_distributed_cache = enable_distributed_cache
        
        # Cache management
        self.cache_instances: Dict[str, Dict[str, CacheEntry]] = {}
        self.cache_configs: Dict[str, CacheConfig] = {}
        self.cache_metrics: Dict[str, CacheMetrics] = {}
        
        # Multi-level cache
        self.cache_levels: Dict[CacheLevel, Dict[str, Any]] = {
            level: {} for level in CacheLevel
        }
        
        # Edge computing
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.geo_cache_mapping: Dict[str, List[str]] = defaultdict(list)  # region -> cache_ids
        
        # Cache events and monitoring
        self.cache_events: deque = deque(maxlen=10000)
        self.access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.prefetch_predictions: Dict[str, float] = {}
        
        # Cache invalidation
        self.invalidation_groups: Dict[str, set] = defaultdict(set)
        self.cache_dependencies: Dict[str, set] = defaultdict(set)
        
        # Performance tracking
        self.global_metrics = {
            "total_operations": 0,
            "total_hits": 0,
            "total_misses": 0,
            "global_hit_ratio": 0.0,
            "total_size_bytes": 0,
            "evictions": 0,
            "compressions": 0
        }
        
        # Background tasks
        self.cache_maintenance_task: Optional[asyncio.Task] = None
        self.metrics_collector_task: Optional[asyncio.Task] = None
        self.prefetch_engine_task: Optional[asyncio.Task] = None
        self.edge_optimizer_task: Optional[asyncio.Task] = None
        
        # State management
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        logger.info("CacheStreams initialized")
        
    async def initialize(self) -> None:
        """Initialize the cache streams system"""
        try:
            if self._running:
                return
                
            # Create default cache
            await self.create_cache("default", self.default_config)
            
            # Start background tasks
            self.cache_maintenance_task = asyncio.create_task(self._cache_maintenance())
            self.metrics_collector_task = asyncio.create_task(self._metrics_collector())
            self.prefetch_engine_task = asyncio.create_task(self._prefetch_engine())
            
            if self.enable_edge_computing:
                self.edge_optimizer_task = asyncio.create_task(self._edge_optimizer())
                
            self._running = True
            logger.info("CacheStreams initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CacheStreams: {e}")
            raise
            
    async def create_cache(self, cache_id: str, config: CacheConfig) -> bool:
        """
        Create a new cache instance
        
        Args:
            cache_id: Cache identifier
            config: Cache configuration
            
        Returns:
            Success status
        """
        try:
            if cache_id in self.cache_instances:
                logger.warning(f"Cache {cache_id} already exists")
                return False
                
            self.cache_instances[cache_id] = {}
            self.cache_configs[cache_id] = config
            self.cache_metrics[cache_id] = CacheMetrics(cache_id=cache_id)
            
            logger.info(f"Cache created: {cache_id} with strategy {config.strategy.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create cache {cache_id}: {e}")
            return False
            
    async def get(
        self,
        cache_id: str,
        key: str,
        default: Any = None,
        update_access: bool = True
    ) -> Any:
        """
        Get value from cache
        
        Args:
            cache_id: Cache identifier
            key: Cache key
            default: Default value if not found
            update_access: Whether to update access statistics
            
        Returns:
            Cached value or default
        """
        try:
            start_time = time.time()
            
            # Check if cache exists
            if cache_id not in self.cache_instances:
                await self._record_cache_event(cache_id, CacheEventType.MISS, CacheOperation.GET, key)
                return default
                
            cache = self.cache_instances[cache_id]
            metrics = self.cache_metrics[cache_id]
            
            # Check if key exists
            if key not in cache:
                await self._record_cache_event(cache_id, CacheEventType.MISS, CacheOperation.GET, key)
                metrics.cache_misses += 1
                self.global_metrics["total_misses"] += 1
                return default
                
            entry = cache[key]
            
            # Check if expired
            if entry.is_expired():
                await self._evict_entry(cache_id, key, reason="expiration")
                await self._record_cache_event(cache_id, CacheEventType.MISS, CacheOperation.GET, key)
                metrics.cache_misses += 1
                return default
                
            # Update access statistics
            if update_access:
                entry.update_access()
                
            # Decompress if needed
            value = entry.value
            if entry.compressed:
                value = await self._decompress_data(value, self.cache_configs[cache_id].compression)
                
            execution_time = (time.time() - start_time) * 1000
            
            # Update metrics
            metrics.cache_hits += 1
            metrics.total_requests += 1
            self.global_metrics["total_hits"] += 1
            self.global_metrics["total_operations"] += 1
            
            await self._record_cache_event(
                cache_id, CacheEventType.HIT, CacheOperation.GET, key,
                execution_time_ms=execution_time
            )
            
            # Record access pattern
            self.access_patterns[key].append(datetime.now(timezone.utc))
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get from cache {cache_id}: {e}")
            return default
            
    async def put(
        self,
        cache_id: str,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[set] = None,
        compress: bool = False
    ) -> bool:
        """
        Put value into cache
        
        Args:
            cache_id: Cache identifier
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            tags: Cache entry tags
            compress: Whether to compress the value
            
        Returns:
            Success status
        """
        try:
            start_time = time.time()
            
            # Check if cache exists
            if cache_id not in self.cache_instances:
                logger.error(f"Cache {cache_id} not found")
                return False
                
            cache = self.cache_instances[cache_id]
            config = self.cache_configs[cache_id]
            metrics = self.cache_metrics[cache_id]
            
            # Compress if requested
            compressed_value = value
            compressed = False
            if compress and config.compression != CompressionType.NONE:
                compressed_value = await self._compress_data(value, config.compression)
                compressed = True
                self.global_metrics["compressions"] += 1
                
            # Calculate size
            size_bytes = len(pickle.dumps(compressed_value))
            
            # Check capacity and evict if necessary
            await self._ensure_capacity(cache_id, size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=compressed_value,
                ttl_seconds=ttl_seconds or config.default_ttl_seconds,
                size_bytes=size_bytes,
                compressed=compressed,
                tags=tags or set()
            )
            
            # Store entry
            cache[key] = entry
            
            # Update metrics
            metrics.total_size_bytes += size_bytes
            metrics.entry_count += 1
            self.global_metrics["total_size_bytes"] += size_bytes
            self.global_metrics["total_operations"] += 1
            
            execution_time = (time.time() - start_time) * 1000
            
            await self._record_cache_event(
                cache_id, CacheEventType.HIT, CacheOperation.PUT, key,
                execution_time_ms=execution_time
            )
            
            logger.debug(f"Cached entry: {key} in {cache_id} ({size_bytes} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to put into cache {cache_id}: {e}")
            return False
            
    async def delete(self, cache_id: str, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            cache_id: Cache identifier
            key: Cache key
            
        Returns:
            Success status
        """
        try:
            if cache_id not in self.cache_instances:
                return False
                
            cache = self.cache_instances[cache_id]
            
            if key in cache:
                entry = cache[key]
                
                # Update metrics
                metrics = self.cache_metrics[cache_id]
                metrics.total_size_bytes -= entry.size_bytes
                metrics.entry_count -= 1
                self.global_metrics["total_size_bytes"] -= entry.size_bytes
                
                del cache[key]
                
                await self._record_cache_event(cache_id, CacheEventType.INVALIDATION, CacheOperation.DELETE, key)
                
                logger.debug(f"Deleted cache entry: {key} from {cache_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete from cache {cache_id}: {e}")
            return False
            
    async def invalidate_by_tags(self, cache_id: str, tags: set) -> int:
        """
        Invalidate cache entries by tags
        
        Args:
            cache_id: Cache identifier
            tags: Tags to invalidate
            
        Returns:
            Number of entries invalidated
        """
        try:
            if cache_id not in self.cache_instances:
                return 0
                
            cache = self.cache_instances[cache_id]
            invalidated_count = 0
            
            # Find entries with matching tags
            keys_to_delete = []
            for key, entry in cache.items():
                if entry.tags.intersection(tags):
                    keys_to_delete.append(key)
                    
            # Delete matching entries
            for key in keys_to_delete:
                if await self.delete(cache_id, key):
                    invalidated_count += 1
                    
            logger.info(f"Invalidated {invalidated_count} entries by tags: {tags}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate by tags: {e}")
            return 0
            
    async def prefetch(
        self,
        cache_id: str,
        keys: List[str],
        data_loader: Callable[[str], Any]
    ) -> Dict[str, bool]:
        """
        Prefetch data into cache
        
        Args:
            cache_id: Cache identifier
            keys: Keys to prefetch
            data_loader: Function to load data for keys
            
        Returns:
            Dictionary of key -> success status
        """
        try:
            results = {}
            
            for key in keys:
                try:
                    # Check if already cached
                    cached_value = await self.get(cache_id, key, update_access=False)
                    if cached_value is not None:
                        results[key] = True
                        continue
                        
                    # Load data
                    data = await data_loader(key) if asyncio.iscoroutinefunction(data_loader) else data_loader(key)
                    
                    # Cache data
                    success = await self.put(cache_id, key, data, compress=True)
                    results[key] = success
                    
                    if success:
                        await self._record_cache_event(cache_id, CacheEventType.PRELOAD, CacheOperation.PREFETCH, key)
                        
                except Exception as e:
                    logger.error(f"Failed to prefetch key {key}: {e}")
                    results[key] = False
                    
            successful_prefetches = sum(1 for success in results.values() if success)
            logger.info(f"Prefetched {successful_prefetches}/{len(keys)} keys")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to prefetch: {e}")
            return {}
            
    async def create_edge_node(
        self,
        node_id: str,
        location: str,
        region: str,
        capacity_mb: int = 1000,
        latency_ms: float = 0.0
    ) -> bool:
        """
        Create an edge computing node
        
        Args:
            node_id: Node identifier
            location: Geographic location
            region: Region identifier
            capacity_mb: Storage capacity in MB
            latency_ms: Network latency
            
        Returns:
            Success status
        """
        try:
            if not self.enable_edge_computing:
                logger.warning("Edge computing is disabled")
                return False
                
            if node_id in self.edge_nodes:
                logger.warning(f"Edge node {node_id} already exists")
                return False
                
            edge_node = EdgeNode(
                node_id=node_id,
                location=location,
                region=region,
                capacity_mb=capacity_mb,
                latency_ms=latency_ms
            )
            
            self.edge_nodes[node_id] = edge_node
            
            # Create cache for edge node
            edge_config = CacheConfig(
                cache_id=f"edge_{node_id}",
                max_size_mb=capacity_mb,
                strategy=CacheStrategy.LRU,
                enable_persistence=True
            )
            
            await self.create_cache(f"edge_{node_id}", edge_config)
            
            # Add to geo mapping
            self.geo_cache_mapping[region].append(f"edge_{node_id}")
            
            logger.info(f"Edge node created: {node_id} in {location}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create edge node {node_id}: {e}")
            return False
            
    async def get_from_nearest_edge(
        self,
        key: str,
        client_region: str,
        default: Any = None
    ) -> Any:
        """
        Get value from nearest edge node
        
        Args:
            key: Cache key
            client_region: Client region
            default: Default value
            
        Returns:
            Cached value or default
        """
        try:
            # Find caches in client region
            region_caches = self.geo_cache_mapping.get(client_region, [])
            
            if not region_caches:
                # Fallback to default cache
                return await self.get("default", key, default)
                
            # Try each cache in region (ordered by performance)
            for cache_id in region_caches:
                value = await self.get(cache_id, key, default=None, update_access=True)
                if value is not None:
                    return value
                    
            # Fallback to default cache
            return await self.get("default", key, default)
            
        except Exception as e:
            logger.error(f"Failed to get from nearest edge: {e}")
            return default
            
    async def get_cache_statistics(self, cache_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Args:
            cache_id: Specific cache ID or None for all caches
            
        Returns:
            Cache statistics
        """
        try:
            if cache_id:
                # Single cache statistics
                if cache_id not in self.cache_metrics:
                    return {}
                    
                metrics = self.cache_metrics[cache_id]
                config = self.cache_configs[cache_id]
                
                # Calculate hit ratio
                total_requests = metrics.cache_hits + metrics.cache_misses
                hit_ratio = (metrics.cache_hits / total_requests) if total_requests > 0 else 0.0
                
                return {
                    "cache_id": cache_id,
                    "strategy": config.strategy.value,
                    "total_requests": total_requests,
                    "cache_hits": metrics.cache_hits,
                    "cache_misses": metrics.cache_misses,
                    "hit_ratio": hit_ratio,
                    "entry_count": metrics.entry_count,
                    "total_size_bytes": metrics.total_size_bytes,
                    "evictions": metrics.evictions,
                    "average_response_time_ms": metrics.average_response_time_ms,
                    "last_updated": metrics.last_updated.isoformat()
                }
            else:
                # Global statistics
                total_requests = self.global_metrics["total_hits"] + self.global_metrics["total_misses"]
                global_hit_ratio = (self.global_metrics["total_hits"] / total_requests) if total_requests > 0 else 0.0
                
                cache_summaries = {}
                for cid in self.cache_instances.keys():
                    cache_stats = await self.get_cache_statistics(cid)
                    cache_summaries[cid] = cache_stats
                    
                return {
                    "global_metrics": {
                        "total_operations": self.global_metrics["total_operations"],
                        "total_hits": self.global_metrics["total_hits"],
                        "total_misses": self.global_metrics["total_misses"],
                        "global_hit_ratio": global_hit_ratio,
                        "total_size_bytes": self.global_metrics["total_size_bytes"],
                        "total_evictions": self.global_metrics["evictions"],
                        "compressions": self.global_metrics["compressions"]
                    },
                    "cache_instances": len(self.cache_instances),
                    "edge_nodes": len(self.edge_nodes),
                    "cache_summaries": cache_summaries
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {}
            
    async def _ensure_capacity(self, cache_id: str, required_bytes: int) -> None:
        """Ensure cache has enough capacity"""
        try:
            cache = self.cache_instances[cache_id]
            config = self.cache_configs[cache_id]
            metrics = self.cache_metrics[cache_id]
            
            max_size_bytes = config.max_size_mb * 1024 * 1024
            
            # Check if we need to evict entries
            while (metrics.total_size_bytes + required_bytes > max_size_bytes or
                   len(cache) >= config.max_entries):
                
                if not cache:
                    break
                    
                # Evict based on strategy
                key_to_evict = await self._select_eviction_candidate(cache_id)
                if key_to_evict:
                    await self._evict_entry(cache_id, key_to_evict, reason="capacity")
                else:
                    break
                    
        except Exception as e:
            logger.error(f"Failed to ensure capacity: {e}")
            
    async def _select_eviction_candidate(self, cache_id: str) -> Optional[str]:
        """Select entry for eviction based on strategy"""
        try:
            cache = self.cache_instances[cache_id]
            config = self.cache_configs[cache_id]
            
            if not cache:
                return None
                
            if config.strategy == CacheStrategy.LRU:
                # Least recently used
                oldest_time = min(entry.last_accessed for entry in cache.values())
                for key, entry in cache.items():
                    if entry.last_accessed == oldest_time:
                        return key
                        
            elif config.strategy == CacheStrategy.LFU:
                # Least frequently used
                min_access_count = min(entry.access_count for entry in cache.values())
                for key, entry in cache.items():
                    if entry.access_count == min_access_count:
                        return key
                        
            elif config.strategy == CacheStrategy.FIFO:
                # First in, first out
                oldest_time = min(entry.created_at for entry in cache.values())
                for key, entry in cache.items():
                    if entry.created_at == oldest_time:
                        return key
                        
            elif config.strategy == CacheStrategy.TTL:
                # Shortest TTL remaining
                current_time = datetime.now(timezone.utc)
                min_remaining_time = float('inf')
                candidate_key = None
                
                for key, entry in cache.items():
                    if entry.ttl_seconds:
                        elapsed = (current_time - entry.created_at).total_seconds()
                        remaining = entry.ttl_seconds - elapsed
                        if remaining < min_remaining_time:
                            min_remaining_time = remaining
                            candidate_key = key
                            
                return candidate_key
                
            else:
                # Default to LRU
                oldest_time = min(entry.last_accessed for entry in cache.values())
                for key, entry in cache.items():
                    if entry.last_accessed == oldest_time:
                        return key
                        
            return None
            
        except Exception as e:
            logger.error(f"Failed to select eviction candidate: {e}")
            return None
            
    async def _evict_entry(self, cache_id: str, key: str, reason: str = "unknown") -> None:
        """Evict cache entry"""
        try:
            cache = self.cache_instances[cache_id]
            metrics = self.cache_metrics[cache_id]
            
            if key in cache:
                entry = cache[key]
                
                # Update metrics
                metrics.total_size_bytes -= entry.size_bytes
                metrics.entry_count -= 1
                metrics.evictions += 1
                self.global_metrics["total_size_bytes"] -= entry.size_bytes
                self.global_metrics["evictions"] += 1
                
                del cache[key]
                
                await self._record_cache_event(
                    cache_id, CacheEventType.EVICTION, CacheOperation.EVICT, key,
                    metadata={"reason": reason}
                )
                
                logger.debug(f"Evicted cache entry: {key} from {cache_id} (reason: {reason})")
                
        except Exception as e:
            logger.error(f"Failed to evict entry: {e}")
            
    async def _compress_data(self, data: Any, compression_type: CompressionType) -> bytes:
        """Compress data"""
        try:
            serialized = pickle.dumps(data)
            
            if compression_type == CompressionType.GZIP:
                return gzip.compress(serialized)
            elif compression_type == CompressionType.LZ4:
                # Would use lz4 if available
                return gzip.compress(serialized)  # Fallback
            elif compression_type == CompressionType.ZSTD:
                # Would use zstd if available
                return gzip.compress(serialized)  # Fallback
            else:
                return serialized
                
        except Exception as e:
            logger.error(f"Failed to compress data: {e}")
            return pickle.dumps(data)
            
    async def _decompress_data(self, data: bytes, compression_type: CompressionType) -> Any:
        """Decompress data"""
        try:
            if compression_type == CompressionType.GZIP:
                decompressed = gzip.decompress(data)
            elif compression_type == CompressionType.LZ4:
                # Would use lz4 if available
                decompressed = gzip.decompress(data)  # Fallback
            elif compression_type == CompressionType.ZSTD:
                # Would use zstd if available
                decompressed = gzip.decompress(data)  # Fallback
            else:
                decompressed = data
                
            return pickle.loads(decompressed)
            
        except Exception as e:
            logger.error(f"Failed to decompress data: {e}")
            return pickle.loads(data)
            
    async def _record_cache_event(
        self,
        cache_id: str,
        event_type: CacheEventType,
        operation: CacheOperation,
        key: str,
        execution_time_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record cache event"""
        try:
            event = CacheEvent(
                event_id=str(uuid.uuid4()),
                cache_id=cache_id,
                event_type=event_type,
                operation=operation,
                key=key,
                execution_time_ms=execution_time_ms,
                metadata=metadata or {}
            )
            
            self.cache_events.append(event)
            
        except Exception as e:
            logger.error(f"Failed to record cache event: {e}")
            
    async def _cache_maintenance(self) -> None:
        """Background cache maintenance task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Maintenance every minute
                
                # Clean expired entries
                for cache_id in self.cache_instances.keys():
                    await self._clean_expired_entries(cache_id)
                    
                # Update cache metrics
                await self._update_cache_metrics()
                
            except Exception as e:
                logger.error(f"Cache maintenance error: {e}")
                
    async def _clean_expired_entries(self, cache_id: str) -> None:
        """Clean expired entries from cache"""
        try:
            cache = self.cache_instances[cache_id]
            expired_keys = []
            
            for key, entry in cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
                    
            for key in expired_keys:
                await self._evict_entry(cache_id, key, reason="expiration")
                
            if expired_keys:
                logger.debug(f"Cleaned {len(expired_keys)} expired entries from {cache_id}")
                
        except Exception as e:
            logger.error(f"Failed to clean expired entries: {e}")
            
    async def _update_cache_metrics(self) -> None:
        """Update cache metrics"""
        try:
            for cache_id, metrics in self.cache_metrics.items():
                # Calculate hit ratio
                total_requests = metrics.cache_hits + metrics.cache_misses
                if total_requests > 0:
                    metrics.hit_ratio = metrics.cache_hits / total_requests
                    
                metrics.last_updated = datetime.now(timezone.utc)
                
            # Update global hit ratio
            total_requests = self.global_metrics["total_hits"] + self.global_metrics["total_misses"]
            if total_requests > 0:
                self.global_metrics["global_hit_ratio"] = self.global_metrics["total_hits"] / total_requests
                
        except Exception as e:
            logger.error(f"Failed to update cache metrics: {e}")
            
    async def _metrics_collector(self) -> None:
        """Background metrics collection task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Collect every 30 seconds
                
                # Collect performance metrics
                await self._collect_performance_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                
    async def _collect_performance_metrics(self) -> None:
        """Collect performance metrics"""
        try:
            # Calculate average response times
            recent_events = [e for e in self.cache_events if e.timestamp >= datetime.now(timezone.utc) - timedelta(minutes=5)]
            
            if recent_events:
                cache_response_times = defaultdict(list)
                for event in recent_events:
                    cache_response_times[event.cache_id].append(event.execution_time_ms)
                    
                for cache_id, response_times in cache_response_times.items():
                    if cache_id in self.cache_metrics:
                        self.cache_metrics[cache_id].average_response_time_ms = statistics.mean(response_times)
                        
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            
    async def _prefetch_engine(self) -> None:
        """Background prefetch engine task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
                # Analyze access patterns
                await self._analyze_access_patterns()
                
                # Generate prefetch predictions
                await self._generate_prefetch_predictions()
                
            except Exception as e:
                logger.error(f"Prefetch engine error: {e}")
                
    async def _analyze_access_patterns(self) -> None:
        """Analyze access patterns for predictive caching"""
        try:
            # Analyze temporal patterns
            current_time = datetime.now(timezone.utc)
            
            for key, access_times in self.access_patterns.items():
                if len(access_times) >= 3:
                    # Calculate access frequency
                    time_deltas = []
                    for i in range(1, len(access_times)):
                        delta = (access_times[i] - access_times[i-1]).total_seconds()
                        time_deltas.append(delta)
                        
                    if time_deltas:
                        avg_interval = statistics.mean(time_deltas)
                        last_access = access_times[-1]
                        
                        # Predict next access time
                        predicted_next_access = last_access + timedelta(seconds=avg_interval)
                        
                        # Calculate prefetch score
                        time_until_predicted = (predicted_next_access - current_time).total_seconds()
                        if 0 < time_until_predicted < 3600:  # Within next hour
                            score = max(0, 1 - (time_until_predicted / 3600))
                            self.prefetch_predictions[key] = score
                            
        except Exception as e:
            logger.error(f"Failed to analyze access patterns: {e}")
            
    async def _generate_prefetch_predictions(self) -> None:
        """Generate prefetch predictions"""
        try:
            # Sort predictions by score
            sorted_predictions = sorted(
                self.prefetch_predictions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Log top predictions
            top_predictions = sorted_predictions[:10]
            if top_predictions:
                logger.debug(f"Top prefetch candidates: {[(k, f'{v:.3f}') for k, v in top_predictions]}")
                
        except Exception as e:
            logger.error(f"Failed to generate prefetch predictions: {e}")
            
    async def _edge_optimizer(self) -> None:
        """Background edge optimization task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(600)  # Optimize every 10 minutes
                
                # Optimize edge node performance
                await self._optimize_edge_nodes()
                
            except Exception as e:
                logger.error(f"Edge optimizer error: {e}")
                
    async def _optimize_edge_nodes(self) -> None:
        """Optimize edge node performance"""
        try:
            for node_id, node in self.edge_nodes.items():
                cache_id = f"edge_{node_id}"
                
                if cache_id in self.cache_metrics:
                    metrics = self.cache_metrics[cache_id]
                    
                    # Update node statistics
                    node.cache_hit_ratio = metrics.hit_ratio
                    
                    # Calculate load based on cache utilization
                    config = self.cache_configs[cache_id]
                    max_size_bytes = config.max_size_mb * 1024 * 1024
                    node.load_percentage = (metrics.total_size_bytes / max_size_bytes) * 100 if max_size_bytes > 0 else 0
                    
                    # Optimize cache strategy if needed
                    if metrics.hit_ratio < 0.7:  # Low hit ratio
                        # Consider changing strategy
                        if config.strategy == CacheStrategy.LRU:
                            config.strategy = CacheStrategy.LFU
                            logger.info(f"Changed edge node {node_id} strategy to LFU")
                            
        except Exception as e:
            logger.error(f"Failed to optimize edge nodes: {e}")
            
    async def shutdown(self) -> None:
        """Gracefully shutdown the cache streams system"""
        try:
            logger.info("Shutting down CacheStreams...")
            
            self._shutdown_event.set()
            
            # Cancel background tasks
            tasks_to_cancel = [
                self.cache_maintenance_task,
                self.metrics_collector_task,
                self.prefetch_engine_task,
                self.edge_optimizer_task
            ]
            
            for task in tasks_to_cancel:
                if task:
                    task.cancel()
                    
            # Persist caches if enabled
            for cache_id, config in self.cache_configs.items():
                if config.enable_persistence:
                    await self._persist_cache(cache_id)
                    
            self._running = False
            logger.info("CacheStreams shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            
    async def _persist_cache(self, cache_id: str) -> None:
        """Persist cache to disk"""
        try:
            # This would implement cache persistence
            # For now, just log the operation
            logger.info(f"Persisting cache {cache_id}")
            
        except Exception as e:
            logger.error(f"Failed to persist cache {cache_id}: {e}")