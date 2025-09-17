#!/usr/bin/env python3
"""
📬 Enterprise Notification Service Template - Ainflue
===================================================
Template enterprise pour services notifications.
Email + SMS + Push + Webhook + template engine + scheduling.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction sans autorisation est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import uuid
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
import logging
import re
from collections import deque
import hashlib
import hmac

from .service_template import EnterpriseServiceBase, ServiceConfig


class NotificationChannel(Enum):
    """Canaux de notification."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Priorités de notification."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Status des notifications."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    READ = "read"


class TemplateType(Enum):
    """Types de templates."""
    EMAIL_HTML = "email_html"
    EMAIL_TEXT = "email_text"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"


@dataclass
class NotificationTemplate:
    """Template de notification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_type: TemplateType = TemplateType.EMAIL_HTML
    subject_template: str = ""
    body_template: str = ""
    variables: List[str] = field(default_factory=list)
    localization: Dict[str, Dict[str, str]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"


@dataclass
class NotificationRequest:
    """Requête de notification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    channel: NotificationChannel
    recipient: str  # email, phone, user_id, etc.
    template_id: Optional[str] = None
    subject: Optional[str] = None
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class NotificationResponse:
    """Réponse de notification."""
    request_id: str
    status: NotificationStatus
    channel: NotificationChannel
    recipient: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    delivery_time_ms: float = 0.0


@dataclass
class ChannelConfig:
    """Configuration canal de notification."""
    channel: NotificationChannel
    provider: str
    config: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Optional[Dict[str, int]] = None  # {per_minute: 60, per_hour: 1000}
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        'max_retries': 3,
        'retry_delay_seconds': 60,
        'exponential_backoff': True
    })
    enabled: bool = True
    fallback_channels: List[NotificationChannel] = field(default_factory=list)


@dataclass
class DeliveryRule:
    """Règle de livraison."""
    name: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    channels: List[NotificationChannel] = field(default_factory=list)
    priority_threshold: NotificationPriority = NotificationPriority.NORMAL
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    user_preferences: bool = True
    enabled: bool = True


class NotificationServiceTemplate(EnterpriseServiceBase):
    """
    📬 Template enterprise pour services notifications.
    Email + SMS + Push + Webhook + template engine + scheduling.
    
    Features:
    - Configuration multi-canaux notifications
    - Moteur templates avec localisation
    - Scheduling notifications avec retry logic
    - Tracking délivrance avec analytics
    - Rate limiting par canal
    - Fallback channels automatiques
    - User preferences et opt-out
    - Compliance (GDPR, CAN-SPAM)
    - A/B testing des templates
    - Analytics et reporting
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize notification service template."""
        super().__init__(config)
        
        self.notification_channels: Dict[NotificationChannel, ChannelConfig] = {}
        self.template_store: Dict[str, NotificationTemplate] = {}
        self.pending_notifications: deque = deque()
        self.notification_history: List[NotificationResponse] = []
        self.delivery_rules: List[DeliveryRule] = []
        
        # Notification metrics
        self.notification_metrics = {
            'notifications_sent': 0,
            'notifications_delivered': 0,
            'notifications_failed': 0,
            'notifications_pending': 0,
            'notifications_cancelled': 0,
            'notifications_read': 0,
            'templates_created': 0,
            'channels_configured': 0,
            'average_delivery_time_ms': 0.0,
            'total_cost': 0.0,
            'rate_limit_hits': 0,
            'fallback_used': 0
        }
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, Dict] = {}
        
        # User preferences
        self.user_preferences: Dict[str, Dict] = {}
        
        # Background tasks
        self.notification_tasks: List[asyncio.Task] = []
        
        self.logger.info(f"📬 Notification Service Template initialized: {config.service_name}")
    
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        try:
            # Setup default templates
            await self._setup_default_templates()
            
            # Setup default delivery rules
            await self._setup_default_delivery_rules()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.info("✅ Notification service components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize notification service: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Stop background tasks
            for task in self.notification_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Clear stores
            self.notification_channels.clear()
            self.template_store.clear()
            self.pending_notifications.clear()
            
            self.logger.info("✅ Notification service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during notification service cleanup: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform notification service-specific health checks."""
        try:
            channel_health = {}
            for channel, config in self.notification_channels.items():
                channel_health[channel.value] = {
                    'enabled': config.enabled,
                    'provider': config.provider,
                    'rate_limit_status': self._get_rate_limit_status(channel)
                }
            
            return {
                'channels_configured': len(self.notification_channels),
                'templates_available': len(self.template_store),
                'pending_notifications': len(self.pending_notifications),
                'delivery_rules': len(self.delivery_rules),
                'channel_health': channel_health,
                'metrics': self.notification_metrics.copy(),
                'user_preferences_count': len(self.user_preferences)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Notification service health check failed: {e}")
            return {'error': str(e), 'status': 'unhealthy'}
    
    async def setup_notification_channels(self, channels_config: Dict[NotificationChannel, ChannelConfig]) -> None:
        """Configuration multi-canaux notifications."""
        try:
            for channel, config in channels_config.items():
                await self._setup_single_channel(channel, config)
            
            self.notification_metrics['channels_configured'] = len(self.notification_channels)
            self.logger.info(f"✅ Notification channels configured: {list(channels_config.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup notification channels: {e}")
            raise
    
    async def _setup_single_channel(self, channel: NotificationChannel, config: ChannelConfig) -> None:
        """Setup single notification channel."""
        try:
            # Validate channel configuration
            await self._validate_channel_config(channel, config)
            
            # Store channel configuration
            self.notification_channels[channel] = config
            
            # Initialize rate limiting for channel
            self.rate_limits[channel.value] = {
                'requests': deque(),
                'last_reset': datetime.now()
            }
            
            self.logger.info(f"✅ Channel configured: {channel.value} ({config.provider})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup channel {channel.value}: {e}")
            raise
    
    async def setup_template_engine(self, template_config: Dict[str, Any]) -> None:
        """Moteur templates avec localisation."""
        try:
            # Load templates from config
            templates = template_config.get('templates', [])
            for template_data in templates:
                template = NotificationTemplate(**template_data)
                self.template_store[template.id] = template
                self.notification_metrics['templates_created'] += 1
            
            self.logger.info(f"✅ Template engine configured: {len(templates)} templates loaded")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup template engine: {e}")
            raise
    
    async def setup_notification_scheduling(self, schedule_config: Dict[str, Any]) -> None:
        """Scheduling notifications avec retry logic."""
        try:
            # Configure scheduling parameters
            self.scheduling_config = {
                'batch_size': schedule_config.get('batch_size', 100),
                'processing_interval_seconds': schedule_config.get('processing_interval_seconds', 10),
                'max_retry_attempts': schedule_config.get('max_retry_attempts', 3),
                'retry_delay_seconds': schedule_config.get('retry_delay_seconds', 60)
            }
            
            self.logger.info("✅ Notification scheduling configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup notification scheduling: {e}")
            raise
    
    async def setup_delivery_tracking(self, tracking_config: Dict[str, Any]) -> None:
        """Tracking délivrance avec analytics."""
        try:
            # Configure delivery tracking
            self.tracking_config = {
                'track_opens': tracking_config.get('track_opens', True),
                'track_clicks': tracking_config.get('track_clicks', True),
                'webhook_url': tracking_config.get('webhook_url'),
                'retention_days': tracking_config.get('retention_days', 90)
            }
            
            self.logger.info("✅ Delivery tracking configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup delivery tracking: {e}")
            raise
    
    async def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        """Send notification."""
        start_time = datetime.now()
        
        try:
            # Validate request
            if not await self._validate_notification_request(request):
                return NotificationResponse(
                    request_id=request.id,
                    status=NotificationStatus.FAILED,
                    channel=request.channel,
                    recipient=request.recipient,
                    error_message="Invalid notification request"
                )
            
            # Check user preferences
            if not await self._check_user_preferences(request):
                return NotificationResponse(
                    request_id=request.id,
                    status=NotificationStatus.CANCELLED,
                    channel=request.channel,
                    recipient=request.recipient,
                    error_message="User preferences block this notification"
                )
            
            # Check rate limits
            if not await self._check_rate_limits(request.channel):
                self.notification_metrics['rate_limit_hits'] += 1
                # Try fallback channel
                fallback_channel = await self._get_fallback_channel(request.channel)
                if fallback_channel:
                    request.channel = fallback_channel
                    self.notification_metrics['fallback_used'] += 1
                else:
                    return NotificationResponse(
                        request_id=request.id,
                        status=NotificationStatus.FAILED,
                        channel=request.channel,
                        recipient=request.recipient,
                        error_message="Rate limit exceeded and no fallback available"
                    )
            
            # Render template if specified
            rendered_content = await self._render_template(request)
            
            # Send notification through channel
            response = await self._send_through_channel(request, rendered_content)
            
            # Calculate delivery time
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            response.delivery_time_ms = delivery_time
            
            # Update metrics
            if response.status == NotificationStatus.SENT:
                self.notification_metrics['notifications_sent'] += 1
                self._update_average_delivery_time(delivery_time)
            elif response.status == NotificationStatus.FAILED:
                self.notification_metrics['notifications_failed'] += 1
            
            # Store in history
            self.notification_history.append(response)
            
            # Schedule retries if failed
            if response.status == NotificationStatus.FAILED and request.retry_count < request.max_retries:
                await self._schedule_retry(request)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send notification: {e}")
            return NotificationResponse(
                request_id=request.id,
                status=NotificationStatus.FAILED,
                channel=request.channel,
                recipient=request.recipient,
                error_message=str(e)
            )
    
    async def schedule_notification(self, request: NotificationRequest, 
                                  scheduled_at: datetime) -> bool:
        """Schedule notification for later delivery."""
        try:
            request.scheduled_at = scheduled_at
            self.pending_notifications.append(request)
            self.notification_metrics['notifications_pending'] += 1
            
            self.logger.info(f"📅 Notification scheduled: {request.id} for {scheduled_at}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule notification: {e}")
            return False
    
    async def cancel_notification(self, notification_id: str) -> bool:
        """Cancel pending notification."""
        try:
            # Remove from pending queue
            for i, request in enumerate(self.pending_notifications):
                if request.id == notification_id:
                    del self.pending_notifications[i]
                    self.notification_metrics['notifications_pending'] -= 1
                    self.notification_metrics['notifications_cancelled'] += 1
                    
                    self.logger.info(f"❌ Notification cancelled: {notification_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cancel notification: {e}")
            return False
    
    async def create_template(self, template: NotificationTemplate) -> str:
        """Create notification template."""
        try:
            self.template_store[template.id] = template
            self.notification_metrics['templates_created'] += 1
            
            self.logger.info(f"📝 Template created: {template.name} ({template.template_type.value})")
            return template.id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create template: {e}")
            raise
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user notification preferences."""
        try:
            self.user_preferences[user_id] = {
                'channels': preferences.get('channels', {}),
                'categories': preferences.get('categories', {}),
                'quiet_hours': preferences.get('quiet_hours', {}),
                'frequency_limits': preferences.get('frequency_limits', {}),
                'opt_out': preferences.get('opt_out', False),
                'updated_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"⚙️ User preferences updated: {user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update user preferences: {e}")
            raise
    
    async def get_notification_analytics(self, time_range: Optional[Dict] = None) -> Dict[str, Any]:
        """Get notification analytics."""
        try:
            # Filter history by time range if specified
            history = self.notification_history
            if time_range:
                start_time = datetime.fromisoformat(time_range.get('start', '2000-01-01T00:00:00'))
                end_time = datetime.fromisoformat(time_range.get('end', datetime.now().isoformat()))
                history = [
                    response for response in history
                    if response.sent_at and start_time <= response.sent_at <= end_time
                ]
            
            # Calculate analytics
            total_sent = len([r for r in history if r.status == NotificationStatus.SENT])
            total_delivered = len([r for r in history if r.status == NotificationStatus.DELIVERED])
            total_failed = len([r for r in history if r.status == NotificationStatus.FAILED])
            
            # Channel breakdown
            channel_stats = {}
            for response in history:
                channel = response.channel.value
                if channel not in channel_stats:
                    channel_stats[channel] = {'sent': 0, 'delivered': 0, 'failed': 0}
                
                if response.status == NotificationStatus.SENT:
                    channel_stats[channel]['sent'] += 1
                elif response.status == NotificationStatus.DELIVERED:
                    channel_stats[channel]['delivered'] += 1
                elif response.status == NotificationStatus.FAILED:
                    channel_stats[channel]['failed'] += 1
            
            return {
                'total_notifications': len(history),
                'sent': total_sent,
                'delivered': total_delivered,
                'failed': total_failed,
                'delivery_rate': (total_delivered / total_sent) if total_sent > 0 else 0,
                'failure_rate': (total_failed / len(history)) if history else 0,
                'channel_breakdown': channel_stats,
                'total_cost': sum(r.cost for r in history),
                'average_delivery_time_ms': sum(r.delivery_time_ms for r in history) / len(history) if history else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get notification analytics: {e}")
            return {}
    
    async def _validate_channel_config(self, channel: NotificationChannel, config: ChannelConfig) -> None:
        """Validate channel configuration."""
        if not config.provider:
            raise ValueError(f"Provider required for channel {channel.value}")
        
        # Channel-specific validation
        if channel == NotificationChannel.EMAIL:
            required_fields = ['smtp_host', 'smtp_port', 'username', 'password']
            for field in required_fields:
                if field not in config.config:
                    raise ValueError(f"Missing required field for email: {field}")
        
        elif channel == NotificationChannel.SMS:
            required_fields = ['api_key', 'sender_id']
            for field in required_fields:
                if field not in config.config:
                    raise ValueError(f"Missing required field for SMS: {field}")
    
    async def _validate_notification_request(self, request: NotificationRequest) -> bool:
        """Validate notification request."""
        if not request.recipient:
            return False
        
        if request.channel not in self.notification_channels:
            return False
        
        if not self.notification_channels[request.channel].enabled:
            return False
        
        # Channel-specific validation
        if request.channel == NotificationChannel.EMAIL:
            return self._validate_email(request.recipient)
        elif request.channel == NotificationChannel.SMS:
            return self._validate_phone(request.recipient)
        
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number."""
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone.replace(' ', '')) is not None
    
    async def _check_user_preferences(self, request: NotificationRequest) -> bool:
        """Check user preferences."""
        # Extract user ID from recipient or metadata
        user_id = request.metadata.get('user_id')
        if not user_id:
            return True  # No preferences set, allow notification
        
        preferences = self.user_preferences.get(user_id, {})
        
        # Check opt-out
        if preferences.get('opt_out', False):
            return False
        
        # Check channel preferences
        channel_prefs = preferences.get('channels', {})
        if request.channel.value in channel_prefs and not channel_prefs[request.channel.value]:
            return False
        
        # Check quiet hours
        quiet_hours = preferences.get('quiet_hours', {})
        if quiet_hours and self._is_in_quiet_hours(quiet_hours):
            return False
        
        return True
    
    def _is_in_quiet_hours(self, quiet_hours: Dict[str, Any]) -> bool:
        """Check if current time is in quiet hours."""
        if not quiet_hours.get('enabled', False):
            return False
        
        current_time = datetime.now().time()
        start_time = datetime.strptime(quiet_hours.get('start', '22:00'), '%H:%M').time()
        end_time = datetime.strptime(quiet_hours.get('end', '08:00'), '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            return current_time >= start_time or current_time <= end_time
    
    async def _check_rate_limits(self, channel: NotificationChannel) -> bool:
        """Check rate limits for channel."""
        if channel not in self.notification_channels:
            return False
        
        config = self.notification_channels[channel]
        if not config.rate_limit:
            return True
        
        channel_key = channel.value
        rate_data = self.rate_limits[channel_key]
        current_time = datetime.now()
        
        # Clean old requests
        rate_data['requests'] = deque([
            req_time for req_time in rate_data['requests']
            if (current_time - req_time).total_seconds() < 3600  # Keep last hour
        ], maxlen=10000)
        
        # Check per-minute limit
        per_minute = config.rate_limit.get('per_minute', 0)
        if per_minute > 0:
            minute_ago = current_time - timedelta(minutes=1)
            recent_requests = [req for req in rate_data['requests'] if req > minute_ago]
            if len(recent_requests) >= per_minute:
                return False
        
        # Check per-hour limit
        per_hour = config.rate_limit.get('per_hour', 0)
        if per_hour > 0:
            hour_ago = current_time - timedelta(hours=1)
            recent_requests = [req for req in rate_data['requests'] if req > hour_ago]
            if len(recent_requests) >= per_hour:
                return False
        
        # Record this request
        rate_data['requests'].append(current_time)
        return True
    
    def _get_rate_limit_status(self, channel: NotificationChannel) -> Dict[str, Any]:
        """Get rate limit status for channel."""
        if channel.value not in self.rate_limits:
            return {'status': 'not_configured'}
        
        config = self.notification_channels[channel]
        if not config.rate_limit:
            return {'status': 'unlimited'}
        
        rate_data = self.rate_limits[channel.value]
        current_time = datetime.now()
        
        # Count recent requests
        minute_ago = current_time - timedelta(minutes=1)
        hour_ago = current_time - timedelta(hours=1)
        
        requests_last_minute = len([req for req in rate_data['requests'] if req > minute_ago])
        requests_last_hour = len([req for req in rate_data['requests'] if req > hour_ago])
        
        return {
            'status': 'active',
            'requests_last_minute': requests_last_minute,
            'requests_last_hour': requests_last_hour,
            'limit_per_minute': config.rate_limit.get('per_minute', 0),
            'limit_per_hour': config.rate_limit.get('per_hour', 0)
        }
    
    async def _get_fallback_channel(self, channel: NotificationChannel) -> Optional[NotificationChannel]:
        """Get fallback channel."""
        if channel not in self.notification_channels:
            return None
        
        config = self.notification_channels[channel]
        for fallback in config.fallback_channels:
            if fallback in self.notification_channels and self.notification_channels[fallback].enabled:
                if await self._check_rate_limits(fallback):
                    return fallback
        
        return None
    
    async def _render_template(self, request: NotificationRequest) -> Dict[str, str]:
        """Render notification template."""
        try:
            if not request.template_id:
                return {
                    'subject': request.subject or '',
                    'body': request.message
                }
            
            template = self.template_store.get(request.template_id)
            if not template:
                raise ValueError(f"Template not found: {request.template_id}")
            
            # Simple template rendering (can be enhanced with Jinja2)
            subject = template.subject_template
            body = template.body_template
            
            # Replace variables
            for key, value in request.data.items():
                placeholder = f"{{{key}}}"
                subject = subject.replace(placeholder, str(value))
                body = body.replace(placeholder, str(value))
            
            return {
                'subject': subject,
                'body': body
            }
            
        except Exception as e:
            self.logger.error(f"❌ Template rendering failed: {e}")
            return {
                'subject': request.subject or 'Notification',
                'body': request.message
            }
    
    async def _send_through_channel(self, request: NotificationRequest, 
                                   content: Dict[str, str]) -> NotificationResponse:
        """Send notification through specific channel."""
        try:
            config = self.notification_channels[request.channel]
            
            if request.channel == NotificationChannel.EMAIL:
                return await self._send_email(request, content, config)
            elif request.channel == NotificationChannel.SMS:
                return await self._send_sms(request, content, config)
            elif request.channel == NotificationChannel.PUSH:
                return await self._send_push(request, content, config)
            elif request.channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(request, content, config)
            else:
                raise ValueError(f"Channel not implemented: {request.channel}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send through channel {request.channel}: {e}")
            return NotificationResponse(
                request_id=request.id,
                status=NotificationStatus.FAILED,
                channel=request.channel,
                recipient=request.recipient,
                error_message=str(e)
            )
    
    async def _send_email(self, request: NotificationRequest, content: Dict[str, str], 
                         config: ChannelConfig) -> NotificationResponse:
        """Send email notification."""
        # Placeholder for email sending
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return NotificationResponse(
            request_id=request.id,
            status=NotificationStatus.SENT,
            channel=NotificationChannel.EMAIL,
            recipient=request.recipient,
            sent_at=datetime.now(),
            cost=0.01  # $0.01 per email
        )
    
    async def _send_sms(self, request: NotificationRequest, content: Dict[str, str], 
                       config: ChannelConfig) -> NotificationResponse:
        """Send SMS notification."""
        # Placeholder for SMS sending
        await asyncio.sleep(0.2)  # Simulate network delay
        
        return NotificationResponse(
            request_id=request.id,
            status=NotificationStatus.SENT,
            channel=NotificationChannel.SMS,
            recipient=request.recipient,
            sent_at=datetime.now(),
            cost=0.05  # $0.05 per SMS
        )
    
    async def _send_push(self, request: NotificationRequest, content: Dict[str, str], 
                        config: ChannelConfig) -> NotificationResponse:
        """Send push notification."""
        # Placeholder for push notification
        await asyncio.sleep(0.05)  # Simulate network delay
        
        return NotificationResponse(
            request_id=request.id,
            status=NotificationStatus.SENT,
            channel=NotificationChannel.PUSH,
            recipient=request.recipient,
            sent_at=datetime.now(),
            cost=0.001  # $0.001 per push
        )
    
    async def _send_webhook(self, request: NotificationRequest, content: Dict[str, str], 
                           config: ChannelConfig) -> NotificationResponse:
        """Send webhook notification."""
        # Placeholder for webhook sending
        await asyncio.sleep(0.3)  # Simulate network delay
        
        return NotificationResponse(
            request_id=request.id,
            status=NotificationStatus.SENT,
            channel=NotificationChannel.WEBHOOK,
            recipient=request.recipient,
            sent_at=datetime.now(),
            cost=0.0  # Free webhooks
        )
    
    async def _schedule_retry(self, request: NotificationRequest) -> None:
        """Schedule notification retry."""
        try:
            request.retry_count += 1
            
            config = self.notification_channels[request.channel]
            delay = config.retry_policy['retry_delay_seconds']
            
            if config.retry_policy.get('exponential_backoff', False):
                delay *= (2 ** (request.retry_count - 1))
            
            # Schedule retry
            retry_time = datetime.now() + timedelta(seconds=delay)
            request.scheduled_at = retry_time
            
            self.pending_notifications.append(request)
            
            self.logger.info(f"🔄 Notification retry scheduled: {request.id} (attempt {request.retry_count})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule retry: {e}")
    
    def _update_average_delivery_time(self, delivery_time_ms: float) -> None:
        """Update average delivery time metric."""
        current_avg = self.notification_metrics['average_delivery_time_ms']
        total_sent = self.notification_metrics['notifications_sent']
        
        if total_sent > 1:
            self.notification_metrics['average_delivery_time_ms'] = (
                (current_avg * (total_sent - 1)) + delivery_time_ms
            ) / total_sent
        else:
            self.notification_metrics['average_delivery_time_ms'] = delivery_time_ms
    
    async def _setup_default_templates(self) -> None:
        """Setup default notification templates."""
        default_templates = [
            NotificationTemplate(
                name="Welcome Email",
                template_type=TemplateType.EMAIL_HTML,
                subject_template="Welcome to {app_name}!",
                body_template="""
                <h1>Welcome {user_name}!</h1>
                <p>Thank you for joining {app_name}. We're excited to have you aboard!</p>
                <p>Get started by exploring our features.</p>
                <p>Best regards,<br>The {app_name} Team</p>
                """,
                variables=["app_name", "user_name"]
            ),
            NotificationTemplate(
                name="Password Reset",
                template_type=TemplateType.EMAIL_HTML,
                subject_template="Reset your password",
                body_template="""
                <h2>Password Reset Request</h2>
                <p>Hi {user_name},</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you didn't request this, please ignore this email.</p>
                """,
                variables=["user_name", "reset_link"]
            )
        ]
        
        for template in default_templates:
            self.template_store[template.id] = template
            self.notification_metrics['templates_created'] += 1
    
    async def _setup_default_delivery_rules(self) -> None:
        """Setup default delivery rules."""
        default_rules = [
            DeliveryRule(
                name="High Priority Email",
                conditions={'priority': 'high'},
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
                priority_threshold=NotificationPriority.HIGH
            ),
            DeliveryRule(
                name="Normal Priority",
                conditions={'priority': 'normal'},
                channels=[NotificationChannel.EMAIL],
                priority_threshold=NotificationPriority.NORMAL
            )
        ]
        
        self.delivery_rules.extend(default_rules)
    
    async def _start_background_tasks(self) -> None:
        """Start background notification tasks."""
        # Notification processing task
        process_task = asyncio.create_task(self._process_pending_notifications())
        self.notification_tasks.append(process_task)
        
        # History cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_old_history())
        self.notification_tasks.append(cleanup_task)
    
    async def _process_pending_notifications(self) -> None:
        """Process pending notifications."""
        while self.status == "running":
            try:
                current_time = datetime.now()
                processed_count = 0
                
                # Process due notifications
                while self.pending_notifications and processed_count < 100:  # Batch size
                    request = self.pending_notifications.popleft()
                    
                    if request.scheduled_at and request.scheduled_at > current_time:
                        # Not due yet, put back
                        self.pending_notifications.appendleft(request)
                        break
                    
                    # Send notification
                    await self.send_notification(request)
                    processed_count += 1
                    self.notification_metrics['notifications_pending'] -= 1
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Notification processing error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_old_history(self) -> None:
        """Cleanup old notification history."""
        while self.status == "running":
            try:
                cutoff_time = datetime.now() - timedelta(days=90)  # Keep 90 days
                
                self.notification_history = [
                    response for response in self.notification_history
                    if response.sent_at and response.sent_at > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ History cleanup error: {e}")
                await asyncio.sleep(7200)
    
    # Abstract methods pour extension
    @abstractmethod
    async def configure_custom_channels(self) -> Dict[NotificationChannel, ChannelConfig]:
        """Configure canaux spécifiques au service."""
        pass
    
    @abstractmethod
    async def configure_custom_templates(self) -> List[NotificationTemplate]:
        """Configure templates spécifiques au service."""
        pass


if __name__ == "__main__":
    print("📬 Enterprise Notification Service Template")
    print("Use this template to create comprehensive notification microservices")