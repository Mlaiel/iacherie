"""
🔎 Similarity Search Engine
===========================

Advanced similarity search engine for content fingerprint matching.
Implements multiple similarity algorithms with configurable thresholds.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import hashlib

try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.preprocessing import normalize
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


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
    DIFFERENT = "different"      # <60% similarity


@dataclass
class SimilarityResult:
    """Result of similarity calculation"""
    query_id: str
    match_id: str
    similarity_score: float
    match_type: MatchType
    metric_used: SimilarityMetric
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


@dataclass
class SearchConfiguration:
    """Configuration for similarity search"""
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    min_similarity: float = 0.6
    max_results: int = 100
    exact_threshold: float = 0.98
    near_duplicate_threshold: float = 0.90
    similar_threshold: float = 0.75
    related_threshold: float = 0.60
    enable_cross_modal: bool = False
    weight_by_confidence: bool = True


class SimilarityCalculator:
    """Calculate similarity between vectors using various metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.SimilarityCalculator")
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 4))
    
    async def calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        metric: SimilarityMetric = SimilarityMetric.COSINE
    ) -> float:
        """Calculate similarity between two vectors"""
        try:
            # Ensure vectors are the same length
            min_len = min(len(vector1), len(vector2))
            v1 = vector1[:min_len]
            v2 = vector2[:min_len]
            
            if len(v1) == 0:
                return 0.0
            
            # Calculate similarity based on metric
            loop = asyncio.get_event_loop()
            similarity = await loop.run_in_executor(
                self.executor,
                self._calculate_similarity_sync,
                v1, v2, metric
            )
            
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_similarity_sync(
        self,
        v1: np.ndarray,
        v2: np.ndarray,
        metric: SimilarityMetric
    ) -> float:
        """Synchronous similarity calculation"""
        try:
            if metric == SimilarityMetric.COSINE:
                if SKLEARN_AVAILABLE:
                    return cosine_similarity([v1], [v2])[0][0]
                else:
                    # Manual cosine similarity
                    dot_product = np.dot(v1, v2)
                    norm1 = np.linalg.norm(v1)
                    norm2 = np.linalg.norm(v2)
                    if norm1 == 0 or norm2 == 0:
                        return 0.0
                    return dot_product / (norm1 * norm2)
            
            elif metric == SimilarityMetric.EUCLIDEAN:
                if SKLEARN_AVAILABLE:
                    distance = euclidean_distances([v1], [v2])[0][0]
                else:
                    distance = np.linalg.norm(v1 - v2)
                # Convert distance to similarity (0-1 range)
                max_distance = np.linalg.norm(v1) + np.linalg.norm(v2)
                return 1.0 - (distance / (max_distance + 1e-8))
            
            elif metric == SimilarityMetric.DOT_PRODUCT:
                # Normalize vectors first
                v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
                v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)
                return np.dot(v1_norm, v2_norm)
            
            elif metric == SimilarityMetric.MANHATTAN:
                distance = np.sum(np.abs(v1 - v2))
                max_distance = np.sum(np.abs(v1)) + np.sum(np.abs(v2))
                return 1.0 - (distance / (max_distance + 1e-8))
            
            elif metric == SimilarityMetric.JACCARD:
                # For binary-like vectors
                intersection = np.sum(np.minimum(v1, v2))
                union = np.sum(np.maximum(v1, v2))
                return intersection / (union + 1e-8)
            
            elif metric == SimilarityMetric.PEARSON:
                # Pearson correlation coefficient
                if len(v1) < 2:
                    return 0.0
                correlation = np.corrcoef(v1, v2)[0, 1]
                return (correlation + 1) / 2  # Convert from [-1, 1] to [0, 1]
            
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Sync similarity calculation failed: {e}")
            return 0.0
    
    async def batch_calculate_similarity(
        self,
        query_vector: np.ndarray,
        candidate_vectors: List[np.ndarray],
        metric: SimilarityMetric = SimilarityMetric.COSINE
    ) -> List[float]:
        """Calculate similarity between query and multiple candidates"""
        try:
            if not candidate_vectors:
                return []
            
            loop = asyncio.get_event_loop()
            similarities = await loop.run_in_executor(
                self.executor,
                self._batch_calculate_similarity_sync,
                query_vector,
                candidate_vectors,
                metric
            )
            
            return [max(0.0, min(1.0, sim)) for sim in similarities]
            
        except Exception as e:
            self.logger.error(f"Batch similarity calculation failed: {e}")
            return [0.0] * len(candidate_vectors)
    
    def _batch_calculate_similarity_sync(
        self,
        query_vector: np.ndarray,
        candidate_vectors: List[np.ndarray],
        metric: SimilarityMetric
    ) -> List[float]:
        """Synchronous batch similarity calculation"""
        similarities = []
        
        for candidate in candidate_vectors:
            sim = self._calculate_similarity_sync(query_vector, candidate, metric)
            similarities.append(sim)
        
        return similarities


class SearchEngine:
    """Advanced similarity search engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.SearchEngine")
        self.similarity_calculator = SimilarityCalculator(config)
        
        # Default search configuration
        self.default_search_config = SearchConfiguration()
        
        # Performance tracking
        self.search_stats = {
            'total_searches': 0,
            'average_response_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Simple cache for frequent queries
        self.result_cache = {}
        self.cache_max_size = config.get('cache_max_size', 1000)
    
    async def search_similar(
        self,
        query_vector: np.ndarray,
        candidate_vectors: Dict[str, np.ndarray],
        query_metadata: Optional[Dict[str, Any]] = None,
        candidate_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
        search_config: Optional[SearchConfiguration] = None
    ) -> List[SimilarityResult]:
        """Search for similar vectors"""
        start_time = time.time()
        
        try:
            config = search_config or self.default_search_config
            
            # Generate cache key
            cache_key = self._generate_cache_key(query_vector, list(candidate_vectors.keys()), config)
            
            # Check cache
            if cache_key in self.result_cache:
                self.search_stats['cache_hits'] += 1
                return self.result_cache[cache_key]
            
            self.search_stats['cache_misses'] += 1
            
            # Calculate similarities
            similarities = await self._calculate_all_similarities(
                query_vector, candidate_vectors, config
            )
            
            # Create results
            results = []
            query_id = query_metadata.get('id', 'unknown') if query_metadata else 'unknown'
            
            for candidate_id, similarity_score in similarities.items():
                if similarity_score < config.min_similarity:
                    continue
                
                # Determine match type
                match_type = self._determine_match_type(similarity_score, config)
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    similarity_score,
                    query_metadata,
                    candidate_metadata.get(candidate_id) if candidate_metadata else None
                )
                
                # Weight by confidence if enabled
                if config.weight_by_confidence:
                    weighted_score = similarity_score * confidence
                else:
                    weighted_score = similarity_score
                
                result = SimilarityResult(
                    query_id=query_id,
                    match_id=candidate_id,
                    similarity_score=weighted_score,
                    match_type=match_type,
                    metric_used=config.similarity_metric,
                    confidence=confidence,
                    metadata=candidate_metadata.get(candidate_id, {}) if candidate_metadata else {},
                    processing_time=time.time() - start_time
                )
                results.append(result)
            
            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit results
            results = results[:config.max_results]
            
            # Cache results
            if len(self.result_cache) < self.cache_max_size:
                self.result_cache[cache_key] = results
            
            # Update statistics
            self.search_stats['total_searches'] += 1
            processing_time = time.time() - start_time
            self.search_stats['average_response_time'] = (
                (self.search_stats['average_response_time'] * (self.search_stats['total_searches'] - 1) + processing_time) /
                self.search_stats['total_searches']
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def _calculate_all_similarities(
        self,
        query_vector: np.ndarray,
        candidate_vectors: Dict[str, np.ndarray],
        config: SearchConfiguration
    ) -> Dict[str, float]:
        """Calculate similarities for all candidates"""
        similarities = {}
        
        # Batch calculation for efficiency
        candidate_ids = list(candidate_vectors.keys())
        candidate_arrays = [candidate_vectors[cid] for cid in candidate_ids]
        
        similarity_scores = await self.similarity_calculator.batch_calculate_similarity(
            query_vector, candidate_arrays, config.similarity_metric
        )
        
        for candidate_id, score in zip(candidate_ids, similarity_scores):
            similarities[candidate_id] = score
        
        return similarities
    
    def _determine_match_type(self, similarity_score: float, config: SearchConfiguration) -> MatchType:
        """Determine match type based on similarity score"""
        if similarity_score >= config.exact_threshold:
            return MatchType.EXACT
        elif similarity_score >= config.near_duplicate_threshold:
            return MatchType.NEAR_DUPLICATE
        elif similarity_score >= config.similar_threshold:
            return MatchType.SIMILAR
        elif similarity_score >= config.related_threshold:
            return MatchType.RELATED
        else:
            return MatchType.DIFFERENT
    
    def _calculate_confidence(
        self,
        similarity_score: float,
        query_metadata: Optional[Dict[str, Any]],
        candidate_metadata: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the match"""
        base_confidence = similarity_score
        
        # Adjust based on metadata quality
        if query_metadata and candidate_metadata:
            # Same content type increases confidence
            if (query_metadata.get('content_type') == candidate_metadata.get('content_type')):
                base_confidence *= 1.1
            
            # Quality scores affect confidence
            query_quality = query_metadata.get('quality_score', 0.8)
            candidate_quality = candidate_metadata.get('quality_score', 0.8)
            quality_factor = (query_quality + candidate_quality) / 2
            base_confidence *= quality_factor
            
            # Size similarity affects confidence
            query_size = query_metadata.get('file_size', 1)
            candidate_size = candidate_metadata.get('file_size', 1)
            if query_size > 0 and candidate_size > 0:
                size_ratio = min(query_size, candidate_size) / max(query_size, candidate_size)
                base_confidence *= (0.8 + 0.2 * size_ratio)
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_cache_key(
        self,
        query_vector: np.ndarray,
        candidate_ids: List[str],
        config: SearchConfiguration
    ) -> str:
        """Generate cache key for search results"""
        query_hash = hashlib.md5(query_vector.tobytes()).hexdigest()[:8]
        candidates_hash = hashlib.md5(''.join(sorted(candidate_ids)).encode()).hexdigest()[:8]
        config_hash = hashlib.md5(str(config.__dict__).encode()).hexdigest()[:8]
        
        return f"{query_hash}_{candidates_hash}_{config_hash}"
    
    async def find_duplicates(
        self,
        vectors: Dict[str, np.ndarray],
        threshold: float = 0.95,
        metadata: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[List[str]]:
        """Find groups of duplicate vectors"""
        try:
            duplicate_groups = []
            processed = set()
            
            vector_ids = list(vectors.keys())
            
            for i, query_id in enumerate(vector_ids):
                if query_id in processed:
                    continue
                
                query_vector = vectors[query_id]
                candidates = {vid: vectors[vid] for vid in vector_ids[i+1:] if vid not in processed}
                
                # Find similar vectors
                config = SearchConfiguration(min_similarity=threshold)
                similar_results = await self.search_similar(
                    query_vector, candidates, 
                    query_metadata={'id': query_id},
                    candidate_metadata=metadata,
                    search_config=config
                )
                
                # Group duplicates
                duplicate_group = [query_id]
                for result in similar_results:
                    if result.similarity_score >= threshold:
                        duplicate_group.append(result.match_id)
                        processed.add(result.match_id)
                
                if len(duplicate_group) > 1:
                    duplicate_groups.append(duplicate_group)
                
                processed.add(query_id)
            
            return duplicate_groups
            
        except Exception as e:
            self.logger.error(f"Duplicate detection failed: {e}")
            return []
    
    async def find_nearest_neighbors(
        self,
        query_vector: np.ndarray,
        candidate_vectors: Dict[str, np.ndarray],
        k: int = 10,
        metric: SimilarityMetric = SimilarityMetric.COSINE
    ) -> List[Tuple[str, float]]:
        """Find k nearest neighbors"""
        try:
            # Calculate all similarities
            similarities = {}
            candidate_arrays = list(candidate_vectors.values())
            candidate_ids = list(candidate_vectors.keys())
            
            similarity_scores = await self.similarity_calculator.batch_calculate_similarity(
                query_vector, candidate_arrays, metric
            )
            
            for cid, score in zip(candidate_ids, similarity_scores):
                similarities[cid] = score
            
            # Sort and return top k
            sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            return sorted_similarities[:k]
            
        except Exception as e:
            self.logger.error(f"Nearest neighbors search failed: {e}")
            return []
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        cache_hit_rate = 0.0
        if self.search_stats['cache_hits'] + self.search_stats['cache_misses'] > 0:
            cache_hit_rate = self.search_stats['cache_hits'] / (
                self.search_stats['cache_hits'] + self.search_stats['cache_misses']
            )
        
        return {
            **self.search_stats,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.result_cache),
            'cache_max_size': self.cache_max_size
        }
    
    def clear_cache(self):
        """Clear search result cache"""
        self.result_cache.clear()
        self.search_stats['cache_hits'] = 0
        self.search_stats['cache_misses'] = 0
    
    def optimize_thresholds(
        self,
        ground_truth: List[Tuple[str, str, bool]],  # (query_id, candidate_id, is_match)
        vectors: Dict[str, np.ndarray]
    ) -> SearchConfiguration:
        """Optimize similarity thresholds based on ground truth data"""
        try:
            # Calculate similarities for ground truth pairs
            similarities_true = []
            similarities_false = []
            
            for query_id, candidate_id, is_match in ground_truth:
                if query_id in vectors and candidate_id in vectors:
                    similarity = asyncio.run(
                        self.similarity_calculator.calculate_similarity(
                            vectors[query_id], vectors[candidate_id]
                        )
                    )
                    
                    if is_match:
                        similarities_true.append(similarity)
                    else:
                        similarities_false.append(similarity)
            
            if not similarities_true or not similarities_false:
                return self.default_search_config
            
            # Find optimal thresholds
            true_mean = statistics.mean(similarities_true)
            false_mean = statistics.mean(similarities_false)
            
            # Set thresholds based on distribution
            optimized_config = SearchConfiguration()
            optimized_config.exact_threshold = min(0.98, true_mean + 0.02)
            optimized_config.near_duplicate_threshold = min(0.95, true_mean - 0.05)
            optimized_config.similar_threshold = min(0.85, (true_mean + false_mean) / 2)
            optimized_config.related_threshold = max(0.60, false_mean + 0.1)
            optimized_config.min_similarity = max(0.50, false_mean)
            
            self.logger.info(f"Optimized thresholds: exact={optimized_config.exact_threshold:.3f}, "
                           f"near_duplicate={optimized_config.near_duplicate_threshold:.3f}, "
                           f"similar={optimized_config.similar_threshold:.3f}, "
                           f"related={optimized_config.related_threshold:.3f}")
            
            return optimized_config
            
        except Exception as e:
            self.logger.error(f"Threshold optimization failed: {e}")
            return self.default_search_config
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self.similarity_calculator, 'executor'):
            self.similarity_calculator.executor.shutdown(wait=False)
