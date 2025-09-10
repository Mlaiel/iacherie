"""Ainflue Core Platform - Notification System Core
=================================================

Enterprise-grade notification system providing multi-channel messaging,
template management, delivery tracking, user preferences, rate limiting,
and analytics for email, SMS, push notifications, and in-app messages.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import re
import hashlib
import time

# Setup logger
logger = logging.getLogger(__name__)

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

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
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RATE_LIMITED = "rate_limited"

class TemplateType(str, Enum):
    """Notification template types"""
    WELCOME = "welcome"
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    COLLABORATION_INVITE = "collaboration_invite"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    ANALYTICS_REPORT = "analytics_report"
    SECURITY_ALERT = "security_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CUSTOM = "custom"

@dataclass
class NotificationTemplate:
    """Notification template definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_type: TemplateType = TemplateType.CUSTOM
    channel: NotificationChannel = NotificationChannel.EMAIL
    subject_template: str = ""
    body_template: str = ""
    html_template: str = ""
    variables: List[str] = field(default_factory=list)
    default_data: Dict[str, Any] = field(default_factory=dict)
    localization: Dict[str, Dict[str, str]] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserPreferences:
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    channel_preferences: Dict[TemplateType, List[NotificationChannel]] = field(default_factory=dict)
    blocked_senders: Set[str] = field(default_factory=set)
    frequency_limits: Dict[str, int] = field(default_factory=dict)  # daily/weekly/monthly limits
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class NotificationRequest:
    """Notification request"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: Optional[str] = None
    template_type: Optional[TemplateType] = None
    channel: NotificationChannel = NotificationChannel.EMAIL
    recipient_id: str = ""
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_device_token: Optional[str] = None
    subject: Optional[str] = None
    body: str = ""
    html_body: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    sender_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class NotificationDelivery:
    """Notification delivery record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    channel: NotificationChannel = NotificationChannel.EMAIL
    recipient_id: str = ""
    recipient_address: str = ""
    status: NotificationStatus = NotificationStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)
    tracking_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class NotificationProvider(ABC):
    """Abstract notification provider"""
    
    def __init__(self, name: str, channel: NotificationChannel):
        self.name = name
        self.channel = channel
        self.active = True
        self.rate_limits = {}
        
    @abstractmethod
    async def send(self, delivery: NotificationDelivery) -> bool:
        """Send notification"""
        pass
    
    @abstractmethod
    async def get_delivery_status(self, tracking_id: str) -> Optional[str]:
        """Get delivery status from provider"""
        pass
    
    @abstractmethod
    def validate_recipient(self, address: str) -> bool:
        """Validate recipient address"""
        pass

class EmailProvider(NotificationProvider):
    """Email notification provider"""
    
    def __init__(self, name: str = "EmailProvider"):
        super().__init__(name, NotificationChannel.EMAIL)
        
    async def send(self, delivery: NotificationDelivery) -> bool:
        """Send email notification"""
        try:
            # Simulate email sending
            await asyncio.sleep(0.1)
            
            # Validate email address
            if not self.validate_recipient(delivery.recipient_address):
                delivery.error_message = "Invalid email address"
                delivery.error_code = "INVALID_EMAIL"
                return False
            
            # Simulate successful sending
            delivery.tracking_id = f"email_{uuid.uuid4().hex[:16]}"
            delivery.sent_at = datetime.utcnow()
            delivery.status = NotificationStatus.SENT
            
            logger.info(f"Email sent to {delivery.recipient_address}")
            return True
            
        except Exception as e:
            delivery.error_message = str(e)
            delivery.error_code = "SEND_FAILED"
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def get_delivery_status(self, tracking_id: str) -> Optional[str]:
        """Get email delivery status"""
        # Simulate status check
        await asyncio.sleep(0.05)
        return NotificationStatus.DELIVERED.value
    
    def validate_recipient(self, address: str) -> bool:
        """Validate email address"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, address) is not None

class SMSProvider(NotificationProvider):
    """SMS notification provider"""
    
    def __init__(self, name: str = "SMSProvider"):
        super().__init__(name, NotificationChannel.SMS)
        
    async def send(self, delivery: NotificationDelivery) -> bool:
        """Send SMS notification"""
        try:
            # Simulate SMS sending
            await asyncio.sleep(0.2)
            
            # Validate phone number
            if not self.validate_recipient(delivery.recipient_address):
                delivery.error_message = "Invalid phone number"
                delivery.error_code = "INVALID_PHONE"
                return False
            
            # Simulate successful sending
            delivery.tracking_id = f"sms_{uuid.uuid4().hex[:16]}"
            delivery.sent_at = datetime.utcnow()
            delivery.status = NotificationStatus.SENT
            
            logger.info(f"SMS sent to {delivery.recipient_address}")
            return True
            
        except Exception as e:
            delivery.error_message = str(e)
            delivery.error_code = "SEND_FAILED"
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    async def get_delivery_status(self, tracking_id: str) -> Optional[str]:
        """Get SMS delivery status"""
        # Simulate status check
        await asyncio.sleep(0.05)
        return NotificationStatus.DELIVERED.value
    
    def validate_recipient(self, address: str) -> bool:
        """Validate phone number"""
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(phone_pattern, address) is not None

class PushProvider(NotificationProvider):
    """Push notification provider"""
    
    def __init__(self, name: str = "PushProvider"):
        super().__init__(name, NotificationChannel.PUSH)
        
    async def send(self, delivery: NotificationDelivery) -> bool:
        """Send push notification"""
        try:
            # Simulate push notification sending
            await asyncio.sleep(0.1)
            
            # Validate device token
            if not self.validate_recipient(delivery.recipient_address):
                delivery.error_message = "Invalid device token"
                delivery.error_code = "INVALID_TOKEN"
                return False
            
            # Simulate successful sending
            delivery.tracking_id = f"push_{uuid.uuid4().hex[:16]}"
            delivery.sent_at = datetime.utcnow()
            delivery.status = NotificationStatus.SENT
            
            logger.info(f"Push notification sent to device {delivery.recipient_address}")
            return True
            
        except Exception as e:
            delivery.error_message = str(e)
            delivery.error_code = "SEND_FAILED"
            logger.error(f"Failed to send push notification: {str(e)}")
            return False
    
    async def get_delivery_status(self, tracking_id: str) -> Optional[str]:
        """Get push notification delivery status"""
        # Simulate status check
        await asyncio.sleep(0.05)
        return NotificationStatus.DELIVERED.value
    
    def validate_recipient(self, address: str) -> bool:
        """Validate device token"""
        # Simple validation for device token (should be hex string)
        return len(address) >= 32 and all(c in '0123456789abcdefABCDEF' for c in address)

class TemplateEngine:
    """Notification template engine"""
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default notification templates"""
        default_templates = [
            NotificationTemplate(
                id="welcome_email",
                name="Welcome Email",
                template_type=TemplateType.WELCOME,
                channel=NotificationChannel.EMAIL,
                subject_template="Welcome to Ainflue, {{user_name}}!",
                body_template="Welcome to Ainflue! We're excited to have you join our creator community.",
                html_template="<h1>Welcome to Ainflue!</h1><p>Hello {{user_name}}, we're excited to have you join our creator community.</p>",
                variables=["user_name", "user_email"]
            ),
            NotificationTemplate(
                id="verification_email",
                name="Email Verification",
                template_type=TemplateType.VERIFICATION,
                channel=NotificationChannel.EMAIL,
                subject_template="Verify your Ainflue account",
                body_template="Please verify your email address by clicking this link: {{verification_link}}",
                html_template="<p>Please verify your email address by <a href='{{verification_link}}'>clicking here</a>.</p>",
                variables=["verification_link", "user_name"]
            ),
            NotificationTemplate(
                id="content_approved",
                name="Content Approved",
                template_type=TemplateType.CONTENT_APPROVED,
                channel=NotificationChannel.IN_APP,
                subject_template="Your content has been approved!",
                body_template="Great news! Your content '{{content_title}}' has been approved and is now live.",
                variables=["content_title", "content_url"]
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
    
    def register_template(self, template: NotificationTemplate):
        """Register notification template"""
        self.templates[template.id] = template
        logger.info(f"Registered template: {template.name}")
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def render_template(self, template_id: str, data: Dict[str, Any], 
                       language: str = "en") -> Dict[str, str]:
        """Render template with data"""
        template = self.templates.get(template_id)
        if not template:
            raise Exception(f"Template not found: {template_id}")
        
        # Get localized templates if available
        if language in template.localization:
            localized = template.localization[language]
            subject_template = localized.get('subject', template.subject_template)
            body_template = localized.get('body', template.body_template)
            html_template = localized.get('html', template.html_template)
        else:
            subject_template = template.subject_template
            body_template = template.body_template
            html_template = template.html_template
        
        # Merge default data with provided data
        render_data = {**template.default_data, **data}
        
        # Simple template rendering (replace {{variable}} with values)
        subject = self._render_string(subject_template, render_data)
        body = self._render_string(body_template, render_data)
        html_body = self._render_string(html_template, render_data) if html_template else None
        
        return {
            'subject': subject,
            'body': body,
            'html_body': html_body
        }
    
    def _render_string(self, template: str, data: Dict[str, Any]) -> str:
        """Render template string with data"""
        result = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

class RateLimiter:
    """Rate limiter for notifications"""
    
    def __init__(self):
        self.limits: Dict[str, Dict[str, Any]] = {}
        self.counters: Dict[str, Dict[str, int]] = {}
        self.reset_times: Dict[str, Dict[str, datetime]] = {}
    
    def set_limit(self, key: str, limit: int, window_seconds: int):
        """Set rate limit for a key"""
        self.limits[key] = {
            'limit': limit,
            'window_seconds': window_seconds
        }
    
    async def check_limit(self, key: str, identifier: str) -> bool:
        """Check if request is within rate limit"""
        if key not in self.limits:
            return True
        
        limit_config = self.limits[key]
        now = datetime.utcnow()
        
        # Initialize counters if not exists
        if key not in self.counters:
            self.counters[key] = {}
            self.reset_times[key] = {}
        
        # Check if window has expired
        if identifier in self.reset_times[key]:
            if now >= self.reset_times[key][identifier]:
                self.counters[key][identifier] = 0
                self.reset_times[key][identifier] = now + timedelta(seconds=limit_config['window_seconds'])
        else:
            self.counters[key][identifier] = 0
            self.reset_times[key][identifier] = now + timedelta(seconds=limit_config['window_seconds'])
        
        # Check limit
        current_count = self.counters[key].get(identifier, 0)
        if current_count >= limit_config['limit']:
            return False
        
        # Increment counter
        self.counters[key][identifier] = current_count + 1
        return True

class NotificationSystemCore:
    """Core notification system"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.providers: Dict[NotificationChannel, List[NotificationProvider]] = {}
        self.template_engine = TemplateEngine()
        self.rate_limiter = RateLimiter()
        self.user_preferences: Dict[str, UserPreferences] = {}
        self.delivery_queue: List[NotificationDelivery] = []
        self.deliveries: Dict[str, NotificationDelivery] = {}
        self.processing_tasks: List[asyncio.Task] = []
        self.is_running = False
        self.metrics = {
            'notifications_sent': 0,
            'notifications_delivered': 0,
            'notifications_failed': 0,
            'rate_limited': 0,
            'template_renders': 0,
            'total_processing_time': 0.0
        }
        
        # Initialize default providers
        self._initialize_providers()
        
        # Setup default rate limits
        self._setup_rate_limits()
        
        logger.info(f"Notification System Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize notification system"""
        try:
            logger.info("Notification System Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Notification System Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start notification system"""
        try:
            self.is_running = True
            
            # Start processing workers
            for i in range(3):  # 3 worker tasks
                task = asyncio.create_task(self._notification_processor(f"worker_{i}"))
                self.processing_tasks.append(task)
            
            logger.info("Notification System Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Notification System Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop notification system"""
        try:
            self.is_running = False
            
            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()
            
            if self.processing_tasks:
                await asyncio.gather(*self.processing_tasks, return_exceptions=True)
            
            self.processing_tasks.clear()
            logger.info("Notification System Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Notification System Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if workers are running
            active_workers = len([task for task in self.processing_tasks if not task.done()])
            if self.is_running and active_workers == 0:
                logger.warning("No active notification workers")
                return False
            
            # Check queue size
            if len(self.delivery_queue) > 10000:
                logger.warning("Notification queue is overloaded")
                return False
            
            # Check provider availability
            for channel, providers in self.providers.items():
                if not any(provider.active for provider in providers):
                    logger.warning(f"No active providers for channel {channel.value}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def _initialize_providers(self):
        """Initialize notification providers"""
        # Email providers
        self.providers[NotificationChannel.EMAIL] = [EmailProvider()]
        
        # SMS providers
        self.providers[NotificationChannel.SMS] = [SMSProvider()]
        
        # Push notification providers
        self.providers[NotificationChannel.PUSH] = [PushProvider()]
        
        # In-app notification (handled internally)
        self.providers[NotificationChannel.IN_APP] = []
    
    def _setup_rate_limits(self):
        """Setup default rate limits"""
        # Per user limits
        self.rate_limiter.set_limit("user_email_hourly", 10, 3600)  # 10 emails per hour per user
        self.rate_limiter.set_limit("user_sms_daily", 5, 86400)     # 5 SMS per day per user
        self.rate_limiter.set_limit("user_push_hourly", 50, 3600)   # 50 push notifications per hour per user
        
        # Global limits
        self.rate_limiter.set_limit("global_email_per_minute", 1000, 60)  # 1000 emails per minute globally
        self.rate_limiter.set_limit("global_sms_per_minute", 100, 60)     # 100 SMS per minute globally
    
    async def _notification_processor(self, worker_id: str):
        """Background notification processor"""
        while self.is_running:
            try:
                if self.delivery_queue:
                    delivery = self.delivery_queue.pop(0)
                    await self._process_delivery(delivery)
                else:
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Notification processor {worker_id} error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_delivery(self, delivery: NotificationDelivery):
        """Process notification delivery"""
        try:
            start_time = time.time()
            
            # Check rate limits
            rate_limit_key = f"user_{delivery.channel.value}_hourly"
            if not await self.rate_limiter.check_limit(rate_limit_key, delivery.recipient_id):
                delivery.status = NotificationStatus.RATE_LIMITED
                delivery.error_message = "Rate limit exceeded"
                self.metrics['rate_limited'] += 1
                logger.warning(f"Rate limit exceeded for user {delivery.recipient_id} on {delivery.channel.value}")
                return
            
            # Get providers for channel
            providers = self.providers.get(delivery.channel, [])
            active_providers = [p for p in providers if p.active]
            
            if not active_providers:
                delivery.status = NotificationStatus.FAILED
                delivery.error_message = f"No active providers for channel {delivery.channel.value}"
                self.metrics['notifications_failed'] += 1
                return
            
            # Try sending with first available provider
            provider = active_providers[0]
            delivery.status = NotificationStatus.SENDING
            delivery.attempts += 1
            
            success = await provider.send(delivery)
            
            processing_time = (time.time() - start_time) * 1000
            self.metrics['total_processing_time'] += processing_time
            
            if success:
                self.metrics['notifications_sent'] += 1
                logger.info(f"Notification sent successfully: {delivery.id}")
                
                # Schedule delivery status check
                asyncio.create_task(self._check_delivery_status(delivery, provider))
            else:
                delivery.status = NotificationStatus.FAILED
                delivery.failed_at = datetime.utcnow()
                self.metrics['notifications_failed'] += 1
                
                # Retry if attempts remaining
                if delivery.attempts < delivery.max_attempts:
                    delivery.status = NotificationStatus.PENDING
                    self.delivery_queue.append(delivery)
                    logger.info(f"Scheduling retry for delivery {delivery.id} (attempt {delivery.attempts + 1})")
            
            # Store delivery record
            self.deliveries[delivery.id] = delivery
            
        except Exception as e:
            delivery.status = NotificationStatus.FAILED
            delivery.error_message = str(e)
            delivery.failed_at = datetime.utcnow()
            self.metrics['notifications_failed'] += 1
            logger.error(f"Failed to process delivery {delivery.id}: {str(e)}")
    
    async def _check_delivery_status(self, delivery: NotificationDelivery, provider: NotificationProvider):
        """Check delivery status after sending"""
        try:
            # Wait a bit before checking status
            await asyncio.sleep(5)
            
            if delivery.tracking_id:
                status = await provider.get_delivery_status(delivery.tracking_id)
                if status:
                    if status == NotificationStatus.DELIVERED.value:
                        delivery.status = NotificationStatus.DELIVERED
                        delivery.delivered_at = datetime.utcnow()
                        self.metrics['notifications_delivered'] += 1
                    elif status in [NotificationStatus.FAILED.value]:
                        delivery.status = NotificationStatus.FAILED
                        delivery.failed_at = datetime.utcnow()
        except Exception as e:
            logger.error(f"Failed to check delivery status for {delivery.id}: {str(e)}")
    
    async def send_notification(self, request: NotificationRequest) -> str:
        """Send notification"""
        try:
            # Get user preferences
            preferences = self.user_preferences.get(request.recipient_id)
            
            # Check if user has notifications enabled for this channel
            if preferences and not self._is_channel_enabled(preferences, request.channel, request.template_type):
                logger.info(f"Notifications disabled for user {request.recipient_id} on channel {request.channel.value}")
                return request.id
            
            # Check quiet hours
            if preferences and self._is_in_quiet_hours(preferences):
                # Schedule for later
                if not request.scheduled_at:
                    request.scheduled_at = self._get_next_allowed_time(preferences)
                logger.info(f"Notification scheduled for quiet hours: {request.scheduled_at}")
            
            # Render template if specified
            if request.template_id:
                language = preferences.language if preferences else "en"
                rendered = self.template_engine.render_template(request.template_id, request.data, language)
                request.subject = rendered['subject']
                request.body = rendered['body']
                request.html_body = rendered['html_body']
                self.metrics['template_renders'] += 1
            
            # Get recipient address based on channel
            recipient_address = self._get_recipient_address(request)
            if not recipient_address:
                raise Exception(f"No recipient address for channel {request.channel.value}")
            
            # Create delivery record
            delivery = NotificationDelivery(
                request_id=request.id,
                channel=request.channel,
                recipient_id=request.recipient_id,
                recipient_address=recipient_address,
                metadata={
                    'subject': request.subject,
                    'body': request.body,
                    'html_body': request.html_body,
                    'priority': request.priority.value,
                    'template_id': request.template_id
                }
            )
            
            # Add to delivery queue
            if request.scheduled_at and request.scheduled_at > datetime.utcnow():
                # Schedule for later (simplified - in real implementation would use a scheduler)
                logger.info(f"Notification {request.id} scheduled for {request.scheduled_at}")
            else:
                self.delivery_queue.append(delivery)
            
            logger.info(f"Notification {request.id} queued for delivery")
            return request.id
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            raise
    
    def _is_channel_enabled(self, preferences: UserPreferences, channel: NotificationChannel, 
                           template_type: Optional[TemplateType]) -> bool:
        """Check if channel is enabled for user"""
        # Check global channel preferences
        if channel == NotificationChannel.EMAIL and not preferences.email_enabled:
            return False
        elif channel == NotificationChannel.SMS and not preferences.sms_enabled:
            return False
        elif channel == NotificationChannel.PUSH and not preferences.push_enabled:
            return False
        elif channel == NotificationChannel.IN_APP and not preferences.in_app_enabled:
            return False
        
        # Check template-specific channel preferences
        if template_type and template_type in preferences.channel_preferences:
            allowed_channels = preferences.channel_preferences[template_type]
            return channel in allowed_channels
        
        return True
    
    def _is_in_quiet_hours(self, preferences: UserPreferences) -> bool:
        """Check if current time is in user's quiet hours"""
        if not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False
        
        # Simplified quiet hours check (assumes same timezone as server)
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        
        start_time = preferences.quiet_hours_start
        end_time = preferences.quiet_hours_end
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            # Quiet hours span midnight
            return current_time >= start_time or current_time <= end_time
    
    def _get_next_allowed_time(self, preferences: UserPreferences) -> datetime:
        """Get next allowed time outside quiet hours"""
        # Simplified - schedule for end of quiet hours
        now = datetime.utcnow()
        if preferences.quiet_hours_end:
            hour, minute = map(int, preferences.quiet_hours_end.split(':'))
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time
        return now + timedelta(hours=1)
    
    def _get_recipient_address(self, request: NotificationRequest) -> Optional[str]:
        """Get recipient address for notification channel"""
        if request.channel == NotificationChannel.EMAIL:
            return request.recipient_email
        elif request.channel == NotificationChannel.SMS:
            return request.recipient_phone
        elif request.channel == NotificationChannel.PUSH:
            return request.recipient_device_token
        elif request.channel == NotificationChannel.IN_APP:
            return request.recipient_id  # Use user ID for in-app notifications
        return None
    
    def register_provider(self, channel: NotificationChannel, provider: NotificationProvider):
        """Register notification provider"""
        if channel not in self.providers:
            self.providers[channel] = []
        self.providers[channel].append(provider)
        logger.info(f"Registered {provider.name} for channel {channel.value}")
    
    def register_template(self, template: NotificationTemplate):
        """Register notification template"""
        self.template_engine.register_template(template)
    
    def set_user_preferences(self, user_id: str, preferences: UserPreferences):
        """Set user notification preferences"""
        preferences.user_id = user_id
        preferences.updated_at = datetime.utcnow()
        self.user_preferences[user_id] = preferences
        logger.info(f"Updated preferences for user {user_id}")
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user notification preferences"""
        return self.user_preferences.get(user_id)
    
    def get_delivery_status(self, delivery_id: str) -> Optional[NotificationDelivery]:
        """Get delivery status"""
        return self.deliveries.get(delivery_id)
    
    def get_delivery_stats(self, user_id: Optional[str] = None, 
                          channel: Optional[NotificationChannel] = None,
                          days: int = 30) -> Dict[str, Any]:
        """Get delivery statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        filtered_deliveries = []
        for delivery in self.deliveries.values():
            if delivery.created_at < since:
                continue
            if user_id and delivery.recipient_id != user_id:
                continue
            if channel and delivery.channel != channel:
                continue
            filtered_deliveries.append(delivery)
        
        total = len(filtered_deliveries)
        sent = len([d for d in filtered_deliveries if d.status == NotificationStatus.SENT])
        delivered = len([d for d in filtered_deliveries if d.status == NotificationStatus.DELIVERED])
        failed = len([d for d in filtered_deliveries if d.status == NotificationStatus.FAILED])
        rate_limited = len([d for d in filtered_deliveries if d.status == NotificationStatus.RATE_LIMITED])
        
        return {
            'total_notifications': total,
            'sent': sent,
            'delivered': delivered,
            'failed': failed,
            'rate_limited': rate_limited,
            'delivery_rate': delivered / total if total > 0 else 0,
            'failure_rate': failed / total if total > 0 else 0,
            'period_days': days
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        avg_processing_time = (
            self.metrics['total_processing_time'] / self.metrics['notifications_sent']
            if self.metrics['notifications_sent'] > 0 else 0
        )
        
        return {
            'level': self.level,
            'notifications_sent': self.metrics['notifications_sent'],
            'notifications_delivered': self.metrics['notifications_delivered'],
            'notifications_failed': self.metrics['notifications_failed'],
            'rate_limited': self.metrics['rate_limited'],
            'template_renders': self.metrics['template_renders'],
            'avg_processing_time_ms': avg_processing_time,
            'delivery_rate': (
                self.metrics['notifications_delivered'] / self.metrics['notifications_sent']
                if self.metrics['notifications_sent'] > 0 else 0
            ),
            'queue_size': len(self.delivery_queue),
            'total_deliveries': len(self.deliveries),
            'registered_templates': len(self.template_engine.templates),
            'user_preferences': len(self.user_preferences),
            'active_providers': {
                channel.value: len([p for p in providers if p.active])
                for channel, providers in self.providers.items()
            },
            'supported_channels': [channel.value for channel in NotificationChannel],
            'is_running': self.is_running
        }

# Global instance
notification_system_core = NotificationSystemCore()

# Convenience functions
async def send_notification(recipient_id: str, channel: NotificationChannel, 
                           subject: str, body: str, template_id: Optional[str] = None,
                           data: Optional[Dict[str, Any]] = None,
                           priority: NotificationPriority = NotificationPriority.NORMAL) -> str:
    """Send notification"""
    request = NotificationRequest(
        recipient_id=recipient_id,
        channel=channel,
        subject=subject,
        body=body,
        template_id=template_id,
        data=data or {},
        priority=priority
    )
    return await notification_system_core.send_notification(request)

def set_user_notification_preferences(user_id: str, email_enabled: bool = True,
                                     sms_enabled: bool = False, push_enabled: bool = True) -> bool:
    """Set user notification preferences"""
    preferences = UserPreferences(
        user_id=user_id,
        email_enabled=email_enabled,
        sms_enabled=sms_enabled,
        push_enabled=push_enabled
    )
    notification_system_core.set_user_preferences(user_id, preferences)
    return True

def get_notification_status(delivery_id: str) -> Optional[NotificationDelivery]:
    """Get notification delivery status"""
    return notification_system_core.get_delivery_status(delivery_id)

# Module exports
__all__ = [
    "NotificationSystemCore", "NotificationRequest", "NotificationDelivery",
    "NotificationTemplate", "UserPreferences", "NotificationProvider",
    "EmailProvider", "SMSProvider", "PushProvider", "TemplateEngine", "RateLimiter",
    "NotificationChannel", "NotificationPriority", "NotificationStatus", "TemplateType",
    "notification_system_core", "send_notification", "set_user_notification_preferences",
    "get_notification_status"
]

logger.info("Notification System Core module loaded")