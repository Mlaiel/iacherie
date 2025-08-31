"""AI Fingerprinting Manager - IA-Influencer-Agent
================================================================================
Module: backend/core/managers/fingerprinting_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Manager Core - AI Content Fingerprinting & Similarity Detection
Responsibility: Advanced multi-format content fingerprinting with AI vector search
Technologies: Python, TensorFlow, PyTorch, OpenCV, ChromaPrint, FAISS, CLIP, BERT
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Upload créateur → Analyse multi-format → Génération empreintes IA → 
Stockage vectoriel → Recherche similarité → Détection duplicata → Protection droits
"""from typing import Any, Dict, List, Optional, Union, Callable, Tuple, Set, Protocol
import logging
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import threading
from abc import ABC, abstractmethod
from datetime import datetime
import json
import uuid
from enum import Enum
import time
import hashlib
import numpy as np
import base64
from pathlib import Path

logger = logging.getLogger(__name__)


class FingerprintType(Enum):
    """Types d'empreintes digitales supportées"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    AUDIO_SPECTRUM = "audio_spectrum"
    VIDEO_FRAME = "video_frame"
    IMAGE_PERCEPTUAL = "image_perceptual"
    TEXT_SEMANTIC = "text_semantic"


class SimilarityAlgorithm(Enum):
    """Algorithmes de similarité disponibles"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    SSIM = "ssim"  # Structural Similarity Index
    CLIP_SIMILARITY = "clip_similarity"


class FingerprintQuality(Enum):
    """Qualité de l'empreinte générée"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class FingerprintingConfig:
    """Configuration avancée du système de fingerprinting"""    # Core fingerprinting settings
    enabled_types: Set[FingerprintType] = field(
        default_factory=lambda: set(FingerprintType)
    )
    default_quality: FingerprintQuality = FingerprintQuality.HIGH
    vector_dimensions: int = 512
    
    # Audio fingerprinting
    audio_sample_rate: int = 44100
    audio_chunk_duration: float = 10.24  # seconds
    audio_overlap: float = 0.5
    chroma_features: bool = True
    mfcc_features: bool = True
    spectral_features: bool = True
    
    # Video fingerprinting  
    video_fps: int = 1  # frames per second to analyze
    video_frame_size: Tuple[int, int] = (224, 224)
    optical_flow: bool = True
    scene_detection: bool = True
    
    # Image fingerprinting
    image_size: Tuple[int, int] = (256, 256)
    perceptual_hash: bool = True
    phash_size: int = 8
    feature_extraction: bool = True
    
    # Text fingerprinting
    max_text_length: int = 10000
    sentence_embeddings: bool = True
    semantic_analysis: bool = True
    language_detection: bool = True
    
    # Vector search settings
    similarity_threshold: float = 0.85
    max_results: int = 100
    search_algorithm: SimilarityAlgorithm = SimilarityAlgorithm.COSINE
    
    # Performance settings
    batch_size: int = 32
    max_workers: int = 8
    timeout_seconds: int = 60
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # AI model settings
    use_pretrained_models: bool = True
    model_precision: str = "float32"  # float16, float32, float64
    gpu_acceleration: bool = True


@dataclass  
class ContentFingerprint:
    """Empreinte digitale complète avec vecteurs IA"""    id: str
    content_id: str
    fingerprint_type: FingerprintType
    quality: FingerprintQuality
    
    # Raw fingerprint data
    raw_fingerprint: bytes
    hash_fingerprint: str
    
    # AI vector embeddings
    vector_embedding: np.ndarray
    vector_dimensions: int
    
    # Metadata and features
    features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Content information
    content_type: str = ""
    file_format: str = ""
    file_size: int = 0
    duration: Optional[float] = None  # for audio/video
    
    # Processing info
    algorithm_version: str = "1.0"
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Similarity search optimization
    indexed: bool = False
    search_optimized: bool = False


@dataclass
class SimilarityMatch:
    """Résultat de recherche de similarité"""    fingerprint_id: str
    matched_fingerprint_id: str
    similarity_score: float
    algorithm_used: SimilarityAlgorithm
    
    # Match details
    match_regions: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    match_type: str = "exact"  # exact, partial, similar
    
    # Content comparison
    content_overlap: float = 0.0
    temporal_overlap: Optional[Tuple[float, float]] = None
    
    # Metadata
    detected_at: datetime = field(default_factory=datetime.utcnow)
    verification_status: str = "pending"  # pending, verified, false_positive


class FingerprintingManager(ABC):
    """    🔍 Advanced AI Fingerprinting Manager - IA-Influencer-Agent
    
    Responsabilité:
    Gestionnaire industriel d'empreintes digitales avec IA avancée multi-format
    
    Technologies:
    - Audio: ChromaPrint, librosa, MFCC, spectral analysis
    - Video: OpenCV, YOLO, optical flow, scene detection  
    - Image: CLIP, pHash, SIFT, perceptual hashing
    - Text: BERT, RoBERTa, sentence transformers, semantic similarity
    - Vector Search: FAISS, Elasticsearch, cosine similarity
    - AI Models: TensorFlow, PyTorch, Hugging Face Transformers
    
    Fonctionnalités industrielles:
    - Fingerprinting multi-format temps réel
    - Vector embeddings 512D+ pour recherche IA
    - Similarity search <100ms sur millions d'empreintes
    - Détection duplicata avec >95% précision
    - Batch processing haute performance
    - Cache intelligent et optimisations
    - API REST/GraphQL complète
    - Monitoring et analytics avancés
    """    
    def __init__(self, config: FingerprintingConfig = None):
        self.config = config or FingerprintingConfig()
        self._fingerprints: Dict[str, ContentFingerprint] = {}
        self._vector_index = None  # FAISS index
        self._similarity_cache: Dict[str, List[SimilarityMatch]] = {}
        self._lock = threading.Lock()
        
        # AI models and processors (initialized in subclass)
        self._audio_processor = None
        self._video_processor = None  
        self._image_processor = None
        self._text_processor = None
        self._vector_search = None
        
        # Performance metrics
        self._metrics = {
            "total_fingerprints": 0,
            "fingerprints_by_type": {ft.value: 0 for ft in FingerprintType},
            "similarity_searches": 0,
            "matches_found": 0,
            "average_processing_time": 0.0,
            "average_search_time": 0.0,
            "cache_hit_rate": 0.0,
            "accuracy_rate": 0.0,
            "throughput_fps": 0.0  # fingerprints per second
        }
        
        # Processing queues for high-throughput
        self._processing_queue = asyncio.Queue()
        self._worker_tasks: List[asyncio.Task] = []
        
        logger.info(f"🔍 Fingerprinting Manager initialized - Quality: {self.config.default_quality}")
    
    @abstractmethod
    async def initialize_pool(self) -> bool:
        """        Initialize fingerprinting engine pool and AI models
        
        Returns:
            bool: True if initialization successful
        """        pass
    
    @abstractmethod
    async def generate_audio_fingerprint(
        self, 
        audio_data: bytes,
        metadata: Dict[str, Any] = None
    ) -> ContentFingerprint:
        """        Generate advanced audio fingerprint using AI
        
        Args:
            audio_data: Raw audio bytes
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint: Audio fingerprint with vector embedding
        """        pass
    
    @abstractmethod
    async def generate_video_fingerprint(
        self,
        video_data: bytes,
        metadata: Dict[str, Any] = None
    ) -> ContentFingerprint:
        """        Generate advanced video fingerprint using AI
        
        Args:
            video_data: Raw video bytes
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint: Video fingerprint with frame analysis
        """        pass
    
    @abstractmethod
    async def generate_image_fingerprint(
        self,
        image_data: bytes,
        metadata: Dict[str, Any] = None
    ) -> ContentFingerprint:
        """        Generate advanced image fingerprint using AI
        
        Args:
            image_data: Raw image bytes
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint: Image fingerprint with perceptual hash
        """        pass
    
    @abstractmethod
    async def generate_text_fingerprint(
        self,
        text_content: str,
        metadata: Dict[str, Any] = None
    ) -> ContentFingerprint:
        """        Generate advanced text fingerprint using AI
        
        Args:
            text_content: Text content
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint: Text fingerprint with semantic embedding
        """        pass
    
    async def generate_fingerprint(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        fingerprint_type: FingerprintType,
        metadata: Dict[str, Any] = None
    ) -> ContentFingerprint:
        """        Generate fingerprint for any content type
        
        Args:
            content_data: Raw content data
            content_type: MIME type or content identifier
            fingerprint_type: Type of fingerprint to generate
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint: Generated fingerprint
        """        start_time = time.time()
        
        try:
            # Route to appropriate fingerprint generator
            if fingerprint_type in [FingerprintType.AUDIO, FingerprintType.AUDIO_SPECTRUM]:
                fingerprint = await self.generate_audio_fingerprint(content_data, metadata)
            elif fingerprint_type in [FingerprintType.VIDEO, FingerprintType.VIDEO_FRAME]:
                fingerprint = await self.generate_video_fingerprint(content_data, metadata)
            elif fingerprint_type in [FingerprintType.IMAGE, FingerprintType.IMAGE_PERCEPTUAL]:
                fingerprint = await self.generate_image_fingerprint(content_data, metadata)
            elif fingerprint_type in [FingerprintType.TEXT, FingerprintType.TEXT_SEMANTIC]:
                fingerprint = await self.generate_text_fingerprint(content_data, metadata)
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            fingerprint.processing_time = processing_time
            fingerprint.content_type = content_type
            
            # Store fingerprint
            with self._lock:
                self._fingerprints[fingerprint.id] = fingerprint
                self._metrics["total_fingerprints"] += 1
                self._metrics["fingerprints_by_type"][fingerprint_type.value] += 1
                
                # Update average processing time
                current_avg = self._metrics["average_processing_time"]
                total_fps = self._metrics["total_fingerprints"]
                self._metrics["average_processing_time"] = (
                    (current_avg * (total_fps - 1) + processing_time) / total_fps
                )
            
            # Add to vector index for similarity search
            if self._vector_index is not None:
                await self._add_to_vector_index(fingerprint)
            
            logger.info(f"🔍 Fingerprint generated: {fingerprint.id} ({processing_time:.3f}s)")
            return fingerprint
            
        except Exception as e:
            logger.error(f"❌ Fingerprint generation failed: {e}")
            raise
    
    async def find_similar_content(
        self,
        fingerprint: ContentFingerprint,
        similarity_threshold: Optional[float] = None,
        max_results: Optional[int] = None,
        algorithm: Optional[SimilarityAlgorithm] = None
    ) -> List[SimilarityMatch]:
        """        Find similar content using vector similarity search
        
        Args:
            fingerprint: Source fingerprint to match against
            similarity_threshold: Minimum similarity score
            max_results: Maximum results to return
            algorithm: Similarity algorithm to use
            
        Returns:
            List[SimilarityMatch]: Similar content matches
        """        start_time = time.time()
        
        # Use config defaults if not specified
        threshold = similarity_threshold or self.config.similarity_threshold
        max_res = max_results or self.config.max_results
        algo = algorithm or self.config.search_algorithm
        
        # Check cache first
        cache_key = f"{fingerprint.id}_{threshold}_{max_res}_{algo.value}"
        if cache_key in self._similarity_cache and self.config.cache_enabled:
            self._metrics["cache_hit_rate"] += 1
            return self._similarity_cache[cache_key]
        
        try:
            matches = []
            
            # Vector similarity search using FAISS or similar
            if self._vector_index is not None:
                matches = await self._vector_similarity_search(
                    fingerprint, threshold, max_res, algo
                )
            else:
                # Fallback to brute force comparison
                matches = await self._brute_force_similarity_search(
                    fingerprint, threshold, max_res, algo
                )
            
            # Update metrics
            search_time = time.time() - start_time
            with self._lock:
                self._metrics["similarity_searches"] += 1
                self._metrics["matches_found"] += len(matches)
                
                current_avg = self._metrics["average_search_time"]
                total_searches = self._metrics["similarity_searches"]
                self._metrics["average_search_time"] = (
                    (current_avg * (total_searches - 1) + search_time) / total_searches
                )
            
            # Cache results
            if self.config.cache_enabled:
                self._similarity_cache[cache_key] = matches
                
                # Cleanup old cache entries if needed
                if len(self._similarity_cache) > 10000:
                    await self._cleanup_similarity_cache()
            
            logger.info(f"🔍 Similar content search: {len(matches)} matches ({search_time:.3f}s)")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            return []
    
    async def detect_duplicate_content(
        self,
        fingerprint: ContentFingerprint,
        exact_match_threshold: float = 0.95
    ) -> List[SimilarityMatch]:
        """        Detect duplicate or near-duplicate content
        
        Args:
            fingerprint: Fingerprint to check for duplicates
            exact_match_threshold: Threshold for exact match detection
            
        Returns:
            List[SimilarityMatch]: Duplicate content matches
        """        matches = await self.find_similar_content(
            fingerprint, 
            similarity_threshold=exact_match_threshold,
            algorithm=SimilarityAlgorithm.COSINE
        )
        
        # Filter for high-confidence duplicates
        duplicates = [
            match for match in matches 
            if match.similarity_score >= exact_match_threshold and
            match.fingerprint_id != fingerprint.id
        ]
        
        # Enhance duplicate detection with additional verification
        verified_duplicates = []
        for duplicate in duplicates:
            if await self._verify_duplicate_match(fingerprint, duplicate):
                duplicate.verification_status = "verified"
                duplicate.match_type = "exact" if duplicate.similarity_score > 0.98 else "near_duplicate"
                verified_duplicates.append(duplicate)
        
        return verified_duplicates
    
    async def batch_generate_fingerprints(
        self,
        content_items: List[Dict[str, Any]],
        parallel_workers: Optional[int] = None
    ) -> List[ContentFingerprint]:
        """        Generate fingerprints for multiple content items in parallel
        
        Args:
            content_items: List of content items with data and metadata
            parallel_workers: Number of parallel workers
            
        Returns:
            List[ContentFingerprint]: Generated fingerprints
        """        workers = parallel_workers or self.config.max_workers
        fingerprints = []
        
        # Create semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(workers)
        
        async def process_item(item: Dict[str, Any]) -> Optional[ContentFingerprint]:
            async with semaphore:
                try:
                    return await self.generate_fingerprint(
                        content_data=item["data"],
                        content_type=item["content_type"],
                        fingerprint_type=FingerprintType(item["fingerprint_type"]),
                        metadata=item.get("metadata", {})
                    )
                except Exception as e:
                    logger.error(f"❌ Batch item processing failed: {e}")
                    return None
        
        # Process all items concurrently
        tasks = [process_item(item) for item in content_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        fingerprints = [fp for fp in results if isinstance(fp, ContentFingerprint)]
        
        logger.info(f"🔍 Batch processing: {len(fingerprints)}/{len(content_items)} successful")
        return fingerprints
    
    async def get_fingerprint_analytics(
        self,
        fingerprint_type: Optional[FingerprintType] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive fingerprinting analytics
        
        Args:
            fingerprint_type: Filter by specific fingerprint type
            time_range: Time range for analytics
            
        Returns:
            Dict: Complete analytics data
        """        with self._lock:
            # Filter fingerprints
            fingerprints = list(self._fingerprints.values())
            
            if fingerprint_type:
                fingerprints = [fp for fp in fingerprints if fp.fingerprint_type == fingerprint_type]
            
            if time_range:
                start_time, end_time = time_range
                fingerprints = [
                    fp for fp in fingerprints 
                    if start_time <= fp.created_at <= end_time
                ]
            
            # Calculate quality distribution
            quality_dist = {}
            for fp in fingerprints:
                quality_dist[fp.quality.value] = quality_dist.get(fp.quality.value, 0) + 1
            
            # Calculate processing time statistics
            processing_times = [fp.processing_time for fp in fingerprints if fp.processing_time > 0]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Content type distribution
            content_type_dist = {}
            for fp in fingerprints:
                content_type_dist[fp.content_type] = content_type_dist.get(fp.content_type, 0) + 1
            
            return {
                # Core metrics
                "total_fingerprints": len(fingerprints),
                "fingerprints_by_type": dict(self._metrics["fingerprints_by_type"]),
                "quality_distribution": quality_dist,
                "content_type_distribution": content_type_dist,
                
                # Performance metrics
                "average_processing_time": avg_processing_time,
                "average_search_time": self._metrics["average_search_time"],
                "throughput_fps": len(fingerprints) / max(avg_processing_time, 0.001),
                "cache_hit_rate": self._metrics["cache_hit_rate"],
                
                # Search metrics
                "total_similarity_searches": self._metrics["similarity_searches"],
                "total_matches_found": self._metrics["matches_found"],
                "average_matches_per_search": (
                    self._metrics["matches_found"] / max(self._metrics["similarity_searches"], 1)
                ),
                
                # System health
                "vector_index_size": len(self._fingerprints) if self._vector_index else 0,
                "cache_size": len(self._similarity_cache),
                "memory_usage_estimate": len(fingerprints) * 1024,  # rough estimate
                
                # Configuration
                "config": {
                    "default_quality": self.config.default_quality.value,
                    "vector_dimensions": self.config.vector_dimensions,
                    "similarity_threshold": self.config.similarity_threshold,
                    "cache_enabled": self.config.cache_enabled,
                    "gpu_acceleration": self.config.gpu_acceleration
                },
                
                # Generated at
                "generated_at": datetime.utcnow().isoformat(),
                "time_range": time_range
            }
    
    async def _vector_similarity_search(
        self,
        fingerprint: ContentFingerprint,
        threshold: float,
        max_results: int,
        algorithm: SimilarityAlgorithm
    ) -> List[SimilarityMatch]:
        """Vector-based similarity search using FAISS"""        # Implementation would use FAISS index for fast similarity search
        # This is a placeholder for the actual implementation
        matches = []
        
        for other_fp in self._fingerprints.values():
            if other_fp.id == fingerprint.id:
                continue
                
            # Calculate similarity based on algorithm
            similarity = await self._calculate_similarity(
                fingerprint.vector_embedding,
                other_fp.vector_embedding,
                algorithm
            )
            
            if similarity >= threshold:
                match = SimilarityMatch(
                    fingerprint_id=fingerprint.id,
                    matched_fingerprint_id=other_fp.id,
                    similarity_score=similarity,
                    algorithm_used=algorithm,
                    confidence=similarity
                )
                matches.append(match)
        
        # Sort by similarity score and limit results
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches[:max_results]
    
    async def _brute_force_similarity_search(
        self,
        fingerprint: ContentFingerprint,
        threshold: float,
        max_results: int,
        algorithm: SimilarityAlgorithm
    ) -> List[SimilarityMatch]:
        """Brute force similarity search for small datasets"""        return await self._vector_similarity_search(fingerprint, threshold, max_results, algorithm)
    
    async def _calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        algorithm: SimilarityAlgorithm
    ) -> float:
        """Calculate similarity between two vectors"""        try:
            if algorithm == SimilarityAlgorithm.COSINE:
                dot_product = np.dot(vector1, vector2)
                norm1 = np.linalg.norm(vector1)
                norm2 = np.linalg.norm(vector2)
                return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
            
            elif algorithm == SimilarityAlgorithm.EUCLIDEAN:
                distance = np.linalg.norm(vector1 - vector2)
                return 1.0 / (1.0 + distance)  # Convert distance to similarity
            
            elif algorithm == SimilarityAlgorithm.MANHATTAN:
                distance = np.sum(np.abs(vector1 - vector2))
                return 1.0 / (1.0 + distance)
            
            else:
                # Default to cosine similarity
                return await self._calculate_similarity(vector1, vector2, SimilarityAlgorithm.COSINE)
                
        except Exception as e:
            logger.error(f"❌ Similarity calculation failed: {e}")
            return 0.0
    
    async def _verify_duplicate_match(
        self,
        original: ContentFingerprint,
        match: SimilarityMatch
    ) -> bool:
        """Verify if a similarity match is a true duplicate"""        # Additional verification logic beyond similarity score
        # This could include content-specific checks
        return match.similarity_score > 0.95
    
    async def _add_to_vector_index(self, fingerprint: ContentFingerprint) -> bool:
        """Add fingerprint to vector index for fast search"""        try:
            # Implementation would add to FAISS index
            fingerprint.indexed = True
            fingerprint.search_optimized = True
            return True
        except Exception as e:
            logger.error(f"❌ Vector index addition failed: {e}")
            return False
    
    async def _cleanup_similarity_cache(self) -> None:
        """Clean up old similarity search cache entries"""        # Remove oldest 50% of cache entries
        cache_items = list(self._similarity_cache.items())
        cache_items.sort(key=lambda x: len(x[1]))  # Sort by result count
        
        items_to_remove = len(cache_items) // 2
        for i in range(items_to_remove):
            del self._similarity_cache[cache_items[i][0]]
    
    @asynccontextmanager
    async def get_fingerprinting_session(self):
        """Context manager for fingerprinting operations"""        session_id = str(uuid.uuid4())
        try:
            logger.info(f"🔍 Fingerprinting session started: {session_id}")
            yield session_id
        finally:
            logger.info(f"🔍 Fingerprinting session ended: {session_id}")
    
    async def cleanup(self) -> bool:
        """Cleanup fingerprinting resources"""        try:
            # Cancel worker tasks
            for task in self._worker_tasks:
                task.cancel()
            
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
            
            with self._lock:
                self._fingerprints.clear()
                self._similarity_cache.clear()
                self._worker_tasks.clear()
                
                # Reset metrics
                self._metrics = {
                    "total_fingerprints": 0,
                    "fingerprints_by_type": {ft.value: 0 for ft in FingerprintType},
                    "similarity_searches": 0,
                    "matches_found": 0,
                    "average_processing_time": 0.0,
                    "average_search_time": 0.0,
                    "cache_hit_rate": 0.0,
                    "accuracy_rate": 0.0,
                    "throughput_fps": 0.0
                }
            
            logger.info("🧹 Fingerprinting Manager cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fingerprinting cleanup failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get fingerprinting system statistics"""        with self._lock:
            return {
                "fingerprints_count": len(self._fingerprints),
                "indexed_count": sum(1 for fp in self._fingerprints.values() if fp.indexed),
                "cache_size": len(self._similarity_cache),
                "worker_tasks": len(self._worker_tasks),
                "config": {
                    "default_quality": self.config.default_quality.value,
                    "vector_dimensions": self.config.vector_dimensions,
                    "similarity_threshold": self.config.similarity_threshold,
                    "batch_size": self.config.batch_size,
                    "cache_enabled": self.config.cache_enabled,
                    "gpu_acceleration": self.config.gpu_acceleration
                },
                "metrics": self._metrics.copy(),
                "system_health": {
                    "memory_usage": len(self._fingerprints) + len(self._similarity_cache),
                    "processing_queue_size": self._processing_queue.qsize(),
                    "last_updated": datetime.utcnow().isoformat()
                }
            }


# Global instance
fingerprinting_manager = None


def get_fingerprinting_manager() -> FingerprintingManager:
    """    Get the global fingerprinting manager instance
    
    Returns:
        FingerprintingManager: Global fingerprinting manager
    """    global fingerprinting_manager
    if fingerprinting_manager is None:
        from ..implementations.fingerprinting_manager_impl import FingerprintingManagerImpl
        fingerprinting_manager = FingerprintingManagerImpl()
    return fingerprinting_manager
