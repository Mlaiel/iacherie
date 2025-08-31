"""Notification Settings Database Model

Enterprise-grade SQLAlchemy model for managing comprehensive notification preferences,
delivery settings, and communication channels for users and creators.

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
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, ARRAY, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, time
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class NotificationType(Enum):
    """Notification type enumeration"""
    CONTENT_PROTECTION = "content_protection"
    COPYRIGHT_VIOLATION = "copyright_violation"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_DECLINED = "collaboration_declined"
    NEW_FOLLOWER = "new_follower"
    NEW_COMMENT = "new_comment"
    NEW_LIKE = "new_like"
    NEW_SHARE = "new_share"
    VIRAL_CONTENT = "viral_content"
    MILESTONE_REACHED = "milestone_reached"
    REVENUE_UPDATE = "revenue_update"
    PAYMENT_RECEIVED = "payment_received"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    PLATFORM_UPDATE = "platform_update"
    SECURITY_ALERT = "security_alert"
    ACCOUNT_VERIFICATION = "account_verification"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_FAILED = "content_failed"
    TRENDING_OPPORTUNITY = "trending_opportunity"
    AI_RECOMMENDATION = "ai_recommendation"
    SYSTEM_MAINTENANCE = "system_maintenance"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    NEWSLETTER = "newsletter"
    CONTEST_ANNOUNCEMENT = "contest_announcement"
    FEATURE_UPDATE = "feature_update"
    PERFORMANCE_REPORT = "performance_report"


class Channel(Enum):
    """Notification delivery channel"""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    BROWSER_NOTIFICATION = "browser_notification"
    DESKTOP_NOTIFICATION = "desktop_notification"
    MOBILE_NOTIFICATION = "mobile_notification"


class Priority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Frequency(Enum):
    """Notification frequency settings"""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"
    CUSTOM = "custom"
    SMART = "smart"  # AI-determined optimal frequency


class Status(Enum):
    """Notification setting status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"


class DeliveryTime(Enum):
    """Preferred delivery time"""
    ANYTIME = "anytime"
    BUSINESS_HOURS = "business_hours"
    EVENING = "evening"
    MORNING = "morning"
    WEEKEND_ONLY = "weekend_only"
    WEEKDAY_ONLY = "weekday_only"
    CUSTOM_SCHEDULE = "custom_schedule"


class NotificationSettings(Base):
    """
    Enterprise Notification Settings Model
    
    Comprehensive notification preference management with multi-channel support,
    smart scheduling, priority handling, and granular control options.
    """
    __tablename__ = 'notification_settings'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    settings_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # User reference
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_profile_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=True, index=True)
    
    # Notification classification
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    category = Column(String(100), nullable=False, default="general", index=True)
    subcategory = Column(String(100), nullable=True)
    
    # Channel configuration
    enabled_channels = Column(ARRAY(String), nullable=False, default=list)
    primary_channel = Column(SQLEnum(Channel), nullable=False, default=Channel.EMAIL, index=True)
    fallback_channels = Column(ARRAY(String), nullable=True)
    
    # Delivery preferences
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.NORMAL, index=True)
    frequency = Column(SQLEnum(Frequency), nullable=False, default=Frequency.IMMEDIATE, index=True)
    status = Column(SQLEnum(Status), nullable=False, default=Status.ACTIVE, index=True)
    
    # Timing preferences
    delivery_time = Column(SQLEnum(DeliveryTime), nullable=False, default=DeliveryTime.ANYTIME)
    timezone = Column(String(50), nullable=False, default="UTC")
    quiet_hours_start = Column(Time, nullable=True)
    quiet_hours_end = Column(Time, nullable=True)
    weekend_delivery = Column(Boolean, nullable=False, default=True)
    
    # Custom scheduling
    custom_schedule = Column(JSONB, nullable=True)  # {day_of_week: {hours: [9, 17]}}
    delivery_window_start = Column(Time, nullable=True)
    delivery_window_end = Column(Time, nullable=True)
    max_daily_notifications = Column(Integer, nullable=True)
    max_hourly_notifications = Column(Integer, nullable=True)
    
    # Channel-specific settings
    email_settings = Column(JSONB, nullable=True)  # {format: html/text, digest: true/false}
    sms_settings = Column(JSONB, nullable=True)    # {shortcode: true, international: false}
    push_settings = Column(JSONB, nullable=True)   # {sound: true, badge: true, vibrate: true}
    webhook_settings = Column(JSONB, nullable=True) # {url: webhook_url, headers: {}}
    
    # Content preferences
    language = Column(String(10), nullable=False, default="en")
    content_format = Column(String(50), nullable=False, default="standard")  # standard, minimal, detailed
    include_attachments = Column(Boolean, nullable=False, default=True)
    include_images = Column(Boolean, nullable=False, default=True)
    include_analytics = Column(Boolean, nullable=False, default=False)
    
    # Personalization
    personalized_content = Column(Boolean, nullable=False, default=True)
    ai_optimization = Column(Boolean, nullable=False, default=True)
    smart_timing = Column(Boolean, nullable=False, default=False)
    adaptive_frequency = Column(Boolean, nullable=False, default=False)
    
    # Filtering and conditions
    minimum_threshold = Column(JSONB, nullable=True)  # Minimum values to trigger notification
    keyword_filters = Column(ARRAY(String), nullable=True)
    blacklist_keywords = Column(ARRAY(String), nullable=True)
    geographic_restrictions = Column(ARRAY(String), nullable=True)
    platform_restrictions = Column(ARRAY(String), nullable=True)
    
    # Advanced filtering
    content_type_filters = Column(ARRAY(String), nullable=True)
    engagement_threshold = Column(Integer, nullable=True)
    revenue_threshold = Column(Float, nullable=True)
    collaboration_filters = Column(JSONB, nullable=True)
    
    # Rate limiting
    rate_limit_enabled = Column(Boolean, nullable=False, default=True)
    rate_limit_per_hour = Column(Integer, nullable=False, default=10)
    rate_limit_per_day = Column(Integer, nullable=False, default=50)
    burst_protection = Column(Boolean, nullable=False, default=True)
    cooldown_period = Column(Integer, nullable=True)  # Minutes between notifications of same type
    
    # Grouping and batching
    batch_notifications = Column(Boolean, nullable=False, default=False)
    batch_size = Column(Integer, nullable=True, default=5)
    batch_timeout = Column(Integer, nullable=True, default=60)  # Minutes
    group_similar = Column(Boolean, nullable=False, default=True)
    digest_enabled = Column(Boolean, nullable=False, default=False)
    digest_frequency = Column(SQLEnum(Frequency), nullable=True)
    
    # Analytics and tracking
    open_rate_tracking = Column(Boolean, nullable=False, default=True)
    click_tracking = Column(Boolean, nullable=False, default=True)
    engagement_tracking = Column(Boolean, nullable=False, default=True)
    delivery_analytics = Column(Boolean, nullable=False, default=True)
    
    # Performance metrics
    delivery_success_rate = Column(Float, nullable=False, default=0.0)
    open_rate = Column(Float, nullable=False, default=0.0)
    click_rate = Column(Float, nullable=False, default=0.0)
    unsubscribe_rate = Column(Float, nullable=False, default=0.0)
    bounce_rate = Column(Float, nullable=False, default=0.0)
    
    # A/B Testing
    ab_test_group = Column(String(50), nullable=True)
    test_variant = Column(String(50), nullable=True)
    experiment_id = Column(String(100), nullable=True)
    control_group = Column(Boolean, nullable=False, default=False)
    
    # Contact information
    email_address = Column(String(200), nullable=True)
    phone_number = Column(String(20), nullable=True)
    mobile_device_tokens = Column(ARRAY(String), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    slack_webhook = Column(String(500), nullable=True)
    discord_webhook = Column(String(500), nullable=True)
    
    # Verification status
    email_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    webhook_verified = Column(Boolean, nullable=False, default=False)
    verification_attempts = Column(Integer, nullable=False, default=0)
    last_verification_attempt = Column(DateTime(timezone=True), nullable=True)
    
    # Compliance and consent
    consent_given = Column(Boolean, nullable=False, default=False)
    consent_date = Column(DateTime(timezone=True), nullable=True)
    gdpr_compliant = Column(Boolean, nullable=False, default=True)
    marketing_consent = Column(Boolean, nullable=False, default=False)
    data_processing_consent = Column(Boolean, nullable=False, default=False)
    
    # Template preferences
    email_template = Column(String(100), nullable=True)
    sms_template = Column(String(100), nullable=True)
    push_template = Column(String(100), nullable=True)
    custom_templates = Column(JSONB, nullable=True)
    
    # Timing information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_notification_sent = Column(DateTime(timezone=True), nullable=True, index=True)
    next_scheduled_notification = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True)
    integration_data = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_system_generated = Column(Boolean, nullable=False, default=False)
    is_user_configurable = Column(Boolean, nullable=False, default=True)
    requires_approval = Column(Boolean, nullable=False, default=False)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    migration_source = Column(String(100), nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_notification_settings_user_type', 'user_id', 'notification_type'),
        Index('idx_notification_settings_channel_priority', 'primary_channel', 'priority'),
        Index('idx_notification_settings_status_frequency', 'status', 'frequency'),
        Index('idx_notification_settings_category', 'category', 'subcategory'),
        Index('idx_notification_settings_delivery_time', 'delivery_time', 'timezone'),
        Index('idx_notification_settings_next_scheduled', 'next_scheduled_notification'),
        Index('idx_notification_settings_last_sent', 'last_notification_sent'),
        Index('idx_notification_settings_active_user', 'is_active', 'user_id'),
        Index('idx_notification_settings_consent', 'consent_given', 'gdpr_compliant'),
        Index('idx_notification_settings_verification', 'email_verified', 'phone_verified'),
    )
    
    # Relationships
    creator_profile = relationship("CreatorProfile", back_populates="notification_settings")
    
    def __repr__(self):
        return f"<NotificationSettings(id={self.id}, user_id={self.user_id}, type={self.notification_type.value})>"
    
    @classmethod
    def create_default_settings(cls, user_id: str, creator_profile_id: str = None) -> List['NotificationSettings']:
        """Create default notification settings for a new user"""
        default_settings = []
        
        # Essential notification types with default configurations
        essential_types = [
            (NotificationType.CONTENT_PROTECTION, Priority.HIGH, Frequency.IMMEDIATE, [Channel.EMAIL.value, Channel.IN_APP.value]),
            (NotificationType.COPYRIGHT_VIOLATION, Priority.URGENT, Frequency.IMMEDIATE, [Channel.EMAIL.value, Channel.PUSH_NOTIFICATION.value]),
            (NotificationType.COLLABORATION_REQUEST, Priority.NORMAL, Frequency.IMMEDIATE, [Channel.EMAIL.value, Channel.IN_APP.value]),
            (NotificationType.VIRAL_CONTENT, Priority.HIGH, Frequency.IMMEDIATE, [Channel.EMAIL.value, Channel.PUSH_NOTIFICATION.value]),
            (NotificationType.REVENUE_UPDATE, Priority.NORMAL, Frequency.DAILY, [Channel.EMAIL.value]),
            (NotificationType.SECURITY_ALERT, Priority.CRITICAL, Frequency.IMMEDIATE, [Channel.EMAIL.value, Channel.SMS.value]),
        ]
        
        for notification_type, priority, frequency, channels in essential_types:
            setting = cls(
                user_id=user_id,
                creator_profile_id=creator_profile_id,
                notification_type=notification_type,
                priority=priority,
                frequency=frequency,
                enabled_channels=channels,
                primary_channel=Channel(channels[0]),
                settings_id=f"{notification_type.value}_{user_id}_{uuid.uuid4().hex[:8]}",
                created_by="system"
            )
            default_settings.append(setting)
        
        return default_settings
    
    def is_delivery_time_valid(self, check_time: datetime = None) -> bool:
        """Check if current time is valid for delivery based on settings"""
        if check_time is None:
            check_time = datetime.now(timezone.utc)
        
        # Convert to user's timezone
        # This is simplified - in production, use proper timezone conversion
        
        # Check quiet hours
        if self.quiet_hours_start and self.quiet_hours_end:
            current_time = check_time.time()
            if self.quiet_hours_start <= self.quiet_hours_end:
                if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                    return False
            else:  # Quiet hours span midnight
                if current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end:
                    return False
        
        # Check weekend delivery
        if not self.weekend_delivery and check_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check delivery window
        if self.delivery_window_start and self.delivery_window_end:
            current_time = check_time.time()
            if not (self.delivery_window_start <= current_time <= self.delivery_window_end):
                return False
        
        return True
    
    def should_send_notification(self, context: Dict[str, Any] = None) -> bool:
        """Determine if notification should be sent based on filters and conditions"""
        if not self.is_active or self.status != Status.ACTIVE:
            return False
        
        # Check rate limits
        if self.rate_limit_enabled and self.last_notification_sent:
            time_since_last = datetime.now(timezone.utc) - self.last_notification_sent
            
            # Check cooldown period
            if self.cooldown_period and time_since_last.total_seconds() < (self.cooldown_period * 60):
                return False
        
        # Check delivery time
        if not self.is_delivery_time_valid():
            return False
        
        # Check thresholds
        if context and self.minimum_threshold:
            for key, min_value in self.minimum_threshold.items():
                if context.get(key, 0) < min_value:
                    return False
        
        # Check keyword filters
        if context and self.blacklist_keywords:
            content_text = str(context.get('content', '')).lower()
            if any(keyword.lower() in content_text for keyword in self.blacklist_keywords):
                return False
        
        return True
    
    def get_optimal_channel(self, context: Dict[str, Any] = None) -> Channel:
        """Get optimal delivery channel based on AI optimization and context"""
        if not self.ai_optimization:
            return self.primary_channel
        
        # AI-based channel selection logic
        if self.priority in [Priority.URGENT, Priority.CRITICAL]:
            # Prefer faster channels for urgent notifications
            if Channel.PUSH_NOTIFICATION.value in self.enabled_channels:
                return Channel.PUSH_NOTIFICATION
            elif Channel.SMS.value in self.enabled_channels:
                return Channel.SMS
        
        # Consider historical engagement rates
        if self.open_rate > 0.7 and Channel.EMAIL.value in self.enabled_channels:
            return Channel.EMAIL
        elif self.click_rate > 0.3 and Channel.PUSH_NOTIFICATION.value in self.enabled_channels:
            return Channel.PUSH_NOTIFICATION
        
        return self.primary_channel
    
    def update_performance_metrics(self, delivered: bool, opened: bool = False, clicked: bool = False) -> None:
        """Update performance metrics based on notification interaction"""
        # This would be implemented with proper statistical tracking
        # Simplified version here
        
        if delivered:
            # Update delivery success rate (would use rolling average)
            pass
        
        if opened:
            # Update open rate
            pass
        
        if clicked:
            # Update click rate
            pass
        
        self.updated_at = datetime.now(timezone.utc)
    
    def schedule_next_notification(self) -> Optional[datetime]:
        """Calculate next notification time based on frequency settings"""
        if self.frequency == Frequency.NEVER:
            return None
        
        now = datetime.now(timezone.utc)
        
        if self.frequency == Frequency.IMMEDIATE:
            return now
        elif self.frequency == Frequency.HOURLY:
            next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif self.frequency == Frequency.DAILY:
            next_time = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            next_time = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        elif self.frequency == Frequency.MONTHLY:
            if now.month == 12:
                next_time = now.replace(year=now.year + 1, month=1, day=1, hour=9, minute=0, second=0, microsecond=0)
            else:
                next_time = now.replace(month=now.month + 1, day=1, hour=9, minute=0, second=0, microsecond=0)
        else:
            return None
        
        # Adjust for delivery time preferences
        if not self.is_delivery_time_valid(next_time):
            # Find next valid delivery time
            while not self.is_delivery_time_valid(next_time):
                next_time += timedelta(hours=1)
        
        self.next_scheduled_notification = next_time
        return next_time
    
    def get_notification_template_data(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get template data for notification rendering"""
        return {
            'user_preferences': {
                'language': self.language,
                'format': self.content_format,
                'timezone': self.timezone,
                'include_images': self.include_images,
                'include_analytics': self.include_analytics
            },
            'delivery_settings': {
                'channel': self.primary_channel.value,
                'priority': self.priority.value,
                'personalized': self.personalized_content
            },
            'context': context or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def clone_settings(self, new_notification_type: NotificationType) -> 'NotificationSettings':
        """Clone settings for a different notification type"""
        new_settings = NotificationSettings(
            user_id=self.user_id,
            creator_profile_id=self.creator_profile_id,
            notification_type=new_notification_type,
            enabled_channels=self.enabled_channels.copy(),
            primary_channel=self.primary_channel,
            fallback_channels=self.fallback_channels.copy() if self.fallback_channels else None,
            priority=self.priority,
            frequency=self.frequency,
            delivery_time=self.delivery_time,
            timezone=self.timezone,
            quiet_hours_start=self.quiet_hours_start,
            quiet_hours_end=self.quiet_hours_end,
            settings_id=f"{new_notification_type.value}_{self.user_id}_{uuid.uuid4().hex[:8]}",
            created_by="clone"
        )
        
        return new_settings
