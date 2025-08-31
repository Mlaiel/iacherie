"""
Notification Agent Index - Quick Access to Core Functionality

Centralized access point for all notification agent functionality with
simplified interfaces and smart defaults for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property are the EXCLUSIVE PROPERTY of Fahed Mlaiel.

STRICTLY PROHIBITED WITHOUT EXPLICIT WRITTEN AUTHORIZATION:
- Copying, cloning, reproducing, or distributing this code
- Using concepts, methodologies, or approaches in other projects
- Commercial exploitation, monetization, or resale
- Reverse engineering, decompilation, or adaptation
- Creating derivative works based on this intellectual property

Contact for licensing inquiries: mlaiel@live.de

Violation of these terms will result in immediate legal action.
All usage is monitored, logged, and legally protected.

Team Specialties & Expertise:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from . import (
    NotificationAgent,
    NotificationDispatcher,
    NotificationEventManager,
    NotificationSubscriptionManager,
    NotificationAnalyticsEngine,
    NotificationWorkflowOrchestrator,
    ChannelManager,
    PriorityHandler,
    TemplateManager,
    NotificationEventType,
    ChannelType,
    WorkflowType
)


class NotificationAgentFacade:
    """
    Simplified facade for the complete notification system
    
    Provides easy-to-use interfaces for common notification operations
    while maintaining access to advanced functionality when needed.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        
        # Core components
        self.channel_manager = None
        self.priority_handler = None
        self.template_manager = None
        self.notification_dispatcher = None
        self.event_manager = None
        self.subscription_manager = None
        self.analytics_engine = None
        self.workflow_orchestrator = None
        self.notification_agent = None
    
    async def initialize(self):
        """Initialize all notification system components"""
        if self._initialized:
            return
        
        try:
            # Initialize core components
            self.channel_manager = ChannelManager()
            self.priority_handler = PriorityHandler()
            self.template_manager = TemplateManager()
            
            # Initialize advanced components
            self.notification_dispatcher = NotificationDispatcher(
                self.channel_manager,
                self.priority_handler,
                self.template_manager
            )
            
            self.subscription_manager = NotificationSubscriptionManager()
            self.analytics_engine = NotificationAnalyticsEngine()
            
            # Initialize event manager with dispatcher
            from ...core.events import EventBus
            event_bus = EventBus()
            
            self.event_manager = NotificationEventManager(
                self.notification_dispatcher,
                self.priority_handler,
                event_bus
            )
            
            # Initialize workflow orchestrator
            self.workflow_orchestrator = NotificationWorkflowOrchestrator(
                self.notification_dispatcher,
                self.event_manager,
                self.subscription_manager,
                self.analytics_engine
            )
            
            # Initialize main notification agent
            self.notification_agent = NotificationAgent(
                agent_id="notification_agent_main",
                config={
                    'dispatcher': self.notification_dispatcher,
                    'event_manager': self.event_manager,
                    'subscription_manager': self.subscription_manager,
                    'analytics_engine': self.analytics_engine,
                    'workflow_orchestrator': self.workflow_orchestrator
                }
            )
            
            self._initialized = True
            self.logger.info("Notification Agent system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise
    
    async def send_notification(
        self,
        user_id: str,
        message: str,
        notification_type: str = "general",
        channels: Optional[List[str]] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Send a simple notification with intelligent defaults
        
        Args:
            user_id: Target user ID
            message: Notification message
            notification_type: Type of notification (content_upload, protection_alert, etc.)
            channels: Preferred channels (auto-selected if None)
            priority: Priority level (low, medium, high, critical)
            
        Returns:
            Notification result with delivery status
        """
        await self._ensure_initialized()
        
        try:
            # Create notification model
            from ...models.notification_models import NotificationModel
            
            notification = NotificationModel(
                id=f"notif_{user_id}_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                notification_type=notification_type,
                title="Notification from IA Influencer Platform",
                content=message,
                priority=priority,
                metadata={'source': 'facade'}
            )
            
            # Convert string channels to ChannelType
            target_channels = None
            if channels:
                target_channels = [
                    ChannelType(ch) for ch in channels
                    if ch in [ct.value for ct in ChannelType]
                ]
            
            # Dispatch notification
            result = await self.notification_dispatcher.dispatch_notification(
                notification, target_channels
            )
            
            return {
                'success': result.final_status.value in ['delivered', 'sent'],
                'notification_id': result.notification_id,
                'channels_used': [ch.value for ch in result.channels_successful],
                'delivery_time': result.total_delivery_time
            }
            
        except Exception as e:
            self.logger.error(f"Send notification failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def trigger_business_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a business event that may result in notifications
        
        Args:
            user_id: User ID
            event_type: Business event type
            event_data: Event context data
            
        Returns:
            Event processing result
        """
        await self._ensure_initialized()
        
        try:
            from .event_manager import NotificationEvent, EventPriority
            
            # Map string event type to enum
            try:
                mapped_event_type = NotificationEventType(event_type)
            except ValueError:
                mapped_event_type = NotificationEventType.PLATFORM_UPDATE
            
            # Create notification event
            event = NotificationEvent(
                event_id=f"event_{user_id}_{datetime.utcnow().isoformat()}",
                event_type=mapped_event_type,
                user_id=user_id,
                priority=EventPriority.MEDIUM,
                business_context=event_data.get('business_context', {}),
                content_metadata=event_data.get('content_metadata', {}),
                custom_attributes=event_data
            )
            
            # Process event
            result = await self.event_manager.process_event(event)
            
            return {
                'success': result.processing_status.value == 'completed',
                'event_id': result.event_id,
                'notifications_triggered': len(result.notifications_triggered),
                'processing_time': result.processing_time_seconds
            }
            
        except Exception as e:
            self.logger.error(f"Business event trigger failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def start_workflow(
        self,
        user_id: str,
        workflow_type: str,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a notification workflow for a user
        
        Args:
            user_id: Target user ID
            workflow_type: Type of workflow to start
            trigger_data: Data that triggered the workflow
            
        Returns:
            Workflow execution details
        """
        await self._ensure_initialized()
        
        try:
            # Map workflow types to built-in workflows
            workflow_mapping = {
                'content_onboarding': 'content_onboarding_v1',
                'content_protection': 'content_protection_v1',
                'collaboration_matching': 'collaboration_matching_v1'
            }
            
            workflow_id = workflow_mapping.get(workflow_type, workflow_type)
            execution_id = await self.workflow_orchestrator.trigger_workflow(
                workflow_id, user_id, trigger_data or {}
            )
            
            if execution_id:
                status = await self.workflow_orchestrator.get_execution_status(execution_id)
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'workflow_id': workflow_id,
                    'status': status
                }
            else:
                return {'success': False, 'error': 'Failed to start workflow'}
            
        except Exception as e:
            self.logger.error(f"Workflow start failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        await self._ensure_initialized()
        
        try:
            profile = await self.subscription_manager.get_user_profile(user_id)
            analytics = await self.subscription_manager.get_subscription_analytics(user_id)
            
            return {
                'user_id': user_id,
                'preferences': profile.global_preferences,
                'subscriptions': {
                    sub_type.value: {
                        'enabled': settings.enabled,
                        'frequency': settings.frequency.value,
                        'channels': [
                            pref.channel_type.value for pref in settings.channel_preferences
                            if pref.enabled
                        ]
                    }
                    for sub_type, settings in profile.subscription_settings.items()
                },
                'analytics': analytics
            }
            
        except Exception as e:
            self.logger.error(f"Get user preferences failed: {str(e)}")
            return {'error': str(e)}
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system performance metrics"""
        await self._ensure_initialized()
        
        try:
            from .analytics_engine import MetricType, AnalyticsTimeframe
            
            # Get real-time metrics
            realtime_metrics = await self.analytics_engine.get_realtime_metrics([
                MetricType.DELIVERY_RATE,
                MetricType.OPEN_RATE,
                MetricType.CLICK_RATE,
                MetricType.ENGAGEMENT_SCORE
            ])
            
            # Get workflow metrics
            workflow_metrics = await self.workflow_orchestrator.get_workflow_metrics()
            
            # Get channel performance
            channel_performance = await self.analytics_engine.get_channel_performance_comparison(
                AnalyticsTimeframe.DAILY,
                [MetricType.DELIVERY_RATE, MetricType.OPEN_RATE]
            )
            
            return {
                'realtime_metrics': {
                    metric.value: value for metric, value in realtime_metrics.items()
                },
                'workflow_metrics': workflow_metrics,
                'channel_performance': {
                    channel.value: {
                        metric.value: value for metric, value in metrics.items()
                    }
                    for channel, metrics in channel_performance.items()
                },
                'system_health': 'healthy' if all(
                    value > 0.5 for value in realtime_metrics.values()
                ) else 'needs_attention'
            }
            
        except Exception as e:
            self.logger.error(f"Get system metrics failed: {str(e)}")
            return {'error': str(e)}
    
    async def _ensure_initialized(self):
        """Ensure system is initialized before use"""
        if not self._initialized:
            await self.initialize()


# Global facade instance
notification_system = NotificationAgentFacade()


# Convenience functions for common operations
async def send_quick_notification(
    user_id: str,
    message: str,
    notification_type: str = "general",
    priority: str = "medium"
) -> Dict[str, Any]:
    """Quick notification sending function"""



    return await notification_system.send_notification(
        user_id, message, notification_type, priority=priority
    )


async def trigger_content_upload_workflow(user_id: str, content_data: Dict[str, Any]):
    """Trigger content upload workflow"""



    return await notification_system.trigger_business_event(
        user_id, 'content_uploaded', {
            'business_context': {'upload_status': 'success'},
            'content_metadata': content_data
        }
    )


async def trigger_protection_alert(user_id: str, protection_data: Dict[str, Any]):
    """Trigger content protection alert"""



    return await notification_system.trigger_business_event(
        user_id, 'infringement_alert', {
            'business_context': {'confidence_score': protection_data.get('confidence', 0.9)},
            'content_metadata': protection_data
        }
    )


async def notify_collaboration_match(user_id: str, match_data: Dict[str, Any]):
    """Notify about collaboration match"""



    return await notification_system.trigger_business_event(
        user_id, 'collaboration_match_found', {
            'collaboration_data': match_data
        }
    )


async def notify_revenue_opportunity(user_id: str, revenue_data: Dict[str, Any]):
    """Notify about revenue opportunity"""



    return await notification_system.trigger_business_event(
        user_id, 'revenue_opportunity', {
            'monetization_data': revenue_data
        }
    )


# Export convenience functions
__all__ = [
    'NotificationAgentFacade',
    'notification_system',
    'send_quick_notification',
    'trigger_content_upload_workflow',
    'trigger_protection_alert',
    'notify_collaboration_match',
    'notify_revenue_opportunity'
]
