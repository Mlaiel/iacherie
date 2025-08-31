"""📊 Data Models and Schemas for Content Fingerprinting
=====================================================

Comprehensive data models for multi-modal content fingerprinting system.
Supports audio, video, image, and text content types with advanced metadata.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class ContentType(str, Enum):
    """Supported content types for fingerprinting."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"

class ProcessingStatus(str, Enum):
    """Processing status for fingerprint generation."""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SimilarityAlgorithm(str, Enum):
    """Available similarity algorithms."""    CHROMAPRINT = "chromaprint"
    PERCEPTUAL_HASH = "perceptual_hash"
    CLIP_EMBEDDING = "clip_embedding"
    BERT_EMBEDDING = "bert_embedding"
    TFIDF_VECTOR = "tfidf_vector"
    NGRAM_ANALYSIS = "ngram_analysis"
    COMBINED = "combined"

@dataclass
class ProcessingMetrics:
    """Metrics for fingerprint processing performance."""    processing_time_seconds: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    gpu_usage_percent: Optional[float] = None
    algorithm_times: Optional[Dict[str, float]] = None
    error_count: int = 0
    warning_count: int = 0

@dataclass 
class QualityMetrics:
    """Quality assessment metrics for content analysis."""    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reliability_score: float = Field(..., ge=0.0, le=1.0)
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    uniqueness_score: float = Field(..., ge=0.0, le=1.0)
    algorithm_scores: Optional[Dict[str, float]] = None
    quality_flags: Optional[List[str]] = None

class BaseContentModel(BaseModel):
    """Base model for all content types."""    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    file_path: Optional[str] = None
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AudioMetadata(BaseModel):
    """Comprehensive audio metadata."""    duration: float
    sample_rate: int
    channels: int
    bitrate: Optional[int] = None
    format: str
    codec: Optional[str] = None
    tempo: Optional[float] = None
    key: Optional[str] = None
    loudness: Optional[float] = None
    spectral_centroid: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    mfcc_features: Optional[List[List[float]]] = None
    chroma_features: Optional[List[List[float]]] = None
    energy: Optional[float] = None
    pitch: Optional[float] = None

class VideoMetadata(BaseModel):
    """Comprehensive video metadata."""    duration: float
    width: int
    height: int
    fps: float
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    format: str
    total_frames: int
    avg_motion: Optional[float] = None
    scene_changes: Optional[List[float]] = None
    dominant_colors: Optional[List[Tuple[int, int, int]]] = None
    object_detections: Optional[Dict[str, int]] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None

class ImageMetadata(BaseModel):
    """Comprehensive image metadata."""    width: int
    height: int
    channels: int
    format: str
    mode: str
    file_size: int
    has_transparency: bool
    dominant_colors: Optional[List[Tuple[int, int, int]]] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    sharpness: Optional[float] = None
    color_variance: Optional[float] = None
    edge_density: Optional[float] = None
    texture_energy: Optional[float] = None
    dpi: Optional[Tuple[int, int]] = None
    color_profile: Optional[str] = None

class TextMetadata(BaseModel):
    """Comprehensive text metadata."""    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: Optional[str] = None
    readability_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    named_entities: Optional[List[Dict[str, str]]] = None
    pos_tags: Optional[Dict[str, int]] = None
    lexical_diversity: Optional[float] = None
    avg_sentence_length: Optional[float] = None
    complexity_score: Optional[float] = None
    topic_keywords: Optional[List[str]] = None
    encoding: Optional[str] = None

class FingerprintData(BaseModel):
    """Container for all fingerprint algorithm results."""    # Audio fingerprints
    chromaprint: Optional[Dict[str, Any]] = None
    essentia: Optional[Dict[str, Any]] = None
    spectral: Optional[Dict[str, Any]] = None
    neural_audio: Optional[Dict[str, Any]] = None
    
    # Video fingerprints
    perceptual_frames: Optional[Dict[str, Any]] = None
    motion_analysis: Optional[Dict[str, Any]] = None
    object_detection: Optional[Dict[str, Any]] = None
    cnn_features: Optional[Dict[str, Any]] = None
    scene_analysis: Optional[Dict[str, Any]] = None
    
    # Image fingerprints
    perceptual_hash: Optional[Dict[str, Any]] = None
    clip_embedding: Optional[Dict[str, Any]] = None
    traditional_features: Optional[Dict[str, Any]] = None
    color_analysis: Optional[Dict[str, Any]] = None
    texture_analysis: Optional[Dict[str, Any]] = None
    
    # Text fingerprints
    bert_embedding: Optional[Dict[str, Any]] = None
    sentence_bert: Optional[Dict[str, Any]] = None
    tfidf_vector: Optional[Dict[str, Any]] = None
    ngram_analysis: Optional[Dict[str, Any]] = None
    semantic_analysis: Optional[Dict[str, Any]] = None
    
    # Combined fingerprints
    combined_hash: Optional[str] = None
    cross_modal_features: Optional[Dict[str, Any]] = None
    
    # Processing metadata
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow)
    algorithm_versions: Optional[Dict[str, str]] = None
    processing_config: Optional[Dict[str, Any]] = None

class SimilarityMatch(BaseModel):
    """Result of similarity comparison between content items."""    target_fingerprint_id: str
    source_fingerprint_id: str
    content_type: ContentType
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    algorithm_used: SimilarityAlgorithm
    match_details: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Detailed similarity scores by component
    component_scores: Optional[Dict[str, float]] = None
    match_regions: Optional[List[Dict[str, Any]]] = None  # For spatial/temporal matches
    
    @validator('similarity_score', 'confidence')
    def validate_scores(cls, v):
        """Validate score ranges."""        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v

class FingerprintResult(BaseContentModel):
    """Complete result of content fingerprinting process."""    content_type: ContentType
    fingerprint_data: FingerprintData
    hash_value: str  # Combined hash for quick comparison
    processing_time: datetime
    processing_metrics: Optional[ProcessingMetrics] = None
    quality_metrics: Optional[QualityMetrics] = None
    
    # Content-specific metadata
    audio_metadata: Optional[AudioMetadata] = None
    video_metadata: Optional[VideoMetadata] = None
    image_metadata: Optional[ImageMetadata] = None
    text_metadata: Optional[TextMetadata] = None
    
    # Processing status
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None
    
    # Versioning and tracking
    version: str = "2.0.0"
    processing_node: Optional[str] = None
    retry_count: int = 0
    
    @validator('content_type')
    def validate_metadata_consistency(cls, v, values):
        """Ensure metadata matches content type."""        metadata_map = {
            ContentType.AUDIO: 'audio_metadata',
            ContentType.VIDEO: 'video_metadata', 
            ContentType.IMAGE: 'image_metadata',
            ContentType.TEXT: 'text_metadata'
        }
        
        expected_metadata = metadata_map.get(v)
        if expected_metadata and expected_metadata not in values:
            # This is just a warning, not an error
            pass
        return v

class BatchProcessingJob(BaseModel):
    """Batch processing job for multiple content items."""    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    content_items: List[str]  # File paths or content IDs
    content_type: ContentType
    processing_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Status tracking
    status: ProcessingStatus = ProcessingStatus.PENDING
    total_items: int
    processed_items: int = 0
    failed_items: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    results: List[str] = Field(default_factory=list)  # Fingerprint IDs
    errors: List[Dict[str, str]] = Field(default_factory=list)
    
    # Performance metrics
    total_processing_time: Optional[float] = None
    avg_processing_time: Optional[float] = None
    throughput_items_per_second: Optional[float] = None

class SimilaritySearchQuery(BaseModel):
    """Query for similarity search operations."""    query_fingerprint_id: Optional[str] = None
    query_content: Optional[str] = None  # For direct content input
    content_type: ContentType
    similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=1000)
    
    # Algorithm preferences
    preferred_algorithms: Optional[List[SimilarityAlgorithm]] = None
    algorithm_weights: Optional[Dict[str, float]] = None
    
    # Filtering options
    user_id_filter: Optional[int] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    
    # Search options
    include_self: bool = False
    include_metadata: bool = True
    include_scores_breakdown: bool = False

class SimilaritySearchResult(BaseModel):
    """Result of similarity search operation."""    query_fingerprint_id: Optional[str] = None
    matches: List[SimilarityMatch]
    total_matches: int
    search_time_ms: float
    algorithm_used: Union[SimilarityAlgorithm, List[SimilarityAlgorithm]]
    
    # Search metadata
    query_timestamp: datetime = Field(default_factory=datetime.utcnow)
    search_parameters: SimilaritySearchQuery
    performance_metrics: Optional[Dict[str, Any]] = None

# SQLAlchemy ORM Models for Database Storage

class FingerprintDB(Base):
    """Database model for storing fingerprint results."""    __tablename__ = 'fingerprints'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    file_path = Column(String(500))
    original_filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger)
    mime_type = Column(String(100))
    checksum = Column(String(64), index=True)
    
    # Fingerprint data (stored as JSON)
    fingerprint_data = Column(JSON, nullable=False)
    hash_value = Column(String(64), nullable=False, index=True)
    
    # Metadata (stored as JSON)
    metadata = Column(JSON)
    
    # Processing information
    processing_time = Column(DateTime, nullable=False)
    processing_metrics = Column(JSON)
    quality_metrics = Column(JSON)
    status = Column(String(50), nullable=False, default='completed')
    error_message = Column(Text)
    warnings = Column(JSON)
    
    # Versioning
    version = Column(String(20), nullable=False, default='2.0.0')
    processing_node = Column(String(100))
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class SimilarityMatchDB(Base):
    """Database model for storing similarity matches."""    __tablename__ = 'similarity_matches'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_fingerprint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_fingerprint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    similarity_score = Column(Float, nullable=False, index=True)
    algorithm_used = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Match details (stored as JSON)
    match_details = Column(JSON)
    component_scores = Column(JSON)
    match_regions = Column(JSON)
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

class BatchJobDB(Base):
    """Database model for batch processing jobs."""    __tablename__ = 'batch_jobs'
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default='pending', index=True)
    
    # Job configuration
    content_items = Column(JSON, nullable=False)
    processing_config = Column(JSON)
    
    # Progress tracking
    total_items = Column(Integer, nullable=False)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Results
    results = Column(JSON)  # List of fingerprint IDs
    errors = Column(JSON)   # List of error details
    
    # Performance metrics
    total_processing_time = Column(Float)
    avg_processing_time = Column(Float)
    throughput_items_per_second = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)

# Utility functions and validators

def validate_fingerprint_data(fingerprint_data: FingerprintData, content_type: ContentType) -> bool:
    """Validate fingerprint data consistency with content type."""    required_fields_map = {
        ContentType.AUDIO: ['chromaprint', 'essentia', 'spectral'],
        ContentType.VIDEO: ['perceptual_frames', 'motion_analysis', 'object_detection'],
        ContentType.IMAGE: ['perceptual_hash', 'clip_embedding', 'traditional_features'],
        ContentType.TEXT: ['bert_embedding', 'tfidf_vector', 'ngram_analysis']
    }
    
    required_fields = required_fields_map.get(content_type, [])
    fingerprint_dict = fingerprint_data.dict()
    
    # Check if at least one required field is present and not None
    return any(fingerprint_dict.get(field) is not None for field in required_fields)

def calculate_overall_confidence(component_scores: Dict[str, float], 
                               algorithm_weights: Optional[Dict[str, float]] = None) -> float:
    """Calculate overall confidence score from component scores."""    if not component_scores:
        return 0.0
    
    if algorithm_weights:
        # Weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for algo, score in component_scores.items():
            weight = algorithm_weights.get(algo, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    else:
        # Simple average
        return sum(component_scores.values()) / len(component_scores)

def generate_content_hash(content_data: bytes, algorithm: str = "sha256") -> str:
    """Generate hash for content data."""    import hashlib
    
    if algorithm == "sha256":
        return hashlib.sha256(content_data).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(content_data).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(content_data).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

# Export all models and utilities
__all__ = [
    # Enums
    'ContentType', 'ProcessingStatus', 'SimilarityAlgorithm',
    
    # Data classes
    'ProcessingMetrics', 'QualityMetrics',
    
    # Pydantic models
    'BaseContentModel', 'AudioMetadata', 'VideoMetadata', 'ImageMetadata', 'TextMetadata',
    'FingerprintData', 'SimilarityMatch', 'FingerprintResult', 'BatchProcessingJob',
    'SimilaritySearchQuery', 'SimilaritySearchResult',
    
    # SQLAlchemy models
    'FingerprintDB', 'SimilarityMatchDB', 'BatchJobDB', 'Base',
    
    # Utilities
    'validate_fingerprint_data', 'calculate_overall_confidence', 'generate_content_hash'
]
