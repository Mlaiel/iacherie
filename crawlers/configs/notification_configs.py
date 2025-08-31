"""
Advanced Notification and Communication Configurations
=====================================================

Comprehensive notification system for alerts, reports, and communication management.
Supports multi-channel delivery, escalation policies, and intelligent routing.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    PUSH = "push"
    TELEGRAM = "telegram"
    TEAMS = "teams"
    WHATSAPP = "whatsapp"
    VOICE_CALL = "voice_call"

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class EscalationAction(Enum):
    """Escalation actions."""
    NOTIFY_MANAGER = "notify_manager"
    CREATE_INCIDENT = "create_incident"
    AUTO_REMEDIATE = "auto_remediate"
    DISABLE_SERVICE = "disable_service"
    EMERGENCY_CONTACT = "emergency_contact"

class MessageFormat(Enum):
    """Message formats."""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"

class DeliveryStatus(Enum):
    """Delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class ChannelConfig:
    """Configuration for individual notification channel."""
    channel: NotificationChannel
    enabled: bool = True
    priority_threshold: NotificationPriority = NotificationPriority.NORMAL
    
    # Channel-specific settings
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_hour: int = 100
    burst_limit: int = 10
    cooldown_minutes: int = 5
    
    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: int = 30
    exponential_backoff: bool = True
    
    # Message formatting
    message_format: MessageFormat = MessageFormat.TEXT
    include_metadata: bool = True
    template_path: Optional[str] = None
    
    # Filtering
    keyword_filters: List[str] = field(default_factory=list)
    source_filters: List[str] = field(default_factory=list)
    severity_filters: List[str] = field(default_factory=list)

@dataclass
class RecipientConfig:
    """Configuration for notification recipients."""
    recipient_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    slack_user_id: Optional[str] = None
    telegram_user_id: Optional[str] = None
    
    # Preferences
    preferred_channels: List[NotificationChannel] = field(default_factory=list)
    timezone: str = "UTC"
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    
    # Escalation
    manager_id: Optional[str] = None
    escalation_delay_minutes: int = 30
    emergency_contact: bool = False
    
    # Subscription settings
    subscribed_categories: List[str] = field(default_factory=list)
    minimum_priority: NotificationPriority = NotificationPriority.NORMAL
    enabled: bool = True

@dataclass
class NotificationTemplate:
    """Template for notification messages."""
    template_id: str
    name: str
    category: str
    subject_template: str
    body_template: str
    
    # Template settings
    template_format: MessageFormat = MessageFormat.TEXT
    variables: List[str] = field(default_factory=list)
    required_variables: List[str] = field(default_factory=list)
    
    # Localization
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    default_language: str = "en"
    
    # Validation
    max_subject_length: int = 200
    max_body_length: int = 4000
    allow_html: bool = False

@dataclass
class EscalationPolicy:
    """Configuration for escalation policies."""
    policy_id: str
    name: str
    description: str
    enabled: bool = True
    
    # Trigger conditions
    trigger_priorities: List[NotificationPriority] = field(default_factory=list)
    trigger_categories: List[str] = field(default_factory=list)
    trigger_keywords: List[str] = field(default_factory=list)
    
    # Escalation steps
    escalation_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    initial_delay_minutes: int = 0
    step_delay_minutes: int = 15
    max_escalation_time_hours: int = 24
    
    # Actions
    auto_acknowledge: bool = False
    create_incident: bool = True
    notify_on_call: bool = True

@dataclass
class AlertingConfig:
    """Configuration for alerting system."""
    enabled: bool = True
    
    # Alert processing
    deduplication_enabled: bool = True
    deduplication_window_minutes: int = 5
    grouping_enabled: bool = True
    grouping_window_minutes: int = 10
    
    # Rate limiting
    alert_rate_limiting: bool = True
    max_alerts_per_minute: int = 50
    burst_threshold: int = 100
    
    # Filtering
    noise_reduction: bool = True
    spam_detection: bool = True
    correlation_analysis: bool = True
    
    # Storage
    alert_retention_days: int = 90
    archive_old_alerts: bool = True
    compress_archived_alerts: bool = True

@dataclass
class DeliveryConfig:
    """Configuration for message delivery."""
    enabled: bool = True
    
    # Delivery options
    parallel_delivery: bool = True
    max_concurrent_deliveries: int = 10
    delivery_timeout_seconds: int = 30
    
    # Reliability
    delivery_confirmation: bool = True
    read_receipts: bool = False
    delivery_tracking: bool = True
    
    # Retry logic
    auto_retry_failed: bool = True
    max_retry_attempts: int = 3
    retry_backoff_multiplier: float = 2.0
    
    # Fallback
    fallback_channels: List[NotificationChannel] = field(default_factory=list)
    emergency_fallback: NotificationChannel = NotificationChannel.EMAIL

class NotificationConfigManager:
    """Manager for notification configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize notification configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.channels: Dict[str, ChannelConfig] = {}
        self.recipients: Dict[str, RecipientConfig] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.alerting = AlertingConfig()
        self.delivery = DeliveryConfig()
        self._load_configurations()
        self._setup_default_channels()
        self._setup_default_templates()
    
    def _load_configurations(self) -> None:
        """Load notification configurations from files."""



        try:
            config_file = self.config_dir / "notification_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load channels
                    for channel_id, channel_data in data.get('channels', {}).items():
                        self.channels[channel_id] = ChannelConfig(**channel_data)
                    # Load recipients
                    for recipient_id, recipient_data in data.get('recipients', {}).items():
                        self.recipients[recipient_id] = RecipientConfig(**recipient_data)
        except Exception as e:
            print(f"Error loading notification configurations: {e}")
    
    def _setup_default_channels(self) -> None:
        """Setup default notification channels."""
        default_channels = [
            ChannelConfig(
                channel=NotificationChannel.EMAIL,
                enabled=True,
                endpoint_url="smtp://localhost:587",
                rate_limit_per_hour=1000,
                message_format=MessageFormat.HTML
            ),
            ChannelConfig(
                channel=NotificationChannel.SLACK,
                enabled=False,
                priority_threshold=NotificationPriority.HIGH,
                rate_limit_per_hour=500,
                message_format=MessageFormat.MARKDOWN
            ),
            ChannelConfig(
                channel=NotificationChannel.WEBHOOK,
                enabled=True,
                rate_limit_per_hour=2000,
                message_format=MessageFormat.JSON
            ),
            ChannelConfig(
                channel=NotificationChannel.SMS,
                enabled=False,
                priority_threshold=NotificationPriority.URGENT,
                rate_limit_per_hour=50,
                max_retries=5
            )
        ]
        
        for channel in default_channels:
            channel_id = channel.channel.value
            if channel_id not in self.channels:
                self.channels[channel_id] = channel
    
    def _setup_default_templates(self) -> None:
        """Setup default notification templates."""
        default_templates = [
            NotificationTemplate(
                template_id="security_alert",
                name="Security Alert",
                category="security",
                subject_template="[SECURITY] {alert_type} - {severity}",
                body_template="""
Security Alert Detected

Alert Type: {alert_type}
Severity: {severity}
Time: {timestamp}
Source: {source}
Description: {description}

Details:
{details}

Please investigate immediately.
                """.strip(),
                variables=["alert_type", "severity", "timestamp", "source", "description", "details"],
                required_variables=["alert_type", "severity", "timestamp"]
            ),
            NotificationTemplate(
                template_id="system_error",
                name="System Error",
                category="system",
                subject_template="[ERROR] System Error in {component}",
                body_template="""
System Error Detected

Component: {component}
Error: {error_message}
Time: {timestamp}
Severity: {severity}

Stack Trace:
{stack_trace}

Please check system status.
                """.strip(),
                variables=["component", "error_message", "timestamp", "severity", "stack_trace"],
                required_variables=["component", "error_message", "timestamp"]
            ),
            NotificationTemplate(
                template_id="content_violation",
                name="Content Violation",
                category="content",
                subject_template="[VIOLATION] Content violation detected",
                body_template="""
Content Violation Detected

Platform: {platform}
Content URL: {content_url}
Violation Type: {violation_type}
Confidence: {confidence}%
Time: {timestamp}

Protected Content:
- Title: {original_title}
- Owner: {content_owner}

Action Required: Review and take appropriate action.
                """.strip(),
                variables=["platform", "content_url", "violation_type", "confidence", "timestamp", "original_title", "content_owner"],
                required_variables=["platform", "violation_type", "timestamp"]
            ),
            NotificationTemplate(
                template_id="performance_alert",
                name="Performance Alert",
                category="performance",
                subject_template="[PERFORMANCE] {metric_name} threshold exceeded",
                body_template="""
Performance Alert

Metric: {metric_name}
Current Value: {current_value}
Threshold: {threshold}
Time: {timestamp}

Impact: {impact_description}

Recommended Actions:
{recommendations}
                """.strip(),
                variables=["metric_name", "current_value", "threshold", "timestamp", "impact_description", "recommendations"],
                required_variables=["metric_name", "current_value", "threshold", "timestamp"]
            )
        ]
        
        for template in default_templates:
            if template.template_id not in self.templates:
                self.templates[template.template_id] = template
    
    def register_channel(self, channel_config: ChannelConfig) -> None:
        """Register a new notification channel."""
        channel_id = channel_config.channel.value
        self.channels[channel_id] = channel_config
        self._save_configurations()
    
    def register_recipient(self, recipient_config: RecipientConfig) -> None:
        """Register a new notification recipient."""
        self.recipients[recipient_config.recipient_id] = recipient_config
        self._save_configurations()
    
    def register_template(self, template: NotificationTemplate) -> None:
        """Register a new notification template."""
        self.templates[template.template_id] = template
        self._save_configurations()
    
    def register_escalation_policy(self, policy: EscalationPolicy) -> None:
        """Register a new escalation policy."""
        self.escalation_policies[policy.policy_id] = policy
        self._save_configurations()
    
    def get_enabled_channels(self, priority: Optional[NotificationPriority] = None) -> List[ChannelConfig]:
        """Get enabled channels, optionally filtered by priority."""
        channels = [c for c in self.channels.values() if c.enabled]
        
        if priority:
            priority_order = {
                NotificationPriority.LOW: 1,
                NotificationPriority.NORMAL: 2,
                NotificationPriority.HIGH: 3,
                NotificationPriority.URGENT: 4,
                NotificationPriority.CRITICAL: 5
            }
            min_priority = priority_order.get(priority, 1)
            channels = [c for c in channels if priority_order.get(c.priority_threshold, 1) <= min_priority]
        
        return channels
    
    def get_recipients_for_category(self, category: str, priority: NotificationPriority) -> List[RecipientConfig]:
        """Get recipients subscribed to a category with sufficient priority."""
        recipients = []
        priority_order = {
            NotificationPriority.LOW: 1,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.HIGH: 3,
            NotificationPriority.URGENT: 4,
            NotificationPriority.CRITICAL: 5
        }
        
        for recipient in self.recipients.values():
            if (recipient.enabled and 
                category in recipient.subscribed_categories and
                priority_order.get(priority, 1) >= priority_order.get(recipient.minimum_priority, 1)):
                recipients.append(recipient)
        
        return recipients
    
    def format_message(self, template_id: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """Format a message using a template."""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Check required variables
        missing_vars = [var for var in template.required_variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Format subject and body
        try:
            subject = template.subject_template.format(**variables)
            body = template.body_template.format(**variables)
            
            return {
                "subject": subject,
                "body": body,
                "format": template.template_format.value
            }
        except KeyError as e:
            raise ValueError(f"Template variable not provided: {e}")
    
    def should_escalate(self, alert_data: Dict[str, Any]) -> Optional[EscalationPolicy]:
        """Check if an alert should be escalated and return the policy."""
        for policy in self.escalation_policies.values():
            if not policy.enabled:
                continue
            
            # Check priority
            alert_priority = alert_data.get('priority')
            if (policy.trigger_priorities and 
                alert_priority not in [p.value for p in policy.trigger_priorities]):
                continue
            
            # Check category
            alert_category = alert_data.get('category')
            if (policy.trigger_categories and 
                alert_category not in policy.trigger_categories):
                continue
            
            # Check keywords
            alert_text = f"{alert_data.get('subject', '')} {alert_data.get('body', '')}"
            if (policy.trigger_keywords and 
                not any(keyword.lower() in alert_text.lower() for keyword in policy.trigger_keywords)):
                continue
            
            return policy
        
        return None
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate notification configuration."""
        issues = {"errors": [], "warnings": []}
        
        # Check if at least one channel is enabled
        enabled_channels = self.get_enabled_channels()
        if not enabled_channels:
            issues["errors"].append("No notification channels are enabled")
        
        # Check channel configurations
        for channel_id, channel in self.channels.items():
            if channel.enabled:
                if channel.channel in [NotificationChannel.EMAIL, NotificationChannel.WEBHOOK]:
                    if not channel.endpoint_url:
                        issues["warnings"].append(f"Channel {channel_id} missing endpoint URL")
                
                if channel.rate_limit_per_hour < 1:
                    issues["warnings"].append(f"Channel {channel_id} has very low rate limit")
        
        # Check recipients
        if not self.recipients:
            issues["warnings"].append("No notification recipients configured")
        
        # Check templates
        for template_id, template in self.templates.items():
            if len(template.required_variables) == 0:
                issues["warnings"].append(f"Template {template_id} has no required variables")
        
        return issues
    
    def _save_configurations(self) -> None:
        """Save configurations to file."""



        try:
            config_file = self.config_dir / "notification_config.json"
            config_data = {
                "channels": {
                    channel_id: {
                        "channel": channel.channel.value,
                        "enabled": channel.enabled,
                        "priority_threshold": channel.priority_threshold.value,
                        "endpoint_url": channel.endpoint_url,
                        "rate_limit_per_hour": channel.rate_limit_per_hour,
                        "message_format": channel.message_format.value
                    }
                    for channel_id, channel in self.channels.items()
                },
                "recipients": {
                    recipient_id: {
                        "recipient_id": recipient.recipient_id,
                        "name": recipient.name,
                        "email": recipient.email,
                        "phone": recipient.phone,
                        "preferred_channels": [ch.value for ch in recipient.preferred_channels],
                        "subscribed_categories": recipient.subscribed_categories,
                        "minimum_priority": recipient.minimum_priority.value,
                        "enabled": recipient.enabled
                    }
                    for recipient_id, recipient in self.recipients.items()
                },
                "templates": {
                    template_id: {
                        "template_id": template.template_id,
                        "name": template.name,
                        "category": template.category,
                        "subject_template": template.subject_template,
                        "body_template": template.body_template,
                        "variables": template.variables,
                        "required_variables": template.required_variables
                    }
                    for template_id, template in self.templates.items()
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving notification configurations: {e}")

# Global notification configuration manager
notification_config_manager = NotificationConfigManager()

# Notification presets for different environments
NOTIFICATION_PRESETS = {
    "development": {
        "channels": {
            "email": {"enabled": True, "rate_limit_per_hour": 100},
            "slack": {"enabled": False},
            "sms": {"enabled": False}
        },
        "alerting": {
            "deduplication_enabled": False,
            "alert_rate_limiting": False
        }
    },
    "staging": {
        "channels": {
            "email": {"enabled": True, "rate_limit_per_hour": 500},
            "slack": {"enabled": True, "priority_threshold": "high"},
            "sms": {"enabled": False}
        },
        "alerting": {
            "deduplication_enabled": True,
            "alert_rate_limiting": True
        }
    },
    "production": {
        "channels": {
            "email": {"enabled": True, "rate_limit_per_hour": 1000},
            "slack": {"enabled": True, "priority_threshold": "normal"},
            "sms": {"enabled": True, "priority_threshold": "urgent"},
            "webhook": {"enabled": True}
        },
        "alerting": {
            "deduplication_enabled": True,
            "alert_rate_limiting": True,
            "noise_reduction": True
        }
    }
}
