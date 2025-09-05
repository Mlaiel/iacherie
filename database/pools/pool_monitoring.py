#!/usr/bin/env python3
"""Pool Monitoring - Real-time Monitoring and Analytics System
==============================================================

Real-time monitoring, metrics collection, and analytics for all database pools
in the IA Influencer Agent + Content Protection Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import json
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    """Types of metrics collected"""
    CONNECTION_COUNT = "connection_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CACHE_HIT_RATIO = "cache_hit_ratio"

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    pool_id: str
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """Alert definition and state"""
    alert_id: str
    pool_id: str
    severity: AlertSeverity
    message: str
    metric_type: MetricType
    threshold_value: float
    current_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: Optional[datetime] = None

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    pool_id: str = "*"  # * for all pools
    metric_type: MetricType = MetricType.CONNECTION_COUNT
    threshold: float = 0.0
    operator: str = ">"  # >, <, >=, <=, ==
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_minutes: int = 5
    enabled: bool = True
    description: str = ""

@dataclass
class PoolHealthStatus:
    """Pool health status summary"""
    pool_id: str
    is_healthy: bool
    health_score: float  # 0-100
    last_check: datetime
    active_alerts: List[Alert]
    metrics_summary: Dict[str, float]
    issues: List[str] = field(default_factory=list)

class MetricsCollector:
    """Collects and stores metrics from database pools"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self._metrics: List[MetricPoint] = []
        self._aggregated_metrics: Dict[str, List[float]] = {}
        
        logger.info("📊 Metrics collector initialized")

    def record_metric(self, pool_id: str, metric_type: MetricType, value: float, labels: Dict[str, str] = None):
        """Record a new metric point"""
        metric = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            metric_type=metric_type,
            value=value,
            pool_id=pool_id,
            labels=labels or {}
        )
        
        self._metrics.append(metric)
        
        # Update aggregated metrics
        key = f"{pool_id}_{metric_type.value}"
        if key not in self._aggregated_metrics:
            self._aggregated_metrics[key] = []
        self._aggregated_metrics[key].append(value)
        
        # Keep only recent metrics
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        self._metrics = [m for m in self._metrics if m.timestamp > cutoff_time]
        
        logger.debug(f"📈 Recorded {metric_type.value} = {value} for {pool_id}")

    def get_metrics(self, 
                   pool_id: Optional[str] = None, 
                   metric_type: Optional[MetricType] = None,
                   hours_back: int = 1) -> List[MetricPoint]:
        """Get metrics with optional filtering"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        filtered_metrics = [
            m for m in self._metrics 
            if m.timestamp > cutoff_time
        ]
        
        if pool_id:
            filtered_metrics = [m for m in filtered_metrics if m.pool_id == pool_id]
        
        if metric_type:
            filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]
        
        return filtered_metrics

    def get_aggregated_stats(self, pool_id: str, metric_type: MetricType, hours_back: int = 1) -> Dict[str, float]:
        """Get aggregated statistics for a metric"""
        metrics = self.get_metrics(pool_id, metric_type, hours_back)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'latest': values[-1] if values else 0.0
        }

class AlertManager:
    """Manages alerts and alert rules"""
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Initialize default alert rules
        self._create_default_rules()
        
        logger.info("🚨 Alert manager initialized")

    def _create_default_rules(self):
        """Create default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="high_connection_usage",
                metric_type=MetricType.CONNECTION_COUNT,
                threshold=40,
                operator=">",
                severity=AlertSeverity.WARNING,
                description="High connection usage detected"
            ),
            AlertRule(
                rule_id="critical_connection_usage",
                metric_type=MetricType.CONNECTION_COUNT,
                threshold=45,
                operator=">",
                severity=AlertSeverity.CRITICAL,
                description="Critical connection usage - immediate attention required"
            ),
            AlertRule(
                rule_id="high_error_rate",
                metric_type=MetricType.ERROR_RATE,
                threshold=5.0,
                operator=">",
                severity=AlertSeverity.WARNING,
                description="High error rate detected"
            ),
            AlertRule(
                rule_id="slow_response_time",
                metric_type=MetricType.RESPONSE_TIME,
                threshold=1000.0,  # 1 second
                operator=">",
                severity=AlertSeverity.WARNING,
                description="Slow response time detected"
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"✅ Alert rule added: {rule.rule_id}")

    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"✅ Alert rule removed: {rule_id}")

    def evaluate_alerts(self, metrics: List[MetricPoint]):
        """Evaluate all alert rules against current metrics"""
        for metric in metrics:
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue
                
                # Check if rule applies to this pool
                if rule.pool_id != "*" and rule.pool_id != metric.pool_id:
                    continue
                
                # Check if rule applies to this metric type
                if rule.metric_type != metric.metric_type:
                    continue
                
                # Evaluate threshold
                should_alert = self._evaluate_threshold(metric.value, rule.threshold, rule.operator)
                
                alert_key = f"{rule.rule_id}_{metric.pool_id}"
                
                if should_alert:
                    if alert_key not in self.active_alerts:
                        # Create new alert
                        alert = Alert(
                            alert_id=alert_key,
                            pool_id=metric.pool_id,
                            severity=rule.severity,
                            message=f"{rule.description} - {metric.metric_type.value}: {metric.value}",
                            metric_type=metric.metric_type,
                            threshold_value=rule.threshold,
                            current_value=metric.value,
                            triggered_at=metric.timestamp
                        )
                        
                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)
                        
                        # Notify callbacks
                        for callback in self.alert_callbacks:
                            try:
                                callback(alert)
                            except Exception as e:
                                logger.error(f"❌ Alert callback error: {e}")
                        
                        logger.warning(f"🚨 Alert triggered: {alert.message}")
                
                else:
                    # Resolve alert if it exists
                    if alert_key in self.active_alerts:
                        alert = self.active_alerts[alert_key]
                        alert.resolved_at = datetime.now(timezone.utc)
                        del self.active_alerts[alert_key]
                        logger.info(f"✅ Alert resolved: {alert.message}")

    def _evaluate_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate if value meets threshold criteria"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001  # Float comparison
        else:
            logger.warning(f"⚠️ Unknown operator: {operator}")
            return False

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now(timezone.utc)
            logger.info(f"✅ Alert acknowledged: {alert_id} by {acknowledged_by}")

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)

class PoolMonitoringManager:
    """Central monitoring manager for all database pools"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.pool_health_status: Dict[str, PoolHealthStatus] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_interval = 10.0  # seconds
        self.metrics_enabled = True
        self.alerts_enabled = True
        
        # Add default alert callback
        self.alert_manager.add_alert_callback(self._log_alert)
        
        logger.info("📊 Pool Monitoring Manager initialized")

    def _log_alert(self, alert: Alert):
        """Default alert logging callback"""
        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🔥",
            AlertSeverity.EMERGENCY: "🚨"
        }
        
        emoji = severity_emoji.get(alert.severity, "❗")
        logger.warning(f"{emoji} {alert.severity.value.upper()}: {alert.message}")

    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Monitoring already running")
            return
        
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🔄 Pool monitoring started")

    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            logger.info("⏹️ Pool monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self._monitoring_interval)
                
                if self.metrics_enabled:
                    await self._collect_metrics()
                
                if self.alerts_enabled:
                    await self._evaluate_alerts()
                
                await self._update_health_status()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")

    async def _collect_metrics(self):
        """Collect metrics from all pools"""
        # This would normally collect from actual pools
        # For now, simulate some metrics
        import random
        
        mock_pools = ["postgresql_main", "redis_cache", "mongodb_content"]
        
        for pool_id in mock_pools:
            # Simulate connection count
            conn_count = random.randint(5, 50)
            self.metrics_collector.record_metric(
                pool_id, MetricType.CONNECTION_COUNT, conn_count
            )
            
            # Simulate response time
            response_time = random.uniform(10, 500)  # ms
            self.metrics_collector.record_metric(
                pool_id, MetricType.RESPONSE_TIME, response_time
            )
            
            # Simulate error rate
            error_rate = random.uniform(0, 10)  # %
            self.metrics_collector.record_metric(
                pool_id, MetricType.ERROR_RATE, error_rate
            )

    async def _evaluate_alerts(self):
        """Evaluate alert rules"""
        # Get recent metrics
        recent_metrics = self.metrics_collector.get_metrics(hours_back=0.1)  # Last 6 minutes
        
        # Evaluate alerts
        self.alert_manager.evaluate_alerts(recent_metrics)

    async def _update_health_status(self):
        """Update health status for all pools"""
        # Get list of pools from recent metrics
        recent_metrics = self.metrics_collector.get_metrics(hours_back=0.5)
        pool_ids = set(m.pool_id for m in recent_metrics)
        
        for pool_id in pool_ids:
            health_status = await self._calculate_pool_health(pool_id)
            self.pool_health_status[pool_id] = health_status

    async def _calculate_pool_health(self, pool_id: str) -> PoolHealthStatus:
        """Calculate health status for a specific pool"""
        # Get active alerts for this pool
        pool_alerts = [
            alert for alert in self.alert_manager.active_alerts.values()
            if alert.pool_id == pool_id
        ]
        
        # Calculate health score based on metrics and alerts
        health_score = 100.0
        issues = []
        
        # Reduce score for active alerts
        for alert in pool_alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                health_score -= 30
                issues.append(f"Critical: {alert.message}")
            elif alert.severity == AlertSeverity.WARNING:
                health_score -= 15
                issues.append(f"Warning: {alert.message}")
            elif alert.severity == AlertSeverity.EMERGENCY:
                health_score -= 50
                issues.append(f"Emergency: {alert.message}")
        
        # Get metrics summary
        metrics_summary = {}
        for metric_type in MetricType:
            stats = self.metrics_collector.get_aggregated_stats(pool_id, metric_type, 0.5)
            if stats:
                metrics_summary[metric_type.value] = stats.get('latest', 0.0)
        
        health_score = max(0.0, health_score)
        is_healthy = health_score > 70 and len([a for a in pool_alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]]) == 0
        
        return PoolHealthStatus(
            pool_id=pool_id,
            is_healthy=is_healthy,
            health_score=health_score,
            last_check=datetime.now(timezone.utc),
            active_alerts=pool_alerts,
            metrics_summary=metrics_summary,
            issues=issues
        )

    def get_pool_health(self, pool_id: str) -> Optional[PoolHealthStatus]:
        """Get health status for a specific pool"""
        return self.pool_health_status.get(pool_id)

    def get_all_pool_health(self) -> Dict[str, PoolHealthStatus]:
        """Get health status for all pools"""
        return self.pool_health_status.copy()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        total_pools = len(self.pool_health_status)
        healthy_pools = sum(1 for status in self.pool_health_status.values() if status.is_healthy)
        total_alerts = len(self.alert_manager.active_alerts)
        critical_alerts = sum(
            1 for alert in self.alert_manager.active_alerts.values()
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
        )
        
        return {
            'summary': {
                'total_pools': total_pools,
                'healthy_pools': healthy_pools,
                'unhealthy_pools': total_pools - healthy_pools,
                'total_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'monitoring_active': self._monitoring_task is not None and not self._monitoring_task.done()
            },
            'pool_health': {
                pool_id: {
                    'health_score': status.health_score,
                    'is_healthy': status.is_healthy,
                    'alert_count': len(status.active_alerts),
                    'last_check': status.last_check.isoformat()
                }
                for pool_id, status in self.pool_health_status.items()
            },
            'recent_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'pool_id': alert.pool_id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'triggered_at': alert.triggered_at.isoformat()
                }
                for alert in sorted(
                    self.alert_manager.active_alerts.values(),
                    key=lambda a: a.triggered_at,
                    reverse=True
                )[:10]
            ]
        }

# Global monitoring manager instance
_monitoring_manager: Optional[PoolMonitoringManager] = None

def get_monitoring_manager() -> PoolMonitoringManager:
    """Get the global monitoring manager"""
    global _monitoring_manager
    if _monitoring_manager is None:
        _monitoring_manager = PoolMonitoringManager()
    return _monitoring_manager

# Export public interface
__all__ = [
    'PoolMonitoringManager',
    'get_monitoring_manager',
    'MetricsCollector',
    'AlertManager',
    'Alert',
    'AlertRule',
    'AlertSeverity',
    'MetricType',
    'PoolHealthStatus'
]