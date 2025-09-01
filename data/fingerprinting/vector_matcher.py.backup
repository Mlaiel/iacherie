"""Vector Matcher Implementation
============================

Professional vector similarity matching system for content fingerprinting.
Implements advanced FAISS-based similarity search and correlation algorithms.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""
import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from pathlib import Path

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available, falling back to CPU-based similarity")

import sklearn.metrics.pairwise as similarity_metrics
from scipy.spatial.distance import cosine, euclidean
import redis
from concurrent.futures import ThreadPoolExecutor


class SimilarityMetric(Enum):
    """Similarity metrics for vector comparison"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"


class IndexType(Enum):
    """FAISS index types for different use cases"""
    FLAT = "IndexFlatL2"
    IVF_FLAT = "IndexIVFFlat"
    IVF_PQ = "IndexIVFPQ"
    HNSW = "IndexHNSWFlat"
    LSH = "IndexLSH"


@dataclass
class MatchResult:
    """Vector matching result"""
    vector_id: str
    similarity_score: float
    distance: float
    metadata: Dict[str, Any]
    match_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VectorIndexConfig:
    """Configuration for vector index"""
    index_type: IndexType
    dimension: int
    nlist: int = 100  # For IVF indices
    nprobe: int = 10  # For IVF indices
    m: int = 8        # For PQ indices
    nbits: int = 8    # For PQ indices
    max_connections: int = 16  # For HNSW
    ef_construction: int = 200  # For HNSW
    ef_search: int = 50       # For HNSW


class VectorMatcher:
    """
    Professional vector similarity matching system using FAISS and custom algorithms.
    
    Features:
    - Multiple similarity metrics support
    - FAISS-based high-performance indexing
    - Distributed caching with Redis
    - Batch processing capabilities
    - Multi-threaded similarity calculations
    - Automatic index optimization
    - Memory-efficient operations
    - Real-time similarity search
    """
    
    def __init__(self, 
                 config: VectorIndexConfig,
                 redis_client: Optional[redis.Redis] = None,
                 cache_ttl: int = 3600,
                 max_workers: int = 4):
        """
        Initialize vector matcher.
        
        Args:
            config: Vector index configuration
            redis_client: Optional Redis client for caching
            cache_ttl: Cache time-to-live in seconds
            max_workers: Maximum worker threads for parallel processing
        """
        self.config = config
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # FAISS index
        self.faiss_index = None
        self.index_trained = False
        
        # Vector storage
        self.vectors: Dict[str, np.ndarray] = {}
        self.vector_metadata: Dict[str, Dict[str, Any]] = {}
        self.vector_ids: List[str] = []
        
        # Performance tracking
        self.search_count = 0
        self.total_search_time = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Thread pool for parallel operations
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Initialize index
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index based on configuration"""
        try:
            if not FAISS_AVAILABLE:
                self.logger.warning("FAISS not available, using fallback similarity")
                return
            
            dimension = self.config.dimension
            
            if self.config.index_type == IndexType.FLAT:
                self.faiss_index = faiss.IndexFlatL2(dimension)
                self.index_trained = True
                
            elif self.config.index_type == IndexType.IVF_FLAT:
                quantizer = faiss.IndexFlatL2(dimension)
                self.faiss_index = faiss.IndexIVFFlat(
                    quantizer, dimension, self.config.nlist
                )
                
            elif self.config.index_type == IndexType.IVF_PQ:
                quantizer = faiss.IndexFlatL2(dimension)
                self.faiss_index = faiss.IndexIVFPQ(
                    quantizer, dimension, self.config.nlist, 
                    self.config.m, self.config.nbits
                )
                
            elif self.config.index_type == IndexType.HNSW:
                self.faiss_index = faiss.IndexHNSWFlat(
                    dimension, self.config.max_connections
                )
                self.faiss_index.hnsw.efConstruction = self.config.ef_construction
                self.faiss_index.hnsw.efSearch = self.config.ef_search
                self.index_trained = True
                
            elif self.config.index_type == IndexType.LSH:
                self.faiss_index = faiss.IndexLSH(dimension, self.config.nbits)
                self.index_trained = True
            
            self.logger.info(f"Initialized FAISS index: {self.config.index_type.value}")
            
        except Exception as e:
            self.logger.error(f"Error initializing FAISS index: {str(e)}")
            self.faiss_index = None
    
    async def add_vector(self, vector_id: str, vector: np.ndarray, 
                        metadata: Dict[str, Any] = None) -> bool:
        """
        Add vector to index.
        
        Args:
            vector_id: Unique identifier for vector
            vector: Vector array
            metadata: Optional metadata associated with vector
            
        Returns:
            True if vector was added successfully
        """
        try:
            # Validate vector dimensions
            if vector.shape[0] != self.config.dimension:
                raise ValueError(f"Vector dimension {vector.shape[0]} doesn't match index dimension {self.config.dimension}")
            
            # Normalize vector
            normalized_vector = self._normalize_vector(vector)
            
            # Store vector and metadata
            self.vectors[vector_id] = normalized_vector
            self.vector_metadata[vector_id] = metadata or {}
            self.vector_ids.append(vector_id)
            
            # Add to FAISS index if available
            if self.faiss_index is not None:
                await self._add_to_faiss_index(normalized_vector)
            
            # Cache vector if Redis available
            if self.redis_client:
                await self._cache_vector(vector_id, normalized_vector, metadata)
            
            self.logger.debug(f"Added vector {vector_id} to index")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding vector {vector_id}: {str(e)}")
            return False
    
    async def add_vectors_batch(self, 
                              vectors_data: List[Tuple[str, np.ndarray, Dict[str, Any]]]) -> int:
        """
        Add multiple vectors in batch for better performance.
        
        Args:
            vectors_data: List of tuples (vector_id, vector, metadata)
            
        Returns:
            Number of vectors successfully added
        """
        try:
            added_count = 0
            batch_vectors = []
            batch_ids = []
            
            for vector_id, vector, metadata in vectors_data:
                try:
                    # Validate dimensions
                    if vector.shape[0] != self.config.dimension:
                        self.logger.warning(f"Skipping vector {vector_id}: dimension mismatch")
                        continue
                    
                    # Normalize vector
                    normalized_vector = self._normalize_vector(vector)
                    
                    # Store locally
                    self.vectors[vector_id] = normalized_vector
                    self.vector_metadata[vector_id] = metadata or {}
                    self.vector_ids.append(vector_id)
                    
                    batch_vectors.append(normalized_vector)
                    batch_ids.append(vector_id)
                    added_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error processing vector {vector_id}: {str(e)}")
                    continue
            
            # Add batch to FAISS index
            if self.faiss_index is not None and batch_vectors:
                await self._add_batch_to_faiss_index(np.array(batch_vectors))
            
            # Cache batch if Redis available
            if self.redis_client and batch_vectors:
                await self._cache_vectors_batch(batch_ids, batch_vectors, 
                                              [self.vector_metadata[vid] for vid in batch_ids])
            
            self.logger.info(f"Added {added_count} vectors to index in batch")
            return added_count
            
        except Exception as e:
            self.logger.error(f"Error in batch vector addition: {str(e)}")
            return 0
    
    async def find_similar_vectors(self, 
                                 query_vector: np.ndarray,
                                 top_k: int = 10,
                                 similarity_threshold: float = 0.8,
                                 metric: SimilarityMetric = SimilarityMetric.COSINE) -> List[MatchResult]:
        """
        Find similar vectors using various similarity metrics.
        
        Args:
            query_vector: Query vector to find similarities for
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            metric: Similarity metric to use
            
        Returns:
            List of matching results sorted by similarity
        """
        try:
            start_time = datetime.utcnow()
            
            # Check cache first
            cache_key = self._get_cache_key(query_vector, top_k, similarity_threshold, metric)
            if self.redis_client:
                cached_results = await self._get_cached_results(cache_key)
                if cached_results:
                    self.cache_hits += 1
                    return cached_results
            
            self.cache_misses += 1
            
            # Normalize query vector
            normalized_query = self._normalize_vector(query_vector)
            
            # Use FAISS if available and appropriate
            if self.faiss_index is not None and metric == SimilarityMetric.COSINE:
                results = await self._search_faiss_index(normalized_query, top_k, similarity_threshold)
            else:
                # Fallback to custom similarity calculation
                results = await self._search_custom_similarity(normalized_query, top_k, similarity_threshold, metric)
            
            # Update performance metrics
            search_time = (datetime.utcnow() - start_time).total_seconds()
            self.search_count += 1
            self.total_search_time += search_time
            
            # Cache results
            if self.redis_client and results:
                await self._cache_results(cache_key, results)
            
            self.logger.debug(f"Found {len(results)} similar vectors in {search_time:.3f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Error finding similar vectors: {str(e)}")
            return []
    
    async def calculate_similarity(self, 
                                 vector1: np.ndarray, 
                                 vector2: np.ndarray,
                                 metric: SimilarityMetric = SimilarityMetric.COSINE) -> float:
        """
        Calculate similarity between two vectors.
        
        Args:
            vector1: First vector
            vector2: Second vector
            metric: Similarity metric to use
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Normalize vectors
            norm_vec1 = self._normalize_vector(vector1)
            norm_vec2 = self._normalize_vector(vector2)
            
            if metric == SimilarityMetric.COSINE:
                # Cosine similarity (higher is more similar)
                similarity = 1 - cosine(norm_vec1, norm_vec2)
                
            elif metric == SimilarityMetric.EUCLIDEAN:
                # Euclidean distance (convert to similarity)
                distance = euclidean(norm_vec1, norm_vec2)
                similarity = 1 / (1 + distance)
                
            elif metric == SimilarityMetric.DOT_PRODUCT:
                # Dot product similarity
                similarity = np.dot(norm_vec1, norm_vec2)
                
            elif metric == SimilarityMetric.MANHATTAN:
                # Manhattan distance (convert to similarity)
                distance = np.sum(np.abs(norm_vec1 - norm_vec2))
                similarity = 1 / (1 + distance)
                
            elif metric == SimilarityMetric.JACCARD:
                # Jaccard similarity for binary vectors
                intersection = np.sum(np.minimum(norm_vec1, norm_vec2))
                union = np.sum(np.maximum(norm_vec1, norm_vec2))
                similarity = intersection / union if union > 0 else 0.0
            
            else:
                raise ValueError(f"Unsupported similarity metric: {metric}")
            
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    async def remove_vector(self, vector_id: str) -> bool:
        """
        Remove vector from index.
        
        Args:
            vector_id: ID of vector to remove
            
        Returns:
            True if vector was removed successfully
        """
        try:
            if vector_id not in self.vectors:
                return False
            
            # Remove from local storage
            del self.vectors[vector_id]
            del self.vector_metadata[vector_id]
            self.vector_ids.remove(vector_id)
            
            # Remove from cache if Redis available
            if self.redis_client:
                await self._remove_cached_vector(vector_id)
            
            # Note: FAISS doesn't support individual removal efficiently
            # For FAISS, we would need to rebuild the index periodically
            
            self.logger.debug(f"Removed vector {vector_id} from index")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing vector {vector_id}: {str(e)}")
            return False
    
    async def rebuild_index(self) -> bool:
        """
        Rebuild FAISS index from scratch (useful after many deletions).
        
        Returns:
            True if index was rebuilt successfully
        """
        try:
            if not self.faiss_index or not self.vectors:
                return False
            
            self.logger.info("Rebuilding FAISS index...")
            
            # Reset index
            self._initialize_index()
            
            # Re-add all vectors
            if self.vectors:
                vectors_array = np.array([self.vectors[vid] for vid in self.vector_ids])
                await self._add_batch_to_faiss_index(vectors_array)
            
            self.logger.info(f"Rebuilt index with {len(self.vectors)} vectors")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rebuilding index: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get matcher statistics"""
        avg_search_time = (self.total_search_time / self.search_count 
                          if self.search_count > 0 else 0.0)
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) 
                         if (self.cache_hits + self.cache_misses) > 0 else 0.0)
        
        return {
            'total_vectors': len(self.vectors),
            'search_count': self.search_count,
            'average_search_time': avg_search_time,
            'cache_hit_rate': cache_hit_rate,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'index_type': self.config.index_type.value,
            'dimension': self.config.dimension,
            'faiss_available': FAISS_AVAILABLE,
            'index_trained': self.index_trained
        }
    
    # Private helper methods
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    async def _add_to_faiss_index(self, vector: np.ndarray):
        """Add single vector to FAISS index"""
        if self.faiss_index is None:
            return
        
        # Train index if needed
        if not self.index_trained and hasattr(self.faiss_index, 'train'):
            # For IVF indices, we need enough training data
            if len(self.vectors) >= self.config.nlist:
                training_vectors = np.array(list(self.vectors.values()))
                self.faiss_index.train(training_vectors)
                self.index_trained = True
            else:
                return  # Wait for more vectors
        
        # Add vector
        vector_2d = vector.reshape(1, -1).astype(np.float32)
        self.faiss_index.add(vector_2d)
    
    async def _add_batch_to_faiss_index(self, vectors: np.ndarray):
        """Add batch of vectors to FAISS index"""
        if self.faiss_index is None:
            return
        
        # Train index if needed
        if not self.index_trained and hasattr(self.faiss_index, 'train'):
            if vectors.shape[0] >= self.config.nlist:
                self.faiss_index.train(vectors.astype(np.float32))
                self.index_trained = True
            else:
                return  # Wait for more vectors
        
        # Add vectors
        self.faiss_index.add(vectors.astype(np.float32))
    
    async def _search_faiss_index(self, query_vector: np.ndarray, 
                                top_k: int, similarity_threshold: float) -> List[MatchResult]:
        """Search using FAISS index"""
        if self.faiss_index is None or not self.index_trained:
            return []
        
        try:
            # Set search parameters for IVF indices
            if hasattr(self.faiss_index, 'nprobe'):
                self.faiss_index.nprobe = self.config.nprobe
            
            # Search
            query_2d = query_vector.reshape(1, -1).astype(np.float32)
            distances, indices = self.faiss_index.search(query_2d, top_k)
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # No more results
                    break
                
                # Convert distance to similarity (for L2 distance)
                similarity = 1 / (1 + distance)
                
                if similarity >= similarity_threshold:
                    vector_id = self.vector_ids[idx]
                    result = MatchResult(
                        vector_id=vector_id,
                        similarity_score=similarity,
                        distance=float(distance),
                        metadata=self.vector_metadata.get(vector_id, {})
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in FAISS search: {str(e)}")
            return []
    
    async def _search_custom_similarity(self, query_vector: np.ndarray,
                                      top_k: int, similarity_threshold: float,
                                      metric: SimilarityMetric) -> List[MatchResult]:
        """Search using custom similarity calculation"""
        results = []
        
        # Calculate similarities with all vectors
        similarity_tasks = []
        for vector_id in self.vector_ids:
            vector = self.vectors[vector_id]
            task = self.thread_pool.submit(
                self._calculate_similarity_sync, query_vector, vector, metric
            )
            similarity_tasks.append((vector_id, task))
        
        # Collect results
        for vector_id, task in similarity_tasks:
            try:
                similarity = task.result()
                if similarity >= similarity_threshold:
                    result = MatchResult(
                        vector_id=vector_id,
                        similarity_score=similarity,
                        distance=1.0 - similarity,
                        metadata=self.vector_metadata.get(vector_id, {})
                    )
                    results.append(result)
            except Exception as e:
                self.logger.warning(f"Error calculating similarity for {vector_id}: {str(e)}")
                continue
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
    
    def _calculate_similarity_sync(self, vector1: np.ndarray, vector2: np.ndarray, 
                                 metric: SimilarityMetric) -> float:
        """Synchronous similarity calculation for threading"""
        try:
            if metric == SimilarityMetric.COSINE:
                return 1 - cosine(vector1, vector2)
            elif metric == SimilarityMetric.EUCLIDEAN:
                distance = euclidean(vector1, vector2)
                return 1 / (1 + distance)
            elif metric == SimilarityMetric.DOT_PRODUCT:
                return np.dot(vector1, vector2)
            elif metric == SimilarityMetric.MANHATTAN:
                distance = np.sum(np.abs(vector1 - vector2))
                return 1 / (1 + distance)
            elif metric == SimilarityMetric.JACCARD:
                intersection = np.sum(np.minimum(vector1, vector2))
                union = np.sum(np.maximum(vector1, vector2))
                return intersection / union if union > 0 else 0.0
            else:
                return 0.0
        except:
            return 0.0
    
    def _get_cache_key(self, query_vector: np.ndarray, top_k: int, 
                      similarity_threshold: float, metric: SimilarityMetric) -> str:
        """Generate cache key for query"""
        vector_hash = hashlib.md5(query_vector.tobytes()).hexdigest()[:16]
        return f"vector_search:{vector_hash}:{top_k}:{similarity_threshold}:{metric.value}"
    
    async def _get_cached_results(self, cache_key: str) -> Optional[List[MatchResult]]:
        """Get cached search results"""
        try:
            if not self.redis_client:
                return None
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                results_data = json.loads(cached_data)
                return [
                    MatchResult(
                        vector_id=r['vector_id'],
                        similarity_score=r['similarity_score'],
                        distance=r['distance'],
                        metadata=r['metadata'],
                        match_timestamp=datetime.fromisoformat(r['match_timestamp'])
                    )
                    for r in results_data
                ]
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error getting cached results: {str(e)}")
            return None
    
    async def _cache_results(self, cache_key: str, results: List[MatchResult]):
        """Cache search results"""
        try:
            if not self.redis_client:
                return
            
            results_data = [
                {
                    'vector_id': r.vector_id,
                    'similarity_score': r.similarity_score,
                    'distance': r.distance,
                    'metadata': r.metadata,
                    'match_timestamp': r.match_timestamp.isoformat()
                }
                for r in results
            ]
            
            await self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(results_data)
            )
            
        except Exception as e:
            self.logger.warning(f"Error caching results: {str(e)}")
    
    async def _cache_vector(self, vector_id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        """Cache individual vector"""
        try:
            if not self.redis_client:
                return
            
            cache_key = f"vector:{vector_id}"
            vector_data = {
                'vector': vector.tolist(),
                'metadata': metadata,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(vector_data)
            )
            
        except Exception as e:
            self.logger.warning(f"Error caching vector {vector_id}: {str(e)}")
    
    async def _cache_vectors_batch(self, vector_ids: List[str], vectors: List[np.ndarray], 
                                 metadata_list: List[Dict[str, Any]]):
        """Cache batch of vectors"""
        try:
            if not self.redis_client:
                return
            
            pipe = self.redis_client.pipeline()
            timestamp = datetime.utcnow().isoformat()
            
            for vector_id, vector, metadata in zip(vector_ids, vectors, metadata_list):
                cache_key = f"vector:{vector_id}"
                vector_data = {
                    'vector': vector.tolist(),
                    'metadata': metadata,
                    'timestamp': timestamp
                }
                pipe.setex(cache_key, self.cache_ttl, json.dumps(vector_data))
            
            await pipe.execute()
            
        except Exception as e:
            self.logger.warning(f"Error caching vector batch: {str(e)}")
    
    async def _remove_cached_vector(self, vector_id: str):
        """Remove vector from cache"""
        try:
            if not self.redis_client:
                return
            
            cache_key = f"vector:{vector_id}"
            await self.redis_client.delete(cache_key)
            
        except Exception as e:
            self.logger.warning(f"Error removing cached vector {vector_id}: {str(e)}")
    
    async def close(self):
        """Cleanup resources"""
        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            self.logger.info("Vector matcher closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing vector matcher: {str(e)}")
