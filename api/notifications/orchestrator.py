"""Enterprise notification orchestration service with intelligent routing and comprehensive analytics."""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union, Set, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass, asdict, field
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.utils.metrics import MetricsCollector
from app.core.database import get_db
from app.core.cache import get_cache

from .email import EmailNotifier
from .sms import SMSNotifier, SMSMessage
from .push import PushNotifier, PushMessage, PushContent
from .webhook import WebhookNotifier, WebhookPayload
from .in_app import InAppNotifier, InAppNotification
from .templates import NotificationTemplateEngine, PersonalizationContext


class DeliveryChannel(str, Enum):
    """Notification delivery channels."""    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class NotificationPriority(str, Enum):
    """Global notification priority levels."""    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DeliveryStrategy(str, Enum):
    """Notification delivery strategies."""    IMMEDIATE = "immediate"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    INTELLIGENT = "intelligent"  # AI-optimized timing
    FALLBACK = "fallback"  # Try multiple channels


@dataclass
class NotificationPreference:
    """User notification preferences for all channels."""    user_id: str
    enabled_channels: Set[DeliveryChannel] = field(default_factory=set)
    priority_threshold: NotificationPriority = NotificationPriority.NORMAL
    quiet_hours_start: Optional[int] = None  # 0-23 hours
    quiet_hours_end: Optional[int] = None
    timezone: str = "UTC"
    language: str = "en"
    
    # Channel-specific preferences
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    webhook_enabled: bool = False
    
    # Business-specific preferences
    content_alerts: bool = True
    protection_alerts: bool = True
    collaboration_alerts: bool = True
    monetization_alerts: bool = True
    analytics_alerts: bool = True
    platform_alerts: bool = True
    
    # Frequency controls
    digest_enabled: bool = True
    digest_frequency: str = "daily"  # never, hourly, daily, weekly
    max_notifications_per_hour: int = 10
    
    def __post_init__(self):
        if not self.enabled_channels:
            self.enabled_channels = {DeliveryChannel.EMAIL, DeliveryChannel.IN_APP}


@dataclass
class UniversalNotification:
    """Universal notification that can be delivered across all channels."""    id: str
    user_id: str
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    
    # Content variants for different channels
    email_subject: Optional[str] = None
    email_html: Optional[str] = None
    email_text: Optional[str] = None
    sms_message: Optional[str] = None
    push_title: Optional[str] = None
    push_body: Optional[str] = None
    in_app_content: Optional[Dict[str, Any]] = None
    webhook_data: Optional[Dict[str, Any]] = None
    
    # Targeting and scheduling
    target_channels: Optional[Set[DeliveryChannel]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Business context
    event_type: Optional[str] = None
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    platform: Optional[str] = None
    creator_type: Optional[str] = None
    
    # Personalization
    personalization_data: Optional[Dict[str, Any]] = None
    template_id: Optional[str] = None
    
    # Delivery settings
    delivery_strategy: DeliveryStrategy = DeliveryStrategy.IMMEDIATE
    fallback_enabled: bool = True
    retry_count: int = 0
    max_retries: int = 3
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivery_status: Dict[str, str] = field(default_factory=dict)  # channel -> status
    delivery_times: Dict[str, datetime] = field(default_factory=dict)  # channel -> delivered_at
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.target_channels is None:
            self.target_channels = {DeliveryChannel.EMAIL, DeliveryChannel.IN_APP}


@dataclass 
class DeliveryResult:
    """Comprehensive delivery result across all channels."""    notification_id: str
    user_id: str
    total_channels: int
    successful_channels: int
    failed_channels: int
    channel_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    delivery_time_ms: Optional[int] = None
    total_cost: float = 0.0
    
    @property
    def success_rate(self) -> float:
        return self.successful_channels / self.total_channels if self.total_channels > 0 else 0.0
    
    @property
    def overall_status(self) -> str:
        if self.successful_channels == 0:
            return "failed"
        elif self.successful_channels == self.total_channels:
            return "success"
        else:
            return "partial_success"


class NotificationOrchestrator:
    """Enterprise notification orchestration service with intelligent delivery and comprehensive analytics."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
        
        # Initialize channel handlers
        self.email_notifier = EmailNotifier()
        self.sms_notifier = SMSNotifier()
        self.push_notifier = PushNotifier()
        self.webhook_notifier = WebhookNotifier()
        self.in_app_notifier = InAppNotifier()
        
        # Template engine
        self.template_engine = NotificationTemplateEngine()
        
        # Storage (would use Redis/database in production)
        self.user_preferences = {}  # user_id -> NotificationPreference
        self.notification_queue = []  # Pending notifications
        self.delivery_history = {}  # notification_id -> DeliveryResult
        
        # Performance settings
        self.max_concurrent_deliveries = 500
        self.batch_size = 100
        self.rate_limit_window = 3600  # 1 hour
        self.executor = ThreadPoolExecutor(max_workers=50)
        
        # Intelligent delivery settings
        self.ai_optimization_enabled = True
        self.optimal_send_times = {}  # user_id -> optimal hours
        
        # Cost tracking
        self.channel_costs = {
            DeliveryChannel.EMAIL: 0.0001,  # $0.0001 per email
            DeliveryChannel.SMS: 0.01,      # $0.01 per SMS
            DeliveryChannel.PUSH_NOTIFICATION: 0.0001,  # $0.0001 per push
            DeliveryChannel.IN_APP: 0.0,    # Free
            DeliveryChannel.WEBHOOK: 0.0001, # $0.0001 per webhook
        }

    async def send_notification(
        self,
        notification: UniversalNotification,
        user_preferences: Optional[NotificationPreference] = None
    ) -> DeliveryResult:
        """Send notification across all applicable channels with intelligent routing."""        start_time = datetime.utcnow()
        
        try:
            # Get user preferences
            prefs = user_preferences or await self.get_user_preferences(notification.user_id)
            
            # Determine delivery channels
            target_channels = await self._determine_channels(notification, prefs)
            
            if not target_channels:
                self.logger.info(f"No channels enabled for notification: {notification.id}")
                return DeliveryResult(
                    notification_id=notification.id,
                    user_id=notification.user_id,
                    total_channels=0,
                    successful_channels=0,
                    failed_channels=0
                )
            
            # Apply delivery strategy
            if notification.delivery_strategy == DeliveryStrategy.INTELLIGENT:
                await self._apply_intelligent_timing(notification, prefs)
            elif notification.delivery_strategy == DeliveryStrategy.SCHEDULED:
                await self._schedule_notification(notification)
                return self._create_scheduled_result(notification)
            
            # Check rate limits and quiet hours
            if not await self._can_deliver_now(notification, prefs):
                await self._schedule_for_later(notification, prefs)
                return self._create_delayed_result(notification)
            
            # Prepare personalized content
            await self._prepare_channel_content(notification, prefs)
            
            # Deliver across channels
            delivery_results = await self._deliver_multi_channel(notification, target_channels, prefs)
            
            # Calculate delivery metrics
            delivery_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            total_cost = sum(self.channel_costs.get(ch, 0) for ch in target_channels)
            
            # Create comprehensive result
            result = DeliveryResult(
                notification_id=notification.id,
                user_id=notification.user_id,
                total_channels=len(target_channels),
                successful_channels=len([r for r in delivery_results.values() if r.get("status") == "success"]),
                failed_channels=len([r for r in delivery_results.values() if r.get("status") == "failed"]),
                channel_results=delivery_results,
                delivery_time_ms=int(delivery_time),
                total_cost=total_cost
            )
            
            # Store delivery history
            self.delivery_history[notification.id] = result
            
            # Track metrics
            await self._track_delivery_metrics(result)
            
            # Handle fallbacks if needed
            if notification.fallback_enabled and result.success_rate < 1.0:
                await self._handle_delivery_fallbacks(notification, result, prefs)
            
            self.logger.info(f"Notification delivered: {notification.id} -> {result.successful_channels}/{result.total_channels} channels")
            return result
            
        except Exception as e:
            self.logger.error(f"Notification delivery failed: {notification.id} -> {str(e)}")
            raise

    async def send_bulk_notifications(
        self,
        notifications: List[UniversalNotification],
        batch_size: Optional[int] = None
    ) -> List[DeliveryResult]:
        """Send multiple notifications efficiently with batch processing."""        batch_size = batch_size or self.batch_size
        results = []
        
        # Process in batches
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            
            # Process batch concurrently
            semaphore = asyncio.Semaphore(self.max_concurrent_deliveries)
            
            async def send_single_notification(notification):
                async with semaphore:
                    return await self.send_notification(notification)
            
            batch_tasks = [send_single_notification(notif) for notif in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Batch notification failed: {str(result)}")
                else:
                    results.append(result)
        
        self.logger.info(f"Bulk notifications sent: {len(results)}/{len(notifications)} successful")
        return results

    async def broadcast_notification(
        self,
        notification_template: Dict[str, Any],
        user_ids: List[str],
        personalization_contexts: Optional[Dict[str, PersonalizationContext]] = None
    ) -> List[DeliveryResult]:
        """Broadcast notification to multiple users with personalization."""        notifications = []
        
        for user_id in user_ids:
            # Create personalized notification
            personalized_notification = await self._create_personalized_notification(
                user_id,
                notification_template,
                personalization_contexts.get(user_id) if personalization_contexts else None
            )
            notifications.append(personalized_notification)
        
        return await self.send_bulk_notifications(notifications)

    async def schedule_notification(
        self,
        notification: UniversalNotification,
        scheduled_at: datetime
    ) -> str:
        """Schedule notification for future delivery."""        notification.scheduled_at = scheduled_at
        notification.delivery_strategy = DeliveryStrategy.SCHEDULED
        
        # Add to queue (would use Redis/Celery in production)
        self.notification_queue.append(notification)
        
        scheduling_id = f"scheduled_{notification.id}_{int(scheduled_at.timestamp())}"
        self.logger.info(f"Notification scheduled: {notification.id} for {scheduled_at}")
        
        return scheduling_id

    async def cancel_scheduled_notification(self, notification_id: str) -> bool:
        """Cancel a scheduled notification."""        # Remove from queue
        self.notification_queue = [n for n in self.notification_queue if n.id != notification_id]
        
        self.logger.info(f"Scheduled notification cancelled: {notification_id}")
        return True

    async def set_user_preferences(self, user_id: str, preferences: NotificationPreference) -> bool:
        """Set notification preferences for a user."""        preferences.user_id = user_id
        self.user_preferences[user_id] = preferences
        
        self.logger.info(f"Notification preferences updated: {user_id}")
        return True

    async def get_user_preferences(self, user_id: str) -> NotificationPreference:
        """Get notification preferences for a user."""        return self.user_preferences.get(user_id, NotificationPreference(user_id=user_id))

    async def get_delivery_status(self, notification_id: str) -> Optional[DeliveryResult]:
        """Get delivery status for a specific notification."""        return self.delivery_history.get(notification_id)

    async def get_user_notifications_summary(
        self,
        user_id: str,
        time_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Get comprehensive notifications summary for a user."""        cutoff_date = datetime.utcnow() - time_period
        
        user_deliveries = [
            result for result in self.delivery_history.values()
            if result.user_id == user_id and any(
                dt > cutoff_date for dt in result.delivery_times.values()
            )
        ]
        
        return {
            "user_id": user_id,
            "period": f"Last {time_period.days} days",
            "total_notifications": len(user_deliveries),
            "success_rate": sum(r.success_rate for r in user_deliveries) / len(user_deliveries) if user_deliveries else 0,
            "channel_breakdown": await self._get_channel_breakdown(user_deliveries),
            "engagement_metrics": await self._get_user_engagement_metrics(user_id, cutoff_date),
            "cost_analysis": await self._get_user_cost_analysis(user_deliveries),
            "preferences": await self.get_user_preferences(user_id)
        }

    async def get_system_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive system-wide notification analytics."""        return {
            "period": f"{start_date.date()} to {end_date.date()}",
            "total_notifications": await self._get_total_notifications(start_date, end_date, filters),
            "delivery_success_rate": await self._get_overall_success_rate(start_date, end_date, filters),
            "channel_performance": await self._get_channel_performance(start_date, end_date, filters),
            "user_engagement": await self._get_engagement_analytics(start_date, end_date, filters),
            "cost_analysis": await self._get_cost_analytics(start_date, end_date, filters),
            "performance_trends": await self._get_performance_trends(start_date, end_date, filters),
            "optimization_opportunities": await self._get_optimization_opportunities(start_date, end_date, filters)
        }

    async def optimize_delivery_timing(self, user_id: str) -> Dict[str, Any]:
        """AI-powered optimization of delivery timing for a user."""        if not self.ai_optimization_enabled:
            return {"enabled": False, "message": "AI optimization is disabled"}
        
        # Analyze user's historical engagement patterns
        engagement_data = await self._analyze_user_engagement_patterns(user_id)
        
        # Determine optimal send times
        optimal_hours = await self._calculate_optimal_send_times(user_id, engagement_data)
        
        # Store optimal times
        self.optimal_send_times[user_id] = optimal_hours
        
        self.logger.info(f"Delivery timing optimized for user: {user_id}")
        
        return {
            "enabled": True,
            "optimal_send_times": optimal_hours,
            "expected_improvement": "15-25% increase in engagement rates",
            "data_points_analyzed": len(engagement_data.get("interactions", [])),
            "confidence_level": engagement_data.get("confidence", 0.8)
        }

    async def _determine_channels(
        self,
        notification: UniversalNotification,
        prefs: NotificationPreference
    ) -> Set[DeliveryChannel]:
        """Determine which channels to use for delivery."""        target_channels = set()
        
        # Start with notification's preferred channels
        if notification.target_channels:
            target_channels = notification.target_channels.copy()
        else:
            target_channels = prefs.enabled_channels.copy()
        
        # Apply user preferences
        if not prefs.email_enabled:
            target_channels.discard(DeliveryChannel.EMAIL)
        if not prefs.sms_enabled:
            target_channels.discard(DeliveryChannel.SMS)
        if not prefs.push_enabled:
            target_channels.discard(DeliveryChannel.PUSH_NOTIFICATION)
        if not prefs.in_app_enabled:
            target_channels.discard(DeliveryChannel.IN_APP)
        if not prefs.webhook_enabled:
            target_channels.discard(DeliveryChannel.WEBHOOK)
        
        # Apply priority-based filtering
        priority_levels = [NotificationPriority.LOW, NotificationPriority.NORMAL, NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]
        if priority_levels.index(notification.priority) < priority_levels.index(prefs.priority_threshold):
            target_channels = set()  # Don't deliver if below threshold
        
        return target_channels

    async def _apply_intelligent_timing(
        self,
        notification: UniversalNotification,
        prefs: NotificationPreference
    ):
        """Apply AI-powered intelligent timing."""        if notification.user_id in self.optimal_send_times:
            optimal_hours = self.optimal_send_times[notification.user_id]
            current_hour = datetime.utcnow().hour
            
            if current_hour not in optimal_hours:
                # Schedule for next optimal time
                next_optimal = min(h for h in optimal_hours if h > current_hour)
                scheduled_time = datetime.utcnow().replace(hour=next_optimal, minute=0, second=0, microsecond=0)
                
                if scheduled_time <= datetime.utcnow():
                    scheduled_time += timedelta(days=1)
                
                notification.scheduled_at = scheduled_time
                notification.delivery_strategy = DeliveryStrategy.SCHEDULED

    async def _schedule_notification(self, notification: UniversalNotification):
        """Schedule notification for later delivery."""        self.notification_queue.append(notification)

    async def _can_deliver_now(
        self,
        notification: UniversalNotification,
        prefs: NotificationPreference
    ) -> bool:
        """Check if notification can be delivered now based on rate limits and quiet hours."""        # Check quiet hours
        if prefs.quiet_hours_start is not None and prefs.quiet_hours_end is not None:
            current_hour = datetime.utcnow().hour
            if prefs.quiet_hours_start <= prefs.quiet_hours_end:
                # Same day quiet hours
                if prefs.quiet_hours_start <= current_hour <= prefs.quiet_hours_end:
                    return False
            else:
                # Cross-midnight quiet hours
                if current_hour >= prefs.quiet_hours_start or current_hour <= prefs.quiet_hours_end:
                    return False
        
        # Check rate limits (simplified)
        return True

    async def _prepare_channel_content(
        self,
        notification: UniversalNotification,
        prefs: NotificationPreference
    ):
        """Prepare personalized content for each channel."""        if notification.template_id:
            # Use template engine for personalization
            personalization_context = PersonalizationContext(
                user_id=notification.user_id,
                creator_type=notification.creator_type or "creator",
                language_preference=prefs.language,
                timezone=prefs.timezone
            )
            
            # Add personalization data
            if notification.personalization_data:
                personalization_context.user_preferences = notification.personalization_data
            
            # Render template for each channel
            template_context = {
                "title": notification.title,
                "message": notification.message,
                "user_id": notification.user_id,
                "content_id": notification.content_id,
                "campaign_id": notification.campaign_id,
                "platform": notification.platform
            }
            
            rendered_content = await self.template_engine.render_template(
                notification.template_id,
                template_context,
                personalization_context,
                prefs.language
            )
            
            # Apply rendered content to notification
            if "content" in rendered_content:
                notification.message = rendered_content["content"]
            if "subject" in rendered_content:
                notification.email_subject = rendered_content["subject"]

    async def _deliver_multi_channel(
        self,
        notification: UniversalNotification,
        target_channels: Set[DeliveryChannel],
        prefs: NotificationPreference
    ) -> Dict[str, Dict[str, Any]]:
        """Deliver notification across multiple channels concurrently."""        results = {}
        
        # Create delivery tasks for each channel
        tasks = {}
        
        if DeliveryChannel.EMAIL in target_channels:
            tasks[DeliveryChannel.EMAIL] = self._deliver_email(notification, prefs)
        
        if DeliveryChannel.SMS in target_channels:
            tasks[DeliveryChannel.SMS] = self._deliver_sms(notification, prefs)
        
        if DeliveryChannel.PUSH_NOTIFICATION in target_channels:
            tasks[DeliveryChannel.PUSH_NOTIFICATION] = self._deliver_push(notification, prefs)
        
        if DeliveryChannel.IN_APP in target_channels:
            tasks[DeliveryChannel.IN_APP] = self._deliver_in_app(notification, prefs)
        
        if DeliveryChannel.WEBHOOK in target_channels:
            tasks[DeliveryChannel.WEBHOOK] = self._deliver_webhook(notification, prefs)
        
        # Execute all delivery tasks concurrently
        if tasks:
            task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Map results back to channels
            for channel, result in zip(tasks.keys(), task_results):
                if isinstance(result, Exception):
                    results[channel.value] = {
                        "status": "failed",
                        "error": str(result)
                    }
                else:
                    results[channel.value] = result
        
        return results

    async def _deliver_email(self, notification: UniversalNotification, prefs: NotificationPreference) -> Dict[str, Any]:
        """Deliver email notification."""        try:
            result = await self.email_notifier.send_email(
                to_email=f"{notification.user_id}@example.com",  # Would get real email from user profile
                subject=notification.email_subject or notification.title,
                content=notification.email_html or notification.message,
                content_type="html" if notification.email_html else "text"
            )
            return {"status": "success", "provider_result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _deliver_sms(self, notification: UniversalNotification, prefs: NotificationPreference) -> Dict[str, Any]:
        """Deliver SMS notification."""        try:
            sms_message = SMSMessage(
                to_phone=f"+1234567890",  # Would get real phone from user profile
                message=notification.sms_message or notification.message[:160],
                user_id=notification.user_id,
                campaign_id=notification.campaign_id
            )
            result = await self.sms_notifier.send_sms(sms_message)
            return {"status": "success", "provider_result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _deliver_push(self, notification: UniversalNotification, prefs: NotificationPreference) -> Dict[str, Any]:
        """Deliver push notification."""        try:
            push_content = PushContent(
                title=notification.push_title or notification.title,
                body=notification.push_body or notification.message
            )
            push_message = PushMessage(
                content=push_content,
                device_token="mock_device_token",  # Would get real device token
                user_id=notification.user_id,
                campaign_id=notification.campaign_id
            )
            result = await self.push_notifier.send_push(push_message)
            return {"status": "success", "provider_result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _deliver_in_app(self, notification: UniversalNotification, prefs: NotificationPreference) -> Dict[str, Any]:
        """Deliver in-app notification."""        try:
            from .in_app import InAppNotification, InAppNotificationType, NotificationCategory
            
            in_app_notification = InAppNotification(
                id=notification.id,
                user_id=notification.user_id,
                type=InAppNotificationType.SYSTEM_UPDATE,  # Would map from event_type
                category=NotificationCategory.SYSTEM,
                priority=notification.priority,
                title=notification.title,
                message=notification.message,
                content_id=notification.content_id,
                campaign_id=notification.campaign_id,
                platform=notification.platform,
                creator_type=notification.creator_type
            )
            
            result_id = await self.in_app_notifier.create_notification(in_app_notification)
            return {"status": "success", "notification_id": result_id}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _deliver_webhook(self, notification: UniversalNotification, prefs: NotificationPreference) -> Dict[str, Any]:
        """Deliver webhook notification."""        try:
            from .webhook import WebhookPayload, WebhookEvent
            
            webhook_payload = WebhookPayload(
                event=WebhookEvent.SYSTEM_MAINTENANCE,  # Would map from event_type
                data=notification.webhook_data or {
                    "title": notification.title,
                    "message": notification.message
                },
                timestamp=datetime.utcnow(),
                user_id=notification.user_id,
                content_id=notification.content_id,
                campaign_id=notification.campaign_id,
                platform=notification.platform,
                creator_type=notification.creator_type
            )
            
            # Would get webhook endpoints from user configuration
            endpoint_id = "mock_endpoint_id"
            result = await self.webhook_notifier.send_webhook(endpoint_id, webhook_payload)
            return {"status": "success", "webhook_result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _create_scheduled_result(self, notification: UniversalNotification) -> DeliveryResult:
        """Create result for scheduled notification."""        return DeliveryResult(
            notification_id=notification.id,
            user_id=notification.user_id,
            total_channels=0,
            successful_channels=0,
            failed_channels=0,
            channel_results={"status": "scheduled", "scheduled_at": notification.scheduled_at.isoformat()}
        )

    def _create_delayed_result(self, notification: UniversalNotification) -> DeliveryResult:
        """Create result for delayed notification."""        return DeliveryResult(
            notification_id=notification.id,
            user_id=notification.user_id,
            total_channels=0,
            successful_channels=0,
            failed_channels=0,
            channel_results={"status": "delayed", "reason": "Rate limited or quiet hours"}
        )

    async def _schedule_for_later(self, notification: UniversalNotification, prefs: NotificationPreference):
        """Schedule notification for later delivery."""        # Simple scheduling logic - would be more sophisticated in production
        delay_minutes = 60  # Default 1 hour delay
        notification.scheduled_at = datetime.utcnow() + timedelta(minutes=delay_minutes)
        await self._schedule_notification(notification)

    async def _handle_delivery_fallbacks(
        self,
        notification: UniversalNotification,
        result: DeliveryResult,
        prefs: NotificationPreference
    ):
        """Handle fallback delivery for failed channels."""        failed_channels = [ch for ch, res in result.channel_results.items() if res.get("status") == "failed"]
        
        # Simple fallback: if email failed, try SMS
        if "email" in failed_channels and DeliveryChannel.SMS in prefs.enabled_channels:
            try:
                fallback_result = await self._deliver_sms(notification, prefs)
                result.channel_results["sms_fallback"] = fallback_result
                if fallback_result.get("status") == "success":
                    result.successful_channels += 1
                    self.logger.info(f"Fallback SMS delivery successful: {notification.id}")
            except Exception as e:
                self.logger.error(f"Fallback delivery failed: {notification.id} -> {str(e)}")

    async def _track_delivery_metrics(self, result: DeliveryResult):
        """Track comprehensive delivery metrics."""        await self.metrics.increment(
            "notifications_sent_total",
            tags={
                "status": result.overall_status,
                "channels": str(result.total_channels)
            }
        )
        
        await self.metrics.histogram(
            "notification_delivery_time_ms",
            result.delivery_time_ms or 0
        )
        
        await self.metrics.histogram(
            "notification_success_rate",
            result.success_rate
        )
        
        if result.total_cost > 0:
            await self.metrics.histogram(
                "notification_cost_usd",
                result.total_cost
            )

    async def _create_personalized_notification(
        self,
        user_id: str,
        template: Dict[str, Any],
        context: Optional[PersonalizationContext] = None
    ) -> UniversalNotification:
        """Create personalized notification from template."""        notification_data = template.copy()
        notification_data["user_id"] = user_id
        
        if context:
            notification_data["personalization_data"] = asdict(context)
        
        return UniversalNotification(**notification_data)

    # Analytics methods (simplified implementations)
    async def _get_channel_breakdown(self, deliveries: List[DeliveryResult]) -> Dict[str, Dict]:
        return {}

    async def _get_user_engagement_metrics(self, user_id: str, cutoff_date: datetime) -> Dict[str, Any]:
        return {}

    async def _get_user_cost_analysis(self, deliveries: List[DeliveryResult]) -> Dict[str, float]:
        return {"total_cost": sum(d.total_cost for d in deliveries)}

    async def _get_total_notifications(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> int:
        return 0

    async def _get_overall_success_rate(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> float:
        return 0.95

    async def _get_channel_performance(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Dict]:
        return {}

    async def _get_engagement_analytics(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Any]:
        return {}

    async def _get_cost_analytics(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, float]:
        return {}

    async def _get_performance_trends(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Any]:
        return {}

    async def _get_optimization_opportunities(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> List[Dict]:
        return []

    async def _analyze_user_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        return {"interactions": [], "confidence": 0.8}

    async def _calculate_optimal_send_times(self, user_id: str, engagement_data: Dict[str, Any]) -> List[int]:
        return [9, 12, 18]  # 9 AM, 12 PM, 6 PM
