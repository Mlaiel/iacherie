"""
IA Influencer Agent Platform - Content Protection Models
Advanced AI-powered content protection and rights management system

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime, timezone
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


class ContentProtection(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Core content protection orchestration and management"""
    
    __tablename__ = 'content_protections'
    
    content_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('contents.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    creator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Protection Strategy
    protection_level: Mapped[str] = mapped_column(
        String(20),
        default='standard',
        nullable=False,
        index=True
    )  # basic, standard, advanced, enterprise
    
    protection_methods: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False
    )  # fingerprinting, watermarking, blockchain, drm
    
    # Protection Status
    is_protected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    protection_strength: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal('0.0000'),
        nullable=False,
        index=True
    )  # 0-1 scale protection strength
    
    # Monitoring Configuration
    monitoring_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    monitoring_frequency: Mapped[str] = mapped_column(
        String(20),
        default='daily',
        nullable=False
    )  # realtime, hourly, daily, weekly
    
    monitoring_platforms: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)),
        nullable=True
    )  # youtube, instagram, tiktok, etc.
    
    # Detection Settings
    similarity_threshold: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal('0.8500'),
        nullable=False
    )  # Similarity threshold for violation detection
    
    auto_takedown_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    alert_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Statistics
    violations_detected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True
    )
    
    takedowns_successful: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    estimated_protected_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    # Relationships
    fingerprints: Mapped[List["Fingerprint"]] = relationship(
        "Fingerprint",
        back_populates="protection",
        cascade="all, delete-orphan"
    )
    
    watermarks: Mapped[List["WatermarkRecord"]] = relationship(
        "WatermarkRecord",
        back_populates="protection",
        cascade="all, delete-orphan"
    )
    
    protection_logs: Mapped[List["ProtectionLog"]] = relationship(
        "ProtectionLog",
        back_populates="protection",
        cascade="all, delete-orphan"
    )
    
    violation_reports: Mapped[List["ViolationReport"]] = relationship(
        "ViolationReport",
        back_populates="protection",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_protection_creator_level', 'creator_id', 'protection_level'),
        Index('idx_protection_status_strength', 'is_protected', 'protection_strength'),
        Index('idx_protection_monitoring', 'monitoring_enabled', 'monitoring_frequency'),
        CheckConstraint('protection_strength >= 0 AND protection_strength <= 1', name='valid_protection_strength'),
        CheckConstraint('similarity_threshold >= 0 AND similarity_threshold <= 1', name='valid_similarity_threshold'),
    )


class Fingerprint(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """AI-generated content fingerprints for similarity detection"""
    
    __tablename__ = 'fingerprints'
    
    protection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('content_protections.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    media_file_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('media_files.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Fingerprint Information
    fingerprint_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # audio, video, image, text, perceptual, cryptographic
    
    algorithm_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # chromaprint, perceptual_hash, clip_embedding, bert_embedding
    
    algorithm_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Fingerprint Data
    fingerprint_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True
    )  # Main fingerprint identifier
    
    fingerprint_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )  # Raw fingerprint data (vectors, hashes, etc.)
    
    fingerprint_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Additional metadata (dimensions, format, etc.)
    
    # Vector Data for Similarity Search
    vector_embedding: Mapped[Optional[List[float]]] = mapped_column(
        JSONB,
        nullable=True
    )  # High-dimensional vector for FAISS/similarity search
    
    vector_dimensions: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Quality and Confidence
    extraction_confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        index=True
    )  # Confidence in fingerprint extraction
    
    quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )  # Quality of source material
    
    # Content Segment Information
    segment_start: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True
    )  # Start time for audio/video segments
    
    segment_duration: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True
    )  # Duration of segment
    
    segment_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Indexing and Search
    is_indexed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    index_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # FAISS index identifier
    
    # Usage Statistics
    match_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    last_matched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Relationships
    protection: Mapped["ContentProtection"] = relationship(
        "ContentProtection",
        back_populates="fingerprints"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_fingerprints_type_algorithm', 'fingerprint_type', 'algorithm_name'),
        Index('idx_fingerprints_confidence', 'extraction_confidence'),
        Index('idx_fingerprints_indexed', 'is_indexed', 'index_name'),
        Index('idx_fingerprints_segment', 'segment_start', 'segment_duration'),
        CheckConstraint('extraction_confidence >= 0 AND extraction_confidence <= 1', name='valid_extraction_confidence'),
        CheckConstraint('quality_score >= 0 AND quality_score <= 1 OR quality_score IS NULL', name='valid_quality_score'),
    )


class WatermarkRecord(BaseModel, UUIDMixin, TimestampMixin, AuditMixin):
    """Digital watermarking records for content authentication"""
    
    __tablename__ = 'watermark_records'
    
    protection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('content_protections.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    media_file_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('media_files.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Watermark Information
    watermark_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # visible, invisible, robust, fragile, steganographic
    
    watermark_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # dct, dwt, lsb, frequency_domain, spatial_domain
    
    # Watermark Data
    watermark_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )  # Unique watermark identifier
    
    watermark_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )  # Watermark data/message
    
    embedding_parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )  # Parameters used for embedding
    
    # Strength and Quality
    embedding_strength: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False
    )  # Watermark strength (0-1)
    
    robustness_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # low, medium, high, extreme
    
    imperceptibility_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )  # How imperceptible the watermark is
    
    # Location and Positioning
    embedding_locations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Where in content watermark is embedded
    
    # Verification Data
    verification_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )  # Key for watermark verification
    
    is_verifiable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    verification_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Relationships
    protection: Mapped["ContentProtection"] = relationship(
        "ContentProtection",
        back_populates="watermarks"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_watermarks_type_method', 'watermark_type', 'watermark_method'),
        Index('idx_watermarks_strength_robustness', 'embedding_strength', 'robustness_level'),
        Index('idx_watermarks_active_expiry', 'is_active', 'expiry_date'),
        CheckConstraint('embedding_strength >= 0 AND embedding_strength <= 1', name='valid_embedding_strength'),
        CheckConstraint('imperceptibility_score >= 0 AND imperceptibility_score <= 1 OR imperceptibility_score IS NULL', name='valid_imperceptibility'),
    )


class ProtectionLog(BaseModel, UUIDMixin, TimestampMixin):
    """Comprehensive logging for protection system activities"""
    
    __tablename__ = 'protection_logs'
    
    protection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('content_protections.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Log Information
    log_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # fingerprint_created, violation_detected, takedown_sent, monitoring_scan
    
    log_level: Mapped[str] = mapped_column(
        String(20),
        default='info',
        nullable=False,
        index=True
    )  # debug, info, warning, error, critical
    
    event_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    # Event Details
    event_description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Structured event data
    
    # System Context
    system_component: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # fingerprinting_engine, monitoring_crawler, takedown_processor
    
    process_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # User and Session
    user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    session_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Performance Metrics
    execution_time: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True
    )  # Execution time in seconds
    
    memory_usage: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Memory usage in MB
    
    # Error Information
    error_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    error_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    stack_trace: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    protection: Mapped["ContentProtection"] = relationship(
        "ContentProtection",
        back_populates="protection_logs"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_protection_logs_type_level', 'log_type', 'log_level'),
        Index('idx_protection_logs_created_at', 'created_at'),
        Index('idx_protection_logs_user', 'user_id', 'session_id'),
        Index('idx_protection_logs_component', 'system_component'),
    )


class ViolationReport(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Content violation detection and reporting system"""
    
    __tablename__ = 'violation_reports'
    
    protection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('content_protections.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Violation Details
    violation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # copyright_infringement, unauthorized_use, similarity_match
    
    detected_platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # youtube, instagram, tiktok, website
    
    infringing_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        index=True
    )
    
    infringing_content_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )  # Platform-specific content ID
    
    # Similarity Analysis
    similarity_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        index=True
    )  # 0-1 similarity score
    
    match_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # exact, partial, substantial, derivative
    
    matched_segments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Which parts of content match
    
    # Detection Information
    detection_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # automated_scan, manual_report, ai_analysis
    
    detection_confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False
    )  # Confidence in violation detection
    
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Infringing Party Information
    infringer_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    infringer_profile_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    infringer_contact: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True
    )
    
    # Content Analysis
    infringing_content_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )  # Title, description, tags, etc.
    
    view_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    like_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    estimated_revenue_impact: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    # Response Actions
    action_taken: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # takedown_request, legal_notice, ignored, monitoring
    
    action_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    action_result: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # successful, failed, pending, partial
    
    # Evidence Collection
    evidence_urls: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )  # Screenshots, recordings, etc.
    
    evidence_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Legal Information
    legal_basis: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )  # DMCA, copyright law, terms of service
    
    jurisdiction: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Relationships
    protection: Mapped["ContentProtection"] = relationship(
        "ContentProtection",
        back_populates="violation_reports"
    )
    
    takedown_requests: Mapped[List["TakedownRequest"]] = relationship(
        "TakedownRequest",
        back_populates="violation_report",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_violations_platform_detected', 'detected_platform', 'detected_at'),
        Index('idx_violations_similarity', 'similarity_score', 'detection_confidence'),
        Index('idx_violations_status_action', 'status', 'action_taken'),
        Index('idx_violations_url_hash', 'infringing_url'),
        CheckConstraint('similarity_score >= 0 AND similarity_score <= 1', name='valid_similarity_score'),
        CheckConstraint('detection_confidence >= 0 AND detection_confidence <= 1', name='valid_detection_confidence'),
    )


class TakedownRequest(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """DMCA and takedown request management"""
    
    __tablename__ = 'takedown_requests'
    
    violation_report_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('violation_reports.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Request Information
    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # dmca, copyright_claim, terms_violation, manual_request
    
    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    request_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # api, web_form, email, legal_notice
    
    # Request Details
    subject_line: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    request_body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    legal_grounds: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Sender Information
    sender_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    sender_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False
    )
    
    sender_organization: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Submission Details
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    platform_reference_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )  # Platform's reference ID for the request
    
    # Response Tracking
    response_received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    response_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    response_action: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # content_removed, claim_approved, claim_rejected, under_review
    
    # Outcome
    is_successful: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    resolution_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Follow-up Actions
    requires_followup: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    followup_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Attachments and Evidence
    attachments: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )  # URLs to evidence files
    
    # Relationships
    violation_report: Mapped["ViolationReport"] = relationship(
        "ViolationReport",
        back_populates="takedown_requests"
    )
    
    legal_actions: Mapped[List["LegalAction"]] = relationship(
        "LegalAction",
        back_populates="takedown_request",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_takedowns_platform_submitted', 'platform', 'submitted_at'),
        Index('idx_takedowns_status_resolution', 'status', 'resolution_date'),
        Index('idx_takedowns_success', 'is_successful'),
        Index('idx_takedowns_followup', 'requires_followup', 'followup_date'),
    )


class LegalAction(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, StatusMixin):
    """Legal action tracking for serious copyright violations"""
    
    __tablename__ = 'legal_actions'
    
    takedown_request_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('takedown_requests.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Legal Action Details
    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # cease_desist, legal_notice, lawsuit, arbitration
    
    jurisdiction: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    legal_basis: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Parties Involved
    plaintiff: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    defendant: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    legal_counsel: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Case Information
    case_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    court_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    # Dates and Timeline
    action_filed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    deadline_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Financial Information
    damages_claimed: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    legal_costs: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    settlement_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    # Documents and Evidence
    legal_documents: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )  # URLs to legal documents
    
    evidence_files: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(500)),
        nullable=True
    )
    
    # Outcome
    resolution_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # settlement, judgment, dismissed, withdrawn
    
    resolution_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Relationships
    takedown_request: Mapped[Optional["TakedownRequest"]] = relationship(
        "TakedownRequest",
        back_populates="legal_actions"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_legal_actions_type_status', 'action_type', 'status'),
        Index('idx_legal_actions_filed_resolved', 'action_filed_at', 'resolved_at'),
        Index('idx_legal_actions_case_number', 'case_number'),
        Index('idx_legal_actions_deadline', 'deadline_date'),
    )
