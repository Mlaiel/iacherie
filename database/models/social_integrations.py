"""Social Integrations Database Model

Enterprise-grade SQLAlchemy model for managing social media platform integrations,
API connections, authentication tokens, and cross-platform synchronization.

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
"""from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class Platform(Enum):
    """Social media platform enumeration"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    TUMBLR = "tumblr"
    VIMEO = "vimeo"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    PODCAST_ADDICT = "podcast_addict"
    ANCHOR = "anchor"


class IntegrationType(Enum):
    """Integration type enumeration"""    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    WEBHOOK = "webhook"
    RSS_FEED = "rss_feed"
    WEB_SCRAPING = "web_scraping"
    NATIVE_SDK = "native_sdk"
    THIRD_PARTY_SERVICE = "third_party_service"
    CUSTOM_INTEGRATION = "custom_integration"


class ConnectionStatus(Enum):
    """Connection status enumeration"""    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    REFRESHING = "refreshing"


class PermissionLevel(Enum):
    """Permission level enumeration"""    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"
    LIMITED = "limited"
    ANALYTICS_ONLY = "analytics_only"
    POSTING_ONLY = "posting_only"
    ADMIN = "admin"


class SyncStatus(Enum):
    """Synchronization status"""    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    SYNC_ERROR = "sync_error"
    NEVER_SYNCED = "never_synced"
    PARTIAL_SYNC = "partial_sync"


class SocialIntegration(Base):
    """    Enterprise Social Integration Model
    
    Comprehensive social media platform integration management with secure
    token handling, API rate limiting, and cross-platform synchronization.
    """    __tablename__ = 'social_integrations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # References
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_profile_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=True, index=True)
    
    # Platform information
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False, index=True)
    connection_status = Column(SQLEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.PENDING, index=True)
    permission_level = Column(SQLEnum(PermissionLevel), nullable=False, default=PermissionLevel.READ_ONLY, index=True)
    
    # Account information
    platform_user_id = Column(String(200), nullable=True, index=True)
    platform_username = Column(String(200), nullable=True, index=True)
    platform_display_name = Column(String(200), nullable=True)
    platform_email = Column(String(200), nullable=True)
    platform_url = Column(Text, nullable=True)
    verified_account = Column(Boolean, nullable=False, default=False)
    
    # Authentication credentials (encrypted)
    access_token = Column(Text, nullable=True)  # Should be encrypted
    refresh_token = Column(Text, nullable=True)  # Should be encrypted
    api_key = Column(String(500), nullable=True)  # Should be encrypted
    api_secret = Column(String(500), nullable=True)  # Should be encrypted
    webhook_secret = Column(String(200), nullable=True)  # Should be encrypted
    
    # Token management
    token_expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_token_refresh = Column(DateTime(timezone=True), nullable=True)
    auto_refresh_enabled = Column(Boolean, nullable=False, default=True)
    
    # API configuration
    api_version = Column(String(20), nullable=True)
    api_endpoint = Column(String(500), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    callback_url = Column(String(500), nullable=True)
    scopes = Column(ARRAY(String), nullable=True)
    permissions = Column(JSONB, nullable=True)
    
    # Rate limiting
    rate_limit_per_hour = Column(Integer, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset_at = Column(DateTime(timezone=True), nullable=True)
    last_api_call = Column(DateTime(timezone=True), nullable=True)
    api_calls_today = Column(Integer, nullable=False, default=0)
    
    # Synchronization settings
    sync_status = Column(SQLEnum(SyncStatus), nullable=False, default=SyncStatus.NEVER_SYNCED, index=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True, index=True)
    sync_frequency = Column(String(50), nullable=False, default="hourly")  # hourly, daily, weekly, manual
    auto_sync_enabled = Column(Boolean, nullable=False, default=True)
    sync_content = Column(Boolean, nullable=False, default=True)
    sync_analytics = Column(Boolean, nullable=False, default=True)
    sync_comments = Column(Boolean, nullable=False, default=False)
    
    # Data synchronization
    sync_configuration = Column(JSONB, nullable=True)
    last_sync_data = Column(JSONB, nullable=True)
    sync_errors = Column(JSONB, nullable=True)
    sync_conflicts = Column(JSONB, nullable=True)
    data_mapping = Column(JSONB, nullable=True)
    
    # Feature flags
    posting_enabled = Column(Boolean, nullable=False, default=False)
    analytics_enabled = Column(Boolean, nullable=False, default=True)
    monitoring_enabled = Column(Boolean, nullable=False, default=True)
    auto_posting_enabled = Column(Boolean, nullable=False, default=False)
    cross_posting_enabled = Column(Boolean, nullable=False, default=False)
    
    # Platform-specific settings
    platform_settings = Column(JSONB, nullable=True)
    content_preferences = Column(JSONB, nullable=True)
    posting_schedule = Column(JSONB, nullable=True)
    hashtag_preferences = Column(JSONB, nullable=True)
    audience_targeting = Column(JSONB, nullable=True)
    
    # Analytics tracking
    total_api_calls = Column(Integer, nullable=False, default=0)
    successful_calls = Column(Integer, nullable=False, default=0)
    failed_calls = Column(Integer, nullable=False, default=0)
    average_response_time = Column(Float, nullable=True)
    uptime_percentage = Column(Float, nullable=False, default=100.0)
    
    # Content tracking
    content_posted = Column(Integer, nullable=False, default=0)
    content_synced = Column(Integer, nullable=False, default=0)
    engagement_tracked = Column(Integer, nullable=False, default=0)
    followers_tracked = Column(Integer, nullable=False, default=0)
    
    # Error handling
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    error_count = Column(Integer, nullable=False, default=0)
    consecutive_errors = Column(Integer, nullable=False, default=0)
    error_threshold = Column(Integer, nullable=False, default=5)
    
    # Timing information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    connected_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security and compliance
    encryption_key_id = Column(String(100), nullable=True)
    data_retention_days = Column(Integer, nullable=False, default=365)
    gdpr_compliant = Column(Boolean, nullable=False, default=True)
    consent_given = Column(Boolean, nullable=False, default=False)
    consent_date = Column(DateTime(timezone=True), nullable=True)
    terms_accepted = Column(Boolean, nullable=False, default=False)
    
    # Monitoring and alerts
    health_check_enabled = Column(Boolean, nullable=False, default=True)
    health_check_interval = Column(Integer, nullable=False, default=60)  # minutes
    alert_on_failure = Column(Boolean, nullable=False, default=True)
    alert_threshold = Column(Integer, nullable=False, default=3)
    monitoring_webhook = Column(String(500), nullable=True)
    
    # Business features
    monetization_enabled = Column(Boolean, nullable=False, default=False)
    revenue_tracking = Column(Boolean, nullable=False, default=False)
    brand_safety_enabled = Column(Boolean, nullable=False, default=True)
    content_moderation = Column(Boolean, nullable=False, default=True)
    
    # Integration metadata
    integration_notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    priority = Column(Integer, nullable=False, default=50)  # 1-100
    
    # Administrative fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    requires_reauth = Column(Boolean, nullable=False, default=False)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    authorized_by = Column(String(100), nullable=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_social_integration_user_platform', 'user_id', 'platform'),
        Index('idx_social_integration_status_sync', 'connection_status', 'sync_status'),
        Index('idx_social_integration_platform_username', 'platform', 'platform_username'),
        Index('idx_social_integration_token_expires', 'token_expires_at'),
        Index('idx_social_integration_last_sync', 'last_sync_at'),
        Index('idx_social_integration_rate_limit', 'rate_limit_reset_at'),
        Index('idx_social_integration_health', 'health_check_enabled', 'last_activity_at'),
        Index('idx_social_integration_permissions', 'permission_level', 'is_verified'),
        Index('idx_social_integration_active_primary', 'is_active', 'is_primary'),
        Index('idx_social_integration_errors', 'consecutive_errors', 'last_error_at'),
    )
    
    # Relationships
    creator_profile = relationship("CreatorProfile", back_populates="social_integrations")
    
    def __repr__(self):
        return f"<SocialIntegration(id={self.id}, platform={self.platform.value}, status={self.connection_status.value})>"
    
    @classmethod
    def create_integration(
        cls, 
        user_id: str, 
        platform: Platform,
        integration_type: IntegrationType,
        platform_username: str = None,
        **kwargs
    ) -> 'SocialIntegration':
        """Create a new social integration"""        return cls(
            user_id=user_id,
            platform=platform,
            integration_type=integration_type,
            platform_username=platform_username,
            integration_id=f"{platform.value}_{uuid.uuid4().hex[:8]}",
            created_by=kwargs.get('created_by', 'system'),
            **{k: v for k, v in kwargs.items() if k != 'created_by'}
        )
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""        if not self.token_expires_at:
            return False
        return datetime.now(timezone.utc) >= self.token_expires_at
    
    def is_refresh_needed(self) -> bool:
        """Check if token refresh is needed"""        if not self.token_expires_at:
            return False
        
        # Refresh if token expires within 1 hour
        refresh_threshold = self.token_expires_at - timedelta(hours=1)
        return datetime.now(timezone.utc) >= refresh_threshold
    
    def update_rate_limit(self, remaining: int, reset_at: datetime) -> None:
        """Update rate limit information"""        self.rate_limit_remaining = remaining
        self.rate_limit_reset_at = reset_at
        self.last_api_call = datetime.now(timezone.utc)
        self.api_calls_today += 1
        self.total_api_calls += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def can_make_api_call(self) -> bool:
        """Check if API call can be made based on rate limits"""        if not self.rate_limit_remaining:
            return True
        
        if self.rate_limit_remaining <= 0:
            if self.rate_limit_reset_at and datetime.now(timezone.utc) < self.rate_limit_reset_at:
                return False
        
        return True
    
    def mark_api_success(self, response_time_ms: int = None) -> None:
        """Mark API call as successful"""        self.successful_calls += 1
        self.consecutive_errors = 0
        self.last_activity_at = datetime.now(timezone.utc)
        
        if response_time_ms:
            if self.average_response_time:
                self.average_response_time = (self.average_response_time + response_time_ms) / 2
            else:
                self.average_response_time = response_time_ms
        
        # Update uptime percentage
        total_calls = self.successful_calls + self.failed_calls
        self.uptime_percentage = (self.successful_calls / total_calls) * 100 if total_calls > 0 else 100.0
        
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_api_failure(self, error_message: str) -> None:
        """Mark API call as failed"""        self.failed_calls += 1
        self.consecutive_errors += 1
        self.error_count += 1
        self.last_error = error_message
        self.last_error_at = datetime.now(timezone.utc)
        
        # Update uptime percentage
        total_calls = self.successful_calls + self.failed_calls
        self.uptime_percentage = (self.successful_calls / total_calls) * 100 if total_calls > 0 else 0.0
        
        # Check if error threshold is exceeded
        if self.consecutive_errors >= self.error_threshold:
            self.connection_status = ConnectionStatus.ERROR
        
        self.updated_at = datetime.now(timezone.utc)
    
    def refresh_access_token(self, new_access_token: str, new_refresh_token: str = None, expires_in: int = None) -> None:
        """Refresh access token"""        self.access_token = new_access_token
        if new_refresh_token:
            self.refresh_token = new_refresh_token
        
        if expires_in:
            self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        self.last_token_refresh = datetime.now(timezone.utc)
        self.connection_status = ConnectionStatus.CONNECTED
        self.updated_at = datetime.now(timezone.utc)
    
    def sync_platform_data(self, data: Dict[str, Any]) -> None:
        """Synchronize data from platform"""        self.last_sync_data = {
            **data,
            'synced_at': datetime.now(timezone.utc).isoformat()
        }
        self.last_sync_at = datetime.now(timezone.utc)
        self.sync_status = SyncStatus.IN_SYNC
        self.content_synced += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_sync_error(self, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Mark synchronization error"""        if not self.sync_errors:
            self.sync_errors = []
        
        error_entry = {
            'message': error_message,
            'details': error_details or {},
            'occurred_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.sync_errors.append(error_entry)
        self.sync_status = SyncStatus.SYNC_ERROR
        self.updated_at = datetime.now(timezone.utc)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get integration health status"""        health_score = 100.0
        issues = []
        
        # Check connection status
        if self.connection_status != ConnectionStatus.CONNECTED:
            health_score -= 30
            issues.append(f"Connection status: {self.connection_status.value}")
        
        # Check token expiration
        if self.is_token_expired():
            health_score -= 20
            issues.append("Access token expired")
        
        # Check error rate
        error_rate = (self.consecutive_errors / max(1, self.total_api_calls)) * 100
        if error_rate > 10:
            health_score -= 25
            issues.append(f"High error rate: {error_rate:.1f}%")
        
        # Check last activity
        if self.last_activity_at:
            hours_inactive = (datetime.now(timezone.utc) - self.last_activity_at).total_seconds() / 3600
            if hours_inactive > 24:
                health_score -= 15
                issues.append(f"Inactive for {hours_inactive:.1f} hours")
        
        # Check sync status
        if self.sync_status == SyncStatus.SYNC_ERROR:
            health_score -= 10
            issues.append("Sync errors detected")
        
        return {
            'health_score': max(0, health_score),
            'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical',
            'issues': issues,
            'last_check': datetime.now(timezone.utc).isoformat()
        }
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get comprehensive integration summary"""        return {
            'platform_info': {
                'platform': self.platform.value,
                'username': self.platform_username,
                'display_name': self.platform_display_name,
                'verified': self.verified_account,
                'url': self.platform_url
            },
            'connection_status': {
                'status': self.connection_status.value,
                'connected_at': self.connected_at.isoformat() if self.connected_at else None,
                'last_activity': self.last_activity_at.isoformat() if self.last_activity_at else None,
                'requires_reauth': self.requires_reauth
            },
            'permissions': {
                'level': self.permission_level.value,
                'scopes': self.scopes or [],
                'posting_enabled': self.posting_enabled,
                'analytics_enabled': self.analytics_enabled
            },
            'sync_info': {
                'status': self.sync_status.value,
                'last_sync': self.last_sync_at.isoformat() if self.last_sync_at else None,
                'frequency': self.sync_frequency,
                'auto_sync': self.auto_sync_enabled
            },
            'performance': {
                'total_api_calls': self.total_api_calls,
                'success_rate': (self.successful_calls / max(1, self.total_api_calls)) * 100,
                'uptime_percentage': self.uptime_percentage,
                'average_response_time': self.average_response_time
            }
        }
    
    def schedule_next_sync(self) -> Optional[datetime]:
        """Calculate next synchronization time"""        if not self.auto_sync_enabled or self.sync_frequency == "manual":
            return None
        
        now = datetime.now(timezone.utc)
        
        if self.sync_frequency == "hourly":
            return now + timedelta(hours=1)
        elif self.sync_frequency == "daily":
            return now + timedelta(days=1)
        elif self.sync_frequency == "weekly":
            return now + timedelta(weeks=1)
        
        return None
    
    def disconnect(self, reason: str = None) -> None:
        """Disconnect the integration"""        self.connection_status = ConnectionStatus.DISCONNECTED
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.sync_status = SyncStatus.OUT_OF_SYNC
        if reason:
            self.integration_notes = f"Disconnected: {reason}"
        self.updated_at = datetime.now(timezone.utc)
