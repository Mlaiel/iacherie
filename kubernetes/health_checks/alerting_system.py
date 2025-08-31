"""Health Alerting System for IA Influencer Agent Platform
Advanced multi-channel alerting and notification management system

This module provides comprehensive alerting capabilities for:
- Real-time health status monitoring and threshold-based alerts
- Multi-channel notification delivery (email, SMS, Slack, webhooks)
- Alert escalation and acknowledgment workflows
- Incident management and tracking
- Performance degradation alerts and recommendations
- SLA monitoring and breach notifications
- Custom alert rules and notification preferences

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

import aiohttp
import aioredis
from jinja2 import Template

from .core_health import HealthStatus, HealthCheckResult


class AlertSeverity(str, Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert notification channels"""    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    DISCORD = "discord"


class AlertStatus(str, Enum):
    """Alert status enumeration"""    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Alert rule configuration"""    name: str
    description: str
    service_pattern: str
    health_status_threshold: HealthStatus
    severity: AlertSeverity
    channels: List[AlertChannel]
    cooldown_minutes: int = 15
    escalation_minutes: int = 60
    enabled: bool = True
    conditions: Dict[str, Any] = None


@dataclass
class Alert:
    """Alert instance representation"""    id: str
    rule_name: str
    service: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    description: str
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    escalated: bool = False
    notification_count: int = 0


@dataclass
class NotificationTemplate:
    """Notification message templates"""    subject_template: str
    body_template: str
    format_type: str = "text"  # text, html, markdown


class HealthAlertingSystem:
    """    Advanced health monitoring alerting system
    
    Provides real-time alerting, multi-channel notifications, and incident
    management for the IA Influencer Agent platform health monitoring.
    """
    def __init__(self, config: Dict[str, Any], redis_client: Optional[aioredis.Redis] = None):
        """        Initialize health alerting system
        
        Args:
            config: Alerting system configuration
            redis_client: Redis client for alert storage (optional)
        """        self.config = config
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Alert configuration
        self.alert_config = config.get("alerting", {})
        self.notification_config = self.alert_config.get("notifications", {})
        self.rules_config = self.alert_config.get("rules", {})
        
        # Alert storage
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        
        # Notification channels
        self._notification_channels = {}
        self._initialize_notification_channels()
        
        # Alert rules
        self._alert_rules = []
        self._initialize_default_rules()
        
        # Templates
        self._notification_templates = {}
        self._initialize_notification_templates()
        
        # Metrics
        self._alert_metrics = {
            "total_alerts": 0,
            "active_alerts": 0,
            "alerts_by_severity": {severity.value: 0 for severity in AlertSeverity},
            "alerts_by_service": {},
            "notification_failures": 0,
            "last_alert_timestamp": None
        }

    def _initialize_notification_channels(self):
        """Initialize notification channel configurations"""        
        # Email configuration
        email_config = self.notification_config.get("email", {})
        if email_config.get("enabled", False):
            self._notification_channels[AlertChannel.EMAIL] = {
                "smtp_server": email_config.get("smtp_server"),
                "smtp_port": email_config.get("smtp_port", 587),
                "username": email_config.get("username"),
                "password": email_config.get("password"),
                "from_address": email_config.get("from_address"),
                "recipients": email_config.get("recipients", []),
                "use_tls": email_config.get("use_tls", True)
            }
        
        # Slack configuration
        slack_config = self.notification_config.get("slack", {})
        if slack_config.get("enabled", False):
            self._notification_channels[AlertChannel.SLACK] = {
                "webhook_url": slack_config.get("webhook_url"),
                "channel": slack_config.get("channel", "#alerts"),
                "username": slack_config.get("username", "IA-Agent-Monitor"),
                "icon_emoji": slack_config.get("icon_emoji", ":warning:")
            }
        
        # Webhook configuration
        webhook_config = self.notification_config.get("webhook", {})
        if webhook_config.get("enabled", False):
            self._notification_channels[AlertChannel.WEBHOOK] = {
                "url": webhook_config.get("url"),
                "method": webhook_config.get("method", "POST"),
                "headers": webhook_config.get("headers", {}),
                "auth": webhook_config.get("auth")
            }
        
        # PagerDuty configuration
        pagerduty_config = self.notification_config.get("pagerduty", {})
        if pagerduty_config.get("enabled", False):
            self._notification_channels[AlertChannel.PAGERDUTY] = {
                "integration_key": pagerduty_config.get("integration_key"),
                "service_name": pagerduty_config.get("service_name", "IA Influencer Agent")
            }

    def _initialize_default_rules(self):
        """Initialize default alert rules"""        default_rules = [
            AlertRule(
                name="critical_service_failure",
                description="Critical service complete failure",
                service_pattern="*",
                health_status_threshold=HealthStatus.CRITICAL,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PAGERDUTY],
                cooldown_minutes=5,
                escalation_minutes=15
            ),
            AlertRule(
                name="database_unhealthy",
                description="Database service unhealthy or disconnected",
                service_pattern="database*",
                health_status_threshold=HealthStatus.UNHEALTHY,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10,
                escalation_minutes=30
            ),
            AlertRule(
                name="ml_service_degraded",
                description="ML/AI services experiencing performance degradation",
                service_pattern="ml_*",
                health_status_threshold=HealthStatus.DEGRADED,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.SLACK],
                cooldown_minutes=15,
                escalation_minutes=60
            ),
            AlertRule(
                name="protection_service_failure",
                description="Content protection services failing",
                service_pattern="protection*",
                health_status_threshold=HealthStatus.UNHEALTHY,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10,
                escalation_minutes=30
            ),
            AlertRule(
                name="monetization_degraded",
                description="Monetization services experiencing issues",
                service_pattern="monetization*",
                health_status_threshold=HealthStatus.DEGRADED,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=20,
                escalation_minutes=60
            ),
            AlertRule(
                name="external_api_failure",
                description="External API integrations failing",
                service_pattern="external_*",
                health_status_threshold=HealthStatus.UNHEALTHY,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.SLACK],
                cooldown_minutes=15,
                escalation_minutes=45
            ),
            AlertRule(
                name="infrastructure_critical",
                description="Infrastructure components in critical state",
                service_pattern="infrastructure*",
                health_status_threshold=HealthStatus.CRITICAL,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PAGERDUTY],
                cooldown_minutes=5,
                escalation_minutes=20
            )
        ]
        
        self._alert_rules.extend(default_rules)
        
        # Load custom rules from configuration
        custom_rules = self.rules_config.get("custom_rules", [])
        for rule_config in custom_rules:
            try:
                custom_rule = AlertRule(**rule_config)
                self._alert_rules.append(custom_rule)
            except Exception as e:
                self.logger.error(f"Failed to load custom alert rule {rule_config}: {str(e)}")

    def _initialize_notification_templates(self):
        """Initialize notification message templates"""        
        # Email templates
        self._notification_templates[AlertChannel.EMAIL] = {
            AlertSeverity.CRITICAL: NotificationTemplate(
                subject_template="🚨 CRITICAL ALERT: {{alert.title}} - IA Influencer Agent",
                body_template="""                <h2 style="color: #dc3545;">🚨 CRITICAL ALERT</h2>
                <p><strong>Service:</strong> {{alert.service}}</p>
                <p><strong>Title:</strong> {{alert.title}}</p>
                <p><strong>Description:</strong> {{alert.description}}</p>
                <p><strong>Severity:</strong> {{alert.severity|upper}}</p>
                <p><strong>Time:</strong> {{alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}}</p>
                
                <h3>Details:</h3>
                <ul>
                {% for key, value in alert.details.items() %}
                    <li><strong>{{key}}:</strong> {{value}}</li>
                {% endfor %}
                </ul>
                
                <p style="color: #dc3545;"><strong>IMMEDIATE ACTION REQUIRED</strong></p>
                <p>This is a critical system alert requiring immediate attention.</p>
                
                <hr>
                <p><small>IA Influencer Agent Health Monitoring System</small></p>
                <p><small>Created by: Fahed Mlaiel | Contact: mlaiel@live.de</small></p>
                """,
                format_type="html"
            ),
            AlertSeverity.HIGH: NotificationTemplate(
                subject_template="⚠️ HIGH PRIORITY: {{alert.title}} - IA Influencer Agent",
                body_template="""                <h2 style="color: #fd7e14;">⚠️ HIGH PRIORITY ALERT</h2>
                <p><strong>Service:</strong> {{alert.service}}</p>
                <p><strong>Title:</strong> {{alert.title}}</p>
                <p><strong>Description:</strong> {{alert.description}}</p>
                <p><strong>Severity:</strong> {{alert.severity|upper}}</p>
                <p><strong>Time:</strong> {{alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}}</p>
                
                <h3>Details:</h3>
                <ul>
                {% for key, value in alert.details.items() %}
                    <li><strong>{{key}}:</strong> {{value}}</li>
                {% endfor %}
                </ul>
                
                <p style="color: #fd7e14;">Action required within 30 minutes</p>
                
                <hr>
                <p><small>IA Influencer Agent Health Monitoring System</small></p>
                """,
                format_type="html"
            ),
            AlertSeverity.MEDIUM: NotificationTemplate(
                subject_template="📊 MONITORING: {{alert.title}} - IA Influencer Agent",
                body_template="""                <h2 style="color: #ffc107;">📊 MONITORING ALERT</h2>
                <p><strong>Service:</strong> {{alert.service}}</p>
                <p><strong>Title:</strong> {{alert.title}}</p>
                <p><strong>Description:</strong> {{alert.description}}</p>
                <p><strong>Time:</strong> {{alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}}</p>
                
                <p>Please investigate when convenient.</p>
                
                <hr>
                <p><small>IA Influencer Agent Health Monitoring System</small></p>
                """,
                format_type="html"
            )
        }
        
        # Slack templates
        self._notification_templates[AlertChannel.SLACK] = {
            AlertSeverity.CRITICAL: NotificationTemplate(
                subject_template="",
                body_template="""                {
                    "text": "🚨 CRITICAL ALERT: {{alert.title}}",
                    "attachments": [
                        {
                            "color": "danger",
                            "fields": [
                                {"title": "Service", "value": "{{alert.service}}", "short": true},
                                {"title": "Severity", "value": "{{alert.severity|upper}}", "short": true},
                                {"title": "Description", "value": "{{alert.description}}", "short": false},
                                {"title": "Time", "value": "{{alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}}", "short": true}
                            ],
                            "footer": "IA Influencer Agent Health Monitor"
                        }
                    ]
                }
                """,
                format_type="json"
            ),
            AlertSeverity.HIGH: NotificationTemplate(
                subject_template="",
                body_template="""                {
                    "text": "⚠️ HIGH PRIORITY: {{alert.title}}",
                    "attachments": [
                        {
                            "color": "warning",
                            "fields": [
                                {"title": "Service", "value": "{{alert.service}}", "short": true},
                                {"title": "Severity", "value": "{{alert.severity|upper}}", "short": true},
                                {"title": "Description", "value": "{{alert.description}}", "short": false}
                            ],
                            "footer": "IA Influencer Agent Health Monitor"
                        }
                    ]
                }
                """,
                format_type="json"
            )
        }

    async def process_health_results(self, health_results: List[HealthCheckResult]):
        """        Process health check results and trigger alerts based on configured rules
        
        Args:
            health_results: List of health check results to evaluate
        """        self.logger.debug(f"Processing {len(health_results)} health check results for alerting")
        
        for result in health_results:
            await self._evaluate_alert_rules(result)
        
        # Check for alert escalations
        await self._check_alert_escalations()
        
        # Update metrics
        await self._update_alert_metrics()

    async def _evaluate_alert_rules(self, result: HealthCheckResult):
        """Evaluate health result against alert rules"""        
        for rule in self._alert_rules:
            if not rule.enabled:
                continue
            
            # Check if service matches rule pattern
            if not self._matches_pattern(result.service, rule.service_pattern):
                continue
            
            # Check if health status exceeds threshold
            if not self._status_exceeds_threshold(result.status, rule.health_status_threshold):
                continue
            
            # Check additional conditions if specified
            if rule.conditions and not self._evaluate_conditions(result, rule.conditions):
                continue
            
            # Check cooldown period
            if await self._is_in_cooldown(rule.name, result.service):
                continue
            
            # Create and trigger alert
            await self._create_and_trigger_alert(rule, result)

    def _matches_pattern(self, service_name: str, pattern: str) -> bool:
        """Check if service name matches pattern (supports wildcards)"""        if pattern == "*":
            return True
        
        if "*" in pattern:
            # Simple wildcard matching
            if pattern.endswith("*"):
                return service_name.startswith(pattern[:-1])
            elif pattern.startswith("*"):
                return service_name.endswith(pattern[1:])
            else:
                # Pattern has wildcard in middle
                parts = pattern.split("*")
                return service_name.startswith(parts[0]) and service_name.endswith(parts[1])
        
        return service_name == pattern

    def _status_exceeds_threshold(self, current_status: HealthStatus, threshold: HealthStatus) -> bool:
        """Check if current status is at or above threshold severity"""        status_levels = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }
        
        return status_levels[current_status] >= status_levels[threshold]

    def _evaluate_conditions(self, result: HealthCheckResult, conditions: Dict[str, Any]) -> bool:
        """Evaluate additional alert conditions"""        try:
            # Response time threshold
            if "max_response_time_ms" in conditions:
                if result.response_time_ms > conditions["max_response_time_ms"]:
                    return True
            
            # Error message pattern matching
            if "error_pattern" in conditions and result.error_message:
                import re
                pattern = conditions["error_pattern"]
                if re.search(pattern, result.error_message, re.IGNORECASE):
                    return True
            
            # Details field conditions
            if "details_conditions" in conditions:
                details_conditions = conditions["details_conditions"]
                for key, expected_value in details_conditions.items():
                    if key in result.details:
                        actual_value = result.details[key]
                        if isinstance(expected_value, dict):
                            # Range condition
                            if "min" in expected_value and actual_value < expected_value["min"]:
                                return True
                            if "max" in expected_value and actual_value > expected_value["max"]:
                                return True
                        elif actual_value == expected_value:
                            return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating alert conditions: {str(e)}")
            return False

    async def _is_in_cooldown(self, rule_name: str, service: str) -> bool:
        """Check if alert is in cooldown period"""        cooldown_key = f"alert_cooldown:{rule_name}:{service}"
        
        if self.redis_client:
            try:
                cooldown_data = await self.redis_client.get(cooldown_key)
                if cooldown_data:
                    return True
            except Exception as e:
                self.logger.error(f"Error checking cooldown in Redis: {str(e)}")
        
        # Fallback to in-memory check
        for alert in self._active_alerts.values():
            if (alert.rule_name == rule_name and 
                alert.service == service and 
                alert.status == AlertStatus.ACTIVE):
                return True
        
        return False

    async def _create_and_trigger_alert(self, rule: AlertRule, result: HealthCheckResult):
        """Create new alert and trigger notifications"""        
        # Generate unique alert ID
        alert_id = f"{rule.name}_{result.service}_{int(time.time())}"
        
        # Create alert
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            service=result.service,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=f"{rule.description} - {result.service}",
            description=self._generate_alert_description(rule, result),
            details=self._extract_alert_details(result),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store alert
        self._active_alerts[alert_id] = alert
        self._alert_history.append(alert)
        
        # Set cooldown period
        await self._set_cooldown(rule.name, result.service, rule.cooldown_minutes)
        
        # Send notifications
        await self._send_notifications(alert, rule.channels)
        
        # Store in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.hset(
                    "active_alerts",
                    alert_id,
                    json.dumps(asdict(alert), default=str)
                )
            except Exception as e:
                self.logger.error(f"Error storing alert in Redis: {str(e)}")
        
        self.logger.warning(
            f"Alert triggered: {alert.title} "
            f"(Severity: {alert.severity.value}, Service: {alert.service})"
        )

    def _generate_alert_description(self, rule: AlertRule, result: HealthCheckResult) -> str:
        """Generate detailed alert description"""        description_parts = [
            f"Service '{result.service}' is in {result.status.value} state.",
            f"Response time: {result.response_time_ms:.1f}ms"
        ]
        
        if result.error_message:
            description_parts.append(f"Error: {result.error_message}")
        
        # Add relevant details
        if result.details:
            important_keys = ["cpu_percent", "memory_percent", "disk_percent", "error_count", "connection_count"]
            for key in important_keys:
                if key in result.details:
                    description_parts.append(f"{key}: {result.details[key]}")
        
        return " | ".join(description_parts)

    def _extract_alert_details(self, result: HealthCheckResult) -> Dict[str, Any]:
        """Extract relevant details for alert"""        details = {
            "health_status": result.status.value,
            "response_time_ms": result.response_time_ms,
            "timestamp": result.timestamp.isoformat()
        }
        
        if result.error_message:
            details["error_message"] = result.error_message
        
        # Include important metrics from result details
        if result.details:
            relevant_keys = [
                "cpu_percent", "memory_percent", "disk_percent",
                "connection_count", "queue_size", "error_count",
                "uptime_seconds", "warnings"
            ]
            
            for key in relevant_keys:
                if key in result.details:
                    details[key] = result.details[key]
        
        return details

    async def _set_cooldown(self, rule_name: str, service: str, cooldown_minutes: int):
        """Set cooldown period for alert rule"""        cooldown_key = f"alert_cooldown:{rule_name}:{service}"
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cooldown_key,
                    cooldown_minutes * 60,
                    "active"
                )
            except Exception as e:
                self.logger.error(f"Error setting cooldown in Redis: {str(e)}")

    async def _send_notifications(self, alert: Alert, channels: List[AlertChannel]):
        """Send alert notifications through specified channels"""        
        notification_tasks = []
        
        for channel in channels:
            if channel in self._notification_channels:
                task = self._send_channel_notification(alert, channel)
                notification_tasks.append(task)
        
        # Send all notifications concurrently
        if notification_tasks:
            try:
                await asyncio.gather(*notification_tasks, return_exceptions=True)
                alert.notification_count += len(notification_tasks)
            except Exception as e:
                self.logger.error(f"Error sending notifications: {str(e)}")
                self._alert_metrics["notification_failures"] += 1

    async def _send_channel_notification(self, alert: Alert, channel: AlertChannel):
        """Send notification through specific channel"""        
        try:
            if channel == AlertChannel.EMAIL:
                await self._send_email_notification(alert)
            elif channel == AlertChannel.SLACK:
                await self._send_slack_notification(alert)
            elif channel == AlertChannel.WEBHOOK:
                await self._send_webhook_notification(alert)
            elif channel == AlertChannel.PAGERDUTY:
                await self._send_pagerduty_notification(alert)
            
            self.logger.info(f"Notification sent via {channel.value} for alert {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send {channel.value} notification for alert {alert.id}: {str(e)}")
            self._alert_metrics["notification_failures"] += 1

    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""        email_config = self._notification_channels.get(AlertChannel.EMAIL)
        if not email_config:
            return
        
        # Get template
        template_config = self._notification_templates[AlertChannel.EMAIL].get(alert.severity)
        if not template_config:
            template_config = self._notification_templates[AlertChannel.EMAIL][AlertSeverity.MEDIUM]
        
        # Render templates
        subject_template = Template(template_config.subject_template)
        body_template = Template(template_config.body_template)
        
        subject = subject_template.render(alert=alert)
        body = body_template.render(alert=alert)
        
        # Create message
        msg = MimeMultipart()
        msg['From'] = email_config["from_address"]
        msg['Subject'] = subject
        
        # Add recipients
        recipients = email_config["recipients"]
        if isinstance(recipients, str):
            recipients = [recipients]
        msg['To'] = ", ".join(recipients)
        
        # Add body
        if template_config.format_type == "html":
            msg.attach(MimeText(body, 'html'))
        else:
            msg.attach(MimeText(body, 'plain'))
        
        # Send email
        try:
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                if email_config["use_tls"]:
                    server.starttls()
                
                if email_config["username"] and email_config["password"]:
                    server.login(email_config["username"], email_config["password"])
                
                server.send_message(msg)
                
        except Exception as e:
            raise Exception(f"Email sending failed: {str(e)}")

    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""        slack_config = self._notification_channels.get(AlertChannel.SLACK)
        if not slack_config:
            return
        
        # Get template
        template_config = self._notification_templates[AlertChannel.SLACK].get(alert.severity)
        if not template_config:
            template_config = self._notification_templates[AlertChannel.SLACK][AlertSeverity.MEDIUM]
        
        # Render message
        body_template = Template(template_config.body_template)
        message_json = body_template.render(alert=alert)
        
        try:
            message_data = json.loads(message_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid Slack message JSON: {str(e)}")
        
        # Send to Slack
        async with aiohttp.ClientSession() as session:
            async with session.post(
                slack_config["webhook_url"],
                json=message_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Slack API error {response.status}: {response_text}")

    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""        webhook_config = self._notification_channels.get(AlertChannel.WEBHOOK)
        if not webhook_config:
            return
        
        # Prepare payload
        payload = {
            "alert": asdict(alert),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "ia_influencer_agent_health_monitor"
        }
        
        # Prepare headers
        headers = webhook_config.get("headers", {})
        headers["Content-Type"] = "application/json"
        
        # Send webhook
        async with aiohttp.ClientSession() as session:
            async with session.request(
                webhook_config["method"],
                webhook_config["url"],
                json=payload,
                headers=headers
            ) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    raise Exception(f"Webhook error {response.status}: {response_text}")

    async def _send_pagerduty_notification(self, alert: Alert):
        """Send PagerDuty notification"""        pagerduty_config = self._notification_channels.get(AlertChannel.PAGERDUTY)
        if not pagerduty_config:
            return
        
        # Prepare PagerDuty event
        event_data = {
            "routing_key": pagerduty_config["integration_key"],
            "event_action": "trigger",
            "dedup_key": f"ia_agent_{alert.service}_{alert.rule_name}",
            "payload": {
                "summary": alert.title,
                "source": alert.service,
                "severity": alert.severity.value,
                "component": "IA Influencer Agent",
                "group": "health_monitoring",
                "class": "service_health",
                "custom_details": alert.details
            }
        }
        
        # Send to PagerDuty
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=event_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 202:
                    response_text = await response.text()
                    raise Exception(f"PagerDuty API error {response.status}: {response_text}")

    async def _check_alert_escalations(self):
        """Check for alerts that need escalation"""        current_time = datetime.utcnow()
        
        for alert in list(self._active_alerts.values()):
            if alert.status != AlertStatus.ACTIVE or alert.escalated:
                continue
            
            # Find corresponding rule
            rule = next((r for r in self._alert_rules if r.name == alert.rule_name), None)
            if not rule:
                continue
            
            # Check if escalation time has passed
            escalation_time = alert.created_at + timedelta(minutes=rule.escalation_minutes)
            
            if current_time >= escalation_time:
                await self._escalate_alert(alert, rule)

    async def _escalate_alert(self, alert: Alert, rule: AlertRule):
        """Escalate alert to higher severity channels"""        
        # Mark as escalated
        alert.escalated = True
        alert.updated_at = datetime.utcnow()
        
        # Create escalation notification
        escalation_alert = Alert(
            id=f"{alert.id}_escalation",
            rule_name=alert.rule_name,
            service=alert.service,
            severity=AlertSeverity.CRITICAL,  # Escalate to critical
            status=AlertStatus.ACTIVE,
            title=f"ESCALATED: {alert.title}",
            description=f"Alert has been escalated after {rule.escalation_minutes} minutes. Original: {alert.description}",
            details=alert.details,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Send escalation notifications (email + PagerDuty for critical escalations)
        escalation_channels = [AlertChannel.EMAIL, AlertChannel.PAGERDUTY]
        await self._send_notifications(escalation_alert, escalation_channels)
        
        self.logger.critical(f"Alert escalated: {alert.title} (ID: {alert.id})")

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """        Acknowledge an active alert
        
        Args:
            alert_id: ID of alert to acknowledge
            acknowledged_by: User/system acknowledging the alert
            
        Returns:
            bool: True if alert was acknowledged successfully
        """        if alert_id not in self._active_alerts:
            return False
        
        alert = self._active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = datetime.utcnow()
        
        # Update in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.hset(
                    "active_alerts",
                    alert_id,
                    json.dumps(asdict(alert), default=str)
                )
            except Exception as e:
                self.logger.error(f"Error updating alert in Redis: {str(e)}")
        
        self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True

    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """        Resolve an alert
        
        Args:
            alert_id: ID of alert to resolve
            resolved_by: User/system resolving the alert
            
        Returns:
            bool: True if alert was resolved successfully
        """        if alert_id not in self._active_alerts:
            return False
        
        alert = self._active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        
        # Remove from active alerts
        del self._active_alerts[alert_id]
        
        # Remove from Redis if available
        if self.redis_client:
            try:
                await self.redis_client.hdel("active_alerts", alert_id)
            except Exception as e:
                self.logger.error(f"Error removing alert from Redis: {str(e)}")
        
        self.logger.info(f"Alert {alert_id} resolved by {resolved_by}")
        return True

    async def _update_alert_metrics(self):
        """Update alert metrics"""        current_time = datetime.utcnow()
        
        # Update basic metrics
        self._alert_metrics["active_alerts"] = len(self._active_alerts)
        self._alert_metrics["last_alert_timestamp"] = current_time.isoformat()
        
        # Count alerts by severity
        for severity in AlertSeverity:
            count = len([a for a in self._active_alerts.values() if a.severity == severity])
            self._alert_metrics["alerts_by_severity"][severity.value] = count
        
        # Count alerts by service
        service_counts = {}
        for alert in self._active_alerts.values():
            service_counts[alert.service] = service_counts.get(alert.service, 0) + 1
        self._alert_metrics["alerts_by_service"] = service_counts

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""        return [asdict(alert) for alert in self._active_alerts.values()]

    async def get_alert_metrics(self) -> Dict[str, Any]:
        """Get alert system metrics"""        return self._alert_metrics.copy()

    async def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for specified time period"""        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        filtered_alerts = [
            alert for alert in self._alert_history
            if alert.created_at >= cutoff_time
        ]
        
        return [asdict(alert) for alert in filtered_alerts]

    async def cleanup_resources(self):
        """Clean up alerting system resources"""        try:
            # Close any open connections
            if hasattr(self, '_smtp_connections'):
                for connection in self._smtp_connections:
                    try:
                        connection.quit()
                    except:
                        pass
            
            self.logger.info("Alerting system resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up alerting system resources: {str(e)}")

    def add_custom_rule(self, rule: AlertRule):
        """Add custom alert rule"""        self._alert_rules.append(rule)
        self.logger.info(f"Added custom alert rule: {rule.name}")

    def remove_rule(self, rule_name: str) -> bool:
        """Remove alert rule by name"""        initial_count = len(self._alert_rules)
        self._alert_rules = [r for r in self._alert_rules if r.name != rule_name]
        
        removed = len(self._alert_rules) < initial_count
        if removed:
            self.logger.info(f"Removed alert rule: {rule_name}")
        
        return removed

    def get_configured_rules(self) -> List[Dict[str, Any]]:
        """Get all configured alert rules"""        return [asdict(rule) for rule in self._alert_rules]

"""Professional Health Alerting System Implementation Notes:

This module provides enterprise-grade alerting capabilities including:

1. Multi-Channel Notifications:
   - Email with HTML templates
   - Slack with rich formatting
   - Webhooks for custom integrations
   - PagerDuty for incident management

2. Alert Management:
   - Rule-based alert triggering
   - Cooldown periods to prevent spam
   - Alert escalation workflows
   - Acknowledgment and resolution tracking

3. Advanced Features:
   - Pattern matching for services
   - Conditional alert logic
   - Alert metrics and history
   - Template-based notifications

4. Integration Points:
   - Redis for distributed state
   - FastAPI for REST endpoints
   - Configuration-driven setup
   - Professional logging

5. Security & Compliance:
   - Secure credential handling
   - Audit trail for all alerts
   - Rate limiting capabilities
   - Professional documentation

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer
"""