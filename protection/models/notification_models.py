#!/usr/bin/env python3
"""
🔔 Notification Models - Protection Models Module
===============================================

Data models for notification system in protection layer.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Models Module
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

# Define chromaprint variable for audio fingerprinting
chromaprint = "chromaprint"

class NotificationType(str, Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    IN_APP = "in_app"

class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Alias for backwards compatibility
DeliveryStatus = NotificationStatus

class NotificationHistory(BaseModel):
    """Notification history tracking"""
    id: str
    notification_id: str
    user_id: str
    type: NotificationType
    subject: str
    content: str
    status: NotificationStatus
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    extra_data: Dict[str, Any] = Field(default_factory=dict)

@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    id: str
    type: NotificationType
    address: str  # email, phone, webhook URL, etc.
    name: Optional[str] = None
    preferences: Dict[str, Any] = None
    extra_data: Dict[str, Any] = None

@dataclass
class NotificationTemplate:
    """Notification template"""
    id: str
    name: str
    type: NotificationType
    subject_template: str
    content_template: str
    variables: List[str] = None
    default_priority: NotificationPriority = NotificationPriority.NORMAL
    created_at: datetime = None
    updated_at: datetime = None

class NotificationRequest(BaseModel):
    """Request to send a notification"""
    type: NotificationType
    recipients: List[str] = Field(..., min_items=1)
    subject: str
    content: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    """Response from notification sending"""
    notification_id: str
    status: NotificationStatus
    type: NotificationType
    recipients_count: int
    sent_count: int = 0
    failed_count: int = 0
    message: Optional[str] = None
    sent_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None

@dataclass
class NotificationLog:
    """Log entry for a notification"""
    id: str
    notification_id: str
    recipient_id: str
    type: NotificationType
    status: NotificationStatus
    subject: str
    content: str
    priority: NotificationPriority
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    extra_data: Dict[str, Any] = None

class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    in_app_notifications: bool = True
    notification_types: Dict[str, bool] = Field(default_factory=dict)
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationChannel(BaseModel):
    """Notification channel configuration"""
    id: str
    name: str
    type: NotificationType
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    rate_limit: Optional[int] = None  # messages per minute
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationStats(BaseModel):
    """Notification statistics"""
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    delivery_rate: float = 0.0
    average_delivery_time: float = 0.0  # seconds
    by_type: Dict[NotificationType, Dict[str, int]] = Field(default_factory=dict)
    by_priority: Dict[NotificationPriority, Dict[str, int]] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class NotificationBatch:
    """Batch of notifications to send"""
    id: str
    name: str
    notifications: List[NotificationRequest]
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    created_at: datetime = None
    status: str = "pending"
    progress: Dict[str, int] = None

class NotificationRule(BaseModel):
    """Notification rule for automated sending"""
    id: str
    name: str
    trigger: str  # event that triggers the notification
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    template_id: str
    recipients_query: str  # query to find recipients
    priority: NotificationPriority = NotificationPriority.NORMAL
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Export all models
__all__ = [
    'NotificationType',
    'NotificationPriority', 
    'NotificationStatus',
    'DeliveryStatus',  # Alias for compatibility
    'NotificationRecipient',
    'NotificationTemplate',
    'NotificationRequest',
    'NotificationResponse',
    'NotificationLog',
    'NotificationHistory',
    'NotificationPreferences',
    'NotificationChannel',
    'NotificationStats',
    'NotificationBatch',
    'NotificationRule'
]