# -*- coding: utf-8 -*-
"""
Ainfluencer Platform - Enterprise Security Metrics
Advanced security monitoring and metrics collection system
Author: Ainfluencer Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import statistics

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class MetricType(Enum):
    """Types of security metrics"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    THREAT_DETECTION = "threat_detection"
    FRAUD_PREVENTION = "fraud_prevention"
    ACCESS_CONTROL = "access_control"
    AUDIT_COMPLIANCE = "audit_compliance"
    BIOMETRIC = "biometric"
    ENCRYPTION = "encryption"
    NETWORK_SECURITY = "network_security"
    INCIDENT_RESPONSE = "incident_response"

class MetricSeverity(Enum):
    """Metric severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class SecurityMetric:
    """Security metric data point"""
    id: str
    name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricThreshold:
    """Metric threshold for alerting"""
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold_value: float
    severity: MetricSeverity
    time_window: Optional[timedelta] = None
    consecutive_breaches: int = 1
    description: str = ""

@dataclass
class SecurityAlert:
    """Security alert based on metrics"""
    id: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: MetricSeverity
    message: str
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityDashboard:
    """Security metrics dashboard data"""
    total_metrics: int
    active_alerts: int
    critical_alerts: int
    system_health_score: float  # 0-100
    last_updated: datetime
    metric_summary: Dict[str, Any]
    top_alerts: List[SecurityAlert]

class SecurityMetricsCollector:
    """Enterprise Security Metrics Collection System"""
    
    def __init__(self):
        """Initialize security metrics collector"""
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.thresholds: Dict[str, List[MetricThreshold]] = defaultdict(list)
        self.alerts: List[SecurityAlert] = []
        self.active_alerts: Dict[str, SecurityAlert] = {}
        self._lock = threading.RLock()
        self._alert_counter = 0
        
        # Metric aggregation windows
        self.aggregation_windows = {
            "1m": timedelta(minutes=1),
            "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15),
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24)
        }
        
        # System health calculation weights
        self.health_weights = {
            MetricType.AUTHENTICATION: 0.2,
            MetricType.THREAT_DETECTION: 0.25,
            MetricType.FRAUD_PREVENTION: 0.15,
            MetricType.ACCESS_CONTROL: 0.15,
            MetricType.BIOMETRIC: 0.1,
            MetricType.AUDIT_COMPLIANCE: 0.1,
            MetricType.ENCRYPTION: 0.05
        }
        
        # Initialize default thresholds and metrics
        self._initialize_default_thresholds()
        self._start_metric_collection()
        
        logger.info("📊 Security Metrics Collector initialized successfully")
    
    def _initialize_default_thresholds(self):
        """Initialize default security metric thresholds"""
        default_thresholds = [
            # Authentication metrics
            MetricThreshold(
                metric_name="failed_login_rate",
                operator=">",
                threshold_value=0.1,  # 10% failure rate
                severity=MetricSeverity.WARNING,
                time_window=timedelta(minutes=5),
                description="High authentication failure rate"
            ),
            MetricThreshold(
                metric_name="failed_login_rate",
                operator=">",
                threshold_value=0.25,  # 25% failure rate
                severity=MetricSeverity.CRITICAL,
                time_window=timedelta(minutes=5),
                description="Critical authentication failure rate"
            ),
            
            # Threat detection metrics
            MetricThreshold(
                metric_name="threats_per_hour",
                operator=">",
                threshold_value=50,
                severity=MetricSeverity.WARNING,
                description="High threat detection rate"
            ),
            MetricThreshold(
                metric_name="critical_threats",
                operator=">",
                threshold_value=5,
                severity=MetricSeverity.CRITICAL,
                time_window=timedelta(hours=1),
                description="Multiple critical threats detected"
            ),
            
            # System performance metrics
            MetricThreshold(
                metric_name="response_time_ms",
                operator=">",
                threshold_value=5000,  # 5 seconds
                severity=MetricSeverity.WARNING,
                description="High security system response time"
            ),
            MetricThreshold(
                metric_name="system_cpu_usage",
                operator=">",
                threshold_value=80.0,  # 80% CPU
                severity=MetricSeverity.WARNING,
                description="High system CPU usage"
            ),
            
            # Fraud prevention metrics
            MetricThreshold(
                metric_name="fraud_detection_rate",
                operator=">",
                threshold_value=0.05,  # 5% of transactions
                severity=MetricSeverity.WARNING,
                time_window=timedelta(hours=1),
                description="High fraud detection rate"
            ),
            
            # Access control metrics
            MetricThreshold(
                metric_name="authorization_failures",
                operator=">",
                threshold_value=100,
                severity=MetricSeverity.WARNING,
                time_window=timedelta(hours=1),
                description="High authorization failure rate"
            ),
            
            # Biometric metrics
            MetricThreshold(
                metric_name="biometric_failure_rate",
                operator=">",
                threshold_value=0.15,  # 15% failure rate
                severity=MetricSeverity.WARNING,
                time_window=timedelta(minutes=10),
                description="High biometric authentication failure rate"
            )
        ]
        
        for threshold in default_thresholds:
            self.thresholds[threshold.metric_name].append(threshold)
        
        logger.info(f"📏 Initialized {len(default_thresholds)} default metric thresholds")
    
    def _start_metric_collection(self):
        """Start automatic metric collection"""
        # This would typically start background threads for metric collection
        # For demo purposes, we'll collect some initial metrics
        self._collect_system_metrics()
        logger.info("🔄 Started automatic metric collection")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType,
                     unit: str = "", tags: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record a security metric"""
        try:
            with self._lock:
                metric = SecurityMetric(
                    id=f"{name}_{int(time.time() * 1000)}",
                    name=name,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    tags=tags or {},
                    metadata=metadata or {}
                )
                
                self.metrics[name].append(metric)
                
                # Check thresholds
                self._check_thresholds(name, value)
                
                logger.debug(f"📈 Recorded metric: {name} = {value} {unit}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error recording metric: {str(e)}")
            return False
    
    def _check_thresholds(self, metric_name: str, current_value: float):
        """Check metric against configured thresholds"""
        try:
            thresholds = self.thresholds.get(metric_name, [])
            
            for threshold in thresholds:
                if self._threshold_breached(threshold, current_value):
                    self._create_alert(threshold, current_value)
            
        except Exception as e:
            logger.error(f"❌ Error checking thresholds: {str(e)}")
    
    def _threshold_breached(self, threshold: MetricThreshold, current_value: float) -> bool:
        """Check if threshold is breached"""
        try:
            operator = threshold.operator
            threshold_value = threshold.threshold_value
            
            if operator == ">":
                return current_value > threshold_value
            elif operator == "<":
                return current_value < threshold_value
            elif operator == ">=":
                return current_value >= threshold_value
            elif operator == "<=":
                return current_value <= threshold_value
            elif operator == "==":
                return current_value == threshold_value
            elif operator == "!=":
                return current_value != threshold_value
            
            return False
            
        except Exception:
            return False
    
    def _create_alert(self, threshold: MetricThreshold, current_value: float):
        """Create security alert for threshold breach"""
        try:
            # Check if alert already exists for this metric
            alert_key = f"{threshold.metric_name}_{threshold.severity.value}"
            if alert_key in self.active_alerts:
                # Update existing alert
                existing_alert = self.active_alerts[alert_key]
                existing_alert.current_value = current_value
                existing_alert.metadata["last_breach"] = datetime.now()
                return
            
            # Create new alert
            self._alert_counter += 1
            alert_id = f"alert_{self._alert_counter}_{int(time.time())}"
            
            message = f"{threshold.description or 'Threshold breached'}: {threshold.metric_name} = {current_value} (threshold: {threshold.threshold_value})"
            
            alert = SecurityAlert(
                id=alert_id,
                metric_name=threshold.metric_name,
                current_value=current_value,
                threshold_value=threshold.threshold_value,
                severity=threshold.severity,
                message=message,
                metadata={
                    "operator": threshold.operator,
                    "time_window": threshold.time_window.total_seconds() if threshold.time_window else None
                }
            )
            
            self.alerts.append(alert)
            self.active_alerts[alert_key] = alert
            
            logger.warning(f"🚨 Security alert created: {alert.severity.value} - {message}")
            
        except Exception as e:
            logger.error(f"❌ Error creating alert: {str(e)}")
    
    def get_metric_summary(self, metric_name: str, time_window: str = "1h") -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        try:
            if metric_name not in self.metrics or time_window not in self.aggregation_windows:
                return {}
            
            window = self.aggregation_windows[time_window]
            cutoff_time = datetime.now() - window
            
            # Filter metrics within time window
            recent_metrics = [
                m for m in self.metrics[metric_name]
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"count": 0, "time_window": time_window}
            
            values = [m.value for m in recent_metrics]
            
            return {
                "metric_name": metric_name,
                "time_window": time_window,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "latest_value": values[-1] if values else 0,
                "latest_timestamp": recent_metrics[-1].timestamp.isoformat() if recent_metrics else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting metric summary: {str(e)}")
            return {}
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score"""
        try:
            health_scores = {}
            
            # Calculate health score for each metric type
            for metric_type in MetricType:
                type_score = self._calculate_type_health_score(metric_type)
                health_scores[metric_type] = type_score
            
            # Calculate weighted average
            total_weight = sum(self.health_weights.values())
            weighted_score = sum(
                score * self.health_weights.get(metric_type, 0)
                for metric_type, score in health_scores.items()
            )
            
            return min(max(weighted_score / total_weight * 100, 0), 100)
            
        except Exception as e:
            logger.error(f"❌ Error calculating system health score: {str(e)}")
            return 50.0  # Default to neutral score
    
    def _calculate_type_health_score(self, metric_type: MetricType) -> float:
        """Calculate health score for specific metric type"""
        try:
            # Get recent alerts for this metric type
            recent_alerts = [
                alert for alert in self.alerts
                if alert.created_at >= datetime.now() - timedelta(hours=1)
                and any(m.metric_type == metric_type for m in self.metrics.get(alert.metric_name, []))
            ]
            
            # Base score
            base_score = 1.0
            
            # Deduct points for alerts
            for alert in recent_alerts:
                if alert.severity == MetricSeverity.CRITICAL:
                    base_score -= 0.3
                elif alert.severity == MetricSeverity.ERROR:
                    base_score -= 0.2
                elif alert.severity == MetricSeverity.WARNING:
                    base_score -= 0.1
            
            return max(base_score, 0.0)
            
        except Exception:
            return 0.5  # Default to neutral score
    
    def get_active_alerts(self, severity_filter: Optional[MetricSeverity] = None) -> List[SecurityAlert]:
        """Get active security alerts"""
        try:
            active_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.status == AlertStatus.ACTIVE
            ]
            
            if severity_filter:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.severity == severity_filter
                ]
            
            # Sort by severity and creation time
            severity_order = {
                MetricSeverity.CRITICAL: 0,
                MetricSeverity.ERROR: 1,
                MetricSeverity.WARNING: 2,
                MetricSeverity.INFO: 3
            }
            
            active_alerts.sort(
                key=lambda a: (severity_order[a.severity], a.created_at),
                reverse=True
            )
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"❌ Error getting active alerts: {str(e)}")
            return []
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge a security alert"""
        try:
            with self._lock:
                # Find alert in active alerts
                for alert in self.active_alerts.values():
                    if alert.id == alert_id:
                        alert.status = AlertStatus.ACKNOWLEDGED
                        alert.acknowledged_at = datetime.now()
                        alert.metadata["acknowledged_by"] = acknowledged_by
                        
                        logger.info(f"✅ Alert acknowledged: {alert_id} by {acknowledged_by}")
                        return True
                
                # Find alert in all alerts
                for alert in self.alerts:
                    if alert.id == alert_id:
                        alert.status = AlertStatus.ACKNOWLEDGED
                        alert.acknowledged_at = datetime.now()
                        alert.metadata["acknowledged_by"] = acknowledged_by
                        return True
                
                logger.warning(f"⚠️ Alert not found: {alert_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error acknowledging alert: {str(e)}")
            return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve a security alert"""
        try:
            with self._lock:
                # Remove from active alerts
                alert_key_to_remove = None
                for key, alert in self.active_alerts.items():
                    if alert.id == alert_id:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = datetime.now()
                        alert.metadata["resolved_by"] = resolved_by
                        alert_key_to_remove = key
                        break
                
                if alert_key_to_remove:
                    del self.active_alerts[alert_key_to_remove]
                    logger.info(f"✅ Alert resolved: {alert_id} by {resolved_by}")
                    return True
                
                logger.warning(f"⚠️ Active alert not found: {alert_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error resolving alert: {str(e)}")
            return False
    
    def get_dashboard_data(self) -> SecurityDashboard:
        """Get security metrics dashboard data"""
        try:
            with self._lock:
                total_metrics = sum(len(metrics) for metrics in self.metrics.values())
                active_alerts = self.get_active_alerts()
                critical_alerts = len([a for a in active_alerts if a.severity == MetricSeverity.CRITICAL])
                
                # Get metric summary by type
                metric_summary = {}
                for metric_type in MetricType:
                    type_metrics = []
                    for metric_name, metrics in self.metrics.items():
                        type_metrics.extend([m for m in metrics if m.metric_type == metric_type])
                    
                    metric_summary[metric_type.value] = {
                        "count": len(type_metrics),
                        "latest_timestamp": max([m.timestamp for m in type_metrics]).isoformat() if type_metrics else None
                    }
                
                # Get top alerts (most recent critical/error alerts)
                top_alerts = sorted(
                    [a for a in active_alerts if a.severity in [MetricSeverity.CRITICAL, MetricSeverity.ERROR]],
                    key=lambda a: a.created_at,
                    reverse=True
                )[:5]
                
                return SecurityDashboard(
                    total_metrics=total_metrics,
                    active_alerts=len(active_alerts),
                    critical_alerts=critical_alerts,
                    system_health_score=self.get_system_health_score(),
                    last_updated=datetime.now(),
                    metric_summary=metric_summary,
                    top_alerts=top_alerts
                )
                
        except Exception as e:
            logger.error(f"❌ Error getting dashboard data: {str(e)}")
            return SecurityDashboard(
                total_metrics=0,
                active_alerts=0,
                critical_alerts=0,
                system_health_score=0.0,
                last_updated=datetime.now(),
                metric_summary={},
                top_alerts=[]
            )
    
    def _collect_system_metrics(self):
        """Collect system-level security metrics"""
        try:
            current_time = datetime.now()
            
            # Simulate some system metrics
            import random
            
            # Authentication metrics
            self.record_metric(
                "auth_requests_per_minute",
                random.uniform(10, 100),
                MetricType.AUTHENTICATION,
                "requests/min"
            )
            
            self.record_metric(
                "failed_login_rate",
                random.uniform(0.02, 0.08),
                MetricType.AUTHENTICATION,
                "ratio"
            )
            
            # Threat detection metrics
            self.record_metric(
                "threats_per_hour",
                random.uniform(5, 30),
                MetricType.THREAT_DETECTION,
                "threats/hour"
            )
            
            # System performance metrics
            self.record_metric(
                "response_time_ms",
                random.uniform(100, 2000),
                MetricType.AUTHENTICATION,
                "milliseconds"
            )
            
            self.record_metric(
                "system_cpu_usage",
                random.uniform(20, 75),
                MetricType.AUTHENTICATION,
                "percentage"
            )
            
            logger.debug("📊 Collected system security metrics")
            
        except Exception as e:
            logger.error(f"❌ Error collecting system metrics: {str(e)}")
    
    def export_metrics(self, format_type: str = "json", time_window: str = "24h") -> Optional[str]:
        """Export metrics data"""
        try:
            if time_window not in self.aggregation_windows:
                return None
            
            window = self.aggregation_windows[time_window]
            cutoff_time = datetime.now() - window
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "time_window": time_window,
                "metrics": {},
                "alerts": [],
                "summary": {
                    "total_metrics": 0,
                    "active_alerts": len(self.active_alerts),
                    "system_health_score": self.get_system_health_score()
                }
            }
            
            # Export metrics
            for metric_name, metrics in self.metrics.items():
                recent_metrics = [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.value,
                        "unit": m.unit,
                        "tags": m.tags,
                        "metadata": m.metadata
                    }
                    for m in metrics if m.timestamp >= cutoff_time
                ]
                
                if recent_metrics:
                    export_data["metrics"][metric_name] = recent_metrics
                    export_data["summary"]["total_metrics"] += len(recent_metrics)
            
            # Export alerts
            recent_alerts = [
                {
                    "id": alert.id,
                    "metric_name": alert.metric_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "status": alert.status.value,
                    "created_at": alert.created_at.isoformat(),
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value
                }
                for alert in self.alerts if alert.created_at >= cutoff_time
            ]
            export_data["alerts"] = recent_alerts
            
            if format_type == "json":
                return json.dumps(export_data, indent=2)
            else:
                return str(export_data)
                
        except Exception as e:
            logger.error(f"❌ Error exporting metrics: {str(e)}")
            return None
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old metrics and alerts"""
        try:
            with self._lock:
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Clean old alerts
                initial_alert_count = len(self.alerts)
                self.alerts = [a for a in self.alerts if a.created_at >= cutoff_time]
                
                # Clean old metrics (already limited by deque maxlen, but cleanup metadata)
                cleaned_alerts = initial_alert_count - len(self.alerts)
                
                if cleaned_alerts > 0:
                    logger.info(f"🧹 Cleaned up {cleaned_alerts} old alerts (>{days} days)")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {str(e)}")

# Create global instance
security_metrics = SecurityMetricsCollector()

# Export main classes and instance
__all__ = [
    'SecurityMetricsCollector',
    'SecurityMetric',
    'MetricThreshold',
    'SecurityAlert',
    'SecurityDashboard',
    'MetricType',
    'MetricSeverity',
    'AlertStatus',
    'security_metrics'
]