"""
Notification Models for IA2Good Platform
Multi-channel notification system (Push, Email, SMS, In-App)
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from database import Base


class NotificationType(enum.Enum):
    """Types of notifications"""
    # Cases
    NEW_CASE_NEARBY = "new_case_nearby"
    CASE_ASSIGNED = "case_assigned"
    CASE_ACCEPTED = "case_accepted"
    CASE_REJECTED = "case_rejected"
    CASE_COMPLETED = "case_completed"
    CASE_CANCELLED = "case_cancelled"
    CASE_UPDATED = "case_updated"
    
    # Assignments
    ASSIGNMENT_ACCEPTED = "assignment_accepted"
    ASSIGNMENT_DECLINED = "assignment_declined"
    ASSIGNMENT_STARTED = "assignment_started"
    ASSIGNMENT_COMPLETED = "assignment_completed"
    
    # Ratings
    RATING_REQUEST = "rating_request"
    RATING_RECEIVED = "rating_received"
    
    # Issues
    ISSUE_REPORTED = "issue_reported"
    ISSUE_STATUS_CHANGED = "issue_status_changed"
    ISSUE_COMMENT_ADDED = "issue_comment_added"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_RESOLVED = "issue_resolved"
    
    # Events
    EVENT_CREATED = "event_created"
    EVENT_REMINDER = "event_reminder"
    EVENT_CANCELLED = "event_cancelled"
    EVENT_UPDATED = "event_updated"
    NEW_ATTENDEE = "new_attendee"
    
    # Campaigns
    CAMPAIGN_LAUNCHED = "campaign_launched"
    DONATION_RECEIVED = "donation_received"
    GOAL_REACHED = "goal_reached"
    CAMPAIGN_ENDING_SOON = "campaign_ending_soon"
    
    # Media
    MEDIA_PROCESSING_COMPLETE = "media_processing_complete"
    MEDIA_PROCESSING_FAILED = "media_processing_failed"
    LIVE_STREAM_STARTED = "live_stream_started"
    
    # Volunteers
    VOLUNTEER_VERIFIED = "volunteer_verified"
    VOLUNTEER_SUSPENDED = "volunteer_suspended"
    VOLUNTEER_BADGE_EARNED = "volunteer_badge_earned"
    
    # System
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    SYSTEM_MAINTENANCE = "system_maintenance"
    ACCOUNT_VERIFICATION = "account_verification"
    PASSWORD_RESET = "password_reset"


class NotificationChannel(enum.Enum):
    """Channels for sending notifications"""
    IN_APP = "in_app"          # Dashboard notification
    PUSH = "push"              # Mobile push notification
    EMAIL = "email"            # Email notification
    SMS = "sms"                # SMS notification
    WEBHOOK = "webhook"        # Webhook callback


class NotificationPriority(enum.Enum):
    """Priority levels for notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    User notifications (in-app and delivery tracking)
    """
    __tablename__ = "ia2good_notifications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Recipient
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Recipient user ID
    
    # Notification details
    type = Column(
        SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    # Priority and urgency
    priority = Column(
        SQLEnum(NotificationPriority, values_callable=lambda x: [e.value for e in x]),
        default=NotificationPriority.NORMAL.value,
        nullable=False
    )
    
    # Related entity (polymorphic)
    entity_type = Column(String(50))  # case, issue, event, campaign, assignment, etc.
    entity_id = Column(UUID(as_uuid=True))  # FK to related entity
    
    # Action URL/Deep link
    action_url = Column(String(500))  # URL to navigate when clicked
    
    # Additional data (JSON)
    data = Column(JSON)  # Extra payload for mobile app
    
    # Read status
    read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True))
    
    # Delivery tracking
    channels = Column(ARRAY(String), default=['in_app'])  # Which channels to use
    
    # Push notification delivery
    push_sent = Column(Boolean, default=False)
    push_sent_at = Column(DateTime(timezone=True))
    push_delivered = Column(Boolean, default=False)
    push_delivery_status = Column(String(50))  # success, failed, pending
    
    # Email delivery
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True))
    email_opened = Column(Boolean, default=False)
    email_opened_at = Column(DateTime(timezone=True))
    
    # SMS delivery
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime(timezone=True))
    sms_delivery_status = Column(String(50))
    
    # Metadata
    expires_at = Column(DateTime(timezone=True))  # Auto-expire notifications
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexing for performance
    __table_args__ = (
        {'comment': 'Multi-channel user notifications with delivery tracking'}
    ,)


class NotificationPreference(Base):
    """
    User notification preferences per channel and type
    """
    __tablename__ = "ia2good_notification_preferences"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Global settings
    enabled = Column(Boolean, default=True, nullable=False)  # Master switch
    
    # Channel preferences
    in_app_enabled = Column(Boolean, default=True, nullable=False)
    push_enabled = Column(Boolean, default=True, nullable=False)
    email_enabled = Column(Boolean, default=True, nullable=False)
    sms_enabled = Column(Boolean, default=False, nullable=False)  # Opt-in only
    
    # Notification type preferences (JSON)
    type_preferences = Column(JSON, default={})
    # Example:
    # {
    #   "new_case_nearby": {"push": true, "email": false, "sms": false},
    #   "case_completed": {"push": true, "email": true, "sms": false},
    #   "event_reminder": {"push": true, "email": true, "sms": true}
    # }
    
    # Quiet hours (DND)
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # "22:00" format
    quiet_hours_end = Column(String(5))    # "08:00" format
    quiet_hours_timezone = Column(String(50), default="UTC")
    
    # Digest settings
    digest_enabled = Column(Boolean, default=False)
    digest_frequency = Column(String(20))  # daily, weekly
    digest_time = Column(String(5))  # "09:00" format
    
    # Device tokens (for push notifications)
    device_tokens = Column(JSON, default=[])
    # Example:
    # [
    #   {"token": "abc123", "platform": "ios", "added_at": "2025-01-01T00:00:00Z"},
    #   {"token": "def456", "platform": "android", "added_at": "2025-01-01T00:00:00Z"}
    # ]
    
    # Contact info
    email = Column(String(255))
    phone = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationTemplate(Base):
    """
    Notification templates for consistent messaging
    """
    __tablename__ = "ia2good_notification_templates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template identification
    type = Column(
        SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        unique=True
    )
    
    # Multi-language support
    language = Column(String(5), default="fr", nullable=False)  # fr, en, ar, es, de, zh
    
    # Template content
    title_template = Column(String(255), nullable=False)  # "🆘 Nouveau cas {{case_type}}"
    body_template = Column(Text, nullable=False)  # Supports Jinja2 syntax
    
    # Email-specific
    email_subject_template = Column(String(255))
    email_html_template = Column(Text)  # HTML version for emails
    
    # SMS-specific (shortened)
    sms_template = Column(Text)  # Max 160 chars
    
    # Push notification-specific
    push_title_template = Column(String(100))
    push_body_template = Column(String(200))
    
    # Default data
    default_data = Column(JSON)
    
    # Metadata
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationLog(Base):
    """
    Audit log for all notification sends (debugging)
    """
    __tablename__ = "ia2good_notification_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Notification reference
    notification_id = Column(UUID(as_uuid=True), index=True)  # FK to notification
    
    # Delivery details
    channel = Column(
        SQLEnum(NotificationChannel, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    recipient = Column(String(255), nullable=False)  # Email, phone, device token
    
    # Status
    status = Column(String(20), nullable=False)  # queued, sent, delivered, failed, bounced
    error_message = Column(Text)
    
    # Provider info
    provider = Column(String(50))  # FCM, APNS, SendGrid, Twilio, etc.
    provider_message_id = Column(String(255))
    
    # Timing
    queued_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Metadata
    metadata = Column(JSON)  # Additional debug info
    
    __table_args__ = (
        {'comment': 'Audit log for notification delivery tracking'}
    ,)
