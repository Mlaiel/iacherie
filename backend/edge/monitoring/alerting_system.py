"""Edge Alerting System
====================

Advanced alerting system for edge computing infrastructure,
providing intelligent alert management, routing, and escalation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json
import smtplib
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of alerts."""
    PERFORMANCE = "performance"
    HEALTH = "health"
    SECURITY = "security"
    RESOURCE = "resource"
    NETWORK = "network"
    APPLICATION = "application"
    SYSTEM = "system"
    CUSTOM = "custom"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    """Alert status states."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class ChannelType(str, Enum):
    """Alert channel types."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    CUSTOM = "custom"


@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    name: str
    description: str
    alert_type: AlertType
    condition: str  # Expression to evaluate
    severity: AlertSeverity
    enabled: bool = True
    cooldown: int = 300  # seconds
    auto_resolve: bool = True
    auto_resolve_timeout: int = 3600  # seconds
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert instance."""
    alert_id: str
    rule_id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    source: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_message: Optional[str] = None


@dataclass
class AlertChannel:
    """Alert notification channel configuration."""
    channel_id: str
    name: str
    channel_type: ChannelType
    config: Dict[str, Any]
    enabled: bool = True
    severity_filter: List[AlertSeverity] = field(default_factory=list)
    type_filter: List[AlertType] = field(default_factory=list)
    tags_filter: Dict[str, str] = field(default_factory=dict)


class EdgeAlertingSystem:
    """Advanced alerting system for edge computing infrastructure."""
    
    def __init__(self,
                 alert_retention: int = 2592000,  # 30 days
                 max_alerts_per_rule: int = 1000,
                 escalation_interval: int = 1800):  # 30 minutes
        
        self.alert_retention = alert_retention
        self.max_alerts_per_rule = max_alerts_per_rule
        self.escalation_interval = escalation_interval
        
        # Alert management
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.rule_cooldowns: Dict[str, datetime] = {}
        
        # Notification channels
        self.alert_channels: Dict[str, AlertChannel] = {}
        self.channel_implementations = {
            ChannelType.EMAIL: self._send_email_alert,
            ChannelType.WEBHOOK: self._send_webhook_alert,
            ChannelType.SLACK: self._send_slack_alert,
            ChannelType.SMS: self._send_sms_alert,
            ChannelType.PAGERDUTY: self._send_pagerduty_alert
        }
        
        # Escalation and suppression
        self.escalation_rules: Dict[str, List[str]] = {}  # rule_id -> channel_ids
        self.suppression_rules: List[Dict[str, Any]] = []
        
        # Event handlers
        self.alert_handlers: List[Callable] = []
        self.resolution_handlers: List[Callable] = []
        
        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.escalation_task: Optional[asyncio.Task] = None
        
        # Control flags
        self.running = False
        
        # Statistics
        self.alert_stats = {
            'total_generated': 0,
            'total_resolved': 0,
            'notifications_sent': 0,
            'escalations_triggered': 0
        }
        
        logger.info("EdgeAlertingSystem initialized")
    
    async def start(self):
        """Start the alerting system."""
        if self.running:
            logger.warning("Alerting system already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.escalation_task = asyncio.create_task(self._escalation_loop())
        
        logger.info("Edge alerting system started")
    
    async def stop(self):
        """Stop the alerting system."""
        self.running = False
        
        # Cancel background tasks
        tasks = [self.monitoring_task, self.cleanup_task, self.escalation_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Edge alerting system stopped")
    
    async def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add an alert rule."""
        try:
            self.alert_rules[rule.rule_id] = rule
            logger.info(f"Added alert rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add alert rule {rule.name}: {e}")
            return False
    
    async def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule."""
        try:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                
                # Remove from cooldowns
                if rule_id in self.rule_cooldowns:
                    del self.rule_cooldowns[rule_id]
                
                logger.info(f"Removed alert rule: {rule_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove alert rule {rule_id}: {e}")
            return False
    
    async def add_alert_channel(self, channel: AlertChannel) -> bool:
        """Add an alert notification channel."""
        try:
            self.alert_channels[channel.channel_id] = channel
            logger.info(f"Added alert channel: {channel.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add alert channel {channel.name}: {e}")
            return False
    
    async def remove_alert_channel(self, channel_id: str) -> bool:
        """Remove an alert notification channel."""
        try:
            if channel_id in self.alert_channels:
                del self.alert_channels[channel_id]
                logger.info(f"Removed alert channel: {channel_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove alert channel {channel_id}: {e}")
            return False
    
    async def trigger_alert(self,
                           rule_id: str,
                           source: str,
                           title: str,
                           message: str,
                           details: Optional[Dict[str, Any]] = None,
                           tags: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Trigger an alert based on a rule."""
        
        if rule_id not in self.alert_rules:
            logger.warning(f"Alert rule {rule_id} not found")
            return None
        
        rule = self.alert_rules[rule_id]
        
        if not rule.enabled:
            logger.debug(f"Alert rule {rule_id} is disabled")
            return None
        
        # Check cooldown
        if await self._is_in_cooldown(rule_id):
            logger.debug(f"Alert rule {rule_id} is in cooldown")
            return None
        
        # Check suppression
        if await self._is_suppressed(rule, source, tags or {}):
            logger.debug(f"Alert for rule {rule_id} is suppressed")
            return None
        
        # Create alert
        alert_id = str(uuid.uuid4())
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule_id,
            alert_type=rule.alert_type,
            severity=rule.severity,
            status=AlertStatus.OPEN,
            title=title,
            message=message,
            source=source,
            timestamp=datetime.now(),
            tags={**rule.tags, **(tags or {})},
            details=details or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Update cooldown
        self.rule_cooldowns[rule_id] = datetime.now()
        
        # Update statistics
        self.alert_stats['total_generated'] += 1
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
        
        logger.info(f"Triggered alert: {title} (ID: {alert_id})")
        return alert_id
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                
                logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    async def resolve_alert(self,
                           alert_id: str,
                           resolution_message: Optional[str] = None) -> bool:
        """Resolve an alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                alert.resolution_message = resolution_message
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                # Update statistics
                self.alert_stats['total_resolved'] += 1
                
                # Trigger resolution handlers
                for handler in self.resolution_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(alert)
                        else:
                            handler(alert)
                    except Exception as e:
                        logger.error(f"Error in resolution handler: {e}")
                
                logger.info(f"Alert {alert_id} resolved")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    async def get_active_alerts(self,
                               severity: Optional[AlertSeverity] = None,
                               alert_type: Optional[AlertType] = None) -> List[Alert]:
        """Get active alerts with optional filtering."""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        # Sort by severity and timestamp
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
            AlertSeverity.INFO: 4
        }
        
        alerts.sort(key=lambda a: (severity_order[a.severity], a.timestamp), reverse=True)
        return alerts
    
    async def get_alert_history(self,
                               limit: Optional[int] = None,
                               since: Optional[datetime] = None,
                               status: Optional[AlertStatus] = None) -> List[Alert]:
        """Get alert history with optional filtering."""
        alerts = self.alert_history.copy()
        
        if since:
            alerts = [a for a in alerts if a.timestamp > since]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        if limit:
            alerts = alerts[:limit]
        
        return alerts
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alerting system statistics."""
        
        # Calculate additional statistics
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        recent_alerts = [a for a in self.alert_history if a.timestamp > last_24h]
        weekly_alerts = [a for a in self.alert_history if a.timestamp > last_week]
        
        stats = {
            **self.alert_stats,
            'active_alerts': len(self.active_alerts),
            'alerts_last_24h': len(recent_alerts),
            'alerts_last_week': len(weekly_alerts),
            'alert_rules': len(self.alert_rules),
            'alert_channels': len(self.alert_channels),
            'by_severity': {},
            'by_type': {},
            'resolution_time_avg': 0.0
        }
        
        # Count by severity and type
        for alert in self.alert_history:
            severity = alert.severity.value
            alert_type = alert.alert_type.value
            
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            stats['by_type'][alert_type] = stats['by_type'].get(alert_type, 0) + 1
        
        # Calculate average resolution time
        resolved_alerts = [a for a in self.alert_history if a.resolved_at]
        if resolved_alerts:
            resolution_times = [
                (a.resolved_at - a.timestamp).seconds 
                for a in resolved_alerts
            ]
            stats['resolution_time_avg'] = sum(resolution_times) / len(resolution_times)
        
        return stats
    
    def add_alert_handler(self, handler: Callable):
        """Add alert event handler."""
        self.alert_handlers.append(handler)
    
    def add_resolution_handler(self, handler: Callable):
        """Add alert resolution handler."""
        self.resolution_handlers.append(handler)
    
    # Private methods
    
    async def _monitoring_loop(self):
        """Main monitoring loop for auto-resolution."""
        while self.running:
            try:
                await self._check_auto_resolution()
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self.running:
            try:
                await self._cleanup_old_alerts()
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _escalation_loop(self):
        """Background escalation loop."""
        while self.running:
            try:
                await self._check_escalations()
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in escalation loop: {e}")
                await asyncio.sleep(300)
    
    async def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if alert rule is in cooldown period."""
        if rule_id not in self.rule_cooldowns:
            return False
        
        rule = self.alert_rules[rule_id]
        last_alert = self.rule_cooldowns[rule_id]
        
        return (datetime.now() - last_alert).seconds < rule.cooldown
    
    async def _is_suppressed(self, rule: AlertRule, source: str, tags: Dict[str, str]) -> bool:
        """Check if alert should be suppressed."""
        for suppression_rule in self.suppression_rules:
            # Check if suppression rule matches
            if (suppression_rule.get('rule_id') == rule.rule_id or
                suppression_rule.get('source') == source or
                any(tags.get(k) == v for k, v in suppression_rule.get('tags', {}).items())):
                
                # Check if suppression is still active
                start_time = suppression_rule.get('start_time')
                end_time = suppression_rule.get('end_time')
                
                if start_time and end_time:
                    now = datetime.now()
                    if start_time <= now <= end_time:
                        return True
        
        return False
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications to configured channels."""
        
        for channel_id, channel in self.alert_channels.items():
            if not channel.enabled:
                continue
            
            # Apply filters
            if channel.severity_filter and alert.severity not in channel.severity_filter:
                continue
            
            if channel.type_filter and alert.alert_type not in channel.type_filter:
                continue
            
            if channel.tags_filter:
                if not any(alert.tags.get(k) == v for k, v in channel.tags_filter.items()):
                    continue
            
            # Send notification
            try:
                channel_impl = self.channel_implementations.get(channel.channel_type)
                if channel_impl:
                    await channel_impl(alert, channel)
                    self.alert_stats['notifications_sent'] += 1
                else:
                    logger.warning(f"Unknown channel type: {channel.channel_type}")
                    
            except Exception as e:
                logger.error(f"Failed to send alert to channel {channel.name}: {e}")
    
    async def _check_auto_resolution(self):
        """Check for alerts that should be auto-resolved."""
        
        for alert_id, alert in list(self.active_alerts.items()):
            rule = self.alert_rules.get(alert.rule_id)
            
            if not rule or not rule.auto_resolve:
                continue
            
            # Check if alert should be auto-resolved
            age = (datetime.now() - alert.timestamp).seconds
            
            if age > rule.auto_resolve_timeout:
                await self.resolve_alert(alert_id, "Auto-resolved due to timeout")
    
    async def _check_escalations(self):
        """Check for alerts that need escalation."""
        
        for alert_id, alert in self.active_alerts.items():
            # Skip acknowledged alerts
            if alert.status == AlertStatus.ACKNOWLEDGED:
                continue
            
            # Check if alert is old enough for escalation
            age = (datetime.now() - alert.timestamp).seconds
            
            if age > self.escalation_interval:
                await self._escalate_alert(alert)
    
    async def _escalate_alert(self, alert: Alert):
        """Escalate an alert to higher notification levels."""
        
        # This is a placeholder for escalation logic
        # In a real implementation, this would send to escalation channels
        
        logger.info(f"Escalating alert {alert.alert_id}: {alert.title}")
        self.alert_stats['escalations_triggered'] += 1
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts from history."""
        
        cutoff_time = datetime.now() - timedelta(seconds=self.alert_retention)
        
        # Remove old alerts from history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]
        
        # Clean up old cooldowns
        old_cooldowns = [
            rule_id for rule_id, timestamp in self.rule_cooldowns.items()
            if timestamp < cutoff_time
        ]
        
        for rule_id in old_cooldowns:
            del self.rule_cooldowns[rule_id]
    
    # Channel implementations
    
    async def _send_email_alert(self, alert: Alert, channel: AlertChannel):
        """Send email alert notification."""
        
        config = channel.config
        smtp_server = config.get('smtp_server')
        smtp_port = config.get('smtp_port', 587)
        username = config.get('username')
        password = config.get('password')
        to_addresses = config.get('to_addresses', [])
        
        if not all([smtp_server, username, password, to_addresses]):
            logger.error(f"Incomplete email configuration for channel {channel.name}")
            return
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
        
        # Email body
        body = f"""
Alert Details:
- ID: {alert.alert_id}
- Type: {alert.alert_type.value}
- Severity: {alert.severity.value}
- Source: {alert.source}
- Time: {alert.timestamp}
- Message: {alert.message}

Details: {json.dumps(alert.details, indent=2) if alert.details else 'None'}
Tags: {json.dumps(alert.tags, indent=2) if alert.tags else 'None'}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Sent email alert for {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert, channel: AlertChannel):
        """Send webhook alert notification."""
        
        config = channel.config
        url = config.get('url')
        headers = config.get('headers', {})
        
        if not url:
            logger.error(f"No URL configured for webhook channel {channel.name}")
            return
        
        # Prepare payload
        payload = {
            'alert_id': alert.alert_id,
            'rule_id': alert.rule_id,
            'type': alert.alert_type.value,
            'severity': alert.severity.value,
            'status': alert.status.value,
            'title': alert.title,
            'message': alert.message,
            'source': alert.source,
            'timestamp': alert.timestamp.isoformat(),
            'tags': alert.tags,
            'details': alert.details
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Sent webhook alert for {alert.alert_id}")
                    else:
                        logger.error(f"Webhook returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    async def _send_slack_alert(self, alert: Alert, channel: AlertChannel):
        """Send Slack alert notification."""
        
        config = channel.config
        webhook_url = config.get('webhook_url')
        
        if not webhook_url:
            logger.error(f"No webhook URL configured for Slack channel {channel.name}")
            return
        
        # Create Slack message
        color_map = {
            AlertSeverity.CRITICAL: 'danger',
            AlertSeverity.HIGH: 'warning',
            AlertSeverity.MEDIUM: 'warning',
            AlertSeverity.LOW: 'good',
            AlertSeverity.INFO: 'good'
        }
        
        payload = {
            'attachments': [{
                'color': color_map.get(alert.severity, 'warning'),
                'title': alert.title,
                'text': alert.message,
                'fields': [
                    {'title': 'Severity', 'value': alert.severity.value, 'short': True},
                    {'title': 'Type', 'value': alert.alert_type.value, 'short': True},
                    {'title': 'Source', 'value': alert.source, 'short': True},
                    {'title': 'Time', 'value': alert.timestamp.isoformat(), 'short': True}
                ],
                'footer': f'Alert ID: {alert.alert_id}'
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Sent Slack alert for {alert.alert_id}")
                    else:
                        logger.error(f"Slack webhook returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    async def _send_sms_alert(self, alert: Alert, channel: AlertChannel):
        """Send SMS alert notification."""
        
        # This would integrate with SMS service (Twilio, AWS SNS, etc.)
        logger.info(f"SMS alert placeholder for {alert.alert_id}")
    
    async def _send_pagerduty_alert(self, alert: Alert, channel: AlertChannel):
        """Send PagerDuty alert notification."""
        
        # This would integrate with PagerDuty API
        logger.info(f"PagerDuty alert placeholder for {alert.alert_id}")


def create_alerting_system(
    alert_retention: int = 2592000,
    max_alerts_per_rule: int = 1000,
    escalation_interval: int = 1800
) -> EdgeAlertingSystem:
    """Create and configure an alerting system instance."""
    return EdgeAlertingSystem(
        alert_retention=alert_retention,
        max_alerts_per_rule=max_alerts_per_rule,
        escalation_interval=escalation_interval
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_alerting_system():
        """Test the alerting system."""
        alerting = create_alerting_system()
        
        # Add alert handler
        async def alert_handler(alert: Alert):
            print(f"New alert: {alert.title}")
        
        alerting.add_alert_handler(alert_handler)
        
        # Start alerting system
        await alerting.start()
        
        # Add alert rule
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test alert rule",
            alert_type=AlertType.SYSTEM,
            condition="cpu > 80",
            severity=AlertSeverity.HIGH
        )
        await alerting.add_alert_rule(rule)
        
        # Add webhook channel
        channel = AlertChannel(
            channel_id="test_webhook",
            name="Test Webhook",
            channel_type=ChannelType.WEBHOOK,
            config={'url': 'https://httpbin.org/post'}
        )
        await alerting.add_alert_channel(channel)
        
        # Trigger test alert
        alert_id = await alerting.trigger_alert(
            rule_id="test_rule",
            source="test_system",
            title="Test Alert",
            message="This is a test alert"
        )
        
        if alert_id:
            print(f"Triggered alert: {alert_id}")
            
            # Get active alerts
            active = await alerting.get_active_alerts()
            print(f"Active alerts: {len(active)}")
            
            # Get statistics
            stats = await alerting.get_alert_statistics()
            print(f"Alert statistics: {stats}")
        
        # Stop alerting system
        await alerting.stop()
    
    # Run test
    asyncio.run(test_alerting_system())