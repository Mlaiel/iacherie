"""Enterprise Alerting System

Comprehensive alerting infrastructure for real-time monitoring and notification
of critical events in the IA Influencer content protection platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart


class AlertSeverity(Enum):
    """Alert severity levels."""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertState(Enum):
    """Alert lifecycle states."""    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class NotificationChannel(Enum):
    """Available notification channels."""    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DASHBOARD = "dashboard"


@dataclass
class Alert:
    """Represents an alert instance."""    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    description: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    state: AlertState
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    notification_count: int = 0
    suppressed_until: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""        data = asdict(self)
        # Convert enums and datetime objects
        data['severity'] = self.severity.value
        data['state'] = self.state.value
        data['triggered_at'] = self.triggered_at.isoformat()
        if self.acknowledged_at:
            data['acknowledged_at'] = self.acknowledged_at.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        if self.suppressed_until:
            data['suppressed_until'] = self.suppressed_until.isoformat()
        return data


@dataclass
class AlertRule:
    """Defines conditions for triggering alerts."""    name: str
    condition: Callable[[Dict], bool]
    severity: AlertSeverity
    message_template: str
    description: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    notification_channels: List[NotificationChannel]
    cooldown_minutes: int = 5
    max_notifications: int = 10
    auto_resolve_minutes: Optional[int] = None
    enabled: bool = True


class RuleEngine:
    """Evaluates alert rules against metrics and events."""    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.rule_states: Dict[str, Dict] = {}
        
    def register_rule(self, rule: AlertRule):
        """Register an alert rule."""        self.rules[rule.name] = rule
        self.rule_states[rule.name] = {
            'last_triggered': None,
            'last_notification': None,
            'notification_count': 0,
            'active_alert_id': None
        }
        
    def evaluate_rules(self, metrics: Dict, events: List[Dict]) -> List[Alert]:
        """Evaluate all rules against current metrics and events."""        triggered_alerts = []
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
                
            try:
                # Check if rule condition is met
                if rule.condition({"metrics": metrics, "events": events}):
                    alert = self._create_alert_from_rule(rule)
                    if self._should_trigger_alert(rule_name, alert):
                        triggered_alerts.append(alert)
                        self._update_rule_state(rule_name, alert.id)
                        
            except Exception as e:
                logging.error(f"Error evaluating rule {rule_name}: {e}")
                
        return triggered_alerts
    
    def _create_alert_from_rule(self, rule: AlertRule) -> Alert:
        """Create an alert instance from a rule."""        alert_id = f"{rule.name}_{int(datetime.utcnow().timestamp())}"
        
        return Alert(
            id=alert_id,
            rule_name=rule.name,
            severity=rule.severity,
            message=rule.message_template,
            description=rule.description,
            labels=rule.labels.copy(),
            annotations=rule.annotations.copy(),
            state=AlertState.TRIGGERED,
            triggered_at=datetime.utcnow()
        )
    
    def _should_trigger_alert(self, rule_name: str, alert: Alert) -> bool:
        """Check if alert should be triggered based on cooldown and limits."""        rule = self.rules[rule_name]
        state = self.rule_states[rule_name]
        now = datetime.utcnow()
        
        # Check cooldown period
        if state['last_triggered']:
            cooldown_end = state['last_triggered'] + timedelta(minutes=rule.cooldown_minutes)
            if now < cooldown_end:
                return False
                
        # Check notification limits
        if state['notification_count'] >= rule.max_notifications:
            return False
            
        return True
    
    def _update_rule_state(self, rule_name: str, alert_id: str):
        """Update rule state after triggering."""        self.rule_states[rule_name].update({
            'last_triggered': datetime.utcnow(),
            'notification_count': self.rule_states[rule_name]['notification_count'] + 1,
            'active_alert_id': alert_id
        })


class NotificationService:
    """Handles alert notifications across multiple channels."""    
    def __init__(self, config: Dict[str, Dict]):
        self.config = config
        self.notification_history: List[Dict] = []
        
    async def send_notification(self, alert: Alert, channels: List[NotificationChannel]):
        """Send alert notification through specified channels."""        tasks = []
        
        for channel in channels:
            if channel in self.config:
                if channel == NotificationChannel.EMAIL:
                    tasks.append(self._send_email_notification(alert))
                elif channel == NotificationChannel.SLACK:
                    tasks.append(self._send_slack_notification(alert))
                elif channel == NotificationChannel.WEBHOOK:
                    tasks.append(self._send_webhook_notification(alert))
                elif channel == NotificationChannel.SMS:
                    tasks.append(self._send_sms_notification(alert))
                elif channel == NotificationChannel.DASHBOARD:
                    tasks.append(self._send_dashboard_notification(alert))
        
        # Execute all notifications concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self._log_notification_results(alert, results)
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification."""        try:
            config = self.config[NotificationChannel.EMAIL]
            
            msg = MimeMultipart()
            msg['From'] = config['from']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.message}"
            
            body = self._format_alert_for_email(alert)
            msg.attach(MimeText(body, 'html'))
            
            # Send email (mock implementation)
            await asyncio.sleep(0.1)  # Simulate network delay
            
            self._record_notification(alert, NotificationChannel.EMAIL, "success")
            
        except Exception as e:
            self._record_notification(alert, NotificationChannel.EMAIL, f"failed: {e}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification."""        try:
            # Mock Slack API call
            await asyncio.sleep(0.1)
            self._record_notification(alert, NotificationChannel.SLACK, "success")
            
        except Exception as e:
            self._record_notification(alert, NotificationChannel.SLACK, f"failed: {e}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification."""        try:
            # Mock webhook call
            await asyncio.sleep(0.1)
            self._record_notification(alert, NotificationChannel.WEBHOOK, "success")
            
        except Exception as e:
            self._record_notification(alert, NotificationChannel.WEBHOOK, f"failed: {e}")
    
    async def _send_sms_notification(self, alert: Alert):
        """Send SMS notification."""        try:
            # Mock SMS service call
            await asyncio.sleep(0.1)
            self._record_notification(alert, NotificationChannel.SMS, "success")
            
        except Exception as e:
            self._record_notification(alert, NotificationChannel.SMS, f"failed: {e}")
    
    async def _send_dashboard_notification(self, alert: Alert):
        """Send dashboard notification."""        try:
            # Mock dashboard update
            await asyncio.sleep(0.05)
            self._record_notification(alert, NotificationChannel.DASHBOARD, "success")
            
        except Exception as e:
            self._record_notification(alert, NotificationChannel.DASHBOARD, f"failed: {e}")
    
    def _format_alert_for_email(self, alert: Alert) -> str:
        """Format alert for email body."""        severity_colors = {
            AlertSeverity.INFO: "#36A2EB",
            AlertSeverity.WARNING: "#FFCE56", 
            AlertSeverity.CRITICAL: "#FF6384",
            AlertSeverity.EMERGENCY: "#FF0000"
        }
        
        color = severity_colors.get(alert.severity, "#000000")
        
        return f"""        <html>
        <body>
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color};">[{alert.severity.value.upper()}] Alert Triggered</h2>
                <p><strong>Message:</strong> {alert.message}</p>
                <p><strong>Description:</strong> {alert.description}</p>
                <p><strong>Triggered At:</strong> {alert.triggered_at.isoformat()}</p>
                <p><strong>Alert ID:</strong> {alert.id}</p>
                
                <h3>Labels:</h3>
                <ul>
                    {"".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in alert.labels.items())}
                </ul>
                
                <h3>Annotations:</h3>
                <ul>
                    {"".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in alert.annotations.items())}
                </ul>
            </div>
        </body>
        </html>
        """    
    def _record_notification(self, alert: Alert, channel: NotificationChannel, result: str):
        """Record notification attempt."""        self.notification_history.append({
            'alert_id': alert.id,
            'channel': channel.value,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def _log_notification_results(self, alert: Alert, results: List):
        """Log notification results."""        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Notification failed for alert {alert.id}: {result}")


class AlertManager:
    """Centralized alert management system."""    
    def __init__(self, notification_config: Dict[str, Dict]):
        self.rule_engine = RuleEngine()
        self.notification_service = NotificationService(notification_config)
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.metrics_buffer = defaultdict(list)
        self.events_buffer = []
        
        # Register default rules for content protection platform
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default alert rules for the platform."""        
        # Content upload failure rate
        self.rule_engine.register_rule(AlertRule(
            name="content_upload_failure_rate_high",
            condition=lambda data: data["metrics"].get("content.upload_failure_rate", 0) > 0.1,
            severity=AlertSeverity.WARNING,
            message_template="Content upload failure rate is {failure_rate:.1%}",
            description="High failure rate detected in content upload processing",
            labels={"service": "content-upload", "team": "backend"},
            annotations={"runbook": "https://wiki/runbooks/content-upload"},
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            cooldown_minutes=15
        ))
        
        # AI processing latency
        self.rule_engine.register_rule(AlertRule(
            name="ai_processing_latency_high", 
            condition=lambda data: data["metrics"].get("ai.processing_time_avg", 0) > 30000,
            severity=AlertSeverity.CRITICAL,
            message_template="AI processing latency is {latency}ms",
            description="AI content processing is taking too long",
            labels={"service": "ai-processing", "team": "ml"},
            annotations={"impact": "User experience degraded", "priority": "P1"},
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
            cooldown_minutes=5
        ))
        
        # Protection system failure
        self.rule_engine.register_rule(AlertRule(
            name="protection_system_failure",
            condition=lambda data: data["metrics"].get("protection.system_health", 1) < 0.9,
            severity=AlertSeverity.EMERGENCY,
            message_template="Content protection system is degraded",
            description="Critical failure in content protection infrastructure",
            labels={"service": "protection", "team": "security"},
            annotations={"escalation": "immediate", "on-call": "security-team"},
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
            cooldown_minutes=1
        ))
        
        # Storage capacity warning
        self.rule_engine.register_rule(AlertRule(
            name="storage_capacity_warning",
            condition=lambda data: data["metrics"].get("storage.usage_percent", 0) > 85,
            severity=AlertSeverity.WARNING,
            message_template="Storage usage is at {usage}%",
            description="Storage capacity approaching limit",
            labels={"service": "storage", "team": "devops"},
            annotations={"action_required": "Add storage capacity"},
            notification_channels=[NotificationChannel.EMAIL],
            cooldown_minutes=60
        ))
    
    async def process_metrics(self, metrics: Dict):
        """Process incoming metrics for alert evaluation."""        # Store metrics for rule evaluation
        timestamp = datetime.utcnow()
        for metric_name, value in metrics.items():
            self.metrics_buffer[metric_name].append({
                'value': value,
                'timestamp': timestamp
            })
            
        # Keep only recent metrics (last hour)
        cutoff = timestamp - timedelta(hours=1)
        for metric_name in self.metrics_buffer:
            self.metrics_buffer[metric_name] = [
                m for m in self.metrics_buffer[metric_name] 
                if m['timestamp'] > cutoff
            ]
    
    async def process_event(self, event: Dict):
        """Process incoming event for alert evaluation."""        event['timestamp'] = datetime.utcnow()
        self.events_buffer.append(event)
        
        # Keep only recent events (last hour)
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.events_buffer = [
            e for e in self.events_buffer 
            if e['timestamp'] > cutoff
        ]
    
    async def evaluate_and_trigger_alerts(self):
        """Evaluate rules and trigger alerts."""        # Prepare current metrics summary
        current_metrics = {}
        for metric_name, values in self.metrics_buffer.items():
            if values:
                latest_value = values[-1]['value']
                current_metrics[metric_name] = latest_value
                
                # Calculate derived metrics
                if len(values) > 1:
                    # Calculate rate of change
                    recent_values = [v['value'] for v in values[-5:]]
                    current_metrics[f"{metric_name}_trend"] = sum(recent_values) / len(recent_values)
        
        # Evaluate rules
        triggered_alerts = self.rule_engine.evaluate_rules(current_metrics, self.events_buffer)
        
        # Process triggered alerts
        for alert in triggered_alerts:
            await self._handle_triggered_alert(alert)
    
    async def _handle_triggered_alert(self, alert: Alert):
        """Handle a triggered alert."""        # Store alert
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        rule = self.rule_engine.rules[alert.rule_name]
        await self.notification_service.send_notification(alert, rule.notification_channels)
        
        logging.info(f"Alert triggered: {alert.id} - {alert.message}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert."""        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            return True
        return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an active alert."""        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            return True
        return False
    
    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get list of active alerts."""        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
            
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)
    
    def get_alert_summary(self) -> Dict:
        """Get summary of alert status."""        active_by_severity = defaultdict(int)
        for alert in self.active_alerts.values():
            active_by_severity[alert.severity.value] += 1
            
        return {
            "total_active": len(self.active_alerts),
            "active_by_severity": dict(active_by_severity),
            "total_rules": len(self.rule_engine.rules),
            "enabled_rules": sum(1 for rule in self.rule_engine.rules.values() if rule.enabled),
            "notification_history_count": len(self.notification_service.notification_history),
            "timestamp": datetime.utcnow().isoformat()
        }
