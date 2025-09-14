"""Alerting System - Advanced Performance Alert Management
========================================================

Advanced alerting system for Ainflue integrations providing intelligent
threshold monitoring, escalation management, and notification orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib

from .performance_monitor_core import (
    PerformanceAlert, PerformanceThreshold, AlertLevel, MetricType,
    IntegrationProfile
)

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    metric_name: str
    integration_name: Optional[str]
    threshold_value: float
    comparison: str  # 'greater', 'less', 'equal'
    alert_level: AlertLevel
    time_window: timedelta
    consecutive_breaches: int = 1
    enabled: bool = True
    
@dataclass 
class AlertNotification:
    """Alert notification configuration."""
    notification_id: str
    alert_levels: List[AlertLevel]
    channels: List[str]  # 'email', 'slack', 'webhook', 'sms'
    escalation_delay: timedelta = timedelta(minutes=15)
    max_escalations: int = 3
    enabled: bool = True

class AlertingSystem:
    """Advanced alerting and notification system."""
    
    def __init__(self, performance_monitor) -> None:
        self.performance_monitor = performance_monitor
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notifications: Dict[str, AlertNotification] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Alerting state
        self.alerting_enabled = True
        self.alert_task: Optional[asyncio.Task] = None
        
        # Alert suppression
        self.suppression_rules: Dict[str, datetime] = {}
        self.max_alerts_per_hour = 100
        self.alert_count_window = deque(maxlen=self.max_alerts_per_hour)
        
        logger.info("Alerting system initialized")

    async def _alert_loop(self) -> None:
        """Background alerting loop."""
        while self.alerting_enabled:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check thresholds and generate alerts
                await self._check_thresholds()
                
                # Process alert escalations
                await self._process_escalations()
                
                # Cleanup old alerts
                await self._cleanup_resolved_alerts()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alerting loop: {e}")
                await asyncio.sleep(60)  # Wait longer before retrying

    async def _check_thresholds(self) -> None:
        """Check all thresholds and generate alerts."""
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
                
            try:
                await self._check_rule_threshold(rule)
            except Exception as e:
                logger.error(f"Error checking threshold for rule {rule_id}: {e}")

    async def _check_rule_threshold(self, rule: AlertRule) -> None:
        """Check a specific alert rule threshold."""
        # Get recent metrics for the rule
        metrics = self.performance_monitor.metrics_collector.get_metrics(
            rule.metric_name, rule.integration_name
        )
        
        if not metrics:
            return
            
        # Filter metrics within time window
        cutoff_time = datetime.utcnow() - rule.time_window
        recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        if len(recent_metrics) < rule.consecutive_breaches:
            return
            
        # Check if threshold is breached for consecutive metrics
        breach_count = 0
        for metric in recent_metrics[-rule.consecutive_breaches:]:
            if self._is_threshold_breached(metric.value, rule.threshold_value, rule.comparison):
                breach_count += 1
            else:
                break  # Reset count if not consecutive
                
        if breach_count >= rule.consecutive_breaches:
            await self._trigger_alert(rule, recent_metrics[-1].value)

    def _is_threshold_breached(self, value: float, threshold: float, comparison: str) -> bool:
        """Check if a value breaches the threshold."""
        if comparison == 'greater':
            return value > threshold
        elif comparison == 'less':
            return value < threshold
        elif comparison == 'equal':
            return abs(value - threshold) < 0.001  # Allow for floating point precision
        else:
            return False

    async def _trigger_alert(self, rule: AlertRule, current_value: float) -> None:
        """Trigger an alert for a rule breach."""
        alert_key = f"{rule.integration_name}:{rule.metric_name}:{rule.alert_level.value}"
        
        # Check if alert is already active
        if alert_key in self.active_alerts and not self.active_alerts[alert_key].resolved:
            return
            
        # Check suppression rules
        if self._is_alert_suppressed(alert_key):
            return
            
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Alert rate limit exceeded, suppressing alert")
            return
            
        # Create alert
        alert_id = hashlib.md5(f"{alert_key}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            metric_name=rule.metric_name,
            integration_name=rule.integration_name,
            alert_level=rule.alert_level,
            threshold_value=rule.threshold_value,
            actual_value=current_value,
            message=self._generate_alert_message(rule, current_value),
            timestamp=datetime.utcnow()
        )
        
        # Store alert
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        # Update performance monitor
        self.performance_monitor.active_alerts[alert_key] = alert
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
                
        logger.warning(f"Alert triggered: {alert.message}")

    def _generate_alert_message(self, rule: AlertRule, current_value: float) -> str:
        """Generate a human-readable alert message."""
        integration_part = f" for {rule.integration_name}" if rule.integration_name else ""
        
        if rule.comparison == 'greater':
            comparison_text = "above"
        elif rule.comparison == 'less':
            comparison_text = "below"
        else:
            comparison_text = "equal to"
            
        return (f"{rule.alert_level.value.upper()}: {rule.metric_name}{integration_part} "
                f"is {comparison_text} threshold ({current_value:.2f} vs {rule.threshold_value:.2f})")

    def _is_alert_suppressed(self, alert_key: str) -> bool:
        """Check if an alert is suppressed."""
        if alert_key in self.suppression_rules:
            if datetime.utcnow() < self.suppression_rules[alert_key]:
                return True
            else:
                # Remove expired suppression
                del self.suppression_rules[alert_key]
        return False

    def _check_rate_limit(self) -> bool:
        """Check if alert rate limit is exceeded."""
        current_time = datetime.utcnow()
        
        # Clean old entries
        cutoff_time = current_time - timedelta(hours=1)
        while self.alert_count_window and self.alert_count_window[0] < cutoff_time:
            self.alert_count_window.popleft()
            
        # Check if under limit
        if len(self.alert_count_window) >= self.max_alerts_per_hour:
            return False
            
        # Add current alert
        self.alert_count_window.append(current_time)
        return True

    async def _send_alert_notifications(self, alert: PerformanceAlert) -> None:
        """Send alert notifications through configured channels."""
        for notification_id, notification in self.notifications.items():
            if not notification.enabled:
                continue
                
            if alert.alert_level in notification.alert_levels:
                await self._send_notification(alert, notification)

    async def _send_notification(self, alert: PerformanceAlert, notification: AlertNotification) -> None:
        """Send a notification through specified channels."""
        for channel in notification.channels:
            try:
                if channel == 'email':
                    await self._send_email_notification(alert, notification)
                elif channel == 'slack':
                    await self._send_slack_notification(alert, notification)
                elif channel == 'webhook':
                    await self._send_webhook_notification(alert, notification)
                elif channel == 'sms':
                    await self._send_sms_notification(alert, notification)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {e}")

    async def _send_email_notification(self, alert: PerformanceAlert, notification: AlertNotification) -> None:
        """Send email notification (placeholder implementation)."""
        logger.info(f"EMAIL NOTIFICATION: {alert.message}")
        # Implementation would integrate with email service

    async def _send_slack_notification(self, alert: PerformanceAlert, notification: AlertNotification) -> None:
        """Send Slack notification (placeholder implementation)."""
        logger.info(f"SLACK NOTIFICATION: {alert.message}")
        # Implementation would integrate with Slack API

    async def _send_webhook_notification(self, alert: PerformanceAlert, notification: AlertNotification) -> None:
        """Send webhook notification (placeholder implementation)."""
        logger.info(f"WEBHOOK NOTIFICATION: {alert.message}")
        # Implementation would send HTTP POST to webhook URL

    async def _send_sms_notification(self, alert: PerformanceAlert, notification: AlertNotification) -> None:
        """Send SMS notification (placeholder implementation)."""
        logger.info(f"SMS NOTIFICATION: {alert.message}")
        # Implementation would integrate with SMS service

    async def _process_escalations(self) -> None:
        """Process alert escalations."""
        for alert_key, alert in self.active_alerts.items():
            if alert.resolved:
                continue
                
            # Check if alert needs escalation
            time_since_alert = datetime.utcnow() - alert.timestamp
            
            # Find matching notification rules
            for notification in self.notifications.values():
                if alert.alert_level in notification.alert_levels:
                    if time_since_alert >= notification.escalation_delay:
                        await self._escalate_alert(alert, notification)

    async def _escalate_alert(self, alert: PerformanceAlert, notification: AlertNotification) -> None:
        """Escalate an alert."""
        escalation_key = f"{alert.alert_id}:{notification.notification_id}"
        
        # Track escalation count (simplified implementation)
        escalation_count = getattr(alert, 'escalation_count', 0)
        if escalation_count >= notification.max_escalations:
            return
            
        # Create escalated alert message
        escalated_message = f"ESCALATED: {alert.message} (unresolved for {datetime.utcnow() - alert.timestamp})"
        
        # Create escalated alert
        escalated_alert = PerformanceAlert(
            alert_id=f"{alert.alert_id}_esc_{escalation_count + 1}",
            metric_name=alert.metric_name,
            integration_name=alert.integration_name,
            alert_level=AlertLevel.CRITICAL,  # Escalate to critical
            threshold_value=alert.threshold_value,
            actual_value=alert.actual_value,
            message=escalated_message,
            timestamp=datetime.utcnow()
        )
        
        # Send escalated notification
        await self._send_notification(escalated_alert, notification)
        
        # Update escalation count
        setattr(alert, 'escalation_count', escalation_count + 1)
        
        logger.warning(f"Alert escalated: {escalated_message}")

    async def _cleanup_resolved_alerts(self) -> None:
        """Clean up old resolved alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Remove old resolved alerts from active alerts
        resolved_keys = []
        for alert_key, alert in self.active_alerts.items():
            if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                resolved_keys.append(alert_key)
                
        for key in resolved_keys:
            del self.active_alerts[key]
            
        # Limit alert history size
        if len(self.alert_history) > 10000:
            self.alert_history = self.alert_history[-5000:]  # Keep last 5000

    async def _clear_alert(self, alert_key: str) -> None:
        """Clear/resolve an active alert."""
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            
            # Send resolution notification
            resolution_message = f"RESOLVED: {alert.message}"
            logger.info(resolution_message)
            
            # Notify through callbacks
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert resolution callback: {e}")

    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.rule_id}")

    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule."""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False

    def add_notification(self, notification: AlertNotification) -> None:
        """Add a notification configuration."""
        self.notifications[notification.notification_id] = notification
        logger.info(f"Added notification: {notification.notification_id}")

    def remove_notification(self, notification_id: str) -> bool:
        """Remove a notification configuration."""
        if notification_id in self.notifications:
            del self.notifications[notification_id]
            logger.info(f"Removed notification: {notification_id}")
            return True
        return False

    def suppress_alert(self, alert_key: str, duration: timedelta) -> None:
        """Suppress alerts for a specific key and duration."""
        self.suppression_rules[alert_key] = datetime.utcnow() + duration
        logger.info(f"Suppressed alerts for {alert_key} until {self.suppression_rules[alert_key]}")

    def add_alert_callback(self, callback: Callable) -> None:
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove an alert callback function."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)

    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active alerts."""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]

    def get_alert_history(
        self,
        integration_name: Optional[str] = None,
        alert_level: Optional[AlertLevel] = None,
        time_window: Optional[timedelta] = None
    ) -> List[PerformanceAlert]:
        """Get alert history with optional filters."""
        alerts = self.alert_history.copy()
        
        if integration_name:
            alerts = [a for a in alerts if a.integration_name == integration_name]
            
        if alert_level:
            alerts = [a for a in alerts if a.alert_level == alert_level]
            
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            alerts = [a for a in alerts if a.timestamp >= cutoff_time]
            
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alerting system statistics."""
        active_alerts = self.get_active_alerts()
        
        stats = {
            'active_alerts': len(active_alerts),
            'total_rules': len(self.alert_rules),
            'total_notifications': len(self.notifications),
            'alerts_last_24h': len([a for a in self.alert_history 
                                  if a.timestamp >= datetime.utcnow() - timedelta(days=1)]),
            'suppressed_alerts': len(self.suppression_rules),
            'alerting_enabled': self.alerting_enabled,
            'rate_limit_remaining': self.max_alerts_per_hour - len(self.alert_count_window)
        }
        
        # Alert level breakdown
        level_counts = {}
        for alert in active_alerts:
            level = alert.alert_level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        stats['alert_levels'] = level_counts
        
        return stats

    async def test_notification(self, notification_id: str) -> bool:
        """Test a notification configuration."""
        if notification_id not in self.notifications:
            return False
            
        notification = self.notifications[notification_id]
        
        # Create test alert
        test_alert = PerformanceAlert(
            alert_id="test",
            metric_name="test_metric",
            integration_name="test_integration",
            alert_level=AlertLevel.INFO,
            threshold_value=100.0,
            actual_value=150.0,
            message="This is a test alert",
            timestamp=datetime.utcnow()
        )
        
        try:
            await self._send_notification(test_alert, notification)
            return True
        except Exception as e:
            logger.error(f"Test notification failed: {e}")
            return False


# Export main classes
__all__ = [
    "AlertingSystem",
    "AlertRule",
    "AlertNotification"
]