"""Alert Management System - Advanced Multi-Channel SEO Alerting
Enterprise-grade alert management with smart routing, escalation workflows,
multi-channel notifications, and intelligent alert grouping.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import smtplib
import aiohttp
from collections import defaultdict, deque
import hashlib
import re

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels with escalation priority"""
    CRITICAL = "critical"  # Immediate response required
    HIGH = "high"         # Response within 1 hour
    MEDIUM = "medium"     # Response within 4 hours
    LOW = "low"          # Response within 24 hours
    INFO = "info"        # No immediate response required


class AlertStatus(Enum):
    """Alert lifecycle status"""
    PENDING = "pending"
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    SUPPRESSED = "suppressed"


class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    PUSH_NOTIFICATION = "push_notification"
    DASHBOARD = "dashboard"
    PAGERDUTY = "pagerduty"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class EscalationAction(Enum):
    """Escalation actions"""
    NOTIFY_MANAGER = "notify_manager"
    INCREASE_SEVERITY = "increase_severity"
    ADD_CHANNELS = "add_channels"
    CREATE_INCIDENT = "create_incident"
    AUTO_REMEDIATE = "auto_remediate"
    SCHEDULE_CALL = "schedule_call"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    severity: AlertSeverity
    metric_name: str
    condition: str  # e.g., "> 100", "< 50", "== 0"
    threshold_value: float
    time_window: int  # seconds
    evaluation_frequency: int  # seconds
    is_active: bool = True
    tags: List[str] = field(default_factory=list)
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    suppression_rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class Alert:
    """Individual alert instance"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    metric_name: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    escalation_level: int = 0
    notification_history: List[Dict[str, Any]] = field(default_factory=list)
    fingerprint: str = ""  # For grouping similar alerts


@dataclass
class NotificationConfig:
    """Notification channel configuration"""
    channel: NotificationChannel
    config: Dict[str, Any]
    is_active: bool = True
    retry_attempts: int = 3
    retry_delay: int = 60  # seconds
    rate_limit: Optional[int] = None  # messages per hour
    template: Optional[str] = None


@dataclass
class EscalationRule:
    """Alert escalation rule"""
    escalation_id: str
    name: str
    trigger_after: int  # seconds
    actions: List[EscalationAction]
    severity_upgrade: Optional[AlertSeverity] = None
    additional_channels: List[NotificationChannel] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class AlertGroup:
    """Grouped alerts for reduced noise"""
    group_id: str
    title: str
    alerts: List[str]  # Alert IDs
    grouping_key: str
    created_at: datetime
    status: AlertStatus
    notification_sent: bool = False
    group_metadata: Dict[str, Any] = field(default_factory=dict)


class AlertManagementSystem:
    """Enterprise Alert Management System
    
    Advanced multi-channel alerting with intelligent routing, escalation workflows,
    alert grouping, fatigue prevention, and comprehensive notification management.
    """
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: Dict[str, Alert] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        self.alert_groups: Dict[str, AlertGroup] = {}
        
        # Alert processing
        self.evaluation_tasks: Dict[str, asyncio.Task] = {}
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.escalation_queue: asyncio.Queue = asyncio.Queue()
        
        # Rate limiting and fatigue prevention
        self.notification_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.suppressed_alerts: Set[str] = set()
        
        # Statistics and monitoring
        self.alert_stats = {
            'total_alerts': 0,
            'alerts_by_severity': defaultdict(int),
            'alerts_by_status': defaultdict(int),
            'notifications_sent': 0,
            'escalations_triggered': 0,
            'alerts_suppressed': 0,
            'avg_resolution_time': 0.0
        }
        
        logger.info("Alert Management System initialized")
    
    async def create_alert_rule(
        self,
        rule_config: AlertRule,
        creator_id: str
    ) -> str:
        """Create new alert rule with validation and activation"""
        try:
            # Validate rule configuration
            await self._validate_alert_rule(rule_config)
            
            # Store alert rule
            rule_config.created_by = creator_id
            self.alert_rules[rule_config.rule_id] = rule_config
            
            # Start evaluation task if rule is active
            if rule_config.is_active:
                await self._start_rule_evaluation(rule_config)
            
            logger.info(f"Alert rule created: {rule_config.rule_id}")
            return rule_config.rule_id
            
        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            raise
    
    async def trigger_alert(
        self,
        rule_id: str,
        metric_name: str,
        current_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Trigger new alert based on rule violation"""
        try:
            if rule_id not in self.alert_rules:
                raise ValueError(f"Alert rule not found: {rule_id}")
            
            rule = self.alert_rules[rule_id]
            
            # Generate alert fingerprint for grouping
            fingerprint = self._generate_alert_fingerprint(rule, metric_name, metadata or {})
            
            # Check if alert should be suppressed
            if await self._should_suppress_alert(rule, fingerprint):
                self.alert_stats['alerts_suppressed'] += 1
                logger.info(f"Alert suppressed: {rule_id}")
                return ""
            
            # Create alert instance
            alert_id = str(uuid.uuid4())
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule_id,
                title=f"{rule.name}: {metric_name}",
                description=f"Metric '{metric_name}' violated threshold: {current_value} {rule.condition}",
                severity=rule.severity,
                status=AlertStatus.TRIGGERED,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=rule.threshold_value,
                triggered_at=datetime.now(),
                tags=rule.tags.copy(),
                metadata=metadata or {},
                fingerprint=fingerprint
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            
            # Update statistics
            self.alert_stats['total_alerts'] += 1
            self.alert_stats['alerts_by_severity'][rule.severity.value] += 1
            self.alert_stats['alerts_by_status'][AlertStatus.TRIGGERED.value] += 1
            
            # Process alert grouping
            await self._process_alert_grouping(alert)
            
            # Send notifications
            await self._queue_alert_notifications(alert)
            
            # Setup escalation if configured
            if rule.escalation_rules:
                await self._setup_alert_escalation(alert)
            
            logger.info(f"Alert triggered: {alert_id}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            raise
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Acknowledge alert and stop escalation"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.assignee = user_id
            
            if notes:
                alert.metadata['acknowledgment_notes'] = notes
            
            # Update statistics
            self.alert_stats['alerts_by_status'][AlertStatus.ACKNOWLEDGED.value] += 1
            self.alert_stats['alerts_by_status'][AlertStatus.TRIGGERED.value] -= 1
            
            # Stop escalation
            await self._stop_alert_escalation(alert_id)
            
            # Send acknowledgment notification
            await self._send_acknowledgment_notification(alert, user_id)
            
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    async def resolve_alert(
        self,
        alert_id: str,
        user_id: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Resolve alert and move to history"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            if resolution_notes:
                alert.metadata['resolution_notes'] = resolution_notes
            
            # Calculate resolution time
            resolution_time = (alert.resolved_at - alert.triggered_at).total_seconds()
            self._update_avg_resolution_time(resolution_time)
            
            # Move to history
            self.alert_history[alert_id] = alert
            del self.active_alerts[alert_id]
            
            # Update statistics
            self.alert_stats['alerts_by_status'][AlertStatus.RESOLVED.value] += 1
            if alert.acknowledged_at:
                self.alert_stats['alerts_by_status'][AlertStatus.ACKNOWLEDGED.value] -= 1
            else:
                self.alert_stats['alerts_by_status'][AlertStatus.TRIGGERED.value] -= 1
            
            # Stop escalation
            await self._stop_alert_escalation(alert_id)
            
            # Send resolution notification
            await self._send_resolution_notification(alert, user_id)
            
            # Update alert group status if applicable
            await self._update_alert_group_status(alert)
            
            logger.info(f"Alert resolved: {alert_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def configure_notification_channel(
        self,
        channel_config: NotificationConfig
    ) -> bool:
        """Configure notification channel with validation"""
        try:
            # Validate channel configuration
            await self._validate_notification_config(channel_config)
            
            # Store configuration
            channel_key = f"{channel_config.channel.value}_{id(channel_config.config)}"
            self.notification_configs[channel_key] = channel_config
            
            # Test channel connectivity
            test_result = await self._test_notification_channel(channel_config)
            if not test_result:
                logger.warning(f"Notification channel test failed: {channel_config.channel.value}")
            
            logger.info(f"Notification channel configured: {channel_config.channel.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure notification channel: {e}")
            return False
    
    async def create_escalation_rule(
        self,
        escalation_config: EscalationRule
    ) -> str:
        """Create escalation rule for alert progression"""
        try:
            # Validate escalation configuration
            await self._validate_escalation_rule(escalation_config)
            
            # Store escalation rule
            self.escalation_rules[escalation_config.escalation_id] = escalation_config
            
            logger.info(f"Escalation rule created: {escalation_config.escalation_id}")
            return escalation_config.escalation_id
            
        except Exception as e:
            logger.error(f"Failed to create escalation rule: {e}")
            raise
    
    async def get_alert_dashboard(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive alert dashboard for user"""
        try:
            # Apply user-specific filters
            filtered_alerts = await self._filter_alerts_for_user(user_id, filters or {})
            
            # Calculate dashboard metrics
            dashboard_data = {
                'overview': {
                    'total_active_alerts': len(self.active_alerts),
                    'critical_alerts': len([a for a in self.active_alerts.values() 
                                          if a.severity == AlertSeverity.CRITICAL]),
                    'unacknowledged_alerts': len([a for a in self.active_alerts.values() 
                                                if a.status == AlertStatus.TRIGGERED]),
                    'assigned_to_user': len([a for a in self.active_alerts.values() 
                                           if a.assignee == user_id])
                },
                'alerts_by_severity': self._get_alerts_by_severity(),
                'alerts_by_status': self._get_alerts_by_status(),
                'recent_alerts': await self._get_recent_alerts(limit=20),
                'trending_metrics': await self._get_trending_alert_metrics(),
                'escalations': await self._get_active_escalations(),
                'alert_groups': list(self.alert_groups.values()),
                'statistics': self.alert_stats.copy(),
                'user_context': {
                    'user_id': user_id,
                    'assigned_alerts': len([a for a in self.active_alerts.values() 
                                          if a.assignee == user_id]),
                    'acknowledged_by_user': len([a for a in self.alert_history.values() 
                                               if a.assignee == user_id])
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get alert dashboard: {e}")
            raise
    
    async def search_alerts(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search alerts with advanced filtering"""
        try:
            all_alerts = {**self.active_alerts, **self.alert_history}
            matching_alerts = []
            
            for alert in all_alerts.values():
                if await self._alert_matches_query(alert, query, filters or {}):
                    matching_alerts.append(self._alert_to_dict(alert))
            
            # Sort by relevance and recency
            matching_alerts.sort(key=lambda x: x['triggered_at'], reverse=True)
            
            return matching_alerts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search alerts: {e}")
            return []
    
    async def export_alert_data(
        self,
        export_format: str = "json",
        time_range: Optional[Tuple[datetime, datetime]] = None,
        include_resolved: bool = True
    ) -> Dict[str, Any]:
        """Export alert data in specified format"""
        try:
            # Collect alerts within time range
            alerts_to_export = []
            
            for alert in self.active_alerts.values():
                if self._alert_in_time_range(alert, time_range):
                    alerts_to_export.append(self._alert_to_dict(alert))
            
            if include_resolved:
                for alert in self.alert_history.values():
                    if self._alert_in_time_range(alert, time_range):
                        alerts_to_export.append(self._alert_to_dict(alert))
            
            export_data = {
                'export_metadata': {
                    'format': export_format,
                    'generated_at': datetime.now().isoformat(),
                    'total_alerts': len(alerts_to_export),
                    'time_range': {
                        'start': time_range[0].isoformat() if time_range else None,
                        'end': time_range[1].isoformat() if time_range else None
                    },
                    'include_resolved': include_resolved
                },
                'alerts': alerts_to_export,
                'statistics': self.alert_stats.copy(),
                'alert_rules': [self._rule_to_dict(rule) for rule in self.alert_rules.values()],
                'escalation_rules': [self._escalation_to_dict(rule) for rule in self.escalation_rules.values()]
            }
            
            # Format based on requested type
            if export_format == "csv":
                return await self._format_alerts_as_csv(export_data)
            elif export_format == "excel":
                return await self._format_alerts_as_excel(export_data)
            elif export_format == "pdf":
                return await self._format_alerts_as_pdf(export_data)
            else:
                return export_data  # JSON format
            
        except Exception as e:
            logger.error(f"Failed to export alert data: {e}")
            raise
    
    # Internal helper methods
    
    async def _validate_alert_rule(self, rule: AlertRule) -> bool:
        """Validate alert rule configuration"""
        if not rule.rule_id or not rule.name:
            raise ValueError("Rule ID and name are required")
        
        if not rule.metric_name:
            raise ValueError("Metric name is required")
        
        # Validate condition format
        if not re.match(r'^[><=!]+\s*\d+(\.\d+)?$', rule.condition.strip()):
            raise ValueError("Invalid condition format")
        
        if rule.evaluation_frequency < 1:
            raise ValueError("Evaluation frequency must be at least 1 second")
        
        return True
    
    async def _start_rule_evaluation(self, rule: AlertRule) -> None:
        """Start continuous evaluation task for alert rule"""
        async def evaluation_loop():
            while rule.is_active:
                try:
                    # Get current metric value
                    current_value = await self._get_metric_value(rule.metric_name)
                    
                    # Evaluate condition
                    if await self._evaluate_alert_condition(rule, current_value):
                        await self.trigger_alert(
                            rule.rule_id,
                            rule.metric_name,
                            current_value
                        )
                    
                    # Wait for next evaluation
                    await asyncio.sleep(rule.evaluation_frequency)
                    
                except Exception as e:
                    logger.error(f"Rule evaluation error for {rule.rule_id}: {e}")
                    await asyncio.sleep(30)  # Wait before retry
        
        # Start evaluation task
        task = asyncio.create_task(evaluation_loop())
        self.evaluation_tasks[rule.rule_id] = task
    
    async def _evaluate_alert_condition(
        self,
        rule: AlertRule,
        current_value: float
    ) -> bool:
        """Evaluate if current value violates alert condition"""
        condition = rule.condition.strip()
        threshold = rule.threshold_value
        
        if condition.startswith('>'):
            return current_value > threshold
        elif condition.startswith('<'):
            return current_value < threshold
        elif condition.startswith('>='):
            return current_value >= threshold
        elif condition.startswith('<='):
            return current_value <= threshold
        elif condition.startswith('=='):
            return abs(current_value - threshold) < 0.001  # Float comparison
        elif condition.startswith('!='):
            return abs(current_value - threshold) >= 0.001
        
        return False
    
    async def _get_metric_value(self, metric_name: str) -> float:
        """Get current value for specified metric"""
        # This would integrate with actual metric collection system
        # For now, return a mock value
        import random
        return random.uniform(50, 150)
    
    def _generate_alert_fingerprint(
        self,
        rule: AlertRule,
        metric_name: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate fingerprint for alert grouping"""
        fingerprint_data = f"{rule.rule_id}:{metric_name}:{rule.severity.value}"
        
        # Include relevant metadata for grouping
        if 'source' in metadata:
            fingerprint_data += f":{metadata['source']}"
        if 'instance' in metadata:
            fingerprint_data += f":{metadata['instance']}"
        
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    async def _should_suppress_alert(
        self,
        rule: AlertRule,
        fingerprint: str
    ) -> bool:
        """Check if alert should be suppressed based on rules"""
        # Check global suppression
        if fingerprint in self.suppressed_alerts:
            return True
        
        # Check rule-specific suppression rules
        for suppression_rule in rule.suppression_rules:
            if await self._matches_suppression_rule(rule, suppression_rule):
                return True
        
        # Check rate limiting
        if await self._is_rate_limited(rule):
            return True
        
        return False
    
    async def _matches_suppression_rule(
        self,
        rule: AlertRule,
        suppression_rule: Dict[str, Any]
    ) -> bool:
        """Check if alert matches suppression rule"""
        # Implementation would check various suppression conditions
        # For now, return False (no suppression)
        return False
    
    async def _is_rate_limited(self, rule: AlertRule) -> bool:
        """Check if alert rule is rate limited"""
        now = datetime.now()
        rate_key = f"rule_{rule.rule_id}"
        
        # Clean old entries (older than 1 hour)
        while (self.notification_rates[rate_key] and 
               (now - self.notification_rates[rate_key][0]).total_seconds() > 3600):
            self.notification_rates[rate_key].popleft()
        
        # Check if we've exceeded rate limit (example: 10 alerts per hour)
        if len(self.notification_rates[rate_key]) >= 10:
            return True
        
        # Add current notification
        self.notification_rates[rate_key].append(now)
        return False
    
    async def _process_alert_grouping(self, alert: Alert) -> None:
        """Process alert for potential grouping"""
        grouping_key = f"{alert.rule_id}:{alert.severity.value}"
        
        # Find existing group or create new one
        existing_group = None
        for group in self.alert_groups.values():
            if (group.grouping_key == grouping_key and 
                group.status != AlertStatus.RESOLVED):
                existing_group = group
                break
        
        if existing_group:
            # Add to existing group
            existing_group.alerts.append(alert.alert_id)
            existing_group.group_metadata['last_updated'] = datetime.now()
        else:
            # Create new group
            group_id = str(uuid.uuid4())
            new_group = AlertGroup(
                group_id=group_id,
                title=f"Alert Group: {alert.title}",
                alerts=[alert.alert_id],
                grouping_key=grouping_key,
                created_at=datetime.now(),
                status=AlertStatus.TRIGGERED,
                group_metadata={
                    'rule_id': alert.rule_id,
                    'severity': alert.severity.value,
                    'first_alert': alert.alert_id
                }
            )
            self.alert_groups[group_id] = new_group
    
    async def _queue_alert_notifications(self, alert: Alert) -> None:
        """Queue alert notifications for processing"""
        rule = self.alert_rules[alert.rule_id]
        
        for channel in rule.notification_channels:
            notification_task = {
                'alert_id': alert.alert_id,
                'channel': channel,
                'attempt': 1,
                'scheduled_at': datetime.now()
            }
            await self.notification_queue.put(notification_task)
    
    async def _setup_alert_escalation(self, alert: Alert) -> None:
        """Setup escalation timeline for alert"""
        rule = self.alert_rules[alert.rule_id]
        
        for escalation_rule_config in rule.escalation_rules:
            escalation_task = {
                'alert_id': alert.alert_id,
                'escalation_config': escalation_rule_config,
                'trigger_at': datetime.now() + timedelta(seconds=escalation_rule_config.get('delay', 3600))
            }
            await self.escalation_queue.put(escalation_task)
    
    async def _stop_alert_escalation(self, alert_id: str) -> None:
        """Stop escalation for resolved/acknowledged alert"""
        # Implementation would remove escalation tasks for this alert
        pass
    
    async def _send_acknowledgment_notification(
        self,
        alert: Alert,
        user_id: str
    ) -> None:
        """Send acknowledgment notification"""
        notification_data = {
            'type': 'acknowledgment',
            'alert_id': alert.alert_id,
            'alert_title': alert.title,
            'acknowledged_by': user_id,
            'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        }
        
        # Send to configured channels
        await self._send_notification_to_channels(
            notification_data,
            [NotificationChannel.DASHBOARD, NotificationChannel.EMAIL]
        )
    
    async def _send_resolution_notification(
        self,
        alert: Alert,
        user_id: str
    ) -> None:
        """Send resolution notification"""
        notification_data = {
            'type': 'resolution',
            'alert_id': alert.alert_id,
            'alert_title': alert.title,
            'resolved_by': user_id,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'resolution_time': (alert.resolved_at - alert.triggered_at).total_seconds() if alert.resolved_at else 0
        }
        
        # Send to configured channels
        await self._send_notification_to_channels(
            notification_data,
            [NotificationChannel.DASHBOARD, NotificationChannel.EMAIL]
        )
    
    async def _send_notification_to_channels(
        self,
        notification_data: Dict[str, Any],
        channels: List[NotificationChannel]
    ) -> None:
        """Send notification to specified channels"""
        for channel in channels:
            try:
                success = await self._send_channel_notification(channel, notification_data)
                if success:
                    self.alert_stats['notifications_sent'] += 1
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.value}: {e}")
    
    async def _send_channel_notification(
        self,
        channel: NotificationChannel,
        data: Dict[str, Any]
    ) -> bool:
        """Send notification via specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(data)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_notification(data)
            elif channel == NotificationChannel.TEAMS:
                return await self._send_teams_notification(data)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(data)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms_notification(data)
            elif channel == NotificationChannel.DASHBOARD:
                return await self._send_dashboard_notification(data)
            else:
                logger.warning(f"Unsupported notification channel: {channel.value}")
                return False
        except Exception as e:
            logger.error(f"Channel notification error ({channel.value}): {e}")
            return False
    
    async def _send_email_notification(self, data: Dict[str, Any]) -> bool:
        """Send email notification"""
        # Implementation would integrate with SMTP or email service
        logger.info(f"Email notification sent: {data.get('alert_title', 'Alert')}")
        return True
    
    async def _send_slack_notification(self, data: Dict[str, Any]) -> bool:
        """Send Slack notification"""
        # Implementation would integrate with Slack API
        logger.info(f"Slack notification sent: {data.get('alert_title', 'Alert')}")
        return True
    
    async def _send_teams_notification(self, data: Dict[str, Any]) -> bool:
        """Send Microsoft Teams notification"""
        # Implementation would integrate with Teams API
        logger.info(f"Teams notification sent: {data.get('alert_title', 'Alert')}")
        return True
    
    async def _send_webhook_notification(self, data: Dict[str, Any]) -> bool:
        """Send webhook notification"""
        # Implementation would send HTTP POST to configured webhook
        logger.info(f"Webhook notification sent: {data.get('alert_title', 'Alert')}")
        return True
    
    async def _send_sms_notification(self, data: Dict[str, Any]) -> bool:
        """Send SMS notification"""
        # Implementation would integrate with SMS service
        logger.info(f"SMS notification sent: {data.get('alert_title', 'Alert')}")
        return True
    
    async def _send_dashboard_notification(self, data: Dict[str, Any]) -> bool:
        """Send dashboard notification"""
        # Implementation would update dashboard notifications
        logger.info(f"Dashboard notification sent: {data.get('alert_title', 'Alert')}")
        return True
    
    async def _update_alert_group_status(self, alert: Alert) -> None:
        """Update alert group status when alert is resolved"""
        for group in self.alert_groups.values():
            if alert.alert_id in group.alerts:
                # Check if all alerts in group are resolved
                all_resolved = all(
                    alert_id in self.alert_history for alert_id in group.alerts
                )
                if all_resolved:
                    group.status = AlertStatus.RESOLVED
                break
    
    def _update_avg_resolution_time(self, resolution_time: float) -> None:
        """Update average resolution time statistic"""
        current_avg = self.alert_stats['avg_resolution_time']
        total_resolved = self.alert_stats['alerts_by_status'].get('resolved', 1)
        
        # Calculate new average
        new_avg = ((current_avg * (total_resolved - 1)) + resolution_time) / total_resolved
        self.alert_stats['avg_resolution_time'] = new_avg
    
    async def _validate_notification_config(self, config: NotificationConfig) -> bool:
        """Validate notification channel configuration"""
        if not config.config:
            raise ValueError("Notification channel configuration is required")
        
        # Channel-specific validation
        if config.channel == NotificationChannel.EMAIL:
            required_fields = ['smtp_server', 'smtp_port', 'username', 'password', 'recipients']
            if not all(field in config.config for field in required_fields):
                raise ValueError("Email configuration missing required fields")
        
        elif config.channel == NotificationChannel.SLACK:
            if 'webhook_url' not in config.config and 'bot_token' not in config.config:
                raise ValueError("Slack configuration requires webhook_url or bot_token")
        
        # Add more channel-specific validations as needed
        
        return True
    
    async def _validate_escalation_rule(self, rule: EscalationRule) -> bool:
        """Validate escalation rule configuration"""
        if not rule.escalation_id or not rule.name:
            raise ValueError("Escalation ID and name are required")
        
        if rule.trigger_after < 0:
            raise ValueError("Trigger delay must be non-negative")
        
        if not rule.actions:
            raise ValueError("At least one escalation action is required")
        
        return True
    
    async def _test_notification_channel(self, config: NotificationConfig) -> bool:
        """Test notification channel connectivity"""
        try:
            test_data = {
                'type': 'test',
                'alert_title': 'Test Notification',
                'message': 'This is a test notification to verify channel configuration.'
            }
            
            return await self._send_channel_notification(config.channel, test_data)
        except Exception as e:
            logger.error(f"Notification channel test failed: {e}")
            return False
    
    async def _filter_alerts_for_user(
        self,
        user_id: str,
        filters: Dict[str, Any]
    ) -> List[Alert]:
        """Filter alerts based on user permissions and filters"""
        all_alerts = list(self.active_alerts.values())
        
        # Apply user-specific filters
        if 'assigned_to_me' in filters and filters['assigned_to_me']:
            all_alerts = [a for a in all_alerts if a.assignee == user_id]
        
        if 'severity' in filters:
            severity_filter = AlertSeverity(filters['severity'])
            all_alerts = [a for a in all_alerts if a.severity == severity_filter]
        
        if 'status' in filters:
            status_filter = AlertStatus(filters['status'])
            all_alerts = [a for a in all_alerts if a.status == status_filter]
        
        return all_alerts
    
    def _get_alerts_by_severity(self) -> Dict[str, int]:
        """Get alert count by severity"""
        counts = {severity.value: 0 for severity in AlertSeverity}
        for alert in self.active_alerts.values():
            counts[alert.severity.value] += 1
        return counts
    
    def _get_alerts_by_status(self) -> Dict[str, int]:
        """Get alert count by status"""
        counts = {status.value: 0 for status in AlertStatus}
        for alert in self.active_alerts.values():
            counts[alert.status.value] += 1
        return counts
    
    async def _get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts sorted by trigger time"""
        all_alerts = list(self.active_alerts.values())
        all_alerts.sort(key=lambda x: x.triggered_at, reverse=True)
        
        return [self._alert_to_dict(alert) for alert in all_alerts[:limit]]
    
    async def _get_trending_alert_metrics(self) -> Dict[str, Any]:
        """Get trending alert metrics and patterns"""
        # Implementation would analyze alert patterns and trends
        return {
            'most_frequent_rules': [],
            'busiest_hours': [],
            'recurring_patterns': []
        }
    
    async def _get_active_escalations(self) -> List[Dict[str, Any]]:
        """Get active escalations"""
        # Implementation would return active escalation information
        return []
    
    async def _alert_matches_query(
        self,
        alert: Alert,
        query: str,
        filters: Dict[str, Any]
    ) -> bool:
        """Check if alert matches search query and filters"""
        # Simple text search in title and description
        query_lower = query.lower()
        if (query_lower in alert.title.lower() or 
            query_lower in alert.description.lower() or
            query_lower in alert.metric_name.lower()):
            return True
        
        # Check tags
        if any(query_lower in tag.lower() for tag in alert.tags):
            return True
        
        return False
    
    def _alert_to_dict(self, alert: Alert) -> Dict[str, Any]:
        """Convert alert to dictionary representation"""
        return {
            'alert_id': alert.alert_id,
            'rule_id': alert.rule_id,
            'title': alert.title,
            'description': alert.description,
            'severity': alert.severity.value,
            'status': alert.status.value,
            'metric_name': alert.metric_name,
            'current_value': alert.current_value,
            'threshold_value': alert.threshold_value,
            'triggered_at': alert.triggered_at.isoformat(),
            'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'assignee': alert.assignee,
            'tags': alert.tags,
            'escalation_level': alert.escalation_level,
            'fingerprint': alert.fingerprint
        }
    
    def _rule_to_dict(self, rule: AlertRule) -> Dict[str, Any]:
        """Convert alert rule to dictionary representation"""
        return {
            'rule_id': rule.rule_id,
            'name': rule.name,
            'description': rule.description,
            'severity': rule.severity.value,
            'metric_name': rule.metric_name,
            'condition': rule.condition,
            'threshold_value': rule.threshold_value,
            'is_active': rule.is_active,
            'created_at': rule.created_at.isoformat(),
            'created_by': rule.created_by
        }
    
    def _escalation_to_dict(self, escalation: EscalationRule) -> Dict[str, Any]:
        """Convert escalation rule to dictionary representation"""
        return {
            'escalation_id': escalation.escalation_id,
            'name': escalation.name,
            'trigger_after': escalation.trigger_after,
            'actions': [action.value for action in escalation.actions],
            'is_active': escalation.is_active
        }
    
    def _alert_in_time_range(
        self,
        alert: Alert,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> bool:
        """Check if alert falls within specified time range"""
        if not time_range:
            return True
        
        start_time, end_time = time_range
        return start_time <= alert.triggered_at <= end_time
    
    async def _format_alerts_as_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format alert data as CSV"""
        # Implementation would convert to CSV format
        return {'format': 'csv', 'data': data}
    
    async def _format_alerts_as_excel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format alert data as Excel"""
        # Implementation would convert to Excel format
        return {'format': 'excel', 'data': data}
    
    async def _format_alerts_as_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format alert data as PDF"""
        # Implementation would convert to PDF format
        return {'format': 'pdf', 'data': data}
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive alert system statistics"""
        return {
            'alert_stats': self.alert_stats.copy(),
            'system_health': {
                'active_rules': len([r for r in self.alert_rules.values() if r.is_active]),
                'total_rules': len(self.alert_rules),
                'active_alerts': len(self.active_alerts),
                'total_alerts_handled': len(self.alert_history),
                'active_escalations': len(self.escalation_rules),
                'notification_channels': len(self.notification_configs),
                'suppressed_alerts': len(self.suppressed_alerts),
                'alert_groups': len(self.alert_groups)
            },
            'performance_metrics': {
                'avg_resolution_time': self.alert_stats['avg_resolution_time'],
                'notifications_per_hour': self.alert_stats['notifications_sent'],
                'escalation_rate': (self.alert_stats['escalations_triggered'] / 
                                   max(self.alert_stats['total_alerts'], 1)) * 100
            }
        }


# Export the main class
__all__ = [
    "AlertManagementSystem", 
    "AlertRule", 
    "Alert", 
    "NotificationConfig", 
    "EscalationRule",
    "AlertSeverity",
    "AlertStatus", 
    "NotificationChannel",
    "EscalationAction"
]