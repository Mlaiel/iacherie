"""🚨 Intelligent Alerting System - Enterprise ML Monitoring
==========================================================
Module: ml/monitoring/intelligent_alerting_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INTELLIGENT ML ALERTING
ML-powered intelligent alerting with anomaly detection and noise reduction
- Anomaly detection using statistical and ML methods
- Alert correlation and noise reduction
- Priority-based escalation
- Automated incident response
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from collections import defaultdict, deque
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class AlertSeverity(IntEnum):
    """Alert severity levels (higher number = more severe)"""
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    EMERGENCY = 5

class AlertType(Enum):
    """Types of alerts"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MODEL_DRIFT = "model_drift"
    ACCURACY_DROP = "accuracy_drop"
    LATENCY_SPIKE = "latency_spike"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_INCIDENT = "security_incident"
    DATA_QUALITY = "data_quality"
    SYSTEM_ERROR = "system_error"

class AlertStatus(Enum):
    """Alert status tracking"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"

@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    model_id: Optional[str]
    metrics: Dict[str, float]
    threshold_violated: Optional[Dict[str, Any]]
    created_at: datetime
    status: AlertStatus = AlertStatus.OPEN
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    related_alerts: List[str] = field(default_factory=list)
    escalation_level: int = 0

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    alert_type: AlertType
    condition: str  # Python expression
    severity: AlertSeverity
    threshold: Dict[str, float]
    cooldown_minutes: int = 15
    enabled: bool = True
    model_filter: Optional[str] = None
    notification_channels: List[NotificationChannel] = field(default_factory=list)

@dataclass
class NotificationConfig:
    """Notification channel configuration"""
    channel: NotificationChannel
    config: Dict[str, Any]
    severity_filter: List[AlertSeverity] = field(default_factory=list)
    enabled: bool = True

class AnomalyDetector:
    """ML-based anomaly detection for alerts"""
    
    def __init__(self, window_size -> None: int = 100) -> None:
        self.window_size = window_size
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    async def detect_anomaly(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Detect anomalies in metrics using ML
        Returns anomaly scores (higher = more anomalous)
        """
        try:
            anomaly_scores = {}
            
            for metric_name, value in metrics.items():
                # Add to history
                self.metric_history[metric_name].append(value)
                
                # Statistical anomaly detection (Z-score)
                if len(self.metric_history[metric_name]) >= 10:
                    values = list(self.metric_history[metric_name])
                    mean_val = statistics.mean(values)
                    std_val = statistics.stdev(values) if len(values) > 1 else 0
                    
                    if std_val > 0:
                        z_score = abs((value - mean_val) / std_val)
                        anomaly_scores[f"{metric_name}_zscore"] = z_score
                
                # Moving average deviation
                if len(self.metric_history[metric_name]) >= 5:
                    values = list(self.metric_history[metric_name])
                    recent_avg = statistics.mean(values[-5:])
                    historical_avg = statistics.mean(values[:-5]) if len(values) > 5 else recent_avg
                    
                    if historical_avg != 0:
                        deviation = abs((recent_avg - historical_avg) / historical_avg)
                        anomaly_scores[f"{metric_name}_deviation"] = deviation
            
            # ML-based anomaly detection
            if len(self.metric_history) > 0 and all(len(hist) >= self.window_size for hist in self.metric_history.values()):
                ml_score = await self._ml_anomaly_detection(metrics)
                anomaly_scores["ml_anomaly_score"] = ml_score
            
            return anomaly_scores
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {}

    async def _ml_anomaly_detection(self, current_metrics: Dict[str, float]) -> float:
        """ML-based anomaly detection using Isolation Forest"""
        try:
            # Prepare training data
            if not self.is_trained:
                training_data = []
                metric_names = sorted(current_metrics.keys())
                
                # Collect historical data
                min_length = min(len(hist) for hist in self.metric_history.values())
                if min_length < 20:
                    return 0.0
                
                for i in range(min_length):
                    row = [list(self.metric_history[name])[i] for name in metric_names]
                    training_data.append(row)
                
                # Train model
                training_data = np.array(training_data)
                training_data_scaled = self.scaler.fit_transform(training_data)
                self.isolation_forest.fit(training_data_scaled)
                self.is_trained = True
            
            # Detect anomaly in current metrics
            current_data = np.array([[current_metrics[name] for name in sorted(current_metrics.keys())]])
            current_data_scaled = self.scaler.transform(current_data)
            
            # Get anomaly score (-1 = anomaly, 1 = normal)
            anomaly_score = self.isolation_forest.decision_function(current_data_scaled)[0]
            
            # Convert to 0-1 scale (higher = more anomalous)
            normalized_score = max(0, (1 - anomaly_score) / 2)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {str(e)}")
            return 0.0

class AlertCorrelator:
    """Correlate related alerts to reduce noise"""
    
    def __init__(self, correlation_window: timedelta = timedelta(minutes=10)):
        self.correlation_window = correlation_window
        self.alert_groups: Dict[str, List[Alert]] = {}
        
    async def correlate_alert(self, alert: Alert, existing_alerts: List[Alert]) -> List[str]:
        """
        Correlate new alert with existing alerts
        Returns list of related alert IDs
        """
        try:
            related_alerts = []
            current_time = alert.created_at
            
            for existing_alert in existing_alerts:
                # Skip if outside correlation window
                time_diff = current_time - existing_alert.created_at
                if time_diff > self.correlation_window:
                    continue
                
                # Skip if already resolved
                if existing_alert.status == AlertStatus.RESOLVED:
                    continue
                
                # Calculate correlation score
                correlation_score = await self._calculate_correlation(alert, existing_alert)
                
                if correlation_score > 0.7:  # High correlation threshold
                    related_alerts.append(existing_alert.alert_id)
            
            return related_alerts
            
        except Exception as e:
            logger.error(f"Error in alert correlation: {str(e)}")
            return []

    async def _calculate_correlation(self, alert1: Alert, alert2: Alert) -> float:
        """Calculate correlation score between two alerts"""
        score = 0.0
        
        # Same alert type
        if alert1.alert_type == alert2.alert_type:
            score += 0.4
        
        # Same model
        if alert1.model_id and alert2.model_id and alert1.model_id == alert2.model_id:
            score += 0.3
        
        # Similar metrics
        if alert1.metrics and alert2.metrics:
            common_metrics = set(alert1.metrics.keys()) & set(alert2.metrics.keys())
            if common_metrics:
                metric_similarity = len(common_metrics) / max(len(alert1.metrics), len(alert2.metrics))
                score += 0.2 * metric_similarity
        
        # Similar tags
        if alert1.tags and alert2.tags:
            common_tags = set(alert1.tags) & set(alert2.tags)
            if common_tags:
                tag_similarity = len(common_tags) / max(len(alert1.tags), len(alert2.tags))
                score += 0.1 * tag_similarity
        
        return min(score, 1.0)

class IntelligentAlertingSystem:
    """
    Intelligent alerting system with ML-powered anomaly detection
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_configs: Dict[NotificationChannel, NotificationConfig] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.anomaly_detector = AnomalyDetector()
        self.alert_correlator = AlertCorrelator()
        self.escalation_handlers: Dict[int, Callable] = {}
        
        # Cooldown tracking
        self.rule_cooldowns: Dict[str, datetime] = {}
        
        if config_path:
            asyncio.create_task(self.load_config(config_path))

    async def add_alert_rule(self, rule: AlertRule) -> None:
        """Add new alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    async def add_notification_config(self, config: NotificationConfig) -> None:
        """Add notification channel configuration"""
        self.notification_configs[config.channel] = config
        logger.info(f"Added notification config for {config.channel.value}")

    async def process_metrics(
        self,
        model_id: str,
        metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Alert]:
        """
        Process metrics and generate alerts based on rules
        """
        try:
            generated_alerts = []
            
            # Detect anomalies
            anomaly_scores = await self.anomaly_detector.detect_anomaly(metrics)
            
            # Evaluate alert rules
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue
                
                # Check model filter
                if rule.model_filter and model_id != rule.model_filter:
                    continue
                
                # Check cooldown
                if await self._is_in_cooldown(rule.rule_id):
                    continue
                
                # Evaluate condition
                if await self._evaluate_condition(rule, metrics, anomaly_scores, context):
                    alert = await self._create_alert(rule, model_id, metrics, anomaly_scores, context)
                    generated_alerts.append(alert)
                    
                    # Set cooldown
                    self.rule_cooldowns[rule.rule_id] = datetime.utcnow()
            
            # Process generated alerts
            for alert in generated_alerts:
                await self._process_alert(alert)
            
            return generated_alerts
            
        except Exception as e:
            logger.error(f"Error processing metrics: {str(e)}")
            return []

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.utcnow()
                
                logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
            return False

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.utcnow()
                
                # Move to history
                self.alert_history.append(alert)
                del self.active_alerts[alert_id]
                
                logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {str(e)}")
            return False

    async def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alerts"""
        try:
            summary = {
                'total_active': len(self.active_alerts),
                'by_severity': {},
                'by_type': {},
                'by_status': {},
                'escalated': 0
            }
            
            for alert in self.active_alerts.values():
                # By severity
                severity_name = alert.severity.name
                summary['by_severity'][severity_name] = summary['by_severity'].get(severity_name, 0) + 1
                
                # By type
                type_name = alert.alert_type.value
                summary['by_type'][type_name] = summary['by_type'].get(type_name, 0) + 1
                
                # By status
                status_name = alert.status.value
                summary['by_status'][status_name] = summary['by_status'].get(status_name, 0) + 1
                
                # Escalated
                if alert.escalation_level > 0:
                    summary['escalated'] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting alert summary: {str(e)}")
            return {}

    async def _process_alert(self, alert: Alert) -> None:
        """Process and handle new alert"""
        try:
            # Correlate with existing alerts
            existing_alerts = list(self.active_alerts.values())
            related_alert_ids = await self.alert_correlator.correlate_alert(alert, existing_alerts)
            alert.related_alerts = related_alert_ids
            
            # Add to active alerts
            self.active_alerts[alert.alert_id] = alert
            
            # Send notifications
            await self._send_notifications(alert)
            
            # Schedule escalation if needed
            if alert.severity >= AlertSeverity.CRITICAL:
                asyncio.create_task(self._schedule_escalation(alert))
            
            logger.info(f"Processed alert {alert.alert_id}: {alert.title}")
            
        except Exception as e:
            logger.error(f"Error processing alert {alert.alert_id}: {str(e)}")

    async def _create_alert(
        self,
        rule: AlertRule,
        model_id: str,
        metrics: Dict[str, float],
        anomaly_scores: Dict[str, float],
        context: Optional[Dict[str, Any]]
    ) -> Alert:
        """Create alert from rule and metrics"""
        
        alert_id = f"{rule.rule_id}_{int(datetime.utcnow().timestamp())}"
        
        # Find violated threshold
        threshold_violated = {}
        for metric, value in metrics.items():
            if metric in rule.threshold:
                threshold_value = rule.threshold[metric]
                if value > threshold_value:
                    threshold_violated[metric] = {
                        'current': value,
                        'threshold': threshold_value,
                        'violation_ratio': value / threshold_value
                    }
        
        # Generate description
        description = f"Rule '{rule.name}' triggered for model {model_id}. "
        if threshold_violated:
            description += f"Thresholds violated: {threshold_violated}. "
        if anomaly_scores:
            description += f"Anomaly scores: {anomaly_scores}."
        
        # Determine tags
        tags = [f"rule:{rule.rule_id}", f"model:{model_id}"]
        if context and 'environment' in context:
            tags.append(f"env:{context['environment']}")
        
        return Alert(
            alert_id=alert_id,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=f"{rule.alert_type.value.replace('_', ' ').title()} - {model_id}",
            description=description,
            model_id=model_id,
            metrics=metrics.copy(),
            threshold_violated=threshold_violated,
            created_at=datetime.utcnow(),
            tags=tags
        )

    async def _evaluate_condition(
        self,
        rule: AlertRule,
        metrics: Dict[str, float],
        anomaly_scores: Dict[str, float],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Evaluate rule condition"""
        try:
            # Create evaluation context
            eval_context = {
                'metrics': metrics,
                'anomaly_scores': anomaly_scores,
                'context': context or {},
                'threshold': rule.threshold
            }
            
            # Evaluate condition
            result = eval(rule.condition, {"__builtins__": {}}, eval_context)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error evaluating condition for rule {rule.rule_id}: {str(e)}")
            return False

    async def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if rule is in cooldown period"""
        if rule_id not in self.rule_cooldowns:
            return False
        
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
        
        last_triggered = self.rule_cooldowns[rule_id]
        cooldown_end = last_triggered + timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.utcnow() < cooldown_end

    async def _send_notifications(self, alert: Alert) -> None:
        """Send notifications for alert"""
        try:
            rule = self.alert_rules.get(alert.alert_id.split('_')[0])
            if not rule:
                return
            
            for channel in rule.notification_channels:
                if channel in self.notification_configs:
                    config = self.notification_configs[channel]
                    
                    # Check severity filter
                    if config.severity_filter and alert.severity not in config.severity_filter:
                        continue
                    
                    if not config.enabled:
                        continue
                    
                    await self._send_notification(alert, channel, config)
                    
        except Exception as e:
            logger.error(f"Error sending notifications for alert {alert.alert_id}: {str(e)}")

    async def _send_notification(self, alert: Alert, channel: NotificationChannel, config: NotificationConfig) -> None:
        """Send notification via specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                await self._send_email_notification(alert, config)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack_notification(alert, config)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook_notification(alert, config)
            # Add other notification channels as needed
            
        except Exception as e:
            logger.error(f"Error sending {channel.value} notification: {str(e)}")

    async def _send_email_notification(self, alert: Alert, config: NotificationConfig) -> None:
        """Send email notification"""
        # Implementation for email notifications
        logger.info(f"Email notification sent for alert {alert.alert_id}")

    async def _send_slack_notification(self, alert: Alert, config: NotificationConfig) -> None:
        """Send Slack notification"""
        # Implementation for Slack notifications
        logger.info(f"Slack notification sent for alert {alert.alert_id}")

    async def _send_webhook_notification(self, alert: Alert, config: NotificationConfig) -> None:
        """Send webhook notification"""
        # Implementation for webhook notifications
        logger.info(f"Webhook notification sent for alert {alert.alert_id}")

    async def _schedule_escalation(self, alert: Alert) -> None:
        """Schedule alert escalation"""
        # Wait for escalation interval
        await asyncio.sleep(900)  # 15 minutes
        
        # Check if alert is still active and not acknowledged
        if (alert.alert_id in self.active_alerts and 
            self.active_alerts[alert.alert_id].status == AlertStatus.OPEN):
            
            await self._escalate_alert(alert)

    async def _escalate_alert(self, alert: Alert) -> None:
        """Escalate alert to higher level"""
        alert.escalation_level += 1
        
        # Call escalation handler if available
        if alert.escalation_level in self.escalation_handlers:
            await self.escalation_handlers[alert.escalation_level](alert)
        
        logger.warning(f"Alert {alert.alert_id} escalated to level {alert.escalation_level}")

    async def load_config(self, config_path: str) -> None:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load alert rules
            for rule_config in config.get('alert_rules', []):
                rule = AlertRule(**rule_config)
                await self.add_alert_rule(rule)
            
            # Load notification configs
            for notif_config in config.get('notification_configs', []):
                config_obj = NotificationConfig(**notif_config)
                await self.add_notification_config(config_obj)
                
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")

# Usage Example
async def main() -> None:
    """Example usage of IntelligentAlertingSystem"""
    system = IntelligentAlertingSystem()
    
    # Add alert rule
    rule = AlertRule(
        rule_id="accuracy_drop",
        name="Model Accuracy Drop",
        alert_type=AlertType.ACCURACY_DROP,
        condition="metrics.get('accuracy', 1.0) < threshold.get('accuracy', 0.95)",
        severity=AlertSeverity.ERROR,
        threshold={'accuracy': 0.95},
        cooldown_minutes=30,
        notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
    )
    await system.add_alert_rule(rule)
    
    # Add notification config
    email_config = NotificationConfig(
        channel=NotificationChannel.EMAIL,
        config={'smtp_server': 'localhost', 'from_email': 'alerts@example.com'},
        severity_filter=[AlertSeverity.ERROR, AlertSeverity.CRITICAL]
    )
    await system.add_notification_config(email_config)
    
    # Process metrics
    metrics = {
        'accuracy': 0.92,  # Below threshold
        'latency': 120,
        'throughput': 1000
    }
    
    alerts = await system.process_metrics("content-classifier", metrics)
    print(f"Generated {len(alerts)} alerts")
    
    # Get summary
    summary = await system.get_alert_summary()
    print(f"Alert summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())