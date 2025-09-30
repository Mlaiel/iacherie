"""
Similarity Engine - Advanced Multi-Modal Similarity Search
==========================================================

Enterprise-grade similarity engine with multiple algorithms, multi-modal
fusion scoring, confidence analysis, and semantic boosting capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import json
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)


class SimilarityMetric(Enum):
    """Supported similarity metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    PEARSON = "pearson"
    HAMMING = "hamming"
    CUSTOM = "custom"


@dataclass
class SimilarityResult:
    """Result of similarity calculation."""
    score: float
    confidence: float
    metric_used: str
    distance: Optional[float] = None
    normalized_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseSimilarityAlgorithm(ABC):
    """Abstract base class for similarity algorithms."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize similarity algorithm.
        
        Args:
            name: Algorithm name
            config: Configuration parameters
        """
        self.name = name
        self.config = config or {}
        self.use_gpu = self.config.get('use_gpu', False)
        self.threshold = self.config.get('threshold', 0.0)
    
    @abstractmethod
    async def calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> SimilarityResult:
        """Calculate similarity between two vectors."""
        pass
    
    @abstractmethod
    async def batch_similarity(
        self,
        query_vector: np.ndarray,
        vectors: np.ndarray
    ) -> List[SimilarityResult]:
        """Calculate similarity between query and multiple vectors."""
        pass
    
    def normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors for similarity calculation."""
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms
    
    def calculate_confidence(self, score: float, context: Dict[str, Any]) -> float:
        """Calculate confidence score for similarity result."""
        # Base confidence calculation
        confidence = min(1.0, abs(score))
        
        # Adjust based on vector dimensions
        if 'dimension' in context:
            dim_factor = min(1.0, context['dimension'] / 768)  # Reference dimension
            confidence *= (0.8 + 0.2 * dim_factor)
        
        # Adjust based on vector norms
        if 'norm1' in context and 'norm2' in context:
            norm_diff = abs(context['norm1'] - context['norm2'])
            max_norm = max(context['norm1'], context['norm2'])
            if max_norm > 0:
                norm_factor = 1.0 - (norm_diff / max_norm)
                confidence *= (0.7 + 0.3 * norm_factor)
        
        return max(0.0, min(1.0, confidence))


class CosineSimilarityAlgorithm(BaseSimilarityAlgorithm):
    """Cosine similarity algorithm with GPU optimization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("cosine", config)
    
    async def calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> SimilarityResult:
        """Calculate cosine similarity between two vectors."""
        try:
            # Ensure vectors are 1D
            if vector1.ndim > 1:
                vector1 = vector1.flatten()
            if vector2.ndim > 1:
                vector2 = vector2.flatten()
            
            # Calculate norms
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            
            if norm1 == 0 or norm2 == 0:
                return SimilarityResult(
                    score=0.0,
                    confidence=0.0,
                    metric_used="cosine",
                    distance=1.0
                )
            
            # Calculate cosine similarity
            dot_product = np.dot(vector1, vector2)
            cosine_sim = dot_product / (norm1 * norm2)
            
            # Calculate confidence
            confidence = self.calculate_confidence(cosine_sim, {
                'dimension': len(vector1),
                'norm1': norm1,
                'norm2': norm2
            })
            
            # Convert to distance
            distance = 1.0 - cosine_sim
            
            return SimilarityResult(
                score=float(cosine_sim),
                confidence=confidence,
                metric_used="cosine",
                distance=float(distance),
                normalized_score=float((cosine_sim + 1) / 2)  # Normalize to [0, 1]
            )
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="cosine",
                distance=float('inf')
            )
    
    async def batch_similarity(
        self,
        query_vector: np.ndarray,
        vectors: np.ndarray
    ) -> List[SimilarityResult]:
        """Calculate cosine similarity for batch of vectors."""
        try:
            if query_vector.ndim > 1:
                query_vector = query_vector.flatten()
            
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            
            # Normalize vectors
            query_norm = np.linalg.norm(query_vector)
            vector_norms = np.linalg.norm(vectors, axis=1)
            
            if query_norm == 0:
                return [SimilarityResult(
                    score=0.0,
                    confidence=0.0,
                    metric_used="cosine",
                    distance=1.0
                ) for _ in range(len(vectors))]
            
            # Avoid division by zero
            vector_norms[vector_norms == 0] = 1
            
            # Calculate batch cosine similarities
            dot_products = np.dot(vectors, query_vector)
            cosine_similarities = dot_products / (query_norm * vector_norms)
            
            # Convert to results
            results = []
            for i, cosine_sim in enumerate(cosine_similarities):
                confidence = self.calculate_confidence(cosine_sim, {
                    'dimension': len(query_vector),
                    'norm1': query_norm,
                    'norm2': vector_norms[i]
                })
                
                distance = 1.0 - cosine_sim
                
                results.append(SimilarityResult(
                    score=float(cosine_sim),
                    confidence=confidence,
                    metric_used="cosine",
                    distance=float(distance),
                    normalized_score=float((cosine_sim + 1) / 2)
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating batch cosine similarity: {e}")
            return [SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="cosine",
                distance=float('inf')
            ) for _ in range(len(vectors))]


class EuclideanSimilarityAlgorithm(BaseSimilarityAlgorithm):
    """Euclidean distance similarity algorithm."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("euclidean", config)
        self.max_distance = self.config.get('max_distance', 1000.0)
    
    async def calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> SimilarityResult:
        """Calculate euclidean distance-based similarity."""
        try:
            if vector1.ndim > 1:
                vector1 = vector1.flatten()
            if vector2.ndim > 1:
                vector2 = vector2.flatten()
            
            # Calculate euclidean distance
            distance = np.linalg.norm(vector1 - vector2)
            
            # Convert distance to similarity (inverse relationship)
            similarity = 1.0 / (1.0 + distance)
            
            # Calculate confidence
            confidence = self.calculate_confidence(similarity, {
                'dimension': len(vector1),
                'distance': distance
            })
            
            return SimilarityResult(
                score=float(similarity),
                confidence=confidence,
                metric_used="euclidean",
                distance=float(distance),
                normalized_score=float(similarity)
            )
            
        except Exception as e:
            logger.error(f"Error calculating euclidean similarity: {e}")
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="euclidean",
                distance=float('inf')
            )
    
    async def batch_similarity(
        self,
        query_vector: np.ndarray,
        vectors: np.ndarray
    ) -> List[SimilarityResult]:
        """Calculate euclidean similarity for batch of vectors."""
        try:
            if query_vector.ndim > 1:
                query_vector = query_vector.flatten()
            
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            
            # Calculate batch euclidean distances
            distances = np.linalg.norm(vectors - query_vector, axis=1)
            
            # Convert to similarities
            similarities = 1.0 / (1.0 + distances)
            
            # Convert to results
            results = []
            for i, (similarity, distance) in enumerate(zip(similarities, distances)):
                confidence = self.calculate_confidence(similarity, {
                    'dimension': len(query_vector),
                    'distance': distance
                })
                
                results.append(SimilarityResult(
                    score=float(similarity),
                    confidence=confidence,
                    metric_used="euclidean",
                    distance=float(distance),
                    normalized_score=float(similarity)
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating batch euclidean similarity: {e}")
            return [SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="euclidean",
                distance=float('inf')
            ) for _ in range(len(vectors))]


class DotProductSimilarityAlgorithm(BaseSimilarityAlgorithm):
    """Dot product similarity algorithm."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("dot_product", config)
        self.normalize = self.config.get('normalize', True)
    
    async def calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> SimilarityResult:
        """Calculate dot product similarity."""
        try:
            if vector1.ndim > 1:
                vector1 = vector1.flatten()
            if vector2.ndim > 1:
                vector2 = vector2.flatten()
            
            # Normalize if required
            if self.normalize:
                vector1 = vector1 / np.linalg.norm(vector1)
                vector2 = vector2 / np.linalg.norm(vector2)
            
            # Calculate dot product
            dot_product = np.dot(vector1, vector2)
            
            # Calculate confidence
            confidence = self.calculate_confidence(dot_product, {
                'dimension': len(vector1)
            })
            
            return SimilarityResult(
                score=float(dot_product),
                confidence=confidence,
                metric_used="dot_product",
                distance=float(-dot_product),  # Negative for distance
                normalized_score=float((dot_product + 1) / 2) if self.normalize else float(dot_product)
            )
            
        except Exception as e:
            logger.error(f"Error calculating dot product similarity: {e}")
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="dot_product",
                distance=0.0
            )
    
    async def batch_similarity(
        self,
        query_vector: np.ndarray,
        vectors: np.ndarray
    ) -> List[SimilarityResult]:
        """Calculate dot product similarity for batch of vectors."""
        try:
            if query_vector.ndim > 1:
                query_vector = query_vector.flatten()
            
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            
            # Normalize if required
            if self.normalize:
                query_vector = query_vector / np.linalg.norm(query_vector)
                vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            
            # Calculate batch dot products
            dot_products = np.dot(vectors, query_vector)
            
            # Convert to results
            results = []
            for dot_product in dot_products:
                confidence = self.calculate_confidence(dot_product, {
                    'dimension': len(query_vector)
                })
                
                results.append(SimilarityResult(
                    score=float(dot_product),
                    confidence=confidence,
                    metric_used="dot_product",
                    distance=float(-dot_product),
                    normalized_score=float((dot_product + 1) / 2) if self.normalize else float(dot_product)
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating batch dot product similarity: {e}")
            return [SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="dot_product",
                distance=0.0
            ) for _ in range(len(vectors))]


class MultiModalFusionEngine:
    """Fusion engine for multi-modal similarity scoring."""
    
    def __init__(self, fusion_weights: Optional[Dict[str, float]] = None):
        """
        Initialize fusion engine.
        
        Args:
            fusion_weights: Weights for different modalities
        """
        self.fusion_weights = fusion_weights or {
            'text': 0.4,
            'audio': 0.3,
            'image': 0.2,
            'video': 0.1
        }
        
    def fuse_scores(
        self,
        scores: Dict[str, SimilarityResult],
        fusion_method: str = "weighted_average"
    ) -> SimilarityResult:
        """
        Fuse similarity scores from different modalities.
        
        Args:
            scores: Dictionary of modality -> SimilarityResult
            fusion_method: Fusion method to use
        
        Returns:
            Fused similarity result
        """
        if not scores:
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="fusion",
                metadata={'fusion_method': fusion_method}
            )
        
        if fusion_method == "weighted_average":
            return self._weighted_average_fusion(scores)
        elif fusion_method == "max_confidence":
            return self._max_confidence_fusion(scores)
        elif fusion_method == "geometric_mean":
            return self._geometric_mean_fusion(scores)
        else:
            return self._weighted_average_fusion(scores)
    
    def _weighted_average_fusion(self, scores: Dict[str, SimilarityResult]) -> SimilarityResult:
        """Weighted average fusion."""
        total_weight = 0.0
        weighted_score = 0.0
        weighted_confidence = 0.0
        
        for modality, result in scores.items():
            weight = self.fusion_weights.get(modality, 1.0)
            total_weight += weight
            weighted_score += result.score * weight
            weighted_confidence += result.confidence * weight
        
        if total_weight == 0:
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="fusion",
                metadata={'fusion_method': 'weighted_average'}
            )
        
        return SimilarityResult(
            score=weighted_score / total_weight,
            confidence=weighted_confidence / total_weight,
            metric_used="fusion",
            metadata={
                'fusion_method': 'weighted_average',
                'modalities': list(scores.keys()),
                'weights': self.fusion_weights
            }
        )
    
    def _max_confidence_fusion(self, scores: Dict[str, SimilarityResult]) -> SimilarityResult:
        """Take the result with maximum confidence."""
        best_result = max(scores.values(), key=lambda x: x.confidence)
        
        return SimilarityResult(
            score=best_result.score,
            confidence=best_result.confidence,
            metric_used="fusion",
            metadata={
                'fusion_method': 'max_confidence',
                'selected_modality': best_result.metric_used,
                'modalities': list(scores.keys())
            }
        )
    
    def _geometric_mean_fusion(self, scores: Dict[str, SimilarityResult]) -> SimilarityResult:
        """Geometric mean fusion."""
        product_score = 1.0
        product_confidence = 1.0
        count = len(scores)
        
        for result in scores.values():
            # Use absolute values to avoid issues with negative scores
            product_score *= max(0.001, abs(result.score))
            product_confidence *= max(0.001, result.confidence)
        
        fused_score = product_score ** (1.0 / count)
        fused_confidence = product_confidence ** (1.0 / count)
        
        return SimilarityResult(
            score=fused_score,
            confidence=fused_confidence,
            metric_used="fusion",
            metadata={
                'fusion_method': 'geometric_mean',
                'modalities': list(scores.keys())
            }
        )


class SimilarityEngine:
    """
    Enterprise similarity engine with advanced algorithms and multi-modal support.
    
    Features:
    - Multiple similarity algorithms (Cosine, Euclidean, Dot Product, etc.)
    - Multi-modal fusion scoring
    - Confidence scoring advanced
    - Batch processing optimized
    - Real-time query adaptation
    - Threshold adaptation automatique
    - Cross-modal similarity
    - Semantic boosting with NLP
    """
    
    def __init__(self, storage: Any, config: Any):
        """
        Initialize similarity engine.
        
        Args:
            storage: Vector storage backend
            config: Configuration object
        """
        self.storage = storage
        self.config = config
        
        # Configuration
        self.default_metric = config.get('similarity.default_metric', 'cosine')
        self.batch_size = config.get('similarity.batch_size', 1000)
        self.enable_fusion = config.get('similarity.enable_fusion', True)
        self.auto_threshold = config.get('similarity.auto_threshold', True)
        self.semantic_boost = config.get('similarity.semantic_boost', False)
        
        # Algorithm registry
        self.algorithms: Dict[str, BaseSimilarityAlgorithm] = {}
        self.fusion_engine = MultiModalFusionEngine()
        
        # Statistics
        self.stats = {
            'total_calculations': 0,
            'batch_calculations': 0,
            'fusion_calculations': 0,
            'avg_confidence': 0.0,
            'algorithm_usage': {}
        }
        
        # Initialize algorithms
        self._initialize_algorithms()
        
        logger.info(f"SimilarityEngine initialized with default metric: {self.default_metric}")
    
    def _initialize_algorithms(self) -> None:
        """Initialize similarity algorithms."""
        try:
            # Core algorithms
            self.algorithms['cosine'] = CosineSimilarityAlgorithm(
                self.config.get('similarity.cosine', {})
            )
            self.algorithms['euclidean'] = EuclideanSimilarityAlgorithm(
                self.config.get('similarity.euclidean', {})
            )
            self.algorithms['dot_product'] = DotProductSimilarityAlgorithm(
                self.config.get('similarity.dot_product', {})
            )
            
            # Additional algorithms can be added here
            # self.algorithms['manhattan'] = ManhattanSimilarityAlgorithm()
            # self.algorithms['jaccard'] = JaccardSimilarityAlgorithm()
            
            logger.info(f"Initialized {len(self.algorithms)} similarity algorithms")
            
        except Exception as e:
            logger.error(f"Failed to initialize similarity algorithms: {e}")
    
    async def initialize(self) -> bool:
        """Initialize the similarity engine."""
        try:
            # Verify storage is available
            if not self.storage or not hasattr(self.storage, 'search_similar'):
                logger.error("Storage backend not available for similarity engine")
                return False
            
            # Test algorithms
            test_vector = np.random.random(768).astype(np.float32)
            for name, algorithm in self.algorithms.items():
                try:
                    result = await algorithm.calculate_similarity(test_vector, test_vector)
                    if result.score != 1.0:  # Should be perfect match
                        logger.warning(f"Algorithm {name} test failed: score={result.score}")
                except Exception as e:
                    logger.error(f"Algorithm {name} test failed: {e}")
            
            logger.info("SimilarityEngine initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SimilarityEngine: {e}")
            return False
    
    async def calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        metric: Optional[str] = None,
        return_all_metrics: bool = False
    ) -> Union[SimilarityResult, Dict[str, SimilarityResult]]:
        """
        Calculate similarity between two vectors.
        
        Args:
            vector1: First vector
            vector2: Second vector
            metric: Similarity metric to use
            return_all_metrics: Return results for all metrics
        
        Returns:
            Similarity result(s)
        """
        try:
            metric = metric or self.default_metric
            
            if return_all_metrics:
                results = {}
                for name, algorithm in self.algorithms.items():
                    result = await algorithm.calculate_similarity(vector1, vector2)
                    results[name] = result
                    self.stats['algorithm_usage'][name] = self.stats['algorithm_usage'].get(name, 0) + 1
                
                self.stats['total_calculations'] += len(results)
                return results
            else:
                if metric not in self.algorithms:
                    logger.warning(f"Unknown metric {metric}, using {self.default_metric}")
                    metric = self.default_metric
                
                algorithm = self.algorithms[metric]
                result = await algorithm.calculate_similarity(vector1, vector2)
                
                self.stats['algorithm_usage'][metric] = self.stats['algorithm_usage'].get(metric, 0) + 1
                self.stats['total_calculations'] += 1
                
                # Update average confidence
                total_calcs = self.stats['total_calculations']
                current_avg = self.stats['avg_confidence']
                self.stats['avg_confidence'] = ((current_avg * (total_calcs - 1)) + result.confidence) / total_calcs
                
                return result
                
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used=metric or self.default_metric
            )
    
    async def batch_similarity(
        self,
        query_vector: np.ndarray,
        vectors: np.ndarray,
        metric: Optional[str] = None
    ) -> List[SimilarityResult]:
        """
        Calculate similarity between query vector and batch of vectors.
        
        Args:
            query_vector: Query vector
            vectors: Batch of vectors
            metric: Similarity metric to use
        
        Returns:
            List of similarity results
        """
        try:
            metric = metric or self.default_metric
            
            if metric not in self.algorithms:
                logger.warning(f"Unknown metric {metric}, using {self.default_metric}")
                metric = self.default_metric
            
            algorithm = self.algorithms[metric]
            results = await algorithm.batch_similarity(query_vector, vectors)
            
            self.stats['batch_calculations'] += 1
            self.stats['algorithm_usage'][metric] = self.stats['algorithm_usage'].get(metric, 0) + len(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating batch similarity: {e}")
            return [SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used=metric or self.default_metric
            ) for _ in range(len(vectors))]
    
    async def multi_modal_similarity(
        self,
        query_embeddings: Dict[str, np.ndarray],
        target_embeddings: Dict[str, np.ndarray],
        fusion_method: str = "weighted_average"
    ) -> SimilarityResult:
        """
        Calculate multi-modal similarity with fusion.
        
        Args:
            query_embeddings: Query embeddings by modality
            target_embeddings: Target embeddings by modality
            fusion_method: Fusion method to use
        
        Returns:
            Fused similarity result
        """
        try:
            if not self.enable_fusion:
                # Use default modality only
                if 'text' in query_embeddings and 'text' in target_embeddings:
                    return await self.calculate_similarity(
                        query_embeddings['text'],
                        target_embeddings['text']
                    )
                else:
                    # Use first available modality
                    modality = next(iter(query_embeddings.keys()))
                    return await self.calculate_similarity(
                        query_embeddings[modality],
                        target_embeddings[modality]
                    )
            
            # Calculate similarity for each modality
            modality_scores = {}
            
            for modality in query_embeddings:
                if modality in target_embeddings:
                    result = await self.calculate_similarity(
                        query_embeddings[modality],
                        target_embeddings[modality]
                    )
                    modality_scores[modality] = result
            
            if not modality_scores:
                return SimilarityResult(
                    score=0.0,
                    confidence=0.0,
                    metric_used="fusion"
                )
            
            # Fuse scores
            fused_result = self.fusion_engine.fuse_scores(modality_scores, fusion_method)
            
            self.stats['fusion_calculations'] += 1
            
            return fused_result
            
        except Exception as e:
            logger.error(f"Error calculating multi-modal similarity: {e}")
            return SimilarityResult(
                score=0.0,
                confidence=0.0,
                metric_used="fusion"
            )
    
    async def adaptive_threshold_search(
        self,
        query_vector: np.ndarray,
        initial_threshold: float = 0.5,
        target_results: int = 10,
        max_iterations: int = 5
    ) -> Tuple[List[Any], float]:
        """
        Adaptive threshold search to find optimal number of results.
        
        Args:
            query_vector: Query vector
            initial_threshold: Initial similarity threshold
            target_results: Target number of results
            max_iterations: Maximum adaptation iterations
        
        Returns:
            Tuple of (results, final_threshold)
        """
        try:
            current_threshold = initial_threshold
            best_results = []
            best_threshold = current_threshold
            
            for iteration in range(max_iterations):
                # Search with current threshold
                results = await self.storage.search_similar(
                    query_vector=query_vector,
                    top_k=target_results * 2,  # Get more candidates
                    threshold=current_threshold
                )
                
                results_count = len(results)
                
                # Check if we have the right number of results
                if results_count == target_results:
                    best_results = results
                    best_threshold = current_threshold
                    break
                elif results_count > target_results:
                    # Too many results, increase threshold
                    best_results = results[:target_results]
                    best_threshold = current_threshold
                    current_threshold = min(1.0, current_threshold + 0.1)
                else:
                    # Too few results, decrease threshold
                    if results_count > len(best_results):
                        best_results = results
                        best_threshold = current_threshold
                    current_threshold = max(0.0, current_threshold - 0.1)
            
            return best_results, best_threshold
            
        except Exception as e:
            logger.error(f"Error in adaptive threshold search: {e}")
            return [], initial_threshold
    
    def add_custom_algorithm(
        self,
        name: str,
        algorithm: BaseSimilarityAlgorithm
    ) -> bool:
        """
        Add a custom similarity algorithm.
        
        Args:
            name: Algorithm name
            algorithm: Algorithm instance
        
        Returns:
            True if added successfully
        """
        try:
            self.algorithms[name] = algorithm
            logger.info(f"Added custom similarity algorithm: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom algorithm {name}: {e}")
            return False
    
    def get_algorithm_stats(self) -> Dict[str, Any]:
        """Get statistics for all algorithms."""
        return {
            'total_algorithms': len(self.algorithms),
            'available_algorithms': list(self.algorithms.keys()),
            'default_metric': self.default_metric,
            'usage_stats': self.stats['algorithm_usage'].copy(),
            'total_calculations': self.stats['total_calculations'],
            'batch_calculations': self.stats['batch_calculations'],
            'fusion_calculations': self.stats['fusion_calculations'],
            'avg_confidence': self.stats['avg_confidence']
        }
    
    async def benchmark_algorithms(
        self,
        test_vectors: np.ndarray,
        iterations: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """
        Benchmark all similarity algorithms.
        
        Args:
            test_vectors: Test vectors for benchmarking
            iterations: Number of iterations
        
        Returns:
            Benchmark results
        """
        import time
        
        benchmark_results = {}
        
        for name, algorithm in self.algorithms.items():
            try:
                start_time = time.time()
                
                for i in range(iterations):
                    idx1 = i % len(test_vectors)
                    idx2 = (i + 1) % len(test_vectors)
                    
                    await algorithm.calculate_similarity(
                        test_vectors[idx1],
                        test_vectors[idx2]
                    )
                
                end_time = time.time()
                avg_time = (end_time - start_time) / iterations
                
                benchmark_results[name] = {
                    'avg_time_ms': avg_time * 1000,
                    'throughput_ops_sec': 1.0 / avg_time
                }
                
            except Exception as e:
                logger.error(f"Benchmark failed for {name}: {e}")
                benchmark_results[name] = {
                    'avg_time_ms': float('inf'),
                    'throughput_ops_sec': 0.0,
                    'error': str(e)
                }
        
        return benchmark_results
    
    async def health_check(self) -> bool:
        """Perform health check on similarity engine."""
        try:
            # Test with dummy vectors
            test_vector1 = np.random.random(768).astype(np.float32)
            test_vector2 = np.random.random(768).astype(np.float32)
            
            # Test default algorithm
            result = await self.calculate_similarity(test_vector1, test_vector2)
            if result.score < 0 or result.score > 1:
                return False
            
            # Test batch calculation
            test_batch = np.random.random((10, 768)).astype(np.float32)
            batch_results = await self.batch_similarity(test_vector1, test_batch)
            if len(batch_results) != 10:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Similarity engine health check failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the similarity engine."""
        logger.info("Shutting down SimilarityEngine...")
        
        # Clear algorithms
        self.algorithms.clear()
        
        logger.info("SimilarityEngine shutdown completed")


# Export main classes
__all__ = [
    'SimilarityEngine',
    'SimilarityMetric',
    'SimilarityResult',
    'BaseSimilarityAlgorithm',
    'CosineSimilarityAlgorithm',
    'EuclideanSimilarityAlgorithm',
    'DotProductSimilarityAlgorithm',
    'MultiModalFusionEngine'
]