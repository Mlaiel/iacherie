"""Content Fingerprints Database Model

Enterprise-grade SQLAlchemy model for content fingerprinting and protection.
Manages all types of content fingerprints (audio, video, image, text, multimodal).

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, Optional

Base = declarative_base()


class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    POST = "post"


class FingerprintAlgorithm(Enum):
    """Fingerprint algorithm types"""
    CHROMAPRINT = "chromaprint"
    OPENCV_PHASH = "opencv_phash"
    CLIP_EMBEDDING = "clip_embedding"
    BERT_SEMANTIC = "bert_semantic"
    CUSTOM_HYBRID = "custom_hybrid"
    MULTIMODAL_FUSION = "multimodal_fusion"
    INDUSTRIAL_V4 = "industrial_v4"


class QualityLevel(Enum):
    """Fingerprint quality levels"""
    ULTRA = "ultra"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    EXPERIMENTAL = "experimental"


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    ARCHIVED = "archived"


class ContentFingerprint(Base):
    """
    Enterprise Content Fingerprint Model
    
    Comprehensive fingerprinting for all content types with advanced AI processing.
    Supports multi-modal content analysis, copyright protection, and monetization tracking.
    """
    __tablename__ = "content_fingerprints"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Content classification
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    algorithm = Column(SQLEnum(FingerprintAlgorithm), nullable=False)
    quality_level = Column(SQLEnum(QualityLevel), default=QualityLevel.HIGH)
    
    # Core fingerprint data
    primary_hash = Column(String(255), nullable=False, unique=True, index=True)
    perceptual_hash = Column(String(255), nullable=True, index=True)
    structural_hash = Column(String(255), nullable=True, index=True)
    semantic_hash = Column(String(255), nullable=True, index=True)
    temporal_signature = Column(Text, nullable=True)
    
    # Vector embeddings (for similarity search)
    feature_vector = Column(BYTEA, nullable=True)  # Pickled numpy array
    embedding_vector = Column(BYTEA, nullable=True)  # AI embeddings
    
    # File and metadata information
    original_filename = Column(String(500), nullable=True)
    file_signature = Column(String(64), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Technical metadata
    technical_metadata = Column(JSON, nullable=True)
    extraction_params = Column(JSON, nullable=True)
    quality_metrics = Column(JSON, nullable=True)
    
    # Processing information
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Quality indicators
    confidence_score = Column(Float, default=0.0)
    precision_score = Column(Float, default=0.0)
    uniqueness_score = Column(Float, default=0.0)
    complexity_score = Column(Float, default=0.0)
    
    # Copyright and protection
    is_original = Column(Boolean, default=True)
    copyright_status = Column(String(50), default="protected")
    protection_level = Column(String(50), default="standard")
    ownership_verified = Column(Boolean, default=False)
    
    # Distribution and monetization
    distribution_channels = Column(JSON, nullable=True)
    monetization_enabled = Column(Boolean, default=False)
    revenue_share_percentage = Column(Float, default=100.0)
    
    # Collaboration and licensing
    collaboration_allowed = Column(Boolean, default=False)
    license_type = Column(String(100), default="all_rights_reserved")
    usage_rights = Column(JSON, nullable=True)
    
    # Platform integration
    platform_metadata = Column(JSON, nullable=True)
    external_ids = Column(JSON, nullable=True)  # IDs from Spotify, YouTube, etc.
    sync_status = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_matched_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_searchable = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Analytics and tracking
    match_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    
    # Relationships
    protection_alerts = relationship("ProtectionAlert", back_populates="fingerprint", cascade="all, delete-orphan")
    revenue_records = relationship("RevenueTracking", back_populates="content_fingerprint", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="content_fingerprint", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_fingerprints_user_type', 'user_id', 'content_type'),
        Index('idx_fingerprints_hash_composite', 'primary_hash', 'content_type'),
        Index('idx_fingerprints_status_created', 'processing_status', 'created_at'),
        Index('idx_fingerprints_monetization', 'monetization_enabled', 'is_active'),
        Index('idx_fingerprints_protection', 'copyright_status', 'protection_level'),
        Index('idx_fingerprints_quality', 'quality_level', 'confidence_score'),
        Index('idx_fingerprints_collaboration', 'collaboration_allowed', 'license_type'),
    )
    
    def __repr__(self):
        return f"<ContentFingerprint(id={self.id}, content_type={self.content_type.value}, algorithm={self.algorithm.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "content_id": self.content_id,
            "user_id": str(self.user_id),
            "content_type": self.content_type.value if self.content_type else None,
            "algorithm": self.algorithm.value if self.algorithm else None,
            "quality_level": self.quality_level.value if self.quality_level else None,
            "primary_hash": self.primary_hash,
            "perceptual_hash": self.perceptual_hash,
            "structural_hash": self.structural_hash,
            "semantic_hash": self.semantic_hash,
            "temporal_signature": self.temporal_signature,
            "original_filename": self.original_filename,
            "file_signature": self.file_signature,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "technical_metadata": self.technical_metadata,
            "quality_metrics": self.quality_metrics,
            "processing_status": self.processing_status.value if self.processing_status else None,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "precision_score": self.precision_score,
            "uniqueness_score": self.uniqueness_score,
            "complexity_score": self.complexity_score,
            "is_original": self.is_original,
            "copyright_status": self.copyright_status,
            "protection_level": self.protection_level,
            "ownership_verified": self.ownership_verified,
            "monetization_enabled": self.monetization_enabled,
            "revenue_share_percentage": self.revenue_share_percentage,
            "collaboration_allowed": self.collaboration_allowed,
            "license_type": self.license_type,
            "usage_rights": self.usage_rights,
            "platform_metadata": self.platform_metadata,
            "external_ids": self.external_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_matched_at": self.last_matched_at.isoformat() if self.last_matched_at else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "is_searchable": self.is_searchable,
            "is_verified": self.is_verified,
            "match_count": self.match_count,
            "view_count": self.view_count,
            "download_count": self.download_count,
            "revenue_generated": self.revenue_generated
        }
    
    @classmethod
    def create_from_fingerprint_data(cls, fingerprint_data: Dict[str, Any], user_id: str) -> 'ContentFingerprint':
        """Create ContentFingerprint from fingerprint engine output"""
        return cls(
            content_id=fingerprint_data.get('content_id'),
            user_id=user_id,
            content_type=ContentType(fingerprint_data.get('content_type', 'audio')),
            algorithm=FingerprintAlgorithm(fingerprint_data.get('algorithm', 'custom_hybrid')),
            primary_hash=fingerprint_data.get('primary_hash'),
            perceptual_hash=fingerprint_data.get('perceptual_hash'),
            structural_hash=fingerprint_data.get('structural_hash'),
            semantic_hash=fingerprint_data.get('semantic_hash'),
            temporal_signature=fingerprint_data.get('temporal_signature'),
            file_signature=fingerprint_data.get('file_signature'),
            technical_metadata=fingerprint_data.get('technical_metadata', {}),
            quality_metrics=fingerprint_data.get('quality_indicators', {}),
            confidence_score=fingerprint_data.get('confidence_score', 0.0),
            processing_status=ProcessingStatus.COMPLETED
        )
