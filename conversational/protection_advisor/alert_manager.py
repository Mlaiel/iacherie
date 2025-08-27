"""
Alert Manager Module - Comprehensive alert management and notification system.

Provides intelligent alerting, escalation management, and notification
delivery for content protection events and system monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict

from ...core.config import settings
from ...core.cache import cache_manager
from ...utils.logging import get_logger

logger = get_logger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertCategory(str, Enum):
    """Alert categories for classification."""
    SECURITY_THREAT = "security_threat"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_PERFORMANCE = "system_performance"
    COMPLIANCE_ISSUE = "compliance_issue"
    CONTENT_PROTECTION = "content_protection"
    FINANCIAL_IMPACT = "financial_impact"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_ERROR = "system_error"


class AlertStatus(str, Enum):
    """Alert status states."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    SUPPRESSED = "suppressed"


class NotificationChannel(str, Enum):
    """Available notification channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    IN_APP = "in_app"


class EscalationLevel(str, Enum):
    """Escalation levels for alerts."""
    LEVEL_1 = "level_1"  # Initial response team
    LEVEL_2 = "level_2"  # Senior team/management
    LEVEL_3 = "level_3"  # Executive/emergency
    EXTERNAL = "external"  # External partners/authorities


@dataclass
class Alert:
    """Individual alert definition."""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    category: AlertCategory
    status: AlertStatus
    source: str
    affected_resources: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    assigned_to: Optional[str]
    escalation_level: EscalationLevel
    correlation_id: Optional[str]
    tags: List[str]


@dataclass
class NotificationRule:
    """Notification rule configuration."""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    channels: List[NotificationChannel]
    recipients: List[str]
    template: str
    cooldown_period: timedelta
    escalation_delay: timedelta
    is_active: bool
    priority: int


@dataclass
class EscalationPolicy:
    """Escalation policy definition."""
    policy_id: str
    name: str
    conditions: Dict[str, Any]
    escalation_steps: List[Dict[str, Any]]
    auto_escalation_enabled: bool
    escalation_intervals: List[timedelta]
    max_escalation_level: EscalationLevel
    is_active: bool


class AlertManager:
    """
    Comprehensive alert management and notification system.
    
    Provides intelligent alerting including:
    - Real-time alert generation and processing
    - Multi-channel notification delivery
    - Escalation management and automation
    - Alert correlation and deduplication
    - Performance monitoring and analytics
    - Integration with external systems
    """

    def __init__(self):
        self.active_alerts = {}
        self.notification_rules = {}
        self.escalation_policies = {}
        self.notification_channels = {}
        self.alert_history = []
        self.correlation_engine = None
        self.cache_ttl = 3600  # 1 hour
        
        # Initialize system components
        asyncio.create_task(self._initialize_alert_system())
    
    async def create_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        category: AlertCategory,
        source: str,
        affected_resources: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """
        Create a new alert with automatic processing.
        
        Args:
            title: Alert title
            description: Detailed description
            severity: Alert severity level
            category: Alert category
            source: Source system/component
            affected_resources: List of affected resources
            metadata: Additional metadata
            
        Returns:
            Created Alert object
        """
        try:
            alert_id = f"alert_{int(datetime.utcnow().timestamp() * 1000)}"
            
            # Check for correlation with existing alerts
            correlation_id = await self._correlate_alert(
                title, description, category, affected_resources
            )
            
            # Create alert object
            alert = Alert(
                alert_id=alert_id,
                title=title,
                description=description,
                severity=severity,
                category=category,
                status=AlertStatus.OPEN,
                source=source,
                affected_resources=affected_resources,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                acknowledged_at=None,
                resolved_at=None,
                assigned_to=None,
                escalation_level=EscalationLevel.LEVEL_1,
                correlation_id=correlation_id,
                tags=await self._generate_alert_tags(title, description, category)
            )
            
            logger.info(f"Creating alert {alert_id}: {title}")
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Cache alert
            await self._cache_alert(alert)
            
            # Process alert through pipeline
            await self._process_new_alert(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            raise
    
    async def process_alert_batch(
        self,
        alerts_data: List[Dict[str, Any]]
    ) -> List[Alert]:
        """
        Process multiple alerts in batch for efficiency.
        
        Args:
            alerts_data: List of alert data dictionaries
            
        Returns:
            List of created Alert objects
        """
        try:
            logger.info(f"Processing batch of {len(alerts_data)} alerts")
            
            # Create alerts in parallel
            alert_tasks = []
            for alert_data in alerts_data:
                task = self.create_alert(
                    title=alert_data.get("title"),
                    description=alert_data.get("description"),
                    severity=AlertSeverity(alert_data.get("severity", "medium")),
                    category=AlertCategory(alert_data.get("category")),
                    source=alert_data.get("source"),
                    affected_resources=alert_data.get("affected_resources", []),
                    metadata=alert_data.get("metadata")
                )
                alert_tasks.append(task)
            
            # Execute batch creation
            created_alerts = await asyncio.gather(*alert_tasks, return_exceptions=True)
            
            # Filter successful creations
            successful_alerts = [
                alert for alert in created_alerts 
                if isinstance(alert, Alert)
            ]
            
            # Log batch results
            logger.info(f"Successfully created {len(successful_alerts)} alerts")
            
            # Perform batch correlation analysis
            await self._analyze_batch_correlations(successful_alerts)
            
            return successful_alerts
            
        except Exception as e:
            logger.error(f"Error processing alert batch: {str(e)}")
            return []
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Acknowledge an alert to stop escalation.
        
        Args:
            alert_id: Alert identifier
            user_id: User acknowledging the alert
            notes: Optional acknowledgment notes
            
        Returns:
            Success status
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alert {alert_id} not found for acknowledgment")
                return False
            
            if alert.status == AlertStatus.ACKNOWLEDGED:
                logger.info(f"Alert {alert_id} already acknowledged")
                return True
            
            # Update alert status
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()
            alert.assigned_to = user_id
            
            # Add acknowledgment metadata
            if "acknowledgments" not in alert.metadata:
                alert.metadata["acknowledgments"] = []
            
            alert.metadata["acknowledgments"].append({
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
            
            # Update cache
            await self._cache_alert(alert)
            
            # Send acknowledgment notifications
            await self._send_acknowledgment_notifications(alert, user_id, notes)
            
            # Stop escalation process
            await self._stop_alert_escalation(alert_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
            return False
    
    async def resolve_alert(
        self,
        alert_id: str,
        user_id: str,
        resolution_notes: str,
        root_cause: Optional[str] = None
    ) -> bool:
        """
        Resolve an alert and update status.
        
        Args:
            alert_id: Alert identifier
            user_id: User resolving the alert
            resolution_notes: Resolution description
            root_cause: Optional root cause analysis
            
        Returns:
            Success status
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alert {alert_id} not found for resolution")
                return False
            
            # Update alert status
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()
            
            # Add resolution metadata
            alert.metadata["resolution"] = {
                "resolved_by": user_id,
                "resolution_notes": resolution_notes,
                "root_cause": root_cause,
                "resolution_time": (
                    alert.resolved_at - alert.created_at
                ).total_seconds()
            }
            
            logger.info(f"Alert {alert_id} resolved by user {user_id}")
            
            # Update cache
            await self._cache_alert(alert)
            
            # Send resolution notifications
            await self._send_resolution_notifications(alert, user_id, resolution_notes)
            
            # Resolve correlated alerts if applicable
            if alert.correlation_id:
                await self._resolve_correlated_alerts(alert.correlation_id, user_id)
            
            # Update metrics
            await self._update_resolution_metrics(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {str(e)}")
            return False
    
    async def suppress_alert(
        self,
        alert_id: str,
        user_id: str,
        suppression_duration: timedelta,
        reason: str
    ) -> bool:
        """
        Suppress an alert for a specified duration.
        
        Args:
            alert_id: Alert identifier
            user_id: User suppressing the alert
            suppression_duration: How long to suppress
            reason: Suppression reason
            
        Returns:
            Success status
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alert {alert_id} not found for suppression")
                return False
            
            # Update alert status
            alert.status = AlertStatus.SUPPRESSED
            alert.updated_at = datetime.utcnow()
            
            # Add suppression metadata
            suppression_until = datetime.utcnow() + suppression_duration
            alert.metadata["suppression"] = {
                "suppressed_by": user_id,
                "reason": reason,
                "suppressed_at": datetime.utcnow().isoformat(),
                "suppression_until": suppression_until.isoformat()
            }
            
            logger.info(f"Alert {alert_id} suppressed until {suppression_until}")
            
            # Schedule unsuppression
            await self._schedule_alert_unsuppression(alert_id, suppression_until)
            
            # Update cache
            await self._cache_alert(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Error suppressing alert {alert_id}: {str(e)}")
            return False
    
    async def get_active_alerts(
        self,
        severity_filter: Optional[List[AlertSeverity]] = None,
        category_filter: Optional[List[AlertCategory]] = None,
        limit: int = 100
    ) -> List[Alert]:
        """
        Get list of active alerts with optional filtering.
        
        Args:
            severity_filter: Filter by severity levels
            category_filter: Filter by categories
            limit: Maximum number of alerts to return
            
        Returns:
            List of filtered active alerts
        """
        try:
            alerts = list(self.active_alerts.values())
            
            # Apply severity filter
            if severity_filter:
                alerts = [a for a in alerts if a.severity in severity_filter]
            
            # Apply category filter
            if category_filter:
                alerts = [a for a in alerts if a.category in category_filter]
            
            # Filter out resolved and closed alerts
            alerts = [
                a for a in alerts 
                if a.status not in [AlertStatus.RESOLVED, AlertStatus.CLOSED]
            ]
            
            # Sort by severity and creation time
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3,
                AlertSeverity.INFO: 4
            }
            
            alerts.sort(
                key=lambda x: (severity_order.get(x.severity, 5), x.created_at),
                reverse=True
            )
            
            return alerts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            return []
    
    async def get_alert_statistics(
        self,
        time_period: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive alert statistics.
        
        Args:
            time_period: Time period for statistics (default: last 24 hours)
            
        Returns:
            Alert statistics and metrics
        """
        try:
            if time_period is None:
                time_period = timedelta(hours=24)
            
            cutoff_time = datetime.utcnow() - time_period
            
            # Filter alerts by time period
            recent_alerts = [
                alert for alert in self.alert_history
                if alert.created_at >= cutoff_time
            ]
            
            # Calculate statistics
            total_alerts = len(recent_alerts)
            
            # Count by severity
            severity_counts = defaultdict(int)
            for alert in recent_alerts:
                severity_counts[alert.severity.value] += 1
            
            # Count by category
            category_counts = defaultdict(int)
            for alert in recent_alerts:
                category_counts[alert.category.value] += 1
            
            # Count by status
            status_counts = defaultdict(int)
            for alert in recent_alerts:
                status_counts[alert.status.value] += 1
            
            # Calculate resolution metrics
            resolved_alerts = [
                a for a in recent_alerts 
                if a.status == AlertStatus.RESOLVED and a.resolved_at
            ]
            
            if resolved_alerts:
                resolution_times = [
                    (a.resolved_at - a.created_at).total_seconds()
                    for a in resolved_alerts
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
                max_resolution_time = max(resolution_times)
                min_resolution_time = min(resolution_times)
            else:
                avg_resolution_time = max_resolution_time = min_resolution_time = 0
            
            # Calculate escalation metrics
            escalated_alerts = [
                a for a in recent_alerts
                if a.escalation_level != EscalationLevel.LEVEL_1
            ]
            escalation_rate = len(escalated_alerts) / total_alerts if total_alerts > 0 else 0
            
            statistics = {
                "time_period": {
                    "start": cutoff_time.isoformat(),
                    "end": datetime.utcnow().isoformat(),
                    "duration_hours": time_period.total_seconds() / 3600
                },
                "total_alerts": total_alerts,
                "active_alerts": len(self.active_alerts),
                "severity_distribution": dict(severity_counts),
                "category_distribution": dict(category_counts),
                "status_distribution": dict(status_counts),
                "resolution_metrics": {
                    "resolved_alerts": len(resolved_alerts),
                    "resolution_rate": len(resolved_alerts) / total_alerts if total_alerts > 0 else 0,
                    "avg_resolution_time_seconds": avg_resolution_time,
                    "max_resolution_time_seconds": max_resolution_time,
                    "min_resolution_time_seconds": min_resolution_time
                },
                "escalation_metrics": {
                    "escalated_alerts": len(escalated_alerts),
                    "escalation_rate": escalation_rate
                },
                "top_sources": await self._get_top_alert_sources(recent_alerts),
                "top_affected_resources": await self._get_top_affected_resources(recent_alerts)
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {str(e)}")
            return {}
    
    async def configure_notification_rule(
        self,
        rule_config: Dict[str, Any]
    ) -> str:
        """
        Configure a new notification rule.
        
        Args:
            rule_config: Rule configuration dictionary
            
        Returns:
            Rule ID
        """
        try:
            rule_id = f"rule_{int(datetime.utcnow().timestamp() * 1000)}"
            
            rule = NotificationRule(
                rule_id=rule_id,
                name=rule_config.get("name"),
                conditions=rule_config.get("conditions", {}),
                channels=[NotificationChannel(ch) for ch in rule_config.get("channels", [])],
                recipients=rule_config.get("recipients", []),
                template=rule_config.get("template", "default"),
                cooldown_period=timedelta(minutes=rule_config.get("cooldown_minutes", 30)),
                escalation_delay=timedelta(minutes=rule_config.get("escalation_delay_minutes", 60)),
                is_active=rule_config.get("is_active", True),
                priority=rule_config.get("priority", 1)
            )
            
            self.notification_rules[rule_id] = rule
            
            logger.info(f"Configured notification rule {rule_id}: {rule.name}")
            
            # Cache rule configuration
            await self._cache_notification_rule(rule)
            
            return rule_id
            
        except Exception as e:
            logger.error(f"Error configuring notification rule: {str(e)}")
            raise
    
    async def configure_escalation_policy(
        self,
        policy_config: Dict[str, Any]
    ) -> str:
        """
        Configure a new escalation policy.
        
        Args:
            policy_config: Policy configuration dictionary
            
        Returns:
            Policy ID
        """
        try:
            policy_id = f"policy_{int(datetime.utcnow().timestamp() * 1000)}"
            
            policy = EscalationPolicy(
                policy_id=policy_id,
                name=policy_config.get("name"),
                conditions=policy_config.get("conditions", {}),
                escalation_steps=policy_config.get("escalation_steps", []),
                auto_escalation_enabled=policy_config.get("auto_escalation_enabled", True),
                escalation_intervals=[
                    timedelta(minutes=interval) 
                    for interval in policy_config.get("escalation_intervals_minutes", [30, 60, 120])
                ],
                max_escalation_level=EscalationLevel(
                    policy_config.get("max_escalation_level", "level_3")
                ),
                is_active=policy_config.get("is_active", True)
            )
            
            self.escalation_policies[policy_id] = policy
            
            logger.info(f"Configured escalation policy {policy_id}: {policy.name}")
            
            # Cache policy configuration
            await self._cache_escalation_policy(policy)
            
            return policy_id
            
        except Exception as e:
            logger.error(f"Error configuring escalation policy: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _initialize_alert_system(self):
        """Initialize alert system components."""
        try:
            # Load existing alerts from cache
            await self._load_cached_alerts()
            
            # Initialize notification channels
            await self._initialize_notification_channels()
            
            # Start background tasks
            asyncio.create_task(self._alert_processor_task())
            asyncio.create_task(self._escalation_monitor_task())
            asyncio.create_task(self._cleanup_task())
            
            logger.info("Alert system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing alert system: {str(e)}")
    
    async def _correlate_alert(
        self,
        title: str,
        description: str,
        category: AlertCategory,
        affected_resources: List[str]
    ) -> Optional[str]:
        """Correlate new alert with existing alerts."""
        try:
            # Simple correlation based on affected resources and category
            for alert in self.active_alerts.values():
                if (alert.category == category and 
                    alert.status in [AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED] and
                    any(resource in alert.affected_resources for resource in affected_resources)):
                    
                    # Found correlation
                    if alert.correlation_id:
                        return alert.correlation_id
                    else:
                        # Create new correlation group
                        correlation_id = f"corr_{int(datetime.utcnow().timestamp())}"
                        alert.correlation_id = correlation_id
                        return correlation_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error correlating alert: {str(e)}")
            return None
    
    async def _generate_alert_tags(
        self,
        title: str,
        description: str,
        category: AlertCategory
    ) -> List[str]:
        """Generate tags for alert categorization."""
        tags = [category.value]
        
        # Add tags based on content
        keywords = ["critical", "urgent", "security", "performance", "error"]
        content = f"{title} {description}".lower()
        
        for keyword in keywords:
            if keyword in content:
                tags.append(keyword)
        
        return list(set(tags))
    
    async def _process_new_alert(self, alert: Alert):
        """Process newly created alert through the pipeline."""
        try:
            # Apply notification rules
            await self._apply_notification_rules(alert)
            
            # Start escalation if applicable
            await self._start_alert_escalation(alert)
            
            # Update metrics
            await self._update_alert_metrics(alert)
            
        except Exception as e:
            logger.error(f"Error processing new alert {alert.alert_id}: {str(e)}")
    
    async def _apply_notification_rules(self, alert: Alert):
        """Apply notification rules to alert."""
        try:
            for rule in self.notification_rules.values():
                if not rule.is_active:
                    continue
                
                # Check if rule conditions match
                if await self._check_rule_conditions(alert, rule.conditions):
                    await self._send_notification(alert, rule)
                    
        except Exception as e:
            logger.error(f"Error applying notification rules: {str(e)}")
    
    async def _check_rule_conditions(self, alert: Alert, conditions: Dict[str, Any]) -> bool:
        """Check if alert matches rule conditions."""
        try:
            # Check severity condition
            if "severity" in conditions:
                if alert.severity.value not in conditions["severity"]:
                    return False
            
            # Check category condition
            if "category" in conditions:
                if alert.category.value not in conditions["category"]:
                    return False
            
            # Check source condition
            if "source" in conditions:
                if alert.source not in conditions["source"]:
                    return False
            
            # Check tags condition
            if "tags" in conditions:
                required_tags = conditions["tags"]
                if not any(tag in alert.tags for tag in required_tags):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rule conditions: {str(e)}")
            return False
    
    async def _send_notification(self, alert: Alert, rule: NotificationRule):
        """Send notification according to rule."""
        try:
            for channel in rule.channels:
                for recipient in rule.recipients:
                    await self._deliver_notification(alert, channel, recipient, rule.template)
                    
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    async def _deliver_notification(
        self,
        alert: Alert,
        channel: NotificationChannel,
        recipient: str,
        template: str
    ):
        """Deliver notification through specified channel."""
        try:
            message = await self._format_notification_message(alert, template)
            
            if channel == NotificationChannel.EMAIL:
                await self._send_email_notification(recipient, alert.title, message)
            elif channel == NotificationChannel.SMS:
                await self._send_sms_notification(recipient, message)
            elif channel == NotificationChannel.PUSH:
                await self._send_push_notification(recipient, alert.title, message)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook_notification(recipient, alert, message)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack_notification(recipient, alert, message)
            elif channel == NotificationChannel.IN_APP:
                await self._send_in_app_notification(recipient, alert, message)
                
            logger.info(f"Notification sent via {channel.value} to {recipient}")
            
        except Exception as e:
            logger.error(f"Error delivering notification via {channel.value}: {str(e)}")
    
    async def _format_notification_message(self, alert: Alert, template: str) -> str:
        """Format notification message using template."""
        try:
            # Basic template formatting
            if template == "default":
                return f"""
Alert: {alert.title}
Severity: {alert.severity.value.upper()}
Category: {alert.category.value}
Description: {alert.description}
Affected Resources: {', '.join(alert.affected_resources)}
Created: {alert.created_at.isoformat()}
Alert ID: {alert.alert_id}
"""
            elif template == "brief":
                return f"{alert.severity.value.upper()}: {alert.title} - {alert.alert_id}"
            else:
                # Use default for unknown templates
                return await self._format_notification_message(alert, "default")
                
        except Exception as e:
            logger.error(f"Error formatting notification message: {str(e)}")
            return f"Alert: {alert.title} (ID: {alert.alert_id})"
    
    # Notification delivery methods (simplified implementations)
    
    async def _send_email_notification(self, recipient: str, subject: str, message: str):
        """Send email notification."""
        logger.info(f"Email notification sent to {recipient}: {subject}")
    
    async def _send_sms_notification(self, recipient: str, message: str):
        """Send SMS notification."""
        logger.info(f"SMS notification sent to {recipient}")
    
    async def _send_push_notification(self, recipient: str, title: str, message: str):
        """Send push notification."""
        logger.info(f"Push notification sent to {recipient}: {title}")
    
    async def _send_webhook_notification(self, webhook_url: str, alert: Alert, message: str):
        """Send webhook notification."""
        logger.info(f"Webhook notification sent to {webhook_url}")
    
    async def _send_slack_notification(self, channel: str, alert: Alert, message: str):
        """Send Slack notification."""
        logger.info(f"Slack notification sent to {channel}")
    
    async def _send_in_app_notification(self, user_id: str, alert: Alert, message: str):
        """Send in-app notification."""
        logger.info(f"In-app notification sent to user {user_id}")
    
    # Escalation methods
    
    async def _start_alert_escalation(self, alert: Alert):
        """Start escalation process for alert."""
        try:
            # Find applicable escalation policy
            policy = await self._find_escalation_policy(alert)
            if policy and policy.auto_escalation_enabled:
                # Schedule escalation
                await self._schedule_escalation(alert, policy)
                
        except Exception as e:
            logger.error(f"Error starting alert escalation: {str(e)}")
    
    async def _find_escalation_policy(self, alert: Alert) -> Optional[EscalationPolicy]:
        """Find applicable escalation policy for alert."""
        try:
            for policy in self.escalation_policies.values():
                if policy.is_active and await self._check_rule_conditions(alert, policy.conditions):
                    return policy
            return None
            
        except Exception as e:
            logger.error(f"Error finding escalation policy: {str(e)}")
            return None
    
    async def _schedule_escalation(self, alert: Alert, policy: EscalationPolicy):
        """Schedule escalation steps."""
        try:
            # This would integrate with a task scheduler
            logger.info(f"Escalation scheduled for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling escalation: {str(e)}")
    
    async def _stop_alert_escalation(self, alert_id: str):
        """Stop escalation process for alert."""
        try:
            # This would cancel scheduled escalation tasks
            logger.info(f"Escalation stopped for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"Error stopping escalation: {str(e)}")
    
    # Background tasks
    
    async def _alert_processor_task(self):
        """Background task for processing alerts."""
        while True:
            try:
                # Process pending alerts
                await asyncio.sleep(30)  # Process every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert processor task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _escalation_monitor_task(self):
        """Background task for monitoring escalations."""
        while True:
            try:
                # Check for alerts that need escalation
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in escalation monitor task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_task(self):
        """Background task for cleanup operations."""
        while True:
            try:
                # Clean up old resolved alerts
                await self._cleanup_old_alerts()
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(3600)
    
    # Additional helper methods (simplified implementations)
    
    async def _cache_alert(self, alert: Alert):
        """Cache alert data."""
        try:
            cache_key = f"alert:{alert.alert_id}"
            await cache_manager.set(cache_key, alert.__dict__, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache alert: {str(e)}")
    
    async def _load_cached_alerts(self):
        """Load alerts from cache."""
        logger.info("Loading cached alerts")
    
    async def _initialize_notification_channels(self):
        """Initialize notification channels."""
        logger.info("Notification channels initialized")
    
    async def _analyze_batch_correlations(self, alerts: List[Alert]):
        """Analyze correlations in batch of alerts."""
        logger.info(f"Analyzing correlations for {len(alerts)} alerts")
    
    async def _send_acknowledgment_notifications(self, alert: Alert, user_id: str, notes: Optional[str]):
        """Send notifications about alert acknowledgment."""
        logger.info(f"Acknowledgment notifications sent for alert {alert.alert_id}")
    
    async def _send_resolution_notifications(self, alert: Alert, user_id: str, resolution_notes: str):
        """Send notifications about alert resolution."""
        logger.info(f"Resolution notifications sent for alert {alert.alert_id}")
    
    async def _resolve_correlated_alerts(self, correlation_id: str, user_id: str):
        """Resolve alerts with the same correlation ID."""
        logger.info(f"Resolving correlated alerts with ID {correlation_id}")
    
    async def _update_resolution_metrics(self, alert: Alert):
        """Update metrics after alert resolution."""
        logger.info(f"Resolution metrics updated for alert {alert.alert_id}")
    
    async def _schedule_alert_unsuppression(self, alert_id: str, unsuppression_time: datetime):
        """Schedule alert to be unsuppressed."""
        logger.info(f"Unsuppression scheduled for alert {alert_id} at {unsuppression_time}")
    
    async def _update_alert_metrics(self, alert: Alert):
        """Update alert metrics."""
        logger.info(f"Metrics updated for new alert {alert.alert_id}")
    
    async def _get_top_alert_sources(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Get top alert sources from list."""
        source_counts = defaultdict(int)
        for alert in alerts:
            source_counts[alert.source] += 1
        
        return [
            {"source": source, "count": count}
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    async def _get_top_affected_resources(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Get top affected resources from list."""
        resource_counts = defaultdict(int)
        for alert in alerts:
            for resource in alert.affected_resources:
                resource_counts[resource] += 1
        
        return [
            {"resource": resource, "count": count}
            for resource, count in sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    async def _cache_notification_rule(self, rule: NotificationRule):
        """Cache notification rule."""
        try:
            cache_key = f"notification_rule:{rule.rule_id}"
            await cache_manager.set(cache_key, rule.__dict__, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache notification rule: {str(e)}")
    
    async def _cache_escalation_policy(self, policy: EscalationPolicy):
        """Cache escalation policy."""
        try:
            cache_key = f"escalation_policy:{policy.policy_id}"
            await cache_manager.set(cache_key, policy.__dict__, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache escalation policy: {str(e)}")
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=30)  # Keep alerts for 30 days
            
            # Remove old alerts from active alerts
            alerts_to_remove = []
            for alert_id, alert in self.active_alerts.items():
                if (alert.status in [AlertStatus.RESOLVED, AlertStatus.CLOSED] and
                    alert.updated_at < cutoff_time):
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
            
            logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
            
        except Exception as e:
            logger.error(f"Error cleaning up old alerts: {str(e)}")
