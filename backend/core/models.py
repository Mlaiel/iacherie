"""🎯 Consolidated Models - IA Influencer Agent Platform Enterprise
import logging

================================================================
Module: backend/core/models.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Consolidated Data Models - Ultra Production-Ready
Responsibility: All data models consolidated into a single comprehensive module
====================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC PIPELINE:
User Registration → Content Upload → AI Processing → Protection → 
Analytics → Collaboration → Monetization → Distribution → Growth
"""

from typing import Dict, List, Optional, Any, Union, Tuple, ClassVar
from datetime import datetime, timezone, timedelta, date
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from pathlib import Path
from decimal import Decimal
import uuid
import json
import hashlib

try:
    import numpy as np
except ImportError:
    np = None

try:
    from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, DECIMAL, Date, ForeignKey
    from sqlalchemy.orm import relationship
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.dialects.postgresql import UUID, ARRAY
    Base = declarative_base()
    HAS_SQLALCHEMY = True
except ImportError:
    Base = object
    HAS_SQLALCHEMY = False


# ============================================================================
# BASE MODELS AND MIXINS
# ============================================================================

class BaseModel:
    """Base model with common fields and functionality"""
    
    def __init__(self) -> None:
        super().__init__()
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now(timezone.utc)


# ============================================================================
# ENUMERATIONS
# ============================================================================

# User-related enums
class UserType(Enum):
    """User type enumeration"""
    CREATOR = "creator"
    ARTIST = "artist"
    INFLUENCER = "influencer" 
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    BUSINESS = "business"
    AGENCY = "agency"
    ADMIN = "admin"

class UserStatus(Enum):
    """User status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    INACTIVE = "inactive"
    PREMIUM = "premium"
    VIP = "vip"

class SubscriptionTier(Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"

# Content-related enums
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

class ContentVisibility(Enum):
    """Content visibility settings"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    SUBSCRIBERS_ONLY = "subscribers_only"
    PREMIUM_ONLY = "premium_only"

# Payment and monetization enums
class PaymentMethod(Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    WALLET = "wallet"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TransactionType(Enum):
    """Transaction type enumeration"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    COMMISSION = "commission"
    ROYALTY = "royalty"

# Analytics and metrics enums
class MetricType(Enum):
    """Types of metrics"""
    CONTENT = "content"
    USER = "user"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    PLATFORM = "platform"
    SYSTEM = "system"

class EngagementType(Enum):
    """Types of engagement"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    DOWNLOAD = "download"
    FOLLOW = "follow"
    SUBSCRIBE = "subscribe"

# ============================================================================
# USER MODELS
# ============================================================================

@dataclass
class UserModel(BaseModel):
    """
    Professional user data model for IA Influencer Agent platform.
    Comprehensive user management with multi-platform integration,
    analytics, subscription management, and content creator features.
    """
    
    def __post_init__(self) -> None:
        super().__init__()
    
    # Primary identification
    username: str = ""
    email: str = ""
    email_verified: bool = False
    phone: Optional[str] = None
    phone_verified: bool = False
    
    # Basic profile information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    
    # User type and status
    user_type: UserType = UserType.CREATOR
    status: UserStatus = UserStatus.ACTIVE
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    is_verified: bool = False
    is_premium: bool = False
    is_business: bool = False
    
    # Authentication and security
    password_hash: Optional[str] = None
    salt: Optional[str] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    
    # Location and demographics
    country: Optional[str] = None  # ISO country code
    region: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"  # Primary language
    languages_spoken: List[str] = field(default_factory=list)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    
    # Creator-specific information
    creator_category: Optional[str] = None
    content_focus: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    collaboration_open: bool = True
    hire_available: bool = False
    hourly_rate: Optional[Decimal] = None
    currency: str = "EUR"
    
    # Platform integrations
    platform_integrations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InfluencerModel(BaseModel):
    """Influencer-specific data model"""
    
    def __post_init__(self) -> None:
        super().__init__()
    
    user_id: str = ""
    niche: str = ""
    follower_count: int = 0
    engagement_rate: float = 0.0
    average_likes: int = 0
    average_comments: int = 0
    media_kit_url: Optional[str] = None
    brand_partnerships: List[str] = field(default_factory=list)
    sponsored_content_rate: Optional[Decimal] = None
    audience_demographics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonalityModel(BaseModel):
    """Personality traits and AI persona model"""
    
    def __post_init__(self) -> None:
        super().__init__()
    
    user_id: str = ""
    personality_type: str = ""  # MBTI, Big Five, etc.
    traits: Dict[str, Any] = field(default_factory=dict)
    content_style: str = ""
    communication_style: str = ""
    target_emotions: List[str] = field(default_factory=list)
    brand_voice: Dict[str, Any] = field(default_factory=dict)
    ai_persona_settings: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CONTENT MODELS
# ============================================================================

@dataclass
class ContentModel(BaseModel):
    """
    Advanced content data model for multi-format creator content 
    with AI protection and monetization
    """
    
    def __post_init__(self) -> None:
        super().__init__()
    
    # Basic content information
    title: str = ""
    description: Optional[str] = None
    content_type: ContentType = ContentType.MIXED
    status: ContentStatus = ContentStatus.UPLOADED
    visibility: ContentVisibility = ContentVisibility.PUBLIC
    
    # Creator and ownership
    creator_id: str = ""
    creator_username: str = ""
    original_creator_id: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)
    
    # File information
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    file_format: str = ""
    file_hash: str = ""
    duration: Optional[float] = None  # in seconds
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    language: str = "en"
    explicit_content: bool = False
    
    # AI and processing
    ai_processed: bool = False
    fingerprint_id: Optional[str] = None
    vector_embedding: Optional[List[float]] = None
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Protection and licensing
    copyright_protected: bool = True
    license_type: str = "standard"
    usage_rights: Dict[str, Any] = field(default_factory=dict)
    
    # Analytics and performance
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    download_count: int = 0
    
    # Monetization
    monetized: bool = False
    price: Optional[Decimal] = None
    revenue_generated: Decimal = Decimal('0.00')
    
    # Publication and distribution
    published_at: Optional[datetime] = None
    distribution_platforms: List[str] = field(default_factory=list)
    seo_optimized: bool = False
    seo_keywords: List[str] = field(default_factory=list)


@dataclass
class PostModel(BaseModel):
    """Social media post model"""
    
    content_id: str = ""
    platform: str = ""
    post_text: str = ""
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoModel(BaseModel):
    """Video content specific model"""
    
    content_id: str = ""
    resolution: str = "1080p"
    frame_rate: float = 30.0
    bitrate: int = 0
    codec: str = "h264"
    thumbnail_url: str = ""
    preview_url: str = ""
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    subtitles: Dict[str, str] = field(default_factory=dict)  # language: subtitle_file
    quality_variants: Dict[str, str] = field(default_factory=dict)


@dataclass
class ImageModel(BaseModel):
    """Image content specific model"""
    
    content_id: str = ""
    width: int = 0
    height: int = 0
    color_depth: int = 24
    compression: str = "jpg"
    thumbnail_url: str = ""
    alt_text: str = ""
    exif_data: Dict[str, Any] = field(default_factory=dict)
    color_palette: List[str] = field(default_factory=list)


@dataclass
class AudioModel(BaseModel):
    """Audio content specific model"""
    
    content_id: str = ""
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2
    codec: str = "mp3"
    waveform_data: Optional[List[float]] = None
    tempo: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None


@dataclass
class VoiceModel(BaseModel):
    """Voice and speech specific model"""
    
    audio_id: str = ""
    speaker_id: str = ""
    language: str = "en"
    accent: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None
    emotion: Optional[str] = None
    transcript: str = ""
    confidence_score: float = 0.0
    voice_characteristics: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FINANCIAL MODELS
# ============================================================================

@dataclass
class SubscriptionModel(BaseModel):
    """Subscription management model"""
    
    user_id: str = ""
    tier: SubscriptionTier = SubscriptionTier.FREE
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    auto_renew: bool = True
    payment_method_id: Optional[str] = None
    monthly_price: Decimal = Decimal('0.00')
    annual_price: Decimal = Decimal('0.00')
    features: List[str] = field(default_factory=list)
    usage_limits: Dict[str, int] = field(default_factory=dict)


@dataclass
class PaymentModel(BaseModel):
    """Payment processing model"""
    
    def __post_init__(self) -> None:
        super().__init__()
    
    user_id: str = ""
    amount: Decimal = Decimal('0.00')
    currency: str = "EUR"
    payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: str = ""
    provider: str = ""
    provider_transaction_id: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvoiceModel(BaseModel):
    """Invoice model"""
    
    user_id: str = ""
    invoice_number: str = ""
    amount: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    currency: str = "EUR"
    due_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None
    items: List[Dict[str, Any]] = field(default_factory=list)
    billing_address: Dict[str, str] = field(default_factory=dict)


@dataclass
class TransactionModel(BaseModel):
    """Financial transaction model"""
    
    user_id: str = ""
    transaction_type: TransactionType = TransactionType.PAYMENT
    amount: Decimal = Decimal('0.00')
    currency: str = "EUR"
    status: PaymentStatus = PaymentStatus.PENDING
    reference_id: str = ""
    description: str = ""
    fee_amount: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    processed_at: Optional[datetime] = None


@dataclass
class WalletModel(BaseModel):
    """Digital wallet model"""
    
    user_id: str = ""
    balance: Decimal = Decimal('0.00')
    currency: str = "EUR"
    frozen_amount: Decimal = Decimal('0.00')
    available_balance: Decimal = Decimal('0.00')
    transactions: List[str] = field(default_factory=list)  # transaction IDs
    last_transaction_at: Optional[datetime] = None


# ============================================================================
# MARKETPLACE MODELS
# ============================================================================

@dataclass
class MarketplaceModel(BaseModel):
    """Marketplace platform model"""
    
    name: str = ""
    description: str = ""
    commission_rate: float = 0.05
    supported_categories: List[str] = field(default_factory=list)
    payment_methods: List[PaymentMethod] = field(default_factory=list)
    active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProductModel(BaseModel):
    """Marketplace product model"""
    
    seller_id: str = ""
    title: str = ""
    description: str = ""
    price: Decimal = Decimal('0.00')
    currency: str = "EUR"
    category: str = ""
    tags: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    digital_product: bool = True
    download_url: Optional[str] = None
    license_terms: str = ""
    active: bool = True


@dataclass
class OrderModel(BaseModel):
    """Marketplace order model"""
    
    buyer_id: str = ""
    seller_id: str = ""
    product_id: str = ""
    quantity: int = 1
    unit_price: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    status: str = "pending"
    payment_id: Optional[str] = None
    fulfillment_date: Optional[datetime] = None
    notes: str = ""


@dataclass
class ReviewModel(BaseModel):
    """Review and rating model"""
    
    reviewer_id: str = ""
    target_id: str = ""  # user, product, content, etc.
    target_type: str = ""  # "user", "product", "content"
    rating: int = 5  # 1-5 stars
    title: str = ""
    review_text: str = ""
    helpful_votes: int = 0
    total_votes: int = 0
    verified_purchase: bool = False
    moderated: bool = False


@dataclass
class RatingModel(BaseModel):
    """Simple rating model"""
    
    user_id: str = ""
    target_id: str = ""
    target_type: str = ""
    rating: float = 0.0
    max_rating: float = 5.0
    weight: float = 1.0


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

@dataclass
class AnalyticsModel(BaseModel):
    """Comprehensive analytics data model"""
    
    def __post_init__(self) -> None:
        super().__init__()
    
    entity_id: str = ""  # user, content, etc.
    entity_type: str = ""
    metric_type: MetricType = MetricType.CONTENT
    metric_name: str = ""
    metric_value: float = 0.0
    unit: str = ""
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dimensions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsModel(BaseModel):
    """Metrics aggregation model"""
    
    target_id: str = ""
    target_type: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period: str = "daily"  # daily, weekly, monthly, yearly


@dataclass
class EngagementModel(BaseModel):
    """Engagement tracking model"""
    
    content_id: str = ""
    user_id: str = ""
    engagement_type: EngagementType = EngagementType.VIEW
    platform: str = ""
    session_id: Optional[str] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GrowthModel(BaseModel):
    """Growth metrics model"""
    
    entity_id: str = ""
    entity_type: str = ""
    growth_metric: str = ""
    current_value: float = 0.0
    previous_value: float = 0.0
    growth_rate: float = 0.0
    growth_absolute: float = 0.0
    period: str = "monthly"
    trend: str = "stable"  # growing, declining, stable


@dataclass
class AudienceModel(BaseModel):
    """Audience analysis model"""
    
    creator_id: str = ""
    total_followers: int = 0
    active_followers: int = 0
    demographics: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class DemographicModel(BaseModel):
    """Demographic data model"""
    
    audience_id: str = ""
    age_groups: Dict[str, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    location_data: Dict[str, float] = field(default_factory=dict)
    language_preferences: Dict[str, float] = field(default_factory=dict)
    device_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class LocationModel(BaseModel):
    """Location-based analytics model"""
    
    entity_id: str = ""
    country: str = ""
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = ""
    user_count: int = 0
    engagement_rate: float = 0.0


# ============================================================================
# COLLABORATION MODELS
# ============================================================================

@dataclass
class CollaborationModel(BaseModel):
    """Collaboration management model"""
    
    def __post_init__(self) -> None:
        super().__init__()
    
    initiator_id: str = ""
    collaborator_id: str = ""
    project_title: str = ""
    description: str = ""
    status: str = "pending"  # pending, active, completed, cancelled
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    revenue_split: Dict[str, float] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)


@dataclass
class CampaignModel(BaseModel):
    """Marketing campaign model"""
    
    creator_id: str = ""
    brand_id: str = ""
    title: str = ""
    description: str = ""
    budget: Decimal = Decimal('0.00')
    currency: str = "EUR"
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    target_audience: Dict[str, Any] = field(default_factory=dict)
    content_requirements: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)


@dataclass
class BrandModel(BaseModel):
    """Brand information model"""
    
    name: str = ""
    description: str = ""
    industry: str = ""
    website_url: str = ""
    logo_url: str = ""
    brand_colors: List[str] = field(default_factory=list)
    brand_voice: str = ""
    target_audience: Dict[str, Any] = field(default_factory=dict)
    budget_range: Dict[str, Decimal] = field(default_factory=dict)
    contact_info: Dict[str, str] = field(default_factory=dict)


@dataclass
class SponsorModel(BaseModel):
    """Sponsor/partnership model"""
    
    brand_id: str = ""
    creator_id: str = ""
    sponsorship_type: str = ""  # product, monetary, service
    value: Decimal = Decimal('0.00')
    currency: str = "EUR"
    duration: int = 30  # days
    requirements: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    tracking_metrics: List[str] = field(default_factory=list)


@dataclass
class ContractModel(BaseModel):
    """Contract and agreement model"""
    
    parties: List[str] = field(default_factory=list)
    contract_type: str = ""
    title: str = ""
    terms_and_conditions: str = ""
    duration: int = 0  # days
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    signed_by: List[str] = field(default_factory=list)
    signed_at: Optional[datetime] = None
    status: str = "draft"  # draft, active, completed, terminated


# ============================================================================
# COMMUNICATION MODELS
# ============================================================================

@dataclass
class NotificationModel(BaseModel):
    """Notification system model"""
    
    recipient_id: str = ""
    sender_id: Optional[str] = None
    title: str = ""
    message: str = ""
    notification_type: str = "info"  # info, warning, error, success
    priority: str = "normal"  # low, normal, high, urgent
    read: bool = False
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageModel(BaseModel):
    """Direct messaging model"""
    
    sender_id: str = ""
    recipient_id: str = ""
    conversation_id: str = ""
    content: str = ""
    message_type: str = "text"  # text, image, file, audio, video
    attachment_urls: List[str] = field(default_factory=list)
    read: bool = False
    read_at: Optional[datetime] = None
    edited: bool = False
    edited_at: Optional[datetime] = None


@dataclass
class ChatModel(BaseModel):
    """Chat/conversation model"""
    
    participants: List[str] = field(default_factory=list)
    title: Optional[str] = None
    chat_type: str = "direct"  # direct, group, channel
    last_message_id: Optional[str] = None
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    muted_by: List[str] = field(default_factory=list)
    archived_by: List[str] = field(default_factory=list)


@dataclass
class CommentModel(BaseModel):
    """Comment system model"""
    
    content_id: str = ""
    author_id: str = ""
    parent_comment_id: Optional[str] = None
    content: str = ""
    like_count: int = 0
    reply_count: int = 0
    edited: bool = False
    edited_at: Optional[datetime] = None
    moderated: bool = False
    flagged: bool = False


# ============================================================================
# SOCIAL INTERACTION MODELS
# ============================================================================

@dataclass
class LikeModel(BaseModel):
    """Like/reaction model"""
    
    user_id: str = ""
    target_id: str = ""  # content, comment, etc.
    target_type: str = ""
    reaction_type: str = "like"  # like, love, laugh, angry, sad


@dataclass
class ShareModel(BaseModel):
    """Share/repost model"""
    
    user_id: str = ""
    content_id: str = ""
    platform: str = ""
    share_type: str = "public"  # public, private, direct
    message: Optional[str] = None
    shared_to: List[str] = field(default_factory=list)


@dataclass
class FollowModel(BaseModel):
    """Follow/subscription model"""
    
    follower_id: str = ""
    followed_id: str = ""
    follow_type: str = "follow"  # follow, subscribe, friend
    notifications_enabled: bool = True
    followed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BlockModel(BaseModel):
    """Block/mute model"""
    
    blocker_id: str = ""
    blocked_id: str = ""
    block_type: str = "block"  # block, mute, restrict
    reason: Optional[str] = None
    blocked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# CREATOR MODELS
# ============================================================================

@dataclass
class CreatorModel(BaseModel):
    """Professional creator model with comprehensive tracking"""
    
    creator_id: str = field(default_factory=lambda: f"creator_{uuid.uuid4().hex[:12]}")
    user_id: str = ""
    creator_type: str = "creator"
    creator_status: str = "active"
    subscription_tier: str = "free"
    verification_level: int = 0
    creator_tier: str = "basic"
    
    # Professional information
    display_name: str = ""
    bio: str = ""
    professional_tagline: str = ""
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    
    # Statistics
    total_followers: int = 0
    total_content: int = 0
    total_collaborations: int = 0
    engagement_rate: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    social_links: Dict[str, str] = field(default_factory=dict)
    platform_data: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# REVENUE MODELS  
# ============================================================================

@dataclass 
class RevenueModel(BaseModel):
    """Revenue tracking model"""
    
    revenue_id: str = field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    content_id: str = ""
    platform: str = ""
    revenue_type: str = "streaming"
    
    # Financial data
    gross_amount: Decimal = field(default=Decimal('0.00'))
    currency: str = "EUR"
    net_amount: Decimal = field(default=Decimal('0.00'))
    platform_fee: Decimal = field(default=Decimal('0.00'))
    tax_amount: Decimal = field(default=Decimal('0.00'))
    payout_amount: Decimal = field(default=Decimal('0.00'))
    
    # Payment tracking
    payment_status: str = "pending"
    payment_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    
    # Analytics
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_verified: bool = False


# ============================================================================
# PROTECTION MODELS
# ============================================================================

@dataclass
class ProtectionModel(BaseModel):
    """Content protection model"""
    
    protection_id: str = field(default_factory=lambda: f"prot_{uuid.uuid4().hex[:12]}")
    content_id: str = ""
    creator_id: str = ""
    protection_type: str = "automatic"
    protection_status: str = "active"
    
    # Protection settings
    monitoring_enabled: bool = True
    takedown_enabled: bool = True
    watermark_enabled: bool = False
    encryption_enabled: bool = False
    
    # Metadata
    protection_rules: Dict[str, Any] = field(default_factory=dict)
    violation_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Statistics
    violations_detected: int = 0
    takedowns_issued: int = 0
    last_scan: Optional[datetime] = None


@dataclass
class ViolationModel(BaseModel):
    """Content violation model"""
    
    violation_id: str = field(default_factory=lambda: f"viol_{uuid.uuid4().hex[:12]}")
    content_id: str = ""
    protection_id: str = ""
    violation_type: str = "copyright"
    violation_status: str = "detected"
    
    # Violation details
    platform: str = ""
    violating_url: str = ""
    similarity_score: float = 0.0
    confidence_score: float = 0.0
    
    # Evidence
    evidence_urls: List[str] = field(default_factory=list)
    evidence_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Resolution
    takedown_requested: bool = False
    takedown_successful: bool = False
    resolution_notes: Optional[str] = None


@dataclass
class TakedownModel(BaseModel):
    """Takedown request model"""
    
    takedown_id: str = field(default_factory=lambda: f"td_{uuid.uuid4().hex[:12]}")
    violation_id: str = ""
    platform: str = ""
    takedown_type: str = "dmca"
    takedown_status: str = "pending"
    
    # Request details
    request_url: str = ""
    request_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_date: Optional[datetime] = None
    
    # Legal information
    legal_basis: str = ""
    counter_notice_period: Optional[datetime] = None
    
    # Results
    success: bool = False
    response_details: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# LICENSING MODELS
# ============================================================================

@dataclass
class LicensingModel(BaseModel):
    """Content licensing model"""
    
    license_id: str = field(default_factory=lambda: f"lic_{uuid.uuid4().hex[:12]}")
    content_id: str = ""
    creator_id: str = ""
    licensee_id: Optional[str] = None
    
    license_type: str = "standard"
    license_status: str = "active"
    
    # Terms
    usage_rights: List[str] = field(default_factory=list)
    territory_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Optional[datetime] = None
    
    # Financial terms
    license_fee: Decimal = field(default=Decimal('0.00'))
    royalty_rate: float = 0.0
    minimum_guarantee: Decimal = field(default=Decimal('0.00'))
    
    # Legal
    contract_url: Optional[str] = None
    terms_accepted: bool = False
    signature_date: Optional[datetime] = None


# ============================================================================
# FINGERPRINT MODELS
# ============================================================================

@dataclass
class FingerprintModel(BaseModel):
    """Content fingerprint model"""
    
    fingerprint_id: str = field(default_factory=lambda: f"fp_{uuid.uuid4().hex[:12]}")
    content_id: str = ""
    fingerprint_type: str = "audio"
    algorithm: str = "perceptual_hash"
    
    # Fingerprint data
    fingerprint_data: str = ""
    fingerprint_hash: str = ""
    quality_score: float = 0.0
    
    # Processing info
    processing_time: float = 0.0
    algorithm_version: str = "1.0"
    confidence_score: float = 0.0
    
    # Metadata
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "pending"


# ============================================================================
# AUDIT MODELS
# ============================================================================

@dataclass
class AuditModel(BaseModel):
    """System audit model"""
    
    audit_id: str = field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    entity_type: str = ""
    entity_id: str = ""
    action: str = ""
    action_type: str = "read"
    
    # User context
    user_id: Optional[str] = None
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Details
    changes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Security
    is_sensitive: bool = False
    retention_period: Optional[datetime] = None


@dataclass
class LogModel(BaseModel):
    """System log model"""
    
    log_id: str = field(default_factory=lambda: f"log_{uuid.uuid4().hex[:12]}")
    level: str = "info"
    source: str = ""
    message: str = ""
    
    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EventModel(BaseModel):
    """System event model"""
    
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: str = ""
    event_category: str = ""
    event_name: str = ""
    
    # Context
    source: str = ""
    user_id: Optional[str] = None
    entity_id: Optional[str] = None
    
    # Data
    event_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# GOVERNANCE MODELS
# ============================================================================

@dataclass
class GovernanceModel(BaseModel):
    """Governance and compliance model"""
    
    governance_id: str = field(default_factory=lambda: f"gov_{uuid.uuid4().hex[:12]}")
    entity_type: str = ""
    entity_id: str = ""
    policy_type: str = ""
    
    # Compliance status
    compliance_status: str = "pending"
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    
    # Policy details
    policy_version: str = "1.0"
    requirements: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    reviewer_id: Optional[str] = None


@dataclass
class ComplianceModel(BaseModel):
    """Compliance tracking model"""
    
    compliance_id: str = field(default_factory=lambda: f"comp_{uuid.uuid4().hex[:12]}")
    entity_id: str = ""
    regulation_type: str = ""
    compliance_status: str = "pending"
    
    # Requirements
    required_actions: List[str] = field(default_factory=list)
    completed_actions: List[str] = field(default_factory=list)
    
    # Deadlines
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    # Evidence
    evidence_urls: List[str] = field(default_factory=list)
    documentation: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyModel(BaseModel):
    """Policy definition model"""
    
    policy_id: str = field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:12]}")
    policy_name: str = ""
    policy_type: str = ""
    policy_status: str = "active"
    
    # Policy content
    policy_text: str = ""
    policy_version: str = "1.0"
    effective_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry_date: Optional[datetime] = None
    
    # Scope
    applicable_entities: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    author_id: Optional[str] = None


# ============================================================================
# PLATFORM MODELS
# ============================================================================

@dataclass
class PlatformModel(BaseModel):
    """Platform integration model"""
    
    platform_id: str = field(default_factory=lambda: f"plat_{uuid.uuid4().hex[:12]}")
    platform_name: str = ""
    platform_type: str = ""
    platform_status: str = "active"
    
    # API configuration
    api_endpoint: str = ""
    api_version: str = "1.0"
    auth_method: str = "oauth2"
    
    # Capabilities
    supported_features: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    
    # Metadata
    configuration: Dict[str, Any] = field(default_factory=dict)
    last_sync: Optional[datetime] = None


@dataclass
class IntegrationModel(BaseModel):
    """Platform integration instance model"""
    
    integration_id: str = field(default_factory=lambda: f"int_{uuid.uuid4().hex[:12]}")
    platform_id: str = ""
    user_id: str = ""
    integration_status: str = "active"
    
    # Credentials
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    
    # Configuration
    settings: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    
    # Statistics
    last_sync: Optional[datetime] = None
    sync_count: int = 0
    error_count: int = 0


@dataclass
class APIModel(BaseModel):
    """API endpoint model"""
    
    api_id: str = field(default_factory=lambda: f"api_{uuid.uuid4().hex[:12]}")
    platform_id: str = ""
    endpoint_name: str = ""
    endpoint_url: str = ""
    http_method: str = "GET"
    
    # Configuration
    headers: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Rate limiting
    rate_limit: int = 100
    rate_window: int = 3600  # seconds
    
    # Monitoring
    success_count: int = 0
    error_count: int = 0
    last_called: Optional[datetime] = None


# ============================================================================
# AI PROCESSING MODELS
# ============================================================================

@dataclass
class AIProcessingJobModel(BaseModel):
    """AI processing job model"""
    
    job_id: str = field(default_factory=lambda: f"job_{uuid.uuid4().hex[:12]}")
    content_id: str = ""
    processing_type: str = "analysis"
    job_status: str = "queued"
    
    # AI model configuration
    ai_model_type: str = "neural_network"
    model_version: str = "1.0"
    processing_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Processing details
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: float = 0.0
    
    # Results
    results: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    error_message: Optional[str] = None
    
    # Resources
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0


# ============================================================================
# PERFORMANCE MODELS
# ============================================================================

@dataclass
class PerformanceMetricModel(BaseModel):
    """Performance metrics model"""
    
    metric_id: str = field(default_factory=lambda: f"metric_{uuid.uuid4().hex[:12]}")
    entity_type: str = ""
    entity_id: str = ""
    metric_type: str = ""
    
    # Metric values
    value: float = 0.0
    unit: str = ""
    threshold: Optional[float] = None
    
    # Context
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period: str = "instant"  # instant, hour, day, week, month
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class MonetizationModel(BaseModel):
    """Monetization configuration model"""
    
    monetization_id: str = field(default_factory=lambda: f"mon_{uuid.uuid4().hex[:12]}")
    content_id: str = ""
    creator_id: str = ""
    monetization_type: str = "subscription"
    
    # Configuration
    is_enabled: bool = True
    pricing_model: str = "fixed"
    base_price: Decimal = field(default=Decimal('0.00'))
    currency: str = "EUR"
    
    # Revenue sharing
    creator_share: float = 0.7
    platform_share: float = 0.3
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    restrictions: List[str] = field(default_factory=list)
    
    # Statistics
    total_revenue: Decimal = field(default=Decimal('0.00'))
    subscription_count: int = 0
    purchase_count: int = 0


# ============================================================================
# ADDITIONAL SPECIALIZED MODELS
# ============================================================================

@dataclass
class RevenueSummaryModel(BaseModel):
    """Revenue summary for analytics and reporting"""
    
    summary_id: str = field(default_factory=lambda: f"summary_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Financial totals
    total_gross: Decimal = field(default=Decimal('0.00'))
    total_net: Decimal = field(default=Decimal('0.00'))
    total_fees: Decimal = field(default=Decimal('0.00'))
    total_taxes: Decimal = field(default=Decimal('0.00'))
    total_payout: Decimal = field(default=Decimal('0.00'))
    currency: str = "EUR"
    
    # Breakdown by revenue type
    revenue_by_type: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_platform: Dict[str, Decimal] = field(default_factory=dict)
    
    # Analytics
    growth_rate: float = 0.0
    comparison_period: Optional[str] = None
    top_performing_content: List[str] = field(default_factory=list)


@dataclass
class MLModelVersionModel(BaseModel):
    """ML model version tracking"""
    
    version_id: str = field(default_factory=lambda: f"mlver_{uuid.uuid4().hex[:12]}")
    model_name: str = ""
    version: str = "1.0"
    model_type: str = "neural_network"
    
    # Performance metrics
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    # Status
    is_active: bool = False
    is_production: bool = False
    deployment_date: Optional[datetime] = None
    
    # Metadata
    training_data_hash: Optional[str] = None
    model_size: Optional[int] = None
    training_duration: Optional[float] = None


@dataclass
class PaymentRequestModel(BaseModel):
    """Payment request model"""
    
    request_id: str = field(default_factory=lambda: f"payreq_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    amount: Decimal = field(default=Decimal('0.00'))
    currency: str = "EUR"
    
    # Request details
    payment_type: str = "payout"
    payment_method: str = "bank_transfer"
    request_status: str = "pending"
    
    # Recipient information
    recipient_name: str = ""
    account_details: Dict[str, str] = field(default_factory=dict)
    
    # Processing
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    processing_notes: Optional[str] = None
    
    # Validation
    is_validated: bool = False
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class PlatformConfigModel(BaseModel):
    """Platform configuration model"""
    
    config_id: str = field(default_factory=lambda: f"config_{uuid.uuid4().hex[:12]}")
    platform_id: str = ""
    config_type: str = "general"
    config_name: str = ""
    
    # Configuration data
    config_value: str = ""
    config_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    is_active: bool = True
    is_sensitive: bool = False
    environment: str = "production"
    
    # Versioning
    version: str = "1.0"
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_by: Optional[str] = None
    
    # Validation
    validation_rules: List[str] = field(default_factory=list)
    is_valid: bool = True


# ============================================================================
# MODEL REGISTRY AND UTILITIES
# ============================================================================

# Model registry for dynamic access
MODEL_REGISTRY = {
    # User models
    "user": UserModel,
    "influencer": InfluencerModel,
    "personality": PersonalityModel,
    
    # Content models
    "content": ContentModel,
    "post": PostModel,
    "video": VideoModel,
    "image": ImageModel,
    "audio": AudioModel,
    "voice": VoiceModel,
    
    # Financial models
    "subscription": SubscriptionModel,
    "payment": PaymentModel,
    "invoice": InvoiceModel,
    "transaction": TransactionModel,
    "wallet": WalletModel,
    
    # Marketplace models
    "marketplace": MarketplaceModel,
    "product": ProductModel,
    "order": OrderModel,
    "review": ReviewModel,
    "rating": RatingModel,
    
    # Analytics models
    "analytics": AnalyticsModel,
    "metrics": MetricsModel,
    "engagement": EngagementModel,
    "growth": GrowthModel,
    "audience": AudienceModel,
    "demographic": DemographicModel,
    "location": LocationModel,
    
    # Collaboration models
    "collaboration": CollaborationModel,
    "campaign": CampaignModel,
    "brand": BrandModel,
    "sponsor": SponsorModel,
    "contract": ContractModel,
    
    # Communication models
    "notification": NotificationModel,
    "message": MessageModel,
    "chat": ChatModel,
    "comment": CommentModel,
    
    # Social interaction models
    "like": LikeModel,
    "share": ShareModel,
    "follow": FollowModel,
    "block": BlockModel,
    
    # Creator models
    "creator": CreatorModel,
    
    # Revenue models
    "revenue": RevenueModel,
    
    # Protection models
    "protection": ProtectionModel,
    "violation": ViolationModel,
    "takedown": TakedownModel,
    
    # Licensing models
    "licensing": LicensingModel,
    
    # Fingerprint models
    "fingerprint": FingerprintModel,
    
    # Audit models
    "audit": AuditModel,
    "log": LogModel,
    "event": EventModel,
    
    # Governance models
    "governance": GovernanceModel,
    "compliance": ComplianceModel,
    "policy": PolicyModel,
    
    # Platform models
    "platform": PlatformModel,
    "integration": IntegrationModel,
    "api": APIModel,
    
    # AI processing models
    "ai_processing_job": AIProcessingJobModel,
    
    # Performance models
    "performance_metric": PerformanceMetricModel,
    "monetization": MonetizationModel,
    
    # Additional specialized models
    "revenue_summary": RevenueSummaryModel,
    "ml_model_version": MLModelVersionModel,
    "payment_request": PaymentRequestModel,
    "platform_config": PlatformConfigModel,
}


def get_model(model_name -> None: str) -> None:
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name.lower())


def list_available_models() -> List[str]:
    """List all available model names"""
    return list(MODEL_REGISTRY.keys())


def create_model(model_name -> None: str, **kwargs) -> None:
    """Create a model instance by name"""
    model_class = get_model(model_name)
    if model_class:
        return model_class(**kwargs)
    raise ValueError(f"Unknown model: {model_name}")


# Export all models and utilities
__all__ = [
    # Base
    "BaseModel",
    
    # Enums
    "UserType", "UserStatus", "SubscriptionTier",
    "ContentType", "ContentStatus", "ContentVisibility",
    "PaymentMethod", "PaymentStatus", "TransactionType",
    "MetricType", "EngagementType",
    
    # User models
    "UserModel", "InfluencerModel", "PersonalityModel",
    
    # Content models
    "ContentModel", "PostModel", "VideoModel", "ImageModel", "AudioModel", "VoiceModel",
    
    # Financial models
    "SubscriptionModel", "PaymentModel", "InvoiceModel", "TransactionModel", "WalletModel",
    
    # Marketplace models
    "MarketplaceModel", "ProductModel", "OrderModel", "ReviewModel", "RatingModel",
    
    # Analytics models
    "AnalyticsModel", "MetricsModel", "EngagementModel", "GrowthModel", 
    "AudienceModel", "DemographicModel", "LocationModel",
    
    # Collaboration models
    "CollaborationModel", "CampaignModel", "BrandModel", "SponsorModel", "ContractModel",
    
    # Communication models
    "NotificationModel", "MessageModel", "ChatModel", "CommentModel",
    
    # Social interaction models
    "LikeModel", "ShareModel", "FollowModel", "BlockModel",
    
    # Creator models
    "CreatorModel",
    
    # Revenue models
    "RevenueModel",
    
    # Protection models
    "ProtectionModel", "ViolationModel", "TakedownModel",
    
    # Licensing models
    "LicensingModel",
    
    # Fingerprint models
    "FingerprintModel",
    
    # Audit models
    "AuditModel", "LogModel", "EventModel",
    
    # Governance models
    "GovernanceModel", "ComplianceModel", "PolicyModel",
    
    # Platform models
    "PlatformModel", "IntegrationModel", "APIModel",
    
    # AI processing models
    "AIProcessingJobModel",
    
    # Performance models
    "PerformanceMetricModel", "MonetizationModel",
    
    # Additional specialized models
    "RevenueSummaryModel", "MLModelVersionModel", "PaymentRequestModel", "PlatformConfigModel",
    
    # Utilities
    "MODEL_REGISTRY", "get_model", "list_available_models", "create_model",
]