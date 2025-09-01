"""Enterprise Notification System Index - IA Influencer Agent

This index file provides quick access to all notification system components
and serves as the main entry point for the notification infrastructure.

Built by Fahed Mlaiel and the IA Influencer Agent Team.
(c) 2025 Fahed Mlaiel. All rights reserved.
"""# Import all major components for easy access
from .orchestrator import (
    NotificationOrchestrator,
    UniversalNotification,
    DeliveryResult,
    NotificationPreference,
    DeliveryChannel,
    DeliveryStrategy
)

from .templates import (
    NotificationTemplateEngine,
    NotificationTemplate,
    PersonalizationContext,
    ABTestVariant,
    TemplateType,
    PersonalizationLevel,
    ContentTone
)

from .email import EmailNotifier
from .sms import SMSNotifier, SMSMessage, SMSProvider
from .push import PushNotifier, PushMessage, PushContent, PushPlatform
from .webhook import WebhookNotifier, WebhookPayload, WebhookEvent, WebhookEndpoint
from .in_app import InAppNotifier, InAppNotification, InAppNotificationType, NotificationPreferences

# Quick setup function for common use cases
def create_notification_system():
    """
Create a fully configured notification system for IA Influencer Agent."""
    orchestrator = NotificationOrchestrator()
    template_engine = NotificationTemplateEngine()
    
    return {
        'orchestrator': orchestrator,
        'template_engine': template_engine,
        'email': orchestrator.email_notifier,
        'sms': orchestrator.sms_notifier,
        'push': orchestrator.push_notifier,
        'webhook': orchestrator.webhook_notifier,
        'in_app': orchestrator.in_app_notifier
    }

# Business-specific notification creators
def create_content_protection_notification(user_id: str, content_title: str, protection_status: str):
    """
Create notification for content protection events."""
    return UniversalNotification(
        user_id=user_id,
        title=f"Content Protection Update: {content_title}",
        message=f"Your content '{content_title}' protection status: {protection_status}",
        event_type="content.protected",
        template_id="content_protection_update"
    )

def create_collaboration_notification(user_id: str, requester_name: str, project_type: str):
    """Create notification for collaboration requests."""
    return UniversalNotification(
        user_id=user_id,
        title="New Collaboration Opportunity",
        message=f"{requester_name} wants to collaborate on a {project_type} project",
        event_type="collaboration.request",
        template_id="collaboration_request"
    )

def create_revenue_notification(user_id: str, amount: float, period: str):
    """Create notification for revenue milestones."""
    return UniversalNotification(
        user_id=user_id,
        title="Revenue Milestone Reached!",
        message=f"You've earned ${amount:.2f} in {period}!",
        event_type="revenue.milestone",
        template_id="revenue_milestone"
    )

def create_viral_content_notification(user_id: str, content_title: str, views: int):
    """Create notification for viral content alerts."""
    return UniversalNotification(
        user_id=user_id,
        title="Your Content is Going Viral!",
        message=f"'{content_title}' has reached {views:,} views!",
        event_type="viral.content_detected",
        template_id="viral_content_alert"
    )

# Export everything
__all__ = [
    # Main components
    'NotificationOrchestrator',
    'NotificationTemplateEngine',
    'UniversalNotification',
    'DeliveryResult',
    'NotificationPreference',
    'PersonalizationContext',
    
    # Channel notifiers
    'EmailNotifier',
    'SMSNotifier',
    'PushNotifier', 
    'WebhookNotifier',
    'InAppNotifier',
    
    # Data classes
    'SMSMessage',
    'PushMessage',
    'PushContent',
    'WebhookPayload',
    'WebhookEndpoint',
    'InAppNotification',
    'NotificationTemplate',
    'ABTestVariant',
    
    # Enums
    'DeliveryChannel',
    'DeliveryStrategy',
    'SMSProvider',
    'PushPlatform',
    'WebhookEvent',
    'InAppNotificationType',
    'TemplateType',
    'PersonalizationLevel',
    'ContentTone',
    
    # Helper functions
    'create_notification_system',
    'create_content_protection_notification',
    'create_collaboration_notification',
    'create_revenue_notification',
    'create_viral_content_notification'
]
