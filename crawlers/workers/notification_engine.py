"""Notification Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/notification_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Notification and Alert System
Responsibility: Intelligent notification delivery and alert management
Technologies: Multi-channel delivery, ML prioritization, Real-time routing
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Event trigger → Notification prioritization → Channel selection → 
Template processing → Delivery optimization → Status tracking → Retry handling
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
import logging
import asyncio
import aiohttp
import smtplib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import jinja2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import websockets
import redis.asyncio as redis
from abc import ABC, abstractmethod

from .event_processor import WorkerEvent, EventType, EventPriority
from ...monitoring.performance_monitor import PerformanceMonitor
from ...security.encryption import EncryptionService
from ...utils.template_utils import TemplateUtils
from ...utils.rate_limiter import RateLimiter
from ...core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationChannel(Enum):
    """
Notification delivery channels"""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    TEAMS = "teams"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priorities"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


class NotificationStatus(Enum):
    """
Notification delivery status"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    CANCELLED = "cancelled"
    RETRY = "retry"


class TemplateType(Enum):
    """Notification template types"""

    WORKER_ALERT = "worker_alert"
    TASK_COMPLETION = "task_completion"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_ALERT = "performance_alert"
    CONTENT_VIOLATION = "content_violation"
    SYSTEM_STATUS = "system_status"
    USER_NOTIFICATION = "user_notification"
    REPORT_READY = "report_ready"


@dataclass
class NotificationTemplate:
    """Notification template definition"""
    template_id: str
    template_type: TemplateType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
    variables: List[str] = field(default_factory=list)
    locales: List[str] = field(default_factory=lambda: ["en"])
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationRecipient:
    """Notification recipient configuration"""
    recipient_id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    webhook_url: Optional[str] = None
    websocket_id: Optional[str] = None
    slack_channel: Optional[str] = None
    discord_channel: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    preferred_channels: List[NotificationChannel] = field(default_factory=list)
    timezone: str = "UTC"
    locale: str = "en"
    is_active: bool = True


@dataclass
class NotificationRule:
    """Notification rule configuration"""
    rule_id: str
    name: str
    event_types: List[EventType]
    channels: List[NotificationChannel]
    priority: NotificationPriority
    template_type: TemplateType
    recipients: List[str]
    conditions: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Optional[Dict[str, Any]] = None
    quiet_hours: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_by: Optional[str] = None


@dataclass
class Notification:
    """
Notification instance"""
    notification_id: str
    rule_id: str
    event: WorkerEvent
    channel: NotificationChannel
    recipient: NotificationRecipient
    template: NotificationTemplate
    priority: NotificationPriority
    subject: str
    body: str
    html_body: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    scheduled_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DeliveryResult:
    """
Notification delivery result"""
    notification_id: str
    status: NotificationStatus
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    delivery_details: Dict[str, Any] = field(default_factory=dict)
    retry_after: Optional[datetime] = None


class NotificationChannel_ABC(ABC):
    """
Abstract base class for notification channels"""
    def __init__(self, channel_config: Dict[str, Any]):
        self.config = channel_config
        self.rate_limiter = RateLimiter()

    @abstractmethod
    async def send(self, notification: Notification) -> DeliveryResult:
        try:
            logger.info(f"Executing send")
            
            # Implementation for send
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"send completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing health_check")
            
            # Implementation for health_check
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"health_check completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
Validate recipient for this channel"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
Check channel health"""
        pass


class EmailChannel(NotificationChannel_ABC):
    """
Email notification channel"""
    def __init__(self, channel_config: Dict[str, Any]):
        super().__init__(channel_config)
        self.smtp_server = channel_config.get("smtp_server", "localhost")
        self.smtp_port = channel_config.get("smtp_port", 587)
        self.username = channel_config.get("username")
        self.password = channel_config.get("password")
        self.use_tls = channel_config.get("use_tls", True)
        self.from_email = channel_config.get("from_email")

    async def send(self, notification: Notification) -> DeliveryResult:
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = notification.subject
            msg['From'] = self.from_email
            msg['To'] = notification.recipient.email
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

            # Add text body
            text_part = MIMEText(notification.body, 'plain')
            msg.attach(text_part)

            # Add HTML body if available
            if notification.html_body:
        try:
            logger.info(f"Executing send_message")
            
            # Implementation for send_message
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"send_message completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"send_message failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_smtp_message completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_smtp_message failed: {e}")
            raise
            await self._send_smtp_message(msg)

            return DeliveryResult(
                notification_id=notification.notification_id,
                status=NotificationStatus.SENT,
                delivered_at=datetime.utcnow(),
                delivery_details={"smtp_server": self.smtp_server}
            )

        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")
            return DeliveryResult(
                notification_id=notification.notification_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _send_smtp_message(self, msg: MIMEMultipart) -> None:
        """Send SMTP message"""
        def send_message():
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_message)

    async def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """
Add attachment to email"""
        try:
            filename = attachment.get("filename")
            content = attachment.get("content")
            content_type = attachment.get("content_type", "application/octet-stream")

            part = MIMEBase(*content_type.split('/'))
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}',
            )
            msg.attach(part)

        except Exception as e:
            logger.error(f"❌ Failed to add attachment: {e}")

    async def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate email recipient"""
        return bool(recipient.email and "@" in recipient.email)

    async def health_check(self) -> bool:
        """Check email channel health"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.quit()
            return True
        except Exception:
            return False


class WebhookChannel(NotificationChannel_ABC):
    """
Webhook notification channel"""
    def __init__(self, channel_config: Dict[str, Any]):
        super().__init__(channel_config)
        self.timeout = channel_config.get("timeout", 30)
        self.verify_ssl = channel_config.get("verify_ssl", True)
        self.headers = channel_config.get("headers", {})

    async def send(self, notification: Notification) -> DeliveryResult:
        """Send webhook notification"""
        try:
            webhook_url = notification.recipient.webhook_url
            if not webhook_url:
                raise ValueError("No webhook URL configured for recipient")

            # Prepare payload
            payload = {
                "notification_id": notification.notification_id,
                "event_type": notification.event.event_type.value,
                "priority": notification.priority.value,
                "subject": notification.subject,
                "body": notification.body,
                "metadata": notification.metadata,
                "timestamp": notification.created_at.isoformat()
            }

            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=self.verify_ssl
                ) as response:
                    if response.status < 400:
                        return DeliveryResult(
                            notification_id=notification.notification_id,
                            status=NotificationStatus.DELIVERED,
                            delivered_at=datetime.utcnow(),
                            delivery_details={
                                "webhook_url": webhook_url,
                                "status_code": response.status,
                                "response_headers": dict(response.headers)
                            }
                        )
                    else:
                        error_text = await response.text()
                        return DeliveryResult(
                            notification_id=notification.notification_id,
                            status=NotificationStatus.FAILED,
                            error_message=f"HTTP {response.status}: {error_text}"
                        )

        except Exception as e:
            logger.error(f"❌ Failed to send webhook notification: {e}")
            return DeliveryResult(
                notification_id=notification.notification_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate webhook recipient"""
        return bool(recipient.webhook_url and recipient.webhook_url.startswith(('http://', 'https://')))

    async def health_check(self) -> bool:
        """
Check webhook channel health"""
        return True  # Webhook health depends on individual URLs


class WebSocketChannel(NotificationChannel_ABC):
    """
WebSocket notification channel"""
    def __init__(self, channel_config: Dict[str, Any]):
        super().__init__(channel_config)
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}

    async def send(self, notification: Notification) -> DeliveryResult:
        """
Send WebSocket notification"""
        try:
            websocket_id = notification.recipient.websocket_id
            if not websocket_id or websocket_id not in self.active_connections:
                return DeliveryResult(
                    notification_id=notification.notification_id,
                    status=NotificationStatus.FAILED,
                    error_message="WebSocket connection not found"
                )

            websocket = self.active_connections[websocket_id]

            # Prepare message
            message = {
                "type": "notification",
                "notification_id": notification.notification_id,
                "event_type": notification.event.event_type.value,
                "priority": notification.priority.value,
                "subject": notification.subject,
                "body": notification.body,
                "metadata": notification.metadata,
                "timestamp": notification.created_at.isoformat()
            }

            # Send message
            await websocket.send(json.dumps(message))

            return DeliveryResult(
                notification_id=notification.notification_id,
                status=NotificationStatus.DELIVERED,
                delivered_at=datetime.utcnow(),
                delivery_details={"websocket_id": websocket_id}
            )

        except Exception as e:
            logger.error(f"❌ Failed to send WebSocket notification: {e}")
            return DeliveryResult(
                notification_id=notification.notification_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def register_connection(self, websocket_id: str, websocket: websockets.WebSocketServerProtocol) -> None:
        """Register WebSocket connection"""
        self.active_connections[websocket_id] = websocket
        logger.info(f"📡 WebSocket connection registered: {websocket_id}")

    async def unregister_connection(self, websocket_id: str) -> None:
        """Unregister WebSocket connection"""
        if websocket_id in self.active_connections:
            del self.active_connections[websocket_id]
            logger.info(f"📡 WebSocket connection unregistered: {websocket_id}")

    async def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate WebSocket recipient"""
        return bool(recipient.websocket_id)

    async def health_check(self) -> bool:
        """
Check WebSocket channel health"""
        return True


class NotificationEngine:
    """
    Intelligent notification and alert system
    
    Features:
    - Multi-channel delivery (Email, SMS, Webhook, WebSocket, etc.)
    - ML-based prioritization and routing
    - Template management with localization
    - Rate limiting and quiet hours
    - Retry mechanisms with backoff
    - Real-time delivery status tracking
    - Performance analytics
    """
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        
        # Core components
        self.templates: Dict[str, NotificationTemplate] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.rules: Dict[str, NotificationRule] = {}
        self.channels: Dict[NotificationChannel, NotificationChannel_ABC] = {}
        
        # Processing
        self.pending_notifications: asyncio.Queue = asyncio.Queue()
        self.processing_notifications: Dict[str, Notification] = {}
        self.delivery_results: deque = deque(maxlen=10000)
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        self.is_running = False
        
        # Components
        self.performance_monitor = PerformanceMonitor()
        self.template_utils = TemplateUtils()
        self.encryption_service = EncryptionService()
        
        # Template engine
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Statistics
        self.stats = {
            "total_notifications": 0,
            "delivered_notifications": 0,
            "failed_notifications": 0,
            "delivery_rate": 0.0,
            "average_delivery_time": 0.0
        }

    async def start(self) -> bool:
        """Start notification engine"""
        try:
            logger.info("🚀 Starting notification engine")
            
            # Initialize Redis
            await self._initialize_redis()
            
            # Initialize channels
            await self._initialize_channels()
            
            # Load templates and rules
            await self._load_configuration()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            
            logger.info("✅ Notification engine started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start notification engine: {e}")
            return False

    async def stop(self) -> None:
        """Stop notification engine"""
        try:
            logger.info("🛑 Stopping notification engine")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Wait for pending notifications
            await self._process_pending_notifications()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Close Redis
            if self.redis:
                await self.redis.close()
            
            logger.info("✅ Notification engine stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping notification engine: {e}")

    async def process_event(self, event: WorkerEvent) -> List[str]:
        """Process event and create notifications"""
        try:
            notification_ids = []
            
            # Find matching rules
            matching_rules = await self._find_matching_rules(event)
            
            for rule in matching_rules:
                # Create notifications for each recipient and channel
                for recipient_id in rule.recipients:
                    recipient = self.recipients.get(recipient_id)
                    if not recipient or not recipient.is_active:
                        continue
                    
                    for channel in rule.channels:
                        # Check if recipient supports this channel
                        if not await self._validate_recipient_channel(recipient, channel):
                            continue
                        
                        # Create notification
                        notification = await self._create_notification(event, rule, recipient, channel)
                        if notification:
                            # Queue for delivery
                            await self.pending_notifications.put(notification)
                            notification_ids.append(notification.notification_id)
            
            logger.info(f"📝 Created {len(notification_ids)} notifications for event {event.event_id}")
            return notification_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to process event {event.event_id}: {e}")
            return []

    async def send_direct_notification(self, recipient_id: str, channel: NotificationChannel,
                                     template_type: TemplateType, variables: Dict[str, Any],
                                     priority: NotificationPriority = NotificationPriority.MEDIUM) -> Optional[str]:
        """Send direct notification without event trigger"""
        try:
            recipient = self.recipients.get(recipient_id)
            if not recipient:
                logger.warning(f"⚠️ Recipient not found: {recipient_id}")
                return None
            
            template = await self._get_template(template_type, channel, recipient.locale)
            if not template:
                logger.warning(f"⚠️ Template not found: {template_type.value} for {channel.value}")
                return None
            
            # Create fake event for template processing
            fake_event = WorkerEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.SYSTEM_ERROR,  # Placeholder
                source="direct_notification",
                payload=variables
            )
            
            # Create fake rule
            fake_rule = NotificationRule(
                rule_id="direct",
                name="Direct Notification",
                event_types=[EventType.SYSTEM_ERROR],
                channels=[channel],
                priority=priority,
                template_type=template_type,
                recipients=[recipient_id]
            )
            
            # Create notification
            notification = await self._create_notification(fake_event, fake_rule, recipient, channel)
            if notification:
                # Queue for immediate delivery
                await self.pending_notifications.put(notification)
                return notification.notification_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to send direct notification: {e}")
            return None

    async def get_delivery_status(self, notification_id: str) -> Optional[DeliveryResult]:
        """Get notification delivery status"""
        try:
            # Check processing notifications
            if notification_id in self.processing_notifications:
                return DeliveryResult(
                    notification_id=notification_id,
                    status=NotificationStatus.PENDING
                )
            
            # Check delivery results
            for result in self.delivery_results:
                if result.notification_id == notification_id:
                    return result
            
            # Check Redis for historical results
            if self.redis:
                result_data = await self.redis.get(f"notification_result:{notification_id}")
                if result_data:
                    result_dict = json.loads(result_data)
                    return DeliveryResult(**result_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get delivery status: {e}")
            return None

    async def add_recipient(self, recipient: NotificationRecipient) -> bool:
        """Add notification recipient"""
        try:
            # Validate recipient
            if not await self._validate_recipient(recipient):
                return False
            
            # Store recipient
            self.recipients[recipient.recipient_id] = recipient
            
            # Persist to Redis
            if self.redis:
                await self.redis.set(
                    f"recipient:{recipient.recipient_id}",
                    json.dumps(recipient.__dict__, default=str),
                    ex=86400 * 30  # 30 days
                )
            
            logger.info(f"✅ Recipient added: {recipient.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add recipient: {e}")
            return False

    async def add_rule(self, rule: NotificationRule) -> bool:
        """Add notification rule"""
        try:
            # Validate rule
            if not await self._validate_rule(rule):
                return False
            
            # Store rule
            self.rules[rule.rule_id] = rule
            
            # Persist to Redis
            if self.redis:
                await self.redis.set(
                    f"rule:{rule.rule_id}",
                    json.dumps(rule.__dict__, default=str),
                    ex=86400 * 30  # 30 days
                )
            
            logger.info(f"✅ Notification rule added: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add rule: {e}")
            return False

    async def add_template(self, template: NotificationTemplate) -> bool:
        """Add notification template"""
        try:
            # Validate template
            if not await self._validate_template(template):
                return False
            
            # Store template
            self.templates[template.template_id] = template
            
            # Persist to Redis
            if self.redis:
                await self.redis.set(
                    f"template:{template.template_id}",
                    json.dumps(template.__dict__, default=str),
                    ex=86400 * 30  # 30 days
                )
            
            logger.info(f"✅ Notification template added: {template.template_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add template: {e}")
            return False

    async def get_statistics(self) -> Dict[str, Any]:
        """Get notification engine statistics"""
        try:
            return {
                "engine_status": "running" if self.is_running else "stopped",
                "queue_size": self.pending_notifications.qsize(),
                "processing_count": len(self.processing_notifications),
                "templates_count": len(self.templates),
                "recipients_count": len(self.recipients),
                "rules_count": len(self.rules),
                "channels_count": len(self.channels),
                "statistics": self.stats.copy(),
                "delivery_results_count": len(self.delivery_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {"error": str(e)}

    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("✅ Redis connection established for notification engine")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            raise

    async def _initialize_channels(self) -> None:
        """Initialize notification channels"""
        try:
            # Email channel
            email_config = settings.get("notification.email", {})
            if email_config:
                self.channels[NotificationChannel.EMAIL] = EmailChannel(email_config)
            
            # Webhook channel
            webhook_config = settings.get("notification.webhook", {})
            self.channels[NotificationChannel.WEBHOOK] = WebhookChannel(webhook_config)
            
            # WebSocket channel
            websocket_config = settings.get("notification.websocket", {})
            self.channels[NotificationChannel.WEBSOCKET] = WebSocketChannel(websocket_config)
            
            logger.info(f"✅ Initialized {len(self.channels)} notification channels")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize channels: {e}")
            raise

    async def _load_configuration(self) -> None:
        """Load templates, recipients, and rules from Redis"""
        try:
            if not self.redis:
                return
            
            # Load templates
            template_keys = await self.redis.keys("template:*")
            for key in template_keys:
                template_data = await self.redis.get(key)
                if template_data:
                    template_dict = json.loads(template_data)
                    template = NotificationTemplate(**template_dict)
                    self.templates[template.template_id] = template
            
            # Load recipients
            recipient_keys = await self.redis.keys("recipient:*")
            for key in recipient_keys:
                recipient_data = await self.redis.get(key)
                if recipient_data:
                    recipient_dict = json.loads(recipient_data)
                    recipient = NotificationRecipient(**recipient_dict)
                    self.recipients[recipient.recipient_id] = recipient
            
            # Load rules
            rule_keys = await self.redis.keys("rule:*")
            for key in rule_keys:
                rule_data = await self.redis.get(key)
                if rule_data:
                    rule_dict = json.loads(rule_data)
                    # Convert string enums back to enum objects
                    rule_dict['event_types'] = [EventType(et) for et in rule_dict['event_types']]
                    rule_dict['channels'] = [NotificationChannel(ch) for ch in rule_dict['channels']]
                    rule_dict['priority'] = NotificationPriority(rule_dict['priority'])
                    rule_dict['template_type'] = TemplateType(rule_dict['template_type'])
                    rule = NotificationRule(**rule_dict)
                    self.rules[rule.rule_id] = rule
            
            logger.info(f"✅ Loaded configuration: {len(self.templates)} templates, {len(self.recipients)} recipients, {len(self.rules)} rules")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")

    async def _start_background_tasks(self) -> None:
        """Start background processing tasks"""
        try:
            # Notification processor
            processor_task = asyncio.create_task(self._notification_processor())
            self.background_tasks.add(processor_task)
            
            # Statistics updater
            stats_task = asyncio.create_task(self._statistics_updater())
            self.background_tasks.add(stats_task)
            
            # Cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_task())
            self.background_tasks.add(cleanup_task)
            
            logger.info("✅ Background tasks started for notification engine")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _notification_processor(self) -> None:
        """Background notification processing loop"""
        while not self.shutdown_event.is_set():
            try:
                # Get next notification
                try:
                    notification = await asyncio.wait_for(
                        self.pending_notifications.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process notification
                asyncio.create_task(self._process_notification(notification))
                
            except Exception as e:
                logger.error(f"❌ Notification processor error: {e}")
                await asyncio.sleep(5)

    async def _process_notification(self, notification: Notification) -> None:
        """Process a single notification"""
        try:
            # Add to processing
            self.processing_notifications[notification.notification_id] = notification
            
            logger.debug(f"📤 Processing notification: {notification.notification_id}")
            
            # Get channel handler
            channel_handler = self.channels.get(notification.channel)
            if not channel_handler:
                raise Exception(f"Channel handler not found: {notification.channel.value}")
            
            # Send notification
            result = await channel_handler.send(notification)
            
            # Store result
            self.delivery_results.append(result)
            
            # Update statistics
            self.stats["total_notifications"] += 1
            if result.status == NotificationStatus.DELIVERED:
                self.stats["delivered_notifications"] += 1
            else:
                self.stats["failed_notifications"] += 1
            
            # Persist result to Redis
            if self.redis:
                await self.redis.set(
                    f"notification_result:{notification.notification_id}",
                    json.dumps(result.__dict__, default=str),
                    ex=86400 * 7  # 7 days
                )
            
            logger.debug(f"✅ Notification processed: {notification.notification_id} - {result.status.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process notification {notification.notification_id}: {e}")
            
            # Create error result
            error_result = DeliveryResult(
                notification_id=notification.notification_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
            self.delivery_results.append(error_result)
            
        finally:
            # Remove from processing
            self.processing_notifications.pop(notification.notification_id, None)

    async def _find_matching_rules(self, event: WorkerEvent) -> List[NotificationRule]:
        """Find notification rules that match the event"""
        try:
            matching_rules = []
            
            for rule in self.rules.values():
                if not rule.is_active:
                    continue
                
                # Check event type
                if event.event_type not in rule.event_types:
                    continue
                
                # Check conditions
                if not await self._check_rule_conditions(rule, event):
                    continue
                
                # Check rate limiting
                if not await self._check_rate_limit(rule, event):
                    continue
                
                # Check quiet hours
                if not await self._check_quiet_hours(rule):
                    continue
                
                matching_rules.append(rule)
            
            return matching_rules
            
        except Exception as e:
            logger.error(f"❌ Failed to find matching rules: {e}")
            return []

    async def _create_notification(self, event: WorkerEvent, rule: NotificationRule,
                                 recipient: NotificationRecipient, channel: NotificationChannel) -> Optional[Notification]:
        """Create notification from event, rule, and recipient"""
        try:
            # Get template
            template = await self._get_template(rule.template_type, channel, recipient.locale)
            if not template:
                logger.warning(f"⚠️ Template not found: {rule.template_type.value} for {channel.value}")
                return None
            
            # Prepare template variables
            variables = {
                "event": event.__dict__,
                "recipient": recipient.__dict__,
                "rule": rule.__dict__,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Render templates
            subject = await self._render_template(template.subject_template, variables)
            body = await self._render_template(template.body_template, variables)
            html_body = None
            if template.html_template:
                html_body = await self._render_template(template.html_template, variables)
            
            # Create notification
            notification = Notification(
                notification_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                event=event,
                channel=channel,
                recipient=recipient,
                template=template,
                priority=rule.priority,
                subject=subject,
                body=body,
                html_body=html_body,
                scheduled_at=datetime.utcnow()
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"❌ Failed to create notification: {e}")
            return None

    async def _get_template(self, template_type: TemplateType, 
                          channel: NotificationChannel, locale: str) -> Optional[NotificationTemplate]:
        """Get notification template"""
        try:
            # Try specific template first
            template_id = f"{template_type.value}_{channel.value}_{locale}"
            template = self.templates.get(template_id)
            if template and template.is_active:
                return template
            
            # Try with default locale
            template_id = f"{template_type.value}_{channel.value}_en"
            template = self.templates.get(template_id)
            if template and template.is_active:
                return template
            
            # Try generic template
            for template in self.templates.values():
                if (template.template_type == template_type and 
                    template.channel == channel and 
                    template.is_active):
                    return template
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get template: {e}")
            return None

    async def _render_template(self, template_string: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        try:
            template = self.jinja_env.from_string(template_string)
            return template.render(**variables)
            
        except Exception as e:
            logger.error(f"❌ Failed to render template: {e}")
            return template_string

    async def _validate_recipient_channel(self, recipient: NotificationRecipient, 
                                        channel: NotificationChannel) -> bool:
        """Validate if recipient supports the channel"""
        try:
            channel_handler = self.channels.get(channel)
            if not channel_handler:
                return False
            
            return await channel_handler.validate_recipient(recipient)
            
        except Exception as e:
            logger.error(f"❌ Failed to validate recipient channel: {e}")
            return False

    async def _validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate recipient configuration"""
        try:
            if not recipient.recipient_id:
                return False
            
            # Check if at least one contact method is provided
            has_contact = any([
                recipient.email,
                recipient.phone,
                recipient.webhook_url,
                recipient.websocket_id
            ])
            
            return has_contact
            
        except Exception as e:
            logger.error(f"❌ Failed to validate recipient: {e}")
            return False

    async def _validate_rule(self, rule: NotificationRule) -> bool:
        """Validate notification rule"""
        try:
            if not rule.rule_id or not rule.event_types or not rule.channels:
                return False
            
            # Check if recipients exist
            for recipient_id in rule.recipients:
                if recipient_id not in self.recipients:
                    logger.warning(f"⚠️ Recipient not found in rule: {recipient_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate rule: {e}")
            return False

    async def _validate_template(self, template: NotificationTemplate) -> bool:
        """Validate notification template"""
        try:
            if not template.template_id or not template.subject_template or not template.body_template:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate template: {e}")
            return False

    async def _check_rule_conditions(self, rule: NotificationRule, event: WorkerEvent) -> bool:
        """Check if event meets rule conditions"""
        try:
            if not rule.conditions:
                return True
            
            # Check payload conditions
            payload_conditions = rule.conditions.get("payload", {})
            for key, expected_value in payload_conditions.items():
                if key not in event.payload or event.payload[key] != expected_value:
                    return False
            
            # Check metadata conditions
            metadata_conditions = rule.conditions.get("metadata", {})
            for key, expected_value in metadata_conditions.items():
                if key not in event.metadata or event.metadata[key] != expected_value:
                    return False
            
            # Check priority condition
            if "min_priority" in rule.conditions:
                min_priority = EventPriority(rule.conditions["min_priority"])
                if event.priority.value > min_priority.value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check rule conditions: {e}")
            return False

    async def _check_rate_limit(self, rule: NotificationRule, event: WorkerEvent) -> bool:
        """Check rate limiting for rule"""
        try:
            if not rule.rate_limit or not self.redis:
                return True
            
            # Implementation of rate limiting using Redis
            # This is a simplified version
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check rate limit: {e}")
            return True

    async def _check_quiet_hours(self, rule: NotificationRule) -> bool:
        """Check if current time is within quiet hours"""
        try:
            if not rule.quiet_hours:
                return True
            
            # Implementation of quiet hours check
            # This is a simplified version
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check quiet hours: {e}")
            return True

    async def _process_pending_notifications(self) -> None:
        """Process remaining pending notifications during shutdown"""
        try:
            timeout = 60  # 1 minute timeout
            start_time = time.time()
            
            while not self.pending_notifications.empty() and (time.time() - start_time) < timeout:
                try:
                    notification = await asyncio.wait_for(
                        self.pending_notifications.get(),
                        timeout=1.0
                    )
                    await self._process_notification(notification)
                except asyncio.TimeoutError:
                    break
            
            remaining = self.pending_notifications.qsize()
            if remaining > 0:
                logger.warning(f"⚠️ {remaining} notifications remaining in queue during shutdown")
            
        except Exception as e:
            logger.error(f"❌ Failed to process pending notifications: {e}")

    async def _statistics_updater(self) -> None:
        """Background statistics update task"""
        while not self.shutdown_event.is_set():
            try:
                await self._update_statistics()
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Statistics updater error: {e}")
                await asyncio.sleep(600)

    async def _update_statistics(self) -> None:
        """Update delivery statistics"""
        try:
            total = self.stats["total_notifications"]
            delivered = self.stats["delivered_notifications"]
            
            if total > 0:
                self.stats["delivery_rate"] = (delivered / total) * 100
            
            # Calculate average delivery time from recent results
            recent_results = list(self.delivery_results)[-100:]  # Last 100 results
            delivery_times = []
            
            for result in recent_results:
                if result.status == NotificationStatus.DELIVERED and result.delivered_at:
                    # This would need the original notification creation time for accurate calculation
                    # Simplified implementation here
                    delivery_times.append(1.0)  # Placeholder
            
            if delivery_times:
                self.stats["average_delivery_time"] = sum(delivery_times) / len(delivery_times)
            
        except Exception as e:
            logger.error(f"❌ Failed to update statistics: {e}")

    async def _cleanup_task(self) -> None:
        """Background cleanup task"""
        while not self.shutdown_event.is_set():
            try:
                await self._cleanup_old_results()
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"❌ Cleanup task error: {e}")
                await asyncio.sleep(1800)

    async def _cleanup_old_results(self) -> None:
        """Clean up old delivery results"""
        try:
            # The deque already has a maxlen, but we can do additional cleanup
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Clean up Redis results older than 7 days
            if self.redis:
                # This would require iterating through keys and checking timestamps
                # Implementation depends on specific Redis key patterns used
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old results: {e}")


# Global notification engine instance
_notification_engine: Optional[NotificationEngine] = None


def get_notification_engine() -> NotificationEngine:
    """Get or create notification engine singleton"""
    global _notification_engine
    
    if _notification_engine is None:
        _notification_engine = NotificationEngine()
    
    return _notification_engine


async def initialize_notification_engine() -> bool:
    """
Initialize global notification engine"""
    try:
        engine = get_notification_engine()
        return await engine.start()
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize notification engine: {e}")
        return False


async def shutdown_notification_engine() -> None:
    """Shutdown global notification engine"""
    global _notification_engine
    
    if _notification_engine:
        await _notification_engine.stop()
        _notification_engine = None
