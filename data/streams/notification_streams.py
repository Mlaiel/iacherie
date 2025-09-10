"""Notification Streams for IA Influencer Agent Platform
====================================================

Real-time notification system with intelligent routing, multi-channel delivery,
and advanced filtering for streaming events and alerts.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    IN_APP = "in_app"
    DASHBOARD = "dashboard"


class NotificationType(str, Enum):
    """Notification types"""
    ALERT = "alert"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"
    SYSTEM = "system"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CONTENT = "content"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DeliveryStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class FilterOperator(str, Enum):
    """Filter operators for notification rules"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class NotificationTemplate:
    """Notification template configuration"""
    template_id: str
    name: str
    channel: NotificationChannel
    subject_template: str = ""
    body_template: str = ""
    variables: List[str] = field(default_factory=list)
    locale: str = "en"
    formatting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationFilter:
    """Notification filter configuration"""
    filter_id: str
    field: str
    operator: FilterOperator
    value: Any
    enabled: bool = True


@dataclass
class NotificationRule:
    """Notification routing rule"""
    rule_id: str
    name: str
    description: str
    priority: int = 0
    conditions: List[NotificationFilter] = field(default_factory=list)
    channels: List[NotificationChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    template_id: Optional[str] = None
    throttle_minutes: int = 0
    enabled: bool = True
    tags: Set[str] = field(default_factory=set)


@dataclass
class Notification:
    """Notification data structure"""
    notification_id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    channels: List[NotificationChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    template_id: Optional[str] = None
    
    # Delivery tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Status tracking
    delivery_status: Dict[str, DeliveryStatus] = field(default_factory=dict)  # channel -> status
    delivery_attempts: Dict[str, int] = field(default_factory=dict)  # channel -> attempts
    delivered_at: Dict[str, datetime] = field(default_factory=dict)  # channel -> timestamp
    
    # Metadata
    source: str = ""
    correlation_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationMetrics:
    """Notification delivery metrics"""
    total_notifications: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    pending_deliveries: int = 0
    average_delivery_time_ms: float = 0.0
    delivery_rate_per_minute: float = 0.0
    channel_success_rates: Dict[NotificationChannel, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Recipient:
    """Notification recipient configuration"""
    recipient_id: str
    name: str
    channels: Dict[NotificationChannel, str] = field(default_factory=dict)  # channel -> address
    preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"
    language: str = "en"
    enabled: bool = True
    tags: Set[str] = field(default_factory=set)


class NotificationStreams:
    """
    Real-time notification system with intelligent routing, multi-channel delivery,
    and advanced filtering for streaming events and alerts.
    
    Features:
    - Multi-channel delivery (Email, SMS, Push, WebHook, WebSocket)
    - Intelligent routing with rule-based filtering
    - Template-based message formatting
    - Priority-based delivery scheduling
    - Throttling and rate limiting
    - Delivery tracking and analytics
    - Real-time WebSocket notifications
    - Integration with external services
    """
    
    def __init__(
        self,
        enable_real_time: bool = True,
        enable_throttling: bool = True,
        max_retry_attempts: int = 3
    ):
        # Configuration
        self.enable_real_time = enable_real_time
        self.enable_throttling = enable_throttling
        self.max_retry_attempts = max_retry_attempts
        
        # Notification management
        self.notifications: Dict[str, Notification] = {}
        self.notification_queue: deque = deque()
        self.scheduled_notifications: Dict[datetime, List[str]] = defaultdict(list)
        
        # Configuration
        self.templates: Dict[str, NotificationTemplate] = {}
        self.rules: Dict[str, NotificationRule] = {}
        self.recipients: Dict[str, Recipient] = {}
        
        # Channel handlers
        self.channel_handlers: Dict[NotificationChannel, Callable] = {}
        self.websocket_connections: Dict[str, Any] = {}  # connection_id -> websocket
        
        # Throttling and rate limiting
        self.delivery_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))  # recipient -> timestamps
        self.channel_rate_limits: Dict[NotificationChannel, Dict[str, Any]] = {}
        
        # Metrics and monitoring
        self.metrics = NotificationMetrics()
        self.delivery_analytics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Background tasks
        self.notification_processor_task: Optional[asyncio.Task] = None
        self.scheduler_task: Optional[asyncio.Task] = None
        self.metrics_collector_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # State management
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # Initialize default templates
        self._init_default_templates()
        
        logger.info("NotificationStreams initialized")
        
    async def initialize(self) -> None:
        """Initialize the notification streams system"""
        try:
            if self._running:
                return
                
            # Start background tasks
            self.notification_processor_task = asyncio.create_task(self._notification_processor())
            self.scheduler_task = asyncio.create_task(self._notification_scheduler())
            self.metrics_collector_task = asyncio.create_task(self._metrics_collector())
            self.cleanup_task = asyncio.create_task(self._cleanup_worker())
            
            # Register default channel handlers
            await self._register_default_handlers()
            
            self._running = True
            logger.info("NotificationStreams initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NotificationStreams: {e}")
            raise
            
    async def send_notification(
        self,
        type: NotificationType,
        priority: NotificationPriority,
        title: str,
        message: str,
        recipients: Optional[List[str]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        data: Optional[Dict[str, Any]] = None,
        template_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        source: str = "",
        tags: Optional[Set[str]] = None
    ) -> str:
        """
        Send a notification
        
        Args:
            type: Notification type
            priority: Priority level
            title: Notification title
            message: Notification message
            recipients: List of recipient IDs
            channels: Preferred delivery channels
            data: Additional data
            template_id: Template to use
            scheduled_at: When to send (optional)
            expires_at: When notification expires
            source: Source of notification
            tags: Notification tags
            
        Returns:
            Notification ID
        """
        try:
            notification_id = str(uuid.uuid4())
            
            notification = Notification(
                notification_id=notification_id,
                type=type,
                priority=priority,
                title=title,
                message=message,
                data=data or {},
                recipients=recipients or [],
                channels=channels or [],
                template_id=template_id,
                scheduled_at=scheduled_at,
                expires_at=expires_at,
                source=source,
                tags=tags or set()
            )
            
            # Apply notification rules to determine routing
            await self._apply_notification_rules(notification)
            
            # Store notification
            self.notifications[notification_id] = notification
            
            # Queue for processing or schedule
            if scheduled_at and scheduled_at > datetime.now(timezone.utc):
                self.scheduled_notifications[scheduled_at].append(notification_id)
            else:
                self.notification_queue.append(notification_id)
                
            self.metrics.total_notifications += 1
            
            logger.info(f"Notification created: {notification_id} ({type.value}, {priority.value})")
            return notification_id
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return ""
            
    async def add_notification_rule(
        self,
        name: str,
        description: str,
        conditions: List[NotificationFilter],
        channels: List[NotificationChannel],
        recipients: List[str],
        priority: int = 0,
        template_id: Optional[str] = None,
        throttle_minutes: int = 0,
        tags: Optional[Set[str]] = None
    ) -> str:
        """
        Add notification routing rule
        
        Args:
            name: Rule name
            description: Rule description
            conditions: Filter conditions
            channels: Target channels
            recipients: Target recipients
            priority: Rule priority (higher = processed first)
            template_id: Template to use
            throttle_minutes: Throttling interval
            tags: Rule tags
            
        Returns:
            Rule ID
        """
        try:
            rule_id = str(uuid.uuid4())
            
            rule = NotificationRule(
                rule_id=rule_id,
                name=name,
                description=description,
                priority=priority,
                conditions=conditions,
                channels=channels,
                recipients=recipients,
                template_id=template_id,
                throttle_minutes=throttle_minutes,
                tags=tags or set()
            )
            
            self.rules[rule_id] = rule
            
            logger.info(f"Notification rule added: {name}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to add notification rule: {e}")
            return ""
            
    async def add_recipient(
        self,
        recipient_id: str,
        name: str,
        channels: Dict[NotificationChannel, str],
        preferences: Optional[Dict[str, Any]] = None,
        timezone: str = "UTC",
        language: str = "en",
        tags: Optional[Set[str]] = None
    ) -> bool:
        """
        Add notification recipient
        
        Args:
            recipient_id: Unique recipient ID
            name: Recipient name
            channels: Channel addresses (email, phone, etc.)
            preferences: Notification preferences
            timezone: Recipient timezone
            language: Preferred language
            tags: Recipient tags
            
        Returns:
            Success status
        """
        try:
            recipient = Recipient(
                recipient_id=recipient_id,
                name=name,
                channels=channels,
                preferences=preferences or {},
                timezone=timezone,
                language=language,
                tags=tags or set()
            )
            
            self.recipients[recipient_id] = recipient
            
            logger.info(f"Recipient added: {name} ({recipient_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add recipient: {e}")
            return False
            
    async def add_template(
        self,
        template_id: str,
        name: str,
        channel: NotificationChannel,
        subject_template: str = "",
        body_template: str = "",
        variables: Optional[List[str]] = None,
        locale: str = "en"
    ) -> bool:
        """
        Add notification template
        
        Args:
            template_id: Unique template ID
            name: Template name
            channel: Target channel
            subject_template: Subject template with variables
            body_template: Body template with variables
            variables: List of available variables
            locale: Template locale
            
        Returns:
            Success status
        """
        try:
            template = NotificationTemplate(
                template_id=template_id,
                name=name,
                channel=channel,
                subject_template=subject_template,
                body_template=body_template,
                variables=variables or [],
                locale=locale
            )
            
            self.templates[template_id] = template
            
            logger.info(f"Template added: {name} for {channel.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add template: {e}")
            return False
            
    async def register_channel_handler(
        self,
        channel: NotificationChannel,
        handler: Callable
    ) -> bool:
        """
        Register channel delivery handler
        
        Args:
            channel: Notification channel
            handler: Async handler function
            
        Returns:
            Success status
        """
        try:
            self.channel_handlers[channel] = handler
            logger.info(f"Channel handler registered: {channel.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register channel handler: {e}")
            return False
            
    async def register_websocket_connection(
        self,
        connection_id: str,
        websocket: Any,
        recipient_id: Optional[str] = None
    ) -> bool:
        """
        Register WebSocket connection for real-time notifications
        
        Args:
            connection_id: Connection identifier
            websocket: WebSocket connection object
            recipient_id: Associated recipient ID
            
        Returns:
            Success status
        """
        try:
            self.websocket_connections[connection_id] = {
                "websocket": websocket,
                "recipient_id": recipient_id,
                "connected_at": datetime.now(timezone.utc)
            }
            
            logger.info(f"WebSocket connection registered: {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register WebSocket connection: {e}")
            return False
            
    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get notification delivery status
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Status information
        """
        try:
            if notification_id not in self.notifications:
                return None
                
            notification = self.notifications[notification_id]
            
            # Calculate overall status
            statuses = list(notification.delivery_status.values())
            if not statuses:
                overall_status = "pending"
            elif all(status == DeliveryStatus.DELIVERED for status in statuses):
                overall_status = "delivered"
            elif any(status == DeliveryStatus.FAILED for status in statuses):
                overall_status = "partial_failure"
            elif any(status == DeliveryStatus.SENT for status in statuses):
                overall_status = "sent"
            else:
                overall_status = "pending"
                
            return {
                "notification_id": notification_id,
                "type": notification.type.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "created_at": notification.created_at.isoformat(),
                "overall_status": overall_status,
                "channel_statuses": {
                    channel.value: status.value
                    for channel, status in notification.delivery_status.items()
                },
                "delivery_attempts": dict(notification.delivery_attempts),
                "delivered_channels": [
                    channel.value for channel, timestamp in notification.delivered_at.items()
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification status: {e}")
            return None
            
    async def get_notification_metrics(self) -> Dict[str, Any]:
        """Get notification system metrics"""
        try:
            # Calculate success rates by channel
            channel_success_rates = {}
            for channel in NotificationChannel:
                analytics = self.delivery_analytics.get(f"{channel.value}_success", deque())
                if analytics:
                    recent_analytics = list(analytics)[-100:]  # Last 100 deliveries
                    success_rate = sum(1 for result in recent_analytics if result) / len(recent_analytics) * 100
                    channel_success_rates[channel.value] = success_rate
                else:
                    channel_success_rates[channel.value] = 0.0
                    
            # Calculate delivery rate
            current_time = datetime.now(timezone.utc)
            recent_deliveries = [
                notification for notification in self.notifications.values()
                if notification.created_at >= current_time - timedelta(minutes=10)
            ]
            delivery_rate = len(recent_deliveries) / 10.0  # Per minute over last 10 minutes
            
            # Count pending notifications
            pending_count = len(self.notification_queue) + sum(
                len(scheduled) for scheduled in self.scheduled_notifications.values()
            )
            
            return {
                "total_notifications": self.metrics.total_notifications,
                "successful_deliveries": self.metrics.successful_deliveries,
                "failed_deliveries": self.metrics.failed_deliveries,
                "pending_deliveries": pending_count,
                "delivery_rate_per_minute": delivery_rate,
                "average_delivery_time_ms": self.metrics.average_delivery_time_ms,
                "channel_success_rates": channel_success_rates,
                "active_websocket_connections": len(self.websocket_connections),
                "total_recipients": len(self.recipients),
                "total_rules": len(self.rules),
                "total_templates": len(self.templates),
                "last_updated": self.metrics.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification metrics: {e}")
            return {}
            
    async def _apply_notification_rules(self, notification: Notification) -> None:
        """Apply notification rules to determine routing"""
        try:
            # Sort rules by priority
            sorted_rules = sorted(
                self.rules.values(),
                key=lambda r: r.priority,
                reverse=True
            )
            
            for rule in sorted_rules:
                if not rule.enabled:
                    continue
                    
                # Check if all conditions match
                if await self._check_rule_conditions(notification, rule.conditions):
                    # Apply rule
                    if rule.channels:
                        notification.channels.extend(rule.channels)
                    if rule.recipients:
                        notification.recipients.extend(rule.recipients)
                    if rule.template_id:
                        notification.template_id = rule.template_id
                        
                    # Add rule tags to notification
                    notification.tags.update(rule.tags)
                    
                    # Check throttling
                    if rule.throttle_minutes > 0:
                        if await self._is_throttled(rule, notification):
                            logger.debug(f"Notification throttled by rule {rule.name}")
                            return
                            
                    logger.debug(f"Applied rule: {rule.name}")
                    
            # Remove duplicates
            notification.channels = list(set(notification.channels))
            notification.recipients = list(set(notification.recipients))
            
        except Exception as e:
            logger.error(f"Failed to apply notification rules: {e}")
            
    async def _check_rule_conditions(
        self,
        notification: Notification,
        conditions: List[NotificationFilter]
    ) -> bool:
        """Check if notification matches rule conditions"""
        try:
            for condition in conditions:
                if not condition.enabled:
                    continue
                    
                # Get field value from notification
                field_value = None
                if condition.field == "type":
                    field_value = notification.type.value
                elif condition.field == "priority":
                    field_value = notification.priority.value
                elif condition.field == "source":
                    field_value = notification.source
                elif condition.field == "title":
                    field_value = notification.title
                elif condition.field == "message":
                    field_value = notification.message
                elif condition.field in notification.data:
                    field_value = notification.data[condition.field]
                elif condition.field in notification.metadata:
                    field_value = notification.metadata[condition.field]
                    
                # Apply operator
                if not await self._apply_filter_operator(field_value, condition.operator, condition.value):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rule conditions: {e}")
            return False
            
    async def _apply_filter_operator(self, field_value: Any, operator: FilterOperator, condition_value: Any) -> bool:
        """Apply filter operator"""
        try:
            if operator == FilterOperator.EQUALS:
                return field_value == condition_value
            elif operator == FilterOperator.NOT_EQUALS:
                return field_value != condition_value
            elif operator == FilterOperator.CONTAINS:
                return str(condition_value) in str(field_value)
            elif operator == FilterOperator.NOT_CONTAINS:
                return str(condition_value) not in str(field_value)
            elif operator == FilterOperator.STARTS_WITH:
                return str(field_value).startswith(str(condition_value))
            elif operator == FilterOperator.ENDS_WITH:
                return str(field_value).endswith(str(condition_value))
            elif operator == FilterOperator.GREATER_THAN:
                return float(field_value) > float(condition_value)
            elif operator == FilterOperator.LESS_THAN:
                return float(field_value) < float(condition_value)
            elif operator == FilterOperator.IN:
                return field_value in condition_value
            elif operator == FilterOperator.NOT_IN:
                return field_value not in condition_value
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply filter operator: {e}")
            return False
            
    async def _is_throttled(self, rule: NotificationRule, notification: Notification) -> bool:
        """Check if notification is throttled by rule"""
        try:
            if rule.throttle_minutes <= 0:
                return False
                
            # Check throttling based on rule and notification combination
            throttle_key = f"{rule.rule_id}:{notification.type.value}:{notification.source}"
            
            now = datetime.now(timezone.utc)
            cutoff_time = now - timedelta(minutes=rule.throttle_minutes)
            
            # Check if similar notification was sent recently
            for existing_notification in self.notifications.values():
                if (existing_notification.type == notification.type and
                    existing_notification.source == notification.source and
                    existing_notification.created_at >= cutoff_time):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Failed to check throttling: {e}")
            return False
            
    async def _notification_processor(self) -> None:
        """Background notification processing task"""
        while not self._shutdown_event.is_set():
            try:
                if self.notification_queue:
                    notification_id = self.notification_queue.popleft()
                    await self._process_notification(notification_id)
                else:
                    await asyncio.sleep(0.1)  # Short delay if no notifications
                    
            except Exception as e:
                logger.error(f"Notification processor error: {e}")
                
    async def _process_notification(self, notification_id: str) -> None:
        """Process a single notification"""
        try:
            if notification_id not in self.notifications:
                return
                
            notification = self.notifications[notification_id]
            
            # Check if notification has expired
            if (notification.expires_at and 
                notification.expires_at < datetime.now(timezone.utc)):
                logger.debug(f"Notification expired: {notification_id}")
                return
                
            # Deliver to each channel
            for channel in notification.channels:
                await self._deliver_to_channel(notification, channel)
                
            # Deliver to WebSocket connections if real-time is enabled
            if self.enable_real_time:
                await self._deliver_to_websockets(notification)
                
        except Exception as e:
            logger.error(f"Failed to process notification {notification_id}: {e}")
            
    async def _deliver_to_channel(self, notification: Notification, channel: NotificationChannel) -> None:
        """Deliver notification to specific channel"""
        try:
            start_time = time.time()
            
            # Initialize delivery status
            notification.delivery_status[channel] = DeliveryStatus.PENDING
            notification.delivery_attempts[channel] = notification.delivery_attempts.get(channel, 0) + 1
            
            # Format message using template if specified
            formatted_message = await self._format_notification(notification, channel)
            
            # Get recipients for this channel
            channel_recipients = []
            for recipient_id in notification.recipients:
                if recipient_id in self.recipients:
                    recipient = self.recipients[recipient_id]
                    if channel in recipient.channels and recipient.enabled:
                        channel_recipients.append(recipient)
                        
            if not channel_recipients:
                logger.debug(f"No recipients for channel {channel.value}")
                return
                
            # Deliver using channel handler
            if channel in self.channel_handlers:
                handler = self.channel_handlers[channel]
                
                try:
                    success = await handler(notification, channel_recipients, formatted_message)
                    
                    if success:
                        notification.delivery_status[channel] = DeliveryStatus.DELIVERED
                        notification.delivered_at[channel] = datetime.now(timezone.utc)
                        self.metrics.successful_deliveries += 1
                        
                        # Record success in analytics
                        self.delivery_analytics[f"{channel.value}_success"].append(True)
                    else:
                        notification.delivery_status[channel] = DeliveryStatus.FAILED
                        self.metrics.failed_deliveries += 1
                        
                        # Record failure in analytics
                        self.delivery_analytics[f"{channel.value}_success"].append(False)
                        
                        # Retry if under limit
                        if notification.delivery_attempts[channel] < self.max_retry_attempts:
                            notification.delivery_status[channel] = DeliveryStatus.RETRYING
                            # Re-queue for retry with delay
                            await asyncio.sleep(2 ** notification.delivery_attempts[channel])  # Exponential backoff
                            self.notification_queue.append(notification.notification_id)
                            
                except Exception as e:
                    logger.error(f"Channel handler failed for {channel.value}: {e}")
                    notification.delivery_status[channel] = DeliveryStatus.FAILED
                    self.metrics.failed_deliveries += 1
            else:
                logger.warning(f"No handler registered for channel {channel.value}")
                notification.delivery_status[channel] = DeliveryStatus.FAILED
                
            # Update metrics
            delivery_time = (time.time() - start_time) * 1000
            total_deliveries = self.metrics.successful_deliveries + self.metrics.failed_deliveries
            if total_deliveries > 0:
                self.metrics.average_delivery_time_ms = (
                    (self.metrics.average_delivery_time_ms * (total_deliveries - 1) + delivery_time) / total_deliveries
                )
            else:
                self.metrics.average_delivery_time_ms = delivery_time
                
        except Exception as e:
            logger.error(f"Failed to deliver to channel {channel.value}: {e}")
            
    async def _deliver_to_websockets(self, notification: Notification) -> None:
        """Deliver notification to WebSocket connections"""
        try:
            message = {
                "type": "notification",
                "data": {
                    "id": notification.notification_id,
                    "type": notification.type.value,
                    "priority": notification.priority.value,
                    "title": notification.title,
                    "message": notification.message,
                    "timestamp": notification.created_at.isoformat(),
                    "data": notification.data
                }
            }
            
            # Send to relevant WebSocket connections
            disconnected_connections = []
            
            for connection_id, connection_info in self.websocket_connections.items():
                try:
                    websocket = connection_info["websocket"]
                    recipient_id = connection_info.get("recipient_id")
                    
                    # Check if this connection should receive the notification
                    should_send = (
                        not notification.recipients or
                        not recipient_id or
                        recipient_id in notification.recipients
                    )
                    
                    if should_send:
                        await websocket.send(json.dumps(message))
                        
                except Exception as e:
                    logger.error(f"Failed to send WebSocket notification: {e}")
                    disconnected_connections.append(connection_id)
                    
            # Clean up disconnected connections
            for connection_id in disconnected_connections:
                del self.websocket_connections[connection_id]
                
        except Exception as e:
            logger.error(f"Failed to deliver to WebSockets: {e}")
            
    async def _format_notification(self, notification: Notification, channel: NotificationChannel) -> Dict[str, str]:
        """Format notification using template"""
        try:
            if not notification.template_id or notification.template_id not in self.templates:
                # Use default formatting
                return {
                    "subject": notification.title,
                    "body": notification.message
                }
                
            template = self.templates[notification.template_id]
            
            if template.channel != channel:
                # Template doesn't match channel, use default
                return {
                    "subject": notification.title,
                    "body": notification.message
                }
                
            # Prepare template variables
            variables = {
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "priority": notification.priority.value,
                "timestamp": notification.created_at.isoformat(),
                **notification.data
            }
            
            # Format subject
            subject = template.subject_template
            for var_name, var_value in variables.items():
                subject = subject.replace(f"{{{var_name}}}", str(var_value))
                
            # Format body
            body = template.body_template
            for var_name, var_value in variables.items():
                body = body.replace(f"{{{var_name}}}", str(var_value))
                
            return {
                "subject": subject,
                "body": body
            }
            
        except Exception as e:
            logger.error(f"Failed to format notification: {e}")
            return {
                "subject": notification.title,
                "body": notification.message
            }
            
    async def _notification_scheduler(self) -> None:
        """Background notification scheduling task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                current_time = datetime.now(timezone.utc)
                
                # Process scheduled notifications
                due_times = [
                    scheduled_time for scheduled_time in self.scheduled_notifications.keys()
                    if scheduled_time <= current_time
                ]
                
                for due_time in due_times:
                    notification_ids = self.scheduled_notifications[due_time]
                    
                    for notification_id in notification_ids:
                        self.notification_queue.append(notification_id)
                        
                    del self.scheduled_notifications[due_time]
                    
                    if notification_ids:
                        logger.debug(f"Scheduled {len(notification_ids)} notifications for processing")
                        
            except Exception as e:
                logger.error(f"Notification scheduler error: {e}")
                
    async def _metrics_collector(self) -> None:
        """Background metrics collection task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Update metrics
                self.metrics.last_updated = datetime.now(timezone.utc)
                
                # Calculate pending deliveries
                pending_count = len(self.notification_queue) + sum(
                    len(scheduled) for scheduled in self.scheduled_notifications.values()
                )
                self.metrics.pending_deliveries = pending_count
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                
    async def _cleanup_worker(self) -> None:
        """Background cleanup task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Clean old notifications
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
                old_notifications = [
                    nid for nid, notification in self.notifications.items()
                    if notification.created_at < cutoff_time
                ]
                
                for notification_id in old_notifications:
                    del self.notifications[notification_id]
                    
                # Clean old delivery analytics
                for analytics_key in self.delivery_analytics.keys():
                    # Keep only recent data (already limited by deque maxlen)
                    pass
                    
                # Clean stale WebSocket connections
                stale_connections = []
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                
                for connection_id, connection_info in self.websocket_connections.items():
                    if connection_info["connected_at"] < cutoff_time:
                        stale_connections.append(connection_id)
                        
                for connection_id in stale_connections:
                    del self.websocket_connections[connection_id]
                    
                if old_notifications or stale_connections:
                    logger.info(f"Cleanup completed: removed {len(old_notifications)} notifications, {len(stale_connections)} stale connections")
                    
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                
    def _init_default_templates(self) -> None:
        """Initialize default notification templates"""
        try:
            # Email alert template
            self.templates["email_alert"] = NotificationTemplate(
                template_id="email_alert",
                name="Email Alert",
                channel=NotificationChannel.EMAIL,
                subject_template="Alert: {title}",
                body_template="Dear recipient,\n\nAn alert has been triggered:\n\nTitle: {title}\nMessage: {message}\nType: {type}\nPriority: {priority}\nTime: {timestamp}\n\nPlease take appropriate action.\n\nBest regards,\nAinflue System",
                variables=["title", "message", "type", "priority", "timestamp"]
            )
            
            # SMS alert template
            self.templates["sms_alert"] = NotificationTemplate(
                template_id="sms_alert",
                name="SMS Alert",
                channel=NotificationChannel.SMS,
                body_template="ALERT: {title} - {message} ({priority}) at {timestamp}",
                variables=["title", "message", "priority", "timestamp"]
            )
            
            # WebSocket notification template
            self.templates["websocket_notification"] = NotificationTemplate(
                template_id="websocket_notification",
                name="WebSocket Notification",
                channel=NotificationChannel.WEBSOCKET,
                body_template='{"title": "{title}", "message": "{message}", "type": "{type}", "priority": "{priority}"}',
                variables=["title", "message", "type", "priority"]
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize default templates: {e}")
            
    async def _register_default_handlers(self) -> None:
        """Register default channel handlers"""
        try:
            # Email handler (simulated)
            async def email_handler(notification, recipients, formatted_message):
                # Simulate email sending
                await asyncio.sleep(0.1)  # Simulate network delay
                logger.info(f"Email sent: {formatted_message['subject']} to {len(recipients)} recipients")
                return True
                
            # SMS handler (simulated)
            async def sms_handler(notification, recipients, formatted_message):
                # Simulate SMS sending
                await asyncio.sleep(0.05)  # Simulate network delay
                logger.info(f"SMS sent: {formatted_message['body'][:50]}... to {len(recipients)} recipients")
                return True
                
            # WebHook handler (simulated)
            async def webhook_handler(notification, recipients, formatted_message):
                # Simulate webhook call
                await asyncio.sleep(0.1)  # Simulate network delay
                logger.info(f"Webhook called for notification {notification.notification_id}")
                return True
                
            # Register handlers
            self.channel_handlers[NotificationChannel.EMAIL] = email_handler
            self.channel_handlers[NotificationChannel.SMS] = sms_handler
            self.channel_handlers[NotificationChannel.WEBHOOK] = webhook_handler
            
        except Exception as e:
            logger.error(f"Failed to register default handlers: {e}")
            
    async def shutdown(self) -> None:
        """Gracefully shutdown the notification streams system"""
        try:
            logger.info("Shutting down NotificationStreams...")
            
            self._shutdown_event.set()
            
            # Cancel background tasks
            tasks_to_cancel = [
                self.notification_processor_task,
                self.scheduler_task,
                self.metrics_collector_task,
                self.cleanup_task
            ]
            
            for task in tasks_to_cancel:
                if task:
                    task.cancel()
                    
            # Close WebSocket connections
            for connection_info in self.websocket_connections.values():
                try:
                    websocket = connection_info["websocket"]
                    await websocket.close()
                except:
                    pass
                    
            self._running = False
            logger.info("NotificationStreams shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")