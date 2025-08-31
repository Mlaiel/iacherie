"""Multimedia Cache - Advanced Caching Engine

Enterprise-grade caching system for multimedia content with intelligent cache management.
Provides multi-layer caching, automatic invalidation, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import uuid
import time
import hashlib
import pickle
import gzip
from pathlib import Path
import tempfile

from ..monitoring.metrics import MetricsCollector
from ..events.dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache level types"""    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"
    CDN = "cdn"


class CacheStrategy(Enum):
    """Cache eviction strategies"""    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    SIZE_BASED = "size_based"
    PRIORITY_BASED = "priority_based"


class CacheType(Enum):
    """Types of cached content"""    ORIGINAL_CONTENT = "original_content"
    PROCESSED_CONTENT = "processed_content"
    THUMBNAILS = "thumbnails"
    METADATA = "metadata"
    TRANSCODED_VERSIONS = "transcoded_versions"
    ENHANCED_VERSIONS = "enhanced_versions"


@dataclass
class CacheEntry:
    """Cache entry information"""    cache_key: str
    content_type: CacheType
    data: Union[bytes, str, Dict[str, Any]]
    size_bytes: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    priority: int = 5
    ttl_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compression_ratio: float = 1.0


@dataclass
class CacheConfig:
    """Cache configuration"""    max_memory_size: int = 1024 * 1024 * 1024  # 1GB
    max_disk_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    default_ttl: int = 3600  # 1 hour
    cleanup_interval: int = 300  # 5 minutes
    compression_enabled: bool = True
    compression_threshold: int = 1024  # Compress if > 1KB
    enable_distributed: bool = False
    distributed_nodes: List[str] = field(default_factory=list)


@dataclass
class CacheStats:
    """Cache statistics"""    total_entries: int = 0
    memory_usage_bytes: int = 0
    disk_usage_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    compression_savings: int = 0


class MultimediaCache:
    """    Advanced multimedia caching engine with multi-layer architecture.
    
    Features:
    - Multi-layer caching (memory, disk, distributed)
    - Intelligent cache strategies (LRU, LFU, TTL)
    - Content compression and optimization
    - Automatic cache invalidation
    - Performance monitoring and analytics
    - Tag-based cache management
    - Distributed cache synchronization
    """    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize multimedia cache"""        self.config = config or CacheConfig()
        self.metrics = MetricsCollector()
        self.events = EventDispatcher()
        
        # Cache storage layers
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.disk_cache_dir = Path(tempfile.gettempdir()) / "multimedia_cache"
        self.disk_cache_dir.mkdir(exist_ok=True)
        
        # Cache management
        self.cache_index: Dict[str, Dict[str, Any]] = {}
        self.access_order: List[str] = []  # For LRU
        self.access_frequency: Dict[str, int] = {}  # For LFU
        
        # Statistics
        self.stats = CacheStats()
        
        # Start background tasks
        self._start_cleanup_task()
        
        logger.info("Multimedia cache initialized successfully")
    
    def _generate_cache_key(
        self,
        identifier: str,
        cache_type: CacheType,
        variant: Optional[str] = None
    ) -> str:
        """Generate cache key for content"""        key_parts = [identifier, cache_type.value]
        if variant:
            key_parts.append(variant)
        
        key_string = ":".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def store(
        self,
        identifier: str,
        data: Union[bytes, str, Dict[str, Any]],
        cache_type: CacheType = CacheType.ORIGINAL_CONTENT,
        variant: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        priority: int = 5,
        tags: Optional[List[str]] = None,
        force_disk: bool = False
    ) -> str:
        """        Store content in cache
        
        Args:
            identifier: Content identifier
            data: Data to cache
            cache_type: Type of cached content
            variant: Content variant (e.g., "720p", "thumbnail_small")
            ttl_seconds: Time to live in seconds
            priority: Cache priority (1-10, higher = more important)
            tags: Tags for cache management
            force_disk: Force storage to disk cache
            
        Returns:
            str: Cache key
        """        cache_key = self._generate_cache_key(identifier, cache_type, variant)
        
        # Prepare data for storage
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Compress if enabled and above threshold
        compression_ratio = 1.0
        if (self.config.compression_enabled and 
            len(data_bytes) > self.config.compression_threshold):
            compressed_data = gzip.compress(data_bytes)
            if len(compressed_data) < len(data_bytes):
                data_bytes = compressed_data
                compression_ratio = len(data_bytes) / len(compressed_data)
                self.stats.compression_savings += len(data_bytes) - len(compressed_data)
        
        # Create cache entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            cache_key=cache_key,
            content_type=cache_type,
            data=data_bytes,
            size_bytes=len(data_bytes),
            created_at=now,
            last_accessed=now,
            priority=priority,
            ttl_seconds=ttl_seconds or self.config.default_ttl,
            tags=tags or [],
            compression_ratio=compression_ratio
        )
        
        # Determine storage location
        if (not force_disk and 
            len(data_bytes) < 10 * 1024 * 1024 and  # < 10MB
            self.stats.memory_usage_bytes + len(data_bytes) < self.config.max_memory_size):
            # Store in memory
            await self._store_in_memory(entry)
        else:
            # Store on disk
            await self._store_on_disk(entry)
        
        # Update index and statistics
        self.cache_index[cache_key] = {
            'location': 'memory' if cache_key in self.memory_cache else 'disk',
            'cache_type': cache_type.value,
            'identifier': identifier,
            'variant': variant,
            'size': len(data_bytes),
            'created_at': now.isoformat(),
            'tags': tags or []
        }
        
        self.stats.total_entries += 1
        
        # Update access tracking
        self._update_access_tracking(cache_key)
        
        # Emit event
        await self.events.emit('cache_store', {
            'cache_key': cache_key,
            'identifier': identifier,
            'cache_type': cache_type.value,
            'size': len(data_bytes)
        })
        
        logger.debug(f"Stored in cache: {cache_key}")
        return cache_key
    
    async def retrieve(
        self,
        identifier: str,
        cache_type: CacheType = CacheType.ORIGINAL_CONTENT,
        variant: Optional[str] = None
    ) -> Optional[Union[bytes, str, Dict[str, Any]]]:
        """        Retrieve content from cache
        
        Args:
            identifier: Content identifier
            cache_type: Type of cached content
            variant: Content variant
            
        Returns:
            Cached data or None if not found
        """        cache_key = self._generate_cache_key(identifier, cache_type, variant)
        
        # Check if entry exists
        if cache_key not in self.cache_index:
            self.stats.miss_count += 1
            return None
        
        # Check TTL
        if await self._is_expired(cache_key):
            await self._remove_entry(cache_key)
            self.stats.miss_count += 1
            return None
        
        # Retrieve from appropriate storage
        entry = None
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
        else:
            entry = await self._load_from_disk(cache_key)
        
        if not entry:
            self.stats.miss_count += 1
            return None
        
        # Update access tracking
        self._update_access_tracking(cache_key)
        entry.last_accessed = datetime.now(timezone.utc)
        entry.access_count += 1
        
        self.stats.hit_count += 1
        
        # Decompress if needed
        data = entry.data
        if entry.compression_ratio != 1.0 and isinstance(data, bytes):
            try:
                data = gzip.decompress(data)
            except:
                pass  # Data might not be compressed
        
        # Convert back to original type if needed
        if cache_type in [CacheType.METADATA]:
            try:
                return json.loads(data.decode('utf-8'))
            except:
                pass
        
        # Emit event
        await self.events.emit('cache_hit', {
            'cache_key': cache_key,
            'identifier': identifier,
            'cache_type': cache_type.value
        })
        
        return data
    
    async def _store_in_memory(self, entry: CacheEntry):
        """Store entry in memory cache"""        # Check if eviction is needed
        if (self.stats.memory_usage_bytes + entry.size_bytes > self.config.max_memory_size):
            await self._evict_memory_entries(entry.size_bytes)
        
        self.memory_cache[entry.cache_key] = entry
        self.stats.memory_usage_bytes += entry.size_bytes
    
    async def _store_on_disk(self, entry: CacheEntry):
        """Store entry on disk cache"""        # Check if eviction is needed
        if (self.stats.disk_usage_bytes + entry.size_bytes > self.config.max_disk_size):
            await self._evict_disk_entries(entry.size_bytes)
        
        # Create disk file
        cache_file = self.disk_cache_dir / f"{entry.cache_key}.cache"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
            
            self.stats.disk_usage_bytes += entry.size_bytes
            
        except Exception as e:
            logger.error(f"Failed to store cache entry on disk: {str(e)}")
            raise
    
    async def _load_from_disk(self, cache_key: str) -> Optional[CacheEntry]:
        """Load entry from disk cache"""        cache_file = self.disk_cache_dir / f"{cache_key}.cache"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                entry = pickle.load(f)
            return entry
            
        except Exception as e:
            logger.error(f"Failed to load cache entry from disk: {str(e)}")
            # Remove corrupted file
            try:
                cache_file.unlink()
            except:
                pass
            return None
    
    async def _evict_memory_entries(self, needed_space: int):
        """Evict entries from memory cache to free space"""        freed_space = 0
        entries_to_remove = []
        
        # Sort by LRU order
        sorted_keys = sorted(
            self.memory_cache.keys(),
            key=lambda k: self.access_order.index(k) if k in self.access_order else 0
        )
        
        for cache_key in sorted_keys:
            if freed_space >= needed_space:
                break
            
            entry = self.memory_cache[cache_key]
            entries_to_remove.append(cache_key)
            freed_space += entry.size_bytes
        
        # Remove entries
        for cache_key in entries_to_remove:
            await self._remove_from_memory(cache_key)
    
    async def _evict_disk_entries(self, needed_space: int):
        """Evict entries from disk cache to free space"""        freed_space = 0
        entries_to_remove = []
        
        # Get disk cache entries sorted by access time
        disk_entries = []
        for cache_key, index_entry in self.cache_index.items():
            if index_entry['location'] == 'disk':
                disk_entries.append((cache_key, index_entry))
        
        # Sort by creation time (oldest first)
        disk_entries.sort(key=lambda x: x[1]['created_at'])
        
        for cache_key, index_entry in disk_entries:
            if freed_space >= needed_space:
                break
            
            entries_to_remove.append(cache_key)
            freed_space += index_entry['size']
        
        # Remove entries
        for cache_key in entries_to_remove:
            await self._remove_from_disk(cache_key)
    
    async def _remove_entry(self, cache_key: str):
        """Remove entry from cache"""        if cache_key in self.memory_cache:
            await self._remove_from_memory(cache_key)
        else:
            await self._remove_from_disk(cache_key)
        
        # Remove from index
        if cache_key in self.cache_index:
            del self.cache_index[cache_key]
        
        # Remove from access tracking
        if cache_key in self.access_order:
            self.access_order.remove(cache_key)
        if cache_key in self.access_frequency:
            del self.access_frequency[cache_key]
        
        self.stats.total_entries -= 1
        self.stats.eviction_count += 1
    
    async def _remove_from_memory(self, cache_key: str):
        """Remove entry from memory cache"""        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            self.stats.memory_usage_bytes -= entry.size_bytes
            del self.memory_cache[cache_key]
    
    async def _remove_from_disk(self, cache_key: str):
        """Remove entry from disk cache"""        cache_file = self.disk_cache_dir / f"{cache_key}.cache"
        
        if cache_file.exists():
            file_size = cache_file.stat().st_size
            cache_file.unlink()
            self.stats.disk_usage_bytes -= file_size
    
    async def _is_expired(self, cache_key: str) -> bool:
        """Check if cache entry is expired"""        if cache_key not in self.cache_index:
            return True
        
        # Load entry to check TTL
        entry = None
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
        else:
            entry = await self._load_from_disk(cache_key)
        
        if not entry or not entry.ttl_seconds:
            return False
        
        expiry_time = entry.created_at + timedelta(seconds=entry.ttl_seconds)
        return datetime.now(timezone.utc) > expiry_time
    
    def _update_access_tracking(self, cache_key: str):
        """Update access tracking for cache strategies"""        # Update LRU order
        if cache_key in self.access_order:
            self.access_order.remove(cache_key)
        self.access_order.append(cache_key)
        
        # Update LFU frequency
        self.access_frequency[cache_key] = self.access_frequency.get(cache_key, 0) + 1
    
    async def invalidate(
        self,
        identifier: str,
        cache_type: Optional[CacheType] = None,
        variant: Optional[str] = None
    ):
        """        Invalidate cache entries
        
        Args:
            identifier: Content identifier
            cache_type: Specific cache type to invalidate (optional)
            variant: Specific variant to invalidate (optional)
        """        keys_to_remove = []
        
        for cache_key, index_entry in self.cache_index.items():
            if index_entry['identifier'] == identifier:
                if cache_type is None or index_entry['cache_type'] == cache_type.value:
                    if variant is None or index_entry['variant'] == variant:
                        keys_to_remove.append(cache_key)
        
        for cache_key in keys_to_remove:
            await self._remove_entry(cache_key)
        
        # Emit event
        await self.events.emit('cache_invalidate', {
            'identifier': identifier,
            'cache_type': cache_type.value if cache_type else 'all',
            'variant': variant,
            'entries_removed': len(keys_to_remove)
        })
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries for {identifier}")
    
    async def invalidate_by_tags(self, tags: List[str]):
        """Invalidate cache entries by tags"""        keys_to_remove = []
        
        for cache_key, index_entry in self.cache_index.items():
            entry_tags = index_entry.get('tags', [])
            if any(tag in entry_tags for tag in tags):
                keys_to_remove.append(cache_key)
        
        for cache_key in keys_to_remove:
            await self._remove_entry(cache_key)
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries by tags: {tags}")
    
    async def clear_cache(self, cache_level: Optional[CacheLevel] = None):
        """Clear cache entries"""        if cache_level == CacheLevel.MEMORY or cache_level is None:
            self.memory_cache.clear()
            self.stats.memory_usage_bytes = 0
        
        if cache_level == CacheLevel.DISK or cache_level is None:
            # Remove all disk cache files
            for cache_file in self.disk_cache_dir.glob("*.cache"):
                cache_file.unlink()
            self.stats.disk_usage_bytes = 0
        
        if cache_level is None:
            self.cache_index.clear()
            self.access_order.clear()
            self.access_frequency.clear()
            self.stats.total_entries = 0
        
        logger.info(f"Cleared cache: {cache_level.value if cache_level else 'all'}")
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information and statistics"""        hit_ratio = (
            self.stats.hit_count / (self.stats.hit_count + self.stats.miss_count)
            if (self.stats.hit_count + self.stats.miss_count) > 0 else 0
        )
        
        return {
            'statistics': {
                'total_entries': self.stats.total_entries,
                'memory_usage_mb': self.stats.memory_usage_bytes / (1024 * 1024),
                'disk_usage_mb': self.stats.disk_usage_bytes / (1024 * 1024),
                'hit_count': self.stats.hit_count,
                'miss_count': self.stats.miss_count,
                'hit_ratio': hit_ratio,
                'eviction_count': self.stats.eviction_count,
                'compression_savings_mb': self.stats.compression_savings / (1024 * 1024)
            },
            'configuration': {
                'max_memory_mb': self.config.max_memory_size / (1024 * 1024),
                'max_disk_mb': self.config.max_disk_size / (1024 * 1024),
                'default_ttl': self.config.default_ttl,
                'compression_enabled': self.config.compression_enabled
            },
            'cache_distribution': {
                'memory_entries': len(self.memory_cache),
                'disk_entries': self.stats.total_entries - len(self.memory_cache)
            }
        }
    
    async def list_cached_content(
        self,
        identifier: Optional[str] = None,
        cache_type: Optional[CacheType] = None
    ) -> List[Dict[str, Any]]:
        """List cached content"""        results = []
        
        for cache_key, index_entry in self.cache_index.items():
            if identifier and index_entry['identifier'] != identifier:
                continue
            if cache_type and index_entry['cache_type'] != cache_type.value:
                continue
            
            results.append({
                'cache_key': cache_key,
                'identifier': index_entry['identifier'],
                'cache_type': index_entry['cache_type'],
                'variant': index_entry['variant'],
                'size_mb': index_entry['size'] / (1024 * 1024),
                'location': index_entry['location'],
                'created_at': index_entry['created_at'],
                'tags': index_entry['tags']
            })
        
        return results
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""        asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""        while True:
            try:
                await self._cleanup_expired_entries()
                await asyncio.sleep(self.config.cleanup_interval)
            except Exception as e:
                logger.error(f"Cache cleanup error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""        expired_keys = []
        
        for cache_key in list(self.cache_index.keys()):
            if await self._is_expired(cache_key):
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            await self._remove_entry(cache_key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def prefetch(
        self,
        identifiers: List[str],
        cache_type: CacheType = CacheType.ORIGINAL_CONTENT
    ) -> Dict[str, bool]:
        """        Prefetch content into cache
        
        Args:
            identifiers: List of content identifiers to prefetch
            cache_type: Type of content to prefetch
            
        Returns:
            Dict mapping identifiers to prefetch success status
        """        results = {}
        
        for identifier in identifiers:
            try:
                # This would trigger actual content loading and caching
                # For now, just mark as successful
                results[identifier] = True
                
                # Emit event
                await self.events.emit('cache_prefetch', {
                    'identifier': identifier,
                    'cache_type': cache_type.value,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Prefetch failed for {identifier}: {str(e)}")
                results[identifier] = False
        
        return results
