"""Similarity Detector
===================

Advanced similarity detection system for content protection and copyright enforcement.
Implements state-of-the-art algorithms for multi-modal content matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
from pathlib import Path
import faiss
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import imagehash
from PIL import Image
import cv2
import librosa
from scipy.spatial.distance import euclidean, cosine
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class MatchingStrategy(Enum):
    """Similarity matching strategy."""
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    PERCEPTUAL_HASH = "perceptual_hash"
    FINGERPRINT_MATCH = "fingerprint_match"
    HYBRID_ANALYSIS = "hybrid_analysis"
    DEEP_LEARNING = "deep_learning"

class SimilarityMetric(Enum):
    """Similarity measurement metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    PEARSON = "pearson"

class ContentDomain(Enum):
    """Content domain for specialized processing."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"

@dataclass
class SimilarityScore:
    """Similarity score with detailed breakdown."""
    overall_score: float
    confidence: float
    strategy_used: MatchingStrategy
    metric_used: SimilarityMetric
    domain: ContentDomain
    breakdown: Dict[str, float] = field(default_factory=dict)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class MatchResult:
    """Complete similarity match result."""
    query_id: str
    match_id: str
    similarity_score: SimilarityScore
    match_type: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    false_positive_probability: float = 0.0
    verification_status: str = "pending"
    human_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)

class SimilarityDetector:
    """
    Advanced similarity detection system with multi-modal capabilities.
    
    Features:
    - Multi-strategy similarity detection
    - Vector database integration with FAISS
    - Real-time and batch processing
    - False positive reduction
    - Confidence scoring and uncertainty quantification
    - Performance optimization for large-scale content libraries
    """
    
    def __init__(
        self,
        vector_db_path: str = "/tmp/similarity_vectors",
        default_threshold: float = 0.8,
        enable_gpu: bool = True,
        max_results: int = 100,
        cache_size: int = 10000
    ):
        """
        Initialize similarity detector.
        
        Args:
            vector_db_path: Path for storing vector database
            default_threshold: Default similarity threshold
            enable_gpu: Enable GPU acceleration for vector operations
            max_results: Maximum number of results to return
            cache_size: Size of similarity cache
        """
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        self.default_threshold = default_threshold
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.max_results = max_results
        self.cache_size = cache_size
        
        # Vector databases for different content types
        self.text_index = None
        self.image_index = None
        self.audio_index = None
        self.video_index = None
        
        # Content mappings
        self.content_mappings = {}
        self.vector_mappings = {}
        
        # Similarity cache
        self.similarity_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Performance tracking
        self.search_times = []
        self.comparison_count = 0
        
        # Initialize vectorizers and models
        self._initialize_models()
        
        logger.info(f"SimilarityDetector initialized with GPU: {self.enable_gpu}")
    
    def _initialize_models(self) -> None:
        """Initialize similarity detection models."""
        try:
            # Text vectorizer
            self.text_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3),
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Initialize FAISS indices
            self._initialize_vector_indices()
            
            logger.info("Similarity models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize similarity models: {e}")
            raise
    
    def _initialize_vector_indices(self) -> None:
        """Initialize FAISS vector indices for different content types."""
        # Text index (768-dimensional for sentence transformers)
        self.text_index = faiss.IndexFlatIP(768)
        if self.enable_gpu:
            self.text_index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, self.text_index)
        
        # Image index (512-dimensional for CLIP)
        self.image_index = faiss.IndexFlatIP(512)
        if self.enable_gpu:
            self.image_index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, self.image_index)
        
        # Audio index (13-dimensional for MFCC features)
        self.audio_index = faiss.IndexFlatIP(13)
        
        # Video index (512-dimensional for averaged frame features)
        self.video_index = faiss.IndexFlatIP(512)
    
    async def detect_similarity(
        self,
        query_content: Dict[str, Any],
        content_database: List[Dict[str, Any]],
        strategy: MatchingStrategy = MatchingStrategy.HYBRID_ANALYSIS,
        threshold: Optional[float] = None,
        domain: Optional[ContentDomain] = None
    ) -> List[MatchResult]:
        """
        Detect similarity between query content and database.
        
        Args:
            query_content: Content to search for
            content_database: Database of content to search in
            strategy: Matching strategy to use
            threshold: Similarity threshold (uses default if None)
            domain: Content domain for specialized processing
            
        Returns:
            List[MatchResult]: Sorted list of similarity matches
        """
        start_time = datetime.now()
        threshold = threshold or self.default_threshold
        
        try:
            # Determine content domain if not specified
            if domain is None:
                domain = self._determine_content_domain(query_content)
            
            # Extract features from query content
            query_features = await self._extract_similarity_features(query_content, domain)
            
            # Search for similar content
            matches = await self._search_similar_content(
                query_features, content_database, strategy, domain, threshold
            )
            
            # Post-process and rank results
            ranked_matches = await self._rank_and_filter_matches(matches, threshold)
            
            # Update performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.search_times.append(processing_time)
            
            logger.info(f"Similarity detection completed: {len(ranked_matches)} matches found")
            return ranked_matches
            
        except Exception as e:
            logger.error(f"Similarity detection failed: {e}")
            return []
    
    def _determine_content_domain(self, content: Dict[str, Any]) -> ContentDomain:
        """Determine the content domain based on available features."""
        has_text = bool(content.get('text') or content.get('text_features'))
        has_image = bool(content.get('image') or content.get('image_features'))
        has_audio = bool(content.get('audio') or content.get('audio_features'))
        has_video = bool(content.get('video') or content.get('video_features'))
        
        domain_count = sum([has_text, has_image, has_audio, has_video])
        
        if domain_count > 1:
            return ContentDomain.MULTIMODAL
        elif has_video:
            return ContentDomain.VIDEO
        elif has_audio:
            return ContentDomain.AUDIO
        elif has_image:
            return ContentDomain.IMAGE
        else:
            return ContentDomain.TEXT
    
    async def _extract_similarity_features(
        self,
        content: Dict[str, Any],
        domain: ContentDomain
    ) -> Dict[str, Any]:
        """Extract features for similarity comparison."""
        features = {}
        
        if domain == ContentDomain.TEXT or domain == ContentDomain.MULTIMODAL:
            features['text'] = await self._extract_text_similarity_features(content)
        
        if domain == ContentDomain.IMAGE or domain == ContentDomain.MULTIMODAL:
            features['image'] = await self._extract_image_similarity_features(content)
        
        if domain == ContentDomain.AUDIO or domain == ContentDomain.MULTIMODAL:
            features['audio'] = await self._extract_audio_similarity_features(content)
        
        if domain == ContentDomain.VIDEO or domain == ContentDomain.MULTIMODAL:
            features['video'] = await self._extract_video_similarity_features(content)
        
        return features
    
    async def _extract_text_similarity_features(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text-specific similarity features."""
        text_data = content.get('text', '')
        
        if not text_data and 'text_features' in content:
            return content['text_features']
        
        features = {
            'raw_text': text_data,
            'normalized_text': self._normalize_text(text_data),
            'character_ngrams': self._extract_character_ngrams(text_data),
            'word_ngrams': self._extract_word_ngrams(text_data),
            'content_hash': hashlib.sha256(text_data.encode()).hexdigest(),
            'length': len(text_data),
            'word_count': len(text_data.split()),
            'unique_words': len(set(text_data.lower().split())),
            'readability_features': self._extract_readability_features(text_data)
        }
        
        return features
    
    async def _extract_image_similarity_features(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract image-specific similarity features."""
        if 'image_features' in content:
            return content['image_features']
        
        image_path = content.get('image')
        if not image_path:
            return {}
        
        try:
            # Load image
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                image = image_path
            
            # Extract perceptual hashes
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            whash = str(imagehash.whash(image))
            ahash = str(imagehash.average_hash(image))
            
            # Extract basic properties
            width, height = image.size
            
            features = {
                'perceptual_hash': phash,
                'difference_hash': dhash,
                'wavelet_hash': whash,
                'average_hash': ahash,
                'width': width,
                'height': height,
                'aspect_ratio': width / height,
                'size': width * height,
                'format': getattr(image, 'format', 'unknown')
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {e}")
            return {}
    
    async def _extract_audio_similarity_features(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audio-specific similarity features."""
        if 'audio_features' in content:
            return content['audio_features']
        
        audio_path = content.get('audio')
        if not audio_path:
            return {}
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Extract features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            features = {
                'mfccs': mfccs.mean(axis=1).tolist(),
                'mfcc_std': mfccs.std(axis=1).tolist(),
                'spectral_centroid': float(spectral_centroid.mean()),
                'zero_crossing_rate': float(zero_crossing_rate.mean()),
                'tempo': float(tempo),
                'duration': len(y) / sr,
                'sample_rate': sr,
                'rms_energy': float(np.sqrt(np.mean(y**2)))
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return {}
    
    async def _extract_video_similarity_features(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract video-specific similarity features."""
        if 'video_features' in content:
            return content['video_features']
        
        video_path = content.get('video')
        if not video_path:
            return {}
        
        try:
            # Open video
            cap = cv2.VideoCapture(str(video_path))
            
            # Get properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Sample keyframes
            keyframes = []
            for i in range(0, frame_count, max(1, frame_count // 10)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Convert to grayscale and compute histogram
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    hist = cv2.calcHist([gray_frame], [0], None, [256], [0, 256])
                    keyframes.append(hist.flatten())
            
            cap.release()
            
            # Average keyframe features
            avg_keyframe = np.mean(keyframes, axis=0) if keyframes else np.zeros(256)
            
            features = {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': frame_count / fps if fps > 0 else 0,
                'aspect_ratio': width / height if height > 0 else 0,
                'keyframe_histogram': avg_keyframe.tolist(),
                'keyframe_count': len(keyframes)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            return {}
    
    async def _search_similar_content(
        self,
        query_features: Dict[str, Any],
        content_database: List[Dict[str, Any]],
        strategy: MatchingStrategy,
        domain: ContentDomain,
        threshold: float
    ) -> List[MatchResult]:
        """Search for similar content using specified strategy."""
        matches = []
        
        for content_item in content_database:
            content_id = content_item.get('id', str(hash(str(content_item))))
            
            # Check cache first
            cache_key = f"{hash(str(query_features))}_{content_id}"
            if cache_key in self.similarity_cache:
                similarity_score = self.similarity_cache[cache_key]
                self.cache_hits += 1
            else:
                # Extract features for comparison content
                comparison_features = await self._extract_similarity_features(content_item, domain)
                
                # Calculate similarity based on strategy
                similarity_score = await self._calculate_similarity(
                    query_features, comparison_features, strategy, domain
                )
                
                # Cache result
                if len(self.similarity_cache) < self.cache_size:
                    self.similarity_cache[cache_key] = similarity_score
                self.cache_misses += 1
            
            # Create match if above threshold
            if similarity_score.overall_score >= threshold:
                match = MatchResult(
                    query_id=query_features.get('id', 'query'),
                    match_id=content_id,
                    similarity_score=similarity_score,
                    match_type=self._determine_match_type(similarity_score.overall_score),
                    evidence=self._generate_match_evidence(query_features, content_item, similarity_score),
                    false_positive_probability=self._estimate_false_positive_probability(similarity_score)
                )
                matches.append(match)
            
            self.comparison_count += 1
        
        return matches
    
    async def _calculate_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        strategy: MatchingStrategy,
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate similarity score between two feature sets."""
        start_time = datetime.now()
        
        if strategy == MatchingStrategy.EXACT_MATCH:
            score = await self._exact_match_similarity(features1, features2, domain)
        elif strategy == MatchingStrategy.SEMANTIC_SIMILARITY:
            score = await self._semantic_similarity(features1, features2, domain)
        elif strategy == MatchingStrategy.PERCEPTUAL_HASH:
            score = await self._perceptual_hash_similarity(features1, features2, domain)
        elif strategy == MatchingStrategy.FINGERPRINT_MATCH:
            score = await self._fingerprint_similarity(features1, features2, domain)
        elif strategy == MatchingStrategy.DEEP_LEARNING:
            score = await self._deep_learning_similarity(features1, features2, domain)
        else:  # HYBRID_ANALYSIS
            score = await self._hybrid_similarity(features1, features2, domain)
        
        score.processing_time = (datetime.now() - start_time).total_seconds()
        return score
    
    async def _exact_match_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate exact match similarity."""
        similarities = []
        breakdown = {}
        
        if domain == ContentDomain.TEXT:
            text1 = features1.get('text', {}).get('content_hash', '')
            text2 = features2.get('text', {}).get('content_hash', '')
            text_sim = 1.0 if text1 == text2 else 0.0
            similarities.append(text_sim)
            breakdown['text_hash'] = text_sim
        
        elif domain == ContentDomain.IMAGE:
            img1 = features1.get('image', {})
            img2 = features2.get('image', {})
            
            # Compare multiple hash types
            hash_types = ['perceptual_hash', 'difference_hash', 'wavelet_hash', 'average_hash']
            hash_similarities = []
            
            for hash_type in hash_types:
                if hash_type in img1 and hash_type in img2:
                    sim = 1.0 if img1[hash_type] == img2[hash_type] else 0.0
                    hash_similarities.append(sim)
                    breakdown[hash_type] = sim
            
            similarities.extend(hash_similarities)
        
        overall_score = np.mean(similarities) if similarities else 0.0
        confidence = 1.0 if overall_score == 1.0 else 0.8
        
        return SimilarityScore(
            overall_score=overall_score,
            confidence=confidence,
            strategy_used=MatchingStrategy.EXACT_MATCH,
            metric_used=SimilarityMetric.HAMMING,
            domain=domain,
            breakdown=breakdown
        )
    
    async def _semantic_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate semantic similarity using embeddings."""
        similarities = []
        breakdown = {}
        
        if domain == ContentDomain.TEXT:
            text1 = features1.get('text', {}).get('embeddings', [])
            text2 = features2.get('text', {}).get('embeddings', [])
            
            if text1 and text2:
                emb1 = np.array(text1)
                emb2 = np.array(text2)
                sim = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
                similarities.append(sim)
                breakdown['text_embeddings'] = sim
        
        elif domain == ContentDomain.IMAGE:
            img1 = features1.get('image', {}).get('clip_embeddings', [])
            img2 = features2.get('image', {}).get('clip_embeddings', [])
            
            if img1 and img2:
                emb1 = np.array(img1)
                emb2 = np.array(img2)
                sim = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
                similarities.append(sim)
                breakdown['image_embeddings'] = sim
        
        overall_score = np.mean(similarities) if similarities else 0.0
        confidence = 0.9 if overall_score > 0.8 else 0.7
        
        return SimilarityScore(
            overall_score=overall_score,
            confidence=confidence,
            strategy_used=MatchingStrategy.SEMANTIC_SIMILARITY,
            metric_used=SimilarityMetric.COSINE,
            domain=domain,
            breakdown=breakdown
        )
    
    async def _perceptual_hash_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate perceptual hash similarity."""
        similarities = []
        breakdown = {}
        
        if domain == ContentDomain.IMAGE:
            img1 = features1.get('image', {})
            img2 = features2.get('image', {})
            
            hash_types = ['perceptual_hash', 'difference_hash', 'wavelet_hash']
            for hash_type in hash_types:
                if hash_type in img1 and hash_type in img2:
                    # Calculate Hamming distance for hashes
                    hash1 = imagehash.hex_to_hash(img1[hash_type])
                    hash2 = imagehash.hex_to_hash(img2[hash_type])
                    distance = hash1 - hash2
                    similarity = max(0, 1.0 - distance / 64.0)  # Normalize to 0-1
                    similarities.append(similarity)
                    breakdown[hash_type] = similarity
        
        overall_score = np.mean(similarities) if similarities else 0.0
        confidence = 0.85 if overall_score > 0.7 else 0.6
        
        return SimilarityScore(
            overall_score=overall_score,
            confidence=confidence,
            strategy_used=MatchingStrategy.PERCEPTUAL_HASH,
            metric_used=SimilarityMetric.HAMMING,
            domain=domain,
            breakdown=breakdown
        )
    
    async def _fingerprint_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate fingerprint-based similarity."""
        similarities = []
        breakdown = {}
        
        if domain == ContentDomain.AUDIO:
            audio1 = features1.get('audio', {})
            audio2 = features2.get('audio', {})
            
            # Compare MFCC features
            mfcc1 = audio1.get('mfccs', [])
            mfcc2 = audio2.get('mfccs', [])
            
            if mfcc1 and mfcc2:
                arr1 = np.array(mfcc1)
                arr2 = np.array(mfcc2)
                sim = 1.0 - cosine(arr1, arr2)
                similarities.append(sim)
                breakdown['mfcc_similarity'] = sim
            
            # Compare tempo
            tempo1 = audio1.get('tempo', 0)
            tempo2 = audio2.get('tempo', 0)
            if tempo1 and tempo2:
                tempo_sim = 1.0 - abs(tempo1 - tempo2) / max(tempo1, tempo2, 1)
                similarities.append(tempo_sim)
                breakdown['tempo_similarity'] = tempo_sim
        
        overall_score = np.mean(similarities) if similarities else 0.0
        confidence = 0.8 if overall_score > 0.6 else 0.5
        
        return SimilarityScore(
            overall_score=overall_score,
            confidence=confidence,
            strategy_used=MatchingStrategy.FINGERPRINT_MATCH,
            metric_used=SimilarityMetric.COSINE,
            domain=domain,
            breakdown=breakdown
        )
    
    async def _deep_learning_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate deep learning-based similarity."""
        # Placeholder for advanced deep learning similarity
        # In production, this would use trained neural networks
        return await self._semantic_similarity(features1, features2, domain)
    
    async def _hybrid_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
        domain: ContentDomain
    ) -> SimilarityScore:
        """Calculate hybrid similarity combining multiple strategies."""
        strategies = [
            MatchingStrategy.EXACT_MATCH,
            MatchingStrategy.SEMANTIC_SIMILARITY,
            MatchingStrategy.PERCEPTUAL_HASH,
            MatchingStrategy.FINGERPRINT_MATCH
        ]
        
        scores = []
        combined_breakdown = {}
        
        for strategy in strategies:
            try:
                score = await self._calculate_similarity(features1, features2, strategy, domain)
                if score.overall_score > 0:
                    scores.append(score)
                    combined_breakdown[strategy.value] = score.overall_score
            except:
                continue
        
        if not scores:
            return SimilarityScore(
                overall_score=0.0,
                confidence=0.0,
                strategy_used=MatchingStrategy.HYBRID_ANALYSIS,
                metric_used=SimilarityMetric.COSINE,
                domain=domain
            )
        
        # Weighted average of scores
        weights = [0.4, 0.3, 0.2, 0.1]  # Preference for semantic > exact > perceptual > fingerprint
        weighted_scores = [score.overall_score * weight for score, weight in zip(scores, weights[:len(scores)])]
        overall_score = sum(weighted_scores) / sum(weights[:len(scores)])
        
        # Confidence based on agreement between strategies
        score_variance = np.var([s.overall_score for s in scores])
        confidence = max(0.1, 1.0 - score_variance)
        
        return SimilarityScore(
            overall_score=overall_score,
            confidence=confidence,
            strategy_used=MatchingStrategy.HYBRID_ANALYSIS,
            metric_used=SimilarityMetric.COSINE,
            domain=domain,
            breakdown=combined_breakdown
        )
    
    def _determine_match_type(self, similarity_score: float) -> str:
        """Determine match type based on similarity score."""
        if similarity_score >= 0.95:
            return "exact_match"
        elif similarity_score >= 0.85:
            return "near_duplicate"
        elif similarity_score >= 0.70:
            return "similar_content"
        else:
            return "potential_match"
    
    def _generate_match_evidence(
        self,
        query_features: Dict[str, Any],
        match_content: Dict[str, Any],
        similarity_score: SimilarityScore
    ) -> List[Dict[str, Any]]:
        """Generate evidence for similarity match."""
        evidence = []
        
        for feature_type, score in similarity_score.breakdown.items():
            if score > 0.7:
                evidence.append({
                    "type": feature_type,
                    "score": score,
                    "description": f"High similarity in {feature_type}: {score:.2%}",
                    "supporting_data": {
                        "query_id": query_features.get('id'),
                        "match_id": match_content.get('id'),
                        "feature_comparison": feature_type
                    }
                })
        
        return evidence
    
    def _estimate_false_positive_probability(self, similarity_score: SimilarityScore) -> float:
        """Estimate probability of false positive based on similarity characteristics."""
        # Higher confidence and specific features reduce false positive probability
        fp_probability = 1.0 - similarity_score.confidence
        
        # Adjust based on strategy used
        if similarity_score.strategy_used == MatchingStrategy.EXACT_MATCH:
            fp_probability *= 0.1  # Exact matches rarely false positive
        elif similarity_score.strategy_used == MatchingStrategy.HYBRID_ANALYSIS:
            fp_probability *= 0.3  # Hybrid analysis is more reliable
        
        # Adjust based on score
        if similarity_score.overall_score > 0.9:
            fp_probability *= 0.2
        elif similarity_score.overall_score > 0.8:
            fp_probability *= 0.5
        
        return min(1.0, max(0.0, fp_probability))
    
    async def _rank_and_filter_matches(
        self,
        matches: List[MatchResult],
        threshold: float
    ) -> List[MatchResult]:
        """Rank and filter matches based on comprehensive scoring."""
        # Sort by similarity score and confidence
        ranked_matches = sorted(
            matches,
            key=lambda m: (m.similarity_score.overall_score, m.similarity_score.confidence),
            reverse=True
        )
        
        # Filter duplicates and low-quality matches
        filtered_matches = []
        seen_ids = set()
        
        for match in ranked_matches:
            if (match.match_id not in seen_ids and 
                match.similarity_score.overall_score >= threshold and
                match.false_positive_probability < 0.7):
                
                filtered_matches.append(match)
                seen_ids.add(match.match_id)
                
                if len(filtered_matches) >= self.max_results:
                    break
        
        return filtered_matches
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove extra whitespace, convert to lowercase, remove special characters
        import re
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def _extract_character_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Extract character n-grams from text."""
        normalized_text = self._normalize_text(text)
        return [normalized_text[i:i+n] for i in range(len(normalized_text)-n+1)]
    
    def _extract_word_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract word n-grams from text."""
        words = self._normalize_text(text).split()
        return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    
    def _extract_readability_features(self, text: str) -> Dict[str, float]:
        """Extract readability features from text."""
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        return {
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
            'avg_sentence_length': np.mean([len(s.split()) for s in sentences]) if sentences else 0,
            'sentence_count': len(sentences),
            'word_count': len(words),
            'complexity_score': len(set(words)) / max(1, len(words))
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the similarity detector."""
        cache_hit_rate = self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        avg_search_time = np.mean(self.search_times) if self.search_times else 0
        
        return {
            "total_comparisons": self.comparison_count,
            "cache_hit_rate": cache_hit_rate,
            "average_search_time": avg_search_time,
            "cache_size": len(self.similarity_cache),
            "gpu_enabled": self.enable_gpu,
            "search_time_percentiles": {
                "p50": np.percentile(self.search_times, 50) if self.search_times else 0,
                "p90": np.percentile(self.search_times, 90) if self.search_times else 0,
                "p99": np.percentile(self.search_times, 99) if self.search_times else 0
            }
        }
    
    async def add_to_index(
        self,
        content_id: str,
        content_features: Dict[str, Any],
        domain: ContentDomain
    ) -> None:
        """Add content to the similarity index for future searches."""
        try:
            if domain == ContentDomain.TEXT and 'text' in content_features:
                embeddings = content_features['text'].get('embeddings')
                if embeddings:
                    vector = np.array(embeddings).astype('float32').reshape(1, -1)
                    self.text_index.add(vector)
                    self.content_mappings[self.text_index.ntotal - 1] = content_id
            
            elif domain == ContentDomain.IMAGE and 'image' in content_features:
                embeddings = content_features['image'].get('clip_embeddings')
                if embeddings:
                    vector = np.array(embeddings).astype('float32').reshape(1, -1)
                    self.image_index.add(vector)
                    self.content_mappings[self.image_index.ntotal - 1] = content_id
            
            logger.debug(f"Added content {content_id} to {domain.value} index")
            
        except Exception as e:
            logger.error(f"Failed to add content to index: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""
        self.similarity_cache.clear()
        self.content_mappings.clear()
        self.vector_mappings.clear()
        self.search_times.clear()
        
        logger.info("SimilarityDetector cleanup completed")
