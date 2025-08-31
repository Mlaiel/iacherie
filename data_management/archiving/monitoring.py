"""
Archival Monitoring and Analytics Module

Comprehensive monitoring system for archival operations with real-time metrics,
performance analytics, alerting, and business intelligence dashboards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json

from ..models import ArchiveEntry
from .archival_manager import ArchivalTier, ArchivalStatus
from .exceptions import ArchivalError


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status states"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ArchivalMetrics:
    """Core archival system metrics"""
    
    # Storage metrics
    total_archives: int = 0
    total_size_bytes: int = 0
    compressed_size_bytes: int = 0
    compression_ratio: float = 1.0
    
    # Tier distribution
    hot_tier_count: int = 0
    cold_tier_count: int = 0
    frozen_tier_count: int = 0
    deep_archive_count: int = 0
    
    # Operation metrics
    archives_created_24h: int = 0
    archives_retrieved_24h: int = 0
    failed_operations_24h: int = 0
    
    # Performance metrics
    avg_compression_time_ms: float = 0.0
    avg_retrieval_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    
    # Cost metrics
    monthly_storage_cost: float = 0.0
    monthly_retrieval_cost: float = 0.0
    cost_per_gb: float = 0.0
    
    # Quality metrics
    integrity_check_failures: int = 0
    corruption_incidents: int = 0
    
    # System health
    system_uptime_hours: float = 0.0
    error_rate_percentage: float = 0.0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceMetrics:
    """Detailed performance analytics"""
    
    # Throughput metrics
    operations_per_second: float = 0.0
    bytes_processed_per_second: float = 0.0
    
    # Latency metrics (percentiles)
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    
    # Resource utilization
    cpu_usage_percentage: float = 0.0
    memory_usage_percentage: float = 0.0
    disk_io_utilization: float = 0.0
    network_io_utilization: float = 0.0
    
    # Queue metrics
    pending_operations: int = 0
    queue_depth: int = 0
    processing_backlog: int = 0
    
    # Error metrics
    total_errors: int = 0
    error_rate: float = 0.0
    retry_attempts: int = 0
    
    # Efficiency metrics
    resource_efficiency_score: float = 1.0
    cost_efficiency_score: float = 1.0
    
    # Timestamp
    measured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertRule:
    """Alert rule definition"""
    rule_id: str
    name: str
    description: str
    
    # Condition
    metric_name: str
    condition: str  # e.g., "> 0.8", "< 100", "== 0"
    threshold_value: float
    evaluation_period_minutes: int = 5
    
    # Severity and routing
    severity: AlertSeverity = AlertSeverity.MEDIUM
    notification_channels: List[str] = field(default_factory=list)
    
    # Behavior
    enabled: bool = True
    suppress_duration_minutes: int = 60
    auto_resolve: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: str = "system"


@dataclass
class Alert:
    """Active alert instance"""
    alert_id: str
    rule_id: str
    
    # Alert details
    title: str
    description: str
    severity: AlertSeverity
    
    # Trigger information
    metric_value: float
    threshold_value: float
    triggered_at: datetime
    
    # Status
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Context
    affected_components: List[str] = field(default_factory=list)
    impact_description: str = ""
    
    # Escalation
    escalation_level: int = 0
    notifications_sent: int = 0
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricCollector(ABC):
    """Abstract base for metric collectors"""
    
    @abstractmethod
    async def collect_metrics(self) -> Dict[str, MetricPoint]:
        """Collect metrics from source"""
        pass
    
    @abstractmethod
    def get_collector_name(self) -> str:
        """Get collector identifier"""
        pass


class ArchivalSystemCollector(MetricCollector):
    """Collector for core archival system metrics"""
    
    def __init__(self, archive_manager):
        self.archive_manager = archive_manager
        self.collection_history: List[ArchivalMetrics] = []
    
    async def collect_metrics(self) -> Dict[str, MetricPoint]:
        """Collect archival system metrics"""



        try:
            timestamp = datetime.utcnow()
            metrics = {}
            
            # Mock metrics collection (in real implementation, query from managers)
            
            # Storage metrics
            metrics["total_archives"] = MetricPoint(timestamp, 1500)
            metrics["total_size_bytes"] = MetricPoint(timestamp, 500 * 1024**3)  # 500GB
            metrics["compression_ratio"] = MetricPoint(timestamp, 0.65)
            
            # Tier distribution
            metrics["hot_tier_archives"] = MetricPoint(timestamp, 800)
            metrics["cold_tier_archives"] = MetricPoint(timestamp, 500)
            metrics["frozen_tier_archives"] = MetricPoint(timestamp, 150)
            metrics["deep_archive_archives"] = MetricPoint(timestamp, 50)
            
            # Operation rates
            metrics["archives_created_rate"] = MetricPoint(timestamp, 45.0)  # per hour
            metrics["archives_retrieved_rate"] = MetricPoint(timestamp, 120.0)  # per hour
            
            # Performance
            metrics["avg_compression_time"] = MetricPoint(timestamp, 1250.0)  # ms
            metrics["avg_retrieval_time"] = MetricPoint(timestamp, 800.0)  # ms
            metrics["cache_hit_rate"] = MetricPoint(timestamp, 0.85)
            
            # Cost metrics
            metrics["monthly_storage_cost"] = MetricPoint(timestamp, 1250.50)  # USD
            metrics["cost_per_gb"] = MetricPoint(timestamp, 0.023)  # USD
            
            # Health metrics
            metrics["error_rate"] = MetricPoint(timestamp, 0.025)  # 2.5%
            metrics["integrity_failures"] = MetricPoint(timestamp, 2)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect archival metrics: {e}")
            return {}
    
    def get_collector_name(self) -> str:
        return "archival_system"


class PerformanceCollector(MetricCollector):
    """Collector for performance metrics"""
    
    def __init__(self):
        self.latency_history: List[float] = []
        self.operation_counts: Dict[str, int] = {}
        self.start_time = time.time()
    
    async def collect_metrics(self) -> Dict[str, MetricPoint]:
        """Collect performance metrics"""



        try:
            timestamp = datetime.utcnow()
            metrics = {}
            
            # Calculate latency percentiles
            if self.latency_history:
                sorted_latencies = sorted(self.latency_history)
                p50_idx = int(len(sorted_latencies) * 0.5)
                p95_idx = int(len(sorted_latencies) * 0.95)
                p99_idx = int(len(sorted_latencies) * 0.99)
                
                metrics["p50_latency"] = MetricPoint(timestamp, sorted_latencies[p50_idx])
                metrics["p95_latency"] = MetricPoint(timestamp, sorted_latencies[p95_idx])
                metrics["p99_latency"] = MetricPoint(timestamp, sorted_latencies[p99_idx])
                metrics["max_latency"] = MetricPoint(timestamp, max(sorted_latencies))
            
            # Operations per second
            total_ops = sum(self.operation_counts.values())
            runtime_seconds = time.time() - self.start_time
            ops_per_second = total_ops / max(runtime_seconds, 1)
            
            metrics["operations_per_second"] = MetricPoint(timestamp, ops_per_second)
            
            # Mock resource metrics
            metrics["cpu_usage"] = MetricPoint(timestamp, 45.5)  # 45.5%
            metrics["memory_usage"] = MetricPoint(timestamp, 68.2)  # 68.2%
            metrics["disk_io_utilization"] = MetricPoint(timestamp, 25.8)
            
            # Queue metrics
            metrics["pending_operations"] = MetricPoint(timestamp, 12)
            metrics["queue_depth"] = MetricPoint(timestamp, 8)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return {}
    
    def get_collector_name(self) -> str:
        return "performance"
    
    def record_operation(self, operation_type: str, latency_ms: float):
        """Record operation for metrics"""
        self.operation_counts[operation_type] = self.operation_counts.get(operation_type, 0) + 1
        self.latency_history.append(latency_ms)
        
        # Keep history bounded
        if len(self.latency_history) > 10000:
            self.latency_history = self.latency_history[-5000:]


class AlertManager:
    """Advanced alert management system"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Notification handlers
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.total_alerts_triggered = 0
        self.alerts_resolved = 0
        
        # Initialize default rules
        asyncio.create_task(self._initialize_default_rules())
        
        logger.info("Alert Manager initialized")
    
    async def add_rule(self, rule: AlertRule) -> bool:
        """Add new alert rule"""



        try:
            if not await self._validate_rule(rule):
                raise ArchivalError(f"Invalid alert rule: {rule.rule_id}")
            
            self.rules[rule.rule_id] = rule
            logger.info(f"Added alert rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert rule: {e}")
            return False
    
    async def evaluate_rules(self, metrics: Dict[str, MetricPoint]):
        """Evaluate alert rules against current metrics"""



        try:
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                if rule.metric_name not in metrics:
                    continue
                
                metric_value = metrics[rule.metric_name].value
                
                # Evaluate condition
                if await self._evaluate_condition(metric_value, rule.condition, rule.threshold_value):
                    await self._trigger_alert(rule, metric_value)
                else:
                    # Check for auto-resolution
                    await self._check_auto_resolve(rule)
            
        except Exception as e:
            logger.error(f"Failed to evaluate alert rules: {e}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert"""



        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert"""



        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            self.alerts_resolved += 1
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # Sort by severity and timestamp
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
            AlertSeverity.INFO: 4
        }
        
        alerts.sort(key=lambda a: (severity_order[a.severity], a.triggered_at), reverse=True)
        return alerts
    
    async def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""



        try:
            # Count by severity
            severity_counts = {}
            for alert in self.active_alerts.values():
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Calculate resolution metrics
            total_alerts = self.total_alerts_triggered
            resolution_rate = (self.alerts_resolved / max(total_alerts, 1)) * 100
            
            # Average resolution time
            resolved_alerts = [a for a in self.alert_history if a.resolved_at]
            avg_resolution_time = 0
            
            if resolved_alerts:
                resolution_times = [
                    (a.resolved_at - a.triggered_at).total_seconds() / 60
                    for a in resolved_alerts
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            return {
                "active_alerts": len(self.active_alerts),
                "total_alerts_triggered": self.total_alerts_triggered,
                "alerts_resolved": self.alerts_resolved,
                "resolution_rate_percentage": resolution_rate,
                "average_resolution_time_minutes": avg_resolution_time,
                "severity_distribution": severity_counts,
                "alert_rules_count": len(self.rules),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get alert stats: {e}")
            return {}
    
    async def _validate_rule(self, rule: AlertRule) -> bool:
        """Validate alert rule"""



        try:
            # Basic validation
            if not rule.rule_id or not rule.name or not rule.metric_name:
                return False
            
            # Validate condition format
            if not re.match(r'^[<>=!]+\s*[\d.]+$', rule.condition.strip()):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            return False
    
    async def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""



        try:
            condition = condition.strip()
            
            if condition.startswith('>='):
                return value >= threshold
            elif condition.startswith('<='):
                return value <= threshold
            elif condition.startswith('>'):
                return value > threshold
            elif condition.startswith('<'):
                return value < threshold
            elif condition.startswith('=='):
                return abs(value - threshold) < 0.001  # Float comparison
            elif condition.startswith('!='):
                return abs(value - threshold) >= 0.001
            
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert"""



        try:
            # Check if alert already exists for this rule
            existing_alert = None
            for alert in self.active_alerts.values():
                if alert.rule_id == rule.rule_id:
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert
                existing_alert.metric_value = metric_value
                return
            
            # Create new alert
            alert_id = f"alert_{rule.rule_id}_{int(time.time())}"
            
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=f"Alert: {rule.name}",
                description=f"{rule.description} (value: {metric_value}, threshold: {rule.threshold_value})",
                severity=rule.severity,
                metric_value=metric_value,
                threshold_value=rule.threshold_value,
                triggered_at=datetime.utcnow()
            )
            
            self.active_alerts[alert_id] = alert
            self.total_alerts_triggered += 1
            
            # Send notifications
            await self._send_notifications(alert, rule)
            
            logger.warning(f"Alert triggered: {rule.name} (value: {metric_value})")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    async def _check_auto_resolve(self, rule: AlertRule):
        """Check for auto-resolution of alerts"""
        if not rule.auto_resolve:
            return
        
        # Find alerts for this rule
        alerts_to_resolve = []
        for alert in self.active_alerts.values():
            if alert.rule_id == rule.rule_id:
                alerts_to_resolve.append(alert.alert_id)
        
        # Resolve alerts
        for alert_id in alerts_to_resolve:
            await self.resolve_alert(alert_id)
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications"""



        try:
            for channel in rule.notification_channels:
                if channel in self.notification_handlers:
                    handler = self.notification_handlers[channel]
                    await handler(alert, rule)
                else:
                    logger.warning(f"No handler for notification channel: {channel}")
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    async def _initialize_default_rules(self):
        """Initialize default alert rules"""



        try:
            # High error rate alert
            error_rate_rule = AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Error rate exceeds acceptable threshold",
                metric_name="error_rate",
                condition="> 0.05",  # 5%
                threshold_value=0.05,
                severity=AlertSeverity.HIGH,
                evaluation_period_minutes=5
            )
            await self.add_rule(error_rate_rule)
            
            # Low cache hit rate
            cache_rule = AlertRule(
                rule_id="low_cache_hit_rate",
                name="Low Cache Hit Rate",
                description="Cache hit rate is below optimal threshold",
                metric_name="cache_hit_rate",
                condition="< 0.7",  # 70%
                threshold_value=0.7,
                severity=AlertSeverity.MEDIUM,
                evaluation_period_minutes=10
            )
            await self.add_rule(cache_rule)
            
            # High storage cost
            cost_rule = AlertRule(
                rule_id="high_storage_cost",
                name="High Storage Cost",
                description="Monthly storage cost exceeds budget",
                metric_name="monthly_storage_cost",
                condition="> 2000",  # $2000
                threshold_value=2000.0,
                severity=AlertSeverity.MEDIUM,
                evaluation_period_minutes=60
            )
            await self.add_rule(cost_rule)
            
            logger.info("Initialized default alert rules")
            
        except Exception as e:
            logger.error(f"Failed to initialize default rules: {e}")


class ArchivalMonitoring:
    """
    Comprehensive monitoring system for archival operations.
    
    Provides real-time metrics collection, performance analytics,
    alerting, and business intelligence for archival systems.
    """
    
    def __init__(self, collection_interval_seconds: int = 60):
        self.collection_interval = collection_interval_seconds
        
        # Core components
        self.collectors: Dict[str, MetricCollector] = {}
        self.alert_manager = AlertManager()
        
        # Metrics storage
        self.current_metrics: Dict[str, MetricPoint] = {}
        self.metric_history: Dict[str, List[MetricPoint]] = {}
        
        # Analytics
        self.performance_analyzer = PerformanceAnalyzer()
        
        # State
        self.monitoring_active = False
        self.collection_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.total_collections = 0
        self.failed_collections = 0
        self.start_time = datetime.utcnow()
        
        logger.info("Archival Monitoring initialized")
    
    async def start_monitoring(self):
        """Start the monitoring system"""



        try:
            if self.monitoring_active:
                logger.warning("Monitoring already active")
                return
            
            self.monitoring_active = True
            self.collection_task = asyncio.create_task(self._collection_loop())
            
            logger.info("Archival monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.monitoring_active = False
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""



        try:
            self.monitoring_active = False
            
            if self.collection_task:
                self.collection_task.cancel()
                try:
                    await self.collection_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Archival monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
    
    async def add_collector(self, collector: MetricCollector):
        """Add a metric collector"""



        try:
            collector_name = collector.get_collector_name()
            self.collectors[collector_name] = collector
            
            logger.info(f"Added metric collector: {collector_name}")
            
        except Exception as e:
            logger.error(f"Failed to add collector: {e}")
    
    async def get_current_metrics(self) -> Dict[str, MetricPoint]:
        """Get current metrics snapshot"""



        return self.current_metrics.copy()
    
    async def get_metric_history(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """Get historical metrics for analysis"""



        try:
            if metric_name not in self.metric_history:
                return []
            
            history = self.metric_history[metric_name]
            
            # Apply time filters
            if start_time or end_time:
                filtered_history = []
                for point in history:
                    if start_time and point.timestamp < start_time:
                        continue
                    if end_time and point.timestamp > end_time:
                        continue
                    filtered_history.append(point)
                return filtered_history
            
            return history.copy()
            
        except Exception as e:
            logger.error(f"Failed to get metric history: {e}")
            return []
    
    async def get_performance_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance analysis for specified time period"""



        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            analysis = await self.performance_analyzer.analyze_performance(
                self.metric_history, start_time, end_time
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to get performance analysis: {e}")
            return {}
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""



        try:
            # Current system status
            current_metrics = await self.get_current_metrics()
            
            # Active alerts
            active_alerts = await self.alert_manager.get_active_alerts()
            
            # Recent performance
            performance_analysis = await self.get_performance_analysis(hours=1)
            
            # Alert statistics
            alert_stats = await self.alert_manager.get_alert_stats()
            
            # System health score
            health_score = await self._calculate_health_score(current_metrics)
            
            # Monitoring statistics
            uptime = (datetime.utcnow() - self.start_time).total_seconds() / 3600
            collection_success_rate = ((self.total_collections - self.failed_collections) / 
                                     max(self.total_collections, 1)) * 100
            
            return {
                "system_health_score": health_score,
                "current_metrics": {k: v.value for k, v in current_metrics.items()},
                "active_alerts_count": len(active_alerts),
                "critical_alerts": [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL],
                "performance_summary": performance_analysis,
                "alert_statistics": alert_stats,
                "monitoring_stats": {
                    "uptime_hours": uptime,
                    "total_collections": self.total_collections,
                    "collection_success_rate": collection_success_rate,
                    "collectors_count": len(self.collectors)
                },
                "dashboard_generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate monitoring dashboard: {e}")
            return {}
    
    async def _collection_loop(self):
        """Main metrics collection loop"""



        try:
            while self.monitoring_active:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
                
        except asyncio.CancelledError:
            logger.info("Metrics collection loop cancelled")
        except Exception as e:
            logger.error(f"Collection loop error: {e}")
    
    async def _collect_all_metrics(self):
        """Collect metrics from all collectors"""



        try:
            timestamp = datetime.utcnow()
            all_metrics = {}
            
            # Collect from all registered collectors
            for collector_name, collector in self.collectors.items():
                try:
                    collector_metrics = await collector.collect_metrics()
                    all_metrics.update(collector_metrics)
                    
                except Exception as e:
                    logger.error(f"Failed to collect from {collector_name}: {e}")
                    self.failed_collections += 1
            
            # Update current metrics
            self.current_metrics = all_metrics
            
            # Store in history
            for metric_name, metric_point in all_metrics.items():
                if metric_name not in self.metric_history:
                    self.metric_history[metric_name] = []
                
                self.metric_history[metric_name].append(metric_point)
                
                # Keep history bounded (last 24 hours)
                cutoff_time = timestamp - timedelta(hours=24)
                self.metric_history[metric_name] = [
                    point for point in self.metric_history[metric_name]
                    if point.timestamp > cutoff_time
                ]
            
            # Evaluate alerts
            await self.alert_manager.evaluate_rules(all_metrics)
            
            self.total_collections += 1
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            self.failed_collections += 1
    
    async def _calculate_health_score(self, metrics: Dict[str, MetricPoint]) -> float:
        """Calculate overall system health score (0-100)"""



        try:
            score = 100.0
            
            # Error rate impact
            if "error_rate" in metrics:
                error_rate = metrics["error_rate"].value
                score -= error_rate * 100 * 10  # 10% penalty per 1% error rate
            
            # Cache performance impact
            if "cache_hit_rate" in metrics:
                cache_hit_rate = metrics["cache_hit_rate"].value
                if cache_hit_rate < 0.8:
                    score -= (0.8 - cache_hit_rate) * 100
            
            # Performance impact
            if "avg_retrieval_time" in metrics:
                retrieval_time = metrics["avg_retrieval_time"].value
                if retrieval_time > 1000:  # > 1 second
                    score -= (retrieval_time - 1000) / 100
            
            # Active critical alerts impact
            critical_alerts = await self.alert_manager.get_active_alerts(AlertSeverity.CRITICAL)
            score -= len(critical_alerts) * 20  # 20 points per critical alert
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 50.0  # Default moderate health


class PerformanceAnalyzer:
    """Advanced performance analytics engine"""
    
    def __init__(self):
        self.trend_cache: Dict[str, Dict[str, float]] = {}
        logger.info("Performance Analyzer initialized")
    
    async def analyze_performance(
        self,
        metric_history: Dict[str, List[MetricPoint]],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Comprehensive performance analysis"""



        try:
            analysis = {
                "analysis_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_hours": (end_time - start_time).total_seconds() / 3600
                },
                "metrics_analyzed": [],
                "trends": {},
                "anomalies": [],
                "performance_summary": {},
                "recommendations": []
            }
            
            for metric_name, history in metric_history.items():
                # Filter by time range
                period_data = [
                    point for point in history
                    if start_time <= point.timestamp <= end_time
                ]
                
                if not period_data:
                    continue
                
                analysis["metrics_analyzed"].append(metric_name)
                
                # Calculate trend
                trend = await self._calculate_trend(period_data)
                analysis["trends"][metric_name] = trend
                
                # Detect anomalies
                anomalies = await self._detect_anomalies(metric_name, period_data)
                analysis["anomalies"].extend(anomalies)
                
                # Performance summary
                values = [point.value for point in period_data]
                analysis["performance_summary"][metric_name] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "data_points": len(values)
                }
            
            # Generate recommendations
            analysis["recommendations"] = await self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_trend(self, data_points: List[MetricPoint]) -> Dict[str, float]:
        """Calculate trend analysis for metric data"""



        try:
            if len(data_points) < 2:
                return {"direction": 0, "slope": 0, "confidence": 0}
            
            # Simple linear trend calculation
            values = [point.value for point in data_points]
            n = len(values)
            
            # Calculate slope
            x_values = list(range(n))
            x_mean = sum(x_values) / n
            y_mean = sum(values) / n
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            slope = numerator / denominator if denominator != 0 else 0
            
            # Determine direction
            direction = 1 if slope > 0 else -1 if slope < 0 else 0
            
            # Calculate confidence (simplified R-squared)
            y_pred = [y_mean + slope * (x - x_mean) for x in x_values]
            ss_res = sum((y - y_pred) ** 2 for y, y_pred in zip(values, y_pred))
            ss_tot = sum((y - y_mean) ** 2 for y in values)
            
            confidence = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                "direction": direction,
                "slope": slope,
                "confidence": max(0, min(1, confidence))
            }
            
        except Exception as e:
            logger.error(f"Trend calculation failed: {e}")
            return {"direction": 0, "slope": 0, "confidence": 0}
    
    async def _detect_anomalies(self, metric_name: str, data_points: List[MetricPoint]) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data"""



        try:
            if len(data_points) < 10:  # Need sufficient data for anomaly detection
                return []
            
            values = [point.value for point in data_points]
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            
            anomalies = []
            threshold = 2.5  # 2.5 standard deviations
            
            for point in data_points:
                z_score = abs(point.value - mean_val) / std_val if std_val > 0 else 0
                
                if z_score > threshold:
                    anomalies.append({
                        "metric_name": metric_name,
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "expected_range": [mean_val - threshold * std_val, mean_val + threshold * std_val],
                        "deviation_score": z_score,
                        "severity": "high" if z_score > 3 else "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for {metric_name}: {e}")
            return []
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on analysis"""



        try:
            recommendations = []
            
            # Check error rate trend
            if "error_rate" in analysis["trends"]:
                error_trend = analysis["trends"]["error_rate"]
                if error_trend["direction"] > 0 and error_trend["confidence"] > 0.7:
                    recommendations.append(
                        "Error rate is trending upward. Consider reviewing recent changes and implementing additional error handling."
                    )
            
            # Check cache performance
            if "cache_hit_rate" in analysis["performance_summary"]:
                cache_stats = analysis["performance_summary"]["cache_hit_rate"]
                if cache_stats["mean"] < 0.8:
                    recommendations.append(
                        "Cache hit rate is below optimal (80%). Consider increasing cache size or reviewing cache eviction policies."
                    )
            
            # Check retrieval performance
            if "avg_retrieval_time" in analysis["performance_summary"]:
                retrieval_stats = analysis["performance_summary"]["avg_retrieval_time"]
                if retrieval_stats["mean"] > 1000:  # > 1 second
                    recommendations.append(
                        "Average retrieval time exceeds 1 second. Consider optimizing storage tiers or implementing prefetching."
                    )
            
            # Check anomalies
            high_severity_anomalies = [a for a in analysis["anomalies"] if a.get("severity") == "high"]
            if len(high_severity_anomalies) > 5:
                recommendations.append(
                    "Multiple high-severity anomalies detected. Consider implementing more robust monitoring and alerting."
                )
            
            # Default recommendation if none specific
            if not recommendations:
                recommendations.append("System performance appears normal. Continue monitoring trends.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to analysis error."]
