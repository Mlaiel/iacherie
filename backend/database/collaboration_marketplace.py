"""🤝 Collaboration & Marketplace Database Module - Advanced Creator Ecosystem
================================================================================
Module: backend/database/collaboration_marketplace.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Collaboration & Marketplace Database - Ultra Enterprise Production-Ready
Responsibility: Creator profiles, collaboration matching, project management, marketplace transactions, and reviews
====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated module provides comprehensive database schemas and operations for:
- Detailed creator profiles with AI-enhanced matching
- Advanced collaboration algorithms and compatibility scoring
- Project management and workflow tracking
- Secure marketplace transactions with escrow
- Comprehensive rating and review systems
- Analytics for collaboration success and ROI

BUSINESS LOGIC INTEGRATION:
Creator Registration → Profile Building → Matching Algorithm → Collaboration → Project Management → Payment & Reviews
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid
import logging

logger = logging.getLogger(__name__)

# Create independent declarative base to avoid conflicts
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# ================================
# ENUMERATIONS
# ================================

class CreatorType(Enum):
    """Creator type categories."""
    MUSICIAN = "musician"
    PRODUCER = "producer"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    SONGWRITER = "songwriter"
    AUDIO_ENGINEER = "audio_engineer"
    VIDEO_CREATOR = "video_creator"
    PHOTOGRAPHER = "photographer"
    GRAPHIC_DESIGNER = "graphic_designer"
    ANIMATOR = "animator"
    BLOGGER = "blogger"
    PODCASTER = "podcaster"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    VOICE_ACTOR = "voice_actor"
    DANCER = "dancer"
    CHOREOGRAPHER = "choreographer"


class SkillLevel(Enum):
    """Skill level classifications."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    PROFESSIONAL = "professional"


class CollaborationStatus(Enum):
    """Collaboration request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class ProjectStatus(Enum):
    """Project status types."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class MarketplaceItemType(Enum):
    """Marketplace item categories."""
    BEATS = "beats"
    SAMPLES = "samples"
    LOOPS = "loops"
    STEMS = "stems"
    VOCALS = "vocals"
    INSTRUMENTALS = "instrumentals"
    MIXING_SERVICES = "mixing_services"
    MASTERING_SERVICES = "mastering_services"
    PRODUCTION_SERVICES = "production_services"
    SONGWRITING_SERVICES = "songwriting_services"
    ARTWORK = "artwork"
    VIDEO_EDITING = "video_editing"
    PHOTOGRAPHY = "photography"
    CUSTOM_WORK = "custom_work"


class EscrowStatus(Enum):
    """Escrow payment status."""
    PENDING = "pending"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


# ================================
# CREATOR PROFILE SCHEMAS
# ================================

class CreatorProfile(Base):
    """Detailed creator profiles with AI-enhanced features."""
    __tablename__ = 'creator_profiles'
    __table_args__ = (
        Index('idx_creator_profile_user', 'user_id'),
        Index('idx_creator_profile_type', 'creator_type'),
        Index('idx_creator_profile_location', 'location'),
        Index('idx_creator_profile_rating', 'overall_rating'),
        Index('idx_creator_profile_verified', 'verified'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Basic profile information
    creator_type = Column(SQLEnum(CreatorType), nullable=False)
    stage_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    tagline = Column(String(500), nullable=True)
    
    # Contact and location
    location = Column(String(255), nullable=True)
    country_code = Column(String(2), nullable=True)
    timezone = Column(String(50), nullable=True)
    languages = Column(ARRAY(String), default=[])
    
    # Professional details
    years_experience = Column(Integer, nullable=True)
    professional_level = Column(SQLEnum(SkillLevel), default=SkillLevel.INTERMEDIATE)
    genres = Column(ARRAY(String), default=[])
    specializations = Column(ARRAY(String), default=[])
    
    # Skills and capabilities
    skills = Column(JSONB, default={})  # skill_name: skill_level
    equipment = Column(JSONB, default={})
    software_proficiency = Column(JSONB, default={})
    available_services = Column(ARRAY(String), default=[])
    
    # Portfolio and media
    portfolio_items = Column(JSONB, default=[])
    social_media_links = Column(JSONB, default={})
    website_url = Column(String(500), nullable=True)
    demo_reel_url = Column(String(500), nullable=True)
    
    # Availability and preferences
    availability_status = Column(String(50), default='available')  # available, busy, unavailable
    collaboration_preferences = Column(JSONB, default={})
    working_hours = Column(JSONB, default={})
    preferred_project_types = Column(ARRAY(String), default=[])
    
    # Pricing and rates
    hourly_rate_min = Column(Numeric(8, 2), nullable=True)
    hourly_rate_max = Column(Numeric(8, 2), nullable=True)
    project_rate_min = Column(Numeric(10, 2), nullable=True)
    project_rate_max = Column(Numeric(10, 2), nullable=True)
    currency_preference = Column(String(3), default='USD')
    
    # Reputation and verification
    verified = Column(Boolean, default=False)
    verification_level = Column(String(50), default='basic')  # basic, advanced, professional
    overall_rating = Column(Float, nullable=True)  # 1.0-5.0
    total_reviews = Column(Integer, default=0)
    total_collaborations = Column(Integer, default=0)
    successful_collaborations = Column(Integer, default=0)
    
    # AI and matching
    ai_compatibility_vector = Column(ARRAY(Float), nullable=True)
    personality_profile = Column(JSONB, default={})
    communication_style = Column(String(50), nullable=True)
    work_style_preferences = Column(JSONB, default={})
    
    # Performance metrics
    response_time_hours = Column(Float, nullable=True)
    project_completion_rate = Column(Float, nullable=True)
    on_time_delivery_rate = Column(Float, nullable=True)
    client_satisfaction_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    sent_collaborations = relationship("CollaborationRequest", foreign_keys="CollaborationRequest.requester_id", back_populates="requester")
    received_collaborations = relationship("CollaborationRequest", foreign_keys="CollaborationRequest.collaborator_id", back_populates="collaborator")
    projects_created = relationship("CollaborationProject", foreign_keys="CollaborationProject.creator_id", back_populates="creator")
    reviews_received = relationship("CreatorReview", foreign_keys="CreatorReview.reviewed_creator_id", back_populates="reviewed_creator")
    reviews_given = relationship("CreatorReview", foreign_keys="CreatorReview.reviewer_id", back_populates="reviewer")


class CollaborationRequest(Base):
    """Collaboration requests and matching system."""
    __tablename__ = 'collaboration_requests'
    __table_args__ = (
        Index('idx_collaboration_request_requester', 'requester_id'),
        Index('idx_collaboration_request_collaborator', 'collaborator_id'),
        Index('idx_collaboration_request_status', 'status'),
        Index('idx_collaboration_request_created', 'created_at'),
        Index('idx_collaboration_request_compatibility', 'compatibility_score'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    collaborator_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    
    # Request details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    collaboration_type = Column(String(100), nullable=False)
    project_scope = Column(Text, nullable=True)
    
    # Requirements and expectations
    required_skills = Column(ARRAY(String), default=[])
    preferred_experience_level = Column(SQLEnum(SkillLevel), nullable=True)
    estimated_duration = Column(String(100), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Budget and compensation
    budget_min = Column(Numeric(10, 2), nullable=True)
    budget_max = Column(Numeric(10, 2), nullable=True)
    currency_code = Column(String(3), default='USD')
    compensation_type = Column(String(50), nullable=False)  # fixed, hourly, revenue_share, equity
    revenue_share_percentage = Column(Float, nullable=True)
    
    # AI matching and compatibility
    compatibility_score = Column(Float, nullable=True)  # 0.0-1.0
    matching_algorithm_version = Column(String(50), nullable=True)
    matching_factors = Column(JSONB, default={})
    ai_recommendation_score = Column(Float, nullable=True)
    
    # Status and response
    status = Column(SQLEnum(CollaborationStatus), default=CollaborationStatus.PENDING)
    response_message = Column(Text, nullable=True)
    counter_offer = Column(JSONB, default={})
    
    # Timeline tracking
    response_deadline = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional metadata
    tags = Column(ARRAY(String), default=[])
    priority_level = Column(Integer, default=3)  # 1-5
    urgency_level = Column(Integer, default=3)  # 1-5
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = relationship("CreatorProfile", foreign_keys=[requester_id], back_populates="sent_collaborations")
    collaborator = relationship("CreatorProfile", foreign_keys=[collaborator_id], back_populates="received_collaborations")
    project = relationship("CollaborationProject", back_populates="collaboration_request", uselist=False)


# ================================
# PROJECT MANAGEMENT SCHEMAS
# ================================

class CollaborationProject(Base):
    """Collaborative project management and tracking."""
    __tablename__ = 'collaboration_projects'
    __table_args__ = (
        Index('idx_collaboration_project_creator', 'creator_id'),
        Index('idx_collaboration_project_request', 'collaboration_request_id'),
        Index('idx_collaboration_project_status', 'project_status'),
        Index('idx_collaboration_project_deadline', 'deadline'),
        Index('idx_collaboration_project_completion', 'completion_percentage'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaboration_request_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_requests.id'), nullable=False, unique=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    
    # Project details
    project_name = Column(String(255), nullable=False)
    project_description = Column(Text, nullable=True)
    project_type = Column(String(100), nullable=False)
    project_status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    
    # Timeline and milestones
    start_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    estimated_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    completion_percentage = Column(Float, default=0.0)  # 0.0-100.0
    milestones = Column(JSONB, default=[])
    deliverables = Column(JSONB, default=[])
    
    # Collaboration details
    team_members = Column(JSONB, default=[])  # Array of user IDs and roles
    roles_and_responsibilities = Column(JSONB, default={})
    communication_channels = Column(JSONB, default={})
    
    # Files and assets
    project_files = Column(JSONB, default=[])
    shared_resources = Column(JSONB, default=[])
    version_history = Column(JSONB, default=[])
    
    # Budget and payment
    total_budget = Column(Numeric(12, 2), nullable=True)
    budget_spent = Column(Numeric(12, 2), default=0)
    payment_schedule = Column(JSONB, default=[])
    revenue_sharing_agreement = Column(JSONB, default={})
    
    # Quality and feedback
    quality_checkpoints = Column(JSONB, default=[])
    feedback_history = Column(JSONB, default=[])
    client_satisfaction = Column(Float, nullable=True)  # 1.0-5.0
    
    # Legal and contracts
    contract_details = Column(JSONB, default={})
    intellectual_property_agreement = Column(JSONB, default={})
    confidentiality_agreement = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collaboration_request = relationship("CollaborationRequest", back_populates="project")
    creator = relationship("CreatorProfile", foreign_keys=[creator_id], back_populates="projects_created")
    marketplace_items = relationship("MarketplaceItem", back_populates="source_project")


# ================================
# MARKETPLACE SCHEMAS
# ================================

class MarketplaceItem(Base):
    """Marketplace items and digital goods for sale."""
    __tablename__ = 'marketplace_items'
    __table_args__ = (
        Index('idx_marketplace_item_creator', 'creator_id'),
        Index('idx_marketplace_item_type', 'item_type'),
        Index('idx_marketplace_item_status', 'status'),
        Index('idx_marketplace_item_price', 'price'),
        Index('idx_marketplace_item_rating', 'average_rating'),
        Index('idx_marketplace_item_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    source_project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=True)
    
    # Item details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    item_type = Column(SQLEnum(MarketplaceItemType), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    
    # Content and media
    primary_file_url = Column(String(500), nullable=False)
    preview_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    additional_files = Column(JSONB, default=[])
    
    # Metadata
    tags = Column(ARRAY(String), default=[])
    genres = Column(ARRAY(String), default=[])
    moods = Column(ARRAY(String), default=[])
    bpm = Column(Integer, nullable=True)
    key_signature = Column(String(10), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Technical specifications
    file_format = Column(String(20), nullable=False)
    quality = Column(String(50), nullable=True)
    file_size_mb = Column(Float, nullable=True)
    technical_details = Column(JSONB, default={})
    
    # Pricing and licensing
    price = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    license_type = Column(String(100), nullable=False)
    usage_rights = Column(JSONB, default={})
    exclusive = Column(Boolean, default=False)
    
    # Status and availability
    status = Column(String(50), default='draft')  # draft, pending_review, active, inactive, sold
    featured = Column(Boolean, default=False)
    promoted = Column(Boolean, default=False)
    
    # Performance metrics
    view_count = Column(BigInteger, default=0)
    download_count = Column(BigInteger, default=0)
    purchase_count = Column(BigInteger, default=0)
    like_count = Column(BigInteger, default=0)
    average_rating = Column(Float, nullable=True)  # 1.0-5.0
    total_ratings = Column(Integer, default=0)
    
    # Sales and revenue
    total_revenue = Column(Numeric(12, 2), default=0)
    last_sale_date = Column(DateTime(timezone=True), nullable=True)
    
    # SEO and discovery
    search_keywords = Column(ARRAY(String), default=[])
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("CreatorProfile", back_populates="marketplace_items")
    source_project = relationship("CollaborationProject", back_populates="marketplace_items")
    transactions = relationship("MarketplaceTransaction", back_populates="item")
    reviews = relationship("MarketplaceReview", back_populates="item")


class MarketplaceTransaction(Base):
    """Marketplace purchase transactions."""
    __tablename__ = 'marketplace_transactions'
    __table_args__ = (
        Index('idx_marketplace_transaction_buyer', 'buyer_id'),
        Index('idx_marketplace_transaction_seller', 'seller_id'),
        Index('idx_marketplace_transaction_item', 'item_id'),
        Index('idx_marketplace_transaction_status', 'transaction_status'),
        Index('idx_marketplace_transaction_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_items.id'), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    seller_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Transaction details
    transaction_id = Column(String(255), nullable=False, unique=True)
    transaction_status = Column(String(50), default='pending')  # pending, completed, failed, refunded
    
    # Financial details
    item_price = Column(Numeric(10, 2), nullable=False)
    platform_fee = Column(Numeric(8, 2), default=0)
    seller_earnings = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    
    # License and usage
    license_granted = Column(JSONB, default={})
    usage_restrictions = Column(JSONB, default={})
    exclusive_purchase = Column(Boolean, default=False)
    
    # Payment details
    payment_method = Column(String(50), nullable=False)
    payment_reference = Column(String(255), nullable=True)
    
    # Download and delivery
    download_url = Column(String(500), nullable=True)
    download_expires_at = Column(DateTime(timezone=True), nullable=True)
    download_count = Column(Integer, default=0)
    max_downloads = Column(Integer, default=5)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    item = relationship("MarketplaceItem", back_populates="transactions")


# ================================
# ESCROW PAYMENT SCHEMAS
# ================================

class EscrowPayment(Base):
    """Secure escrow payments for collaborations."""
    __tablename__ = 'escrow_payments'
    __table_args__ = (
        Index('idx_escrow_payment_project', 'project_id'),
        Index('idx_escrow_payment_payer', 'payer_id'),
        Index('idx_escrow_payment_payee', 'payee_id'),
        Index('idx_escrow_payment_status', 'escrow_status'),
        Index('idx_escrow_payment_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    payer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payee_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Escrow details
    escrow_amount = Column(Numeric(12, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    escrow_status = Column(SQLEnum(EscrowStatus), default=EscrowStatus.PENDING)
    
    # Milestone and release conditions
    milestone_description = Column(Text, nullable=False)
    release_conditions = Column(JSONB, default={})
    auto_release_date = Column(DateTime(timezone=True), nullable=True)
    
    # Approval and verification
    payer_approval = Column(Boolean, default=False)
    payee_confirmation = Column(Boolean, default=False)
    milestone_verified = Column(Boolean, default=False)
    
    # Dispute handling
    dispute_raised = Column(Boolean, default=False)
    dispute_reason = Column(Text, nullable=True)
    dispute_resolution = Column(Text, nullable=True)
    mediator_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Payment processing
    payment_method = Column(String(50), nullable=False)
    payment_reference = Column(String(255), nullable=True)
    platform_fee = Column(Numeric(8, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    funded_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    disputed_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


# ================================
# RATING AND REVIEW SCHEMAS
# ================================

class CreatorReview(Base):
    """Creator ratings and reviews system."""
    __tablename__ = 'creator_reviews'
    __table_args__ = (
        Index('idx_creator_review_reviewed', 'reviewed_creator_id'),
        Index('idx_creator_review_reviewer', 'reviewer_id'),
        Index('idx_creator_review_project', 'project_id'),
        Index('idx_creator_review_rating', 'overall_rating'),
        Index('idx_creator_review_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reviewed_creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=True)
    
    # Overall rating
    overall_rating = Column(Float, nullable=False)  # 1.0-5.0
    
    # Detailed ratings
    communication_rating = Column(Float, nullable=True)  # 1.0-5.0
    quality_rating = Column(Float, nullable=True)  # 1.0-5.0
    timeliness_rating = Column(Float, nullable=True)  # 1.0-5.0
    professionalism_rating = Column(Float, nullable=True)  # 1.0-5.0
    creativity_rating = Column(Float, nullable=True)  # 1.0-5.0
    
    # Written review
    review_title = Column(String(255), nullable=True)
    review_text = Column(Text, nullable=True)
    
    # Review metadata
    verified_collaboration = Column(Boolean, default=False)
    helpful_votes = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    
    # Response from reviewed creator
    creator_response = Column(Text, nullable=True)
    creator_responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewed_creator = relationship("CreatorProfile", foreign_keys=[reviewed_creator_id], back_populates="reviews_received")
    reviewer = relationship("CreatorProfile", foreign_keys=[reviewer_id], back_populates="reviews_given")


class MarketplaceReview(Base):
    """Marketplace item reviews and ratings."""
    __tablename__ = 'marketplace_reviews'
    __table_args__ = (
        Index('idx_marketplace_review_item', 'item_id'),
        Index('idx_marketplace_review_reviewer', 'reviewer_id'),
        Index('idx_marketplace_review_rating', 'rating'),
        Index('idx_marketplace_review_verified', 'verified_purchase'),
        Index('idx_marketplace_review_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_items.id'), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_transactions.id'), nullable=True)
    
    # Rating and review
    rating = Column(Float, nullable=False)  # 1.0-5.0
    review_title = Column(String(255), nullable=True)
    review_text = Column(Text, nullable=True)
    
    # Verification and authenticity
    verified_purchase = Column(Boolean, default=False)
    
    # Review engagement
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    
    # Creator response
    creator_response = Column(Text, nullable=True)
    creator_responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("MarketplaceItem", back_populates="reviews")


# ================================
# COLLABORATION ANALYTICS SCHEMAS
# ================================

class CollaborationAnalytics(Base):
    """Analytics for collaboration success and ROI tracking."""
    __tablename__ = 'collaboration_analytics'
    __table_args__ = (
        Index('idx_collaboration_analytics_creator', 'creator_id'),
        Index('idx_collaboration_analytics_project', 'project_id'),
        Index('idx_collaboration_analytics_period', 'analytics_period'),
        Index('idx_collaboration_analytics_roi', 'roi_percentage'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=True)
    
    # Analytics period
    analytics_period = Column(String(20), nullable=False)  # daily, weekly, monthly, project_based
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Collaboration metrics
    total_collaborations = Column(Integer, default=0)
    successful_collaborations = Column(Integer, default=0)
    failed_collaborations = Column(Integer, default=0)
    collaboration_success_rate = Column(Float, nullable=True)
    
    # Financial metrics
    total_revenue_generated = Column(Numeric(15, 2), default=0)
    average_project_value = Column(Numeric(10, 2), nullable=True)
    total_costs = Column(Numeric(15, 2), default=0)
    roi_percentage = Column(Float, nullable=True)
    
    # Performance metrics
    average_project_duration_days = Column(Float, nullable=True)
    on_time_completion_rate = Column(Float, nullable=True)
    client_satisfaction_average = Column(Float, nullable=True)
    repeat_client_rate = Column(Float, nullable=True)
    
    # Network growth
    new_connections_made = Column(Integer, default=0)
    network_size = Column(Integer, default=0)
    referrals_received = Column(Integer, default=0)
    referrals_given = Column(Integer, default=0)
    
    # Skill development
    new_skills_acquired = Column(ARRAY(String), default=[])
    skill_improvement_scores = Column(JSONB, default={})
    
    # Market positioning
    market_share_percentage = Column(Float, nullable=True)
    competitive_ranking = Column(Integer, nullable=True)
    price_competitiveness_score = Column(Float, nullable=True)
    
    # Detailed analytics data
    detailed_metrics = Column(JSONB, default={})
    trend_analysis = Column(JSONB, default={})
    recommendations = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ================================
# EXPORT FUNCTIONS
# ================================

def get_collaboration_marketplace_models():
    """Get all collaboration and marketplace models."""
    return [
        CreatorProfile,
        CollaborationRequest,
        CollaborationProject,
        MarketplaceItem,
        MarketplaceTransaction,
        EscrowPayment,
        CreatorReview,
        MarketplaceReview,
        CollaborationAnalytics,
    ]


def create_collaboration_marketplace_tables(engine):
    """Create all collaboration and marketplace tables."""
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_collaboration_marketplace_models()])
        logger.info("Successfully created collaboration and marketplace tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create collaboration and marketplace tables: {str(e)}")
        return False


# Export all models and functions
__all__ = [
    # Enums
    'CreatorType', 'SkillLevel', 'CollaborationStatus', 'ProjectStatus', 
    'MarketplaceItemType', 'EscrowStatus',
    
    # Models
    'CreatorProfile', 'CollaborationRequest', 'CollaborationProject', 'MarketplaceItem',
    'MarketplaceTransaction', 'EscrowPayment', 'CreatorReview', 'MarketplaceReview',
    'CollaborationAnalytics',
    
    # Functions
    'get_collaboration_marketplace_models', 'create_collaboration_marketplace_tables'
]