"""Platform Integrations Database Model

Enterprise-grade SQLAlchemy model for managing platform integrations, API connections,
and cross-platform synchronization for content distribution and monetization.

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
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class PlatformType(Enum):
    """Platform type enumeration"""
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    SOCIAL_MEDIA = "social_media"
    PODCAST_PLATFORM = "podcast_platform"
    DISTRIBUTION_SERVICE = "distribution_service"
    LICENSING_AGENCY = "licensing_agency"
    PERFORMANCE_SOCIETY = "performance_society"
    ANALYTICS_SERVICE = "analytics_service"
    PAYMENT_PROCESSOR = "payment_processor"
    CONTENT_DELIVERY = "content_delivery"
    COLLABORATION_TOOL = "collaboration_tool"
    MARKETING_PLATFORM = "marketing_platform"
    NFT_MARKETPLACE = "nft_marketplace"
    BLOCKCHAIN_SERVICE = "blockchain_service"


class Platform(Enum):
    """Supported platforms"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    DISTROKID = "distrokid"
    CD_BABY = "cd_baby"
    TUNECORE = "tunecore"
    LANDR = "landr"
    ASCAP = "ascap"
    BMI = "bmi"
    SESAC = "sesac"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    OPENSEA = "opensea"
    RARIBLE = "rarible"
    FOUNDATION = "foundation"
    ASYNC_ART = "async_art"
    OTHER = "other"


class IntegrationStatus(Enum):
    """Integration status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    DEPRECATED = "deprecated"


class AuthType(Enum):
    """Authentication type enumeration"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    WEBHOOK = "webhook"
    SSL_CERT = "ssl_cert"
    CUSTOM = "custom"


class SyncStatus(Enum):
    """Synchronization status"""
    SYNCED = "synced"
    PENDING = "pending"
    FAILED = "failed"
    PARTIAL = "partial"
    CONFLICT = "conflict"
    OUTDATED = "outdated"
    DISABLED = "disabled"


class PermissionLevel(Enum):
    """Permission levels for platform access"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"
    ADMIN = "admin"
    LIMITED = "limited"
    CUSTOM = "custom"


class PlatformIntegration(Base):
    """
    Enterprise Platform Integration Model
    
    Comprehensive platform integration management for content distribution,
    analytics synchronization, and revenue tracking across multiple platforms.
    """
    __tablename__ = "platform_integrations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Platform identification
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    platform_type = Column(SQLEnum(PlatformType), nullable=False, index=True)
    platform_name = Column(String(255), nullable=False)
    platform_url = Column(String(500), nullable=True)
    platform_version = Column(String(50), nullable=True)
    
    # Integration configuration
    integration_status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING, index=True)
    auth_type = Column(SQLEnum(AuthType), nullable=False)
    permission_level = Column(SQLEnum(PermissionLevel), default=PermissionLevel.READ_WRITE)
    
    # Authentication credentials (encrypted)
    access_token = Column(Text, nullable=True)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    api_key = Column(Text, nullable=True)  # Encrypted
    client_id = Column(String(255), nullable=True)
    client_secret = Column(Text, nullable=True)  # Encrypted
    webhook_secret = Column(Text, nullable=True)  # Encrypted
    
    # Platform-specific user identification
    platform_user_id = Column(String(255), nullable=True, index=True)
    platform_username = Column(String(255), nullable=True)
    platform_email = Column(String(255), nullable=True)
    platform_profile_url = Column(String(500), nullable=True)
    
    # Account and profile information
    account_type = Column(String(100), nullable=True)  # artist, creator, business, etc.
    account_tier = Column(String(100), nullable=True)  # free, premium, pro, etc.
    verification_status = Column(String(50), nullable=True)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    profile_metadata = Column(JSON, nullable=True)
    
    # API configuration
    api_endpoint = Column(String(500), nullable=True)
    api_version = Column(String(20), nullable=True)
    rate_limit = Column(Integer, nullable=True)  # Requests per hour
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset = Column(DateTime(timezone=True), nullable=True)
    
    # Synchronization settings
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)
    auto_sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(50), default="hourly")  # hourly, daily, weekly
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    next_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_retry_count = Column(Integer, default=0)
    max_retry_attempts = Column(Integer, default=3)
    
    # Data synchronization scope
    sync_content = Column(Boolean, default=True)
    sync_analytics = Column(Boolean, default=True)
    sync_revenue = Column(Boolean, default=True)
    sync_audience = Column(Boolean, default=True)
    sync_metadata = Column(Boolean, default=True)
    sync_comments = Column(Boolean, default=False)
    sync_likes = Column(Boolean, default=True)
    
    # Content distribution settings
    auto_publish = Column(Boolean, default=False)
    auto_update = Column(Boolean, default=True)
    content_format_preferences = Column(JSON, nullable=True)
    distribution_settings = Column(JSON, nullable=True)
    monetization_settings = Column(JSON, nullable=True)
    
    # Platform capabilities and features
    supported_content_types = Column(ARRAY(String), nullable=True)
    supported_formats = Column(ARRAY(String), nullable=True)
    max_file_size = Column(Integer, nullable=True)  # Bytes
    max_duration = Column(Integer, nullable=True)  # Seconds
    quality_limits = Column(JSON, nullable=True)
    feature_availability = Column(JSON, nullable=True)
    
    # Analytics and revenue tracking
    analytics_enabled = Column(Boolean, default=True)
    revenue_tracking_enabled = Column(Boolean, default=True)
    copyright_protection_enabled = Column(Boolean, default=True)
    content_id_system_enabled = Column(Boolean, default=False)
    
    # Error handling and monitoring
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    error_history = Column(JSON, nullable=True)
    health_status = Column(String(50), default="healthy")
    monitoring_enabled = Column(Boolean, default=True)
    
    # Webhook configuration
    webhook_url = Column(String(500), nullable=True)
    webhook_events = Column(ARRAY(String), nullable=True)
    webhook_status = Column(String(50), nullable=True)
    webhook_last_received = Column(DateTime(timezone=True), nullable=True)
    
    # Platform-specific settings and metadata
    platform_settings = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    integration_metadata = Column(JSON, nullable=True)
    external_references = Column(JSON, nullable=True)
    
    # Performance metrics
    api_response_time = Column(Float, nullable=True)  # Average response time in seconds
    success_rate = Column(Float, default=1.0)  # Success rate percentage
    uptime_percentage = Column(Float, default=100.0)
    data_accuracy_score = Column(Float, default=1.0)
    
    # Token expiration and renewal
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    token_refresh_threshold = Column(Integer, default=86400)  # Seconds before expiry to refresh
    auto_token_refresh = Column(Boolean, default=True)
    token_refresh_failed_count = Column(Integer, default=0)
    
    # Compliance and security
    gdpr_compliant = Column(Boolean, default=True)
    data_retention_days = Column(Integer, default=365)
    encryption_enabled = Column(Boolean, default=True)
    security_level = Column(String(50), default="high")
    compliance_notes = Column(Text, nullable=True)
    
    # Usage statistics
    api_calls_made = Column(Integer, default=0)
    data_transferred = Column(Integer, default=0)  # Bytes
    content_synced_count = Column(Integer, default=0)
    revenue_events_processed = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    connected_at = Column(DateTime(timezone=True), nullable=True)
    disconnected_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary platform for this type
    is_verified = Column(Boolean, default=False)
    requires_reauthorization = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_platform_integrations_user_platform', 'user_id', 'platform'),
        Index('idx_platform_integrations_status_type', 'integration_status', 'platform_type'),
        Index('idx_platform_integrations_sync_status', 'sync_status', 'last_sync_at'),
        Index('idx_platform_integrations_auth_type', 'auth_type', 'permission_level'),
        Index('idx_platform_integrations_health', 'health_status', 'error_count'),
        Index('idx_platform_integrations_token_expiry', 'token_expires_at', 'auto_token_refresh'),
        Index('idx_platform_integrations_activity', 'last_activity_at', 'is_active'),
        Index('idx_platform_integrations_verification', 'is_verified', 'verification_status'),
        Index('idx_platform_integrations_primary', 'user_id', 'platform_type', 'is_primary'),
    )
    
    def __repr__(self):
        return f"<PlatformIntegration(id={self.id}, platform={self.platform.value}, user_id={self.user_id}, status={self.integration_status.value})>"
    
    def to_dict(self, include_credentials: bool = False, include_analytics: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        base_dict = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "platform": self.platform.value if self.platform else None,
            "platform_type": self.platform_type.value if self.platform_type else None,
            "platform_name": self.platform_name,
            "platform_url": self.platform_url,
            "platform_version": self.platform_version,
            "integration_status": self.integration_status.value if self.integration_status else None,
            "auth_type": self.auth_type.value if self.auth_type else None,
            "permission_level": self.permission_level.value if self.permission_level else None,
            "platform_user_id": self.platform_user_id,
            "platform_username": self.platform_username,
            "platform_profile_url": self.platform_profile_url,
            "account_type": self.account_type,
            "account_tier": self.account_tier,
            "verification_status": self.verification_status,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "profile_metadata": self.profile_metadata,
            "api_version": self.api_version,
            "rate_limit": self.rate_limit,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
            "sync_status": self.sync_status.value if self.sync_status else None,
            "auto_sync_enabled": self.auto_sync_enabled,
            "sync_frequency": self.sync_frequency,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "next_sync_at": self.next_sync_at.isoformat() if self.next_sync_at else None,
            "sync_retry_count": self.sync_retry_count,
            "sync_content": self.sync_content,
            "sync_analytics": self.sync_analytics,
            "sync_revenue": self.sync_revenue,
            "sync_audience": self.sync_audience,
            "auto_publish": self.auto_publish,
            "auto_update": self.auto_update,
            "content_format_preferences": self.content_format_preferences,
            "distribution_settings": self.distribution_settings,
            "monetization_settings": self.monetization_settings,
            "supported_content_types": self.supported_content_types,
            "supported_formats": self.supported_formats,
            "max_file_size": self.max_file_size,
            "max_duration": self.max_duration,
            "quality_limits": self.quality_limits,
            "feature_availability": self.feature_availability,
            "analytics_enabled": self.analytics_enabled,
            "revenue_tracking_enabled": self.revenue_tracking_enabled,
            "copyright_protection_enabled": self.copyright_protection_enabled,
            "content_id_system_enabled": self.content_id_system_enabled,
            "health_status": self.health_status,
            "monitoring_enabled": self.monitoring_enabled,
            "webhook_url": self.webhook_url,
            "webhook_events": self.webhook_events,
            "webhook_status": self.webhook_status,
            "webhook_last_received": self.webhook_last_received.isoformat() if self.webhook_last_received else None,
            "platform_settings": self.platform_settings,
            "custom_fields": self.custom_fields,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "auto_token_refresh": self.auto_token_refresh,
            "gdpr_compliant": self.gdpr_compliant,
            "data_retention_days": self.data_retention_days,
            "encryption_enabled": self.encryption_enabled,
            "security_level": self.security_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "is_primary": self.is_primary,
            "is_verified": self.is_verified,
            "requires_reauthorization": self.requires_reauthorization,
            "is_deprecated": self.is_deprecated
        }
        
        if include_credentials:
            # Only include in secure contexts
            base_dict.update({
                "client_id": self.client_id,
                "api_endpoint": self.api_endpoint
            })
        
        if include_analytics:
            base_dict.update({
                "api_response_time": self.api_response_time,
                "success_rate": self.success_rate,
                "uptime_percentage": self.uptime_percentage,
                "data_accuracy_score": self.data_accuracy_score,
                "api_calls_made": self.api_calls_made,
                "data_transferred": self.data_transferred,
                "content_synced_count": self.content_synced_count,
                "revenue_events_processed": self.revenue_events_processed,
                "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
                "error_count": self.error_count,
                "last_error": self.last_error
            })
        
        return base_dict
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return datetime.now(timezone.utc) >= self.token_expires_at
    
    def needs_token_refresh(self) -> bool:
        """Check if token needs refresh based on threshold"""
        if not self.token_expires_at or not self.auto_token_refresh:
            return False
        
        threshold_time = self.token_expires_at - timezone.utc.localize(
            datetime.fromtimestamp(self.token_refresh_threshold)
        )
        return datetime.now(timezone.utc) >= threshold_time
    
    def is_healthy(self) -> bool:
        """Check overall health status of integration"""
        return (
            self.integration_status == IntegrationStatus.ACTIVE and
            self.health_status == "healthy" and
            self.error_count < 5 and
            not self.is_token_expired() and
            self.success_rate >= 0.95
        )
    
    def get_sync_priority(self) -> int:
        """Calculate sync priority based on various factors"""
        priority = 5  # Base priority
        
        # Platform importance
        if self.is_primary:
            priority += 3
        
        # Revenue tracking importance
        if self.revenue_tracking_enabled:
            priority += 2
        
        # Error penalty
        priority -= min(self.error_count, 3)
        
        # Activity bonus
        if self.last_activity_at:
            hours_since_activity = (datetime.now(timezone.utc) - self.last_activity_at).total_seconds() / 3600
            if hours_since_activity < 24:
                priority += 1
        
        return max(priority, 1)  # Minimum priority of 1
    
    def should_retry_sync(self) -> bool:
        """Determine if sync should be retried"""
        return (
            self.sync_status in [SyncStatus.FAILED, SyncStatus.PARTIAL] and
            self.sync_retry_count < self.max_retry_attempts and
            self.integration_status == IntegrationStatus.ACTIVE
        )
    
    @classmethod
    def create_integration(cls, platform_data: Dict[str, Any], user_id: str) -> 'PlatformIntegration':
        """Create PlatformIntegration from platform connection data"""
        return cls(
            user_id=user_id,
            platform=Platform(platform_data.get('platform', 'other')),
            platform_type=PlatformType(platform_data.get('platform_type', 'music_streaming')),
            platform_name=platform_data.get('platform_name'),
            platform_url=platform_data.get('platform_url'),
            auth_type=AuthType(platform_data.get('auth_type', 'oauth2')),
            permission_level=PermissionLevel(platform_data.get('permission_level', 'read_write')),
            platform_user_id=platform_data.get('platform_user_id'),
            platform_username=platform_data.get('platform_username'),
            platform_email=platform_data.get('platform_email'),
            account_type=platform_data.get('account_type'),
            account_tier=platform_data.get('account_tier'),
            api_endpoint=platform_data.get('api_endpoint'),
            api_version=platform_data.get('api_version'),
            rate_limit=platform_data.get('rate_limit'),
            supported_content_types=platform_data.get('supported_content_types', []),
            supported_formats=platform_data.get('supported_formats', []),
            feature_availability=platform_data.get('feature_availability', {}),
            platform_settings=platform_data.get('platform_settings', {}),
            connected_at=datetime.now(timezone.utc)
        )
