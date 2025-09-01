"""Advanced Cache Manager for IA Influencer Agent Platform
Enterprise-grade cache orchestration with multi-backend support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from concurrent.futures import ThreadPoolExecutor
import redis.asyncio as redis
from redis.cluster import RedisCluster

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheBackend(Enum):
    """Cache backend types"""
    REDIS = "redis"
    REDIS_CLUSTER = "redis_cluster"
    MEMORY = "memory"
    VECTOR = "vector"
    HYBRID = "hybrid"

class CachePolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    FIFO = "fifo"
    RANDOM = "random"

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    backend: CacheBackend = CacheBackend.REDIS
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 100
    
    # Cache behavior
    default_ttl: int = 3600  # 1 hour
    max_memory: int = 1024 * 1024 * 1024  # 1GB
    eviction_policy: CachePolicy = CachePolicy.LRU
    
    # Serialization
    serializer: str = "json"
    compression: bool = True
    
    # Clustering
    cluster_nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Monitoring
    enable_metrics: bool = True
    metrics_interval: int = 60
    
    # Multi-tenant isolation
    tenant_isolation: bool = True
    tenant_prefix: str = "tenant"

class CacheMetadata:
    """Cache entry metadata"""
    def __init__(self, 
                 key: str,
                 size: int,
                 created_at: datetime,
                 accessed_at: datetime,
                 ttl: Optional[int] = None,
                 hit_count: int = 0,
                 tenant_id: Optional[str] = None):
        self.key = key
        self.size = size
        self.created_at = created_at
        self.accessed_at = accessed_at
        self.ttl = ttl
        self.hit_count = hit_count
        self.tenant_id = tenant_id
        
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if not self.ttl:
            return False
        expiry_time = self.created_at + timedelta(seconds=self.ttl)
        return datetime.utcnow() > expiry_time
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'size': self.size,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'ttl': self.ttl,
            'hit_count': self.hit_count,
            'tenant_id': self.tenant_id
        }

class CacheManager(Generic[T]):
    """
    Advanced cache manager with multi-backend support
    Handles cache operations across different storage backends
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._backends: Dict[str, Any] = {}
        self._metadata: Dict[str, CacheMetadata] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._lock = asyncio.Lock()
        
        # Initialize backends
        self._initialize_backends()
        
        # Metrics
        self._metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        logger.info(f"CacheManager initialized with backend: {config.backend}")
    
    def _initialize_backends(self):
        """Initialize cache backends"""
        if self.config.backend == CacheBackend.REDIS:
            self._init_redis()
        elif self.config.backend == CacheBackend.REDIS_CLUSTER:
            self._init_redis_cluster()
        elif self.config.backend == CacheBackend.MEMORY:
            self._init_memory()
        elif self.config.backend == CacheBackend.HYBRID:
            self._init_hybrid()
    
    def _init_redis(self):
        """Initialize Redis backend"""
        try:
            self._backends['redis'] = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                max_connections=self.config.max_connections,
                decode_responses=True
            )
            logger.info("Redis backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def _init_redis_cluster(self):
        """Initialize Redis Cluster backend"""
        try:
            startup_nodes = [
                {"host": node["host"], "port": node["port"]}
                for node in self.config.cluster_nodes
            ]
            self._backends['redis_cluster'] = RedisCluster(
                startup_nodes=startup_nodes,
                password=self.config.password,
                decode_responses=True
            )
            logger.info("Redis Cluster backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis Cluster: {e}")
            raise
    
    def _init_memory(self):
        """Initialize memory backend"""
        from .memory_cache import MemoryCache
        self._backends['memory'] = MemoryCache(
            max_size=self.config.max_memory,
            eviction_policy=self.config.eviction_policy
        )
        logger.info("Memory backend initialized")
    
    def _init_hybrid(self):
        """Initialize hybrid backend (Redis + Memory)"""
        self._init_redis()
        self._init_memory()
        logger.info("Hybrid backend initialized")
    
    def _generate_key(self, key: str, tenant_id: Optional[str] = None) -> str:
        """Generate cache key with tenant isolation"""
        if self.config.tenant_isolation and tenant_id:
            return f"{self.config.tenant_prefix}:{tenant_id}:{key}"
        return key
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage"""
        if self.config.serializer == "json":
            return json.dumps(value, default=str)
        return str(value)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage"""
        if self.config.serializer == "json":
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
    
    async def get(self, 
                  key: str, 
                  tenant_id: Optional[str] = None,
                  default: Optional[T] = None) -> Optional[T]:
        """
        Get value from cache with tenant isolation
        """
        cache_key = self._generate_key(key, tenant_id)
        
        try:
            # Try Redis first for hybrid setup
            if 'redis' in self._backends:
                value = await self._backends['redis'].get(cache_key)
                if value is not None:
                    self._metrics['hits'] += 1
                    await self._update_metadata(cache_key, access=True)
                    return self._deserialize_value(value)
            
            # Try memory cache
            if 'memory' in self._backends:
                value = self._backends['memory'].get(cache_key)
                if value is not None:
                    self._metrics['hits'] += 1
                    await self._update_metadata(cache_key, access=True)
                    return value
            
            self._metrics['misses'] += 1
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            self._metrics['errors'] += 1
            return default
    
    async def set(self, 
                  key: str, 
                  value: T, 
                  ttl: Optional[int] = None,
                  tenant_id: Optional[str] = None) -> bool:
        """
        Set value in cache with optional TTL
        """
        cache_key = self._generate_key(key, tenant_id)
        ttl = ttl or self.config.default_ttl
        
        try:
            serialized_value = self._serialize_value(value)
            
            # Set in Redis
            if 'redis' in self._backends:
                await self._backends['redis'].setex(
                    cache_key, ttl, serialized_value
                )
            
            # Set in memory cache
            if 'memory' in self._backends:
                self._backends['memory'].set(cache_key, value, ttl)
            
            # Update metadata
            await self._update_metadata(
                cache_key, 
                size=len(serialized_value),
                ttl=ttl,
                tenant_id=tenant_id
            )
            
            self._metrics['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            self._metrics['errors'] += 1
            return False
    
    async def delete(self, 
                     key: str, 
                     tenant_id: Optional[str] = None) -> bool:
        """
        Delete key from cache
        """
        cache_key = self._generate_key(key, tenant_id)
        
        try:
            deleted = False
            
            # Delete from Redis
            if 'redis' in self._backends:
                result = await self._backends['redis'].delete(cache_key)
                deleted = deleted or bool(result)
            
            # Delete from memory
            if 'memory' in self._backends:
                result = self._backends['memory'].delete(cache_key)
                deleted = deleted or result
            
            # Remove metadata
            if cache_key in self._metadata:
                del self._metadata[cache_key]
            
            if deleted:
                self._metrics['deletes'] += 1
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            self._metrics['errors'] += 1
            return False
    
    async def exists(self, 
                     key: str, 
                     tenant_id: Optional[str] = None) -> bool:
        """
        Check if key exists in cache
        """
        cache_key = self._generate_key(key, tenant_id)
        
        try:
            # Check Redis
            if 'redis' in self._backends:
                exists = await self._backends['redis'].exists(cache_key)
                if exists:
                    return True
            
            # Check memory
            if 'memory' in self._backends:
                return self._backends['memory'].exists(cache_key)
            
            return False
            
        except Exception as e:
            logger.error(f"Cache exists error for key {cache_key}: {e}")
            return False
    
    async def clear(self, tenant_id: Optional[str] = None) -> bool:
        """
        Clear cache for tenant or all data
        """
        try:
            if tenant_id and self.config.tenant_isolation:
                # Clear tenant-specific data
                pattern = f"{self.config.tenant_prefix}:{tenant_id}:*"
                
                if 'redis' in self._backends:
                    keys = await self._backends['redis'].keys(pattern)
                    if keys:
                        await self._backends['redis'].delete(*keys)
                
                if 'memory' in self._backends:
                    self._backends['memory'].clear_pattern(pattern)
                
                # Clear metadata
                keys_to_remove = [
                    k for k in self._metadata.keys() 
                    if k.startswith(f"{self.config.tenant_prefix}:{tenant_id}:")
                ]
                for key in keys_to_remove:
                    del self._metadata[key]
            else:
                # Clear all data
                if 'redis' in self._backends:
                    await self._backends['redis'].flushdb()
                
                if 'memory' in self._backends:
                    self._backends['memory'].clear()
                
                self._metadata.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    async def _update_metadata(self, 
                              key: str, 
                              size: Optional[int] = None,
                              ttl: Optional[int] = None,
                              tenant_id: Optional[str] = None,
                              access: bool = False):
        """Update cache metadata"""
        async with self._lock:
            now = datetime.utcnow()
            
            if key in self._metadata:
                metadata = self._metadata[key]
                if access:
                    metadata.accessed_at = now
                    metadata.hit_count += 1
            else:
                self._metadata[key] = CacheMetadata(
                    key=key,
                    size=size or 0,
                    created_at=now,
                    accessed_at=now,
                    ttl=ttl,
                    tenant_id=tenant_id
                )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_keys = len(self._metadata)
        total_size = sum(meta.size for meta in self._metadata.values())
        
        return {
            'metrics': self._metrics.copy(),
            'total_keys': total_keys,
            'total_size_bytes': total_size,
            'backend': self.config.backend.value,
            'uptime': datetime.utcnow().isoformat()
        }
    
    async def get_metadata(self, key: str, tenant_id: Optional[str] = None) -> Optional[CacheMetadata]:
        """Get metadata for cache key"""
        cache_key = self._generate_key(key, tenant_id)
        return self._metadata.get(cache_key)
    
    async def cleanup_expired(self) -> int:
        """Cleanup expired cache entries"""
        expired_keys = []
        
        async with self._lock:
            for key, metadata in self._metadata.items():
                if metadata.is_expired:
                    expired_keys.append(key)
        
        # Delete expired keys
        for key in expired_keys:
            if 'redis' in self._backends:
                await self._backends['redis'].delete(key)
            if 'memory' in self._backends:
                self._backends['memory'].delete(key)
            if key in self._metadata:
                del self._metadata[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    async def close(self):
        """Close cache connections"""
        try:
            if 'redis' in self._backends:
                await self._backends['redis'].close()
            
            self._executor.shutdown(wait=True)
            logger.info("Cache manager closed")
            
        except Exception as e:
            logger.error(f"Error closing cache manager: {e}")

# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        config = CacheConfig()
        _cache_manager = CacheManager(config)
    return _cache_manager

async def initialize_cache(config: CacheConfig) -> CacheManager:
    """Initialize global cache manager"""
    global _cache_manager
    _cache_manager = CacheManager(config)
    return _cache_manager
