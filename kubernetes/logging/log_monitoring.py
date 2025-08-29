"""
IA Influencer Agent - Log Monitoring Service
Real-time log monitoring and alerting system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import aiohttp
import aioredis
from slack_sdk.web.async_client import AsyncWebClient

from ...core.config import settings
from ...core.exceptions import LoggingError, MonitoringError
from .log_aggregator import LogEntry, LogLevel
from .log_analytics import LogAnalyticsEngine, LogAlert, AlertSeverity


class NotificationChannel(str, Enum):
    """Notification channel types"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    TEAMS = "teams"
    DISCORD = "discord"


class MonitoringState(str, Enum):
    """Monitoring service state"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class NotificationConfig:
    """Notification configuration"""
    channel: NotificationChannel
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MonitoringRule:
    """Real-time monitoring rule"""
    id: str
    name: str
    description: str
    log_pattern: str
    condition: str  # e.g., "count > 10 in 5min"
    severity: AlertSeverity
    notification_channels: List[NotificationChannel]
    enabled: bool = True
    cooldown_minutes: int = 15
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def is_in_cooldown(self) -> bool:
        """Check if rule is in cooldown period"""
        if not self.last_triggered:
            return False
        
        cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
        return datetime.now(timezone.utc) < cooldown_end
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.last_triggered:
            data['last_triggered'] = self.last_triggered.isoformat()
        return data


class NotificationSender:
    """Base notification sender interface"""
    
    async def send_notification(self, 
                               message: str,
                               subject: str,
                               severity: AlertSeverity,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send notification"""
        # Default implementation for notification senders without sending support
        logging.warning(f"Notification sending not implemented for {self.__class__.__name__}")
        return False


class EmailNotificationSender(NotificationSender):
    """Email notification sender"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_host = config.get('smtp_host', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email')
        self.to_emails = config.get('to_emails', [])
        self.use_tls = config.get('use_tls', True)
    
    async def send_notification(self, 
                               message: str,
                               subject: str,
                               severity: AlertSeverity,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send email notification"""
        if not self.to_emails:
            return False
        
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[{severity.value.upper()}] {subject}"
            
            # Create HTML body
            html_body = self._create_html_body(message, severity, metadata)
            msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            logging.info(f"Email notification sent to {len(self.to_emails)} recipients")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_html_body(self, 
                         message: str,
                         severity: AlertSeverity,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create HTML email body"""
        severity_colors = {
            AlertSeverity.LOW: "#28a745",
            AlertSeverity.MEDIUM: "#ffc107",
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545"
        }
        
        color = severity_colors.get(severity, "#6c757d")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px; margin-bottom: 20px;">
                <h2 style="color: {color}; margin-top: 0;">
                    IA Influencer Agent Alert - {severity.value.title()}
                </h2>
                <p style="font-size: 16px; color: #333;">
                    {message}
                </p>
            </div>
            
            {self._format_metadata_html(metadata) if metadata else ''}
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">
                    Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                    System: IA Influencer Agent Monitoring<br>
                    Contact: mlaiel@live.de
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as HTML table"""
        html = """
        <div style="margin: 20px 0;">
            <h3 style="color: #333;">Alert Details</h3>
            <table style="border-collapse: collapse; width: 100%;">
        """
        
        for key, value in metadata.items():
            html += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; background-color: #f9f9f9; font-weight: bold;">
                        {key.replace('_', ' ').title()}
                    </td>
                    <td style="border: 1px solid #ddd; padding: 8px;">
                        {str(value)}
                    </td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html


class SlackNotificationSender(NotificationSender):
    """Slack notification sender"""
    
    def __init__(self, config: Dict[str, Any]):
        self.token = config.get('token')
        self.channel = config.get('channel', '#alerts')
        self.client = AsyncWebClient(token=self.token) if self.token else None
    
    async def send_notification(self, 
                               message: str,
                               subject: str,
                               severity: AlertSeverity,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send Slack notification"""
        if not self.client:
            return False
        
        try:
            # Create Slack message
            severity_colors = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger"
            }
            
            color = severity_colors.get(severity, "warning")
            
            attachment = {
                "color": color,
                "title": f"IA Influencer Agent Alert - {severity.value.title()}",
                "text": message,
                "fields": [],
                "footer": "IA Influencer Agent Monitoring",
                "ts": int(datetime.now(timezone.utc).timestamp())
            }
            
            # Add metadata as fields
            if metadata:
                for key, value in metadata.items():
                    attachment["fields"].append({
                        "title": key.replace('_', ' ').title(),
                        "value": str(value),
                        "short": True
                    })
            
            # Send message
            response = await self.client.chat_postMessage(
                channel=self.channel,
                text=f"Alert: {subject}",
                attachments=[attachment]
            )
            
            if response["ok"]:
                logging.info(f"Slack notification sent to {self.channel}")
                return True
            else:
                logging.error(f"Slack notification failed: {response.get('error')}")
                return False
            
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")
            return False


class WebhookNotificationSender(NotificationSender):
    """Webhook notification sender"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('webhook_url')
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.auth_token = config.get('auth_token')
        
        if self.auth_token:
            self.headers['Authorization'] = f"Bearer {self.auth_token}"
    
    async def send_notification(self, 
                               message: str,
                               subject: str,
                               severity: AlertSeverity,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send webhook notification"""
        if not self.webhook_url:
            return False
        
        try:
            # Create payload
            payload = {
                "alert": {
                    "subject": subject,
                    "message": message,
                    "severity": severity.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "ia-influencer-agent",
                    "metadata": metadata or {}
                }
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status < 400:
                        logging.info(f"Webhook notification sent to {self.webhook_url}")
                        return True
                    else:
                        error_text = await response.text()
                        logging.error(f"Webhook notification failed: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logging.error(f"Failed to send webhook notification: {e}")
            return False


class TeamsNotificationSender(NotificationSender):
    """Microsoft Teams notification sender"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('webhook_url')
    
    async def send_notification(self, 
                               message: str,
                               subject: str,
                               severity: AlertSeverity,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send Teams notification"""
        if not self.webhook_url:
            return False
        
        try:
            # Create Teams adaptive card
            severity_colors = {
                AlertSeverity.LOW: "Good",
                AlertSeverity.MEDIUM: "Warning",
                AlertSeverity.HIGH: "Attention",
                AlertSeverity.CRITICAL: "Attention"
            }
            
            theme_color = {
                AlertSeverity.LOW: "28a745",
                AlertSeverity.MEDIUM: "ffc107",
                AlertSeverity.HIGH: "fd7e14",
                AlertSeverity.CRITICAL: "dc3545"
            }.get(severity, "6c757d")
            
            card = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": theme_color,
                "summary": f"IA Influencer Agent Alert - {severity.value.title()}",
                "sections": [
                    {
                        "activityTitle": f"IA Influencer Agent Alert - {severity.value.title()}",
                        "activitySubtitle": subject,
                        "text": message,
                        "facts": []
                    }
                ]
            }
            
            # Add metadata as facts
            if metadata:
                for key, value in metadata.items():
                    card["sections"][0]["facts"].append({
                        "name": key.replace('_', ' ').title(),
                        "value": str(value)
                    })
            
            # Add timestamp
            card["sections"][0]["facts"].append({
                "name": "Timestamp",
                "value": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            })
            
            # Send to Teams
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=card,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status < 400:
                        logging.info("Teams notification sent successfully")
                        return True
                    else:
                        error_text = await response.text()
                        logging.error(f"Teams notification failed: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logging.error(f"Failed to send Teams notification: {e}")
            return False


class LogMonitoringService:
    """Real-time log monitoring service for IA Influencer Agent"""
    
    def __init__(self, 
                 analytics_engine: LogAnalyticsEngine,
                 redis_url: str = "redis://localhost:6379"):
        self.analytics_engine = analytics_engine
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        self.state = MonitoringState.STOPPED
        self.monitoring_rules: List[MonitoringRule] = []
        self.notification_configs: Dict[NotificationChannel, NotificationConfig] = {}
        self.notification_senders: Dict[NotificationChannel, NotificationSender] = {}
        
        self.log_buffer: List[LogEntry] = []
        self.buffer_size = 100
        self.check_interval = 30  # seconds
        
        self._setup_default_rules()
        self._setup_notification_channels()
    
    def _setup_default_rules(self):
        """Setup default monitoring rules"""
        default_rules = [
            MonitoringRule(
                id="critical_errors",
                name="Critical Error Spike",
                description="Critical errors exceeding threshold",
                log_pattern="level:CRITICAL",
                condition="count > 5 in 5min",
                severity=AlertSeverity.CRITICAL,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_minutes=10
            ),
            MonitoringRule(
                id="high_error_rate",
                name="High Error Rate",
                description="Error rate above 10% in 15 minutes",
                log_pattern="level:ERROR OR level:CRITICAL",
                condition="rate > 0.1 in 15min",
                severity=AlertSeverity.HIGH,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_minutes=15
            ),
            MonitoringRule(
                id="ai_processing_failures",
                name="AI Processing Failures",
                description="AI processing failures spike",
                log_pattern="service:ai* AND level:ERROR",
                condition="count > 20 in 30min",
                severity=AlertSeverity.HIGH,
                notification_channels=[NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
                cooldown_minutes=20
            ),
            MonitoringRule(
                id="fingerprinting_errors",
                name="Fingerprinting Errors",
                description="Fingerprinting service errors",
                log_pattern="service:fingerprinting AND level:ERROR",
                condition="count > 10 in 15min",
                severity=AlertSeverity.HIGH,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.TEAMS],
                cooldown_minutes=15
            ),
            MonitoringRule(
                id="auth_failures",
                name="Authentication Failures",
                description="Authentication failure spike",
                log_pattern="module:auth AND level:ERROR",
                condition="count > 50 in 10min",
                severity=AlertSeverity.CRITICAL,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_minutes=5
            ),
            MonitoringRule(
                id="revenue_processing_errors",
                name="Revenue Processing Errors",
                description="Revenue processing system errors",
                log_pattern="service:monetization AND level:ERROR",
                condition="count > 1 in 60min",
                severity=AlertSeverity.CRITICAL,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.TEAMS],
                cooldown_minutes=30
            ),
            MonitoringRule(
                id="database_connection_errors",
                name="Database Connection Errors",
                description="Database connection issues",
                log_pattern="message:*database* AND level:ERROR",
                condition="count > 5 in 10min",
                severity=AlertSeverity.CRITICAL,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_minutes=10
            ),
            MonitoringRule(
                id="storage_errors",
                name="Storage Errors",
                description="File storage system errors",
                log_pattern="service:storage AND level:ERROR",
                condition="count > 10 in 30min",
                severity=AlertSeverity.MEDIUM,
                notification_channels=[NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
                cooldown_minutes=20
            )
        ]
        
        self.monitoring_rules.extend(default_rules)
    
    def _setup_notification_channels(self):
        """Setup notification channels from configuration"""
        # Email configuration
        if hasattr(settings, 'EMAIL_CONFIG'):
            email_config = NotificationConfig(
                channel=NotificationChannel.EMAIL,
                enabled=True,
                config=settings.EMAIL_CONFIG
            )
            self.notification_configs[NotificationChannel.EMAIL] = email_config
            self.notification_senders[NotificationChannel.EMAIL] = EmailNotificationSender(
                settings.EMAIL_CONFIG
            )
        
        # Slack configuration
        if hasattr(settings, 'SLACK_CONFIG'):
            slack_config = NotificationConfig(
                channel=NotificationChannel.SLACK,
                enabled=True,
                config=settings.SLACK_CONFIG
            )
            self.notification_configs[NotificationChannel.SLACK] = slack_config
            self.notification_senders[NotificationChannel.SLACK] = SlackNotificationSender(
                settings.SLACK_CONFIG
            )
        
        # Webhook configuration
        if hasattr(settings, 'WEBHOOK_CONFIG'):
            webhook_config = NotificationConfig(
                channel=NotificationChannel.WEBHOOK,
                enabled=True,
                config=settings.WEBHOOK_CONFIG
            )
            self.notification_configs[NotificationChannel.WEBHOOK] = webhook_config
            self.notification_senders[NotificationChannel.WEBHOOK] = WebhookNotificationSender(
                settings.WEBHOOK_CONFIG
            )
        
        # Teams configuration
        if hasattr(settings, 'TEAMS_CONFIG'):
            teams_config = NotificationConfig(
                channel=NotificationChannel.TEAMS,
                enabled=True,
                config=settings.TEAMS_CONFIG
            )
            self.notification_configs[NotificationChannel.TEAMS] = teams_config
            self.notification_senders[NotificationChannel.TEAMS] = TeamsNotificationSender(
                settings.TEAMS_CONFIG
            )
    
    async def start(self):
        """Start the monitoring service"""
        if self.state != MonitoringState.STOPPED:
            raise MonitoringError(f"Service already running or in transition. State: {self.state}")
        
        self.state = MonitoringState.STARTING
        
        try:
            # Connect to Redis
            self.redis_client = await aioredis.from_url(self.redis_url)
            
            # Start monitoring tasks
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._alert_checking_loop())
            
            self.state = MonitoringState.RUNNING
            logging.info("Log monitoring service started")
            
        except Exception as e:
            self.state = MonitoringState.ERROR
            logging.error(f"Failed to start monitoring service: {e}")
            raise MonitoringError(f"Startup failed: {e}")
    
    async def stop(self):
        """Stop the monitoring service"""
        self.state = MonitoringState.STOPPING
        
        try:
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            self.state = MonitoringState.STOPPED
            logging.info("Log monitoring service stopped")
            
        except Exception as e:
            logging.error(f"Error stopping monitoring service: {e}")
            self.state = MonitoringState.ERROR
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.state == MonitoringState.RUNNING:
            try:
                # Process buffered logs
                if self.log_buffer:
                    await self._process_log_batch(self.log_buffer.copy())
                    self.log_buffer.clear()
                
                # Wait for next cycle
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    async def _alert_checking_loop(self):
        """Periodic alert checking loop"""
        while self.state == MonitoringState.RUNNING:
            try:
                # Check analytics-based alerts
                triggered_alerts = await self.analytics_engine.check_alerts()
                
                for alert_data in triggered_alerts:
                    await self._send_alert_notifications(
                        alert_data["alert"]["name"],
                        f"Alert triggered: {alert_data['alert']['description']}",
                        AlertSeverity(alert_data["alert"]["severity"]),
                        alert_data
                    )
                
                # Wait for next check (longer interval for analytics)
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logging.error(f"Error in alert checking loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def add_log_entry(self, log_entry: LogEntry):
        """Add log entry to monitoring buffer"""
        if self.state != MonitoringState.RUNNING:
            return
        
        self.log_buffer.append(log_entry)
        
        # Process immediately if buffer is full
        if len(self.log_buffer) >= self.buffer_size:
            await self._process_log_batch(self.log_buffer.copy())
            self.log_buffer.clear()
    
    async def _process_log_batch(self, logs: List[LogEntry]):
        """Process batch of logs for rule matching"""
        for rule in self.monitoring_rules:
            if not rule.enabled or rule.is_in_cooldown():
                continue
            
            try:
                # Check if rule matches any logs in batch
                matching_logs = []
                for log in logs:
                    if self._log_matches_pattern(log, rule.log_pattern):
                        matching_logs.append(log)
                
                if matching_logs:
                    # Evaluate condition
                    if await self._evaluate_rule_condition(rule, matching_logs):
                        # Rule triggered
                        await self._trigger_rule(rule, matching_logs)
                
            except Exception as e:
                logging.error(f"Error processing rule '{rule.name}': {e}")
    
    def _log_matches_pattern(self, log_entry: LogEntry, pattern: str) -> bool:
        """Check if log entry matches pattern"""
        # Simple pattern matching - can be enhanced with proper query parsing
        pattern_lower = pattern.lower()
        
        # Check level matching
        if "level:" in pattern_lower:
            for part in pattern_lower.split():
                if part.startswith("level:"):
                    level = part.split(":", 1)[1]
                    if log_entry.level.value.lower() == level:
                        return True
        
        # Check service matching
        if "service:" in pattern_lower:
            for part in pattern_lower.split():
                if part.startswith("service:"):
                    service_pattern = part.split(":", 1)[1]
                    if service_pattern.endswith("*"):
                        # Wildcard matching
                        service_prefix = service_pattern[:-1]
                        if log_entry.service and log_entry.service.lower().startswith(service_prefix):
                            return True
                    else:
                        if log_entry.service and log_entry.service.lower() == service_pattern:
                            return True
        
        # Check module matching
        if "module:" in pattern_lower:
            for part in pattern_lower.split():
                if part.startswith("module:"):
                    module = part.split(":", 1)[1]
                    if log_entry.module and log_entry.module.lower() == module:
                        return True
        
        # Check message content
        if "message:" in pattern_lower:
            for part in pattern_lower.split():
                if part.startswith("message:"):
                    message_pattern = part.split(":", 1)[1]
                    if message_pattern.startswith("*") and message_pattern.endswith("*"):
                        # Contains pattern
                        search_term = message_pattern[1:-1]
                        if search_term in log_entry.message.lower():
                            return True
        
        return False
    
    async def _evaluate_rule_condition(self, 
                                     rule: MonitoringRule, 
                                     matching_logs: List[LogEntry]) -> bool:
        """Evaluate rule condition"""
        # Parse condition (simplified)
        condition = rule.condition.lower()
        
        if "count >" in condition:
            # Extract threshold
            parts = condition.split("count >")
            if len(parts) > 1:
                threshold_part = parts[1].strip().split()[0]
                try:
                    threshold = int(threshold_part)
                    return len(matching_logs) > threshold
                except ValueError:
                    pass
        
        elif "rate >" in condition:
            # Calculate error rate (simplified)
            # This would need access to total log count for accurate rate calculation
            return len(matching_logs) > 0  # Simplified for now
        
        return False
    
    async def _trigger_rule(self, rule: MonitoringRule, matching_logs: List[LogEntry]):
        """Trigger monitoring rule"""
        rule.last_triggered = datetime.now(timezone.utc)
        rule.trigger_count += 1
        
        # Create alert message
        subject = f"Monitoring Alert: {rule.name}"
        message = f"{rule.description}\n\nTriggered by {len(matching_logs)} matching log entries."
        
        # Add sample log details
        if matching_logs:
            message += f"\n\nSample log entry:\n"
            sample_log = matching_logs[0]
            message += f"Service: {sample_log.service}\n"
            message += f"Level: {sample_log.level.value}\n"
            message += f"Message: {sample_log.message}\n"
            message += f"Timestamp: {sample_log.timestamp.isoformat()}"
        
        metadata = {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "matching_logs_count": len(matching_logs),
            "trigger_count": rule.trigger_count,
            "condition": rule.condition
        }
        
        # Send notifications
        for channel in rule.notification_channels:
            if channel in self.notification_senders:
                await self._send_notification(
                    channel, subject, message, rule.severity, metadata
                )
        
        logging.warning(f"Monitoring rule '{rule.name}' triggered with {len(matching_logs)} matching logs")
    
    async def _send_notification(self,
                                channel: NotificationChannel,
                                subject: str,
                                message: str,
                                severity: AlertSeverity,
                                metadata: Optional[Dict[str, Any]] = None):
        """Send notification to specific channel"""
        if channel not in self.notification_senders:
            logging.warning(f"No sender configured for channel: {channel}")
            return
        
        config = self.notification_configs.get(channel)
        if not config or not config.enabled:
            return
        
        try:
            sender = self.notification_senders[channel]
            success = await sender.send_notification(message, subject, severity, metadata)
            
            if success:
                logging.info(f"Notification sent via {channel.value}")
            else:
                logging.error(f"Failed to send notification via {channel.value}")
                
        except Exception as e:
            logging.error(f"Error sending notification via {channel.value}: {e}")
    
    async def _send_alert_notifications(self,
                                       subject: str,
                                       message: str,
                                       severity: AlertSeverity,
                                       metadata: Optional[Dict[str, Any]] = None):
        """Send notifications to all configured channels"""
        for channel, sender in self.notification_senders.items():
            config = self.notification_configs.get(channel)
            if config and config.enabled:
                await self._send_notification(channel, subject, message, severity, metadata)
    
    def add_monitoring_rule(self, rule: MonitoringRule):
        """Add custom monitoring rule"""
        self.monitoring_rules.append(rule)
    
    def remove_monitoring_rule(self, rule_id: str) -> bool:
        """Remove monitoring rule"""
        for i, rule in enumerate(self.monitoring_rules):
            if rule.id == rule_id:
                del self.monitoring_rules[i]
                return True
        return False
    
    def get_monitoring_rule(self, rule_id: str) -> Optional[MonitoringRule]:
        """Get monitoring rule by ID"""
        for rule in self.monitoring_rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def update_monitoring_rule(self, rule_id: str, **kwargs) -> bool:
        """Update monitoring rule"""
        rule = self.get_monitoring_rule(rule_id)
        if rule:
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            return True
        return False
    
    def configure_notification_channel(self, 
                                     channel: NotificationChannel,
                                     config: Dict[str, Any],
                                     enabled: bool = True):
        """Configure notification channel"""
        notification_config = NotificationConfig(
            channel=channel,
            enabled=enabled,
            config=config
        )
        
        self.notification_configs[channel] = notification_config
        
        # Create appropriate sender
        if channel == NotificationChannel.EMAIL:
            self.notification_senders[channel] = EmailNotificationSender(config)
        elif channel == NotificationChannel.SLACK:
            self.notification_senders[channel] = SlackNotificationSender(config)
        elif channel == NotificationChannel.WEBHOOK:
            self.notification_senders[channel] = WebhookNotificationSender(config)
        elif channel == NotificationChannel.TEAMS:
            self.notification_senders[channel] = TeamsNotificationSender(config)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get monitoring service status"""
        return {
            "state": self.state.value,
            "enabled_rules": len([r for r in self.monitoring_rules if r.enabled]),
            "total_rules": len(self.monitoring_rules),
            "configured_channels": len(self.notification_configs),
            "enabled_channels": len([c for c in self.notification_configs.values() if c.enabled]),
            "buffer_size": len(self.log_buffer),
            "last_check": datetime.now(timezone.utc).isoformat()
        }
    
    def get_rule_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for all monitoring rules"""
        stats = []
        for rule in self.monitoring_rules:
            rule_stats = rule.to_dict()
            rule_stats["is_in_cooldown"] = rule.is_in_cooldown()
            stats.append(rule_stats)
        
        return stats
