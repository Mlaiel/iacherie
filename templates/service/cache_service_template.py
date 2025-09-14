"""{{service_name}} Cache Service for Ainflue Platform
{{service_description}}

Enterprise-grade distributed caching service with Redis, Memcached, and in-memory support,
cache warming, invalidation strategies, and performance optimization.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: Backend Senior + Caching Architect
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import time
import hashlib
import pickle
import zlib
from dataclasses import dataclass

import aioredis
import aiomcache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import orjson

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError, CacheError
from models.cache import (
    CacheEntry, CacheNamespace, CacheStatistics, 
    CacheInvalidation, WarmupTask
)
from services.analytics_service import AnalyticsService
from utils.validation import validate_cache_data
from utils.serialization import serialize_data, deserialize_data
from monitoring.cache_metrics import CacheMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheBackend(Enum):
    """Cache backend types"""
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"
    MULTI_TIER = "multi_tier"


class CacheStrategy(Enum):
    """Cache replacement strategies"""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    FIFO = "fifo"         # First In First Out
    TTL = "ttl"           # Time To Live
    RANDOM = "random"     # Random replacement


class SerializationFormat(Enum):
    """Serialization formats"""
    JSON = "json"
    PICKLE = "pickle"
    ORJSON = "orjson"
    MSGPACK = "msgpack"
    ZLIB_JSON = "zlib_json"


class InvalidationPattern(Enum):
    """Cache invalidation patterns"""
    TTL = "ttl"                    # Time-based expiration
    TAG_BASED = "tag_based"        # Tag-based invalidation
    EVENT_DRIVEN = "event_driven"  # Event-triggered
    WRITE_THROUGH = "write_through" # Write-through invalidation
    MANUAL = "manual"              # Manual invalidation


class CacheLevel(Enum):
    """Cache hierarchy levels"""
    L1 = 1    # In-memory (fastest)
    L2 = 2    # Redis (fast)
    L3 = 3    # Memcached (medium)
    L4 = 4    # Database (slowest)


@dataclass
class CacheConfig:
    """Cache configuration"""
    backend: CacheBackend
    strategy: CacheStrategy
    serialization: SerializationFormat
    default_ttl: int = 3600
    max_size: Optional[int] = None
    compression: bool = False
    namespace: str = "default"


# Pydantic Models for Request/Response
class CacheSetRequest(BaseModel):
    """Request model for setting cache values"""
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Value to cache")
    ttl: Optional[int] = Field(None, description="Time to live in seconds")
    namespace: str = Field("default", description="Cache namespace")
    tags: Optional[List[str]] = Field(default_factory=list, description="Cache tags")
    compression: Optional[bool] = Field(None, description="Enable compression")
    serialization: Optional[SerializationFormat] = Field(None, description="Serialization format")

    @validator('key')
    def validate_key(cls, v) -> None:
        if not v or len(v.strip()) == 0:
            raise ValueError('Cache key cannot be empty')
        return v.strip()


class CacheGetRequest(BaseModel):
    """Request model for getting cache values"""
    key: str = Field(..., description="Cache key")
    namespace: str = Field("default", description="Cache namespace")
    default: Optional[Any] = Field(None, description="Default value if not found")


class CacheDeleteRequest(BaseModel):
    """Request model for deleting cache values"""
    key: Optional[str] = Field(None, description="Specific cache key")
    pattern: Optional[str] = Field(None, description="Key pattern for bulk delete")
    namespace: Optional[str] = Field(None, description="Namespace to clear")
    tags: Optional[List[str]] = Field(None, description="Tags to invalidate")


class WarmupRequest(BaseModel):
    """Request model for cache warming"""
    namespace: str = Field(..., description="Namespace to warm")
    keys: Optional[List[str]] = Field(None, description="Specific keys to warm")
    data_source: str = Field(..., description="Data source function/method")
    priority: int = Field(5, description="Warmup priority (1-10)")
    parallel_workers: int = Field(1, description="Number of parallel workers")

    @validator('priority')
    def validate_priority(cls, v) -> None:
        if v < 1 or v > 10:
            raise ValueError('Priority must be between 1 and 10')
        return v


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics"""
    namespace: str = Field(..., description="Cache namespace")
    total_keys: int = Field(..., description="Total number of keys")
    memory_usage: int = Field(..., description="Memory usage in bytes")
    hit_rate: float = Field(..., description="Cache hit rate")
    miss_rate: float = Field(..., description="Cache miss rate")
    avg_ttl: float = Field(..., description="Average TTL")
    last_updated: datetime = Field(..., description="Last update time")


class {{service_class_name}}(BaseService):
    """
    Enterprise Cache Service for Ainflue Platform
    
    Handles comprehensive caching management including:
    - Multi-backend support (Redis, Memcached, In-memory)
    - Multi-tier caching architecture
    - Cache warming and preloading
    - Tag-based invalidation
    - Compression and serialization
    - Performance monitoring and analytics
    - Automatic cleanup and eviction
    - Distributed cache coordination
    - Cache-aside and write-through patterns
    - Real-time cache statistics
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "{{service_name}}"
        self.version = "{{service_version}}"
        self.redis_client = None
        self.memcached_client = None
        self.memory_cache = {}
        self.metrics_collector = CacheMetricsCollector()
        
        # Cache configurations by namespace
        self.namespace_configs = {}
        
        # Cache statistics tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        
        # Background task tracking
        self.warmup_tasks = {}
        self.cleanup_running = False
        
        # Default configuration
        self.default_config = CacheConfig(
            backend=CacheBackend.REDIS,
            strategy=CacheStrategy.LRU,
            serialization=SerializationFormat.ORJSON,
            default_ttl=3600,
            compression=False
        )
        
        # Serialization handlers
        self.serializers = {
            SerializationFormat.JSON: (json.dumps, json.loads),
            SerializationFormat.ORJSON: (orjson.dumps, orjson.loads),
            SerializationFormat.PICKLE: (pickle.dumps, pickle.loads),
            SerializationFormat.ZLIB_JSON: (
                lambda x: zlib.compress(json.dumps(x).encode()),
                lambda x: json.loads(zlib.decompress(x).decode())
            )
        }

    async def initialize(self) -> None:
        """Initialize service with dependencies"""
        try:
            await super().initialize()
            
            # Initialize Redis client
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Handle binary data
                retry_on_timeout=True,
                max_connections=20
            )
            
            # Initialize Memcached client if configured
            if hasattr(settings, 'MEMCACHED_SERVERS') and settings.MEMCACHED_SERVERS:
                self.memcached_client = aiomcache.Client(
                    settings.MEMCACHED_SERVERS,
                    pool_size=10
                )
            
            # Initialize metrics collection
            await self.metrics_collector.initialize()
            
            # Load namespace configurations
            await self._load_namespace_configs()
            
            # Start background workers
            asyncio.create_task(self._cleanup_worker())
            asyncio.create_task(self._stats_collector_worker())
            asyncio.create_task(self._warmup_scheduler())
            
            self.cleanup_running = True
            
            logger.info(f"{self.name} service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} service: {e}")
            raise ServiceException(f"Service initialization failed: {e}")

    async def set(
        self,
        request: CacheSetRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Set a value in cache
        
        Args:
            request: Cache set request
            session: Database session
            
        Returns:
            Set operation result
        """
        try:
            # Get namespace configuration
            config = await self._get_namespace_config(request.namespace)
            
            # Generate cache key
            cache_key = self._generate_cache_key(request.key, request.namespace)
            
            # Prepare value for caching
            cached_value = await self._prepare_cache_value(
                request.value,
                config,
                request.compression,
                request.serialization
            )
            
            # Calculate TTL
            ttl = request.ttl or config.default_ttl
            
            # Set in appropriate backend(s)
            if config.backend == CacheBackend.MULTI_TIER:
                await self._set_multi_tier(cache_key, cached_value, ttl, config)
            else:
                await self._set_single_backend(cache_key, cached_value, ttl, config)
            
            # Store metadata
            await self._store_cache_metadata(
                cache_key,
                request.namespace,
                request.tags,
                ttl,
                session
            )
            
            # Update statistics
            self.stats['sets'] += 1
            await self.metrics_collector.record_cache_set(
                namespace=request.namespace,
                key=request.key,
                size=len(str(cached_value)),
                ttl=ttl
            )
            
            logger.debug(f"Cache set: {cache_key}")
            
            return {
                "success": True,
                "key": request.key,
                "namespace": request.namespace,
                "ttl": ttl,
                "size": len(str(cached_value)),
                "cached_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            await self.metrics_collector.record_error("cache_set", str(e))
            raise ServiceException(f"Cache set failed: {e}")

    async def get(
        self,
        request: CacheGetRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get a value from cache
        
        Args:
            request: Cache get request
            session: Database session
            
        Returns:
            Cached value or default
        """
        try:
            # Get namespace configuration
            config = await self._get_namespace_config(request.namespace)
            
            # Generate cache key
            cache_key = self._generate_cache_key(request.key, request.namespace)
            
            # Get from appropriate backend(s)
            if config.backend == CacheBackend.MULTI_TIER:
                cached_value = await self._get_multi_tier(cache_key, config)
            else:
                cached_value = await self._get_single_backend(cache_key, config)
            
            if cached_value is not None:
                # Cache hit
                value = await self._deserialize_cache_value(cached_value, config)
                
                # Update access time and statistics
                await self._update_access_time(cache_key)
                self.stats['hits'] += 1
                
                await self.metrics_collector.record_cache_hit(
                    namespace=request.namespace,
                    key=request.key
                )
                
                logger.debug(f"Cache hit: {cache_key}")
                
                return {
                    "found": True,
                    "value": value,
                    "key": request.key,
                    "namespace": request.namespace,
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            else:
                # Cache miss
                self.stats['misses'] += 1
                
                await self.metrics_collector.record_cache_miss(
                    namespace=request.namespace,
                    key=request.key
                )
                
                logger.debug(f"Cache miss: {cache_key}")
                
                return {
                    "found": False,
                    "value": request.default,
                    "key": request.key,
                    "namespace": request.namespace,
                    "retrieved_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            await self.metrics_collector.record_error("cache_get", str(e))
            raise ServiceException(f"Cache get failed: {e}")

    async def delete(
        self,
        request: CacheDeleteRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Delete cache entries
        
        Args:
            request: Cache delete request
            session: Database session
            
        Returns:
            Delete operation result
        """
        try:
            deleted_count = 0
            
            if request.key:
                # Delete specific key
                cache_key = self._generate_cache_key(request.key, request.namespace or "default")
                deleted = await self._delete_from_backends(cache_key)
                if deleted:
                    deleted_count = 1
                    
            elif request.pattern:
                # Delete by pattern
                deleted_count = await self._delete_by_pattern(
                    request.pattern, 
                    request.namespace or "default"
                )
                
            elif request.namespace:
                # Delete entire namespace
                deleted_count = await self._delete_namespace(request.namespace)
                
            elif request.tags:
                # Delete by tags
                deleted_count = await self._delete_by_tags(request.tags, session)
            
            # Update statistics
            self.stats['deletes'] += deleted_count
            await self.metrics_collector.record_cache_delete(
                namespace=request.namespace or "default",
                count=deleted_count
            )
            
            logger.info(f"Cache delete: {deleted_count} entries removed")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            await self.metrics_collector.record_error("cache_delete", str(e))
            raise ServiceException(f"Cache delete failed: {e}")

    async def warm_cache(
        self,
        request: WarmupRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Warm cache with data
        
        Args:
            request: Warmup request
            session: Database session
            
        Returns:
            Warmup operation result
        """
        try:
            # Create warmup task
            task_id = str(uuid.uuid4())
            
            async with self.get_session(session) as db_session:
                warmup_task = WarmupTask(
                    id=task_id,
                    namespace=request.namespace,
                    data_source=request.data_source,
                    keys=json.dumps(request.keys) if request.keys else None,
                    priority=request.priority,
                    parallel_workers=request.parallel_workers,
                    status="queued",
                    created_at=datetime.utcnow()
                )
                
                db_session.add(warmup_task)
                await db_session.commit()
            
            # Start warmup process
            asyncio.create_task(self._execute_warmup(task_id, request))
            
            logger.info(f"Cache warmup started: {task_id}")
            
            return {
                "success": True,
                "task_id": task_id,
                "namespace": request.namespace,
                "status": "queued",
                "started_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start cache warmup: {e}")
            raise ServiceException(f"Cache warmup failed: {e}")

    async def get_stats(
        self,
        namespace: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Union[CacheStatsResponse, List[CacheStatsResponse]]:
        """
        Get cache statistics
        
        Args:
            namespace: Optional specific namespace
            session: Database session
            
        Returns:
            Cache statistics
        """
        try:
            if namespace:
                # Get stats for specific namespace
                stats = await self._get_namespace_stats(namespace)
                return CacheStatsResponse(**stats)
            else:
                # Get stats for all namespaces
                all_stats = []
                
                # Get all namespaces
                async with self.get_session(session) as db_session:
                    result = await db_session.execute(
                        select(CacheNamespace.name).distinct()
                    )
                    namespaces = [row[0] for row in result.fetchall()]
                
                for ns in namespaces:
                    stats = await self._get_namespace_stats(ns)
                    all_stats.append(CacheStatsResponse(**stats))
                
                return all_stats
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            raise ServiceException(f"Cache stats failed: {e}")

    # Backend-specific operations
    async def _set_single_backend(
        self,
        cache_key -> None: str,
        value -> None: bytes,
        ttl -> None: int,
        config -> None: CacheConfig
    ) -> None:
        """Set value in single backend"""
        if config.backend == CacheBackend.REDIS:
            await self.redis_client.setex(cache_key, ttl, value)
        elif config.backend == CacheBackend.MEMCACHED and self.memcached_client:
            await self.memcached_client.set(cache_key.encode(), value, exptime=ttl)
        elif config.backend == CacheBackend.MEMORY:
            self.memory_cache[cache_key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'accessed_at': time.time()
            }

    async def _get_single_backend(
        self,
        cache_key: str,
        config: CacheConfig
    ) -> Optional[bytes]:
        """Get value from single backend"""
        if config.backend == CacheBackend.REDIS:
            return await self.redis_client.get(cache_key)
        elif config.backend == CacheBackend.MEMCACHED and self.memcached_client:
            value = await self.memcached_client.get(cache_key.encode())
            return value
        elif config.backend == CacheBackend.MEMORY:
            entry = self.memory_cache.get(cache_key)
            if entry and entry['expires_at'] > time.time():
                entry['accessed_at'] = time.time()
                return entry['value']
            elif entry:
                # Expired
                del self.memory_cache[cache_key]
        
        return None

    async def _set_multi_tier(
        self,
        cache_key -> None: str,
        value -> None: bytes,
        ttl -> None: int,
        config -> None: CacheConfig
    ) -> None:
        """Set value in multi-tier cache"""
        # Set in all tiers
        tasks = []
        
        # L1: Memory (fastest)
        if len(value) <= 1024:  # Only cache small values in memory
            self.memory_cache[cache_key] = {
                'value': value,
                'expires_at': time.time() + min(ttl, 300),  # Max 5 minutes in memory
                'accessed_at': time.time()
            }
        
        # L2: Redis
        tasks.append(self.redis_client.setex(cache_key, ttl, value))
        
        # L3: Memcached (if available)
        if self.memcached_client:
            tasks.append(
                self.memcached_client.set(cache_key.encode(), value, exptime=ttl)
            )
        
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _get_multi_tier(
        self,
        cache_key: str,
        config: CacheConfig
    ) -> Optional[bytes]:
        """Get value from multi-tier cache"""
        # Try L1: Memory first
        memory_entry = self.memory_cache.get(cache_key)
        if memory_entry and memory_entry['expires_at'] > time.time():
            memory_entry['accessed_at'] = time.time()
            return memory_entry['value']
        elif memory_entry:
            del self.memory_cache[cache_key]
        
        # Try L2: Redis
        value = await self.redis_client.get(cache_key)
        if value:
            # Promote to L1 if small
            if len(value) <= 1024:
                self.memory_cache[cache_key] = {
                    'value': value,
                    'expires_at': time.time() + 300,  # 5 minutes
                    'accessed_at': time.time()
                }
            return value
        
        # Try L3: Memcached
        if self.memcached_client:
            value = await self.memcached_client.get(cache_key.encode())
            if value:
                # Promote to upper tiers
                asyncio.create_task(
                    self.redis_client.setex(cache_key, 3600, value)
                )
                if len(value) <= 1024:
                    self.memory_cache[cache_key] = {
                        'value': value,
                        'expires_at': time.time() + 300,
                        'accessed_at': time.time()
                    }
                return value
        
        return None

    async def _prepare_cache_value(
        self,
        value: Any,
        config: CacheConfig,
        compression: Optional[bool] = None,
        serialization: Optional[SerializationFormat] = None
    ) -> bytes:
        """Prepare value for caching"""
        # Choose serialization format
        format_to_use = serialization or config.serialization
        
        # Serialize value
        if format_to_use in self.serializers:
            serializer, _ = self.serializers[format_to_use]
            serialized = serializer(value)
        else:
            serialized = pickle.dumps(value)
        
        # Convert to bytes if necessary
        if isinstance(serialized, str):
            serialized = serialized.encode('utf-8')
        
        # Apply compression if enabled
        use_compression = compression if compression is not None else config.compression
        if use_compression and len(serialized) > 1024:  # Only compress larger values
            serialized = zlib.compress(serialized)
        
        return serialized

    async def _deserialize_cache_value(
        self,
        cached_value: bytes,
        config: CacheConfig
    ) -> Any:
        """Deserialize cached value"""
        try:
            # Try decompression first
            try:
                decompressed = zlib.decompress(cached_value)
                cached_value = decompressed
            except:
                # Not compressed or different compression
                pass
            
            # Try different serialization formats
            for format_type, (_, deserializer) in self.serializers.items():
                try:
                    if format_type == config.serialization:
                        if isinstance(cached_value, bytes) and format_type in [
                            SerializationFormat.JSON, SerializationFormat.ORJSON
                        ]:
                            cached_value = cached_value.decode('utf-8')
                        return deserializer(cached_value)
                except:
                    continue
            
            # Fallback to pickle
            return pickle.loads(cached_value)
            
        except Exception as e:
            logger.error(f"Failed to deserialize cache value: {e}")
            raise ServiceException(f"Cache deserialization failed: {e}")

    async def _generate_cache_key(self, key: str, namespace: str) -> str:
        """Generate namespaced cache key"""
        return f"{namespace}:{key}"

    async def _get_namespace_config(self, namespace: str) -> CacheConfig:
        """Get configuration for namespace"""
        return self.namespace_configs.get(namespace, self.default_config)

    async def _store_cache_metadata(
        self,
        cache_key -> None: str,
        namespace -> None: str,
        tags -> None: Optional[List[str]],
        ttl -> None: int,
        session -> None: Optional[AsyncSession]
    ) -> None:
        """Store cache metadata"""
        if session:
            try:
                cache_entry = CacheEntry(
                    id=str(uuid.uuid4()),
                    cache_key=cache_key,
                    namespace=namespace,
                    tags=json.dumps(tags) if tags else None,
                    ttl=ttl,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                    accessed_at=datetime.utcnow()
                )
                
                session.add(cache_entry)
                await session.commit()
                
            except Exception as e:
                logger.warning(f"Failed to store cache metadata: {e}")

    async def _update_access_time(self, cache_key -> None: str) -> None:
        """Update access time for cache entry"""
        try:
            async with self.get_session() as session:
                await session.execute(
                    update(CacheEntry)
                    .where(CacheEntry.cache_key == cache_key)
                    .values(accessed_at=datetime.utcnow())
                )
                await session.commit()
        except Exception as e:
            logger.debug(f"Failed to update access time: {e}")

    async def _delete_from_backends(self, cache_key: str) -> bool:
        """Delete from all backends"""
        deleted = False
        
        # Delete from memory
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            deleted = True
        
        # Delete from Redis
        if self.redis_client:
            result = await self.redis_client.delete(cache_key)
            if result > 0:
                deleted = True
        
        # Delete from Memcached
        if self.memcached_client:
            try:
                await self.memcached_client.delete(cache_key.encode())
                deleted = True
            except:
                pass
        
        return deleted

    async def _delete_by_pattern(self, pattern: str, namespace: str) -> int:
        """Delete keys by pattern"""
        full_pattern = f"{namespace}:{pattern}"
        deleted_count = 0
        
        # Redis pattern deletion
        if self.redis_client:
            keys = await self.redis_client.keys(full_pattern)
            if keys:
                deleted_count += await self.redis_client.delete(*keys)
        
        # Memory cache pattern deletion
        matching_keys = [
            key for key in self.memory_cache.keys() 
            if key.startswith(f"{namespace}:") and pattern in key
        ]
        for key in matching_keys:
            del self.memory_cache[key]
            deleted_count += 1
        
        return deleted_count

    async def _delete_namespace(self, namespace: str) -> int:
        """Delete entire namespace"""
        return await self._delete_by_pattern("*", namespace)

    async def _delete_by_tags(
        self,
        tags: List[str],
        session: Optional[AsyncSession]
    ) -> int:
        """Delete cache entries by tags"""
        if not session:
            return 0
        
        try:
            # Find cache entries with matching tags
            result = await session.execute(
                select(CacheEntry.cache_key).where(
                    CacheEntry.tags.isnot(None)
                )
            )
            entries = result.fetchall()
            
            keys_to_delete = []
            for entry in entries:
                entry_tags = json.loads(entry.tags or "[]")
                if any(tag in entry_tags for tag in tags):
                    keys_to_delete.append(entry.cache_key)
            
            # Delete from backends
            deleted_count = 0
            for cache_key in keys_to_delete:
                if await self._delete_from_backends(cache_key):
                    deleted_count += 1
            
            # Delete metadata
            await session.execute(
                delete(CacheEntry).where(
                    CacheEntry.cache_key.in_(keys_to_delete)
                )
            )
            await session.commit()
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete by tags: {e}")
            return 0

    async def _execute_warmup(self, task_id -> None: str, request -> None: WarmupRequest) -> None:
        """Execute cache warmup task"""
        try:
            # Update task status
            async with self.get_session() as session:
                await session.execute(
                    update(WarmupTask)
                    .where(WarmupTask.id == task_id)
                    .values(
                        status="running",
                        started_at=datetime.utcnow()
                    )
                )
                await session.commit()
            
            # Get data source function
            # This would be implemented based on your data source registry
            # For now, we'll simulate the warmup process
            
            keys_warmed = 0
            total_keys = len(request.keys) if request.keys else 100
            
            # Simulate warmup with parallel workers
            semaphore = asyncio.Semaphore(request.parallel_workers)
            
            async def warm_key(key -> None: str) -> None:
                nonlocal keys_warmed
                async with semaphore:
                    try:
                        # Simulate data loading and caching
                        await asyncio.sleep(0.1)  # Simulate work
                        
                        # This would call your actual data source
                        # value = await self.data_sources[request.data_source](key)
                        # await self.set(CacheSetRequest(
                        #     key=key,
                        #     value=value,
                        #     namespace=request.namespace
                        # ))
                        
                        keys_warmed += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to warm key {key}: {e}")
            
            # Process keys
            if request.keys:
                tasks = [warm_key(key) for key in request.keys]
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update task completion
            async with self.get_session() as session:
                await session.execute(
                    update(WarmupTask)
                    .where(WarmupTask.id == task_id)
                    .values(
                        status="completed",
                        completed_at=datetime.utcnow(),
                        keys_warmed=keys_warmed
                    )
                )
                await session.commit()
            
            logger.info(f"Cache warmup completed: {task_id}, {keys_warmed} keys warmed")
            
        except Exception as e:
            logger.error(f"Cache warmup failed: {e}")
            
            # Update task with error
            async with self.get_session() as session:
                await session.execute(
                    update(WarmupTask)
                    .where(WarmupTask.id == task_id)
                    .values(
                        status="failed",
                        completed_at=datetime.utcnow(),
                        error_message=str(e)
                    )
                )
                await session.commit()

    async def _get_namespace_stats(self, namespace: str) -> Dict[str, Any]:
        """Get statistics for a namespace"""
        try:
            # Count keys in Redis
            pattern = f"{namespace}:*"
            keys = await self.redis_client.keys(pattern) if self.redis_client else []
            total_keys = len(keys)
            
            # Calculate memory usage
            memory_usage = 0
            if keys:
                for key in keys[:100]:  # Sample first 100 keys
                    try:
                        size = await self.redis_client.memory_usage(key)
                        if size:
                            memory_usage += size
                    except:
                        pass
                
                # Extrapolate for all keys
                if len(keys) > 100:
                    memory_usage = int(memory_usage * (len(keys) / 100))
            
            # Get hit/miss rates from metrics
            hit_rate, miss_rate = await self.metrics_collector.get_hit_miss_rates(namespace)
            
            # Calculate average TTL
            avg_ttl = 0
            if keys:
                ttl_sum = 0
                ttl_count = 0
                for key in keys[:50]:  # Sample
                    try:
                        ttl = await self.redis_client.ttl(key)
                        if ttl > 0:
                            ttl_sum += ttl
                            ttl_count += 1
                    except:
                        pass
                
                if ttl_count > 0:
                    avg_ttl = ttl_sum / ttl_count
            
            return {
                "namespace": namespace,
                "total_keys": total_keys,
                "memory_usage": memory_usage,
                "hit_rate": hit_rate,
                "miss_rate": miss_rate,
                "avg_ttl": avg_ttl,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get namespace stats: {e}")
            return {
                "namespace": namespace,
                "total_keys": 0,
                "memory_usage": 0,
                "hit_rate": 0.0,
                "miss_rate": 0.0,
                "avg_ttl": 0.0,
                "last_updated": datetime.utcnow()
            }

    async def _load_namespace_configs(self) -> None:
        """Load namespace configurations"""
        try:
            async with self.get_session() as session:
                result = await session.execute(select(CacheNamespace))
                namespaces = result.scalars().all()
                
                for ns in namespaces:
                    config_data = json.loads(ns.config) if ns.config else {}
                    self.namespace_configs[ns.name] = CacheConfig(
                        backend=CacheBackend(config_data.get('backend', 'redis')),
                        strategy=CacheStrategy(config_data.get('strategy', 'lru')),
                        serialization=SerializationFormat(config_data.get('serialization', 'orjson')),
                        default_ttl=config_data.get('default_ttl', 3600),
                        max_size=config_data.get('max_size'),
                        compression=config_data.get('compression', False),
                        namespace=ns.name
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to load namespace configs: {e}")

    # Background workers
    async def _cleanup_worker(self) -> None:
        """Background worker for cache cleanup"""
        while self.cleanup_running:
            try:
                # Clean expired entries from memory cache
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.memory_cache.items()
                    if entry['expires_at'] <= current_time
                ]
                
                for key in expired_keys:
                    del self.memory_cache[key]
                    self.stats['evictions'] += 1
                
                # Clean up metadata for expired entries
                async with self.get_session() as session:
                    await session.execute(
                        delete(CacheEntry).where(
                            CacheEntry.expires_at <= datetime.utcnow()
                        )
                    )
                    await session.commit()
                
                # Implement LRU eviction for memory cache if it's too large
                if len(self.memory_cache) > 10000:  # Max 10k entries in memory
                    # Sort by access time and remove oldest
                    sorted_items = sorted(
                        self.memory_cache.items(),
                        key=lambda x: x[1]['accessed_at']
                    )
                    
                    keys_to_remove = [item[0] for item in sorted_items[:1000]]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                        self.stats['evictions'] += 1
                
                await asyncio.sleep(60)  # Clean every minute
                
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                await asyncio.sleep(60)

    async def _stats_collector_worker(self) -> None:
        """Background worker for collecting cache statistics"""
        while self.cleanup_running:
            try:
                # Collect and store statistics
                async with self.get_session() as session:
                    for namespace in self.namespace_configs.keys():
                        stats = await self._get_namespace_stats(namespace)
                        
                        cache_stats = CacheStatistics(
                            id=str(uuid.uuid4()),
                            namespace=namespace,
                            total_keys=stats['total_keys'],
                            memory_usage=stats['memory_usage'],
                            hit_rate=stats['hit_rate'],
                            miss_rate=stats['miss_rate'],
                            avg_ttl=stats['avg_ttl'],
                            collected_at=datetime.utcnow()
                        )
                        
                        session.add(cache_stats)
                    
                    await session.commit()
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                logger.error(f"Stats collector error: {e}")
                await asyncio.sleep(300)

    async def _warmup_scheduler(self) -> None:
        """Background scheduler for warmup tasks"""
        while self.cleanup_running:
            try:
                # Check for pending warmup tasks
                async with self.get_session() as session:
                    result = await session.execute(
                        select(WarmupTask).where(
                            WarmupTask.status == "queued"
                        ).order_by(WarmupTask.priority.desc(), WarmupTask.created_at)
                    )
                    tasks = result.scalars().all()
                    
                    for task in tasks[:5]:  # Process up to 5 tasks
                        if task.id not in self.warmup_tasks:
                            # Start warmup task
                            warmup_request = WarmupRequest(
                                namespace=task.namespace,
                                keys=json.loads(task.keys) if task.keys else None,
                                data_source=task.data_source,
                                priority=task.priority,
                                parallel_workers=task.parallel_workers
                            )
                            
                            task_coroutine = asyncio.create_task(
                                self._execute_warmup(task.id, warmup_request)
                            )
                            self.warmup_tasks[task.id] = task_coroutine
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Warmup scheduler error: {e}")
                await asyncio.sleep(30)

    async def flush_cache(
        self,
        namespace: Optional[str] = None,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Flush cache (use with caution)
        
        Args:
            namespace: Optional namespace to flush
            confirm: Confirmation flag
            
        Returns:
            Flush operation result
        """
        if not confirm:
            raise ValidationError("Cache flush requires confirmation")
        
        try:
            flushed_count = 0
            
            if namespace:
                # Flush specific namespace
                flushed_count = await self._delete_namespace(namespace)
            else:
                # Flush all caches
                if self.redis_client:
                    await self.redis_client.flushdb()
                
                if self.memcached_client:
                    await self.memcached_client.flush_all()
                
                self.memory_cache.clear()
                
                # Clean metadata
                async with self.get_session() as session:
                    result = await session.execute(select(func.count(CacheEntry.id)))
                    flushed_count = result.scalar() or 0
                    
                    await session.execute(delete(CacheEntry))
                    await session.commit()
            
            logger.warning(f"Cache flushed: {flushed_count} entries removed")
            
            return {
                "success": True,
                "flushed_count": flushed_count,
                "namespace": namespace,
                "flushed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to flush cache: {e}")
            raise ServiceException(f"Cache flush failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = await super().health_check()
            
            # Check Redis connectivity
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = "healthy"
            
            # Check Memcached connectivity
            if self.memcached_client:
                try:
                    await self.memcached_client.version()
                    health_status["memcached"] = "healthy"
                except:
                    health_status["memcached"] = "unhealthy"
            
            # Cache statistics
            health_status["cache_stats"] = {
                "memory_entries": len(self.memory_cache),
                "hit_rate": self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0,
                "operations": {
                    "hits": self.stats['hits'],
                    "misses": self.stats['misses'],
                    "sets": self.stats['sets'],
                    "deletes": self.stats['deletes'],
                    "evictions": self.stats['evictions']
                }
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup(self) -> None:
        """Cleanup service resources"""
        try:
            self.cleanup_running = False
            
            # Cancel warmup tasks
            for task_id, task in self.warmup_tasks.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Close connections
            if self.redis_client:
                await self.redis_client.close()
            
            if self.memcached_client:
                await self.memcached_client.close()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
                
            await super().cleanup()
            logger.info(f"{self.name} service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {self.name} service: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def main() -> None:
        service = {{service_class_name}}()
        await service.initialize()
        
        try:
            # Set cache value
            set_request = CacheSetRequest(
                key="user:123",
                value={"name": "John Doe", "email": "john@example.com"},
                ttl=3600,
                namespace="users",
                tags=["user", "profile"]
            )
            
            set_result = await service.set(set_request)
            print(f"Cache set: {set_result}")
            
            # Get cache value
            get_request = CacheGetRequest(
                key="user:123",
                namespace="users"
            )
            
            get_result = await service.get(get_request)
            print(f"Cache get: {get_result}")
            
            # Get cache statistics
            stats = await service.get_stats("users")
            print(f"Cache stats: {stats}")
            
            # Start cache warmup
            warmup_request = WarmupRequest(
                namespace="users",
                data_source="load_user_data",
                keys=["user:1", "user:2", "user:3"],
                parallel_workers=2
            )
            
            warmup_result = await service.warm_cache(warmup_request)
            print(f"Cache warmup: {warmup_result}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await service.cleanup()

    asyncio.run(main())

# File has syntax issues - needs manual review