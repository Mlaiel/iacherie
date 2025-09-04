"""Notification and Messaging Schemas

Comprehensive Pydantic schemas for notifications, messaging system,
and communication management in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class NotificationTypeEnum(str, Enum):
    """
Types of notifications"""

    SYSTEM = "system"
    SECURITY = "security"
    CONTENT = "content"
    COLLABORATION = "collaboration"
    PROTECTION = "protection"
    REVENUE = "revenue"
    LICENSING = "licensing"
    PLATFORM = "platform"
    MARKETING = "marketing"
    SOCIAL = "social"
    REMINDER = "reminder"
    UPDATE = "update"
    ALERT = "alert"
    WARNING = "warning"
    ERROR = "error"


class NotificationPriorityEnum(str, Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationChannelEnum(str, Enum):
    """Notification delivery channels"""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class NotificationStatusEnum(str, Enum):
    """Notification status"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MessageTypeEnum(str, Enum):
    """Types of messages"""

    DIRECT_MESSAGE = "direct_message"
    GROUP_MESSAGE = "group_message"
    SYSTEM_MESSAGE = "system_message"
    COLLABORATION_MESSAGE = "collaboration_message"
    SUPPORT_MESSAGE = "support_message"
    ANNOUNCEMENT = "announcement"
    FEEDBACK = "feedback"
    COMPLAINT = "complaint"


class MessageStatusEnum(str, Enum):
    """Message status"""

    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AttachmentTypeEnum(str, Enum):
    """Types of message attachments"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    LINK = "link"
    CODE = "code"
    LOCATION = "location"


class CommunicationPreferencesSchema(BaseModel):
    """Schema for communication preferences"""
    # Channel preferences
    email_enabled: bool = Field(True, description="Enable email notifications")
    sms_enabled: bool = Field(False, description="Enable SMS notifications")
    push_enabled: bool = Field(True, description="Enable push notifications")
    in_app_enabled: bool = Field(True, description="Enable in-app notifications")
    
    # Notification type preferences
    system_notifications: bool = Field(True, description="System notifications")
    security_alerts: bool = Field(True, description="Security alerts")
    content_updates: bool = Field(True, description="Content-related updates")
    collaboration_messages: bool = Field(True, description="Collaboration messages")
    protection_alerts: bool = Field(True, description="Protection alerts")
    revenue_notifications: bool = Field(True, description="Revenue notifications")
    licensing_updates: bool = Field(True, description="Licensing updates")
    platform_news: bool = Field(False, description="Platform news and updates")
    marketing_messages: bool = Field(False, description="Marketing communications")
    
    # Frequency settings
    instant_notifications: bool = Field(True, description="Instant notifications")
    daily_digest: bool = Field(False, description="Daily digest emails")
    weekly_summary: bool = Field(True, description="Weekly summary emails")
    
    # Quiet hours
    quiet_hours_enabled: bool = Field(False, description="Enable quiet hours")
    quiet_start_time: Optional[str] = Field(None, description="Quiet hours start time (HH:MM)")
    quiet_end_time: Optional[str] = Field(None, description="Quiet hours end time (HH:MM)")
    quiet_timezone: str = Field("UTC", description="Timezone for quiet hours")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_enabled": True,
                "push_enabled": True,
                "security_alerts": True,
                "collaboration_messages": True,
                "marketing_messages": False,
                "quiet_hours_enabled": True,
                "quiet_start_time": "22:00",
                "quiet_end_time": "08:00"
            }
        }


class NotificationTemplateSchema(BaseModel):
    """Schema for notification templates"""
    template_id: str = Field(..., description="Unique template identifier")
    template_name: str = Field(..., description="Template name")
    notification_type: NotificationTypeEnum = Field(..., description="Notification type")
    
    # Template content
    subject_template: str = Field(..., description="Subject line template")
    body_template: str = Field(..., description="Message body template")
    html_template: Optional[str] = Field(None, description="HTML template for rich content")
    
    # Localization
    language: str = Field("en", description="Template language")
    localized_templates: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Localized templates")
    
    # Variables and placeholders
    template_variables: List[str] = Field(..., description="Available template variables")
    required_variables: List[str] = Field(..., description="Required template variables")
    
    # Styling and formatting
    style_config: Optional[Dict[str, Any]] = Field(None, description="Style configuration")
    brand_elements: Optional[Dict[str, str]] = Field(None, description="Brand elements (logo, colors)")
    
    # Template metadata
    created_by: str = Field(..., description="Template creator")
    version: str = Field("1.0", description="Template version")
    active: bool = Field(True, description="Whether template is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "TPL-PROTECTION-001",
                "template_name": "Protection Alert",
                "notification_type": "protection",
                "subject_template": "Protection Alert: Unauthorized use detected",
                "body_template": "Hello {{user_name}}, we detected unauthorized use of your content...",
                "template_variables": ["user_name", "content_title", "platform"],
                "language": "en"
            }
        }


class MessageAttachmentSchema(BaseModel):
    """Schema for message attachments"""
    attachment_id: str = Field(..., description="Unique attachment identifier")
    attachment_type: AttachmentTypeEnum = Field(..., description="Type of attachment")
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="File URL")
    file_size: PositiveInt = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    
    # Media-specific metadata
    duration: Optional[float] = Field(None, description="Duration for audio/video in seconds")
    dimensions: Optional[Dict[str, int]] = Field(None, description="Image/video dimensions")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    
    # Security and validation
    virus_scanned: bool = Field(False, description="Virus scan status")
    file_hash: Optional[str] = Field(None, description="File hash for integrity")
    encryption_status: Optional[str] = Field(None, description="Encryption status")
    
    # Metadata
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    download_count: int = Field(0, description="Number of downloads")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attachment_id": "ATT-2024-001234",
                "attachment_type": "audio",
                "filename": "demo_track.mp3",
                "file_size": 8388608,
                "mime_type": "audio/mpeg",
                "duration": 180.5,
                "virus_scanned": True
            }
        }


class NotificationBaseSchema(BaseModel):
    """Base schema for notifications"""
    notification_type: NotificationTypeEnum = Field(..., description="Type of notification")
    priority: NotificationPriorityEnum = Field(..., description="Notification priority")
    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., max_length=1000, description="Notification message")
    
    # Recipients
    recipient_user_id: PositiveInt = Field(..., description="Recipient user ID")
    sender_user_id: Optional[PositiveInt] = Field(None, description="Sender user ID (if applicable)")
    
    # Delivery channels
    channels: List[NotificationChannelEnum] = Field(..., description="Delivery channels")
    
    # Content and context
    action_url: Optional[HttpUrl] = Field(None, description="Action URL")
    action_text: Optional[str] = Field(None, description="Action button text")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    related_entity_type: Optional[str] = Field(None, description="Related entity type")
    related_entity_id: Optional[str] = Field(None, description="Related entity ID")
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled delivery time")
    expires_at: Optional[datetime] = Field(None, description="Notification expiration")
    
    # Personalization
    personalization_data: Optional[Dict[str, Any]] = Field(None, description="Personalization data")
    template_id: Optional[str] = Field(None, description="Notification template ID")


class NotificationCreateSchema(NotificationBaseSchema):
    """Schema for creating notifications"""
    # Delivery options
    immediate_delivery: bool = Field(True, description="Deliver immediately")
    retry_on_failure: bool = Field(True, description="Retry on delivery failure")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    
    # Tracking and analytics
    track_opens: bool = Field(True, description="Track notification opens")
    track_clicks: bool = Field(True, description="Track link clicks")
    analytics_tags: Optional[List[str]] = Field(None, description="Analytics tags")
    
    # Grouping and deduplication
    group_key: Optional[str] = Field(None, description="Grouping key for similar notifications")
    deduplicate_window: Optional[int] = Field(None, description="Deduplication window in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "notification_type": "protection",
                "priority": "high",
                "title": "Protection Alert",
                "message": "Unauthorized use of your content detected on YouTube",
                "recipient_user_id": 123,
                "channels": ["in_app", "email", "push"],
                "action_url": "https://app.example.com/protection/alerts/12345",
                "immediate_delivery": True
            }
        }


class NotificationResponseSchema(NotificationBaseSchema):
    """Schema for notification responses"""
    id: PositiveInt = Field(..., description="Unique notification ID")
    notification_reference: str = Field(..., description="Human-readable notification reference")
    
    # Status and delivery
    status: NotificationStatusEnum = Field(..., description="Notification status")
    delivery_attempts: int = Field(0, description="Number of delivery attempts")
    delivery_status: Dict[str, str] = Field(..., description="Delivery status per channel")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    sent_at: Optional[datetime] = Field(None, description="Sent timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivered timestamp")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    
    # Interaction tracking
    opened: bool = Field(False, description="Whether notification was opened")
    clicked: bool = Field(False, description="Whether action was clicked")
    dismissed: bool = Field(False, description="Whether notification was dismissed")
    
    # Analytics data
    open_count: int = Field(0, description="Number of opens")
    click_count: int = Field(0, description="Number of clicks")
    interaction_metadata: Optional[Dict[str, Any]] = Field(None, description="Interaction metadata")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")
    retry_count: int = Field(0, description="Number of retries attempted")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "notification_reference": "NOT-2024-001234",
                "notification_type": "protection",
                "status": "delivered",
                "recipient_user_id": 123,
                "title": "Protection Alert",
                "opened": True,
                "clicked": False,
                "created_at": "2024-08-24T10:30:00Z",
                "delivered_at": "2024-08-24T10:31:00Z"
            }
        }


class MessageBaseSchema(BaseModel):
    """Base schema for messages"""
    message_type: MessageTypeEnum = Field(..., description="Type of message")
    subject: Optional[str] = Field(None, max_length=200, description="Message subject")
    content: str = Field(..., max_length=5000, description="Message content")
    
    # Participants
    sender_user_id: PositiveInt = Field(..., description="Sender user ID")
    recipient_user_ids: List[PositiveInt] = Field(..., description="Recipient user IDs")
    
    # Thread and conversation
    thread_id: Optional[str] = Field(None, description="Thread ID for conversation")
    parent_message_id: Optional[PositiveInt] = Field(None, description="Parent message ID for replies")
    
    # Content and formatting
    content_format: str = Field("text", description="Content format (text, html, markdown)")
    attachments: List[MessageAttachmentSchema] = Field([], description="Message attachments")
    
    # Context and metadata
    context_type: Optional[str] = Field(None, description="Context type (collaboration, support, etc.)")
    context_id: Optional[str] = Field(None, description="Context ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    # Message options
    priority: NotificationPriorityEnum = Field(NotificationPriorityEnum.NORMAL, description="Message priority")
    read_receipt_requested: bool = Field(False, description="Request read receipt")
    auto_delete_after: Optional[int] = Field(None, description="Auto-delete after hours")


class MessageCreateSchema(MessageBaseSchema):
    """Schema for creating messages"""
    # Delivery options
    send_immediately: bool = Field(True, description="Send immediately")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    
    # Notification options
    send_notification: bool = Field(True, description="Send notification to recipients")
    notification_channels: Optional[List[NotificationChannelEnum]] = Field(None, description="Notification channels")
    
    # Collaboration context
    collaboration_request_id: Optional[PositiveInt] = Field(None, description="Related collaboration request")
    content_id: Optional[PositiveInt] = Field(None, description="Related content ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_type": "collaboration_message",
                "subject": "Collaboration Proposal",
                "content": "Hi! I'd love to collaborate on your latest track...",
                "sender_user_id": 123,
                "recipient_user_ids": [456],
                "context_type": "collaboration",
                "send_immediately": True,
                "send_notification": True
            }
        }


class MessageResponseSchema(MessageBaseSchema):
    """Schema for message responses"""
    id: PositiveInt = Field(..., description="Unique message ID")
    message_reference: str = Field(..., description="Human-readable message reference")
    
    # Status and delivery
    status: MessageStatusEnum = Field(..., description="Message status")
    delivered_to: List[PositiveInt] = Field([], description="User IDs who received the message")
    read_by: List[Dict[str, datetime]] = Field([], description="Read receipts")
    
    # Thread information
    is_reply: bool = Field(False, description="Whether this is a reply")
    reply_count: int = Field(0, description="Number of replies")
    thread_participants: List[PositiveInt] = Field([], description="Thread participant IDs")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    sent_at: Optional[datetime] = Field(None, description="Sent timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Interaction tracking
    view_count: int = Field(0, description="Number of views")
    reaction_counts: Dict[str, int] = Field({}, description="Reaction counts")
    
    # Moderation
    flagged: bool = Field(False, description="Whether message was flagged")
    moderated: bool = Field(False, description="Whether message was moderated")
    moderation_reason: Optional[str] = Field(None, description="Moderation reason")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "message_reference": "MSG-2024-001234",
                "message_type": "collaboration_message",
                "sender_user_id": 123,
                "recipient_user_ids": [456],
                "status": "delivered",
                "read_by": [{"user_id": 456, "read_at": "2024-08-24T11:00:00Z"}],
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class ConversationThreadSchema(BaseModel):
    """Schema for conversation threads"""
    thread_id: str = Field(..., description="Unique thread identifier")
    thread_title: Optional[str] = Field(None, description="Thread title")
    thread_type: str = Field(..., description="Type of conversation thread")
    
    # Participants
    participants: List[PositiveInt] = Field(..., description="Thread participant user IDs")
    created_by: PositiveInt = Field(..., description="Thread creator user ID")
    
    # Thread metadata
    message_count: int = Field(0, description="Number of messages in thread")
    last_message_id: Optional[PositiveInt] = Field(None, description="Last message ID")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Thread settings
    archived: bool = Field(False, description="Whether thread is archived")
    muted_by: List[PositiveInt] = Field([], description="User IDs who muted the thread")
    pinned: bool = Field(False, description="Whether thread is pinned")
    
    # Context
    context_type: Optional[str] = Field(None, description="Context type")
    context_id: Optional[str] = Field(None, description="Context ID")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "THR-2024-001234",
                "thread_title": "Electronic Track Collaboration",
                "thread_type": "collaboration",
                "participants": [123, 456],
                "created_by": 123,
                "message_count": 15,
                "archived": False,
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class NotificationBatchSchema(BaseModel):
    """Schema for batch notification operations"""
    batch_id: str = Field(..., description="Unique batch identifier")
    notifications: List[NotificationCreateSchema] = Field(..., description="Notifications to send")
    batch_options: Optional[Dict[str, Any]] = Field(None, description="Batch processing options")
    
    # Delivery settings
    stagger_delivery: bool = Field(False, description="Stagger delivery timing")
    stagger_interval: Optional[int] = Field(None, description="Stagger interval in seconds")
    max_concurrent: int = Field(100, description="Maximum concurrent deliveries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "BATCH-2024-001234",
                "notifications": [],
                "stagger_delivery": True,
                "stagger_interval": 5,
                "max_concurrent": 50
            }
        }


class CommunicationAnalyticsSchema(BaseModel):
    """Schema for communication analytics"""
    analytics_period: str = Field(..., description="Analytics period")
    
    # Notification metrics
    total_notifications_sent: int = Field(0, description="Total notifications sent")
    delivery_rate: float = Field(0.0, description="Delivery success rate")
    open_rate: float = Field(0.0, description="Notification open rate")
    click_rate: float = Field(0.0, description="Notification click rate")
    
    # Channel performance
    channel_performance: Dict[str, Dict[str, float]] = Field({}, description="Performance by channel")
    
    # Message metrics
    total_messages_sent: int = Field(0, description="Total messages sent")
    average_response_time: Optional[float] = Field(None, description="Average response time in hours")
    conversation_engagement: float = Field(0.0, description="Conversation engagement rate")
    
    # User engagement
    active_conversations: int = Field(0, description="Number of active conversations")
    user_satisfaction: Optional[float] = Field(None, description="User satisfaction score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analytics_period": "last_30_days",
                "total_notifications_sent": 15000,
                "delivery_rate": 0.98,
                "open_rate": 0.75,
                "click_rate": 0.12,
                "total_messages_sent": 5000,
                "active_conversations": 1200
            }
        }


# Export schemas
__all__ = [
    # Enums
    "NotificationTypeEnum",
    "NotificationPriorityEnum",
    "NotificationChannelEnum",
    "NotificationStatusEnum",
    "MessageTypeEnum",
    "MessageStatusEnum",
    "AttachmentTypeEnum",
    
    # Complex schemas
    "CommunicationPreferencesSchema",
    "NotificationTemplateSchema",
    "MessageAttachmentSchema",
    "ConversationThreadSchema",
    "NotificationBatchSchema",
    "CommunicationAnalyticsSchema",
    
    # Main schemas
    "NotificationBaseSchema",
    "NotificationCreateSchema",
    "NotificationResponseSchema",
    "MessageBaseSchema",
    "MessageCreateSchema",
    "MessageResponseSchema"
]
