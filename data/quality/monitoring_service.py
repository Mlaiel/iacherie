"""
Quality Monitoring Service - Real-time Quality Monitoring System
================================================================

Enterprise-grade real-time quality monitoring service for continuous quality oversight.
Provides real-time alerts, trend analysis, and automated quality monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, Any, List, Optional, Callable, Set
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import deque

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class MonitoringMetric(Enum):
    """Monitoring metrics"""
    QUALITY_SCORE = "quality_score"
    ERROR_RATE = "error_rate"
    PROCESSING_TIME = "processing_time"
    THROUGHPUT = "throughput"
    COMPLIANCE_RATE = "compliance_rate"
    INTEGRITY_RATE = "integrity_rate"

@dataclass
class QualityAlert:
    """Quality alert container"""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    metric: MonitoringMetric
    current_value: float
    threshold_value: float
    message: str
    content_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class MonitoringRule:
    """Monitoring rule configuration"""
    name: str
    metric: MonitoringMetric
    threshold: float
    comparison: str  # 'lt', 'gt', 'eq'
    severity: AlertSeverity
    enabled: bool = True
    content_types: Optional[List[str]] = None
    cooldown_minutes: int = 5

class QualityMonitoringService:
    """
    Real-time quality monitoring service.
    
    Provides continuous monitoring of quality metrics, automated alerting,
    trend analysis, and quality dashboard support.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the quality monitoring service.
        
        Args:
            config: Monitoring service configuration
        """
        self.config = config
        self.logger = logger
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Metrics storage (in-memory, would be replaced with proper time-series DB)
        self.metrics_buffer: Dict[MonitoringMetric, deque] = {
            metric: deque(maxlen=1000) for metric in MonitoringMetric
        }
        
        # Alert management
        self.active_alerts: Dict[str, QualityAlert] = {}
        self.alert_history: List[QualityAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring rules
        self.monitoring_rules: List[MonitoringRule] = []
        self._initialize_default_rules()
        
        # Quality assessments storage
        self.recent_assessments: deque = deque(maxlen=100)
        
        # Performance tracking
        self.performance_metrics = {
            'total_assessments': 0,
            'total_alerts': 0,
            'avg_quality_score': 0.0,
            'current_throughput': 0.0
        }
        
        self.logger.info("QualityMonitoringService initialized")
    
    def _initialize_default_rules(self):
        """Initialize default monitoring rules"""
        
        default_rules = [
            MonitoringRule(
                name="critical_quality_drop",
                metric=MonitoringMetric.QUALITY_SCORE,
                threshold=50.0,
                comparison="lt",
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=2
            ),
            MonitoringRule(
                name="low_quality_warning",
                metric=MonitoringMetric.QUALITY_SCORE,
                threshold=70.0,
                comparison="lt",
                severity=AlertSeverity.HIGH,
                cooldown_minutes=5
            ),
            MonitoringRule(
                name="high_error_rate",
                metric=MonitoringMetric.ERROR_RATE,
                threshold=10.0,
                comparison="gt",
                severity=AlertSeverity.HIGH,
                cooldown_minutes=3
            ),
            MonitoringRule(
                name="slow_processing",
                metric=MonitoringMetric.PROCESSING_TIME,
                threshold=30.0,
                comparison="gt",
                severity=AlertSeverity.MEDIUM,
                cooldown_minutes=10
            ),
            MonitoringRule(
                name="low_throughput",
                metric=MonitoringMetric.THROUGHPUT,
                threshold=1.0,
                comparison="lt",
                severity=AlertSeverity.MEDIUM,
                cooldown_minutes=15
            ),
            MonitoringRule(
                name="compliance_failure",
                metric=MonitoringMetric.COMPLIANCE_RATE,
                threshold=95.0,
                comparison="lt",
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=1
            )
        ]
        
        self.monitoring_rules = default_rules
        self.logger.info(f"Initialized {len(default_rules)} default monitoring rules")
    
    async def start_monitoring(self):
        """Start the monitoring service"""
        
        if self.is_monitoring:
            self.logger.warning("Monitoring service is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("Quality monitoring service started")
    
    async def stop_monitoring(self):
        """Stop the monitoring service"""
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Quality monitoring service stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        
        check_interval = self.config.get('check_interval', 60)  # seconds
        
        while self.is_monitoring:
            try:
                await self._check_monitoring_rules()
                await self._update_performance_metrics()
                await self._cleanup_old_data()
                
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(check_interval)
    
    async def record_assessment(self, assessment: Dict[str, Any]):
        """Record a quality assessment for monitoring"""
        
        try:
            # Store the assessment
            assessment_record = {
                'timestamp': datetime.utcnow(),
                'assessment': assessment
            }
            self.recent_assessments.append(assessment_record)
            
            # Update metrics
            self._update_metrics_from_assessment(assessment)
            
            # Check rules against new data
            await self._check_monitoring_rules()
            
            # Update performance counters
            self.performance_metrics['total_assessments'] += 1
            
            self.logger.debug(f"Recorded quality assessment with score: {assessment.get('overall_score', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error recording assessment: {str(e)}")
    
    def _update_metrics_from_assessment(self, assessment: Dict[str, Any]):
        """Update metrics from a quality assessment"""
        
        timestamp = datetime.utcnow()
        
        # Quality score
        overall_score = assessment.get('overall_score', 0)
        self.metrics_buffer[MonitoringMetric.QUALITY_SCORE].append({
            'timestamp': timestamp,
            'value': overall_score,
            'content_type': assessment.get('content_type')
        })
        
        # Processing time
        processing_time = assessment.get('processing_time', 0)
        self.metrics_buffer[MonitoringMetric.PROCESSING_TIME].append({
            'timestamp': timestamp,
            'value': processing_time,
            'content_type': assessment.get('content_type')
        })
        
        # Error rate (based on assessment status)
        error_occurred = assessment.get('status') == 'error'
        self.metrics_buffer[MonitoringMetric.ERROR_RATE].append({
            'timestamp': timestamp,
            'value': 1.0 if error_occurred else 0.0,
            'content_type': assessment.get('content_type')
        })
        
        # Compliance rate
        compliance_passed = assessment.get('compliance', {}).get('status') == 'passed'
        self.metrics_buffer[MonitoringMetric.COMPLIANCE_RATE].append({
            'timestamp': timestamp,
            'value': 1.0 if compliance_passed else 0.0,
            'content_type': assessment.get('content_type')
        })
        
        # Integrity rate
        integrity_passed = assessment.get('integrity', {}).get('status') == 'passed'
        self.metrics_buffer[MonitoringMetric.INTEGRITY_RATE].append({
            'timestamp': timestamp,
            'value': 1.0 if integrity_passed else 0.0,
            'content_type': assessment.get('content_type')
        })
    
    async def _check_monitoring_rules(self):
        """Check all monitoring rules against current metrics"""
        
        for rule in self.monitoring_rules:
            if not rule.enabled:
                continue
            
            try:
                await self._evaluate_rule(rule)
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.name}: {str(e)}")
    
    async def _evaluate_rule(self, rule: MonitoringRule):
        """Evaluate a single monitoring rule"""
        
        # Get recent metric values
        metric_data = self.metrics_buffer.get(rule.metric, deque())
        
        if not metric_data:
            return
        
        # Calculate current metric value
        current_value = self._calculate_metric_value(rule.metric, metric_data, rule.content_types)
        
        # Check if rule condition is met
        condition_met = self._check_rule_condition(rule, current_value)
        
        if condition_met:
            # Check cooldown period
            if not self._is_in_cooldown(rule):
                await self._trigger_alert(rule, current_value)
    
    def _calculate_metric_value(
        self,
        metric: MonitoringMetric,
        data: deque,
        content_types: Optional[List[str]] = None
    ) -> float:
        """Calculate current value for a metric"""
        
        # Filter by content types if specified
        filtered_data = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)  # Last 5 minutes
        
        for record in data:
            if record['timestamp'] < cutoff_time:
                continue
            
            if content_types and record.get('content_type') not in content_types:
                continue
            
            filtered_data.append(record['value'])
        
        if not filtered_data:
            return 0.0
        
        # Calculate metric based on type
        if metric in [MonitoringMetric.QUALITY_SCORE, MonitoringMetric.PROCESSING_TIME]:
            return sum(filtered_data) / len(filtered_data)  # Average
        elif metric in [MonitoringMetric.ERROR_RATE, MonitoringMetric.COMPLIANCE_RATE, MonitoringMetric.INTEGRITY_RATE]:
            return (sum(filtered_data) / len(filtered_data)) * 100  # Percentage
        elif metric == MonitoringMetric.THROUGHPUT:
            return len(filtered_data) / 5.0  # Items per minute (5-minute window)
        else:
            return 0.0
    
    def _check_rule_condition(self, rule: MonitoringRule, current_value: float) -> bool:
        """Check if rule condition is met"""
        
        if rule.comparison == 'lt':
            return current_value < rule.threshold
        elif rule.comparison == 'gt':
            return current_value > rule.threshold
        elif rule.comparison == 'eq':
            return abs(current_value - rule.threshold) < 0.1
        else:
            return False
    
    def _is_in_cooldown(self, rule: MonitoringRule) -> bool:
        """Check if rule is in cooldown period"""
        
        cooldown_key = f"rule_{rule.name}"
        
        # Check for recent alerts from this rule
        cutoff_time = datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)
        
        for alert in self.alert_history:
            if (alert.details.get('rule_name') == rule.name and 
                alert.timestamp > cutoff_time):
                return True
        
        return False
    
    async def _trigger_alert(self, rule: MonitoringRule, current_value: float):
        """Trigger an alert for a rule violation"""
        
        alert_id = f"alert_{rule.name}_{int(datetime.utcnow().timestamp())}"
        
        alert = QualityAlert(
            id=alert_id,
            timestamp=datetime.utcnow(),
            severity=rule.severity,
            metric=rule.metric,
            current_value=current_value,
            threshold_value=rule.threshold,
            message=f"Quality monitoring rule '{rule.name}' triggered: {rule.metric.value} is {current_value:.2f} (threshold: {rule.threshold})",
            details={
                'rule_name': rule.name,
                'comparison': rule.comparison,
                'content_types': rule.content_types
            }
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Update performance metrics
        self.performance_metrics['total_alerts'] += 1
        
        # Notify callbacks
        await self._notify_alert_callbacks(alert)
        
        self.logger.warning(f"Quality alert triggered: {alert.message}")
    
    async def _notify_alert_callbacks(self, alert: QualityAlert):
        """Notify all registered alert callbacks"""
        
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {str(e)}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        
        # Calculate average quality score
        quality_scores = [
            record['value'] for record in self.metrics_buffer[MonitoringMetric.QUALITY_SCORE]
            if record['timestamp'] > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if quality_scores:
            self.performance_metrics['avg_quality_score'] = sum(quality_scores) / len(quality_scores)
        
        # Calculate current throughput
        recent_assessments = [
            assessment for assessment in self.recent_assessments
            if assessment['timestamp'] > datetime.utcnow() - timedelta(minutes=5)
        ]
        
        self.performance_metrics['current_throughput'] = len(recent_assessments) / 5.0  # per minute
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        
        retention_hours = self.config.get('retention_hours', 24)
        cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
        
        # Clean up alert history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]
        
        # Clean up resolved active alerts
        resolved_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.resolved and alert.resolution_time and alert.resolution_time < cutoff_time
        ]
        
        for alert_id in resolved_alerts:
            del self.active_alerts[alert_id]
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable):
        """Remove an alert callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert"""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            self.active_alerts[alert_id].details['acknowledged_by'] = user
            self.active_alerts[alert_id].details['acknowledged_at'] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Alert {alert_id} acknowledged by {user}")
            return True
        
        return False
    
    def resolve_alert(self, alert_id: str, user: str = "system", resolution: str = "") -> bool:
        """Resolve an alert"""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.active_alerts[alert_id].resolution_time = datetime.utcnow()
            self.active_alerts[alert_id].details['resolved_by'] = user
            self.active_alerts[alert_id].details['resolution'] = resolution
            
            self.logger.info(f"Alert {alert_id} resolved by {user}")
            return True
        
        return False
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        
        active_alert_count = len([a for a in self.active_alerts.values() if not a.resolved])
        
        return {
            'is_monitoring': self.is_monitoring,
            'total_assessments': self.performance_metrics['total_assessments'],
            'total_alerts': self.performance_metrics['total_alerts'],
            'active_alerts': active_alert_count,
            'avg_quality_score': round(self.performance_metrics['avg_quality_score'], 2),
            'current_throughput': round(self.performance_metrics['current_throughput'], 2),
            'monitoring_rules_count': len([r for r in self.monitoring_rules if r.enabled]),
            'uptime': datetime.utcnow().isoformat()
        }
    
    def get_alerts(
        self,
        active_only: bool = False,
        severity: Optional[AlertSeverity] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        
        alerts = list(self.active_alerts.values()) if active_only else self.alert_history
        
        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Filter by resolved status if active_only
        if active_only:
            alerts = [a for a in alerts if not a.resolved]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Limit results
        if limit:
            alerts = alerts[:limit]
        
        # Convert to dictionaries
        return [
            {
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.value,
                'metric': alert.metric.value,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'message': alert.message,
                'content_type': alert.content_type,
                'acknowledged': alert.acknowledged,
                'resolved': alert.resolved,
                'resolution_time': alert.resolution_time.isoformat() if alert.resolution_time else None,
                'details': alert.details
            }
            for alert in alerts
        ]
    
    def add_monitoring_rule(self, rule: MonitoringRule):
        """Add a custom monitoring rule"""
        self.monitoring_rules.append(rule)
        self.logger.info(f"Added monitoring rule: {rule.name}")
    
    def remove_monitoring_rule(self, rule_name: str) -> bool:
        """Remove a monitoring rule"""
        
        for i, rule in enumerate(self.monitoring_rules):
            if rule.name == rule_name:
                del self.monitoring_rules[i]
                self.logger.info(f"Removed monitoring rule: {rule_name}")
                return True
        
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a monitoring rule"""
        
        for rule in self.monitoring_rules:
            if rule.name == rule_name:
                rule.enabled = True
                self.logger.info(f"Enabled monitoring rule: {rule_name}")
                return True
        
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a monitoring rule"""
        
        for rule in self.monitoring_rules:
            if rule.name == rule_name:
                rule.enabled = False
                self.logger.info(f"Disabled monitoring rule: {rule_name}")
                return True
        
        return False
