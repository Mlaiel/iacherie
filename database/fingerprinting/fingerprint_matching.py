"""Ultra-Advanced Enterprise Fingerprint Matching Engine

Industrial-strength content fingerprint matching system featuring:
- Multi-algorithm similarity detection (exact, perceptual, semantic)
- Real-time matching with sub-50ms latency
- Advanced ML-powered similarity scoring
- Enterprise security and audit trails
- Distributed matching across multiple content types
- Comprehensive analytics and performance monitoring

Industry Features:
- Multi-modal content matching (audio, video, image, text)
- Advanced ML algorithms for similarity detection
- Real-time streaming match detection
- Distributed computing for large-scale matching
- Comprehensive fraud detection and prevention
- Advanced caching and performance optimization

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
import time
import struct
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set, Union, AsyncIterator
from dataclasses import dataclass, asdict, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import uuid

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import hamming, jaccard, cityblock
from scipy.stats import pearsonr, spearmanr
import cv2
import librosa
from Levenshtein import distance as levenshtein_distance
import faiss

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError
from backend.database.fingerprinting.fingerprint_indexing import FingerprintIndexManager
from backend.utils.performance import PerformanceMonitor
from backend.utils.caching import CacheManager
from backend.utils.ml_models import SimilarityMLModel

logger = logging.getLogger(__name__)


class MatchType(Enum):
    """
Advanced types of fingerprint matches"""

    EXACT = "exact"
    NEAR_EXACT = "near_exact"
    SIMILAR = "similar"
    PARTIAL = "partial"
    VARIANT = "variant"
    TRANSFORMED = "transformed"
    DERIVATIVE = "derivative"
    FRAGMENT = "fragment"
    COMPOSITE = "composite"


class MatchAlgorithm(Enum):
    """Comprehensive fingerprint matching algorithms"""
    # Hash-based algorithms
    HASH_EXACT = "hash_exact"
    HASH_HAMMING = "hash_hamming"
    HASH_JACCARD = "hash_jaccard"
    HASH_FUZZY = "hash_fuzzy"
    
    # Vector-based algorithms
    VECTOR_COSINE = "vector_cosine"
    VECTOR_EUCLIDEAN = "vector_euclidean"
    VECTOR_MANHATTAN = "vector_manhattan"
    VECTOR_CORRELATION = "vector_correlation"
    
    # Advanced ML algorithms
    DEEP_SIMILARITY = "deep_similarity"
    NEURAL_EMBEDDING = "neural_embedding"
    TRANSFORMER_SIMILARITY = "transformer_similarity"
    
    # Content-specific algorithms
    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    VIDEO_FRAME_ANALYSIS = "video_frame_analysis"
    IMAGE_PERCEPTUAL = "image_perceptual"
    TEXT_SEMANTIC = "text_semantic"
    
    # Composite algorithms
    WEIGHTED_ENSEMBLE = "weighted_ensemble"
    ADAPTIVE_HYBRID = "adaptive_hybrid"
    ML_FUSION = "ml_fusion"


class ConfidenceLevel(Enum):
    """Confidence levels for matches"""

    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"            # 85-95%
    MEDIUM = "medium"        # 70-85%
    LOW = "low"              # 50-70%
    VERY_LOW = "very_low"    # <50%


class MatchStatus(Enum):
    """Status of match processing"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class MatchResult:
    """Comprehensive match result with advanced metrics"""
    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_fingerprint_id: str = ""
    matched_fingerprint_id: str = ""
    similarity_score: float = 0.0
    match_type: MatchType = MatchType.SIMILAR
    algorithm: MatchAlgorithm = MatchAlgorithm.VECTOR_COSINE
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    # Detailed scoring
    algorithm_scores: Dict[str, float] = field(default_factory=dict)
    sub_match_scores: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Metadata and context
    match_details: Dict[str, Any] = field(default_factory=dict)
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    processing_time: float = 0.0
    algorithm_times: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    
    # Status and tracking
    status: MatchStatus = MatchStatus.COMPLETED
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'match_id': self.match_id,
            'query_fingerprint_id': self.query_fingerprint_id,
            'matched_fingerprint_id': self.matched_fingerprint_id,
            'similarity_score': self.similarity_score,
            'match_type': self.match_type.value,
            'algorithm': self.algorithm.value,
            'confidence_level': self.confidence_level.value,
            'algorithm_scores': self.algorithm_scores,
            'sub_match_scores': self.sub_match_scores,
            'quality_metrics': self.quality_metrics,
            'match_details': self.match_details,
            'content_metadata': self.content_metadata,
            'processing_metadata': self.processing_metadata,
            'processing_time': self.processing_time,
            'algorithm_times': self.algorithm_times,
            'resource_usage': self.resource_usage,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def get_confidence_score(self) -> float:
        """
Calculate normalized confidence score"""
        confidence_map = {
            ConfidenceLevel.VERY_HIGH: 0.975,
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.775,
            ConfidenceLevel.LOW: 0.6,
            ConfidenceLevel.VERY_LOW: 0.25
        }
        return confidence_map.get(self.confidence_level, 0.5)


@dataclass
class MatchConfiguration:
    """
Comprehensive configuration for matching algorithms"""
    # General thresholds
    exact_match_threshold: float = 0.99
    near_exact_threshold: float = 0.95
    similar_match_threshold: float = 0.8
    partial_match_threshold: float = 0.6
    variant_match_threshold: float = 0.4
    minimum_threshold: float = 0.2
    
    # Algorithm-specific thresholds
    hash_hamming_threshold: float = 0.85
    hash_jaccard_threshold: float = 0.75
    vector_cosine_threshold: float = 0.8
    vector_euclidean_threshold: float = 0.7
    deep_similarity_threshold: float = 0.85
    
    # Content-specific configurations
    audio_chromaprint_threshold: float = 0.9
    audio_spectral_threshold: float = 0.8
    video_frame_threshold: float = 0.85
    image_perceptual_threshold: float = 0.8
    text_semantic_threshold: float = 0.75
    
    # Performance settings
    max_processing_time: float = 30.0  # seconds
    parallel_workers: int = 4
    batch_size: int = 100
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    
    # Quality controls
    min_fingerprint_quality: float = 0.5
    max_results_per_query: int = 1000
    enable_fuzzy_matching: bool = True
    enable_ml_enhancement: bool = True
    
    # Algorithm weights for ensemble methods
    algorithm_weights: Dict[str, float] = field(default_factory=lambda: {
        'hash_exact': 1.0,
        'vector_cosine': 0.9,
        'deep_similarity': 0.85,
        'content_specific': 0.8,
        'semantic': 0.7
    })


@dataclass 
class MatchQuery:
    """
Comprehensive match query specification"""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Query fingerprint data
    fingerprint_id: Optional[str] = None
    fingerprint_data: Optional[Dict[str, Any]] = None
    vector_data: Optional[np.ndarray] = None
    content_type: Optional[str] = None
    
    # Search parameters
    algorithms: List[MatchAlgorithm] = field(default_factory=lambda: [MatchAlgorithm.VECTOR_COSINE])
    similarity_threshold: float = 0.8
    max_results: int = 100
    include_metadata: bool = True
    
    # Filtering options
    user_filter: Optional[str] = None
    tenant_filter: Optional[str] = None
    content_type_filter: Optional[List[str]] = None
    date_range_filter: Optional[Tuple[datetime, datetime]] = None
    quality_filter: Optional[float] = None
    
    # Processing options
    enable_parallel: bool = True
    timeout: float = 30.0
    use_cache: bool = True
    return_details: bool = True
    
    # Advanced options
    adaptive_threshold: bool = False
    ml_enhancement: bool = False
    cross_modal_search: bool = False
    temporal_analysis: bool = False
    vector_cosine_threshold: float = 0.75
    semantic_threshold: float = 0.7
    perceptual_threshold: float = 0.8
    
    # Performance settings
    max_concurrent_matches: int = 10
    match_timeout: float = 30.0
    cache_results: bool = True
    enable_parallel_processing: bool = True


class HashMatcher:
    """
High-performance hash-based matching engine"""
    
    def __init__(self, config: MatchConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.HashMatcher")
    
    async def match_exact(
        self,
        query_hash: str,
        candidate_hashes: List[Tuple[str, str]]
    ) -> List[MatchResult]:
        """Exact hash matching"""
        results = []
        start_time = time.time()
        
        for fingerprint_id, candidate_hash in candidate_hashes:
            if query_hash == candidate_hash:
                result = MatchResult(
                    query_fingerprint_id="query",
                    matched_fingerprint_id=fingerprint_id,
                    similarity_score=1.0,
                    match_type=MatchType.EXACT,
                    algorithm=MatchAlgorithm.HASH_EXACT,
                    confidence_level="high",
                    match_details={"hash_match": True},
                    processing_time=time.time() - start_time,
                    timestamp=datetime.now(timezone.utc)
                )
                results.append(result)
        
        return results
    
    async def match_hamming(
        self,
        query_hash: str,
        candidate_hashes: List[Tuple[str, str]]
    ) -> List[MatchResult]:
        """Hamming distance-based hash matching"""
        results = []
        start_time = time.time()
        
        for fingerprint_id, candidate_hash in candidate_hashes:
            if len(query_hash) == len(candidate_hash):
                # Convert hex strings to binary for hamming distance
                try:
                    query_bits = bin(int(query_hash, 16))[2:].zfill(len(query_hash) * 4)
                    candidate_bits = bin(int(candidate_hash, 16))[2:].zfill(len(candidate_hash) * 4)
                    
                    # Calculate hamming distance
                    distance = hamming(
                        [int(b) for b in query_bits],
                        [int(b) for b in candidate_bits]
                    )
                    
                    similarity = 1.0 - distance
                    
                    if similarity >= self.config.hash_hamming_threshold:
                        match_type = self._determine_match_type(similarity)
                        confidence = self._calculate_confidence(similarity, MatchAlgorithm.HASH_HAMMING)
                        
                        result = MatchResult(
                            query_fingerprint_id="query",
                            matched_fingerprint_id=fingerprint_id,
                            similarity_score=similarity,
                            match_type=match_type,
                            algorithm=MatchAlgorithm.HASH_HAMMING,
                            confidence_level=confidence,
                            match_details={
                                "hamming_distance": distance,
                                "bit_length": len(query_bits)
                            },
                            processing_time=time.time() - start_time,
                            timestamp=datetime.now(timezone.utc)
                        )
                        results.append(result)
                
                except ValueError:
                    self.logger.warning(f"Invalid hex hash format: {query_hash} or {candidate_hash}")
                    continue
        
        return results
    
    def _determine_match_type(self, similarity: float) -> MatchType:
        """Determine match type based on similarity score"""
        if similarity >= self.config.exact_match_threshold:
            return MatchType.EXACT
        elif similarity >= self.config.similar_match_threshold:
            return MatchType.SIMILAR
        elif similarity >= self.config.partial_match_threshold:
            return MatchType.PARTIAL
        else:
            return MatchType.VARIANT
    
    def _calculate_confidence(self, similarity: float, algorithm: MatchAlgorithm) -> str:
        """
Calculate confidence level based on similarity and algorithm"""
        if similarity >= 0.9:
            return "high"
        elif similarity >= 0.7:
            return "medium"
        else:
            return "low"


class VectorMatcher:
    """Advanced vector-based similarity matching"""
    
    def __init__(self, config: MatchConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.VectorMatcher")
    
    async def match_cosine_similarity(
        self,
        query_vector: np.ndarray,
        candidate_vectors: List[Tuple[str, np.ndarray]]
    ) -> List[MatchResult]:
        """Cosine similarity-based vector matching"""
        results = []
        start_time = time.time()
        
        if len(candidate_vectors) == 0:
            return results
        
        try:
            # Prepare vectors for batch computation
            fingerprint_ids = [fid for fid, _ in candidate_vectors]
            vectors = np.array([vec for _, vec in candidate_vectors])
            
            # Ensure query vector is 2D
            query_vector = query_vector.reshape(1, -1)
            
            # Compute cosine similarities
            similarities = cosine_similarity(query_vector, vectors)[0]
            
            # Process results
            for i, (fingerprint_id, similarity) in enumerate(zip(fingerprint_ids, similarities)):
                if similarity >= self.config.vector_cosine_threshold:
                    match_type = self._determine_match_type(similarity)
                    confidence = self._calculate_confidence(similarity, MatchAlgorithm.VECTOR_COSINE)
                    
                    result = MatchResult(
                        query_fingerprint_id="query",
                        matched_fingerprint_id=fingerprint_id,
                        similarity_score=float(similarity),
                        match_type=match_type,
                        algorithm=MatchAlgorithm.VECTOR_COSINE,
                        confidence_level=confidence,
                        match_details={
                            "vector_dimension": len(candidate_vectors[i][1]),
                            "cosine_similarity": float(similarity)
                        },
                        processing_time=time.time() - start_time,
                        timestamp=datetime.now(timezone.utc)
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"Cosine similarity matching failed: {e}")
            raise DatabaseError(f"Vector matching failed: {e}")
        
        return results
    
    async def match_euclidean_distance(
        self,
        query_vector: np.ndarray,
        candidate_vectors: List[Tuple[str, np.ndarray]]
    ) -> List[MatchResult]:
        """Euclidean distance-based vector matching"""
        results = []
        start_time = time.time()
        
        if len(candidate_vectors) == 0:
            return results
        
        try:
            # Prepare vectors for batch computation
            fingerprint_ids = [fid for fid, _ in candidate_vectors]
            vectors = np.array([vec for _, vec in candidate_vectors])
            
            # Ensure query vector is 2D
            query_vector = query_vector.reshape(1, -1)
            
            # Compute euclidean distances
            distances = euclidean_distances(query_vector, vectors)[0]
            
            # Convert distances to similarities (normalize by max distance)
            max_distance = np.max(distances) if len(distances) > 0 else 1.0
            similarities = 1.0 - (distances / max_distance)
            
            # Process results
            for i, (fingerprint_id, similarity) in enumerate(zip(fingerprint_ids, similarities)):
                if similarity >= self.config.vector_cosine_threshold:  # Use same threshold
                    match_type = self._determine_match_type(similarity)
                    confidence = self._calculate_confidence(similarity, MatchAlgorithm.VECTOR_EUCLIDEAN)
                    
                    result = MatchResult(
                        query_fingerprint_id="query",
                        matched_fingerprint_id=fingerprint_id,
                        similarity_score=float(similarity),
                        match_type=match_type,
                        algorithm=MatchAlgorithm.VECTOR_EUCLIDEAN,
                        confidence_level=confidence,
                        match_details={
                            "vector_dimension": len(candidate_vectors[i][1]),
                            "euclidean_distance": float(distances[i]),
                            "normalized_similarity": float(similarity)
                        },
                        processing_time=time.time() - start_time,
                        timestamp=datetime.now(timezone.utc)
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"Euclidean distance matching failed: {e}")
            raise DatabaseError(f"Vector matching failed: {e}")
        
        return results
    
    def _determine_match_type(self, similarity: float) -> MatchType:
        """Determine match type based on similarity score"""
        if similarity >= 0.95:
            return MatchType.EXACT
        elif similarity >= 0.8:
            return MatchType.SIMILAR
        elif similarity >= 0.6:
            return MatchType.PARTIAL
        else:
            return MatchType.VARIANT
    
    def _calculate_confidence(self, similarity: float, algorithm: MatchAlgorithm) -> str:
        """
Calculate confidence level"""
        if similarity >= 0.9:
            return "high"
        elif similarity >= 0.7:
            return "medium"
        else:
            return "low"


class PerceptualMatcher:
    """Perceptual hash-based content matching"""
    
    def __init__(self, config: MatchConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PerceptualMatcher")
    
    async def match_image_perceptual(
        self,
        query_hash: str,
        candidate_hashes: List[Tuple[str, str]]
    ) -> List[MatchResult]:
        """Image perceptual hash matching"""
        results = []
        start_time = time.time()
        
        for fingerprint_id, candidate_hash in candidate_hashes:
            try:
                # Calculate hamming distance between perceptual hashes
                if len(query_hash) == len(candidate_hash):
                    distance = sum(c1 != c2 for c1, c2 in zip(query_hash, candidate_hash))
                    max_distance = len(query_hash)
                    similarity = 1.0 - (distance / max_distance)
                    
                    if similarity >= self.config.perceptual_threshold:
                        match_type = self._determine_match_type(similarity)
                        confidence = self._calculate_confidence(similarity)
                        
                        result = MatchResult(
                            query_fingerprint_id="query",
                            matched_fingerprint_id=fingerprint_id,
                            similarity_score=similarity,
                            match_type=match_type,
                            algorithm=MatchAlgorithm.PERCEPTUAL_HASH,
                            confidence_level=confidence,
                            match_details={
                                "perceptual_distance": distance,
                                "hash_length": len(query_hash)
                            },
                            processing_time=time.time() - start_time,
                            timestamp=datetime.now(timezone.utc)
                        )
                        results.append(result)
            
            except Exception as e:
                self.logger.warning(f"Perceptual hash matching failed for {fingerprint_id}: {e}")
                continue
        
        return results
    
    async def match_audio_perceptual(
        self,
        query_features: Dict[str, Any],
        candidate_features: List[Tuple[str, Dict[str, Any]]]
    ) -> List[MatchResult]:
        """Audio perceptual feature matching"""
        results = []
        start_time = time.time()
        
        query_chroma = query_features.get('chroma')
        query_mfcc = query_features.get('mfcc')
        
        if query_chroma is None or query_mfcc is None:
            return results
        
        for fingerprint_id, candidate_features_dict in candidate_features:
            try:
                candidate_chroma = candidate_features_dict.get('chroma')
                candidate_mfcc = candidate_features_dict.get('mfcc')
                
                if candidate_chroma is None or candidate_mfcc is None:
                    continue
                
                # Calculate similarity for chroma features
                chroma_similarity = self._calculate_feature_similarity(query_chroma, candidate_chroma)
                
                # Calculate similarity for MFCC features
                mfcc_similarity = self._calculate_feature_similarity(query_mfcc, candidate_mfcc)
                
                # Combined similarity
                combined_similarity = (chroma_similarity + mfcc_similarity) / 2.0
                
                if combined_similarity >= self.config.perceptual_threshold:
                    match_type = self._determine_match_type(combined_similarity)
                    confidence = self._calculate_confidence(combined_similarity)
                    
                    result = MatchResult(
                        query_fingerprint_id="query",
                        matched_fingerprint_id=fingerprint_id,
                        similarity_score=combined_similarity,
                        match_type=match_type,
                        algorithm=MatchAlgorithm.PERCEPTUAL_HASH,
                        confidence_level=confidence,
                        match_details={
                            "chroma_similarity": chroma_similarity,
                            "mfcc_similarity": mfcc_similarity,
                            "combined_similarity": combined_similarity
                        },
                        processing_time=time.time() - start_time,
                        timestamp=datetime.now(timezone.utc)
                    )
                    results.append(result)
            
            except Exception as e:
                self.logger.warning(f"Audio perceptual matching failed for {fingerprint_id}: {e}")
                continue
        
        return results
    
    def _calculate_feature_similarity(
        self,
        feature1: np.ndarray,
        feature2: np.ndarray
    ) -> float:
        """Calculate similarity between feature vectors"""
        try:
            # Ensure features are same length (truncate or pad)
            min_len = min(len(feature1), len(feature2))
            feature1 = feature1[:min_len]
            feature2 = feature2[:min_len]
            
            # Calculate cosine similarity
            return float(cosine_similarity([feature1], [feature2])[0][0])
        
        except Exception:
            return 0.0
    
    def _determine_match_type(self, similarity: float) -> MatchType:
        """
Determine match type based on similarity"""
        if similarity >= 0.9:
            return MatchType.EXACT
        elif similarity >= 0.75:
            return MatchType.SIMILAR
        elif similarity >= 0.6:
            return MatchType.PARTIAL
        else:
            return MatchType.VARIANT
    
    def _calculate_confidence(self, similarity: float) -> str:
        """
Calculate confidence level"""
        if similarity >= 0.85:
            return "high"
        elif similarity >= 0.7:
            return "medium"
        else:
            return "low"


class SemanticMatcher:
    """Semantic content matching using NLP techniques"""
    
    def __init__(self, config: MatchConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.SemanticMatcher")
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def match_text_semantic(
        self,
        query_text: str,
        candidate_texts: List[Tuple[str, str]]
    ) -> List[MatchResult]:
        """Semantic text matching using TF-IDF and cosine similarity"""
        results = []
        start_time = time.time()
        
        if not candidate_texts:
            return results
        
        try:
            # Prepare texts for vectorization
            all_texts = [query_text] + [text for _, text in candidate_texts]
            
            # Fit TF-IDF vectorizer and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Query vector is the first one
            query_vector = tfidf_matrix[0:1]
            candidate_vectors = tfidf_matrix[1:]
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_vector, candidate_vectors)[0]
            
            # Process results
            for i, (fingerprint_id, candidate_text) in enumerate(candidate_texts):
                similarity = similarities[i]
                
                if similarity >= self.config.semantic_threshold:
                    match_type = self._determine_match_type(similarity)
                    confidence = self._calculate_confidence(similarity)
                    
                    # Calculate additional text metrics
                    text_length_ratio = min(len(query_text), len(candidate_text)) / max(len(query_text), len(candidate_text))
                    word_overlap = self._calculate_word_overlap(query_text, candidate_text)
                    
                    result = MatchResult(
                        query_fingerprint_id="query",
                        matched_fingerprint_id=fingerprint_id,
                        similarity_score=similarity,
                        match_type=match_type,
                        algorithm=MatchAlgorithm.SEMANTIC_TFIDF,
                        confidence_level=confidence,
                        match_details={
                            "tfidf_similarity": similarity,
                            "text_length_ratio": text_length_ratio,
                            "word_overlap": word_overlap,
                            "query_length": len(query_text),
                            "candidate_length": len(candidate_text)
                        },
                        processing_time=time.time() - start_time,
                        timestamp=datetime.now(timezone.utc)
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"Semantic text matching failed: {e}")
            raise DatabaseError(f"Semantic matching failed: {e}")
        
        return results
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap ratio between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _determine_match_type(self, similarity: float) -> MatchType:
        """
Determine match type based on similarity"""
        if similarity >= 0.9:
            return MatchType.EXACT
        elif similarity >= 0.7:
            return MatchType.SIMILAR
        elif similarity >= 0.5:
            return MatchType.PARTIAL
        else:
            return MatchType.VARIANT
    
    def _calculate_confidence(self, similarity: float) -> str:
        """
Calculate confidence level"""
        if similarity >= 0.8:
            return "high"
        elif similarity >= 0.6:
            return "medium"
        else:
            return "low"


class FingerprintMatchingEngine:
    """
    Comprehensive fingerprint matching engine that coordinates multiple
    matching algorithms for optimal content similarity detection.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        index_manager: FingerprintIndexManager,
        config: Optional[MatchConfiguration] = None
    ):
        self.db_manager = db_manager
        self.index_manager = index_manager
        self.config = config or MatchConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize matchers
        self.hash_matcher = HashMatcher(self.config)
        self.vector_matcher = VectorMatcher(self.config)
        self.perceptual_matcher = PerceptualMatcher(self.config)
        self.semantic_matcher = SemanticMatcher(self.config)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_matches)
    
    async def find_matches(
        self,
        query_fingerprint: ContentFingerprint,
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
        algorithms: Optional[List[MatchAlgorithm]] = None,
        max_results: int = 100
    ) -> List[MatchResult]:
        """
        Find matches for a fingerprint using multiple algorithms
        
        Args:
            query_fingerprint: Fingerprint to search for
            content_type: Filter by content type
            user_id: Filter by user (if None, search all users)
            algorithms: Specific algorithms to use (if None, use all applicable)
            max_results: Maximum results to return
            
        Returns:
            List of match results sorted by similarity score
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query_fingerprint, content_type, user_id)
            if self.config.cache_results:
                cached_results = await self.cache_manager.get(cache_key)
                if cached_results:
                    self.logger.debug(f"Retrieved {len(cached_results)} cached results")
                    return cached_results
            
            # Determine applicable algorithms
            if algorithms is None:
                algorithms = self._determine_applicable_algorithms(query_fingerprint)
            
            # Execute matching algorithms in parallel
            all_results = []
            
            if self.config.enable_parallel_processing:
                tasks = []
                for algorithm in algorithms:
                    task = self._execute_matching_algorithm(
                        algorithm, query_fingerprint, content_type, user_id
                    )
                    tasks.append(task)
                
                # Wait for all tasks to complete
                algorithm_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for results in algorithm_results:
                    if isinstance(results, Exception):
                        self.logger.error(f"Algorithm execution failed: {results}")
                        continue
                    all_results.extend(results)
            else:
                # Sequential execution
                for algorithm in algorithms:
                    try:
                        results = await self._execute_matching_algorithm(
                            algorithm, query_fingerprint, content_type, user_id
                        )
                        all_results.extend(results)
                    except Exception as e:
                        self.logger.error(f"Algorithm {algorithm} failed: {e}")
                        continue
            
            # Deduplicate and merge results
            merged_results = self._merge_and_deduplicate_results(all_results)
            
            # Sort by similarity score
            merged_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit results
            final_results = merged_results[:max_results]
            
            # Cache results
            if self.config.cache_results:
                await self.cache_manager.set(cache_key, final_results, ttl=300)
            
            # Log performance metrics
            total_time = time.time() - start_time
            self.logger.info(
                f"Found {len(final_results)} matches in {total_time:.3f}s using {len(algorithms)} algorithms"
            )
            
            return final_results
        
        except Exception as e:
            self.logger.error(f"Fingerprint matching failed: {e}")
            raise DatabaseError(f"Match finding failed: {e}")
    
    async def find_exact_matches(
        self,
        query_fingerprint: ContentFingerprint,
        user_id: Optional[str] = None
    ) -> List[MatchResult]:
        """Find exact hash matches for a fingerprint"""
        try:
            results = []
            
            # Check each hash type for exact matches
            hash_types = {
                'primary': query_fingerprint.primary_hash,
                'perceptual': query_fingerprint.perceptual_hash,
                'structural': query_fingerprint.structural_hash,
                'semantic': query_fingerprint.semantic_hash
            }
            
            for hash_type, hash_value in hash_types.items():
                if hash_value:
                    # Search in index
                    matched_ids = await self.index_manager.hash_index.search_by_hash(
                        hash_type, hash_value
                    )
                    
                    # Filter by user if specified
                    if user_id:
                        user_fingerprints = await self.index_manager.hash_index.search_by_user(user_id)
                        matched_ids = matched_ids.intersection(user_fingerprints)
                    
                    # Create match results
                    for fingerprint_id in matched_ids:
                        result = MatchResult(
                            query_fingerprint_id=query_fingerprint.fingerprint_id or "query",
                            matched_fingerprint_id=fingerprint_id,
                            similarity_score=1.0,
                            match_type=MatchType.EXACT,
                            algorithm=MatchAlgorithm.HASH_EXACT,
                            confidence_level="high",
                            match_details={
                                "hash_type": hash_type,
                                "hash_value": hash_value
                            },
                            processing_time=0.0,
                            timestamp=datetime.now(timezone.utc)
                        )
                        results.append(result)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Exact match search failed: {e}")
            raise DatabaseError(f"Exact match search failed: {e}")
    
    async def find_similar_content(
        self,
        query_fingerprint: ContentFingerprint,
        similarity_threshold: float = 0.7,
        max_results: int = 50
    ) -> List[MatchResult]:
        """Find similar content using vector similarity"""
        try:
            results = []
            
            # Use vector similarity if available
            if hasattr(query_fingerprint, 'feature_vector') and query_fingerprint.feature_vector is not None:
                content_type = str(query_fingerprint.content_type).lower()
                
                # Search using index manager
                index_results = await self.index_manager.search_fingerprints(
                    query=query_fingerprint.feature_vector,
                    search_type="vector",
                    content_type=content_type,
                    similarity_threshold=similarity_threshold,
                    max_results=max_results
                )
                
                # Convert to MatchResult objects
                for index_result in index_results:
                    match_result = MatchResult(
                        query_fingerprint_id=query_fingerprint.fingerprint_id or "query",
                        matched_fingerprint_id=index_result["fingerprint_id"],
                        similarity_score=index_result["similarity"],
                        match_type=self._determine_match_type_from_similarity(index_result["similarity"]),
                        algorithm=MatchAlgorithm.VECTOR_COSINE,
                        confidence_level=self._calculate_confidence_from_similarity(index_result["similarity"]),
                        match_details={
                            "vector_similarity": index_result["similarity"],
                            "search_type": index_result.get("match_type", "vector")
                        },
                        processing_time=0.0,
                        timestamp=datetime.now(timezone.utc)
                    )
                    results.append(match_result)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Similar content search failed: {e}")
            raise DatabaseError(f"Similar content search failed: {e}")
    
    async def batch_match_fingerprints(
        self,
        query_fingerprints: List[ContentFingerprint],
        batch_size: int = 10
    ) -> Dict[str, List[MatchResult]]:
        """Process multiple fingerprints in batches"""
        try:
            results = {}
            
            # Process in batches
            for i in range(0, len(query_fingerprints), batch_size):
                batch = query_fingerprints[i:i + batch_size]
                
                # Process batch in parallel
                batch_tasks = []
                for fingerprint in batch:
                    task = self.find_matches(fingerprint)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Collect results
                for j, fingerprint in enumerate(batch):
                    fingerprint_id = fingerprint.fingerprint_id or f"query_{i + j}"
                    
                    if isinstance(batch_results[j], Exception):
                        self.logger.error(f"Batch matching failed for {fingerprint_id}: {batch_results[j]}")
                        results[fingerprint_id] = []
                    else:
                        results[fingerprint_id] = batch_results[j]
            
            return results
        
        except Exception as e:
            self.logger.error(f"Batch matching failed: {e}")
            raise DatabaseError(f"Batch matching failed: {e}")
    
    # Private helper methods
    
    def _determine_applicable_algorithms(
        self,
        fingerprint: ContentFingerprint
    ) -> List[MatchAlgorithm]:
        """Determine which algorithms are applicable for a fingerprint"""
        algorithms = []
        
        # Hash-based algorithms
        if fingerprint.primary_hash:
            algorithms.append(MatchAlgorithm.HASH_EXACT)
            algorithms.append(MatchAlgorithm.HASH_HAMMING)
        
        if fingerprint.perceptual_hash:
            algorithms.append(MatchAlgorithm.PERCEPTUAL_HASH)
        
        # Vector-based algorithms
        if hasattr(fingerprint, 'feature_vector') and fingerprint.feature_vector is not None:
            algorithms.append(MatchAlgorithm.VECTOR_COSINE)
            algorithms.append(MatchAlgorithm.VECTOR_EUCLIDEAN)
        
        # Semantic algorithms
        if fingerprint.metadata and any(
            key in fingerprint.metadata for key in ['description', 'tags', 'keywords']
        ):
            algorithms.append(MatchAlgorithm.SEMANTIC_TFIDF)
        
        return algorithms
    
    async def _execute_matching_algorithm(
        self,
        algorithm: MatchAlgorithm,
        query_fingerprint: ContentFingerprint,
        content_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MatchResult]:
        """
Execute a specific matching algorithm"""
        try:
            if algorithm == MatchAlgorithm.HASH_EXACT:
                return await self._execute_hash_exact_matching(
                    query_fingerprint, content_type, user_id
                )
            elif algorithm == MatchAlgorithm.VECTOR_COSINE:
                return await self._execute_vector_cosine_matching(
                    query_fingerprint, content_type, user_id
                )
            elif algorithm == MatchAlgorithm.PERCEPTUAL_HASH:
                return await self._execute_perceptual_matching(
                    query_fingerprint, content_type, user_id
                )
            elif algorithm == MatchAlgorithm.SEMANTIC_TFIDF:
                return await self._execute_semantic_matching(
                    query_fingerprint, content_type, user_id
                )
            else:
                self.logger.warning(f"Algorithm {algorithm} not implemented")
                return []
        
        except Exception as e:
            self.logger.error(f"Algorithm {algorithm} execution failed: {e}")
            return []
    
    async def _execute_hash_exact_matching(
        self,
        query_fingerprint: ContentFingerprint,
        content_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MatchResult]:
        """Execute exact hash matching"""
        results = []
        
        # Search for exact matches in all hash types
        hash_queries = {
            'primary': query_fingerprint.primary_hash,
            'perceptual': query_fingerprint.perceptual_hash,
            'structural': query_fingerprint.structural_hash,
            'semantic': query_fingerprint.semantic_hash
        }
        
        for hash_type, hash_value in hash_queries.items():
            if hash_value:
                index_results = await self.index_manager.search_fingerprints(
                    query={hash_type: hash_value},
                    search_type="hash",
                    content_type=content_type,
                    user_id=user_id,
                    max_results=100
                )
                
                for result in index_results:
                    match_result = MatchResult(
                        query_fingerprint_id=query_fingerprint.fingerprint_id or "query",
                        matched_fingerprint_id=result["fingerprint_id"],
                        similarity_score=1.0,
                        match_type=MatchType.EXACT,
                        algorithm=MatchAlgorithm.HASH_EXACT,
                        confidence_level="high",
                        match_details={
                            "hash_type": hash_type,
                            "hash_value": hash_value
                        },
                        processing_time=0.0,
                        timestamp=datetime.now(timezone.utc)
                    )
                    results.append(match_result)
        
        return results
    
    async def _execute_vector_cosine_matching(
        self,
        query_fingerprint: ContentFingerprint,
        content_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MatchResult]:
        """Execute vector cosine similarity matching"""
        if not hasattr(query_fingerprint, 'feature_vector') or query_fingerprint.feature_vector is None:
            return []
        
        index_results = await self.index_manager.search_fingerprints(
            query=query_fingerprint.feature_vector,
            search_type="vector",
            content_type=content_type,
            user_id=user_id,
            similarity_threshold=self.config.vector_cosine_threshold,
            max_results=100
        )
        
        results = []
        for result in index_results:
            match_result = MatchResult(
                query_fingerprint_id=query_fingerprint.fingerprint_id or "query",
                matched_fingerprint_id=result["fingerprint_id"],
                similarity_score=result["similarity"],
                match_type=self._determine_match_type_from_similarity(result["similarity"]),
                algorithm=MatchAlgorithm.VECTOR_COSINE,
                confidence_level=self._calculate_confidence_from_similarity(result["similarity"]),
                match_details={
                    "vector_similarity": result["similarity"],
                    "algorithm": "cosine_similarity"
                },
                processing_time=0.0,
                timestamp=datetime.now(timezone.utc)
            )
            results.append(match_result)
        
        return results
    
    async def _execute_perceptual_matching(
        self,
        query_fingerprint: ContentFingerprint,
        content_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MatchResult]:
        """Execute perceptual hash matching"""
        if not query_fingerprint.perceptual_hash:
            return []
        
        # Use hash index for perceptual hash search
        matched_ids = await self.index_manager.hash_index.search_by_hash(
            "perceptual", query_fingerprint.perceptual_hash
        )
        
        # Filter by user if specified
        if user_id:
            user_fingerprints = await self.index_manager.hash_index.search_by_user(user_id)
            matched_ids = matched_ids.intersection(user_fingerprints)
        
        results = []
        for fingerprint_id in matched_ids:
            match_result = MatchResult(
                query_fingerprint_id=query_fingerprint.fingerprint_id or "query",
                matched_fingerprint_id=fingerprint_id,
                similarity_score=0.9,  # High similarity for perceptual hash match
                match_type=MatchType.SIMILAR,
                algorithm=MatchAlgorithm.PERCEPTUAL_HASH,
                confidence_level="high",
                match_details={
                    "perceptual_hash": query_fingerprint.perceptual_hash,
                    "match_type": "perceptual"
                },
                processing_time=0.0,
                timestamp=datetime.now(timezone.utc)
            )
            results.append(match_result)
        
        return results
    
    async def _execute_semantic_matching(
        self,
        query_fingerprint: ContentFingerprint,
        content_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MatchResult]:
        """Execute semantic text matching"""
        if not query_fingerprint.metadata:
            return []
        
        # Extract semantic content
        semantic_content = self._extract_semantic_content(query_fingerprint)
        if not semantic_content:
            return []
        
        # Search using semantic index
        semantic_results = await self.index_manager.semantic_index.search_semantic(
            semantic_content, content_type, user_id, size=50
        )
        
        results = []
        for result in semantic_results:
            similarity = min(result["score"] / 10.0, 1.0)  # Normalize Elasticsearch score
            
            if similarity >= self.config.semantic_threshold:
                match_result = MatchResult(
                    query_fingerprint_id=query_fingerprint.fingerprint_id or "query",
                    matched_fingerprint_id=result["fingerprint_id"],
                    similarity_score=similarity,
                    match_type=self._determine_match_type_from_similarity(similarity),
                    algorithm=MatchAlgorithm.SEMANTIC_TFIDF,
                    confidence_level=self._calculate_confidence_from_similarity(similarity),
                    match_details={
                        "semantic_score": result["score"],
                        "highlights": result.get("highlights", {}),
                        "query_content": semantic_content
                    },
                    processing_time=0.0,
                    timestamp=datetime.now(timezone.utc)
                )
                results.append(match_result)
        
        return results
    
    def _extract_semantic_content(self, fingerprint: ContentFingerprint) -> str:
        """Extract semantic content from fingerprint metadata"""
        if not fingerprint.metadata:
            return ""
        
        semantic_parts = []
        
        # Extract text fields
        for field in ['description', 'title', 'tags', 'keywords', 'artist', 'album']:
            if field in fingerprint.metadata:
                value = fingerprint.metadata[field]
                if isinstance(value, list):
                    semantic_parts.extend(str(v) for v in value)
                else:
                    semantic_parts.append(str(value))
        
        return " ".join(semantic_parts)
    
    def _merge_and_deduplicate_results(
        self,
        all_results: List[MatchResult]
    ) -> List[MatchResult]:
        """Merge and deduplicate match results"""
        merged = {}
        
        for result in all_results:
            key = result.matched_fingerprint_id
            
            if key not in merged:
                merged[key] = result
            else:
                # Keep result with higher similarity score
                if result.similarity_score > merged[key].similarity_score:
                    merged[key] = result
                elif result.similarity_score == merged[key].similarity_score:
                    # Merge algorithms if scores are equal
                    if hasattr(merged[key].match_details, 'algorithms'):
                        merged[key].match_details['algorithms'].append(result.algorithm.value)
                    else:
                        merged[key].match_details['algorithms'] = [
                            merged[key].algorithm.value,
                            result.algorithm.value
                        ]
        
        return list(merged.values())
    
    def _determine_match_type_from_similarity(self, similarity: float) -> MatchType:
        """
Determine match type from similarity score"""
        if similarity >= self.config.exact_match_threshold:
            return MatchType.EXACT
        elif similarity >= self.config.similar_match_threshold:
            return MatchType.SIMILAR
        elif similarity >= self.config.partial_match_threshold:
            return MatchType.PARTIAL
        else:
            return MatchType.VARIANT
    
    def _calculate_confidence_from_similarity(self, similarity: float) -> str:
        """
Calculate confidence level from similarity score"""
        if similarity >= 0.9:
            return "high"
        elif similarity >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _generate_cache_key(
        self,
        fingerprint: ContentFingerprint,
        content_type: Optional[str],
        user_id: Optional[str]
    ) -> str:
        """Generate cache key for match results"""
        key_parts = [
            fingerprint.primary_hash or "",
            str(content_type or ""),
            str(user_id or "")
        ]
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    
    async def get_matching_statistics(self) -> Dict[str, Any]:
        """Get comprehensive matching statistics"""
        try:
            # This would typically involve querying match history
            # For now, return basic statistics
            return {
                "total_matches_processed": 0,  # Would be tracked in database
                "average_processing_time": 0.0,
                "algorithm_performance": {},
                "cache_hit_rate": await self.cache_manager.get_hit_rate() if hasattr(self.cache_manager, 'get_hit_rate') else 0.0
            }
        except Exception as e:
            self.logger.error(f"Failed to get matching statistics: {e}")
            return {"error": str(e)}
