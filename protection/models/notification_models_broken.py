"""
Notification Models - Protection System
======================================

Data models for notification system and multi-channel delivery.

🧠 Lead Dev IA: Intelligent notification routing and delivery optimization models
🏗️ Backend Senior: Scalable notification data architecture with real-time tracking
🤖 ML Engineer: Predictive notification analytics and user preference modeling
🗄️ DBA: Optimized notification storage and high-performance delivery tracking
🔒 Sécurité: Secure notification data handling and encrypted delivery channels
🌐 Microservices: Distributed notification services with event-driven architecture
🎵 Audio Engineer: Audio notification models and voice synthesis configurations
⚙️ DevOps: Notification monitoring and auto-scaling infrastructure models
💡 IA Prompt Engineer: AI-generated notification content and intelligent messaging

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL NOTICE: This code is proprietary and protected by copyright law.
Unauthorized use, reproduction, or distribution is strictly prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Import base model utilities but don't inherit to avoid dataclass issues
from .base_models import BaseModel

class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    DISCORD = "discord"
    SLACK = "slack"
    TELEGRAM = "telegram"
    PUSH = "push"
    VOICE = "voice"
    IN_APP = "in_app"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class DeliveryStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TemplateType(Enum):
    """Notification template types"""
    ALERT = "alert"
    REPORT = "report"
    REMINDER = "reminder"
    CONFIRMATION = "confirmation"
    MARKETING = "marketing"
    SYSTEM = "system"
    SECURITY = "security"
    LEGAL = "legal"

@dataclass
class NotificationTemplate:
    """Notification message template"""
    # Required fields first
    name: str
    template_type: TemplateType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    
    # Optional fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    html_template: Optional[str] = None
    
    # Localization
    language: str = "en"
    variables: List[str] = field(default_factory=list)
    
    # Formatting options
    use_markdown: bool = False
    use_html: bool = True
    include_attachments: bool = False
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    version: str = "1.0"

@dataclass
class NotificationRule:
    """Notification delivery rules and conditions"""
    # Required fields
    name: str
    template_name: str
    
    # Base model fields  
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Optional fields with defaults
    description: Optional[str] = None
    
    # Trigger conditions
    alert_types: List[str] = field(default_factory=list)
    severity_levels: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    
    # Delivery settings
    channels: List[NotificationChannel] = field(default_factory=list)
    template_name: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    
    # Recipients
    user_groups: List[str] = field(default_factory=list)
    specific_users: List[str] = field(default_factory=list)
    external_recipients: List[str] = field(default_factory=list)
    
    # Timing constraints
    delay_seconds: int = 0
    rate_limit_per_hour: Optional[int] = None
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None
    timezone: str = "UTC"
    
    # Conditions
    is_active: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    
    # Channel preferences
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    
    # Frequency settings
    digest_frequency: str = "daily"  # immediate, hourly, daily, weekly
    max_notifications_per_hour: int = 10
    batch_notifications: bool = False
    
    # Priority filters
    min_priority: NotificationPriority = NotificationPriority.LOW
    critical_only: bool = False
    
    # Content filters
    alert_types: List[str] = field(default_factory=list)
    excluded_platforms: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Timing preferences
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"
    
    # Contact information
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    discord_id: Optional[str] = None
    slack_id: Optional[str] = None

@dataclass
class DeliveryAttempt(BaseModel):
    """Individual delivery attempt record"""
    notification_id: str
    channel: NotificationChannel
    recipient: str
    
    # Attempt details
    attempt_number: int = 1
    status: DeliveryStatus = DeliveryStatus.PENDING
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    
    # Results
    success: bool = False
    error_message: Optional[str] = None
    response_code: Optional[str] = None
    external_id: Optional[str] = None  # ID from external service
    
    # Metadata
    provider_used: Optional[str] = None
    cost: Optional[float] = None
    delivery_time_ms: Optional[int] = None

@dataclass
class NotificationHistory(BaseModel):
    """Notification delivery history and tracking"""
    notification_id: str
    
    # Source information
    alert_id: Optional[str] = None
    rule_id: str
    template_id: str
    triggered_by: str
    
    # Content
    subject: str
    content: str
    variables_used: Dict[str, Any] = field(default_factory=dict)
    
    # Recipients and delivery
    total_recipients: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    delivery_attempts: List[DeliveryAttempt] = field(default_factory=list)
    
    # Status tracking
    overall_status: DeliveryStatus = DeliveryStatus.PENDING
    priority: NotificationPriority = NotificationPriority.MEDIUM
    
    # Timing
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Performance metrics
    total_processing_time: Optional[int] = None  # milliseconds
    total_cost: Optional[float] = None
    
    # Engagement tracking
    opened_count: int = 0
    clicked_count: int = 0
    unsubscribed_count: int = 0

@dataclass
class NotificationAnalytics(BaseModel):
    """📊 Notification analytics and metrics"""
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    # Volume metrics
    total_notifications_sent: int = 0
    total_recipients: int = 0
    total_delivery_attempts: int = 0
    
    # Success metrics
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    delivery_rate: float = 0.0
    
    # Channel breakdown
    channel_metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Performance metrics
    avg_delivery_time_ms: Optional[float] = None
    avg_processing_time_ms: Optional[float] = None
    total_cost: Optional[float] = None
    
    # Engagement metrics
    open_rate: float = 0.0
    click_rate: float = 0.0
    unsubscribe_rate: float = 0.0
    
    # Error analysis
    top_errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_rate: float = 0.0
    
    def calculate_metrics(self) -> None:
        """🤖 ML Engineer: Calculate derived metrics"""
        if self.total_delivery_attempts > 0:
            self.delivery_rate = self.successful_deliveries / self.total_delivery_attempts
            self.retry_rate = (self.total_delivery_attempts - self.total_notifications_sent) / self.total_delivery_attempts
        
        if self.successful_deliveries > 0:
            self.open_rate = self.open_rate if hasattr(self, '_open_count') else 0.0
            self.click_rate = self.click_rate if hasattr(self, '_click_count') else 0.0

@dataclass
class NotificationQueue(BaseModel):
    """🌐 Microservices: Notification queue management"""
    
    # Queue identification
    queue_name: str
    channel: NotificationChannel
    priority: NotificationPriority
    
    # Queue status
    pending_count: int = 0
    processing_count: int = 0
    failed_count: int = 0
    
    # Performance metrics
    avg_processing_time: Optional[float] = None
    throughput_per_minute: Optional[float] = None
    error_rate: float = 0.0
    
    # Configuration
    max_retries: int = 3
    retry_delay_seconds: int = 60
    batch_size: int = 100
    rate_limit_per_second: Optional[int] = None
    
    # Health status
    is_healthy: bool = True
    last_processed_at: Optional[datetime] = None
    last_error: Optional[str] = None

@dataclass
class NotificationProvider(BaseModel):
    """External notification service provider configuration"""
    
    # Provider details
    name: str
    provider_type: str  # smtp, twilio, sendgrid, etc.
    channel: NotificationChannel
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Status and limits
    is_active: bool = True
    rate_limit_per_minute: Optional[int] = None
    monthly_quota: Optional[int] = None
    monthly_usage: int = 0
    
    # Health monitoring
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    health_score: float = 100.0
    
    # Performance metrics
    avg_response_time_ms: Optional[float] = None
    success_rate: float = 100.0
    total_sent: int = 0
    total_failed: int = 0
    
    # Cost tracking
    cost_per_notification: Optional[float] = None
    total_cost: float = 0.0