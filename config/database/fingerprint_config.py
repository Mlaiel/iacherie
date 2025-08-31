"""Fingerprint Database Configuration Module for IA-Influencer Agent Platform
==========================================================================

Professional fingerprint database configuration for multi-format content
fingerprinting, similarity matching, and AI-powered content identification.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import asyncio
import asyncpg
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

logger = logging.getLogger(__name__)

Base = declarative_base()


class FingerprintType(Enum):
    """Fingerprint algorithm types"""    CHROMAPRINT = "chromaprint"
    SPECTRAL_HASH = "spectral_hash"
    MFCC_FEATURES = "mfcc_features"
    PERCEPTUAL_HASH = "perceptual_hash"
    PHASH = "phash"
    DHASH = "dhash"
    WAVELET_HASH = "wavelet_hash"
    CLIP_EMBEDDING = "clip_embedding"
    BERT_EMBEDDING = "bert_embedding"
    RESNET_FEATURES = "resnet_features"
    VGG_FEATURES = "vgg_features"
    SIFT_FEATURES = "sift_features"
    ORB_FEATURES = "orb_features"


class ContentFormat(Enum):
    """Content format types"""    AUDIO_MP3 = "audio_mp3"
    AUDIO_WAV = "audio_wav"
    AUDIO_FLAC = "audio_flac"
    AUDIO_AAC = "audio_aac"
    AUDIO_OGG = "audio_ogg"
    
    VIDEO_MP4 = "video_mp4"
    VIDEO_AVI = "video_avi"
    VIDEO_MOV = "video_mov"
    VIDEO_MKV = "video_mkv"
    VIDEO_WEBM = "video_webm"
    
    IMAGE_JPG = "image_jpg"
    IMAGE_PNG = "image_png"
    IMAGE_GIF = "image_gif"
    IMAGE_WEBP = "image_webp"
    IMAGE_BMP = "image_bmp"
    
    TEXT_PLAIN = "text_plain"
    TEXT_HTML = "text_html"
    TEXT_MARKDOWN = "text_markdown"
    TEXT_PDF = "text_pdf"


class MatchingAlgorithm(Enum):
    """Similarity matching algorithms"""    COSINE_SIMILARITY = "cosine_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    HAMMING_DISTANCE = "hamming_distance"
    JACCARD_SIMILARITY = "jaccard_similarity"
    LEVENSHTEIN_DISTANCE = "levenshtein_distance"
    SSIM = "ssim"
    MSE = "mse"
    NEURAL_SIMILARITY = "neural_similarity"


class ProcessingStatus(Enum):
    """Fingerprint processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    OPTIMIZING = "optimizing"
    ARCHIVED = "archived"


@dataclass
class FingerprintCredentials:
    """Fingerprint database authentication"""    database_url: str = os.getenv("FINGERPRINT_DATABASE_URL", "postgresql://user:pass@localhost:5432/fingerprints")
    redis_url: str = os.getenv("FINGERPRINT_REDIS_URL", "redis://localhost:6379/4")
    elasticsearch_url: str = os.getenv("FINGERPRINT_ES_URL", "http://localhost:9200")
    vector_db_url: str = os.getenv("FINGERPRINT_VECTOR_URL", "http://localhost:8001")
    
    # ML/AI service endpoints
    audio_processing_url: str = os.getenv("AUDIO_PROCESSING_URL", "http://localhost:8010")
    video_processing_url: str = os.getenv("VIDEO_PROCESSING_URL", "http://localhost:8011")
    image_processing_url: str = os.getenv("IMAGE_PROCESSING_URL", "http://localhost:8012")
    text_processing_url: str = os.getenv("TEXT_PROCESSING_URL", "http://localhost:8013")
    
    pool_size: int = 30
    max_overflow: int = 60


@dataclass
class FingerprintQuality:
    """Fingerprint quality metrics"""    distinctiveness: float = 0.0  # How unique is this fingerprint
    robustness: float = 0.0       # Resistance to transformations
    compactness: float = 0.0      # Storage efficiency
    computation_time: float = 0.0  # Processing time in seconds
    error_rate: float = 0.0       # False positive/negative rate
    confidence_score: float = 0.0 # Overall confidence


@dataclass
class AudioFingerprintConfig:
    """Audio fingerprinting configuration"""    sample_rate: int = 44100
    hop_length: int = 512
    n_fft: int = 2048
    n_mels: int = 128
    n_mfcc: int = 13
    
    # Chromaprint settings
    chromaprint_algorithm: int = 1
    chromaprint_duration: int = 30  # seconds
    
    # Spectral settings
    spectral_features: List[str] = field(default_factory=lambda: [
        "spectral_centroid", "spectral_rolloff", "spectral_bandwidth", "zero_crossing_rate"
    ])
    
    # Quality thresholds
    min_duration: float = 5.0  # minimum 5 seconds
    max_duration: float = 600.0  # maximum 10 minutes
    min_quality_score: float = 0.7


@dataclass
class VideoFingerprintConfig:
    """Video fingerprinting configuration"""    frame_rate: int = 1  # frames per second for analysis
    resize_width: int = 224
    resize_height: int = 224
    
    # Feature extraction
    use_optical_flow: bool = True
    use_edge_detection: bool = True
    use_color_histograms: bool = True
    use_deep_features: bool = True
    
    # Temporal settings
    temporal_window: int = 30  # seconds
    keyframe_extraction: bool = True
    scene_detection: bool = True
    
    # Quality settings
    min_resolution: Tuple[int, int] = (320, 240)
    min_duration: float = 10.0
    max_duration: float = 1800.0  # 30 minutes


@dataclass
class ImageFingerprintConfig:
    """Image fingerprinting configuration"""    resize_dimensions: Tuple[int, int] = (256, 256)
    hash_size: int = 8
    
    # Feature extraction methods
    use_phash: bool = True
    use_dhash: bool = True
    use_wavelet: bool = True
    use_sift: bool = False  # Computationally expensive
    use_orb: bool = True
    use_deep_features: bool = True
    
    # Deep learning models
    clip_model: str = "ViT-B/32"
    resnet_model: str = "resnet50"
    
    # Quality settings
    min_dimensions: Tuple[int, int] = (64, 64)
    supported_formats: List[str] = field(default_factory=lambda: ["jpg", "png", "gif", "webp", "bmp"])


@dataclass
class TextFingerprintConfig:
    """Text fingerprinting configuration"""    max_length: int = 10000  # characters
    min_length: int = 50
    
    # NLP models
    bert_model: str = "bert-base-uncased"
    sentence_transformer: str = "all-MiniLM-L6-v2"
    
    # Feature extraction
    use_ngrams: bool = True
    ngram_range: Tuple[int, int] = (2, 5)
    use_tfidf: bool = True
    use_embeddings: bool = True
    use_syntactic_features: bool = True
    
    # Language settings
    supported_languages: List[str] = field(default_factory=lambda: ["en", "de", "fr", "es", "it"])
    auto_detect_language: bool = True


class ContentFingerprint(Base):
    """Master fingerprint table"""    __tablename__ = 'content_fingerprints_master'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    content_type = Column(String(20), nullable=False, index=True)
    content_format = Column(String(30), nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    content_duration = Column(Float, nullable=True)  # seconds for audio/video
    content_dimensions = Column(String(20), nullable=True)  # WxH for images/videos
    
    # Processing status
    status = Column(String(20), default=ProcessingStatus.PENDING.value, index=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)
    
    # Quality metrics
    quality_metrics = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=0.0)
    
    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)


class AudioFingerprint(Base):
    """Audio-specific fingerprints"""    __tablename__ = 'audio_fingerprints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_fingerprint_id = Column(Integer, nullable=False, index=True)
    
    # Chromaprint data
    chromaprint_fingerprint = Column(Text, nullable=True)
    chromaprint_duration = Column(Float, nullable=True)
    
    # Spectral features
    spectral_hash = Column(String(128), nullable=True)
    mfcc_features = Column(LargeBinary, nullable=True)  # Serialized numpy array
    spectral_features = Column(JSON, nullable=True)
    
    # Audio properties
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    tempo = Column(Float, nullable=True)
    key_signature = Column(String(10), nullable=True)
    
    # Processing metadata
    fingerprint_type = Column(String(30), nullable=False)
    algorithm_version = Column(String(20), nullable=True)
    processing_time = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VideoFingerprint(Base):
    """Video-specific fingerprints"""    __tablename__ = 'video_fingerprints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_fingerprint_id = Column(Integer, nullable=False, index=True)
    
    # Frame-based fingerprints
    keyframe_hashes = Column(JSON, nullable=True)
    perceptual_hash = Column(String(64), nullable=True)
    temporal_hash = Column(String(128), nullable=True)
    
    # Deep features
    resnet_features = Column(LargeBinary, nullable=True)
    optical_flow_features = Column(LargeBinary, nullable=True)
    color_histograms = Column(JSON, nullable=True)
    
    # Video properties
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    codec = Column(String(20), nullable=True)
    total_frames = Column(Integer, nullable=True)
    
    # Scene detection
    scene_boundaries = Column(JSON, nullable=True)
    dominant_colors = Column(JSON, nullable=True)
    
    # Processing metadata
    fingerprint_type = Column(String(30), nullable=False)
    keyframes_extracted = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ImageFingerprint(Base):
    """Image-specific fingerprints"""    __tablename__ = 'image_fingerprints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_fingerprint_id = Column(Integer, nullable=False, index=True)
    
    # Hash-based fingerprints
    phash = Column(String(64), nullable=True)
    dhash = Column(String(64), nullable=True)
    wavelet_hash = Column(String(128), nullable=True)
    
    # Feature descriptors
    sift_features = Column(LargeBinary, nullable=True)
    orb_features = Column(LargeBinary, nullable=True)
    clip_embedding = Column(LargeBinary, nullable=True)
    resnet_features = Column(LargeBinary, nullable=True)
    
    # Image properties
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    color_mode = Column(String(10), nullable=True)
    format = Column(String(10), nullable=True)
    
    # Image analysis
    dominant_colors = Column(JSON, nullable=True)
    edge_density = Column(Float, nullable=True)
    texture_features = Column(JSON, nullable=True)
    
    # Processing metadata
    fingerprint_type = Column(String(30), nullable=False)
    processing_time = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TextFingerprint(Base):
    """Text-specific fingerprints"""    __tablename__ = 'text_fingerprints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_fingerprint_id = Column(Integer, nullable=False, index=True)
    
    # Text hashes
    content_hash = Column(String(64), nullable=False)
    normalized_hash = Column(String(64), nullable=True)
    semantic_hash = Column(String(128), nullable=True)
    
    # Embeddings
    bert_embedding = Column(LargeBinary, nullable=True)
    sentence_embedding = Column(LargeBinary, nullable=True)
    tfidf_features = Column(LargeBinary, nullable=True)
    
    # Text properties
    character_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    sentence_count = Column(Integer, nullable=True)
    language = Column(String(10), nullable=True)
    
    # Linguistic features
    ngram_features = Column(JSON, nullable=True)
    syntactic_features = Column(JSON, nullable=True)
    stylistic_features = Column(JSON, nullable=True)
    
    # Processing metadata
    fingerprint_type = Column(String(30), nullable=False)
    processing_time = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SimilarityMatch(Base):
    """Similarity matching results"""    __tablename__ = 'similarity_matches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_fingerprint_id = Column(Integer, nullable=False, index=True)
    target_fingerprint_id = Column(Integer, nullable=False, index=True)
    
    # Match details
    similarity_score = Column(Float, nullable=False, index=True)
    matching_algorithm = Column(String(30), nullable=False)
    confidence_level = Column(Float, nullable=False)
    
    # Match type classification
    is_exact_match = Column(Boolean, default=False)
    is_near_match = Column(Boolean, default=False)
    is_derivative = Column(Boolean, default=False)
    is_remix = Column(Boolean, default=False)
    
    # Analysis details
    match_segments = Column(JSON, nullable=True)  # Which parts match
    transformation_detected = Column(JSON, nullable=True)
    quality_degradation = Column(Float, nullable=True)
    
    # Processing metadata
    match_processing_time = Column(Float, nullable=True)
    verified_by_human = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class FingerprintConfig:
    """Professional fingerprint configuration"""    
    # Database credentials
    credentials: FingerprintCredentials = field(default_factory=FingerprintCredentials)
    
    # Content-specific configurations
    audio_config: AudioFingerprintConfig = field(default_factory=AudioFingerprintConfig)
    video_config: VideoFingerprintConfig = field(default_factory=VideoFingerprintConfig)
    image_config: ImageFingerprintConfig = field(default_factory=ImageFingerprintConfig)
    text_config: TextFingerprintConfig = field(default_factory=TextFingerprintConfig)
    
    # Matching configuration
    similarity_threshold: float = 0.80
    exact_match_threshold: float = 0.95
    near_match_threshold: float = 0.85
    
    # Performance settings
    max_concurrent_processing: int = 20
    batch_processing_size: int = 100
    cache_ttl: int = 3600
    
    # Feature flags
    enable_real_time_processing: bool = True
    enable_batch_processing: bool = True
    enable_cross_content_matching: bool = True
    enable_ai_enhancement: bool = True
    enable_quality_optimization: bool = True
    
    # Retention settings
    fingerprint_retention_days: int = 1095  # 3 years
    match_history_retention_days: int = 365  # 1 year
    
    def get_content_config(self, content_type: str):
        """Get configuration for specific content type"""        config_map = {
            "audio": self.audio_config,
            "video": self.video_config,
            "image": self.image_config,
            "text": self.text_config
        }
        return config_map.get(content_type)


class FingerprintManager:
    """Professional fingerprint database manager"""    
    def __init__(self, config: FingerprintConfig):
        self.config = config
        self._engine = None
        self._session_factory = None
        self._redis_pool = None
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize fingerprint database connections"""        try:
            # Initialize PostgreSQL connection
            self._engine = create_engine(
                self.config.credentials.database_url,
                pool_size=self.config.credentials.pool_size,
                max_overflow=self.config.credentials.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Initialize Redis for caching
            self._redis_pool = redis.from_url(
                self.config.credentials.redis_url,
                encoding="utf-8", 
                decode_responses=True,
                max_connections=30
            )
            
            # Create tables
            Base.metadata.create_all(self._engine)
            
            # Test connections
            await self._test_connections()
            
            self._is_initialized = True
            logger.info("Fingerprint database manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize fingerprint manager: {e}")
            return False
    
    async def _test_connections(self):
        """Test database connections"""        with self._engine.connect() as conn:
            conn.execute("SELECT 1")
        
        await self._redis_pool.ping()
    
    async def generate_content_hash(self, content: bytes, algorithm: str = "sha256") -> str:
        """Generate cryptographic hash of content"""        if algorithm == "sha256":
            return hashlib.sha256(content).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(content).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    async def create_master_fingerprint(self,
                                      user_id: int,
                                      content_hash: str,
                                      content_type: str,
                                      content_format: ContentFormat,
                                      metadata: Optional[Dict] = None) -> int:
        """Create master fingerprint record"""        try:
            with self._session_factory() as session:
                fingerprint = ContentFingerprint(
                    user_id=user_id,
                    content_hash=content_hash,
                    content_type=content_type,
                    content_format=content_format.value,
                    metadata=metadata,
                    status=ProcessingStatus.PENDING.value
                )
                
                session.add(fingerprint)
                session.commit()
                session.refresh(fingerprint)
                
                logger.info(f"Created master fingerprint {fingerprint.id} for user {user_id}")
                return fingerprint.id
                
        except Exception as e:
            logger.error(f"Failed to create master fingerprint: {e}")
            raise
    
    async def store_audio_fingerprint(self,
                                    master_id: int,
                                    fingerprint_data: Dict[str, Any]) -> int:
        """Store audio fingerprint data"""        try:
            with self._session_factory() as session:
                audio_fp = AudioFingerprint(
                    master_fingerprint_id=master_id,
                    chromaprint_fingerprint=fingerprint_data.get("chromaprint"),
                    chromaprint_duration=fingerprint_data.get("duration"),
                    spectral_hash=fingerprint_data.get("spectral_hash"),
                    mfcc_features=fingerprint_data.get("mfcc_features"),
                    spectral_features=fingerprint_data.get("spectral_features"),
                    sample_rate=fingerprint_data.get("sample_rate"),
                    channels=fingerprint_data.get("channels"),
                    bitrate=fingerprint_data.get("bitrate"),
                    tempo=fingerprint_data.get("tempo"),
                    key_signature=fingerprint_data.get("key"),
                    fingerprint_type=fingerprint_data.get("type", "chromaprint"),
                    processing_time=fingerprint_data.get("processing_time")
                )
                
                session.add(audio_fp)
                session.commit()
                session.refresh(audio_fp)
                
                # Update master status
                master = session.query(ContentFingerprint).filter_by(id=master_id).first()
                if master:
                    master.status = ProcessingStatus.COMPLETED.value
                    master.processing_completed_at = datetime.utcnow()
                    session.commit()
                
                logger.info(f"Stored audio fingerprint {audio_fp.id}")
                return audio_fp.id
                
        except Exception as e:
            logger.error(f"Failed to store audio fingerprint: {e}")
            raise
    
    async def find_similar_content(self,
                                 content_hash: str,
                                 content_type: str,
                                 threshold: float = None) -> List[Dict]:
        """Find similar content using fingerprint matching"""        try:
            if threshold is None:
                threshold = self.config.similarity_threshold
                
            # This is a simplified version - in production would use
            # vector similarity search with FAISS or similar
            with self._session_factory() as session:
                # Find potential matches based on content type
                candidates = session.query(ContentFingerprint).filter(
                    ContentFingerprint.content_type == content_type,
                    ContentFingerprint.status == ProcessingStatus.COMPLETED.value,
                    ContentFingerprint.content_hash != content_hash  # Exclude self
                ).all()
                
                matches = []
                for candidate in candidates:
                    # Simplified similarity calculation
                    # In production, would use proper similarity algorithms
                    similarity = await self._calculate_similarity(content_hash, candidate.content_hash)
                    
                    if similarity >= threshold:
                        matches.append({
                            "fingerprint_id": candidate.id,
                            "user_id": candidate.user_id,
                            "similarity": similarity,
                            "content_type": candidate.content_type,
                            "created_at": candidate.created_at.isoformat()
                        })
                
                # Sort by similarity descending
                matches.sort(key=lambda x: x["similarity"], reverse=True)
                
                logger.info(f"Found {len(matches)} similar content items")
                return matches
                
        except Exception as e:
            logger.error(f"Failed to find similar content: {e}")
            return []
    
    async def _calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two content hashes"""        # Simplified implementation - in production would use
        # appropriate similarity algorithms based on content type
        if hash1 == hash2:
            return 1.0
        
        # Simple Jaccard similarity for demonstration
        set1 = set(hash1)
        set2 = set(hash2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    async def record_similarity_match(self,
                                    source_id: int,
                                    target_id: int,
                                    similarity: float,
                                    algorithm: MatchingAlgorithm,
                                    confidence: float) -> int:
        """Record similarity match result"""        try:
            with self._session_factory() as session:
                match = SimilarityMatch(
                    source_fingerprint_id=source_id,
                    target_fingerprint_id=target_id,
                    similarity_score=similarity,
                    matching_algorithm=algorithm.value,
                    confidence_level=confidence,
                    is_exact_match=similarity >= self.config.exact_match_threshold,
                    is_near_match=similarity >= self.config.near_match_threshold
                )
                
                session.add(match)
                session.commit()
                session.refresh(match)
                
                logger.info(f"Recorded similarity match {match.id}")
                return match.id
                
        except Exception as e:
            logger.error(f"Failed to record similarity match: {e}")
            raise
    
    async def get_fingerprint_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get fingerprint processing statistics"""        try:
            with self._session_factory() as session:
                base_query = session.query(ContentFingerprint)
                if user_id:
                    base_query = base_query.filter_by(user_id=user_id)
                
                stats = {
                    "total_fingerprints": base_query.count(),
                    "by_type": {},
                    "by_status": {},
                    "recent_matches": 0,
                    "processing_stats": {}
                }
                
                # Statistics by content type
                for content_type in ["audio", "video", "image", "text"]:
                    count = base_query.filter_by(content_type=content_type).count()
                    stats["by_type"][content_type] = count
                
                # Statistics by status
                for status in ProcessingStatus:
                    count = base_query.filter_by(status=status.value).count()
                    stats["by_status"][status.value] = count
                
                # Recent matches (last 24 hours)
                recent_date = datetime.utcnow() - timedelta(hours=24)
                stats["recent_matches"] = session.query(SimilarityMatch).filter(
                    SimilarityMatch.created_at >= recent_date
                ).count()
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get fingerprint statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_fingerprints(self):
        """Cleanup old fingerprint data"""        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.fingerprint_retention_days)
            
            with self._session_factory() as session:
                old_count = session.query(ContentFingerprint).filter(
                    ContentFingerprint.created_at < cutoff_date,
                    ContentFingerprint.is_active == False
                ).count()
                
                if old_count > 0:
                    logger.info(f"Would archive {old_count} old fingerprints")
                    # In production, move to archive tables instead of deleting
                
        except Exception as e:
            logger.error(f"Failed to cleanup old fingerprints: {e}")
    
    async def shutdown(self):
        """Shutdown fingerprint manager"""        try:
            if self._redis_pool:
                await self._redis_pool.close()
            
            if self._engine:
                self._engine.dispose()
            
            self._is_initialized = False
            logger.info("Fingerprint manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during fingerprint manager shutdown: {e}")


def create_fingerprint_config() -> FingerprintConfig:
    """Create default fingerprint configuration"""    return FingerprintConfig()


def create_fingerprint_manager(config: Optional[FingerprintConfig] = None) -> FingerprintManager:
    """Create fingerprint manager with configuration"""    if config is None:
        config = create_fingerprint_config()
    return FingerprintManager(config)


# Export configuration for production use
__all__ = [
    'FingerprintType',
    'ContentFormat',
    'MatchingAlgorithm', 
    'ProcessingStatus',
    'FingerprintConfig',
    'FingerprintManager',
    'AudioFingerprintConfig',
    'VideoFingerprintConfig',
    'ImageFingerprintConfig',
    'TextFingerprintConfig',
    'create_fingerprint_config',
    'create_fingerprint_manager'
]
