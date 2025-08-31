"""Advanced Channel Manager - Multi-Channel Notification Delivery System

This module provides sophisticated multi-channel notification delivery capabilities for the IA Influencer Agent platform,
handling intelligent channel selection, delivery optimization, and cross-platform communication management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ...models.notification_models import (
    NotificationModel, NotificationChannel, NotificationPriority,
    ChannelDeliveryResult, ChannelConfiguration
)
from ...integrations.messaging_integrations import MessagingIntegrationManager
from ...security.channel_security import ChannelSecurityManager
from ...monitoring.channel_monitoring import ChannelMonitoringService


class ChannelType(Enum):
    """Extended channel types for comprehensive delivery"""    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    VOICE_CALL = "voice_call"
    SOCIAL_MEDIA = "social_media"


class DeliveryStatus(Enum):
    """Comprehensive delivery status tracking"""    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    CLICKED = "clicked"
    FAILED = "failed"
    BOUNCE = "bounce"
    SPAM = "spam"
    BLOCKED = "blocked"


@dataclass
class ChannelMetrics:
    """Channel performance metrics"""    channel: ChannelType
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    total_read: int = 0
    total_clicked: int = 0
    average_delivery_time: float = 0.0
    success_rate: float = 0.0
    engagement_rate: float = 0.0
    cost_per_delivery: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChannelCapability:
    """Channel capability configuration"""    channel: ChannelType
    supports_rich_content: bool
    supports_attachments: bool
    supports_interactive_elements: bool
    max_content_length: int
    delivery_speed: str  # "instant", "fast", "normal", "slow"
    cost_tier: int  # 1=low, 2=medium, 3=high cost
    reliability_score: float  # 0.0-1.0
    global_availability: bool


class BaseChannelHandler(ABC):
    """Abstract base class for channel-specific handlers"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = ChannelMetrics(channel=self.get_channel_type())
        
    @abstractmethod
    def get_channel_type(self) -> ChannelType:
        """Get the channel type this handler manages"""        pass
        
    @abstractmethod
    async def send_notification(
        self, 
        user_id: str, 
        content: Dict[str, Any], 
        priority: NotificationPriority
    ) -> ChannelDeliveryResult:
        """Send notification through this channel"""        pass
        
    @abstractmethod
    async def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate content for this channel"""        pass
        
    async def get_delivery_status(self, delivery_id: str) -> DeliveryStatus:
        """Get delivery status for a specific message"""        # Default implementation - override in specific handlers
        return DeliveryStatus.DELIVERED
        
    async def update_metrics(self, delivery_result: ChannelDeliveryResult):
        """Update channel performance metrics"""        self.metrics.total_sent += 1
        
        if delivery_result.status == DeliveryStatus.DELIVERED:
            self.metrics.total_delivered += 1
        elif delivery_result.status == DeliveryStatus.FAILED:
            self.metrics.total_failed += 1
            
        # Update success rate
        if self.metrics.total_sent > 0:
            self.metrics.success_rate = self.metrics.total_delivered / self.metrics.total_sent
            
        self.metrics.last_updated = datetime.utcnow()


class EmailChannelHandler(BaseChannelHandler):
    """Advanced email channel handler with multiple provider support"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_config = config.get('smtp', {})
        self.api_providers = config.get('api_providers', {})
        self.templates = {}
        
    def get_channel_type(self) -> ChannelType:
        return ChannelType.EMAIL
        
    async def send_notification(
        self, 
        user_id: str, 
        content: Dict[str, Any], 
        priority: NotificationPriority
    ) -> ChannelDeliveryResult:
        """Send email notification with provider failover"""        try:
            delivery_id = str(uuid.uuid4())
            
            # Validate email content
            if not await self.validate_content(content):
                return ChannelDeliveryResult(
                    delivery_id=delivery_id,
                    channel=self.get_channel_type(),
                    status=DeliveryStatus.FAILED,
                    error_message="Content validation failed"
                )
                
            # Try primary provider first
            result = await self._send_via_primary_provider(user_id, content, delivery_id)
            
            # Fallback to secondary provider if primary fails
            if result.status == DeliveryStatus.FAILED:
                result = await self._send_via_fallback_provider(user_id, content, delivery_id)
                
            # Update metrics
            await self.update_metrics(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Email delivery failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=str(uuid.uuid4()),
                channel=self.get_channel_type(),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate email content"""        required_fields = ['recipient_email', 'subject', 'body']
        return all(field in content for field in required_fields)
        
    async def _send_via_primary_provider(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send email via primary provider (SendGrid, Mailgun, etc.)"""        try:
            if 'sendgrid' in self.api_providers:
                return await self._send_via_sendgrid(user_id, content, delivery_id)
            elif 'mailgun' in self.api_providers:
                return await self._send_via_mailgun(user_id, content, delivery_id)
            else:
                return await self._send_via_smtp(user_id, content, delivery_id)
                
        except Exception as e:
            self.logger.error(f"Primary email provider failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def _send_via_fallback_provider(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send email via fallback provider"""        try:
            # Use SMTP as fallback
            return await self._send_via_smtp(user_id, content, delivery_id)
            
        except Exception as e:
            self.logger.error(f"Fallback email provider failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def _send_via_smtp(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send email via SMTP"""        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = content['recipient_email']
            msg['Subject'] = content['subject']
            
            # Add body
            if 'html_body' in content:
                msg.attach(MIMEText(content['html_body'], 'html'))
            else:
                msg.attach(MIMEText(content['body'], 'plain'))
                
            # Send email
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            if self.smtp_config.get('use_tls'):
                server.starttls()
            if self.smtp_config.get('username'):
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                
            server.send_message(msg)
            server.quit()
            
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.SENT,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"SMTP email delivery failed: {str(e)}")
            raise
            
    async def _send_via_sendgrid(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send email via SendGrid API"""        try:
            sendgrid_config = self.api_providers['sendgrid']
            
            # Prepare SendGrid payload
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": content['recipient_email']}],
                        "subject": content['subject']
                    }
                ],
                "from": {"email": sendgrid_config['from_email']},
                "content": [
                    {
                        "type": "text/html" if 'html_body' in content else "text/plain",
                        "value": content.get('html_body', content['body'])
                    }
                ]
            }
            
            # Send via SendGrid API
            headers = {
                'Authorization': f"Bearer {sendgrid_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.sendgrid.com/v3/mail/send',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 202:
                        return ChannelDeliveryResult(
                            delivery_id=delivery_id,
                            channel=self.get_channel_type(),
                            status=DeliveryStatus.SENT,
                            timestamp=datetime.utcnow()
                        )
                    else:
                        raise Exception(f"SendGrid API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"SendGrid email delivery failed: {str(e)}")
            raise


class SMSChannelHandler(BaseChannelHandler):
    """Advanced SMS channel handler with multiple provider support"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sms_providers = config.get('sms_providers', {})
        
    def get_channel_type(self) -> ChannelType:
        return ChannelType.SMS
        
    async def send_notification(
        self, 
        user_id: str, 
        content: Dict[str, Any], 
        priority: NotificationPriority
    ) -> ChannelDeliveryResult:
        """Send SMS notification"""        try:
            delivery_id = str(uuid.uuid4())
            
            # Validate SMS content
            if not await self.validate_content(content):
                return ChannelDeliveryResult(
                    delivery_id=delivery_id,
                    channel=self.get_channel_type(),
                    status=DeliveryStatus.FAILED,
                    error_message="Content validation failed"
                )
                
            # Send via preferred provider
            if 'twilio' in self.sms_providers:
                result = await self._send_via_twilio(user_id, content, delivery_id)
            elif 'aws_sns' in self.sms_providers:
                result = await self._send_via_aws_sns(user_id, content, delivery_id)
            else:
                raise Exception("No SMS provider configured")
                
            # Update metrics
            await self.update_metrics(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"SMS delivery failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=str(uuid.uuid4()),
                channel=self.get_channel_type(),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate SMS content"""        required_fields = ['phone_number', 'message']
        if not all(field in content for field in required_fields):
            return False
            
        # Check message length (160 characters for SMS)
        if len(content['message']) > 160:
            return False
            
        return True
        
    async def _send_via_twilio(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send SMS via Twilio"""        try:
            twilio_config = self.sms_providers['twilio']
            
            # Twilio API call (simplified - would use actual Twilio SDK)
            payload = {
                'From': twilio_config['from_number'],
                'To': content['phone_number'],
                'Body': content['message']
            }
            
            # Simulated API call (replace with actual Twilio SDK usage)
            self.logger.info(f"Sending SMS via Twilio: {delivery_id}")
            
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.SENT,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Twilio SMS delivery failed: {str(e)}")
            raise


class PushNotificationChannelHandler(BaseChannelHandler):
    """Advanced push notification handler for mobile and web"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.push_config = config.get('push_notification', {})
        
    def get_channel_type(self) -> ChannelType:
        return ChannelType.PUSH_NOTIFICATION
        
    async def send_notification(
        self, 
        user_id: str, 
        content: Dict[str, Any], 
        priority: NotificationPriority
    ) -> ChannelDeliveryResult:
        """Send push notification"""        try:
            delivery_id = str(uuid.uuid4())
            
            # Validate push content
            if not await self.validate_content(content):
                return ChannelDeliveryResult(
                    delivery_id=delivery_id,
                    channel=self.get_channel_type(),
                    status=DeliveryStatus.FAILED,
                    error_message="Content validation failed"
                )
                
            # Send to appropriate push service
            if content.get('platform') == 'ios':
                result = await self._send_ios_push(user_id, content, delivery_id)
            elif content.get('platform') == 'android':
                result = await self._send_android_push(user_id, content, delivery_id)
            else:
                result = await self._send_web_push(user_id, content, delivery_id)
                
            # Update metrics
            await self.update_metrics(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Push notification delivery failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=str(uuid.uuid4()),
                channel=self.get_channel_type(),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate push notification content"""        required_fields = ['title', 'body', 'device_token']
        return all(field in content for field in required_fields)
        
    async def _send_ios_push(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send iOS push notification via APNS"""        try:
            # iOS push implementation (would use actual APNS)
            self.logger.info(f"Sending iOS push notification: {delivery_id}")
            
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.SENT,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"iOS push delivery failed: {str(e)}")
            raise
            
    async def _send_android_push(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send Android push notification via FCM"""        try:
            # Android push implementation (would use actual FCM)
            self.logger.info(f"Sending Android push notification: {delivery_id}")
            
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.SENT,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Android push delivery failed: {str(e)}")
            raise
            
    async def _send_web_push(self, user_id: str, content: Dict[str, Any], delivery_id: str) -> ChannelDeliveryResult:
        """Send web push notification"""        try:
            # Web push implementation
            self.logger.info(f"Sending web push notification: {delivery_id}")
            
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                channel=self.get_channel_type(),
                status=DeliveryStatus.SENT,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Web push delivery failed: {str(e)}")
            raise


class ChannelManager:
    """    Advanced multi-channel notification delivery manager
    
    Features:
    - Intelligent channel selection and optimization
    - Failover and redundancy management
    - Performance monitoring and analytics
    - Cost optimization and budget management
    - Content adaptation per channel
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Channel handlers
        self.channel_handlers: Dict[ChannelType, BaseChannelHandler] = {}
        self._initialize_channel_handlers()
        
        # Channel capabilities
        self.channel_capabilities = self._define_channel_capabilities()
        
        # Security and monitoring
        self.security_manager = ChannelSecurityManager(config.get('security', {}))
        self.monitoring = ChannelMonitoringService(config.get('monitoring', {}))
        
        # Performance optimization
        self.channel_router = self._initialize_channel_router()
        self.cost_optimizer = self._initialize_cost_optimizer()
        
        # Delivery tracking
        self.active_deliveries: Dict[str, Dict[str, Any]] = {}
        self.delivery_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance metrics
        self.system_metrics = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'channel_performance': {},
            'cost_metrics': {}
        }
        
    def _initialize_channel_handlers(self):
        """Initialize all channel handlers"""        try:
            # Email handler
            if 'email' in self.config:
                self.channel_handlers[ChannelType.EMAIL] = EmailChannelHandler(
                    self.config['email']
                )
                
            # SMS handler
            if 'sms' in self.config:
                self.channel_handlers[ChannelType.SMS] = SMSChannelHandler(
                    self.config['sms']
                )
                
            # Push notification handler
            if 'push_notification' in self.config:
                self.channel_handlers[ChannelType.PUSH_NOTIFICATION] = PushNotificationChannelHandler(
                    self.config['push_notification']
                )
                
            # Additional handlers can be added here
            
            self.logger.info(f"Initialized {len(self.channel_handlers)} channel handlers")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize channel handlers: {str(e)}")
            
    def _define_channel_capabilities(self) -> Dict[ChannelType, ChannelCapability]:
        """Define capabilities for each channel type"""        return {
            ChannelType.EMAIL: ChannelCapability(
                channel=ChannelType.EMAIL,
                supports_rich_content=True,
                supports_attachments=True,
                supports_interactive_elements=True,
                max_content_length=100000,  # 100KB
                delivery_speed="normal",
                cost_tier=1,
                reliability_score=0.95,
                global_availability=True
            ),
            ChannelType.SMS: ChannelCapability(
                channel=ChannelType.SMS,
                supports_rich_content=False,
                supports_attachments=False,
                supports_interactive_elements=False,
                max_content_length=160,
                delivery_speed="fast",
                cost_tier=2,
                reliability_score=0.98,
                global_availability=True
            ),
            ChannelType.PUSH_NOTIFICATION: ChannelCapability(
                channel=ChannelType.PUSH_NOTIFICATION,
                supports_rich_content=True,
                supports_attachments=False,
                supports_interactive_elements=True,
                max_content_length=4000,
                delivery_speed="instant",
                cost_tier=1,
                reliability_score=0.92,
                global_availability=True
            )
        }
        
    def _initialize_channel_router(self):
        """Initialize intelligent channel routing system"""        from ...ai.channel_routing import ChannelRoutingEngine
        return ChannelRoutingEngine(self.config.get('routing', {}))
        
    def _initialize_cost_optimizer(self):
        """Initialize cost optimization system"""        from ...business.cost_optimization import CostOptimizer
        return CostOptimizer(self.config.get('cost_optimization', {}))
        
    async def send_multi_channel_notification(
        self,
        notification: NotificationModel,
        preferred_channels: Optional[List[ChannelType]] = None
    ) -> Dict[ChannelType, ChannelDeliveryResult]:
        """Send notification across multiple channels with intelligent optimization"""        try:
            # Determine optimal channels
            optimal_channels = preferred_channels or await self._determine_optimal_channels(
                notification
            )
            
            # Prepare content for each channel
            channel_content = await self._prepare_multi_channel_content(
                notification, optimal_channels
            )
            
            # Send notifications concurrently
            delivery_tasks = {}
            for channel in optimal_channels:
                if channel in self.channel_handlers:
                    content = channel_content.get(channel, {})
                    task = asyncio.create_task(
                        self._send_to_channel(channel, notification.user_id, content, notification.priority)
                    )
                    delivery_tasks[channel] = task
                    
            # Wait for all deliveries
            delivery_results = {}
            for channel, task in delivery_tasks.items():
                try:
                    result = await task
                    delivery_results[channel] = result
                    
                    # Track delivery
                    self.active_deliveries[result.delivery_id] = {
                        'notification_id': notification.id,
                        'channel': channel,
                        'user_id': notification.user_id,
                        'timestamp': datetime.utcnow()
                    }
                    
                except Exception as e:
                    self.logger.error(f"Channel {channel.value} delivery failed: {str(e)}")
                    delivery_results[channel] = ChannelDeliveryResult(
                        delivery_id=str(uuid.uuid4()),
                        channel=channel,
                        status=DeliveryStatus.FAILED,
                        error_message=str(e)
                    )
                    
            # Update system metrics
            await self._update_system_metrics(delivery_results)
            
            # Record delivery history
            self._record_delivery_history(notification.id, delivery_results)
            
            return delivery_results
            
        except Exception as e:
            self.logger.error(f"Multi-channel delivery failed: {str(e)}")
            return {}
            
    async def _determine_optimal_channels(
        self,
        notification: NotificationModel
    ) -> List[ChannelType]:
        """Determine optimal channels based on AI routing and user preferences"""        try:
            # Use AI-driven channel routing
            optimal_channels = await self.channel_router.determine_optimal_channels(
                notification.user_id,
                notification.type,
                notification.priority,
                notification.context
            )
            
            # Filter based on available handlers
            available_channels = [
                channel for channel in optimal_channels
                if channel in self.channel_handlers
            ]
            
            # Ensure at least one channel is selected
            if not available_channels:
                available_channels = [ChannelType.EMAIL]  # Fallback
                
            return available_channels
            
        except Exception as e:
            self.logger.error(f"Failed to determine optimal channels: {str(e)}")
            return [ChannelType.EMAIL]
            
    async def _prepare_multi_channel_content(
        self,
        notification: NotificationModel,
        channels: List[ChannelType]
    ) -> Dict[ChannelType, Dict[str, Any]]:
        """Prepare content optimized for each channel"""        try:
            channel_content = {}
            base_content = notification.content
            
            for channel in channels:
                capability = self.channel_capabilities.get(channel)
                if not capability:
                    continue
                    
                # Adapt content based on channel capabilities
                adapted_content = await self._adapt_content_for_channel(
                    base_content, channel, capability
                )
                
                channel_content[channel] = adapted_content
                
            return channel_content
            
        except Exception as e:
            self.logger.error(f"Failed to prepare multi-channel content: {str(e)}")
            return {}
            
    async def _adapt_content_for_channel(
        self,
        content: Dict[str, Any],
        channel: ChannelType,
        capability: ChannelCapability
    ) -> Dict[str, Any]:
        """Adapt content based on channel-specific capabilities"""        try:
            adapted_content = content.copy()
            
            # Truncate content if necessary
            if 'message' in adapted_content:
                message = adapted_content['message']
                if len(message) > capability.max_content_length:
                    adapted_content['message'] = message[:capability.max_content_length-3] + "..."
                    
            # Remove rich content if not supported
            if not capability.supports_rich_content:
                adapted_content.pop('html_content', None)
                adapted_content.pop('rich_formatting', None)
                
            # Remove attachments if not supported
            if not capability.supports_attachments:
                adapted_content.pop('attachments', None)
                
            # Remove interactive elements if not supported
            if not capability.supports_interactive_elements:
                adapted_content.pop('buttons', None)
                adapted_content.pop('interactive_elements', None)
                
            # Channel-specific adaptations
            if channel == ChannelType.SMS:
                adapted_content = await self._adapt_for_sms(adapted_content)
            elif channel == ChannelType.EMAIL:
                adapted_content = await self._adapt_for_email(adapted_content)
            elif channel == ChannelType.PUSH_NOTIFICATION:
                adapted_content = await self._adapt_for_push(adapted_content)
                
            return adapted_content
            
        except Exception as e:
            self.logger.error(f"Failed to adapt content for {channel.value}: {str(e)}")
            return content
            
    async def _adapt_for_sms(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content specifically for SMS"""        adapted = {
            'phone_number': content.get('recipient_phone', ''),
            'message': content.get('title', '') + ': ' + content.get('message', '')
        }
        
        # Truncate to SMS limits
        if len(adapted['message']) > 160:
            adapted['message'] = adapted['message'][:157] + "..."
            
        return adapted
        
    async def _adapt_for_email(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content specifically for email"""        return {
            'recipient_email': content.get('recipient_email', ''),
            'subject': content.get('title', 'Notification'),
            'body': content.get('message', ''),
            'html_body': content.get('html_content', ''),
            'attachments': content.get('attachments', [])
        }
        
    async def _adapt_for_push(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content specifically for push notifications"""        return {
            'device_token': content.get('device_token', ''),
            'title': content.get('title', 'Notification')[:50],
            'body': content.get('message', '')[:200],
            'icon': content.get('icon', ''),
            'action_url': content.get('action_url', ''),
            'platform': content.get('platform', 'web')
        }
        
    async def _send_to_channel(
        self,
        channel: ChannelType,
        user_id: str,
        content: Dict[str, Any],
        priority: NotificationPriority
    ) -> ChannelDeliveryResult:
        """Send notification to specific channel"""        try:
            handler = self.channel_handlers.get(channel)
            if not handler:
                raise Exception(f"No handler available for channel: {channel.value}")
                
            # Security validation
            if not await self.security_manager.validate_channel_delivery(channel, content):
                raise Exception("Security validation failed")
                
            # Send notification
            result = await handler.send_notification(user_id, content, priority)
            
            # Monitor delivery
            await self.monitoring.record_delivery_attempt(channel, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send to channel {channel.value}: {str(e)}")
            raise
            
    async def _update_system_metrics(self, delivery_results: Dict[ChannelType, ChannelDeliveryResult]):
        """Update system-wide performance metrics"""        try:
            for channel, result in delivery_results.items():
                # Update total counts
                self.system_metrics['total_sent'] += 1
                
                if result.status == DeliveryStatus.DELIVERED:
                    self.system_metrics['total_delivered'] += 1
                elif result.status == DeliveryStatus.FAILED:
                    self.system_metrics['total_failed'] += 1
                    
                # Update channel-specific metrics
                if channel.value not in self.system_metrics['channel_performance']:
                    self.system_metrics['channel_performance'][channel.value] = {
                        'sent': 0, 'delivered': 0, 'failed': 0
                    }
                    
                channel_metrics = self.system_metrics['channel_performance'][channel.value]
                channel_metrics['sent'] += 1
                
                if result.status == DeliveryStatus.DELIVERED:
                    channel_metrics['delivered'] += 1
                elif result.status == DeliveryStatus.FAILED:
                    channel_metrics['failed'] += 1
                    
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {str(e)}")
            
    def _record_delivery_history(
        self,
        notification_id: str,
        delivery_results: Dict[ChannelType, ChannelDeliveryResult]
    ):
        """Record delivery history for analytics"""        try:
            if notification_id not in self.delivery_history:
                self.delivery_history[notification_id] = []
                
            history_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'channels': {},
                'total_channels': len(delivery_results),
                'successful_channels': 0
            }
            
            for channel, result in delivery_results.items():
                history_entry['channels'][channel.value] = {
                    'delivery_id': result.delivery_id,
                    'status': result.status.value,
                    'timestamp': result.timestamp.isoformat() if result.timestamp else None,
                    'error': result.error_message
                }
                
                if result.status == DeliveryStatus.DELIVERED:
                    history_entry['successful_channels'] += 1
                    
            self.delivery_history[notification_id].append(history_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to record delivery history: {str(e)}")


class MultiChannelSender:
    """    High-level multi-channel notification sender with advanced orchestration
    """    
    def __init__(self, channel_manager: ChannelManager):
        self.channel_manager = channel_manager
        self.logger = logging.getLogger(__name__)
        
    async def send_notification_with_fallback(
        self,
        notification: NotificationModel,
        primary_channels: List[ChannelType],
        fallback_channels: List[ChannelType]
    ) -> Dict[str, Any]:
        """Send notification with intelligent fallback strategy"""        try:
            # Try primary channels first
            primary_results = await self.channel_manager.send_multi_channel_notification(
                notification, primary_channels
            )
            
            # Check if any primary delivery was successful
            primary_success = any(
                result.status == DeliveryStatus.DELIVERED 
                for result in primary_results.values()
            )
            
            fallback_results = {}
            
            # Use fallback channels if primary failed
            if not primary_success and fallback_channels:
                fallback_results = await self.channel_manager.send_multi_channel_notification(
                    notification, fallback_channels
                )
                
            # Combine results
            all_results = {**primary_results, **fallback_results}
            
            return {
                'notification_id': notification.id,
                'primary_results': primary_results,
                'fallback_results': fallback_results,
                'overall_success': any(
                    result.status == DeliveryStatus.DELIVERED 
                    for result in all_results.values()
                ),
                'delivery_summary': self._create_delivery_summary(all_results)
            }
            
        except Exception as e:
            self.logger.error(f"Multi-channel send with fallback failed: {str(e)}")
            return {
                'notification_id': notification.id,
                'error': str(e),
                'overall_success': False
            }
            
    def _create_delivery_summary(self, results: Dict[ChannelType, ChannelDeliveryResult]) -> Dict[str, Any]:
        """Create summary of delivery results"""        try:
            summary = {
                'total_channels': len(results),
                'successful_deliveries': 0,
                'failed_deliveries': 0,
                'channels_used': [],
                'delivery_details': {}
            }
            
            for channel, result in results.items():
                summary['channels_used'].append(channel.value)
                summary['delivery_details'][channel.value] = {
                    'status': result.status.value,
                    'delivery_id': result.delivery_id,
                    'timestamp': result.timestamp.isoformat() if result.timestamp else None
                }
                
                if result.status == DeliveryStatus.DELIVERED:
                    summary['successful_deliveries'] += 1
                else:
                    summary['failed_deliveries'] += 1
                    
            summary['success_rate'] = (
                summary['successful_deliveries'] / summary['total_channels'] 
                if summary['total_channels'] > 0 else 0
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to create delivery summary: {str(e)}")
            return {}
            
    async def send_batch_notifications(
        self,
        notifications: List[NotificationModel],
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Send batch of notifications efficiently"""        try:
            results = []
            
            # Process in batches
            for i in range(0, len(notifications), batch_size):
                batch = notifications[i:i + batch_size]
                
                # Process batch concurrently
                batch_tasks = []
                for notification in batch:
                    task = asyncio.create_task(
                        self.channel_manager.send_multi_channel_notification(notification)
                    )
                    batch_tasks.append((notification.id, task))
                    
                # Wait for batch completion
                for notification_id, task in batch_tasks:
                    try:
                        delivery_results = await task
                        results.append({
                            'notification_id': notification_id,
                            'results': delivery_results,
                            'success': any(
                                result.status == DeliveryStatus.DELIVERED 
                                for result in delivery_results.values()
                            )
                        })
                    except Exception as e:
                        results.append({
                            'notification_id': notification_id,
                            'error': str(e),
                            'success': False
                        })
                        
                # Brief pause between batches to avoid overwhelming services
                if i + batch_size < len(notifications):
                    await asyncio.sleep(0.1)
                    
            return results
            
        except Exception as e:
            self.logger.error(f"Batch notification sending failed: {str(e)}")
            return []
            
    async def get_delivery_analytics(
        self, 
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive delivery analytics"""        try:
            analytics = {
                'system_metrics': self.channel_manager.system_metrics.copy(),
                'channel_capabilities': {},
                'performance_trends': {},
                'cost_analysis': {},
                'recommendations': []
            }
            
            # Channel capabilities summary
            for channel, capability in self.channel_manager.channel_capabilities.items():
                analytics['channel_capabilities'][channel.value] = {
                    'reliability_score': capability.reliability_score,
                    'cost_tier': capability.cost_tier,
                    'delivery_speed': capability.delivery_speed,
                    'supports_rich_content': capability.supports_rich_content
                }
                
            # Performance trends (would be calculated from historical data)
            analytics['performance_trends'] = await self._calculate_performance_trends(time_range)
            
            # Cost analysis
            analytics['cost_analysis'] = await self._calculate_cost_analysis(time_range)
            
            # Generate recommendations
            analytics['recommendations'] = await self._generate_optimization_recommendations()
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get delivery analytics: {str(e)}")
            return {}
            
    async def _calculate_performance_trends(
        self, 
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Calculate performance trends over time"""        # Placeholder implementation - would analyze historical data
        return {
            'delivery_rate_trend': 'improving',
            'average_delivery_time_trend': 'stable',
            'failure_rate_trend': 'decreasing',
            'peak_usage_hours': [9, 10, 11, 14, 15, 16],
            'best_performing_channels': ['email', 'push_notification'],
            'worst_performing_channels': []
        }
        
    async def _calculate_cost_analysis(
        self, 
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Calculate cost analysis and optimization opportunities"""        # Placeholder implementation - would calculate actual costs
        return {
            'total_cost': 0.0,
            'cost_per_channel': {},
            'cost_per_delivery': 0.0,
            'cost_optimization_potential': 15.0,  # Percentage savings possible
            'recommended_cost_optimizations': [
                'Reduce SMS usage for non-urgent notifications',
                'Optimize email delivery timing to reduce failures'
            ]
        }
        
    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate channel optimization recommendations"""        recommendations = []
        
        # Analyze system metrics for recommendations
        system_metrics = self.channel_manager.system_metrics
        
        if system_metrics['total_failed'] > 0:
            failure_rate = system_metrics['total_failed'] / system_metrics['total_sent']
            if failure_rate > 0.05:  # More than 5% failure rate
                recommendations.append(
                    "High failure rate detected. Consider implementing better fallback strategies."
                )
                
        # Channel-specific recommendations
        for channel, metrics in system_metrics.get('channel_performance', {}).items():
            if metrics['sent'] > 0:
                channel_failure_rate = metrics['failed'] / metrics['sent']
                if channel_failure_rate > 0.1:  # More than 10% failure rate
                    recommendations.append(
                        f"Channel '{channel}' has high failure rate. Review configuration and provider settings."
                    )
                    
        # Add general recommendations
        if not recommendations:
            recommendations.extend([
                "System performing well. Consider A/B testing different channel combinations.",
                "Monitor delivery timing optimization opportunities.",
                "Review cost optimization strategies for high-volume periods."
            ])
            
        return recommendations
    cost_tier: str  # "free", "low", "medium", "high"
    reliability_score: float
    supported_content_types: List[str]


class BaseChannelHandler(ABC):
    """Abstract base class for channel handlers"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_initialized = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the channel handler"""        pass
        
    @abstractmethod
    async def send_notification(
        self,
        notification: NotificationModel,
        content: Dict[str, Any]
    ) -> ChannelDeliveryResult:
        """Send notification through this channel"""        pass
        
    @abstractmethod
    async def get_delivery_status(self, delivery_id: str) -> DeliveryStatus:
        """Get delivery status for a notification"""        pass
        
    @abstractmethod
    async def validate_configuration(self) -> bool:
        """Validate channel configuration"""        pass


class EmailChannelHandler(BaseChannelHandler):
    """Advanced email channel handler with SMTP and API support"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_config = config.get('smtp', {})
        self.api_config = config.get('api', {})
        self.delivery_tracking = {}
        
    async def initialize(self) -> bool:
        """Initialize email channel"""        try:
            # Validate SMTP configuration if provided
            if self.smtp_config:
                await self._validate_smtp_connection()
                
            # Validate API configuration if provided
            if self.api_config:
                await self._validate_api_connection()
                
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize email channel: {str(e)}")
            return False
            
    async def send_notification(
        self,
        notification: NotificationModel,
        content: Dict[str, Any]
    ) -> ChannelDeliveryResult:
        """Send email notification"""        try:
            delivery_id = str(uuid.uuid4())
            
            # Prepare email content
            email_content = await self._prepare_email_content(content)
            
            # Choose delivery method
            if self.api_config.get('enabled', False):
                result = await self._send_via_api(email_content, delivery_id)
            else:
                result = await self._send_via_smtp(email_content, delivery_id)
                
            # Track delivery
            self.delivery_tracking[delivery_id] = {
                'notification_id': notification.id,
                'sent_at': datetime.utcnow().isoformat(),
                'status': result.status,
                'recipient': content.get('recipient'),
                'subject': email_content.get('subject')
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=str(uuid.uuid4()),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def get_delivery_status(self, delivery_id: str) -> DeliveryStatus:
        """Get email delivery status"""        try:
            tracking_info = self.delivery_tracking.get(delivery_id)
            if not tracking_info:
                return DeliveryStatus.FAILED
                
            # If using API, check status via API
            if self.api_config.get('enabled', False):
                return await self._check_api_status(delivery_id)
            else:
                # For SMTP, return last known status
                return DeliveryStatus(tracking_info['status'])
                
        except Exception as e:
            self.logger.error(f"Failed to get email delivery status: {str(e)}")
            return DeliveryStatus.FAILED
            
    async def validate_configuration(self) -> bool:
        """Validate email configuration"""        try:
            if self.smtp_config:
                required_smtp_fields = ['host', 'port', 'username', 'password']
                if not all(field in self.smtp_config for field in required_smtp_fields):
                    return False
                    
            if self.api_config:
                required_api_fields = ['api_key', 'endpoint']
                if not all(field in self.api_config for field in required_api_fields):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Email configuration validation failed: {str(e)}")
            return False
            
    async def _prepare_email_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare email-specific content"""        return {
            'to': content.get('recipient'),
            'subject': content.get('subject', 'Notification'),
            'html_body': content.get('html_content', ''),
            'text_body': content.get('text_content', ''),
            'from_email': self.config.get('from_email', 'noreply@iainfluencer.com'),
            'from_name': self.config.get('from_name', 'IA Influencer Agent'),
            'attachments': content.get('attachments', [])
        }
        
    async def _send_via_smtp(
        self,
        email_content: Dict[str, Any],
        delivery_id: str
    ) -> ChannelDeliveryResult:
        """Send email via SMTP"""        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_content['subject']
            msg['From'] = f"{email_content['from_name']} <{email_content['from_email']}>"
            msg['To'] = email_content['to']
            msg['X-Delivery-ID'] = delivery_id
            
            # Add text and HTML parts
            if email_content['text_body']:
                text_part = MIMEText(email_content['text_body'], 'plain')
                msg.attach(text_part)
                
            if email_content['html_body']:
                html_part = MIMEText(email_content['html_body'], 'html')
                msg.attach(html_part)
                
            # Send via SMTP
            with smtplib.SMTP(
                self.smtp_config['host'],
                self.smtp_config['port']
            ) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                    
                server.login(
                    self.smtp_config['username'],
                    self.smtp_config['password']
                )
                
                server.send_message(msg)
                
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                status=DeliveryStatus.SENT,
                sent_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"SMTP send failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def _send_via_api(
        self,
        email_content: Dict[str, Any],
        delivery_id: str
    ) -> ChannelDeliveryResult:
        """Send email via API (e.g., SendGrid, Mailgun)"""        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'to': email_content['to'],
                    'from': email_content['from_email'],
                    'subject': email_content['subject'],
                    'html': email_content['html_body'],
                    'text': email_content['text_body'],
                    'custom_args': {'delivery_id': delivery_id}
                }
                
                headers = {
                    'Authorization': f"Bearer {self.api_config['api_key']}",
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    self.api_config['endpoint'],
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return ChannelDeliveryResult(
                            delivery_id=delivery_id,
                            status=DeliveryStatus.SENT,
                            sent_at=datetime.utcnow(),
                            external_id=response_data.get('id')
                        )
                    else:
                        error_text = await response.text()
                        return ChannelDeliveryResult(
                            delivery_id=delivery_id,
                            status=DeliveryStatus.FAILED,
                            error_message=f"API error: {error_text}"
                        )
                        
        except Exception as e:
            self.logger.error(f"API send failed: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )


class SMSChannelHandler(BaseChannelHandler):
    """Advanced SMS channel handler with multiple provider support"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_config = config.get('provider', {})
        self.delivery_tracking = {}
        
    async def initialize(self) -> bool:
        """Initialize SMS channel"""        try:
            # Validate provider configuration
            if not await self.validate_configuration():
                return False
                
            # Test connection with provider
            await self._test_provider_connection()
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SMS channel: {str(e)}")
            return False
            
    async def send_notification(
        self,
        notification: NotificationModel,
        content: Dict[str, Any]
    ) -> ChannelDeliveryResult:
        """Send SMS notification"""        try:
            delivery_id = str(uuid.uuid4())
            
            # Prepare SMS content
            sms_content = await self._prepare_sms_content(content)
            
            # Send via provider
            result = await self._send_via_provider(sms_content, delivery_id)
            
            # Track delivery
            self.delivery_tracking[delivery_id] = {
                'notification_id': notification.id,
                'sent_at': datetime.utcnow().isoformat(),
                'status': result.status,
                'recipient': sms_content.get('to'),
                'message': sms_content.get('message')
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=str(uuid.uuid4()),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def get_delivery_status(self, delivery_id: str) -> DeliveryStatus:
        """Get SMS delivery status"""        try:
            # Check with provider API
            return await self._check_provider_status(delivery_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get SMS delivery status: {str(e)}")
            return DeliveryStatus.FAILED
            
    async def validate_configuration(self) -> bool:
        """Validate SMS configuration"""        try:
            required_fields = ['api_key', 'from_number', 'provider_endpoint']
            return all(field in self.provider_config for field in required_fields)
            
        except Exception as e:
            self.logger.error(f"SMS configuration validation failed: {str(e)}")
            return False
            
    async def _prepare_sms_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare SMS-specific content with length limits"""        message = content.get('message', '')
        
        # Truncate message if too long (SMS limit is typically 160 characters)
        max_length = self.config.get('max_message_length', 160)
        if len(message) > max_length:
            message = message[:max_length-3] + "..."
            
        return {
            'to': content.get('recipient'),
            'from': self.provider_config['from_number'],
            'message': message,
            'delivery_receipt': True
        }
        
    async def _send_via_provider(
        self,
        sms_content: Dict[str, Any],
        delivery_id: str
    ) -> ChannelDeliveryResult:
        """Send SMS via provider API"""        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'to': sms_content['to'],
                    'from': sms_content['from'],
                    'text': sms_content['message'],
                    'delivery_receipt': sms_content.get('delivery_receipt', True),
                    'custom_data': {'delivery_id': delivery_id}
                }
                
                headers = {
                    'Authorization': f"Bearer {self.provider_config['api_key']}",
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    self.provider_config['provider_endpoint'],
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return ChannelDeliveryResult(
                            delivery_id=delivery_id,
                            status=DeliveryStatus.SENT,
                            sent_at=datetime.utcnow(),
                            external_id=response_data.get('message_id')
                        )
                    else:
                        error_text = await response.text()
                        return ChannelDeliveryResult(
                            delivery_id=delivery_id,
                            status=DeliveryStatus.FAILED,
                            error_message=f"Provider error: {error_text}"
                        )
                        
        except Exception as e:
            return ChannelDeliveryResult(
                delivery_id=delivery_id,
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )


class PushNotificationChannelHandler(BaseChannelHandler):
    """Advanced push notification handler for mobile and web"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.fcm_config = config.get('fcm', {})
        self.apns_config = config.get('apns', {})
        self.web_push_config = config.get('web_push', {})
        self.delivery_tracking = {}
        
    async def initialize(self) -> bool:
        """Initialize push notification channel"""        try:
            # Initialize FCM if configured
            if self.fcm_config:
                await self._initialize_fcm()
                
            # Initialize APNS if configured
            if self.apns_config:
                await self._initialize_apns()
                
            # Initialize Web Push if configured
            if self.web_push_config:
                await self._initialize_web_push()
                
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize push notification channel: {str(e)}")
            return False
            
    async def send_notification(
        self,
        notification: NotificationModel,
        content: Dict[str, Any]
    ) -> ChannelDeliveryResult:
        """Send push notification"""        try:
            delivery_id = str(uuid.uuid4())
            
            # Determine platform
            platform = content.get('platform', 'auto')
            
            # Prepare push content
            push_content = await self._prepare_push_content(content)
            
            # Send based on platform
            if platform == 'ios' or (platform == 'auto' and self.apns_config):
                result = await self._send_apns(push_content, delivery_id)
            elif platform == 'android' or (platform == 'auto' and self.fcm_config):
                result = await self._send_fcm(push_content, delivery_id)
            elif platform == 'web' or (platform == 'auto' and self.web_push_config):
                result = await self._send_web_push(push_content, delivery_id)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
                
            # Track delivery
            self.delivery_tracking[delivery_id] = {
                'notification_id': notification.id,
                'sent_at': datetime.utcnow().isoformat(),
                'status': result.status,
                'platform': platform,
                'recipient': content.get('device_token')
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {str(e)}")
            return ChannelDeliveryResult(
                delivery_id=str(uuid.uuid4()),
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            
    async def get_delivery_status(self, delivery_id: str) -> DeliveryStatus:
        """Get push notification delivery status"""        try:
            tracking_info = self.delivery_tracking.get(delivery_id)
            if not tracking_info:
                return DeliveryStatus.FAILED
                
            # Return last known status (push notifications don't typically provide detailed delivery status)
            return DeliveryStatus(tracking_info['status'])
            
        except Exception as e:
            self.logger.error(f"Failed to get push notification delivery status: {str(e)}")
            return DeliveryStatus.FAILED
            
    async def validate_configuration(self) -> bool:
        """Validate push notification configuration"""        try:
            # At least one platform should be configured
            return bool(self.fcm_config or self.apns_config or self.web_push_config)
            
        except Exception as e:
            self.logger.error(f"Push notification configuration validation failed: {str(e)}")
            return False
            
    async def _prepare_push_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare push notification content"""        return {
            'device_token': content.get('device_token'),
            'title': content.get('title', '')[:50],  # Truncate title
            'body': content.get('message', '')[:200],  # Truncate body
            'icon': content.get('icon', ''),
            'click_action': content.get('action_url', ''),
            'badge': content.get('badge', 0),
            'sound': content.get('sound', 'default'),
            'data': content.get('custom_data', {})
        }


class ChannelManager:
    """    Advanced multi-channel notification delivery manager
    
    Provides intelligent channel selection, delivery optimization, and comprehensive
    multi-platform communication management for the IA Influencer Agent platform.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize channel handlers
        self.handlers: Dict[ChannelType, BaseChannelHandler] = {}
        self.channel_capabilities: Dict[ChannelType, ChannelCapability] = {}
        self.channel_metrics: Dict[ChannelType, ChannelMetrics] = {}
        
        # Security and monitoring
        self.security_manager = ChannelSecurityManager(config.get('security', {}))
        self.monitoring = ChannelMonitoringService(config.get('monitoring', {}))
        
        # Delivery tracking
        self.active_deliveries: Dict[str, Dict[str, Any]] = {}
        self.delivery_history: List[Dict[str, Any]] = []
        
        # Performance optimization
        self.channel_performance_cache = {}
        self.optimal_channel_cache = {}
        
        # AI-driven channel selection
        self.ai_optimizer = self._initialize_ai_optimizer()
        
    def _initialize_ai_optimizer(self):
        """Initialize AI-driven channel optimization"""        from ...ai.optimization.channel_optimizer import ChannelOptimizer
        return ChannelOptimizer(self.config.get('ai_optimizer', {}))
        
    async def initialize_manager(self):
        """Initialize the channel manager and all handlers"""        try:
            self.logger.info("Initializing ChannelManager with advanced multi-channel support")
            
            # Initialize configured channel handlers
            await self._initialize_channel_handlers()
            
            # Load channel capabilities
            await self._load_channel_capabilities()
            
            # Initialize metrics
            await self._initialize_channel_metrics()
            
            # Start monitoring
            await self.monitoring.start_monitoring()
            
            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._monitor_channel_performance()),
                asyncio.create_task(self._optimize_channel_selection()),
                asyncio.create_task(self._cleanup_delivery_history())
            ]
            
            self.logger.info("ChannelManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChannelManager: {str(e)}")
            return False
            
    async def _initialize_channel_handlers(self):
        """Initialize all configured channel handlers"""        handler_configs = self.config.get('channels', {})
        
        # Email handler
        if 'email' in handler_configs:
            email_handler = EmailChannelHandler(handler_configs['email'])
            if await email_handler.initialize():
                self.handlers[ChannelType.EMAIL] = email_handler
                
        # SMS handler
        if 'sms' in handler_configs:
            sms_handler = SMSChannelHandler(handler_configs['sms'])
            if await sms_handler.initialize():
                self.handlers[ChannelType.SMS] = sms_handler
                
        # Push notification handler
        if 'push' in handler_configs:
            push_handler = PushNotificationChannelHandler(handler_configs['push'])
            if await push_handler.initialize():
                self.handlers[ChannelType.PUSH_NOTIFICATION] = push_handler
                
        # Additional handlers can be initialized here
        
        self.logger.info(f"Initialized {len(self.handlers)} channel handlers")
        
    async def _load_channel_capabilities(self):
        """Load capabilities for each initialized channel"""        for channel_type in self.handlers.keys():
            if channel_type == ChannelType.EMAIL:
                self.channel_capabilities[channel_type] = ChannelCapability(
                    channel=channel_type,
                    supports_rich_content=True,
                    supports_attachments=True,
                    supports_interactive_elements=True,
                    max_content_length=50000,
                    delivery_speed="fast",
                    cost_tier="low",
                    reliability_score=0.95,
                    supported_content_types=["text", "html", "images", "documents"]
                )
            elif channel_type == ChannelType.SMS:
                self.channel_capabilities[channel_type] = ChannelCapability(
                    channel=channel_type,
                    supports_rich_content=False,
                    supports_attachments=False,
                    supports_interactive_elements=False,
                    max_content_length=160,
                    delivery_speed="instant",
                    cost_tier="medium",
                    reliability_score=0.98,
                    supported_content_types=["text"]
                )
            elif channel_type == ChannelType.PUSH_NOTIFICATION:
                self.channel_capabilities[channel_type] = ChannelCapability(
                    channel=channel_type,
                    supports_rich_content=False,
                    supports_attachments=False,
                    supports_interactive_elements=True,
                    max_content_length=250,
                    delivery_speed="instant",
                    cost_tier="free",
                    reliability_score=0.90,
                    supported_content_types=["text", "images"]
                )
                
    async def _initialize_channel_metrics(self):
        """Initialize metrics tracking for all channels"""        for channel_type in self.handlers.keys():
            self.channel_metrics[channel_type] = ChannelMetrics(channel=channel_type)
            
    async def send_multi_channel_notification(
        self,
        notification: NotificationModel,
        channels: List[ChannelType],
        content_variants: Dict[ChannelType, Dict[str, Any]],
        delivery_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[ChannelType, ChannelDeliveryResult]:
        """        Send notification through multiple channels with optimized delivery
        
        Args:
            notification: Notification to send
            channels: List of channels to use
            content_variants: Channel-specific content variants
            delivery_preferences: Delivery optimization preferences
            
        Returns:
            Dictionary of delivery results per channel
        """        try:
            delivery_results = {}
            
            # Security validation
            if not await self.security_manager.validate_multi_channel_request(
                notification, channels
            ):
                raise ValueError("Security validation failed for multi-channel request")
                
            # Optimize channel selection if requested
            if delivery_preferences and delivery_preferences.get('optimize_channels', False):
                channels = await self._optimize_channel_selection(
                    notification, channels, delivery_preferences
                )
                
            # Send through each channel
            delivery_tasks = []
            for channel in channels:
                if channel in self.handlers:
                    content = content_variants.get(channel, {})
                    task = asyncio.create_task(
                        self._send_single_channel(notification, channel, content)
                    )
                    delivery_tasks.append((channel, task))
                    
            # Wait for all deliveries to complete
            for channel, task in delivery_tasks:
                try:
                    result = await task
                    delivery_results[channel] = result
                    
                    # Update metrics
                    await self._update_channel_metrics(channel, result)
                    
                except Exception as e:
                    self.logger.error(f"Channel delivery failed for {channel.value}: {str(e)}")
                    delivery_results[channel] = ChannelDeliveryResult(
                        delivery_id=str(uuid.uuid4()),
                        status=DeliveryStatus.FAILED,
                        error_message=str(e)
                    )
                    
            # Record delivery attempt
            await self.monitoring.record_multi_channel_delivery(
                notification.id, delivery_results
            )
            
            return delivery_results
            
        except Exception as e:
            self.logger.error(f"Multi-channel delivery failed: {str(e)}")
            raise
            
    async def _send_single_channel(
        self,
        notification: NotificationModel,
        channel: ChannelType,
        content: Dict[str, Any]
    ) -> ChannelDeliveryResult:
        """Send notification through a single channel"""        try:
            handler = self.handlers.get(channel)
            if not handler:
                raise ValueError(f"No handler available for channel: {channel.value}")
                
            # Validate content for channel
            await self._validate_channel_content(channel, content)
            
            # Send notification
            result = await handler.send_notification(notification, content)
            
            # Track active delivery
            if result.status not in [DeliveryStatus.FAILED]:
                self.active_deliveries[result.delivery_id] = {
                    'notification_id': notification.id,
                    'channel': channel.value,
                    'sent_at': datetime.utcnow().isoformat(),
                    'status': result.status.value
                }
                
            return result
            
        except Exception as e:
            self.logger.error(f"Single channel delivery failed: {str(e)}")
            raise
            
    async def get_optimal_channels(
        self,
        user_preferences: Dict[str, Any],
        notification_type: str,
        priority: NotificationPriority,
        content_requirements: Optional[Dict[str, Any]] = None
    ) -> List[ChannelType]:
        """        Get optimal channel selection using AI-driven optimization
        
        Args:
            user_preferences: User's channel preferences
            notification_type: Type of notification
            priority: Notification priority
            content_requirements: Content-specific requirements
            
        Returns:
            List of optimal channels in priority order
        """        try:
            # Check cache first
            cache_key = self._generate_cache_key(
                user_preferences, notification_type, priority
            )
            
            if cache_key in self.optimal_channel_cache:
                cached_result = self.optimal_channel_cache[cache_key]
                if (datetime.utcnow() - cached_result['timestamp']).seconds < 3600:  # 1 hour cache
                    return cached_result['channels']
                    
            # Use AI optimizer to determine optimal channels
            optimal_channels = await self.ai_optimizer.optimize_channel_selection(
                available_channels=list(self.handlers.keys()),
                channel_capabilities=self.channel_capabilities,
                channel_metrics=self.channel_metrics,
                user_preferences=user_preferences,
                notification_type=notification_type,
                priority=priority,
                content_requirements=content_requirements or {}
            )
            
            # Cache result
            self.optimal_channel_cache[cache_key] = {
                'channels': optimal_channels,
                'timestamp': datetime.utcnow()
            }
            
            return optimal_channels
            
        except Exception as e:
            self.logger.error(f"Failed to get optimal channels: {str(e)}")
            # Fallback to default channels
            return self._get_default_channels(priority)
            
    async def get_channel_status(self, channel: ChannelType) -> Dict[str, Any]:
        """Get comprehensive status information for a channel"""        try:
            handler = self.handlers.get(channel)
            if not handler:
                return {"error": "Channel not configured"}
                
            capabilities = self.channel_capabilities.get(channel)
            metrics = self.channel_metrics.get(channel)
            
            return {
                "channel": channel.value,
                "is_initialized": handler.is_initialized,
                "capabilities": capabilities.__dict__ if capabilities else {},
                "metrics": metrics.__dict__ if metrics else {},
                "configuration_valid": await handler.validate_configuration(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get channel status: {str(e)}")
            return {"error": str(e)}
            
    async def get_delivery_status(
        self,
        delivery_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive delivery status information"""        try:
            # Check active deliveries
            active_delivery = self.active_deliveries.get(delivery_id)
            if not active_delivery:
                # Check history
                for record in self.delivery_history:
                    if record.get('delivery_id') == delivery_id:
                        return record
                return {"error": "Delivery not found"}
                
            channel_type = ChannelType(active_delivery['channel'])
            handler = self.handlers.get(channel_type)
            
            if handler:
                # Get current status from handler
                current_status = await handler.get_delivery_status(delivery_id)
                active_delivery['current_status'] = current_status.value
                
            return active_delivery
            
        except Exception as e:
            self.logger.error(f"Failed to get delivery status: {str(e)}")
            return {"error": str(e)}
            
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive channel system analytics"""        try:
            analytics = {
                "channel_performance": {},
                "delivery_statistics": {},
                "optimization_insights": {},
                "system_health": {}
            }
            
            # Channel performance
            for channel_type, metrics in self.channel_metrics.items():
                analytics["channel_performance"][channel_type.value] = {
                    "success_rate": metrics.success_rate,
                    "engagement_rate": metrics.engagement_rate,
                    "average_delivery_time": metrics.average_delivery_time,
                    "cost_per_delivery": metrics.cost_per_delivery,
                    "total_sent": metrics.total_sent,
                    "total_delivered": metrics.total_delivered
                }
                
            # Delivery statistics
            total_deliveries = sum(m.total_sent for m in self.channel_metrics.values())
            total_successful = sum(m.total_delivered for m in self.channel_metrics.values())
            
            analytics["delivery_statistics"] = {
                "total_deliveries": total_deliveries,
                "total_successful": total_successful,
                "overall_success_rate": total_successful / total_deliveries if total_deliveries > 0 else 0,
                "active_deliveries": len(self.active_deliveries)
            }
            
            # System health
            healthy_channels = sum(
                1 for handler in self.handlers.values()
                if handler.is_initialized
            )
            
            analytics["system_health"] = {
                "total_channels": len(self.handlers),
                "healthy_channels": healthy_channels,
                "health_percentage": healthy_channels / len(self.handlers) if self.handlers else 0
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get system analytics: {str(e)}")
            return {}


class MultiChannelSender:
    """    High-level multi-channel sender with intelligent routing and fallback
    """    
    def __init__(self, channel_manager: ChannelManager):
        self.channel_manager = channel_manager
        self.logger = logging.getLogger(__name__)
        
    async def send_with_fallback(
        self,
        notification: NotificationModel,
        primary_channels: List[ChannelType],
        fallback_channels: List[ChannelType],
        content_variants: Dict[ChannelType, Dict[str, Any]],
        fallback_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Send notification with intelligent fallback mechanism
        
        Args:
            notification: Notification to send
            primary_channels: Primary channels to try first
            fallback_channels: Fallback channels if primary fails
            content_variants: Content variants for each channel
            fallback_conditions: Conditions that trigger fallback
            
        Returns:
            Comprehensive delivery report
        """        try:
            delivery_report = {
                "notification_id": notification.id,
                "primary_results": {},
                "fallback_results": {},
                "final_status": "unknown",
                "channels_used": [],
                "delivery_time": datetime.utcnow().isoformat()
            }
            
            # Try primary channels first
            primary_results = await self.channel_manager.send_multi_channel_notification(
                notification, primary_channels, content_variants
            )
            
            delivery_report["primary_results"] = {
                ch.value: result.__dict__ for ch, result in primary_results.items()
            }
            
            # Check if fallback is needed
            need_fallback = await self._check_fallback_conditions(
                primary_results, fallback_conditions or {}
            )
            
            if need_fallback and fallback_channels:
                self.logger.info(f"Triggering fallback for notification {notification.id}")
                
                fallback_results = await self.channel_manager.send_multi_channel_notification(
                    notification, fallback_channels, content_variants
                )
                
                delivery_report["fallback_results"] = {
                    ch.value: result.__dict__ for ch, result in fallback_results.items()
                }
                
            # Determine final status
            all_results = {**primary_results, **delivery_report.get("fallback_results", {})}
            successful_deliveries = [
                ch for ch, result in all_results.items()
                if hasattr(result, 'status') and result.status == DeliveryStatus.DELIVERED
            ]
            
            if successful_deliveries:
                delivery_report["final_status"] = "success"
                delivery_report["channels_used"] = [ch.value if hasattr(ch, 'value') else str(ch) for ch in successful_deliveries]
            else:
                delivery_report["final_status"] = "failed"
                
            return delivery_report
            
        except Exception as e:
            self.logger.error(f"Multi-channel send with fallback failed: {str(e)}")
            return {
                "notification_id": notification.id,
                "final_status": "error",
                "error_message": str(e)
            }
            
    async def _check_fallback_conditions(
        self,
        primary_results: Dict[ChannelType, ChannelDeliveryResult],
        fallback_conditions: Dict[str, Any]
    ) -> bool:
        """Check if fallback conditions are met"""        try:
            # Default fallback conditions
            default_conditions = {
                "min_success_rate": 0.5,
                "max_failures": len(primary_results),
                "required_channels": []
            }
            
            conditions = {**default_conditions, **fallback_conditions}
            
            # Calculate success rate
            successful = sum(
                1 for result in primary_results.values()
                if result.status not in [DeliveryStatus.FAILED, DeliveryStatus.BLOCKED]
            )
            
            success_rate = successful / len(primary_results) if primary_results else 0
            
            # Check conditions
            if success_rate < conditions["min_success_rate"]:
                return True
                
            failures = len(primary_results) - successful
            if failures >= conditions["max_failures"]:
                return True
                
            # Check required channels
            for required_channel in conditions["required_channels"]:
                if required_channel not in primary_results:
                    return True
                result = primary_results[required_channel]
                if result.status in [DeliveryStatus.FAILED, DeliveryStatus.BLOCKED]:
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking fallback conditions: {str(e)}")
            return True  # Fallback on error
