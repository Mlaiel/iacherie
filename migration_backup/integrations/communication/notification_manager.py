"""Notification Manager - Multi-Channel Notification System
=========================================================

Centralized notification management system supporting multiple channels
including email, SMS, push notifications, webhooks, and custom channels.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque

import httpx
import jinja2
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis


class NotificationChannel(Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"
    CUSTOM = "custom"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Notification delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    READ = "read"
    CLICKED = "clicked"


@dataclass
class NotificationTemplate:
    """Notification template configuration."""
    id: str
    name: str
    channel: NotificationChannel
    subject_template: Optional[str] = None
    body_template: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class NotificationRecipient:
    """Notification recipient information."""
    id: str
    channel: NotificationChannel
    address: str  # email, phone, device_token, webhook_url, etc.
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    """Notification instance."""
    id: str
    template_id: Optional[str]
    channel: NotificationChannel
    priority: NotificationPriority
    recipient: NotificationRecipient
    subject: Optional[str]
    body: str
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class NotificationBatch:
    """Batch notification for multiple recipients."""
    id: str
    template_id: str
    channel: NotificationChannel
    priority: NotificationPriority
    recipients: List[NotificationRecipient]
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    total_count: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    failed_count: int = 0


class NotificationManager:
    """Centralized notification management system."""
    
    def __init__(
        self,
        redis_url: str,
        database_session: AsyncSession,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Dependencies
        self.redis_url = redis_url
        self.redis_client = None
        self.db_session = database_session
        
        # Template engine
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=True
        )
        
        # Notification state
        self.templates: Dict[str, NotificationTemplate] = {}
        self.channel_providers: Dict[NotificationChannel, Any] = {}
        self.notification_queue = asyncio.Queue()
        self.active_notifications: Dict[str, Notification] = {}
        self.batch_notifications: Dict[str, NotificationBatch] = {}
        
        # Processing control
        self.processing_workers = []
        self.is_running = False
        self.worker_count = self.config.get('worker_count', 4)
        
        # Rate limiting per channel
        self.rate_limits: Dict[NotificationChannel, Dict[str, Any]] = {}
        self.rate_limit_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Metrics and monitoring
        self.metrics = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'total_read': 0,
            'total_clicked': 0,
            'channel_stats': defaultdict(lambda: {
                'sent': 0, 'delivered': 0, 'failed': 0
            }),
            'priority_stats': defaultdict(lambda: {
                'sent': 0, 'delivered': 0, 'failed': 0
            })
        }
        
        # Webhook callbacks for status updates
        self.status_webhooks: List[str] = []
        
    async def initialize(self):
        """Initialize the notification manager."""
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url)
        
        # Load notification templates from database
        await self._load_templates()
        
        # Setup rate limits
        self._setup_rate_limits()
        
        self.logger.info("Notification manager initialized")
    
    def register_channel_provider(self, channel: NotificationChannel, provider: Any):
        """Register channel-specific provider."""
        self.channel_providers[channel] = provider
        self.logger.info(f"Registered provider for channel: {channel.value}")
    
    def add_template(self, template: NotificationTemplate):
        """Add notification template."""
        self.templates[template.id] = template
        self.logger.info(f"Added notification template: {template.name}")
    
    def remove_template(self, template_id: str):
        """Remove notification template."""
        if template_id in self.templates:
            del self.templates[template_id]
            self.logger.info(f"Removed notification template: {template_id}")
    
    async def send_notification(
        self,
        template_id: Optional[str],
        channel: NotificationChannel,
        recipient: NotificationRecipient,
        variables: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None
    ) -> str:
        """Send single notification."""
        notification_id = str(uuid.uuid4())
        
        # Create notification object
        notification = Notification(
            id=notification_id,
            template_id=template_id,
            channel=channel,
            priority=priority,
            recipient=recipient,
            subject=subject,
            body=body or "",
            variables=variables or {},
            scheduled_at=scheduled_at
        )
        
        # Render notification content if template provided
        if template_id and template_id in self.templates:
            await self._render_notification(notification)
        
        # Validate notification
        self._validate_notification(notification)
        
        # Check rate limits
        if not await self._check_rate_limit(channel, recipient.address):
            notification.status = NotificationStatus.FAILED
            notification.error_message = "Rate limit exceeded"
            return notification_id
        
        # Queue for processing
        if scheduled_at and scheduled_at > datetime.now():
            # Schedule for later delivery
            await self._schedule_notification(notification)
        else:
            # Queue for immediate delivery
            await self.notification_queue.put(notification)
            notification.status = NotificationStatus.QUEUED
        
        self.active_notifications[notification_id] = notification
        
        self.logger.info(f"Queued notification {notification_id} for {channel.value}")
        return notification_id
    
    async def send_batch_notification(
        self,
        template_id: str,
        channel: NotificationChannel,
        recipients: List[NotificationRecipient],
        variables: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """Send batch notification to multiple recipients."""
        batch_id = str(uuid.uuid4())
        
        batch = NotificationBatch(
            id=batch_id,
            template_id=template_id,
            channel=channel,
            priority=priority,
            recipients=recipients,
            variables=variables or {},
            scheduled_at=scheduled_at,
            total_count=len(recipients)
        )
        
        self.batch_notifications[batch_id] = batch
        
        # Create individual notifications
        for recipient in recipients:
            await self.send_notification(
                template_id=template_id,
                channel=channel,
                recipient=recipient,
                variables=variables,
                priority=priority,
                scheduled_at=scheduled_at
            )
        
        self.logger.info(f"Queued batch notification {batch_id} for {len(recipients)} recipients")
        return batch_id
    
    async def start_processing(self):
        """Start notification processing workers."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._notification_worker(f"worker-{i}"))
            self.processing_workers.append(worker)
        
        # Start scheduled notification processor
        scheduler_task = asyncio.create_task(self._scheduled_notification_processor())
        self.processing_workers.append(scheduler_task)
        
        self.logger.info(f"Started {self.worker_count} notification workers")
    
    async def stop_processing(self):
        """Stop notification processing workers."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all workers
        for worker in self.processing_workers:
            worker.cancel()
        
        # Wait for workers to complete
        await asyncio.gather(*self.processing_workers, return_exceptions=True)
        self.processing_workers.clear()
        
        self.logger.info("Stopped notification processing")
    
    async def _notification_worker(self, worker_name: str):
        """Notification processing worker."""
        self.logger.info(f"Started notification worker: {worker_name}")
        
        while self.is_running:
            try:
                # Get notification from queue with timeout
                notification = await asyncio.wait_for(
                    self.notification_queue.get(), 
                    timeout=1.0
                )
                
                # Process notification
                await self._process_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_notification(self, notification: Notification):
        """Process individual notification."""
        try:
            notification.status = NotificationStatus.SENDING
            notification.sent_at = datetime.now()
            
            # Get channel provider
            provider = self.channel_providers.get(notification.channel)
            if not provider:
                raise ValueError(f"No provider for channel: {notification.channel.value}")
            
            # Send notification
            result = await self._send_via_provider(provider, notification)
            
            if result.get('success', False):
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.now()
                
                # Update metrics
                self.metrics['total_sent'] += 1
                self.metrics['total_delivered'] += 1
                self.metrics['channel_stats'][notification.channel]['sent'] += 1
                self.metrics['channel_stats'][notification.channel]['delivered'] += 1
                self.metrics['priority_stats'][notification.priority]['sent'] += 1
                self.metrics['priority_stats'][notification.priority]['delivered'] += 1
                
            else:
                raise Exception(result.get('error', 'Unknown error'))
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            
            # Retry if possible
            if notification.retry_count < notification.max_retries:
                notification.retry_count += 1
                notification.status = NotificationStatus.PENDING
                
                # Re-queue with exponential backoff
                delay = 2 ** notification.retry_count
                await asyncio.sleep(delay)
                await self.notification_queue.put(notification)
                
                self.logger.warning(
                    f"Retrying notification {notification.id} "
                    f"(attempt {notification.retry_count}/{notification.max_retries})"
                )
            else:
                # Update metrics
                self.metrics['total_failed'] += 1
                self.metrics['channel_stats'][notification.channel]['failed'] += 1
                self.metrics['priority_stats'][notification.priority]['failed'] += 1
                
                self.logger.error(f"Notification {notification.id} failed: {e}")
        
        # Update notification in storage
        await self._update_notification_status(notification)
        
        # Send webhook notification if configured
        await self._send_status_webhook(notification)
    
    async def _send_via_provider(self, provider: Any, notification: Notification) -> Dict[str, Any]:
        """Send notification via channel provider."""
        try:
            if hasattr(provider, 'send_notification'):
                return await provider.send_notification(
                    recipient=notification.recipient.address,
                    subject=notification.subject,
                    body=notification.body,
                    metadata=notification.metadata
                )
            else:
                raise ValueError("Provider does not support notification sending")
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _render_notification(self, notification: Notification):
        """Render notification content using template."""
        template = self.templates.get(notification.template_id)
        if not template:
            raise ValueError(f"Template not found: {notification.template_id}")
        
        # Prepare template context
        context = {
            'recipient': notification.recipient,
            'variables': notification.variables,
            'metadata': notification.metadata,
            'notification': notification
        }
        
        # Render subject if template has one
        if template.subject_template:
            subject_template = self.jinja_env.from_string(template.subject_template)
            notification.subject = subject_template.render(**context)
        
        # Render body
        body_template = self.jinja_env.from_string(template.body_template)
        notification.body = body_template.render(**context)
    
    def _validate_notification(self, notification: Notification):
        """Validate notification before sending."""
        if not notification.recipient.address:
            raise ValueError("Recipient address is required")
        
        if notification.channel == NotificationChannel.EMAIL:
            if '@' not in notification.recipient.address:
                raise ValueError("Invalid email address")
        elif notification.channel == NotificationChannel.SMS:
            if not notification.recipient.address.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                raise ValueError("Invalid phone number")
        elif notification.channel == NotificationChannel.WEBHOOK:
            if not notification.recipient.address.startswith(('http://', 'https://')):
                raise ValueError("Invalid webhook URL")
    
    async def _check_rate_limit(self, channel: NotificationChannel, address: str) -> bool:
        """Check if notification is within rate limits."""
        if channel not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[channel]
        limit_key = f"{channel.value}:{address}"
        window_duration = limit_config['window_seconds']
        max_requests = limit_config['max_requests']
        
        # Clean old entries
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=window_duration)
        
        window = self.rate_limit_windows[limit_key]
        while window and window[0] < cutoff_time:
            window.popleft()
        
        # Check if under limit
        if len(window) >= max_requests:
            return False
        
        # Add current request
        window.append(current_time)
        return True
    
    async def _schedule_notification(self, notification: Notification):
        """Schedule notification for future delivery."""
        # Store in Redis with expiration
        schedule_key = f"scheduled_notification:{notification.scheduled_at.timestamp()}:{notification.id}"
        notification_data = {
            'id': notification.id,
            'data': json.dumps(notification.__dict__, default=str)
        }
        
        # Set to expire shortly after scheduled time
        expire_seconds = int((notification.scheduled_at - datetime.now()).total_seconds()) + 3600
        await self.redis_client.setex(
            schedule_key,
            expire_seconds,
            json.dumps(notification_data)
        )
    
    async def _scheduled_notification_processor(self):
        """Process scheduled notifications."""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Get scheduled notifications from Redis
                pattern = "scheduled_notification:*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys:
                    try:
                        # Extract timestamp from key
                        timestamp_str = key.decode().split(':')[1]
                        scheduled_time = datetime.fromtimestamp(float(timestamp_str))
                        
                        # Check if it's time to send
                        if scheduled_time <= current_time:
                            # Get notification data
                            data = await self.redis_client.get(key)
                            if data:
                                notification_data = json.loads(data)
                                notification_dict = json.loads(notification_data['data'])
                                
                                # Recreate notification object
                                notification = Notification(**notification_dict)
                                
                                # Queue for immediate delivery
                                await self.notification_queue.put(notification)
                                
                                # Remove from scheduled storage
                                await self.redis_client.delete(key)
                    
                    except Exception as e:
                        self.logger.error(f"Error processing scheduled notification: {e}")
                
                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Scheduled processor error: {e}")
                await asyncio.sleep(30)
    
    def _setup_rate_limits(self):
        """Setup default rate limits for channels."""
        self.rate_limits = {
            NotificationChannel.EMAIL: {
                'max_requests': 100,
                'window_seconds': 3600  # 100 emails per hour
            },
            NotificationChannel.SMS: {
                'max_requests': 10,
                'window_seconds': 3600  # 10 SMS per hour
            },
            NotificationChannel.PUSH: {
                'max_requests': 1000,
                'window_seconds': 3600  # 1000 push notifications per hour
            },
            NotificationChannel.WEBHOOK: {
                'max_requests': 100,
                'window_seconds': 60  # 100 webhooks per minute
            }
        }
    
    async def _load_templates(self):
        """Load notification templates from database."""
        # This would typically load from database
        # For now, we'll initialize with empty templates
        pass
    
    async def _update_notification_status(self, notification: Notification):
        """Update notification status in persistent storage."""
        # Update in-memory store
        self.active_notifications[notification.id] = notification
        
        # Update in database (implementation depends on your database setup)
        # await self.db_session.merge(notification)
        # await self.db_session.commit()
    
    async def _send_status_webhook(self, notification: Notification):
        """Send webhook notification for status updates."""
        if not self.status_webhooks:
            return
        
        webhook_data = {
            'notification_id': notification.id,
            'status': notification.status.value,
            'channel': notification.channel.value,
            'recipient': notification.recipient.address,
            'timestamp': datetime.now().isoformat(),
            'error_message': notification.error_message
        }
        
        for webhook_url in self.status_webhooks:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(webhook_url, json=webhook_data, timeout=10.0)
            except Exception as e:
                self.logger.warning(f"Failed to send status webhook: {e}")
    
    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get notification status."""
        notification = self.active_notifications.get(notification_id)
        if not notification:
            return None
        
        return {
            'id': notification.id,
            'status': notification.status.value,
            'channel': notification.channel.value,
            'priority': notification.priority.value,
            'created_at': notification.created_at.isoformat(),
            'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
            'delivered_at': notification.delivered_at.isoformat() if notification.delivered_at else None,
            'read_at': notification.read_at.isoformat() if notification.read_at else None,
            'clicked_at': notification.clicked_at.isoformat() if notification.clicked_at else None,
            'error_message': notification.error_message,
            'retry_count': notification.retry_count
        }
    
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch notification status."""
        batch = self.batch_notifications.get(batch_id)
        if not batch:
            return None
        
        return {
            'id': batch.id,
            'template_id': batch.template_id,
            'channel': batch.channel.value,
            'priority': batch.priority.value,
            'total_count': batch.total_count,
            'sent_count': batch.sent_count,
            'delivered_count': batch.delivered_count,
            'failed_count': batch.failed_count,
            'created_at': batch.created_at.isoformat(),
            'scheduled_at': batch.scheduled_at.isoformat() if batch.scheduled_at else None
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get notification metrics."""
        return {
            'total_notifications': {
                'sent': self.metrics['total_sent'],
                'delivered': self.metrics['total_delivered'],
                'failed': self.metrics['total_failed'],
                'read': self.metrics['total_read'],
                'clicked': self.metrics['total_clicked']
            },
            'by_channel': dict(self.metrics['channel_stats']),
            'by_priority': dict(self.metrics['priority_stats']),
            'queue_size': self.notification_queue.qsize(),
            'active_notifications': len(self.active_notifications),
            'batch_notifications': len(self.batch_notifications)
        }
    
    def add_status_webhook(self, webhook_url: str):
        """Add webhook URL for status updates."""
        if webhook_url not in self.status_webhooks:
            self.status_webhooks.append(webhook_url)
    
    def remove_status_webhook(self, webhook_url: str):
        """Remove webhook URL."""
        if webhook_url in self.status_webhooks:
            self.status_webhooks.remove(webhook_url)


# Example usage
if __name__ == "__main__":
    async def main():
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        # Initialize database session
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session = sessionmaker(engine, class_=AsyncSession)
        
        async with async_session() as session:
            # Initialize notification manager
            manager = NotificationManager(
                redis_url="redis://localhost:6379",
                database_session=session
            )
            
            await manager.initialize()
            
            # Create notification template
            template = NotificationTemplate(
                id="welcome_email",
                name="Welcome Email",
                channel=NotificationChannel.EMAIL,
                subject_template="Welcome to {{ variables.platform_name }}!",
                body_template="Hello {{ recipient.address }}, welcome to our platform!"
            )
            
            manager.add_template(template)
            
            # Create recipient
            recipient = NotificationRecipient(
                id="user_123",
                channel=NotificationChannel.EMAIL,
                address="user@example.com"
            )
            
            # Send notification
            notification_id = await manager.send_notification(
                template_id="welcome_email",
                channel=NotificationChannel.EMAIL,
                recipient=recipient,
                variables={"platform_name": "Ainflue"}
            )
            
            print(f"Notification queued: {notification_id}")
            
            # Start processing
            await manager.start_processing()
            
            # Wait a bit for processing
            await asyncio.sleep(5)
            
            # Check status
            status = await manager.get_notification_status(notification_id)
            print(f"Notification status: {status}")
            
            # Stop processing
            await manager.stop_processing()
    
    asyncio.run(main())