"""Platform Integration Models
===========================

Advanced platform integration models for IA Influencer Agent platform.
Comprehensive multi-platform API connections with cross-platform synchronization,
data flow management, and scalable integration architecture.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• 35+ platform integrations (YouTube, Spotify, Instagram, TikTok, etc.)
• Cross-platform synchronization & management
• API connection monitoring & optimization
• Real-time data flow management
• Platform-specific feature utilization
• Integration performance analytics
• Automated conflict resolution
• Scalable integration architecture
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - Platform System
# ============================================================================

class Platform(Enum):
    """Supported platforms for integration (35+ platforms)"""
    # Video Platforms
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    FACEBOOK_VIDEO = "facebook_video"
    INSTAGRAM_TV = "instagram_tv"
    TIKTOK = "tiktok"
    SNAPCHAT = "snapchat"
    TWITTER_VIDEO = "twitter_video"
    
    # Music & Audio Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    TIDAL = "tidal"
    YOUTUBE_MUSIC = "youtube_music"
    PANDORA = "pandora"
    AUDIOMACK = "audiomack"
    
    # Social Media Platforms
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    
    # Podcast Platforms
    APPLE_PODCASTS = "apple_podcasts"
    SPOTIFY_PODCASTS = "spotify_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    ANCHOR = "anchor"
    STITCHER = "stitcher"
    POCKET_CASTS = "pocket_casts"
    OVERCAST = "overcast"
    
    # Professional & Content Platforms
    MEDIUM = "medium"
    SUBSTACK = "substack"
    WORDPRESS = "wordpress"
    WATTPAD = "wattpad"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    DEVIANTART = "deviantart"
    
    # Emerging & Specialized
    CLUBHOUSE = "clubhouse"
    SPACES = "spaces"
    MASTODON = "mastodon"
    RUMBLE = "rumble"
    ODYSEE = "odysee"
    PEERTUBE = "peertube"


class IntegrationType(Enum):
    """Types of platform integrations"""
    UPLOAD = "upload"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    SOCIAL = "social"
    MESSAGING = "messaging"
    LIVE_STREAMING = "live_streaming"
    COLLABORATION = "collaboration"
    COMMUNITY = "community"
    COMMERCE = "commerce"
    ADVERTISING = "advertising"
    DISCOVERY = "discovery"
    RECOMMENDATION = "recommendation"
    AUTOMATION = "automation"


class SyncStatus(Enum):
    """Cross-platform synchronization status"""
    SYNCED = "synced"
    PENDING = "pending"
    SYNCING = "syncing"
    FAILED = "failed"
    CONFLICT = "conflict"
    PARTIAL = "partial"
    MANUAL_REQUIRED = "manual_required"
    DISABLED = "disabled"
    ERROR = "error"
    TIMEOUT = "timeout"


class APIStatus(Enum):
    """API connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTHENTICATING = "authenticating"
    EXPIRED = "expired"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    UPGRADING = "upgrading"


class DataFlow(Enum):
    """Direction of data flow"""
    INBOUND = "inbound"       # Data coming into our platform
    OUTBOUND = "outbound"     # Data going to external platform
    BIDIRECTIONAL = "bidirectional"  # Two-way data sync
    WEBHOOK = "webhook"       # Event-driven updates
    BATCH = "batch"          # Scheduled batch transfers
    REAL_TIME = "real_time"   # Real-time streaming
    ON_DEMAND = "on_demand"   # User-triggered sync


class IntegrationLevel(Enum):
    """Level of integration depth"""
    BASIC = "basic"           # Basic API access
    STANDARD = "standard"     # Standard features
    PREMIUM = "premium"       # Premium features
    ENTERPRISE = "enterprise" # Full enterprise features
    CUSTOM = "custom"         # Custom integration
    BETA = "beta"            # Beta features
    EXPERIMENTAL = "experimental"  # Experimental features


# ============================================================================
# PLATFORM CONNECTION MODELS
# ============================================================================

class PlatformConnectionModel(Base):
    """
    Platform connection model for managing API connections to external platforms.
    Comprehensive connection management with authentication and monitoring.
    """
    __tablename__ = 'platform_connections'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Platform details
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False, index=True)
    integration_level = Column(SQLEnum(IntegrationLevel), nullable=False, default=IntegrationLevel.STANDARD)
    api_status = Column(SQLEnum(APIStatus), nullable=False, default=APIStatus.DISCONNECTED, index=True)
    
    # Connection configuration
    connection_name = Column(String(300), nullable=False)
    platform_user_id = Column(String(200))  # User ID on the platform
    platform_username = Column(String(200))  # Username on the platform
    platform_display_name = Column(String(300))  # Display name on platform
    platform_profile_url = Column(String(1000))
    
    # Authentication details
    auth_type = Column(String(50), nullable=False)  # "oauth2", "api_key", "jwt", "basic"
    access_token_id = Column(String(200))  # Reference to encrypted token storage
    refresh_token_id = Column(String(200))  # Reference to encrypted refresh token
    token_expires_at = Column(DateTime(timezone=True))
    scope_permissions = Column(JSONB, default=list)  # Granted permissions
    
    # API configuration
    api_endpoint_base = Column(String(500))
    api_version = Column(String(20))
    rate_limit_per_hour = Column(Integer)
    rate_limit_per_day = Column(Integer)
    concurrent_request_limit = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=30)
    
    # Feature capabilities
    upload_supported = Column(Boolean, default=False)
    download_supported = Column(Boolean, default=False)
    analytics_supported = Column(Boolean, default=False)
    monetization_supported = Column(Boolean, default=False)
    live_streaming_supported = Column(Boolean, default=False)
    scheduling_supported = Column(Boolean, default=False)
    
    # Data flow configuration
    data_flow = Column(SQLEnum(DataFlow), nullable=False, default=DataFlow.BIDIRECTIONAL)
    sync_frequency = Column(String(50), default="hourly")  # "real_time", "hourly", "daily"
    auto_sync_enabled = Column(Boolean, default=True)
    sync_content_types = Column(JSONB, default=list)  # Types of content to sync
    
    # Performance tracking
    total_api_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    failed_calls = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)  # milliseconds
    last_successful_call = Column(DateTime(timezone=True))
    last_failed_call = Column(DateTime(timezone=True))
    
    # Rate limiting & Usage
    calls_this_hour = Column(Integer, default=0)
    calls_this_day = Column(Integer, default=0)
    rate_limit_reset_time = Column(DateTime(timezone=True))
    quota_usage_percentage = Column(Float, default=0.0)
    cost_per_call = Column(Float, default=0.0)
    total_api_cost = Column(Float, default=0.0)
    
    # Error handling
    error_count = Column(Integer, default=0)
    last_error_message = Column(Text)
    last_error_code = Column(String(50))
    error_pattern = Column(String(200))  # Common error pattern
    retry_strategy = Column(String(100), default="exponential_backoff")
    max_retries = Column(Integer, default=3)
    
    # Health monitoring
    health_score = Column(Float, default=100.0)  # 0-100 health rating
    uptime_percentage = Column(Float, default=100.0)
    last_health_check = Column(DateTime(timezone=True))
    health_check_interval = Column(Integer, default=300)  # seconds
    alert_thresholds = Column(JSONB, default=dict)
    
    # Platform-specific settings
    platform_settings = Column(JSONB, default=dict)  # Platform-specific configuration
    webhook_urls = Column(JSONB, default=list)  # Webhook endpoints
    callback_urls = Column(JSONB, default=list)  # OAuth callback URLs
    api_key_rotation_days = Column(Integer, default=90)
    
    # Business metrics
    content_uploaded = Column(Integer, default=0)
    content_downloaded = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    followers_gained = Column(Integer, default=0)
    engagement_generated = Column(Integer, default=0)
    
    # Compliance & Security
    gdpr_compliant = Column(Boolean, default=True)
    data_retention_days = Column(Integer, default=90)
    encryption_enabled = Column(Boolean, default=True)
    audit_logging = Column(Boolean, default=True)
    security_scan_passed = Column(Boolean, default=True)
    
    # Integration metadata
    integration_version = Column(String(20), default="1.0")
    sdk_version = Column(String(50))
    last_updated_by_platform = Column(DateTime(timezone=True))
    platform_api_changes = Column(JSONB, default=list)
    migration_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    connected_at = Column(DateTime(timezone=True))
    last_sync_at = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_primary = Column(Boolean, default=False)  # Primary connection for this platform
    is_test_connection = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="platform_connections")
    integration_configs = relationship("IntegrationConfigModel", back_populates="platform_connection", cascade="all, delete-orphan")
    sync_records = relationship("SyncStatusModel", back_populates="platform_connection", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_platform_user_platform', 'user_id', 'platform'),
        Index('idx_platform_status_active', 'api_status', 'is_active'),
        Index('idx_platform_type_level', 'integration_type', 'integration_level'),
        Index('idx_platform_health_sync', 'health_score', 'last_sync_at'),
    )
    
    def __repr__(self) -> None:
        return f"<PlatformConnectionModel(id={self.id}, platform={self.platform.value}, status={self.api_status.value})>"


# ============================================================================
# INTEGRATION CONFIGURATION MODELS
# ============================================================================

class IntegrationConfigModel(Base):
    """
    Integration configuration model for detailed platform-specific settings.
    Comprehensive configuration management with feature toggles and customization.
    """
    __tablename__ = 'integration_configs'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), ForeignKey('platform_connections.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Configuration details
    config_name = Column(String(300), nullable=False)
    config_type = Column(String(100), nullable=False)  # "upload", "analytics", "monetization"
    config_version = Column(String(20), default="1.0")
    is_default_config = Column(Boolean, default=False)
    
    # Upload configuration
    upload_quality = Column(String(50))  # "high", "medium", "low", "original"
    upload_format = Column(String(50))   # Preferred upload format
    upload_privacy = Column(String(50), default="public")  # "public", "private", "unlisted"
    upload_scheduling = Column(Boolean, default=False)
    upload_optimization = Column(Boolean, default=True)
    
    # Content transformation
    auto_resize = Column(Boolean, default=True)
    auto_compress = Column(Boolean, default=True)
    watermark_enabled = Column(Boolean, default=False)
    watermark_settings = Column(JSONB, default=dict)
    thumbnail_generation = Column(Boolean, default=True)
    thumbnail_settings = Column(JSONB, default=dict)
    
    # Metadata configuration
    auto_generate_titles = Column(Boolean, default=False)
    auto_generate_descriptions = Column(Boolean, default=False)
    auto_generate_tags = Column(Boolean, default=True)
    seo_optimization = Column(Boolean, default=True)
    hashtag_generation = Column(Boolean, default=True)
    
    # Analytics configuration
    analytics_enabled = Column(Boolean, default=True)
    analytics_frequency = Column(String(50), default="daily")
    analytics_metrics = Column(JSONB, default=list)  # Metrics to track
    analytics_retention_days = Column(Integer, default=365)
    real_time_analytics = Column(Boolean, default=False)
    
    # Monetization settings
    monetization_enabled = Column(Boolean, default=False)
    revenue_sharing = Column(Boolean, default=True)
    ad_placement = Column(JSONB, default=dict)
    sponsorship_enabled = Column(Boolean, default=False)
    merchandise_integration = Column(Boolean, default=False)
    
    # Audience & Targeting
    target_demographics = Column(JSONB, default=dict)
    geographic_targeting = Column(JSONB, default=list)
    language_preferences = Column(JSONB, default=list)
    audience_restrictions = Column(JSONB, default=dict)
    content_rating = Column(String(50), default="general")
    
    # Posting & Scheduling
    optimal_posting_times = Column(JSONB, default=dict)
    posting_frequency = Column(String(50))
    batch_posting_enabled = Column(Boolean, default=False)
    cross_posting_rules = Column(JSONB, default=dict)
    posting_templates = Column(JSONB, default=list)
    
    # Engagement features
    auto_respond_enabled = Column(Boolean, default=False)
    auto_respond_rules = Column(JSONB, default=list)
    comment_moderation = Column(String(50), default="manual")
    community_guidelines = Column(JSONB, default=dict)
    fan_engagement_tools = Column(JSONB, default=list)
    
    # Platform-specific features
    platform_features = Column(JSONB, default=dict)  # Platform-specific settings
    feature_flags = Column(JSONB, default=dict)      # Feature toggles
    experimental_features = Column(JSONB, default=list)
    beta_features_enabled = Column(Boolean, default=False)
    
    # Notification settings
    notification_preferences = Column(JSONB, default=dict)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    webhook_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(50), default="immediate")
    
    # Performance optimization
    caching_enabled = Column(Boolean, default=True)
    cache_duration_minutes = Column(Integer, default=60)
    compression_level = Column(String(50), default="standard")
    cdn_enabled = Column(Boolean, default=True)
    load_balancing = Column(Boolean, default=False)
    
    # Quality assurance
    content_validation = Column(Boolean, default=True)
    quality_checks = Column(JSONB, default=list)
    approval_workflow = Column(Boolean, default=False)
    review_required = Column(Boolean, default=False)
    compliance_checks = Column(JSONB, default=list)
    
    # Backup & Recovery
    backup_enabled = Column(Boolean, default=True)
    backup_frequency = Column(String(50), default="daily")
    backup_retention_days = Column(Integer, default=30)
    disaster_recovery = Column(Boolean, default=False)
    failover_enabled = Column(Boolean, default=False)
    
    # Custom scripting & Automation
    custom_scripts = Column(JSONB, default=list)
    automation_rules = Column(JSONB, default=list)
    workflow_triggers = Column(JSONB, default=list)
    integration_hooks = Column(JSONB, default=list)
    api_extensions = Column(JSONB, default=list)
    
    # Testing & Validation
    test_mode_enabled = Column(Boolean, default=False)
    sandbox_environment = Column(Boolean, default=False)
    validation_rules = Column(JSONB, default=list)
    testing_frequency = Column(String(50), default="weekly")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_validated = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    platform_connection = relationship("PlatformConnectionModel", back_populates="integration_configs")
    user = relationship("UserModel", backref="integration_configs")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_config_connection_type', 'platform_connection_id', 'config_type'),
        Index('idx_config_user_active', 'user_id', 'is_active'),
        Index('idx_config_default_template', 'is_default_config', 'is_template'),
    )
    
    def __repr__(self) -> None:
        return f"<IntegrationConfigModel(id={self.id}, name='{self.config_name}', type={self.config_type})>"


# ============================================================================
# SYNC STATUS MODELS
# ============================================================================

class SyncStatusModel(Base):
    """
    Synchronization status model for tracking cross-platform data sync.
    Comprehensive sync monitoring with conflict resolution and analytics.
    """
    __tablename__ = 'sync_status'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), ForeignKey('platform_connections.id'), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Sync details
    sync_status = Column(SQLEnum(SyncStatus), nullable=False, default=SyncStatus.PENDING, index=True)
    sync_type = Column(String(100), nullable=False)  # "upload", "update", "delete", "analytics"
    sync_direction = Column(SQLEnum(DataFlow), nullable=False)
    sync_method = Column(String(100))  # "api", "webhook", "batch", "manual"
    
    # Content synchronization
    local_content_id = Column(String(200))     # Our platform content ID
    platform_content_id = Column(String(200)) # External platform content ID
    content_type = Column(String(100))         # Type of content being synced
    content_hash = Column(String(200))         # Content hash for integrity
    
    # Sync operation details
    operation_type = Column(String(100))       # "create", "update", "delete", "sync"
    batch_id = Column(String(200))            # Batch operation ID
    parent_sync_id = Column(UUID(as_uuid=True), ForeignKey('sync_status.id'))  # Parent sync operation
    dependency_sync_ids = Column(JSONB, default=list)  # Dependencies
    
    # Progress tracking
    total_items = Column(Integer, default=1)
    completed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    current_step = Column(String(200))
    estimated_completion_time = Column(DateTime(timezone=True))
    
    # Data integrity
    source_checksum = Column(String(200))      # Source data checksum
    destination_checksum = Column(String(200)) # Destination data checksum
    data_size_bytes = Column(Integer)
    compression_applied = Column(Boolean, default=False)
    encryption_applied = Column(Boolean, default=False)
    
    # Performance metrics
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    transfer_rate_mbps = Column(Float)
    api_calls_made = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    
    # Error handling
    error_count = Column(Integer, default=0)
    error_messages = Column(JSONB, default=list)
    error_codes = Column(JSONB, default=list)
    last_error_timestamp = Column(DateTime(timezone=True))
    resolution_attempts = Column(Integer, default=0)
    
    # Conflict resolution
    conflicts_detected = Column(Integer, default=0)
    conflict_details = Column(JSONB, default=list)
    conflict_resolution_strategy = Column(String(100))
    manual_resolution_required = Column(Boolean, default=False)
    conflict_resolution_notes = Column(Text)
    
    # Sync metadata
    metadata_synced = Column(JSONB, default=dict)  # What metadata was synced
    tags_synced = Column(JSONB, default=list)
    analytics_synced = Column(Boolean, default=False)
    comments_synced = Column(Boolean, default=False)
    engagement_synced = Column(Boolean, default=False)
    
    # Platform response
    platform_response = Column(JSONB)          # Raw platform response
    platform_status_code = Column(Integer)
    platform_message = Column(Text)
    platform_warnings = Column(JSONB, default=list)
    rate_limit_hit = Column(Boolean, default=False)
    
    # Quality assurance
    validation_passed = Column(Boolean, default=True)
    quality_score = Column(Float, default=1.0)  # 0-1 quality rating
    data_loss_detected = Column(Boolean, default=False)
    integrity_verified = Column(Boolean, default=False)
    
    # Business impact
    revenue_impact = Column(Float, default=0.0)
    engagement_impact = Column(Float, default=0.0)
    audience_reach_impact = Column(Integer, default=0)
    seo_impact = Column(Float, default=0.0)
    brand_impact = Column(Float, default=0.0)
    
    # Automation features
    auto_retry_enabled = Column(Boolean, default=True)
    auto_rollback_enabled = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    escalation_triggered = Column(Boolean, default=False)
    
    # Analytics & Insights
    sync_analytics = Column(JSONB, default=dict)
    performance_insights = Column(JSONB, default=list)
    optimization_suggestions = Column(JSONB, default=list)
    cost_analysis = Column(JSONB, default=dict)
    
    # Compliance & Audit
    audit_trail = Column(JSONB, default=list)
    compliance_checked = Column(Boolean, default=True)
    gdpr_compliant = Column(Boolean, default=True)
    data_retention_applied = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    scheduled_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True))
    
    # System flags
    is_priority = Column(Boolean, default=False)
    is_manual_sync = Column(Boolean, default=False)
    is_test_sync = Column(Boolean, default=False)
    is_rollback = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    platform_connection = relationship("PlatformConnectionModel", back_populates="sync_records")
    content = relationship("ContentModel", backref="sync_records")
    user = relationship("UserModel", backref="sync_records")
    parent_sync = relationship("SyncStatusModel", remote_side=[id], backref="child_syncs")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_sync_connection_status', 'platform_connection_id', 'sync_status'),
        Index('idx_sync_content_type', 'content_id', 'sync_type'),
        Index('idx_sync_user_created', 'user_id', 'created_at'),
        Index('idx_sync_batch_operation', 'batch_id', 'operation_type'),
        Index('idx_sync_scheduled_priority', 'scheduled_at', 'is_priority'),
    )
    
    def __repr__(self) -> None:
        return f"<SyncStatusModel(id={self.id}, status={self.sync_status.value}, type={self.sync_type})>"


# ============================================================================
# API ENDPOINT MODELS
# ============================================================================

class APIEndpointModel(Base):
    """
    API endpoint model for managing external platform endpoints.
    Comprehensive endpoint monitoring with performance tracking.
    """
    __tablename__ = 'api_endpoints'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_connection_id = Column(UUID(as_uuid=True), ForeignKey('platform_connections.id'), nullable=False, index=True)
    
    # Endpoint details
    endpoint_name = Column(String(300), nullable=False)
    endpoint_url = Column(String(1000), nullable=False)
    http_method = Column(String(20), nullable=False)  # GET, POST, PUT, DELETE, etc.
    endpoint_type = Column(String(100))  # "upload", "analytics", "user_info", etc.
    api_version = Column(String(50))
    
    # Authentication requirements
    auth_required = Column(Boolean, default=True)
    auth_type = Column(String(50))  # "bearer", "oauth2", "api_key"
    required_scopes = Column(JSONB, default=list)
    permission_level = Column(String(50))  # "read", "write", "admin"
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer)
    rate_limit_per_hour = Column(Integer)
    rate_limit_per_day = Column(Integer)
    burst_limit = Column(Integer)
    rate_limit_window = Column(String(50))
    
    # Request/Response format
    request_format = Column(String(50))    # "json", "form-data", "xml"
    response_format = Column(String(50))   # "json", "xml", "csv"
    content_type = Column(String(100))
    accept_header = Column(String(100))
    
    # Performance metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)  # milliseconds
    fastest_response_time = Column(Float, default=0.0)
    slowest_response_time = Column(Float, default=0.0)
    
    # Reliability metrics
    uptime_percentage = Column(Float, default=100.0)
    error_rate = Column(Float, default=0.0)
    timeout_rate = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    reliability_score = Column(Float, default=100.0)
    
    # Response analysis
    common_response_codes = Column(JSONB, default=dict)
    error_patterns = Column(JSONB, default=list)
    response_size_stats = Column(JSONB, default=dict)
    header_analysis = Column(JSONB, default=dict)
    
    # Monitoring configuration
    monitoring_enabled = Column(Boolean, default=True)
    health_check_interval = Column(Integer, default=300)  # seconds
    timeout_threshold = Column(Integer, default=30)  # seconds
    retry_attempts = Column(Integer, default=3)
    circuit_breaker_enabled = Column(Boolean, default=True)
    
    # Documentation & Support
    documentation_url = Column(String(1000))
    support_contact = Column(String(300))
    changelog_url = Column(String(1000))
    status_page_url = Column(String(1000))
    deprecation_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True))
    last_health_check = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_deprecated = Column(Boolean, default=False)
    is_beta = Column(Boolean, default=False)
    is_critical = Column(Boolean, default=False)  # Critical for platform functionality
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    platform_connection = relationship("PlatformConnectionModel", backref="api_endpoints")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_endpoint_connection_type', 'platform_connection_id', 'endpoint_type'),
        Index('idx_endpoint_active_critical', 'is_active', 'is_critical'),
        Index('idx_endpoint_method_url', 'http_method', 'endpoint_url'),
    )
    
    def __repr__(self) -> None:
        return f"<APIEndpointModel(id={self.id}, name='{self.endpoint_name}', method={self.http_method})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_platform_connection_example(user_id: str, platform: Platform = Platform.YOUTUBE) -> PlatformConnectionModel:
    """Create example platform connection for testing and development"""
    return PlatformConnectionModel(
        user_id=user_id,
        platform=platform,
        integration_type=IntegrationType.UPLOAD,
        connection_name=f"Sample {platform.value.title()} Connection",
        auth_type="oauth2",
        scope_permissions=["upload", "analytics"],
        rate_limit_per_hour=1000,
        upload_supported=True,
        analytics_supported=True
    )


def create_integration_config_example(platform_connection_id: str, user_id: str) -> IntegrationConfigModel:
    """Create example integration config for testing and development"""
    return IntegrationConfigModel(
        platform_connection_id=platform_connection_id,
        user_id=user_id,
        config_name="Default Upload Configuration",
        config_type="upload",
        upload_quality="high",
        upload_privacy="public",
        auto_generate_tags=True,
        seo_optimization=True,
        analytics_enabled=True
    )


def calculate_sync_priority(content_importance: int, platform_priority: int, 
                          user_tier: str = "standard") -> int:
    """Calculate sync priority based on multiple factors"""
    # Base priority from content importance (1-10) and platform priority (1-10)
    base_priority = (content_importance + platform_priority) // 2
    
    # User tier multiplier
    tier_multipliers = {
        "free": 0.5,
        "basic": 0.7,
        "standard": 1.0,
        "premium": 1.5,
        "enterprise": 2.0
    }
    
    multiplier = tier_multipliers.get(user_tier, 1.0)
    final_priority = min(10, int(base_priority * multiplier))
    
    return final_priority


def estimate_sync_duration(content_size_mb: float, platform: Platform, 
                         connection_speed: str = "standard") -> float:
    """Estimate sync duration in seconds"""
    # Base upload speeds by platform (MB/s)
    platform_speeds = {
        Platform.YOUTUBE: 2.0,
        Platform.INSTAGRAM: 1.5,
        Platform.TIKTOK: 1.8,
        Platform.SPOTIFY: 1.0,
        Platform.TWITTER: 1.2,
    }
    
    # Connection speed multipliers
    speed_multipliers = {
        "slow": 0.5,
        "standard": 1.0,
        "fast": 2.0,
        "enterprise": 3.0
    }
    
    base_speed = platform_speeds.get(platform, 1.0)  # Default 1 MB/s
    speed_multiplier = speed_multipliers.get(connection_speed, 1.0)
    effective_speed = base_speed * speed_multiplier
    
    # Add processing overhead (20% of transfer time)
    transfer_time = content_size_mb / effective_speed
    processing_overhead = transfer_time * 0.2
    
    return transfer_time + processing_overhead


def generate_sync_batch_id() -> str:
    """Generate unique batch ID for sync operations"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"batch_{timestamp}_{unique_id}"


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'PlatformConnectionModel', 'IntegrationConfigModel', 'SyncStatusModel', 'APIEndpointModel',
    
    # Platform Enums
    'Platform', 'IntegrationType', 'SyncStatus', 'APIStatus', 'DataFlow', 'IntegrationLevel',
    
    # Utility Functions
    'create_platform_connection_example', 'create_integration_config_example',
    'calculate_sync_priority', 'estimate_sync_duration', 'generate_sync_batch_id'
]