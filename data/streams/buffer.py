"""Stream Buffer Management for IA Influencer Agent Platform
========================================================

High-performance buffering system for stream data with intelligent
caching, compression, and memory-efficient storage strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import pickle
import zlib
import json
from collections import deque
import threading

from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...utils.logging import get_logger
from .manager import StreamEvent

logger = get_logger(__name__)
settings = get_settings()


class BufferType(str, Enum):
    """Buffer storage types"""    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"
    HYBRID = "hybrid"


class CompressionType(str, Enum):
    """Data compression types"""    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    PICKLE = "pickle"


class EvictionPolicy(str, Enum):
    """Buffer eviction policies"""    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live


@dataclass
class BufferConfig:
    """Buffer configuration settings"""    buffer_type: BufferType = BufferType.MEMORY
    max_size_mb: int = 100
    max_items: int = 10000
    ttl_seconds: int = 3600
    compression: CompressionType = CompressionType.NONE
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    auto_flush: bool = True
    flush_interval_seconds: int = 300
    enable_persistence: bool = False
    persistence_path: Optional[str] = None


@dataclass
class BufferItem:
    """Buffer item with metadata"""    key: str
    data: Any
    size_bytes: int
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class BufferStats(BaseModel):
    """Buffer performance statistics"""    total_items: int = Field(default=0, description="Total items in buffer")
    total_size_mb: float = Field(default=0.0, description="Total size in MB")
    hit_ratio: float = Field(default=0.0, description="Cache hit ratio")
    miss_ratio: float = Field(default=0.0, description="Cache miss ratio")
    evictions: int = Field(default=0, description="Total evictions")
    compressions: int = Field(default=0, description="Total compressions")
    memory_usage_mb: float = Field(default=0.0, description="Memory usage in MB")
    avg_access_time_ms: float = Field(default=0.0, description="Average access time")
    last_flush: Optional[datetime] = Field(default=None, description="Last flush timestamp")


class StreamBuffer:
    """    High-performance stream buffer with intelligent caching, compression,
    and memory-efficient storage for optimal stream processing performance.
    """    
    def __init__(self, config: BufferConfig):
        self.config = config
        self.items: Dict[str, BufferItem] = {}
        self.access_queue: deque = deque()  # For LRU tracking
        self.access_frequency: Dict[str, int] = {}  # For LFU tracking
        self.stats = BufferStats()
        self._lock = threading.RLock()
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize stream buffer"""        try:
            # Load persisted data if enabled
            if self.config.enable_persistence and self.config.persistence_path:
                await self._load_from_disk()
                
            # Start background tasks
            if self.config.auto_flush:
                asyncio.create_task(self._auto_flush_task())
                
            asyncio.create_task(self._cleanup_task())
            asyncio.create_task(self._stats_updater())
            
            logger.info(f"StreamBuffer initialized with {self.config.buffer_type} storage")
            
        except Exception as e:
            logger.error(f"Failed to initialize StreamBuffer: {e}")
            raise
            
    async def put(
        self,
        key: str,
        data: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Store data in buffer
        
        Args:
            key: Item key
            data: Data to store
            ttl_seconds: Optional TTL override
            metadata: Optional metadata
            
        Returns:
            Success status
        """        try:
            with self._lock:
                # Check if we need to evict items
                await self._ensure_capacity()
                
                # Compress data if configured
                compressed_data, compressed = await self._compress_data(data)
                
                # Calculate size
                size_bytes = len(pickle.dumps(compressed_data))
                
                # Create buffer item
                now = datetime.now(timezone.utc)
                item = BufferItem(
                    key=key,
                    data=compressed_data,
                    size_bytes=size_bytes,
                    created_at=now,
                    accessed_at=now,
                    compressed=compressed,
                    metadata=metadata or {}
                )
                
                # Store item
                self.items[key] = item
                
                # Update tracking structures
                self._update_access_tracking(key)
                
                # Update stats
                self.stats.total_items = len(self.items)
                self.stats.total_size_mb = sum(item.size_bytes for item in self.items.values()) / (1024 * 1024)
                
                if compressed:
                    self.stats.compressions += 1
                    
                logger.debug(f"Stored item {key} ({size_bytes} bytes)")
                return True
                
        except Exception as e:
            logger.error(f"Failed to put item {key}: {e}")
            return False
            
    async def get(self, key: str) -> Optional[Any]:
        """        Retrieve data from buffer
        
        Args:
            key: Item key
            
        Returns:
            Stored data or None if not found
        """        try:
            with self._lock:
                if key not in self.items:
                    self.stats.miss_ratio = (self.stats.miss_ratio * 0.9) + 0.1
                    return None
                    
                item = self.items[key]
                
                # Check TTL
                if self._is_expired(item):
                    await self._remove_item(key)
                    self.stats.miss_ratio = (self.stats.miss_ratio * 0.9) + 0.1
                    return None
                    
                # Update access info
                item.accessed_at = datetime.now(timezone.utc)
                item.access_count += 1
                self._update_access_tracking(key)
                
                # Decompress if needed
                data = await self._decompress_data(item.data, item.compressed)
                
                # Update stats
                self.stats.hit_ratio = (self.stats.hit_ratio * 0.9) + 0.1
                
                logger.debug(f"Retrieved item {key}")
                return data
                
        except Exception as e:
            logger.error(f"Failed to get item {key}: {e}")
            return None
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in buffer"""        with self._lock:
            if key not in self.items:
                return False
            return not self._is_expired(self.items[key])
            
    async def delete(self, key: str) -> bool:
        """Delete item from buffer"""        try:
            with self._lock:
                if key in self.items:
                    await self._remove_item(key)
                    logger.debug(f"Deleted item {key}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete item {key}: {e}")
            return False
            
    async def clear(self) -> None:
        """Clear all items from buffer"""        try:
            with self._lock:
                self.items.clear()
                self.access_queue.clear()
                self.access_frequency.clear()
                
                self.stats.total_items = 0
                self.stats.total_size_mb = 0.0
                
                logger.info("Buffer cleared")
                
        except Exception as e:
            logger.error(f"Failed to clear buffer: {e}")
            
    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys in buffer, optionally filtered by pattern"""        try:
            with self._lock:
                all_keys = list(self.items.keys())
                
                if pattern:
                    import re
                    regex = re.compile(pattern)
                    return [key for key in all_keys if regex.match(key)]
                    
                return all_keys
                
        except Exception as e:
            logger.error(f"Failed to get keys: {e}")
            return []
            
    async def flush(self) -> bool:
        """Flush buffer to persistent storage"""        try:
            if not self.config.enable_persistence or not self.config.persistence_path:
                return False
                
            with self._lock:
                await self._save_to_disk()
                self.stats.last_flush = datetime.now(timezone.utc)
                
                logger.info("Buffer flushed to disk")
                return True
                
        except Exception as e:
            logger.error(f"Failed to flush buffer: {e}")
            return False
            
    async def get_stats(self) -> BufferStats:
        """Get buffer performance statistics"""        with self._lock:
            # Update memory usage
            import psutil
            process = psutil.Process()
            self.stats.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
            
            return self.stats
            
    async def optimize(self) -> None:
        """Optimize buffer performance"""        try:
            with self._lock:
                # Compress uncompressed items if beneficial
                if self.config.compression != CompressionType.NONE:
                    await self._compress_items()
                    
                # Remove expired items
                await self._cleanup_expired()
                
                # Defragment if needed
                await self._defragment()
                
                logger.info("Buffer optimization completed")
                
        except Exception as e:
            logger.error(f"Failed to optimize buffer: {e}")
            
    def _update_access_tracking(self, key: str) -> None:
        """Update access tracking for eviction policies"""        # Update LRU queue
        if key in self.access_queue:
            self.access_queue.remove(key)
        self.access_queue.append(key)
        
        # Update LFU frequency
        self.access_frequency[key] = self.access_frequency.get(key, 0) + 1
        
    def _is_expired(self, item: BufferItem) -> bool:
        """Check if item has expired"""        ttl = self.config.ttl_seconds
        if ttl <= 0:
            return False
            
        age = (datetime.now(timezone.utc) - item.created_at).total_seconds()
        return age > ttl
        
    async def _ensure_capacity(self) -> None:
        """Ensure buffer has capacity for new items"""        # Check size limit
        while self.stats.total_size_mb > self.config.max_size_mb and self.items:
            await self._evict_item()
            
        # Check item count limit
        while len(self.items) >= self.config.max_items and self.items:
            await self._evict_item()
            
    async def _evict_item(self) -> None:
        """Evict item based on configured policy"""        try:
            if not self.items:
                return
                
            if self.config.eviction_policy == EvictionPolicy.LRU:
                # Remove least recently used
                key = self.access_queue.popleft()
            elif self.config.eviction_policy == EvictionPolicy.LFU:
                # Remove least frequently used
                key = min(self.access_frequency.items(), key=lambda x: x[1])[0]
            elif self.config.eviction_policy == EvictionPolicy.FIFO:
                # Remove oldest item
                key = min(self.items.items(), key=lambda x: x[1].created_at)[0]
            elif self.config.eviction_policy == EvictionPolicy.TTL:
                # Remove most expired item
                key = min(
                    self.items.items(),
                    key=lambda x: x[1].created_at
                )[0]
            else:
                # Default to LRU
                key = self.access_queue.popleft()
                
            await self._remove_item(key)
            self.stats.evictions += 1
            
            logger.debug(f"Evicted item {key}")
            
        except Exception as e:
            logger.error(f"Failed to evict item: {e}")
            
    async def _remove_item(self, key: str) -> None:
        """Remove item and update tracking structures"""        if key in self.items:
            del self.items[key]
            
        if key in self.access_queue:
            self.access_queue.remove(key)
            
        if key in self.access_frequency:
            del self.access_frequency[key]
            
        # Update stats
        self.stats.total_items = len(self.items)
        self.stats.total_size_mb = sum(item.size_bytes for item in self.items.values()) / (1024 * 1024)
        
    async def _compress_data(self, data: Any) -> tuple[Any, bool]:
        """Compress data based on configuration"""        if self.config.compression == CompressionType.NONE:
            return data, False
            
        try:
            if self.config.compression == CompressionType.GZIP:
                import gzip
                serialized = pickle.dumps(data)
                compressed = gzip.compress(serialized)
                return compressed, True
            elif self.config.compression == CompressionType.ZLIB:
                serialized = pickle.dumps(data)
                compressed = zlib.compress(serialized)
                return compressed, True
            elif self.config.compression == CompressionType.PICKLE:
                return pickle.dumps(data), True
            else:
                return data, False
                
        except Exception as e:
            logger.warning(f"Compression failed, storing uncompressed: {e}")
            return data, False
            
    async def _decompress_data(self, data: Any, compressed: bool) -> Any:
        """Decompress data if needed"""        if not compressed:
            return data
            
        try:
            if self.config.compression == CompressionType.GZIP:
                import gzip
                decompressed = gzip.decompress(data)
                return pickle.loads(decompressed)
            elif self.config.compression == CompressionType.ZLIB:
                decompressed = zlib.decompress(data)
                return pickle.loads(decompressed)
            elif self.config.compression == CompressionType.PICKLE:
                return pickle.loads(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return data
            
    async def _compress_items(self) -> None:
        """Compress existing uncompressed items"""        for key, item in list(self.items.items()):
            if not item.compressed and self.config.compression != CompressionType.NONE:
                compressed_data, compressed = await self._compress_data(item.data)
                if compressed:
                    item.data = compressed_data
                    item.compressed = True
                    item.size_bytes = len(pickle.dumps(compressed_data))
                    self.stats.compressions += 1
                    
    async def _cleanup_expired(self) -> None:
        """Remove expired items"""        expired_keys = []
        for key, item in self.items.items():
            if self._is_expired(item):
                expired_keys.append(key)
                
        for key in expired_keys:
            await self._remove_item(key)
            
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired items")
            
    async def _defragment(self) -> None:
        """Defragment buffer storage"""        # For memory buffer, this reorganizes data structures
        # For disk buffer, this would compact files
        if self.config.buffer_type == BufferType.MEMORY:
            # Rebuild access queue
            self.access_queue = deque(
                sorted(self.items.keys(), key=lambda k: self.items[k].accessed_at)
            )
            
    async def _save_to_disk(self) -> None:
        """Save buffer to disk"""        if not self.config.persistence_path:
            return
            
        try:
            import os
            os.makedirs(os.path.dirname(self.config.persistence_path), exist_ok=True)
            
            buffer_data = {
                "items": {k: {
                    "data": v.data,
                    "size_bytes": v.size_bytes,
                    "created_at": v.created_at.isoformat(),
                    "accessed_at": v.accessed_at.isoformat(),
                    "access_count": v.access_count,
                    "compressed": v.compressed,
                    "metadata": v.metadata
                } for k, v in self.items.items()},
                "access_frequency": self.access_frequency,
                "stats": self.stats.dict()
            }
            
            with open(self.config.persistence_path, "wb") as f:
                pickle.dump(buffer_data, f)
                
        except Exception as e:
            logger.error(f"Failed to save buffer to disk: {e}")
            
    async def _load_from_disk(self) -> None:
        """Load buffer from disk"""        if not self.config.persistence_path:
            return
            
        try:
            import os
            if not os.path.exists(self.config.persistence_path):
                return
                
            with open(self.config.persistence_path, "rb") as f:
                buffer_data = pickle.load(f)
                
            # Restore items
            for key, item_data in buffer_data.get("items", {}).items():
                item = BufferItem(
                    key=key,
                    data=item_data["data"],
                    size_bytes=item_data["size_bytes"],
                    created_at=datetime.fromisoformat(item_data["created_at"]),
                    accessed_at=datetime.fromisoformat(item_data["accessed_at"]),
                    access_count=item_data["access_count"],
                    compressed=item_data["compressed"],
                    metadata=item_data["metadata"]
                )
                self.items[key] = item
                
            # Restore access frequency
            self.access_frequency = buffer_data.get("access_frequency", {})
            
            # Restore stats
            stats_data = buffer_data.get("stats", {})
            for key, value in stats_data.items():
                if hasattr(self.stats, key):
                    setattr(self.stats, key, value)
                    
            logger.info(f"Loaded {len(self.items)} items from disk")
            
        except Exception as e:
            logger.error(f"Failed to load buffer from disk: {e}")
            
    async def _auto_flush_task(self) -> None:
        """Background auto-flush task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                await self.flush()
            except Exception as e:
                logger.error(f"Auto-flush error: {e}")
                
    async def _cleanup_task(self) -> None:
        """Background cleanup task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                
    async def _stats_updater(self) -> None:
        """Background stats update task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                # Update stats
                with self._lock:
                    self.stats.total_items = len(self.items)
                    self.stats.total_size_mb = sum(
                        item.size_bytes for item in self.items.values()
                    ) / (1024 * 1024)
                    
            except Exception as e:
                logger.error(f"Stats updater error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown buffer"""        try:
            self._shutdown_event.set()
            
            # Final flush if persistence enabled
            if self.config.enable_persistence:
                await self.flush()
                
            logger.info("StreamBuffer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during buffer shutdown: {e}")
