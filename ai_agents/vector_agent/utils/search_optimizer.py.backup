"""Search Optimizer - Intelligent Vector Search Performance Enhancement

Ultra-advanced search optimization engine providing intelligent caching,
query optimization, and result enhancement for vector similarity operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""
import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, OrderedDict
import heapq
from concurrent.futures import ThreadPoolExecutor

from .models import VectorSearchRequest, VectorSearchResult, VectorMetrics
from .config import VectorConfig
from .exceptions import VectorProcessingError, SearchOptimizationError

logger = logging.getLogger(__name__)


@dataclass
class QueryPerformanceMetric:
    """Performance metrics for search queries"""
    query_hash: str
    execution_time: float
    result_count: int
    cache_hit: bool
    optimization_applied: bool
    timestamp: datetime
    content_type: str
    similarity_threshold: float


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    query_hash: str
    results: List[VectorSearchResult]
    created_at: datetime
    access_count: int
    last_accessed: datetime
    size_bytes: int
    ttl_seconds: int


class QueryCache:
    """Intelligent query result caching system"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_size_bytes": 0
        }
    
    def _generate_query_hash(self, request: VectorSearchRequest) -> str:
        """Generate unique hash for search request"""
        # Include relevant parameters that affect results
        query_data = {
            "query_vector_hash": hashlib.md5(np.array(request.query_vector).tobytes()).hexdigest()[:16],
            "content_type": request.content_type,
            "max_results": request.max_results,
            "similarity_threshold": request.similarity_threshold,
            "search_parameters": request.search_parameters
        }
        
        query_string = json.dumps(query_data, sort_keys=True)
        return hashlib.sha256(query_string.encode()).hexdigest()[:32]
    
    def get(self, request: VectorSearchRequest) -> Optional[List[VectorSearchResult]]:
        """Get cached results if available and valid"""
        query_hash = self._generate_query_hash(request)
        
        if query_hash in self.cache:
            entry = self.cache[query_hash]
            
            # Check TTL
            if self._is_entry_valid(entry):
                # Move to end (LRU)
                self.cache.move_to_end(query_hash)
                
                # Update access metrics
                entry.access_count += 1
                entry.last_accessed = datetime.now(timezone.utc)
                
                self.cache_stats["hits"] += 1
                return entry.results
            else:
                # Remove expired entry
                self.remove(query_hash)
        
        self.cache_stats["misses"] += 1
        return None
    
    def put(self, request: VectorSearchRequest, results: List[VectorSearchResult], 
            ttl: Optional[int] = None) -> None:
        """Cache search results"""
        query_hash = self._generate_query_hash(request)
        
        # Calculate entry size
        entry_size = self._estimate_entry_size(results)
        
        # Check if we need to evict entries
        while len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        # Create cache entry
        entry = CacheEntry(
            query_hash=query_hash,
            results=results,
            created_at=datetime.now(timezone.utc),
            access_count=0,
            last_accessed=datetime.now(timezone.utc),
            size_bytes=entry_size,
            ttl_seconds=ttl or self.default_ttl
        )
        
        self.cache[query_hash] = entry
        self.cache_stats["total_size_bytes"] += entry_size
    
    def remove(self, query_hash: str) -> None:
        """Remove entry from cache"""
        if query_hash in self.cache:
            entry = self.cache.pop(query_hash)
            self.cache_stats["total_size_bytes"] -= entry.size_bytes
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_size_bytes": 0
        }
    
    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        age = (datetime.now(timezone.utc) - entry.created_at).total_seconds()
        return age < entry.ttl_seconds
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry"""
        if self.cache:
            query_hash, entry = self.cache.popitem(last=False)
            self.cache_stats["total_size_bytes"] -= entry.size_bytes
            self.cache_stats["evictions"] += 1
    
    def _estimate_entry_size(self, results: List[VectorSearchResult]) -> int:
        """Estimate memory size of cache entry"""
        # Basic estimation: assume ~1KB per result
        base_size = len(results) * 1024
        
        # Add size for metadata
        for result in results:
            if result.metadata:
                metadata_size = len(str(result.metadata)) * 2  # Rough estimation
                base_size += metadata_size
        
        return base_size
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "total_size_mb": self.cache_stats["total_size_bytes"] / (1024 * 1024),
            **self.cache_stats
        }


class QueryOptimizer:
    """Intelligent query optimization engine"""
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.performance_history: List[QueryPerformanceMetric] = []
        self.optimization_rules: Dict[str, Any] = self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self) -> Dict[str, Any]:
        """Initialize optimization rules based on content types and patterns"""
        return {
            "similarity_threshold_adjustment": {
                "audio": {"min": 0.65, "max": 0.95, "optimal": 0.80},
                "video": {"min": 0.70, "max": 0.98, "optimal": 0.85},
                "image": {"min": 0.75, "max": 0.95, "optimal": 0.85},
                "text": {"min": 0.60, "max": 0.90, "optimal": 0.75}
            },
            "max_results_optimization": {
                "performance_threshold_ms": 100,
                "max_results_limit": 1000,
                "optimal_range": {"min": 10, "max": 50}
            },
            "content_type_specific": {
                "audio": {"preferred_algorithms": ["cosine", "euclidean"]},
                "video": {"preferred_algorithms": ["cosine", "manhattan"]},
                "image": {"preferred_algorithms": ["cosine", "euclidean", "jaccard"]},
                "text": {"preferred_algorithms": ["cosine", "pearson"]}
            }
        }
    
    def optimize_search_request(self, request: VectorSearchRequest) -> VectorSearchRequest:
        """Optimize search request based on historical performance"""
        optimized_request = VectorSearchRequest(
            query_id=request.query_id,
            query_vector=request.query_vector,
            content_type=request.content_type,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold,
            search_parameters=request.search_parameters.copy() if request.search_parameters else {}
        )
        
        # Apply optimization rules
        optimized_request = self._optimize_similarity_threshold(optimized_request)
        optimized_request = self._optimize_max_results(optimized_request)
        optimized_request = self._optimize_search_parameters(optimized_request)
        
        return optimized_request
    
    def _optimize_similarity_threshold(self, request: VectorSearchRequest) -> VectorSearchRequest:
        """Optimize similarity threshold based on content type and history"""
        content_type = request.content_type
        current_threshold = request.similarity_threshold
        
        if content_type in self.optimization_rules["similarity_threshold_adjustment"]:
            rules = self.optimization_rules["similarity_threshold_adjustment"][content_type]
            optimal_threshold = rules["optimal"]
            
            # Analyze historical performance for this content type
            historical_performance = self._get_historical_performance(content_type)
            
            if historical_performance:
                # Adjust based on performance patterns
                avg_execution_time = np.mean([h.execution_time for h in historical_performance])
                
                if avg_execution_time > 50:  # ms
                    # If queries are slow, increase threshold to reduce results
                    optimal_threshold = min(rules["max"], optimal_threshold + 0.05)
                elif avg_execution_time < 10:  # ms
                    # If queries are fast, decrease threshold for more results
                    optimal_threshold = max(rules["min"], optimal_threshold - 0.05)
            
            # Apply optimization with smoothing
            new_threshold = (current_threshold * 0.7) + (optimal_threshold * 0.3)
            request.similarity_threshold = max(rules["min"], min(rules["max"], new_threshold))
        
        return request
    
    def _optimize_max_results(self, request: VectorSearchRequest) -> VectorSearchRequest:
        """Optimize maximum results based on performance targets"""
        rules = self.optimization_rules["max_results_optimization"]
        current_max = request.max_results
        
        # Get recent performance for similar queries
        recent_performance = self._get_recent_performance(request.content_type, limit=10)
        
        if recent_performance:
            avg_time = np.mean([p.execution_time for p in recent_performance])
            avg_results = np.mean([p.result_count for p in recent_performance])
            
            # If queries are slow and returning many results, reduce max_results
            if avg_time > rules["performance_threshold_ms"] and avg_results > rules["optimal_range"]["max"]:
                new_max = max(rules["optimal_range"]["min"], int(current_max * 0.8))
                request.max_results = new_max
            
            # If queries are fast and not returning enough results, increase max_results
            elif avg_time < rules["performance_threshold_ms"] / 2 and avg_results < rules["optimal_range"]["min"]:
                new_max = min(rules["max_results_limit"], int(current_max * 1.2))
                request.max_results = new_max
        
        return request
    
    def _optimize_search_parameters(self, request: VectorSearchRequest) -> VectorSearchRequest:
        """Optimize additional search parameters"""
        content_type = request.content_type
        
        if content_type in self.optimization_rules["content_type_specific"]:
            content_rules = self.optimization_rules["content_type_specific"][content_type]
            
            # Set preferred algorithms if not specified
            if "preferred_algorithms" not in request.search_parameters:
                request.search_parameters["preferred_algorithms"] = content_rules["preferred_algorithms"]
            
            # Add content-type specific optimizations
            request.search_parameters["optimization_applied"] = True
            request.search_parameters["optimized_at"] = datetime.now(timezone.utc).isoformat()
        
        return request
    
    def record_performance(self, request: VectorSearchRequest, execution_time: float,
                          result_count: int, cache_hit: bool = False) -> None:
        """Record query performance for future optimization"""
        metric = QueryPerformanceMetric(
            query_hash=self._generate_query_hash(request),
            execution_time=execution_time,
            result_count=result_count,
            cache_hit=cache_hit,
            optimization_applied=request.search_parameters.get("optimization_applied", False),
            timestamp=datetime.now(timezone.utc),
            content_type=request.content_type,
            similarity_threshold=request.similarity_threshold
        )
        
        self.performance_history.append(metric)
        
        # Keep only recent history to prevent memory growth
        max_history = self.config.max_performance_history
        if len(self.performance_history) > max_history:
            self.performance_history = self.performance_history[-max_history:]
    
    def _generate_query_hash(self, request: VectorSearchRequest) -> str:
        """Generate hash for query tracking"""
        return hashlib.md5(f"{request.content_type}_{request.similarity_threshold}_{request.max_results}".encode()).hexdigest()[:16]
    
    def _get_historical_performance(self, content_type: str, days: int = 7) -> List[QueryPerformanceMetric]:
        """Get historical performance metrics for content type"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        return [
            metric for metric in self.performance_history
            if metric.content_type == content_type and metric.timestamp > cutoff_date
        ]
    
    def _get_recent_performance(self, content_type: str, limit: int = 10) -> List[QueryPerformanceMetric]:
        """Get recent performance metrics"""
        content_metrics = [
            metric for metric in self.performance_history
            if metric.content_type == content_type
        ]
        
        # Return most recent metrics
        return sorted(content_metrics, key=lambda x: x.timestamp, reverse=True)[:limit]


class ResultEnhancer:
    """Advanced result enhancement and post-processing"""
    
    def __init__(self, config: VectorConfig):
        self.config = config
    
    def enhance_results(self, results: List[VectorSearchResult], 
                       request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Enhance search results with additional processing"""
        try:
            enhanced_results = []
            
            for result in results:
                enhanced_result = self._enhance_single_result(result, request)
                enhanced_results.append(enhanced_result)
            
            # Apply result-level optimizations
            enhanced_results = self._apply_result_optimizations(enhanced_results, request)
            
            # Sort and rank results
            enhanced_results = self._rank_results(enhanced_results, request)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Result enhancement failed: {e}")
            return results  # Return original results if enhancement fails
    
    def _enhance_single_result(self, result: VectorSearchResult, 
                             request: VectorSearchRequest) -> VectorSearchResult:
        """Enhance individual search result"""
        enhanced_metadata = result.metadata.copy() if result.metadata else {}
        
        # Add enhancement metadata
        enhanced_metadata["enhanced_at"] = datetime.now(timezone.utc).isoformat()
        enhanced_metadata["original_similarity"] = result.similarity_score
        
        # Apply content-type specific enhancements
        if request.content_type == "audio":
            enhanced_metadata = self._enhance_audio_result(enhanced_metadata, result)
        elif request.content_type == "video":
            enhanced_metadata = self._enhance_video_result(enhanced_metadata, result)
        elif request.content_type == "image":
            enhanced_metadata = self._enhance_image_result(enhanced_metadata, result)
        elif request.content_type == "text":
            enhanced_metadata = self._enhance_text_result(enhanced_metadata, result)
        
        # Create enhanced result
        return VectorSearchResult(
            document_id=result.document_id,
            similarity_score=result.similarity_score,
            confidence=result.confidence,
            match_type=result.match_type,
            detailed_scores=result.detailed_scores,
            metadata=enhanced_metadata
        )
    
    def _enhance_audio_result(self, metadata: Dict[str, Any], 
                            result: VectorSearchResult) -> Dict[str, Any]:
        """Enhance audio-specific result metadata"""
        metadata["audio_enhancement"] = {
            "confidence_boost": min(1.0, result.confidence + 0.1) if result.confidence < 0.9 else result.confidence,
            "spectral_match_quality": "high" if result.similarity_score > 0.8 else "medium"
        }
        return metadata
    
    def _enhance_video_result(self, metadata: Dict[str, Any], 
                            result: VectorSearchResult) -> Dict[str, Any]:
        """Enhance video-specific result metadata"""
        metadata["video_enhancement"] = {
            "visual_similarity": result.detailed_scores.get("cosine", 0.0) if result.detailed_scores else 0.0,
            "temporal_consistency": "stable" if result.confidence > 0.8 else "variable"
        }
        return metadata
    
    def _enhance_image_result(self, metadata: Dict[str, Any], 
                            result: VectorSearchResult) -> Dict[str, Any]:
        """Enhance image-specific result metadata"""
        metadata["image_enhancement"] = {
            "perceptual_similarity": result.similarity_score,
            "structural_match": result.detailed_scores.get("euclidean", 0.0) if result.detailed_scores else 0.0
        }
        return metadata
    
    def _enhance_text_result(self, metadata: Dict[str, Any], 
                           result: VectorSearchResult) -> Dict[str, Any]:
        """Enhance text-specific result metadata"""
        metadata["text_enhancement"] = {
            "semantic_similarity": result.detailed_scores.get("cosine", 0.0) if result.detailed_scores else 0.0,
            "linguistic_match": result.detailed_scores.get("pearson", 0.0) if result.detailed_scores else 0.0
        }
        return metadata
    
    def _apply_result_optimizations(self, results: List[VectorSearchResult], 
                                  request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Apply result-level optimizations"""
        # Remove very low confidence results
        min_confidence = 0.1
        filtered_results = [r for r in results if r.confidence >= min_confidence]
        
        # Boost scores for exact matches
        for result in filtered_results:
            if result.match_type == "exact":
                result.similarity_score = min(1.0, result.similarity_score * 1.05)
        
        return filtered_results
    
    def _rank_results(self, results: List[VectorSearchResult], 
                     request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Advanced result ranking"""
        # Multi-factor ranking combining similarity, confidence, and match type
        def ranking_score(result: VectorSearchResult) -> float:
            base_score = result.similarity_score * 0.7
            confidence_score = result.confidence * 0.2
            
            # Match type bonuses
            match_type_bonus = {
                "exact": 0.1,
                "near_duplicate": 0.05,
                "similar": 0.02,
                "related": 0.0
            }.get(result.match_type, 0.0)
            
            return base_score + confidence_score + match_type_bonus
        
        # Sort by ranking score
        return sorted(results, key=ranking_score, reverse=True)


class SearchOptimizer:
    """
    Ultra-Advanced Search Optimization Engine
    
    Provides intelligent query optimization, caching, and result enhancement
    for maximum vector search performance and relevance.
    """
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.query_cache = QueryCache(config.cache_size, config.cache_ttl)
        self.query_optimizer = QueryOptimizer(config)
        self.result_enhancer = ResultEnhancer(config)
        self.metrics = VectorMetrics()
        
        # Performance tracking
        self.optimization_stats = {
            "queries_optimized": 0,
            "cache_usage_ratio": 0.0,
            "average_optimization_improvement": 0.0
        }
        
        logger.info("Search Optimizer initialized")
    
    async def initialize(self) -> None:
        """Initialize search optimizer"""
        try:
            # Initialize optimization components
            logger.info("Search Optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Search Optimizer initialization failed: {e}")
            raise SearchOptimizationError(f"Initialization failed: {str(e)}")
    
    async def optimize_results(self, results: List[VectorSearchResult], 
                             request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Optimize search results with caching and enhancement"""
        try:
            start_time = time.time()
            
            # Check cache first
            cached_results = self.query_cache.get(request)
            if cached_results is not None:
                optimization_time = time.time() - start_time
                self._record_optimization_performance(request, optimization_time, cache_hit=True)
                return cached_results
            
            # Optimize the search request
            optimized_request = self.query_optimizer.optimize_search_request(request)
            
            # Enhance results
            enhanced_results = self.result_enhancer.enhance_results(results, optimized_request)
            
            # Cache the enhanced results
            self.query_cache.put(optimized_request, enhanced_results)
            
            # Record performance
            optimization_time = time.time() - start_time
            self._record_optimization_performance(optimized_request, optimization_time, cache_hit=False)
            
            # Update statistics
            self.optimization_stats["queries_optimized"] += 1
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Result optimization failed: {e}")
            raise SearchOptimizationError(f"Optimization failed: {str(e)}")
    
    async def optimize_search_request(self, request: VectorSearchRequest) -> VectorSearchRequest:
        """Optimize search request parameters"""
        try:
            optimized_request = self.query_optimizer.optimize_search_request(request)
            return optimized_request
            
        except Exception as e:
            logger.error(f"Search request optimization failed: {e}")
            return request  # Return original request if optimization fails
    
    async def record_query_performance(self, request: VectorSearchRequest, 
                                     execution_time: float, result_count: int) -> None:
        """Record query performance for optimization learning"""
        try:
            self.query_optimizer.record_performance(request, execution_time, result_count)
            
            # Update metrics
            self.metrics.searches_performed += 1
            self.metrics.total_search_time += execution_time
            
        except Exception as e:
            logger.error(f"Performance recording failed: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return self.query_cache.get_statistics()
    
    async def clear_cache(self) -> None:
        """Clear optimization cache"""
        self.query_cache.clear()
        logger.info("Search optimization cache cleared")
    
    async def get_optimization_recommendations(self, content_type: str) -> Dict[str, Any]:
        """Get optimization recommendations for content type"""
        try:
            # Get historical performance
            historical_performance = self.query_optimizer._get_historical_performance(content_type)
            
            if not historical_performance:
                return {"message": "Insufficient data for recommendations"}
            
            # Analyze performance patterns
            avg_execution_time = np.mean([h.execution_time for h in historical_performance])
            avg_result_count = np.mean([h.result_count for h in historical_performance])
            cache_hit_rate = sum(1 for h in historical_performance if h.cache_hit) / len(historical_performance)
            
            recommendations = []
            
            # Performance-based recommendations
            if avg_execution_time > 100:  # ms
                recommendations.append("Consider increasing similarity threshold to reduce search time")
            
            if avg_result_count < 5:
                recommendations.append("Consider decreasing similarity threshold to get more results")
            elif avg_result_count > 50:
                recommendations.append("Consider increasing similarity threshold or reducing max_results")
            
            if cache_hit_rate < 0.3:
                recommendations.append("Consider adjusting cache TTL or query patterns for better cache utilization")
            
            return {
                "content_type": content_type,
                "performance_analysis": {
                    "avg_execution_time_ms": avg_execution_time,
                    "avg_result_count": avg_result_count,
                    "cache_hit_rate": cache_hit_rate
                },
                "recommendations": recommendations,
                "sample_size": len(historical_performance)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return {"error": str(e)}
    
    def _record_optimization_performance(self, request: VectorSearchRequest, 
                                       optimization_time: float, cache_hit: bool) -> None:
        """Record optimization performance metrics"""
        try:
            # Update cache usage statistics
            total_queries = self.optimization_stats["queries_optimized"] + 1
            current_cache_ratio = self.optimization_stats["cache_usage_ratio"]
            
            if cache_hit:
                new_cache_ratio = (current_cache_ratio * (total_queries - 1) + 1) / total_queries
            else:
                new_cache_ratio = (current_cache_ratio * (total_queries - 1)) / total_queries
            
            self.optimization_stats["cache_usage_ratio"] = new_cache_ratio
            
            # Estimate optimization improvement (simplified)
            if not cache_hit:
                improvement_estimate = min(0.2, max(0.0, (50 - optimization_time) / 100))  # 0-20% improvement
                current_avg = self.optimization_stats["average_optimization_improvement"]
                new_avg = (current_avg * (total_queries - 1) + improvement_estimate) / total_queries
                self.optimization_stats["average_optimization_improvement"] = new_avg
            
        except Exception as e:
            logger.error(f"Error recording optimization performance: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        try:
            cache_stats = await self.get_cache_stats()
            
            return {
                "optimization_statistics": self.optimization_stats,
                "cache_statistics": cache_stats,
                "performance_metrics": asdict(self.metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get optimization statistics: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Graceful shutdown of search optimizer"""
        try:
            # Clear cache to free memory
            await self.clear_cache()
            
            logger.info("Search Optimizer shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during Search Optimizer shutdown: {e}")
