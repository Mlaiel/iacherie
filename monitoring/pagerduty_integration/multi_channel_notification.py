"""
Multi-Channel Notification System for IA Chérie Platform
Intelligent notification delivery across multiple channels

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import re
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    IN_APP = "in_app"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = "critical"      # Immediate delivery, all channels
    HIGH = "high"              # Fast delivery, primary channels
    MEDIUM = "medium"          # Normal delivery, preferred channels
    LOW = "low"                # Batch delivery, minimal channels
    INFORMATIONAL = "informational"  # Best effort delivery


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"
    RESPONDED = "responded"
    IGNORED = "ignored"
    RATE_LIMITED = "rate_limited"


class NotificationType(Enum):
    """Types of notifications"""
    INCIDENT_ALERT = "incident_alert"
    INCIDENT_UPDATE = "incident_update"
    INCIDENT_RESOLVED = "incident_resolved"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_WARNING = "performance_warning"
    CREATOR_MILESTONE = "creator_milestone"
    COLLABORATION_REQUEST = "collaboration_request"
    REVENUE_REPORT = "revenue_report"
    PLATFORM_ANNOUNCEMENT = "platform_announcement"


@dataclass
class NotificationPreferences:
    """User notification preferences"""
    user_id: str
    channels: Dict[NotificationChannel, bool]  # Channel enabled/disabled
    priority_routing: Dict[NotificationPriority, List[NotificationChannel]]
    type_routing: Dict[NotificationType, List[NotificationChannel]]
    quiet_hours: Dict[str, str]  # start_time -> end_time
    timezone: str
    frequency_limits: Dict[NotificationChannel, int]  # Max notifications per hour
    delivery_preferences: Dict[str, Any]
    emergency_contact: Optional[str]
    backup_channels: List[NotificationChannel]


@dataclass
class NotificationTemplate:
    """Notification message template"""
    template_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    rich_content_template: Optional[Dict[str, Any]]  # For Slack blocks, Teams cards
    variables: List[str]
    localization: Dict[str, Dict[str, str]]  # Language -> field -> translation
    formatting_rules: Dict[str, Any]
    character_limits: Dict[str, int]
    retry_policy: Dict[str, Any]


@dataclass
class NotificationMessage:
    """Individual notification message"""
    message_id: str
    user_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    channel: NotificationChannel
    subject: str
    content: str
    rich_content: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    status: NotificationStatus
    retry_count: int
    max_retries: int
    error_message: Optional[str]
    delivery_receipt: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]


@dataclass
class NotificationCampaign:
    """Bulk notification campaign"""
    campaign_id: str
    name: str
    notification_type: NotificationType
    target_users: List[str]
    template_id: str
    priority: NotificationPriority
    scheduled_at: Optional[datetime]
    created_at: datetime
    created_by: str
    status: str  # draft, scheduled, sending, completed, failed
    progress: Dict[str, int]  # sent, delivered, failed counts
    delivery_stats: Dict[NotificationChannel, Dict[str, int]]
    completion_time: Optional[datetime]


@dataclass
class DeliveryAttempt:
    """Notification delivery attempt record"""
    attempt_id: str
    message_id: str
    channel: NotificationChannel
    attempted_at: datetime
    success: bool
    response_code: Optional[int]
    response_message: Optional[str]
    latency_ms: int
    retry_after: Optional[int]
    error_details: Optional[Dict[str, Any]]


class ChannelProvider:
    """Base class for notification channel providers"""
    
    def __init__(self, channel: NotificationChannel, config: Dict[str, Any]):
        self.channel = channel
        self.config = config
        self.rate_limiter = {}
        self.circuit_breaker = {"failures": 0, "last_failure": None, "is_open": False}
    
    async def send_message(self, message: NotificationMessage) -> DeliveryAttempt:
        """Send notification message through this channel"""
        raise NotImplementedError
    
    async def check_delivery_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Check delivery status of a message"""
        raise NotImplementedError
    
    def is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited"""
        now = datetime.utcnow()
        user_history = self.rate_limiter.get(user_id, deque(maxlen=100))
        
        # Remove old entries (older than 1 hour)
        while user_history and (now - user_history[0]).total_seconds() > 3600:
            user_history.popleft()
        
        # Check rate limit
        limit = self.config.get("hourly_rate_limit", 50)
        return len(user_history) >= limit
    
    def record_send_attempt(self, user_id: str):
        """Record a send attempt for rate limiting"""
        if user_id not in self.rate_limiter:
            self.rate_limiter[user_id] = deque(maxlen=100)
        self.rate_limiter[user_id].append(datetime.utcnow())
    
    def is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.circuit_breaker["is_open"]:
            return False
        
        # Reset circuit breaker after 5 minutes
        if self.circuit_breaker["last_failure"]:
            time_since_failure = (datetime.utcnow() - self.circuit_breaker["last_failure"]).total_seconds()
            if time_since_failure > 300:  # 5 minutes
                self.circuit_breaker = {"failures": 0, "last_failure": None, "is_open": False}
                return False
        
        return True
    
    def record_failure(self):
        """Record a delivery failure"""
        self.circuit_breaker["failures"] += 1
        self.circuit_breaker["last_failure"] = datetime.utcnow()
        
        # Open circuit breaker after 5 consecutive failures
        if self.circuit_breaker["failures"] >= 5:
            self.circuit_breaker["is_open"] = True


class EmailProvider(ChannelProvider):
    """Email notification provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.EMAIL, config)
    
    async def send_message(self, message: NotificationMessage) -> DeliveryAttempt:
        attempt_id = f"EMAIL-{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        try:
            # Simulate email sending
            await asyncio.sleep(0.1)  # Simulate API call latency
            
            # TODO: Integrate with actual email service (SendGrid, AWS SES, etc.)
            success = True  # Simulate success
            response_code = 200
            response_message = "Email queued for delivery"
            
            if success:
                self.circuit_breaker["failures"] = 0
            
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return DeliveryAttempt(
                attempt_id=attempt_id,
                message_id=message.message_id,
                channel=self.channel,
                attempted_at=start_time,
                success=success,
                response_code=response_code,
                response_message=response_message,
                latency_ms=latency_ms,
                retry_after=None,
                error_details=None
            )
            
        except Exception as e:
            self.record_failure()
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return DeliveryAttempt(
                attempt_id=attempt_id,
                message_id=message.message_id,
                channel=self.channel,
                attempted_at=start_time,
                success=False,
                response_code=500,
                response_message=str(e),
                latency_ms=latency_ms,
                retry_after=300,  # Retry after 5 minutes
                error_details={"exception": str(e)}
            )


class SlackProvider(ChannelProvider):
    """Slack notification provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.SLACK, config)
    
    async def send_message(self, message: NotificationMessage) -> DeliveryAttempt:
        attempt_id = f"SLACK-{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        try:
            # Simulate Slack API call
            await asyncio.sleep(0.2)
            
            # TODO: Integrate with Slack Web API
            success = True
            response_code = 200
            response_message = "Message sent to Slack"
            
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return DeliveryAttempt(
                attempt_id=attempt_id,
                message_id=message.message_id,
                channel=self.channel,
                attempted_at=start_time,
                success=success,
                response_code=response_code,
                response_message=response_message,
                latency_ms=latency_ms,
                retry_after=None,
                error_details=None
            )
            
        except Exception as e:
            self.record_failure()
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return DeliveryAttempt(
                attempt_id=attempt_id,
                message_id=message.message_id,
                channel=self.channel,
                attempted_at=start_time,
                success=False,
                response_code=500,
                response_message=str(e),
                latency_ms=latency_ms,
                retry_after=60,
                error_details={"exception": str(e)}
            )


class SMSProvider(ChannelProvider):
    """SMS notification provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(NotificationChannel.SMS, config)
    
    async def send_message(self, message: NotificationMessage) -> DeliveryAttempt:
        attempt_id = f"SMS-{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()
        
        try:
            # Simulate SMS sending
            await asyncio.sleep(0.3)
            
            # TODO: Integrate with SMS service (Twilio, AWS SNS, etc.)
            success = True
            response_code = 200
            response_message = "SMS sent"
            
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return DeliveryAttempt(
                attempt_id=attempt_id,
                message_id=message.message_id,
                channel=self.channel,
                attempted_at=start_time,
                success=success,
                response_code=response_code,
                response_message=response_message,
                latency_ms=latency_ms,
                retry_after=None,
                error_details=None
            )
            
        except Exception as e:
            self.record_failure()
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return DeliveryAttempt(
                attempt_id=attempt_id,
                message_id=message.message_id,
                channel=self.channel,
                attempted_at=start_time,
                success=False,
                response_code=500,
                response_message=str(e),
                latency_ms=latency_ms,
                retry_after=180,
                error_details={"exception": str(e)}
            )


class MultiChannelNotificationSystem:
    """
    Advanced multi-channel notification system
    Intelligent routing, delivery optimization, and fatigue prevention
    """
    
    def __init__(self):
        """Initialize the notification system"""
        self.providers = {}
        self.templates = {}
        self.user_preferences = {}
        self.pending_messages = {}
        self.delivery_history = defaultdict(list)
        self.campaigns = {}
        
        # Configuration
        self.config = self._load_default_config()
        
        # Initialize providers
        self._initialize_providers()
        
        # Load default templates
        self._load_default_templates()
        
        # Background tasks
        self.delivery_queue = asyncio.Queue()
        self.retry_queue = asyncio.Queue()
        
        logger.info("Multi-Channel Notification System initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "delivery_settings": {
                "max_concurrent_deliveries": 50,
                "retry_intervals": [60, 300, 900, 3600],  # 1m, 5m, 15m, 1h
                "max_retries": 3,
                "batch_size": 100,
                "delivery_timeout": 30
            },
            
            "fatigue_prevention": {
                "max_notifications_per_hour": 10,
                "max_notifications_per_day": 50,
                "quiet_hours_default": {"start": "22:00", "end": "08:00"},
                "cool_down_period_minutes": 5
            },
            
            "channel_config": {
                NotificationChannel.EMAIL: {
                    "enabled": True,
                    "hourly_rate_limit": 100,
                    "character_limit": 10000,
                    "priority": 1
                },
                NotificationChannel.SLACK: {
                    "enabled": True,
                    "hourly_rate_limit": 200,
                    "character_limit": 4000,
                    "priority": 2
                },
                NotificationChannel.SMS: {
                    "enabled": True,
                    "hourly_rate_limit": 20,
                    "character_limit": 160,
                    "priority": 3
                }
            },
            
            "emergency_escalation": {
                "enabled": True,
                "escalation_delay_minutes": 15,
                "max_escalation_levels": 3,
                "emergency_channels": [NotificationChannel.SMS, NotificationChannel.SLACK]
            }
        }
    
    def _initialize_providers(self):
        """Initialize notification channel providers"""
        try:
            # Email provider
            email_config = self.config["channel_config"][NotificationChannel.EMAIL]
            self.providers[NotificationChannel.EMAIL] = EmailProvider(email_config)
            
            # Slack provider
            slack_config = self.config["channel_config"][NotificationChannel.SLACK]
            self.providers[NotificationChannel.SLACK] = SlackProvider(slack_config)
            
            # SMS provider
            sms_config = self.config["channel_config"][NotificationChannel.SMS]
            self.providers[NotificationChannel.SMS] = SMSProvider(sms_config)
            
            logger.info(f"Initialized {len(self.providers)} notification providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
    
    def _load_default_templates(self):
        """Load default notification templates"""
        # Incident alert template
        self.templates["incident_alert_email"] = NotificationTemplate(
            template_id="incident_alert_email",
            notification_type=NotificationType.INCIDENT_ALERT,
            channel=NotificationChannel.EMAIL,
            subject_template="🚨 URGENT: {incident_type} - {service_name}",
            body_template="""
Dear {user_name},

We've detected a {incident_severity} incident affecting your Creator Economy platform:

Incident Details:
- Type: {incident_type}
- Service: {service_name}
- Started: {incident_start_time}
- Impact: {impact_description}

We are actively working to resolve this issue. You'll receive updates as we make progress.

Current Status: {current_status}
Estimated Resolution: {estimated_resolution}

For real-time updates, visit: {status_page_url}

Best regards,
IA Chérie Platform Team
            """,
            rich_content_template=None,
            variables=["user_name", "incident_type", "service_name", "incident_severity", 
                      "incident_start_time", "impact_description", "current_status", 
                      "estimated_resolution", "status_page_url"],
            localization={},
            formatting_rules={"date_format": "%Y-%m-%d %H:%M UTC"},
            character_limits={"subject": 100, "body": 2000},
            retry_policy={"max_retries": 3, "retry_intervals": [60, 300, 900]}
        )
        
        # Slack incident alert
        self.templates["incident_alert_slack"] = NotificationTemplate(
            template_id="incident_alert_slack",
            notification_type=NotificationType.INCIDENT_ALERT,
            channel=NotificationChannel.SLACK,
            subject_template="",  # Slack doesn't use subjects
            body_template="🚨 *{incident_severity}* incident: {incident_type} affecting {service_name}",
            rich_content_template={
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "🚨 Incident Alert"}
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": "*Type:*\n{incident_type}"},
                            {"type": "mrkdwn", "text": "*Severity:*\n{incident_severity}"},
                            {"type": "mrkdwn", "text": "*Service:*\n{service_name}"},
                            {"type": "mrkdwn", "text": "*Started:*\n{incident_start_time}"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "*Impact:* {impact_description}"}
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "View Incident"},
                                "url": "{incident_url}"
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Status Page"},
                                "url": "{status_page_url}"
                            }
                        ]
                    }
                ]
            },
            variables=["incident_type", "incident_severity", "service_name", 
                      "incident_start_time", "impact_description", "incident_url", "status_page_url"],
            localization={},
            formatting_rules={},
            character_limits={"body": 3000},
            retry_policy={"max_retries": 2, "retry_intervals": [30, 120]}
        )
        
        # SMS incident alert
        self.templates["incident_alert_sms"] = NotificationTemplate(
            template_id="incident_alert_sms",
            notification_type=NotificationType.INCIDENT_ALERT,
            channel=NotificationChannel.SMS,
            subject_template="",
            body_template="🚨 IA Chérie Alert: {incident_severity} {incident_type} affecting {service_name}. Started {incident_start_time}. Check email for details.",
            rich_content_template=None,
            variables=["incident_severity", "incident_type", "service_name", "incident_start_time"],
            localization={},
            formatting_rules={"date_format": "%H:%M"},
            character_limits={"body": 160},
            retry_policy={"max_retries": 2, "retry_intervals": [120, 600]}
        )
        
        logger.info(f"Loaded {len(self.templates)} notification templates")
    
    async def send_notification(self,
                              user_id: str,
                              notification_type: NotificationType,
                              priority: NotificationPriority,
                              template_variables: Dict[str, Any],
                              custom_channels: List[NotificationChannel] = None,
                              schedule_at: Optional[datetime] = None) -> List[str]:
        """
        Send notification to user across appropriate channels
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification
            priority: Priority level
            template_variables: Variables for template rendering
            custom_channels: Override channel selection
            schedule_at: Schedule for future delivery
            
        Returns:
            List of message IDs created
        """
        try:
            # Get user preferences
            preferences = self.user_preferences.get(user_id, self._get_default_preferences(user_id))
            
            # Determine channels to use
            channels = self._select_channels(user_id, notification_type, priority, preferences, custom_channels)
            
            # Check fatigue prevention
            if not self._check_fatigue_limits(user_id, priority):
                logger.warning(f"Notification blocked due to fatigue limits for user {user_id}")
                return []
            
            # Check quiet hours
            if not self._check_quiet_hours(user_id, priority, preferences):
                logger.info(f"Notification deferred due to quiet hours for user {user_id}")
                # TODO: Schedule for later delivery
                return []
            
            # Create messages for each channel
            message_ids = []
            for channel in channels:
                try:
                    message = await self._create_message(
                        user_id, notification_type, priority, channel, 
                        template_variables, schedule_at
                    )
                    
                    if message:
                        message_ids.append(message.message_id)
                        self.pending_messages[message.message_id] = message
                        
                        # Queue for delivery
                        if schedule_at is None or schedule_at <= datetime.utcnow():
                            await self.delivery_queue.put(message)
                        
                except Exception as e:
                    logger.error(f"Failed to create message for channel {channel}: {e}")
            
            logger.info(f"Created {len(message_ids)} notifications for user {user_id}")
            return message_ids
            
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
            return []
    
    def _get_default_preferences(self, user_id: str) -> NotificationPreferences:
        """Get default notification preferences for user"""
        return NotificationPreferences(
            user_id=user_id,
            channels={
                NotificationChannel.EMAIL: True,
                NotificationChannel.SLACK: True,
                NotificationChannel.SMS: False
            },
            priority_routing={
                NotificationPriority.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS],
                NotificationPriority.HIGH: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
                NotificationPriority.MEDIUM: [NotificationChannel.EMAIL],
                NotificationPriority.LOW: [NotificationChannel.EMAIL],
                NotificationPriority.INFORMATIONAL: [NotificationChannel.EMAIL]
            },
            type_routing={},
            quiet_hours={"22:00": "08:00"},
            timezone="UTC",
            frequency_limits={
                NotificationChannel.EMAIL: 20,
                NotificationChannel.SLACK: 30,
                NotificationChannel.SMS: 5
            },
            delivery_preferences={},
            emergency_contact=None,
            backup_channels=[NotificationChannel.EMAIL]
        )
    
    def _select_channels(self,
                        user_id: str,
                        notification_type: NotificationType,
                        priority: NotificationPriority,
                        preferences: NotificationPreferences,
                        custom_channels: Optional[List[NotificationChannel]]) -> List[NotificationChannel]:
        """Select appropriate channels for notification"""
        if custom_channels:
            return [ch for ch in custom_channels if preferences.channels.get(ch, False)]
        
        # Check type-specific routing first
        if notification_type in preferences.type_routing:
            return preferences.type_routing[notification_type]
        
        # Use priority-based routing
        if priority in preferences.priority_routing:
            return [ch for ch in preferences.priority_routing[priority] 
                   if preferences.channels.get(ch, False)]
        
        # Fallback to enabled channels
        return [ch for ch, enabled in preferences.channels.items() if enabled]
    
    def _check_fatigue_limits(self, user_id: str, priority: NotificationPriority) -> bool:
        """Check if user has exceeded fatigue limits"""
        # Critical notifications always go through
        if priority == NotificationPriority.CRITICAL:
            return True
        
        now = datetime.utcnow()
        user_history = self.delivery_history[user_id]
        
        # Remove old entries
        cutoff_time = now - timedelta(hours=1)
        self.delivery_history[user_id] = [
            msg for msg in user_history if msg.get("sent_at", now) > cutoff_time
        ]
        
        # Check hourly limit
        hourly_limit = self.config["fatigue_prevention"]["max_notifications_per_hour"]
        if len(self.delivery_history[user_id]) >= hourly_limit:
            return False
        
        return True
    
    def _check_quiet_hours(self, 
                          user_id: str, 
                          priority: NotificationPriority, 
                          preferences: NotificationPreferences) -> bool:
        """Check if notification should be sent during quiet hours"""
        # Critical notifications always go through
        if priority == NotificationPriority.CRITICAL:
            return True
        
        # TODO: Implement timezone-aware quiet hours check
        # For now, allow all notifications
        return True
    
    async def _create_message(self,
                            user_id: str,
                            notification_type: NotificationType,
                            priority: NotificationPriority,
                            channel: NotificationChannel,
                            template_variables: Dict[str, Any],
                            schedule_at: Optional[datetime]) -> Optional[NotificationMessage]:
        """Create notification message from template"""
        try:
            # Find appropriate template
            template_id = f"{notification_type.value}_{channel.value}"
            template = self.templates.get(template_id)
            
            if not template:
                logger.warning(f"No template found for {template_id}")
                return None
            
            # Render template
            subject = self._render_template(template.subject_template, template_variables)
            content = self._render_template(template.body_template, template_variables)
            
            # Render rich content if available
            rich_content = None
            if template.rich_content_template:
                rich_content = self._render_rich_content(template.rich_content_template, template_variables)
            
            # Apply character limits
            content = self._apply_character_limits(content, template.character_limits.get("body", 10000))
            if subject:
                subject = self._apply_character_limits(subject, template.character_limits.get("subject", 200))
            
            # Create message
            message = NotificationMessage(
                message_id=f"MSG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                notification_type=notification_type,
                priority=priority,
                channel=channel,
                subject=subject or "",
                content=content,
                rich_content=rich_content,
                metadata=template_variables.copy(),
                created_at=datetime.utcnow(),
                scheduled_at=schedule_at,
                sent_at=None,
                delivered_at=None,
                read_at=None,
                status=NotificationStatus.PENDING,
                retry_count=0,
                max_retries=template.retry_policy.get("max_retries", 3),
                error_message=None,
                delivery_receipt=None,
                response_data=None
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            return None
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        try:
            # Simple template rendering (replace {variable} with value)
            result = template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                result = result.replace(placeholder, str(value))
            
            # Remove any unresolved placeholders
            result = re.sub(r'\{[^}]+\}', '[N/A]', result)
            
            return result
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template
    
    def _render_rich_content(self, template: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Render rich content template (Slack blocks, etc.)"""
        try:
            # Convert template to JSON string, render, and parse back
            template_str = json.dumps(template)
            rendered_str = self._render_template(template_str, variables)
            return json.loads(rendered_str)
            
        except Exception as e:
            logger.error(f"Rich content rendering failed: {e}")
            return template
    
    def _apply_character_limits(self, content: str, limit: int) -> str:
        """Apply character limits to content"""
        if len(content) <= limit:
            return content
        
        # Truncate and add ellipsis
        return content[:limit-3] + "..."
    
    async def _process_delivery_queue(self):
        """Process the delivery queue"""
        while True:
            try:
                message = await self.delivery_queue.get()
                await self._deliver_message(message)
                self.delivery_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing delivery queue: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message(self, message: NotificationMessage):
        """Deliver a single message"""
        try:
            provider = self.providers.get(message.channel)
            if not provider:
                logger.error(f"No provider available for channel {message.channel}")
                message.status = NotificationStatus.FAILED
                message.error_message = f"No provider for channel {message.channel}"
                return
            
            # Check circuit breaker
            if provider.is_circuit_breaker_open():
                logger.warning(f"Circuit breaker open for {message.channel}, requeueing message")
                await self.retry_queue.put((message, datetime.utcnow() + timedelta(minutes=5)))
                return
            
            # Check rate limiting
            if provider.is_rate_limited(message.user_id):
                logger.warning(f"Rate limited for user {message.user_id} on {message.channel}")
                message.status = NotificationStatus.RATE_LIMITED
                await self.retry_queue.put((message, datetime.utcnow() + timedelta(minutes=10)))
                return
            
            # Record send attempt
            provider.record_send_attempt(message.user_id)
            
            # Update message status
            message.status = NotificationStatus.SENDING
            message.sent_at = datetime.utcnow()
            
            # Attempt delivery
            attempt = await provider.send_message(message)
            
            # Update message based on delivery result
            if attempt.success:
                message.status = NotificationStatus.DELIVERED
                message.delivered_at = datetime.utcnow()
                
                # Record successful delivery
                self.delivery_history[message.user_id].append({
                    "message_id": message.message_id,
                    "sent_at": message.sent_at,
                    "channel": message.channel.value,
                    "success": True
                })
                
                logger.info(f"Message {message.message_id} delivered via {message.channel}")
                
            else:
                message.status = NotificationStatus.FAILED
                message.error_message = attempt.response_message
                
                # Schedule retry if retries remaining
                if message.retry_count < message.max_retries:
                    retry_delay = self._calculate_retry_delay(message.retry_count)
                    retry_time = datetime.utcnow() + timedelta(seconds=retry_delay)
                    await self.retry_queue.put((message, retry_time))
                    logger.info(f"Scheduled retry for message {message.message_id} in {retry_delay}s")
                else:
                    logger.error(f"Message {message.message_id} failed permanently after {message.retry_count} retries")
            
        except Exception as e:
            logger.error(f"Failed to deliver message {message.message_id}: {e}")
            message.status = NotificationStatus.FAILED
            message.error_message = str(e)
    
    def _calculate_retry_delay(self, retry_count: int) -> int:
        """Calculate retry delay using exponential backoff"""
        retry_intervals = self.config["delivery_settings"]["retry_intervals"]
        if retry_count < len(retry_intervals):
            return retry_intervals[retry_count]
        
        # Use last interval for further retries
        return retry_intervals[-1]
    
    async def _process_retry_queue(self):
        """Process the retry queue"""
        while True:
            try:
                if not self.retry_queue.empty():
                    message, retry_time = await self.retry_queue.get()
                    
                    if datetime.utcnow() >= retry_time:
                        message.retry_count += 1
                        message.status = NotificationStatus.PENDING
                        await self.delivery_queue.put(message)
                    else:
                        # Put back in queue for later
                        await self.retry_queue.put((message, retry_time))
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error processing retry queue: {e}")
                await asyncio.sleep(60)
    
    async def start_background_tasks(self):
        """Start background delivery and retry tasks"""
        try:
            # Start delivery workers
            delivery_workers = [
                asyncio.create_task(self._process_delivery_queue())
                for _ in range(self.config["delivery_settings"]["max_concurrent_deliveries"])
            ]
            
            # Start retry processor
            retry_worker = asyncio.create_task(self._process_retry_queue())
            
            logger.info(f"Started {len(delivery_workers)} delivery workers and 1 retry worker")
            
            # Return tasks so they can be managed externally
            return delivery_workers + [retry_worker]
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")
            return []
    
    def register_user_preferences(self, preferences: NotificationPreferences) -> bool:
        """Register user notification preferences"""
        try:
            self.user_preferences[preferences.user_id] = preferences
            logger.info(f"Registered preferences for user {preferences.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register user preferences: {e}")
            return False
    
    def get_delivery_statistics(self, user_id: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get delivery statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            if user_id:
                user_history = self.delivery_history.get(user_id, [])
                recent_deliveries = [msg for msg in user_history if msg.get("sent_at", datetime.min) > cutoff_time]
                
                return {
                    "user_id": user_id,
                    "total_deliveries": len(recent_deliveries),
                    "successful_deliveries": sum(1 for msg in recent_deliveries if msg.get("success")),
                    "channels_used": list(set(msg.get("channel") for msg in recent_deliveries)),
                    "time_period_hours": hours
                }
            else:
                # Global statistics
                total_deliveries = 0
                successful_deliveries = 0
                channels_used = set()
                
                for user_history in self.delivery_history.values():
                    recent_deliveries = [msg for msg in user_history if msg.get("sent_at", datetime.min) > cutoff_time]
                    total_deliveries += len(recent_deliveries)
                    successful_deliveries += sum(1 for msg in recent_deliveries if msg.get("success"))
                    channels_used.update(msg.get("channel") for msg in recent_deliveries)
                
                return {
                    "total_deliveries": total_deliveries,
                    "successful_deliveries": successful_deliveries,
                    "success_rate": successful_deliveries / total_deliveries if total_deliveries > 0 else 0,
                    "channels_used": list(channels_used),
                    "unique_users": len(self.delivery_history),
                    "pending_messages": len(self.pending_messages),
                    "time_period_hours": hours
                }
                
        except Exception as e:
            logger.error(f"Failed to get delivery statistics: {e}")
            return {}
    
    def export_delivery_report(self, message_id: str) -> Dict[str, Any]:
        """Export detailed delivery report for a message"""
        message = self.pending_messages.get(message_id)
        if not message:
            return {"error": "Message not found"}
        
        return {
            "message_details": asdict(message),
            "delivery_timeline": [
                {"timestamp": message.created_at.isoformat(), "event": "Message Created"},
                {"timestamp": message.sent_at.isoformat() if message.sent_at else None, "event": "Sending Started"},
                {"timestamp": message.delivered_at.isoformat() if message.delivered_at else None, "event": "Delivered"},
                {"timestamp": message.read_at.isoformat() if message.read_at else None, "event": "Read"}
            ],
            "retry_history": {
                "retry_count": message.retry_count,
                "max_retries": message.max_retries,
                "final_status": message.status.value
            },
            "channel_performance": {
                "channel": message.channel.value,
                "provider_status": "active" if message.channel in self.providers else "inactive"
            }
        }


# Factory function
def create_multi_channel_notification_system() -> MultiChannelNotificationSystem:
    """Create new multi-channel notification system instance"""
    return MultiChannelNotificationSystem()


# Export all classes and functions
__all__ = [
    'MultiChannelNotificationSystem',
    'NotificationChannel',
    'NotificationPriority',
    'NotificationStatus',
    'NotificationType',
    'NotificationPreferences',
    'NotificationTemplate',
    'NotificationMessage',
    'NotificationCampaign',
    'DeliveryAttempt',
    'ChannelProvider',
    'EmailProvider',
    'SlackProvider',
    'SMSProvider',
    'create_multi_channel_notification_system'
]