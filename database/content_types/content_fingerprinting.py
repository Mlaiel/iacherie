"""
Content Fingerprinting Module - AI-Powered Content Protection System

Module avancé pour la génération d'empreintes numériques et la protection
intelligente du contenu multimédia dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: ML Engineer, Content Protection Specialist, AI Security Expert
Copyright: Fahed Mlaiel - All rights reserved

  AVERTISSEMENT LÉGAL 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging
import hashlib
import asyncio
import json
import base64
import uuid
from enum import Enum

import numpy as np
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, LargeBinary, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .content_models import Base, ContentType, ContentStatus

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of fingerprinting algorithms"""
    PERCEPTUAL_HASH = "perceptual_hash"
    CHROMAPRINT = "chromaprint"
    SPECTROGRAM_HASH = "spectrogram_hash"
    CLIP_EMBEDDING = "clip_embedding"
    BERT_EMBEDDING = "bert_embedding"
    VISUAL_HASH = "visual_hash"
    FRAME_HASH = "frame_hash"
    COMBINED_HASH = "combined_hash"

class FingerprintAlgorithm(Enum):
    """Fingerprinting algorithms by content type"""
    # Audio algorithms
    AUDIO_CHROMAPRINT = "chromaprint"
    AUDIO_ESSENTIA = "essentia"
    AUDIO_SPECTRAL = "spectral_hash"
    AUDIO_MFCC = "mfcc"
    
    # Video algorithms
    VIDEO_OPENCV = "opencv_hash"
    VIDEO_PHASH = "perceptual_hash"
    VIDEO_YOLO = "yolo_features"
    VIDEO_FRAME = "frame_analysis"
    
    # Image algorithms
    IMAGE_CLIP = "clip_embeddings"
    IMAGE_PHASH = "perceptual_hash"
    IMAGE_DHASH = "difference_hash"
    IMAGE_WAVELET = "wavelet_hash"
    
    # Text algorithms
    TEXT_BERT = "bert_embeddings"
    TEXT_ROBERTA = "roberta_embeddings"
    TEXT_TFIDF = "tfidf_vectorizer"
    TEXT_SEMANTIC = "semantic_hash"

class SimilarityMetric(Enum):
    """Similarity measurement methods"""
    COSINE_SIMILARITY = "cosine"
    EUCLIDEAN_DISTANCE = "euclidean"
    HAMMING_DISTANCE = "hamming"
    JACCARD_SIMILARITY = "jaccard"
    MANHATTAN_DISTANCE = "manhattan"
    PEARSON_CORRELATION = "pearson"

@dataclass
class FingerprintVector:
    """Container for fingerprint vector data"""
    vector: np.ndarray
    algorithm: FingerprintAlgorithm
    dimension: int
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_bytes(self) -> bytes:
        """Convert vector to bytes for storage"""



        return self.vector.tobytes()
    
    @classmethod
    def from_bytes(cls, data: bytes, algorithm: FingerprintAlgorithm, 
                   dimension: int, confidence: float = 1.0) -> 'FingerprintVector':
        """Restore vector from bytes"""
        vector = np.frombuffer(data, dtype=np.float32).reshape(-1)
        return cls(vector, algorithm, dimension, confidence)

@dataclass
class SimilarityResult:
    """Container for similarity comparison results"""
    fingerprint_id: str
    similarity_score: float
    metric_used: SimilarityMetric
    algorithm_used: FingerprintAlgorithm
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContentFingerprint(Base):
    """Database model for content fingerprints"""
    __tablename__ = "content_fingerprints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Content information
    content_type = Column(String(20), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    
    # Fingerprint data
    fingerprint_type = Column(String(30), nullable=False)
    algorithm_used = Column(String(50), nullable=False)
    fingerprint_hash = Column(Text, nullable=False, index=True)
    vector_embedding = Column(LargeBinary, nullable=True)
    vector_dimension = Column(Integer, nullable=True)
    
    # Quality metrics
    confidence_score = Column(Float, nullable=False, default=1.0)
    quality_score = Column(Float, nullable=False, default=1.0)
    processing_time = Column(Float, nullable=False)
    
    # Metadata
    metadata = Column(JSONB, nullable=False, default={})
    extraction_metadata = Column(JSONB, nullable=False, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self) -> str:
        return f"<ContentFingerprint(id={self.id}, type={self.content_type}, algorithm={self.algorithm_used})>"

class FingerprintMatch(Base):
    """Database model for fingerprint matches and similarities"""
    __tablename__ = "fingerprint_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=False)
    target_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=False)
    
    # Match details
    similarity_score = Column(Float, nullable=False, index=True)
    similarity_metric = Column(String(30), nullable=False)
    algorithm_used = Column(String(50), nullable=False)
    confidence_level = Column(Float, nullable=False, default=1.0)
    
    # Detection details
    detection_platform = Column(String(100), nullable=True)
    detection_url = Column(Text, nullable=True)
    detection_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Evidence
    evidence_screenshot = Column(Text, nullable=True)
    evidence_metadata = Column(JSONB, nullable=False, default={})
    
    # Status
    match_status = Column(String(20), nullable=False, default='pending')  # pending, confirmed, false_positive, resolved
    is_violation = Column(Boolean, nullable=False, default=False)
    action_taken = Column(String(50), nullable=True)
    
    # Relationships
    source_fingerprint = relationship("ContentFingerprint", foreign_keys=[source_fingerprint_id])
    target_fingerprint = relationship("ContentFingerprint", foreign_keys=[target_fingerprint_id])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<FingerprintMatch(id={self.id}, score={self.similarity_score}, status={self.match_status})>"

class FingerprintProcessor:
    """Advanced fingerprint processing and analysis engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.similarity_threshold = self.config.get('similarity_threshold', 0.85)
        self.vector_cache = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def generate_fingerprint(self, content_path: Path, 
                                 content_type: ContentType,
                                 algorithms: List[FingerprintAlgorithm] = None) -> List[FingerprintVector]:
        """
        Generate multiple fingerprints for content using specified algorithms
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            algorithms: List of algorithms to use (auto-selected if None)
            
        Returns:
            List of fingerprint vectors
        """



        try:
            if algorithms is None:
                algorithms = self._get_default_algorithms(content_type)
            
            fingerprints = []
            for algorithm in algorithms:
                fingerprint = await self._generate_single_fingerprint(
                    content_path, content_type, algorithm
                )
                if fingerprint:
                    fingerprints.append(fingerprint)
            
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            raise
    
    async def _generate_single_fingerprint(self, content_path: Path,
                                         content_type: ContentType,
                                         algorithm: FingerprintAlgorithm) -> Optional[FingerprintVector]:
        """Generate fingerprint using specific algorithm"""



        try:
            if content_type == ContentType.AUDIO:
                return await self._generate_audio_fingerprint(content_path, algorithm)
            elif content_type == ContentType.VIDEO:
                return await self._generate_video_fingerprint(content_path, algorithm)
            elif content_type == ContentType.IMAGE:
                return await self._generate_image_fingerprint(content_path, algorithm)
            elif content_type == ContentType.TEXT:
                return await self._generate_text_fingerprint(content_path, algorithm)
            else:
                self.logger.warning(f"Unsupported content type: {content_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Single fingerprint generation failed for {algorithm}: {e}")
            return None
    
    async def _generate_audio_fingerprint(self, content_path: Path,
                                        algorithm: FingerprintAlgorithm) -> Optional[FingerprintVector]:
        """Generate audio fingerprint using specified algorithm"""



        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(str(content_path), sr=None)
            
            if algorithm == FingerprintAlgorithm.AUDIO_CHROMAPRINT:
                # Use chromaprint for audio fingerprinting
                import acoustid
                duration, fingerprint = acoustid.fingerprint_file(str(content_path))
                vector = np.array([int(x, 16) for x in fingerprint.split(',')], dtype=np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.95)
                
            elif algorithm == FingerprintAlgorithm.AUDIO_MFCC:
                # MFCC features
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                vector = np.mean(mfccs, axis=1).astype(np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.90)
                
            elif algorithm == FingerprintAlgorithm.AUDIO_SPECTRAL:
                # Spectral features
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
                
                features = np.concatenate([
                    np.mean(spectral_centroids, axis=1),
                    np.mean(spectral_rolloff, axis=1),
                    np.mean(spectral_bandwidth, axis=1)
                ]).astype(np.float32)
                
                return FingerprintVector(features, algorithm, len(features), 0.85)
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint generation failed: {e}")
            return None
    
    async def _generate_video_fingerprint(self, content_path: Path,
                                        algorithm: FingerprintAlgorithm) -> Optional[FingerprintVector]:
        """Generate video fingerprint using specified algorithm"""



        try:
            import cv2
            
            cap = cv2.VideoCapture(str(content_path))
            frames = []
            
            # Extract representative frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_count = min(10, frame_count)  # Sample max 10 frames
            
            for i in range(sample_count):
                frame_idx = i * (frame_count // sample_count)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            
            if not frames:
                return None
            
            if algorithm == FingerprintAlgorithm.VIDEO_PHASH:
                # Perceptual hash for video frames
                import imagehash
                from PIL import Image
                
                hashes = []
                for frame in frames:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    phash = imagehash.phash(pil_image)
                    hashes.append(str(phash))
                
                # Combine hashes into vector
                combined_hash = ''.join(hashes)
                vector = np.array([int(x, 16) for x in combined_hash], dtype=np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.88)
            
        except Exception as e:
            self.logger.error(f"Video fingerprint generation failed: {e}")
            return None
    
    async def _generate_image_fingerprint(self, content_path: Path,
                                        algorithm: FingerprintAlgorithm) -> Optional[FingerprintVector]:
        """Generate image fingerprint using specified algorithm"""



        try:
            from PIL import Image
            import imagehash
            
            image = Image.open(content_path)
            
            if algorithm == FingerprintAlgorithm.IMAGE_PHASH:
                phash = imagehash.phash(image)
                vector = np.array([int(x, 16) for x in str(phash)], dtype=np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.92)
                
            elif algorithm == FingerprintAlgorithm.IMAGE_DHASH:
                dhash = imagehash.dhash(image)
                vector = np.array([int(x, 16) for x in str(dhash)], dtype=np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.90)
                
            elif algorithm == FingerprintAlgorithm.IMAGE_CLIP:
                # CLIP embeddings (would require CLIP model)
                # This is a placeholder for CLIP integration
                # In production, would use actual CLIP model
                resized = image.resize((224, 224))
                array = np.array(resized).flatten().astype(np.float32)
                vector = array[:512]  # Simulate CLIP embedding size
                return FingerprintVector(vector, algorithm, len(vector), 0.95)
            
        except Exception as e:
            self.logger.error(f"Image fingerprint generation failed: {e}")
            return None
    
    async def _generate_text_fingerprint(self, content_path: Path,
                                       algorithm: FingerprintAlgorithm) -> Optional[FingerprintVector]:
        """Generate text fingerprint using specified algorithm"""



        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if algorithm == FingerprintAlgorithm.TEXT_TFIDF:
                from sklearn.feature_extraction.text import TfidfVectorizer
                
                vectorizer = TfidfVectorizer(max_features=512, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([text])
                vector = tfidf_matrix.toarray()[0].astype(np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.85)
                
            elif algorithm == FingerprintAlgorithm.TEXT_SEMANTIC:
                # Semantic hashing (simplified)
                import hashlib
                words = text.lower().split()
                word_hashes = [hashlib.md5(word.encode()).hexdigest()[:8] for word in words[:64]]
                vector = np.array([int(h, 16) for h in word_hashes], dtype=np.float32)
                return FingerprintVector(vector, algorithm, len(vector), 0.80)
            
        except Exception as e:
            self.logger.error(f"Text fingerprint generation failed: {e}")
            return None
    
    def _get_default_algorithms(self, content_type: ContentType) -> List[FingerprintAlgorithm]:
        """Get default algorithms for content type"""
        defaults = {
            ContentType.AUDIO: [
                FingerprintAlgorithm.AUDIO_CHROMAPRINT,
                FingerprintAlgorithm.AUDIO_MFCC,
                FingerprintAlgorithm.AUDIO_SPECTRAL
            ],
            ContentType.VIDEO: [
                FingerprintAlgorithm.VIDEO_PHASH,
                FingerprintAlgorithm.VIDEO_OPENCV
            ],
            ContentType.IMAGE: [
                FingerprintAlgorithm.IMAGE_PHASH,
                FingerprintAlgorithm.IMAGE_DHASH,
                FingerprintAlgorithm.IMAGE_CLIP
            ],
            ContentType.TEXT: [
                FingerprintAlgorithm.TEXT_TFIDF,
                FingerprintAlgorithm.TEXT_SEMANTIC
            ]
        }
        return defaults.get(content_type, [])
    
    async def compare_fingerprints(self, fp1: FingerprintVector, fp2: FingerprintVector,
                                 metric: SimilarityMetric = SimilarityMetric.COSINE_SIMILARITY) -> SimilarityResult:
        """Compare two fingerprint vectors using specified metric"""



        try:
            if fp1.algorithm != fp2.algorithm:
                raise ValueError("Cannot compare fingerprints from different algorithms")
            
            if metric == SimilarityMetric.COSINE_SIMILARITY:
                from sklearn.metrics.pairwise import cosine_similarity
                similarity = cosine_similarity([fp1.vector], [fp2.vector])[0][0]
                
            elif metric == SimilarityMetric.EUCLIDEAN_DISTANCE:
                distance = np.linalg.norm(fp1.vector - fp2.vector)
                similarity = 1.0 / (1.0 + distance)  # Convert to similarity
                
            elif metric == SimilarityMetric.HAMMING_DISTANCE:
                # For binary/hash vectors
                distance = np.sum(fp1.vector != fp2.vector)
                similarity = 1.0 - (distance / len(fp1.vector))
                
            else:
                raise ValueError(f"Unsupported similarity metric: {metric}")
            
            confidence = min(fp1.confidence, fp2.confidence)
            
            return SimilarityResult(
                fingerprint_id=str(uuid.uuid4()),
                similarity_score=float(similarity),
                metric_used=metric,
                algorithm_used=fp1.algorithm,
                confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Fingerprint comparison failed: {e}")
            raise
    
    async def batch_similarity_search(self, query_fingerprint: FingerprintVector,
                                    candidate_fingerprints: List[FingerprintVector],
                                    threshold: float = None) -> List[SimilarityResult]:
        """Perform batch similarity search against multiple candidates"""
        threshold = threshold or self.similarity_threshold
        results = []
        
        for candidate in candidate_fingerprints:
            if candidate.algorithm == query_fingerprint.algorithm:
                similarity = await self.compare_fingerprints(query_fingerprint, candidate)
                if similarity.similarity_score >= threshold:
                    results.append(similarity)
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results

class FingerprintManager:
    """High-level fingerprint management interface"""
    
    def __init__(self, processor: FingerprintProcessor = None):
        self.processor = processor or FingerprintProcessor()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_content_fingerprint(self, content_path: Path, content_id: str,
                                       user_id: str, content_type: ContentType) -> ContentFingerprint:
        """Create complete fingerprint record for content"""



        try:
            # Generate fingerprints
            fingerprints = await self.processor.generate_fingerprint(
                content_path, content_type
            )
            
            if not fingerprints:
                raise ValueError("No fingerprints could be generated")
            
            # Use the best quality fingerprint as primary
            primary_fp = max(fingerprints, key=lambda x: x.confidence)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(content_path)
            
            # Create database record
            fingerprint_record = ContentFingerprint(
                content_id=content_id,
                user_id=user_id,
                content_type=content_type.value,
                original_filename=content_path.name,
                file_size=content_path.stat().st_size,
                file_hash=file_hash,
                fingerprint_type=primary_fp.algorithm.value,
                algorithm_used=primary_fp.algorithm.value,
                fingerprint_hash=base64.b64encode(primary_fp.to_bytes()).decode(),
                vector_embedding=primary_fp.to_bytes(),
                vector_dimension=primary_fp.dimension,
                confidence_score=primary_fp.confidence,
                quality_score=self._calculate_quality_score(primary_fp),
                processing_time=0.0,  # Would be measured in real implementation
                metadata=primary_fp.metadata,
                extraction_metadata={
                    'algorithms_used': [fp.algorithm.value for fp in fingerprints],
                    'vector_count': len(fingerprints),
                    'file_info': {
                        'path': str(content_path),
                        'size': content_path.stat().st_size,
                        'modified': content_path.stat().st_mtime
                    }
                }
            )
            
            return fingerprint_record
            
        except Exception as e:
            self.logger.error(f"Content fingerprint creation failed: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _calculate_quality_score(self, fingerprint: FingerprintVector) -> float:
        """Calculate quality score based on fingerprint characteristics"""
        base_score = fingerprint.confidence
        
        # Adjust based on vector dimension (more features = higher quality)
        dimension_factor = min(1.0, fingerprint.dimension / 512)
        
        # Adjust based on algorithm reliability
        algorithm_weights = {
            FingerprintAlgorithm.AUDIO_CHROMAPRINT: 0.95,
            FingerprintAlgorithm.IMAGE_CLIP: 0.95,
            FingerprintAlgorithm.VIDEO_PHASH: 0.90,
            FingerprintAlgorithm.TEXT_BERT: 0.90,
            FingerprintAlgorithm.AUDIO_MFCC: 0.85,
            # Add more algorithm weights as needed
        }
        
        algorithm_weight = algorithm_weights.get(fingerprint.algorithm, 0.80)
        
        quality_score = base_score * dimension_factor * algorithm_weight
        return min(1.0, quality_score)

# Export all classes and enums
__all__ = [
    'FingerprintType',
    'FingerprintAlgorithm', 
    'SimilarityMetric',
    'FingerprintVector',
    'SimilarityResult',
    'ContentFingerprint',
    'FingerprintMatch',
    'FingerprintProcessor',
    'FingerprintManager'
]
