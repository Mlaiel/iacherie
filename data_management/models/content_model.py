"""
🎯 Content Model - IA Influencer Agent Platform Enterprise
=========================================================
Module: backend/data_management/models/content_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Content Data Model - Ultra Production-Ready
Responsibility: Advanced data models for multi-format creator content with AI protection and monetization
==========================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC CONTENT PIPELINE:
Upload → Validation → AI Fingerprinting → Metadata Extraction → Vector Embeddings → 
Indexing → Protection → SEO Optimization → Multi-Platform Distribution → Revenue Analytics
"""

from typing import Dict, List, Optional, Any, Union, Tuple, ClassVar
from datetime import datetime, timezone, timedelta
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from pathlib import Path
import uuid
import json
import hashlib
from decimal import Decimal
import numpy as np

class ContentType(Enum):
    """Content types supported by the platform"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    DOCUMENT = "document"
    PODCAST = "podcast"
    STREAM = "stream"
    PHOTO_SERIES = "photo_series"
    ALBUM = "album"
    PLAYLIST = "playlist"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    LIVE = "live"
    MIXED = "mixed"

class ContentStatus(Enum):
    """Content processing status lifecycle"""
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    PROCESSING = "processing"
    FINGERPRINTING = "fingerprinting"
    ANALYZING = "analyzing"
    VECTORIZING = "vectorizing"
    PROTECTING = "protecting"
    SEO_OPTIMIZING = "seo_optimizing"
    PROCESSED = "processed"
    PROTECTED = "protected"
    PUBLISHED = "published"
    DISTRIBUTED = "distributed"
    MONETIZED = "monetized"
    ARCHIVED = "archived"
    FAILED = "failed"
    REJECTED = "rejected"
    DELETED = "deleted"

class ContentQuality(IntEnum):
    """Content quality rating"""
    POOR = 1
    FAIR = 2
    GOOD = 3
    EXCELLENT = 4
    PREMIUM = 5

class ContentOriginality(Enum):
    """Content originality status"""
    ORIGINAL = "original"
    DERIVATIVE = "derivative"
    COVER = "cover"
    REMIX = "remix"
    SAMPLE = "sample"
    COLLABORATION = "collaboration"
    UNKNOWN = "unknown"

class DistributionStatus(Enum):
    """Multi-platform distribution status"""
    PENDING = "pending"
    DISTRIBUTING = "distributing"
    DISTRIBUTED = "distributed"
    PARTIAL = "partial"
    FAILED = "failed"
    BLOCKED = "blocked"

class MonetizationStatus(Enum):
    """Content monetization status"""
    NOT_ELIGIBLE = "not_eligible"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    MONETIZING = "monetizing"
    EARNING = "earning"
    SUSPENDED = "suspended"
    DEMONETIZED = "demonetized"

class CreatorType(Enum):
    """Types de créateurs"""
    MUSICIAN = "musician"
    INFLUENCER = "influencer"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"

class QualityLevel(Enum):
    """Niveaux de qualité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    PROFESSIONAL = "professional"

@dataclass
class ContentFingerprint:
    """Advanced AI fingerprint for content protection and similarity matching"""
    
    # Core fingerprint identifiers
    fingerprint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    fingerprint_type: ContentType = ContentType.MIXED
    
    # AI-generated fingerprints by modality
    audio_fingerprint: Optional[str] = None  # Chromaprint hash
    video_fingerprint: Optional[str] = None  # pHash + frame hashes
    image_fingerprint: Optional[str] = None  # Perceptual hash + CLIP embeddings
    text_fingerprint: Optional[str] = None   # BERT embeddings hash
    
    # Vector embeddings for similarity search
    audio_embeddings: Optional[List[float]] = None  # Audio feature vectors
    visual_embeddings: Optional[List[float]] = None  # Image/video embeddings
    text_embeddings: Optional[List[float]] = None    # Text semantic embeddings
    multimodal_embedding: Optional[List[float]] = None  # Combined embedding
    
    # Fingerprint quality and confidence
    confidence_score: float = 0.0  # 0.0 to 1.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Technical metadata
    algorithm_version: str = "1.0.0"
    processing_time: float = 0.0  # seconds
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_similarity(self, other: 'ContentFingerprint') -> float:
        """Calculate similarity score with another fingerprint"""
        if not other or self.fingerprint_type != other.fingerprint_type:
            return 0.0
            
        similarities = []
        
        # Calculate embedding similarities using cosine similarity
        if self.multimodal_embedding and other.multimodal_embedding:
            sim = self._cosine_similarity(self.multimodal_embedding, other.multimodal_embedding)
            similarities.append(sim)
            
        if self.audio_embeddings and other.audio_embeddings:
            sim = self._cosine_similarity(self.audio_embeddings, other.audio_embeddings)
            similarities.append(sim * 1.2)  # Weight audio higher for music
            
        if self.visual_embeddings and other.visual_embeddings:
            sim = self._cosine_similarity(self.visual_embeddings, other.visual_embeddings)
            similarities.append(sim)
            
        if self.text_embeddings and other.text_embeddings:
            sim = self._cosine_similarity(self.text_embeddings, other.text_embeddings)
            similarities.append(sim * 0.8)  # Weight text lower
            
        return max(similarities) if similarities else 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        except:
            return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "fingerprint_id": self.fingerprint_id,
            "content_id": self.content_id,
            "fingerprint_type": self.fingerprint_type.value,
            "audio_fingerprint": self.audio_fingerprint,
            "video_fingerprint": self.video_fingerprint,
            "image_fingerprint": self.image_fingerprint,
            "text_fingerprint": self.text_fingerprint,
            "audio_embeddings": self.audio_embeddings,
            "visual_embeddings": self.visual_embeddings,
            "text_embeddings": self.text_embeddings,
            "multimodal_embedding": self.multimodal_embedding,
            "confidence_score": self.confidence_score,
            "quality_metrics": self.quality_metrics,
            "algorithm_version": self.algorithm_version,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

@dataclass 
class ContentMetadata:
    """Advanced metadata extraction and enrichment for all content types"""
    
    # Core technical metadata
    file_size: int = 0
    mime_type: str = ""
    file_extension: str = ""
    checksum: str = ""  # SHA-256 hash
    
    # Audio/Video specific
    duration: Optional[float] = None  # seconds
    bitrate: Optional[int] = None     # kbps
    sample_rate: Optional[int] = None # Hz
    channels: Optional[int] = None    # audio channels
    codec: Optional[str] = None
    container_format: Optional[str] = None
    
    # Visual specific
    resolution: Optional[Tuple[int, int]] = None  # (width, height)
    aspect_ratio: Optional[str] = None
    color_space: Optional[str] = None
    frame_rate: Optional[float] = None  # fps for video
    
    # Content metadata
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    language: str = "en"
    
    # Creator metadata  
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[int] = None  # BPM for music
    key: Optional[str] = None    # Musical key
    year: Optional[int] = None
    copyright: Optional[str] = None
    license: Optional[str] = None
    
    # AI-extracted metadata
    ai_generated_tags: List[str] = field(default_factory=list)
    sentiment_score: Optional[float] = None  # -1.0 to 1.0
    content_rating: Optional[str] = None     # G, PG, PG-13, R
    nsfw_score: Optional[float] = None       # 0.0 to 1.0
    
    # SEO metadata
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: List[str] = field(default_factory=list)
    social_media_optimized: bool = False
    
    # Geographic metadata
    location: Optional[str] = None
    gps_coordinates: Optional[Tuple[float, float]] = None
    
    # Quality metrics
    quality_score: float = 0.0  # 0.0 to 1.0
    technical_quality: Dict[str, float] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_seo_score(self) -> float:
        """Calculate SEO optimization score"""
        score = 0.0
        max_score = 10.0
        
        # Title optimization
        if self.seo_title and len(self.seo_title) >= 30:
            score += 2.0
        elif self.title:
            score += 1.0
            
        # Description optimization
        if self.seo_description and len(self.seo_description) >= 100:
            score += 2.0
        elif self.description:
            score += 1.0
            
        # Keywords
        if len(self.seo_keywords) >= 5:
            score += 2.0
        elif len(self.keywords) >= 3:
            score += 1.0
            
        # Tags
        if len(self.tags) >= 10:
            score += 2.0
        elif len(self.tags) >= 5:
            score += 1.0
            
        # Social media optimization
        if self.social_media_optimized:
            score += 2.0
            
        return min(score / max_score, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "file_extension": self.file_extension,
            "checksum": self.checksum,
            "duration": self.duration,
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "codec": self.codec,
            "container_format": self.container_format,
            "resolution": self.resolution,
            "aspect_ratio": self.aspect_ratio,
            "color_space": self.color_space,
            "frame_rate": self.frame_rate,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "keywords": self.keywords,
            "categories": self.categories,
            "language": self.language,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre,
            "mood": self.mood,
            "tempo": self.tempo,
            "key": self.key,
            "year": self.year,
            "copyright": self.copyright,
            "license": self.license,
            "ai_generated_tags": self.ai_generated_tags,
            "sentiment_score": self.sentiment_score,
            "content_rating": self.content_rating,
            "nsfw_score": self.nsfw_score,
            "seo_title": self.seo_title,
            "seo_description": self.seo_description,
            "seo_keywords": self.seo_keywords,
            "social_media_optimized": self.social_media_optimized,
            "location": self.location,
            "gps_coordinates": self.gps_coordinates,
            "quality_score": self.quality_score,
            "technical_quality": self.technical_quality,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
@dataclass
class ContentModel:
    """
    Ultra-advanced content model for multi-format creator content with AI protection and monetization
    Supports: Audio, Video, Images, Documents, Podcasts, Streams with full lifecycle management
    """
    
    # Core identifiers
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    tenant_id: str = ""  # Multi-tenant support
    
    # Content classification
    content_type: ContentType = ContentType.MIXED
    content_status: ContentStatus = ContentStatus.UPLOADED
    originality: ContentOriginality = ContentOriginality.UNKNOWN
    quality: ContentQuality = ContentQuality.GOOD
    
    # File information
    filename: str = ""
    original_filename: str = ""
    file_path: str = ""
    storage_bucket: str = ""
    storage_region: str = ""
    cdn_url: Optional[str] = None
    
    # Content metadata
    metadata: ContentMetadata = field(default_factory=ContentMetadata)
    fingerprint: Optional[ContentFingerprint] = None
    
    # Processing pipeline status
    validation_status: str = "pending"
    processing_stages: Dict[str, str] = field(default_factory=dict)
    processing_errors: List[str] = field(default_factory=list)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    
    # AI Analysis results
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    ai_confidence: float = 0.0
    ai_tags: List[str] = field(default_factory=list)
    ai_recommendations: List[str] = field(default_factory=list)
    
    # Protection and copyright
    copyright_status: str = "unknown"
    protection_enabled: bool = True
    fingerprint_matches: List[str] = field(default_factory=list)
    dmca_claims: List[str] = field(default_factory=list)
    
    # Distribution and publishing
    distribution_status: DistributionStatus = DistributionStatus.PENDING
    published_platforms: List[str] = field(default_factory=list)
    distribution_urls: Dict[str, str] = field(default_factory=dict)
    
    # Monetization
    monetization_status: MonetizationStatus = MonetizationStatus.NOT_ELIGIBLE
    monetization_enabled: bool = False
    revenue_tracking: Dict[str, Any] = field(default_factory=dict)
    licensing_terms: Optional[str] = None
    
    # Analytics and performance
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    download_count: int = 0
    comment_count: int = 0
    engagement_rate: float = 0.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # SEO and discoverability
    seo_score: float = 0.0
    search_keywords: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    trending_score: float = 0.0
    
    # Collaboration
    collaboration_id: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)
    collaboration_terms: Optional[Dict[str, Any]] = None
    
    # Versioning and history
    version: int = 1
    parent_content_id: Optional[str] = None
    child_content_ids: List[str] = field(default_factory=list)
    revision_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps and lifecycle
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    # Cache and optimization
    cache_key: str = field(default_factory=lambda: str(uuid.uuid4()))
    etag: str = field(default_factory=lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest())
    
    def update_status(self, new_status: ContentStatus, error: Optional[str] = None) -> None:
        """Update content status with timestamp tracking"""
        old_status = self.content_status
        self.content_status = new_status
        self.updated_at = datetime.now(timezone.utc)
        
        # Track processing stages
        stage_key = f"{old_status.value}_to_{new_status.value}"
        self.processing_stages[stage_key] = self.updated_at.isoformat()
        
        if error:
            self.processing_errors.append(f"{new_status.value}: {error}")
            
        # Update processing timestamps
        if new_status == ContentStatus.PROCESSING and not self.processing_started_at:
            self.processing_started_at = self.updated_at
        elif new_status in [ContentStatus.PROCESSED, ContentStatus.FAILED]:
            self.processing_completed_at = self.updated_at
    
    def calculate_engagement_rate(self) -> float:
        """Calculate content engagement rate"""
        total_views = max(self.view_count, 1)  # Avoid division by zero
        total_engagement = self.like_count + self.share_count + self.comment_count
        self.engagement_rate = (total_engagement / total_views) * 100
        return self.engagement_rate
    
    def update_seo_score(self) -> float:
        """Update and calculate SEO optimization score"""
        if self.metadata:
            self.seo_score = self.metadata.calculate_seo_score()
        return self.seo_score
    
    def add_fingerprint_match(self, match_content_id: str, similarity: float) -> None:
        """Add a fingerprint match with similarity score"""
        match_data = f"{match_content_id}:{similarity:.3f}"
        if match_data not in self.fingerprint_matches:
            self.fingerprint_matches.append(match_data)
    
    def get_processing_duration(self) -> Optional[float]:
        """Get total processing duration in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            delta = self.processing_completed_at - self.processing_started_at
            return delta.total_seconds()
        return None
    
    def is_monetizable(self) -> bool:
        """Check if content meets monetization criteria"""
        criteria = [
            self.content_status == ContentStatus.PROCESSED,
            self.quality.value >= ContentQuality.GOOD.value,
            self.originality in [ContentOriginality.ORIGINAL, ContentOriginality.COLLABORATION],
            len(self.dmca_claims) == 0,
            self.ai_confidence > 0.7
        ]
        return all(criteria)
    
    def generate_cache_key(self) -> str:
        """Generate optimized cache key"""
        key_data = f"{self.content_id}:{self.version}:{self.updated_at.timestamp()}"
        self.cache_key = hashlib.sha256(key_data.encode()).hexdigest()[:32]
        return self.cache_key
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary with optional sensitive data inclusion"""
        base_data = {
            "content_id": self.content_id,
            "creator_id": self.creator_id,
            "tenant_id": self.tenant_id,
            "content_type": self.content_type.value,
            "content_status": self.content_status.value,
            "originality": self.originality.value,
            "quality": self.quality.value,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "cdn_url": self.cdn_url,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "fingerprint": self.fingerprint.to_dict() if self.fingerprint else None,
            "ai_analysis": self.ai_analysis,
            "ai_confidence": self.ai_confidence,
            "ai_tags": self.ai_tags,
            "ai_recommendations": self.ai_recommendations,
            "copyright_status": self.copyright_status,
            "protection_enabled": self.protection_enabled,
            "distribution_status": self.distribution_status.value,
            "published_platforms": self.published_platforms,
            "distribution_urls": self.distribution_urls,
            "monetization_status": self.monetization_status.value,
            "monetization_enabled": self.monetization_enabled,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "download_count": self.download_count,
            "comment_count": self.comment_count,
            "engagement_rate": self.engagement_rate,
            "seo_score": self.seo_score,
            "search_keywords": self.search_keywords,
            "hashtags": self.hashtags,
            "trending_score": self.trending_score,
            "collaboration_id": self.collaboration_id,
            "collaborators": self.collaborators,
            "version": self.version,
            "parent_content_id": self.parent_content_id,
            "child_content_ids": self.child_content_ids,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "cache_key": self.cache_key,
            "etag": self.etag
        }
        
        if include_sensitive:
            base_data.update({
                "file_path": self.file_path,
                "storage_bucket": self.storage_bucket,
                "storage_region": self.storage_region,
                "processing_stages": self.processing_stages,
                "processing_errors": self.processing_errors,
                "fingerprint_matches": self.fingerprint_matches,
                "dmca_claims": self.dmca_claims,
                "revenue_tracking": self.revenue_tracking,
                "performance_metrics": self.performance_metrics,
                "collaboration_terms": self.collaboration_terms,
                "revision_history": self.revision_history
            })
        
        return base_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentModel':
        """Create ContentModel instance from dictionary"""
        # Handle enum conversions
        if 'content_type' in data:
            data['content_type'] = ContentType(data['content_type'])
        if 'content_status' in data:
            data['content_status'] = ContentStatus(data['content_status'])
        if 'originality' in data:
            data['originality'] = ContentOriginality(data['originality'])
        if 'quality' in data:
            data['quality'] = ContentQuality(data['quality'])
        if 'distribution_status' in data:
            data['distribution_status'] = DistributionStatus(data['distribution_status'])
        if 'monetization_status' in data:
            data['monetization_status'] = MonetizationStatus(data['monetization_status'])
            
        # Handle datetime conversions
        for field in ['created_at', 'updated_at', 'published_at', 'archived_at', 'deleted_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                
        # Handle metadata and fingerprint
        if data.get('metadata'):
            data['metadata'] = ContentMetadata(**data['metadata'])
        if data.get('fingerprint'):
            data['fingerprint'] = ContentFingerprint(**data['fingerprint'])
            
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    
    def __repr__(self) -> str:
        return f"ContentModel(id={self.content_id}, type={self.content_type.value}, status={self.content_status.value})"


@dataclass 
class ContentFingerprint:
    """Empreinte digitale du contenu pour protection"""
    
    # Identifiants
    fingerprint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_hash: str = ""
    perceptual_hash: str = ""
    
    # Fingerprints par type
    audio_fingerprint: Optional[str] = None  # Chromaprint
    video_fingerprint: Optional[str] = None  # Frame hashing
    image_fingerprint: Optional[str] = None  # pHash, dHash
    text_fingerprint: Optional[str] = None  # NLP embeddings
    
    # Vecteurs pour similarity search
    vector_embedding: Optional[List[float]] = None
    vector_dimensions: Optional[int] = None
    
    # Algorithmes utilisés
    algorithms_used: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    # Métadonnées fingerprint
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def generate_content_hash(self, content_bytes: bytes) -> str:
        """Génère un hash unique du contenu"""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content_bytes)
        self.content_hash = sha256_hash.hexdigest()
        return self.content_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour stockage"""
        return {
            "fingerprint_id": self.fingerprint_id,
            "content_hash": self.content_hash,
            "perceptual_hash": self.perceptual_hash,
            "audio_fingerprint": self.audio_fingerprint,
            "video_fingerprint": self.video_fingerprint,
            "image_fingerprint": self.image_fingerprint,
            "text_fingerprint": self.text_fingerprint,
            "vector_embedding": self.vector_embedding,
            "vector_dimensions": self.vector_dimensions,
            "algorithms_used": self.algorithms_used,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class ContentModel:
    """Modèle principal pour le contenu créateur"""
    
    # Identifiants uniques
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    tenant_id: str = ""  # Multi-tenant
    
    # Informations de base
    original_filename: str = ""
    content_type: ContentType = ContentType.MIXED
    creator_type: CreatorType = CreatorType.MUSICIAN
    mime_type: str = ""
    file_extension: str = ""
    
    # Statut et workflow
    status: ContentStatus = ContentStatus.UPLOADED
    processing_stage: str = "upload"
    quality_level: QualityLevel = QualityLevel.MEDIUM
    
    # Stockage
    storage_path: str = ""
    storage_provider: str = "local"  # local, s3, gcs, azure
    storage_bucket: Optional[str] = None
    cdn_url: Optional[str] = None
    
    # Métadonnées et fingerprint
    metadata: ContentMetadata = field(default_factory=lambda: ContentMetadata(file_size=0))
    fingerprint: ContentFingerprint = field(default_factory=ContentFingerprint)
    
    # Versioning et historique
    version: int = 1
    parent_content_id: Optional[str] = None  # Pour versions/dérivés
    children_content_ids: List[str] = field(default_factory=list)
    
    # Protection et droits
    is_protected: bool = False
    protection_level: str = "basic"  # basic, advanced, premium
    rights_metadata: Dict[str, Any] = field(default_factory=dict)
    license_type: str = "all_rights_reserved"
    
    # Distribution et plateformes
    published_platforms: List[str] = field(default_factory=list)
    platform_urls: Dict[str, str] = field(default_factory=dict)
    distribution_status: Dict[str, str] = field(default_factory=dict)
    
    # Analytics et performance
    view_count: int = 0
    download_count: int = 0
    share_count: int = 0
    like_count: int = 0
    revenue_generated: Decimal = field(default_factory=lambda: Decimal('0.00'))
    
    # Collaboration et projets
    project_id: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)
    collaboration_rights: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    
    # Flags et marqueurs
    def __repr__(self) -> str:
        return f"ContentModel(id={self.content_id}, type={self.content_type.value}, status={self.content_status.value})"


# Content processing utility functions
def validate_content_type(file_extension: str) -> ContentType:
    """Validate and determine content type from file extension"""
    ext = file_extension.lower().lstrip('.')
    
    audio_extensions = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aiff', 'wma', 'aac'}
    video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v'}
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'tiff', 'bmp', 'heic'}
    document_extensions = {'txt', 'md', 'html', 'pdf', 'docx', 'rtf', 'odt'}
    
    if ext in audio_extensions:
        return ContentType.AUDIO
    elif ext in video_extensions:
        return ContentType.VIDEO
    elif ext in image_extensions:
        return ContentType.IMAGE
    elif ext in document_extensions:
        return ContentType.DOCUMENT
    else:
        return ContentType.MIXED


def generate_content_path(creator_id: str, content_type: ContentType, created_at: datetime) -> str:
    """Generate optimized storage path for content"""
    date_path = created_at.strftime("%Y/%m/%d")
    type_path = content_type.value
    creator_hash = hashlib.md5(creator_id.encode()).hexdigest()[:8]
    
    return f"content/{creator_hash}/{type_path}/{date_path}"


def calculate_content_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of content file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except FileNotFoundError:
        return ""


# Export all content model classes
__all__ = [
    "ContentType", "ContentStatus", "ContentQuality", "ContentOriginality",
    "DistributionStatus", "MonetizationStatus", "ContentFingerprint", 
    "ContentMetadata", "ContentModel", "validate_content_type",
    "generate_content_path", "calculate_content_hash"
]
