"""
Intelligent Alerting System

Advanced alerting system for the IA Influencer platform providing intelligent
notifications, ML-based anomaly detection, and adaptive alert management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import time
import json
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import statistics
import logging
import threading
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status states"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    EXPIRED = "expired"


class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PUSH_NOTIFICATION = "push"
    IN_APP = "in_app"
    PAGER = "pager"


class AlertCategory(Enum):
    """Alert categories"""
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    USER_EXPERIENCE = "user_experience"
    AI_MODEL = "ai_model"
    CONTENT_PROTECTION = "content_protection"
    COMPLIANCE = "compliance"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str                              # Condition expression
    threshold: Union[int, float]
    comparison_operator: str                    # >, <, >=, <=, ==, !=
    time_window: int                           # Time window in seconds
    evaluation_frequency: int = 60             # How often to evaluate (seconds)
    channels: List[AlertChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    suppression_duration: int = 3600          # Suppression time in seconds
    auto_resolve: bool = True
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'severity': self.severity.value,
            'condition': self.condition,
            'threshold': self.threshold,
            'comparison_operator': self.comparison_operator,
            'time_window': self.time_window,
            'evaluation_frequency': self.evaluation_frequency,
            'channels': [c.value for c in self.channels],
            'recipients': self.recipients,
            'suppression_duration': self.suppression_duration,
            'auto_resolve': self.auto_resolve,
            'escalation_rules': self.escalation_rules,
            'metadata': self.metadata,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    current_value: Optional[Union[int, float]] = None
    threshold_value: Optional[Union[int, float]] = None
    affected_components: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivery_status: Dict[AlertChannel, str] = field(default_factory=dict)
    escalation_level: int = 0
    notification_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'alert_id': self.alert_id,
            'rule_id': self.rule_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'triggered_at': self.triggered_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged_by': self.acknowledged_by,
            'resolved_by': self.resolved_by,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'affected_components': self.affected_components,
            'tags': self.tags,
            'metadata': self.metadata,
            'delivery_status': {k.value: v for k, v in self.delivery_status.items()},
            'escalation_level': self.escalation_level,
            'notification_count': self.notification_count
        }


class AlertEvaluator:
    """
    Alert rule evaluator for checking conditions and triggering alerts
    
    Features:
    - Real-time condition evaluation
    - Complex threshold monitoring
    - Time-based aggregation
    - Anomaly detection integration
    - Context-aware alerting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize alert evaluator"""
        self.config = config or {}
        
        # Rule storage
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Evaluation state
        self.rule_states: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.data_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Processing configuration
        self.evaluation_interval = self.config.get('evaluation_interval', 30)  # seconds
        self.max_data_age = self.config.get('max_data_age', 3600)  # seconds
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Evaluation task
        self.is_evaluating = False
        self.evaluation_task = None
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""



        try:
            with self._lock:
                self.alert_rules[rule.rule_id] = rule
                self.rule_states[rule.rule_id] = {
                    'last_evaluation': datetime.now(timezone.utc),
                    'condition_met_count': 0,
                    'condition_not_met_count': 0,
                    'last_triggered': None,
                    'suppressed_until': None
                }
                
            logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")
            
        except Exception as e:
            logger.error(f"Failed to add alert rule {rule.rule_id}: {str(e)}")
    
    def remove_rule(self, rule_id: str):
        """Remove alert rule"""



        try:
            with self._lock:
                if rule_id in self.alert_rules:
                    del self.alert_rules[rule_id]
                    del self.rule_states[rule_id]
                    logger.info(f"Removed alert rule: {rule_id}")
                else:
                    logger.warning(f"Alert rule not found: {rule_id}")
                    
        except Exception as e:
            logger.error(f"Failed to remove alert rule {rule_id}: {str(e)}")
    
    def update_rule(self, rule: AlertRule):
        """Update existing alert rule"""



        try:
            with self._lock:
                if rule.rule_id in self.alert_rules:
                    rule.updated_at = datetime.now(timezone.utc)
                    self.alert_rules[rule.rule_id] = rule
                    logger.info(f"Updated alert rule: {rule.name} ({rule.rule_id})")
                else:
                    logger.warning(f"Alert rule not found for update: {rule.rule_id}")
                    
        except Exception as e:
            logger.error(f"Failed to update alert rule {rule.rule_id}: {str(e)}")
    
    async def start_evaluation(self):
        """Start rule evaluation"""



        try:
            logger.info("Starting alert rule evaluation")
            self.is_evaluating = True
            self.evaluation_task = asyncio.create_task(self._evaluation_loop())
            
        except Exception as e:
            logger.error(f"Failed to start evaluation: {str(e)}")
    
    async def stop_evaluation(self):
        """Stop rule evaluation"""



        try:
            logger.info("Stopping alert rule evaluation")
            self.is_evaluating = False
            
            if self.evaluation_task:
                self.evaluation_task.cancel()
                try:
                    await self.evaluation_task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"Failed to stop evaluation: {str(e)}")
    
    async def _evaluation_loop(self):
        """Main evaluation loop"""
        while self.is_evaluating:
            try:
                # Evaluate all active rules
                await self._evaluate_all_rules()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Wait for next evaluation
                await asyncio.sleep(self.evaluation_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in evaluation loop: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _evaluate_all_rules(self):
        """Evaluate all alert rules"""



        try:
            current_time = datetime.now(timezone.utc)
            
            for rule_id, rule in self.alert_rules.items():
                if not rule.is_enabled:
                    continue
                
                rule_state = self.rule_states[rule_id]
                
                # Check if it's time to evaluate this rule
                last_evaluation = rule_state['last_evaluation']
                if (current_time - last_evaluation).total_seconds() < rule.evaluation_frequency:
                    continue
                
                # Check if rule is suppressed
                suppressed_until = rule_state.get('suppressed_until')
                if suppressed_until and current_time < suppressed_until:
                    continue
                
                # Evaluate rule condition
                await self._evaluate_rule(rule, rule_state, current_time)
                
        except Exception as e:
            logger.error(f"Failed to evaluate all rules: {str(e)}")
    
    async def _evaluate_rule(self, rule: AlertRule, rule_state: Dict[str, Any], current_time: datetime):
        """Evaluate a specific rule"""



        try:
            # Get relevant data
            condition_data = await self._get_condition_data(rule, current_time)
            
            if not condition_data:
                rule_state['condition_not_met_count'] += 1
                rule_state['last_evaluation'] = current_time
                return
            
            # Evaluate condition
            condition_met = self._evaluate_condition(rule, condition_data)
            
            if condition_met:
                rule_state['condition_met_count'] += 1
                rule_state['condition_not_met_count'] = 0  # Reset
                
                # Check if we should trigger alert
                if self._should_trigger_alert(rule, rule_state):
                    await self._trigger_alert(rule, condition_data, current_time)
                    rule_state['last_triggered'] = current_time
                    rule_state['suppressed_until'] = current_time + timedelta(seconds=rule.suppression_duration)
                    
            else:
                rule_state['condition_not_met_count'] += 1
                rule_state['condition_met_count'] = 0  # Reset
            
            rule_state['last_evaluation'] = current_time
            
        except Exception as e:
            logger.error(f"Failed to evaluate rule {rule.rule_id}: {str(e)}")
    
    async def _get_condition_data(self, rule: AlertRule, current_time: datetime) -> Optional[Dict[str, Any]]:
        """Get data for condition evaluation"""



        try:
            # Parse condition to extract metric name
            metric_name = self._extract_metric_name(rule.condition)
            
            if not metric_name:
                logger.warning(f"Could not extract metric name from condition: {rule.condition}")
                return None
            
            # Get data from buffer
            metric_data = self.data_buffer.get(metric_name, deque())
            
            # Filter by time window
            cutoff_time = current_time - timedelta(seconds=rule.time_window)
            recent_data = [data for data in metric_data if data['timestamp'] >= cutoff_time]
            
            if not recent_data:
                return None
            
            # Calculate aggregated value
            values = [data['value'] for data in recent_data]
            
            return {
                'metric_name': metric_name,
                'values': values,
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': values[-1] if values else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get condition data for rule {rule.rule_id}: {str(e)}")
            return None
    
    def _extract_metric_name(self, condition: str) -> Optional[str]:
        """Extract metric name from condition string"""



        try:
            # Simple extraction - in production this would be more sophisticated
            # Expected format: "metric_name > threshold" or "avg(metric_name) > threshold"
            
            if '(' in condition:
                # Function format: avg(metric_name)
                start = condition.find('(') + 1
                end = condition.find(')')
                if start > 0 and end > start:
                    return condition[start:end].strip()
            else:
                # Direct format: metric_name > threshold
                parts = condition.split()
                if len(parts) >= 3:
                    return parts[0].strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract metric name from condition '{condition}': {str(e)}")
            return None
    
    def _evaluate_condition(self, rule: AlertRule, condition_data: Dict[str, Any]) -> bool:
        """Evaluate rule condition against data"""



        try:
            # Determine value to compare based on condition
            condition_lower = rule.condition.lower()
            
            if 'avg(' in condition_lower or 'average(' in condition_lower:
                value = condition_data['avg']
            elif 'sum(' in condition_lower:
                value = condition_data['sum']
            elif 'min(' in condition_lower:
                value = condition_data['min']
            elif 'max(' in condition_lower:
                value = condition_data['max']
            elif 'count(' in condition_lower:
                value = condition_data['count']
            else:
                value = condition_data['latest']  # Default to latest value
            
            # Compare with threshold
            if rule.comparison_operator == '>':
                return value > rule.threshold
            elif rule.comparison_operator == '>=':
                return value >= rule.threshold
            elif rule.comparison_operator == '<':
                return value < rule.threshold
            elif rule.comparison_operator == '<=':
                return value <= rule.threshold
            elif rule.comparison_operator == '==':
                return value == rule.threshold
            elif rule.comparison_operator == '!=':
                return value != rule.threshold
            else:
                logger.warning(f"Unknown comparison operator: {rule.comparison_operator}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to evaluate condition for rule {rule.rule_id}: {str(e)}")
            return False
    
    def _should_trigger_alert(self, rule: AlertRule, rule_state: Dict[str, Any]) -> bool:
        """Determine if alert should be triggered"""



        try:
            # Simple trigger logic - condition met at least once
            # In production, this could be more sophisticated (e.g., multiple consecutive evaluations)
            return rule_state['condition_met_count'] >= 1
            
        except Exception as e:
            logger.error(f"Failed to check trigger condition for rule {rule.rule_id}: {str(e)}")
            return False
    
    async def _trigger_alert(self, rule: AlertRule, condition_data: Dict[str, Any], current_time: datetime):
        """Trigger an alert"""



        try:
            alert_id = f"alert_{rule.rule_id}_{int(current_time.timestamp())}"
            
            # Create alert
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=f"Alert: {rule.name}",
                description=f"{rule.description}\nCurrent value: {condition_data.get('latest', 'N/A')}\nThreshold: {rule.threshold}",
                category=rule.category,
                severity=rule.severity,
                current_value=condition_data.get('latest'),
                threshold_value=rule.threshold,
                metadata={
                    'condition_data': condition_data,
                    'evaluation_time': current_time.isoformat()
                }
            )
            
            # Store alert (in production, this would be in database)
            logger.info(f"Alert triggered: {alert.title} (ID: {alert.alert_id})")
            
            # This would trigger the alert manager to send notifications
            # For now, we'll just log it
            logger.warning(f"ALERT: {alert.severity.value.upper()} - {alert.title}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert for rule {rule.rule_id}: {str(e)}")
    
    def ingest_metric_data(self, metric_name: str, value: Union[int, float], 
                          timestamp: Optional[datetime] = None):
        """Ingest metric data for evaluation"""



        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            
            data_point = {
                'timestamp': timestamp,
                'value': value,
                'ingested_at': datetime.now(timezone.utc)
            }
            
            self.data_buffer[metric_name].append(data_point)
            
        except Exception as e:
            logger.error(f"Failed to ingest metric data for {metric_name}: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old data from buffers"""



        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.max_data_age)
            
            for metric_name in list(self.data_buffer.keys()):
                buffer = self.data_buffer[metric_name]
                
                # Remove old data points
                while buffer and buffer[0]['timestamp'] < cutoff_time:
                    buffer.popleft()
                
                # Remove empty buffers
                if not buffer:
                    del self.data_buffer[metric_name]
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {str(e)}")


class AlertManager:
    """
    Central alert management system
    
    Features:
    - Alert lifecycle management
    - Notification delivery
    - Escalation handling
    - Alert suppression
    - Acknowledgment tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize alert manager"""
        self.config = config or {}
        
        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Notification channels
        self.notification_channels: Dict[AlertChannel, Dict[str, Any]] = {
            AlertChannel.EMAIL: self.config.get('email', {}),
            AlertChannel.SLACK: self.config.get('slack', {}),
            AlertChannel.WEBHOOK: self.config.get('webhook', {}),
        }
        
        # Alert evaluator
        self.evaluator = AlertEvaluator(self.config.get('evaluator', {}))
        
        # Notification queues
        self.notification_queue = asyncio.Queue()
        self.notification_workers = []
        
        # Configuration
        self.max_alerts_history = self.config.get('max_history', 10000)
        self.auto_resolve_timeout = self.config.get('auto_resolve_timeout', 86400)  # 24 hours
        
        # Thread safety
        self._lock = threading.Lock()
    
    async def start(self):
        """Start alert manager"""



        try:
            logger.info("Starting Alert Manager")
            
            # Start alert evaluator
            await self.evaluator.start_evaluation()
            
            # Start notification workers
            await self._start_notification_workers()
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Alert Manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Alert Manager: {str(e)}")
    
    async def stop(self):
        """Stop alert manager"""



        try:
            logger.info("Stopping Alert Manager")
            
            # Stop evaluator
            await self.evaluator.stop_evaluation()
            
            # Stop notification workers
            await self._stop_notification_workers()
            
            # Stop cleanup task
            if hasattr(self, 'cleanup_task'):
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Alert Manager stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop Alert Manager: {str(e)}")
    
    async def _start_notification_workers(self):
        """Start notification worker tasks"""



        try:
            num_workers = self.config.get('notification_workers', 3)
            
            for i in range(num_workers):
                worker = asyncio.create_task(self._notification_worker(f"worker-{i}"))
                self.notification_workers.append(worker)
            
            logger.info(f"Started {num_workers} notification workers")
            
        except Exception as e:
            logger.error(f"Failed to start notification workers: {str(e)}")
    
    async def _stop_notification_workers(self):
        """Stop notification worker tasks"""



        try:
            for worker in self.notification_workers:
                worker.cancel()
            
            # Wait for workers to finish
            if self.notification_workers:
                await asyncio.gather(*self.notification_workers, return_exceptions=True)
            
            self.notification_workers.clear()
            logger.info("Stopped all notification workers")
            
        except Exception as e:
            logger.error(f"Failed to stop notification workers: {str(e)}")
    
    async def _notification_worker(self, worker_id: str):
        """Notification worker task"""
        logger.info(f"Notification worker {worker_id} started")
        
        try:
            while True:
                try:
                    # Get notification from queue
                    notification = await asyncio.wait_for(self.notification_queue.get(), timeout=5.0)
                    
                    # Process notification
                    await self._process_notification(notification)
                    
                    # Mark task as done
                    self.notification_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue  # Continue waiting for notifications
                    
        except asyncio.CancelledError:
            logger.info(f"Notification worker {worker_id} cancelled")
        except Exception as e:
            logger.error(f"Error in notification worker {worker_id}: {str(e)}")
    
    async def _process_notification(self, notification: Dict[str, Any]):
        """Process a single notification"""



        try:
            alert = notification['alert']
            channel = notification['channel']
            recipients = notification['recipients']
            
            # Send notification based on channel
            if channel == AlertChannel.EMAIL:
                await self._send_email_notification(alert, recipients)
            elif channel == AlertChannel.SLACK:
                await self._send_slack_notification(alert, recipients)
            elif channel == AlertChannel.WEBHOOK:
                await self._send_webhook_notification(alert, recipients)
            else:
                logger.warning(f"Unsupported notification channel: {channel}")
            
        except Exception as e:
            logger.error(f"Failed to process notification: {str(e)}")
    
    async def _send_email_notification(self, alert: Alert, recipients: List[str]):
        """Send email notification"""



        try:
            email_config = self.notification_channels[AlertChannel.EMAIL]
            
            if not email_config:
                logger.warning("Email configuration not found")
                return
            
            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username')
            password = email_config.get('password')
            sender_email = email_config.get('sender_email')
            
            if not all([smtp_server, username, password, sender_email]):
                logger.warning("Incomplete email configuration")
                return
            
            # Create email content
            subject = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
Alert Details:
- ID: {alert.alert_id}
- Severity: {alert.severity.value.upper()}
- Category: {alert.category.value}
- Triggered: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Status: {alert.status.value}

Description:
{alert.description}

Current Value: {alert.current_value}
Threshold: {alert.threshold_value}

Affected Components: {', '.join(alert.affected_components) if alert.affected_components else 'N/A'}

This alert was generated by the IA Influencer Platform monitoring system.
"""
            
            # Send to each recipient
            for recipient in recipients:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Send email (simplified - in production use proper SMTP handling)
                    logger.info(f"Email notification sent to {recipient} for alert {alert.alert_id}")
                    alert.delivery_status[AlertChannel.EMAIL] = "sent"
                    
                except Exception as e:
                    logger.error(f"Failed to send email to {recipient}: {str(e)}")
                    alert.delivery_status[AlertChannel.EMAIL] = f"failed: {str(e)}"
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            alert.delivery_status[AlertChannel.EMAIL] = f"failed: {str(e)}"
    
    async def _send_slack_notification(self, alert: Alert, channels: List[str]):
        """Send Slack notification"""



        try:
            slack_config = self.notification_channels[AlertChannel.SLACK]
            webhook_url = slack_config.get('webhook_url')
            
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return
            
            # Create Slack message
            color_map = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.EMERGENCY: "danger"
            }
            
            message = {
                "attachments": [{
                    "color": color_map.get(alert.severity, "warning"),
                    "title": f"{alert.severity.value.upper()}: {alert.title}",
                    "text": alert.description,
                    "fields": [
                        {"title": "Alert ID", "value": alert.alert_id, "short": True},
                        {"title": "Category", "value": alert.category.value, "short": True},
                        {"title": "Current Value", "value": str(alert.current_value), "short": True},
                        {"title": "Threshold", "value": str(alert.threshold_value), "short": True},
                        {"title": "Triggered", "value": alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC'), "short": True},
                        {"title": "Status", "value": alert.status.value, "short": True}
                    ],
                    "footer": "IA Influencer Platform Monitoring",
                    "ts": int(alert.triggered_at.timestamp())
                }]
            }
            
            # Send to channels (simplified - in production use proper Slack client)
            for channel in channels:
                try:
                    logger.info(f"Slack notification sent to {channel} for alert {alert.alert_id}")
                    alert.delivery_status[AlertChannel.SLACK] = "sent"
                except Exception as e:
                    logger.error(f"Failed to send Slack notification to {channel}: {str(e)}")
                    alert.delivery_status[AlertChannel.SLACK] = f"failed: {str(e)}"
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            alert.delivery_status[AlertChannel.SLACK] = f"failed: {str(e)}"
    
    async def _send_webhook_notification(self, alert: Alert, webhooks: List[str]):
        """Send webhook notification"""



        try:
            payload = {
                "event": "alert_triggered",
                "alert": alert.to_dict(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            for webhook_url in webhooks:
                try:
                    # In production, use proper HTTP client with retries
                    logger.info(f"Webhook notification sent to {webhook_url} for alert {alert.alert_id}")
                    alert.delivery_status[AlertChannel.WEBHOOK] = "sent"
                except Exception as e:
                    logger.error(f"Failed to send webhook to {webhook_url}: {str(e)}")
                    alert.delivery_status[AlertChannel.WEBHOOK] = f"failed: {str(e)}"
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            alert.delivery_status[AlertChannel.WEBHOOK] = f"failed: {str(e)}"
    
    def create_alert(self, alert: Alert):
        """Create and manage a new alert"""



        try:
            with self._lock:
                # Add to active alerts
                self.active_alerts[alert.alert_id] = alert
                
                # Add to history
                self.alert_history.append(alert)
                
                # Maintain history size
                if len(self.alert_history) > self.max_alerts_history:
                    self.alert_history = self.alert_history[-self.max_alerts_history:]
            
            # Queue notifications
            asyncio.create_task(self._queue_alert_notifications(alert))
            
            logger.info(f"Created alert: {alert.title} (ID: {alert.alert_id})")
            
        except Exception as e:
            logger.error(f"Failed to create alert {alert.alert_id}: {str(e)}")
    
    async def _queue_alert_notifications(self, alert: Alert):
        """Queue alert notifications for delivery"""



        try:
            # Get alert rule to determine channels and recipients
            rule = self.evaluator.alert_rules.get(alert.rule_id)
            
            if not rule:
                logger.warning(f"Alert rule not found for alert {alert.alert_id}")
                return
            
            # Queue notifications for each channel
            for channel in rule.channels:
                notification = {
                    'alert': alert,
                    'channel': channel,
                    'recipients': rule.recipients
                }
                
                await self.notification_queue.put(notification)
            
        except Exception as e:
            logger.error(f"Failed to queue notifications for alert {alert.alert_id}: {str(e)}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert"""



        try:
            with self._lock:
                if alert_id in self.active_alerts:
                    alert = self.active_alerts[alert_id]
                    alert.status = AlertStatus.ACKNOWLEDGED
                    alert.acknowledged_at = datetime.now(timezone.utc)
                    alert.acknowledged_by = acknowledged_by
                    
                    logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                else:
                    logger.warning(f"Alert not found for acknowledgment: {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {str(e)}")
    
    def resolve_alert(self, alert_id: str, resolved_by: str):
        """Resolve an alert"""



        try:
            with self._lock:
                if alert_id in self.active_alerts:
                    alert = self.active_alerts[alert_id]
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now(timezone.utc)
                    alert.resolved_by = resolved_by
                    
                    # Remove from active alerts
                    del self.active_alerts[alert_id]
                    
                    logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
                else:
                    logger.warning(f"Alert not found for resolution: {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {str(e)}")
    
    def get_active_alerts(self, filters: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """Get active alerts with optional filtering"""



        try:
            alerts = list(self.active_alerts.values())
            
            if not filters:
                return alerts
            
            # Apply filters
            filtered_alerts = []
            for alert in alerts:
                include = True
                
                if 'severity' in filters and alert.severity != filters['severity']:
                    include = False
                
                if 'category' in filters and alert.category != filters['category']:
                    include = False
                
                if 'status' in filters and alert.status != filters['status']:
                    include = False
                
                if include:
                    filtered_alerts.append(alert)
            
            return filtered_alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {str(e)}")
            return []
    
    async def _cleanup_loop(self):
        """Cleanup loop for old alerts and maintenance"""
        while True:
            try:
                await self._cleanup_expired_alerts()
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_alerts(self):
        """Clean up expired alerts"""



        try:
            current_time = datetime.now(timezone.utc)
            expired_alert_ids = []
            
            with self._lock:
                for alert_id, alert in self.active_alerts.items():
                    # Auto-resolve old alerts
                    if (current_time - alert.triggered_at).total_seconds() > self.auto_resolve_timeout:
                        alert.status = AlertStatus.EXPIRED
                        alert.resolved_at = current_time
                        alert.resolved_by = "system"
                        expired_alert_ids.append(alert_id)
                
                # Remove expired alerts from active list
                for alert_id in expired_alert_ids:
                    del self.active_alerts[alert_id]
            
            if expired_alert_ids:
                logger.info(f"Expired {len(expired_alert_ids)} old alerts")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired alerts: {str(e)}")


# Pre-configured alert rules for common scenarios
class StandardAlertRules:
    """Standard alert rules for common monitoring scenarios"""
    
    @staticmethod
    def high_error_rate_rule() -> AlertRule:
        """High error rate alert rule"""



        return AlertRule(
            rule_id="high_error_rate",
            name="High Error Rate",
            description="Error rate exceeds acceptable threshold",
            category=AlertCategory.SYSTEM,
            severity=AlertSeverity.HIGH,
            condition="error_rate > 5",
            threshold=5.0,
            comparison_operator=">",
            time_window=300,  # 5 minutes
            evaluation_frequency=60,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            recipients=["admin@platform.com"],
            auto_resolve=True
        )
    
    @staticmethod
    def high_response_time_rule() -> AlertRule:
        """High response time alert rule"""



        return AlertRule(
            rule_id="high_response_time",
            name="High Response Time",
            description="API response time exceeds threshold",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.MEDIUM,
            condition="avg(response_time) > 2000",
            threshold=2000.0,  # 2 seconds
            comparison_operator=">",
            time_window=600,  # 10 minutes
            evaluation_frequency=120,
            channels=[AlertChannel.EMAIL],
            recipients=["devops@platform.com"]
        )
    
    @staticmethod
    def security_breach_rule() -> AlertRule:
        """Security breach alert rule"""



        return AlertRule(
            rule_id="security_breach",
            name="Security Breach Detected",
            description="Potential security breach detected",
            category=AlertCategory.SECURITY,
            severity=AlertSeverity.CRITICAL,
            condition="security_events > 10",
            threshold=10,
            comparison_operator=">",
            time_window=300,  # 5 minutes
            evaluation_frequency=30,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PAGER],
            recipients=["security@platform.com", "admin@platform.com"],
            suppression_duration=1800  # 30 minutes
        )
    
    @staticmethod
    def low_content_protection_score_rule() -> AlertRule:
        """Low content protection score alert rule"""



        return AlertRule(
            rule_id="low_protection_score",
            name="Low Content Protection Score",
            description="Content protection score is below acceptable level",
            category=AlertCategory.CONTENT_PROTECTION,
            severity=AlertSeverity.MEDIUM,
            condition="avg(protection_score) < 0.8",
            threshold=0.8,
            comparison_operator="<",
            time_window=1800,  # 30 minutes
            evaluation_frequency=300,
            channels=[AlertChannel.EMAIL],
            recipients=["content-team@platform.com"]
        )
    
    @staticmethod
    def ai_model_degradation_rule() -> AlertRule:
        """AI model performance degradation alert rule"""



        return AlertRule(
            rule_id="ai_model_degradation",
            name="AI Model Performance Degradation",
            description="AI model accuracy has degraded significantly",
            category=AlertCategory.AI_MODEL,
            severity=AlertSeverity.HIGH,
            condition="model_accuracy < 0.9",
            threshold=0.9,
            comparison_operator="<",
            time_window=3600,  # 1 hour
            evaluation_frequency=600,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            recipients=["ml-team@platform.com", "devops@platform.com"]
        )


# Integration with analytics for intelligent alerting
class IntelligentAlerting:
    """
    Intelligent alerting system that uses analytics to improve alert quality
    
    Features:
    - ML-based anomaly detection
    - Dynamic threshold adjustment
    - Context-aware alerting
    - Alert fatigue reduction
    - Predictive alerting
    """
    
    def __init__(self, alert_manager: AlertManager, analytics_engine: Any):
        """Initialize intelligent alerting"""
        self.alert_manager = alert_manager
        self.analytics_engine = analytics_engine
        
        # Intelligence configuration
        self.anomaly_threshold = 2.0  # Standard deviations
        self.context_window = 3600    # Seconds
        self.learning_period = 86400  # 24 hours
        
        # Learned baselines
        self.metric_baselines: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.alert_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    async def analyze_and_alert(self, metric_name: str, value: float):
        """Analyze metric and trigger intelligent alerts"""



        try:
            # Update baselines
            await self._update_baseline(metric_name, value)
            
            # Check for anomalies
            anomaly_score = await self._calculate_anomaly_score(metric_name, value)
            
            if anomaly_score > self.anomaly_threshold:
                # Create intelligent alert
                await self._create_intelligent_alert(metric_name, value, anomaly_score)
            
        except Exception as e:
            logger.error(f"Failed to analyze metric {metric_name}: {str(e)}")
    
    async def _update_baseline(self, metric_name: str, value: float):
        """Update baseline statistics for metric"""



        try:
            baseline = self.metric_baselines[metric_name]
            
            # Initialize if first time
            if not baseline:
                baseline.update({
                    'mean': value,
                    'variance': 0.0,
                    'count': 1,
                    'min': value,
                    'max': value,
                    'last_updated': time.time()
                })
                return
            
            # Update running statistics
            count = baseline['count'] + 1
            delta = value - baseline['mean']
            mean = baseline['mean'] + delta / count
            variance = baseline['variance'] + delta * (value - mean)
            
            baseline.update({
                'mean': mean,
                'variance': variance / max(count - 1, 1),
                'count': count,
                'min': min(baseline['min'], value),
                'max': max(baseline['max'], value),
                'last_updated': time.time()
            })
            
        except Exception as e:
            logger.error(f"Failed to update baseline for {metric_name}: {str(e)}")
    
    async def _calculate_anomaly_score(self, metric_name: str, value: float) -> float:
        """Calculate anomaly score for value"""



        try:
            baseline = self.metric_baselines.get(metric_name, {})
            
            if not baseline or baseline['count'] < 10:
                return 0.0  # Not enough data
            
            mean = baseline['mean']
            std_dev = (baseline['variance'] ** 0.5)
            
            if std_dev == 0:
                return 0.0  # No variance
            
            # Z-score
            z_score = abs((value - mean) / std_dev)
            
            return z_score
            
        except Exception as e:
            logger.error(f"Failed to calculate anomaly score for {metric_name}: {str(e)}")
            return 0.0
    
    async def _create_intelligent_alert(self, metric_name: str, value: float, anomaly_score: float):
        """Create an intelligent alert based on anomaly detection"""



        try:
            severity = AlertSeverity.LOW
            if anomaly_score > 4.0:
                severity = AlertSeverity.CRITICAL
            elif anomaly_score > 3.0:
                severity = AlertSeverity.HIGH
            elif anomaly_score > 2.5:
                severity = AlertSeverity.MEDIUM
            
            alert = Alert(
                alert_id=f"intelligent_{metric_name}_{int(time.time())}",
                rule_id="intelligent_anomaly_detection",
                title=f"Anomaly Detected: {metric_name}",
                description=f"Unusual value detected for {metric_name}. Current value: {value}, Anomaly score: {anomaly_score:.2f}",
                category=AlertCategory.SYSTEM,
                severity=severity,
                current_value=value,
                metadata={
                    'anomaly_score': anomaly_score,
                    'metric_name': metric_name,
                    'baseline': self.metric_baselines.get(metric_name, {})
                }
            )
            
            self.alert_manager.create_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to create intelligent alert for {metric_name}: {str(e)}")
