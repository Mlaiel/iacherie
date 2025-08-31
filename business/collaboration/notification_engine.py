"""
Advanced Collaboration Notification System for IA Influencer Agent
Professional notification management and communication orchestration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import asyncio
import logging
import uuid
import json

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of collaboration notifications"""
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_REJECTED = "collaboration_rejected"
    COLLABORATION_EXPIRED = "collaboration_expired"
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    REVENUE_GENERATED = "revenue_generated"
    PAYOUT_PROCESSED = "payout_processed"
    PAYOUT_FAILED = "payout_failed"
    PARTNERSHIP_OPPORTUNITY = "partnership_opportunity"
    MILESTONE_REACHED = "milestone_reached"
    DEADLINE_APPROACHING = "deadline_approaching"
    PERFORMANCE_ALERT = "performance_alert"
    SYSTEM_UPDATE = "system_update"
    LEGAL_NOTICE = "legal_notice"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


@dataclass
class NotificationRecipient:
    """Notification recipient configuration"""
    user_id: str
    user_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_channels: List[NotificationChannel] = field(default_factory=list)
    timezone: str = "UTC"
    language: str = "en"
    notification_preferences: Dict[str, Any] = field(default_factory=dict)
    do_not_disturb_hours: Optional[Tuple[int, int]] = None  # (start_hour, end_hour)


@dataclass
class NotificationTemplate:
    """Notification template configuration"""
    template_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str] = field(default_factory=list)
    localized_templates: Dict[str, Dict[str, str]] = field(default_factory=dict)
    formatting_rules: Dict[str, Any] = field(default_factory=dict)


class CollaborationNotification(BaseModel):
    """Collaboration notification model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    
    # Content
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    rich_content: Optional[Dict[str, Any]] = None
    
    # Recipients
    recipients: List[NotificationRecipient]
    channels: List[NotificationChannel]
    
    # Context
    collaboration_id: Optional[str] = None
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    
    # Scheduling
    scheduled_time: Optional[datetime] = None
    timezone: str = "UTC"
    respect_do_not_disturb: bool = True
    
    # Delivery tracking
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    status: NotificationStatus = NotificationStatus.PENDING
    
    # Analytics
    tracking_enabled: bool = True
    click_tracking: bool = True
    open_tracking: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class NotificationDeliveryResult:
    """Result of notification delivery attempt"""
    notification_id: str
    recipient_id: str
    channel: NotificationChannel
    status: NotificationStatus
    delivery_time: Optional[datetime] = None
    error_message: Optional[str] = None
    external_id: Optional[str] = None  # ID from external service
    cost: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationAnalytics:
    """Notification analytics data"""
    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_clicked: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    by_channel: Dict[NotificationChannel, Dict[str, int]] = field(default_factory=dict)
    by_type: Dict[NotificationType, Dict[str, int]] = field(default_factory=dict)


class NotificationEngine:
    """
    Advanced Collaboration Notification Engine
    Manages notification delivery, templates, preferences, and analytics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.notification_queue: List[CollaborationNotification] = []
        self.sent_notifications: Dict[str, CollaborationNotification] = {}
        self.delivery_results: List[NotificationDeliveryResult] = []
        self.templates: Dict[str, NotificationTemplate] = {}
        self.channel_providers = {}
        self.analytics_data = NotificationAnalytics()
        
        # Initialize engine
        asyncio.create_task(self._initialize_engine())
    
    async def _initialize_engine(self):
        """Initialize notification engine"""



        try:
            await self._setup_channel_providers()
            await self._load_notification_templates()
            await self._initialize_analytics_tracking()
            await self._setup_delivery_scheduler()
            
            logger.info("Notification engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing notification engine: {str(e)}")
            raise
    
    async def send_notification(
        self,
        notification: CollaborationNotification,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Send notification to recipients
        """



        try:
            notification_id = notification.id
            
            # Validate notification
            validation_result = await self._validate_notification(notification)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'notification_id': notification_id,
                    'error': validation_result['error']
                }
            
            # Apply user preferences
            filtered_notification = await self._apply_user_preferences(notification)
            
            # Check scheduling
            if immediate or not notification.scheduled_time:
                delivery_results = await self._deliver_notification(filtered_notification)
            else:
                # Schedule for later delivery
                await self._schedule_notification(filtered_notification)
                delivery_results = []
            
            # Store notification
            self.sent_notifications[notification_id] = filtered_notification
            
            # Update analytics
            await self._update_analytics(filtered_notification, delivery_results)
            
            return {
                'success': True,
                'notification_id': notification_id,
                'delivery_results': [
                    {
                        'recipient_id': r.recipient_id,
                        'channel': r.channel.value,
                        'status': r.status.value,
                        'error': r.error_message
                    }
                    for r in delivery_results
                ],
                'scheduled': notification.scheduled_time is not None and not immediate,
                'sent_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return {
                'success': False,
                'notification_id': notification.id,
                'error': str(e)
            }
    
    async def send_collaboration_request_notification(
        self,
        collaboration_data: Dict[str, Any],
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send collaboration request notification
        """



        try:
            # Create recipients
            notification_recipients = [
                NotificationRecipient(
                    user_id=r['user_id'],
                    user_name=r['user_name'],
                    email=r.get('email'),
                    preferred_channels=r.get('preferred_channels', [NotificationChannel.EMAIL, NotificationChannel.IN_APP])
                )
                for r in recipients
            ]
            
            # Create notification
            notification = CollaborationNotification(
                type=NotificationType.COLLABORATION_REQUEST,
                priority=NotificationPriority.HIGH,
                title=f"New Collaboration Request: {collaboration_data['title']}",
                message=f"You have received a new collaboration request from {collaboration_data['creator_name']}. "
                       f"Project: {collaboration_data['title']}. Click to view details and respond.",
                recipients=notification_recipients,
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                collaboration_id=collaboration_data['collaboration_id'],
                rich_content={
                    'collaboration_type': collaboration_data['type'],
                    'expected_duration': collaboration_data.get('duration'),
                    'budget': collaboration_data.get('budget'),
                    'action_url': f"/collaborations/{collaboration_data['collaboration_id']}/view"
                }
            )
            
            return await self.send_notification(notification)
            
        except Exception as e:
            logger.error(f"Error sending collaboration request notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def send_revenue_notification(
        self,
        revenue_data: Dict[str, Any],
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send revenue notification to collaborators
        """



        try:
            # Create recipients
            notification_recipients = [
                NotificationRecipient(
                    user_id=r['user_id'],
                    user_name=r['user_name'],
                    email=r.get('email'),
                    preferred_channels=r.get('preferred_channels', [NotificationChannel.EMAIL])
                )
                for r in recipients
            ]
            
            # Create notification
            notification = CollaborationNotification(
                type=NotificationType.REVENUE_GENERATED,
                priority=NotificationPriority.MEDIUM,
                title=f"Revenue Generated: €{revenue_data['amount']}",
                message=f"Your collaboration '{revenue_data['collaboration_name']}' has generated "
                       f"€{revenue_data['amount']} in revenue. Your share: €{revenue_data.get('your_share', '0.00')}. "
                       f"View detailed breakdown in your dashboard.",
                recipients=notification_recipients,
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                collaboration_id=revenue_data['collaboration_id'],
                rich_content={
                    'total_revenue': revenue_data['amount'],
                    'your_share': revenue_data.get('your_share'),
                    'revenue_source': revenue_data.get('source'),
                    'action_url': f"/dashboard/revenue/{revenue_data['collaboration_id']}"
                }
            )
            
            return await self.send_notification(notification)
            
        except Exception as e:
            logger.error(f"Error sending revenue notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def send_payout_notification(
        self,
        payout_data: Dict[str, Any],
        recipient: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send payout notification to collaborator
        """



        try:
            # Create recipient
            notification_recipient = NotificationRecipient(
                user_id=recipient['user_id'],
                user_name=recipient['user_name'],
                email=recipient.get('email'),
                preferred_channels=recipient.get('preferred_channels', [NotificationChannel.EMAIL])
            )
            
            # Create notification
            notification = CollaborationNotification(
                type=NotificationType.PAYOUT_PROCESSED,
                priority=NotificationPriority.HIGH,
                title=f"Payout Processed: €{payout_data['amount']}",
                message=f"Your payout of €{payout_data['amount']} has been processed successfully. "
                       f"Payment method: {payout_data['payment_method']}. "
                       f"Reference: {payout_data['reference']}. Funds should arrive within 1-3 business days.",
                recipients=[notification_recipient],
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
                collaboration_id=payout_data.get('collaboration_id'),
                rich_content={
                    'amount': payout_data['amount'],
                    'payment_method': payout_data['payment_method'],
                    'reference': payout_data['reference'],
                    'expected_arrival': payout_data.get('expected_arrival'),
                    'action_url': f"/dashboard/payouts/{payout_data['payout_id']}"
                }
            )
            
            return await self.send_notification(notification)
            
        except Exception as e:
            logger.error(f"Error sending payout notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def send_deadline_reminder(
        self,
        collaboration_data: Dict[str, Any],
        recipients: List[Dict[str, Any]],
        deadline: datetime
    ) -> Dict[str, Any]:
        """
        Send deadline reminder notification
        """



        try:
            days_remaining = (deadline - datetime.utcnow()).days
            
            # Determine priority based on time remaining
            if days_remaining <= 1:
                priority = NotificationPriority.URGENT
            elif days_remaining <= 3:
                priority = NotificationPriority.HIGH
            else:
                priority = NotificationPriority.MEDIUM
            
            # Create recipients
            notification_recipients = [
                NotificationRecipient(
                    user_id=r['user_id'],
                    user_name=r['user_name'],
                    email=r.get('email'),
                    preferred_channels=r.get('preferred_channels', [NotificationChannel.EMAIL, NotificationChannel.IN_APP])
                )
                for r in recipients
            ]
            
            # Create notification
            notification = CollaborationNotification(
                type=NotificationType.DEADLINE_APPROACHING,
                priority=priority,
                title=f"Deadline Approaching: {collaboration_data['title']}",
                message=f"Reminder: The deadline for '{collaboration_data['title']}' is approaching. "
                       f"{'Tomorrow' if days_remaining == 1 else f'{days_remaining} days remaining'}. "
                       f"Please complete your tasks to avoid delays.",
                recipients=notification_recipients,
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                collaboration_id=collaboration_data['collaboration_id'],
                rich_content={
                    'deadline': deadline.isoformat(),
                    'days_remaining': days_remaining,
                    'pending_tasks': collaboration_data.get('pending_tasks', []),
                    'action_url': f"/collaborations/{collaboration_data['collaboration_id']}/tasks"
                }
            )
            
            return await self.send_notification(notification)
            
        except Exception as e:
            logger.error(f"Error sending deadline reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_notification_analytics(
        self,
        time_period: Optional[Tuple[datetime, datetime]] = None,
        collaboration_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get notification analytics
        """



        try:
            # Filter notifications based on criteria
            filtered_notifications = list(self.sent_notifications.values())
            
            if time_period:
                start_date, end_date = time_period
                filtered_notifications = [
                    n for n in filtered_notifications
                    if start_date <= n.created_at <= end_date
                ]
            
            if collaboration_id:
                filtered_notifications = [
                    n for n in filtered_notifications
                    if n.collaboration_id == collaboration_id
                ]
            
            # Calculate analytics
            total_sent = len(filtered_notifications)
            total_delivered = sum(1 for n in filtered_notifications if n.status in [NotificationStatus.DELIVERED, NotificationStatus.READ])
            total_read = sum(1 for n in filtered_notifications if n.status == NotificationStatus.READ)
            
            # Calculate rates
            delivery_rate = (total_delivered / total_sent) if total_sent > 0 else 0.0
            read_rate = (total_read / total_delivered) if total_delivered > 0 else 0.0
            
            # Analytics by type
            by_type = {}
            for notification_type in NotificationType:
                type_notifications = [n for n in filtered_notifications if n.type == notification_type]
                by_type[notification_type.value] = {
                    'sent': len(type_notifications),
                    'delivered': sum(1 for n in type_notifications if n.status in [NotificationStatus.DELIVERED, NotificationStatus.READ]),
                    'read': sum(1 for n in type_notifications if n.status == NotificationStatus.READ)
                }
            
            # Analytics by channel
            by_channel = {}
            for channel in NotificationChannel:
                channel_results = [r for r in self.delivery_results if r.channel == channel]
                by_channel[channel.value] = {
                    'sent': len([r for r in channel_results if r.status == NotificationStatus.SENT]),
                    'delivered': len([r for r in channel_results if r.status == NotificationStatus.DELIVERED]),
                    'failed': len([r for r in channel_results if r.status == NotificationStatus.FAILED])
                }
            
            return {
                'time_period': time_period,
                'collaboration_id': collaboration_id,
                'summary': {
                    'total_sent': total_sent,
                    'total_delivered': total_delivered,
                    'total_read': total_read,
                    'delivery_rate': round(delivery_rate * 100, 2),
                    'read_rate': round(read_rate * 100, 2)
                },
                'by_type': by_type,
                'by_channel': by_channel,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting notification analytics: {str(e)}")
            return {'error': str(e), 'generated_at': datetime.utcnow()}
    
    # Private helper methods
    async def _setup_channel_providers(self):
        """Setup notification channel providers"""
        self.channel_providers = {
            NotificationChannel.EMAIL: {
                'provider': 'sendgrid',
                'configured': True,
                'cost_per_notification': 0.001
            },
            NotificationChannel.SMS: {
                'provider': 'twilio',
                'configured': True,
                'cost_per_notification': 0.05
            },
            NotificationChannel.PUSH_NOTIFICATION: {
                'provider': 'firebase',
                'configured': True,
                'cost_per_notification': 0.0
            },
            NotificationChannel.IN_APP: {
                'provider': 'internal',
                'configured': True,
                'cost_per_notification': 0.0
            },
            NotificationChannel.WEBHOOK: {
                'provider': 'internal',
                'configured': True,
                'cost_per_notification': 0.0
            }
        }
    
    async def _load_notification_templates(self):
        """Load notification templates"""
        # Mock templates - in reality would load from database
        self.templates = {
            'collaboration_request_email': NotificationTemplate(
                template_id='collaboration_request_email',
                notification_type=NotificationType.COLLABORATION_REQUEST,
                channel=NotificationChannel.EMAIL,
                subject_template="New Collaboration Request: {title}",
                body_template="You have received a collaboration request from {creator_name}...",
                variables=['title', 'creator_name', 'description', 'action_url']
            ),
            'revenue_generated_email': NotificationTemplate(
                template_id='revenue_generated_email',
                notification_type=NotificationType.REVENUE_GENERATED,
                channel=NotificationChannel.EMAIL,
                subject_template="Revenue Generated: €{amount}",
                body_template="Your collaboration has generated €{amount} in revenue...",
                variables=['amount', 'collaboration_name', 'your_share', 'action_url']
            )
        }
    
    async def _initialize_analytics_tracking(self):
        """Initialize analytics tracking"""
        self.analytics_data = NotificationAnalytics()
    
    async def _setup_delivery_scheduler(self):
        """Setup notification delivery scheduler"""
        # This would setup a background task to process scheduled notifications
        asyncio.create_task(self._process_scheduled_notifications())
    
    async def _validate_notification(self, notification: CollaborationNotification) -> Dict[str, Any]:
        """Validate notification before sending"""



        try:
            # Check recipients
            if not notification.recipients:
                return {'valid': False, 'error': 'No recipients specified'}
            
            # Check channels
            if not notification.channels:
                return {'valid': False, 'error': 'No delivery channels specified'}
            
            # Validate recipient contact information
            for recipient in notification.recipients:
                for channel in notification.channels:
                    if channel == NotificationChannel.EMAIL and not recipient.email:
                        return {'valid': False, 'error': f'Email required for recipient {recipient.user_id}'}
                    elif channel == NotificationChannel.SMS and not recipient.phone:
                        return {'valid': False, 'error': f'Phone required for recipient {recipient.user_id}'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    async def _apply_user_preferences(
        self, 
        notification: CollaborationNotification
    ) -> CollaborationNotification:
        """Apply user preferences to notification"""
        # Filter recipients based on their preferences
        filtered_recipients = []
        
        for recipient in notification.recipients:
            # Check if user has disabled this notification type
            if self._user_allows_notification(recipient, notification.type):
                # Filter channels based on user preferences
                allowed_channels = [
                    channel for channel in notification.channels
                    if channel in recipient.preferred_channels or not recipient.preferred_channels
                ]
                
                if allowed_channels:
                    filtered_recipients.append(recipient)
        
        # Update notification with filtered recipients
        notification.recipients = filtered_recipients
        
        return notification
    
    def _user_allows_notification(
        self, 
        recipient: NotificationRecipient, 
        notification_type: NotificationType
    ) -> bool:
        """Check if user allows this type of notification"""
        # Check notification preferences
        preferences = recipient.notification_preferences
        type_key = f"allow_{notification_type.value}"
        
        # Default to True if not specified
        return preferences.get(type_key, True)
    
    async def _deliver_notification(
        self, 
        notification: CollaborationNotification
    ) -> List[NotificationDeliveryResult]:
        """Deliver notification to all recipients via all channels"""
        delivery_results = []
        
        for recipient in notification.recipients:
            for channel in notification.channels:
                # Check do-not-disturb hours
                if self._is_do_not_disturb_time(recipient, notification):
                    # Schedule for later
                    await self._schedule_notification_for_recipient(notification, recipient, channel)
                    continue
                
                # Deliver notification
                result = await self._deliver_to_channel(notification, recipient, channel)
                delivery_results.append(result)
        
        return delivery_results
    
    def _is_do_not_disturb_time(
        self, 
        recipient: NotificationRecipient, 
        notification: CollaborationNotification
    ) -> bool:
        """Check if it's do-not-disturb time for recipient"""
        if not notification.respect_do_not_disturb or not recipient.do_not_disturb_hours:
            return False
        
        # Convert current time to recipient's timezone
        current_hour = datetime.utcnow().hour  # Simplified - should handle timezone properly
        start_hour, end_hour = recipient.do_not_disturb_hours
        
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:  # Spans midnight
            return current_hour >= start_hour or current_hour <= end_hour
    
    async def _deliver_to_channel(
        self,
        notification: CollaborationNotification,
        recipient: NotificationRecipient,
        channel: NotificationChannel
    ) -> NotificationDeliveryResult:
        """Deliver notification via specific channel"""



        try:
            # Get channel provider
            provider = self.channel_providers.get(channel)
            if not provider or not provider['configured']:
                return NotificationDeliveryResult(
                    notification_id=notification.id,
                    recipient_id=recipient.user_id,
                    channel=channel,
                    status=NotificationStatus.FAILED,
                    error_message=f"Channel {channel.value} not configured"
                )
            
            # Mock delivery - in reality would use actual providers
            await asyncio.sleep(0.1)  # Simulate delivery time
            
            # Simulate success/failure
            import random
            success_rate = 0.95  # 95% success rate
            
            if random.random() < success_rate:
                result = NotificationDeliveryResult(
                    notification_id=notification.id,
                    recipient_id=recipient.user_id,
                    channel=channel,
                    status=NotificationStatus.DELIVERED,
                    delivery_time=datetime.utcnow(),
                    external_id=f"{channel.value}_{uuid.uuid4().hex[:8]}",
                    cost=provider['cost_per_notification']
                )
            else:
                result = NotificationDeliveryResult(
                    notification_id=notification.id,
                    recipient_id=recipient.user_id,
                    channel=channel,
                    status=NotificationStatus.FAILED,
                    error_message="Delivery failed"
                )
            
            # Store result
            self.delivery_results.append(result)
            
            return result
            
        except Exception as e:
            return NotificationDeliveryResult(
                notification_id=notification.id,
                recipient_id=recipient.user_id,
                channel=channel,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
    
    async def _schedule_notification(self, notification: CollaborationNotification):
        """Schedule notification for later delivery"""
        notification.status = NotificationStatus.SCHEDULED
        self.notification_queue.append(notification)
    
    async def _schedule_notification_for_recipient(
        self,
        notification: CollaborationNotification,
        recipient: NotificationRecipient,
        channel: NotificationChannel
    ):
        """Schedule notification for specific recipient and channel"""
        # Implementation would add to scheduled queue with specific timing
        pass
    
    async def _update_analytics(
        self,
        notification: CollaborationNotification,
        delivery_results: List[NotificationDeliveryResult]
    ):
        """Update analytics with notification results"""
        self.analytics_data.total_sent += 1
        
        delivered_count = sum(1 for r in delivery_results if r.status == NotificationStatus.DELIVERED)
        self.analytics_data.total_delivered += delivered_count
        
        # Update rates
        if self.analytics_data.total_sent > 0:
            self.analytics_data.delivery_rate = self.analytics_data.total_delivered / self.analytics_data.total_sent
    
    async def _process_scheduled_notifications(self):
        """Background task to process scheduled notifications"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Find notifications ready to be sent
                ready_notifications = [
                    n for n in self.notification_queue
                    if n.scheduled_time and n.scheduled_time <= current_time
                ]
                
                # Process ready notifications
                for notification in ready_notifications:
                    await self._deliver_notification(notification)
                    self.notification_queue.remove(notification)
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = current_time
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error processing scheduled notifications: {str(e)}")
                await asyncio.sleep(60)  # Continue after error
