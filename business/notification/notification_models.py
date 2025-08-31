"""
Notification Models - Data Models and DTOs for Business Notification System

Comprehensive data models and data transfer objects for the IA Influencer Agent
notification system. Defines structure for requests, responses, templates,
channels, workflows, analytics, and business rules.

Business Integration:
- Multi-format content creator support data structures
- AI content protection notification schemas
- Collaboration matching and partnership data models
- Monetization opportunity and revenue tracking models
- SEO optimization and performance analytics schemas
- Multi-platform distribution status models

Data Models:
- NotificationRequest: Complete notification request with business context
- NotificationResponse: Delivery response with status and metadata
- NotificationTemplate: Template structure with personalization support
- NotificationChannel: Channel configuration and performance metrics
- NotificationWorkflow: Complex workflow definitions and state management
- NotificationAnalytics: Performance analytics and business intelligence
- UserPreferences: Granular user preference management
- BusinessRules: Configurable business logic and validation rules

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
from uuid import uuid4


# Enumerations

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DeliveryStatus(Enum):
    """Notification delivery status."""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    PARTIALLY_DELIVERED = "partially_delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class ChannelType(Enum):
    """Supported notification channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class NotificationType(Enum):
    """Business notification types."""
    # Content Protection
    CONTENT_PROTECTION = "content_protection"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    PROTECTION_ALERT = "protection_alert"
    RIGHTS_VIOLATION = "rights_violation"
    
    # Collaboration & Partnership
    COLLABORATION_MATCH = "collaboration_match"
    PARTNERSHIP_OPPORTUNITY = "partnership_opportunity"
    COLLABORATION_REQUEST = "collaboration_request"
    PARTNERSHIP_PROPOSAL = "partnership_proposal"
    
    # Monetization & Revenue
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"
    REVENUE_ALERT = "revenue_alert"
    PAYMENT_NOTIFICATION = "payment_notification"
    EARNINGS_UPDATE = "earnings_update"
    
    # SEO & Performance
    SEO_OPTIMIZATION = "seo_optimization"
    PERFORMANCE_ALERT = "performance_alert"
    RANKING_UPDATE = "ranking_update"
    ANALYTICS_REPORT = "analytics_report"
    
    # Distribution & Platform
    DISTRIBUTION_STATUS = "distribution_status"
    PLATFORM_SYNC = "platform_sync"
    CONTENT_PUBLISHED = "content_published"
    DISTRIBUTION_COMPLETE = "distribution_complete"
    
    # System & Security
    SECURITY_ALERT = "security_alert"
    SYSTEM_NOTIFICATION = "system_notification"
    ACCOUNT_UPDATE = "account_update"
    
    # Engagement & User Experience
    ONBOARDING = "onboarding"
    ENGAGEMENT = "engagement"
    MILESTONE = "milestone"
    WELCOME = "welcome"


class ProcessingStage(Enum):
    """Notification processing stages."""
    VALIDATION = "validation"
    PRIORITY_CLASSIFICATION = "priority_classification"
    TEMPLATE_PROCESSING = "template_processing"
    PERSONALIZATION = "personalization"
    CHANNEL_SELECTION = "channel_selection"
    DELIVERY = "delivery"
    ANALYTICS = "analytics"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Data Transfer Objects

@dataclass
class NotificationContent:
    """Notification content structure."""
    subject: Optional[str] = None
    title: Optional[str] = None
    message: str = ""
    html_content: Optional[str] = None
    markdown_content: Optional[str] = None
    rich_content: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    action_buttons: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationRecipient:
    """Notification recipient information."""
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    push_tokens: Optional[List[str]] = None
    webhook_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    language: str = "en"
    user_type: Optional[str] = None  # musician, blogger, photographer, influencer, comedian
    business_context: Optional[Dict[str, Any]] = None


@dataclass
class NotificationRequest:
    """Complete notification request with business context."""
    notification_id: str = field(default_factory=lambda: str(uuid4()))
    notification_type: str = ""
    recipient: NotificationRecipient = field(default_factory=lambda: NotificationRecipient(""))
    content: NotificationContent = field(default_factory=NotificationContent)
    priority: str = NotificationPriority.MEDIUM.value
    channels: Optional[List[str]] = None
    delivery_time: Optional[str] = None  # immediate, scheduled, optimal
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    template_id: Optional[str] = None
    personalization_data: Optional[Dict[str, Any]] = None
    business_context: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None
    parent_notification_id: Optional[str] = None
    urgency_score: Optional[float] = None
    retry_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""



        return {
            "notification_id": self.notification_id,
            "notification_type": self.notification_type,
            "recipient": {
                "user_id": self.recipient.user_id,
                "email": self.recipient.email,
                "phone": self.recipient.phone,
                "push_tokens": self.recipient.push_tokens,
                "webhook_url": self.recipient.webhook_url,
                "preferences": self.recipient.preferences,
                "timezone": self.recipient.timezone,
                "language": self.recipient.language,
                "user_type": self.recipient.user_type,
                "business_context": self.recipient.business_context
            },
            "content": {
                "subject": self.content.subject,
                "title": self.content.title,
                "message": self.content.message,
                "html_content": self.content.html_content,
                "markdown_content": self.content.markdown_content,
                "rich_content": self.content.rich_content,
                "attachments": self.content.attachments,
                "action_buttons": self.content.action_buttons,
                "metadata": self.content.metadata
            },
            "priority": self.priority,
            "channels": self.channels,
            "delivery_time": self.delivery_time,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "template_id": self.template_id,
            "personalization_data": self.personalization_data,
            "business_context": self.business_context,
            "workflow_id": self.workflow_id,
            "parent_notification_id": self.parent_notification_id,
            "urgency_score": self.urgency_score,
            "retry_config": self.retry_config,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class NotificationResponse:
    """Notification delivery response."""
    notification_id: str
    status: DeliveryStatus
    message: str
    timestamp: datetime
    delivery_channels: Optional[List[str]] = None
    delivery_details: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    retry_count: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""



        return {
            "notification_id": self.notification_id,
            "status": self.status.value if isinstance(self.status, DeliveryStatus) else self.status,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "delivery_channels": self.delivery_channels,
            "delivery_details": self.delivery_details,
            "processing_time": self.processing_time,
            "retry_count": self.retry_count,
            "error_details": self.error_details,
            "metadata": self.metadata
        }


@dataclass
class NotificationTemplate:
    """Notification template with personalization support."""
    template_id: str
    template_name: str
    notification_type: str
    version: str = "1.0"
    language: str = "en"
    channel_templates: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    personalization_rules: Optional[Dict[str, Any]] = None
    business_rules: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    fallback_template: Optional[str] = None
    a_b_test_config: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    is_active: bool = True
    
    def get_template_for_channel(self, channel: str) -> Optional[Dict[str, Any]]:
        """Get template configuration for specific channel."""



        return self.channel_templates.get(channel)
    
    def add_channel_template(self, channel: str, template_config: Dict[str, Any]):
        """Add template configuration for specific channel."""
        self.channel_templates[channel] = template_config
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class NotificationChannel:
    """Notification channel configuration and metrics."""
    channel_id: str
    channel_type: ChannelType
    name: str
    is_enabled: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Optional[Dict[str, int]] = None
    retry_config: Optional[Dict[str, Any]] = None
    cost_per_notification: Optional[float] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    health_status: str = "healthy"
    last_health_check: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def update_performance_metrics(self, delivery_time: float, success: bool):
        """Update channel performance metrics."""
        if "total_sent" not in self.performance_metrics:
            self.performance_metrics["total_sent"] = 0
        if "successful_deliveries" not in self.performance_metrics:
            self.performance_metrics["successful_deliveries"] = 0
        if "average_delivery_time" not in self.performance_metrics:
            self.performance_metrics["average_delivery_time"] = 0.0
        
        self.performance_metrics["total_sent"] += 1
        if success:
            self.performance_metrics["successful_deliveries"] += 1
        
        # Update average delivery time
        total = self.performance_metrics["total_sent"]
        current_avg = self.performance_metrics["average_delivery_time"]
        self.performance_metrics["average_delivery_time"] = (
            (current_avg * (total - 1) + delivery_time) / total
        )
    
    def get_success_rate(self) -> float:
        """Calculate channel success rate."""
        total = self.performance_metrics.get("total_sent", 0)
        successful = self.performance_metrics.get("successful_deliveries", 0)
        return (successful / total * 100) if total > 0 else 0.0


@dataclass
class NotificationWorkflow:
    """Complex notification workflow definition."""
    workflow_id: str
    workflow_name: str
    workflow_type: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = None
    business_rules: Optional[Dict[str, Any]] = None
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_step: int = 0
    completed_steps: List[int] = field(default_factory=list)
    failed_steps: List[int] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    def add_step(self, step_config: Dict[str, Any]):
        """Add step to workflow."""
        step_config["step_id"] = len(self.steps)
        self.steps.append(step_config)
    
    def mark_step_completed(self, step_id: int, execution_data: Optional[Dict[str, Any]] = None):
        """Mark workflow step as completed."""
        if step_id not in self.completed_steps:
            self.completed_steps.append(step_id)
        
        # Record execution history
        self.execution_history.append({
            "step_id": step_id,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_data": execution_data
        })
        
        # Update current step
        if step_id == self.current_step:
            self.current_step += 1
    
    def mark_step_failed(self, step_id: int, error: str):
        """Mark workflow step as failed."""
        if step_id not in self.failed_steps:
            self.failed_steps.append(step_id)
        
        # Record execution history
        self.execution_history.append({
            "step_id": step_id,
            "status": "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error
        })
        
        # Update workflow status
        self.status = WorkflowStatus.FAILED


@dataclass
class NotificationMetrics:
    """Comprehensive notification metrics and analytics."""
    metric_id: str = field(default_factory=lambda: str(uuid4()))
    time_period: str = "24h"
    notification_type: Optional[str] = None
    total_sent: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    partially_delivered: int = 0
    average_processing_time: float = 0.0
    average_delivery_time: float = 0.0
    channel_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    business_metrics: Dict[str, Any] = field(default_factory=dict)
    cost_metrics: Dict[str, float] = field(default_factory=dict)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate."""
        total = self.total_sent
        successful = self.successful_deliveries + self.partially_delivered
        return (successful / total * 100) if total > 0 else 0.0
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate."""



        return 100.0 - self.get_success_rate()
    
    def add_delivery_metric(
        self,
        channel: str,
        delivery_time: float,
        success: bool,
        cost: Optional[float] = None
    ):
        """Add delivery metric data."""
        # Update overall metrics
        self.total_sent += 1
        if success:
            self.successful_deliveries += 1
        else:
            self.failed_deliveries += 1
        
        # Update channel performance
        if channel not in self.channel_performance:
            self.channel_performance[channel] = {
                "total_sent": 0,
                "successful": 0,
                "average_delivery_time": 0.0,
                "success_rate": 0.0
            }
        
        channel_metrics = self.channel_performance[channel]
        channel_metrics["total_sent"] += 1
        if success:
            channel_metrics["successful"] += 1
        
        # Update average delivery time
        total = channel_metrics["total_sent"]
        current_avg = channel_metrics["average_delivery_time"]
        channel_metrics["average_delivery_time"] = (
            (current_avg * (total - 1) + delivery_time) / total
        )
        
        # Update success rate
        channel_metrics["success_rate"] = (
            channel_metrics["successful"] / channel_metrics["total_sent"] * 100
        )
        
        # Update cost metrics
        if cost is not None:
            if "total_cost" not in self.cost_metrics:
                self.cost_metrics["total_cost"] = 0.0
            if channel not in self.cost_metrics:
                self.cost_metrics[channel] = 0.0
            
            self.cost_metrics["total_cost"] += cost
            self.cost_metrics[channel] += cost


@dataclass
class UserPreferences:
    """Comprehensive user notification preferences."""
    user_id: str
    preferences_id: str = field(default_factory=lambda: str(uuid4()))
    global_enabled: bool = True
    quiet_hours: Optional[Dict[str, str]] = None  # {"start": "22:00", "end": "08:00"}
    timezone: str = "UTC"
    language: str = "en"
    
    # Channel preferences
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    webhook_enabled: bool = False
    
    # Notification type preferences
    notification_type_preferences: Dict[str, bool] = field(default_factory=dict)
    
    # Priority preferences
    priority_preferences: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    
    # Business-specific preferences
    content_protection_alerts: bool = True
    collaboration_notifications: bool = True
    monetization_alerts: bool = True
    seo_notifications: bool = True
    distribution_updates: bool = True
    
    # Delivery preferences
    immediate_delivery_types: List[str] = field(default_factory=list)
    batch_delivery_types: List[str] = field(default_factory=list)
    digest_frequency: str = "daily"  # never, daily, weekly
    
    # Personalization preferences
    personalization_level: str = "high"  # low, medium, high
    include_recommendations: bool = True
    include_analytics: bool = True
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_notification_enabled(self, notification_type: str) -> bool:
        """Check if notification type is enabled for user."""
        if not self.global_enabled:
            return False
        
        return self.notification_type_preferences.get(notification_type, True)
    
    def is_channel_enabled(self, channel: str) -> bool:
        """Check if channel is enabled for user."""
        channel_map = {
            "email": self.email_enabled,
            "sms": self.sms_enabled,
            "push": self.push_enabled,
            "webhook": self.webhook_enabled
        }
        
        return channel_map.get(channel, False)
    
    def update_preference(self, key: str, value: Any):
        """Update user preference."""
        if hasattr(self, key):
            setattr(self, key, value)
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class BusinessRules:
    """Configurable business rules for notification processing."""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    rule_name: str = ""
    notification_type: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: Dict[str, Any] = field(default_factory=dict)
    priority_overrides: Optional[Dict[str, str]] = None
    channel_routing: Optional[Dict[str, List[str]]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    rate_limiting: Optional[Dict[str, int]] = None
    cost_optimization: Optional[Dict[str, Any]] = None
    personalization_rules: Optional[Dict[str, Any]] = None
    a_b_testing: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate rule conditions against context."""



        try:
            # Simple condition evaluation
            for key, expected_value in self.conditions.items():
                if key not in context:
                    return False
                
                actual_value = context[key]
                
                # Handle different comparison types
                if isinstance(expected_value, dict):
                    if "operator" in expected_value:
                        operator = expected_value["operator"]
                        value = expected_value["value"]
                        
                        if operator == "equals" and actual_value != value:
                            return False
                        elif operator == "greater_than" and actual_value <= value:
                            return False
                        elif operator == "less_than" and actual_value >= value:
                            return False
                        elif operator == "contains" and value not in str(actual_value):
                            return False
                else:
                    if actual_value != expected_value:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def apply_actions(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rule actions to notification request."""



        try:
            modified_request = request.copy()
            
            # Apply priority overrides
            if self.priority_overrides and request.get("notification_type") in self.priority_overrides:
                modified_request["priority"] = self.priority_overrides[request["notification_type"]]
            
            # Apply channel routing
            if self.channel_routing and request.get("notification_type") in self.channel_routing:
                modified_request["channels"] = self.channel_routing[request["notification_type"]]
            
            # Apply other actions
            for action_type, action_config in self.actions.items():
                if action_type == "set_delivery_time":
                    modified_request["delivery_time"] = action_config
                elif action_type == "add_metadata":
                    if "metadata" not in modified_request:
                        modified_request["metadata"] = {}
                    modified_request["metadata"].update(action_config)
                elif action_type == "enable_personalization":
                    if "personalization_data" not in modified_request:
                        modified_request["personalization_data"] = {}
                    modified_request["personalization_data"]["enabled"] = action_config
            
            return modified_request
            
        except Exception:
            return request


# Utility functions for model validation and serialization

def validate_notification_request(data: Dict[str, Any]) -> bool:
    """Validate notification request data."""



    try:
        required_fields = ["notification_type", "recipient", "content"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate recipient
        recipient = data["recipient"]
        if not isinstance(recipient, dict) or "user_id" not in recipient:
            return False
        
        # Validate content
        content = data["content"]
        if not isinstance(content, dict) or not content.get("message"):
            return False
        
        return True
        
    except Exception:
        return False


def serialize_notification_response(response: NotificationResponse) -> str:
    """Serialize notification response to JSON."""



    try:
        return json.dumps(response.to_dict(), indent=2)
    except Exception:
        return "{}"


def deserialize_notification_request(data: str) -> Optional[NotificationRequest]:
    """Deserialize JSON data to NotificationRequest."""



    try:
        parsed_data = json.loads(data)
        
        if not validate_notification_request(parsed_data):
            return None
        
        # Create recipient
        recipient_data = parsed_data["recipient"]
        recipient = NotificationRecipient(
            user_id=recipient_data["user_id"],
            email=recipient_data.get("email"),
            phone=recipient_data.get("phone"),
            push_tokens=recipient_data.get("push_tokens"),
            webhook_url=recipient_data.get("webhook_url"),
            preferences=recipient_data.get("preferences"),
            timezone=recipient_data.get("timezone"),
            language=recipient_data.get("language", "en"),
            user_type=recipient_data.get("user_type"),
            business_context=recipient_data.get("business_context")
        )
        
        # Create content
        content_data = parsed_data["content"]
        content = NotificationContent(
            subject=content_data.get("subject"),
            title=content_data.get("title"),
            message=content_data["message"],
            html_content=content_data.get("html_content"),
            markdown_content=content_data.get("markdown_content"),
            rich_content=content_data.get("rich_content"),
            attachments=content_data.get("attachments"),
            action_buttons=content_data.get("action_buttons"),
            metadata=content_data.get("metadata")
        )
        
        # Create request
        request = NotificationRequest(
            notification_id=parsed_data.get("notification_id", str(uuid4())),
            notification_type=parsed_data["notification_type"],
            recipient=recipient,
            content=content,
            priority=parsed_data.get("priority", NotificationPriority.MEDIUM.value),
            channels=parsed_data.get("channels"),
            delivery_time=parsed_data.get("delivery_time"),
            scheduled_at=datetime.fromisoformat(parsed_data["scheduled_at"]) if parsed_data.get("scheduled_at") else None,
            expires_at=datetime.fromisoformat(parsed_data["expires_at"]) if parsed_data.get("expires_at") else None,
            template_id=parsed_data.get("template_id"),
            personalization_data=parsed_data.get("personalization_data"),
            business_context=parsed_data.get("business_context"),
            workflow_id=parsed_data.get("workflow_id"),
            parent_notification_id=parsed_data.get("parent_notification_id"),
            urgency_score=parsed_data.get("urgency_score"),
            retry_config=parsed_data.get("retry_config"),
            metadata=parsed_data.get("metadata"),
            created_at=datetime.fromisoformat(parsed_data["created_at"]) if parsed_data.get("created_at") else datetime.now(timezone.utc)
        )
        
        return request
        
    except Exception:
        return None
