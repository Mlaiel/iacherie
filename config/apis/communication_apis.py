"""Communication APIs Configuration - Email, SMS & Notification Services
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module configures communication APIs for email delivery, SMS messaging,
push notifications, and other communication channels for user engagement.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class CommunicationServiceType(Enum):
    """Communication service types"""    EMAIL_DELIVERY = "email_delivery"
    SMS_MESSAGING = "sms_messaging"
    PUSH_NOTIFICATIONS = "push_notifications"
    IN_APP_MESSAGING = "in_app_messaging"
    VOICE_CALLING = "voice_calling"
    CHATBOT = "chatbot"

class MessagePriority(Enum):
    """Message priority levels"""    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class CommunicationAPIConfig:
    """Configuration class for communication APIs"""    service_name: str
    service_type: CommunicationServiceType
    base_url: str
    api_version: str
    
    # Credentials (from environment)
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    sender_id: Optional[str] = None
    
    # Message configuration
    default_sender_email: Optional[str] = None
    default_sender_name: Optional[str] = None
    default_phone_number: Optional[str] = None
    
    # Delivery settings
    delivery_retry_attempts: int = 3
    delivery_timeout_seconds: int = 30
    supports_scheduling: bool = True
    supports_templating: bool = True
    supports_personalization: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 6000
    rate_limit_per_day: int = 100000
    
    # Features
    supports_html_email: bool = True
    supports_attachments: bool = True
    supports_tracking: bool = True
    supports_analytics: bool = True
    supports_bounce_handling: bool = True
    supports_unsubscribe: bool = True
    
    # Compliance
    gdpr_compliant: bool = True
    can_spam_compliant: bool = True
    supports_opt_in: bool = True
    supports_opt_out: bool = True
    
    # Cost structure
    cost_per_email: float = 0.001
    cost_per_sms: float = 0.05
    cost_per_push: float = 0.0001
    monthly_free_quota: int = 10000
    
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> Dict[str, Any]:
        """Get configuration for specific environment"""        base_config = self.__dict__.copy()
        env_config = self.environments.get(environment, {})
        base_config.update(env_config)
        return base_config

# SendGrid Email Configuration
SENDGRID_CONFIG = CommunicationAPIConfig(
    service_name="sendgrid",
    service_type=CommunicationServiceType.EMAIL_DELIVERY,
    base_url="https://api.sendgrid.com",
    api_version="v3",
    api_key=os.getenv("SENDGRID_API_KEY"),
    sender_id=os.getenv("SENDGRID_SENDER_ID"),
    default_sender_email=os.getenv("SENDGRID_FROM_EMAIL", "noreply@ia-influencer.com"),
    default_sender_name=os.getenv("SENDGRID_FROM_NAME", "IA Influencer Agent"),
    supports_html_email=True,
    supports_attachments=True,
    supports_tracking=True,
    supports_analytics=True,
    supports_bounce_handling=True,
    supports_unsubscribe=True,
    supports_scheduling=True,
    supports_templating=True,
    supports_personalization=True,
    rate_limit_per_minute=600,
    rate_limit_per_hour=36000,
    rate_limit_per_day=600000,
    cost_per_email=0.0006,
    monthly_free_quota=40000,
    environments={
        "development": {
            "default_sender_email": "dev-noreply@ia-influencer.com",
            "monthly_free_quota": 100
        },
        "staging": {
            "default_sender_email": "staging-noreply@ia-influencer.com", 
            "monthly_free_quota": 1000
        }
    }
)

# Mailgun Email Configuration
MAILGUN_CONFIG = CommunicationAPIConfig(
    service_name="mailgun",
    service_type=CommunicationServiceType.EMAIL_DELIVERY,
    base_url="https://api.mailgun.net",
    api_version="v3",
    api_key=os.getenv("MAILGUN_API_KEY"),
    secret_key=os.getenv("MAILGUN_DOMAIN"),
    default_sender_email=os.getenv("MAILGUN_FROM_EMAIL", "noreply@mail.ia-influencer.com"),
    default_sender_name="IA Influencer Agent",
    supports_html_email=True,
    supports_attachments=True,
    supports_tracking=True,
    supports_analytics=True,
    supports_bounce_handling=True,
    supports_scheduling=True,
    supports_templating=True,
    rate_limit_per_minute=100,
    rate_limit_per_hour=10000,
    cost_per_email=0.0008,
    monthly_free_quota=10000,
    environments={
        "development": {
            "secret_key": os.getenv("MAILGUN_SANDBOX_DOMAIN"),
            "default_sender_email": "dev-noreply@sandbox.mailgun.org"
        }
    }
)

# AWS SES Configuration
AWS_SES_CONFIG = CommunicationAPIConfig(
    service_name="aws_ses",
    service_type=CommunicationServiceType.EMAIL_DELIVERY,
    base_url="https://email.amazonaws.com",
    api_version="2010-12-01",
    api_key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    default_sender_email=os.getenv("AWS_SES_FROM_EMAIL", "noreply@ia-influencer.com"),
    default_sender_name="IA Influencer Agent",
    supports_html_email=True,
    supports_attachments=True,
    supports_tracking=False,  # Requires additional setup
    supports_bounce_handling=True,
    supports_templating=True,
    rate_limit_per_minute=200,  # Depends on SES sending limits
    rate_limit_per_hour=12000,
    rate_limit_per_day=200000,
    cost_per_email=0.0001,  # Very cheap
    monthly_free_quota=62000,
    environments={
        "development": {
            "default_sender_email": "dev-noreply@ia-influencer.com"
        }
    }
)

# Twilio SMS Configuration
TWILIO_SMS_CONFIG = CommunicationAPIConfig(
    service_name="twilio",
    service_type=CommunicationServiceType.SMS_MESSAGING,
    base_url="https://api.twilio.com",
    api_version="2010-04-01",
    account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
    default_phone_number=os.getenv("TWILIO_PHONE_NUMBER"),
    supports_scheduling=True,
    supports_templating=False,  # Basic SMS
    supports_tracking=True,
    supports_analytics=True,
    rate_limit_per_minute=100,
    rate_limit_per_hour=6000,
    cost_per_sms=0.0075,  # US pricing
    monthly_free_quota=0,  # No free tier for SMS
    environments={
        "development": {
            "default_phone_number": os.getenv("TWILIO_TEST_PHONE_NUMBER")
        }
    }
)

# Firebase Cloud Messaging (Push Notifications)
FCM_CONFIG = CommunicationAPIConfig(
    service_name="firebase_messaging",
    service_type=CommunicationServiceType.PUSH_NOTIFICATIONS,
    base_url="https://fcm.googleapis.com",
    api_version="v1",
    api_key=os.getenv("FIREBASE_SERVER_KEY"),
    secret_key=os.getenv("FIREBASE_PROJECT_ID"),
    supports_scheduling=True,
    supports_templating=True,
    supports_personalization=True,
    supports_tracking=True,
    supports_analytics=True,
    rate_limit_per_minute=600,
    rate_limit_per_hour=36000,
    cost_per_push=0.0,  # Free
    monthly_free_quota=10000000,  # Very generous
    environments={
        "development": {
            "secret_key": os.getenv("FIREBASE_DEV_PROJECT_ID")
        },
        "staging": {
            "secret_key": os.getenv("FIREBASE_STAGING_PROJECT_ID")
        }
    }
)

# OneSignal Push Notifications Configuration
ONESIGNAL_CONFIG = CommunicationAPIConfig(
    service_name="onesignal",
    service_type=CommunicationServiceType.PUSH_NOTIFICATIONS,
    base_url="https://onesignal.com/api/v1",
    api_version="v1",
    api_key=os.getenv("ONESIGNAL_API_KEY"),
    secret_key=os.getenv("ONESIGNAL_APP_ID"),
    supports_scheduling=True,
    supports_templating=True,
    supports_personalization=True,
    supports_tracking=True,
    supports_analytics=True,
    rate_limit_per_minute=2000,
    cost_per_push=0.0005,
    monthly_free_quota=30000,
    environments={
        "development": {
            "secret_key": os.getenv("ONESIGNAL_DEV_APP_ID")
        },
        "staging": {
            "secret_key": os.getenv("ONESIGNAL_STAGING_APP_ID")
        }
    }
)

# Slack Configuration (Team Communication)
SLACK_CONFIG = CommunicationAPIConfig(
    service_name="slack",
    service_type=CommunicationServiceType.IN_APP_MESSAGING,
    base_url="https://slack.com/api",
    api_version="v1",
    api_key=os.getenv("SLACK_BOT_TOKEN"),
    secret_key=os.getenv("SLACK_WEBHOOK_URL"),
    supports_templating=True,
    supports_personalization=True,
    supports_attachments=True,
    rate_limit_per_minute=50,  # Conservative for Slack API
    cost_per_push=0.0,  # Free for basic usage
    monthly_free_quota=10000,
    environments={
        "development": {
            "api_key": os.getenv("SLACK_DEV_BOT_TOKEN"),
            "secret_key": os.getenv("SLACK_DEV_WEBHOOK_URL")
        }
    }
)

# Discord Configuration (Community Communication)
DISCORD_CONFIG = CommunicationAPIConfig(
    service_name="discord",
    service_type=CommunicationServiceType.IN_APP_MESSAGING,
    base_url="https://discord.com/api",
    api_version="v10",
    api_key=os.getenv("DISCORD_BOT_TOKEN"),
    secret_key=os.getenv("DISCORD_WEBHOOK_URL"),
    supports_templating=True,
    supports_attachments=True,
    rate_limit_per_minute=50,
    cost_per_push=0.0,
    monthly_free_quota=100000,
    environments={
        "development": {
            "api_key": os.getenv("DISCORD_DEV_BOT_TOKEN"),
            "secret_key": os.getenv("DISCORD_DEV_WEBHOOK_URL")
        }
    }
)

# WhatsApp Business API Configuration
WHATSAPP_CONFIG = CommunicationAPIConfig(
    service_name="whatsapp_business",
    service_type=CommunicationServiceType.SMS_MESSAGING,
    base_url="https://graph.facebook.com",
    api_version="v17.0",
    api_key=os.getenv("WHATSAPP_ACCESS_TOKEN"),
    secret_key=os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
    supports_templating=True,
    supports_personalization=True,
    supports_tracking=True,
    supports_analytics=True,
    rate_limit_per_minute=80,
    cost_per_sms=0.005,  # Varies by country
    monthly_free_quota=1000,
    environments={
        "development": {
            "api_key": os.getenv("WHATSAPP_TEST_ACCESS_TOKEN"),
            "secret_key": os.getenv("WHATSAPP_TEST_PHONE_NUMBER_ID")
        }
    }
)

# Custom Email Service Configuration
CUSTOM_EMAIL_CONFIG = CommunicationAPIConfig(
    service_name="custom_email",
    service_type=CommunicationServiceType.EMAIL_DELIVERY,
    base_url="https://api.ia-influencer.com/email",
    api_version="v1",
    api_key=os.getenv("CUSTOM_EMAIL_API_KEY"),
    default_sender_email="noreply@ia-influencer.com",
    default_sender_name="IA Influencer Agent",
    supports_html_email=True,
    supports_attachments=True,
    supports_tracking=True,
    supports_analytics=True,
    supports_bounce_handling=True,
    supports_unsubscribe=True,
    supports_scheduling=True,
    supports_templating=True,
    supports_personalization=True,
    rate_limit_per_minute=1000,
    cost_per_email=0.0,  # Internal service
    monthly_free_quota=10000000,
    environments={
        "development": {
            "base_url": "http://localhost:8000/api/email",
            "default_sender_email": "dev-noreply@localhost"
        },
        "staging": {
            "base_url": "https://staging-api.ia-influencer.com/email",
            "default_sender_email": "staging-noreply@ia-influencer.com"
        }
    }
)

# Communication configurations registry
COMMUNICATION_CONFIGS: Dict[str, CommunicationAPIConfig] = {
    "sendgrid": SENDGRID_CONFIG,
    "mailgun": MAILGUN_CONFIG,
    "aws_ses": AWS_SES_CONFIG,
    "twilio": TWILIO_SMS_CONFIG,
    "firebase_messaging": FCM_CONFIG,
    "onesignal": ONESIGNAL_CONFIG,
    "slack": SLACK_CONFIG,
    "discord": DISCORD_CONFIG,
    "whatsapp_business": WHATSAPP_CONFIG,
    "custom_email": CUSTOM_EMAIL_CONFIG
}

def get_communication_config(service: str) -> Optional[CommunicationAPIConfig]:
    """Get communication service configuration by name"""    return COMMUNICATION_CONFIGS.get(service.lower())

def get_services_by_type(service_type: CommunicationServiceType) -> List[CommunicationAPIConfig]:
    """Get all communication services of specific type"""    return [config for config in COMMUNICATION_CONFIGS.values() 
            if config.service_type == service_type]

def get_email_services() -> List[CommunicationAPIConfig]:
    """Get all email delivery services"""    return get_services_by_type(CommunicationServiceType.EMAIL_DELIVERY)

def get_sms_services() -> List[CommunicationAPIConfig]:
    """Get all SMS messaging services"""    return get_services_by_type(CommunicationServiceType.SMS_MESSAGING)

def get_push_notification_services() -> List[CommunicationAPIConfig]:
    """Get all push notification services"""    return get_services_by_type(CommunicationServiceType.PUSH_NOTIFICATIONS)

def get_services_with_templating() -> List[CommunicationAPIConfig]:
    """Get services that support message templating"""    return [config for config in COMMUNICATION_CONFIGS.values() 
            if config.supports_templating]

def get_services_with_analytics() -> List[CommunicationAPIConfig]:
    """Get services that support analytics tracking"""    return [config for config in COMMUNICATION_CONFIGS.values() 
            if config.supports_analytics]
