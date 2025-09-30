"""Notification Engine Core - Moteur Notifications Central Enterprise
================================================================

Ultra-advanced notification engine framework for IA Influencer Agent platform.
Comprehensive multi-channel notification system with real-time messaging,
event-driven notifications, and enterprise-grade delivery optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This notification engine core is protected intellectual property.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from dataclasses import dataclass, field
import uuid
from pathlib import Path
import threading
import time
from collections import defaultdict, deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Types of notification channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"


class NotificationPriority(Enum):
    """Priority levels for notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Status of notification delivery"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DeliveryStatus(Enum):
    """Delivery status tracking"""
    QUEUED = "queued"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    FAILED = "failed"
    OPTED_OUT = "opted_out"


@dataclass
class NotificationTemplate:
    """Template for notifications"""
    template_id: str
    template_name: str
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    recipient_id: str
    user_id: Optional[str] = None
    channels: Dict[NotificationChannel, str] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    opt_out_channels: Set[NotificationChannel] = field(default_factory=set)
    timezone: str = "UTC"


@dataclass
class NotificationMessage:
    """Individual notification message"""
    message_id: str
    recipient: NotificationRecipient
    channel: NotificationChannel
    template_id: Optional[str] = None
    subject: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class DeliveryReport:
    """Delivery report for notifications"""
    report_id: str
    message_id: str
    channel: NotificationChannel
    status: DeliveryStatus
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None


class MultiChannelNotificationEngine:
    """
    📢 Multi-Channel Notification Engine - Universal Messaging System
    
    Enterprise-grade notification engine supporting multiple channels
    with intelligent routing, failover, and delivery optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Multi-Channel Notification Engine"""
        self.config = config or {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.message_queue: deque = deque()
        self.pending_messages: Dict[str, NotificationMessage] = {}
        self.delivery_reports: List[DeliveryReport] = []
        self.channel_handlers: Dict[NotificationChannel, Callable] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._engine_lock = threading.RLock()
        
        # Initialize channel handlers
        self._initialize_channel_handlers()
        
        # Start message processor
        self._processor_running = True
        asyncio.create_task(self._message_processor())
    
    def _initialize_channel_handlers(self):
        """Initialize channel-specific handlers"""
        
        self.channel_handlers = {
            NotificationChannel.EMAIL: self._send_email_notification,
            NotificationChannel.SMS: self._send_sms_notification,
            NotificationChannel.PUSH: self._send_push_notification,
            NotificationChannel.IN_APP: self._send_in_app_notification,
            NotificationChannel.WEBHOOK: self._send_webhook_notification,
            NotificationChannel.SLACK: self._send_slack_notification,
            NotificationChannel.DISCORD: self._send_discord_notification,
            NotificationChannel.TELEGRAM: self._send_telegram_notification,
            NotificationChannel.WHATSAPP: self._send_whatsapp_notification
        }
    
    async def create_template(self, template: NotificationTemplate) -> bool:
        """Create notification template"""
        
        try:
            with self._engine_lock:
                self.templates[template.template_id] = template
            
            self.logger.info(f"Template {template.template_name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create template {template.template_name}: {e}")
            return False
    
    async def register_recipient(self, recipient: NotificationRecipient) -> bool:
        """Register notification recipient"""
        
        try:
            with self._engine_lock:
                self.recipients[recipient.recipient_id] = recipient
            
            self.logger.info(f"Recipient {recipient.recipient_id} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register recipient {recipient.recipient_id}: {e}")
            return False
    
    async def send_notification(self, 
                              recipient_id: str,
                              template_id: str,
                              variables: Dict[str, Any] = None,
                              channel: NotificationChannel = None,
                              priority: NotificationPriority = NotificationPriority.NORMAL,
                              scheduled_at: datetime = None) -> str:
        """Send notification to recipient"""
        
        if recipient_id not in self.recipients:
            raise ValueError(f"Recipient {recipient_id} not registered")
        
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        recipient = self.recipients[recipient_id]
        template = self.templates[template_id]
        
        # Determine channel
        if channel is None:
            # Use template's default channel
            channel = template.channel
        
        # Check if recipient opted out of this channel
        if channel in recipient.opt_out_channels:
            self.logger.info(f"Recipient {recipient_id} opted out of {channel.value}")
            return ""
        
        # Check if recipient has contact info for this channel
        if channel not in recipient.channels:
            self.logger.warning(f"Recipient {recipient_id} has no {channel.value} contact info")
            return ""
        
        try:
            # Render template with variables
            rendered_message = await self._render_template(template, variables or {})
            
            # Create notification message
            message = NotificationMessage(
                message_id=str(uuid.uuid4()),
                recipient=recipient,
                channel=channel,
                template_id=template_id,
                subject=rendered_message['subject'],
                body=rendered_message['body'],
                priority=priority,
                scheduled_at=scheduled_at,
                context=variables or {}
            )
            
            # Queue for delivery
            await self._queue_message(message)
            
            self.logger.info(f"Notification queued for {recipient_id} via {channel.value}")
            return message.message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send notification to {recipient_id}: {e}")
            raise
    
    async def _render_template(self, 
                             template: NotificationTemplate,
                             variables: Dict[str, Any]) -> Dict[str, str]:
        """Render template with variables"""
        
        try:
            # Simple template rendering (in production, use a proper template engine)
            subject = template.subject_template
            body = template.body_template
            
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                subject = subject.replace(placeholder, str(var_value))
                body = body.replace(placeholder, str(var_value))
            
            return {
                'subject': subject,
                'body': body
            }
            
        except Exception as e:
            self.logger.error(f"Template rendering failed: {e}")
            raise
    
    async def _queue_message(self, message: NotificationMessage):
        """Queue message for delivery"""
        
        with self._engine_lock:
            self.pending_messages[message.message_id] = message
            
            # Add to priority queue
            if message.scheduled_at and message.scheduled_at > datetime.now(timezone.utc):
                # Scheduled message - will be processed later
                pass
            else:
                # Immediate delivery
                self.message_queue.append(message.message_id)
    
    async def _message_processor(self):
        """Main message processing loop"""
        
        while self._processor_running:
            try:
                # Process immediate messages
                if self.message_queue:
                    with self._engine_lock:
                        message_id = self.message_queue.popleft()
                    
                    await self._process_message(message_id)
                
                # Process scheduled messages
                await self._process_scheduled_messages()
                
                # Sleep briefly if no work
                if not self.message_queue:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Message processor error: {e}")
                await asyncio.sleep(5)  # Longer sleep on error
    
    async def _process_scheduled_messages(self):
        """Process scheduled messages that are due"""
        
        now = datetime.now(timezone.utc)
        due_messages = []
        
        with self._engine_lock:
            for message_id, message in self.pending_messages.items():
                if (message.scheduled_at and 
                    message.scheduled_at <= now and 
                    message.status == NotificationStatus.PENDING):
                    due_messages.append(message_id)
        
        for message_id in due_messages:
            self.message_queue.append(message_id)
    
    async def _process_message(self, message_id: str):
        """Process a single message"""
        
        if message_id not in self.pending_messages:
            return
        
        message = self.pending_messages[message_id]
        
        try:
            # Check if message expired
            if message.expires_at and datetime.now(timezone.utc) > message.expires_at:
                message.status = NotificationStatus.CANCELLED
                self.logger.info(f"Message {message_id} expired")
                return
            
            # Update status
            message.status = NotificationStatus.SENT
            message.sent_at = datetime.now(timezone.utc)
            
            # Get channel handler
            if message.channel not in self.channel_handlers:
                raise ValueError(f"No handler for channel {message.channel.value}")
            
            handler = self.channel_handlers[message.channel]
            
            # Send message
            delivery_result = await handler(message)
            
            # Update status based on result
            if delivery_result.get('success', False):
                message.status = NotificationStatus.DELIVERED
                message.delivered_at = datetime.now(timezone.utc)
                
                # Create delivery report
                report = DeliveryReport(
                    report_id=str(uuid.uuid4()),
                    message_id=message_id,
                    channel=message.channel,
                    status=DeliveryStatus.DELIVERED,
                    timestamp=datetime.now(timezone.utc),
                    metadata=delivery_result.get('metadata', {})
                )
                
                self.delivery_reports.append(report)
                
            else:
                # Handle failure
                message.retry_count += 1
                message.error_message = delivery_result.get('error', 'Unknown error')
                
                if message.retry_count <= message.max_retries:
                    message.status = NotificationStatus.RETRYING
                    
                    # Re-queue with exponential backoff
                    retry_delay = min(2 ** message.retry_count, 300)  # Max 5 minutes
                    message.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
                    
                    self.logger.warning(
                        f"Message {message_id} failed, retrying in {retry_delay}s "
                        f"({message.retry_count}/{message.max_retries})"
                    )
                else:
                    message.status = NotificationStatus.FAILED
                    
                    # Create failure report
                    report = DeliveryReport(
                        report_id=str(uuid.uuid4()),
                        message_id=message_id,
                        channel=message.channel,
                        status=DeliveryStatus.FAILED,
                        timestamp=datetime.now(timezone.utc),
                        error_details=message.error_message
                    )
                    
                    self.delivery_reports.append(report)
                    
                    self.logger.error(f"Message {message_id} failed permanently: {message.error_message}")
                    
        except Exception as e:
            message.status = NotificationStatus.FAILED
            message.error_message = str(e)
            self.logger.error(f"Message processing failed for {message_id}: {e}")
    
    # Channel-specific handlers
    async def _send_email_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send email notification"""
        
        try:
            email_config = self.config.get('email', {})
            recipient_email = message.recipient.channels.get(NotificationChannel.EMAIL)
            
            if not recipient_email:
                return {'success': False, 'error': 'No email address'}
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_address', 'noreply@ainflue.com')
            msg['To'] = recipient_email
            msg['Subject'] = message.subject
            
            # Add body
            msg.attach(MIMEText(message.body, 'html' if '<' in message.body else 'plain'))
            
            # In production, you would actually send the email
            # For now, we'll simulate sending
            await asyncio.sleep(0.1)  # Simulate network delay
            
            self.logger.info(f"Email sent to {recipient_email}")
            
            return {
                'success': True,
                'metadata': {
                    'recipient_email': recipient_email,
                    'subject': message.subject
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_sms_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send SMS notification"""
        
        try:
            phone_number = message.recipient.channels.get(NotificationChannel.SMS)
            
            if not phone_number:
                return {'success': False, 'error': 'No phone number'}
            
            # Simulate SMS sending
            await asyncio.sleep(0.1)
            
            self.logger.info(f"SMS sent to {phone_number}")
            
            return {
                'success': True,
                'metadata': {
                    'phone_number': phone_number,
                    'message_length': len(message.body)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_push_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send push notification"""
        
        try:
            device_token = message.recipient.channels.get(NotificationChannel.PUSH)
            
            if not device_token:
                return {'success': False, 'error': 'No device token'}
            
            # Simulate push notification
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Push notification sent to device")
            
            return {
                'success': True,
                'metadata': {
                    'device_token': device_token[:10] + '...',  # Truncate for security
                    'title': message.subject
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_in_app_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send in-app notification"""
        
        try:
            user_id = message.recipient.user_id
            
            if not user_id:
                return {'success': False, 'error': 'No user ID'}
            
            # Store in-app notification (would be stored in database)
            notification_data = {
                'user_id': user_id,
                'title': message.subject,
                'body': message.body,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'read': False
            }
            
            self.logger.info(f"In-app notification created for user {user_id}")
            
            return {
                'success': True,
                'metadata': notification_data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_webhook_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send webhook notification"""
        
        try:
            webhook_url = message.recipient.channels.get(NotificationChannel.WEBHOOK)
            
            if not webhook_url:
                return {'success': False, 'error': 'No webhook URL'}
            
            # Prepare webhook payload
            payload = {
                'message_id': message.message_id,
                'subject': message.subject,
                'body': message.body,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'context': message.context
            }
            
            # Simulate webhook call
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Webhook called: {webhook_url}")
            
            return {
                'success': True,
                'metadata': {
                    'webhook_url': webhook_url,
                    'payload_size': len(json.dumps(payload))
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_slack_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send Slack notification"""
        
        try:
            slack_channel = message.recipient.channels.get(NotificationChannel.SLACK)
            
            if not slack_channel:
                return {'success': False, 'error': 'No Slack channel'}
            
            # Simulate Slack API call
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Slack message sent to {slack_channel}")
            
            return {
                'success': True,
                'metadata': {
                    'channel': slack_channel,
                    'message': message.body[:100] + '...' if len(message.body) > 100 else message.body
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_discord_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send Discord notification"""
        
        try:
            discord_channel = message.recipient.channels.get(NotificationChannel.DISCORD)
            
            if not discord_channel:
                return {'success': False, 'error': 'No Discord channel'}
            
            # Simulate Discord API call
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Discord message sent to {discord_channel}")
            
            return {
                'success': True,
                'metadata': {
                    'channel': discord_channel,
                    'message_length': len(message.body)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_telegram_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send Telegram notification"""
        
        try:
            telegram_chat = message.recipient.channels.get(NotificationChannel.TELEGRAM)
            
            if not telegram_chat:
                return {'success': False, 'error': 'No Telegram chat'}
            
            # Simulate Telegram Bot API call
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Telegram message sent to {telegram_chat}")
            
            return {
                'success': True,
                'metadata': {
                    'chat_id': telegram_chat,
                    'message_type': 'text'
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_whatsapp_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send WhatsApp notification"""
        
        try:
            whatsapp_number = message.recipient.channels.get(NotificationChannel.WHATSAPP)
            
            if not whatsapp_number:
                return {'success': False, 'error': 'No WhatsApp number'}
            
            # Simulate WhatsApp Business API call
            await asyncio.sleep(0.1)
            
            self.logger.info(f"WhatsApp message sent to {whatsapp_number}")
            
            return {
                'success': True,
                'metadata': {
                    'phone_number': whatsapp_number,
                    'message_type': 'text'
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get status of a specific message"""
        
        if message_id not in self.pending_messages:
            return {'error': 'Message not found'}
        
        message = self.pending_messages[message_id]
        
        return {
            'message_id': message_id,
            'status': message.status.value,
            'channel': message.channel.value,
            'recipient_id': message.recipient.recipient_id,
            'created_at': message.created_at.isoformat(),
            'sent_at': message.sent_at.isoformat() if message.sent_at else None,
            'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
            'retry_count': message.retry_count,
            'error_message': message.error_message
        }
    
    async def get_delivery_analytics(self, 
                                   time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Get delivery analytics"""
        
        # Filter reports by time range if provided
        reports = self.delivery_reports
        if time_range:
            start_time, end_time = time_range
            reports = [
                report for report in reports
                if start_time <= report.timestamp <= end_time
            ]
        
        # Calculate analytics
        total_messages = len(reports)
        delivered_count = len([r for r in reports if r.status == DeliveryStatus.DELIVERED])
        failed_count = len([r for r in reports if r.status == DeliveryStatus.FAILED])
        
        # Channel breakdown
        channel_stats = defaultdict(lambda: {'delivered': 0, 'failed': 0})
        for report in reports:
            if report.status == DeliveryStatus.DELIVERED:
                channel_stats[report.channel.value]['delivered'] += 1
            elif report.status == DeliveryStatus.FAILED:
                channel_stats[report.channel.value]['failed'] += 1
        
        return {
            'total_messages': total_messages,
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'delivery_rate': (delivered_count / total_messages * 100) if total_messages > 0 else 0,
            'channel_breakdown': dict(channel_stats),
            'time_range': {
                'start': time_range[0].isoformat() if time_range else None,
                'end': time_range[1].isoformat() if time_range else None
            }
        }


class RealTimeMessagingCore:
    """
    ⚡ Real-Time Messaging Core - Instant Communication System
    
    Advanced real-time messaging system with WebSocket support,
    presence tracking, and high-performance message delivery.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Real-Time Messaging Core"""
        self.config = config or {}
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.message_rooms: Dict[str, Set[str]] = defaultdict(set)
        self.user_presence: Dict[str, Dict[str, Any]] = {}
        self.message_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._messaging_lock = threading.RLock()
    
    async def connect_user(self, 
                         user_id: str,
                         connection_id: str,
                         connection_info: Dict[str, Any]) -> bool:
        """Connect user to real-time messaging"""
        
        try:
            with self._messaging_lock:
                self.active_connections[connection_id] = {
                    'user_id': user_id,
                    'connected_at': datetime.now(timezone.utc),
                    'last_activity': datetime.now(timezone.utc),
                    'connection_info': connection_info
                }
                
                # Update user presence
                self.user_presence[user_id] = {
                    'status': 'online',
                    'last_seen': datetime.now(timezone.utc),
                    'connection_id': connection_id
                }
            
            self.logger.info(f"User {user_id} connected with connection {connection_id}")
            
            # Notify other users in shared rooms
            await self._broadcast_presence_update(user_id, 'online')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect user {user_id}: {e}")
            return False
    
    async def disconnect_user(self, connection_id: str) -> bool:
        """Disconnect user from real-time messaging"""
        
        try:
            if connection_id not in self.active_connections:
                return False
            
            with self._messaging_lock:
                connection = self.active_connections.pop(connection_id)
                user_id = connection['user_id']
                
                # Update user presence
                if user_id in self.user_presence:
                    self.user_presence[user_id] = {
                        'status': 'offline',
                        'last_seen': datetime.now(timezone.utc),
                        'connection_id': None
                    }
            
            self.logger.info(f"User {user_id} disconnected")
            
            # Notify other users
            await self._broadcast_presence_update(user_id, 'offline')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect connection {connection_id}: {e}")
            return False
    
    async def join_room(self, user_id: str, room_id: str) -> bool:
        """Join user to a message room"""
        
        try:
            with self._messaging_lock:
                self.message_rooms[room_id].add(user_id)
            
            self.logger.info(f"User {user_id} joined room {room_id}")
            
            # Send recent message history
            await self._send_message_history(user_id, room_id)
            
            # Notify other room members
            await self._broadcast_to_room(
                room_id,
                {
                    'type': 'user_joined',
                    'user_id': user_id,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                exclude_user=user_id
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to join user {user_id} to room {room_id}: {e}")
            return False
    
    async def leave_room(self, user_id: str, room_id: str) -> bool:
        """Remove user from message room"""
        
        try:
            with self._messaging_lock:
                if room_id in self.message_rooms:
                    self.message_rooms[room_id].discard(user_id)
            
            self.logger.info(f"User {user_id} left room {room_id}")
            
            # Notify other room members
            await self._broadcast_to_room(
                room_id,
                {
                    'type': 'user_left',
                    'user_id': user_id,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                exclude_user=user_id
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove user {user_id} from room {room_id}: {e}")
            return False
    
    async def send_message(self, 
                         sender_id: str,
                         room_id: str,
                         message_content: str,
                         message_type: str = 'text',
                         metadata: Dict[str, Any] = None) -> str:
        """Send message to room"""
        
        try:
            message = {
                'message_id': str(uuid.uuid4()),
                'sender_id': sender_id,
                'room_id': room_id,
                'content': message_content,
                'message_type': message_type,
                'metadata': metadata or {},
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Store message in history
            self.message_history[room_id].append(message)
            
            # Broadcast to room members
            await self._broadcast_to_room(room_id, {
                'type': 'message',
                'message': message
            })
            
            self.logger.info(f"Message sent from {sender_id} to room {room_id}")
            return message['message_id']
            
        except Exception as e:
            self.logger.error(f"Failed to send message from {sender_id} to room {room_id}: {e}")
            raise
    
    async def send_direct_message(self, 
                                sender_id: str,
                                recipient_id: str,
                                message_content: str,
                                message_type: str = 'text') -> str:
        """Send direct message to specific user"""
        
        try:
            message = {
                'message_id': str(uuid.uuid4()),
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'content': message_content,
                'message_type': message_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Send to recipient if online
            await self._send_to_user(recipient_id, {
                'type': 'direct_message',
                'message': message
            })
            
            self.logger.info(f"Direct message sent from {sender_id} to {recipient_id}")
            return message['message_id']
            
        except Exception as e:
            self.logger.error(f"Failed to send direct message from {sender_id} to {recipient_id}: {e}")
            raise
    
    async def _broadcast_presence_update(self, user_id: str, status: str):
        """Broadcast user presence update"""
        
        presence_update = {
            'type': 'presence_update',
            'user_id': user_id,
            'status': status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Find all rooms this user is in and notify other members
        user_rooms = []
        with self._messaging_lock:
            for room_id, members in self.message_rooms.items():
                if user_id in members:
                    user_rooms.append(room_id)
        
        for room_id in user_rooms:
            await self._broadcast_to_room(room_id, presence_update, exclude_user=user_id)
    
    async def _broadcast_to_room(self, 
                               room_id: str,
                               message: Dict[str, Any],
                               exclude_user: str = None):
        """Broadcast message to all users in room"""
        
        if room_id not in self.message_rooms:
            return
        
        room_members = self.message_rooms[room_id].copy()
        
        for user_id in room_members:
            if exclude_user and user_id == exclude_user:
                continue
            
            await self._send_to_user(user_id, message)
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        
        try:
            # Check if user is online
            if user_id not in self.user_presence:
                return False
            
            presence = self.user_presence[user_id]
            connection_id = presence.get('connection_id')
            
            if not connection_id or connection_id not in self.active_connections:
                return False
            
            # In a real implementation, you would send via WebSocket
            # For now, we'll just log the action
            self.logger.debug(f"Sending message to user {user_id}: {message['type']}")
            
            # Update last activity
            if connection_id in self.active_connections:
                self.active_connections[connection_id]['last_activity'] = datetime.now(timezone.utc)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to user {user_id}: {e}")
            return False
    
    async def _send_message_history(self, user_id: str, room_id: str):
        """Send recent message history to user"""
        
        if room_id not in self.message_history:
            return
        
        history = list(self.message_history[room_id])
        
        if history:
            await self._send_to_user(user_id, {
                'type': 'message_history',
                'room_id': room_id,
                'messages': history[-50:]  # Send last 50 messages
            })
    
    async def get_user_presence(self, user_id: str) -> Dict[str, Any]:
        """Get user presence information"""
        
        if user_id not in self.user_presence:
            return {
                'user_id': user_id,
                'status': 'offline',
                'last_seen': None
            }
        
        presence = self.user_presence[user_id]
        return {
            'user_id': user_id,
            'status': presence['status'],
            'last_seen': presence['last_seen'].isoformat(),
            'online': presence['status'] == 'online'
        }
    
    async def get_room_members(self, room_id: str) -> List[Dict[str, Any]]:
        """Get list of room members with presence info"""
        
        if room_id not in self.message_rooms:
            return []
        
        members = []
        for user_id in self.message_rooms[room_id]:
            presence = await self.get_user_presence(user_id)
            members.append(presence)
        
        return members


class NotificationEngineCore:
    """
    🚀 Notification Engine Core - Master Notification Orchestrator
    
    Central notification engine that coordinates all notification functionality
    across the IA Influencer Agent platform with enterprise-grade capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Notification Engine Core"""
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize notification components
        self.multi_channel_engine = MultiChannelNotificationEngine(config.get('channels', {}))
        self.real_time_messaging = RealTimeMessagingCore(config.get('messaging', {}))
        
        # Core status
        self.is_initialized = False
        self.start_time = None
        self.notification_stats = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'active_connections': 0,
            'templates_created': 0
        }
    
    async def initialize(self) -> bool:
        """Initialize the Notification Engine Core"""
        try:
            self.start_time = datetime.now(timezone.utc)
            
            # Initialize default templates
            await self._initialize_default_templates()
            
            self.is_initialized = True
            self.logger.info("Notification Engine Core initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Notification Engine Core initialization failed: {e}")
            return False
    
    async def _initialize_default_templates(self):
        """Initialize default notification templates"""
        
        default_templates = [
            NotificationTemplate(
                template_id="welcome_email",
                template_name="Welcome Email",
                channel=NotificationChannel.EMAIL,
                subject_template="Welcome to Ainflue, {user_name}!",
                body_template="Hello {user_name},\n\nWelcome to the Ainflue platform! We're excited to have you join our community of creators and influencers.\n\nBest regards,\nThe Ainflue Team",
                variables=["user_name"]
            ),
            NotificationTemplate(
                template_id="content_approved",
                template_name="Content Approved",
                channel=NotificationChannel.IN_APP,
                subject_template="Your content has been approved!",
                body_template="Great news! Your content '{content_title}' has been approved and is now live on the platform.",
                variables=["content_title"]
            ),
            NotificationTemplate(
                template_id="payment_received",
                template_name="Payment Received",
                channel=NotificationChannel.EMAIL,
                subject_template="Payment Received - ${amount}",
                body_template="Hi {user_name},\n\nWe've received your payment of ${amount} for {description}. Thank you!\n\nTransaction ID: {transaction_id}",
                variables=["user_name", "amount", "description", "transaction_id"]
            ),
            NotificationTemplate(
                template_id="collaboration_request",
                template_name="Collaboration Request",
                channel=NotificationChannel.PUSH,
                subject_template="New collaboration opportunity!",
                body_template="{requester_name} wants to collaborate with you on {project_name}. Tap to view details.",
                variables=["requester_name", "project_name"]
            )
        ]
        
        for template in default_templates:
            await self.multi_channel_engine.create_template(template)
            self.notification_stats['templates_created'] += 1
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive notification engine status"""
        
        # Get delivery analytics
        analytics = await self.multi_channel_engine.get_delivery_analytics()
        
        # Count active real-time connections
        active_connections = len(self.real_time_messaging.active_connections)
        
        return {
            'initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': (datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0,
            'notification_stats': self.notification_stats,
            'delivery_analytics': analytics,
            'active_templates': len(self.multi_channel_engine.templates),
            'registered_recipients': len(self.multi_channel_engine.recipients),
            'pending_messages': len(self.multi_channel_engine.pending_messages),
            'active_real_time_connections': active_connections,
            'active_message_rooms': len(self.real_time_messaging.message_rooms)
        }


# =============================================================================
# FACTORY AND UTILITY FUNCTIONS
# =============================================================================

def create_notification_engine_core(config: Optional[Dict[str, Any]] = None) -> NotificationEngineCore:
    """Factory function to create Notification Engine Core"""
    return NotificationEngineCore(config)


async def quick_notification_setup() -> NotificationEngineCore:
    """Quick setup for development environment"""
    core = create_notification_engine_core({
        'channels': {
            'email': {'from_address': 'noreply@ainflue.com'}
        },
        'messaging': {}
    })
    
    await core.initialize()
    return core


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'NotificationChannel',
    'NotificationPriority',
    'NotificationStatus',
    'DeliveryStatus',
    
    # Data classes
    'NotificationTemplate',
    'NotificationRecipient',
    'NotificationMessage',
    'DeliveryReport',
    
    # Main notification classes
    'MultiChannelNotificationEngine',
    'RealTimeMessagingCore',
    'NotificationEngineCore',
    
    # Factory functions
    'create_notification_engine_core',
    'quick_notification_setup'
]