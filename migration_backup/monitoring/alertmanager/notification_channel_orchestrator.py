# WARNING: Potential SQL injection risk - use parameterized queries
#!/usr/bin/env python3
"""
Notification Channel Orchestrator - Multi-Channel Notification Coordination
===========================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - All Rights Reserved

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries - AI-Powered Creator Economy Platform
Module: Notification Channel Orchestrator
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import smtplib
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import re

logger = logging.getLogger(__name__)


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    SUPPRESSED = "suppressed"


class NotificationPriority(Enum):
    """Notification priority levels"""
    IMMEDIATE = "immediate"    # 0 seconds delay
    HIGH = "high"             # < 30 seconds delay
    MEDIUM = "medium"         # < 5 minutes delay
    LOW = "low"               # < 30 minutes delay
    BATCH = "batch"           # Next batch cycle


@dataclass
class NotificationTemplate:
    """Template for notification messages"""
    template_id: str
    channel: str
    language: str
    subject_template: str
    body_template: str
    content_type: str = "text/plain"
    variables: List[str] = field(default_factory=list)


@dataclass
class NotificationRecipient:
    """Recipient information for notifications"""
    recipient_id: str
    name: str
    channels: Dict[str, str]  # channel -> address/identifier
    preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"
    language: str = "en"
    creator_tier: Optional[str] = None


@dataclass
class NotificationMessage:
    """Structured notification message"""
    message_id: str
    channel: str
    recipient: NotificationRecipient
    subject: str
    content: str
    priority: NotificationPriority
    scheduled_time: datetime
    max_retries: int = 3
    retry_count: int = 0
    status: NotificationStatus = NotificationStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivery_confirmation: Optional[Dict[str, Any]] = None


class NotificationChannelOrchestrator:
    """
    Multi-Channel Notification Orchestrator for Creator Economy
    
    Features:
    - Slack/Teams integration enterprise
    - Email notification templating
    - SMS/Push notification dispatch
    - PagerDuty integration avancée
    - Creator-specific notification preferences
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the notification orchestrator"""
        self.config = config
        self.templates = self._load_notification_templates()
        self.recipients = {}  # Would be loaded from database
        self.delivery_queue = asyncio.Queue()
        self.retry_queue = asyncio.Queue()
        self.batch_queue = {}  # Channel -> messages
        
        # Channel configurations
        self.channel_configs = self._initialize_channel_configs()
        
        # Delivery tracking
        self.delivery_stats = {
            "total_sent": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "retries_attempted": 0,
            "channels_active": set()
        }
        
        # Rate limiting
        self.rate_limiters = self._initialize_rate_limiters()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Notification Channel Orchestrator initialized")
    
    def _load_notification_templates(self) -> Dict[str, NotificationTemplate]:
        """Load notification templates for different scenarios"""
        templates = {}
        
        # Critical Alert Templates
        templates["critical_slack"] = NotificationTemplate(
            template_id="critical_slack",
            channel="slack",
            language="en",
            subject_template="🔴 CRITICAL: {alert_name}",
            body_template="""
🚨 *CRITICAL ALERT* 🚨

*Service:* {service}
*Severity:* {severity}
*Creator Impact:* {creator_impact}
*Time:* {timestamp}

*Description:* {description}

*Affected:*
• {affected_creators_count} creators
• {estimated_revenue_loss:.2f} USD revenue impact
• {user_count_affected} users affected

*Actions Required:*
{recommended_actions}

*Dashboard:* <{dashboard_url}|View Dashboard>
*Runbook:* <{runbook_url}|View Runbook>
""",
            content_type="slack_markdown",
            variables=["alert_name", "service", "severity", "creator_impact", "timestamp", 
                      "description", "affected_creators_count", "estimated_revenue_loss",
                      "user_count_affected", "recommended_actions", "dashboard_url", "runbook_url"]
        )
        
        templates["critical_email"] = NotificationTemplate(
            template_id="critical_email",
            channel="email",
            language="en",
            subject_template="🔴 CRITICAL ALERT: {alert_name} - {service}",
            body_template="""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="background-color: #ff4444; color: white; padding: 15px; border-radius: 5px;">
        <h2>🚨 CRITICAL ALERT DETECTED</h2>
    </div>
    
    <div style="padding: 20px;">
        <h3>Alert Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Service:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{service}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Severity:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{severity}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Time:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{timestamp}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Creator Impact:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{creator_impact}</td></tr>
        </table>
        
        <h3>Impact Assessment</h3>
        <ul>
            <li><strong>Affected Creators:</strong> {affected_creators_count}</li>
            <li><strong>Estimated Revenue Impact:</strong> ${estimated_revenue_loss:.2f}</li>
            <li><strong>Users Affected:</strong> {user_count_affected}</li>
        </ul>
        
        <h3>Description</h3>
        <p>{description}</p>
        
        <h3>Recommended Actions</h3>
        <div>{recommended_actions}</div>
        
        <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
            <p><strong>Quick Links:</strong></p>
            <a href="{dashboard_url}" style="color: #007bff; text-decoration: none;">📊 View Dashboard</a> | 
            <a href="{runbook_url}" style="color: #007bff; text-decoration: none;">📖 View Runbook</a>
        </div>
    </div>
    
    <div style="margin-top: 20px; padding: 15px; background-color: #333; color: white; text-align: center;">
        <p>IA Chéries AlertManager Enterprise • AI-Powered Creator Economy Platform</p>
        <p>© 2025 Fahed Mlaiel - All Rights Reserved</p>
    </div>
</body>
</html>
""",
            content_type="text/html",
            variables=["alert_name", "service", "severity", "creator_impact", "timestamp",
                      "description", "affected_creators_count", "estimated_revenue_loss",
                      "user_count_affected", "recommended_actions", "dashboard_url", "runbook_url"]
        )
        
        # Creator-specific templates
        templates["creator_impact_email"] = NotificationTemplate(
            template_id="creator_impact_email",
            channel="email",
            language="en",
            subject_template="Service Impact Notification - {creator_name}",
            body_template="""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="background-color: #4a90e2; color: white; padding: 15px; border-radius: 5px;">
        <h2>📢 Service Impact Notification</h2>
    </div>
    
    <div style="padding: 20px;">
        <p>Dear {creator_name},</p>
        
        <p>We want to inform you about a service impact that may affect your Creator experience on IA Chéries.</p>
        
        <h3>Impact Details</h3>
        <ul>
            <li><strong>Affected Service:</strong> {service}</li>
            <li><strong>Impact Level:</strong> {impact_level}</li>
            <li><strong>Estimated Duration:</strong> {estimated_duration} minutes</li>
            <li><strong>Your Tier:</strong> {creator_tier}</li>
        </ul>
        
        <h3>What This Means for You</h3>
        <p>{creator_specific_impact}</p>
        
        <h3>What We're Doing</h3>
        <p>Our engineering team is actively working to resolve this issue. We'll keep you updated on our progress.</p>
        
        <div style="margin-top: 20px; padding: 15px; background-color: #e8f4fd; border-radius: 5px;">
            <p><strong>Support:</strong> If you need immediate assistance, please contact our Creator Support team.</p>
            <p><strong>Status Page:</strong> <a href="{status_page_url}">Check real-time status updates</a></p>
        </div>
        
        <p>Thank you for your patience as we work to resolve this issue.</p>
        
        <p>Best regards,<br>
        The IA Chéries Team</p>
    </div>
</body>
</html>
""",
            content_type="text/html",
            variables=["creator_name", "service", "impact_level", "estimated_duration",
                      "creator_tier", "creator_specific_impact", "status_page_url"]
        )
        
        # SMS templates
        templates["critical_sms"] = NotificationTemplate(
            template_id="critical_sms",
            channel="sms",
            language="en",
            subject_template="",  # SMS doesn't use subject
            body_template="🚨 CRITICAL: {service} alert! {affected_creators_count} creators affected. Revenue impact: ${estimated_revenue_loss:.0f}. Check dashboard: {short_url}",
            content_type="text/plain",
            variables=["service", "affected_creators_count", "estimated_revenue_loss", "short_url"]
        )
        
        # PagerDuty templates
        templates["pagerduty_incident"] = NotificationTemplate(
            template_id="pagerduty_incident",
            channel="pagerduty",
            language="en",
            subject_template="{severity}: {service} - {alert_name}",
            body_template=json.dumps({
                "summary": "{alert_name}",
                "source": "{service}",
                "severity": "{severity}",  
                "component": "{service}",
                "group": "ainflue-alerts",
                "class": "creator-economy",
                "custom_details": {
                    "creator_impact": "{creator_impact}",
                    "affected_creators": "{affected_creators_count}",
                    "revenue_impact": "{estimated_revenue_loss}",
                    "description": "{description}",
                    "dashboard_url": "{dashboard_url}",
                    "runbook_url": "{runbook_url}"
                }
            }),
            content_type="application/json",
            variables=["alert_name", "service", "severity", "creator_impact",
                      "affected_creators_count", "estimated_revenue_loss",
                      "description", "dashboard_url", "runbook_url"]
        )
        
        return templates
    
    def _initialize_channel_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize configuration for each notification channel"""
        return {
            "slack": {
                "enabled": self.config.get("channels", {}).get("slack", {}).get("enabled", True),
                "webhook_url": self.config.get("channels", {}).get("slack", {}).get("webhook_url"),
                "default_channel": "#alerts",
                "rate_limit": 30,  # messages per minute
                "retry_delay": 60,  # seconds
                "timeout": 10  # seconds
            },
            "email": {
                "enabled": self.config.get("channels", {}).get("email", {}).get("enabled", True),
                "smtp_host": self.config.get("channels", {}).get("email", {}).get("smtp_host", "smtp.gmail.com"),
                "smtp_port": self.config.get("channels", {}).get("email", {}).get("smtp_port", 587),
                "sender": self.config.get("channels", {}).get("email", {}).get("sender", "alerts@ainflue.com"),
                "username": self.config.get("channels", {}).get("email", {}).get("username"),
                "password": self.config.get("channels", {}).get("email", {}).get("password"),
                "rate_limit": 60,  # messages per minute
                "retry_delay": 120,  # seconds
                "timeout": 30  # seconds
            },
            "sms": {
                "enabled": self.config.get("channels", {}).get("sms", {}).get("enabled", True),
                "provider": self.config.get("channels", {}).get("sms", {}).get("provider", "twilio"),
                "api_key": self.config.get("channels", {}).get("sms", {}).get("api_key"),
                "phone_number": self.config.get("channels", {}).get("sms", {}).get("phone_number"),
                "rate_limit": 10,  # messages per minute
                "retry_delay": 300,  # seconds
                "timeout": 15  # seconds
            },
            "pagerduty": {
                "enabled": self.config.get("channels", {}).get("pagerduty", {}).get("enabled", True),
                "api_key": self.config.get("channels", {}).get("pagerduty", {}).get("api_key"),
                "service_key": self.config.get("channels", {}).get("pagerduty", {}).get("service_key"),
                "api_url": "https://events.pagerduty.com/v2/enqueue",
                "rate_limit": 100,  # messages per minute
                "retry_delay": 180,  # seconds
                "timeout": 20  # seconds
            },
            "webhook": {
                "enabled": True,
                "endpoints": self.config.get("channels", {}).get("webhook", {}).get("endpoints", []),
                "rate_limit": 120,  # messages per minute
                "retry_delay": 60,  # seconds
                "timeout": 10  # seconds
            }
        }
    
    def _initialize_rate_limiters(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rate limiters for each channel"""
        rate_limiters = {}
        
        for channel, config in self.channel_configs.items():
            rate_limiters[channel] = {
                "requests": [],  # Timestamps of recent requests
                "limit": config.get("rate_limit", 60),
                "window": 60  # 1 minute window
            }
        
        return rate_limiters
    
    def _start_background_tasks(self) -> None:
        """Start background tasks for message processing"""
        asyncio.create_task(self._process_delivery_queue())
        asyncio.create_task(self._process_retry_queue())
        asyncio.create_task(self._process_batch_queue())
        asyncio.create_task(self._cleanup_rate_limiters())
    
    async def dispatch_notifications(
        self,
        alert_context: Any,
        routing_decision: Any
    ) -> List[Any]:  # Returns List[NotificationResult]
        """
        Main notification dispatch function
        
        Args:
            alert_context: Enhanced alert context
            routing_decision: Routing decision from routing engine
            
        Returns:
            List of NotificationResult objects
        """
        try:
            notification_results = []
            
            # Get recipients for this alert
            recipients = await self._get_notification_recipients(alert_context, routing_decision)
            
            # Generate notification messages
            messages = await self._generate_notification_messages(
                alert_context, routing_decision, recipients
            )
            
            # Dispatch messages based on priority
            for message in messages:
                if message.priority == NotificationPriority.IMMEDIATE:
                    # Send immediately
                    result = await self._send_notification(message)
                    notification_results.append(result)
                else:
                    # Queue for later processing
                    await self.delivery_queue.put(message)
                    
                    # Create pending result
                    from .index import NotificationResult  # Import here to avoid circular import
                    result = NotificationResult(
                        channel=message.channel,
                        success=False,  # Will be updated when actually sent
                        delivery_time=datetime.now(),
                        error_message="Queued for delivery"
                    )
                    notification_results.append(result)
            
            logger.info(
                f"Dispatched {len(messages)} notifications for alert {alert_context.alert_id} "
                f"across {len(set(m.channel for m in messages))} channels"
            )
            
            return notification_results
            
        except Exception as e:
            logger.error(f"Failed to dispatch notifications: {e}")
            return []
    
    async def _get_notification_recipients(
        self,
        alert_context: Any,
        routing_decision: Any
    ) -> List[NotificationRecipient]:
        """Get recipients for notifications based on alert and routing"""
        recipients = []
        
        try:
            # Creator-specific recipient
            if alert_context.creator_id:
                creator_recipient = await self._get_creator_recipient(alert_context.creator_id)
                if creator_recipient:
                    recipients.append(creator_recipient)
            
            # Team recipients based on service and severity
            team_recipients = await self._get_team_recipients(alert_context, routing_decision)
            recipients.extend(team_recipients)
            
            # On-call recipients for critical alerts
            if alert_context.severity.value in ["emergency", "critical"]:
                oncall_recipients = await self._get_oncall_recipients(alert_context)
                recipients.extend(oncall_recipients)
            
            # Remove duplicates
            unique_recipients = {}
            for recipient in recipients:
                unique_recipients[recipient.recipient_id] = recipient
            
            return list(unique_recipients.values())
            
        except Exception as e:
            logger.error(f"Failed to get notification recipients: {e}")
            return []
    
    async def _get_creator_recipient(self, creator_id: str) -> Optional[NotificationRecipient]:
        """Get Creator as notification recipient"""
        try:
            # Mock implementation - would query Creator database
            if creator_id.startswith("creator_"):
                return NotificationRecipient(
                    recipient_id=creator_id,
                    name=f"Creator {creator_id}",
                    channels={
                        "email": f"{creator_id}@example.com",
                        "sms": "+1234567890"  # Would be real phone number
                    },
                    preferences={
                        "notification_hours": {"start": 8, "end": 22},
                        "preferred_channels": ["email"],
                        "critical_alerts_sms": True
                    },
                    timezone="UTC",
                    language="en",
                    creator_tier="professional"
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get Creator recipient: {e}")
            return None
    
    async def _get_team_recipients(
        self,
        alert_context: Any,
        routing_decision: Any
    ) -> List[NotificationRecipient]:
        """Get team recipients based on service and routing"""
        recipients = []
        
        try:
            # Service-specific team mappings
            service_teams = {
                "api": ["backend-team", "devops-team"],
                "database": ["dba-team", "backend-team"],
                "ai-engine": ["ml-team", "ai-team"],
                "payment": ["payments-team", "security-team"],
                "security": ["security-team", "devops-team"],
                "frontend": ["frontend-team", "ux-team"]
            }
            
            teams = service_teams.get(alert_context.source_service, ["devops-team"])
            
            # Mock team recipients
            for team in teams:
                recipients.append(NotificationRecipient(
                    recipient_id=f"team_{team}",
                    name=f"{team.replace('-', ' ').title()}",
                    channels={
                        "slack": f"#{team}",
                        "email": f"{team}@ainflue.com"
                    },
                    preferences={
                        "escalation_delay": 900  # 15 minutes
                    }
                ))
            
            return recipients
            
        except Exception as e:
            logger.error(f"Failed to get team recipients: {e}")
            return []
    
    async def _get_oncall_recipients(self, alert_context: Any) -> List[NotificationRecipient]:
        """Get on-call recipients for critical alerts"""
        try:
            # Mock on-call recipient
            return [
                NotificationRecipient(
                    recipient_id="oncall_primary",
                    name="On-Call Engineer",
                    channels={
                        "pagerduty": "primary-oncall",
                        "sms": "+1-555-ONCALL",
                        "email": "oncall@ainflue.com"
                    },
                    preferences={
                        "always_notify": True,
                        "escalation_timeout": 300  # 5 minutes
                    }
                )
            ]
        except Exception as e:
            logger.error(f"Failed to get on-call recipients: {e}")
            return []
    
    async def _generate_notification_messages(
        self,
        alert_context: Any,
        routing_decision: Any,
        recipients: List[NotificationRecipient]
    ) -> List[NotificationMessage]:
        """Generate notification messages for all channels and recipients"""
        messages = []
        
        try:
            # Prepare template variables
            template_vars = self._prepare_template_variables(alert_context, routing_decision)
            
            # Generate messages for each channel in routing decision
            for channel in routing_decision.channels:
                channel_name = channel.value
                
                if not self.channel_configs.get(channel_name, {}).get("enabled", False):
                    logger.warning(f"Channel {channel_name} is disabled, skipping")
                    continue
                
                # Get appropriate template
                template = self._select_template(alert_context, channel_name)
                if not template:
                    logger.warning(f"No template found for channel {channel_name}")
                    continue
                
                # Generate messages for each recipient
                for recipient in recipients:
                    if channel_name not in recipient.channels:
                        continue
                    
                    # Customize template variables for this recipient
                    recipient_vars = self._customize_variables_for_recipient(
                        template_vars, recipient, alert_context
                    )
                    
                    # Render message content
                    subject = self._render_template(template.subject_template, recipient_vars)
                    content = self._render_template(template.body_template, recipient_vars)
                    
                    # Determine priority
                    priority = self._determine_message_priority(
                        alert_context, routing_decision, recipient
                    )
                    
                    # Calculate scheduled time
                    scheduled_time = datetime.now() + timedelta(seconds=routing_decision.delay_seconds)
                    
                    message = NotificationMessage(
                        message_id=f"{alert_context.alert_id}_{channel_name}_{recipient.recipient_id}_{int(datetime.now().timestamp())}",
                        channel=channel_name,
                        recipient=recipient,
                        subject=subject,
                        content=content,
                        priority=priority,
                        scheduled_time=scheduled_time,
                        metadata={
                            "alert_id": alert_context.alert_id,
                            "template_id": template.template_id,
                            "routing_decision_id": getattr(routing_decision, 'decision_id', 'unknown')
                        }
                    )
                    
                    messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to generate notification messages: {e}")
            return []
    
    def _prepare_template_variables(self, alert_context: Any, routing_decision: Any) -> Dict[str, Any]:
        """Prepare variables for template rendering"""
        variables = {
            "alert_name": getattr(alert_context, 'metadata', {}).get('summary', 'Unknown Alert'),
            "alert_id": alert_context.alert_id,
            "service": alert_context.source_service,
            "severity": alert_context.severity.value,
            "timestamp": alert_context.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "creator_impact": f"{alert_context.business_impact:.1%}",
            "description": getattr(alert_context, 'metadata', {}).get('description', 'No description available'),
            "dashboard_url": f"https://dashboard.ainflue.com/alerts/{alert_context.alert_id}",
            "runbook_url": f"https://docs.ainflue.com/runbooks/{alert_context.source_service}",
            "status_page_url": "https://status.ainflue.com",
            "short_url": f"https://ainflue.co/a/{alert_context.alert_id[:8]}",
            
            # Impact metrics
            "user_count_affected": alert_context.user_count_affected,
            "affected_creators_count": 0,
            "estimated_revenue_loss": 0.0,
            
            # Actions
            "recommended_actions": "Please investigate immediately"
        }
        
        # Add Creator impact analysis if available
        if hasattr(alert_context, 'metadata') and 'creator_impact_analysis' in alert_context.metadata:
            impact_data = alert_context.metadata['creator_impact_analysis']
            variables.update({
                "affected_creators_count": impact_data.get('affected_creators_count', 0),
                "estimated_revenue_loss": impact_data.get('estimated_revenue_loss', 0.0),
                "estimated_duration": impact_data.get('recovery_time_estimate', 30)
            })
        
        # Add routing decision recommendations
        if hasattr(routing_decision, 'rationale'):
            variables["recommended_actions"] = routing_decision.rationale
        
        return variables
    
    def _select_template(self, alert_context: Any, channel: str) -> Optional[NotificationTemplate]:
        """Select appropriate template based on alert and channel"""
        try:
            # Template selection logic
            severity = alert_context.severity.value
            
            # Critical alerts get special templates
            if severity in ["emergency", "critical"]:
                template_key = f"critical_{channel}"
                if template_key in self.templates:
                    return self.templates[template_key]
            
            # Creator-specific templates
            if alert_context.creator_id and channel == "email":
                template_key = f"creator_impact_{channel}"
                if template_key in self.templates:
                    return self.templates[template_key]
            
            # Service-specific templates
            service_template_key = f"{alert_context.source_service}_{channel}"
            if service_template_key in self.templates:
                return self.templates[service_template_key]
            
            # Default templates
            default_template_key = f"default_{channel}"
            if default_template_key in self.templates:
                return self.templates[default_template_key]
            
            # Fallback to any template for this channel
            for template_id, template in self.templates.items():
                if template.channel == channel:
                    return template
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to select template: {e}")
            return None
    
    def _customize_variables_for_recipient(
        self,
        template_vars: Dict[str, Any],
        recipient: NotificationRecipient,
        alert_context: Any
    ) -> Dict[str, Any]:
        """Customize template variables for specific recipient"""
        customized_vars = template_vars.copy()
        
        try:
            # Recipient-specific variables
            if recipient.recipient_id.startswith("creator_"):
                customized_vars.update({
                    "creator_name": recipient.name,
                    "creator_tier": recipient.creator_tier or "starter",
                    "creator_specific_impact": self._generate_creator_specific_impact(
                        alert_context, recipient
                    )
                })
            
            # Language-specific customization
            if recipient.language != "en":
                # Would implement localization here
                pass
            
            # Timezone adjustment
            if recipient.timezone != "UTC":
                # Would implement timezone conversion here
                pass
            
            return customized_vars
            
        except Exception as e:
            logger.error(f"Failed to customize variables for recipient: {e}")
            return template_vars
    
    def _generate_creator_specific_impact(self, alert_context: Any, recipient: NotificationRecipient) -> str:
        """Generate Creator-specific impact description"""
        try:
            service = alert_context.source_service
            tier = recipient.creator_tier or "starter"
            
            impact_descriptions = {
                "api": {
                    "premium": "You may experience delays in content uploads and analytics updates. Our team is prioritizing resolution for premium creators.",
                    "professional": "Content processing and analytics may be temporarily affected. We're working to resolve this quickly.",
                    "emerging": "Some platform features may be temporarily unavailable. We appreciate your patience.",
                    "starter": "You may notice slower response times. We're working to restore normal service."
                },
                "ai-engine": {
                    "premium": "AI-powered content enhancement features may be temporarily limited. Priority processing will resume shortly.",
                    "professional": "AI content tools may be slower than usual. Your content will be processed as soon as possible.",
                    "emerging": "AI features may be temporarily unavailable. Manual tools remain functional.",
                    "starter": "AI assistance may be limited. Basic content creation tools are still available."
                },
                "payment": {
                    "premium": "Earnings tracking and payouts may be delayed. Your revenue is secure and will be processed.",
                    "professional": "Payment processing may be temporarily affected. All transactions are being queued safely.",
                    "emerging": "Monetization features may be limited. Your earnings data is safe.",
                    "starter": "Payment features may be temporarily unavailable."
                }
            }
            
            return impact_descriptions.get(service, {}).get(tier, 
                "Some platform features may be temporarily affected. We're working to resolve this issue.")
        
        except Exception as e:
            logger.error(f"Failed to generate Creator-specific impact: {e}")
            return "Service impact detected. We're working to resolve this issue."
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        try:
            # Simple template rendering (would use Jinja2 in production)
            rendered = template
            for key, value in variables.items():
                placeholder = "{" + key + "}"
                if placeholder in rendered:
                    rendered = rendered.replace(placeholder, str(value))
            
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return template  # Return original template on error
    
    def _determine_message_priority(
        self,
        alert_context: Any,
        routing_decision: Any,
        recipient: NotificationRecipient
    ) -> NotificationPriority:
        """Determine message priority based on context"""
        try:
            # Emergency/Critical alerts are immediate
            if alert_context.severity.value in ["emergency", "critical"]:
                return NotificationPriority.IMMEDIATE
            
            # Premium creators get high priority
            if recipient.creator_tier == "premium":
                return NotificationPriority.HIGH
            
            # High severity alerts
            if alert_context.severity.value == "high":
                return NotificationPriority.HIGH
            
            # Warning severity
            if alert_context.severity.value == "warning":
                return NotificationPriority.MEDIUM
            
            # Everything else is low priority
            return NotificationPriority.LOW
            
        except Exception as e:
            logger.error(f"Failed to determine message priority: {e}")
            return NotificationPriority.MEDIUM
    
    async def _send_notification(self, message: NotificationMessage) -> Any:
        """Send individual notification message"""
        from .index import NotificationResult  # Import here to avoid circular import
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(message.channel):
                logger.warning(f"Rate limit exceeded for channel {message.channel}")
                message.status = NotificationStatus.RETRY
                await self.retry_queue.put(message)
                return NotificationResult(
                    channel=message.channel,
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="Rate limit exceeded"
                )
            
            # Send based on channel type
            if message.channel == "slack":
                result = await self._send_slack_notification(message)
            elif message.channel == "email":
                result = await self._send_email_notification(message)
            elif message.channel == "sms":
                result = await self._send_sms_notification(message)
            elif message.channel == "pagerduty":
                result = await self._send_pagerduty_notification(message)
            elif message.channel == "webhook":
                result = await self._send_webhook_notification(message)
            else:
                logger.error(f"Unknown notification channel: {message.channel}")
                result = NotificationResult(
                    channel=message.channel,
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="Unknown channel"
                )
            
            # Update statistics
            self.delivery_stats["total_sent"] += 1
            self.delivery_stats["channels_active"].add(message.channel)
            
            if result.success:
                self.delivery_stats["successful_deliveries"] += 1
                message.status = NotificationStatus.SENT
            else:
                self.delivery_stats["failed_deliveries"] += 1
                message.status = NotificationStatus.FAILED
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            message.status = NotificationStatus.FAILED
            return NotificationResult(
                channel=message.channel,
                success=False,
                delivery_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _check_rate_limit(self, channel: str) -> bool:
        """Check if channel is within rate limits"""
        try:
            if channel not in self.rate_limiters:
                return True
            
            rate_limiter = self.rate_limiters[channel]
            now = datetime.now()
            
            # Remove old requests outside the window
            cutoff = now - timedelta(seconds=rate_limiter["window"])
            rate_limiter["requests"] = [
                req_time for req_time in rate_limiter["requests"]
                if req_time > cutoff
            ]
            
            # Check if under limit
            if len(rate_limiter["requests"]) < rate_limiter["limit"]:
                rate_limiter["requests"].append(now)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True  # Allow on error
    
    async def _send_slack_notification(self, message: NotificationMessage) -> Any:
        """Send Slack notification"""
        from .index import NotificationResult
        
        try:
            config = self.channel_configs["slack"]
            webhook_url = config.get("webhook_url")
            
            if not webhook_url:
                return NotificationResult(
                    channel="slack",
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="Slack webhook URL not configured"
                )
            
            # Prepare Slack payload
            slack_channel = message.recipient.channels.get("slack", config["default_channel"])
            
            payload = {
                "channel": slack_channel,
                "username": "IA Chéries AlertManager",
                "icon_emoji": ":rotating_light:",
                "text": message.content
            }
            
            # Send HTTP request
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config["timeout"])) as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        return NotificationResult(
                            channel="slack",
                            success=True,
                            delivery_time=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        return NotificationResult(
                            channel="slack",
                            success=False,
                            delivery_time=datetime.now(),
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return NotificationResult(
                channel="slack",
                success=False,
                delivery_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _send_email_notification(self, message: NotificationMessage) -> Any:
        """Send email notification"""
        from .index import NotificationResult
        
        try:
            config = self.channel_configs["email"]
            
            if not all([config.get("smtp_host"), config.get("sender")]):
                return NotificationResult(
                    channel="email",
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="Email configuration incomplete"
                )
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = config["sender"]
            msg['To'] = message.recipient.channels.get("email", "")
            
            # Add content
            if "html" in message.metadata.get("content_type", ""):
                html_part = MIMEText(message.content, 'html')
                msg.attach(html_part)
            else:
                text_part = MIMEText(message.content, 'plain')
                msg.attach(text_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
                server.starttls(context=context)
                if config.get("username") and config.get("password"):
                    server.login(config["username"], config["password"])
                server.send_message(msg)
            
            return NotificationResult(
                channel="email",
                success=True,
                delivery_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return NotificationResult(
                channel="email",
                success=False,
                delivery_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _send_sms_notification(self, message: NotificationMessage) -> Any:
        """Send SMS notification"""
        from .index import NotificationResult
        
        try:
            config = self.channel_configs["sms"]
            
            # Mock SMS sending (would integrate with Twilio/AWS SNS in production)
            logger.info(f"SMS would be sent to {message.recipient.channels.get('sms', 'unknown')}: {message.content}")
            
            return NotificationResult(
                channel="sms",
                success=True,
                delivery_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return NotificationResult(
                channel="sms",
                success=False,
                delivery_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _send_pagerduty_notification(self, message: NotificationMessage) -> Any:
        """Send PagerDuty notification"""
        from .index import NotificationResult
        
        try:
            config = self.channel_configs["pagerduty"]
            api_url = config.get("api_url")
            api_key = config.get("api_key")
            
            if not api_key:
                return NotificationResult(
                    channel="pagerduty",
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="PagerDuty API key not configured"
                )
            
            # Parse content as JSON for PagerDuty
            try:
                content_data = json.loads(message.content)
            except:
                content_data = {"summary": message.content}
            
            payload = {
                "routing_key": api_key,
                "event_action": "trigger",
                "payload": content_data
            }
            
            # Send to PagerDuty
            headers = {"Content-Type": "application/json"}
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config["timeout"])) as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status in [200, 202]:
                        return NotificationResult(
                            channel="pagerduty",
                            success=True,
                            delivery_time=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        return NotificationResult(
                            channel="pagerduty",
                            success=False,
                            delivery_time=datetime.now(),
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
        
        except Exception as e:
            logger.error(f"Failed to send PagerDuty notification: {e}")
            return NotificationResult(
                channel="pagerduty",
                success=False,
                delivery_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _send_webhook_notification(self, message: NotificationMessage) -> Any:
        """Send webhook notification"""
        from .index import NotificationResult
        
        try:
            config = self.channel_configs["webhook"]
            endpoints = config.get("endpoints", [])
            
            if not endpoints:
                return NotificationResult(
                    channel="webhook",
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="No webhook endpoints configured"
                )
            
            # Send to all configured endpoints
            success_count = 0
            errors = []
            
            for endpoint in endpoints:
                try:
                    payload = {
                        "message_id": message.message_id,
                        "channel": message.channel,
                        "recipient": message.recipient.recipient_id,
                        "subject": message.subject,
                        "content": message.content,
                        "priority": message.priority.value,
                        "timestamp": message.scheduled_time.isoformat(),
                        "metadata": message.metadata
                    }
                    
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config["timeout"])) as session:
                        async with session.post(endpoint, json=payload) as response:
                            if response.status in [200, 201, 202]:
                                success_count += 1
                            else:
                                error_text = await response.text()
                                errors.append(f"{endpoint}: HTTP {response.status}")
                
                except Exception as e:
                    errors.append(f"{endpoint}: {str(e)}")
            
            if success_count > 0:
                return NotificationResult(
                    channel="webhook",
                    success=True,
                    delivery_time=datetime.now()
                )
            else:
                return NotificationResult(
                    channel="webhook",
                    success=False,
                    delivery_time=datetime.now(),
                    error_message="; ".join(errors)
                )
        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return NotificationResult(
                channel="webhook",
                success=False,
                delivery_time=datetime.now(),
                error_message=str(e)
            )
    
    async def _process_delivery_queue(self) -> None:
        """Background task to process the delivery queue"""
        while True:
            try:
                # Get message from queue
                message = await self.delivery_queue.get()
                
                # Check if it's time to send
                if datetime.now() >= message.scheduled_time:
                    await self._send_notification(message)
                else:
                    # Put back in queue for later
                    await asyncio.sleep(1)
                    await self.delivery_queue.put(message)
                
                self.delivery_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing delivery queue: {e}")
                await asyncio.sleep(5)
    
    async def _process_retry_queue(self) -> None:
        """Background task to process retry queue"""
        while True:
            try:
                # Get message from retry queue
                message = await self.retry_queue.get()
                
                if message.retry_count < message.max_retries:
                    # Calculate exponential backoff delay
                    delay = min(300, 30 * (2 ** message.retry_count))  # Max 5 minutes
                    await asyncio.sleep(delay)
                    
                    message.retry_count += 1
                    result = await self._send_notification(message)
                    
                    if not result.success and message.retry_count < message.max_retries:
                        await self.retry_queue.put(message)
                    
                    self.delivery_stats["retries_attempted"] += 1
                
                self.retry_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing retry queue: {e}")
                await asyncio.sleep(5)
    
    async def _process_batch_queue(self) -> None:
        """Background task to process batch notifications"""
        while True:
            try:
                await asyncio.sleep(300)  # Process batches every 5 minutes
                
                # Process each channel's batch queue
                for channel, messages in self.batch_queue.items():
                    if messages:
                        logger.info(f"Processing {len(messages)} batched messages for {channel}")
                        
                        # Send batched messages
                        for message in messages:
                            await self._send_notification(message)
                        
                        # Clear batch
                        self.batch_queue[channel] = []
                
            except Exception as e:
                logger.error(f"Error processing batch queue: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_rate_limiters(self) -> None:
        """Background task to clean up rate limiter data"""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
                now = datetime.now()
                for channel, rate_limiter in self.rate_limiters.items():
                    cutoff = now - timedelta(seconds=rate_limiter["window"] * 2)
                    rate_limiter["requests"] = [
                        req_time for req_time in rate_limiter["requests"]
                        if req_time > cutoff
                    ]
                
            except Exception as e:
                logger.error(f"Error cleaning up rate limiters: {e}")
                await asyncio.sleep(60)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for notification orchestrator"""
        return {
            "status": "healthy",
            "channels_configured": len(self.channel_configs),
            "channels_enabled": len([c for c in self.channel_configs.values() if c.get("enabled")]),
            "templates_loaded": len(self.templates),
            "delivery_queue_size": self.delivery_queue.qsize(),
            "retry_queue_size": self.retry_queue.qsize(),
            "delivery_stats": self.delivery_stats.copy()
        }
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get notification statistics and performance metrics"""
        stats = self.delivery_stats.copy()
        stats["channels_active"] = list(stats["channels_active"])
        
        if stats["total_sent"] > 0:
            stats["success_rate"] = stats["successful_deliveries"] / stats["total_sent"]
            stats["failure_rate"] = stats["failed_deliveries"] / stats["total_sent"]
        
        return stats


if __name__ == "__main__":
    # Testing/development code
    import asyncio
    
    async def test_notification_orchestrator():
        config = {
            "channels": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"},
                "email": {"enabled": True, "smtp_host": "smtp.gmail.com", "sender": "test@ainflue.com"}
            }
        }
        
        orchestrator = NotificationChannelOrchestrator(config)
        
        # Mock alert context and routing decision
        class MockAlertContext:
            def __init__(self):
                self.alert_id = "test_notification_001"
                self.timestamp = datetime.now()
                self.source_service = "api"
                self.severity = type('Severity', (), {'value': 'critical'})()
                self.creator_id = "creator_001"
                self.creator_tier = type('CreatorTier', (), {'value': 'premium'})()
                self.business_impact = 0.8
                self.user_count_affected = 5000
                self.metadata = {
                    "summary": "API response time degraded",
                    "description": "High response times detected on API endpoints"
                }
        
        class MockRoutingDecision:
            def __init__(self):
                from .intelligent_alert_routing_engine import NotificationChannel
                self.channels = [NotificationChannel.SLACK, NotificationChannel.EMAIL]
                self.delay_seconds = 0
                self.rationale = "Immediate notification required for critical API issue"
        
        mock_alert = MockAlertContext()
        mock_routing = MockRoutingDecision()
        
        # Test notification dispatch
        results = await orchestrator.dispatch_notifications(mock_alert, mock_routing)
        
        print(f"Notification dispatch results:")
        for result in results:
            print(f"  Channel: {result.channel}, Success: {result.success}")
        
        # Wait a bit for background processing
        await asyncio.sleep(2)
        
        # Get statistics
        stats = orchestrator.get_notification_statistics()
        print(f"\nNotification Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(test_notification_orchestrator())