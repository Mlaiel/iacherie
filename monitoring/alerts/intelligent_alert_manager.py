"""🚨 Intelligent Alert Manager - Central Alert System
==================================================

Unified intelligent alert system for the Ainflue platform that consolidates and enhances
existing alert infrastructure with intelligent routing, escalation, and correlation.

Features:
- Business Alerts (Revenue, User Experience)
- Technical Alerts (Infrastructure, Security)
- AI Alerts (Model Drift, Accuracy Degradation)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


class AlertCategory(Enum):
    """
Alert categories for intelligent routing"""

    BUSINESS = "business"
    TECHNICAL = "technical" 
    AI_ML = "ai_ml"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"


class AlertSeverity(Enum):
    """Alert severity levels with escalation priority"""

    EMERGENCY = "emergency"  # Immediate escalation required
    CRITICAL = "critical"    # Escalate within 15 minutes
    WARNING = "warning"      # Escalate within 1 hour
    INFO = "info"           # No automatic escalation
    

class AlertType(Enum):
    """Specific alert types"""
    # Business Alerts
    REVENUE_DROP = "revenue_drop"
    REVENUE_ANOMALY = "revenue_anomaly"
    USER_EXPERIENCE_DEGRADATION = "user_experience_degradation"
    ENGAGEMENT_DROP = "engagement_drop"
    PAYMENT_FAILURE = "payment_failure"
    
    # Technical Alerts
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    SERVICE_DOWN = "service_down"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    API_ERROR_SPIKE = "api_error_spike"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    
    # Security Alerts
    SECURITY_BREACH = "security_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    AUTHENTICATION_FAILURE = "authentication_failure"
    
    # AI/ML Alerts
    MODEL_DRIFT = "model_drift"
    ACCURACY_DEGRADATION = "accuracy_degradation"
    TRAINING_FAILURE = "training_failure"
    INFERENCE_LATENCY = "inference_latency"
    DATA_QUALITY_ISSUE = "data_quality_issue"


@dataclass
class AlertRule:
    """Intelligent alert rule with advanced capabilities"""
    rule_id: str
    name: str
    category: AlertCategory
    alert_type: AlertType
    severity: AlertSeverity
    expression: str
    threshold: Dict[str, Any]
    duration: str = "5m"
    enabled: bool = True
    auto_resolve: bool = True
    suppress_duration: str = "1h"
    escalation_levels: List[Dict[str, Any]] = field(default_factory=list)
    correlation_rules: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelligentAlert:
    """Enhanced alert with intelligent features"""
    alert_id: str
    rule_id: str
    category: AlertCategory
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    value: Union[float, str, Dict[str, Any]]
    threshold: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    escalation_level: int = 0
    escalated_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    auto_resolved: bool = False
    suppressed: bool = False
    suppressed_until: Optional[datetime] = None


class IntelligentAlertManager:
    """
    Central intelligent alert management system
    
    Features:
    - Intelligent alert correlation and deduplication
    - Automatic escalation based on severity and response time
    - Alert suppression and noise reduction
    - Business, technical, and AI/ML alert categorization
    - Advanced notification routing
    """
    
    def __init__(self):
        """
Initialize the intelligent alert manager"""
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, IntelligentAlert] = {}
        self.alert_history: List[IntelligentAlert] = []
        self.correlation_groups: Dict[str, List[str]] = defaultdict(list)
        self.escalation_tasks: Dict[str, asyncio.Task] = {}
        
        # Alert statistics
        self.alert_stats = {
            "total_alerts": 0,
            "alerts_by_category": defaultdict(int),
            "alerts_by_severity": defaultdict(int),
            "avg_resolution_time": 0,
            "escalation_rate": 0
        }
        
        # Initialize built-in alert rules
        self._initialize_default_rules()
        
        logger.info("IntelligentAlertManager initialized")
    
    def _initialize_default_rules(self):
        """Initialize default alert rules for all categories"""
        
        # Business Alert Rules
        self.add_alert_rule(AlertRule(
            rule_id="business_revenue_drop",
            name="Significant Revenue Drop",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.REVENUE_DROP,
            severity=AlertSeverity.CRITICAL,
            expression="(current_revenue - previous_revenue) / previous_revenue < -0.3",
            threshold={"percentage_drop": 30, "minimum_amount": 1000},
            duration="30m",
            escalation_levels=[
                {"level": 1, "delay": "15m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "1h", "channels": ["email", "slack", "phone"]}
            ],
            correlation_rules=["business_engagement_drop", "technical_payment_failure"]
        ))
        
        self.add_alert_rule(AlertRule(
            rule_id="business_user_experience",
            name="User Experience Degradation",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.USER_EXPERIENCE_DEGRADATION,
            severity=AlertSeverity.WARNING,
            expression="avg_response_time > 5000 or error_rate > 0.05",
            threshold={"response_time_ms": 5000, "error_rate": 0.05},
            duration="10m",
            escalation_levels=[
                {"level": 1, "delay": "30m", "channels": ["slack"]},
                {"level": 2, "delay": "2h", "channels": ["email", "slack"]}
            ]
        ))
        
        # Technical Alert Rules
        self.add_alert_rule(AlertRule(
            rule_id="technical_service_down",
            name="Critical Service Down",
            category=AlertCategory.TECHNICAL,
            alert_type=AlertType.SERVICE_DOWN,
            severity=AlertSeverity.EMERGENCY,
            expression="service_availability < 1",
            threshold={"availability": 1.0},
            duration="1m",
            escalation_levels=[
                {"level": 1, "delay": "5m", "channels": ["email", "slack", "phone"]},
                {"level": 2, "delay": "15m", "channels": ["email", "slack", "phone", "pagerduty"]}
            ]
        ))
        
        self.add_alert_rule(AlertRule(
            rule_id="technical_resource_exhaustion",
            name="System Resource Exhaustion",
            category=AlertCategory.TECHNICAL,
            alert_type=AlertType.RESOURCE_EXHAUSTION,
            severity=AlertSeverity.CRITICAL,
            expression="cpu_usage > 90 or memory_usage > 85 or disk_usage > 90",
            threshold={"cpu_percent": 90, "memory_percent": 85, "disk_percent": 90},
            duration="5m",
            escalation_levels=[
                {"level": 1, "delay": "15m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "45m", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Security Alert Rules
        self.add_alert_rule(AlertRule(
            rule_id="security_breach_detected",
            name="Security Breach Detected",
            category=AlertCategory.SECURITY,
            alert_type=AlertType.SECURITY_BREACH,
            severity=AlertSeverity.EMERGENCY,
            expression="security_threat_score > 0.8",
            threshold={"threat_score": 0.8},
            duration="1m",
            auto_resolve=False,
            escalation_levels=[
                {"level": 1, "delay": "0m", "channels": ["email", "slack", "phone", "pagerduty"]},
                {"level": 2, "delay": "10m", "channels": ["email", "slack", "phone", "pagerduty", "sms"]}
            ]
        ))
        
        self.add_alert_rule(AlertRule(
            rule_id="security_suspicious_activity",
            name="Suspicious Activity Detected",
            category=AlertCategory.SECURITY,
            alert_type=AlertType.SUSPICIOUS_ACTIVITY,
            severity=AlertSeverity.WARNING,
            expression="failed_login_rate > 10 or unusual_access_pattern > 0.7",
            threshold={"failed_logins_per_minute": 10, "unusual_pattern_score": 0.7},
            duration="5m",
            escalation_levels=[
                {"level": 1, "delay": "30m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "2h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # AI/ML Alert Rules
        self.add_alert_rule(AlertRule(
            rule_id="ai_model_drift",
            name="AI Model Drift Detected",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.MODEL_DRIFT,
            severity=AlertSeverity.CRITICAL,
            expression="model_drift_score > 0.3",
            threshold={"drift_score": 0.3, "confidence_threshold": 0.95},
            duration="15m",
            escalation_levels=[
                {"level": 1, "delay": "1h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "4h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        self.add_alert_rule(AlertRule(
            rule_id="ai_accuracy_degradation",
            name="Model Accuracy Degradation",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.ACCURACY_DEGRADATION,
            severity=AlertSeverity.WARNING,
            expression="model_accuracy < baseline_accuracy * 0.95",
            threshold={"accuracy_drop_percent": 5, "minimum_samples": 100},
            duration="30m",
            escalation_levels=[
                {"level": 1, "delay": "2h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "8h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        self.add_alert_rule(AlertRule(
            rule_id="ai_inference_latency",
            name="AI Inference Latency High",
            category=AlertCategory.AI_ML,
            alert_type=AlertType.INFERENCE_LATENCY,
            severity=AlertSeverity.WARNING,
            expression="p95_inference_time > 10000",
            threshold={"latency_ms": 10000, "percentile": 95},
            duration="10m",
            escalation_levels=[
                {"level": 1, "delay": "1h", "channels": ["slack"]},
                {"level": 2, "delay": "3h", "channels": ["email", "slack"]}
            ]
        ))
        
        logger.info(f"Initialized {len(self.alert_rules)} default alert rules")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.rule_id} - {rule.name}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
    
    async def evaluate_alert_rules(self, metrics: Dict[str, Any]) -> List[IntelligentAlert]:
        """Evaluate all alert rules against current metrics"""
        triggered_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                # Check if rule conditions are met
                if await self._evaluate_rule_expression(rule, metrics):
                    alert = await self._create_alert(rule, metrics)
                    
                    # Check for correlation and deduplication
                    if not await self._is_duplicate_alert(alert):
                        triggered_alerts.append(alert)
                        await self._process_new_alert(alert)
                        
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_id}: {e}")
        
        return triggered_alerts
    
    async def _evaluate_rule_expression(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate if a rule expression is triggered"""
        try:
            # This is a simplified evaluation - in production, use a proper expression evaluator
            if rule.alert_type == AlertType.REVENUE_DROP:
                current = metrics.get("current_revenue", 0)
                previous = metrics.get("previous_revenue", 1)
                drop_percent = abs((current - previous) / previous) * 100 if previous > 0 else 0
                return drop_percent >= rule.threshold.get("percentage_drop", 30)
            
            elif rule.alert_type == AlertType.USER_EXPERIENCE_DEGRADATION:
                response_time = metrics.get("avg_response_time", 0)
                error_rate = metrics.get("error_rate", 0)
                return (response_time > rule.threshold.get("response_time_ms", 5000) or 
                       error_rate > rule.threshold.get("error_rate", 0.05))
            
            elif rule.alert_type == AlertType.SERVICE_DOWN:
                availability = metrics.get("service_availability", 1.0)
                return availability < rule.threshold.get("availability", 1.0)
            
            elif rule.alert_type == AlertType.RESOURCE_EXHAUSTION:
                cpu = metrics.get("cpu_usage", 0)
                memory = metrics.get("memory_usage", 0)
                disk = metrics.get("disk_usage", 0)
                return (cpu > rule.threshold.get("cpu_percent", 90) or
                       memory > rule.threshold.get("memory_percent", 85) or
                       disk > rule.threshold.get("disk_percent", 90))
            
            elif rule.alert_type == AlertType.SECURITY_BREACH:
                threat_score = metrics.get("security_threat_score", 0)
                return threat_score > rule.threshold.get("threat_score", 0.8)
            
            elif rule.alert_type == AlertType.MODEL_DRIFT:
                drift_score = metrics.get("model_drift_score", 0)
                return drift_score > rule.threshold.get("drift_score", 0.3)
            
            elif rule.alert_type == AlertType.ACCURACY_DEGRADATION:
                current_accuracy = metrics.get("model_accuracy", 1.0)
                baseline_accuracy = metrics.get("baseline_accuracy", 1.0)
                drop_threshold = rule.threshold.get("accuracy_drop_percent", 5) / 100
                return current_accuracy < baseline_accuracy * (1 - drop_threshold)
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating expression for rule {rule.rule_id}: {e}")
            return False
    
    async def _create_alert(self, rule: AlertRule, metrics: Dict[str, Any]) -> IntelligentAlert:
        """Create a new alert from a triggered rule"""
        alert_id = self._generate_alert_id(rule.rule_id, metrics)
        
        # Generate correlation ID if rule has correlation rules
        correlation_id = None
        if rule.correlation_rules:
            correlation_id = self._generate_correlation_id(rule.correlation_rules, metrics)
        
        alert = IntelligentAlert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            category=rule.category,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=self._generate_alert_title(rule, metrics),
            description=self._generate_alert_description(rule, metrics),
            timestamp=datetime.utcnow(),
            value=self._extract_alert_value(rule, metrics),
            threshold=rule.threshold,
            metadata={
                "rule_name": rule.name,
                "evaluation_metrics": metrics,
                "custom_metadata": rule.custom_metadata
            },
            correlation_id=correlation_id
        )
        
        return alert
    
    async def _is_duplicate_alert(self, alert: IntelligentAlert) -> bool:
        """Check if this is a duplicate alert that should be suppressed"""
        # Check if the same alert is already active
        if alert.alert_id in self.active_alerts:
            existing_alert = self.active_alerts[alert.alert_id]
            if not existing_alert.resolved:
                logger.debug(f"Suppressing duplicate alert: {alert.alert_id}")
                return True
        
        # Check for recent similar alerts (within suppress duration)
        suppress_duration = self._parse_duration(
            self.alert_rules[alert.rule_id].suppress_duration
        )
        cutoff_time = datetime.utcnow() - suppress_duration
        
        for historical_alert in reversed(self.alert_history):
            if historical_alert.timestamp < cutoff_time:
                break
            
            if (historical_alert.rule_id == alert.rule_id and
                historical_alert.alert_type == alert.alert_type and
                not historical_alert.resolved):
                logger.debug(f"Suppressing alert due to recent similar alert: {alert.alert_id}")
                return True
        
        return False
    
    async def _process_new_alert(self, alert: IntelligentAlert):
        """Process a new alert through the intelligent system"""
        # Add to active alerts
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Update statistics
        self.alert_stats["total_alerts"] += 1
        self.alert_stats["alerts_by_category"][alert.category.value] += 1
        self.alert_stats["alerts_by_severity"][alert.severity.value] += 1
        
        # Handle correlation
        if alert.correlation_id:
            self.correlation_groups[alert.correlation_id].append(alert.alert_id)
        
        # Schedule escalation if needed
        await self._schedule_escalation(alert)
        
        # Send initial notifications
        await self._send_alert_notifications(alert)
        
        logger.info(f"Processed new alert: {alert.alert_id} - {alert.title}")
    
    async def _schedule_escalation(self, alert: IntelligentAlert):
        """Schedule automatic escalation for an alert"""
        rule = self.alert_rules[alert.rule_id]
        
        if not rule.escalation_levels:
            return
        
        async def escalate_alert():
            try:
            logger.info(f"Executing escalate_alert")
            
            # Implementation for escalate_alert
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"escalate_alert completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"escalate_alert failed: {e}")
            raise
                for level_config in rule.escalation_levels:
                    level = level_config["level"]
                    delay = self._parse_duration(level_config["delay"])
                    
                    # Wait for the specified delay
                    await asyncio.sleep(delay.total_seconds())
                    
                    # Check if alert is still active and not acknowledged
                    if (alert.alert_id in self.active_alerts and 
                        not alert.acknowledged and not alert.resolved):
                        
                        alert.escalation_level = level
                        alert.escalated_at = datetime.utcnow()
                        
                        # Send escalation notifications
                        await self._send_escalation_notifications(alert, level_config)
                        
                        self.alert_stats["escalation_rate"] += 1
                        
                        logger.warning(f"Escalated alert {alert.alert_id} to level {level}")
                    else:
                        # Alert was resolved or acknowledged, stop escalation
                        break
                        
            except asyncio.CancelledError:
                logger.debug(f"Escalation cancelled for alert {alert.alert_id}")
            except Exception as e:
                logger.error(f"Error in escalation for alert {alert.alert_id}: {e}")
        
        # Start escalation task
        task = asyncio.create_task(escalate_alert())
        self.escalation_tasks[alert.alert_id] = task
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        # Cancel escalation if active
        if alert_id in self.escalation_tasks:
            self.escalation_tasks[alert_id].cancel()
            del self.escalation_tasks[alert_id]
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
    
    async def resolve_alert(self, alert_id: str, auto_resolved: bool = False) -> bool:
        """Resolve an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.auto_resolved = auto_resolved
        
        # Cancel escalation if active
        if alert_id in self.escalation_tasks:
            self.escalation_tasks[alert_id].cancel()
            del self.escalation_tasks[alert_id]
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        # Update resolution time statistics
        resolution_time = (alert.resolved_at - alert.timestamp).total_seconds()
        self._update_resolution_time_stats(resolution_time)
        
        logger.info(f"Alert resolved: {alert_id} ({'auto' if auto_resolved else 'manual'})")
        return True
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Get comprehensive alert statistics"""
        active_count = len(self.active_alerts)
        
        # Calculate alert distribution
        severity_distribution = {}
        category_distribution = {}
        
        for alert in self.active_alerts.values():
            severity_distribution[alert.severity.value] = severity_distribution.get(alert.severity.value, 0) + 1
            category_distribution[alert.category.value] = category_distribution.get(alert.category.value, 0) + 1
        
        return {
            "total_alerts": self.alert_stats["total_alerts"],
            "active_alerts": active_count,
            "alerts_by_category": dict(self.alert_stats["alerts_by_category"]),
            "alerts_by_severity": dict(self.alert_stats["alerts_by_severity"]),
            "active_severity_distribution": severity_distribution,
            "active_category_distribution": category_distribution,
            "avg_resolution_time_seconds": self.alert_stats["avg_resolution_time"],
            "escalation_rate": self.alert_stats["escalation_rate"],
            "correlation_groups": len(self.correlation_groups)
        }
    
    def _generate_alert_id(self, rule_id: str, metrics: Dict[str, Any]) -> str:
        """Generate a unique alert ID"""
        content = f"{rule_id}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _generate_correlation_id(self, correlation_rules: List[str], metrics: Dict[str, Any]) -> str:
        """Generate correlation ID for related alerts"""
        content = "_".join(sorted(correlation_rules))
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_alert_title(self, rule: AlertRule, metrics: Dict[str, Any]) -> str:
        """Generate alert title based on rule and metrics"""
        base_title = rule.name
        
        if rule.alert_type == AlertType.REVENUE_DROP:
            drop_amount = metrics.get("current_revenue", 0) - metrics.get("previous_revenue", 0)
            return f"{base_title}: €{abs(drop_amount):.2f}"
        
        elif rule.alert_type == AlertType.RESOURCE_EXHAUSTION:
            resource = "CPU" if metrics.get("cpu_usage", 0) > 90 else "Memory" if metrics.get("memory_usage", 0) > 85 else "Disk"
            return f"{base_title}: {resource} usage critical"
        
        elif rule.alert_type == AlertType.MODEL_DRIFT:
            drift_score = metrics.get("model_drift_score", 0)
            return f"{base_title}: Drift score {drift_score:.3f}"
        
        return base_title
    
    def _generate_alert_description(self, rule: AlertRule, metrics: Dict[str, Any]) -> str:
        """Generate detailed alert description"""
        base_desc = f"Alert triggered for rule: {rule.name}\n"
        base_desc += f"Severity: {rule.severity.value}\n"
        base_desc += f"Category: {rule.category.value}\n\n"
        
        # Add rule-specific details
        if rule.alert_type == AlertType.REVENUE_DROP:
            current = metrics.get("current_revenue", 0)
            previous = metrics.get("previous_revenue", 0)
            drop_percent = abs((current - previous) / previous) * 100 if previous > 0 else 0
            base_desc += f"Revenue dropped from €{previous:.2f} to €{current:.2f} ({drop_percent:.1f}% decrease)"
        
        elif rule.alert_type == AlertType.MODEL_DRIFT:
            drift_score = metrics.get("model_drift_score", 0)
            model_name = metrics.get("model_name", "Unknown")
            base_desc += f"Model '{model_name}' drift score: {drift_score:.3f} (threshold: {rule.threshold.get('drift_score', 0.3)})"
        
        return base_desc
    
    def _extract_alert_value(self, rule: AlertRule, metrics: Dict[str, Any]) -> Union[float, str, Dict[str, Any]]:
        """Extract the key value that triggered the alert"""
        if rule.alert_type == AlertType.REVENUE_DROP:
            return {
                "current_revenue": metrics.get("current_revenue", 0),
                "previous_revenue": metrics.get("previous_revenue", 0),
                "drop_percentage": abs((metrics.get("current_revenue", 0) - metrics.get("previous_revenue", 1)) / metrics.get("previous_revenue", 1)) * 100
            }
        
        elif rule.alert_type == AlertType.MODEL_DRIFT:
            return metrics.get("model_drift_score", 0)
        
        elif rule.alert_type == AlertType.RESOURCE_EXHAUSTION:
            return {
                "cpu_usage": metrics.get("cpu_usage", 0),
                "memory_usage": metrics.get("memory_usage", 0),
                "disk_usage": metrics.get("disk_usage", 0)
            }
        
        return str(metrics)
    
    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string to timedelta"""
        if duration_str.endswith('m'):
            return timedelta(minutes=int(duration_str[:-1]))
        elif duration_str.endswith('h'):
            return timedelta(hours=int(duration_str[:-1]))
        elif duration_str.endswith('s'):
            return timedelta(seconds=int(duration_str[:-1]))
        else:
            return timedelta(minutes=5)  # Default to 5 minutes
    
    def _update_resolution_time_stats(self, resolution_time_seconds: float):
        """
Update average resolution time statistics"""
        current_avg = self.alert_stats["avg_resolution_time"]
        total_alerts = self.alert_stats["total_alerts"]
        
        # Calculate running average
        if total_alerts > 0:
            self.alert_stats["avg_resolution_time"] = (
                (current_avg * (total_alerts - 1) + resolution_time_seconds) / total_alerts
            )
        else:
            self.alert_stats["avg_resolution_time"] = resolution_time_seconds
    
    async def _send_alert_notifications(self, alert: IntelligentAlert):
        """Send initial alert notifications"""
        # This would integrate with existing notification systems
        logger.info(f"Sending notifications for alert: {alert.alert_id}")
        # Implementation would call existing notification services
    
    async def _send_escalation_notifications(self, alert: IntelligentAlert, level_config: Dict[str, Any]):
        """Send escalation notifications"""
        channels = level_config.get("channels", [])
        logger.warning(f"Sending escalation notifications for alert {alert.alert_id} to channels: {channels}")
        # Implementation would call existing notification services with escalation context


# Export the main class
__all__ = ["IntelligentAlertManager", "AlertCategory", "AlertSeverity", "AlertType", "AlertRule", "IntelligentAlert"]