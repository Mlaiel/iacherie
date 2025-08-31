"""Real-time Alert System - Advanced Monitoring and Notification Engine
Provides real-time alerts and notifications for competitor activities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
from collections import defaultdict

try:
    from core.exceptions import AlertError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AlertError, ValidationError = globals().get('AlertError, ValidationError', Exception)
from ...core.monitoring import EventEmitter
from ...integrations.notification_service import NotificationService
from ...utils.template_engine import TemplateEngine


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of competitor alerts."""
    CONTENT_UPDATE = "content_update"
    PRICING_CHANGE = "pricing_change"
    PRODUCT_LAUNCH = "product_launch"
    MARKETING_CAMPAIGN = "marketing_campaign"
    FUNDING_NEWS = "funding_news"
    STAFF_CHANGE = "staff_change"
    PARTNERSHIP = "partnership"
    PERFORMANCE_CHANGE = "performance_change"
    MARKET_SHARE_SHIFT = "market_share_shift"
    TECHNOLOGY_ADOPTION = "technology_adoption"


@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    name: str
    description: str
    alert_type: AlertType
    conditions: Dict[str, Any]
    severity: AlertSeverity
    enabled: bool
    frequency: str  # immediate, hourly, daily, weekly
    channels: List[str]  # email, slack, webhook, sms
    filters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class Alert:
    """Alert instance."""
    alert_id: str
    rule_id: str
    competitor_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool
    resolved: bool
    actions_taken: List[str]
    assignee: Optional[str]


@dataclass
class AlertMetrics:
    """Alert system metrics."""
    total_alerts: int
    alerts_by_severity: Dict[str, int]
    alerts_by_type: Dict[str, int]
    response_time_avg: float
    resolution_time_avg: float
    acknowledgment_rate: float
    false_positive_rate: float
    period: str


class AlertSystem:
    """
    Advanced real-time alert system for competitor monitoring.
    
    Provides intelligent alerting, notification routing, and alert management
    with support for multiple channels and customizable rules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the alert system."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.event_emitter = EventEmitter()
        self.notification_service = NotificationService(config.get("notifications", {}))
        self.template_engine = TemplateEngine()
        
        # Alert data
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Processing queues
        self.alert_queue = asyncio.Queue()
        self.notification_queue = asyncio.Queue()
        
        # Rate limiting
        self.rate_limits = defaultdict(lambda: {"count": 0, "reset_time": datetime.utcnow()})
        self.max_alerts_per_hour = config.get("max_alerts_per_hour", 100)
        
        # Alert processors
        self.alert_processors: Dict[AlertType, Callable] = {
            AlertType.CONTENT_UPDATE: self._process_content_update,
            AlertType.PRICING_CHANGE: self._process_pricing_change,
            AlertType.PRODUCT_LAUNCH: self._process_product_launch,
            AlertType.MARKETING_CAMPAIGN: self._process_marketing_campaign,
            AlertType.FUNDING_NEWS: self._process_funding_news,
            AlertType.STAFF_CHANGE: self._process_staff_change,
            AlertType.PARTNERSHIP: self._process_partnership,
            AlertType.PERFORMANCE_CHANGE: self._process_performance_change,
            AlertType.MARKET_SHARE_SHIFT: self._process_market_share_shift,
            AlertType.TECHNOLOGY_ADOPTION: self._process_technology_adoption,
        }
        
        # Start background tasks
        asyncio.create_task(self._alert_processing_loop())
        asyncio.create_task(self._notification_processing_loop())
        asyncio.create_task(self._alert_cleanup_loop())
        
        self.logger.info("AlertSystem initialized")
    
    async def create_alert_rule(self, rule_data: Dict[str, Any]) -> AlertRule:
        """Create a new alert rule."""
        try:
            # Validate rule data
            required_fields = ["name", "alert_type", "conditions", "severity"]
            for field in required_fields:
                if field not in rule_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            rule_id = f"rule_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            rule = AlertRule(
                rule_id=rule_id,
                name=rule_data["name"],
                description=rule_data.get("description", ""),
                alert_type=AlertType(rule_data["alert_type"]),
                conditions=rule_data["conditions"],
                severity=AlertSeverity(rule_data["severity"]),
                enabled=rule_data.get("enabled", True),
                frequency=rule_data.get("frequency", "immediate"),
                channels=rule_data.get("channels", ["email"]),
                filters=rule_data.get("filters", {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.alert_rules[rule_id] = rule
            
            self.logger.info(f"Created alert rule: {rule.name} ({rule_id})")
            return rule
            
        except Exception as e:
            self.logger.error(f"Error creating alert rule: {str(e)}")
            raise AlertError(f"Failed to create alert rule: {str(e)}")
    
    async def evaluate_data_for_alerts(self, competitor_id: str, data_type: str, data: Dict[str, Any]):
        """Evaluate incoming data against alert rules."""
        try:
            relevant_rules = [
                rule for rule in self.alert_rules.values()
                if rule.enabled and self._is_rule_relevant(rule, competitor_id, data_type, data)
            ]
            
            for rule in relevant_rules:
                if await self._evaluate_rule_conditions(rule, competitor_id, data):
                    await self._trigger_alert(rule, competitor_id, data)
                    
        except Exception as e:
            self.logger.error(f"Error evaluating data for alerts: {str(e)}")
    
    async def _trigger_alert(self, rule: AlertRule, competitor_id: str, data: Dict[str, Any]):
        """Trigger an alert based on a rule match."""
        try:
            # Check rate limits
            if not self._check_rate_limit(rule.rule_id):
                self.logger.warning(f"Rate limit exceeded for rule {rule.name}")
                return
            
            # Create alert
            alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                competitor_id=competitor_id,
                alert_type=rule.alert_type,
                severity=rule.severity,
                title=await self._generate_alert_title(rule, data),
                message=await self._generate_alert_message(rule, data),
                data=data,
                metadata={
                    "rule_name": rule.name,
                    "trigger_conditions": rule.conditions,
                    "evaluation_time": datetime.utcnow().isoformat()
                },
                timestamp=datetime.utcnow(),
                acknowledged=False,
                resolved=False,
                actions_taken=[],
                assignee=None
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Queue for processing
            await self.alert_queue.put(alert)
            
            # Emit event
            self.event_emitter.emit("alert_triggered", {
                "alert_id": alert_id,
                "rule_id": rule.rule_id,
                "severity": alert.severity.value,
                "competitor_id": competitor_id
            })
            
            self.logger.info(f"Alert triggered: {alert.title} ({alert_id})")
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")
    
    async def _alert_processing_loop(self):
        """Main alert processing loop."""
        while True:
            try:
                # Get alert from queue
                alert = await self.alert_queue.get()
                
                # Process alert based on type
                processor = self.alert_processors.get(alert.alert_type)
                if processor:
                    await processor(alert)
                
                # Schedule notifications based on frequency
                await self._schedule_notification(alert)
                
                # Mark as processed
                self.alert_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error processing alert: {str(e)}")
                await asyncio.sleep(1)
    
    async def _notification_processing_loop(self):
        """Process notification queue."""
        while True:
            try:
                # Get notification from queue
                notification_data = await self.notification_queue.get()
                
                # Send notifications through configured channels
                await self._send_notifications(notification_data)
                
                # Mark as processed
                self.notification_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error processing notification: {str(e)}")
                await asyncio.sleep(1)
    
    async def _send_notifications(self, notification_data: Dict[str, Any]):
        """Send notifications through configured channels."""
        try:
            alert = notification_data["alert"]
            rule = self.alert_rules[alert.rule_id]
            
            for channel in rule.channels:
                try:
                    if channel == "email":
                        await self._send_email_notification(alert, notification_data)
                    elif channel == "slack":
                        await self._send_slack_notification(alert, notification_data)
                    elif channel == "webhook":
                        await self._send_webhook_notification(alert, notification_data)
                    elif channel == "sms":
                        await self._send_sms_notification(alert, notification_data)
                        
                except Exception as e:
                    self.logger.error(f"Error sending {channel} notification: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error sending notifications: {str(e)}")
    
    async def _process_content_update(self, alert: Alert):
        """Process content update alerts."""
        try:
            content_data = alert.data
            
            # Analyze content changes
            analysis = {
                "change_type": content_data.get("change_type", "unknown"),
                "content_size": len(str(content_data.get("new_content", ""))),
                "keywords_added": content_data.get("keywords_added", []),
                "keywords_removed": content_data.get("keywords_removed", []),
                "sentiment_change": content_data.get("sentiment_change", 0.0)
            }
            
            # Add analysis to alert metadata
            alert.metadata["content_analysis"] = analysis
            
            # Generate recommendations
            recommendations = await self._generate_content_recommendations(analysis)
            alert.metadata["recommendations"] = recommendations
            
        except Exception as e:
            self.logger.error(f"Error processing content update alert: {str(e)}")
    
    async def _process_pricing_change(self, alert: Alert):
        """Process pricing change alerts."""
        try:
            pricing_data = alert.data
            
            # Analyze pricing changes
            analysis = {
                "change_percentage": pricing_data.get("change_percentage", 0.0),
                "previous_price": pricing_data.get("previous_price", 0.0),
                "new_price": pricing_data.get("new_price", 0.0),
                "price_tier": pricing_data.get("price_tier", "unknown"),
                "competitive_position": await self._analyze_competitive_pricing(pricing_data)
            }
            
            alert.metadata["pricing_analysis"] = analysis
            
            # Generate pricing recommendations
            recommendations = await self._generate_pricing_recommendations(analysis)
            alert.metadata["recommendations"] = recommendations
            
        except Exception as e:
            self.logger.error(f"Error processing pricing change alert: {str(e)}")
    
    async def _process_product_launch(self, alert: Alert):
        """Process product launch alerts."""
        try:
            product_data = alert.data
            
            # Analyze product launch
            analysis = {
                "product_category": product_data.get("category", "unknown"),
                "target_market": product_data.get("target_market", []),
                "key_features": product_data.get("features", []),
                "pricing_model": product_data.get("pricing_model", "unknown"),
                "competitive_advantage": product_data.get("competitive_advantage", []),
                "threat_level": await self._assess_product_threat_level(product_data)
            }
            
            alert.metadata["product_analysis"] = analysis
            
            # Generate strategic recommendations
            recommendations = await self._generate_product_recommendations(analysis)
            alert.metadata["recommendations"] = recommendations
            
        except Exception as e:
            self.logger.error(f"Error processing product launch alert: {str(e)}")
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, notes: str = "") -> bool:
        """Acknowledge an alert."""
        try:
            if alert_id not in self.active_alerts:
                raise ValidationError(f"Alert not found: {alert_id}")
            
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.assignee = user_id
            alert.actions_taken.append(f"Acknowledged by {user_id} at {datetime.utcnow().isoformat()}")
            
            if notes:
                alert.metadata["acknowledgment_notes"] = notes
            
            # Emit event
            self.event_emitter.emit("alert_acknowledged", {
                "alert_id": alert_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {str(e)}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert."""
        try:
            if alert_id not in self.active_alerts:
                raise ValidationError(f"Alert not found: {alert_id}")
            
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.actions_taken.append(f"Resolved by {user_id} at {datetime.utcnow().isoformat()}")
            
            if resolution_notes:
                alert.metadata["resolution_notes"] = resolution_notes
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            # Emit event
            self.event_emitter.emit("alert_resolved", {
                "alert_id": alert_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Alert resolved: {alert_id} by {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    async def get_alert_metrics(self, period: str = "24h") -> AlertMetrics:
        """Get alert system metrics for specified period."""
        try:
            # Calculate period start
            if period == "1h":
                start_time = datetime.utcnow() - timedelta(hours=1)
            elif period == "24h":
                start_time = datetime.utcnow() - timedelta(days=1)
            elif period == "7d":
                start_time = datetime.utcnow() - timedelta(days=7)
            elif period == "30d":
                start_time = datetime.utcnow() - timedelta(days=30)
            else:
                start_time = datetime.utcnow() - timedelta(days=1)
            
            # Filter alerts for period
            period_alerts = [
                alert for alert in self.alert_history
                if alert.timestamp >= start_time
            ]
            
            # Calculate metrics
            total_alerts = len(period_alerts)
            
            alerts_by_severity = defaultdict(int)
            alerts_by_type = defaultdict(int)
            acknowledged_count = 0
            resolved_count = 0
            response_times = []
            resolution_times = []
            
            for alert in period_alerts:
                alerts_by_severity[alert.severity.value] += 1
                alerts_by_type[alert.alert_type.value] += 1
                
                if alert.acknowledged:
                    acknowledged_count += 1
                
                if alert.resolved:
                    resolved_count += 1
                    # Calculate resolution time (simplified)
                    resolution_times.append(60)  # Placeholder
                
                # Calculate response time (simplified)
                response_times.append(30)  # Placeholder
            
            return AlertMetrics(
                total_alerts=total_alerts,
                alerts_by_severity=dict(alerts_by_severity),
                alerts_by_type=dict(alerts_by_type),
                response_time_avg=sum(response_times) / len(response_times) if response_times else 0,
                resolution_time_avg=sum(resolution_times) / len(resolution_times) if resolution_times else 0,
                acknowledgment_rate=acknowledged_count / total_alerts if total_alerts > 0 else 0,
                false_positive_rate=0.05,  # Placeholder
                period=period
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating alert metrics: {str(e)}")
            return AlertMetrics(0, {}, {}, 0, 0, 0, 0, period)
    
    async def get_active_alerts(self, filters: Dict[str, Any] = None) -> List[Alert]:
        """Get active alerts with optional filters."""
        try:
            alerts = list(self.active_alerts.values())
            
            if filters:
                if "severity" in filters:
                    alerts = [a for a in alerts if a.severity.value == filters["severity"]]
                
                if "competitor_id" in filters:
                    alerts = [a for a in alerts if a.competitor_id == filters["competitor_id"]]
                
                if "alert_type" in filters:
                    alerts = [a for a in alerts if a.alert_type.value == filters["alert_type"]]
                
                if "acknowledged" in filters:
                    alerts = [a for a in alerts if a.acknowledged == filters["acknowledged"]]
            
            # Sort by timestamp (newest first)
            alerts.sort(key=lambda x: x.timestamp, reverse=True)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {str(e)}")
            return []
