"""🔎 Search Operations & Query Engine
====================================

Advanced similarity search engine and query processing system for content 
fingerprint matching. Implements multiple similarity algorithms with 
configurable thresholds and intelligent query optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import time
import statistics
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.preprocessing import normalize
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# SIMILARITY SEARCH ENGINE SECTION
# =============================================================================

class SimilarityMetric(Enum):
    """Similarity metrics supported"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    PEARSON = "pearson"


class MatchType(Enum):
    """Types of content matches"""
    EXACT = "exact"              # 98-100% similarity
    NEAR_DUPLICATE = "near_duplicate"  # 90-98% similarity
    SIMILAR = "similar"          # 75-90% similarity
    RELATED = "related"          # 60-75% similarity
    WEAK = "weak"               # 40-60% similarity


@dataclass
class SimilarityMatch:
    """Individual similarity match result"""
    target_id: str
    source_id: str
    similarity_score: float
    match_type: MatchType
    confidence: float
    algorithm_used: SimilarityMetric
    metadata: Dict[str, Any] = field(default_factory=dict)
    computation_time_ms: float = 0.0


@dataclass
class SearchRequest:
    """Search request configuration"""
    query_vector: np.ndarray
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    k: int = 10
    similarity_threshold: float = 0.6
    include_metadata: bool = True
    metadata_filters: Optional[Dict[str, Any]] = None
    max_computation_time_ms: Optional[float] = None


@dataclass
class SearchResponse:
    """Search operation response"""
    matches: List[SimilarityMatch]
    total_matches_found: int
    search_time_ms: float
    algorithm_used: SimilarityMetric
    query_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimilaritySearchEngine:
    """
    Advanced similarity search engine for content fingerprint matching.
    Implements multiple similarity algorithms with configurable thresholds.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize similarity search engine.
        
        Args:
            config: Search engine configuration
        """
        self.config = config or {}
        self.default_metric = SimilarityMetric.COSINE
        self.similarity_thresholds = {
            MatchType.EXACT: 0.98,
            MatchType.NEAR_DUPLICATE: 0.90,
            MatchType.SIMILAR: 0.75,
            MatchType.RELATED: 0.60,
            MatchType.WEAK: 0.40
        }
        
        # Performance monitoring
        self.search_stats = {
            'total_searches': 0,
            'avg_search_time_ms': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Simple LRU cache for repeated queries
        self.query_cache = {}
        self.cache_max_size = self.config.get('cache_max_size', 1000)
        
        # Thread executor for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=self.config.get('max_workers', 4))
        
        self.logger = logging.getLogger(f"{__name__}.SimilaritySearchEngine")
        self.logger.info("Similarity search engine initialized")
    
    async def search(
        self, 
        query_vector: np.ndarray, 
        target_vectors: List[Tuple[str, np.ndarray]], 
        request: SearchRequest
    ) -> SearchResponse:
        """
        Perform similarity search against target vectors.
        
        Args:
            query_vector: Query vector for search
            target_vectors: List of (id, vector) tuples to search against
            request: Search request configuration
            
        Returns:
            Search response with results
        """
        start_time = time.time()
        query_id = self._generate_query_id(query_vector, request)
        
        try:
            # Check cache first
            cached_result = self._check_cache(query_id)
            if cached_result:
                self.search_stats['cache_hits'] += 1
                self.logger.debug(f"Cache hit for query {query_id}")
                return cached_result
            
            self.search_stats['cache_misses'] += 1
            
            # Perform similarity computation
            matches = await self._compute_similarities(
                query_vector, target_vectors, request
            )
            
            # Filter and rank results
            filtered_matches = self._filter_and_rank_matches(matches, request)
            
            # Create response
            search_time_ms = (time.time() - start_time) * 1000
            response = SearchResponse(
                matches=filtered_matches[:request.k],
                total_matches_found=len(filtered_matches),
                search_time_ms=search_time_ms,
                algorithm_used=request.similarity_metric,
                query_id=query_id
            )
            
            # Cache result
            self._cache_result(query_id, response)
            
            # Update statistics
            self._update_search_stats(search_time_ms)
            
            self.logger.debug(f"Search completed: {len(filtered_matches)} matches in {search_time_ms:.2f}ms")
            return response
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return SearchResponse(
                matches=[],
                total_matches_found=0,
                search_time_ms=(time.time() - start_time) * 1000,
                algorithm_used=request.similarity_metric,
                query_id=query_id,
                metadata={'error': str(e)}
            )
    
    async def _compute_similarities(
        self, 
        query_vector: np.ndarray, 
        target_vectors: List[Tuple[str, np.ndarray]], 
        request: SearchRequest
    ) -> List[SimilarityMatch]:
        """Compute similarities between query and target vectors"""
        
        # Prepare vectors for computation
        query = query_vector.astype(np.float32).reshape(1, -1)
        target_ids = [item[0] for item in target_vectors]
        targets = np.stack([item[1].astype(np.float32) for item in target_vectors])
        
        # Compute similarities based on metric
        if request.similarity_metric == SimilarityMetric.COSINE:
            similarities = await self._compute_cosine_similarities(query, targets)
        elif request.similarity_metric == SimilarityMetric.EUCLIDEAN:
            similarities = await self._compute_euclidean_similarities(query, targets)
        elif request.similarity_metric == SimilarityMetric.DOT_PRODUCT:
            similarities = await self._compute_dot_product_similarities(query, targets)
        elif request.similarity_metric == SimilarityMetric.MANHATTAN:
            similarities = await self._compute_manhattan_similarities(query, targets)
        else:
            # Fallback to cosine
            similarities = await self._compute_cosine_similarities(query, targets)
        
        # Create match objects
        matches = []
        for i, (target_id, similarity) in enumerate(zip(target_ids, similarities)):
            match_type = self._determine_match_type(similarity)
            confidence = self._calculate_confidence(similarity, request.similarity_metric)
            
            match = SimilarityMatch(
                target_id=target_id,
                source_id="query",
                similarity_score=float(similarity),
                match_type=match_type,
                confidence=confidence,
                algorithm_used=request.similarity_metric
            )
            matches.append(match)
        
        return matches
    
    async def _compute_cosine_similarities(self, query: np.ndarray, targets: np.ndarray) -> np.ndarray:
        """Compute cosine similarities"""
        if SKLEARN_AVAILABLE:
            loop = asyncio.get_event_loop()
            similarities = await loop.run_in_executor(
                self.executor, cosine_similarity, query, targets
            )
            return similarities[0]
        else:
            # Manual implementation
            query_norm = np.linalg.norm(query, axis=1, keepdims=True)
            targets_norm = np.linalg.norm(targets, axis=1, keepdims=True)
            
            dot_products = np.dot(query, targets.T)[0]
            similarities = dot_products / (query_norm[0] * targets_norm.flatten())
            
            return similarities
    
    async def _compute_euclidean_similarities(self, query: np.ndarray, targets: np.ndarray) -> np.ndarray:
        """Compute Euclidean distance-based similarities"""
        if SKLEARN_AVAILABLE:
            loop = asyncio.get_event_loop()
            distances = await loop.run_in_executor(
                self.executor, euclidean_distances, query, targets
            )
            # Convert distances to similarities (0-1 range)
            similarities = 1.0 / (1.0 + distances[0])
            return similarities
        else:
            # Manual implementation
            differences = targets - query
            distances = np.sqrt(np.sum(differences**2, axis=1))
            similarities = 1.0 / (1.0 + distances)
            return similarities
    
    async def _compute_dot_product_similarities(self, query: np.ndarray, targets: np.ndarray) -> np.ndarray:
        """Compute dot product similarities"""
        dot_products = np.dot(query, targets.T)[0]
        return dot_products
    
    async def _compute_manhattan_similarities(self, query: np.ndarray, targets: np.ndarray) -> np.ndarray:
        """Compute Manhattan distance-based similarities"""
        distances = np.sum(np.abs(targets - query), axis=1)
        similarities = 1.0 / (1.0 + distances)
        return similarities
    
    def _determine_match_type(self, similarity: float) -> MatchType:
        """Determine match type based on similarity score"""
        if similarity >= self.similarity_thresholds[MatchType.EXACT]:
            return MatchType.EXACT
        elif similarity >= self.similarity_thresholds[MatchType.NEAR_DUPLICATE]:
            return MatchType.NEAR_DUPLICATE
        elif similarity >= self.similarity_thresholds[MatchType.SIMILAR]:
            return MatchType.SIMILAR
        elif similarity >= self.similarity_thresholds[MatchType.RELATED]:
            return MatchType.RELATED
        else:
            return MatchType.WEAK
    
    def _calculate_confidence(self, similarity: float, metric: SimilarityMetric) -> float:
        """Calculate confidence score for a similarity match"""
        # Confidence is based on similarity score and metric reliability
        base_confidence = similarity
        
        # Adjust for metric characteristics
        if metric == SimilarityMetric.COSINE:
            # Cosine is reliable for normalized vectors
            metric_factor = 1.0
        elif metric == SimilarityMetric.EUCLIDEAN:
            # Euclidean can be sensitive to scale
            metric_factor = 0.9
        elif metric == SimilarityMetric.DOT_PRODUCT:
            # Dot product depends on vector magnitudes
            metric_factor = 0.85
        else:
            metric_factor = 0.8
        
        return min(base_confidence * metric_factor, 1.0)
    
    def _filter_and_rank_matches(self, matches: List[SimilarityMatch], request: SearchRequest) -> List[SimilarityMatch]:
        """Filter and rank matches based on request criteria"""
        # Filter by similarity threshold
        filtered = [
            match for match in matches 
            if match.similarity_score >= request.similarity_threshold
        ]
        
        # Sort by similarity score (descending)
        filtered.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return filtered
    
    def _generate_query_id(self, query_vector: np.ndarray, request: SearchRequest) -> str:
        """Generate unique query ID for caching"""
        query_hash = hashlib.md5(query_vector.tobytes()).hexdigest()[:8]
        request_hash = hashlib.md5(
            f"{request.similarity_metric.value}_{request.k}_{request.similarity_threshold}".encode()
        ).hexdigest()[:8]
        return f"q_{query_hash}_{request_hash}"
    
    def _check_cache(self, query_id: str) -> Optional[SearchResponse]:
        """Check if query result is cached"""
        return self.query_cache.get(query_id)
    
    def _cache_result(self, query_id: str, response: SearchResponse):
        """Cache query result"""
        if len(self.query_cache) >= self.cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[query_id] = response
    
    def _update_search_stats(self, search_time_ms: float):
        """Update search performance statistics"""
        self.search_stats['total_searches'] += 1
        
        # Update rolling average
        current_avg = self.search_stats['avg_search_time_ms']
        total_searches = self.search_stats['total_searches']
        
        new_avg = ((current_avg * (total_searches - 1)) + search_time_ms) / total_searches
        self.search_stats['avg_search_time_ms'] = new_avg
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search performance statistics"""
        cache_total = self.search_stats['cache_hits'] + self.search_stats['cache_misses']
        cache_hit_rate = (self.search_stats['cache_hits'] / cache_total) if cache_total > 0 else 0.0
        
        return {
            **self.search_stats,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.query_cache)
        }
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        self.logger.info("Query cache cleared")


# =============================================================================
# QUERY ENGINE SECTION
# =============================================================================

class QueryType(Enum):
    """Supported query types"""
    SIMILARITY_SEARCH = "similarity_search"
    RANGE_SEARCH = "range_search" 
    KNN_SEARCH = "knn_search"
    HYBRID_SEARCH = "hybrid_search"
    MULTI_MODAL_SEARCH = "multi_modal_search"
    CONTENT_MATCHING = "content_matching"
    DUPLICATE_DETECTION = "duplicate_detection"


class QueryPriority(Enum):
    """Query execution priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class QueryStatus(Enum):
    """Query execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueryRequest:
    """Advanced query request with optimization parameters"""
    query_id: str
    query_type: QueryType
    query_vector: np.ndarray
    parameters: Dict[str, Any]
    priority: QueryPriority = QueryPriority.NORMAL
    max_execution_time_ms: Optional[float] = None
    enable_optimization: bool = True
    enable_caching: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Query execution result"""
    query_id: str
    status: QueryStatus
    results: List[Any]
    execution_time_ms: float
    optimization_applied: bool = False
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class QueryOptimizer:
    """Query optimization engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.optimization_rules = {}
        self.performance_history = defaultdict(list)
        
    async def optimize_query(self, request: QueryRequest) -> QueryRequest:
        """Apply optimization rules to query request"""
        if not request.enable_optimization:
            return request
        
        optimized_request = request
        
        # Apply query-type specific optimizations
        if request.query_type == QueryType.KNN_SEARCH:
            optimized_request = await self._optimize_knn_query(optimized_request)
        elif request.query_type == QueryType.SIMILARITY_SEARCH:
            optimized_request = await self._optimize_similarity_query(optimized_request)
        
        return optimized_request
    
    async def _optimize_knn_query(self, request: QueryRequest) -> QueryRequest:
        """Optimize KNN search query"""
        # Adjust k based on performance history
        avg_time = np.mean(self.performance_history[request.query_type.value]) if self.performance_history[request.query_type.value] else 0
        
        if avg_time > 1000:  # If queries are slow, reduce k
            current_k = request.parameters.get('k', 10)
            request.parameters['k'] = max(current_k * 0.8, 5)
        
        return request
    
    async def _optimize_similarity_query(self, request: QueryRequest) -> QueryRequest:
        """Optimize similarity search query"""
        # Adjust similarity threshold for better performance
        if 'similarity_threshold' not in request.parameters:
            request.parameters['similarity_threshold'] = 0.7  # Set reasonable default
        
        return request


class QueryCache:
    """Advanced caching system for query results"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        
    def get(self, query_id: str) -> Optional[QueryResult]:
        """Get cached query result"""
        if query_id not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.access_times[query_id] > self.ttl_seconds:
            del self.cache[query_id]
            del self.access_times[query_id]
            return None
        
        # Update access time
        self.access_times[query_id] = time.time()
        return self.cache[query_id]
    
    def put(self, query_id: str, result: QueryResult):
        """Cache query result"""
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[query_id] = result
        self.access_times[query_id] = time.time()


class VectorQueryEngine:
    """
    Advanced query processing and optimization engine for vector database operations.
    Supports complex multi-criteria queries with intelligent optimization and caching.
    """
    
    def __init__(self, vector_store, config: Dict[str, Any] = None):
        """
        Initialize query engine.
        
        Args:
            vector_store: Vector storage backend
            config: Query engine configuration
        """
        self.vector_store = vector_store
        self.config = config or {}
        
        # Initialize components
        self.similarity_engine = SimilaritySearchEngine(self.config.get('similarity', {}))
        self.optimizer = QueryOptimizer(self.config.get('optimizer', {}))
        
        cache_config = self.config.get('cache', {})
        self.cache = QueryCache(
            max_size=cache_config.get('max_cache_size', 10000),
            ttl_seconds=cache_config.get('default_ttl_seconds', 300)
        )
        
        # Query queue for priority handling
        self.query_queue = asyncio.PriorityQueue()
        self.active_queries = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_queries': 0,
            'avg_execution_time_ms': 0.0,
            'cache_hit_rate': 0.0,
            'optimization_success_rate': 0.0
        }
        
        self.logger = logging.getLogger(f"{__name__}.VectorQueryEngine")
        self.logger.info("Vector query engine initialized")
    
    async def execute_query(self, request: QueryRequest) -> QueryResult:
        """
        Execute a query request with optimization and caching.
        
        Args:
            request: Query request to execute
            
        Returns:
            Query execution result
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if request.enable_caching:
                cached_result = self.cache.get(request.query_id)
                if cached_result:
                    cached_result.cache_hit = True
                    self.logger.debug(f"Cache hit for query {request.query_id}")
                    return cached_result
            
            # Optimize query
            optimized_request = request
            if request.enable_optimization:
                optimized_request = await self.optimizer.optimize_query(request)
            
            # Execute query based on type
            results = await self._execute_query_by_type(optimized_request)
            
            # Create result
            execution_time_ms = (time.time() - start_time) * 1000
            result = QueryResult(
                query_id=request.query_id,
                status=QueryStatus.COMPLETED,
                results=results,
                execution_time_ms=execution_time_ms,
                optimization_applied=request.enable_optimization,
                cache_hit=False
            )
            
            # Cache result
            if request.enable_caching:
                self.cache.put(request.query_id, result)
            
            # Update metrics
            self._update_performance_metrics(execution_time_ms)
            
            self.logger.debug(f"Query {request.query_id} completed in {execution_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_result = QueryResult(
                query_id=request.query_id,
                status=QueryStatus.FAILED,
                results=[],
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )
            
            self.logger.error(f"Query {request.query_id} failed: {e}")
            return error_result
    
    async def _execute_query_by_type(self, request: QueryRequest) -> List[Any]:
        """Execute query based on type"""
        if request.query_type == QueryType.SIMILARITY_SEARCH:
            return await self._execute_similarity_search(request)
        elif request.query_type == QueryType.KNN_SEARCH:
            return await self._execute_knn_search(request)
        elif request.query_type == QueryType.RANGE_SEARCH:
            return await self._execute_range_search(request)
        elif request.query_type == QueryType.DUPLICATE_DETECTION:
            return await self._execute_duplicate_detection(request)
        else:
            raise ValueError(f"Unsupported query type: {request.query_type}")
    
    async def _execute_similarity_search(self, request: QueryRequest) -> List[Any]:
        """Execute similarity search query"""
        search_request = SearchRequest(
            query_vector=request.query_vector,
            similarity_metric=SimilarityMetric(request.parameters.get('similarity_metric', 'cosine')),
            k=request.parameters.get('k', 10),
            similarity_threshold=request.parameters.get('similarity_threshold', 0.6),
            include_metadata=request.parameters.get('include_metadata', True),
            metadata_filters=request.parameters.get('metadata_filters')
        )
        
        # For this implementation, we'll return a placeholder
        # In a real implementation, you'd integrate with the vector store
        return []
    
    async def _execute_knn_search(self, request: QueryRequest) -> List[Any]:
        """Execute K-nearest neighbors search"""
        from .vector_backends import SearchQuery
        
        query = SearchQuery(
            query_vector=request.query_vector,
            k=request.parameters.get('k', 10),
            similarity_threshold=request.parameters.get('similarity_threshold'),
            metadata_filters=request.parameters.get('metadata_filters')
        )
        
        results = await self.vector_store.search(query)
        return results
    
    async def _execute_range_search(self, request: QueryRequest) -> List[Any]:
        """Execute range search query"""
        # Placeholder implementation
        return []
    
    async def _execute_duplicate_detection(self, request: QueryRequest) -> List[Any]:
        """Execute duplicate detection query"""
        # High similarity threshold for duplicate detection
        search_request = SearchRequest(
            query_vector=request.query_vector,
            similarity_metric=SimilarityMetric.COSINE,
            k=request.parameters.get('k', 100),
            similarity_threshold=0.95,  # High threshold for duplicates
            include_metadata=True
        )
        
        # Implementation would involve comparing against existing vectors
        return []
    
    def _update_performance_metrics(self, execution_time_ms: float):
        """Update performance metrics"""
        self.performance_metrics['total_queries'] += 1
        
        # Update rolling average
        current_avg = self.performance_metrics['avg_execution_time_ms']
        total_queries = self.performance_metrics['total_queries']
        
        new_avg = ((current_avg * (total_queries - 1)) + execution_time_ms) / total_queries
        self.performance_metrics['avg_execution_time_ms'] = new_avg
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get query engine performance metrics"""
        return {
            **self.performance_metrics,
            'cache_size': len(self.cache.cache),
            'active_queries': len(self.active_queries)
        }
    
    async def clear_cache(self):
        """Clear query cache"""
        self.cache.cache.clear()
        self.cache.access_times.clear()
        self.logger.info("Query cache cleared")


# Export all classes and functions
__all__ = [
    # Similarity search exports
    'SimilarityMetric',
    'MatchType', 
    'SimilarityMatch',
    'SearchRequest',
    'SearchResponse',
    'SimilaritySearchEngine',
    
    # Query engine exports
    'QueryType',
    'QueryPriority',
    'QueryStatus',
    'QueryRequest',
    'QueryResult',
    'QueryOptimizer',
    'QueryCache',
    'VectorQueryEngine'
]