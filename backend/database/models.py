"""🗃️ Backend Database Models - Consolidated Enterprise Data Models
import logging

====================================================================
Module: backend/database/models.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Database Models - Ultra Enterprise Production-Ready
Responsibility: Complete data models for multi-format content protection and AI monetization
========================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated models module provides comprehensive data models for:
- User management and creator profiles
- Multi-modal content fingerprinting (audio, video, image, text)
- AI-powered protection and monitoring infrastructure
- Creator monetization and revenue tracking systems
- Collaborative platform integration and synchronization
- Real-time analytics and performance optimization

CONSOLIDATED BUSINESS LOGIC MODELS:
- User Management: User profiles, permissions, teams, workspaces
- Content Protection: Fingerprints, alerts, policies, monitoring
- Monetization: Revenue tracking, payment processing, billing
- AI Analytics: Analysis results, model performance, optimization
- Platform Integration: Social media, streaming, distribution
- Collaboration: Team management, revenue sharing, matching
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid

# Create declarative base
Base = declarative_base()


# ================================
# ENUMERATIONS
# ================================

class ContentType(Enum):
    """Content type enumeration."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMEDIA = "multimedia"


class CreatorType(Enum):
    """Creator type enumeration."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    WRITER = "writer"
    OTHER = "other"


class SubscriptionTier(Enum):
    """Subscription tier enumeration."""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class AlertType(Enum):
    """Protection alert type enumeration."""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    CONTENT_THEFT = "content_theft"
    DUPLICATE_DETECTION = "duplicate_detection"
    REVENUE_LOSS = "revenue_loss"
    PLATFORM_VIOLATION = "platform_violation"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status enumeration."""
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"


class ProcessingStatus(Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Platform(Enum):
    """Social media and content platforms."""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    PINTEREST = "pinterest"


class IntegrationStatus(Enum):
    """Platform integration status."""
    PENDING = "pending"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SUSPENDED = "suspended"


class RevenueSource(Enum):
    """Revenue source enumeration."""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    LIVE_EVENTS = "live_events"
    COLLABORATION = "collaboration"
    SUBSCRIPTION = "subscription"


class Currency(Enum):
    """Currency codes."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"


class PaymentStatus(Enum):
    """Payment transaction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


# ================================
# CORE USER MODELS
# ================================

class User(Base):
    """
    🧑‍💼 Core User Model
    
    Central user entity managing creator profiles, authentication, and subscription management.
    Supports multi-tenant architecture with comprehensive metadata tracking.
    """
    __tablename__ = "users"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    creator_type = Column(SQLEnum(CreatorType), nullable=False)
    bio = Column(Text)
    profile_image_url = Column(String(500))
    
    # System fields
    tenant_id = Column(String(16), nullable=False, index=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True))
    
    # Relationships
    content_fingerprints = relationship("ContentFingerprint", back_populates="user", cascade="all, delete-orphan")
    protection_alerts = relationship("ProtectionAlert", back_populates="user", cascade="all, delete-orphan")
    revenue_records = relationship("RevenueTracking", back_populates="user", cascade="all, delete-orphan")
    platform_integrations = relationship("PlatformIntegration", back_populates="user", cascade="all, delete-orphan")
    user_content = relationship("UserContent", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_username', 'username'),
        Index('idx_users_tenant_creator', 'tenant_id', 'creator_type'),
        Index('idx_users_subscription', 'subscription_tier'),
        Index('idx_users_active_verified', 'is_active', 'is_verified'),
    )
    
    def __repr__(self) -> None:
        return f"<User(id={self.id}, email={self.email}, creator_type={self.creator_type.value})>"


# ================================
# CONTENT PROTECTION MODELS
# ================================

class ContentFingerprint(Base):
    """
    🔍 Content Fingerprint Model
    
    Advanced content fingerprinting for multi-modal content protection.
    Supports audio, video, image, and text fingerprinting with AI-powered analysis.
    """
    __tablename__ = "content_fingerprints"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    
    # Content identification
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    content_title = Column(String(255))
    content_description = Column(Text)
    
    # Fingerprint data
    fingerprint_data = Column(JSON, nullable=False)
    algorithm_version = Column(String(20), nullable=False)
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    quality_score = Column(Float, default=0.0)
    confidence_level = Column(Float, default=0.0)
    
    # File information
    file_size = Column(BigInteger)
    file_format = Column(String(20))
    duration = Column(Float)  # For audio/video content
    resolution = Column(String(20))  # For image/video content
    
    # Metadata
    tags = Column(ARRAY(String), default=[])
    category = Column(String(50))
    language = Column(String(10))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="content_fingerprints")
    protection_alerts = relationship("ProtectionAlert", back_populates="content_fingerprint", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_fingerprints_user_type', 'user_id', 'content_type'),
        Index('idx_fingerprints_hash', 'content_hash'),
        Index('idx_fingerprints_status', 'processing_status'),
        Index('idx_fingerprints_quality', 'quality_score'),
        Index('idx_fingerprints_created', 'created_at'),
    )
    
    def __repr__(self) -> None:
        return f"<ContentFingerprint(id={self.id}, type={self.content_type.value}, status={self.processing_status.value})>"


class ProtectionAlert(Base):
    """
    🚨 Protection Alert Model
    
    Advanced alert system for content protection violations and unauthorized usage.
    Integrates with AI monitoring and automated response systems.
    """
    __tablename__ = "protection_alerts"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    fingerprint_id = Column(String(32), ForeignKey('content_fingerprints.id'), nullable=False, index=True)
    
    # Alert information
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Detection information
    detection_method = Column(String(30), nullable=False)
    detection_confidence = Column(Float, default=0.0)
    evidence_data = Column(JSON)
    source_url = Column(String(500))
    platform_source = Column(String(50))
    
    # Response information
    automated_actions = Column(JSON)
    response_status = Column(String(20), default='pending')
    resolution_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="protection_alerts")
    content_fingerprint = relationship("ContentFingerprint", back_populates="protection_alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alerts_user_severity', 'user_id', 'severity'),
        Index('idx_alerts_status', 'status'),
        Index('idx_alerts_type', 'alert_type'),
        Index('idx_alerts_platform', 'platform_source'),
        Index('idx_alerts_created', 'created_at'),
    )
    
    def __repr__(self) -> None:
        return f"<ProtectionAlert(id={self.id}, type={self.alert_type.value}, severity={self.severity.value})>"


# ================================
# MONETIZATION MODELS
# ================================

class RevenueTracking(Base):
    """
    💰 Revenue Tracking Model
    
    Comprehensive revenue tracking and analytics for content creators.
    Supports multiple revenue streams and detailed financial reporting.
    """
    __tablename__ = "revenue_tracking"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(String(32), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    
    # Revenue information
    revenue_amount = Column(Numeric(15, 2), nullable=False)
    revenue_source = Column(SQLEnum(RevenueSource), nullable=False)
    currency = Column(SQLEnum(Currency), default=Currency.USD)
    exchange_rate = Column(Float, default=1.0)
    
    # Transaction details
    transaction_id = Column(String(100), unique=True, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    platform = Column(String(50))
    platform_fee = Column(Numeric(15, 2), default=0)
    net_revenue = Column(Numeric(15, 2))
    
    # Analytics
    audience_metrics = Column(JSON)
    performance_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="revenue_records")
    content = relationship("ContentFingerprint", backref="revenue_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_revenue_user_date', 'user_id', 'transaction_date'),
        Index('idx_revenue_source', 'revenue_source'),
        Index('idx_revenue_platform', 'platform'),
        Index('idx_revenue_amount', 'revenue_amount'),
        Index('idx_revenue_transaction', 'transaction_id'),
    )
    
    def __repr__(self) -> None:
        return f"<RevenueTracking(id={self.id}, amount={self.revenue_amount}, source={self.revenue_source.value})>"


class PaymentTransaction(Base):
    """
    💳 Payment Transaction Model
    
    Secure payment processing and transaction management for the platform.
    Supports multiple payment methods and currencies.
    """
    __tablename__ = "payment_transactions"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    
    # Transaction details
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment gateway information
    gateway_provider = Column(String(50))
    gateway_transaction_id = Column(String(100))
    gateway_response = Column(JSON)
    
    # Billing information
    billing_address = Column(JSON)
    invoice_number = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", backref="payment_transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_payments_user_status', 'user_id', 'status'),
        Index('idx_payments_transaction', 'transaction_id'),
        Index('idx_payments_gateway', 'gateway_provider'),
        Index('idx_payments_amount', 'amount'),
        Index('idx_payments_created', 'created_at'),
    )
    
    def __repr__(self) -> None:
        return f"<PaymentTransaction(id={self.id}, amount={self.amount}, status={self.status.value})>"


# ================================
# PLATFORM INTEGRATION MODELS
# ================================

class PlatformIntegration(Base):
    """
    🔗 Platform Integration Model
    
    Social media and content platform integration management.
    Handles authentication, synchronization, and cross-platform operations.
    """
    __tablename__ = "platform_integrations"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    
    # Platform information
    platform = Column(SQLEnum(Platform), nullable=False)
    platform_user_id = Column(String(100), nullable=False)
    platform_username = Column(String(100))
    
    # Integration details
    integration_status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING)
    integration_type = Column(String(50), default='oauth')
    
    # Authentication
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))
    
    # Synchronization
    sync_settings = Column(JSON, default={})
    last_sync_at = Column(DateTime(timezone=True))
    sync_status = Column(String(20), default='pending')
    
    # Analytics
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    performance_metrics = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="platform_integrations")
    
    # Indexes
    __table_args__ = (
        Index('idx_integrations_user_platform', 'user_id', 'platform'),
        Index('idx_integrations_status', 'integration_status'),
        Index('idx_integrations_platform_user', 'platform', 'platform_user_id'),
        Index('idx_integrations_sync', 'last_sync_at'),
    )
    
    def __repr__(self) -> None:
        return f"<PlatformIntegration(id={self.id}, platform={self.platform.value}, status={self.integration_status.value})>"


# ================================
# USER CONTENT MODELS
# ================================

class UserContent(Base):
    """
    📝 User Content Model
    
    User-generated content management with comprehensive metadata and lifecycle tracking.
    Supports all content types with advanced categorization and analytics.
    """
    __tablename__ = "user_content"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    
    # Content information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    file_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # Content metadata
    file_size = Column(BigInteger)
    file_format = Column(String(20))
    duration = Column(Float)  # For audio/video
    resolution = Column(String(20))  # For image/video
    
    # Categorization
    category = Column(String(50))
    tags = Column(ARRAY(String), default=[])
    genre = Column(String(50))
    mood = Column(String(50))
    language = Column(String(10))
    
    # Status and visibility
    status = Column(String(20), default='draft')
    is_public = Column(Boolean, default=False)
    is_monetized = Column(Boolean, default=False)
    
    # Analytics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="user_content")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_user_type', 'user_id', 'content_type'),
        Index('idx_content_status', 'status'),
        Index('idx_content_public', 'is_public'),
        Index('idx_content_created', 'created_at'),
        Index('idx_content_views', 'view_count'),
    )
    
    def __repr__(self) -> None:
        return f"<UserContent(id={self.id}, title={self.title}, type={self.content_type.value})>"


# ================================
# AI ANALYSIS MODELS
# ================================

class AIAnalysis(Base):
    """
    🤖 AI Analysis Model
    
    AI-powered content analysis and insights for optimization and protection.
    Supports multiple AI models and analysis types.
    """
    __tablename__ = "ai_analysis"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    content_id = Column(String(32), ForeignKey('content_fingerprints.id'), nullable=False, index=True)
    
    # Analysis information
    analysis_type = Column(String(30), nullable=False)  # sentiment, quality, trend, etc.
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20))
    
    # Results
    analysis_results = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    
    # Performance metrics
    processing_time = Column(Integer)  # milliseconds
    tokens_processed = Column(Integer)
    cost_estimate = Column(Numeric(10, 4))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    content = relationship("ContentFingerprint", backref="ai_analyses")
    
    # Indexes
    __table_args__ = (
        Index('idx_analysis_content_type', 'content_id', 'analysis_type'),
        Index('idx_analysis_model', 'model_name'),
        Index('idx_analysis_confidence', 'confidence_score'),
        Index('idx_analysis_created', 'created_at'),
    )
    
    def __repr__(self) -> None:
        return f"<AIAnalysis(id={self.id}, type={self.analysis_type}, model={self.model_name})>"


# ================================
# COLLABORATION MODELS
# ================================

class CollaborationRequest(Base):
    """
    🤝 Collaboration Request Model
    
    Advanced collaboration matching and management system for content creators.
    Supports AI-powered matching and revenue sharing agreements.
    """
    __tablename__ = "collaboration_requests"
    
    # Primary identification
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    requester_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    target_id = Column(String(32), ForeignKey('users.id'), nullable=False, index=True)
    
    # Collaboration details
    collaboration_type = Column(String(50), nullable=False)  # music, video, cross_promotion
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Status and terms
    status = Column(String(20), default='pending')  # pending, accepted, rejected, completed
    priority = Column(String(20), default='medium')
    
    # Revenue sharing
    revenue_share_percentage = Column(Float, default=50.0)
    revenue_share_type = Column(String(30), default='equal')
    
    # Requirements and preferences
    requirements = Column(JSON)
    preferences = Column(JSON)
    collaboration_scope = Column(String(100))
    
    # AI matching data
    matching_score = Column(Float, default=0.0)
    matching_factors = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], backref="sent_collaboration_requests")
    target = relationship("User", foreign_keys=[target_id], backref="received_collaboration_requests")
    
    # Indexes
    __table_args__ = (
        Index('idx_collaboration_requester', 'requester_id'),
        Index('idx_collaboration_target', 'target_id'),
        Index('idx_collaboration_status', 'status'),
        Index('idx_collaboration_type', 'collaboration_type'),
        Index('idx_collaboration_score', 'matching_score'),
    )
    
    def __repr__(self) -> None:
        return f"<CollaborationRequest(id={self.id}, type={self.collaboration_type}, status={self.status})>"


# Export all model classes and enums
__all__ = [
    # Base
    "Base",
    
    # Core Models
    "User",
    "ContentFingerprint", 
    "ProtectionAlert",
    "RevenueTracking",
    "PaymentTransaction",
    "PlatformIntegration",
    "UserContent",
    "AIAnalysis",
    "CollaborationRequest",
    
    # Enumerations
    "ContentType",
    "CreatorType",
    "SubscriptionTier",
    "AlertType",
    "AlertSeverity", 
    "AlertStatus",
    "ProcessingStatus",
    "Platform",
    "IntegrationStatus",
    "RevenueSource",
    "Currency",
    "PaymentStatus",
]