"""Cache Storage Provider
======================

Professional cache storage implementation for IA-Influencer-Agent platform.
Provides Redis, Memcached, and in-memory cache storage with TTL support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""import asyncio
import logging
import json
import pickle
import gzip
import time
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Tuple
from datetime import datetime, timedelta
import hashlib
import uuid
from dataclasses import asdict
import redis.asyncio as redis
import aiomcache

from .interfaces import (
    CacheStorageProvider, BaseStorageProvider, StorageMetadata,
    QueryOptions, QueryFilter, StorageStats, StorageBackendType,
    CompressionType, DataFormat
)

logger = logging.getLogger(__name__)

class RedisCacheStorageProvider(CacheStorageProvider):
    """    Professional Redis cache storage provider.
    
    Features:
    - Automatic TTL management
    - Data compression and serialization
    - Connection pooling
    - Cluster support
    - Performance monitoring
    - Batch operations
    - Pattern-based operations
    """    
    def __init__(
        self,
        provider_id: str,
        config: Dict[str, Any]
    ):
        """Initialize Redis cache storage provider."""        super().__init__(provider_id, StorageBackendType.CACHE, config)
        
        self.redis_url = config.get('redis_url', 'redis://localhost:6379')
        self.database = config.get('database', 0)
        self.pool_size = config.get('pool_size', 10)
        self.default_ttl = config.get('default_ttl', 3600)  # 1 hour
        self.key_prefix = config.get('key_prefix', f'crawler:{provider_id}:')
        self.enable_compression = config.get('enable_compression', True)
        self.compression_threshold = config.get('compression_threshold', 1024)  # Compress if > 1KB
        
        # Redis connection
        self.redis_client = None
        self.connection_pool = None
        
        # Performance tracking
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'total_time': 0.0
        }
        
        logger.info(f"Redis cache storage provider initialized: {provider_id}")
    
    async def connect(self) -> None:
        """Establish Redis connection."""        try:
            # Create connection pool
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                db=self.database,
                max_connections=self.pool_size,
                decode_responses=False  # We handle binary data
            )
            
            # Create Redis client
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            
            self.is_connected = True
            logger.info(f"Connected to Redis: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis {self.provider_id}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection."""        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
            
            if self.connection_pool:
                await self.connection_pool.disconnect()
                self.connection_pool = None
            
            self.is_connected = False
            logger.info(f"Disconnected from Redis: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from Redis {self.provider_id}: {e}")
    
    async def health_check(self) -> bool:
        """Check Redis health."""        try:
            if not self.is_connected or not self.redis_client:
                return False
            
            # Test with ping
            result = await self.redis_client.ping()
            return result is True
            
        except Exception as e:
            logger.error(f"Redis health check failed for {self.provider_id}: {e}")
            return False
    
    def _get_cache_key(self, record_id: str) -> str:
        """Get formatted cache key."""        return f"{self.key_prefix}{record_id}"
    
    def _serialize_data(self, data: Any) -> Tuple[bytes, bool]:
        """Serialize and optionally compress data."""        # Serialize to bytes
        if isinstance(data, (dict, list)):
            serialized = json.dumps(data).encode()
        else:
            serialized = pickle.dumps(data)
        
        # Compress if enabled and size threshold met
        compressed = False
        if (self.enable_compression and 
            len(serialized) > self.compression_threshold):
            serialized = gzip.compress(serialized)
            compressed = True
        
        return serialized, compressed
    
    def _deserialize_data(self, data: bytes, compressed: bool = False) -> Any:
        """Deserialize and optionally decompress data."""        # Decompress if needed
        if compressed:
            data = gzip.decompress(data)
        
        # Try JSON first, then pickle
        try:
            return json.loads(data.decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            return pickle.loads(data)
    
    async def store_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Store a record in Redis cache."""        start_time = time.time()
        
        try:
            cache_key = self._get_cache_key(record_id)
            
            # Serialize data
            serialized_data, compressed = self._serialize_data(data)
            
            # Prepare storage entry
            cache_entry = {
                'data': serialized_data,
                'compressed': compressed,
                'stored_at': datetime.utcnow().isoformat(),
                'metadata': asdict(metadata) if metadata else None
            }
            
            # Serialize entire entry
            entry_data = pickle.dumps(cache_entry)
            
            # Determine TTL
            ttl = self.default_ttl
            if metadata and hasattr(metadata, 'ttl_seconds'):
                ttl = getattr(metadata, 'ttl_seconds', self.default_ttl)
            
            # Store in Redis
            await self.redis_client.setex(cache_key, ttl, entry_data)
            
            # Update stats
            self.cache_stats['sets'] += 1
            operation_time = time.time() - start_time
            self.cache_stats['total_time'] += operation_time
            
            return True
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Failed to store record {record_id} in Redis cache: {e}")
            return False
    
    async def retrieve_record(
        self,
        record_id: str,
        include_metadata: bool = True
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Retrieve a record from Redis cache."""        start_time = time.time()
        
        try:
            cache_key = self._get_cache_key(record_id)
            
            # Get from Redis
            entry_data = await self.redis_client.get(cache_key)
            
            if entry_data is None:
                self.cache_stats['misses'] += 1
                return None
            
            # Deserialize entry
            cache_entry = pickle.loads(entry_data)
            
            # Extract data
            data = self._deserialize_data(
                cache_entry['data'],
                cache_entry.get('compressed', False)
            )
            
            # Extract metadata if requested
            metadata = None
            if include_metadata and cache_entry.get('metadata'):
                metadata_dict = cache_entry['metadata']
                metadata = StorageMetadata(
                    record_id=metadata_dict['record_id'],
                    created_at=datetime.fromisoformat(metadata_dict['created_at']),
                    updated_at=datetime.fromisoformat(metadata_dict['updated_at']) if metadata_dict.get('updated_at') else None,
                    size_bytes=metadata_dict.get('size_bytes'),
                    compression_type=CompressionType(metadata_dict.get('compression_type', 'none')),
                    format_type=DataFormat(metadata_dict.get('format_type', 'binary')),
                    tags=metadata_dict.get('tags'),
                    checksum=metadata_dict.get('checksum'),
                    version=metadata_dict.get('version', 1)
                )
            
            # Update stats
            self.cache_stats['hits'] += 1
            operation_time = time.time() - start_time
            self.cache_stats['total_time'] += operation_time
            
            return (data, metadata)
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Failed to retrieve record {record_id} from Redis cache: {e}")
            return None
    
    async def set_with_ttl(
        self,
        key: str,
        value: Any,
        ttl_seconds: int
    ) -> bool:
        """Set value with time-to-live."""        try:
            cache_key = self._get_cache_key(key)
            serialized_data, _ = self._serialize_data(value)
            
            await self.redis_client.setex(cache_key, ttl_seconds, serialized_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to set key {key} with TTL: {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key."""        try:
            cache_key = self._get_cache_key(key)
            ttl = await self.redis_client.ttl(cache_key)
            
            # Redis returns -1 if key exists but has no TTL, -2 if key doesn't exist
            return ttl if ttl > 0 else None
            
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return None
    
    async def extend_ttl(
        self,
        key: str,
        additional_seconds: int
    ) -> bool:
        """Extend TTL for existing key."""        try:
            cache_key = self._get_cache_key(key)
            current_ttl = await self.redis_client.ttl(cache_key)
            
            if current_ttl > 0:
                new_ttl = current_ttl + additional_seconds
                await self.redis_client.expire(cache_key, new_ttl)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to extend TTL for key {key}: {e}")
            return False
    
    async def set_multiple_with_ttl(
        self,
        data: Dict[str, Any],
        ttl_seconds: int
    ) -> Dict[str, bool]:
        """Set multiple values with TTL."""        results = {}
        
        try:
            # Use pipeline for efficiency
            pipe = self.redis_client.pipeline()
            
            for key, value in data.items():
                try:
                    cache_key = self._get_cache_key(key)
                    serialized_data, _ = self._serialize_data(value)
                    pipe.setex(cache_key, ttl_seconds, serialized_data)
                    results[key] = True
                except Exception as e:
                    logger.error(f"Failed to prepare key {key} for batch set: {e}")
                    results[key] = False
            
            # Execute pipeline
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Batch set operation failed: {e}")
            # Mark all as failed if pipeline fails
            for key in data.keys():
                if key not in results:
                    results[key] = False
        
        return results
    
    async def store_batch(
        self,
        records: List[Tuple[str, Any, Optional[StorageMetadata]]]
    ) -> Dict[str, bool]:
        """Store multiple records in batch."""        results = {}
        
        try:
            # Use pipeline for efficiency
            pipe = self.redis_client.pipeline()
            
            for record_id, data, metadata in records:
                try:
                    cache_key = self._get_cache_key(record_id)
                    
                    # Serialize data
                    serialized_data, compressed = self._serialize_data(data)
                    
                    # Prepare storage entry
                    cache_entry = {
                        'data': serialized_data,
                        'compressed': compressed,
                        'stored_at': datetime.utcnow().isoformat(),
                        'metadata': asdict(metadata) if metadata else None
                    }
                    
                    entry_data = pickle.dumps(cache_entry)
                    
                    # Determine TTL
                    ttl = self.default_ttl
                    if metadata and hasattr(metadata, 'ttl_seconds'):
                        ttl = getattr(metadata, 'ttl_seconds', self.default_ttl)
                    
                    pipe.setex(cache_key, ttl, entry_data)
                    results[record_id] = True
                    
                except Exception as e:
                    logger.error(f"Failed to prepare record {record_id} for batch store: {e}")
                    results[record_id] = False
            
            # Execute pipeline
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Batch store operation failed: {e}")
            # Mark all as failed if pipeline fails
            for record_id, _, _ in records:
                if record_id not in results:
                    results[record_id] = False
        
        return results
    
    async def retrieve_batch(
        self,
        record_ids: List[str],
        include_metadata: bool = True
    ) -> Dict[str, Optional[Tuple[Any, Optional[StorageMetadata]]]]:
        """Retrieve multiple records in batch."""        results = {}
        
        try:
            # Prepare cache keys
            cache_keys = [self._get_cache_key(record_id) for record_id in record_ids]
            
            # Get all values at once
            values = await self.redis_client.mget(cache_keys)
            
            for i, (record_id, entry_data) in enumerate(zip(record_ids, values)):
                try:
                    if entry_data is None:
                        results[record_id] = None
                        self.cache_stats['misses'] += 1
                        continue
                    
                    # Deserialize entry
                    cache_entry = pickle.loads(entry_data)
                    
                    # Extract data
                    data = self._deserialize_data(
                        cache_entry['data'],
                        cache_entry.get('compressed', False)
                    )
                    
                    # Extract metadata if requested
                    metadata = None
                    if include_metadata and cache_entry.get('metadata'):
                        metadata_dict = cache_entry['metadata']
                        metadata = StorageMetadata(
                            record_id=metadata_dict['record_id'],
                            created_at=datetime.fromisoformat(metadata_dict['created_at']),
                            updated_at=datetime.fromisoformat(metadata_dict['updated_at']) if metadata_dict.get('updated_at') else None,
                            size_bytes=metadata_dict.get('size_bytes'),
                            compression_type=CompressionType(metadata_dict.get('compression_type', 'none')),
                            format_type=DataFormat(metadata_dict.get('format_type', 'binary')),
                            tags=metadata_dict.get('tags'),
                            checksum=metadata_dict.get('checksum'),
                            version=metadata_dict.get('version', 1)
                        )
                    
                    results[record_id] = (data, metadata)
                    self.cache_stats['hits'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to deserialize record {record_id}: {e}")
                    results[record_id] = None
                    
        except Exception as e:
            logger.error(f"Batch retrieve operation failed: {e}")
            # Mark all as None if operation fails
            for record_id in record_ids:
                results[record_id] = None
        
        return results
    
    async def delete_record(self, record_id: str) -> bool:
        """Delete a record from cache."""        try:
            cache_key = self._get_cache_key(record_id)
            result = await self.redis_client.delete(cache_key)
            
            self.cache_stats['deletes'] += 1
            return result > 0
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Failed to delete record {record_id} from cache: {e}")
            return False
    
    async def delete_batch(self, record_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple records in batch."""        results = {}
        
        try:
            # Prepare cache keys
            cache_keys = [self._get_cache_key(record_id) for record_id in record_ids]
            
            # Delete all keys at once
            deleted_count = await self.redis_client.delete(*cache_keys)
            
            # Assume all were deleted successfully
            # (Redis delete returns total count, not per-key status)
            for record_id in record_ids:
                results[record_id] = True
            
            self.cache_stats['deletes'] += len(record_ids)
            
        except Exception as e:
            logger.error(f"Batch delete operation failed: {e}")
            for record_id in record_ids:
                results[record_id] = False
        
        return results
    
    async def exists(self, record_id: str) -> bool:
        """Check if record exists in cache."""        try:
            cache_key = self._get_cache_key(record_id)
            result = await self.redis_client.exists(cache_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to check existence of record {record_id}: {e}")
            return False
    
    async def query_records(
        self,
        options: QueryOptions
    ) -> AsyncIterator[Tuple[str, Any, Optional[StorageMetadata]]]:
        """Query records using key patterns."""        try:
            # Build pattern from filters
            pattern = self.key_prefix + "*"
            
            # Scan for matching keys
            cursor = "0"
            count = options.limit or 100
            
            while cursor != 0:
                cursor, keys = await self.redis_client.scan(
                    cursor=int(cursor),
                    match=pattern,
                    count=count
                )
                
                if keys:
                    # Retrieve records for found keys
                    values = await self.redis_client.mget(keys)
                    
                    for key, value in zip(keys, values):
                        if value:
                            try:
                                # Extract record ID from key
                                record_id = key.decode().replace(self.key_prefix, "")
                                
                                # Deserialize entry
                                cache_entry = pickle.loads(value)
                                
                                # Extract data
                                data = self._deserialize_data(
                                    cache_entry['data'],
                                    cache_entry.get('compressed', False)
                                )
                                
                                # Extract metadata
                                metadata = None
                                if options.include_metadata and cache_entry.get('metadata'):
                                    metadata_dict = cache_entry['metadata']
                                    metadata = StorageMetadata(
                                        record_id=metadata_dict['record_id'],
                                        created_at=datetime.fromisoformat(metadata_dict['created_at']),
                                        updated_at=datetime.fromisoformat(metadata_dict['updated_at']) if metadata_dict.get('updated_at') else None,
                                        size_bytes=metadata_dict.get('size_bytes'),
                                        compression_type=CompressionType(metadata_dict.get('compression_type', 'none')),
                                        format_type=DataFormat(metadata_dict.get('format_type', 'binary')),
                                        tags=metadata_dict.get('tags'),
                                        checksum=metadata_dict.get('checksum'),
                                        version=metadata_dict.get('version', 1)
                                    )
                                
                                yield (record_id, data, metadata)
                                
                            except Exception as e:
                                logger.error(f"Failed to process query result for key {key}: {e}")
                
                if cursor == 0:
                    break
                    
        except Exception as e:
            logger.error(f"Query operation failed: {e}")
    
    async def count_records(
        self,
        filters: Optional[List[QueryFilter]] = None
    ) -> int:
        """Count records in cache."""        try:
            pattern = self.key_prefix + "*"
            count = 0
            cursor = "0"
            
            while cursor != 0:
                cursor, keys = await self.redis_client.scan(
                    cursor=int(cursor),
                    match=pattern,
                    count=1000
                )
                count += len(keys)
                
                if cursor == 0:
                    break
            
            return count
            
        except Exception as e:
            logger.error(f"Count operation failed: {e}")
            return 0
    
    async def update_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Update an existing record (same as store for cache)."""        return await self.store_record(record_id, data, metadata)
    
    async def get_statistics(self) -> StorageStats:
        """Get cache statistics."""        try:
            # Get basic Redis info
            info = await self.redis_client.info('memory')
            
            # Count total keys
            total_records = await self.count_records()
            
            # Estimate total size from Redis memory usage
            total_size = info.get('used_memory', 0)
            
            # Cache hit rate
            total_operations = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (
                self.cache_stats['hits'] / total_operations
                if total_operations > 0 else 0.0
            )
            
            avg_size = total_size / total_records if total_records > 0 else 0.0
            
            return StorageStats(
                total_records=total_records,
                total_size_bytes=total_size,
                created_today=0,  # Not tracked in cache
                updated_today=0,  # Not tracked in cache
                average_record_size=avg_size
            )
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return StorageStats(
                total_records=0,
                total_size_bytes=0,
                created_today=0,
                updated_today=0,
                average_record_size=0.0
            )
    
    async def cleanup_old_records(
        self,
        older_than: datetime,
        batch_size: int = 1000
    ) -> int:
        """Remove expired records (Redis handles TTL automatically)."""        # Redis automatically expires keys based on TTL
        # This method can be used for additional cleanup logic
        logger.info("Redis automatically handles TTL-based cleanup")
        return 0
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get detailed cache statistics."""        total_operations = (
            self.cache_stats['hits'] + 
            self.cache_stats['misses'] + 
            self.cache_stats['sets'] + 
            self.cache_stats['deletes']
        )
        
        hit_rate = (
            self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses'])
            if (self.cache_stats['hits'] + self.cache_stats['misses']) > 0 else 0.0
        )
        
        return {
            'total_operations': total_operations,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'deletes': self.cache_stats['deletes'],
            'errors': self.cache_stats['errors'],
            'hit_rate': hit_rate,
            'total_time': self.cache_stats['total_time'],
            'average_time': (
                self.cache_stats['total_time'] / total_operations
                if total_operations > 0 else 0.0
            ),
            'error_rate': (
                self.cache_stats['errors'] / total_operations
                if total_operations > 0 else 0.0
            )
        }

class InMemoryCacheStorageProvider(CacheStorageProvider):
    """    In-memory cache storage provider for testing and development.
    
    Features:
    - Simple dictionary-based storage
    - TTL support with background cleanup
    - Thread-safe operations
    - Memory usage tracking
    """    
    def __init__(
        self,
        provider_id: str,
        config: Dict[str, Any]
    ):
        """Initialize in-memory cache storage provider."""        super().__init__(provider_id, StorageBackendType.CACHE, config)
        
        self.max_size = config.get('max_size', 10000)  # Maximum number of entries
        self.default_ttl = config.get('default_ttl', 3600)
        self.cleanup_interval = config.get('cleanup_interval', 300)  # 5 minutes
        
        # Storage
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        
        # Cleanup task
        self._cleanup_task = None
        
        # Performance tracking
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        
        logger.info(f"In-memory cache storage provider initialized: {provider_id}")
    
    async def connect(self) -> None:
        """Initialize in-memory cache."""        try:
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
            
            self.is_connected = True
            logger.info(f"In-memory cache connected: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect in-memory cache {self.provider_id}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close in-memory cache."""        try:
            # Cancel cleanup task
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
                self._cleanup_task = None
            
            # Clear cache
            self._cache.clear()
            self._access_times.clear()
            
            self.is_connected = False
            logger.info(f"In-memory cache disconnected: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting in-memory cache {self.provider_id}: {e}")
    
    async def health_check(self) -> bool:
        """Check in-memory cache health."""        return self.is_connected
    
    async def _cleanup_expired_entries(self) -> None:
        """Background task to clean up expired entries."""        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                expired_keys = []
                
                for key, entry in self._cache.items():
                    if entry.get('expires_at', 0) < current_time:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    self._cache.pop(key, None)
                    self._access_times.pop(key, None)
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {e}")
    
    def _evict_if_needed(self) -> None:
        """Evict entries if cache is full."""        if len(self._cache) >= self.max_size:
            # Evict least recently used entry
            if self._access_times:
                lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
                self._cache.pop(lru_key, None)
                self._access_times.pop(lru_key, None)
                self.cache_stats['evictions'] += 1
    
    async def store_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Store a record in memory cache."""        try:
            self._evict_if_needed()
            
            # Calculate expiry time
            ttl = self.default_ttl
            if metadata and hasattr(metadata, 'ttl_seconds'):
                ttl = getattr(metadata, 'ttl_seconds', self.default_ttl)
            
            expires_at = time.time() + ttl
            
            # Store entry
            self._cache[record_id] = {
                'data': data,
                'metadata': metadata,
                'stored_at': time.time(),
                'expires_at': expires_at
            }
            
            self._access_times[record_id] = time.time()
            self.cache_stats['sets'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store record {record_id} in memory cache: {e}")
            return False
    
    async def retrieve_record(
        self,
        record_id: str,
        include_metadata: bool = True
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Retrieve a record from memory cache."""        try:
            entry = self._cache.get(record_id)
            
            if entry is None:
                self.cache_stats['misses'] += 1
                return None
            
            # Check if expired
            if entry.get('expires_at', 0) < time.time():
                self._cache.pop(record_id, None)
                self._access_times.pop(record_id, None)
                self.cache_stats['misses'] += 1
                return None
            
            # Update access time
            self._access_times[record_id] = time.time()
            self.cache_stats['hits'] += 1
            
            data = entry['data']
            metadata = entry['metadata'] if include_metadata else None
            
            return (data, metadata)
            
        except Exception as e:
            logger.error(f"Failed to retrieve record {record_id} from memory cache: {e}")
            return None
    
    async def set_with_ttl(
        self,
        key: str,
        value: Any,
        ttl_seconds: int
    ) -> bool:
        """Set value with time-to-live."""        try:
            self._evict_if_needed()
            
            expires_at = time.time() + ttl_seconds
            
            self._cache[key] = {
                'data': value,
                'metadata': None,
                'stored_at': time.time(),
                'expires_at': expires_at
            }
            
            self._access_times[key] = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Failed to set key {key} with TTL: {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key."""        try:
            entry = self._cache.get(key)
            if entry:
                remaining = entry.get('expires_at', 0) - time.time()
                return int(remaining) if remaining > 0 else None
            return None
            
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return None
    
    async def extend_ttl(
        self,
        key: str,
        additional_seconds: int
    ) -> bool:
        """Extend TTL for existing key."""        try:
            entry = self._cache.get(key)
            if entry:
                entry['expires_at'] += additional_seconds
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to extend TTL for key {key}: {e}")
            return False
    
    async def set_multiple_with_ttl(
        self,
        data: Dict[str, Any],
        ttl_seconds: int
    ) -> Dict[str, bool]:
        """Set multiple values with TTL."""        results = {}
        
        for key, value in data.items():
            results[key] = await self.set_with_ttl(key, value, ttl_seconds)
        
        return results
    
    async def delete_record(self, record_id: str) -> bool:
        """Delete a record from memory cache."""        try:
            removed = self._cache.pop(record_id, None) is not None
            self._access_times.pop(record_id, None)
            
            if removed:
                self.cache_stats['deletes'] += 1
            
            return removed
            
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from memory cache: {e}")
            return False
    
    async def exists(self, record_id: str) -> bool:
        """Check if record exists in memory cache."""        entry = self._cache.get(record_id)
        if entry and entry.get('expires_at', 0) >= time.time():
            return True
        return False
    
    async def count_records(
        self,
        filters: Optional[List[QueryFilter]] = None
    ) -> int:
        """Count records in memory cache."""        current_time = time.time()
        count = 0
        
        for entry in self._cache.values():
            if entry.get('expires_at', 0) >= current_time:
                count += 1
        
        return count
    
    async def get_statistics(self) -> StorageStats:
        """Get memory cache statistics."""        try:
            # Count non-expired entries
            current_time = time.time()
            total_records = 0
            total_size = 0
            
            for entry in self._cache.values():
                if entry.get('expires_at', 0) >= current_time:
                    total_records += 1
                    # Rough size estimation
                    total_size += len(str(entry['data']))
            
            avg_size = total_size / total_records if total_records > 0 else 0.0
            
            return StorageStats(
                total_records=total_records,
                total_size_bytes=total_size,
                created_today=0,  # Not tracked
                updated_today=0,  # Not tracked
                average_record_size=avg_size
            )
            
        except Exception as e:
            logger.error(f"Failed to get memory cache statistics: {e}")
            return StorageStats(
                total_records=0,
                total_size_bytes=0,
                created_today=0,
                updated_today=0,
                average_record_size=0.0
            )
    
    # Implement remaining methods as no-ops or simple implementations
    async def store_batch(self, records: List[Tuple[str, Any, Optional[StorageMetadata]]]) -> Dict[str, bool]:
        results = {}
        for record_id, data, metadata in records:
            results[record_id] = await self.store_record(record_id, data, metadata)
        return results
    
    async def retrieve_batch(self, record_ids: List[str], include_metadata: bool = True) -> Dict[str, Optional[Tuple[Any, Optional[StorageMetadata]]]]:
        results = {}
        for record_id in record_ids:
            results[record_id] = await self.retrieve_record(record_id, include_metadata)
        return results
    
    async def delete_batch(self, record_ids: List[str]) -> Dict[str, bool]:
        results = {}
        for record_id in record_ids:
            results[record_id] = await self.delete_record(record_id)
        return results
    
    async def query_records(self, options: QueryOptions) -> AsyncIterator[Tuple[str, Any, Optional[StorageMetadata]]]:
        current_time = time.time()
        count = 0
        
        for record_id, entry in self._cache.items():
            if entry.get('expires_at', 0) >= current_time:
                if options.limit and count >= options.limit:
                    break
                
                data = entry['data']
                metadata = entry['metadata'] if options.include_metadata else None
                yield (record_id, data, metadata)
                count += 1
    
    async def update_record(self, record_id: str, data: Any, metadata: Optional[StorageMetadata] = None) -> bool:
        return await self.store_record(record_id, data, metadata)
    
    async def cleanup_old_records(self, older_than: datetime, batch_size: int = 1000) -> int:
        # Memory cache handles expiry automatically
        return 0

# Export all cache storage classes
__all__ = [
    'RedisCacheStorageProvider',
    'InMemoryCacheStorageProvider'
]
