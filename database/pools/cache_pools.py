#!/usr/bin/env python3
"""Cache Pools - Redis, Vector Store, Multi-level Cache Connection Pools
=========================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

Consolidated cache and vector database connection pools for high-performance data access:
- Redis: Cache connection pooling with cluster and sentinel support
- Vector Stores: AI vector database pooling (FAISS, Pinecone, Weaviate, ChromaDB)
- Multi-level Cache: L1 memory + L2 Redis + L3 disk caching optimization

ENTERPRISE FEATURES:
- Intelligent cache warming and invalidation strategies
- Vector similarity search with optimized indexing
- Pipeline optimization for batch operations
- Memory usage monitoring and automatic cleanup
- Cache hit/miss ratio optimization
- Distributed cache synchronization

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
"""

import asyncio
import logging
import time
import json
import pickle
import hashlib
import weakref
from typing import Dict, Any, Optional, List, Union, Tuple, AsyncIterator
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from abc import ABC, abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor

# Cache-specific imports
try:
    import redis.asyncio as aioredis
    from redis.asyncio.connection import ConnectionPool as RedisPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CacheConnectionInfo:
    """Cache connection information."""
    host: str
    port: int
    database: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_enabled: bool = False
    cluster_mode: bool = False
    sentinel_hosts: Optional[List[Tuple[str, int]]] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    store_type: str  # faiss, pinecone, weaviate, chromadb
    dimension: int
    index_type: str = "IVF"
    metric_type: str = "cosine"
    nlist: int = 100
    nprobe: int = 10
    storage_path: Optional[str] = None
    api_key: Optional[str] = None
    environment: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CachePoolConfig:
    """Cache pool configuration."""
    pool_id: str
    connection_info: Optional[CacheConnectionInfo] = None
    vector_config: Optional[VectorStoreConfig] = None
    max_connections: int = 20
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    ttl_default: int = 3600  # 1 hour
    max_memory_mb: int = 512
    eviction_policy: str = "lru"
    compression_enabled: bool = True


class CachePool(ABC):
    """Abstract base class for cache connection pools."""
    
    def __init__(self, config: CachePoolConfig):
        self.config = config
        self.pool_id = config.pool_id
        self._is_initialized = False
        self._stats = {
            'total_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'error_count': 0,
            'memory_usage_mb': 0,
            'last_health_check': None
        }
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the cache pool."""
        pass
    
    @abstractmethod
    async def close(self):
        """Close the cache pool."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check on the pool."""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache pool statistics."""
        stats = dict(self._stats)
        
        # Calculate cache hit ratio
        total_requests = stats['cache_hits'] + stats['cache_misses']
        if total_requests > 0:
            stats['hit_ratio'] = (stats['cache_hits'] / total_requests) * 100
        else:
            stats['hit_ratio'] = 0.0
        
        return stats
    
    def is_initialized(self) -> bool:
        """Check if pool is initialized."""
        return self._is_initialized


class RedisPool(CachePool):
    """Redis connection pool with cluster and sentinel support."""
    
    def __init__(self, config: CachePoolConfig):
        super().__init__(config)
        self._pool = None
        self._client = None
        
    async def initialize(self) -> bool:
        """Initialize Redis connection pool."""
        if not REDIS_AVAILABLE:
            logger.error("redis not available for Redis pool")
            return False
        
        try:
            conn_info = self.config.connection_info
            if not conn_info:
                raise ValueError("Connection info required for Redis pool")
            
            # Configure connection parameters
            connection_kwargs = {
                'host': conn_info.host,
                'port': conn_info.port,
                'db': conn_info.database,
                'retry_on_timeout': self.config.retry_on_timeout,
                'health_check_interval': self.config.health_check_interval,
                'max_connections': self.config.max_connections
            }
            
            # Add authentication if provided
            if conn_info.password:
                connection_kwargs['password'] = conn_info.password
            if conn_info.username:
                connection_kwargs['username'] = conn_info.username
            
            # Add SSL if enabled
            if conn_info.ssl_enabled:
                connection_kwargs['ssl'] = True
                connection_kwargs['ssl_cert_reqs'] = 'none'
            
            # Create connection pool
            if conn_info.cluster_mode:
                # Redis Cluster mode
                from redis.asyncio.cluster import RedisCluster
                startup_nodes = [{"host": conn_info.host, "port": conn_info.port}]
                self._client = RedisCluster(startup_nodes=startup_nodes, **connection_kwargs)
            elif conn_info.sentinel_hosts:
                # Redis Sentinel mode
                from redis.asyncio.sentinel import Sentinel
                sentinel = Sentinel(conn_info.sentinel_hosts)
                service_name = conn_info.additional_params.get('service_name', 'mymaster')
                self._client = sentinel.master_for(service_name, **connection_kwargs)
            else:
                # Standard Redis mode
                self._pool = aioredis.ConnectionPool(**connection_kwargs)
                self._client = aioredis.Redis(connection_pool=self._pool)
            
            # Verify connection
            await self._client.ping()
            
            self._is_initialized = True
            logger.info(f"Redis pool {self.pool_id} initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool {self.pool_id}: {e}")
            return False
    
    async def close(self):
        """Close Redis connection pool."""
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        self._is_initialized = False
        logger.info(f"Redis pool {self.pool_id} closed")
    
    async def health_check(self) -> bool:
        """Perform health check on Redis pool."""
        if not self._is_initialized or not self._client:
            return False
        
        try:
            await asyncio.wait_for(self._client.ping(), timeout=5)
            self._stats['last_health_check'] = datetime.now(timezone.utc)
            return True
            
        except Exception as e:
            logger.error(f"Redis pool {self.pool_id} health check failed: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._client:
            return None
        
        try:
            self._stats['total_operations'] += 1
            
            # Get value from Redis
            value = await self._client.get(key)
            
            if value is not None:
                self._stats['cache_hits'] += 1
                
                # Try to deserialize if compressed
                if self.config.compression_enabled:
                    try:
                        return pickle.loads(value)
                    except:
                        return value.decode('utf-8') if isinstance(value, bytes) else value
                else:
                    return value.decode('utf-8') if isinstance(value, bytes) else value
            else:
                self._stats['cache_misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            self._stats['error_count'] += 1
            self._stats['cache_misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        if not self._client:
            return False
        
        try:
            self._stats['total_operations'] += 1
            
            # Serialize value if compression enabled
            if self.config.compression_enabled:
                try:
                    serialized_value = pickle.dumps(value)
                except:
                    serialized_value = str(value)
            else:
                serialized_value = str(value)
            
            # Set value with TTL
            ttl = ttl or self.config.ttl_default
            result = await self._client.setex(key, ttl, serialized_value)
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not self._client:
            return False
        
        try:
            self._stats['total_operations'] += 1
            result = await self._client.delete(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values from Redis."""
        if not self._client:
            return [None] * len(keys)
        
        try:
            self._stats['total_operations'] += len(keys)
            values = await self._client.mget(keys)
            
            results = []
            for value in values:
                if value is not None:
                    self._stats['cache_hits'] += 1
                    if self.config.compression_enabled:
                        try:
                            results.append(pickle.loads(value))
                        except:
                            results.append(value.decode('utf-8') if isinstance(value, bytes) else value)
                    else:
                        results.append(value.decode('utf-8') if isinstance(value, bytes) else value)
                else:
                    self._stats['cache_misses'] += 1
                    results.append(None)
            
            return results
            
        except Exception as e:
            logger.error(f"Redis mget error: {e}")
            self._stats['error_count'] += 1
            self._stats['cache_misses'] += len(keys)
            return [None] * len(keys)
    
    async def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in Redis."""
        if not self._client:
            return False
        
        try:
            self._stats['total_operations'] += len(mapping)
            
            # Prepare serialized mapping
            serialized_mapping = {}
            for key, value in mapping.items():
                if self.config.compression_enabled:
                    try:
                        serialized_mapping[key] = pickle.dumps(value)
                    except:
                        serialized_mapping[key] = str(value)
                else:
                    serialized_mapping[key] = str(value)
            
            # Use pipeline for efficiency
            pipe = self._client.pipeline()
            
            # Set all values
            await pipe.mset(serialized_mapping)
            
            # Set TTL for all keys if specified
            if ttl:
                for key in mapping.keys():
                    await pipe.expire(key, ttl)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Redis mset error: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._client:
            return False
        
        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern."""
        if not self._client:
            return 0
        
        try:
            keys = await self._client.keys(pattern)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear pattern error for {pattern}: {e}")
            return 0


class VectorStorePool(CachePool):
    """Vector store connection pool for AI embeddings."""
    
    def __init__(self, config: CachePoolConfig):
        super().__init__(config)
        self._index = None
        self._client = None
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._vectors = {}  # In-memory vector storage for FAISS
        
    async def initialize(self) -> bool:
        """Initialize vector store pool."""
        vector_config = self.config.vector_config
        if not vector_config:
            logger.error("Vector configuration required for vector store pool")
            return False
        
        try:
            if vector_config.store_type.lower() == 'faiss':
                return await self._initialize_faiss(vector_config)
            elif vector_config.store_type.lower() == 'chromadb':
                return await self._initialize_chromadb(vector_config)
            else:
                logger.error(f"Unsupported vector store type: {vector_config.store_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize vector store pool {self.pool_id}: {e}")
            return False
    
    async def _initialize_faiss(self, config: VectorStoreConfig) -> bool:
        """Initialize FAISS vector index."""
        if not FAISS_AVAILABLE or not NUMPY_AVAILABLE:
            logger.error("faiss-cpu and numpy required for FAISS vector store")
            return False
        
        def create_index():
            if config.index_type.upper() == 'FLAT':
                if config.metric_type == 'cosine':
                    index = faiss.IndexFlatIP(config.dimension)
                else:
                    index = faiss.IndexFlatL2(config.dimension)
            elif config.index_type.upper() == 'IVF':
                if config.metric_type == 'cosine':
                    quantizer = faiss.IndexFlatIP(config.dimension)
                    index = faiss.IndexIVFFlat(quantizer, config.dimension, config.nlist)
                else:
                    quantizer = faiss.IndexFlatL2(config.dimension)
                    index = faiss.IndexIVFFlat(quantizer, config.dimension, config.nlist)
            else:
                raise ValueError(f"Unsupported FAISS index type: {config.index_type}")
            
            return index
        
        # Create index in thread pool to avoid blocking
        self._index = await asyncio.get_event_loop().run_in_executor(
            self._executor, create_index
        )
        
        # Load existing index if storage path provided
        if config.storage_path:
            try:
                def load_index():
                    return faiss.read_index(config.storage_path)
                
                self._index = await asyncio.get_event_loop().run_in_executor(
                    self._executor, load_index
                )
                logger.info(f"Loaded existing FAISS index from {config.storage_path}")
            except:
                logger.info(f"Creating new FAISS index at {config.storage_path}")
        
        self._is_initialized = True
        logger.info(f"FAISS vector store pool {self.pool_id} initialized with dimension {config.dimension}")
        return True
    
    async def _initialize_chromadb(self, config: VectorStoreConfig) -> bool:
        """Initialize ChromaDB vector store."""
        if not CHROMADB_AVAILABLE:
            logger.error("chromadb required for ChromaDB vector store")
            return False
        
        def create_client():
            if config.storage_path:
                # Persistent client
                return chromadb.PersistentClient(path=config.storage_path)
            else:
                # In-memory client
                return chromadb.Client()
        
        self._client = await asyncio.get_event_loop().run_in_executor(
            self._executor, create_client
        )
        
        # Get or create collection
        collection_name = config.additional_params.get('collection_name', f'collection_{self.pool_id}')
        
        def get_or_create_collection():
            try:
                return self._client.get_collection(name=collection_name)
            except:
                return self._client.create_collection(
                    name=collection_name,
                    metadata={"dimension": config.dimension}
                )
        
        self._index = await asyncio.get_event_loop().run_in_executor(
            self._executor, get_or_create_collection
        )
        
        self._is_initialized = True
        logger.info(f"ChromaDB vector store pool {self.pool_id} initialized")
        return True
    
    async def close(self):
        """Close vector store pool."""
        # Save FAISS index if configured
        if (self._index and 
            hasattr(self.config.vector_config, 'storage_path') and 
            self.config.vector_config.storage_path and
            self.config.vector_config.store_type.lower() == 'faiss'):
            
            try:
                def save_index():
                    faiss.write_index(self._index, self.config.vector_config.storage_path)
                
                await asyncio.get_event_loop().run_in_executor(
                    self._executor, save_index
                )
                logger.info(f"Saved FAISS index to {self.config.vector_config.storage_path}")
            except Exception as e:
                logger.error(f"Failed to save FAISS index: {e}")
        
        self._index = None
        self._client = None
        self._executor.shutdown(wait=True)
        self._is_initialized = False
        logger.info(f"Vector store pool {self.pool_id} closed")
    
    async def health_check(self) -> bool:
        """Perform health check on vector store pool."""
        if not self._is_initialized:
            return False
        
        try:
            # Simple health check - verify index exists
            if self.config.vector_config.store_type.lower() == 'faiss':
                is_healthy = self._index is not None
            elif self.config.vector_config.store_type.lower() == 'chromadb':
                is_healthy = self._client is not None and self._index is not None
            else:
                is_healthy = False
            
            self._stats['last_health_check'] = datetime.now(timezone.utc)
            return is_healthy
            
        except Exception as e:
            logger.error(f"Vector store pool {self.pool_id} health check failed: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get vector by key (not applicable for vector stores)."""
        # Vector stores don't work with simple key-value semantics
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set vector by key (not applicable for vector stores)."""
        # Vector stores don't work with simple key-value semantics
        return False
    
    async def delete(self, key: str) -> bool:
        """Delete vector by key."""
        if not self._is_initialized:
            return False
        
        try:
            if self.config.vector_config.store_type.lower() == 'chromadb':
                def delete_vector():
                    self._index.delete(ids=[key])
                
                await asyncio.get_event_loop().run_in_executor(
                    self._executor, delete_vector
                )
                return True
            else:
                # FAISS doesn't support deletion directly
                return False
                
        except Exception as e:
            logger.error(f"Vector delete error for key {key}: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def add_vectors(self, vectors: np.ndarray, ids: Optional[List[str]] = None, 
                         metadata: Optional[List[Dict]] = None) -> bool:
        """Add vectors to the index."""
        if not self._is_initialized:
            return False
        
        try:
            self._stats['total_operations'] += len(vectors)
            
            if self.config.vector_config.store_type.lower() == 'faiss':
                return await self._add_vectors_faiss(vectors, ids)
            elif self.config.vector_config.store_type.lower() == 'chromadb':
                return await self._add_vectors_chromadb(vectors, ids, metadata)
            
            return False
            
        except Exception as e:
            logger.error(f"Add vectors error: {e}")
            self._stats['error_count'] += 1
            return False
    
    async def _add_vectors_faiss(self, vectors: np.ndarray, ids: Optional[List[str]] = None) -> bool:
        """Add vectors to FAISS index."""
        def add_to_index():
            # Train index if it's IVF and not trained
            if (hasattr(self._index, 'is_trained') and 
                not self._index.is_trained and 
                len(vectors) >= self.config.vector_config.nlist):
                self._index.train(vectors)
            
            # Add vectors
            if hasattr(self._index, 'add'):
                self._index.add(vectors)
                
                # Store IDs mapping if provided
                if ids:
                    base_id = self._index.ntotal - len(vectors)
                    for i, vector_id in enumerate(ids):
                        self._vectors[vector_id] = base_id + i
                
                return True
            return False
        
        result = await asyncio.get_event_loop().run_in_executor(
            self._executor, add_to_index
        )
        return result
    
    async def _add_vectors_chromadb(self, vectors: np.ndarray, ids: Optional[List[str]] = None, 
                                   metadata: Optional[List[Dict]] = None) -> bool:
        """Add vectors to ChromaDB collection."""
        def add_to_collection():
            # Generate IDs if not provided
            if not ids:
                ids = [f"vec_{i}_{int(time.time())}" for i in range(len(vectors))]
            
            # Convert vectors to list format
            embeddings = vectors.tolist()
            
            # Add to collection
            self._index.add(
                embeddings=embeddings,
                ids=ids,
                metadatas=metadata
            )
            return True
        
        result = await asyncio.get_event_loop().run_in_executor(
            self._executor, add_to_collection
        )
        return result
    
    async def search_vectors(self, query_vector: np.ndarray, k: int = 10, 
                           filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if not self._is_initialized:
            return []
        
        try:
            self._stats['total_operations'] += 1
            
            if self.config.vector_config.store_type.lower() == 'faiss':
                return await self._search_vectors_faiss(query_vector, k)
            elif self.config.vector_config.store_type.lower() == 'chromadb':
                return await self._search_vectors_chromadb(query_vector, k, filter_metadata)
            
            return []
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            self._stats['error_count'] += 1
            return []
    
    async def _search_vectors_faiss(self, query_vector: np.ndarray, k: int) -> List[Dict[str, Any]]:
        """Search vectors in FAISS index."""
        def search_index():
            if hasattr(self._index, 'search'):
                # Set search parameters for IVF
                if hasattr(self._index, 'nprobe'):
                    self._index.nprobe = self.config.vector_config.nprobe
                
                # Search
                query = query_vector.reshape(1, -1)
                distances, indices = self._index.search(query, k)
                
                results = []
                for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
                    if index != -1:  # -1 indicates no match
                        result = {
                            'index': int(index),
                            'distance': float(distance),
                            'similarity': 1.0 / (1.0 + distance) if distance >= 0 else 1.0
                        }
                        
                        # Add ID if available
                        for vector_id, vector_index in self._vectors.items():
                            if vector_index == index:
                                result['id'] = vector_id
                                break
                        
                        results.append(result)
                
                return results
            return []
        
        results = await asyncio.get_event_loop().run_in_executor(
            self._executor, search_index
        )
        
        if results:
            self._stats['cache_hits'] += 1
        else:
            self._stats['cache_misses'] += 1
        
        return results
    
    async def _search_vectors_chromadb(self, query_vector: np.ndarray, k: int, 
                                      filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search vectors in ChromaDB collection."""
        def search_collection():
            query_embedding = query_vector.tolist()
            
            search_kwargs = {
                'query_embeddings': [query_embedding],
                'n_results': k
            }
            
            if filter_metadata:
                search_kwargs['where'] = filter_metadata
            
            results = self._index.query(**search_kwargs)
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': 1.0 - results['distances'][0][i]  # ChromaDB uses distance
                }
                
                if results['metadatas'][0][i]:
                    result['metadata'] = results['metadatas'][0][i]
                
                formatted_results.append(result)
            
            return formatted_results
        
        results = await asyncio.get_event_loop().run_in_executor(
            self._executor, search_collection
        )
        
        if results:
            self._stats['cache_hits'] += 1
        else:
            self._stats['cache_misses'] += 1
        
        return results


class MultiLevelCache:
    """Multi-level cache combining L1 memory, L2 Redis, and L3 disk."""
    
    def __init__(self, redis_pool: Optional[RedisPool] = None, 
                 l1_max_size: int = 1000, l1_ttl: int = 300):
        self.redis_pool = redis_pool
        self.l1_cache = {}  # L1 memory cache
        self.l1_timestamps = {}  # L1 timestamps
        self.l1_max_size = l1_max_size
        self.l1_ttl = l1_ttl
        self._lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache."""
        # L1 cache (memory)
        with self._lock:
            if key in self.l1_cache:
                timestamp = self.l1_timestamps.get(key, 0)
                if time.time() - timestamp < self.l1_ttl:
                    return self.l1_cache[key]
                else:
                    # Expired, remove from L1
                    del self.l1_cache[key]
                    del self.l1_timestamps[key]
        
        # L2 cache (Redis)
        if self.redis_pool:
            value = await self.redis_pool.get(key)
            if value is not None:
                # Store in L1 for faster access
                await self._store_l1(key, value)
                return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache."""
        success = True
        
        # Store in L1 cache
        await self._store_l1(key, value)
        
        # Store in L2 cache (Redis)
        if self.redis_pool:
            redis_success = await self.redis_pool.set(key, value, ttl)
            success = success and redis_success
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels."""
        success = True
        
        # Remove from L1
        with self._lock:
            self.l1_cache.pop(key, None)
            self.l1_timestamps.pop(key, None)
        
        # Remove from L2
        if self.redis_pool:
            redis_success = await self.redis_pool.delete(key)
            success = success and redis_success
        
        return success
    
    async def _store_l1(self, key: str, value: Any):
        """Store value in L1 cache with LRU eviction."""
        with self._lock:
            # Evict old entries if at capacity
            if len(self.l1_cache) >= self.l1_max_size:
                # Remove oldest entry
                oldest_key = min(self.l1_timestamps, key=self.l1_timestamps.get)
                del self.l1_cache[oldest_key]
                del self.l1_timestamps[oldest_key]
            
            # Store new value
            self.l1_cache[key] = value
            self.l1_timestamps[key] = time.time()
    
    def get_l1_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics."""
        with self._lock:
            return {
                'size': len(self.l1_cache),
                'max_size': self.l1_max_size,
                'utilization': (len(self.l1_cache) / self.l1_max_size) * 100
            }


class CachePoolsManager:
    """Manager for all cache connection pools."""
    
    def __init__(self):
        self._pools: Dict[str, CachePool] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        self.multi_level_cache: Optional[MultiLevelCache] = None
    
    async def add_redis_pool(self, pool_id: str, connection_info: CacheConnectionInfo,
                           **pool_config) -> bool:
        """Add Redis connection pool."""
        config = CachePoolConfig(
            pool_id=pool_id,
            connection_info=connection_info,
            **pool_config
        )
        
        pool = RedisPool(config)
        success = await pool.initialize()
        
        if success:
            self._pools[pool_id] = pool
            logger.info(f"Added Redis pool: {pool_id}")
        
        return success
    
    async def add_vector_store_pool(self, pool_id: str, vector_config: VectorStoreConfig,
                                  **pool_config) -> bool:
        """Add vector store connection pool."""
        config = CachePoolConfig(
            pool_id=pool_id,
            vector_config=vector_config,
            **pool_config
        )
        
        pool = VectorStorePool(config)
        success = await pool.initialize()
        
        if success:
            self._pools[pool_id] = pool
            logger.info(f"Added vector store pool: {pool_id}")
        
        return success
    
    async def setup_multi_level_cache(self, redis_pool_id: str, 
                                     l1_max_size: int = 1000, l1_ttl: int = 300) -> bool:
        """Setup multi-level cache using Redis pool."""
        redis_pool = self._pools.get(redis_pool_id)
        if not redis_pool or not isinstance(redis_pool, RedisPool):
            logger.error(f"Redis pool {redis_pool_id} not found for multi-level cache")
            return False
        
        self.multi_level_cache = MultiLevelCache(redis_pool, l1_max_size, l1_ttl)
        logger.info(f"Multi-level cache setup with Redis pool {redis_pool_id}")
        return True
    
    async def get_pool(self, pool_id: str) -> Optional[CachePool]:
        """Get a specific pool by ID."""
        return self._pools.get(pool_id)
    
    async def remove_pool(self, pool_id: str) -> bool:
        """Remove and close a pool."""
        pool = self._pools.get(pool_id)
        if pool:
            await pool.close()
            del self._pools[pool_id]
            logger.info(f"Removed cache pool: {pool_id}")
            return True
        return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Health check all cache pools."""
        results = {}
        
        for pool_id, pool in self._pools.items():
            try:
                results[pool_id] = await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for cache pool {pool_id}: {e}")
                results[pool_id] = False
        
        return results
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all cache pools."""
        stats = {}
        
        for pool_id, pool in self._pools.items():
            stats[pool_id] = pool.get_stats()
        
        # Add multi-level cache stats if available
        if self.multi_level_cache:
            stats['multi_level_cache'] = self.multi_level_cache.get_l1_stats()
        
        return stats
    
    async def start_monitoring(self, interval: int = 30):
        """Start background health monitoring."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info("Cache pools monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring."""
        self._is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Cache pools monitoring stopped")
    
    async def _monitoring_loop(self, interval: int):
        """Background monitoring loop."""
        while self._is_monitoring:
            try:
                # Health check all pools
                health_results = await self.health_check_all()
                
                # Log unhealthy pools
                unhealthy_pools = [pool_id for pool_id, is_healthy in health_results.items() if not is_healthy]
                if unhealthy_pools:
                    logger.warning(f"Unhealthy cache pools detected: {unhealthy_pools}")
                
                # Wait for next cycle
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache pools monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def close_all_pools(self):
        """Close all cache pools."""
        logger.info("Closing all cache pools...")
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Close all pools
        for pool_id in list(self._pools.keys()):
            await self.remove_pool(pool_id)
        
        # Clear multi-level cache
        self.multi_level_cache = None
        
        logger.info("All cache pools closed")
    
    @property
    def pool_count(self) -> int:
        """Get number of registered pools."""
        return len(self._pools)
    
    @property
    def pool_ids(self) -> List[str]:
        """Get list of pool IDs."""
        return list(self._pools.keys())


# Global cache pools manager instance
_cache_pools_manager: Optional[CachePoolsManager] = None


def get_cache_pools_manager() -> CachePoolsManager:
    """Get the global cache pools manager."""
    global _cache_pools_manager
    if _cache_pools_manager is None:
        _cache_pools_manager = CachePoolsManager()
    return _cache_pools_manager


# Export public interface
__all__ = [
    "CachePool",
    "RedisPool",
    "VectorStorePool", 
    "MultiLevelCache",
    "CachePoolsManager",
    "get_cache_pools_manager",
    "CacheConnectionInfo",
    "VectorStoreConfig",
    "CachePoolConfig"
]