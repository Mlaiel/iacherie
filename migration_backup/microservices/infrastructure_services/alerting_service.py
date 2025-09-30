"""
Alerting Service
===============

Enterprise-grade alerting service for proactive monitoring and incident response.
Provides intelligent alerting with escalation and notification management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    """Alert status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"

class AlertingService:
    """
    Enterprise Alerting Service
    
    Provides intelligent alerting with escalation policies,
    notification routing, and comprehensive alert management.
    """
    
    def __init__(self):
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = {}
        self.escalation_policies = {}
        self.notification_channels = {}
        self.is_active = False
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize alerting service"""
        try:
            logger.info("Initializing Alerting Service...")
            
            # Setup default alert rules
            await self._setup_default_alert_rules()
            
            # Setup escalation policies
            await self._setup_escalation_policies()
            
            # Setup notification channels
            await self._setup_notification_channels()
            
            # Start alert monitoring
            asyncio.create_task(self._alert_monitoring_loop())
            
            self.is_active = True
            
            return {
                "status": "success",
                "service": "alerting",
                "alert_rules": len(self.alert_rules),
                "escalation_policies": len(self.escalation_policies)
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize alerting service: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            "high_error_rate": {
                "name": "High Error Rate",
                "description": "Error rate exceeds threshold",
                "condition": "error_rate > 5",
                "severity": AlertSeverity.WARNING,
                "threshold": 5.0,
                "evaluation_window": 300,  # 5 minutes
                "escalation_policy": "default"
            },
            "critical_error_rate": {
                "name": "Critical Error Rate", 
                "description": "Error rate critically high",
                "condition": "error_rate > 15",
                "severity": AlertSeverity.CRITICAL,
                "threshold": 15.0,
                "evaluation_window": 180,  # 3 minutes
                "escalation_policy": "critical"
            },
            "high_response_time": {
                "name": "High Response Time",
                "description": "Response time exceeds acceptable threshold",
                "condition": "avg_response_time > 2000",
                "severity": AlertSeverity.WARNING,
                "threshold": 2000.0,
                "evaluation_window": 600,  # 10 minutes
                "escalation_policy": "default"
            },
            "service_down": {
                "name": "Service Down",
                "description": "Service health check failing",
                "condition": "service_health == 0",
                "severity": AlertSeverity.EMERGENCY,
                "threshold": 0,
                "evaluation_window": 60,  # 1 minute
                "escalation_policy": "emergency"
            },
            "high_cpu_usage": {
                "name": "High CPU Usage",
                "description": "CPU usage exceeds threshold",
                "condition": "cpu_usage > 80",
                "severity": AlertSeverity.WARNING,
                "threshold": 80.0,
                "evaluation_window": 300,  # 5 minutes
                "escalation_policy": "default"
            },
            "low_disk_space": {
                "name": "Low Disk Space",
                "description": "Disk space critically low",
                "condition": "disk_usage > 90",
                "severity": AlertSeverity.CRITICAL,
                "threshold": 90.0,
                "evaluation_window": 300,  # 5 minutes
                "escalation_policy": "critical"
            }
        }
    
    async def _setup_escalation_policies(self):
        """Setup escalation policies"""
        self.escalation_policies = {
            "default": {
                "name": "Default Escalation",
                "steps": [
                    {"delay": 0, "channels": ["email"], "recipients": ["dev-team"]},
                    {"delay": 900, "channels": ["email", "slack"], "recipients": ["dev-team", "team-lead"]},  # 15 min
                    {"delay": 3600, "channels": ["email", "slack", "phone"], "recipients": ["dev-team", "team-lead", "manager"]}  # 1 hour
                ]
            },
            "critical": {
                "name": "Critical Escalation",
                "steps": [
                    {"delay": 0, "channels": ["email", "slack"], "recipients": ["dev-team", "team-lead"]},
                    {"delay": 300, "channels": ["email", "slack", "phone"], "recipients": ["dev-team", "team-lead", "manager"]},  # 5 min
                    {"delay": 900, "channels": ["email", "slack", "phone"], "recipients": ["all-hands"]}  # 15 min
                ]
            },
            "emergency": {
                "name": "Emergency Escalation",
                "steps": [
                    {"delay": 0, "channels": ["email", "slack", "phone", "sms"], "recipients": ["dev-team", "team-lead", "manager", "cto"]}
                ]
            }
        }
    
    async def _setup_notification_channels(self):
        """Setup notification channels"""
        self.notification_channels = {
            "email": {
                "enabled": True,
                "endpoint": "smtp://mail.ainflue.com",
                "rate_limit": 100  # per hour
            },
            "slack": {
                "enabled": True,
                "webhook": "https://hooks.slack.com/services/...",
                "rate_limit": 50
            },
            "phone": {
                "enabled": True,
                "provider": "twilio",
                "rate_limit": 10
            },
            "sms": {
                "enabled": True,
                "provider": "twilio",
                "rate_limit": 20
            }
        }
    
    async def evaluate_alert_condition(
        self,
        rule_name: str,
        metric_value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Evaluate alert condition against current metrics"""
        try:
            if rule_name not in self.alert_rules:
                return {"status": "error", "error": "Alert rule not found"}
            
            rule = self.alert_rules[rule_name]
            
            # Check if condition is met
            condition_met = False
            
            if ">" in rule["condition"]:
                condition_met = metric_value > rule["threshold"]
            elif "<" in rule["condition"]:
                condition_met = metric_value < rule["threshold"]
            elif "==" in rule["condition"]:
                condition_met = metric_value == rule["threshold"]
            
            if condition_met:
                # Fire alert
                alert_result = await self._fire_alert(rule_name, metric_value, labels)
                return alert_result
            else:
                # Check if we should resolve existing alert
                await self._check_alert_resolution(rule_name, metric_value, labels)
                return {
                    "status": "success",
                    "action": "condition_not_met",
                    "rule": rule_name,
                    "value": metric_value
                }
            
        except Exception as e:
            logger.error(f"Failed to evaluate alert condition: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _fire_alert(
        self,
        rule_name: str,
        metric_value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Fire an alert"""
        try:
            rule = self.alert_rules[rule_name]
            alert_id = f"alert_{rule_name}_{datetime.utcnow().timestamp()}"
            
            # Check if similar alert already exists
            existing_alert = await self._find_existing_alert(rule_name, labels)
            if existing_alert:
                return {
                    "status": "success",
                    "action": "alert_exists",
                    "alert_id": existing_alert["id"]
                }
            
            alert_data = {
                "id": alert_id,
                "rule_name": rule_name,
                "rule": rule,
                "metric_value": metric_value,
                "labels": labels or {},
                "severity": rule["severity"].value,
                "status": AlertStatus.OPEN.value,
                "fired_at": datetime.utcnow().isoformat(),
                "escalation_step": 0,
                "notifications_sent": []
            }
            
            self.active_alerts[alert_id] = alert_data
            
            # Start escalation process
            await self._start_escalation(alert_id)
            
            logger.warning(f"Alert fired: {rule_name} - Value: {metric_value}")
            
            return {
                "status": "success",
                "action": "alert_fired",
                "alert_id": alert_id,
                "severity": rule["severity"].value
            }
            
        except Exception as e:
            logger.error(f"Failed to fire alert: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _find_existing_alert(
        self,
        rule_name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Find existing alert for the same condition"""
        for alert_id, alert_data in self.active_alerts.items():
            if (alert_data["rule_name"] == rule_name and 
                alert_data["labels"] == (labels or {}) and
                alert_data["status"] in [AlertStatus.OPEN.value, AlertStatus.ACKNOWLEDGED.value]):
                return alert_data
        return None
    
    async def _start_escalation(self, alert_id: str):
        """Start escalation process for alert"""
        alert_data = self.active_alerts.get(alert_id)
        if not alert_data:
            return
        
        rule = alert_data["rule"]
        escalation_policy = self.escalation_policies.get(rule["escalation_policy"])
        
        if not escalation_policy:
            logger.error(f"Escalation policy not found: {rule['escalation_policy']}")
            return
        
        # Start with first escalation step
        await self._execute_escalation_step(alert_id, 0)
    
    async def _execute_escalation_step(self, alert_id: str, step_index: int):
        """Execute specific escalation step"""
        alert_data = self.active_alerts.get(alert_id)
        if not alert_data:
            return
        
        rule = alert_data["rule"]
        escalation_policy = self.escalation_policies.get(rule["escalation_policy"])
        
        if step_index >= len(escalation_policy["steps"]):
            return
        
        step = escalation_policy["steps"][step_index]
        
        # Wait for delay if specified
        if step["delay"] > 0:
            await asyncio.sleep(step["delay"])
        
        # Check if alert is still active
        if alert_id not in self.active_alerts or self.active_alerts[alert_id]["status"] != AlertStatus.OPEN.value:
            return
        
        # Send notifications
        notification_result = await self._send_notifications(alert_id, step)
        
        # Update alert
        alert_data["escalation_step"] = step_index
        alert_data["notifications_sent"].append({
            "step": step_index,
            "timestamp": datetime.utcnow().isoformat(),
            "result": notification_result
        })
        
        # Schedule next escalation step
        if step_index + 1 < len(escalation_policy["steps"]):
            asyncio.create_task(self._execute_escalation_step(alert_id, step_index + 1))
    
    async def _send_notifications(self, alert_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications for escalation step"""
        alert_data = self.active_alerts.get(alert_id)
        if not alert_data:
            return {"status": "error", "error": "Alert not found"}
        
        notification_results = []
        
        for channel in step["channels"]:
            if channel in self.notification_channels and self.notification_channels[channel]["enabled"]:
                result = await self._send_notification_to_channel(alert_id, channel, step["recipients"])
                notification_results.append(result)
        
        return {
            "status": "success",
            "notifications_sent": len(notification_results),
            "results": notification_results
        }
    
    async def _send_notification_to_channel(
        self,
        alert_id: str,
        channel: str,
        recipients: List[str]
    ) -> Dict[str, Any]:
        """Send notification to specific channel"""
        # Mock notification sending - in real implementation would call actual notification services
        logger.info(f"Sending alert {alert_id} via {channel} to {recipients}")
        
        return {
            "channel": channel,
            "recipients": recipients,
            "status": "sent",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_alert_resolution(
        self,
        rule_name: str,
        metric_value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Check if existing alert should be resolved"""
        existing_alert = await self._find_existing_alert(rule_name, labels)
        if existing_alert and existing_alert["status"] == AlertStatus.OPEN.value:
            await self.resolve_alert(existing_alert["id"], "auto_resolved", "Condition no longer met")
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, note: str = "") -> Dict[str, Any]:
        """Acknowledge an alert"""
        try:
            if alert_id not in self.active_alerts:
                return {"status": "error", "error": "Alert not found"}
            
            alert_data = self.active_alerts[alert_id]
            alert_data["status"] = AlertStatus.ACKNOWLEDGED.value
            alert_data["acknowledged_by"] = user_id
            alert_data["acknowledged_at"] = datetime.utcnow().isoformat()
            alert_data["acknowledgment_note"] = note
            
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            
            return {
                "status": "success",
                "alert_id": alert_id,
                "acknowledged_by": user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return {"status": "error", "error": str(e)}
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_note: str = "") -> Dict[str, Any]:
        """Resolve an alert"""
        try:
            if alert_id not in self.active_alerts:
                return {"status": "error", "error": "Alert not found"}
            
            alert_data = self.active_alerts[alert_id]
            alert_data["status"] = AlertStatus.RESOLVED.value
            alert_data["resolved_by"] = resolved_by
            alert_data["resolved_at"] = datetime.utcnow().isoformat()
            alert_data["resolution_note"] = resolution_note
            
            # Move to history
            self.alert_history[alert_id] = alert_data
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
            
            return {
                "status": "success",
                "alert_id": alert_id,
                "resolved_by": resolved_by
            }
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _alert_monitoring_loop(self):
        """Continuous alert monitoring loop"""
        while self.is_active:
            try:
                # Check for stale alerts (alerts that should auto-resolve)
                await self._check_stale_alerts()
                
                # Clean up old alert history
                await self._cleanup_alert_history()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in alert monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _check_stale_alerts(self):
        """Check for stale alerts that should be auto-resolved"""
        current_time = datetime.utcnow()
        
        for alert_id, alert_data in list(self.active_alerts.items()):
            fired_time = datetime.fromisoformat(alert_data["fired_at"])
            
            # Auto-resolve alerts older than 24 hours if no acknowledgment
            if (current_time - fired_time).total_seconds() > 86400:  # 24 hours
                if alert_data["status"] == AlertStatus.OPEN.value:
                    await self.resolve_alert(alert_id, "system", "Auto-resolved after 24 hours")
    
    async def _cleanup_alert_history(self):
        """Clean up old alert history"""
        cutoff_time = datetime.utcnow() - timedelta(days=90)  # Keep 90 days
        
        to_remove = []
        for alert_id, alert_data in self.alert_history.items():
            resolved_time = datetime.fromisoformat(alert_data.get("resolved_at", alert_data["fired_at"]))
            if resolved_time < cutoff_time:
                to_remove.append(alert_id)
        
        for alert_id in to_remove:
            del self.alert_history[alert_id]
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> Dict[str, Any]:
        """Get active alerts optionally filtered by severity"""
        try:
            alerts = list(self.active_alerts.values())
            
            if severity:
                alerts = [alert for alert in alerts if alert["severity"] == severity.value]
            
            return {
                "status": "success",
                "active_alerts": alerts,
                "count": len(alerts)
            }
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alerting statistics"""
        total_alerts = len(self.active_alerts) + len(self.alert_history)
        
        severity_breakdown = {severity.value: 0 for severity in AlertSeverity}
        for alert in list(self.active_alerts.values()) + list(self.alert_history.values()):
            severity_breakdown[alert["severity"]] += 1
        
        return {
            "service": "alerting",
            "statistics": {
                "total_alerts": total_alerts,
                "active_alerts": len(self.active_alerts),
                "resolved_alerts": len(self.alert_history),
                "alert_rules": len(self.alert_rules),
                "escalation_policies": len(self.escalation_policies),
                "severity_breakdown": severity_breakdown
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get alerting service health status"""
        return {
            "service": "alerting",
            "status": "healthy" if self.is_active else "inactive",
            "active_alerts": len(self.active_alerts),
            "monitoring_active": self.is_active,
            "last_check": datetime.utcnow().isoformat()
        }