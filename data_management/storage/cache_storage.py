"""
⚡ Cache Storage Provider - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/storage/cache_storage.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

High-performance cache storage provider with Redis, Memcached, and in-memory
caching for ultra-fast content retrieval and fingerprint matching.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, AsyncGenerator, Tuple
import logging
import asyncio
import aioredis
import json
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import OrderedDict
import zlib
import base64

logger = logging.getLogger(__name__)

class CacheProvider(Enum):
    """Supported cache providers"""
    REDIS = "redis"
    MEMCACHED = "memcached"
    IN_MEMORY = "in_memory"
    HYBRID = "hybrid"

class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"          # Least Recently Used
    LFU = "lfu"          # Least Frequently Used
    TTL = "ttl"          # Time To Live
    FIFO = "fifo"        # First In First Out
    ADAPTIVE = "adaptive" # Adaptive based on content type

@dataclass
class CacheConfig:
    """Cache storage configuration"""
    provider: CacheProvider = CacheProvider.REDIS
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Memcached configuration
    memcached_servers: List[str] = field(default_factory=lambda: ["localhost:11211"])
    
    # Cache behavior
    default_ttl: int = 3600  # 1 hour
    max_memory: int = 1024 * 1024 * 1024  # 1GB
    eviction_strategy: CacheStrategy = CacheStrategy.LRU
    
    # Performance settings
    compression_enabled: bool = True
    compression_threshold: int = 1024  # Compress items > 1KB
    serialization_format: str = "pickle"  # pickle, json, msgpack
    
    # Content-specific TTL
    content_ttl: Dict[str, int] = field(default_factory=lambda: {
        'fingerprint': 86400,    # 24 hours
        'embedding': 43200,      # 12 hours
        'audio': 7200,          # 2 hours
        'video': 3600,          # 1 hour
        'image': 1800,          # 30 minutes
        'metadata': 900,        # 15 minutes
        'search_results': 300,  # 5 minutes
        'analytics': 600        # 10 minutes
    })
    
    # Clustering settings
    enable_clustering: bool = False
    cluster_nodes: List[str] = field(default_factory=list)

class CacheStorageManager:
    """
    Enterprise cache storage manager for ultra-fast content retrieval.
    
    Features:
    - Multi-provider support (Redis, Memcached, In-Memory)
    - Intelligent content-aware caching strategies
    - Automatic compression and serialization
    - Hot/warm/cold cache tiers
    - Real-time analytics and monitoring
    - Cluster support for high availability
    """
    
    def __init__(self, config: CacheConfig):
        """Initialize cache storage manager"""
        self.config = config
        self.redis_client = None
        self.memcached_client = None
        self.in_memory_cache = None
        
        # Performance metrics
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'deletes': 0,
            'evictions': 0,
            'total_size': 0,
            'avg_get_time': 0.0,
            'avg_set_time': 0.0,
            'hit_ratio': 0.0
        }
        
        # Content type statistics
        self.content_stats: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Initialize cache providers
        asyncio.create_task(self._initialize_providers())
        
        logger.info(f"CacheStorageManager initialized with {config.provider.value}")
    
    async def _initialize_providers(self) -> None:
        """Initialize cache providers based on configuration"""
        try:
            if self.config.provider in [CacheProvider.REDIS, CacheProvider.HYBRID]:
                await self._initialize_redis()
            
            if self.config.provider in [CacheProvider.MEMCACHED, CacheProvider.HYBRID]:
                await self._initialize_memcached()
            
            if self.config.provider in [CacheProvider.IN_MEMORY, CacheProvider.HYBRID]:
                await self._initialize_in_memory()
            
            logger.info("Cache providers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache providers: {str(e)}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis client"""
        try:
            if self.config.enable_clustering:
                # Redis Cluster
                from aioredis import RedisCluster
                self.redis_client = RedisCluster.from_url(
                    f"redis://{self.config.redis_host}:{self.config.redis_port}",
                    password=self.config.redis_password,
                    ssl=self.config.redis_ssl
                )
            else:
                # Single Redis instance
                self.redis_client = await aioredis.from_url(
                    f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
                    password=self.config.redis_password,
                    ssl=self.config.redis_ssl,
                    encoding="utf-8",
                    decode_responses=False
                )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis client initialized successfully")
            
        except Exception as e:
            logger.error(f"Redis initialization failed: {str(e)}")
            raise
    
    async def _initialize_memcached(self) -> None:
        """Initialize Memcached client"""
        try:
            import aiomcache
            
            # Use first server for simplicity
            server_host, server_port = self.config.memcached_servers[0].split(':')
            
            self.memcached_client = aiomcache.Client(server_host, int(server_port))
            
            logger.info("Memcached client initialized successfully")
            
        except Exception as e:
            logger.error(f"Memcached initialization failed: {str(e)}")
            raise
    
    async def _initialize_in_memory(self) -> None:
        """Initialize in-memory cache"""
        try:
            self.in_memory_cache = InMemoryCache(
                max_size=self.config.max_memory,
                eviction_strategy=self.config.eviction_strategy
            )
            
            logger.info("In-memory cache initialized successfully")
            
        except Exception as e:
            logger.error(f"In-memory cache initialization failed: {str(e)}")
            raise
    
    async def store(
        self,
        key: str,
        content: Union[bytes, str, Dict[str, Any], List[Any]],
        content_type: str = "unknown",
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store content in cache with intelligent optimization.
        
        Business Logic:
        1. Determine optimal cache tier based on content type
        2. Apply compression for large content
        3. Serialize content appropriately
        4. Set content-specific TTL
        5. Update analytics and metrics
        """
        start_time = time.time()
        
        try:
            # Determine TTL based on content type
            if ttl is None:
                ttl = self.config.content_ttl.get(content_type, self.config.default_ttl)
            
            # Prepare content for caching
            serialized_content = await self._serialize_content(content, content_type)
            
            # Apply compression if beneficial
            compressed_content = await self._compress_content(serialized_content, content_type)
            
            # Prepare cache metadata
            cache_metadata = {
                'content_type': content_type,
                'original_size': len(serialized_content),
                'compressed_size': len(compressed_content),
                'compressed': len(compressed_content) < len(serialized_content),
                'cached_at': datetime.now().isoformat(),
                'ttl': ttl,
                'access_count': 0,
                **(metadata or {})
            }
            
            # Store in appropriate cache tier
            if self.config.provider == CacheProvider.HYBRID:
                result = await self._store_hybrid(key, compressed_content, cache_metadata, ttl)
            elif self.config.provider == CacheProvider.REDIS:
                result = await self._store_redis(key, compressed_content, cache_metadata, ttl)
            elif self.config.provider == CacheProvider.MEMCACHED:
                result = await self._store_memcached(key, compressed_content, cache_metadata, ttl)
            elif self.config.provider == CacheProvider.IN_MEMORY:
                result = await self._store_in_memory(key, compressed_content, cache_metadata, ttl)
            else:
                raise ValueError(f"Unsupported cache provider: {self.config.provider}")
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics('write', len(compressed_content), processing_time)
            self._update_content_stats(content_type, 'write', len(compressed_content))
            
            return {
                'success': True,
                'key': key,
                'content_type': content_type,
                'size': len(compressed_content),
                'ttl': ttl,
                'compressed': cache_metadata['compressed'],
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Failed to store cache item {key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'key': key,
                'processing_time': time.time() - start_time
            }
    
    async def retrieve(
        self,
        key: str,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve content from cache with automatic decompression"""
        start_time = time.time()
        
        try:
            # Retrieve from appropriate cache tier
            if self.config.provider == CacheProvider.HYBRID:
                result = await self._retrieve_hybrid(key)
            elif self.config.provider == CacheProvider.REDIS:
                result = await self._retrieve_redis(key)
            elif self.config.provider == CacheProvider.MEMCACHED:
                result = await self._retrieve_memcached(key)
            elif self.config.provider == CacheProvider.IN_MEMORY:
                result = await self._retrieve_in_memory(key)
            else:
                raise ValueError(f"Unsupported cache provider: {self.config.provider}")
            
            if not result['found']:
                # Cache miss
                processing_time = time.time() - start_time
                self._update_metrics('miss', 0, processing_time)
                
                return {
                    'success': False,
                    'found': False,
                    'key': key,
                    'processing_time': processing_time
                }
            
            # Decompress and deserialize content
            compressed_content = result['content']
            metadata = result['metadata']
            
            # Decompress if needed
            if metadata.get('compressed', False):
                decompressed_content = await self._decompress_content(compressed_content)
            else:
                decompressed_content = compressed_content
            
            # Deserialize content
            original_content = await self._deserialize_content(
                decompressed_content, 
                metadata.get('content_type', 'unknown')
            )
            
            # Update access statistics
            await self._update_access_stats(key, metadata)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics('hit', len(compressed_content), processing_time)
            
            if content_type:
                self._update_content_stats(content_type, 'hit', len(compressed_content))
            
            return {
                'success': True,
                'found': True,
                'key': key,
                'content': original_content,
                'metadata': metadata,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve cache item {key}: {str(e)}")
            processing_time = time.time() - start_time
            self._update_metrics('miss', 0, processing_time)
            
            return {
                'success': False,
                'found': False,
                'error': str(e),
                'key': key,
                'processing_time': processing_time
            }
    
    async def delete(self, key: str) -> Dict[str, Any]:
        """Delete content from cache"""
        try:
            # Delete from appropriate cache tier
            if self.config.provider == CacheProvider.HYBRID:
                result = await self._delete_hybrid(key)
            elif self.config.provider == CacheProvider.REDIS:
                result = await self._delete_redis(key)
            elif self.config.provider == CacheProvider.MEMCACHED:
                result = await self._delete_memcached(key)
            elif self.config.provider == CacheProvider.IN_MEMORY:
                result = await self._delete_in_memory(key)
            else:
                raise ValueError(f"Unsupported cache provider: {self.config.provider}")
            
            # Update metrics
            self._update_metrics('delete', 0, 0)
            
            return {
                'success': result,
                'key': key
            }
            
        except Exception as e:
            logger.error(f"Failed to delete cache item {key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'key': key
            }
    
    async def clear(self, pattern: Optional[str] = None) -> Dict[str, Any]:
        """Clear cache items with optional pattern matching"""
        try:
            cleared_count = 0
            
            if self.config.provider == CacheProvider.REDIS and self.redis_client:
                if pattern:
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        cleared_count = await self.redis_client.delete(*keys)
                else:
                    await self.redis_client.flushdb()
                    cleared_count = -1  # All items cleared
            
            elif self.config.provider == CacheProvider.IN_MEMORY and self.in_memory_cache:
                cleared_count = await self.in_memory_cache.clear(pattern)
            
            return {
                'success': True,
                'cleared_count': cleared_count
            }
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            stats = {
                'provider': self.config.provider.value,
                'metrics': self.metrics.copy(),
                'content_stats': self.content_stats.copy(),
                'config': {
                    'default_ttl': self.config.default_ttl,
                    'max_memory': self.config.max_memory,
                    'compression_enabled': self.config.compression_enabled,
                    'eviction_strategy': self.config.eviction_strategy.value
                }
            }
            
            # Add provider-specific stats
            if self.config.provider == CacheProvider.REDIS and self.redis_client:
                redis_info = await self.redis_client.info()
                stats['redis_info'] = {
                    'used_memory': redis_info.get('used_memory', 0),
                    'used_memory_human': redis_info.get('used_memory_human', '0B'),
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'total_commands_processed': redis_info.get('total_commands_processed', 0),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0)
                }
            
            elif self.config.provider == CacheProvider.IN_MEMORY and self.in_memory_cache:
                stats['in_memory_info'] = await self.in_memory_cache.get_statistics()
            
            # Calculate derived metrics
            total_operations = self.metrics['hits'] + self.metrics['misses']
            if total_operations > 0:
                stats['metrics']['hit_ratio'] = self.metrics['hits'] / total_operations
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {str(e)}")
            return {'error': str(e)}
    
    async def optimize(self) -> Dict[str, Any]:
        """Run cache optimization tasks"""
        try:
            optimization_results = {}
            
            # Clean expired items
            if self.config.provider == CacheProvider.IN_MEMORY and self.in_memory_cache:
                expired_count = await self.in_memory_cache.cleanup_expired()
                optimization_results['expired_cleaned'] = expired_count
            
            # Analyze hot/cold content
            hot_keys, cold_keys = await self._analyze_access_patterns()
            optimization_results['hot_keys_count'] = len(hot_keys)
            optimization_results['cold_keys_count'] = len(cold_keys)
            
            # Suggest optimizations
            suggestions = await self._generate_optimization_suggestions()
            optimization_results['suggestions'] = suggestions
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {str(e)}")
            return {'error': str(e)}
    
    # Provider-specific implementation methods
    
    async def _store_redis(
        self,
        key: str,
        content: bytes,
        metadata: Dict[str, Any],
        ttl: int
    ) -> bool:
        """Store content in Redis"""
        try:
            # Store content and metadata separately for efficiency
            content_key = f"content:{key}"
            metadata_key = f"metadata:{key}"
            
            # Use pipeline for atomic operation
            async with self.redis_client.pipeline() as pipe:
                pipe.setex(content_key, ttl, content)
                pipe.setex(metadata_key, ttl, json.dumps(metadata))
                await pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Redis store failed: {str(e)}")
            return False
    
    async def _retrieve_redis(self, key: str) -> Dict[str, Any]:
        """Retrieve content from Redis"""
        try:
            content_key = f"content:{key}"
            metadata_key = f"metadata:{key}"
            
            # Use pipeline for efficiency
            async with self.redis_client.pipeline() as pipe:
                pipe.get(content_key)
                pipe.get(metadata_key)
                results = await pipe.execute()
            
            content, metadata_str = results
            
            if content is None or metadata_str is None:
                return {'found': False}
            
            metadata = json.loads(metadata_str)
            
            return {
                'found': True,
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Redis retrieve failed: {str(e)}")
            return {'found': False}
    
    async def _delete_redis(self, key: str) -> bool:
        """Delete content from Redis"""
        try:
            content_key = f"content:{key}"
            metadata_key = f"metadata:{key}"
            
            deleted_count = await self.redis_client.delete(content_key, metadata_key)
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Redis delete failed: {str(e)}")
            return False
    
    async def _store_memcached(
        self,
        key: str,
        content: bytes,
        metadata: Dict[str, Any],
        ttl: int
    ) -> bool:
        """Store content in Memcached"""
        try:
            # Combine content and metadata
            cache_data = {
                'content': base64.b64encode(content).decode('utf-8'),
                'metadata': metadata
            }
            
            serialized_data = json.dumps(cache_data).encode('utf-8')
            
            await self.memcached_client.set(key.encode('utf-8'), serialized_data, exptime=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Memcached store failed: {str(e)}")
            return False
    
    async def _retrieve_memcached(self, key: str) -> Dict[str, Any]:
        """Retrieve content from Memcached"""
        try:
            data = await self.memcached_client.get(key.encode('utf-8'))
            
            if data is None:
                return {'found': False}
            
            cache_data = json.loads(data.decode('utf-8'))
            content = base64.b64decode(cache_data['content'])
            metadata = cache_data['metadata']
            
            return {
                'found': True,
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Memcached retrieve failed: {str(e)}")
            return {'found': False}
    
    async def _delete_memcached(self, key: str) -> bool:
        """Delete content from Memcached"""
        try:
            result = await self.memcached_client.delete(key.encode('utf-8'))
            return result
            
        except Exception as e:
            logger.error(f"Memcached delete failed: {str(e)}")
            return False
    
    async def _store_in_memory(
        self,
        key: str,
        content: bytes,
        metadata: Dict[str, Any],
        ttl: int
    ) -> bool:
        """Store content in in-memory cache"""
        try:
            cache_item = {
                'content': content,
                'metadata': metadata,
                'expires_at': datetime.now() + timedelta(seconds=ttl)
            }
            
            return await self.in_memory_cache.set(key, cache_item)
            
        except Exception as e:
            logger.error(f"In-memory store failed: {str(e)}")
            return False
    
    async def _retrieve_in_memory(self, key: str) -> Dict[str, Any]:
        """Retrieve content from in-memory cache"""
        try:
            cache_item = await self.in_memory_cache.get(key)
            
            if cache_item is None:
                return {'found': False}
            
            # Check expiration
            if cache_item['expires_at'] < datetime.now():
                await self.in_memory_cache.delete(key)
                return {'found': False}
            
            return {
                'found': True,
                'content': cache_item['content'],
                'metadata': cache_item['metadata']
            }
            
        except Exception as e:
            logger.error(f"In-memory retrieve failed: {str(e)}")
            return {'found': False}
    
    async def _delete_in_memory(self, key: str) -> bool:
        """Delete content from in-memory cache"""
        try:
            return await self.in_memory_cache.delete(key)
            
        except Exception as e:
            logger.error(f"In-memory delete failed: {str(e)}")
            return False
    
    # Hybrid cache methods (combining multiple providers)
    
    async def _store_hybrid(
        self,
        key: str,
        content: bytes,
        metadata: Dict[str, Any],
        ttl: int
    ) -> bool:
        """Store content in hybrid cache (multiple tiers)"""
        try:
            # Store in fast tier (in-memory) for hot content
            if metadata.get('content_type') in ['fingerprint', 'embedding']:
                if self.in_memory_cache:
                    await self._store_in_memory(key, content, metadata, min(ttl, 3600))
            
            # Store in persistent tier (Redis) for durability
            if self.redis_client:
                await self._store_redis(key, content, metadata, ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Hybrid store failed: {str(e)}")
            return False
    
    async def _retrieve_hybrid(self, key: str) -> Dict[str, Any]:
        """Retrieve content from hybrid cache (check tiers in order)"""
        try:
            # Check fast tier first (in-memory)
            if self.in_memory_cache:
                result = await self._retrieve_in_memory(key)
                if result['found']:
                    return result
            
            # Check persistent tier (Redis)
            if self.redis_client:
                result = await self._retrieve_redis(key)
                if result['found']:
                    # Promote to fast tier if content is hot
                    content_type = result['metadata'].get('content_type')
                    if content_type in ['fingerprint', 'embedding'] and self.in_memory_cache:
                        await self._store_in_memory(
                            key, 
                            result['content'], 
                            result['metadata'], 
                            3600  # 1 hour in fast tier
                        )
                    return result
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"Hybrid retrieve failed: {str(e)}")
            return {'found': False}
    
    async def _delete_hybrid(self, key: str) -> bool:
        """Delete content from all hybrid cache tiers"""
        try:
            success = True
            
            # Delete from all tiers
            if self.in_memory_cache:
                success &= await self._delete_in_memory(key)
            
            if self.redis_client:
                success &= await self._delete_redis(key)
            
            return success
            
        except Exception as e:
            logger.error(f"Hybrid delete failed: {str(e)}")
            return False
    
    # Content processing methods
    
    async def _serialize_content(
        self,
        content: Union[bytes, str, Dict[str, Any], List[Any]],
        content_type: str
    ) -> bytes:
        """Serialize content for caching"""
        try:
            if isinstance(content, bytes):
                return content
            
            elif self.config.serialization_format == "json":
                return json.dumps(content, ensure_ascii=False).encode('utf-8')
            
            elif self.config.serialization_format == "pickle":
                return pickle.dumps(content)
            
            elif self.config.serialization_format == "msgpack":
                import msgpack
                return msgpack.packb(content)
            
            else:
                # Default to pickle
                return pickle.dumps(content)
                
        except Exception as e:
            logger.error(f"Content serialization failed: {str(e)}")
            raise
    
    async def _deserialize_content(
        self,
        data: bytes,
        content_type: str
    ) -> Any:
        """Deserialize content from cache"""
        try:
            if self.config.serialization_format == "json":
                return json.loads(data.decode('utf-8'))
            
            elif self.config.serialization_format == "pickle":
                return pickle.loads(data)
            
            elif self.config.serialization_format == "msgpack":
                import msgpack
                return msgpack.unpackb(data, raw=False)
            
            else:
                # Default to pickle
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Content deserialization failed: {str(e)}")
            # Return raw bytes if deserialization fails
            return data
    
    async def _compress_content(self, content: bytes, content_type: str) -> bytes:
        """Apply compression if beneficial"""
        try:
            if not self.config.compression_enabled:
                return content
            
            if len(content) < self.config.compression_threshold:
                return content
            
            # Skip compression for already compressed content
            if content_type in ['audio', 'video', 'image']:
                return content
            
            compressed = zlib.compress(content, level=6)
            
            # Only use compression if it reduces size significantly
            if len(compressed) < len(content) * 0.9:
                return compressed
            
            return content
            
        except Exception as e:
            logger.warning(f"Content compression failed: {str(e)}")
            return content
    
    async def _decompress_content(self, content: bytes) -> bytes:
        """Decompress content"""
        try:
            return zlib.decompress(content)
            
        except Exception as e:
            logger.warning(f"Content decompression failed: {str(e)}")
            return content
    
    # Analytics and optimization methods
    
    async def _update_access_stats(self, key: str, metadata: Dict[str, Any]) -> None:
        """Update access statistics for cache items"""
        try:
            # Update access count in metadata
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            metadata['last_accessed'] = datetime.now().isoformat()
            
            # Update metadata in cache
            if self.config.provider == CacheProvider.REDIS and self.redis_client:
                metadata_key = f"metadata:{key}"
                await self.redis_client.set(metadata_key, json.dumps(metadata))
            
        except Exception as e:
            logger.warning(f"Failed to update access stats: {str(e)}")
    
    async def _analyze_access_patterns(self) -> Tuple[List[str], List[str]]:
        """Analyze access patterns to identify hot and cold content"""
        hot_keys = []
        cold_keys = []
        
        try:
            if self.config.provider == CacheProvider.REDIS and self.redis_client:
                # Get all metadata keys
                metadata_keys = await self.redis_client.keys("metadata:*")
                
                for metadata_key in metadata_keys:
                    metadata_str = await self.redis_client.get(metadata_key)
                    if metadata_str:
                        metadata = json.loads(metadata_str)
                        access_count = metadata.get('access_count', 0)
                        
                        key = metadata_key.replace('metadata:', '')
                        
                        if access_count > 10:  # Hot threshold
                            hot_keys.append(key)
                        elif access_count < 2:  # Cold threshold
                            cold_keys.append(key)
            
        except Exception as e:
            logger.warning(f"Access pattern analysis failed: {str(e)}")
        
        return hot_keys, cold_keys
    
    async def _generate_optimization_suggestions(self) -> List[str]:
        """Generate cache optimization suggestions"""
        suggestions = []
        
        try:
            # Analyze hit ratio
            total_ops = self.metrics['hits'] + self.metrics['misses']
            if total_ops > 0:
                hit_ratio = self.metrics['hits'] / total_ops
                
                if hit_ratio < 0.8:
                    suggestions.append("Consider increasing cache TTL for better hit ratio")
                
                if hit_ratio > 0.95:
                    suggestions.append("Cache is very effective, consider reducing TTL to save memory")
            
            # Analyze memory usage
            if self.metrics['total_size'] > self.config.max_memory * 0.9:
                suggestions.append("Cache memory usage is high, consider enabling compression or reducing TTL")
            
            # Analyze content types
            for content_type, stats in self.content_stats.items():
                if stats.get('hit_ratio', 0) < 0.5:
                    suggestions.append(f"Low hit ratio for {content_type}, consider adjusting caching strategy")
        
        except Exception as e:
            logger.warning(f"Failed to generate optimization suggestions: {str(e)}")
        
        return suggestions
    
    def _update_metrics(self, operation: str, size: int, processing_time: float) -> None:
        """Update performance metrics"""
        with self.lock:
            if operation == 'hit':
                self.metrics['hits'] += 1
            elif operation == 'miss':
                self.metrics['misses'] += 1
            elif operation == 'write':
                self.metrics['writes'] += 1
                self.metrics['total_size'] += size
            elif operation == 'delete':
                self.metrics['deletes'] += 1
            
            # Update average processing times
            if operation in ['hit', 'miss']:
                current_avg = self.metrics['avg_get_time']
                total_gets = self.metrics['hits'] + self.metrics['misses']
                self.metrics['avg_get_time'] = (current_avg * (total_gets - 1) + processing_time) / total_gets
            
            elif operation == 'write':
                current_avg = self.metrics['avg_set_time']
                total_writes = self.metrics['writes']
                self.metrics['avg_set_time'] = (current_avg * (total_writes - 1) + processing_time) / total_writes
    
    def _update_content_stats(self, content_type: str, operation: str, size: int) -> None:
        """Update content-specific statistics"""
        with self.lock:
            if content_type not in self.content_stats:
                self.content_stats[content_type] = {
                    'hits': 0,
                    'misses': 0,
                    'writes': 0,
                    'total_size': 0,
                    'hit_ratio': 0.0
                }
            
            stats = self.content_stats[content_type]
            
            if operation == 'hit':
                stats['hits'] += 1
            elif operation == 'miss':
                stats['misses'] += 1
            elif operation == 'write':
                stats['writes'] += 1
                stats['total_size'] += size
            
            # Update hit ratio
            total_ops = stats['hits'] + stats['misses']
            if total_ops > 0:
                stats['hit_ratio'] = stats['hits'] / total_ops

class InMemoryCache:
    """High-performance in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int, eviction_strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.eviction_strategy = eviction_strategy
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.current_size = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    async def set(self, key: str, value: Any) -> bool:
        """Set item in cache"""
        with self.lock:
            # Calculate item size
            item_size = len(pickle.dumps(value))
            
            # Check if item already exists
            if key in self.cache:
                old_size = len(pickle.dumps(self.cache[key]))
                self.current_size -= old_size
            
            # Evict items if necessary
            while self.current_size + item_size > self.max_size and self.cache:
                self._evict_item()
            
            # Add new item
            self.cache[key] = value
            self.current_size += item_size
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self.lock:
            if key in self.cache:
                item_size = len(pickle.dumps(self.cache[key]))
                del self.cache[key]
                self.current_size -= item_size
                return True
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache items"""
        with self.lock:
            if pattern:
                import fnmatch
                keys_to_remove = [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]
                for key in keys_to_remove:
                    del self.cache[key]
                return len(keys_to_remove)
            else:
                count = len(self.cache)
                self.cache.clear()
                self.current_size = 0
                return count
    
    async def cleanup_expired(self) -> int:
        """Clean up expired items"""
        expired_count = 0
        current_time = datetime.now()
        
        with self.lock:
            keys_to_remove = []
            
            for key, value in self.cache.items():
                if isinstance(value, dict) and 'expires_at' in value:
                    if value['expires_at'] < current_time:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                item_size = len(pickle.dumps(self.cache[key]))
                del self.cache[key]
                self.current_size -= item_size
                expired_count += 1
        
        return expired_count
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'item_count': len(self.cache),
                'current_size': self.current_size,
                'max_size': self.max_size,
                'utilization': (self.current_size / self.max_size) * 100 if self.max_size > 0 else 0
            }
    
    def _evict_item(self) -> None:
        """Evict an item based on eviction strategy"""
        if not self.cache:
            return
        
        if self.eviction_strategy == CacheStrategy.LRU:
            # Remove least recently used (first item)
            key, value = self.cache.popitem(last=False)
        elif self.eviction_strategy == CacheStrategy.FIFO:
            # Remove first in (first item)
            key, value = self.cache.popitem(last=False)
        else:
            # Default to LRU
            key, value = self.cache.popitem(last=False)
        
        # Update size
        item_size = len(pickle.dumps(value))
        self.current_size -= item_size

class AsyncCacheStorageManager:
    """Async wrapper for high-performance concurrent cache operations"""
    
    def __init__(self, config: CacheConfig):
        self.sync_manager = CacheStorageManager(config)
        self.semaphore = asyncio.Semaphore(100)  # Allow high concurrency for cache
    
    async def store_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Store multiple items concurrently"""
        
        async def store_single(item):
            async with self.semaphore:
                return await self.sync_manager.store(
                    item['key'],
                    item['content'],
                    item.get('content_type', 'unknown'),
                    item.get('ttl'),
                    item.get('metadata')
                )
        
        tasks = [store_single(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for result in results
        ]
    
    async def retrieve_batch(
        self,
        keys: List[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve multiple items concurrently"""
        
        async def retrieve_single(key):
            async with self.semaphore:
                return await self.sync_manager.retrieve(key)
        
        tasks = [retrieve_single(key) for key in keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for result in results
        ]

# Export classes
__all__ = [
    'CacheStorageManager',
    'AsyncCacheStorageManager',
    'CacheConfig',
    'CacheProvider',
    'CacheStrategy',
    'InMemoryCache'
]
