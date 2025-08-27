"""
IA Influencer Agent - Pipeline Notification System
Enterprise-Grade Notification and Alerting for Pipeline Events

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive notification and alerting capabilities for pipeline events,
supporting multiple channels and integration with monitoring systems.

Features:
- Multi-channel notifications (email, Slack, Teams, webhooks)
- Event-driven notification triggers
- Customizable notification templates
- Escalation policies and alert routing
- Integration with monitoring systems

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""

import asyncio
import aiohttp
import smtplib
import logging
import json
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import jinja2
from pathlib import Path

from .pipeline_manager import PipelineExecution

class NotificationChannel(Enum):
    """Notification channel types"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    SMS = "sms"
    DISCORD = "discord"

class NotificationLevel(Enum):
    """Notification severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class NotificationEvent(Enum):
    """Pipeline events that trigger notifications"""
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    PIPELINE_CANCELLED = "pipeline_cancelled"
    STEP_FAILED = "step_failed"
    DEPLOYMENT_SUCCESSFUL = "deployment_successful"
    DEPLOYMENT_FAILED = "deployment_failed"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_ISSUE = "performance_issue"

@dataclass
class NotificationConfig:
    """Notification configuration settings"""
    channel: NotificationChannel
    enabled: bool = True
    recipients: List[str] = None
    webhook_url: Optional[str] = None
    template: Optional[str] = None
    level_filter: List[NotificationLevel] = None
    event_filter: List[NotificationEvent] = None
    throttle_minutes: int = 0

@dataclass
class NotificationMessage:
    """Notification message structure"""
    title: str
    content: str
    level: NotificationLevel
    event: NotificationEvent
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class NotificationTemplate:
    """Notification template management"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent / "notification_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        self._create_default_templates()
        
    def _create_default_templates(self):
        """Create default notification templates"""
        templates = {
            'pipeline_started.html': '''
            <h2>🚀 Pipeline Started</h2>
            <p><strong>Pipeline:</strong> {{ pipeline_name }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
            <p><strong>Type:</strong> {{ pipeline_type }}</p>
            <p><strong>Started at:</strong> {{ start_time }}</p>
            <p><strong>Execution ID:</strong> {{ execution_id }}</p>
            ''',
            
            'pipeline_completed.html': '''
            <h2>✅ Pipeline Completed Successfully</h2>
            <p><strong>Pipeline:</strong> {{ pipeline_name }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
            <p><strong>Duration:</strong> {{ duration }}</p>
            <p><strong>Completed at:</strong> {{ end_time }}</p>
            <p><strong>Execution ID:</strong> {{ execution_id }}</p>
            
            <h3>Steps Summary:</h3>
            <ul>
            {% for step in steps %}
                <li>{{ step.name }}: {{ step.status }}</li>
            {% endfor %}
            </ul>
            ''',
            
            'pipeline_failed.html': '''
            <h2>❌ Pipeline Failed</h2>
            <p><strong>Pipeline:</strong> {{ pipeline_name }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
            <p><strong>Failed at:</strong> {{ end_time }}</p>
            <p><strong>Duration:</strong> {{ duration }}</p>
            <p><strong>Execution ID:</strong> {{ execution_id }}</p>
            
            <h3>Failed Steps:</h3>
            <ul>
            {% for step in failed_steps %}
                <li><strong>{{ step.name }}</strong>: {{ step.error_output }}</li>
            {% endfor %}
            </ul>
            
            <h3>All Steps:</h3>
            <ul>
            {% for step in steps %}
                <li>{{ step.name }}: {{ step.status }}</li>
            {% endfor %}
            </ul>
            ''',
            
            'slack_message.json': '''
            {
                "text": "{{ title }}",
                "attachments": [
                    {
                        "color": "{% if level == 'error' or level == 'critical' %}danger{% elif level == 'warning' %}warning{% else %}good{% endif %}",
                        "fields": [
                            {
                                "title": "Pipeline",
                                "value": "{{ pipeline_name }}",
                                "short": true
                            },
                            {
                                "title": "Environment", 
                                "value": "{{ environment }}",
                                "short": true
                            },
                            {
                                "title": "Status",
                                "value": "{{ status }}",
                                "short": true
                            },
                            {
                                "title": "Duration",
                                "value": "{{ duration }}",
                                "short": true
                            }
                        ],
                        "footer": "IA Influencer Agent",
                        "ts": {{ timestamp }}
                    }
                ]
            }
            '''
        }
        
        for template_name, content in templates.items():
            template_file = self.templates_dir / template_name
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write(content.strip())
                    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render notification template with provided data"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logging.error(f"Template rendering failed for {template_name}: {str(e)}")
            return f"Template rendering failed: {str(e)}"

class EmailNotificationHandler:
    """Email notification handler"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, 
                 password: str, use_tls: bool = True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.logger = logging.getLogger(__name__)
        
    async def send_notification(self, config: NotificationConfig, 
                              message: NotificationMessage) -> bool:
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.title
            msg['From'] = self.username
            msg['To'] = ', '.join(config.recipients or [])
            
            # Add content
            html_part = MIMEText(message.content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            self.logger.info(f"Email notification sent to {config.recipients}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False

class SlackNotificationHandler:
    """Slack notification handler"""
    
    def __init__(self, default_webhook_url: Optional[str] = None):
        self.default_webhook_url = default_webhook_url
        self.logger = logging.getLogger(__name__)
        
    async def send_notification(self, config: NotificationConfig, 
                              message: NotificationMessage) -> bool:
        """Send Slack notification"""
        webhook_url = config.webhook_url or self.default_webhook_url
        if not webhook_url:
            self.logger.error("No Slack webhook URL configured")
            return False
            
        try:
            # Prepare Slack message
            slack_data = {
                "text": message.title,
                "attachments": [{
                    "color": self._get_color_for_level(message.level),
                    "fields": [
                        {"title": "Level", "value": message.level.value, "short": True},
                        {"title": "Event", "value": message.event.value, "short": True},
                        {"title": "Time", "value": message.timestamp.isoformat(), "short": True}
                    ],
                    "text": message.content[:500] + "..." if len(message.content) > 500 else message.content
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_data) as response:
                    if response.status == 200:
                        self.logger.info("Slack notification sent successfully")
                        return True
                    else:
                        self.logger.error(f"Slack API error: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
            return False
            
    def _get_color_for_level(self, level: NotificationLevel) -> str:
        """Get Slack color for notification level"""
        color_map = {
            NotificationLevel.INFO: "good",
            NotificationLevel.WARNING: "warning", 
            NotificationLevel.ERROR: "danger",
            NotificationLevel.CRITICAL: "danger"
        }
        return color_map.get(level, "good")

class WebhookNotificationHandler:
    """Generic webhook notification handler"""
    
    def __init__(self, default_headers: Optional[Dict[str, str]] = None):
        self.default_headers = default_headers or {"Content-Type": "application/json"}
        self.logger = logging.getLogger(__name__)
        
    async def send_notification(self, config: NotificationConfig, 
                              message: NotificationMessage) -> bool:
        """Send webhook notification"""
        if not config.webhook_url:
            self.logger.error("No webhook URL configured")
            return False
            
        try:
            payload = {
                "title": message.title,
                "content": message.content,
                "level": message.level.value,
                "event": message.event.value,
                "timestamp": message.timestamp.isoformat(),
                "metadata": message.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.webhook_url, 
                    json=payload, 
                    headers=self.default_headers
                ) as response:
                    if response.status < 300:
                        self.logger.info(f"Webhook notification sent to {config.webhook_url}")
                        return True
                    else:
                        self.logger.error(f"Webhook error: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {str(e)}")
            return False

class NotificationManager:
    """
    Advanced Notification Management System for Pipeline Events
    
    Provides enterprise-grade notification capabilities with:
    - Multi-channel notification support
    - Event-driven notification triggers
    - Customizable templates and formatting
    - Throttling and escalation policies
    - Integration with monitoring systems
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.template_manager = NotificationTemplate(templates_dir)
        
        # Notification handlers
        self.handlers: Dict[NotificationChannel, Any] = {}
        self.configurations: List[NotificationConfig] = []
        
        # Throttling
        self.last_notification_times: Dict[str, datetime] = {}
        
        # Initialize default configurations
        self._load_default_configurations()
        
    def _load_default_configurations(self):
        """Load default notification configurations"""
        # Default configurations for different environments
        default_configs = [
            NotificationConfig(
                channel=NotificationChannel.EMAIL,
                enabled=True,
                recipients=["admin@ia-influencer.com"],
                level_filter=[NotificationLevel.ERROR, NotificationLevel.CRITICAL],
                event_filter=[
                    NotificationEvent.PIPELINE_FAILED, 
                    NotificationEvent.DEPLOYMENT_FAILED,
                    NotificationEvent.SECURITY_ALERT
                ]
            ),
            NotificationConfig(
                channel=NotificationChannel.SLACK,
                enabled=True,
                level_filter=[NotificationLevel.INFO, NotificationLevel.WARNING, 
                            NotificationLevel.ERROR, NotificationLevel.CRITICAL],
                event_filter=[
                    NotificationEvent.PIPELINE_COMPLETED,
                    NotificationEvent.PIPELINE_FAILED,
                    NotificationEvent.DEPLOYMENT_SUCCESSFUL,
                    NotificationEvent.DEPLOYMENT_FAILED
                ],
                throttle_minutes=5
            )
        ]
        
        self.configurations.extend(default_configs)
        
    def register_handler(self, channel: NotificationChannel, handler: Any):
        """Register notification handler for specific channel"""
        self.handlers[channel] = handler
        self.logger.info(f"Registered notification handler for {channel.value}")
        
    def add_configuration(self, config: NotificationConfig):
        """Add notification configuration"""
        self.configurations.append(config)
        self.logger.info(f"Added notification configuration for {config.channel.value}")
        
    async def send_pipeline_notification(self, execution: PipelineExecution, 
                                       event: NotificationEvent) -> List[bool]:
        """Send notifications for pipeline events"""
        # Determine notification level based on event
        level = self._get_level_for_event(event, execution)
        
        # Create message
        message = self._create_pipeline_message(execution, event, level)
        
        # Send notifications
        results = []
        for config in self.configurations:
            if self._should_send_notification(config, message):
                result = await self._send_notification(config, message)
                results.append(result)
                
        return results
        
    def _get_level_for_event(self, event: NotificationEvent, 
                           execution: PipelineExecution) -> NotificationLevel:
        """Determine notification level based on event and execution"""
        if event in [NotificationEvent.PIPELINE_FAILED, NotificationEvent.DEPLOYMENT_FAILED]:
            return NotificationLevel.ERROR
        elif event == NotificationEvent.SECURITY_ALERT:
            return NotificationLevel.CRITICAL
        elif event in [NotificationEvent.STEP_FAILED, NotificationEvent.PERFORMANCE_ISSUE]:
            return NotificationLevel.WARNING
        else:
            return NotificationLevel.INFO
            
    def _create_pipeline_message(self, execution: PipelineExecution, 
                               event: NotificationEvent, 
                               level: NotificationLevel) -> NotificationMessage:
        """Create notification message for pipeline event"""
        # Prepare template data
        template_data = {
            'pipeline_name': execution.config.name,
            'environment': execution.config.environment.value,
            'pipeline_type': execution.config.pipeline_type.value,
            'execution_id': execution.execution_id,
            'status': execution.status.value,
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'duration': str(execution.get_duration()) if execution.get_duration() else None,
            'steps': [
                {
                    'name': step.name,
                    'status': step.status.value,
                    'error_output': step.error_output
                }
                for step in execution.steps
            ],
            'failed_steps': [
                {
                    'name': step.name,
                    'status': step.status.value,
                    'error_output': step.error_output
                }
                for step in execution.steps 
                if step.status.value == 'failed'
            ],
            'level': level.value,
            'timestamp': int(datetime.utcnow().timestamp())
        }
        
        # Generate title
        title_map = {
            NotificationEvent.PIPELINE_STARTED: f"🚀 Pipeline Started: {execution.config.name}",
            NotificationEvent.PIPELINE_COMPLETED: f"✅ Pipeline Completed: {execution.config.name}",
            NotificationEvent.PIPELINE_FAILED: f"❌ Pipeline Failed: {execution.config.name}",
            NotificationEvent.DEPLOYMENT_SUCCESSFUL: f"🎉 Deployment Successful: {execution.config.name}",
            NotificationEvent.DEPLOYMENT_FAILED: f"💥 Deployment Failed: {execution.config.name}"
        }
        
        title = title_map.get(event, f"Pipeline Event: {execution.config.name}")
        
        # Render content based on event
        template_name = f"{event.value}.html"
        content = self.template_manager.render_template(template_name, **template_data)
        
        return NotificationMessage(
            title=title,
            content=content,
            level=level,
            event=event,
            metadata={
                'execution_id': execution.execution_id,
                'pipeline_type': execution.config.pipeline_type.value,
                'environment': execution.config.environment.value
            }
        )
        
    def _should_send_notification(self, config: NotificationConfig, 
                                message: NotificationMessage) -> bool:
        """Check if notification should be sent based on configuration"""
        if not config.enabled:
            return False
            
        # Check level filter
        if config.level_filter and message.level not in config.level_filter:
            return False
            
        # Check event filter  
        if config.event_filter and message.event not in config.event_filter:
            return False
            
        # Check throttling
        if config.throttle_minutes > 0:
            throttle_key = f"{config.channel.value}_{message.event.value}"
            last_time = self.last_notification_times.get(throttle_key)
            
            if last_time:
                time_diff = datetime.utcnow() - last_time
                if time_diff < timedelta(minutes=config.throttle_minutes):
                    return False
                    
        return True
        
    async def _send_notification(self, config: NotificationConfig, 
                               message: NotificationMessage) -> bool:
        """Send notification using configured handler"""
        handler = self.handlers.get(config.channel)
        if not handler:
            self.logger.warning(f"No handler registered for {config.channel.value}")
            return False
            
        try:
            result = await handler.send_notification(config, message)
            
            # Update throttling timestamp
            if config.throttle_minutes > 0:
                throttle_key = f"{config.channel.value}_{message.event.value}"
                self.last_notification_times[throttle_key] = datetime.utcnow()
                
            return result
            
        except Exception as e:
            self.logger.error(f"Notification sending failed for {config.channel.value}: {str(e)}")
            return False

# Global notification manager instance
notification_manager = NotificationManager()
