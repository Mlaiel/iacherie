"""Advanced Notification Agent - Core Intelligent Notification Management System

This module provides comprehensive notification management for IA Influencer Agent platform,
handling multi-format content creator notifications, AI-driven content protection alerts,
collaboration matching notifications, and monetization opportunities.

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
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.base_agent import BaseAgent
from ...models.notification_models import (
    NotificationModel, NotificationStatus, NotificationPriority,
    NotificationChannel, NotificationTemplate, AlertModel
)
from ...business.notification_business import NotificationBusinessLogic
from ...security.notification_security import NotificationSecurityManager
from ...integrations.messaging_integrations import MessagingIntegrationManager
from ...monitoring.notification_monitoring import NotificationMonitoringService


class NotificationType(Enum):
    """Comprehensive notification types for IA Influencer platform"""    CONTENT_UPLOAD = "content_upload"
    AI_PROTECTION_ALERT = "ai_protection_alert"
    COLLABORATION_MATCH = "collaboration_match"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION_STATUS = "distribution_status"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    SECURITY_ALERT = "security_alert"
    PLATFORM_UPDATE = "platform_update"
    ANALYTICS_REPORT = "analytics_report"
    PAYMENT_NOTIFICATION = "payment_notification"
    USER_ENGAGEMENT = "user_engagement"


class NotificationDeliveryStatus(Enum):
    """Notification delivery status tracking"""    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


@dataclass
class NotificationContext:
    """Rich context information for notifications"""    user_id: str
    content_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    collaboration_data: Dict[str, Any] = field(default_factory=dict)
    monetization_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationConfiguration:
    """Advanced notification configuration"""    enabled_channels: List[NotificationChannel]
    priority_rules: Dict[str, NotificationPriority]
    template_preferences: Dict[str, str]
    delivery_preferences: Dict[str, Any]
    frequency_limits: Dict[str, int]
    ai_personalization_enabled: bool = True
    real_time_enabled: bool = True
    batch_processing_enabled: bool = True


class NotificationAgent(BaseAgent):
    """    Advanced AI-powered notification agent for comprehensive communication management
    
    Handles all notification aspects of the IA Influencer platform:
    - Multi-format content upload notifications
    - AI content protection alerts
    - Collaboration matching notifications
    - Monetization opportunity alerts
    - SEO optimization notifications
    - Multi-platform distribution status
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Core components initialization
        self._initialize_core_components()
        
        # Business logic integration
        self.business_logic = NotificationBusinessLogic(config.get('business_config', {}))
        
        # Security layer
        self.security_manager = NotificationSecurityManager(config.get('security_config', {}))
        
        # External integrations
        self.integration_manager = MessagingIntegrationManager(config.get('integration_config', {}))
        
        # Monitoring service
        self.monitoring = NotificationMonitoringService(config.get('monitoring_config', {}))
        
        # AI-driven personalization engine
        self.ai_personalizer = self._initialize_ai_personalizer()
        
        # Notification queue and processing
        self.notification_queue = asyncio.Queue()
        self.batch_queue = asyncio.Queue()
        self.processing_tasks = []
        
        # Performance metrics
        self.performance_metrics = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'average_delivery_time': 0.0,
            'channel_performance': {}
        }
        
    def _initialize_core_components(self):
        """Initialize core notification components"""        self.notification_storage = {}
        self.user_preferences = {}
        self.template_cache = {}
        self.delivery_history = {}
        self.retry_queue = asyncio.Queue()
        
    def _initialize_ai_personalizer(self):
        """Initialize AI-driven notification personalization"""        from ...ai.personalization.notification_personalizer import NotificationPersonalizer
        return NotificationPersonalizer(self.config.get('ai_personalization', {}))
        
    async def start_agent(self):
        """Start the notification agent with all processing tasks"""        try:
            self.logger.info("Starting NotificationAgent with advanced processing capabilities")
            
            # Start core processing tasks
            self.processing_tasks.extend([
                asyncio.create_task(self._process_notification_queue()),
                asyncio.create_task(self._process_batch_queue()),
                asyncio.create_task(self._retry_failed_notifications()),
                asyncio.create_task(self._cleanup_expired_notifications()),
                asyncio.create_task(self._generate_analytics_reports())
            ])
            
            # Initialize monitoring
            await self.monitoring.start_monitoring()
            
            self.logger.info("NotificationAgent started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start NotificationAgent: {str(e)}")
            return False
            
    async def stop_agent(self):
        """Gracefully stop the notification agent"""        try:
            self.logger.info("Stopping NotificationAgent")
            
            # Cancel all processing tasks
            for task in self.processing_tasks:
                task.cancel()
                
            # Process remaining notifications
            await self._process_remaining_notifications()
            
            # Stop monitoring
            await self.monitoring.stop_monitoring()
            
            self.logger.info("NotificationAgent stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping NotificationAgent: {str(e)}")
            return False
            
    async def send_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext,
        channels: Optional[List[NotificationChannel]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        template_override: Optional[str] = None
    ) -> str:
        """        Send intelligent notification with AI-driven personalization
        
        Args:
            notification_type: Type of notification to send
            context: Rich context information
            channels: Target delivery channels
            priority: Notification priority level
            template_override: Custom template to use
            
        Returns:
            notification_id: Unique identifier for tracking
        """        try:
            # Generate unique notification ID
            notification_id = str(uuid.uuid4())
            
            # Security validation
            if not await self.security_manager.validate_notification_request(context):
                raise ValueError("Security validation failed for notification request")
                
            # Business logic validation
            if not await self.business_logic.validate_notification_context(notification_type, context):
                raise ValueError("Business logic validation failed for notification")
                
            # AI-driven personalization
            personalized_content = await self.ai_personalizer.personalize_notification(
                notification_type, context, template_override
            )
            
            # Determine optimal channels
            optimal_channels = channels or await self._determine_optimal_channels(
                context.user_id, notification_type, priority
            )
            
            # Create notification model
            notification = NotificationModel(
                id=notification_id,
                type=notification_type.value,
                user_id=context.user_id,
                channels=optimal_channels,
                priority=priority,
                content=personalized_content,
                context=context,
                created_at=datetime.utcnow(),
                status=NotificationStatus.PENDING
            )
            
            # Queue for processing
            await self.notification_queue.put(notification)
            
            # Update metrics
            await self.monitoring.record_notification_created(notification_id, notification_type)
            
            self.logger.info(f"Notification queued successfully: {notification_id}")
            return notification_id
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            await self.monitoring.record_notification_error(str(e))
            raise
            
    async def send_bulk_notifications(
        self,
        notifications: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> List[str]:
        """        Send bulk notifications efficiently with batch processing
        
        Args:
            notifications: List of notification configurations
            batch_size: Size of processing batches
            
        Returns:
            List of notification IDs
        """        try:
            notification_ids = []
            
            # Process in batches
            for i in range(0, len(notifications), batch_size):
                batch = notifications[i:i + batch_size]
                batch_ids = []
                
                # Process batch concurrently
                tasks = []
                for notif_config in batch:
                    task = asyncio.create_task(
                        self.send_notification(**notif_config)
                    )
                    tasks.append(task)
                    
                # Wait for batch completion
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, str):  # Success - notification ID
                        batch_ids.append(result)
                    else:  # Exception occurred
                        self.logger.error(f"Bulk notification failed: {result}")
                        
                notification_ids.extend(batch_ids)
                
                # Brief pause between batches
                await asyncio.sleep(0.1)
                
            self.logger.info(f"Bulk notifications processed: {len(notification_ids)} successful")
            return notification_ids
            
        except Exception as e:
            self.logger.error(f"Bulk notification processing failed: {str(e)}")
            raise
            
    async def get_notification_status(self, notification_id: str) -> Dict[str, Any]:
        """Get comprehensive notification status and delivery information"""        try:
            notification = self.notification_storage.get(notification_id)
            if not notification:
                return {"error": "Notification not found"}
                
            # Get delivery history
            delivery_info = self.delivery_history.get(notification_id, {})
            
            # Get performance metrics
            metrics = await self.monitoring.get_notification_metrics(notification_id)
            
            return {
                "notification_id": notification_id,
                "status": notification.status.value,
                "created_at": notification.created_at.isoformat(),
                "channels": [ch.value for ch in notification.channels],
                "priority": notification.priority.value,
                "delivery_info": delivery_info,
                "metrics": metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get notification status: {str(e)}")
            return {"error": str(e)}
            
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: NotificationConfiguration
    ) -> bool:
        """Update user notification preferences with validation"""        try:
            # Validate preferences
            if not await self._validate_user_preferences(preferences):
                return False
                
            # Store preferences
            self.user_preferences[user_id] = preferences
            
            # Update AI personalization model
            await self.ai_personalizer.update_user_preferences(user_id, preferences)
            
            self.logger.info(f"User preferences updated: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update user preferences: {str(e)}")
            return False
            
    async def _process_notification_queue(self):
        """Process notifications from the main queue"""        while True:
            try:
                notification = await self.notification_queue.get()
                await self._deliver_notification(notification)
                self.notification_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing notification queue: {str(e)}")
                await asyncio.sleep(1)
                
    async def _deliver_notification(self, notification: NotificationModel):
        """Deliver notification through multiple channels"""        try:
            delivery_results = {}
            
            # Update status
            notification.status = NotificationStatus.PROCESSING
            self.notification_storage[notification.id] = notification
            
            # Deliver through each channel
            for channel in notification.channels:
                try:
                    result = await self._deliver_to_channel(notification, channel)
                    delivery_results[channel.value] = result
                    
                except Exception as e:
                    delivery_results[channel.value] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    
            # Update delivery history
            self.delivery_history[notification.id] = {
                "delivered_at": datetime.utcnow().isoformat(),
                "channels": delivery_results,
                "attempts": 1
            }
            
            # Determine overall status
            if any(r.get("status") == "success" for r in delivery_results.values()):
                notification.status = NotificationStatus.DELIVERED
            else:
                notification.status = NotificationStatus.FAILED
                # Queue for retry if applicable
                if notification.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]:
                    await self.retry_queue.put(notification)
                    
            # Update metrics
            await self._update_delivery_metrics(notification, delivery_results)
            
        except Exception as e:
            self.logger.error(f"Failed to deliver notification {notification.id}: {str(e)}")
            notification.status = NotificationStatus.FAILED
            
    async def _deliver_to_channel(
        self,
        notification: NotificationModel,
        channel: NotificationChannel
    ) -> Dict[str, Any]:
        """Deliver notification to specific channel"""        try:
            # Get appropriate delivery handler
            handler = self.integration_manager.get_channel_handler(channel)
            
            # Prepare channel-specific content
            channel_content = await self._prepare_channel_content(notification, channel)
            
            # Deliver notification
            delivery_result = await handler.send_notification(
                user_id=notification.user_id,
                content=channel_content,
                priority=notification.priority
            )
            
            return {
                "status": "success",
                "delivery_id": delivery_result.get("delivery_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Channel delivery failed for {channel.value}: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    async def _determine_optimal_channels(
        self,
        user_id: str,
        notification_type: NotificationType,
        priority: NotificationPriority
    ) -> List[NotificationChannel]:
        """AI-driven optimal channel selection"""        try:
            # Get user preferences
            user_prefs = self.user_preferences.get(user_id)
            if not user_prefs:
                # Use default channels based on notification type and priority
                return await self._get_default_channels(notification_type, priority)
                
            # Apply AI-driven channel optimization
            optimal_channels = await self.ai_personalizer.optimize_channels(
                user_id, notification_type, priority, user_prefs
            )
            
            return optimal_channels
            
        except Exception as e:
            self.logger.error(f"Failed to determine optimal channels: {str(e)}")
            return [NotificationChannel.EMAIL]  # Fallback
            
    async def _get_default_channels(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority
    ) -> List[NotificationChannel]:
        """Get default channels based on notification type and priority"""        channel_mapping = {
            NotificationType.SECURITY_ALERT: [
                NotificationChannel.EMAIL,
                NotificationChannel.SMS,
                NotificationChannel.PUSH
            ],
            NotificationType.COPYRIGHT_INFRINGEMENT: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP
            ],
            NotificationType.COLLABORATION_MATCH: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP,
                NotificationChannel.PUSH
            ],
            NotificationType.MONETIZATION_OPPORTUNITY: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP
            ]
        }
        
        # Priority-based channel adjustment
        base_channels = channel_mapping.get(notification_type, [NotificationChannel.EMAIL])
        
        if priority == NotificationPriority.URGENT:
            # Add immediate channels for urgent notifications
            if NotificationChannel.SMS not in base_channels:
                base_channels.append(NotificationChannel.SMS)
            if NotificationChannel.PUSH not in base_channels:
                base_channels.append(NotificationChannel.PUSH)
                
        return base_channels
        
    async def _prepare_channel_content(
        self,
        notification: NotificationModel,
        channel: NotificationChannel
    ) -> Dict[str, Any]:
        """Prepare channel-specific content formatting"""        try:
            base_content = notification.content
            
            # Channel-specific formatting
            if channel == NotificationChannel.SMS:
                return await self._format_sms_content(base_content)
            elif channel == NotificationChannel.EMAIL:
                return await self._format_email_content(base_content)
            elif channel == NotificationChannel.PUSH:
                return await self._format_push_content(base_content)
            elif channel == NotificationChannel.IN_APP:
                return await self._format_in_app_content(base_content)
            else:
                return base_content
                
        except Exception as e:
            self.logger.error(f"Failed to prepare channel content: {str(e)}")
            return notification.content
            
    async def _format_sms_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for SMS delivery"""        return {
            "message": content.get("title", "")[:160],  # SMS character limit
            "short_url": content.get("action_url", "")
        }
        
    async def _format_email_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for email delivery"""        return {
            "subject": content.get("title", ""),
            "html_body": content.get("html_content", ""),
            "text_body": content.get("text_content", ""),
            "attachments": content.get("attachments", [])
        }
        
    async def _format_push_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for push notification delivery"""        return {
            "title": content.get("title", "")[:50],  # Push title limit
            "body": content.get("summary", "")[:200],  # Push body limit
            "icon": content.get("icon", ""),
            "action_url": content.get("action_url", "")
        }
        
    async def _format_in_app_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for in-app notification display"""        return {
            "title": content.get("title", ""),
            "message": content.get("message", ""),
            "rich_content": content.get("rich_content", {}),
            "actions": content.get("actions", [])
        }
        
    async def _update_delivery_metrics(
        self,
        notification: NotificationModel,
        delivery_results: Dict[str, Any]
    ):
        """Update performance metrics based on delivery results"""        try:
            # Update total counts
            self.performance_metrics['total_sent'] += 1
            
            # Count successful deliveries
            successful_deliveries = sum(
                1 for result in delivery_results.values()
                if result.get("status") == "success"
            )
            
            if successful_deliveries > 0:
                self.performance_metrics['total_delivered'] += 1
            else:
                self.performance_metrics['total_failed'] += 1
                
            # Update channel-specific metrics
            for channel, result in delivery_results.items():
                if channel not in self.performance_metrics['channel_performance']:
                    self.performance_metrics['channel_performance'][channel] = {
                        'sent': 0, 'delivered': 0, 'failed': 0
                    }
                    
                self.performance_metrics['channel_performance'][channel]['sent'] += 1
                
                if result.get("status") == "success":
                    self.performance_metrics['channel_performance'][channel]['delivered'] += 1
                else:
                    self.performance_metrics['channel_performance'][channel]['failed'] += 1
                    
            # Record metrics in monitoring system
            await self.monitoring.record_delivery_metrics(notification.id, delivery_results)
            
        except Exception as e:
            self.logger.error(f"Failed to update delivery metrics: {str(e)}")
            
    async def _validate_user_preferences(
        self,
        preferences: NotificationConfiguration
    ) -> bool:
        """Validate user notification preferences"""        try:
            # Validate enabled channels
            if not preferences.enabled_channels:
                return False
                
            # Validate priority rules
            valid_priorities = [p.value for p in NotificationPriority]
            for rule_priority in preferences.priority_rules.values():
                if rule_priority.value not in valid_priorities:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Preference validation failed: {str(e)}")
            return False
            
    async def _process_batch_queue(self):
        """Process batched notifications for efficiency"""        while True:
            try:
                batch_notifications = []
                
                # Collect batch of notifications
                while len(batch_notifications) < 50:  # Batch size limit
                    try:
                        notification = await asyncio.wait_for(
                            self.batch_queue.get(), timeout=5.0
                        )
                        batch_notifications.append(notification)
                    except asyncio.TimeoutError:
                        break
                        
                if batch_notifications:
                    await self._process_notification_batch(batch_notifications)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Batch processing error: {str(e)}")
                await asyncio.sleep(1)
                
    async def _process_notification_batch(self, notifications: List[NotificationModel]):
        """Process a batch of notifications efficiently"""        try:
            # Group by channel for efficient delivery
            channel_groups = {}
            for notification in notifications:
                for channel in notification.channels:
                    if channel not in channel_groups:
                        channel_groups[channel] = []
                    channel_groups[channel].append(notification)
                    
            # Process each channel group
            for channel, channel_notifications in channel_groups.items():
                handler = self.integration_manager.get_channel_handler(channel)
                await handler.send_batch_notifications(channel_notifications)
                
            self.logger.info(f"Processed notification batch: {len(notifications)} notifications")
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            
    async def _retry_failed_notifications(self):
        """Handle retry logic for failed notifications"""        while True:
            try:
                notification = await self.retry_queue.get()
                
                # Check retry limits
                retry_count = self.delivery_history.get(notification.id, {}).get('attempts', 0)
                max_retries = self._get_max_retries(notification.priority)
                
                if retry_count < max_retries:
                    # Exponential backoff
                    delay = min(300, 2 ** retry_count)  # Max 5 minutes
                    await asyncio.sleep(delay)
                    
                    # Retry delivery
                    await self._deliver_notification(notification)
                    
                    # Update retry count
                    if notification.id in self.delivery_history:
                        self.delivery_history[notification.id]['attempts'] = retry_count + 1
                        
                else:
                    # Mark as permanently failed
                    notification.status = NotificationStatus.FAILED
                    self.logger.warning(f"Notification permanently failed: {notification.id}")
                    
                self.retry_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Retry processing error: {str(e)}")
                await asyncio.sleep(1)
                
    def _get_max_retries(self, priority: NotificationPriority) -> int:
        """Get maximum retry count based on priority"""        retry_limits = {
            NotificationPriority.LOW: 1,
            NotificationPriority.MEDIUM: 3,
            NotificationPriority.HIGH: 5,
            NotificationPriority.URGENT: 10
        }
        return retry_limits.get(priority, 3)
        
    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications and delivery history"""        while True:
            try:
                current_time = datetime.utcnow()
                expired_ids = []
                
                # Find expired notifications (older than 7 days)
                for notif_id, notification in self.notification_storage.items():
                    if (current_time - notification.created_at).days > 7:
                        expired_ids.append(notif_id)
                        
                # Clean up expired data
                for notif_id in expired_ids:
                    del self.notification_storage[notif_id]
                    if notif_id in self.delivery_history:
                        del self.delivery_history[notif_id]
                        
                if expired_ids:
                    self.logger.info(f"Cleaned up {len(expired_ids)} expired notifications")
                    
                # Sleep for 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup process error: {str(e)}")
                await asyncio.sleep(3600)
                
    async def _generate_analytics_reports(self):
        """Generate periodic analytics reports"""        while True:
            try:
                # Generate daily report
                report_data = await self._compile_analytics_report()
                
                # Send report to administrators
                await self._send_analytics_report(report_data)
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Analytics report generation error: {str(e)}")
                await asyncio.sleep(86400)
                
    async def _compile_analytics_report(self) -> Dict[str, Any]:
        """Compile comprehensive analytics report"""        try:
            return {
                "report_date": datetime.utcnow().isoformat(),
                "performance_metrics": self.performance_metrics.copy(),
                "channel_effectiveness": await self._calculate_channel_effectiveness(),
                "user_engagement": await self._calculate_user_engagement(),
                "delivery_trends": await self._analyze_delivery_trends(),
                "ai_insights": await self.ai_personalizer.get_analytics_insights()
            }
        except Exception as e:
            self.logger.error(f"Analytics compilation failed: {str(e)}")
            return {}
            
    async def _calculate_channel_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness score for each channel"""        effectiveness = {}
        
        for channel, metrics in self.performance_metrics['channel_performance'].items():
            if metrics['sent'] > 0:
                effectiveness[channel] = metrics['delivered'] / metrics['sent']
            else:
                effectiveness[channel] = 0.0
                
        return effectiveness
        
    async def _calculate_user_engagement(self) -> Dict[str, Any]:
        """Calculate user engagement metrics"""        # This would analyze read rates, response rates, etc.
        return {
            "average_read_rate": 0.75,  # Placeholder
            "response_rate": 0.25,      # Placeholder
            "opt_out_rate": 0.02        # Placeholder
        }
        
    async def _analyze_delivery_trends(self) -> Dict[str, Any]:
        """Analyze delivery trends and patterns"""        return {
            "peak_hours": [9, 10, 11, 14, 15, 16],  # Placeholder
            "best_days": ["Tuesday", "Wednesday", "Thursday"],  # Placeholder
            "seasonal_patterns": {}  # Placeholder
        }
        
    async def _send_analytics_report(self, report_data: Dict[str, Any]):
        """Send analytics report to administrators"""        try:
            # Create notification for analytics report
            admin_context = NotificationContext(
                user_id="system_admin",
                content_type="analytics_report",
                metadata=report_data
            )
            
            await self.send_notification(
                NotificationType.ANALYTICS_REPORT,
                admin_context,
                [NotificationChannel.EMAIL],
                NotificationPriority.LOW
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send analytics report: {str(e)}")
            
    async def _process_remaining_notifications(self):
        """Process any remaining notifications during shutdown"""        try:
            # Process remaining in main queue
            while not self.notification_queue.empty():
                notification = await self.notification_queue.get()
                await self._deliver_notification(notification)
                self.notification_queue.task_done()
                
            # Process remaining in batch queue
            while not self.batch_queue.empty():
                notification = await self.batch_queue.get()
                await self._deliver_notification(notification)
                self.batch_queue.task_done()
                
        except Exception as e:
            self.logger.error(f"Error processing remaining notifications: {str(e)}")


class NotificationAgentManager:
    """    Advanced manager for multiple notification agent instances
    Handles load balancing, failover, and distributed notification processing
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, NotificationAgent] = {}
        self.load_balancer = self._initialize_load_balancer()
        self.health_monitor = self._initialize_health_monitor()
        
    def _initialize_load_balancer(self):
        """Initialize intelligent load balancing system"""        from ...infrastructure.load_balancer import NotificationLoadBalancer
        return NotificationLoadBalancer(self.config.get('load_balancer', {}))
        
    def _initialize_health_monitor(self):
        """Initialize agent health monitoring system"""        from ...monitoring.agent_health_monitor import AgentHealthMonitor
        return AgentHealthMonitor(self.config.get('health_monitor', {}))
        
    async def create_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> bool:
        """Create and start a new notification agent instance"""        try:
            agent = NotificationAgent(agent_config)
            success = await agent.start_agent()
            
            if success:
                self.agents[agent_id] = agent
                await self.health_monitor.register_agent(agent_id, agent)
                self.logger.info(f"Notification agent created: {agent_id}")
                return True
            else:
                self.logger.error(f"Failed to start notification agent: {agent_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create notification agent {agent_id}: {str(e)}")
            return False
            
    async def get_optimal_agent(self, workload_hint: Optional[str] = None) -> Optional[NotificationAgent]:
        """Get the most suitable agent for current workload"""        try:
            return await self.load_balancer.get_optimal_agent(self.agents, workload_hint)
        except Exception as e:
            self.logger.error(f"Failed to get optimal agent: {str(e)}")
            return None
            
    async def distribute_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext,
        **kwargs
    ) -> str:
        """Distribute notification to optimal agent"""        try:
            agent = await self.get_optimal_agent(notification_type.value)
            if not agent:
                raise ValueError("No available agents for notification processing")
                
            return await agent.send_notification(notification_type, context, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to distribute notification: {str(e)}")
            raise
            
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics from all agents"""        try:
            system_metrics = {
                "total_agents": len(self.agents),
                "active_agents": 0,
                "total_performance": {
                    'total_sent': 0,
                    'total_delivered': 0,
                    'total_failed': 0,
                    'average_delivery_time': 0.0
                },
                "agent_metrics": {}
            }
            
            # Collect metrics from all agents
            for agent_id, agent in self.agents.items():
                try:
                    if await self.health_monitor.is_agent_healthy(agent_id):
                        system_metrics["active_agents"] += 1
                        
                        # Add agent performance to totals
                        agent_perf = agent.performance_metrics
                        system_metrics["total_performance"]["total_sent"] += agent_perf["total_sent"]
                        system_metrics["total_performance"]["total_delivered"] += agent_perf["total_delivered"]
                        system_metrics["total_performance"]["total_failed"] += agent_perf["total_failed"]
                        
                        system_metrics["agent_metrics"][agent_id] = agent_perf
                        
                except Exception as e:
                    self.logger.error(f"Failed to get metrics from agent {agent_id}: {str(e)}")
                    
            return system_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {str(e)}")
            return {}
