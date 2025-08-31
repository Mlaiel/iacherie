"""🔧 Notification System - IA-Influencer-Agent CI/CD
================================================================
Expert: DEVOPS_ENGINEER + COMMUNICATION_SPECIALIST
Created: 2025-08-24
Author: Fahed Mlaiel (mlaiel@live.de)

Enterprise notification system for CI/CD pipeline events and alerts.
Multi-channel communication with intelligent routing and escalation.
================================================================
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
import json
import time
import aiohttp
import smtplib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import boto3

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """Notification channel enumeration"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"
    PAGERDUTY = "pagerduty"

class NotificationPriority(Enum):
    """Notification priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class EventType(Enum):
    """Pipeline event type enumeration"""
    BUILD_STARTED = "build_started"
    BUILD_SUCCESS = "build_success"
    BUILD_FAILED = "build_failed"
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_SUCCESS = "deployment_success"
    DEPLOYMENT_FAILED = "deployment_failed"
    SECURITY_SCAN_FAILED = "security_scan_failed"
    QUALITY_GATE_FAILED = "quality_gate_failed"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    ENVIRONMENT_DOWN = "environment_down"
    HIGH_ERROR_RATE = "high_error_rate"
    PERFORMANCE_DEGRADED = "performance_degraded"

@dataclass
class NotificationConfiguration:
    """Notification configuration"""
    channel: NotificationChannel
    enabled: bool = True
    webhook_url: Optional[str] = None
    email_config: Optional[Dict[str, str]] = None
    slack_config: Optional[Dict[str, str]] = None
    priority_filter: List[NotificationPriority] = None
    event_filter: List[EventType] = None
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    
    def __post_init__(self):
        if self.priority_filter is None:
            self.priority_filter = list(NotificationPriority)
        if self.event_filter is None:
            self.event_filter = list(EventType)

@dataclass
class NotificationMessage:
    """Notification message"""
    event_type: EventType
    priority: NotificationPriority
    title: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    pipeline_id: Optional[str] = None
    environment: Optional[str] = None
    user: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class NotificationRecipient:
    """Notification recipient"""
    name: str
    email: Optional[str] = None
    slack_user: Optional[str] = None
    phone: Optional[str] = None
    roles: List[str] = None
    on_call: bool = False
    priority_threshold: NotificationPriority = NotificationPriority.MEDIUM
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []

class NotificationSystem:
    """Enterprise notification system for CI/CD pipelines"""
    
    def __init__(self):
        """Initialize notification system"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.configurations: Dict[NotificationChannel, NotificationConfiguration] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.message_history: List[NotificationMessage] = []
        self.rate_limits: Dict[str, datetime] = {}
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize notification system"""
        try:
            # Setup notification channels
            await self._setup_notification_channels()
            
            # Configure recipients for IA-Influencer team
            await self._setup_ia_influencer_recipients()
            
            # Initialize rate limiting
            await self._initialize_rate_limiting()
            
            self.initialized = True
            self.logger.info("✅ Notification system initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize notification system: {e}")
            return False
    
    async def _setup_notification_channels(self) -> None:
        """Setup notification channels"""
        
        # Email configuration for critical alerts
        self.configurations[NotificationChannel.EMAIL] = NotificationConfiguration(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            email_config={
                "smtp_host": "smtp.gmail.com",
                "smtp_port": "587",
                "sender_email": "alerts@ia-influencer.com",
                "sender_name": "IA-Influencer CI/CD",
                "use_tls": "true"
            },
            priority_filter=[NotificationPriority.CRITICAL, NotificationPriority.HIGH],
            event_filter=[
                EventType.BUILD_FAILED,
                EventType.DEPLOYMENT_FAILED,
                EventType.SECURITY_SCAN_FAILED,
                EventType.ENVIRONMENT_DOWN
            ]
        )
        
        # Slack configuration for team communication
        self.configurations[NotificationChannel.SLACK] = NotificationConfiguration(
            channel=NotificationChannel.SLACK,
            enabled=True,
            slack_config={
                "webhook_url": "https://hooks.slack.com/services/...",
                "channel": "#ia-influencer-alerts",
                "username": "CI/CD Bot",
                "icon_emoji": ":robot_face:"
            },
            priority_filter=[
                NotificationPriority.CRITICAL,
                NotificationPriority.HIGH,
                NotificationPriority.MEDIUM
            ]
        )
        
        # Microsoft Teams for management updates
        self.configurations[NotificationChannel.TEAMS] = NotificationConfiguration(
            channel=NotificationChannel.TEAMS,
            enabled=True,
            webhook_url="https://outlook.office.com/webhook/...",
            priority_filter=[NotificationPriority.CRITICAL, NotificationPriority.HIGH],
            event_filter=[
                EventType.DEPLOYMENT_SUCCESS,
                EventType.DEPLOYMENT_FAILED,
                EventType.SECURITY_SCAN_FAILED
            ]
        )
        
        # PagerDuty for on-call emergencies
        self.configurations[NotificationChannel.PAGERDUTY] = NotificationConfiguration(
            channel=NotificationChannel.PAGERDUTY,
            enabled=True,
            webhook_url="https://events.pagerduty.com/v2/enqueue",
            priority_filter=[NotificationPriority.CRITICAL],
            event_filter=[
                EventType.ENVIRONMENT_DOWN,
                EventType.HIGH_ERROR_RATE,
                EventType.SECURITY_SCAN_FAILED
            ]
        )
        
        # Discord for community updates
        self.configurations[NotificationChannel.DISCORD] = NotificationConfiguration(
            channel=NotificationChannel.DISCORD,
            enabled=True,
            webhook_url="https://discord.com/api/webhooks/...",
            priority_filter=[NotificationPriority.HIGH, NotificationPriority.MEDIUM],
            event_filter=[
                EventType.BUILD_SUCCESS,
                EventType.DEPLOYMENT_SUCCESS
            ]
        )
    
    async def _setup_ia_influencer_recipients(self) -> None:
        """Setup recipients for IA-Influencer team"""
        
        # Lead Architect
        self.recipients["fahed_mlaiel"] = NotificationRecipient(
            name="Fahed Mlaiel",
            email="mlaiel@live.de",
            slack_user="@fahed.mlaiel",
            phone="+49xxxxxxxxx",
            roles=["lead_architect", "devops_lead"],
            on_call=True,
            priority_threshold=NotificationPriority.HIGH
        )
        
        # DevOps Team
        self.recipients["devops_team"] = NotificationRecipient(
            name="DevOps Team",
            email="devops@ia-influencer.com",
            slack_user="@devops-team",
            roles=["devops", "infrastructure"],
            on_call=True,
            priority_threshold=NotificationPriority.MEDIUM
        )
        
        # Security Team
        self.recipients["security_team"] = NotificationRecipient(
            name="Security Team",
            email="security@ia-influencer.com",
            slack_user="@security-team",
            roles=["security", "compliance"],
            on_call=False,
            priority_threshold=NotificationPriority.HIGH
        )
        
        # ML Engineers
        self.recipients["ml_team"] = NotificationRecipient(
            name="ML Engineering Team",
            email="ml@ia-influencer.com",
            slack_user="@ml-team",
            roles=["ml_engineer", "ai_specialist"],
            on_call=False,
            priority_threshold=NotificationPriority.MEDIUM
        )
        
        # Quality Assurance
        self.recipients["qa_team"] = NotificationRecipient(
            name="QA Team",
            email="qa@ia-influencer.com",
            slack_user="@qa-team",
            roles=["qa", "testing"],
            on_call=False,
            priority_threshold=NotificationPriority.MEDIUM
        )
    
    async def send_notification(
        self,
        event_type: EventType,
        priority: NotificationPriority,
        title: str,
        message: str,
        details: Dict[str, Any],
        pipeline_id: Optional[str] = None,
        environment: Optional[str] = None,
        user: Optional[str] = None,
        custom_channels: Optional[List[NotificationChannel]] = None
    ) -> Dict[NotificationChannel, bool]:
        """Send notification across configured channels"""
        try:
            notification_msg = NotificationMessage(
                event_type=event_type,
                priority=priority,
                title=title,
                message=message,
                details=details,
                timestamp=datetime.now(),
                pipeline_id=pipeline_id,
                environment=environment,
                user=user,
                tags=self._generate_tags(event_type, environment)
            )
            
            # Store in history
            self.message_history.append(notification_msg)
            
            # Determine channels to use
            channels_to_use = custom_channels or list(self.configurations.keys())
            
            # Send notifications
            results = {}
            tasks = []
            
            for channel in channels_to_use:
                if channel in self.configurations:
                    config = self.configurations[channel]
                    
                    # Check filters
                    if (config.enabled and 
                        priority in config.priority_filter and 
                        event_type in config.event_filter and
                        not self._is_rate_limited(channel, notification_msg)):
                        
                        task = asyncio.create_task(
                            self._send_channel_notification(channel, config, notification_msg)
                        )
                        tasks.append((channel, task))
            
            # Wait for all notifications to complete
            for channel, task in tasks:
                try:
                    success = await task
                    results[channel] = success
                except Exception as e:
                    self.logger.error(f"Failed to send {channel.value} notification: {e}")
                    results[channel] = False
            
            self.logger.info(
                f"Notification sent: {title} (Priority: {priority.value}, "
                f"Channels: {len([r for r in results.values() if r])}/{len(results)})"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return {}
    
    async def _send_channel_notification(
        self,
        channel: NotificationChannel,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send notification to specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(config, message)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_notification(config, message)
            elif channel == NotificationChannel.TEAMS:
                return await self._send_teams_notification(config, message)
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord_notification(config, message)
            elif channel == NotificationChannel.PAGERDUTY:
                return await self._send_pagerduty_notification(config, message)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(config, message)
            else:
                self.logger.warning(f"Unsupported channel: {channel.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send {channel.value} notification: {e}")
            return False
    
    async def _send_email_notification(
        self,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send email notification"""
        try:
            email_config = config.email_config
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{email_config['sender_name']} <{email_config['sender_email']}>"
            msg['Subject'] = f"[IA-Influencer] {message.title}"
            
            # Get recipients for this message
            recipients = self._get_recipients_for_message(message)
            msg['To'] = ", ".join([r.email for r in recipients if r.email])
            
            # Create HTML body
            html_body = self._create_email_html(message)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_host'], int(email_config['smtp_port']))
            if email_config.get('use_tls') == 'true':
                server.starttls()
            
            # In production, use environment variables for credentials
            # server.login(email_username, email_password)
            
            text = msg.as_string()
            server.sendmail(
                email_config['sender_email'],
                [r.email for r in recipients if r.email],
                text
            )
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    async def _send_slack_notification(
        self,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send Slack notification"""
        try:
            slack_config = config.slack_config
            webhook_url = slack_config['webhook_url']
            
            # Create Slack message
            color = self._get_priority_color(message.priority)
            
            payload = {
                "channel": slack_config['channel'],
                "username": slack_config['username'],
                "icon_emoji": slack_config['icon_emoji'],
                "attachments": [
                    {
                        "color": color,
                        "title": message.title,
                        "text": message.message,
                        "fields": [
                            {
                                "title": "Priority",
                                "value": message.priority.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Environment",
                                "value": message.environment or "N/A",
                                "short": True
                            },
                            {
                                "title": "Pipeline ID",
                                "value": message.pipeline_id or "N/A",
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": message.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "short": True
                            }
                        ],
                        "footer": "IA-Influencer CI/CD",
                        "ts": int(message.timestamp.timestamp())
                    }
                ]
            }
            
            # Add details if available
            if message.details:
                details_text = "\n".join([f"• {k}: {v}" for k, v in message.details.items()])
                payload["attachments"][0]["fields"].append({
                    "title": "Details",
                    "value": f"```{details_text}```",
                    "short": False
                })
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def _send_teams_notification(
        self,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send Microsoft Teams notification"""
        try:
            webhook_url = config.webhook_url
            color = self._get_priority_color(message.priority)
            
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color.replace("#", ""),
                "summary": message.title,
                "sections": [
                    {
                        "activityTitle": message.title,
                        "activitySubtitle": f"Priority: {message.priority.value.upper()}",
                        "activityImage": "https://ia-influencer.com/assets/logo.png",
                        "text": message.message,
                        "facts": [
                            {
                                "name": "Environment",
                                "value": message.environment or "N/A"
                            },
                            {
                                "name": "Pipeline ID",
                                "value": message.pipeline_id or "N/A"
                            },
                            {
                                "name": "Timestamp",
                                "value": message.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Failed to send Teams notification: {e}")
            return False
    
    async def _send_discord_notification(
        self,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send Discord notification"""
        try:
            webhook_url = config.webhook_url
            color = int(self._get_priority_color(message.priority).replace("#", ""), 16)
            
            embed = {
                "title": message.title,
                "description": message.message,
                "color": color,
                "timestamp": message.timestamp.isoformat(),
                "footer": {
                    "text": "IA-Influencer CI/CD"
                },
                "fields": [
                    {
                        "name": "Priority",
                        "value": message.priority.value.upper(),
                        "inline": True
                    },
                    {
                        "name": "Environment",
                        "value": message.environment or "N/A",
                        "inline": True
                    }
                ]
            }
            
            if message.pipeline_id:
                embed["fields"].append({
                    "name": "Pipeline ID",
                    "value": message.pipeline_id,
                    "inline": True
                })
            
            payload = {
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    async def _send_pagerduty_notification(
        self,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send PagerDuty notification"""
        try:
            webhook_url = config.webhook_url
            
            payload = {
                "routing_key": "YOUR_INTEGRATION_KEY",  # From environment
                "event_action": "trigger",
                "payload": {
                    "summary": message.title,
                    "source": "IA-Influencer CI/CD",
                    "severity": self._map_priority_to_severity(message.priority),
                    "component": message.environment or "unknown",
                    "group": "ci_cd",
                    "class": message.event_type.value,
                    "custom_details": {
                        "message": message.message,
                        "pipeline_id": message.pipeline_id,
                        "environment": message.environment,
                        "details": message.details
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status == 202  # PagerDuty returns 202
                    
        except Exception as e:
            self.logger.error(f"Failed to send PagerDuty notification: {e}")
            return False
    
    async def _send_webhook_notification(
        self,
        config: NotificationConfiguration,
        message: NotificationMessage
    ) -> bool:
        """Send generic webhook notification"""
        try:
            webhook_url = config.webhook_url
            
            payload = {
                "event_type": message.event_type.value,
                "priority": message.priority.value,
                "title": message.title,
                "message": message.message,
                "details": message.details,
                "timestamp": message.timestamp.isoformat(),
                "pipeline_id": message.pipeline_id,
                "environment": message.environment,
                "user": message.user,
                "tags": message.tags
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status < 400
                    
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _get_recipients_for_message(self, message: NotificationMessage) -> List[NotificationRecipient]:
        """Get appropriate recipients for a message"""
        recipients = []
        
        for recipient in self.recipients.values():
            # Check priority threshold
            priority_levels = {
                NotificationPriority.CRITICAL: 4,
                NotificationPriority.HIGH: 3,
                NotificationPriority.MEDIUM: 2,
                NotificationPriority.LOW: 1,
                NotificationPriority.INFO: 0
            }
            
            if priority_levels[message.priority] >= priority_levels[recipient.priority_threshold]:
                recipients.append(recipient)
        
        return recipients
    
    def _create_email_html(self, message: NotificationMessage) -> str:
        """Create HTML email body"""
        color = self._get_priority_color(message.priority)
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
                <div style="border-left: 4px solid {color}; padding-left: 20px;">
                    <h2 style="color: {color}; margin-top: 0;">{message.title}</h2>
                    <p style="font-size: 16px; line-height: 1.5;">{message.message}</p>
                    
                    <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">Priority:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{message.priority.value.upper()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">Environment:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{message.environment or "N/A"}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">Pipeline ID:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{message.pipeline_id or "N/A"}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">Timestamp:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{message.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}</td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                        <h4 style="margin-top: 0;">Details:</h4>
                        <pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px;">
{json.dumps(message.details, indent=2)}
                        </pre>
                    </div>
                    
                    <footer style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                        <p>This notification was generated by IA-Influencer CI/CD System</p>
                        <p>For support, contact: <a href="mailto:mlaiel@live.de">Fahed Mlaiel</a></p>
                    </footer>
                </div>
            </body>
        </html>
        """
        return html
    
    def _get_priority_color(self, priority: NotificationPriority) -> str:
        """Get color code for priority level"""
        colors = {
            NotificationPriority.CRITICAL: "#DC3545",
            NotificationPriority.HIGH: "#FD7E14",
            NotificationPriority.MEDIUM: "#FFC107",
            NotificationPriority.LOW: "#20C997",
            NotificationPriority.INFO: "#6C757D"
        }
        return colors.get(priority, "#6C757D")
    
    def _map_priority_to_severity(self, priority: NotificationPriority) -> str:
        """Map priority to PagerDuty severity"""
        mapping = {
            NotificationPriority.CRITICAL: "critical",
            NotificationPriority.HIGH: "error",
            NotificationPriority.MEDIUM: "warning",
            NotificationPriority.LOW: "info",
            NotificationPriority.INFO: "info"
        }
        return mapping.get(priority, "info")
    
    def _generate_tags(self, event_type: EventType, environment: Optional[str]) -> List[str]:
        """Generate tags for the message"""
        tags = ["ci_cd", event_type.value]
        if environment:
            tags.append(f"env:{environment}")
        return tags
    
    def _is_rate_limited(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """Check if notification is rate limited"""
        # Implement rate limiting logic
        rate_key = f"{channel.value}:{message.event_type.value}"
        now = datetime.now()
        
        if rate_key in self.rate_limits:
            last_sent = self.rate_limits[rate_key]
            # Rate limit: max 1 notification per event type per channel per minute
            if now - last_sent < timedelta(minutes=1):
                return True
        
        self.rate_limits[rate_key] = now
        return False
    
    async def _initialize_rate_limiting(self) -> None:
        """Initialize rate limiting"""
        # Clean old rate limit entries periodically
        self.rate_limits = {}
        self.logger.info("Rate limiting initialized")
    
    async def get_notification_history(
        self,
        hours: int = 24,
        priority: Optional[NotificationPriority] = None,
        event_type: Optional[EventType] = None
    ) -> List[Dict[str, Any]]:
        """Get notification history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_messages = []
        for msg in self.message_history:
            if msg.timestamp >= cutoff_time:
                if priority is None or msg.priority == priority:
                    if event_type is None or msg.event_type == event_type:
                        filtered_messages.append(asdict(msg))
        
        return filtered_messages
    
    async def test_notifications(self) -> Dict[NotificationChannel, bool]:
        """Test all configured notification channels"""
        test_results = {}
        
        test_message = NotificationMessage(
            event_type=EventType.BUILD_SUCCESS,
            priority=NotificationPriority.INFO,
            title="Test Notification",
            message="This is a test notification from IA-Influencer CI/CD system",
            details={"test": True, "timestamp": datetime.now().isoformat()},
            timestamp=datetime.now(),
            pipeline_id="test-pipeline",
            environment="test",
            tags=["test", "ci_cd"]
        )
        
        for channel, config in self.configurations.items():
            if config.enabled:
                try:
                    success = await self._send_channel_notification(channel, config, test_message)
                    test_results[channel] = success
                except Exception as e:
                    self.logger.error(f"Test failed for {channel.value}: {e}")
                    test_results[channel] = False
        
        return test_results

# Global instance
notification_system = NotificationSystem()
