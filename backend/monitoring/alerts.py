"""🚨 Unified Alerts Module - IA Influencer Agent Platform
========================================================

Consolidated alert management system combining:
- Intelligent alert routing and correlation
- Business, technical, AI/ML, and security alerts  
- PagerDuty integration and escalation management
- Alert suppression and noise reduction

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AlertCategory(Enum):
    """Alert categories for intelligent routing"""
    BUSINESS = "business"
    TECHNICAL = "technical" 
    AI_ML = "ai_ml"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    CONTENT = "content"
    USER = "user"
    REVENUE = "revenue"


class AlertSeverity(Enum):
    """Alert severity levels with escalation priority"""
    EMERGENCY = "emergency"  # Immediate escalation required
    CRITICAL = "critical"    # Escalate within 15 minutes
    WARNING = "warning"      # Escalate within 1 hour
    INFO = "info"           # No automatic escalation
    

class AlertStatus(Enum):
    """Alert lifecycle status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    TEAMS = "teams"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    """Individual alert definition"""
    id: str
    title: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.OPEN
    source: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str
    threshold: float
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown_minutes: int = 15
    escalation_minutes: int = 60


@dataclass
class EscalationPolicy:
    """Alert escalation policy"""
    name: str
    levels: List[Dict[str, Any]]
    timeout_minutes: int = 30
    repeat_escalation: bool = True


class AlertCorrelator:
    """Alert correlation and noise reduction engine"""
    
    def __init__(self):
        self.correlation_window = timedelta(minutes=5)
        self.similarity_threshold = 0.8
        self.correlation_cache = {}
    
    def correlate_alerts(self, new_alert: Alert, existing_alerts: List[Alert]) -> List[Alert]:
        """Correlate new alert with existing alerts to reduce noise"""
        correlated = []
        
        for existing in existing_alerts:
            if self._are_correlated(new_alert, existing):
                correlated.append(existing)
        
        return correlated
    
    def _are_correlated(self, alert1: Alert, alert2: Alert) -> bool:
        """Check if two alerts are correlated"""
        # Time window check
        time_diff = abs((alert1.created_at - alert2.created_at).total_seconds())
        if time_diff > self.correlation_window.total_seconds():
            return False
        
        # Category and severity correlation
        if alert1.category == alert2.category and alert1.severity == alert2.severity:
            return True
        
        # Source correlation
        if alert1.source == alert2.source and alert1.source:
            return True
        
        # Tag similarity
        common_tags = set(alert1.tags.keys()) & set(alert2.tags.keys())
        if len(common_tags) >= 2:
            matching_values = sum(
                1 for tag in common_tags 
                if alert1.tags[tag] == alert2.tags[tag]
            )
            if matching_values / len(common_tags) >= self.similarity_threshold:
                return True
        
        return False


class PagerDutyIntegration:
    """PagerDuty integration for alert escalation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.integration_key = config.get("integration_key", "")
        self.service_name = config.get("service_name", "IA Influencer Agent")
        self.enabled = bool(self.integration_key)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to PagerDuty"""
        if not self.enabled:
            logger.warning("PagerDuty integration not configured")
            return False
        
        try:
            # Simulate PagerDuty API call
            payload = {
                "routing_key": self.integration_key,
                "event_action": "trigger",
                "dedup_key": alert.id,
                "payload": {
                    "summary": alert.title,
                    "source": alert.source or "IA-Influencer-Agent",
                    "severity": self._map_severity(alert.severity),
                    "component": alert.category.value,
                    "group": alert.tags.get("service", "unknown"),
                    "class": alert.tags.get("alert_type", "unknown"),
                    "custom_details": alert.metadata
                }
            }
            
            # In a real implementation, this would make an HTTP request to PagerDuty
            logger.info(f"Would send PagerDuty alert: {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert in PagerDuty"""
        if not self.enabled:
            return False
        
        try:
            # Simulate PagerDuty resolve API call
            logger.info(f"Would resolve PagerDuty alert: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve PagerDuty alert: {e}")
            return False
    
    def _map_severity(self, severity: AlertSeverity) -> str:
        """Map internal severity to PagerDuty severity"""
        mapping = {
            AlertSeverity.EMERGENCY: "critical",
            AlertSeverity.CRITICAL: "critical",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.INFO: "info"
        }
        return mapping.get(severity, "info")


class UnifiedAlertManager:
    """
    Unified alert management system that consolidates all alerting functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerts: Dict[str, Alert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        
        # Alert processing components
        self.correlator = AlertCorrelator()
        self.pagerduty = PagerDutyIntegration(self.config.get("pagerduty", {}))
        
        # Alert state tracking
        self.alert_counts = defaultdict(int)
        self.recent_alerts = deque(maxlen=1000)
        self.suppressed_alerts = set()
        
        # Initialize default rules and policies
        self._initialize_default_rules()
        self._initialize_escalation_policies()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            # Business alerts
            AlertRule(
                name="revenue_drop",
                category=AlertCategory.BUSINESS,
                severity=AlertSeverity.CRITICAL,
                condition="revenue < previous_day * 0.8",
                threshold=0.8,
                channels=[AlertChannel.EMAIL, AlertChannel.PAGERDUTY]
            ),
            AlertRule(
                name="user_churn_spike",
                category=AlertCategory.BUSINESS,
                severity=AlertSeverity.WARNING,
                condition="churn_rate > 0.05",
                threshold=0.05,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
            ),
            
            # Technical alerts
            AlertRule(
                name="high_cpu_usage",
                category=AlertCategory.TECHNICAL,
                severity=AlertSeverity.WARNING,
                condition="cpu_percent > 80",
                threshold=80.0,
                channels=[AlertChannel.EMAIL]
            ),
            AlertRule(
                name="memory_exhaustion",
                category=AlertCategory.TECHNICAL,
                severity=AlertSeverity.CRITICAL,
                condition="memory_percent > 90",
                threshold=90.0,
                channels=[AlertChannel.EMAIL, AlertChannel.PAGERDUTY]
            ),
            
            # AI/ML alerts
            AlertRule(
                name="model_accuracy_degradation",
                category=AlertCategory.AI_ML,
                severity=AlertSeverity.WARNING,
                condition="model_accuracy < 0.85",
                threshold=0.85,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
            ),
            AlertRule(
                name="inference_latency_spike",
                category=AlertCategory.AI_ML,
                severity=AlertSeverity.WARNING,
                condition="inference_latency > 100",
                threshold=100.0,
                channels=[AlertChannel.EMAIL]
            ),
            
            # Security alerts
            AlertRule(
                name="suspicious_login_attempts",
                category=AlertCategory.SECURITY,
                severity=AlertSeverity.CRITICAL,
                condition="failed_logins > 10",
                threshold=10.0,
                channels=[AlertChannel.EMAIL, AlertChannel.PAGERDUTY, AlertChannel.SMS]
            ),
            AlertRule(
                name="data_breach_detection",
                category=AlertCategory.SECURITY,
                severity=AlertSeverity.EMERGENCY,
                condition="unauthorized_access_detected",
                threshold=1.0,
                channels=[AlertChannel.EMAIL, AlertChannel.PAGERDUTY, AlertChannel.SMS]
            ),
        ]
        
        for rule in default_rules:
            self.rules[rule.name] = rule
    
    def _initialize_escalation_policies(self):
        """Initialize escalation policies"""
        default_policies = [
            EscalationPolicy(
                name="business_critical",
                levels=[
                    {"channels": [AlertChannel.EMAIL], "timeout_minutes": 15},
                    {"channels": [AlertChannel.PAGERDUTY], "timeout_minutes": 30},
                    {"channels": [AlertChannel.SMS], "timeout_minutes": 60}
                ],
                timeout_minutes=30
            ),
            EscalationPolicy(
                name="technical_standard",
                levels=[
                    {"channels": [AlertChannel.EMAIL], "timeout_minutes": 30},
                    {"channels": [AlertChannel.SLACK], "timeout_minutes": 60}
                ],
                timeout_minutes=60
            )
        ]
        
        for policy in default_policies:
            self.escalation_policies[policy.name] = policy
    
    async def create_alert(
        self,
        title: str,
        description: str,
        category: AlertCategory,
        severity: AlertSeverity,
        source: str = "",
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new alert"""
        
        alert_id = self._generate_alert_id(title, source, category)
        
        # Check if alert already exists (deduplication)
        if alert_id in self.alerts and self.alerts[alert_id].status == AlertStatus.OPEN:
            logger.debug(f"Alert {alert_id} already exists and is open")
            return alert_id
        
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            source=source,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Check for correlation with existing alerts
        existing_alerts = [a for a in self.alerts.values() if a.status == AlertStatus.OPEN]
        correlated = self.correlator.correlate_alerts(alert, existing_alerts)
        
        # If highly correlated, suppress this alert
        if len(correlated) >= 3:
            alert.status = AlertStatus.SUPPRESSED
            alert.metadata["suppressed_reason"] = "highly_correlated"
            alert.metadata["correlated_alerts"] = [a.id for a in correlated]
            self.suppressed_alerts.add(alert_id)
            logger.info(f"Alert {alert_id} suppressed due to correlation")
        
        # Store alert
        self.alerts[alert_id] = alert
        self.recent_alerts.append(alert)
        self.alert_counts[category] += 1
        
        # Process alert if not suppressed
        if alert.status != AlertStatus.SUPPRESSED:
            await self._process_alert(alert)
        
        logger.info(f"Created alert {alert_id}: {title}")
        return alert_id
    
    async def _process_alert(self, alert: Alert):
        """Process alert through notification and escalation system"""
        
        # Send notifications based on severity
        await self._send_notifications(alert)
        
        # Schedule escalation if required
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            await self._schedule_escalation(alert)
    
    async def _send_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.rules.values()
            if rule.category == alert.category and rule.enabled
        ]
        
        channels = set()
        for rule in applicable_rules:
            channels.update(rule.channels)
        
        # Send to each channel
        for channel in channels:
            try:
                await self._send_to_channel(alert, channel)
            except Exception as e:
                logger.error(f"Failed to send alert {alert.id} to {channel}: {e}")
    
    async def _send_to_channel(self, alert: Alert, channel: AlertChannel):
        """Send alert to specific notification channel"""
        
        if channel == AlertChannel.PAGERDUTY:
            await self.pagerduty.send_alert(alert)
        elif channel == AlertChannel.EMAIL:
            logger.info(f"Would send email alert: {alert.title}")
        elif channel == AlertChannel.SLACK:
            logger.info(f"Would send Slack alert: {alert.title}")
        elif channel == AlertChannel.SMS:
            logger.info(f"Would send SMS alert: {alert.title}")
        elif channel == AlertChannel.TEAMS:
            logger.info(f"Would send Teams alert: {alert.title}")
        elif channel == AlertChannel.WEBHOOK:
            logger.info(f"Would send webhook alert: {alert.title}")
    
    async def _schedule_escalation(self, alert: Alert):
        """Schedule alert escalation based on policies"""
        
        policy_name = "business_critical" if alert.category == AlertCategory.BUSINESS else "technical_standard"
        policy = self.escalation_policies.get(policy_name)
        
        if not policy:
            logger.warning(f"No escalation policy found for alert {alert.id}")
            return
        
        # In a real implementation, this would schedule background tasks
        logger.info(f"Scheduled escalation for alert {alert.id} using policy {policy_name}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        
        if alert_id not in self.alerts:
            logger.warning(f"Alert {alert_id} not found")
            return False
        
        alert = self.alerts[alert_id]
        if alert.status != AlertStatus.OPEN:
            logger.warning(f"Alert {alert_id} is not open (status: {alert.status})")
            return False
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = datetime.now()
        
        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_note: str = "") -> bool:
        """Resolve an alert"""
        
        if alert_id not in self.alerts:
            logger.warning(f"Alert {alert_id} not found")
            return False
        
        alert = self.alerts[alert_id]
        if alert.status == AlertStatus.RESOLVED:
            logger.warning(f"Alert {alert_id} is already resolved")
            return False
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.resolved_by = resolved_by
        alert.updated_at = datetime.now()
        
        if resolution_note:
            alert.metadata["resolution_note"] = resolution_note
        
        # Resolve in external systems
        await self.pagerduty.resolve_alert(alert_id)
        
        logger.info(f"Alert {alert_id} resolved by {resolved_by}")
        return True
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get specific alert by ID"""
        return self.alerts.get(alert_id)
    
    def get_alerts_by_status(self, status: AlertStatus) -> List[Alert]:
        """Get alerts by status"""
        return [alert for alert in self.alerts.values() if alert.status == status]
    
    def get_alerts_by_category(self, category: AlertCategory) -> List[Alert]:
        """Get alerts by category"""
        return [alert for alert in self.alerts.values() if alert.category == category]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity"""
        return [alert for alert in self.alerts.values() if alert.severity == severity]
    
    def get_open_alerts(self) -> List[Alert]:
        """Get all open alerts"""
        return self.get_alerts_by_status(AlertStatus.OPEN)
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts within specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alerts.values()
            if alert.created_at >= cutoff_time
        ]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get comprehensive alert statistics"""
        total_alerts = len(self.alerts)
        open_alerts = len(self.get_open_alerts())
        recent_alerts = len(self.get_recent_alerts(24))
        
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for alert in self.alerts.values():
            severity_counts[alert.severity.value] += 1
            category_counts[alert.category.value] += 1
        
        return {
            "total_alerts": total_alerts,
            "open_alerts": open_alerts,
            "recent_alerts_24h": recent_alerts,
            "suppressed_alerts": len(self.suppressed_alerts),
            "alerts_by_severity": dict(severity_counts),
            "alerts_by_category": dict(category_counts),
            "rules_configured": len(self.rules),
            "escalation_policies": len(self.escalation_policies)
        }
    
    def _generate_alert_id(self, title: str, source: str, category: AlertCategory) -> str:
        """Generate unique alert ID"""
        content = f"{title}_{source}_{category.value}_{int(time.time() // 300)}"  # 5-minute buckets
        return hashlib.md5(content.encode()).hexdigest()[:12]


# Global alert manager instance
alert_manager = UnifiedAlertManager()


# Convenience functions for external use
async def create_business_alert(title: str, description: str, severity: AlertSeverity = AlertSeverity.WARNING, **kwargs) -> str:
    """Create a business alert"""
    return await alert_manager.create_alert(
        title=title,
        description=description,
        category=AlertCategory.BUSINESS,
        severity=severity,
        **kwargs
    )


async def create_technical_alert(title: str, description: str, severity: AlertSeverity = AlertSeverity.WARNING, **kwargs) -> str:
    """Create a technical alert"""
    return await alert_manager.create_alert(
        title=title,
        description=description,
        category=AlertCategory.TECHNICAL,
        severity=severity,
        **kwargs
    )


async def create_ai_alert(title: str, description: str, severity: AlertSeverity = AlertSeverity.WARNING, **kwargs) -> str:
    """Create an AI/ML alert"""
    return await alert_manager.create_alert(
        title=title,
        description=description,
        category=AlertCategory.AI_ML,
        severity=severity,
        **kwargs
    )


async def create_security_alert(title: str, description: str, severity: AlertSeverity = AlertSeverity.CRITICAL, **kwargs) -> str:
    """Create a security alert"""
    return await alert_manager.create_alert(
        title=title,
        description=description,
        category=AlertCategory.SECURITY,
        severity=severity,
        **kwargs
    )


def get_open_alerts() -> List[Alert]:
    """Get all open alerts"""
    return alert_manager.get_open_alerts()


def get_alert_statistics() -> Dict[str, Any]:
    """Get alert statistics"""
    return alert_manager.get_alert_statistics()