"""🎯 Content Matching Engine
==========================

Advanced AI-powered content matching and similarity detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

This module provides:
- Multi-modal content fingerprint matching
- Vector similarity search with FAISS
- Real-time similarity calculation
- Batch processing optimization
- Advanced matching algorithms
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MatchingAlgorithm(Enum):
    """Content matching algorithms."""    COSINE_SIMILARITY = "cosine"
    EUCLIDEAN_DISTANCE = "euclidean" 
    HAMMING_DISTANCE = "hamming"
    JACCARD_SIMILARITY = "jaccard"
    PERCEPTUAL_HASH = "perceptual"
    DEEP_LEARNING = "deep_learning"

class ContentType(Enum):
    """Content types for matching."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

@dataclass
class MatchResult:
    """Content matching result."""    original_id: str
    candidate_id: str
    content_type: ContentType
    similarity_score: float
    algorithm_used: MatchingAlgorithm
    match_confidence: float
    feature_breakdown: Dict[str, float]
    match_timestamp: datetime
    processing_time_ms: int

class ContentMatcher:
    """    Advanced content matching engine with multi-modal capabilities.
    
    Provides high-performance content similarity detection using
    multiple algorithms and AI-powered feature extraction.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """        Initialize the Content Matcher.
        
        Args:
            config: Matcher configuration parameters
        """        self.config = config or {}
        self._initialized = False
        
        # Matching parameters
        self.similarity_threshold = self.config.get('similarity_threshold', 0.75)
        self.batch_size = self.config.get('batch_size', 1000)
        self.max_candidates = self.config.get('max_candidates', 10000)
        
        # Algorithm weights for ensemble matching
        self.algorithm_weights = {
            MatchingAlgorithm.COSINE_SIMILARITY: 0.3,
            MatchingAlgorithm.DEEP_LEARNING: 0.4,
            MatchingAlgorithm.PERCEPTUAL_HASH: 0.2,
            MatchingAlgorithm.JACCARD_SIMILARITY: 0.1
        }
        
        # Services and models
        self.vector_db = None
        self.feature_extractors = {}
        self.similarity_models = {}
        
        # Matching cache and statistics
        self.matching_cache = {}
        self.matching_stats = {
            'total_matches_performed': 0,
            'cache_hit_rate': 0.0,
            'average_similarity_score': 0.0,
            'performance_metrics': {}
        }
        
        logger.info("Content Matcher initialized")
    
    async def initialize(self) -> bool:
        """        Initialize matcher components and models.
        
        Returns:
            bool: True if initialization successful
        """        try:
            logger.info("Initializing Content Matcher components...")
            
            # Initialize vector database
            await self._initialize_vector_database()
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            # Initialize similarity models
            await self._initialize_similarity_models()
            
            # Warm up models
            await self._warmup_models()
            
            self._initialized = True
            logger.info("Content Matcher successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Content Matcher: {str(e)}")
            return False
    
    async def _initialize_vector_database(self) -> None:
        """Initialize vector database for similarity search."""        try:
            from ..vector_database import VectorDatabaseService
            self.vector_db = VectorDatabaseService(self.config.get('vector_db', {}))
            await self.vector_db.initialize()
            logger.info("Vector database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            raise
    
    async def _initialize_feature_extractors(self) -> None:
        """Initialize feature extractors for different content types."""        # Audio feature extractor
        self.feature_extractors[ContentType.AUDIO] = {
            'model': 'audio_feature_extractor_v2',
            'features': ['mfcc', 'chroma', 'spectral_centroid', 'zero_crossing_rate'],
            'vector_size': 512
        }
        
        # Video feature extractor
        self.feature_extractors[ContentType.VIDEO] = {
            'model': 'video_feature_extractor_v2',
            'features': ['optical_flow', 'scene_detection', 'object_detection'],
            'vector_size': 1024
        }
        
        # Image feature extractor
        self.feature_extractors[ContentType.IMAGE] = {
            'model': 'image_feature_extractor_v2',
            'features': ['sift', 'surf', 'orb', 'deep_features'],
            'vector_size': 768
        }
        
        # Text feature extractor
        self.feature_extractors[ContentType.TEXT] = {
            'model': 'text_feature_extractor_v2',
            'features': ['bert_embeddings', 'tfidf', 'semantic_similarity'],
            'vector_size': 512
        }
        
        logger.info("Feature extractors initialized")
    
    async def _initialize_similarity_models(self) -> None:
        """Initialize similarity calculation models."""        for algorithm in MatchingAlgorithm:
            self.similarity_models[algorithm] = {
                'model_version': '2.0.0',
                'optimization': 'gpu_accelerated',
                'batch_processing': True,
                'loaded': True
            }
        
        logger.info("Similarity models initialized")
    
    async def _warmup_models(self) -> None:
        """Warm up models with dummy data."""        # Simulate model warmup
        logger.info("Warming up matching models...")
        await asyncio.sleep(0.1)  # Simulate warmup time
        logger.info("Model warmup complete")
    
    async def find_matches(self, content_id: str, content_type: ContentType,
                          candidate_pool: Optional[List[str]] = None,
                          algorithm: Optional[MatchingAlgorithm] = None) -> List[MatchResult]:
        """        Find similar content matches for given content.
        
        Args:
            content_id: ID of content to find matches for
            content_type: Type of content being matched
            candidate_pool: Optional list of candidate IDs to search within
            algorithm: Optional specific algorithm to use
            
        Returns:
            List of match results sorted by similarity score
        """        if not self._initialized:
            raise RuntimeError("Matcher not initialized")
        
        start_time = datetime.utcnow()
        logger.info(f"Finding matches for content: {content_id} ({content_type.value})")
        
        try:
            # Check cache first
            cache_key = f"{content_id}_{content_type.value}_{hash(str(candidate_pool))}"
            if cache_key in self.matching_cache:
                cached_result = self.matching_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self._update_cache_stats(True)
                    return cached_result['matches']
            
            self._update_cache_stats(False)
            
            # Get content features
            content_features = await self._extract_features(content_id, content_type)
            if not content_features:
                logger.warning(f"Could not extract features for content: {content_id}")
                return []
            
            # Determine candidates
            candidates = candidate_pool or await self._get_candidate_pool(content_type)
            
            # Perform matching
            if algorithm:
                matches = await self._single_algorithm_matching(
                    content_id, content_features, candidates, algorithm, content_type
                )
            else:
                matches = await self._ensemble_matching(
                    content_id, content_features, candidates, content_type
                )
            
            # Filter and sort matches
            filtered_matches = [
                match for match in matches 
                if match.similarity_score >= self.similarity_threshold
            ]
            filtered_matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit results
            final_matches = filtered_matches[:self.config.get('max_results', 100)]
            
            # Cache results
            self.matching_cache[cache_key] = {
                'matches': final_matches,
                'timestamp': datetime.utcnow(),
                'ttl_hours': 1
            }
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_matching_stats(final_matches, processing_time)
            
            logger.info(f"Found {len(final_matches)} matches for content {content_id}")
            return final_matches
            
        except Exception as e:
            logger.error(f"Error finding matches for content {content_id}: {str(e)}")
            raise
    
    async def _extract_features(self, content_id: str, content_type: ContentType) -> Optional[Dict[str, Any]]:
        """        Extract features from content for matching.
        
        Args:
            content_id: Content identifier
            content_type: Type of content
            
        Returns:
            Extracted features dictionary
        """        try:
            extractor = self.feature_extractors.get(content_type)
            if not extractor:
                logger.error(f"No feature extractor available for content type: {content_type}")
                return None
            
            # Simulate feature extraction
            # In production, this would use actual ML models
            vector_size = extractor['vector_size']
            features = {
                'vector': np.random.rand(vector_size).tolist(),
                'content_type': content_type.value,
                'extractor_version': extractor['model'],
                'features_extracted': extractor['features'],
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features for content {content_id}: {str(e)}")
            return None
    
    async def _get_candidate_pool(self, content_type: ContentType) -> List[str]:
        """        Get candidate pool for content type.
        
        Args:
            content_type: Type of content
            
        Returns:
            List of candidate content IDs
        """        try:
            # Query vector database for candidates
            if self.vector_db:
                candidates = await self.vector_db.get_candidates_by_type(
                    content_type.value, 
                    limit=self.max_candidates
                )
                return candidates
            
            # Fallback to dummy candidates
            return [f"candidate_{i}" for i in range(min(100, self.max_candidates))]
            
        except Exception as e:
            logger.error(f"Error getting candidate pool: {str(e)}")
            return []
    
    async def _single_algorithm_matching(self, content_id: str, content_features: Dict[str, Any],
                                       candidates: List[str], algorithm: MatchingAlgorithm,
                                       content_type: ContentType) -> List[MatchResult]:
        """        Perform matching using a single algorithm.
        
        Args:
            content_id: Original content ID
            content_features: Extracted features
            candidates: List of candidate IDs
            algorithm: Matching algorithm to use
            content_type: Content type
            
        Returns:
            List of match results
        """        matches = []
        start_time = datetime.utcnow()
        
        try:
            # Process candidates in batches
            for i in range(0, len(candidates), self.batch_size):
                batch = candidates[i:i + self.batch_size]
                batch_matches = await self._process_batch(
                    content_id, content_features, batch, algorithm, content_type
                )
                matches.extend(batch_matches)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"Single algorithm matching complete: {len(matches)} matches found in {processing_time:.2f}ms")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in single algorithm matching: {str(e)}")
            return []
    
    async def _ensemble_matching(self, content_id: str, content_features: Dict[str, Any],
                               candidates: List[str], content_type: ContentType) -> List[MatchResult]:
        """        Perform ensemble matching using multiple algorithms.
        
        Args:
            content_id: Original content ID
            content_features: Extracted features
            candidates: List of candidate IDs
            content_type: Content type
            
        Returns:
            List of match results
        """        algorithm_results = {}
        
        try:
            # Run multiple algorithms in parallel
            tasks = []
            for algorithm in self.algorithm_weights.keys():
                task = self._single_algorithm_matching(
                    content_id, content_features, candidates, algorithm, content_type
                )
                tasks.append((algorithm, task))
            
            # Wait for all algorithms to complete
            for algorithm, task in tasks:
                try:
                    result = await task
                    algorithm_results[algorithm] = result
                except Exception as e:
                    logger.error(f"Error in {algorithm.value} matching: {str(e)}")
                    algorithm_results[algorithm] = []
            
            # Combine results using weighted ensemble
            combined_matches = self._combine_algorithm_results(
                algorithm_results, content_id, content_type
            )
            
            return combined_matches
            
        except Exception as e:
            logger.error(f"Error in ensemble matching: {str(e)}")
            return []
    
    async def _process_batch(self, content_id: str, content_features: Dict[str, Any],
                           batch: List[str], algorithm: MatchingAlgorithm,
                           content_type: ContentType) -> List[MatchResult]:
        """        Process a batch of candidates with specific algorithm.
        
        Args:
            content_id: Original content ID
            content_features: Content features
            batch: Batch of candidate IDs
            algorithm: Matching algorithm
            content_type: Content type
            
        Returns:
            List of match results for the batch
        """        batch_matches = []
        
        try:
            for candidate_id in batch:
                # Get candidate features
                candidate_features = await self._get_candidate_features(candidate_id, content_type)
                if not candidate_features:
                    continue
                
                # Calculate similarity
                similarity_score = await self._calculate_similarity(
                    content_features, candidate_features, algorithm
                )
                
                if similarity_score >= self.similarity_threshold:
                    match_result = MatchResult(
                        original_id=content_id,
                        candidate_id=candidate_id,
                        content_type=content_type,
                        similarity_score=similarity_score,
                        algorithm_used=algorithm,
                        match_confidence=self._calculate_confidence(similarity_score, algorithm),
                        feature_breakdown=self._get_feature_breakdown(
                            content_features, candidate_features
                        ),
                        match_timestamp=datetime.utcnow(),
                        processing_time_ms=0  # Will be updated later
                    )
                    batch_matches.append(match_result)
            
            return batch_matches
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            return []
    
    async def _get_candidate_features(self, candidate_id: str, content_type: ContentType) -> Optional[Dict[str, Any]]:
        """Get features for a candidate content."""        # Simulate getting candidate features
        # In production, this would query the vector database
        extractor = self.feature_extractors.get(content_type)
        if not extractor:
            return None
        
        return {
            'vector': np.random.rand(extractor['vector_size']).tolist(),
            'content_type': content_type.value,
            'candidate_id': candidate_id
        }
    
    async def _calculate_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any],
                                  algorithm: MatchingAlgorithm) -> float:
        """        Calculate similarity between two feature sets.
        
        Args:
            features1: First feature set
            features2: Second feature set
            algorithm: Similarity algorithm to use
            
        Returns:
            Similarity score (0.0 to 1.0)
        """        try:
            vector1 = np.array(features1.get('vector', []))
            vector2 = np.array(features2.get('vector', []))
            
            if len(vector1) == 0 or len(vector2) == 0:
                return 0.0
            
            if algorithm == MatchingAlgorithm.COSINE_SIMILARITY:
                return self._cosine_similarity(vector1, vector2)
            elif algorithm == MatchingAlgorithm.EUCLIDEAN_DISTANCE:
                return self._euclidean_similarity(vector1, vector2)
            elif algorithm == MatchingAlgorithm.HAMMING_DISTANCE:
                return self._hamming_similarity(vector1, vector2)
            elif algorithm == MatchingAlgorithm.JACCARD_SIMILARITY:
                return self._jaccard_similarity(vector1, vector2)
            elif algorithm == MatchingAlgorithm.PERCEPTUAL_HASH:
                return self._perceptual_hash_similarity(vector1, vector2)
            elif algorithm == MatchingAlgorithm.DEEP_LEARNING:
                return self._deep_learning_similarity(vector1, vector2)
            else:
                return self._cosine_similarity(vector1, vector2)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _cosine_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors."""        try:
            dot_product = np.dot(vector1, vector2)
            norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
            if norm_product == 0:
                return 0.0
            return abs(dot_product / norm_product)
        except:
            return 0.0
    
    def _euclidean_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate similarity based on Euclidean distance."""        try:
            distance = np.linalg.norm(vector1 - vector2)
            max_distance = np.sqrt(len(vector1))  # Maximum possible distance
            return 1.0 - min(distance / max_distance, 1.0)
        except:
            return 0.0
    
    def _hamming_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate Hamming similarity."""        try:
            # Convert to binary for Hamming distance
            binary1 = (vector1 > np.mean(vector1)).astype(int)
            binary2 = (vector2 > np.mean(vector2)).astype(int)
            hamming_dist = np.sum(binary1 != binary2)
            return 1.0 - (hamming_dist / len(binary1))
        except:
            return 0.0
    
    def _jaccard_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate Jaccard similarity."""        try:
            # Convert to sets for Jaccard
            set1 = set(np.where(vector1 > np.mean(vector1))[0])
            set2 = set(np.where(vector2 > np.mean(vector2))[0])
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            return intersection / union if union > 0 else 0.0
        except:
            return 0.0
    
    def _perceptual_hash_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate perceptual hash similarity."""        # Simplified perceptual hash similarity
        return self._cosine_similarity(vector1, vector2)
    
    def _deep_learning_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate deep learning-based similarity."""        # Simulate deep learning similarity
        # In production, this would use trained neural networks
        base_similarity = self._cosine_similarity(vector1, vector2)
        # Add some learned adjustments
        return min(1.0, base_similarity * 1.1)
    
    def _calculate_confidence(self, similarity_score: float, algorithm: MatchingAlgorithm) -> float:
        """Calculate confidence score for a match."""        # Algorithm-specific confidence adjustments
        algorithm_confidence_factors = {
            MatchingAlgorithm.DEEP_LEARNING: 1.0,
            MatchingAlgorithm.COSINE_SIMILARITY: 0.9,
            MatchingAlgorithm.PERCEPTUAL_HASH: 0.85,
            MatchingAlgorithm.EUCLIDEAN_DISTANCE: 0.8,
            MatchingAlgorithm.JACCARD_SIMILARITY: 0.75,
            MatchingAlgorithm.HAMMING_DISTANCE: 0.7
        }
        
        factor = algorithm_confidence_factors.get(algorithm, 0.8)
        return min(1.0, similarity_score * factor)
    
    def _get_feature_breakdown(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Dict[str, float]:
        """Get detailed feature-by-feature similarity breakdown."""        # Simplified feature breakdown
        return {
            'vector_similarity': self._cosine_similarity(
                np.array(features1.get('vector', [])),
                np.array(features2.get('vector', []))
            ),
            'metadata_similarity': 0.8,  # Placeholder
            'structural_similarity': 0.7   # Placeholder
        }
    
    def _combine_algorithm_results(self, algorithm_results: Dict[MatchingAlgorithm, List[MatchResult]],
                                 content_id: str, content_type: ContentType) -> List[MatchResult]:
        """        Combine results from multiple algorithms using weighted ensemble.
        
        Args:
            algorithm_results: Results from each algorithm
            content_id: Original content ID
            content_type: Content type
            
        Returns:
            Combined match results
        """        candidate_scores = {}
        
        # Aggregate scores from all algorithms
        for algorithm, matches in algorithm_results.items():
            weight = self.algorithm_weights.get(algorithm, 0.1)
            
            for match in matches:
                candidate_id = match.candidate_id
                if candidate_id not in candidate_scores:
                    candidate_scores[candidate_id] = {
                        'weighted_score': 0.0,
                        'algorithm_scores': {},
                        'match_data': match
                    }
                
                candidate_scores[candidate_id]['weighted_score'] += match.similarity_score * weight
                candidate_scores[candidate_id]['algorithm_scores'][algorithm] = match.similarity_score
        
        # Create combined match results
        combined_matches = []
        for candidate_id, score_data in candidate_scores.items():
            # Only include if multiple algorithms agree
            if len(score_data['algorithm_scores']) >= 2:
                # Use the best match data as template
                base_match = score_data['match_data']
                
                combined_match = MatchResult(
                    original_id=content_id,
                    candidate_id=candidate_id,
                    content_type=content_type,
                    similarity_score=score_data['weighted_score'],
                    algorithm_used=MatchingAlgorithm.DEEP_LEARNING,  # Ensemble result
                    match_confidence=min(1.0, score_data['weighted_score'] * 1.1),
                    feature_breakdown=base_match.feature_breakdown,
                    match_timestamp=datetime.utcnow(),
                    processing_time_ms=0
                )
                
                combined_matches.append(combined_match)
        
        return combined_matches
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid."""        cache_time = cached_data.get('timestamp')
        ttl_hours = cached_data.get('ttl_hours', 1)
        
        if cache_time:
            age = datetime.utcnow() - cache_time
            return age.total_seconds() < (ttl_hours * 3600)
        
        return False
    
    def _update_cache_stats(self, cache_hit: bool) -> None:
        """Update cache statistics."""        total_requests = self.matching_stats.get('total_requests', 0) + 1
        cache_hits = self.matching_stats.get('cache_hits', 0)
        
        if cache_hit:
            cache_hits += 1
        
        self.matching_stats['total_requests'] = total_requests
        self.matching_stats['cache_hits'] = cache_hits
        self.matching_stats['cache_hit_rate'] = cache_hits / total_requests if total_requests > 0 else 0.0
    
    def _update_matching_stats(self, matches: List[MatchResult], processing_time: float) -> None:
        """Update matching performance statistics."""        self.matching_stats['total_matches_performed'] += 1
        
        if matches:
            avg_similarity = sum(match.similarity_score for match in matches) / len(matches)
            current_avg = self.matching_stats.get('average_similarity_score', 0.0)
            total_matches = self.matching_stats['total_matches_performed']
            
            new_avg = ((current_avg * (total_matches - 1)) + avg_similarity) / total_matches
            self.matching_stats['average_similarity_score'] = new_avg
        
        # Update performance metrics
        if 'processing_times' not in self.matching_stats['performance_metrics']:
            self.matching_stats['performance_metrics']['processing_times'] = []
        
        self.matching_stats['performance_metrics']['processing_times'].append(processing_time)
        
        # Keep only last 1000 processing times
        if len(self.matching_stats['performance_metrics']['processing_times']) > 1000:
            self.matching_stats['performance_metrics']['processing_times'] = \
                self.matching_stats['performance_metrics']['processing_times'][-1000:]
    
    async def get_matching_stats(self) -> Dict[str, Any]:
        """Get matching performance statistics."""        stats = self.matching_stats.copy()
        
        # Calculate additional metrics
        processing_times = stats.get('performance_metrics', {}).get('processing_times', [])
        if processing_times:
            stats['performance_metrics'].update({
                'avg_processing_time_ms': sum(processing_times) / len(processing_times),
                'min_processing_time_ms': min(processing_times),
                'max_processing_time_ms': max(processing_times)
            })
        
        return stats
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the matcher."""        logger.info("Shutting down Content Matcher...")
        
        # Clear cache
        self.matching_cache.clear()
        
        # Shutdown vector database
        if self.vector_db:
            await self.vector_db.shutdown()
        
        logger.info("Content Matcher shutdown complete")
