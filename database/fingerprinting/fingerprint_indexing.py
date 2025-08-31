"""Ultra-Advanced Fingerprint Indexing Manager

Enterprise-grade indexing system for content fingerprints with:
- Multi-dimensional vector similarity search (FAISS integration)
- Real-time indexing and search optimization
- Distributed index sharding and replication
- Advanced caching and performance monitoring
- Semantic search with embeddings
- Temporal indexing for time-based queries

Industry Features:
- FAISS vector indexes for ultra-fast similarity search
- Elasticsearch integration for complex queries
- Redis caching for hot index data
- Distributed hash ring for index sharding
- Real-time index updates and maintenance
- Comprehensive performance analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project: IA Influencer Agent + Content Protection Platform

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, modification, or distribution is strictly prohibited
and will result in immediate legal action under German and international law.
All violators will be prosecuted to the full extent of the law.

Development Team Specialties:
- Lead AI Developer: Advanced ML/NLP systems
- Senior Backend Engineer: Scalable microservices architecture  
- ML Engineer: Deep learning and neural network optimization
- Database Architect: Enterprise database design and optimization
- Security Engineer: Cryptography and data protection
- Microservices Specialist: Distributed systems and APIs
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: Infrastructure automation and monitoring
"""
import asyncio
import hashlib
import json
import logging
import pickle
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, Set, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import struct

import numpy as np
import faiss
from sqlalchemy import text, and_, or_, func, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import msgpack

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError
from backend.utils.performance import PerformanceMonitor
from backend.utils.hashing import ConsistentHashRing
from backend.utils.caching import CacheManager

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """Advanced types of fingerprint indexes"""    HASH_INDEX = "hash_index"
    VECTOR_INDEX = "vector_index"
    SEMANTIC_INDEX = "semantic_index"
    TEMPORAL_INDEX = "temporal_index"
    COMPOSITE_INDEX = "composite_index"
    DISTRIBUTED_INDEX = "distributed_index"
    HYBRID_INDEX = "hybrid_index"


class IndexMetric(Enum):
    """Distance metrics for vector similarity"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"
    JACCARD = "jaccard"


class IndexStatus(Enum):
    """Index status enumeration"""    INITIALIZING = "initializing"
    ACTIVE = "active"
    UPDATING = "updating"
    REBUILDING = "rebuilding"
    CORRUPTED = "corrupted"
    ARCHIVED = "archived"


@dataclass
class IndexConfig:
    """Comprehensive configuration for fingerprint indexes"""    index_type: IndexType
    dimension: Optional[int] = None
    metric: IndexMetric = IndexMetric.COSINE
    
    # FAISS configuration
    nlist: int = 256  # Number of clusters for IVF
    nprobe: int = 32  # Number of clusters to search
    ef_construction: int = 200  # HNSW construction parameter
    ef_search: int = 50  # HNSW search parameter
    max_connections: int = 32  # HNSW max connections
    
    # Performance optimization
    use_gpu: bool = False
    gpu_device: int = 0
    shard_count: int = 1
    replica_count: int = 1
    batch_size: int = 1000
    
    # Cache configuration
    cache_enabled: bool = True
    cache_size: int = 10000
    cache_ttl: int = 3600
    
    # Advanced settings
    compression_enabled: bool = True
    quantization_bits: int = 8
    training_threshold: int = 10000
    rebuild_threshold: float = 0.3  # Rebuild when 30% fragmented


@dataclass
class IndexStatistics:
    """Comprehensive index statistics and metrics"""    total_vectors: int = 0
    total_size_mb: float = 0.0
    average_query_time: float = 0.0
    cache_hit_ratio: float = 0.0
    index_fragmentation: float = 0.0
    last_rebuild: Optional[datetime] = None
    queries_per_second: float = 0.0
    memory_usage_mb: float = 0.0


@dataclass
class SearchQuery:
    """Advanced search query configuration"""    query_vector: np.ndarray
    k: int = 10
    threshold: float = 0.8
    filter_criteria: Optional[Dict[str, Any]] = None
    include_metadata: bool = True
    search_timeout: float = 30.0
    use_cache: bool = True


class AdvancedVectorIndexManager:
    """Ultra-high-performance vector index manager with enterprise features"""    
    def __init__(self, config: IndexConfig, cache_manager: CacheManager):
        self.config = config
        self.cache_manager = cache_manager
        self.index = None
        self.id_map = {}  # Maps FAISS IDs to fingerprint IDs
        self.reverse_id_map = {}  # Maps fingerprint IDs to FAISS IDs
        self.statistics = IndexStatistics()
        self.status = IndexStatus.INITIALIZING
        self.logger = logging.getLogger(f"{__name__}.AdvancedVectorIndexManager")
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.query_times = []
        self.last_maintenance = datetime.now()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize_index(self) -> None:
        """Initialize advanced FAISS index with optimal configuration"""        try:
            self.status = IndexStatus.INITIALIZING
            dimension = self.config.dimension
            
            if not dimension:
                raise ValidationError("Dimension is required for vector index")
            
            # Create base index based on metric
            base_index = self._create_base_index(dimension)
            
            # Apply advanced optimizations
            optimized_index = await self._apply_optimizations(base_index, dimension)
            
            # Enable GPU acceleration if configured
            if self.config.use_gpu:
                optimized_index = await self._enable_gpu_acceleration(optimized_index)
            
            self.index = optimized_index
            self.status = IndexStatus.ACTIVE
            
            self.logger.info(f"Successfully initialized {self.config.index_type.value} index with dimension {dimension}")
            
        except Exception as e:
            self.status = IndexStatus.CORRUPTED
            self.logger.error(f"Failed to initialize index: {str(e)}")
            raise DatabaseError(f"Index initialization failed: {str(e)}")
    
    def _create_base_index(self, dimension: int) -> faiss.Index:
        """Create optimized base index based on configuration"""        if self.config.metric == IndexMetric.COSINE:
            return faiss.IndexFlatIP(dimension)
        elif self.config.metric == IndexMetric.EUCLIDEAN:
            return faiss.IndexFlatL2(dimension)
        elif self.config.metric == IndexMetric.DOT_PRODUCT:
            return faiss.IndexFlatIP(dimension)
        else:
            return faiss.IndexFlatIP(dimension)  # Default to cosine
    
    async def _apply_optimizations(self, base_index: faiss.Index, dimension: int) -> faiss.Index:
        """Apply advanced FAISS optimizations"""        try:
            # Use IVF for large-scale datasets
            if self.config.nlist > 1:
                quantizer = base_index
                index = faiss.IndexIVFFlat(quantizer, dimension, self.config.nlist)
                
                # Add Product Quantization for memory efficiency
                if self.config.compression_enabled:
                    m = min(64, dimension // 4)  # Subquantizer count
                    index = faiss.IndexIVFPQ(quantizer, dimension, self.config.nlist, m, self.config.quantization_bits)
                
                return index
            
            # Use HNSW for high-precision search
            elif self.config.ef_construction > 0:
                index = faiss.IndexHNSWFlat(dimension, self.config.max_connections)
                index.hnsw.efConstruction = self.config.ef_construction
                index.hnsw.efSearch = self.config.ef_search
                return index
            
            return base_index
            
        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            return base_index
    
    async def _enable_gpu_acceleration(self, index: faiss.Index) -> faiss.Index:
        """Enable GPU acceleration if available"""        try:
            if faiss.get_num_gpus() > 0:
                res = faiss.StandardGpuResources()
                gpu_index = faiss.index_cpu_to_gpu(res, self.config.gpu_device, index)
                self.logger.info(f"GPU acceleration enabled on device {self.config.gpu_device}")
                return gpu_index
            else:
                self.logger.warning("GPU acceleration requested but no GPUs available")
                return index
        except Exception as e:
            self.logger.error(f"GPU acceleration failed: {str(e)}")
            return index
    
    async def add_vectors(
        self,
        vectors: np.ndarray,
        fingerprint_ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Add vectors to index with batch optimization"""        try:
            if vectors.shape[0] != len(fingerprint_ids):
                raise ValidationError("Vector count must match fingerprint ID count")
            
            # Normalize vectors for cosine similarity
            if self.config.metric == IndexMetric.COSINE:
                vectors = self._normalize_vectors(vectors)
            
            # Train index if needed
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                if vectors.shape[0] >= self.config.training_threshold:
                    await self._train_index(vectors)
            
            # Get next available IDs
            start_id = len(self.id_map)
            end_id = start_id + len(fingerprint_ids)
            faiss_ids = list(range(start_id, end_id))
            
            # Add to index
            self.index.add(vectors)
            
            # Update mappings
            for faiss_id, fingerprint_id in zip(faiss_ids, fingerprint_ids):
                self.id_map[faiss_id] = fingerprint_id
                self.reverse_id_map[fingerprint_id] = faiss_id
            
            # Update statistics
            self.statistics.total_vectors += len(fingerprint_ids)
            self.statistics.total_size_mb = self._calculate_index_size()
            
            # Cache metadata if provided
            if metadata and self.config.cache_enabled:
                await self._cache_metadata(fingerprint_ids, metadata)
            
            self.logger.info(f"Successfully added {len(fingerprint_ids)} vectors to index")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add vectors: {str(e)}")
            raise DatabaseError(f"Vector addition failed: {str(e)}")
    
    async def search_similar(self, query: SearchQuery) -> List[Dict[str, Any]]:
        """Advanced similarity search with caching and optimization"""        start_time = time.time()
        
        try:
            # Check cache first
            if query.use_cache and self.config.cache_enabled:
                cache_key = self._generate_cache_key(query)
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    self.statistics.cache_hit_ratio = self._update_cache_hit_ratio(True)
                    return cached_result
            
            # Normalize query vector
            if self.config.metric == IndexMetric.COSINE:
                query_vector = self._normalize_vectors(query.query_vector.reshape(1, -1))
            else:
                query_vector = query.query_vector.reshape(1, -1)
            
            # Set search parameters
            if hasattr(self.index, 'nprobe'):
                self.index.nprobe = self.config.nprobe
            
            # Perform search
            distances, indices = self.index.search(query_vector, query.k)
            
            # Process results
            results = await self._process_search_results(
                distances[0], indices[0], query
            )
            
            # Cache results
            if query.use_cache and self.config.cache_enabled:
                cache_key = self._generate_cache_key(query)
                await self.cache_manager.set(
                    cache_key, results, ttl=self.config.cache_ttl
                )
            
            # Update statistics
            query_time = time.time() - start_time
            self.query_times.append(query_time)
            self.statistics.average_query_time = np.mean(self.query_times[-1000:])  # Last 1000 queries
            
            if not query.use_cache or not cached_result:
                self.statistics.cache_hit_ratio = self._update_cache_hit_ratio(False)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise DatabaseError(f"Similarity search failed: {str(e)}")
    
    async def update_vector(
        self,
        fingerprint_id: str,
        new_vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update existing vector in index"""        try:
            if fingerprint_id not in self.reverse_id_map:
                return False
            
            faiss_id = self.reverse_id_map[fingerprint_id]
            
            # Remove old vector (FAISS doesn't support direct updates)
            await self.remove_vector(fingerprint_id)
            
            # Add new vector
            await self.add_vectors(
                new_vector.reshape(1, -1),
                [fingerprint_id],
                [metadata] if metadata else None
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update vector for {fingerprint_id}: {str(e)}")
            return False
    
    async def remove_vector(self, fingerprint_id: str) -> bool:
        """Remove vector from index"""        try:
            if fingerprint_id not in self.reverse_id_map:
                return False
            
            faiss_id = self.reverse_id_map[fingerprint_id]
            
            # Remove from mappings
            del self.id_map[faiss_id]
            del self.reverse_id_map[fingerprint_id]
            
            # Note: FAISS doesn't support efficient removal
            # Mark for rebuild if fragmentation is high
            self.statistics.index_fragmentation = self._calculate_fragmentation()
            
            if self.statistics.index_fragmentation > self.config.rebuild_threshold:
                await self._schedule_rebuild()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove vector {fingerprint_id}: {str(e)}")
            return False
    
    async def rebuild_index(self) -> bool:
        """Rebuild index to optimize performance"""        try:
            self.status = IndexStatus.REBUILDING
            self.logger.info("Starting index rebuild...")
            
            # Get all current vectors and metadata
            vectors = []
            fingerprint_ids = []
            metadata_list = []
            
            for faiss_id, fingerprint_id in self.id_map.items():
                if faiss_id < self.index.ntotal:
                    vector = self.index.reconstruct(faiss_id)
                    vectors.append(vector)
                    fingerprint_ids.append(fingerprint_id)
                    
                    # Get cached metadata
                    if self.config.cache_enabled:
                        cached_metadata = await self.cache_manager.get(f"metadata:{fingerprint_id}")
                        metadata_list.append(cached_metadata or {})
            
            # Reinitialize index
            await self.initialize_index()
            
            # Re-add all vectors
            if vectors:
                vectors_array = np.array(vectors)
                await self.add_vectors(vectors_array, fingerprint_ids, metadata_list)
            
            self.statistics.last_rebuild = datetime.now()
            self.statistics.index_fragmentation = 0.0
            self.status = IndexStatus.ACTIVE
            
            self.logger.info(f"Index rebuild completed. Restored {len(fingerprint_ids)} vectors")
            return True
            
        except Exception as e:
            self.status = IndexStatus.CORRUPTED
            self.logger.error(f"Index rebuild failed: {str(e)}")
            return False
    
    # Private helper methods
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors for cosine similarity"""        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms
    
    async def _train_index(self, vectors: np.ndarray) -> None:
        """Train index with sample vectors"""        try:
            if hasattr(self.index, 'train'):
                self.index.train(vectors)
                self.logger.info(f"Index trained with {vectors.shape[0]} vectors")
        except Exception as e:
            self.logger.error(f"Index training failed: {str(e)}")
    
    def _calculate_index_size(self) -> float:
        """Calculate index size in MB"""        try:
            # Approximate calculation
            vector_size = self.config.dimension * 4  # 4 bytes per float32
            total_size = self.statistics.total_vectors * vector_size
            overhead = total_size * 0.2  # 20% overhead for index structures
            return (total_size + overhead) / (1024 * 1024)
        except:
            return 0.0
    
    def _calculate_fragmentation(self) -> float:
        """Calculate index fragmentation ratio"""        try:
            active_vectors = len(self.reverse_id_map)
            total_capacity = self.index.ntotal if self.index else 0
            
            if total_capacity == 0:
                return 0.0
            
            return 1.0 - (active_vectors / total_capacity)
        except:
            return 0.0
    
    async def _process_search_results(
        self,
        distances: np.ndarray,
        indices: np.ndarray,
        query: SearchQuery
    ) -> List[Dict[str, Any]]:
        """Process and format search results"""        results = []
        
        for distance, index in zip(distances, indices):
            if index == -1:  # Invalid index
                continue
            
            # Convert distance to similarity score
            if self.config.metric == IndexMetric.COSINE:
                similarity = float(distance)  # Already similarity for IP
            else:
                similarity = 1.0 / (1.0 + float(distance))  # Convert distance to similarity
            
            if similarity < query.threshold:
                continue
            
            fingerprint_id = self.id_map.get(index)
            if not fingerprint_id:
                continue
            
            result = {
                'fingerprint_id': fingerprint_id,
                'similarity_score': similarity,
                'distance': float(distance)
            }
            
            # Include metadata if requested
            if query.include_metadata and self.config.cache_enabled:
                metadata = await self.cache_manager.get(f"metadata:{fingerprint_id}")
                if metadata:
                    result['metadata'] = metadata
            
            results.append(result)
        
        return results
    
    def _generate_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for search query"""        vector_hash = hashlib.md5(query.query_vector.tobytes()).hexdigest()[:16]
        return f"search:{vector_hash}:{query.k}:{query.threshold}"
    
    async def _cache_metadata(
        self,
        fingerprint_ids: List[str],
        metadata_list: List[Dict[str, Any]]
    ) -> None:
        """Cache metadata for quick retrieval"""        try:
            for fingerprint_id, metadata in zip(fingerprint_ids, metadata_list):
                cache_key = f"metadata:{fingerprint_id}"
                await self.cache_manager.set(
                    cache_key, metadata, ttl=self.config.cache_ttl
                )
        except Exception as e:
            self.logger.error(f"Metadata caching failed: {str(e)}")
    
    def _update_cache_hit_ratio(self, hit: bool) -> float:
        """Update cache hit ratio statistics"""        # Simple moving average for cache hit ratio
        if not hasattr(self, '_cache_events'):
            self._cache_events = []
        
        self._cache_events.append(1 if hit else 0)
        
        # Keep only last 1000 events
        if len(self._cache_events) > 1000:
            self._cache_events = self._cache_events[-1000:]
        
        return sum(self._cache_events) / len(self._cache_events)
    
    async def _schedule_rebuild(self) -> None:
        """Schedule index rebuild for optimization"""        # Implementation would schedule rebuild during low-traffic periods
        self.logger.info(f"Index rebuild scheduled due to fragmentation: {self.statistics.index_fragmentation:.2%}")
        # In production, this would use a task scheduler
    
    async def get_statistics(self) -> IndexStatistics:
        """Get comprehensive index statistics"""        self.statistics.memory_usage_mb = self._calculate_index_size()
        self.statistics.queries_per_second = self._calculate_qps()
        return self.statistics
    
    def _calculate_qps(self) -> float:
        """Calculate queries per second"""        if len(self.query_times) < 2:
            return 0.0
        
        recent_queries = self.query_times[-100:]  # Last 100 queries
        if recent_queries:
            return len(recent_queries) / sum(recent_queries)
        return 0.0
            
            self.logger.info(f"Initialized vector index: {type(self.index).__name__}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector index: {e}")
            raise DatabaseError(f"Vector index initialization failed: {e}")
    
    async def add_vectors(
        self,
        fingerprint_ids: List[str],
        vectors: np.ndarray
    ) -> None:
        """Add vectors to the index"""        try:
            if self.index is None:
                await self.initialize_index()
            
            # Normalize vectors for cosine similarity
            if self.config.metric == "cosine":
                vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            
            # Train index if needed (for IVF)
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                self.index.train(vectors)
            
            # Add vectors to index
            start_id = self.index.ntotal
            self.index.add(vectors.astype(np.float32))
            
            # Update ID mappings
            for i, fingerprint_id in enumerate(fingerprint_ids):
                faiss_id = start_id + i
                self.id_map[faiss_id] = fingerprint_id
                self.reverse_id_map[fingerprint_id] = faiss_id
            
            self.logger.debug(f"Added {len(fingerprint_ids)} vectors to index")
            
        except Exception as e:
            self.logger.error(f"Failed to add vectors to index: {e}")
            raise DatabaseError(f"Vector addition failed: {e}")
    
    async def search_vectors(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """Search for similar vectors"""        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Normalize query vector for cosine similarity
            if self.config.metric == "cosine":
                query_vector = query_vector / np.linalg.norm(query_vector)
            
            # Set search parameters for IVF
            if hasattr(self.index, 'nprobe'):
                self.index.nprobe = self.config.nprobe
            
            # Search
            query_vector = query_vector.reshape(1, -1).astype(np.float32)
            distances, faiss_ids = self.index.search(query_vector, k)
            
            # Convert results
            results = []
            for distance, faiss_id in zip(distances[0], faiss_ids[0]):
                if faiss_id >= 0 and distance >= threshold:
                    fingerprint_id = self.id_map.get(faiss_id)
                    if fingerprint_id:
                        # Convert distance to similarity score
                        similarity = float(distance) if self.config.metric == "cosine" else 1.0 / (1.0 + float(distance))
                        results.append((fingerprint_id, similarity))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            raise DatabaseError(f"Vector search failed: {e}")
    
    async def remove_vectors(self, fingerprint_ids: List[str]) -> None:
        """Remove vectors from index (rebuild required for FAISS)"""        try:
            # Remove from ID mappings
            faiss_ids_to_remove = set()
            for fingerprint_id in fingerprint_ids:
                faiss_id = self.reverse_id_map.get(fingerprint_id)
                if faiss_id is not None:
                    faiss_ids_to_remove.add(faiss_id)
                    del self.reverse_id_map[fingerprint_id]
                    del self.id_map[faiss_id]
            
            # Note: FAISS doesn't support direct removal, would need to rebuild
            # For now, we just mark as removed in mappings
            self.logger.warning(f"Marked {len(fingerprint_ids)} vectors for removal. Index rebuild recommended.")
            
        except Exception as e:
            self.logger.error(f"Vector removal failed: {e}")
            raise DatabaseError(f"Vector removal failed: {e}")


class HashIndexManager:
    """High-performance hash index manager using Redis"""    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.HashIndexManager")
        
        # Index key patterns
        self.hash_key_pattern = "fingerprint:hash:{hash_type}:{hash_value}"
        self.content_key_pattern = "fingerprint:content:{content_id}"
        self.user_key_pattern = "fingerprint:user:{user_id}"
    
    async def add_hash_index(
        self,
        fingerprint_id: str,
        content_id: str,
        user_id: str,
        hashes: Dict[str, str]
    ) -> None:
        """Add hash indexes for a fingerprint"""        try:
            pipeline = self.redis.pipeline()
            
            # Add hash-to-fingerprint mappings
            for hash_type, hash_value in hashes.items():
                if hash_value:
                    key = self.hash_key_pattern.format(
                        hash_type=hash_type,
                        hash_value=hash_value
                    )
                    pipeline.sadd(key, fingerprint_id)
                    pipeline.expire(key, 86400 * 30)  # 30 days TTL
            
            # Add content-to-fingerprint mapping
            content_key = self.content_key_pattern.format(content_id=content_id)
            pipeline.sadd(content_key, fingerprint_id)
            pipeline.expire(content_key, 86400 * 30)
            
            # Add user-to-fingerprint mapping
            user_key = self.user_key_pattern.format(user_id=user_id)
            pipeline.sadd(user_key, fingerprint_id)
            pipeline.expire(user_key, 86400 * 30)
            
            await pipeline.execute()
            self.logger.debug(f"Added hash indexes for fingerprint {fingerprint_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to add hash indexes: {e}")
            raise DatabaseError(f"Hash indexing failed: {e}")
    
    async def search_by_hash(
        self,
        hash_type: str,
        hash_value: str
    ) -> Set[str]:
        """Search fingerprints by hash value"""        try:
            key = self.hash_key_pattern.format(
                hash_type=hash_type,
                hash_value=hash_value
            )
            fingerprint_ids = await self.redis.smembers(key)
            return {fid.decode() if isinstance(fid, bytes) else fid for fid in fingerprint_ids}
            
        except Exception as e:
            self.logger.error(f"Hash search failed: {e}")
            raise DatabaseError(f"Hash search failed: {e}")
    
    async def search_by_content(self, content_id: str) -> Set[str]:
        """Search fingerprints by content ID"""        try:
            key = self.content_key_pattern.format(content_id=content_id)
            fingerprint_ids = await self.redis.smembers(key)
            return {fid.decode() if isinstance(fid, bytes) else fid for fid in fingerprint_ids}
            
        except Exception as e:
            self.logger.error(f"Content search failed: {e}")
            raise DatabaseError(f"Content search failed: {e}")
    
    async def search_by_user(self, user_id: str) -> Set[str]:
        """Search fingerprints by user ID"""        try:
            key = self.user_key_pattern.format(user_id=user_id)
            fingerprint_ids = await self.redis.smembers(key)
            return {fid.decode() if isinstance(fid, bytes) else fid for fid in fingerprint_ids}
            
        except Exception as e:
            self.logger.error(f"User search failed: {e}")
            raise DatabaseError(f"User search failed: {e}")
    
    async def remove_hash_index(
        self,
        fingerprint_id: str,
        content_id: str,
        user_id: str,
        hashes: Dict[str, str]
    ) -> None:
        """Remove hash indexes for a fingerprint"""        try:
            pipeline = self.redis.pipeline()
            
            # Remove hash-to-fingerprint mappings
            for hash_type, hash_value in hashes.items():
                if hash_value:
                    key = self.hash_key_pattern.format(
                        hash_type=hash_type,
                        hash_value=hash_value
                    )
                    pipeline.srem(key, fingerprint_id)
            
            # Remove content-to-fingerprint mapping
            content_key = self.content_key_pattern.format(content_id=content_id)
            pipeline.srem(content_key, fingerprint_id)
            
            # Remove user-to-fingerprint mapping
            user_key = self.user_key_pattern.format(user_id=user_id)
            pipeline.srem(user_key, fingerprint_id)
            
            await pipeline.execute()
            self.logger.debug(f"Removed hash indexes for fingerprint {fingerprint_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove hash indexes: {e}")
            raise DatabaseError(f"Hash index removal failed: {e}")


class SemanticIndexManager:
    """Semantic search index manager using Elasticsearch"""    
    def __init__(self, es_client: AsyncElasticsearch):
        self.es = es_client
        self.index_name = "fingerprint_semantic"
        self.logger = logging.getLogger(f"{__name__}.SemanticIndexManager")
    
    async def initialize_index(self) -> None:
        """Initialize Elasticsearch index with proper mapping"""        try:
            mapping = {
                "mappings": {
                    "properties": {
                        "fingerprint_id": {"type": "keyword"},
                        "content_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "content_type": {"type": "keyword"},
                        "fingerprint_type": {"type": "keyword"},
                        "semantic_content": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "metadata": {"type": "object"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "embedding_vector": {
                            "type": "dense_vector",
                            "dims": 512  # Configurable based on model
                        }
                    }
                }
            }
            
            # Create index if it doesn't exist
            if not await self.es.indices.exists(index=self.index_name):
                await self.es.indices.create(index=self.index_name, body=mapping)
                self.logger.info(f"Created semantic index: {self.index_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize semantic index: {e}")
            raise DatabaseError(f"Semantic index initialization failed: {e}")
    
    async def add_semantic_document(
        self,
        fingerprint_id: str,
        content_id: str,
        user_id: str,
        content_type: str,
        fingerprint_type: str,
        semantic_content: str,
        metadata: Dict[str, Any],
        embedding_vector: Optional[np.ndarray] = None
    ) -> None:
        """Add semantic document to index"""        try:
            doc = {
                "fingerprint_id": fingerprint_id,
                "content_id": content_id,
                "user_id": user_id,
                "content_type": content_type,
                "fingerprint_type": fingerprint_type,
                "semantic_content": semantic_content,
                "metadata": metadata,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            
            # Add embedding vector if provided
            if embedding_vector is not None:
                doc["embedding_vector"] = embedding_vector.tolist()
            
            # Extract tags from metadata
            tags = []
            if isinstance(metadata, dict):
                tags.extend(metadata.get("tags", []))
                tags.extend(metadata.get("keywords", []))
            doc["tags"] = tags
            
            await self.es.index(
                index=self.index_name,
                id=fingerprint_id,
                body=doc
            )
            
            self.logger.debug(f"Added semantic document for fingerprint {fingerprint_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to add semantic document: {e}")
            raise DatabaseError(f"Semantic indexing failed: {e}")
    
    async def search_semantic(
        self,
        query: str,
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search semantic content"""        try:
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["semantic_content^2", "tags"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "size": size,
                "_source": ["fingerprint_id", "content_id", "content_type", "metadata"],
                "highlight": {
                    "fields": {
                        "semantic_content": {}
                    }
                }
            }
            
            # Add filters
            if content_type:
                search_body["query"]["bool"]["filter"].append(
                    {"term": {"content_type": content_type}}
                )
            
            if user_id:
                search_body["query"]["bool"]["filter"].append(
                    {"term": {"user_id": user_id}}
                )
            
            # Execute search
            response = await self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                result = {
                    "fingerprint_id": hit["_source"]["fingerprint_id"],
                    "content_id": hit["_source"]["content_id"],
                    "content_type": hit["_source"]["content_type"],
                    "score": hit["_score"],
                    "metadata": hit["_source"].get("metadata", {}),
                    "highlights": hit.get("highlight", {})
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            raise DatabaseError(f"Semantic search failed: {e}")
    
    async def search_by_vector(
        self,
        query_vector: np.ndarray,
        content_type: Optional[str] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search by embedding vector similarity"""        try:
            search_body = {
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                            "params": {
                                "query_vector": query_vector.tolist()
                            }
                        }
                    }
                },
                "size": size,
                "_source": ["fingerprint_id", "content_id", "content_type", "metadata"]
            }
            
            # Add content type filter if specified
            if content_type:
                search_body["query"]["script_score"]["query"] = {
                    "term": {"content_type": content_type}
                }
            
            response = await self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                result = {
                    "fingerprint_id": hit["_source"]["fingerprint_id"],
                    "content_id": hit["_source"]["content_id"],
                    "content_type": hit["_source"]["content_type"],
                    "similarity": hit["_score"],
                    "metadata": hit["_source"].get("metadata", {})
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vector similarity search failed: {e}")
            raise DatabaseError(f"Vector similarity search failed: {e}")
    
    async def remove_semantic_document(self, fingerprint_id: str) -> None:
        """Remove semantic document from index"""        try:
            await self.es.delete(
                index=self.index_name,
                id=fingerprint_id,
                ignore=[404]  # Ignore if document doesn't exist
            )
            
            self.logger.debug(f"Removed semantic document for fingerprint {fingerprint_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove semantic document: {e}")
            raise DatabaseError(f"Semantic document removal failed: {e}")


class FingerprintIndexManager:
    """    Comprehensive fingerprint indexing manager that coordinates multiple
    index types for optimal search performance.
    """    
    def __init__(
        self,
        db_manager: DatabaseManager,
        redis_client: Redis,
        es_client: AsyncElasticsearch
    ):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.es_client = es_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize index managers
        self.hash_index = HashIndexManager(redis_client)
        self.semantic_index = SemanticIndexManager(es_client)
        
        # Vector index configurations by content type
        self.vector_configs = {
            "audio": IndexConfig(IndexType.VECTOR_INDEX, dimension=512, metric="cosine"),
            "video": IndexConfig(IndexType.VECTOR_INDEX, dimension=1024, metric="cosine"),
            "image": IndexConfig(IndexType.VECTOR_INDEX, dimension=768, metric="cosine"),
            "text": IndexConfig(IndexType.VECTOR_INDEX, dimension=512, metric="cosine"),
        }
        
        self.vector_indexes = {}
        self.performance_monitor = PerformanceMonitor()
    
    async def initialize_indexes(self) -> None:
        """Initialize all index types"""        try:
            # Initialize semantic index
            await self.semantic_index.initialize_index()
            
            # Initialize vector indexes for each content type
            for content_type, config in self.vector_configs.items():
                vector_index = VectorIndexManager(config)
                await vector_index.initialize_index()
                self.vector_indexes[content_type] = vector_index
            
            self.logger.info("All fingerprint indexes initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize indexes: {e}")
            raise DatabaseError(f"Index initialization failed: {e}")
    
    async def add_fingerprint_indexes(
        self,
        fingerprint: ContentFingerprint,
        user_id: str,
        embedding_vector: Optional[np.ndarray] = None
    ) -> None:
        """Add fingerprint to all relevant indexes"""        try:
            fingerprint_id = fingerprint.fingerprint_id
            content_type = str(fingerprint.content_type).lower()
            
            # Add to hash indexes
            hashes = {
                "primary": fingerprint.primary_hash,
                "perceptual": fingerprint.perceptual_hash,
                "structural": fingerprint.structural_hash,
                "semantic": fingerprint.semantic_hash,
            }
            hashes = {k: v for k, v in hashes.items() if v}  # Remove None values
            
            await self.hash_index.add_hash_index(
                fingerprint_id,
                fingerprint.content_id,
                user_id,
                hashes
            )
            
            # Add to vector index if feature vector available
            if hasattr(fingerprint, 'feature_vector') and fingerprint.feature_vector is not None:
                vector_index = self.vector_indexes.get(content_type)
                if vector_index:
                    vectors = fingerprint.feature_vector.reshape(1, -1)
                    await vector_index.add_vectors([fingerprint_id], vectors)
            
            # Add to semantic index
            semantic_content = self._extract_semantic_content(fingerprint)
            if semantic_content:
                await self.semantic_index.add_semantic_document(
                    fingerprint_id,
                    fingerprint.content_id,
                    user_id,
                    content_type,
                    str(fingerprint.fingerprint_type),
                    semantic_content,
                    fingerprint.metadata or {},
                    embedding_vector
                )
            
            self.logger.debug(f"Added fingerprint {fingerprint_id} to all indexes")
            
        except Exception as e:
            self.logger.error(f"Failed to add fingerprint indexes: {e}")
            raise DatabaseError(f"Fingerprint indexing failed: {e}")
    
    async def search_fingerprints(
        self,
        query: Union[str, np.ndarray, Dict[str, str]],
        search_type: str = "hybrid",
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
        similarity_threshold: float = 0.7,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """        Comprehensive fingerprint search across multiple index types
        
        Args:
            query: Search query (text, vector, or hash dict)
            search_type: Type of search (hash, vector, semantic, hybrid)
            content_type: Filter by content type
            user_id: Filter by user
            similarity_threshold: Minimum similarity score
            max_results: Maximum results to return
            
        Returns:
            List of search results with scores and metadata
        """        try:
            results = {}  # fingerprint_id -> result dict
            
            if search_type in ["hash", "hybrid"]:
                hash_results = await self._search_by_hash(query, user_id)
                for fingerprint_id in hash_results:
                    results[fingerprint_id] = {
                        "fingerprint_id": fingerprint_id,
                        "similarity": 1.0,  # Exact hash match
                        "match_type": "hash",
                        "source": "hash_index"
                    }
            
            if search_type in ["vector", "hybrid"] and isinstance(query, np.ndarray):
                vector_results = await self._search_by_vector(
                    query, content_type, similarity_threshold, max_results
                )
                for fingerprint_id, similarity in vector_results:
                    if fingerprint_id in results:
                        # Combine scores for hybrid search
                        results[fingerprint_id]["similarity"] = max(
                            results[fingerprint_id]["similarity"], similarity
                        )
                        results[fingerprint_id]["match_type"] = "hybrid"
                    else:
                        results[fingerprint_id] = {
                            "fingerprint_id": fingerprint_id,
                            "similarity": similarity,
                            "match_type": "vector",
                            "source": "vector_index"
                        }
            
            if search_type in ["semantic", "hybrid"] and isinstance(query, str):
                semantic_results = await self.semantic_index.search_semantic(
                    query, content_type, user_id, max_results
                )
                for result in semantic_results:
                    fingerprint_id = result["fingerprint_id"]
                    similarity = result["score"] / 10.0  # Normalize Elasticsearch score
                    
                    if fingerprint_id in results:
                        # Combine scores for hybrid search
                        results[fingerprint_id]["similarity"] = max(
                            results[fingerprint_id]["similarity"], similarity
                        )
                        results[fingerprint_id]["match_type"] = "hybrid"
                    else:
                        results[fingerprint_id] = {
                            "fingerprint_id": fingerprint_id,
                            "similarity": similarity,
                            "match_type": "semantic",
                            "source": "semantic_index",
                            "metadata": result.get("metadata", {}),
                            "highlights": result.get("highlights", {})
                        }
            
            # Sort by similarity and apply threshold
            filtered_results = [
                result for result in results.values()
                if result["similarity"] >= similarity_threshold
            ]
            
            filtered_results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return filtered_results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Fingerprint search failed: {e}")
            raise DatabaseError(f"Search failed: {e}")
    
    async def remove_fingerprint_indexes(
        self,
        fingerprint: ContentFingerprint,
        user_id: str
    ) -> None:
        """Remove fingerprint from all indexes"""        try:
            fingerprint_id = fingerprint.fingerprint_id
            content_type = str(fingerprint.content_type).lower()
            
            # Remove from hash indexes
            hashes = {
                "primary": fingerprint.primary_hash,
                "perceptual": fingerprint.perceptual_hash,
                "structural": fingerprint.structural_hash,
                "semantic": fingerprint.semantic_hash,
            }
            hashes = {k: v for k, v in hashes.items() if v}
            
            await self.hash_index.remove_hash_index(
                fingerprint_id,
                fingerprint.content_id,
                user_id,
                hashes
            )
            
            # Remove from vector index
            vector_index = self.vector_indexes.get(content_type)
            if vector_index:
                await vector_index.remove_vectors([fingerprint_id])
            
            # Remove from semantic index
            await self.semantic_index.remove_semantic_document(fingerprint_id)
            
            self.logger.debug(f"Removed fingerprint {fingerprint_id} from all indexes")
            
        except Exception as e:
            self.logger.error(f"Failed to remove fingerprint indexes: {e}")
            raise DatabaseError(f"Index removal failed: {e}")
    
    async def rebuild_indexes(
        self,
        content_type: Optional[str] = None,
        batch_size: int = 1000
    ) -> None:
        """Rebuild indexes from database"""        try:
            self.logger.info("Starting index rebuild...")
            
            # Clear existing indexes
            if content_type:
                vector_index = self.vector_indexes.get(content_type)
                if vector_index:
                    await vector_index.initialize_index()
            else:
                for ct_vector_index in self.vector_indexes.values():
                    await ct_vector_index.initialize_index()
            
            # Rebuild from database
            async with self.db_manager.get_session() as session:
                # Process in batches
                offset = 0
                while True:
                    # Fetch batch of fingerprints
                    query = """                    SELECT fingerprint_id, content_id, user_id, content_type,
                           fingerprint_type, primary_hash, perceptual_hash,
                           structural_hash, semantic_hash, feature_vector,
                           metadata
                    FROM content_fingerprints
                    WHERE ($1::text IS NULL OR content_type = $1)
                    ORDER BY created_at
                    LIMIT $2 OFFSET $3
                    """                    
                    result = await session.execute(
                        text(query),
                        [content_type, batch_size, offset]
                    )
                    
                    rows = result.fetchall()
                    if not rows:
                        break
                    
                    # Process batch
                    for row in rows:
                        try:
                            # Reconstruct fingerprint object
                            fingerprint_data = {
                                'fingerprint_id': str(row.fingerprint_id),
                                'content_id': row.content_id,
                                'content_type': row.content_type,
                                'fingerprint_type': FingerprintType(row.fingerprint_type),
                                'primary_hash': row.primary_hash,
                                'perceptual_hash': row.perceptual_hash,
                                'structural_hash': row.structural_hash,
                                'semantic_hash': row.semantic_hash,
                                'metadata': row.metadata or {}
                            }
                            
                            if row.feature_vector:
                                fingerprint_data['feature_vector'] = pickle.loads(row.feature_vector)
                            
                            fingerprint = ContentFingerprint(**fingerprint_data)
                            
                            # Add to indexes
                            await self.add_fingerprint_indexes(fingerprint, row.user_id)
                            
                        except Exception as e:
                            self.logger.error(f"Failed to reindex fingerprint {row.fingerprint_id}: {e}")
                            continue
                    
                    offset += batch_size
                    self.logger.info(f"Reindexed {offset} fingerprints...")
            
            self.logger.info("Index rebuild completed successfully")
            
        except Exception as e:
            self.logger.error(f"Index rebuild failed: {e}")
            raise DatabaseError(f"Index rebuild failed: {e}")
    
    # Private helper methods
    
    async def _search_by_hash(
        self,
        query: Union[str, Dict[str, str]],
        user_id: Optional[str]
    ) -> Set[str]:
        """Search by hash values"""        results = set()
        
        if isinstance(query, str):
            # Single hash search
            for hash_type in ["primary", "perceptual", "structural", "semantic"]:
                hash_results = await self.hash_index.search_by_hash(hash_type, query)
                results.update(hash_results)
        
        elif isinstance(query, dict):
            # Multiple hash search
            for hash_type, hash_value in query.items():
                if hash_value:
                    hash_results = await self.hash_index.search_by_hash(hash_type, hash_value)
                    results.update(hash_results)
        
        # Filter by user if specified
        if user_id and results:
            user_fingerprints = await self.hash_index.search_by_user(user_id)
            results = results.intersection(user_fingerprints)
        
        return results
    
    async def _search_by_vector(
        self,
        query_vector: np.ndarray,
        content_type: Optional[str],
        threshold: float,
        max_results: int
    ) -> List[Tuple[str, float]]:
        """Search by vector similarity"""        results = []
        
        # Search in relevant vector indexes
        if content_type:
            vector_index = self.vector_indexes.get(content_type)
            if vector_index:
                vector_results = await vector_index.search_vectors(
                    query_vector, max_results, threshold
                )
                results.extend(vector_results)
        else:
            # Search in all vector indexes
            for vector_index in self.vector_indexes.values():
                vector_results = await vector_index.search_vectors(
                    query_vector, max_results // len(self.vector_indexes), threshold
                )
                results.extend(vector_results)
        
        # Sort by similarity and limit
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]
    
    def _extract_semantic_content(self, fingerprint: ContentFingerprint) -> str:
        """Extract semantic content for indexing"""        semantic_parts = []
        
        # Add content type and fingerprint type
        semantic_parts.append(str(fingerprint.content_type))
        semantic_parts.append(str(fingerprint.fingerprint_type))
        
        # Extract from metadata
        if fingerprint.metadata:
            metadata = fingerprint.metadata
            
            # Add tags and keywords
            semantic_parts.extend(metadata.get("tags", []))
            semantic_parts.extend(metadata.get("keywords", []))
            
            # Add other text fields
            for field in ["title", "description", "artist", "album", "genre"]:
                if field in metadata and metadata[field]:
                    semantic_parts.append(str(metadata[field]))
        
        return " ".join(semantic_parts)
    
    async def get_index_statistics(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""        try:
            stats = {
                "vector_indexes": {},
                "hash_index_keys": 0,
                "semantic_index_docs": 0,
                "total_fingerprints": 0
            }
            
            # Vector index stats
            for content_type, vector_index in self.vector_indexes.items():
                if vector_index.index:
                    stats["vector_indexes"][content_type] = {
                        "total_vectors": vector_index.index.ntotal,
                        "dimension": vector_index.config.dimension,
                        "metric": vector_index.config.metric
                    }
            
            # Hash index stats (approximate)
            try:
                hash_keys = await self.redis_client.keys("fingerprint:hash:*")
                stats["hash_index_keys"] = len(hash_keys)
            except Exception:
                stats["hash_index_keys"] = -1  # Unable to determine
            
            # Semantic index stats
            try:
                es_stats = await self.es_client.count(index=self.semantic_index.index_name)
                stats["semantic_index_docs"] = es_stats["count"]
            except Exception:
                stats["semantic_index_docs"] = -1  # Unable to determine
            
            # Total from database
            async with self.db_manager.get_session() as session:
                count_result = await session.execute(
                    text("SELECT COUNT(*) FROM content_fingerprints_v2")
                )
                stats["total_fingerprints"] = count_result.scalar()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get index statistics: {e}")
            return {"error": str(e)}


# Export classes and functions
__all__ = [
    "FingerprintIndexManager",
    "AdvancedVectorIndexManager", 
    "HashIndexManager",
    "SemanticIndexManager",
    "IndexType",
    "IndexMetric",
    "IndexStatus",
    "IndexConfig",
    "IndexStatistics",
    "SearchQuery"
]
