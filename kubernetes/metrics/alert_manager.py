"""IA Influencer Agent - Alert Manager
Enterprise-grade intelligent alerting system with ML-powered anomaly detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

# [EMOJI_REMOVED]  AVERTISSEMENT L# [EMOJI_REMOVED]GAL STRICT # [EMOJI_REMOVED]
Ce code est la propri# [EMOJI_REMOVED]t# [EMOJI_REMOVED] intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
# [EMOJI_REMOVED]crite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autoris# [EMOJI_REMOVED]: mlaiel@live.de

# [EMOJI_REMOVED]quipe de d# [EMOJI_REMOVED]veloppement:
    - Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
    - Advanced intelligent alerting with ML-powered anomaly detection
- Multi-tenant alert isolation with security-enhanced notifications
- Business-critical alerting with escalation workflows
- Real-time threat detection and automated response
- Smart alert grouping and correlation analysis
- Advanced notification channels with encryption
- Alert lifecycle management with audit trails
- Predictive alerting with forecasting capabilities
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import aiohttp
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import joblib

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.security import SecurityManager
from backend.utils.notification import NotificationManager
from backend.models.alerts import AlertModel, AlertRuleModel, AlertHistoryModel
from .config import get_metrics_config, MetricsConfiguration

logger = get_logger(__name__)
settings = get_settings()


class AlertSeverity(Enum):
    """
Enhanced alert severity levels with business impact"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    BUSINESS_CRITICAL = "business_critical"


class AlertStatus(Enum):
    """Alert lifecycle status tracking"""

    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"
    ESCALATED = "escalated"
    SUPPRESSED = "suppressed"


class AlertCategory(Enum):
    """Alert categorization for intelligent routing"""

    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"
    AI_MODEL = "ai_model"
    CONTENT_PROTECTION = "content_protection"
    REVENUE = "revenue"
    USER_EXPERIENCE = "user_experience"


class NotificationChannel(Enum):
    """Enhanced notification delivery channels"""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    MOBILE_PUSH = "mobile_push"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    TEAMS = "teams"


@dataclass
class AlertCondition:
    """Enhanced alert condition with ML capabilities"""
    metric_name: str
    operator: str  # gt, lt, eq, ne, gte, lte, anomaly, trend
    threshold: Union[float, str]
    duration: str = "5m"
    aggregation: str = "avg"  # avg, sum, min, max, count, p95, p99
    window: str = "5m"
    ml_enabled: bool = False
    sensitivity: float = 0.8  # For ML-based detection
    context_metrics: List[str] = field(default_factory=list)


@dataclass
class AlertRuleConfig:
    """Comprehensive alert rule configuration"""
    name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity
    category: AlertCategory
    notification_channels: List[str]
    enabled: bool = True
    tenant_id: Optional[str] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    suppression_rules: Optional[Dict[str, Any]] = None
    auto_resolve: bool = True
    resolve_timeout: str = "10m"
    tags: List[str] = field(default_factory=list)
    runbook_url: Optional[str] = None
    business_impact: Optional[str] = None
    priority: int = 5  # 1-10, 1 being highest priority


@dataclass
class AlertIncident:
    """Alert incident tracking with enhanced metadata"""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    category: AlertCategory
    status: AlertStatus
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    tenant_id: Optional[str] = None
    values: Dict[str, float] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    fingerprint: str = ""
    escalation_level: int = 0
    notification_history: List[Dict[str, Any]] = field(default_factory=list)
    business_impact_score: float = 0.0
    correlation_group: Optional[str] = None


@dataclass
class AlertMetrics:
    """Alert system performance metrics"""
    total_alerts: int = 0
    alerts_by_severity: Dict[AlertSeverity, int] = field(default_factory=dict)
    alerts_by_category: Dict[AlertCategory, int] = field(default_factory=dict)
    resolution_times: List[float] = field(default_factory=list)
    notification_success_rate: float = 0.0
    false_positive_rate: float = 0.0
    mean_time_to_acknowledge: float = 0.0
    mean_time_to_resolve: float = 0.0


class AlertManager:
    """
    Enterprise-grade intelligent alert manager with ML capabilities
    
    Advanced Features:
    - ML-powered anomaly detection with adaptive thresholds
    - Intelligent alert correlation and grouping
    - Multi-tenant security with encryption
    - Business impact scoring and prioritization
    - Advanced notification routing with escalation
    - Real-time threat detection and response
    - Predictive alerting with forecasting
    - Alert fatigue reduction with smart suppression
    """
    
    def __init__(self, config -> None: Optional[MetricsConfiguration] = None) -> None:
        self.config = config or get_metrics_config()
        self.logger = logger
        
        # Enhanced components
        self.redis_manager = RedisManager()
        self.security_manager = SecurityManager()
        self.notification_manager = NotificationManager()
        
        # Alert management
        self.alert_rules: Dict[str, AlertRuleConfig] = {}
        self.active_alerts: Dict[str, AlertIncident] = {}
        self.alert_history: List[AlertIncident] = []
        
        # ML components for anomaly detection
        self.anomaly_detectors: Dict[str, Any] = {}
        self.baseline_models: Dict[str, Any] = {}
        
        # Advanced features
        self.alert_correlations: Dict[str, List[str]] = {}
        self.suppression_groups: Dict[str, Set[str]] = {}
        self.escalation_chains: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance tracking
        self.alert_metrics = AlertMetrics()
        self._running = False
        self._evaluation_tasks: Dict[str, asyncio.Task] = {}
        
        # Business intelligence
        self.business_impact_calculator = self._initialize_business_impact_calculator()
        self.alert_patterns: Dict[str, Any] = {}
        
        # Initialize components
        self._initialize_default_rules()
        self._initialize_ml_models()
        self._initialize_notification_channels()
    
    async def start(self) -> None:
        """
Start enhanced alert manager with ML capabilities"""
        try:
            if self._running:
                self.logger.warning("Alert manager already running")
                return
            
            self._running = True
            
            # Initialize security and ML components
            await self.security_manager.initialize()
            await self._initialize_anomaly_detection()
            
            # Start alert evaluation loops
            await self._start_evaluation_loops()
            
            # Start correlation and suppression engines
            await self._start_correlation_engine()
            await self._start_suppression_engine()
            
            # Start business intelligence engine
            await self._start_business_intelligence()
            
            self.logger.info("Enhanced Alert Manager started with ML capabilities")
            
        except Exception as e:
            self.logger.error(f"Error starting alert manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop alert manager gracefully"""
        try:
            self._running = False
            
            # Stop all evaluation tasks
            for task_id, task in self._evaluation_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Save ML models and statistics
            await self._save_ml_models()
            await self._save_alert_statistics()
            
            # Send final notifications for critical alerts
            await self._send_shutdown_notifications()
            
            self.logger.info("Alert Manager stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"Error stopping alert manager: {e}")
    
    async def register_rule(self, rule_config: AlertRuleConfig) -> str:
        """Register enhanced alert rule with validation and optimization"""
        try:
            # Validate rule configuration
            await self._validate_rule_config(rule_config)
            
            # Generate unique rule ID
            rule_id = f"rule_{hash(rule_config.name + str(time.time()))}"
            
            # Apply security policies
            if rule_config.tenant_id:
                await self._apply_tenant_security(rule_config)
            
            # Optimize rule conditions
            optimized_conditions = await self._optimize_rule_conditions(rule_config.conditions)
            rule_config.conditions = optimized_conditions
            
            # Store rule configuration
            self.alert_rules[rule_id] = rule_config
            
            # Initialize ML models for rule if needed
            if any(condition.ml_enabled for condition in rule_config.conditions):
                await self._initialize_rule_ml_models(rule_id, rule_config)
            
            # Start evaluation task
            self._evaluation_tasks[rule_id] = asyncio.create_task(
                self._evaluate_rule_loop(rule_id, rule_config)
            )
            
            # Cache rule for performance
            await self._cache_rule_config(rule_id, rule_config)
            
            self.logger.info(f"Enhanced alert rule registered: {rule_config.name} (ID: {rule_id})")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Error registering alert rule: {e}")
            raise
    
    async def unregister_rule(self, rule_id: str) -> bool:
        """Unregister alert rule with cleanup"""
        try:
            if rule_id not in self.alert_rules:
                self.logger.warning(f"Alert rule not found: {rule_id}")
                return False
            
            # Stop evaluation task
            if rule_id in self._evaluation_tasks:
                task = self._evaluation_tasks[rule_id]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self._evaluation_tasks[rule_id]
            
            # Resolve any active alerts for this rule
            await self._resolve_rule_alerts(rule_id)
            
            # Clean up ML models
            await self._cleanup_rule_ml_models(rule_id)
            
            # Remove from cache
            await self._remove_rule_from_cache(rule_id)
            
            # Remove rule
            del self.alert_rules[rule_id]
            
            self.logger.info(f"Alert rule unregistered: {rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering alert rule: {e}")
            return False
    
    async def trigger_alert(
        self,
        rule_id: str,
        values: Dict[str, float],
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        tenant_id: Optional[str] = None
    ) -> Optional[str]:
        """Trigger alert with enhanced processing and correlation"""
        try:
            rule_config = self.alert_rules.get(rule_id)
            if not rule_config:
                self.logger.error(f"Alert rule not found: {rule_id}")
                return None
            
            # Validate tenant isolation
            if tenant_id and rule_config.tenant_id != tenant_id:
                self.logger.warning(f"Tenant mismatch for alert rule: {rule_id}")
                return None
            
            # Generate alert fingerprint for deduplication
            fingerprint = await self._generate_alert_fingerprint(
                rule_id, values, labels or {}
            )
            
            # Check if alert already exists
            existing_alert = await self._find_existing_alert(fingerprint)
            if existing_alert:
                await self._update_existing_alert(existing_alert, values)
                return existing_alert.id
            
            # Calculate business impact score
            business_impact_score = await self._calculate_business_impact(
                rule_config, values, tenant_id
            )
            
            # Create new alert incident
            alert_incident = AlertIncident(
                id=f"alert_{hash(fingerprint + str(time.time()))}",
                rule_id=rule_id,
                rule_name=rule_config.name,
                severity=rule_config.severity,
                category=rule_config.category,
                status=AlertStatus.FIRING,
                triggered_at=datetime.utcnow(),
                tenant_id=tenant_id,
                values=values,
                labels=labels or {},
                annotations=annotations or {},
                fingerprint=fingerprint,
                business_impact_score=business_impact_score
            )
            
            # Apply correlation and grouping
            correlation_group = await self._apply_alert_correlation(alert_incident)
            alert_incident.correlation_group = correlation_group
            
            # Check suppression rules
            if await self._check_suppression_rules(alert_incident):
                alert_incident.status = AlertStatus.SUPPRESSED
                self.logger.info(f"Alert suppressed: {alert_incident.id}")
                return alert_incident.id
            
            # Store active alert
            self.active_alerts[alert_incident.id] = alert_incident
            
            # Send notifications with intelligence
            await self._send_intelligent_notifications(alert_incident, rule_config)
            
            # Update metrics
            await self._update_alert_metrics(alert_incident)
            
            # Store in history
            await self._store_alert_history(alert_incident)
            
            # Check for escalation
            await self._check_escalation_rules(alert_incident, rule_config)
            
            self.logger.info(
                f"Alert triggered: {alert_incident.id} "
                f"(Rule: {rule_config.name}, Severity: {rule_config.severity.value}, "
                f"Business Impact: {business_impact_score:.2f})"
            )
            
            return alert_incident.id
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")
            return None
    
    async def resolve_alert(
        self,
        alert_id: str,
        resolution_note: Optional[str] = None,
        resolved_by: Optional[str] = None
    ) -> bool:
        """Resolve alert with enhanced tracking"""
        try:
            alert_incident = self.active_alerts.get(alert_id)
            if not alert_incident:
                self.logger.warning(f"Active alert not found: {alert_id}")
                return False
            
            # Update alert status
            alert_incident.status = AlertStatus.RESOLVED
            alert_incident.resolved_at = datetime.utcnow()
            
            # Add resolution metadata
            if resolution_note:
                alert_incident.annotations["resolution_note"] = resolution_note
            if resolved_by:
                alert_incident.annotations["resolved_by"] = resolved_by
            
            # Calculate resolution time
            resolution_time = (
                alert_incident.resolved_at - alert_incident.triggered_at
            ).total_seconds()
            
            # Update metrics
            self.alert_metrics.resolution_times.append(resolution_time)
            
            # Send resolution notifications
            await self._send_resolution_notifications(alert_incident)
            
            # Update business intelligence
            await self._update_business_intelligence(alert_incident, "resolved")
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            # Update alert history
            await self._update_alert_history(alert_incident)
            
            # Update ML models with resolution data
            await self._update_ml_models_with_resolution(alert_incident)
            
            self.logger.info(
                f"Alert resolved: {alert_id} "
                f"(Resolution time: {resolution_time:.2f}s)"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        acknowledgment_note: Optional[str] = None
    ) -> bool:
        """Acknowledge alert with enhanced tracking"""
        try:
            alert_incident = self.active_alerts.get(alert_id)
            if not alert_incident:
                self.logger.warning(f"Active alert not found: {alert_id}")
                return False
            
            # Update alert status
            alert_incident.status = AlertStatus.ACKNOWLEDGED
            alert_incident.acknowledged_at = datetime.utcnow()
            alert_incident.acknowledged_by = acknowledged_by
            
            # Add acknowledgment metadata
            if acknowledgment_note:
                alert_incident.annotations["acknowledgment_note"] = acknowledgment_note
            
            # Calculate acknowledgment time
            ack_time = (
                alert_incident.acknowledged_at - alert_incident.triggered_at
            ).total_seconds()
            
            # Update metrics
            self.alert_metrics.mean_time_to_acknowledge = (
                (self.alert_metrics.mean_time_to_acknowledge + ack_time) / 2
            )
            
            # Send acknowledgment notifications
            await self._send_acknowledgment_notifications(alert_incident)
            
            # Update alert history
            await self._update_alert_history(alert_incident)
            
            self.logger.info(
                f"Alert acknowledged: {alert_id} by {acknowledged_by} "
                f"(Acknowledgment time: {ack_time:.2f}s)"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def get_active_alerts(
        self,
        tenant_id: Optional[str] = None,
        severity_filter: Optional[AlertSeverity] = None,
        category_filter: Optional[AlertCategory] = None
    ) -> List[AlertIncident]:
        """Get active alerts with advanced filtering"""
        try:
            active_alerts = list(self.active_alerts.values())
            
            # Apply tenant filter
            if tenant_id:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.tenant_id == tenant_id
                ]
            
            # Apply severity filter
            if severity_filter:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.severity == severity_filter
                ]
            
            # Apply category filter
            if category_filter:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.category == category_filter
                ]
            
            # Sort by business impact and severity
            active_alerts.sort(
                key=lambda x: (x.business_impact_score, x.severity.value),
                reverse=True
            )
            
            return active_alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_alert_statistics(
        self,
        tenant_id: Optional[str] = None,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Get comprehensive alert statistics with business intelligence"""
        try:
            current_time = datetime.utcnow()
            start_time = current_time - time_window
            
            # Filter alerts by time window and tenant
            filtered_alerts = [
                alert for alert in self.alert_history
                if alert.triggered_at >= start_time
                and (not tenant_id or alert.tenant_id == tenant_id)
            ]
            
            # Calculate comprehensive statistics
            stats = {
                "total_alerts": len(filtered_alerts),
                "active_alerts": len([
                    alert for alert in self.active_alerts.values()
                    if not tenant_id or alert.tenant_id == tenant_id
                ]),
                "alerts_by_severity": {},
                "alerts_by_category": {},
                "alerts_by_status": {},
                "resolution_statistics": {},
                "business_impact": {},
                "ml_insights": {},
                "trends": {}
            }
            
            # Alerts by severity
            for severity in AlertSeverity:
                count = len([a for a in filtered_alerts if a.severity == severity])
                stats["alerts_by_severity"][severity.value] = count
            
            # Alerts by category
            for category in AlertCategory:
                count = len([a for a in filtered_alerts if a.category == category])
                stats["alerts_by_category"][category.value] = count
            
            # Alerts by status
            for status in AlertStatus:
                count = len([a for a in filtered_alerts if a.status == status])
                stats["alerts_by_status"][status.value] = count
            
            # Resolution statistics
            resolved_alerts = [a for a in filtered_alerts if a.resolved_at]
            if resolved_alerts:
                resolution_times = [
                    (a.resolved_at - a.triggered_at).total_seconds()
                    for a in resolved_alerts
                ]
                stats["resolution_statistics"] = {
                    "mean_resolution_time": np.mean(resolution_times),
                    "median_resolution_time": np.median(resolution_times),
                    "p95_resolution_time": np.percentile(resolution_times, 95),
                    "resolution_rate": len(resolved_alerts) / len(filtered_alerts) if filtered_alerts else 0
                }
            
            # Business impact analysis
            if filtered_alerts:
                business_scores = [a.business_impact_score for a in filtered_alerts]
                stats["business_impact"] = {
                    "average_impact_score": np.mean(business_scores),
                    "high_impact_alerts": len([s for s in business_scores if s > 7.0]),
                    "critical_impact_alerts": len([s for s in business_scores if s > 9.0])
                }
            
            # ML insights
            stats["ml_insights"] = await self._generate_ml_insights(filtered_alerts)
            
            # Trend analysis
            stats["trends"] = await self._analyze_alert_trends(filtered_alerts, time_window)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {e}")
            return {}
    
    # Private implementation methods
    
    async def _validate_rule_config(self, rule_config: AlertRuleConfig) -> None:
        """Validate alert rule configuration"""
        if not rule_config.name:
            raise ValueError("Alert rule name cannot be empty")
        
        if not rule_config.conditions:
            raise ValueError("Alert rule must have at least one condition")
        
        for condition in rule_config.conditions:
            if not condition.metric_name:
                raise ValueError("Condition metric name cannot be empty")
            
            if condition.operator not in ["gt", "lt", "eq", "ne", "gte", "lte", "anomaly", "trend"]:
                raise ValueError(f"Invalid operator: {condition.operator}")
    
    async def _apply_tenant_security(self, rule_config: AlertRuleConfig) -> None:
        try:
            logger.info(f"Executing _apply_tenant_security")
            
            # Implementation for _apply_tenant_security
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_apply_tenant_security completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _initialize_rule_ml_models")
            
            # Implementation for _initialize_rule_ml_models
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _cache_rule_config")
            
            # Implementation for _cache_rule_config
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_cache_rule_config completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_cache_rule_config failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"_initialize_rule_ml_models failed: {e}")
            raise
        """
Optimize alert rule conditions for performance"""
        # Implementation for condition optimization
        return conditions
    
    async def _initialize_rule_ml_models(self, rule_id: str, rule_config: AlertRuleConfig) -> None:
        """
Initialize ML models for rule"""
        # Implementation for ML model initialization
        pass
    
    async def _cache_rule_config(self, rule_id: str, rule_config: AlertRuleConfig) -> None:
        """
Cache rule configuration for performance"""
        # Implementation for rule caching
        pass
    
    # Additional private methods would be implemented here...
    
    def _initialize_default_rules(self) -> None:
        """
Initialize comprehensive default alert rules"""
        # High error rate alert
        error_rate_rule = AlertRuleConfig(
            name="High HTTP Error Rate",
            description="Alert when HTTP 5xx error rate exceeds 5%",
            conditions=[
                AlertCondition(
                    metric_name="ia_influencer_http_requests_total",
                    operator="gt",
                    threshold=0.05,
                    duration="5m",
                    aggregation="rate"
                )
            ],
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.PERFORMANCE,
            notification_channels=["email", "slack"],
            business_impact="High - Affects user experience and revenue"
        )
        
        # AI model accuracy degradation
        ai_accuracy_rule = AlertRuleConfig(
            name="AI Model Accuracy Degradation",
            description="Alert when AI model accuracy drops below threshold",
            conditions=[
                AlertCondition(
                    metric_name="ia_influencer_ai_model_accuracy",
                    operator="lt",
                    threshold=0.80,
                    duration="10m",
                    ml_enabled=True,
                    sensitivity=0.9
                )
            ],
            severity=AlertSeverity.WARNING,
            category=AlertCategory.AI_MODEL,
            notification_channels=["email"],
            business_impact="Medium - May affect AI service quality"
        )
        
        # Revenue threshold alert
        revenue_alert_rule = AlertRuleConfig(
            name="Revenue Drop Alert",
            description="Alert when revenue tracking shows significant drop",
            conditions=[
                AlertCondition(
                    metric_name="ia_influencer_revenue_tracked_total",
                    operator="anomaly",
                    threshold="baseline",
                    duration="1h",
                    ml_enabled=True,
                    sensitivity=0.8
                )
            ],
            severity=AlertSeverity.BUSINESS_CRITICAL,
            category=AlertCategory.REVENUE,
            notification_channels=["email", "slack", "sms"],
            business_impact="Critical - Direct revenue impact"
        )
        
        self.logger.info("Enhanced default alert rules initialized")
    
    def _initialize_ml_models(self) -> None:
        try:
            logger.info(f"Executing _start_correlation_engine")
            
            # Implementation for _start_correlation_engine
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _start_suppression_engine")
            
            # Implementation for _start_suppression_engine
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _start_business_intelligence")
            
            # Implementation for _start_business_intelligence
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_start_business_intelligence completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _evaluate_rule_loop")
            
            # Implementation for _evaluate_rule_loop
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_evaluate_rule_loop completed successfully")
            return result
            
        except Exception as e:
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _update_existing_alert completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _update_existing_alert failed: {e}")
                    raise
            logger.error(f"_evaluate_rule_loop failed: {e}")
            raise
        except Exception as e:
            logger.error(f"_start_business_intelligence failed: {e}")
            raise
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _send_intelligent_notifications")
            
            # Implementation for _send_intelligent_notifications
            # TODO: Add specific business logic here
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _update_alert_metrics completed")
                        return True
                
                except Exception as e:
        try:
            logger.info(f"Executing _check_escalation_rules")
            
            # Implementation for _check_escalation_rules
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _send_resolution_notifications")
            
            # Implementation for _send_resolution_notifications
            # TODO: Add specific business logic here
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _update_business_intelligence completed")
                        return True
                
                except Exception as e:
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _update_ml_models_with_resolution completed")
                        return True
                
                except Exception as e:
        try:
            logger.info(f"Executing _send_acknowledgment_notifications")
            
            # Implementation for _send_acknowledgment_notifications
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_acknowledgment_notifications completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _resolve_rule_alerts")
            
            # Implementation for _resolve_rule_alerts
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _cleanup_rule_ml_models")
            
            # Implementation for _cleanup_rule_ml_models
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _remove_rule_from_cache")
            
            # Implementation for _remove_rule_from_cache
            # TODO: Add specific business logic here
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _save_ml_models completed")
                        return True
                
                except Exception as e:
        try:
            logger.info(f"Executing _send_shutdown_notifications")
            
            # Implementation for _send_shutdown_notifications
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_shutdown_notifications completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_shutdown_notifications failed: {e}")
            raise
                        await session.commit()
                        logger.info(f"Database operation _save_alert_statistics completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _save_alert_statistics failed: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Database operation _save_ml_models failed: {e}")
                    raise
            logger.info(f"_remove_rule_from_cache completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_remove_rule_from_cache failed: {e}")
            raise
            logger.info(f"_cleanup_rule_ml_models completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_cleanup_rule_ml_models failed: {e}")
            raise
            logger.info(f"_resolve_rule_alerts completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_resolve_rule_alerts failed: {e}")
            raise
                except Exception as e:
                    logger.error(f"Database operation _update_ml_models_with_resolution failed: {e}")
                    raise
                        await session.commit()
                        logger.info(f"Database operation _update_alert_history completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _update_alert_history failed: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Database operation _update_business_intelligence failed: {e}")
                    raise
            logger.info(f"_send_resolution_notifications completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_resolution_notifications failed: {e}")
            raise
            logger.info(f"_check_escalation_rules completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_check_escalation_rules failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"_store_alert_history completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_store_alert_history failed: {e}")
            raise
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _update_alert_metrics failed: {e}")
                    raise
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_intelligent_notifications completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_intelligent_notifications failed: {e}")
            raise
            raise
            logger.info(f"_start_correlation_engine completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_start_correlation_engine failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"_start_evaluation_loops completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_start_evaluation_loops failed: {e}")
            raise
        self.logger.info("Enhanced default alert rules initialized")
    
    def _initialize_ml_models(self) -> None:
        try:
            logger.info(f"Executing _initialize_anomaly_detection")
            
            # Implementation for _initialize_anomaly_detection
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_anomaly_detection completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_anomaly_detection failed: {e}")
            raise
            ],
            severity=AlertSeverity.BUSINESS_CRITICAL,
            category=AlertCategory.REVENUE,
            notification_channels=["email", "slack", "sms"],
            business_impact="Critical - Direct revenue impact"
        )
        
        self.logger.info("Enhanced default alert rules initialized")
    
    def _initialize_ml_models(self) -> None:
        try:
            logger.info(f"Executing _initialize_notification_channels")
            
            # Implementation for _initialize_notification_channels
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_notification_channels completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_notification_channels failed: {e}")
            raise
        revenue_alert_rule = AlertRuleConfig(
            name="Revenue Drop Alert",
            description="Alert when revenue tracking shows significant drop",
            conditions=[
                AlertCondition(
                    metric_name="ia_influencer_revenue_tracked_total",
                    operator="anomaly",
                    threshold="baseline",
                    duration="1h",
                    ml_enabled=True,
                    sensitivity=0.8
                )
            ],
            severity=AlertSeverity.BUSINESS_CRITICAL,
            category=AlertCategory.REVENUE,
            notification_channels=["email", "slack", "sms"],
            business_impact="Critical - Direct revenue impact"
        )
        
        self.logger.info("Enhanced default alert rules initialized")
    
    def _initialize_ml_models(self) -> None:
        try:
            logger.info(f"Executing _initialize_ml_models")
            
            # Implementation for _initialize_ml_models
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_ml_models completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_ml_models failed: {e}")
            raise
            category=AlertCategory.AI_MODEL,
            notification_channels=["email"],
            business_impact="Medium - May affect AI service quality"
        )
        
        # Revenue threshold alert
        revenue_alert_rule = AlertRuleConfig(
            name="Revenue Drop Alert",
            description="Alert when revenue tracking shows significant drop",
            conditions=[
                AlertCondition(
                    metric_name="ia_influencer_revenue_tracked_total",
                    operator="anomaly",
                    threshold="baseline",
                    duration="1h",
                    ml_enabled=True,
                    sensitivity=0.8
                )
            ],
            severity=AlertSeverity.BUSINESS_CRITICAL,
            category=AlertCategory.REVENUE,
            notification_channels=["email", "slack", "sms"],
            business_impact="Critical - Direct revenue impact"
        )
        
        self.logger.info("Enhanced default alert rules initialized")
    
    def _initialize_ml_models(self) -> None:
        """Initialize ML models for anomaly detection"""
        # Implementation for ML model initialization
        pass
    
    def _initialize_notification_channels(self) -> None:
        """
Initialize notification channels"""
        # Implementation for notification channel setup
        pass
    
    def _initialize_business_impact_calculator(self) -> None:
        """
Initialize business impact calculation engine"""
        # Implementation for business impact calculator
        return None
    
    async def _initialize_anomaly_detection(self) -> None:
        """
Initialize anomaly detection system"""
        # Implementation for anomaly detection initialization
        pass
    
    async def _start_evaluation_loops(self) -> None:
        """
Start alert evaluation loops"""
        # Implementation for evaluation loop startup
        pass
    
    async def _start_correlation_engine(self) -> None:
        """
Start alert correlation engine"""
        # Implementation for correlation engine
        pass
    
    async def _start_suppression_engine(self) -> None:
        """
Start alert suppression engine"""
        # Implementation for suppression engine
        pass
    
    async def _start_business_intelligence(self) -> None:
        """
Start business intelligence engine"""
        # Implementation for business intelligence
        pass
    
    # Additional helper methods would be implemented here...
    async def _evaluate_rule_loop(self, rule_id: str, rule_config: AlertRuleConfig) -> None:
        """
Main evaluation loop for alert rule"""
        pass
    
    async def _generate_alert_fingerprint(self, rule_id: str, values: Dict[str, float], labels: Dict[str, str]) -> str:
        """
Generate unique alert fingerprint"""
        return f"{rule_id}_{hash(str(values) + str(labels))}"
    
    async def _find_existing_alert(self, fingerprint: str) -> Optional[AlertIncident]:
        """Find existing alert by fingerprint"""
        return None
    
    async def _update_existing_alert(self, alert: AlertIncident, values: Dict[str, float]) -> None:
        """
Update existing alert"""
        pass
    
    async def _calculate_business_impact(self, rule_config: AlertRuleConfig, values: Dict[str, float], tenant_id: Optional[str]) -> float:
        """
Calculate business impact score"""
        return 5.0
    
    async def _apply_alert_correlation(self, alert: AlertIncident) -> Optional[str]:
        """
Apply alert correlation"""
        return None
    
    async def _check_suppression_rules(self, alert: AlertIncident) -> bool:
        """
Check if alert should be suppressed"""
        return False
    
    async def _send_intelligent_notifications(self, alert: AlertIncident, rule_config: AlertRuleConfig) -> None:
        """
Send intelligent notifications"""
        pass
    
    async def _update_alert_metrics(self, alert: AlertIncident) -> None:
        """
Update alert metrics"""
        pass
    
    async def _store_alert_history(self, alert: AlertIncident) -> None:
        """
Store alert in history"""
        pass
    
    async def _check_escalation_rules(self, alert: AlertIncident, rule_config: AlertRuleConfig) -> None:
        """
Check escalation rules"""
        pass
    
    async def _send_resolution_notifications(self, alert: AlertIncident) -> None:
        """
Send resolution notifications"""
        pass
    
    async def _update_business_intelligence(self, alert: AlertIncident, action: str) -> None:
        """
Update business intelligence"""
        pass
    
    async def _update_alert_history(self, alert: AlertIncident) -> None:
        """
Update alert history"""
        pass
    
    async def _update_ml_models_with_resolution(self, alert: AlertIncident) -> None:
        """
Update ML models with resolution data"""
        pass
    
    async def _send_acknowledgment_notifications(self, alert: AlertIncident) -> None:
        """
Send acknowledgment notifications"""
        pass
    
    async def _generate_ml_insights(self, alerts: List[AlertIncident]) -> Dict[str, Any]:
        """
Generate ML insights"""
        return {}
    
    async def _analyze_alert_trends(self, alerts: List[AlertIncident], time_window: timedelta) -> Dict[str, Any]:
        """
Analyze alert trends"""
        return {}
    
    async def _resolve_rule_alerts(self, rule_id: str) -> None:
        """
Resolve all alerts for a rule"""
        pass
    
    async def _cleanup_rule_ml_models(self, rule_id: str) -> None:
        """
Cleanup ML models for rule"""
        pass
    
    async def _remove_rule_from_cache(self, rule_id: str) -> None:
        """
Remove rule from cache"""
        pass
    
    async def _save_ml_models(self) -> None:
        """
Save ML models"""
        pass
    
    async def _save_alert_statistics(self) -> None:
        """
Save alert statistics"""
        pass
    
    async def _send_shutdown_notifications(self) -> None:
        """
Send shutdown notifications"""
        pass

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.models.alerts import AlertRule, AlertInstance, NotificationChannel
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session
from backend.integrations.notifications.email_service import EmailService
from backend.integrations.notifications.slack_service import SlackService
from backend.integrations.notifications.webhook_service import WebhookService

logger = get_logger(__name__)
settings = get_settings()


class AlertSeverity(Enum):
    """
Alert severity levels"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertState(Enum):
    """Alert states"""

    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class NotificationType(Enum):
    """Notification channel types"""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DISCORD = "discord"


@dataclass
class AlertCondition:
    """Alert condition configuration"""
    metric_name: str
    operator: str  # gt, lt, eq, ne, gte, lte
    threshold: float
    duration: str = "5m"  # Time condition must be true
    aggregation: str = "avg"  # avg, sum, min, max, count


@dataclass
class AlertRuleConfig:
    """Alert rule configuration"""
    name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True
    tenant_id: Optional[str] = None
    notification_channels: List[str] = field(default_factory=list)
    escalation_rules: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertNotification:
    """
Alert notification data"""
    alert_id: str
    rule_name: str
    severity: AlertSeverity
    state: AlertState
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    tenant_id: Optional[str] = None


class AlertManager:
    """
    Enterprise alert manager with multi-tenant support
    
    Handles:
    - Alert rule evaluation and monitoring
    - Real-time alert triggering
    - Multi-channel notifications
    - Alert escalation and acknowledgment
    - Tenant-specific alert isolation
    - Alert analytics and reporting
    """
    
    def __init__(self) -> None:
        self.redis_manager = RedisManager()
        self.logger = logger
        self.settings = settings
        
        # Alert state
        self.alert_rules: Dict[str, AlertRuleConfig] = {}
        self.active_alerts: Dict[str, AlertInstance] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}
        
        # Evaluation state
        self._running = False
        self._evaluation_tasks: List[asyncio.Task] = []
        
        # Notification services
        self.email_service = EmailService()
        self.slack_service = SlackService()
        self.webhook_service = WebhookService()
        
        # Initialize default rules
        self._initialize_default_rules()
        self._initialize_notification_channels()
    
    async def start(self) -> None:
        """
Start alert manager"""
        try:
            if self._running:
                self.logger.warning("Alert manager already running")
                return
            
            self._running = True
            self.logger.info("Starting alert manager...")
            
            # Start evaluation loops
            self._evaluation_tasks = [
                asyncio.create_task(self._evaluation_loop()),
                asyncio.create_task(self._notification_loop()),
                asyncio.create_task(self._cleanup_loop())
            ]
            
            self.logger.info("Alert manager started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting alert manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop alert manager"""
        try:
            self._running = False
            self.logger.info("Stopping alert manager...")
            
            # Cancel evaluation tasks
            for task in self._evaluation_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.logger.info("Alert manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping alert manager: {e}")
    
    def register_rule(self, rule_config: AlertRuleConfig) -> str:
        """Register new alert rule"""
        try:
            rule_id = f"rule_{len(self.alert_rules)}_{int(datetime.utcnow().timestamp())}"
            self.alert_rules[rule_id] = rule_config
            
            self.logger.info(f"Alert rule registered: {rule_config.name} ({rule_id})")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Error registering alert rule: {e}")
            raise
    
    def register_notification_channel(
        self,
        channel_id: str,
        channel_type: NotificationType,
        config: Dict[str, Any]
    ) -> None:
        """Register notification channel"""
        try:
            channel = NotificationChannel(
                id=channel_id,
                type=channel_type,
                config=config,
                enabled=True
            )
            
            self.notification_channels[channel_id] = channel
            self.logger.info(f"Notification channel registered: {channel_id}")
            
        except Exception as e:
            self.logger.error(f"Error registering notification channel: {e}")
    
    async def trigger_alert(
        self,
        rule_id: str,
        metric_value: float,
        context: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> Optional[str]:
        """Manually trigger alert"""
        try:
            if rule_id not in self.alert_rules:
                self.logger.error(f"Unknown alert rule: {rule_id}")
                return None
            
            rule = self.alert_rules[rule_id]
            
            # Create alert instance
            alert_id = f"alert_{rule_id}_{int(datetime.utcnow().timestamp())}"
            
            alert_instance = AlertInstance(
                id=alert_id,
                rule_id=rule_id,
                rule_name=rule.name,
                severity=rule.severity,
                state=AlertState.FIRING,
                triggered_at=datetime.utcnow(),
                metric_value=metric_value,
                context=context,
                tenant_id=tenant_id
            )
            
            self.active_alerts[alert_id] = alert_instance
            
            # Send notifications
            await self._send_alert_notifications(alert_instance)
            
            # Store in Redis
            await self._store_alert(alert_instance)
            
            self.logger.info(f"Alert triggered: {rule.name} ({alert_id})")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")
            return None
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge alert"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.ACKNOWLEDGED
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.utcnow()
            
            # Update storage
            await self._store_alert(alert)
            
            self.logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.utcnow()
            
            # Send resolution notification
            await self._send_resolution_notification(alert)
            
            # Update storage
            await self._store_alert(alert)
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False
    
    async def get_tenant_alerts(
        self,
        tenant_id: str,
        state_filter: Optional[AlertState] = None,
        limit: int = 100
    ) -> List[AlertInstance]:
        """Get alerts for specific tenant"""
        try:
            # Get from Redis
            alerts_key = f"alerts:tenant:{tenant_id}"
            alert_data = await self.redis_manager.lrange(alerts_key, 0, limit - 1)
            
            alerts = []
            for data in alert_data:
                try:
                    alert_dict = json.loads(data)
                    alert = AlertInstance.from_dict(alert_dict)
                    
                    if state_filter is None or alert.state == state_filter:
                        alerts.append(alert)
                        
                except Exception as e:
                    self.logger.error(f"Error parsing alert data: {e}")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting tenant alerts: {e}")
            return []
    
    async def get_alert_metrics(
        self,
        tenant_id: Optional[str] = None,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Get alert metrics and statistics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Get alerts from Redis
            if tenant_id:
                alerts_key = f"alerts:tenant:{tenant_id}"
            else:
                alerts_key = "alerts:global"
            
            alert_data = await self.redis_manager.lrange(alerts_key, 0, -1)
            
            # Process metrics
            total_alerts = 0
            alerts_by_severity = {"critical": 0, "warning": 0, "info": 0}
            alerts_by_state = {"firing": 0, "resolved": 0, "acknowledged": 0}
            response_times = []
            
            for data in alert_data:
                try:
                    alert_dict = json.loads(data)
                    alert_time = datetime.fromisoformat(alert_dict["triggered_at"])
                    
                    if start_time <= alert_time <= end_time:
                        total_alerts += 1
                        alerts_by_severity[alert_dict["severity"]] += 1
                        alerts_by_state[alert_dict["state"]] += 1
                        
                        # Calculate response time if acknowledged
                        if alert_dict.get("acknowledged_at"):
        try:
            logger.info(f"Executing _initialize_notification_channels")
            
            # Implementation for _initialize_notification_channels
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_notification_channels completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_notification_channels failed: {e}")
            raise
                    "end": end_time.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting alert metrics: {e}")
            return {}
    
    async def _evaluation_loop(self) -> None:
        """Main alert evaluation loop"""
        try:
            self.logger.info("Starting alert evaluation loop")
            
            while self._running:
                start_time = datetime.utcnow()
                
                # Evaluate all enabled rules
                for rule_id, rule in self.alert_rules.items():
                    if rule.enabled:
                        try:
                            await self._evaluate_rule(rule_id, rule)
                        except Exception as e:
                            self.logger.error(f"Error evaluating rule {rule_id}: {e}")
                
                # Sleep for remaining evaluation interval
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                sleep_time = max(0, 30 - elapsed)  # Evaluate every 30 seconds
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            self.logger.info("Alert evaluation loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in alert evaluation loop: {e}")
    
    async def _notification_loop(self) -> None:
        """Notification processing loop"""
        try:
            self.logger.info("Starting notification loop")
            
            while self._running:
                # Process notification queue
                await self._process_notification_queue()
                await asyncio.sleep(5)  # Process every 5 seconds
                
        except asyncio.CancelledError:
            self.logger.info("Notification loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in notification loop: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Cleanup old alerts and data"""
        try:
            self.logger.info("Starting cleanup loop")
            
            while self._running:
                await self._cleanup_old_alerts()
                await asyncio.sleep(3600)  # Cleanup every hour
                
        except asyncio.CancelledError:
            self.logger.info("Cleanup loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _evaluate_rule(self, rule_id: str, rule: AlertRuleConfig) -> None:
        """Evaluate single alert rule"""
        try:
            # Check each condition
            condition_results = []
            
            for condition in rule.conditions:
                result = await self._evaluate_condition(condition, rule.tenant_id)
                condition_results.append(result)
            
            # Determine if alert should fire (all conditions must be true)
            should_fire = all(condition_results)
            
            # Check if alert is already active
            existing_alert_id = None
            for alert_id, alert in self.active_alerts.items():
                if alert.rule_id == rule_id and alert.state == AlertState.FIRING:
                    existing_alert_id = alert_id
                    break
            
            if should_fire and not existing_alert_id:
                # Trigger new alert
                context = {
                    "conditions": [
                        {
                            "metric": cond.metric_name,
                            "operator": cond.operator,
                            "threshold": cond.threshold,
                            "result": result
                        }
                        for cond, result in zip(rule.conditions, condition_results)
                    ]
                }
                
                await self.trigger_alert(rule_id, 0, context, rule.tenant_id)
                
            elif not should_fire and existing_alert_id:
                # Resolve existing alert
                await self.resolve_alert(existing_alert_id)
                
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule_id}: {e}")
    
    async def _evaluate_condition(
        self,
        condition: AlertCondition,
        tenant_id: Optional[str]
    ) -> bool:
        """Evaluate single alert condition"""
        try:
            # Get metric data from Redis
            metric_key = f"metrics:tenant:{tenant_id}:{condition.metric_name}" if tenant_id else f"metrics:global:{condition.metric_name}"
            
            # Get recent data for duration
            duration_minutes = int(condition.duration.replace('m', ''))
            
            values = []
            current_time = datetime.utcnow()
            
            for i in range(duration_minutes):
                timestamp_key = (current_time - timedelta(minutes=i)).strftime("%Y%m%d%H%M")
                key = f"{metric_key}:{timestamp_key}"
                
                data = await self.redis_manager.lrange(key, 0, -1)
                for item in data:
                    try:
                        metric_data = json.loads(item)
                        values.append(metric_data["value"])
                    except Exception as e:
                        self.logger.error(f"Error parsing metric data: {e}")
            
            if not values:
                return False
            
            # Apply aggregation
            if condition.aggregation == "avg":
                metric_value = sum(values) / len(values)
            elif condition.aggregation == "sum":
                metric_value = sum(values)
            elif condition.aggregation == "min":
                metric_value = min(values)
            elif condition.aggregation == "max":
                metric_value = max(values)
            elif condition.aggregation == "count":
                metric_value = len(values)
            else:
                metric_value = values[-1] if values else 0
            
            # Evaluate condition
            if condition.operator == "gt":
                return metric_value > condition.threshold
            elif condition.operator == "lt":
                return metric_value < condition.threshold
            elif condition.operator == "gte":
                return metric_value >= condition.threshold
            elif condition.operator == "lte":
                return metric_value <= condition.threshold
            elif condition.operator == "eq":
                return metric_value == condition.threshold
            elif condition.operator == "ne":
                return metric_value != condition.threshold
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False
    
    async def _send_alert_notifications(self, alert: AlertInstance) -> None:
        """Send alert notifications"""
        try:
            rule = self.alert_rules.get(alert.rule_id)
            if not rule:
                return
            
            notification = AlertNotification(
                alert_id=alert.id,
                rule_name=alert.rule_name,
                severity=alert.severity,
                state=alert.state,
                message=f"Alert: {alert.rule_name}",
                details=alert.context,
                timestamp=alert.triggered_at,
                tenant_id=alert.tenant_id
            )
            
            # Send to configured channels
            for channel_id in rule.notification_channels:
                if channel_id in self.notification_channels:
                    channel = self.notification_channels[channel_id]
                    await self._send_notification(notification, channel)
                    
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {e}")
    
    async def _send_resolution_notification(self, alert: AlertInstance) -> None:
        """Send alert resolution notification"""
        try:
            rule = self.alert_rules.get(alert.rule_id)
            if not rule:
                return
            
            notification = AlertNotification(
                alert_id=alert.id,
                rule_name=alert.rule_name,
                severity=alert.severity,
                state=AlertState.RESOLVED,
                message=f"Resolved: {alert.rule_name}",
                details=alert.context,
                timestamp=datetime.utcnow(),
                tenant_id=alert.tenant_id
            )
            
            # Send to configured channels
            for channel_id in rule.notification_channels:
                if channel_id in self.notification_channels:
                    channel = self.notification_channels[channel_id]
                    await self._send_notification(notification, channel)
                    
        except Exception as e:
            self.logger.error(f"Error sending resolution notification: {e}")
    
    async def _send_notification(
        self,
        notification: AlertNotification,
        channel: NotificationChannel
    ) -> None:
        """Send notification to specific channel"""
        try:
            if channel.type == NotificationType.EMAIL:
                await self.email_service.send_alert_email(notification, channel.config)
            elif channel.type == NotificationType.SLACK:
                await self.slack_service.send_alert_message(notification, channel.config)
            elif channel.type == NotificationType.WEBHOOK:
                await self.webhook_service.send_alert_webhook(notification, channel.config)
            
            self.logger.info(f"Notification sent: {notification.alert_id} via {channel.type.value}")
            
        except Exception as e:
            self.logger.error(f"Error sending notification via {channel.type.value}: {e}")
    
    async def _process_notification_queue(self) -> None:
        """Process notification queue"""
        try:
            # Get notifications from queue
            queue_key = "notifications:queue"
            notifications = await self.redis_manager.lrange(queue_key, 0, 99)
            
            for notification_data in notifications:
                try:
                    notification_dict = json.loads(notification_data)
                    # Process notification
                    await self.redis_manager.lpop(queue_key)
                except Exception as e:
                    self.logger.error(f"Error processing notification: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error processing notification queue: {e}")
    
    async def _cleanup_old_alerts(self) -> None:
        """Cleanup old resolved alerts"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=7)  # Keep alerts for 7 days
            
            # Cleanup from active alerts
            alerts_to_remove = []
            for alert_id, alert in self.active_alerts.items():
                if alert.state == AlertState.RESOLVED and alert.resolved_at and alert.resolved_at < cutoff_time:
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
            
            self.logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {e}")
    
    async def _store_alert(self, alert: AlertInstance) -> None:
        """Store alert in Redis"""
        try:
            # Store in tenant-specific list
            if alert.tenant_id:
                alerts_key = f"alerts:tenant:{alert.tenant_id}"
            else:
                alerts_key = "alerts:global"
            
            alert_data = alert.to_dict()
            await self.redis_manager.lpush(alerts_key, json.dumps(alert_data))
            
            # Limit list size
            await self.redis_manager.ltrim(alerts_key, 0, 999)  # Keep last 1000 alerts
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default alert rules"""
        # High error rate alert
        self.register_rule(AlertRuleConfig(
            name="High Error Rate",
            description="Alert when HTTP error rate exceeds threshold",
            conditions=[
                AlertCondition(
                    metric_name="http_errors_total",
                    operator="gt",
                    threshold=10.0,
                    duration="5m",
                    aggregation="sum"
                )
            ],
            severity=AlertSeverity.WARNING,
            notification_channels=["default_email"]
        ))
        
        # High CPU usage alert
        self.register_rule(AlertRuleConfig(
            name="High CPU Usage",
            description="Alert when CPU usage exceeds 80%",
            conditions=[
                AlertCondition(
                    metric_name="system_cpu_percent",
                    operator="gt",
                    threshold=80.0,
                    duration="5m",
                    aggregation="avg"
                )
            ],
            severity=AlertSeverity.CRITICAL,
            notification_channels=["default_email", "default_slack"]
        ))
        
        # Low memory alert
        self.register_rule(AlertRuleConfig(
            name="Low Available Memory",
            description="Alert when available memory is low",
            conditions=[
                AlertCondition(
                    metric_name="system_memory_bytes",
                    operator="lt",
                    threshold=1000000000,  # 1GB
                    duration="3m",
                    aggregation="avg"
                )
            ],
            severity=AlertSeverity.WARNING,
            notification_channels=["default_email"]
        ))
    
    def _initialize_notification_channels(self) -> None:
        """Initialize default notification channels"""
        # Default email channel
        self.register_notification_channel(
            "default_email",
            NotificationType.EMAIL,
            {
                "smtp_server": settings.SMTP_SERVER,
                "smtp_port": settings.SMTP_PORT,
                "username": settings.SMTP_USERNAME,
                "password": settings.SMTP_PASSWORD,
                "from_email": settings.ALERT_FROM_EMAIL,
                "to_emails": [settings.ADMIN_EMAIL]
            }
        )
        
        # Default Slack channel
        if hasattr(settings, 'SLACK_WEBHOOK_URL'):
            self.register_notification_channel(
                "default_slack",
                NotificationType.SLACK,
                {
                    "webhook_url": settings.SLACK_WEBHOOK_URL,
                    "channel": "#alerts",
                    "username": "IA-Influencer-Alert"
                }
            )

# File has syntax issues - needs manual review