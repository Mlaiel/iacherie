"""
Database Schema Definitions
Enterprise database schema for IA Influencer Agent platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, 
    BigInteger, JSON, LargeBinary, ForeignKey, Index, 
    UniqueConstraint, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()


# Enums for database fields
class ContentType(Enum):
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"


class ProtectionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROTECTED = "protected"
    FAILED = "failed"
    VIOLATION_DETECTED = "violation_detected"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RevenueStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    PAID = "paid"


# Core platform tables
class User(Base):
    """User accounts and profiles"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_image_url = Column(String(500))
    bio = Column(Text)
    website_url = Column(String(500))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Subscription and billing
    subscription_tier = Column(String(50), default='free')
    subscription_expires_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Relationships
    content_fingerprints = relationship("ContentFingerprint", back_populates="user")
    protection_alerts = relationship("ProtectionAlert", back_populates="user")
    revenue_records = relationship("RevenueRecord", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_username', 'username'),
        Index('idx_users_uuid', 'uuid'),
        Index('idx_users_subscription', 'subscription_tier'),
    )


class ContentFingerprint(Base):
    """Content fingerprinting and protection records"""
    __tablename__ = 'content_fingerprints'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Content metadata
    content_type = Column(SQLEnum(ContentType), nullable=False)
    original_filename = Column(String(500))
    file_size_bytes = Column(BigInteger)
    file_hash = Column(String(128))  # SHA-256 hash
    mime_type = Column(String(100))
    
    # Fingerprinting data
    fingerprint_hash = Column(String(256), nullable=False)  # Main fingerprint
    vector_embedding = Column(BYTEA)  # Binary vector for similarity search
    audio_fingerprint = Column(Text)  # Audio-specific fingerprint (Chromaprint)
    video_fingerprint = Column(Text)  # Video-specific fingerprint
    image_fingerprint = Column(Text)  # Image-specific fingerprint (pHash)
    text_fingerprint = Column(Text)   # Text-specific fingerprint
    
    # Content metadata from AI analysis
    content_metadata = Column(JSONB)  # Flexible metadata storage
    ai_tags = Column(JSONB)           # AI-generated tags
    description = Column(Text)        # User or AI description
    
    # Protection settings
    protection_enabled = Column(Boolean, default=True)
    monitoring_enabled = Column(Boolean, default=True)
    takedown_automation = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(SQLEnum(ProtectionStatus), default=ProtectionStatus.PENDING)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Usage and licensing
    license_type = Column(String(100))
    usage_rights = Column(JSONB)
    commercial_use_allowed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content_fingerprints")
    protection_alerts = relationship("ProtectionAlert", back_populates="content_fingerprint")
    revenue_records = relationship("RevenueRecord", back_populates="content_fingerprint")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_content_fingerprints_user_id', 'user_id'),
        Index('idx_content_fingerprints_content_type', 'content_type'),
        Index('idx_content_fingerprints_status', 'status'),
        Index('idx_content_fingerprints_fingerprint_hash', 'fingerprint_hash'),
        Index('idx_content_fingerprints_created_at', 'created_at'),
        UniqueConstraint('user_id', 'file_hash', name='uq_user_file_hash'),
    )


class ProtectionAlert(Base):
    """Content protection violation alerts"""
    __tablename__ = 'protection_alerts'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_fingerprint_id = Column(Integer, ForeignKey('content_fingerprints.id'), nullable=False)
    
    # Detection details
    detected_url = Column(String(2000), nullable=False)
    platform = Column(String(100))  # YouTube, Instagram, TikTok, etc.
    similarity_score = Column(Float)  # 0.0 to 1.0
    confidence_level = Column(Float)  # AI confidence in detection
    
    # Alert metadata
    alert_type = Column(String(50))  # unauthorized_use, copyright_infringement, etc.
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
    description = Column(Text)
    
    # Evidence collection
    screenshot_url = Column(String(1000))
    screenshot_hash = Column(String(128))
    evidence_metadata = Column(JSONB)
    crawl_timestamp = Column(DateTime)
    
    # Status and actions
    status = Column(String(50), default='pending')  # pending, investigating, resolved, false_positive
    reviewed_by_user = Column(Boolean, default=False)
    takedown_requested = Column(Boolean, default=False)
    takedown_successful = Column(Boolean)
    takedown_reference = Column(String(200))
    
    # Response tracking
    platform_response = Column(Text)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="protection_alerts")
    content_fingerprint = relationship("ContentFingerprint", back_populates="protection_alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_protection_alerts_user_id', 'user_id'),
        Index('idx_protection_alerts_content_id', 'content_fingerprint_id'),
        Index('idx_protection_alerts_platform', 'platform'),
        Index('idx_protection_alerts_status', 'status'),
        Index('idx_protection_alerts_severity', 'severity'),
        Index('idx_protection_alerts_created_at', 'created_at'),
        Index('idx_protection_alerts_detected_url', 'detected_url'),
    )


class CrawlerJob(Base):
    """Web crawler job tracking"""
    __tablename__ = 'crawler_jobs'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Job configuration
    job_type = Column(String(50))  # scheduled, on_demand, targeted
    target_platforms = Column(JSONB)  # List of platforms to crawl
    search_keywords = Column(JSONB)   # Keywords to search for
    crawl_depth = Column(Integer, default=1)
    
    # Execution details
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    execution_time_seconds = Column(Float)
    
    # Results
    pages_crawled = Column(Integer, default=0)
    matches_found = Column(Integer, default=0)
    alerts_generated = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Configuration and logs
    crawler_config = Column(JSONB)
    execution_logs = Column(Text)
    error_details = Column(Text)
    
    # Scheduling
    is_recurring = Column(Boolean, default=False)
    cron_schedule = Column(String(100))
    next_run_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_crawler_jobs_user_id', 'user_id'),
        Index('idx_crawler_jobs_status', 'status'),
        Index('idx_crawler_jobs_next_run', 'next_run_at'),
        Index('idx_crawler_jobs_created_at', 'created_at'),
    )


class RevenueRecord(Base):
    """Content monetization and revenue tracking"""
    __tablename__ = 'revenue_records'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_fingerprint_id = Column(Integer, ForeignKey('content_fingerprints.id'))
    
    # Revenue source
    platform = Column(String(100), nullable=False)  # YouTube, Instagram, Spotify, etc.
    revenue_source = Column(String(100))  # ads, streaming, licensing, etc.
    external_content_id = Column(String(200))  # Platform-specific content ID
    
    # Financial data
    revenue_amount = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    exchange_rate = Column(Float)  # Rate to EUR if different currency
    revenue_amount_eur = Column(Float)  # Normalized to EUR
    
    # Period and attribution
    revenue_period_start = Column(DateTime, nullable=False)
    revenue_period_end = Column(DateTime, nullable=False)
    attribution_percentage = Column(Float, default=100.0)  # % attributed to this content
    
    # Platform data
    platform_data = Column(JSONB)  # Raw data from platform APIs
    views_count = Column(BigInteger)
    engagement_metrics = Column(JSONB)
    
    # Status and validation
    status = Column(SQLEnum(RevenueStatus), default=RevenueStatus.PENDING)
    verified_at = Column(DateTime)
    verified_by = Column(String(100))
    
    # Payment tracking
    payment_processed = Column(Boolean, default=False)
    payment_amount = Column(Float)
    payment_fees = Column(Float)
    payment_reference = Column(String(200))
    payment_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="revenue_records")
    content_fingerprint = relationship("ContentFingerprint", back_populates="revenue_records")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_revenue_records_user_id', 'user_id'),
        Index('idx_revenue_records_content_id', 'content_fingerprint_id'),
        Index('idx_revenue_records_platform', 'platform'),
        Index('idx_revenue_records_status', 'status'),
        Index('idx_revenue_records_period', 'revenue_period_start', 'revenue_period_end'),
        Index('idx_revenue_records_created_at', 'created_at'),
        CheckConstraint('revenue_amount >= 0', name='chk_revenue_amount_positive'),
        CheckConstraint('attribution_percentage >= 0 AND attribution_percentage <= 100', 
                       name='chk_attribution_percentage_valid'),
    )


class PlatformIntegration(Base):
    """Platform API integrations and credentials"""
    __tablename__ = 'platform_integrations'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Platform details
    platform_name = Column(String(100), nullable=False)  # youtube, instagram, spotify, etc.
    platform_user_id = Column(String(200))  # User ID on the platform
    platform_username = Column(String(200))
    
    # Integration status
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    connection_status = Column(String(50))  # connected, expired, error, etc.
    
    # API credentials (encrypted)
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text)
    api_key_encrypted = Column(Text)
    credentials_metadata = Column(JSONB)  # Additional platform-specific data
    
    # Token management
    token_expires_at = Column(DateTime)
    last_refresh_at = Column(DateTime)
    refresh_attempts = Column(Integer, default=0)
    
    # Permissions and scopes
    granted_scopes = Column(JSONB)  # Permissions granted by user
    required_scopes = Column(JSONB)  # Permissions needed for full functionality
    
    # Usage tracking
    last_sync_at = Column(DateTime)
    sync_frequency_hours = Column(Integer, default=24)
    api_calls_today = Column(Integer, default=0)
    api_quota_limit = Column(Integer)
    
    # Error tracking
    last_error_at = Column(DateTime)
    last_error_message = Column(Text)
    consecutive_errors = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_platform_integrations_user_id', 'user_id'),
        Index('idx_platform_integrations_platform', 'platform_name'),
        Index('idx_platform_integrations_status', 'connection_status'),
        UniqueConstraint('user_id', 'platform_name', name='uq_user_platform'),
    )


class AuditLog(Base):
    """System audit and activity logging"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Actor information
    user_id = Column(Integer, ForeignKey('users.id'))
    actor_type = Column(String(50))  # user, system, api, crawler
    actor_identifier = Column(String(200))  # IP address, API key ID, etc.
    
    # Action details
    action = Column(String(100), nullable=False)  # create, update, delete, view, etc.
    resource_type = Column(String(100))  # user, content, alert, etc.
    resource_id = Column(String(100))
    
    # Context and metadata
    description = Column(Text)
    metadata = Column(JSONB)  # Additional context data
    request_data = Column(JSONB)  # Request parameters
    response_data = Column(JSONB)  # Response data (if applicable)
    
    # Technical details
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    session_id = Column(String(100))
    api_version = Column(String(20))
    
    # Status and results
    status = Column(String(50))  # success, failure, partial
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    
    # Security context
    security_level = Column(String(20))  # public, protected, sensitive, critical
    requires_review = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_created_at', 'created_at'),
        Index('idx_audit_logs_ip_address', 'ip_address'),
        Index('idx_audit_logs_status', 'status'),
    )


class SystemConfiguration(Base):
    """System-wide configuration settings"""
    __tablename__ = 'system_configuration'
    
    id = Column(Integer, primary_key=True)
    
    # Configuration key and value
    config_key = Column(String(200), unique=True, nullable=False)
    config_value = Column(Text)
    config_type = Column(String(50))  # string, integer, float, boolean, json
    
    # Metadata
    description = Column(Text)
    category = Column(String(100))  # security, performance, features, etc.
    is_sensitive = Column(Boolean, default=False)  # Contains sensitive data
    is_system_managed = Column(Boolean, default=False)  # Managed by system
    
    # Validation
    validation_rules = Column(JSONB)  # Validation constraints
    default_value = Column(Text)
    
    # Change tracking
    last_modified_by = Column(String(100))
    last_modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_system_config_key', 'config_key'),
        Index('idx_system_config_category', 'category'),
    )


# Migration tracking table (handled by MigrationRunner)
class SchemaMigration(Base):
    """Database schema migration tracking"""
    __tablename__ = 'schema_migrations'
    
    id = Column(Integer, primary_key=True)
    version = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    checksum = Column(String(64), nullable=False)
    status = Column(String(20), default='pending')
    executed_at = Column(DateTime, default=datetime.utcnow)
    execution_time = Column(Float, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_schema_migrations_version', 'version'),
        Index('idx_schema_migrations_status', 'status'),
    )


# Function to create all tables
def create_all_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(engine)


class ContentLicensing(Base):
    """Content licensing and rights management"""
    __tablename__ = 'content_licensing'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    content_fingerprint_id = Column(Integer, ForeignKey('content_fingerprints.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # License details
    license_type = Column(String(100), nullable=False)  # commercial, creative_commons, custom
    license_scope = Column(String(100))  # global, regional, platform_specific
    usage_rights = Column(JSONB)  # Detailed usage permissions
    
    # Terms and conditions
    commercial_use_allowed = Column(Boolean, default=False)
    modification_allowed = Column(Boolean, default=False)
    redistribution_allowed = Column(Boolean, default=False)
    attribution_required = Column(Boolean, default=True)
    
    # Pricing and royalties
    license_fee = Column(Float)
    currency = Column(String(3), default='EUR')
    royalty_percentage = Column(Float)
    minimum_royalty = Column(Float)
    
    # Geographical restrictions
    allowed_territories = Column(JSONB)  # List of allowed countries/regions
    restricted_territories = Column(JSONB)  # List of restricted areas
    
    # Temporal restrictions
    license_start_date = Column(DateTime)
    license_end_date = Column(DateTime)
    renewal_terms = Column(Text)
    
    # Platform restrictions
    allowed_platforms = Column(JSONB)  # YouTube, Instagram, TikTok, etc.
    restricted_platforms = Column(JSONB)
    
    # Contract details
    contract_reference = Column(String(200))
    legal_text = Column(Text)
    license_agreement_url = Column(String(1000))
    
    # Status tracking
    status = Column(String(50), default='active')  # active, expired, revoked, pending
    approval_required = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    
    # Revenue tracking
    total_revenue_generated = Column(Float, default=0)
    total_uses_tracked = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_licensing_user_id', 'user_id'),
        Index('idx_content_licensing_content_id', 'content_fingerprint_id'),
        Index('idx_content_licensing_status', 'status'),
        Index('idx_content_licensing_license_type', 'license_type'),
        Index('idx_content_licensing_dates', 'license_start_date', 'license_end_date'),
    )


class CollaborationRequest(Base):
    """Collaboration requests between creators"""
    __tablename__ = 'collaboration_requests'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Parties involved
    requester_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    target_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Collaboration details
    collaboration_type = Column(String(100))  # remix, feature, duet, collaboration
    content_type = Column(SQLEnum(ContentType))
    project_title = Column(String(255))
    project_description = Column(Text)
    
    # Original content reference
    original_content_id = Column(Integer, ForeignKey('content_fingerprints.id'))
    
    # Terms and conditions
    revenue_split_percentage = Column(Float)  # Percentage for requester
    credit_requirements = Column(JSONB)
    usage_restrictions = Column(JSONB)
    deadline = Column(DateTime)
    
    # Status and workflow
    status = Column(String(50), default='pending')  # pending, accepted, rejected, completed, cancelled
    message = Column(Text)  # Initial message from requester
    response_message = Column(Text)  # Response from target user
    
    # AI matching scores
    compatibility_score = Column(Float)  # AI-calculated compatibility
    genre_match_score = Column(Float)
    audience_overlap_score = Column(Float)
    style_similarity_score = Column(Float)
    
    # Contract and legal
    contract_generated = Column(Boolean, default=False)
    contract_url = Column(String(1000))
    legal_review_required = Column(Boolean, default=False)
    
    # Timeline tracking
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Result tracking
    collaboration_successful = Column(Boolean)
    final_content_id = Column(Integer, ForeignKey('content_fingerprints.id'))
    rating_by_requester = Column(Integer)  # 1-5 stars
    rating_by_target = Column(Integer)  # 1-5 stars
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_user_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    original_content = relationship("ContentFingerprint", foreign_keys=[original_content_id])
    final_content = relationship("ContentFingerprint", foreign_keys=[final_content_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_collaboration_requests_requester', 'requester_user_id'),
        Index('idx_collaboration_requests_target', 'target_user_id'),
        Index('idx_collaboration_requests_status', 'status'),
        Index('idx_collaboration_requests_type', 'collaboration_type'),
        Index('idx_collaboration_requests_created_at', 'created_at'),
        UniqueConstraint('requester_user_id', 'target_user_id', 'original_content_id', 
                        name='uq_collaboration_request'),
    )


class AIRecommendation(Base):
    """AI-generated recommendations for users"""
    __tablename__ = 'ai_recommendations'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String(100), nullable=False)  # collaboration, content_optimization, trending_topic, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # AI analysis
    confidence_score = Column(Float)  # 0.0 to 1.0
    relevance_score = Column(Float)  # 0.0 to 1.0
    potential_impact_score = Column(Float)  # Estimated impact
    
    # Recommendation data
    recommendation_data = Column(JSONB)  # Structured recommendation details
    target_content_id = Column(Integer, ForeignKey('content_fingerprints.id'))
    target_user_id = Column(Integer, ForeignKey('users.id'))
    
    # Categorization
    category = Column(String(100))  # marketing, collaboration, content_creation, monetization
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    tags = Column(JSONB)
    
    # User interaction
    viewed = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    acted_upon = Column(Boolean, default=False)
    dismissed = Column(Boolean, default=False)
    user_rating = Column(Integer)  # 1-5 stars feedback
    
    # Timing and expiration
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    optimal_timing = Column(DateTime)  # When to show this recommendation
    
    # A/B testing
    experiment_id = Column(String(100))
    variant = Column(String(50))
    
    # Performance tracking
    impression_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    viewed_at = Column(DateTime)
    acted_upon_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    target_content = relationship("ContentFingerprint")
    target_user = relationship("User", foreign_keys=[target_user_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_recommendations_user_id', 'user_id'),
        Index('idx_ai_recommendations_type', 'recommendation_type'),
        Index('idx_ai_recommendations_category', 'category'),
        Index('idx_ai_recommendations_priority', 'priority'),
        Index('idx_ai_recommendations_valid', 'valid_from', 'valid_until'),
        Index('idx_ai_recommendations_created_at', 'created_at'),
    )


class VectorSimilarity(Base):
    """Vector similarity search results for content matching"""
    __tablename__ = 'vector_similarities'
    
    id = Column(Integer, primary_key=True)
    
    # Source and target content
    source_content_id = Column(Integer, ForeignKey('content_fingerprints.id'), nullable=False)
    target_content_id = Column(Integer, ForeignKey('content_fingerprints.id'), nullable=False)
    
    # Similarity scores
    overall_similarity = Column(Float, nullable=False)  # 0.0 to 1.0
    audio_similarity = Column(Float)
    visual_similarity = Column(Float)
    text_similarity = Column(Float)
    metadata_similarity = Column(Float)
    
    # Matching details
    matching_algorithm = Column(String(100))  # FAISS, cosine, euclidean, etc.
    vector_dimensions = Column(Integer)
    distance_metric = Column(String(50))
    
    # Analysis context
    comparison_type = Column(String(100))  # copyright_check, collaboration_match, duplicate_detection
    analysis_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time_ms = Column(Float)
    
    # Confidence and quality
    confidence_level = Column(Float)  # How confident we are in this similarity
    quality_score = Column(Float)    # Quality of the match
    false_positive_probability = Column(Float)
    
    # Additional metadata
    matching_segments = Column(JSONB)  # Which parts of content match
    metadata = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    source_content = relationship("ContentFingerprint", foreign_keys=[source_content_id])
    target_content = relationship("ContentFingerprint", foreign_keys=[target_content_id])
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_vector_similarities_source', 'source_content_id'),
        Index('idx_vector_similarities_target', 'target_content_id'),
        Index('idx_vector_similarities_overall', 'overall_similarity'),
        Index('idx_vector_similarities_timestamp', 'analysis_timestamp'),
        Index('idx_vector_similarities_type', 'comparison_type'),
        UniqueConstraint('source_content_id', 'target_content_id', 'comparison_type', 
                        name='uq_vector_similarity'),
    )


class ContentAnalytics(Base):
    """Advanced analytics and insights for content performance"""
    __tablename__ = 'content_analytics'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    content_fingerprint_id = Column(Integer, ForeignKey('content_fingerprints.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Time period for analytics
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20))  # daily, weekly, monthly, quarterly, yearly
    
    # Engagement metrics
    total_views = Column(BigInteger, default=0)
    unique_views = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    shares_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    saves_count = Column(BigInteger, default=0)
    
    # Platform-specific metrics
    platform_metrics = Column(JSONB)  # Different metrics per platform
    
    # Audience analytics
    audience_demographics = Column(JSONB)  # Age, gender, location breakdown
    audience_interests = Column(JSONB)
    audience_retention = Column(JSONB)  # Where people drop off
    
    # Performance scores
    engagement_rate = Column(Float)
    viral_score = Column(Float)  # AI-calculated virality potential
    quality_score = Column(Float)  # Content quality assessment
    trend_score = Column(Float)   # How trending this content is
    
    # Revenue analytics
    revenue_generated = Column(Float, default=0)
    revenue_per_view = Column(Float, default=0)
    monetization_rate = Column(Float, default=0)
    
    # Geographic distribution
    geographic_distribution = Column(JSONB)  # Views by country/region
    top_countries = Column(JSONB)
    
    # Temporal patterns
    peak_viewing_hours = Column(JSONB)
    viewing_patterns = Column(JSONB)  # When content performs best
    
    # Comparative analytics
    relative_performance = Column(Float)  # Compared to user's other content
    category_performance = Column(Float)  # Compared to similar content
    industry_benchmark = Column(Float)    # Compared to industry average
    
    # AI insights
    ai_insights = Column(JSONB)  # AI-generated insights and recommendations
    optimization_suggestions = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_analytics_content_id', 'content_fingerprint_id'),
        Index('idx_content_analytics_user_id', 'user_id'),
        Index('idx_content_analytics_period', 'period_start', 'period_end'),
        Index('idx_content_analytics_period_type', 'period_type'),
        Index('idx_content_analytics_created_at', 'created_at'),
        UniqueConstraint('content_fingerprint_id', 'period_start', 'period_end', 'period_type',
                        name='uq_content_analytics_period'),
    )


class TakedownRequest(Base):
    """DMCA and copyright takedown requests"""
    __tablename__ = 'takedown_requests'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_fingerprint_id = Column(Integer, ForeignKey('content_fingerprints.id'), nullable=False)
    protection_alert_id = Column(Integer, ForeignKey('protection_alerts.id'))
    
    # Request details
    request_type = Column(String(50), default='dmca')  # dmca, copyright, trademark
    platform = Column(String(100), nullable=False)  # YouTube, Instagram, etc.
    infringing_url = Column(String(2000), nullable=False)
    
    # Legal information
    copyright_holder = Column(String(255))
    legal_representative = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Claim details
    description_of_work = Column(Text)
    description_of_infringement = Column(Text)
    good_faith_statement = Column(Text)
    perjury_statement = Column(Text)
    
    # Evidence
    evidence_urls = Column(JSONB)  # Screenshots, original content links
    evidence_description = Column(Text)
    copyright_registration = Column(String(200))
    
    # Request status
    status = Column(String(50), default='pending')  # pending, submitted, acknowledged, resolved, rejected
    submission_method = Column(String(100))  # api, web_form, email
    platform_reference_id = Column(String(200))
    
    # Automation
    auto_generated = Column(Boolean, default=False)
    template_used = Column(String(100))
    ai_confidence = Column(Float)  # Confidence in automated request
    
    # Timeline
    submitted_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    expected_resolution_date = Column(DateTime)
    
    # Response from platform
    platform_response = Column(Text)
    resolution_outcome = Column(String(100))  # content_removed, claim_rejected, counter_notice
    appeal_deadline = Column(DateTime)
    
    # Counter-notice handling
    counter_notice_received = Column(Boolean, default=False)
    counter_notice_details = Column(Text)
    counter_notice_response = Column(Text)
    
    # Success metrics
    successful = Column(Boolean)
    content_removed = Column(Boolean, default=False)
    revenue_recovered = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    content_fingerprint = relationship("ContentFingerprint")
    protection_alert = relationship("ProtectionAlert")
    
    # Indexes
    __table_args__ = (
        Index('idx_takedown_requests_user_id', 'user_id'),
        Index('idx_takedown_requests_content_id', 'content_fingerprint_id'),
        Index('idx_takedown_requests_platform', 'platform'),
        Index('idx_takedown_requests_status', 'status'),
        Index('idx_takedown_requests_created_at', 'created_at'),
        Index('idx_takedown_requests_url', 'infringing_url'),
    )


class DataRetentionPolicy(Base):
    """Data retention and deletion policies"""
    __tablename__ = 'data_retention_policies'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Policy details
    policy_name = Column(String(255), nullable=False)
    policy_description = Column(Text)
    data_category = Column(String(100), nullable=False)  # user_data, content, analytics, audit
    
    # Retention rules
    retention_period_days = Column(Integer, nullable=False)
    retention_trigger = Column(String(100))  # user_deletion, content_deletion, time_based
    
    # Geographical compliance
    applicable_jurisdictions = Column(JSONB)  # EU, California, etc.
    compliance_frameworks = Column(JSONB)  # GDPR, CCPA, etc.
    
    # Deletion rules
    soft_delete_enabled = Column(Boolean, default=True)
    soft_delete_period_days = Column(Integer, default=30)
    hard_delete_automated = Column(Boolean, default=True)
    
    # Exceptions
    legal_hold_exceptions = Column(JSONB)
    business_critical_exceptions = Column(JSONB)
    
    # Status
    active = Column(Boolean, default=True)
    version = Column(String(20), default='1.0')
    
    # Approval and audit
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    last_reviewed_at = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_data_retention_category', 'data_category'),
        Index('idx_data_retention_active', 'active'),
        Index('idx_data_retention_compliance', 'compliance_frameworks'),
        UniqueConstraint('policy_name', 'version', name='uq_retention_policy_version'),
    )


class ConsentRecord(Base):
    """User consent records for GDPR compliance"""
    __tablename__ = 'consent_records'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Consent details
    consent_type = Column(String(100), nullable=False)  # data_processing, marketing, analytics, cookies
    consent_purpose = Column(String(255), nullable=False)
    consent_given = Column(Boolean, nullable=False)
    
    # Legal basis
    legal_basis = Column(String(100))  # consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests
    lawful_basis_description = Column(Text)
    
    # Consent mechanism
    consent_method = Column(String(100))  # website_form, email, phone, written
    consent_medium = Column(String(100))  # web, mobile_app, email, phone
    consent_location = Column(String(255))  # URL or location where consent was given
    
    # Consent evidence
    consent_evidence = Column(JSONB)  # IP address, timestamp, form data, etc.
    consent_text_shown = Column(Text)  # Exact text shown to user
    privacy_policy_version = Column(String(50))
    terms_version = Column(String(50))
    
    # Withdrawal
    withdrawn = Column(Boolean, default=False)
    withdrawal_date = Column(DateTime)
    withdrawal_method = Column(String(100))
    withdrawal_reason = Column(Text)
    
    # Consent metadata
    granular_consents = Column(JSONB)  # Detailed breakdown of specific consents
    consent_scope = Column(JSONB)      # What data/processing this covers
    
    # Expiration
    expires_at = Column(DateTime)
    renewal_required = Column(Boolean, default=False)
    auto_renewal = Column(Boolean, default=False)
    
    # Compliance tracking
    gdpr_compliant = Column(Boolean, default=True)
    ccpa_compliant = Column(Boolean, default=True)
    compliance_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_consent_records_user_id', 'user_id'),
        Index('idx_consent_records_type', 'consent_type'),
        Index('idx_consent_records_given', 'consent_given'),
        Index('idx_consent_records_withdrawn', 'withdrawn'),
        Index('idx_consent_records_expires', 'expires_at'),
        Index('idx_consent_records_created_at', 'created_at'),
    )


# Function to create all tables
def create_all_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(engine)


# Function to drop all tables (use with caution!)
def drop_all_tables(engine):
    """Drop all database tables - USE WITH EXTREME CAUTION!"""
    Base.metadata.drop_all(engine)
