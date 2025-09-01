"""Data Governance Monitoring and Surveillance System

Advanced monitoring system for data governance compliance,
policy enforcement, and real-time governance violations detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

from ...core.base import BaseManager
from ...core.exceptions import MonitoringError, ValidationError
from .policies import PolicyManager, PolicyViolation
from .compliance import ComplianceManager
from .privacy import PrivacyManager
from .access import AccessController


class AlertSeverity(Enum):
    """
Alert severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MonitoringScope(Enum):
    """Monitoring scope types"""

    GLOBAL = "global"
    CONTENT_TYPE = "content_type"
    USER_GROUP = "user_group"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"


class MetricType(Enum):
    """Types of governance metrics"""

    POLICY_VIOLATIONS = "policy_violations"
    COMPLIANCE_SCORE = "compliance_score"
    ACCESS_VIOLATIONS = "access_violations"
    PRIVACY_BREACHES = "privacy_breaches"
    DATA_QUALITY = "data_quality"
    RETENTION_COMPLIANCE = "retention_compliance"
    LINEAGE_COMPLETENESS = "lineage_completeness"


@dataclass
class GovernanceAlert:
    """Governance monitoring alert"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    metric_type: MetricType
    source_component: str
    scope: MonitoringScope
    threshold_violated: float
    current_value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MonitoringThreshold:
    """
Monitoring threshold configuration"""
    threshold_id: str
    name: str
    metric_type: MetricType
    operator: str  # "gt", "lt", "eq", "gte", "lte"
    value: float
    severity: AlertSeverity
    scope: MonitoringScope
    enabled: bool = True
    alert_frequency: int = 300  # seconds
    last_alerted: Optional[datetime] = None


@dataclass
class MetricSnapshot:
    """Point-in-time metric measurement"""
    metric_type: MetricType
    scope: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceDashboard:
    """
Governance monitoring dashboard data"""
    total_policies: int
    active_violations: int
    compliance_score: float
    privacy_risk_score: float
    data_quality_score: float
    alerts_by_severity: Dict[str, int]
    recent_violations: List[PolicyViolation]
    trends: Dict[str, List[float]]
    last_updated: datetime = field(default_factory=datetime.utcnow)


class MetricsCollector:
    """
    Collects governance metrics from various components
    
    Aggregates metrics from policy engine, compliance checker,
    privacy manager, and other governance components.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Metric storage
        self.metric_history: Dict[MetricType, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.current_metrics: Dict[str, MetricSnapshot] = {}
        
        # Component references
        self.policy_manager: Optional[PolicyManager] = None
        self.compliance_manager: Optional[ComplianceManager] = None
        self.privacy_manager: Optional[PrivacyManager] = None
        self.access_controller: Optional[AccessController] = None
    
    def set_components(
        self,
        policy_manager: PolicyManager,
        compliance_manager: ComplianceManager,
        privacy_manager: PrivacyManager,
        access_controller: AccessController
    ) -> None:
        """
Set references to governance components"""
        self.policy_manager = policy_manager
        self.compliance_manager = compliance_manager
        self.privacy_manager = privacy_manager
        self.access_controller = access_controller
    
    async def collect_all_metrics(self) -> Dict[MetricType, MetricSnapshot]:
        """
Collect all governance metrics"""
        try:
            metrics = {}
            
            # Collect policy violation metrics
            if self.policy_manager:
                policy_metrics = await self._collect_policy_metrics()
                metrics.update(policy_metrics)
            
            # Collect compliance metrics
            if self.compliance_manager:
                compliance_metrics = await self._collect_compliance_metrics()
                metrics.update(compliance_metrics)
            
            # Collect privacy metrics
            if self.privacy_manager:
                privacy_metrics = await self._collect_privacy_metrics()
                metrics.update(privacy_metrics)
            
            # Collect access control metrics
            if self.access_controller:
                access_metrics = await self._collect_access_metrics()
                metrics.update(access_metrics)
            
            # Update metric history
            for metric_type, snapshot in metrics.items():
                self.metric_history[metric_type].append(snapshot)
                self.current_metrics[f"{metric_type.value}_global"] = snapshot
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            raise MonitoringError(f"Metric collection failed: {e}")
    
    async def _collect_policy_metrics(self) -> Dict[MetricType, MetricSnapshot]:
        """Collect policy-related metrics"""
        try:
            metrics = {}
            
            # Get policy violations
            violations = await self.policy_manager.get_policy_violations()
            active_violations = [v for v in violations if not v.resolved]
            
            # Policy violation count
            violation_metric = MetricSnapshot(
                metric_type=MetricType.POLICY_VIOLATIONS,
                scope="global",
                value=len(active_violations),
                metadata={
                    "total_violations": len(violations),
                    "resolved_violations": len(violations) - len(active_violations),
                    "violation_types": list(set(v.violation_type for v in active_violations))
                }
            )
            metrics[MetricType.POLICY_VIOLATIONS] = violation_metric
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting policy metrics: {e}")
            return {}
    
    async def _collect_compliance_metrics(self) -> Dict[MetricType, MetricSnapshot]:
        """Collect compliance-related metrics"""
        try:
            metrics = {}
            
            # Get compliance scores
            compliance_metrics = await self.compliance_manager.get_metrics()
            
            # Overall compliance score
            compliance_metric = MetricSnapshot(
                metric_type=MetricType.COMPLIANCE_SCORE,
                scope="global",
                value=compliance_metrics.get("overall_compliance_score", 0.0),
                metadata={
                    "gdpr_score": compliance_metrics.get("gdpr_compliance_score", 0.0),
                    "ccpa_score": compliance_metrics.get("ccpa_compliance_score", 0.0),
                    "dmca_score": compliance_metrics.get("dmca_compliance_score", 0.0),
                    "total_assessments": compliance_metrics.get("total_assessments", 0)
                }
            )
            metrics[MetricType.COMPLIANCE_SCORE] = compliance_metric
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting compliance metrics: {e}")
            return {}
    
    async def _collect_privacy_metrics(self) -> Dict[MetricType, MetricSnapshot]:
        """Collect privacy-related metrics"""
        try:
            metrics = {}
            
            # Get privacy metrics
            privacy_metrics = await self.privacy_manager.get_metrics()
            
            # Privacy breach risk score (based on PII detection rate)
            pii_detection_rate = privacy_metrics.get("pii_detection_rate", 0.0)
            privacy_metric = MetricSnapshot(
                metric_type=MetricType.PRIVACY_BREACHES,
                scope="global",
                value=pii_detection_rate,
                metadata={
                    "total_scans": privacy_metrics.get("total_scans", 0),
                    "pii_detected_count": privacy_metrics.get("pii_detected_count", 0),
                    "anonymizations_performed": privacy_metrics.get("anonymizations_performed", 0)
                }
            )
            metrics[MetricType.PRIVACY_BREACHES] = privacy_metric
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting privacy metrics: {e}")
            return {}
    
    async def _collect_access_metrics(self) -> Dict[MetricType, MetricSnapshot]:
        """Collect access control metrics"""
        try:
            metrics = {}
            
            # Get access control metrics
            access_metrics = await self.access_controller.get_metrics()
            
            # Access violations
            access_violations = access_metrics.get("access_denied_count", 0)
            access_metric = MetricSnapshot(
                metric_type=MetricType.ACCESS_VIOLATIONS,
                scope="global",
                value=access_violations,
                metadata={
                    "total_requests": access_metrics.get("total_requests", 0),
                    "access_granted_count": access_metrics.get("access_granted_count", 0),
                    "policy_evaluations": access_metrics.get("policy_evaluations", 0)
                }
            )
            metrics[MetricType.ACCESS_VIOLATIONS] = access_metric
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting access metrics: {e}")
            return {}
    
    def get_metric_trend(
        self,
        metric_type: MetricType,
        time_window: int = 3600  # seconds
    ) -> List[float]:
        """Get metric trend over time window"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
        
        history = self.metric_history.get(metric_type, [])
        recent_metrics = [
            m for m in history
            if m.timestamp >= cutoff_time
        ]
        
        return [m.value for m in recent_metrics]


class AlertManager:
    """
    Manages governance alerts and notifications
    
    Processes threshold violations, sends notifications,
    and tracks alert resolution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Alert storage
        self.active_alerts: Dict[str, GovernanceAlert] = {}
        self.alert_history: List[GovernanceAlert] = []
        self.thresholds: Dict[str, MonitoringThreshold] = {}
        
        # Alert handlers
        self.alert_handlers: List[Callable[[GovernanceAlert], Awaitable[None]]] = []
    
    def add_alert_handler(
        self,
        handler: Callable[[GovernanceAlert], Awaitable[None]]
    ) -> None:
        """
Add an alert handler"""
        self.alert_handlers.append(handler)
    
    async def configure_threshold(self, threshold: MonitoringThreshold) -> None:
        """
Configure a monitoring threshold"""
        try:
            # Validate threshold
            await self._validate_threshold(threshold)
            
            # Store threshold
            self.thresholds[threshold.threshold_id] = threshold
            
            self.logger.info(f"Configured threshold: {threshold.threshold_id}")
            
        except Exception as e:
            self.logger.error(f"Error configuring threshold {threshold.threshold_id}: {e}")
            raise MonitoringError(f"Threshold configuration failed: {e}")
    
    async def evaluate_thresholds(
        self,
        metrics: Dict[MetricType, MetricSnapshot]
    ) -> List[GovernanceAlert]:
        """Evaluate metrics against thresholds and generate alerts"""
        try:
            alerts = []
            
            for threshold in self.thresholds.values():
                if not threshold.enabled:
                    continue
                
                # Check if we should skip due to alert frequency
                if self._should_skip_alert(threshold):
                    continue
                
                # Find matching metric
                metric = metrics.get(threshold.metric_type)
                if not metric:
                    continue
                
                # Evaluate threshold
                if self._evaluate_threshold(threshold, metric.value):
                    alert = await self._create_alert(threshold, metric)
                    alerts.append(alert)
                    
                    # Update last alerted time
                    threshold.last_alerted = datetime.utcnow()
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error evaluating thresholds: {e}")
            raise MonitoringError(f"Threshold evaluation failed: {e}")
    
    async def create_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        metric_type: MetricType,
        source_component: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GovernanceAlert:
        """Create a new governance alert"""
        try:
            alert = GovernanceAlert(
                alert_id=f"alert_{datetime.utcnow().timestamp()}",
                title=title,
                description=description,
                severity=severity,
                metric_type=metric_type,
                source_component=source_component,
                scope=MonitoringScope.GLOBAL,
                threshold_violated=0.0,
                current_value=0.0,
                metadata=metadata or {}
            )
            
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            self.logger.warning(f"Created alert: {alert.title} ({alert.severity.value})")
            return alert
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            raise MonitoringError(f"Alert creation failed: {e}")
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.acknowledged = True
            alert.metadata["acknowledged_by"] = user_id
            alert.metadata["acknowledged_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution: str) -> bool:
        """Resolve an alert"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.metadata["resolved_by"] = user_id
            alert.metadata["resolution"] = resolution
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert {alert_id} resolved by {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        metric_type: Optional[MetricType] = None
    ) -> List[GovernanceAlert]:
        """Get active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if metric_type:
            alerts = [a for a in alerts if a.metric_type == metric_type]
        
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)
    
    def _should_skip_alert(self, threshold: MonitoringThreshold) -> bool:
        """
Check if alert should be skipped due to frequency limits"""
        if not threshold.last_alerted:
            return False
        
        time_since_last = datetime.utcnow() - threshold.last_alerted
        return time_since_last.total_seconds() < threshold.alert_frequency
    
    def _evaluate_threshold(self, threshold: MonitoringThreshold, value: float) -> bool:
        """
Evaluate if threshold is violated"""
        if threshold.operator == "gt":
            return value > threshold.value
        elif threshold.operator == "gte":
            return value >= threshold.value
        elif threshold.operator == "lt":
            return value < threshold.value
        elif threshold.operator == "lte":
            return value <= threshold.value
        elif threshold.operator == "eq":
            return value == threshold.value
        else:
            return False
    
    async def _create_alert(
        self,
        threshold: MonitoringThreshold,
        metric: MetricSnapshot
    ) -> GovernanceAlert:
        """Create alert from threshold violation"""
        alert = GovernanceAlert(
            alert_id=f"threshold_{threshold.threshold_id}_{datetime.utcnow().timestamp()}",
            title=f"Threshold Violation: {threshold.name}",
            description=f"Metric {threshold.metric_type.value} violated threshold {threshold.value} (current: {metric.value})",
            severity=threshold.severity,
            metric_type=threshold.metric_type,
            source_component="monitoring",
            scope=threshold.scope,
            threshold_violated=threshold.value,
            current_value=metric.value,
            metadata={
                "threshold_id": threshold.threshold_id,
                "operator": threshold.operator,
                "metric_metadata": metric.metadata
            }
        )
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        return alert
    
    async def _send_alert_notifications(self, alert: GovernanceAlert) -> None:
        """Send alert notifications to handlers"""
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
    
    async def _validate_threshold(self, threshold: MonitoringThreshold) -> None:
        """Validate threshold configuration"""
        valid_operators = {"gt", "gte", "lt", "lte", "eq"}
        if threshold.operator not in valid_operators:
            raise ValidationError(f"Invalid threshold operator: {threshold.operator}")
        
        if threshold.alert_frequency < 0:
            raise ValidationError("Alert frequency must be non-negative")


class GovernanceMonitor(BaseManager):
    """
    Central governance monitoring system
    
    Coordinates monitoring of all governance components,
    collects metrics, evaluates thresholds, and manages alerts.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize the governance monitor"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.metrics_collector = MetricsCollector(config)
        self.alert_manager = AlertManager(config)
        
        # Monitoring configuration
        self.monitoring_interval = config.get("monitoring_interval", 60)  # seconds
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Dashboard data
        self.dashboard_data: Optional[GovernanceDashboard] = None
        
        # Component references
        self.policy_manager: Optional[PolicyManager] = None
        self.compliance_manager: Optional[ComplianceManager] = None
        self.privacy_manager: Optional[PrivacyManager] = None
        self.access_controller: Optional[AccessController] = None
    
    async def initialize(self) -> None:
        """Initialize the governance monitor"""
        try:
            # Configure default thresholds
            await self._configure_default_thresholds()
            
            # Set up default alert handlers
            await self._setup_default_alert_handlers()
            
            self.logger.info("Governance monitor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize governance monitor: {e}")
            raise MonitoringError(f"Monitor initialization failed: {e}")
    
    def set_governance_components(
        self,
        policy_manager: PolicyManager,
        compliance_manager: ComplianceManager,
        privacy_manager: PrivacyManager,
        access_controller: AccessController
    ) -> None:
        """Set references to governance components"""
        self.policy_manager = policy_manager
        self.compliance_manager = compliance_manager
        self.privacy_manager = privacy_manager
        self.access_controller = access_controller
        
        # Set components in metrics collector
        self.metrics_collector.set_components(
            policy_manager, compliance_manager, privacy_manager, access_controller
        )
    
    async def start_monitoring(self) -> None:
        """
Start continuous governance monitoring"""
        if self.is_monitoring:
            self.logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("Started governance monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop governance monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        self.logger.info("Stopped governance monitoring")
    
    async def collect_metrics(self) -> Dict[MetricType, MetricSnapshot]:
        """Manually trigger metric collection"""
        return await self.metrics_collector.collect_all_metrics()
    
    async def create_manual_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        source_component: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GovernanceAlert:
        """
Create a manual alert"""
        return await self.alert_manager.create_alert(
            title=title,
            description=description,
            severity=severity,
            metric_type=MetricType.POLICY_VIOLATIONS,  # Default
            source_component=source_component,
            metadata=metadata
        )
    
    async def get_dashboard_data(self) -> GovernanceDashboard:
        """
Get current governance dashboard data"""
        try:
            # Collect latest metrics
            metrics = await self.collect_metrics()
            
            # Get active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Calculate scores
            compliance_score = 0.0
            privacy_risk_score = 0.0
            data_quality_score = 85.0  # Placeholder
            
            if MetricType.COMPLIANCE_SCORE in metrics:
                compliance_score = metrics[MetricType.COMPLIANCE_SCORE].value
            
            if MetricType.PRIVACY_BREACHES in metrics:
                privacy_risk_score = metrics[MetricType.PRIVACY_BREACHES].value
            
            # Count alerts by severity
            alerts_by_severity = {
                severity.value: 0 for severity in AlertSeverity
            }
            for alert in active_alerts:
                alerts_by_severity[alert.severity.value] += 1
            
            # Get recent violations
            recent_violations = []
            if self.policy_manager:
                all_violations = await self.policy_manager.get_policy_violations()
                recent_violations = sorted(
                    all_violations,
                    key=lambda v: v.detected_at,
                    reverse=True
                )[:10]
            
            # Get trends
            trends = {}
            for metric_type in MetricType:
                trend = self.metrics_collector.get_metric_trend(metric_type)
                trends[metric_type.value] = trend[-24:] if len(trend) > 24 else trend
            
            self.dashboard_data = GovernanceDashboard(
                total_policies=len(getattr(self.policy_manager, 'policies', {})),
                active_violations=len([v for v in recent_violations if not v.resolved]),
                compliance_score=compliance_score,
                privacy_risk_score=privacy_risk_score,
                data_quality_score=data_quality_score,
                alerts_by_severity=alerts_by_severity,
                recent_violations=recent_violations,
                trends=trends
            )
            
            return self.dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard data: {e}")
            raise MonitoringError(f"Dashboard generation failed: {e}")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            "is_monitoring": self.is_monitoring,
            "monitoring_interval": self.monitoring_interval,
            "active_alerts_count": len(self.alert_manager.active_alerts),
            "total_thresholds": len(self.alert_manager.thresholds),
            "components_connected": {
                "policy_manager": self.policy_manager is not None,
                "compliance_manager": self.compliance_manager is not None,
                "privacy_manager": self.privacy_manager is not None,
                "access_controller": self.access_controller is not None
            },
            "last_metric_collection": getattr(self, "_last_metric_collection", None),
            "metric_types_tracked": [mt.value for mt in MetricType]
        }
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = await self.metrics_collector.collect_all_metrics()
                self._last_metric_collection = datetime.utcnow()
                
                # Evaluate thresholds and generate alerts
                new_alerts = await self.alert_manager.evaluate_thresholds(metrics)
                
                if new_alerts:
                    self.logger.info(f"Generated {len(new_alerts)} new alerts")
                
                # Wait for next iteration
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _configure_default_thresholds(self) -> None:
        """Configure default monitoring thresholds"""
        # Policy violations threshold
        policy_threshold = MonitoringThreshold(
            threshold_id="policy_violations_high",
            name="High Policy Violations",
            metric_type=MetricType.POLICY_VIOLATIONS,
            operator="gt",
            value=10.0,
            severity=AlertSeverity.HIGH,
            scope=MonitoringScope.GLOBAL,
            alert_frequency=300
        )
        await self.alert_manager.configure_threshold(policy_threshold)
        
        # Compliance score threshold
        compliance_threshold = MonitoringThreshold(
            threshold_id="compliance_score_low",
            name="Low Compliance Score",
            metric_type=MetricType.COMPLIANCE_SCORE,
            operator="lt",
            value=80.0,
            severity=AlertSeverity.MEDIUM,
            scope=MonitoringScope.GLOBAL,
            alert_frequency=600
        )
        await self.alert_manager.configure_threshold(compliance_threshold)
        
        # Privacy breaches threshold
        privacy_threshold = MonitoringThreshold(
            threshold_id="privacy_breaches_high",
            name="High Privacy Risk",
            metric_type=MetricType.PRIVACY_BREACHES,
            operator="gt",
            value=20.0,
            severity=AlertSeverity.CRITICAL,
            scope=MonitoringScope.GLOBAL,
            alert_frequency=180
        )
        await self.alert_manager.configure_threshold(privacy_threshold)
        
        # Access violations threshold
        access_threshold = MonitoringThreshold(
            threshold_id="access_violations_high",
            name="High Access Violations",
            metric_type=MetricType.ACCESS_VIOLATIONS,
            operator="gt",
            value=50.0,
            severity=AlertSeverity.HIGH,
            scope=MonitoringScope.GLOBAL,
            alert_frequency=300
        )
        await self.alert_manager.configure_threshold(access_threshold)
    
    async def _setup_default_alert_handlers(self) -> None:
        """Set up default alert handlers"""
        # Log alert handler
        async def log_alert_handler(alert: GovernanceAlert) -> None:
            log_level = {
                AlertSeverity.CRITICAL: logging.CRITICAL,
                AlertSeverity.HIGH: logging.ERROR,
                AlertSeverity.MEDIUM: logging.WARNING,
                AlertSeverity.LOW: logging.INFO,
                AlertSeverity.INFO: logging.INFO
            }.get(alert.severity, logging.INFO)
            
            self.logger.log(
                log_level,
                f"GOVERNANCE ALERT: {alert.title} - {alert.description}"
            )
        
        self.alert_manager.add_alert_handler(log_alert_handler)
