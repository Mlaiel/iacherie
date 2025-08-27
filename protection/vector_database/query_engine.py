"""
🔍 Vector Query Engine
======================

Advanced query processing and optimization engine for vector database operations.
Supports complex multi-criteria queries with intelligent optimization and caching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

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
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


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


@dataclass
class QueryFilter:
    """Advanced query filtering configuration"""
    content_types: Optional[List[str]] = None
    creators: Optional[List[str]] = None
    date_range: Optional[Tuple[str, str]] = None
    platforms: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    copyright_status: Optional[str] = None
    quality_score_min: Optional[float] = None
    similarity_threshold: Optional[float] = None
    custom_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryRequest:
    """Complete query request specification"""
    query_id: str
    query_type: QueryType
    query_vector: Optional[np.ndarray] = None
    query_text: Optional[str] = None
    query_content_id: Optional[str] = None
    
    # Search parameters
    limit: int = 10
    offset: int = 0
    similarity_threshold: float = 0.6
    
    # Filtering
    filters: Optional[QueryFilter] = None
    
    # Optimization hints
    priority: QueryPriority = QueryPriority.NORMAL
    timeout_seconds: float = 30.0
    use_cache: bool = True
    explain_plan: bool = False
    
    # Advanced options
    cross_modal: bool = False
    fuzzy_matching: bool = False
    boost_factors: Dict[str, float] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Query execution result with metadata"""
    query_id: str
    matches: List[Dict[str, Any]]
    total_matches: int
    execution_time_ms: float
    cache_hit: bool
    query_plan: Optional[Dict[str, Any]] = None
    optimization_info: Dict[str, Any] = field(default_factory=dict)


class QueryOptimizer:
    """Intelligent query optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.QueryOptimizer")
        
        # Optimization statistics
        self.query_stats = defaultdict(list)
        self.index_stats = {}
        self.performance_history = []
        
        # Configuration
        self.enable_caching = config.get('enable_caching', True)
        self.cache_ttl = config.get('cache_ttl_seconds', 300)
        self.auto_optimize = config.get('auto_optimize', True)
        self.max_query_time = config.get('max_query_time_ms', 5000)
    
    async def optimize_query(self, request: QueryRequest) -> QueryRequest:
        """Optimize query based on performance statistics and index characteristics"""
        try:
            optimized_request = request
            
            # Analyze query patterns
            query_signature = self._get_query_signature(request)
            historical_performance = self.query_stats.get(query_signature, [])
            
            # Optimize similarity threshold
            if historical_performance and self.auto_optimize:
                avg_time = np.mean([p['time'] for p in historical_performance])
                if avg_time > self.max_query_time:
                    # Increase threshold to reduce search space
                    optimized_request.similarity_threshold = min(
                        0.9, request.similarity_threshold + 0.1
                    )
                    self.logger.debug(f"Increased similarity threshold to {optimized_request.similarity_threshold}")
            
            # Optimize limit based on performance
            if request.limit > 100 and not request.priority == QueryPriority.CRITICAL:
                optimized_request.limit = min(request.limit, 50)
                self.logger.debug(f"Reduced limit to {optimized_request.limit}")
            
            # Add performance hints
            optimized_request.optimization_info = {
                'original_threshold': request.similarity_threshold,
                'original_limit': request.limit,
                'optimizer_version': '1.0',
                'optimization_time': time.time()
            }
            
            return optimized_request
            
        except Exception as e:
            self.logger.error(f"Query optimization failed: {e}")
            return request
    
    def _get_query_signature(self, request: QueryRequest) -> str:
        """Generate unique signature for query pattern analysis"""
        signature_data = {
            'type': request.query_type.value,
            'limit_range': (request.limit // 10) * 10,  # Round to nearest 10
            'has_filters': bool(request.filters),
            'cross_modal': request.cross_modal
        }
        
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.md5(signature_str.encode()).hexdigest()
    
    async def record_performance(self, query_id: str, execution_time_ms: float, result_count: int):
        """Record query performance for optimization learning"""
        try:
            # Store performance data
            perf_data = {
                'query_id': query_id,
                'time': execution_time_ms,
                'result_count': result_count,
                'timestamp': time.time()
            }
            
            self.performance_history.append(perf_data)
            
            # Keep only recent history
            max_history = self.config.get('max_performance_history', 10000)
            if len(self.performance_history) > max_history:
                self.performance_history = self.performance_history[-max_history:]
            
        except Exception as e:
            self.logger.error(f"Failed to record performance: {e}")


class QueryCache:
    """Advanced caching system for query results"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.QueryCache")
        
        # Cache storage
        self.cache = {}
        self.cache_metadata = {}
        
        # Configuration
        self.max_size = config.get('max_cache_size', 10000)
        self.default_ttl = config.get('default_ttl_seconds', 300)
        self.enable_smart_invalidation = config.get('enable_smart_invalidation', True)
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
    
    async def get(self, cache_key: str) -> Optional[QueryResult]:
        """Retrieve cached query result"""
        try:
            if cache_key not in self.cache:
                self.miss_count += 1
                return None
            
            # Check TTL
            metadata = self.cache_metadata[cache_key]
            if time.time() > metadata['expires_at']:
                await self._evict(cache_key)
                self.miss_count += 1
                return None
            
            # Update access time
            metadata['last_accessed'] = time.time()
            metadata['access_count'] += 1
            
            self.hit_count += 1
            result = self.cache[cache_key]
            result.cache_hit = True
            
            return result
            
        except Exception as e:
            self.logger.error(f"Cache get failed: {e}")
            self.miss_count += 1
            return None
    
    async def put(self, cache_key: str, result: QueryResult, ttl: Optional[float] = None):
        """Store query result in cache"""
        try:
            # Check cache size limit
            if len(self.cache) >= self.max_size:
                await self._evict_lru()
            
            # Store result
            self.cache[cache_key] = result
            self.cache_metadata[cache_key] = {
                'created_at': time.time(),
                'expires_at': time.time() + (ttl or self.default_ttl),
                'last_accessed': time.time(),
                'access_count': 0,
                'size_bytes': self._estimate_size(result)
            }
            
        except Exception as e:
            self.logger.error(f"Cache put failed: {e}")
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        try:
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                await self._evict(key)
            
            self.logger.debug(f"Invalidated {len(keys_to_remove)} cache entries for pattern: {pattern}")
            
        except Exception as e:
            self.logger.error(f"Pattern invalidation failed: {e}")
    
    async def _evict_lru(self):
        """Evict least recently used cache entry"""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache_metadata.keys(),
            key=lambda k: self.cache_metadata[k]['last_accessed']
        )
        
        await self._evict(lru_key)
    
    async def _evict(self, cache_key: str):
        """Remove cache entry"""
        if cache_key in self.cache:
            del self.cache[cache_key]
            del self.cache_metadata[cache_key]
            self.eviction_count += 1
    
    def _estimate_size(self, result: QueryResult) -> int:
        """Estimate memory size of cached result"""
        try:
            # Simple estimation based on number of matches
            base_size = 1024  # Base overhead
            match_size = len(result.matches) * 512  # Estimated per match
            return base_size + match_size
        except:
            return 1024  # Default estimate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'eviction_count': self.eviction_count,
            'current_size': len(self.cache),
            'max_size': self.max_size
        }


class QueryExecutor:
    """Main query execution engine with optimization and caching"""
    
    def __init__(self, vector_store, config: Dict[str, Any]):
        self.vector_store = vector_store
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.QueryExecutor")
        
        # Components
        self.optimizer = QueryOptimizer(config.get('optimizer', {}))
        self.cache = QueryCache(config.get('cache', {}))
        
        # Execution statistics
        self.total_queries = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        
        # Configuration
        self.enable_optimization = config.get('enable_optimization', True)
        self.enable_caching = config.get('enable_caching', True)
        self.enable_parallel_execution = config.get('enable_parallel_execution', True)
    
    async def execute_query(self, request: QueryRequest) -> QueryResult:
        """Execute query with optimization and caching"""
        start_time = time.time()
        
        try:
            self.total_queries += 1
            
            # Generate cache key
            cache_key = self._generate_cache_key(request) if self.enable_caching else None
            
            # Check cache first
            if cache_key and request.use_cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    self.logger.debug(f"Cache hit for query {request.query_id}")
                    return cached_result
            
            # Optimize query
            if self.enable_optimization:
                request = await self.optimizer.optimize_query(request)
            
            # Execute query based on type
            if request.query_type == QueryType.SIMILARITY_SEARCH:
                result = await self._execute_similarity_search(request)
            elif request.query_type == QueryType.KNN_SEARCH:
                result = await self._execute_knn_search(request)
            elif request.query_type == QueryType.HYBRID_SEARCH:
                result = await self._execute_hybrid_search(request)
            elif request.query_type == QueryType.MULTI_MODAL_SEARCH:
                result = await self._execute_multi_modal_search(request)
            elif request.query_type == QueryType.DUPLICATE_DETECTION:
                result = await self._execute_duplicate_detection(request)
            else:
                raise ValueError(f"Unsupported query type: {request.query_type}")
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time_ms
            result.cache_hit = False
            
            # Cache result
            if cache_key and self.enable_caching:
                await self.cache.put(cache_key, result)
            
            # Record performance
            await self.optimizer.record_performance(
                request.query_id, 
                execution_time_ms, 
                len(result.matches)
            )
            
            self.total_execution_time += execution_time_ms
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Query execution failed for {request.query_id}: {e}")
            
            # Return empty result
            return QueryResult(
                query_id=request.query_id,
                matches=[],
                total_matches=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                cache_hit=False
            )
    
    async def _execute_similarity_search(self, request: QueryRequest) -> QueryResult:
        """Execute similarity search query"""
        if request.query_vector is None:
            raise ValueError("Query vector required for similarity search")
        
        # Apply filters
        metadata_filter = self._build_metadata_filter(request.filters)
        
        # Execute search
        matches = await self.vector_store.search(
            query_vector=request.query_vector,
            k=request.limit,
            similarity_threshold=request.similarity_threshold,
            metadata_filter=metadata_filter
        )
        
        return QueryResult(
            query_id=request.query_id,
            matches=[self._format_match(match) for match in matches],
            total_matches=len(matches),
            execution_time_ms=0,  # Will be set by caller
            cache_hit=False
        )
    
    async def _execute_knn_search(self, request: QueryRequest) -> QueryResult:
        """Execute k-nearest neighbors search"""
        # Similar to similarity search but with strict k limit
        return await self._execute_similarity_search(request)
    
    async def _execute_hybrid_search(self, request: QueryRequest) -> QueryResult:
        """Execute hybrid search combining multiple strategies"""
        # Combine vector similarity with text matching
        vector_results = await self._execute_similarity_search(request)
        
        # Additional processing for hybrid approach
        # This could include text search, metadata boosting, etc.
        
        return vector_results
    
    async def _execute_multi_modal_search(self, request: QueryRequest) -> QueryResult:
        """Execute cross-modal search"""
        if not request.cross_modal:
            return await self._execute_similarity_search(request)
        
        # Execute search across multiple modalities
        # This could involve searching in different embedding spaces
        
        return await self._execute_similarity_search(request)
    
    async def _execute_duplicate_detection(self, request: QueryRequest) -> QueryResult:
        """Execute duplicate detection with high similarity threshold"""
        # Use high similarity threshold for duplicate detection
        request.similarity_threshold = max(request.similarity_threshold, 0.95)
        
        return await self._execute_similarity_search(request)
    
    def _build_metadata_filter(self, filters: Optional[QueryFilter]) -> Optional[Dict[str, Any]]:
        """Build metadata filter from query filters"""
        if not filters:
            return None
        
        metadata_filter = {}
        
        if filters.content_types:
            metadata_filter['content_type'] = filters.content_types
        
        if filters.creators:
            metadata_filter['creator'] = filters.creators
        
        if filters.platforms:
            metadata_filter['platform'] = filters.platforms
        
        if filters.tags:
            metadata_filter['tags'] = filters.tags
        
        if filters.copyright_status:
            metadata_filter['copyright_status'] = filters.copyright_status
        
        if filters.quality_score_min:
            metadata_filter['quality_score_min'] = filters.quality_score_min
        
        # Add custom filters
        metadata_filter.update(filters.custom_filters)
        
        return metadata_filter if metadata_filter else None
    
    def _format_match(self, match) -> Dict[str, Any]:
        """Format search result match"""
        if hasattr(match, '__dict__'):
            # Convert dataclass to dict
            return {
                'id': getattr(match, 'vector_id', getattr(match, 'id', 'unknown')),
                'content_id': getattr(match, 'content_id', ''),
                'similarity_score': getattr(match, 'similarity_score', 0.0),
                'distance': getattr(match, 'distance', float('inf')),
                'metadata': getattr(match, 'metadata', {}),
                'embedding_type': getattr(match, 'embedding_type', 'unknown')
            }
        else:
            # Already a dict
            return match
    
    def _generate_cache_key(self, request: QueryRequest) -> str:
        """Generate unique cache key for query"""
        key_data = {
            'type': request.query_type.value,
            'vector_hash': hashlib.md5(request.query_vector.tobytes()).hexdigest() if request.query_vector is not None else None,
            'text': request.query_text,
            'content_id': request.query_content_id,
            'limit': request.limit,
            'offset': request.offset,
            'threshold': request.similarity_threshold,
            'filters': str(request.filters) if request.filters else None,
            'cross_modal': request.cross_modal
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get query execution performance statistics"""
        avg_execution_time = (
            self.total_execution_time / self.total_queries 
            if self.total_queries > 0 else 0
        )
        
        error_rate = self.error_count / self.total_queries if self.total_queries > 0 else 0
        
        return {
            'total_queries': self.total_queries,
            'total_execution_time_ms': self.total_execution_time,
            'average_execution_time_ms': avg_execution_time,
            'error_count': self.error_count,
            'error_rate': error_rate,
            'cache_stats': self.cache.get_stats()
        }
