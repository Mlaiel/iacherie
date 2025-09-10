"""
Monitoring Module - Alerting System
Intelligent alerting system for Ainflue Distribution Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis.asyncio as redis
import httpx

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(Enum):
    """Alert status states"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    PAGERDUTY = "pagerduty"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    id: str
    name: str
    description: str
    condition: str  # Python expression to evaluate
    severity: AlertSeverity
    threshold: float
    duration: int  # seconds
    channels: List[AlertChannel]
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    cooldown: int = 300  # seconds between alerts
    escalation_rules: List[Dict] = field(default_factory=list)

@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationConfig:
    """Notification channel configuration"""
    channel: AlertChannel
    config: Dict[str, Any]
    enabled: bool = True
    severity_filter: List[AlertSeverity] = field(default_factory=list)

class AlertingSystem:
    """
    Intelligent alerting system with multiple notification channels
    and advanced alert management capabilities
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_configs: Dict[AlertChannel, NotificationConfig] = {}
        self.alert_history = deque(maxlen=10000)
        self.evaluation_tasks = {}
        self.running = False
        
    async def start(self):
        """Start the alerting system"""
        self.running = True
        logger.info("Starting alerting system")
        
        # Load configuration
        await self._load_alert_rules()
        await self._load_notification_configs()
        await self._load_active_alerts()
        
        # Start evaluation tasks
        await self._start_evaluation_tasks()
        
    async def stop(self):
        """Stop the alerting system"""
        self.running = False
        logger.info("Stopping alerting system")
        
        # Cancel evaluation tasks
        for task in self.evaluation_tasks.values():
            task.cancel()
        
        await asyncio.gather(*self.evaluation_tasks.values(), return_exceptions=True)
        
    async def add_alert_rule(self, rule: AlertRule):
        """Add or update an alert rule"""
        self.alert_rules[rule.id] = rule
        
        # Save to Redis
        await self.redis.hset("alert_rules", rule.id, json.dumps({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "condition": rule.condition,
            "severity": rule.severity.value,
            "threshold": rule.threshold,
            "duration": rule.duration,
            "channels": [c.value for c in rule.channels],
            "enabled": rule.enabled,
            "tags": rule.tags,
            "cooldown": rule.cooldown,
            "escalation_rules": rule.escalation_rules
        }))
        
        # Start evaluation task if enabled
        if rule.enabled and self.running:
            await self._start_rule_evaluation(rule)
            
        logger.info(f"Added alert rule: {rule.id}")
    
    async def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            
            # Remove from Redis
            await self.redis.hdel("alert_rules", rule_id)
            
            # Cancel evaluation task
            if rule_id in self.evaluation_tasks:
                self.evaluation_tasks[rule_id].cancel()
                del self.evaluation_tasks[rule_id]
            
            logger.info(f"Removed alert rule: {rule_id}")
    
    async def trigger_alert(self, rule_id: str, metrics: Dict[str, Any], context: Dict[str, Any] = None):
        """Trigger an alert for a rule"""
        if rule_id not in self.alert_rules:
            logger.warning(f"Alert rule not found: {rule_id}")
            return
        
        rule = self.alert_rules[rule_id]
        
        # Check cooldown
        if await self._is_in_cooldown(rule_id):
            logger.debug(f"Alert rule {rule_id} is in cooldown period")
            return
        
        # Create alert
        alert_id = f"{rule_id}_{int(datetime.now().timestamp())}"
        alert = Alert(
            id=alert_id,
            rule_id=rule_id,
            title=rule.name,
            description=rule.description,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            timestamp=datetime.now(),
            metrics=metrics,
            tags=rule.tags,
            context=context or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        await self._save_alert(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        # Set cooldown
        await self._set_cooldown(rule_id, rule.cooldown)
        
        # Add to history
        self.alert_history.append(alert)
        
        logger.warning(f"Alert triggered: {alert.title} [{alert.severity.value}]")
    
    async def acknowledge_alert(self, alert_id: str, user_id: str):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user_id
            
            await self._save_alert(alert)
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            await self._save_alert(alert)
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert_id}")
    
    async def suppress_alert(self, alert_id: str, duration: int = 3600):
        """Suppress an alert for a specified duration"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            
            await self._save_alert(alert)
            
            # Set suppression expiry
            await self.redis.setex(f"alert_suppressed:{alert_id}", duration, "1")
            
            logger.info(f"Alert suppressed: {alert_id} for {duration} seconds")
    
    async def _load_alert_rules(self):
        """Load alert rules from Redis"""
        rules_data = await self.redis.hgetall("alert_rules")
        
        for rule_id, rule_json in rules_data.items():
            try:
                rule_data = json.loads(rule_json)
                rule = AlertRule(
                    id=rule_data["id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    condition=rule_data["condition"],
                    severity=AlertSeverity(rule_data["severity"]),
                    threshold=rule_data["threshold"],
                    duration=rule_data["duration"],
                    channels=[AlertChannel(c) for c in rule_data["channels"]],
                    enabled=rule_data["enabled"],
                    tags=rule_data["tags"],
                    cooldown=rule_data["cooldown"],
                    escalation_rules=rule_data["escalation_rules"]
                )
                self.alert_rules[rule.id] = rule
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"Failed to load alert rule {rule_id}: {e}")
    
    async def _load_notification_configs(self):
        """Load notification configurations"""
        # Default configurations - would typically load from database
        self.notification_configs = {
            AlertChannel.EMAIL: NotificationConfig(
                channel=AlertChannel.EMAIL,
                config={
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "alerts@ainflue.com",
                    "password": "app_password",
                    "recipients": ["admin@ainflue.com", "ops@ainflue.com"]
                }
            ),
            AlertChannel.SLACK: NotificationConfig(
                channel=AlertChannel.SLACK,
                config={
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#alerts",
                    "username": "AinflueBot"
                }
            ),
            AlertChannel.WEBHOOK: NotificationConfig(
                channel=AlertChannel.WEBHOOK,
                config={
                    "url": "https://api.ainflue.com/alerts/webhook",
                    "headers": {"Authorization": "Bearer token"},
                    "method": "POST"
                }
            )
        }
    
    async def _load_active_alerts(self):
        """Load active alerts from Redis"""
        alerts_data = await self.redis.hgetall("active_alerts")
        
        for alert_id, alert_json in alerts_data.items():
            try:
                alert_data = json.loads(alert_json)
                alert = Alert(
                    id=alert_data["id"],
                    rule_id=alert_data["rule_id"],
                    title=alert_data["title"],
                    description=alert_data["description"],
                    severity=AlertSeverity(alert_data["severity"]),
                    status=AlertStatus(alert_data["status"]),
                    timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                    resolved_at=datetime.fromisoformat(alert_data["resolved_at"]) if alert_data.get("resolved_at") else None,
                    acknowledged_at=datetime.fromisoformat(alert_data["acknowledged_at"]) if alert_data.get("acknowledged_at") else None,
                    acknowledged_by=alert_data.get("acknowledged_by"),
                    metrics=alert_data["metrics"],
                    tags=alert_data["tags"],
                    context=alert_data["context"]
                )
                self.active_alerts[alert.id] = alert
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"Failed to load alert {alert_id}: {e}")
    
    async def _start_evaluation_tasks(self):
        """Start evaluation tasks for all enabled rules"""
        for rule in self.alert_rules.values():
            if rule.enabled:
                await self._start_rule_evaluation(rule)
    
    async def _start_rule_evaluation(self, rule: AlertRule):
        """Start evaluation task for a rule"""
        if rule.id in self.evaluation_tasks:
            self.evaluation_tasks[rule.id].cancel()
        
        self.evaluation_tasks[rule.id] = asyncio.create_task(
            self._evaluate_rule_continuously(rule)
        )
    
    async def _evaluate_rule_continuously(self, rule: AlertRule):
        """Continuously evaluate a rule"""
        try:
            while self.running:
                try:
                    # Get metrics for evaluation
                    metrics = await self._get_metrics_for_rule(rule)
                    
                    # Evaluate condition
                    if await self._evaluate_condition(rule, metrics):
                        # Wait for duration before triggering
                        await asyncio.sleep(rule.duration)
                        
                        # Re-check condition after duration
                        updated_metrics = await self._get_metrics_for_rule(rule)
                        if await self._evaluate_condition(rule, updated_metrics):
                            await self.trigger_alert(rule.id, updated_metrics)
                    
                    # Wait before next evaluation
                    await asyncio.sleep(30)  # Evaluate every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error evaluating rule {rule.id}: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
        except asyncio.CancelledError:
            logger.debug(f"Rule evaluation cancelled: {rule.id}")
    
    async def _get_metrics_for_rule(self, rule: AlertRule) -> Dict[str, Any]:
        """Get metrics needed for rule evaluation"""
        # This would typically fetch from your metrics system
        # For demonstration, returning sample metrics
        return {
            "error_rate": 0.05,
            "response_time": 250,
            "cpu_usage": 75,
            "memory_usage": 85,
            "active_connections": 1500,
            "failed_distributions": 10,
            "platform_errors": 5
        }
    
    async def _evaluate_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate rule condition against metrics"""
        try:
            # Create safe evaluation context
            eval_context = {
                "metrics": metrics,
                "threshold": rule.threshold,
                "__builtins__": {}  # Disable built-ins for security
            }
            
            # Evaluate condition
            result = eval(rule.condition, eval_context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating condition for rule {rule.id}: {e}")
            return False
    
    async def _send_notifications(self, alert: Alert):
        """Send notifications for alert"""
        rule = self.alert_rules[alert.rule_id]
        
        for channel in rule.channels:
            if channel in self.notification_configs:
                config = self.notification_configs[channel]
                if config.enabled:
                    try:
                        await self._send_notification(alert, channel, config)
                    except Exception as e:
                        logger.error(f"Failed to send {channel.value} notification: {e}")
    
    async def _send_notification(self, alert: Alert, channel: AlertChannel, config: NotificationConfig):
        """Send notification to specific channel"""
        if channel == AlertChannel.EMAIL:
            await self._send_email_notification(alert, config)
        elif channel == AlertChannel.SLACK:
            await self._send_slack_notification(alert, config)
        elif channel == AlertChannel.WEBHOOK:
            await self._send_webhook_notification(alert, config)
        # Add more channels as needed
    
    async def _send_email_notification(self, alert: Alert, config: NotificationConfig):
        """Send email notification"""
        smtp_config = config.config
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['username']
        msg['To'] = ', '.join(smtp_config['recipients'])
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
        
        # Create email body
        body = f"""
Alert: {alert.title}
Severity: {alert.severity.value.upper()}
Time: {alert.timestamp.isoformat()}
Description: {alert.description}

Metrics:
{json.dumps(alert.metrics, indent=2)}

Context:
{json.dumps(alert.context, indent=2)}

Alert ID: {alert.id}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            logger.info(f"Email notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert, config: NotificationConfig):
        """Send Slack notification"""
        slack_config = config.config
        
        # Create Slack message
        color_map = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.HIGH: "warning",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "good",
            AlertSeverity.INFO: "good"
        }
        
        payload = {
            "channel": slack_config['channel'],
            "username": slack_config['username'],
            "attachments": [{
                "color": color_map.get(alert.severity, "warning"),
                "title": alert.title,
                "text": alert.description,
                "fields": [
                    {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                    {"title": "Time", "value": alert.timestamp.isoformat(), "short": True},
                    {"title": "Alert ID", "value": alert.id, "short": True}
                ],
                "footer": "Ainflue Alerting System",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        # Send to Slack
        async with httpx.AsyncClient() as client:
            response = await client.post(slack_config['webhook_url'], json=payload)
            if response.status_code == 200:
                logger.info(f"Slack notification sent for alert {alert.id}")
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
    
    async def _send_webhook_notification(self, alert: Alert, config: NotificationConfig):
        """Send webhook notification"""
        webhook_config = config.config
        
        # Create webhook payload
        payload = {
            "alert_id": alert.id,
            "rule_id": alert.rule_id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "timestamp": alert.timestamp.isoformat(),
            "metrics": alert.metrics,
            "tags": alert.tags,
            "context": alert.context
        }
        
        # Send webhook
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=webhook_config['method'],
                url=webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {})
            )
            if response.status_code < 400:
                logger.info(f"Webhook notification sent for alert {alert.id}")
            else:
                logger.error(f"Failed to send webhook notification: {response.status_code}")
    
    async def _save_alert(self, alert: Alert):
        """Save alert to Redis"""
        alert_data = {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "timestamp": alert.timestamp.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "metrics": alert.metrics,
            "tags": alert.tags,
            "context": alert.context
        }
        
        if alert.status == AlertStatus.RESOLVED:
            # Move to resolved alerts
            await self.redis.hset("resolved_alerts", alert.id, json.dumps(alert_data))
            await self.redis.hdel("active_alerts", alert.id)
        else:
            # Keep in active alerts
            await self.redis.hset("active_alerts", alert.id, json.dumps(alert_data))
    
    async def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if rule is in cooldown period"""
        cooldown_key = f"alert_cooldown:{rule_id}"
        return await self.redis.exists(cooldown_key)
    
    async def _set_cooldown(self, rule_id: str, duration: int):
        """Set cooldown period for rule"""
        cooldown_key = f"alert_cooldown:{rule_id}"
        await self.redis.setex(cooldown_key, duration, "1")
    
    # Query methods
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get all active alerts"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return list(self.alert_history)[-limit:]
    
    async def get_alert_stats(self) -> Dict[str, Any]:
        """Get alerting system statistics"""
        active_count = len(self.active_alerts)
        severity_counts = {}
        
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "active_alerts": active_count,
            "total_rules": len(self.alert_rules),
            "enabled_rules": sum(1 for r in self.alert_rules.values() if r.enabled),
            "severity_breakdown": severity_counts,
            "evaluation_tasks": len(self.evaluation_tasks),
            "notification_channels": len(self.notification_configs)
        }

# Predefined alert rules for common scenarios
PREDEFINED_RULES = [
    AlertRule(
        id="high_error_rate",
        name="High Error Rate",
        description="Error rate exceeds threshold",
        condition="metrics['error_rate'] > threshold",
        severity=AlertSeverity.HIGH,
        threshold=0.05,  # 5% error rate
        duration=300,  # 5 minutes
        channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
        tags={"category": "performance", "team": "sre"}
    ),
    AlertRule(
        id="slow_response_time",
        name="Slow Response Time",
        description="Response time is above acceptable threshold",
        condition="metrics['response_time'] > threshold",
        severity=AlertSeverity.MEDIUM,
        threshold=1000,  # 1 second
        duration=180,  # 3 minutes
        channels=[AlertChannel.SLACK],
        tags={"category": "performance", "team": "backend"}
    ),
    AlertRule(
        id="distribution_failures",
        name="Distribution Failures",
        description="High number of distribution failures",
        condition="metrics['failed_distributions'] > threshold",
        severity=AlertSeverity.CRITICAL,
        threshold=50,
        duration=60,  # 1 minute
        channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK],
        tags={"category": "distribution", "team": "platform"}
    )
]