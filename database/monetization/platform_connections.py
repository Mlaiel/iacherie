"""Platform Connections - Multi-Platform API Integration System

Ultra-advanced platform integration system connecting to all major content platforms
(YouTube, Spotify, Instagram, TikTok, etc.) for revenue tracking and content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""
from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, Boolean, JSON, 
    ForeignKey, Index, Enum as SQLEnum, Numeric, UniqueConstraint,
    CheckConstraint, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union

Base = declarative_base()


class Platform(Enum):
    """Supported content platforms"""    # Music platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    
    # Video platforms
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    
    # Social media
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"
    CLUBHOUSE = "clubhouse"
    
    # Podcast platforms
    APPLE_PODCASTS = "apple_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    ANCHOR = "anchor"
    CASTBOX = "castbox"
    
    # Creator platforms
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    
    # E-commerce
    SHOPIFY = "shopify"
    ETSY = "etsy"
    AMAZON = "amazon"
    
    # Live streaming
    YOUTUBE_LIVE = "youtube_live"
    FACEBOOK_LIVE = "facebook_live"
    INSTAGRAM_LIVE = "instagram_live"
    TIKTOK_LIVE = "tiktok_live"


class ConnectionStatus(Enum):
    """Platform connection status"""    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"


class DataSyncFrequency(Enum):
    """Data synchronization frequency options"""    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"


class PlatformConnection(Base):
    """User connections to content platforms"""    __tablename__ = "platform_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Platform identification
    platform = Column(SQLEnum(Platform), nullable=False)
    platform_user_id = Column(String(255), nullable=False)
    platform_username = Column(String(255))
    platform_display_name = Column(String(255))
    platform_email = Column(String(255))
    
    # Connection status and authentication
    status = Column(SQLEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.DISCONNECTED)
    auth_method = Column(String(50))  # oauth2, api_key, manual
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    token_expires_at = Column(DateTime(timezone=True))
    
    # API configuration
    api_version = Column(String(20))
    api_endpoint = Column(String(255))
    rate_limit_per_hour = Column(Integer)
    rate_limit_remaining = Column(Integer)
    rate_limit_reset_at = Column(DateTime(timezone=True))
    
    # Data synchronization settings
    sync_frequency = Column(SQLEnum(DataSyncFrequency), default=DataSyncFrequency.DAILY)
    last_sync_at = Column(DateTime(timezone=True))
    next_sync_at = Column(DateTime(timezone=True))
    sync_enabled = Column(Boolean, default=True)
    
    # Data types to sync
    sync_analytics = Column(Boolean, default=True)
    sync_revenue = Column(Boolean, default=True)
    sync_content = Column(Boolean, default=True)
    sync_audience = Column(Boolean, default=True)
    sync_engagement = Column(Boolean, default=True)
    
    # Platform-specific configuration
    platform_config = Column(JSONB)
    webhook_url = Column(String(255))
    webhook_secret = Column(String(255))  # Encrypted
    
    # Account verification and status
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    account_type = Column(String(50))  # personal, business, creator
    monetization_enabled = Column(Boolean, default=False)
    
    # Analytics and metrics access
    has_analytics_access = Column(Boolean, default=False)
    has_revenue_access = Column(Boolean, default=False)
    has_content_management = Column(Boolean, default=False)
    
    # Connection metadata
    connection_source = Column(String(100))  # web, mobile, api
    user_agent = Column(Text)
    ip_address = Column(String(45))
    
    # Error handling
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    max_retry_attempts = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=300)
    
    # Audit and compliance
    gdpr_consent = Column(Boolean, default=False)
    data_retention_days = Column(Integer, default=365)
    privacy_settings = Column(JSONB)
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True))
    disconnected_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sync_logs = relationship("PlatformSyncLog", back_populates="connection")
    analytics_data = relationship("PlatformAnalytics", back_populates="connection")
    revenue_data = relationship("PlatformRevenue", back_populates="connection")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform_connections_user", "user_id"),
        Index("idx_platform_connections_platform", "platform"),
        Index("idx_platform_connections_status", "status"),
        Index("idx_platform_connections_sync", "next_sync_at"),
        UniqueConstraint("user_id", "platform", "platform_user_id", 
                        name="uq_user_platform_account"),
    )


class PlatformSyncLog(Base):
    """Logging for platform data synchronization operations"""    __tablename__ = "platform_sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("platform_connections.id"), nullable=False)
    
    # Sync operation details
    sync_type = Column(String(50), nullable=False)  # full, incremental, manual
    sync_scope = Column(ARRAY(String))  # analytics, revenue, content, etc.
    
    # Execution details
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Results and statistics
    status = Column(String(20), nullable=False, default="running")  # running, completed, failed, partial
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # API usage
    api_calls_made = Column(Integer, default=0)
    api_quota_used = Column(Integer, default=0)
    rate_limit_hits = Column(Integer, default=0)
    
    # Data ranges
    data_start_date = Column(DateTime(timezone=True))
    data_end_date = Column(DateTime(timezone=True))
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSONB)
    warnings = Column(JSONB)
    
    # Sync metadata
    sync_metadata = Column(JSONB)
    trigger_source = Column(String(50))  # scheduled, manual, webhook, retry
    
    # Relationships
    connection = relationship("PlatformConnection", back_populates="sync_logs")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform_sync_logs_connection", "connection_id"),
        Index("idx_platform_sync_logs_date", "started_at"),
        Index("idx_platform_sync_logs_status", "status"),
        Index("idx_platform_sync_logs_type", "sync_type"),
    )


class PlatformAnalytics(Base):
    """Analytics data from various platforms"""    __tablename__ = "platform_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("platform_connections.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Analytics identification
    platform = Column(SQLEnum(Platform), nullable=False)
    metric_type = Column(String(100), nullable=False)
    content_id = Column(String(255))  # Platform-specific content ID
    content_title = Column(String(500))
    content_type = Column(String(50))  # video, audio, post, story, etc.
    
    # Time period
    date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Core metrics
    views = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    reactions = Column(Integer, default=0)
    
    # Time-based metrics
    watch_time_seconds = Column(Integer, default=0)
    average_view_duration = Column(Integer, default=0)
    completion_rate = Column(Numeric(5, 2))  # Percentage
    
    # Audience metrics
    subscriber_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    new_subscribers = Column(Integer, default=0)
    new_followers = Column(Integer, default=0)
    
    # Revenue metrics
    revenue_amount = Column(Numeric(12, 2), default=0)
    revenue_currency = Column(String(3), default="EUR")
    rpm = Column(Numeric(8, 2))  # Revenue per mille
    cpm = Column(Numeric(8, 2))  # Cost per mille
    
    # Demographic breakdown
    demographics = Column(JSONB)  # Age, gender, location breakdown
    traffic_sources = Column(JSONB)  # Where views/traffic came from
    device_breakdown = Column(JSONB)  # Mobile, desktop, tablet, etc.
    
    # Platform-specific metrics
    platform_specific_metrics = Column(JSONB)
    
    # Data quality and metadata
    data_freshness = Column(DateTime(timezone=True))
    is_estimated = Column(Boolean, default=False)
    confidence_level = Column(Numeric(4, 2))  # 0-100%
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    connection = relationship("PlatformConnection", back_populates="analytics_data")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform_analytics_connection", "connection_id"),
        Index("idx_platform_analytics_user", "user_id"),
        Index("idx_platform_analytics_platform", "platform"),
        Index("idx_platform_analytics_date", "date"),
        Index("idx_platform_analytics_content", "content_id"),
        Index("idx_platform_analytics_metric", "metric_type"),
        UniqueConstraint("connection_id", "content_id", "date", "metric_type",
                        name="uq_analytics_record"),
    )


class PlatformRevenue(Base):
    """Revenue data from various platforms"""    __tablename__ = "platform_revenue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("platform_connections.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Revenue identification
    platform = Column(SQLEnum(Platform), nullable=False)
    revenue_stream = Column(String(100), nullable=False)  # ads, subscriptions, tips, etc.
    content_id = Column(String(255))  # Platform-specific content ID
    content_title = Column(String(500))
    content_type = Column(String(50))
    
    # Time period
    date = Column(DateTime(timezone=True), nullable=False)
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # Revenue amounts
    gross_revenue = Column(Numeric(12, 2), nullable=False)
    platform_fee = Column(Numeric(10, 2), default=0)
    net_revenue = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Exchange rate handling
    original_currency = Column(String(3))
    exchange_rate = Column(Numeric(10, 6))
    exchange_date = Column(DateTime(timezone=True))
    
    # Performance metrics that drove revenue
    units_sold = Column(Integer)  # Downloads, streams, views, etc.
    average_price = Column(Numeric(8, 4))
    conversion_rate = Column(Numeric(5, 2))
    
    # Revenue source details
    advertiser_count = Column(Integer)
    subscriber_contribution = Column(Numeric(10, 2))
    fan_funding = Column(Numeric(10, 2))
    merchandise_sales = Column(Numeric(10, 2))
    
    # Tax and compliance
    tax_withheld = Column(Numeric(10, 2), default=0)
    tax_jurisdiction = Column(String(50))
    tax_id = Column(String(100))
    
    # Geographic breakdown
    revenue_by_country = Column(JSONB)
    top_countries = Column(ARRAY(String))
    
    # Revenue quality metrics
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    disputed_amount = Column(Numeric(10, 2), default=0)
    chargeback_amount = Column(Numeric(10, 2), default=0)
    
    # Platform-specific data
    platform_specific_data = Column(JSONB)
    
    # Payout information
    payout_scheduled = Column(Boolean, default=False)
    payout_date = Column(DateTime(timezone=True))
    payout_reference = Column(String(255))
    
    # Metadata
    data_source = Column(String(100))  # api, manual, estimated
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    connection = relationship("PlatformConnection", back_populates="revenue_data")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform_revenue_connection", "connection_id"),
        Index("idx_platform_revenue_user", "user_id"),
        Index("idx_platform_revenue_platform", "platform"),
        Index("idx_platform_revenue_date", "date"),
        Index("idx_platform_revenue_stream", "revenue_stream"),
        Index("idx_platform_revenue_payout", "payout_scheduled", "payout_date"),
        CheckConstraint("gross_revenue >= 0", name="chk_positive_gross_revenue"),
        CheckConstraint("net_revenue >= 0", name="chk_positive_net_revenue"),
    )


class PlatformContentMetadata(Base):
    """Content metadata from various platforms"""    __tablename__ = "platform_content_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("platform_connections.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content identification
    platform = Column(SQLEnum(Platform), nullable=False)
    content_id = Column(String(255), nullable=False)  # Platform-specific ID
    content_url = Column(Text)
    content_type = Column(String(50), nullable=False)
    
    # Content details
    title = Column(String(500))
    description = Column(Text)
    tags = Column(ARRAY(String))
    categories = Column(ARRAY(String))
    language = Column(String(10))
    
    # Media properties
    duration_seconds = Column(Integer)
    file_size_bytes = Column(Integer)
    resolution = Column(String(20))  # 1080p, 720p, etc.
    bitrate = Column(Integer)
    format = Column(String(20))  # mp4, mp3, jpg, etc.
    
    # Publishing information
    published_at = Column(DateTime(timezone=True))
    visibility = Column(String(20))  # public, private, unlisted
    monetization_enabled = Column(Boolean, default=False)
    copyright_status = Column(String(50))
    
    # Content protection
    has_fingerprint = Column(Boolean, default=False)
    fingerprint_id = Column(UUID(as_uuid=True), ForeignKey("content_fingerprints.id"))
    protection_status = Column(String(50))
    
    # Licensing and rights
    license_type = Column(String(100))
    rights_holder = Column(String(255))
    usage_rights = Column(JSONB)
    collaboration_data = Column(JSONB)
    
    # Performance summary
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0)
    
    # Platform-specific metadata
    platform_metadata = Column(JSONB)
    
    # Content status
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deletion_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime(timezone=True))
    
    # Relationships
    connection = relationship("PlatformConnection")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform_content_connection", "connection_id"),
        Index("idx_platform_content_user", "user_id"),
        Index("idx_platform_content_platform", "platform"),
        Index("idx_platform_content_id", "content_id"),
        Index("idx_platform_content_type", "content_type"),
        Index("idx_platform_content_published", "published_at"),
        UniqueConstraint("connection_id", "platform", "content_id",
                        name="uq_platform_content"),
    )


class PlatformWebhook(Base):
    """Webhook configurations for real-time platform updates"""    __tablename__ = "platform_webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("platform_connections.id"), nullable=False)
    
    # Webhook configuration
    webhook_url = Column(String(255), nullable=False)
    webhook_secret = Column(String(255))  # Encrypted
    platform_webhook_id = Column(String(255))  # Platform-assigned webhook ID
    
    # Event subscriptions
    subscribed_events = Column(ARRAY(String))
    event_filters = Column(JSONB)
    
    # Status and configuration
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    
    # Processing settings
    retry_attempts = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=30)
    timeout_seconds = Column(Integer, default=30)
    
    # Statistics
    total_events_received = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    last_event_at = Column(DateTime(timezone=True))
    
    # Error handling
    last_error = Column(Text)
    consecutive_failures = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    connection = relationship("PlatformConnection")
    webhook_events = relationship("WebhookEvent", back_populates="webhook")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform_webhooks_connection", "connection_id"),
        Index("idx_platform_webhooks_url", "webhook_url"),
        Index("idx_platform_webhooks_active", "is_active"),
    )


class WebhookEvent(Base):
    """Individual webhook events received from platforms"""    __tablename__ = "webhook_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("platform_webhooks.id"), nullable=False)
    
    # Event identification
    event_id = Column(String(255))  # Platform-provided event ID
    event_type = Column(String(100), nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Event data
    payload = Column(JSONB, nullable=False)
    headers = Column(JSONB)
    signature = Column(String(255))
    
    # Processing status
    processing_status = Column(String(20), default="pending")  # pending, processed, failed
    processed_at = Column(DateTime(timezone=True))
    processing_error = Column(Text)
    
    # Event metadata
    source_ip = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    webhook = relationship("PlatformWebhook", back_populates="webhook_events")
    
    # Indexes
    __table_args__ = (
        Index("idx_webhook_events_webhook", "webhook_id"),
        Index("idx_webhook_events_type", "event_type"),
        Index("idx_webhook_events_timestamp", "event_timestamp"),
        Index("idx_webhook_events_status", "processing_status"),
    )


# SQLAlchemy event listeners
@event.listens_for(PlatformConnection, 'before_update')
def platform_connection_before_update(mapper, connection, target):
    """Update connection status and sync schedule"""    if target.status == ConnectionStatus.CONNECTED and not target.connected_at:
        target.connected_at = datetime.now(timezone.utc)
    elif target.status == ConnectionStatus.DISCONNECTED:
        target.disconnected_at = datetime.now(timezone.utc)
    
    # Schedule next sync based on frequency
    if target.sync_enabled and target.sync_frequency:
        sync_intervals = {
            DataSyncFrequency.HOURLY: timedelta(hours=1),
            DataSyncFrequency.DAILY: timedelta(days=1),
            DataSyncFrequency.WEEKLY: timedelta(weeks=1),
            DataSyncFrequency.MONTHLY: timedelta(days=30)
        }
        
        interval = sync_intervals.get(target.sync_frequency)
        if interval:
            target.next_sync_at = datetime.now(timezone.utc) + interval


@event.listens_for(PlatformSyncLog, 'before_update')
def sync_log_before_update(mapper, connection, target):
    """Calculate duration and update statistics"""    if target.completed_at and target.started_at:
        target.duration_seconds = int((target.completed_at - target.started_at).total_seconds())


# Export all models
__all__ = [
    'Platform', 'ConnectionStatus', 'DataSyncFrequency',
    'PlatformConnection', 'PlatformSyncLog', 'PlatformAnalytics',
    'PlatformRevenue', 'PlatformContentMetadata', 'PlatformWebhook',
    'WebhookEvent'
]
