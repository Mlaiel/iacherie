"""
Notification Configuration Module
=================================

Enterprise notification system configuration for multi-channel communication.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


class NotificationType(str, Enum):
    """Types of notifications in the system."""
    # Content-related notifications
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_PROCESSED = "content_processed"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    CONTENT_FLAGGED = "content_flagged"
    
    # Protection and security notifications
    PROTECTION_VIOLATION_DETECTED = "protection_violation_detected"
    FINGERPRINT_MATCH_FOUND = "fingerprint_match_found"
    COPYRIGHT_CLAIM_RECEIVED = "copyright_claim_received"
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Collaboration notifications
    COLLABORATION_INVITATION = "collaboration_invitation"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_DECLINED = "collaboration_declined"
    COLLABORATION_COMPLETED = "collaboration_completed"
    COLLABORATION_REMINDER = "collaboration_reminder"
    
    # Financial notifications
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    REVENUE_REPORT_READY = "revenue_report_ready"
    PAYOUT_SCHEDULED = "payout_scheduled"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    BILLING_ISSUE = "billing_issue"
    
    # System notifications
    SYSTEM_MAINTENANCE = "system_maintenance"
    FEATURE_UPDATE = "feature_update"
    API_RATE_LIMIT_EXCEEDED = "api_rate_limit_exceeded"
    ACCOUNT_SUSPENDED = "account_suspended"
    LOGIN_ATTEMPT = "login_attempt"
    
    # Analytics and reporting
    ANALYTICS_REPORT_READY = "analytics_report_ready"
    PERFORMANCE_MILESTONE = "performance_milestone"
    ENGAGEMENT_SPIKE = "engagement_spike"
    
    # Administrative
    USER_REGISTRATION = "user_registration"
    SUPPORT_TICKET_UPDATE = "support_ticket_update"
    POLICY_UPDATE = "policy_update"


class NotificationChannel(str, Enum):
    """Available notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"


class NotificationPriority(str, Enum):
    """Priority levels for notifications."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class NotificationFrequency(str, Enum):
    """Frequency settings for recurring notifications."""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class NotificationTemplate:
    """Template definition for notifications."""
    subject: str
    body_text: str
    body_html: Optional[str] = None
    variables: List[str] = None
    localization_keys: Dict[str, str] = None


@dataclass
class NotificationRule:
    """Business rule for notification triggering."""
    notification_type: NotificationType
    trigger_conditions: Dict[str, Any]
    channels: List[NotificationChannel]
    priority: NotificationPriority
    frequency: NotificationFrequency
    user_roles: List[str]
    tenant_tiers: List[str]
    enabled: bool = True
    retry_count: int = 3
    cooldown_minutes: int = 0


class NotificationConfig:
    """Enterprise notification system configuration."""

    # Notification type configurations
    NOTIFICATION_CONFIGS = {
        NotificationType.CONTENT_UPLOADED: {
            "priority": NotificationPriority.MEDIUM,
            "default_channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            "user_configurable": True,
            "requires_user_action": False,
            "expires_after_hours": 24,
            "template_key": "content_upload_success",
            "variables": ["content_title", "upload_time", "processing_eta"],
            "trigger_delay_seconds": 0
        },
        NotificationType.CONTENT_PROCESSED: {
            "priority": NotificationPriority.MEDIUM,
            "default_channels": [NotificationChannel.IN_APP, NotificationChannel.PUSH_NOTIFICATION],
            "user_configurable": True,
            "requires_user_action": False,
            "expires_after_hours": 48,
            "template_key": "content_processing_complete",
            "variables": ["content_title", "processing_time", "next_steps"],
            "trigger_delay_seconds": 30
        },
        NotificationType.PROTECTION_VIOLATION_DETECTED: {
            "priority": NotificationPriority.CRITICAL,
            "default_channels": [
                NotificationChannel.EMAIL,
                NotificationChannel.SMS,
                NotificationChannel.PUSH_NOTIFICATION,
                NotificationChannel.IN_APP
            ],
            "user_configurable": False,
            "requires_user_action": True,
            "expires_after_hours": 72,
            "template_key": "protection_violation_alert",
            "variables": ["violation_type", "detected_platform", "similarity_score", "action_required"],
            "trigger_delay_seconds": 0,
            "escalation_hours": 2
        },
        NotificationType.COLLABORATION_INVITATION: {
            "priority": NotificationPriority.HIGH,
            "default_channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            "user_configurable": True,
            "requires_user_action": True,
            "expires_after_hours": 168,  # 7 days
            "template_key": "collaboration_invite",
            "variables": ["inviter_name", "collaboration_type", "project_details", "deadline"],
            "trigger_delay_seconds": 0,
            "reminder_intervals_hours": [24, 72, 144]
        },
        NotificationType.PAYMENT_PROCESSED: {
            "priority": NotificationPriority.HIGH,
            "default_channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            "user_configurable": True,
            "requires_user_action": False,
            "expires_after_hours": 720,  # 30 days
            "template_key": "payment_confirmation",
            "variables": ["amount", "currency", "transaction_id", "payment_method", "date"],
            "trigger_delay_seconds": 60,
            "receipt_attached": True
        },
        NotificationType.SYSTEM_MAINTENANCE: {
            "priority": NotificationPriority.HIGH,
            "default_channels": [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP,
                NotificationChannel.PUSH_NOTIFICATION
            ],
            "user_configurable": False,
            "requires_user_action": False,
            "expires_after_hours": 24,
            "template_key": "system_maintenance_notice",
            "variables": ["maintenance_start", "maintenance_end", "affected_services", "alternative_access"],
            "advance_notice_hours": 24,
            "reminder_intervals_hours": [24, 2, 0.5]
        },
        NotificationType.SUBSCRIPTION_EXPIRING: {
            "priority": NotificationPriority.HIGH,
            "default_channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            "user_configurable": True,
            "requires_user_action": True,
            "expires_after_hours": 720,  # 30 days
            "template_key": "subscription_expiration_warning",
            "variables": ["expiry_date", "plan_name", "renewal_link", "contact_support"],
            "advance_notice_days": [30, 14, 7, 3, 1],
            "auto_renewal_offer": True
        }
    }

    # Channel-specific configurations
    CHANNEL_CONFIGS = {
        NotificationChannel.EMAIL: {
            "provider": "ses",
            "rate_limit_per_hour": 1000,
            "template_format": "html",
            "tracking_enabled": True,
            "unsubscribe_link": True,
            "sender_name": "IA-Influencer Agent",
            "sender_email": "notifications@ia-influencer.com",
            "bounce_handling": True,
            "retry_attempts": 3,
            "retry_delay_minutes": [5, 15, 60]
        },
        NotificationChannel.SMS: {
            "provider": "twilio",
            "rate_limit_per_hour": 100,
            "max_message_length": 160,
            "international_support": True,
            "opt_out_keywords": ["STOP", "UNSUBSCRIBE"],
            "delivery_reports": True,
            "retry_attempts": 2,
            "retry_delay_minutes": [2, 10]
        },
        NotificationChannel.PUSH_NOTIFICATION: {
            "provider": "fcm",
            "platforms": ["ios", "android", "web"],
            "rate_limit_per_hour": 5000,
            "payload_max_size": 4096,
            "badge_updates": True,
            "sound_enabled": True,
            "retry_attempts": 3,
            "retry_delay_minutes": [1, 5, 15]
        },
        NotificationChannel.IN_APP: {
            "storage_duration_days": 30,
            "mark_read_after_view": True,
            "real_time_delivery": True,
            "batch_updates": False,
            "categorization": True,
            "search_enabled": True,
            "export_enabled": True
        },
        NotificationChannel.WEBHOOK: {
            "timeout_seconds": 30,
            "retry_attempts": 5,
            "retry_delay_minutes": [1, 2, 5, 10, 30],
            "signature_verification": True,
            "payload_encryption": True,
            "rate_limit_per_minute": 100,
            "dead_letter_queue": True
        },
        NotificationChannel.SLACK: {
            "rate_limit_per_minute": 1,
            "message_formatting": "markdown",
            "thread_replies": True,
            "emoji_reactions": True,
            "file_attachments": True,
            "channel_types": ["direct_message", "channel", "private_group"]
        }
    }

    # User preference templates
    USER_PREFERENCE_TEMPLATES = {
        "creator_standard": {
            NotificationType.CONTENT_UPLOADED: [NotificationChannel.IN_APP],
            NotificationType.CONTENT_PROCESSED: [NotificationChannel.IN_APP, NotificationChannel.PUSH_NOTIFICATION],
            NotificationType.PROTECTION_VIOLATION_DETECTED: [
                NotificationChannel.EMAIL,
                NotificationChannel.PUSH_NOTIFICATION,
                NotificationChannel.IN_APP
            ],
            NotificationType.COLLABORATION_INVITATION: [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            NotificationType.PAYMENT_PROCESSED: [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            NotificationType.SYSTEM_MAINTENANCE: [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            "quiet_hours": {"start": "22:00", "end": "08:00"},
            "timezone": "auto_detect",
            "language": "en",
            "digest_frequency": NotificationFrequency.DAILY
        },
        "creator_professional": {
            NotificationType.CONTENT_UPLOADED: [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            NotificationType.CONTENT_PROCESSED: [
                NotificationChannel.IN_APP,
                NotificationChannel.PUSH_NOTIFICATION,
                NotificationChannel.SLACK
            ],
            NotificationType.PROTECTION_VIOLATION_DETECTED: [
                NotificationChannel.EMAIL,
                NotificationChannel.SMS,
                NotificationChannel.PUSH_NOTIFICATION,
                NotificationChannel.IN_APP,
                NotificationChannel.SLACK
            ],
            NotificationType.COLLABORATION_INVITATION: [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP,
                NotificationChannel.PUSH_NOTIFICATION
            ],
            NotificationType.PAYMENT_PROCESSED: [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            NotificationType.ANALYTICS_REPORT_READY: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
            "quiet_hours": {"start": "23:00", "end": "07:00"},
            "timezone": "auto_detect",
            "language": "en",
            "digest_frequency": NotificationFrequency.WEEKLY,
            "webhook_url": "configurable"
        },
        "tenant_admin": {
            # All notifications enabled with multiple channels
            "default_channels": [
                NotificationChannel.EMAIL,
                NotificationChannel.IN_APP,
                NotificationChannel.PUSH_NOTIFICATION
            ],
            "critical_channels": [
                NotificationChannel.EMAIL,
                NotificationChannel.SMS,
                NotificationChannel.PUSH_NOTIFICATION,
                NotificationChannel.SLACK
            ],
            "quiet_hours": {"start": "00:00", "end": "06:00"},
            "timezone": "auto_detect",
            "language": "en",
            "digest_frequency": NotificationFrequency.IMMEDIATE,
            "escalation_enabled": True
        }
    }

    # Notification templates
    TEMPLATES = {
        "content_upload_success": NotificationTemplate(
            subject="Content Upload Successful - {content_title}",
            body_text="""
            Hi {user_name},

            Your content "{content_title}" has been successfully uploaded to IA-Influencer Agent.

            Upload Details:
            - File: {content_title}
            - Upload Time: {upload_time}
            - Processing ETA: {processing_eta}

            Next Steps:
            Your content is now being processed for fingerprinting and protection. You'll receive another notification once processing is complete.

            Thank you for using IA-Influencer Agent!

            Best regards,
            The IA-Influencer Team
            """,
            variables=["user_name", "content_title", "upload_time", "processing_eta"]
        ),
        "protection_violation_alert": NotificationTemplate(
            subject="URGENT: Copyright Protection Violation Detected",
            body_text="""
            Hi {user_name},

            We've detected a potential copyright violation of your protected content:

            Content: {content_title}
            Violation Type: {violation_type}
            Platform: {detected_platform}
            Similarity Score: {similarity_score}%
            Detection Time: {detection_time}

            IMMEDIATE ACTION REQUIRED:
            {action_required}

            View full details and take action: {action_link}

            This is an automated alert from IA-Influencer Agent content protection system.
            """,
            variables=[
                "user_name", "content_title", "violation_type", 
                "detected_platform", "similarity_score", "detection_time", "action_required", "action_link"
            ]
        ),
        "collaboration_invite": NotificationTemplate(
            subject="Collaboration Invitation from {inviter_name}",
            body_text="""
            Hi {recipient_name},

            You've received a collaboration invitation!

            From: {inviter_name}
            Type: {collaboration_type}
            Project: {project_details}
            Deadline: {deadline}

            Review and respond to this invitation: {invitation_link}

            This invitation will expire in 7 days.

            Best regards,
            IA-Influencer Agent Team
            """,
            variables=["recipient_name", "inviter_name", "collaboration_type", "project_details", "deadline", "invitation_link"]
        )
    }

    # Notification business rules
    BUSINESS_RULES = {
        "rate_limiting": {
            "same_type_cooldown_minutes": 5,
            "user_hourly_limit": 20,
            "user_daily_limit": 100,
            "critical_bypass_limits": True,
            "tenant_rate_limits": {
                "starter": 500,
                "professional": 2000,
                "enterprise": 10000
            }
        },
        "delivery_optimization": {
            "batch_non_critical": True,
            "intelligent_timing": True,
            "timezone_awareness": True,
            "quiet_hours_respect": True,
            "channel_fallback": True,
            "retry_strategy": "exponential_backoff"
        },
        "privacy_compliance": {
            "data_retention_days": 365,
            "anonymization_enabled": True,
            "consent_required": True,
            "unsubscribe_honor": True,
            "gdpr_compliant": True,
            "ccpa_compliant": True
        }
    }

    # Analytics and monitoring
    ANALYTICS_CONFIG = {
        "delivery_tracking": True,
        "open_rate_tracking": True,
        "click_through_tracking": True,
        "engagement_scoring": True,
        "performance_metrics": [
            "delivery_rate",
            "open_rate",
            "click_rate",
            "conversion_rate",
            "unsubscribe_rate",
            "bounce_rate"
        ],
        "reporting_frequency": "weekly",
        "retention_period_days": 365
    }

    @classmethod
    def get_notification_config(cls, notification_type: NotificationType) -> Dict[str, Any]:
        """Get configuration for specific notification type."""



        return cls.NOTIFICATION_CONFIGS.get(notification_type, {})

    @classmethod
    def get_channel_config(cls, channel: NotificationChannel) -> Dict[str, Any]:
        """Get configuration for specific notification channel."""



        return cls.CHANNEL_CONFIGS.get(channel, {})

    @classmethod
    def get_user_preferences(cls, user_role: str) -> Dict[str, Any]:
        """Get default notification preferences for user role."""



        return cls.USER_PREFERENCE_TEMPLATES.get(user_role, cls.USER_PREFERENCE_TEMPLATES["creator_standard"])

    @classmethod
    def should_send_notification(cls, notification_type: NotificationType, user_id: str, 
                               current_time: datetime, last_sent: Optional[datetime] = None) -> bool:
        """Determine if notification should be sent based on business rules."""
        config = cls.get_notification_config(notification_type)
        rules = cls.BUSINESS_RULES["rate_limiting"]
        
        # Check cooldown period
        if last_sent and config.get("cooldown_minutes", 0) > 0:
            cooldown_period = timedelta(minutes=config["cooldown_minutes"])
            if current_time - last_sent < cooldown_period:
                return False
        
        # Check if it's critical notification (bypasses limits)
        if config.get("priority") == NotificationPriority.CRITICAL:
            return True
        
        # Check quiet hours (would integrate with user preferences)
        # This is a simplified check - real implementation would use user timezone
        if 0 <= current_time.hour <= 6:  # Quiet hours
            if config.get("priority") not in [NotificationPriority.CRITICAL, NotificationPriority.HIGH]:
                return False
        
        return True

    @classmethod
    def get_template(cls, template_key: str) -> Optional[NotificationTemplate]:
        """Get notification template by key."""



        return cls.TEMPLATES.get(template_key)

    @classmethod
    def validate_notification_channels(cls, channels: List[NotificationChannel], 
                                     user_preferences: Dict[str, Any]) -> List[NotificationChannel]:
        """Validate and filter notification channels based on user preferences."""
        valid_channels = []
        
        for channel in channels:
            # Check if channel is available
            if channel not in cls.CHANNEL_CONFIGS:
                continue
            
            # Check user preferences and opt-outs
            if user_preferences.get(f"{channel.value}_enabled", True):
                valid_channels.append(channel)
        
        return valid_channels

    @classmethod
    def calculate_notification_priority(cls, notification_type: NotificationType, 
                                      context: Dict[str, Any]) -> NotificationPriority:
        """Calculate dynamic notification priority based on context."""
        base_priority = cls.NOTIFICATION_CONFIGS.get(notification_type, {}).get("priority", NotificationPriority.MEDIUM)
        
        # Upgrade priority based on context
        if context.get("security_threat", False):
            return NotificationPriority.CRITICAL
        
        if context.get("revenue_impact", False):
            if base_priority == NotificationPriority.MEDIUM:
                return NotificationPriority.HIGH
        
        if context.get("user_tier") == "enterprise":
            if base_priority == NotificationPriority.LOW:
                return NotificationPriority.MEDIUM
        
        return base_priority
