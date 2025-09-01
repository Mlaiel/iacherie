"""Similarity Engine - Advanced Multi-Modal Content Similarity Analysis

Ultra-sophisticated similarity computation engine providing comprehensive
content matching capabilities across audio, video, image, and text modalities.

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
import math
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean, manhattan, hamming
from scipy.stats import pearsonr, spearmanr

from .models import VectorSearchRequest, VectorSearchResult, SimilarityMatch, VectorMetrics
from .config import VectorConfig
from .exceptions import VectorProcessingError, SimilarityComputationError

logger = logging.getLogger(__name__)


@dataclass
class SimilarityScore:
    """
Comprehensive similarity score with breakdown"""
    overall_score: float
    cosine_similarity: float
    euclidean_similarity: float
    pearson_correlation: float
    spearman_correlation: float
    confidence: float
    match_type: str  # exact, near_duplicate, similar, related


class SimilarityAlgorithm:
    """
Individual similarity algorithm implementation"""
    
    def __init__(self, algorithm_name: str, weight: float = 1.0):
        self.algorithm_name = algorithm_name
        self.weight = weight
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    def compute_similarity(self, vector_a: np.ndarray, vector_b: np.ndarray) -> float:
        """
Compute similarity using specific algorithm"""
        start_time = time.time()
        
        try:
            if self.algorithm_name == "cosine":
                score = self._cosine_similarity(vector_a, vector_b)
            elif self.algorithm_name == "euclidean":
                score = self._euclidean_similarity(vector_a, vector_b)
            elif self.algorithm_name == "manhattan":
                score = self._manhattan_similarity(vector_a, vector_b)
            elif self.algorithm_name == "pearson":
                score = self._pearson_correlation(vector_a, vector_b)
            elif self.algorithm_name == "spearman":
                score = self._spearman_correlation(vector_a, vector_b)
            elif self.algorithm_name == "jaccard":
                score = self._jaccard_similarity(vector_a, vector_b)
            elif self.algorithm_name == "hamming":
                score = self._hamming_similarity(vector_a, vector_b)
            else:
                score = self._cosine_similarity(vector_a, vector_b)  # Default
            
            self.execution_count += 1
            self.total_execution_time += time.time() - start_time
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Similarity computation failed for {self.algorithm_name}: {e}")
            return 0.0
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity"""
        if len(a.shape) == 1:
            a = a.reshape(1, -1)
        if len(b.shape) == 1:
            b = b.reshape(1, -1)
        
        return cosine_similarity(a, b)[0, 0]
    
    def _euclidean_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
Compute similarity based on Euclidean distance"""
        distance = euclidean(a.flatten(), b.flatten())
        # Convert distance to similarity (0-1 range)
        return 1.0 / (1.0 + distance)
    
    def _manhattan_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
Compute similarity based on Manhattan distance"""
        distance = manhattan(a.flatten(), b.flatten())
        return 1.0 / (1.0 + distance)
    
    def _pearson_correlation(self, a: np.ndarray, b: np.ndarray) -> float:
        """
Compute Pearson correlation coefficient"""
        try:
            corr, _ = pearsonr(a.flatten(), b.flatten())
            return abs(corr) if not np.isnan(corr) else 0.0
        except:
            return 0.0
    
    def _spearman_correlation(self, a: np.ndarray, b: np.ndarray) -> float:
        """
Compute Spearman correlation coefficient"""
        try:
            corr, _ = spearmanr(a.flatten(), b.flatten())
            return abs(corr) if not np.isnan(corr) else 0.0
        except:
            return 0.0
    
    def _jaccard_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
Compute Jaccard similarity (for binary/sparse vectors)"""
        try:
            # Binarize vectors (threshold at mean)
            a_binary = (a > np.mean(a)).astype(int)
            b_binary = (b > np.mean(b)).astype(int)
            
            intersection = np.sum(a_binary & b_binary)
            union = np.sum(a_binary | b_binary)
            
            return intersection / union if union > 0 else 0.0
        except:
            return 0.0
    
    def _hamming_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
Compute similarity based on Hamming distance"""
        try:
            # Binarize vectors
            a_binary = (a > np.mean(a)).astype(int)
            b_binary = (b > np.mean(b)).astype(int)
            
            distance = hamming(a_binary.flatten(), b_binary.flatten())
            return 1.0 - distance
        except:
            return 0.0


class ContentTypeSimilarityProcessor:
    """
Specialized similarity processor for specific content types"""
    
    def __init__(self, content_type: str, config: VectorConfig):
        self.content_type = content_type
        self.config = config
        self.algorithms = self._initialize_algorithms()
    
    def _initialize_algorithms(self) -> List[SimilarityAlgorithm]:
        """
Initialize algorithms based on content type"""
        if self.content_type in ["audio", "music"]:
            return [
                SimilarityAlgorithm("cosine", weight=0.4),
                SimilarityAlgorithm("euclidean", weight=0.3),
                SimilarityAlgorithm("pearson", weight=0.2),
                SimilarityAlgorithm("spearman", weight=0.1)
            ]
        elif self.content_type in ["video", "visual"]:
            return [
                SimilarityAlgorithm("cosine", weight=0.5),
                SimilarityAlgorithm("euclidean", weight=0.3),
                SimilarityAlgorithm("manhattan", weight=0.2)
            ]
        elif self.content_type in ["image", "photo"]:
            return [
                SimilarityAlgorithm("cosine", weight=0.4),
                SimilarityAlgorithm("euclidean", weight=0.3),
                SimilarityAlgorithm("manhattan", weight=0.2),
                SimilarityAlgorithm("jaccard", weight=0.1)
            ]
        elif self.content_type in ["text", "document"]:
            return [
                SimilarityAlgorithm("cosine", weight=0.6),
                SimilarityAlgorithm("pearson", weight=0.2),
                SimilarityAlgorithm("jaccard", weight=0.2)
            ]
        else:
            # Generic algorithms
            return [
                SimilarityAlgorithm("cosine", weight=0.5),
                SimilarityAlgorithm("euclidean", weight=0.3),
                SimilarityAlgorithm("pearson", weight=0.2)
            ]
    
    def compute_comprehensive_similarity(self, vector_a: np.ndarray, 
                                       vector_b: np.ndarray) -> SimilarityScore:
        """Compute comprehensive similarity score"""
        try:
            # Normalize vectors
            vector_a = self._normalize_vector(vector_a)
            vector_b = self._normalize_vector(vector_b)
            
            # Compute individual algorithm scores
            algorithm_scores = {}
            weighted_scores = []
            
            for algorithm in self.algorithms:
                score = algorithm.compute_similarity(vector_a, vector_b)
                algorithm_scores[algorithm.algorithm_name] = score
                weighted_scores.append(score * algorithm.weight)
            
            # Calculate overall weighted score
            total_weight = sum(algo.weight for algo in self.algorithms)
            overall_score = sum(weighted_scores) / total_weight
            
            # Determine match type based on score thresholds
            match_type = self._determine_match_type(overall_score)
            
            # Calculate confidence based on score consistency
            confidence = self._calculate_confidence(list(algorithm_scores.values()))
            
            return SimilarityScore(
                overall_score=overall_score,
                cosine_similarity=algorithm_scores.get("cosine", 0.0),
                euclidean_similarity=algorithm_scores.get("euclidean", 0.0),
                pearson_correlation=algorithm_scores.get("pearson", 0.0),
                spearman_correlation=algorithm_scores.get("spearman", 0.0),
                confidence=confidence,
                match_type=match_type
            )
            
        except Exception as e:
            logger.error(f"Comprehensive similarity computation failed: {e}")
            return SimilarityScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "error")
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector using appropriate method for content type"""
        try:
            if self.content_type in ["audio", "music"]:
                # L2 normalization for audio
                norm = np.linalg.norm(vector)
                return vector / norm if norm > 0 else vector
            elif self.content_type in ["text", "document"]:
                # Unit normalization for text
                return vector / np.linalg.norm(vector) if np.linalg.norm(vector) > 0 else vector
            else:
                # Standard normalization
                return (vector - np.mean(vector)) / (np.std(vector) + 1e-8)
        except:
            return vector
    
    def _determine_match_type(self, score: float) -> str:
        """Determine match type based on similarity score"""
        if score >= 0.95:
            return "exact"
        elif score >= 0.85:
            return "near_duplicate"
        elif score >= 0.65:
            return "similar"
        elif score >= 0.45:
            return "related"
        else:
            return "different"
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """Calculate confidence based on score consistency"""
        if not scores:
            return 0.0
        
        try:
            # Use coefficient of variation as confidence metric
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            if mean_score == 0:
                return 0.0
            
            cv = std_score / mean_score
            # Convert to confidence (lower variation = higher confidence)
            confidence = 1.0 / (1.0 + cv)
            
            return min(1.0, max(0.0, confidence))
            
        except:
            return 0.5  # Default medium confidence


class SimilarityEngine:
    """
    Ultra-Advanced Multi-Modal Similarity Computation Engine
    
    Provides comprehensive similarity analysis across different content types
    with sophisticated algorithms and optimization strategies.
    """
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.processors: Dict[str, ContentTypeSimilarityProcessor] = {}
        self.metrics = VectorMetrics()
        
        # Performance optimization
        self.thread_pool = ThreadPoolExecutor(
            max_workers=config.max_worker_threads,
            thread_name_prefix="SimilarityWorker"
        )
        
        # Caching for repeated computations
        self.similarity_cache: Dict[str, SimilarityScore] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("Similarity Engine initialized")
    
    async def initialize(self) -> None:
        """Initialize similarity engine and processors"""
        try:
            # Initialize processors for different content types
            content_types = ["audio", "video", "image", "text", "composite"]
            
            for content_type in content_types:
                self.processors[content_type] = ContentTypeSimilarityProcessor(
                    content_type, self.config
                )
            
            logger.info(f"Similarity Engine initialized with {len(self.processors)} processors")
            
        except Exception as e:
            logger.error(f"Similarity Engine initialization failed: {e}")
            raise VectorProcessingError(f"Initialization failed: {str(e)}")
    
    async def search_similar(self, request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Search for similar vectors using advanced similarity computation"""
        try:
            start_time = time.time()
            
            # Extract search parameters
            query_vector = np.array(request.query_vector, dtype=np.float32)
            content_type = request.content_type
            max_results = request.max_results
            similarity_threshold = request.similarity_threshold
            
            # Get appropriate processor
            processor = self.processors.get(content_type, self.processors.get("composite"))
            
            if not processor:
                raise SimilarityComputationError(f"No processor available for content type: {content_type}")
            
            # For demonstration, we'll simulate candidate vectors
            # In real implementation, this would come from FAISS search results
            candidate_vectors = await self._get_candidate_vectors(query_vector, content_type, max_results * 2)
            
            # Compute detailed similarity for each candidate
            similarity_results = []
            
            for candidate in candidate_vectors:
                candidate_vector = candidate["vector"]
                candidate_metadata = candidate.get("metadata", {})
                
                # Compute comprehensive similarity
                similarity_score = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    processor.compute_comprehensive_similarity,
                    query_vector,
                    candidate_vector
                )
                
                # Filter by threshold
                if similarity_score.overall_score >= similarity_threshold:
                    result = VectorSearchResult(
                        document_id=candidate["document_id"],
                        similarity_score=similarity_score.overall_score,
                        confidence=similarity_score.confidence,
                        match_type=similarity_score.match_type,
                        detailed_scores={
                            "cosine": similarity_score.cosine_similarity,
                            "euclidean": similarity_score.euclidean_similarity,
                            "pearson": similarity_score.pearson_correlation,
                            "spearman": similarity_score.spearman_correlation
                        },
                        metadata=candidate_metadata
                    )
                    similarity_results.append(result)
            
            # Sort by similarity score
            similarity_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit to max results
            final_results = similarity_results[:max_results]
            
            # Update metrics
            search_time = time.time() - start_time
            self.metrics.searches_performed += 1
            self.metrics.total_search_time += search_time
            
            return final_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise SimilarityComputationError(f"Search failed: {str(e)}")
    
    async def compute_pairwise_similarity(self, vector_a: np.ndarray, vector_b: np.ndarray,
                                        content_type: str) -> SimilarityScore:
        """Compute similarity between two specific vectors"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(vector_a, vector_b, content_type)
            
            # Check cache
            if cache_key in self.similarity_cache:
                self.cache_hits += 1
                return self.similarity_cache[cache_key]
            
            self.cache_misses += 1
            
            # Get processor
            processor = self.processors.get(content_type, self.processors.get("composite"))
            
            # Compute similarity
            similarity_score = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                processor.compute_comprehensive_similarity,
                vector_a,
                vector_b
            )
            
            # Cache result
            if len(self.similarity_cache) < self.config.cache_size:
                self.similarity_cache[cache_key] = similarity_score
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"Pairwise similarity computation failed: {e}")
            raise SimilarityComputationError(f"Computation failed: {str(e)}")
    
    async def batch_similarity_computation(self, query_vector: np.ndarray, 
                                         candidate_vectors: List[np.ndarray],
                                         content_type: str) -> List[SimilarityScore]:
        """Compute similarity for batch of candidates"""
        try:
            processor = self.processors.get(content_type, self.processors.get("composite"))
            
            # Process in parallel batches
            batch_size = min(self.config.batch_size, len(candidate_vectors))
            results = []
            
            for i in range(0, len(candidate_vectors), batch_size):
                batch = candidate_vectors[i:i + batch_size]
                
                # Compute similarities in parallel
                batch_tasks = []
                for candidate_vector in batch:
                    task = asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        processor.compute_comprehensive_similarity,
                        query_vector,
                        candidate_vector
                    )
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                results.extend(batch_results)
                
                # Yield control
                await asyncio.sleep(0.001)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch similarity computation failed: {e}")
            return []
    
    async def process_audio_similarity(self, vector_data: np.ndarray, 
                                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio-specific similarity computation"""
        try:
            # Audio-specific preprocessing
            if "spectral_features" in metadata:
                spectral_weight = 0.6
                temporal_weight = 0.4
            else:
                spectral_weight = 1.0
                temporal_weight = 0.0
            
            # Enhanced audio similarity computation
            processor = self.processors["audio"]
            
            # For demonstration - in real implementation would use actual reference vectors
            reference_vector = np.random.rand(*vector_data.shape).astype(np.float32)
            
            similarity_score = processor.compute_comprehensive_similarity(vector_data, reference_vector)
            
            return {
                "audio_similarity": similarity_score.overall_score,
                "spectral_match": similarity_score.cosine_similarity * spectral_weight,
                "temporal_match": similarity_score.pearson_correlation * temporal_weight,
                "confidence": similarity_score.confidence,
                "processing_metadata": {
                    "content_type": "audio",
                    "vector_dimension": vector_data.shape,
                    "has_spectral_features": "spectral_features" in metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Audio similarity processing failed: {e}")
            return {"error": str(e)}
    
    async def process_video_similarity(self, vector_data: np.ndarray, 
                                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process video-specific similarity computation"""
        try:
            # Video-specific features
            visual_weight = 0.7
            temporal_weight = 0.3
            
            processor = self.processors["video"]
            reference_vector = np.random.rand(*vector_data.shape).astype(np.float32)
            
            similarity_score = processor.compute_comprehensive_similarity(vector_data, reference_vector)
            
            return {
                "video_similarity": similarity_score.overall_score,
                "visual_match": similarity_score.cosine_similarity * visual_weight,
                "temporal_match": similarity_score.euclidean_similarity * temporal_weight,
                "confidence": similarity_score.confidence,
                "processing_metadata": {
                    "content_type": "video",
                    "vector_dimension": vector_data.shape,
                    "has_motion_features": "motion_vectors" in metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Video similarity processing failed: {e}")
            return {"error": str(e)}
    
    async def process_image_similarity(self, vector_data: np.ndarray, 
                                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process image-specific similarity computation"""
        try:
            processor = self.processors["image"]
            reference_vector = np.random.rand(*vector_data.shape).astype(np.float32)
            
            similarity_score = processor.compute_comprehensive_similarity(vector_data, reference_vector)
            
            return {
                "image_similarity": similarity_score.overall_score,
                "visual_similarity": similarity_score.cosine_similarity,
                "structural_similarity": similarity_score.euclidean_similarity,
                "confidence": similarity_score.confidence,
                "processing_metadata": {
                    "content_type": "image",
                    "vector_dimension": vector_data.shape,
                    "has_color_features": "color_histogram" in metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Image similarity processing failed: {e}")
            return {"error": str(e)}
    
    async def process_text_similarity(self, vector_data: np.ndarray, 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process text-specific similarity computation"""
        try:
            processor = self.processors["text"]
            reference_vector = np.random.rand(*vector_data.shape).astype(np.float32)
            
            similarity_score = processor.compute_comprehensive_similarity(vector_data, reference_vector)
            
            return {
                "text_similarity": similarity_score.overall_score,
                "semantic_similarity": similarity_score.cosine_similarity,
                "syntactic_similarity": similarity_score.pearson_correlation,
                "confidence": similarity_score.confidence,
                "processing_metadata": {
                    "content_type": "text",
                    "vector_dimension": vector_data.shape,
                    "has_linguistic_features": "pos_tags" in metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Text similarity processing failed: {e}")
            return {"error": str(e)}
    
    async def process_generic_similarity(self, vector_data: np.ndarray, 
                                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic similarity computation"""
        try:
            processor = self.processors["composite"]
            reference_vector = np.random.rand(*vector_data.shape).astype(np.float32)
            
            similarity_score = processor.compute_comprehensive_similarity(vector_data, reference_vector)
            
            return {
                "generic_similarity": similarity_score.overall_score,
                "confidence": similarity_score.confidence,
                "processing_metadata": {
                    "content_type": "generic",
                    "vector_dimension": vector_data.shape
                }
            }
            
        except Exception as e:
            logger.error(f"Generic similarity processing failed: {e}")
            return {"error": str(e)}
    
    async def _get_candidate_vectors(self, query_vector: np.ndarray, 
                                   content_type: str, max_candidates: int) -> List[Dict[str, Any]]:
        """Get candidate vectors for similarity computation"""
        # Simulation - in real implementation would query FAISS index
        candidates = []
        
        for i in range(max_candidates):
            # Generate similar vectors with some noise
            noise = np.random.normal(0, 0.1, query_vector.shape)
            candidate_vector = query_vector + noise
            
            candidates.append({
                "document_id": f"doc_{i:04d}",
                "vector": candidate_vector,
                "metadata": {
                    "content_type": content_type,
                    "candidate_rank": i,
                    "generated": True
                }
            })
        
        return candidates
    
    def _generate_cache_key(self, vector_a: np.ndarray, vector_b: np.ndarray, 
                           content_type: str) -> str:
        """Generate cache key for vector pair"""
        import hashlib
        
        # Create hash from vector data
        combined = np.concatenate([vector_a.flatten(), vector_b.flatten()])
        vector_hash = hashlib.md5(combined.tobytes()).hexdigest()[:16]
        
        return f"{content_type}_{vector_hash}"
    
    async def get_metrics(self) -> VectorMetrics:
        """Get similarity engine metrics"""
        # Update cache statistics
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0.0
        
        # Add cache metrics to base metrics
        self.metrics.cache_hit_rate = cache_hit_rate
        self.metrics.cache_size = len(self.similarity_cache)
        
        return self.metrics
    
    async def clear_cache(self):
        """
Clear similarity cache"""
        self.similarity_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Similarity cache cleared")
    
    async def shutdown(self):
        """Graceful shutdown of similarity engine"""
        try:
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear cache
            await self.clear_cache()
            
            logger.info("Similarity Engine shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during Similarity Engine shutdown: {e}")
