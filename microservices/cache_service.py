"""
🎯 Cache Management Microservice
Distributed caching layer management with multiple backends, intelligent eviction, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import logging
import hashlib
import pickle
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import threading
import weakref
from datetime import datetime, timedelta
from collections import OrderedDict
import struct
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CacheBackend(str, Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    FILE = "file"
    HYBRID = "hybrid"


class EvictionPolicy(str, Enum):
    """Cache eviction policies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    RANDOM = "random"


class SerializationFormat(str, Enum):
    """Serialization formats"""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    STRING = "string"
    BYTES = "bytes"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    serialization_format: SerializationFormat = SerializationFormat.PICKLE
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
        
    def touch(self):
        """Update access time and increment access count"""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'access_count': self.access_count,
            'size_bytes': self.size_bytes,
            'tags': self.tags,
            'serialization_format': self.serialization_format.value
        }


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entries_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
        
    @property
    def miss_rate(self) -> float:
        """Calculate miss rate"""
        return 1.0 - self.hit_rate
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'evictions': self.evictions,
            'size_bytes': self.size_bytes,
            'entries_count': self.entries_count,
            'hit_rate': self.hit_rate,
            'miss_rate': self.miss_rate
        }


class CacheSerializer:
    """Cache value serialization"""
    
    @staticmethod
    def serialize(value: Any, format: SerializationFormat) -> bytes:
        """Serialize value"""
        if format == SerializationFormat.STRING:
            return str(value).encode('utf-8')
        elif format == SerializationFormat.BYTES:
            if isinstance(value, bytes):
                return value
            elif isinstance(value, str):
                return value.encode('utf-8')
            else:
                return str(value).encode('utf-8')
        elif format == SerializationFormat.JSON:
            return json.dumps(value, default=str).encode('utf-8')
        elif format == SerializationFormat.PICKLE:
            return pickle.dumps(value)
        elif format == SerializationFormat.MSGPACK:
            try:
                import msgpack
                return msgpack.packb(value, default=str)
            except ImportError:
                logger.warning("msgpack not available, falling back to pickle")
                return pickle.dumps(value)
        else:
            return pickle.dumps(value)
            
    @staticmethod
    def deserialize(data: bytes, format: SerializationFormat) -> Any:
        """Deserialize value"""
        if format == SerializationFormat.STRING:
            return data.decode('utf-8')
        elif format == SerializationFormat.BYTES:
            return data
        elif format == SerializationFormat.JSON:
            return json.loads(data.decode('utf-8'))
        elif format == SerializationFormat.PICKLE:
            return pickle.loads(data)
        elif format == SerializationFormat.MSGPACK:
            try:
                import msgpack
                return msgpack.unpackb(data, raw=False)
            except ImportError:
                logger.warning("msgpack not available, falling back to pickle")
                return pickle.loads(data)
        else:
            return pickle.loads(data)
            
    @staticmethod
    def calculate_size(value: Any, format: SerializationFormat) -> int:
        """Calculate serialized size"""
        try:
            serialized = CacheSerializer.serialize(value, format)
            return len(serialized)
        except Exception:
            # Fallback estimation
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, bytes):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, bool):
                return 1
            else:
                return len(str(value).encode('utf-8'))


class CacheBackendInterface(ABC):
    """Abstract cache backend interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get value from cache"""
        pass
        
    @abstractmethod
    async def set(self, entry: CacheEntry) -> bool:
        """Set value in cache"""
        pass
        
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
        
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
        
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries"""
        pass
        
    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        pass
        
    @abstractmethod
    async def close(self):
        """Close backend connection"""
        pass


class MemoryCacheBackend(CacheBackendInterface):
    """In-memory cache backend"""
    
    def __init__(self, max_size: int = 1000, max_memory: int = 100*1024*1024, 
                 eviction_policy: EvictionPolicy = EvictionPolicy.LRU):
        self.max_size = max_size
        self.max_memory = max_memory
        self.eviction_policy = eviction_policy
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats()
        self._lock = threading.RLock()
        self.access_order: OrderedDict[str, float] = OrderedDict()
        
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get value from memory cache"""
        with self._lock:
            if key not in self.cache:
                self.stats.misses += 1
                return None
                
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.access_order.pop(key, None)
                self.stats.misses += 1
                self.stats.evictions += 1
                self._update_stats()
                return None
                
            # Update access info
            entry.touch()
            self.stats.hits += 1
            
            # Update access order for LRU
            if self.eviction_policy == EvictionPolicy.LRU:
                self.cache.move_to_end(key)
                self.access_order[key] = time.time()
                
            return entry
            
    async def set(self, entry: CacheEntry) -> bool:
        """Set value in memory cache"""
        with self._lock:
            # Check if we need to evict
            await self._ensure_capacity(entry)
            
            # Store entry
            self.cache[entry.key] = entry
            self.access_order[entry.key] = time.time()
            self.stats.sets += 1
            self._update_stats()
            
            return True
            
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.pop(key, None)
                self.stats.deletes += 1
                self._update_stats()
                return True
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        with self._lock:
            if key not in self.cache:
                return False
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.access_order.pop(key, None)
                self.stats.evictions += 1
                self._update_stats()
                return False
            return True
            
    async def clear(self) -> bool:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self._update_stats()
            return True
            
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self.stats
        
    async def close(self):
        """Close memory cache"""
        await self.clear()
        
    async def _ensure_capacity(self, new_entry: CacheEntry):
        """Ensure cache has capacity for new entry"""
        # Calculate current memory usage
        current_memory = sum(entry.size_bytes for entry in self.cache.values())
        
        # Evict entries if needed
        while (len(self.cache) >= self.max_size or 
               current_memory + new_entry.size_bytes > self.max_memory):
            
            if not self.cache:
                break
                
            # Apply eviction policy
            evicted_key = await self._select_eviction_candidate()
            if evicted_key:
                evicted_entry = self.cache.pop(evicted_key, None)
                self.access_order.pop(evicted_key, None)
                if evicted_entry:
                    current_memory -= evicted_entry.size_bytes
                    self.stats.evictions += 1
            else:
                break
                
    async def _select_eviction_candidate(self) -> Optional[str]:
        """Select candidate for eviction based on policy"""
        if not self.cache:
            return None
            
        if self.eviction_policy == EvictionPolicy.LRU:
            # Return least recently used (first in OrderedDict)
            return next(iter(self.cache))
            
        elif self.eviction_policy == EvictionPolicy.LFU:
            # Return least frequently used
            return min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            
        elif self.eviction_policy == EvictionPolicy.FIFO:
            # Return first inserted (oldest created_at)
            return min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            
        elif self.eviction_policy == EvictionPolicy.TTL:
            # Return entry with earliest expiration
            candidates = [k for k in self.cache.keys() if self.cache[k].expires_at]
            if candidates:
                return min(candidates, key=lambda k: self.cache[k].expires_at)
            else:
                return next(iter(self.cache))  # Fallback to FIFO
                
        elif self.eviction_policy == EvictionPolicy.RANDOM:
            import random
            return random.choice(list(self.cache.keys()))
            
        return next(iter(self.cache))  # Default fallback
        
    def _update_stats(self):
        """Update cache statistics"""
        self.stats.entries_count = len(self.cache)
        self.stats.size_bytes = sum(entry.size_bytes for entry in self.cache.values())


class RedisCacheBackend(CacheBackendInterface):
    """Redis cache backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 prefix: str = "ainflue:", db: int = 0):
        self.redis_url = redis_url
        self.prefix = prefix
        self.db = db
        self.redis = None
        self.stats = CacheStats()
        
    async def _ensure_connection(self):
        """Ensure Redis connection"""
        if self.redis is None:
            try:
                import aioredis
                self.redis = await aioredis.from_url(self.redis_url, db=self.db)
            except ImportError:
                logger.error("aioredis library not available")
                raise
                
    def _make_key(self, key: str) -> str:
        """Create prefixed key"""
        return f"{self.prefix}{key}"
        
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get value from Redis"""
        try:
            await self._ensure_connection()
            
            redis_key = self._make_key(key)
            data = await self.redis.get(redis_key)
            
            if data is None:
                self.stats.misses += 1
                return None
                
            # Deserialize entry
            entry_data = json.loads(data)
            entry = CacheEntry(
                key=entry_data['key'],
                value=CacheSerializer.deserialize(
                    entry_data['value'].encode('latin-1'),
                    SerializationFormat(entry_data['serialization_format'])
                ),
                created_at=datetime.fromisoformat(entry_data['created_at']),
                accessed_at=datetime.fromisoformat(entry_data['accessed_at']),
                expires_at=datetime.fromisoformat(entry_data['expires_at']) if entry_data['expires_at'] else None,
                access_count=entry_data['access_count'],
                size_bytes=entry_data['size_bytes'],
                tags=entry_data['tags'],
                serialization_format=SerializationFormat(entry_data['serialization_format'])
            )
            
            # Check expiration
            if entry.is_expired():
                await self.redis.delete(redis_key)
                self.stats.misses += 1
                self.stats.evictions += 1
                return None
                
            # Update access info
            entry.touch()
            self.stats.hits += 1
            
            # Save updated entry back to Redis
            await self._save_entry(entry)
            
            return entry
            
        except Exception as e:
            logger.error(f"Error getting from Redis: {str(e)}")
            self.stats.misses += 1
            return None
            
    async def set(self, entry: CacheEntry) -> bool:
        """Set value in Redis"""
        try:
            await self._ensure_connection()
            await self._save_entry(entry)
            self.stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"Error setting in Redis: {str(e)}")
            return False
            
    async def _save_entry(self, entry: CacheEntry):
        """Save entry to Redis"""
        redis_key = self._make_key(entry.key)
        
        # Serialize entry
        serialized_value = CacheSerializer.serialize(entry.value, entry.serialization_format)
        entry_data = {
            'key': entry.key,
            'value': serialized_value.decode('latin-1'),  # Store as string
            'created_at': entry.created_at.isoformat(),
            'accessed_at': entry.accessed_at.isoformat(),
            'expires_at': entry.expires_at.isoformat() if entry.expires_at else None,
            'access_count': entry.access_count,
            'size_bytes': entry.size_bytes,
            'tags': entry.tags,
            'serialization_format': entry.serialization_format.value
        }
        
        # Set with expiration if specified
        if entry.expires_at:
            ttl = int((entry.expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis.setex(redis_key, ttl, json.dumps(entry_data))
            else:
                # Already expired, don't store
                return
        else:
            await self.redis.set(redis_key, json.dumps(entry_data))
            
    async def delete(self, key: str) -> bool:
        """Delete value from Redis"""
        try:
            await self._ensure_connection()
            redis_key = self._make_key(key)
            result = await self.redis.delete(redis_key)
            if result > 0:
                self.stats.deletes += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from Redis: {str(e)}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            await self._ensure_connection()
            redis_key = self._make_key(key)
            return await self.redis.exists(redis_key) > 0
        except Exception as e:
            logger.error(f"Error checking existence in Redis: {str(e)}")
            return False
            
    async def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            await self._ensure_connection()
            # Delete all keys with our prefix
            keys = await self.redis.keys(f"{self.prefix}*")
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {str(e)}")
            return False
            
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self.stats
        
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()


class CacheManager:
    """Cache layer manager with intelligent routing"""
    
    def __init__(self, default_ttl: int = 3600, default_format: SerializationFormat = SerializationFormat.PICKLE):
        self.backends: Dict[str, CacheBackendInterface] = {}
        self.default_backend: Optional[str] = None
        self.default_ttl = default_ttl
        self.default_format = default_format
        self.routing_rules: List[Callable[[str], Optional[str]]] = []
        self.stats = CacheStats()
        
    def add_backend(self, name: str, backend: CacheBackendInterface, is_default: bool = False):
        """Add cache backend"""
        self.backends[name] = backend
        if is_default or not self.default_backend:
            self.default_backend = name
        logger.info(f"Added cache backend: {name}")
        
    def add_routing_rule(self, rule: Callable[[str], Optional[str]]):
        """Add routing rule for cache backend selection"""
        self.routing_rules.append(rule)
        
    def _select_backend(self, key: str) -> Optional[CacheBackendInterface]:
        """Select appropriate backend for key"""
        # Apply routing rules
        for rule in self.routing_rules:
            backend_name = rule(key)
            if backend_name and backend_name in self.backends:
                return self.backends[backend_name]
                
        # Use default backend
        if self.default_backend and self.default_backend in self.backends:
            return self.backends[self.default_backend]
            
        # Use any available backend
        if self.backends:
            return next(iter(self.backends.values()))
            
        return None
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        backend = self._select_backend(key)
        if not backend:
            self.stats.misses += 1
            return None
            
        entry = await backend.get(key)
        if entry:
            self.stats.hits += 1
            return entry.value
        else:
            self.stats.misses += 1
            return None
            
    async def set(self, key: str, value: Any, ttl: int = None, 
                  format: SerializationFormat = None, tags: List[str] = None) -> bool:
        """Set value in cache"""
        backend = self._select_backend(key)
        if not backend:
            return False
            
        ttl = ttl if ttl is not None else self.default_ttl
        format = format or self.default_format
        tags = tags or []
        
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl) if ttl > 0 else None
        
        # Calculate size
        size_bytes = CacheSerializer.calculate_size(value, format)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            accessed_at=now,
            expires_at=expires_at,
            size_bytes=size_bytes,
            tags=tags,
            serialization_format=format
        )
        
        success = await backend.set(entry)
        if success:
            self.stats.sets += 1
        return success
        
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        backend = self._select_backend(key)
        if not backend:
            return False
            
        success = await backend.delete(key)
        if success:
            self.stats.deletes += 1
        return success
        
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        backend = self._select_backend(key)
        if not backend:
            return False
        return await backend.exists(key)
        
    async def get_or_set(self, key: str, factory: Callable[[], Any], 
                        ttl: int = None, format: SerializationFormat = None) -> Any:
        """Get value or set it using factory function"""
        value = await self.get(key)
        if value is not None:
            return value
            
        # Generate value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
            
        # Store in cache
        await self.set(key, value, ttl, format)
        return value
        
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        # This is a simplified implementation
        # In a real system, you'd maintain tag indices
        invalidated = 0
        for backend in self.backends.values():
            # This would need backend-specific implementation
            pass
        return invalidated
        
    async def clear_all(self) -> bool:
        """Clear all cache backends"""
        success = True
        for backend in self.backends.values():
            try:
                await backend.clear()
            except Exception as e:
                logger.error(f"Error clearing backend: {str(e)}")
                success = False
        return success
        
    async def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics from all backends"""
        aggregated = {
            'total_hits': self.stats.hits,
            'total_misses': self.stats.misses,
            'total_sets': self.stats.sets,
            'total_deletes': self.stats.deletes,
            'hit_rate': self.stats.hit_rate,
            'backends': {}
        }
        
        for name, backend in self.backends.items():
            try:
                backend_stats = await backend.get_stats()
                aggregated['backends'][name] = backend_stats.to_dict()
            except Exception as e:
                logger.error(f"Error getting stats from backend {name}: {str(e)}")
                
        return aggregated


class CacheService:
    """Distributed Cache Management Service"""
    
    def __init__(self, name: str = "cache_service"):
        self.name = name
        self.cache_manager = CacheManager()
        self.running = False
        self.cleanup_task = None
        self.cleanup_interval = 300  # 5 minutes
        
    async def start(self):
        """Start cache service"""
        self.running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
        
        logger.info(f"Started cache service: {self.name}")
        
    async def stop(self):
        """Stop cache service"""
        self.running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Close all backends
        for backend in self.cache_manager.backends.values():
            await backend.close()
            
        logger.info(f"Stopped cache service: {self.name}")
        
    def add_memory_backend(self, name: str = "memory", max_size: int = 1000, 
                          max_memory: int = 100*1024*1024, 
                          eviction_policy: EvictionPolicy = EvictionPolicy.LRU,
                          is_default: bool = True):
        """Add memory cache backend"""
        backend = MemoryCacheBackend(max_size, max_memory, eviction_policy)
        self.cache_manager.add_backend(name, backend, is_default)
        
    def add_redis_backend(self, name: str = "redis", redis_url: str = "redis://localhost:6379",
                         prefix: str = "ainflue:", db: int = 0, is_default: bool = False):
        """Add Redis cache backend"""
        backend = RedisCacheBackend(redis_url, prefix, db)
        self.cache_manager.add_backend(name, backend, is_default)
        
    def add_routing_rule(self, rule: Callable[[str], Optional[str]]):
        """Add cache routing rule"""
        self.cache_manager.add_routing_rule(rule)
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return await self.cache_manager.get(key)
        
    async def set(self, key: str, value: Any, ttl: int = None, 
                  format: SerializationFormat = None, tags: List[str] = None) -> bool:
        """Set value in cache"""
        return await self.cache_manager.set(key, value, ttl, format, tags)
        
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        return await self.cache_manager.delete(key)
        
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.cache_manager.exists(key)
        
    async def get_or_set(self, key: str, factory: Callable[[], Any], 
                        ttl: int = None, format: SerializationFormat = None) -> Any:
        """Get value or set it using factory function"""
        return await self.cache_manager.get_or_set(key, factory, ttl, format)
        
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        return await self.cache_manager.invalidate_by_tags(tags)
        
    async def clear_all(self) -> bool:
        """Clear all caches"""
        return await self.cache_manager.clear_all()
        
    async def _cleanup_expired_entries(self):
        """Periodically cleanup expired entries"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                # Cleanup logic would go here
                # For now, just log that cleanup ran
                logger.debug("Cache cleanup task executed")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {str(e)}")
                
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "backends_count": len(self.cache_manager.backends),
            "default_backend": self.cache_manager.default_backend,
            "default_ttl": self.cache_manager.default_ttl,
            "cleanup_interval": self.cleanup_interval,
            "backends": list(self.cache_manager.backends.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return await self.cache_manager.get_aggregated_stats()


def create_cache_service(config: Dict[str, Any] = None) -> CacheService:
    """Factory function to create Cache service"""
    config = config or {}
    service_name = config.get('name', 'cache_service')
    
    service = CacheService(service_name)
    
    # Configure default TTL
    if 'default_ttl' in config:
        service.cache_manager.default_ttl = config['default_ttl']
        
    # Configure cleanup interval
    if 'cleanup_interval' in config:
        service.cleanup_interval = config['cleanup_interval']
        
    # Add backends
    if 'backends' in config:
        for backend_config in config['backends']:
            backend_type = backend_config.get('type')
            name = backend_config.get('name', backend_type)
            is_default = backend_config.get('is_default', False)
            
            if backend_type == 'memory':
                service.add_memory_backend(
                    name=name,
                    max_size=backend_config.get('max_size', 1000),
                    max_memory=backend_config.get('max_memory', 100*1024*1024),
                    eviction_policy=EvictionPolicy(backend_config.get('eviction_policy', 'lru')),
                    is_default=is_default
                )
            elif backend_type == 'redis':
                service.add_redis_backend(
                    name=name,
                    redis_url=backend_config.get('redis_url', 'redis://localhost:6379'),
                    prefix=backend_config.get('prefix', 'ainflue:'),
                    db=backend_config.get('db', 0),
                    is_default=is_default
                )
                
    # Add default memory backend if no backends configured
    if not service.cache_manager.backends:
        service.add_memory_backend()
        
    return service


__all__ = [
    'CacheService', 'CacheManager', 'CacheEntry', 'CacheStats',
    'CacheBackend', 'EvictionPolicy', 'SerializationFormat',
    'MemoryCacheBackend', 'RedisCacheBackend',
    'create_cache_service'
]