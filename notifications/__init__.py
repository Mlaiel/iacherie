"""Enterprise notification system with multi-channel delivery, AI personalization, and comprehensive analytics.

This module provides a complete notification infrastructure for the IA Influencer Agent platform,
supporting email, SMS, push notifications, webhooks, in-app notifications, and more.

Built by Fahed Mlaiel and the IA Influencer Agent Team.
© 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

WARNING: This code is proprietary and confidential. Unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action. All intellectual property rights
belong exclusively to Fahed Mlaiel.
"""
from .email import EmailNotifier
from .sms import SMSNotifier, SMSMessage, SMSDeliveryResult, SMSProvider
from .push import PushNotifier, PushMessage, PushContent, PushDeliveryResult, PushPlatform, NotificationPriority
from .webhook import WebhookNotifier, WebhookPayload, WebhookDeliveryResult, WebhookEvent, WebhookEndpoint
from .in_app import InAppNotifier, InAppNotification, InAppNotificationType, NotificationPreferences
from .templates import NotificationTemplateEngine, NotificationTemplate, PersonalizationContext, ABTestVariant
from .orchestrator import NotificationOrchestrator, UniversalNotification, DeliveryResult, NotificationPreference

__all__ = [
    # Core notifiers
    "EmailNotifier",
    "SMSNotifier", "SMSMessage", "SMSDeliveryResult", "SMSProvider",
    "PushNotifier", "PushMessage", "PushContent", "PushDeliveryResult", "PushPlatform",
    "WebhookNotifier", "WebhookPayload", "WebhookDeliveryResult", "WebhookEvent", "WebhookEndpoint",
    "InAppNotifier", "InAppNotification", "InAppNotificationType", "NotificationPreferences",
    
    # Template engine
    "NotificationTemplateEngine", "NotificationTemplate", "PersonalizationContext", "ABTestVariant",
    
    # Orchestration
    "NotificationOrchestrator", "UniversalNotification", "DeliveryResult", "NotificationPreference",
    
    # Enums
    "NotificationPriority"
]
from .email import EmailNotifier
from .sms import SMSNotifier  
from .push import PushNotifier
from .webhook import WebhookNotifier

__all__ = [
    "EmailNotifier",
    "SMSNotifier",
    "PushNotifier", 
    "WebhookNotifier",
]
