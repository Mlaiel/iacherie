"""IA Influencer Agent Platform - AI and Machine Learning Models
Advanced AI system management and analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Numeric,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .base import (
    BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin,
    AuditMixin, MetadataMixin, StatusMixin
)


class AIModel(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin, MetadataMixin):
    """AI model registry and management"""    
    __tablename__ = 'ai_models'
    
    # Model Identity
    model_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    model_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # fingerprinting, content_analysis, recommendation, generation
    
    # Model Details
    architecture: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # transformer, cnn, lstm, custom
    
    framework: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # tensorflow, pytorch, huggingface, custom
    
    model_size_mb: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Training Information
    training_data_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    training_samples_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    training_duration_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        nullable=True
    )
    
    # Performance Metrics
    accuracy_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    precision_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    recall_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    f1_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Deployment Information
    model_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    checkpoint_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    config_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Resource Requirements
    cpu_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    memory_requirements_mb: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    gpu_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Usage Statistics
    total_inferences: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    average_inference_time_ms: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True
    )
    
    # Relationships
    training_jobs: Mapped[List["AITraining"]] = relationship(
        "AITraining",
        back_populates="model",
        cascade="all, delete-orphan"
    )
    
    inferences: Mapped[List["AIInference"]] = relationship(
        "AIInference",
        back_populates="model",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_models_name_version', 'model_name', 'model_version'),
        Index('idx_ai_models_type_status', 'model_type', 'status'),
        UniqueConstraint('model_name', 'model_version', name='unique_model_version'),
    )


class AITraining(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """AI model training job tracking"""    
    __tablename__ = 'ai_training'
    
    model_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('ai_models.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Training Job Details
    job_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    training_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # initial, fine_tuning, retraining, transfer_learning
    
    # Training Configuration
    hyperparameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    training_config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    # Data Information
    training_dataset: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    validation_dataset: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    test_dataset: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Training Progress
    current_epoch: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    total_epochs: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    estimated_completion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Performance Tracking
    current_loss: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6),
        nullable=True
    )
    
    best_loss: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6),
        nullable=True
    )
    
    validation_accuracy: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Resource Usage
    gpu_hours_used: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 3),
        nullable=True
    )
    
    compute_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    # Results
    final_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    model_artifacts: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    training_logs: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    model: Mapped["AIModel"] = relationship(
        "AIModel",
        back_populates="training_jobs"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_training_model_type', 'model_id', 'training_type'),
        Index('idx_training_status_started', 'status', 'started_at'),
        Index('idx_training_progress', 'progress_percentage'),
    )


class AIInference(BaseModel, UUIDMixin, TimestampMixin):
    """AI model inference execution tracking"""    
    __tablename__ = 'ai_inferences'
    
    model_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('ai_models.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Request Information
    request_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    inference_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # fingerprint_generation, content_analysis, similarity_search
    
    # Input Data
    input_data_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True
    )
    
    input_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Processing Details
    processing_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    processing_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Results
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Status and Error Handling
    is_successful: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Resource Usage
    cpu_usage_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    memory_usage_mb: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    gpu_usage_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # User Context
    user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    session_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Relationships
    model: Mapped["AIModel"] = relationship(
        "AIModel",
        back_populates="inferences"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_inferences_model_type', 'model_id', 'inference_type'),
        Index('idx_inferences_started_at', 'processing_started_at'),
        Index('idx_inferences_successful', 'is_successful'),
        Index('idx_inferences_user', 'user_id'),
    )


class AIFingerprint(BaseModel, UUIDMixin, TimestampMixin):
    """AI-generated fingerprints for content similarity"""    
    __tablename__ = 'ai_fingerprints'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    model_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('ai_models.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Fingerprint Details
    fingerprint_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # perceptual, semantic, acoustic, visual
    
    fingerprint_hash: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Vector Data
    embedding_vector: Mapped[List[float]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    vector_dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Extraction Metadata
    extraction_confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False
    )
    
    extraction_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Search Index Information
    index_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    is_indexed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_fingerprints_content_model', 'content_id', 'model_id'),
        Index('idx_ai_fingerprints_type', 'fingerprint_type'),
        Index('idx_ai_fingerprints_indexed', 'is_indexed'),
        UniqueConstraint('content_id', 'model_id', 'fingerprint_type', name='unique_content_model_fingerprint'),
    )


class VectorEmbedding(BaseModel, UUIDMixin, TimestampMixin):
    """High-dimensional vector embeddings for similarity search"""    
    __tablename__ = 'vector_embeddings'
    
    # Source Reference
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # content, fingerprint, description, metadata
    
    source_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    # Embedding Information
    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    embedding_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Vector Data
    vector_data: Mapped[List[float]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Normalization and Processing
    is_normalized: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    normalization_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Quality Metrics
    embedding_quality: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_embeddings_source', 'source_type', 'source_id'),
        Index('idx_embeddings_model_version', 'embedding_model', 'embedding_version'),
        UniqueConstraint('source_type', 'source_id', 'embedding_model', name='unique_source_embedding'),
    )


class SimilarityMatch(BaseModel, UUIDMixin, TimestampMixin):
    """Similarity matching results and analytics"""    
    __tablename__ = 'similarity_matches'
    
    # Query Information
    query_fingerprint_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('ai_fingerprints.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Match Information
    match_fingerprint_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('ai_fingerprints.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Similarity Metrics
    similarity_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        index=True
    )
    
    distance_metric: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # cosine, euclidean, hamming, jaccard
    
    # Match Details
    match_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # exact, near_exact, partial, derivative
    
    confidence_level: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False
    )
    
    # Processing Information
    algorithm_used: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    processing_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Verification
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    verification_method: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_similarity_query_match', 'query_fingerprint_id', 'match_fingerprint_id'),
        Index('idx_similarity_score', 'similarity_score'),
        Index('idx_similarity_type', 'match_type'),
        UniqueConstraint('query_fingerprint_id', 'match_fingerprint_id', name='unique_fingerprint_match'),
    )


class ContentAnalysis(BaseModel, UUIDMixin, TimestampMixin):
    """AI-powered content analysis and insights"""    
    __tablename__ = 'content_analysis'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Analysis Configuration
    analysis_types: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False
    )  # sentiment, quality, genre, mood, technical
    
    models_used: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False
    )
    
    # Content Understanding
    detected_categories: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Category predictions with confidence
    
    sentiment_analysis: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Sentiment scores
    
    emotion_analysis: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Emotion predictions
    
    # Quality Assessment
    technical_quality: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Audio/video quality metrics
    
    content_quality: Mapped[Optional[Dict[str, Decimal]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Content quality assessment
    
    # Recommendations
    improvement_suggestions: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    optimization_tips: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Overall Scores
    overall_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    marketability_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    virality_potential: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )
    
    # Analysis Metadata
    processing_duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Processing time in seconds
    
    # Indexes
    __table_args__ = (
        Index('idx_analysis_overall_score', 'overall_score'),
        Index('idx_analysis_marketability', 'marketability_score'),
    )
