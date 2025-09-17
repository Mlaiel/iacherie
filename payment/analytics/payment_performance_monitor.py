"""🚀 Payment Performance Monitor - Enterprise Performance Analytics Engine
=========================================================================

Real-time payment system performance monitoring and SLA compliance tracking.
DevOps-grade performance analytics with advanced alerting and optimization.

Performance Targets: < 10ms monitoring operations
Enterprise SLA monitoring and alert management system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from decimal import Decimal
from collections import defaultdict, deque
import statistics

# Enterprise monitoring and alerting
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import structlog

logger = structlog.get_logger(__name__)

class PerformanceMetricType(Enum):
    """Performance metric types for comprehensive monitoring"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    LATENCY = "latency"
    SUCCESS_RATE = "success_rate"
    QUEUE_DEPTH = "queue_depth"
    CONNECTION_POOL = "connection_pool"
    MEMORY_USAGE = "memory_usage"
    CPU_UTILIZATION = "cpu_utilization"

class SLALevel(Enum):
    """SLA compliance levels"""
    CRITICAL = "critical"  # 99.9% uptime
    HIGH = "high"         # 99.5% uptime
    STANDARD = "standard" # 99.0% uptime
    BASIC = "basic"       # 95.0% uptime

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class PerformanceThresholds:
    """Performance thresholds configuration"""
    response_time_ms: float = 100.0
    error_rate_percent: float = 1.0
    availability_percent: float = 99.9
    throughput_rps: float = 1000.0
    latency_p95_ms: float = 200.0
    latency_p99_ms: float = 500.0
    queue_depth_max: int = 100
    memory_usage_percent: float = 80.0
    cpu_utilization_percent: float = 70.0

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    threshold_breached: bool = False
    severity: AlertSeverity = AlertSeverity.INFO

@dataclass
class SLAStatus:
    """SLA compliance status"""
    sla_level: SLALevel
    current_availability: float
    target_availability: float
    compliance: bool
    breach_count: int = 0
    last_breach: Optional[datetime] = None
    mttr_minutes: float = 0.0  # Mean Time To Recovery
    mtbf_hours: float = 0.0    # Mean Time Between Failures

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    metric_type: PerformanceMetricType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    tags: Dict[str, str] = field(default_factory=dict)

class PerformanceTracker:
    """Enterprise performance tracking engine"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=10000)
        self.active_alerts = {}
        self.registry = CollectorRegistry()
        self._init_prometheus_metrics()
        
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics collectors"""
        self.response_time_histogram = Histogram(
            'payment_response_time_seconds',
            'Payment response time',
            buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry
        )
        
        self.error_counter = Counter(
            'payment_errors_total',
            'Total payment errors',
            ['error_type', 'gateway'],
            registry=self.registry
        )
        
        self.throughput_gauge = Gauge(
            'payment_throughput_rps',
            'Payment throughput (requests per second)',
            registry=self.registry
        )
        
        self.availability_gauge = Gauge(
            'payment_availability_percent',
            'Payment system availability percentage',
            registry=self.registry
        )
        
    async def record_metric(
        self,
        metric_type: PerformanceMetricType,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> PerformanceMetric:
        """Record performance metric with enterprise tracking"""
        try:
            start_time = time.perf_counter()
            
            tags = tags or {}
            timestamp = datetime.utcnow()
            
            # Create metric
            metric = PerformanceMetric(
                metric_type=metric_type,
                value=value,
                timestamp=timestamp,
                tags=tags
            )
            
            # Record in Prometheus
            await self._record_prometheus_metric(metric)
            
            # Store in history
            self.metrics_history.append(metric)
            
            # Performance logging
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Performance metric recorded",
                metric_type=metric_type.value,
                value=value,
                duration_ms=duration_ms,
                tags=tags
            )
            
            return metric
            
        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")
            raise
    
    async def _record_prometheus_metric(self, metric: PerformanceMetric):
        """Record metric in Prometheus"""
        if metric.metric_type == PerformanceMetricType.RESPONSE_TIME:
            self.response_time_histogram.observe(metric.value / 1000)
        elif metric.metric_type == PerformanceMetricType.THROUGHPUT:
            self.throughput_gauge.set(metric.value)
        elif metric.metric_type == PerformanceMetricType.AVAILABILITY:
            self.availability_gauge.set(metric.value)
        elif metric.metric_type == PerformanceMetricType.ERROR_RATE:
            error_type = metric.tags.get('error_type', 'unknown')
            gateway = metric.tags.get('gateway', 'unknown')
            self.error_counter.labels(error_type=error_type, gateway=gateway).inc()
    
    async def get_metrics_summary(
        self,
        metric_type: Optional[PerformanceMetricType] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        try:
            cutoff_time = datetime.utcnow() - time_window
            
            # Filter metrics
            relevant_metrics = [
                m for m in self.metrics_history
                if m.timestamp >= cutoff_time and (
                    metric_type is None or m.metric_type == metric_type
                )
            ]
            
            if not relevant_metrics:
                return {"message": "No metrics available", "count": 0}
            
            # Calculate statistics
            values = [m.value for m in relevant_metrics]
            
            summary = {
                "count": len(relevant_metrics),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "p95": self._calculate_percentile(values, 95),
                "p99": self._calculate_percentile(values, 99),
                "stddev": statistics.stdev(values) if len(values) > 1 else 0,
                "time_window_hours": time_window.total_seconds() / 3600
            }
            
            logger.info("Metrics summary generated", **summary)
            return summary
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            raise
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

class SLAMonitor:
    """Enterprise SLA monitoring and compliance tracking"""
    
    def __init__(self):
        self.sla_history = deque(maxlen=10000)
        self.breach_incidents = []
        self.downtime_tracker = defaultdict(list)
        
    async def monitor_sla_compliance(
        self,
        sla_level: SLALevel,
        current_metrics: Dict[str, float],
        time_window: timedelta = timedelta(hours=24)
    ) -> SLAStatus:
        """Monitor SLA compliance with enterprise tracking"""
        try:
            start_time = time.perf_counter()
            
            # Define SLA targets
            sla_targets = {
                SLALevel.CRITICAL: 99.9,
                SLALevel.HIGH: 99.5,
                SLALevel.STANDARD: 99.0,
                SLALevel.BASIC: 95.0
            }
            
            target_availability = sla_targets[sla_level]
            current_availability = current_metrics.get('availability', 0.0)
            
            # Check compliance
            compliance = current_availability >= target_availability
            
            # Calculate MTTR and MTBF
            mttr = await self._calculate_mttr(time_window)
            mtbf = await self._calculate_mtbf(time_window)
            
            # Count breaches
            breach_count = len([
                incident for incident in self.breach_incidents
                if incident['timestamp'] >= datetime.utcnow() - time_window
            ])
            
            # Get last breach
            last_breach = None
            if self.breach_incidents:
                last_breach = max(
                    incident['timestamp'] for incident in self.breach_incidents
                )
            
            sla_status = SLAStatus(
                sla_level=sla_level,
                current_availability=current_availability,
                target_availability=target_availability,
                compliance=compliance,
                breach_count=breach_count,
                last_breach=last_breach,
                mttr_minutes=mttr,
                mtbf_hours=mtbf
            )
            
            # Record SLA status
            self.sla_history.append({
                'timestamp': datetime.utcnow(),
                'sla_status': sla_status,
                'compliance': compliance
            })
            
            # Log SLA breach if needed
            if not compliance:
                await self._record_sla_breach(sla_level, current_availability, target_availability)
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "SLA compliance monitored",
                sla_level=sla_level.value,
                compliance=compliance,
                current_availability=current_availability,
                target_availability=target_availability,
                duration_ms=duration_ms
            )
            
            return sla_status
            
        except Exception as e:
            logger.error(f"Error monitoring SLA compliance: {e}")
            raise
    
    async def _calculate_mttr(self, time_window: timedelta) -> float:
        """Calculate Mean Time To Recovery"""
        recent_incidents = [
            incident for incident in self.breach_incidents
            if incident['timestamp'] >= datetime.utcnow() - time_window
            and incident.get('resolved_at')
        ]
        
        if not recent_incidents:
            return 0.0
        
        recovery_times = [
            (incident['resolved_at'] - incident['timestamp']).total_seconds() / 60
            for incident in recent_incidents
        ]
        
        return statistics.mean(recovery_times)
    
    async def _calculate_mtbf(self, time_window: timedelta) -> float:
        """Calculate Mean Time Between Failures"""
        recent_incidents = [
            incident for incident in self.breach_incidents
            if incident['timestamp'] >= datetime.utcnow() - time_window
        ]
        
        if len(recent_incidents) < 2:
            return 0.0
        
        # Sort by timestamp
        recent_incidents.sort(key=lambda x: x['timestamp'])
        
        # Calculate time between failures
        intervals = []
        for i in range(1, len(recent_incidents)):
            interval = (recent_incidents[i]['timestamp'] - recent_incidents[i-1]['timestamp']).total_seconds() / 3600
            intervals.append(interval)
        
        return statistics.mean(intervals) if intervals else 0.0
    
    async def _record_sla_breach(
        self,
        sla_level: SLALevel,
        current_availability: float,
        target_availability: float
    ):
        """Record SLA breach incident"""
        incident = {
            'timestamp': datetime.utcnow(),
            'sla_level': sla_level.value,
            'current_availability': current_availability,
            'target_availability': target_availability,
            'breach_percentage': target_availability - current_availability
        }
        
        self.breach_incidents.append(incident)
        
        logger.warning(
            "SLA breach recorded",
            **incident
        )

class AlertManager:
    """Enterprise alert management and notification system"""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = deque(maxlen=10000)
        self.escalation_rules = {}
        
    async def create_alert(
        self,
        metric_type: PerformanceMetricType,
        severity: AlertSeverity,
        message: str,
        tags: Optional[Dict[str, str]] = None
    ) -> PerformanceAlert:
        """Create performance alert with enterprise tracking"""
        try:
            start_time = time.perf_counter()
            
            alert_id = f"{metric_type.value}_{int(time.time())}"
            tags = tags or {}
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                metric_type=metric_type,
                severity=severity,
                message=message,
                timestamp=datetime.utcnow(),
                tags=tags
            )
            
            # Store active alert
            self.active_alerts[alert_id] = alert
            
            # Add to history
            self.alert_history.append(alert)
            
            # Handle escalation
            await self._handle_alert_escalation(alert)
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.warning(
                "Performance alert created",
                alert_id=alert_id,
                metric_type=metric_type.value,
                severity=severity.value,
                message=message,
                duration_ms=duration_ms
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                logger.info("Alert acknowledged", alert_id=alert_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                del self.active_alerts[alert_id]
                logger.info("Alert resolved", alert_id=alert_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    async def _handle_alert_escalation(self, alert: PerformanceAlert):
        """Handle alert escalation based on severity"""
        if alert.severity == AlertSeverity.CRITICAL:
            # Immediate escalation for critical alerts
            await self._escalate_to_oncall(alert)
        elif alert.severity == AlertSeverity.HIGH:
            # Schedule escalation if not acknowledged within 15 minutes
            await self._schedule_escalation(alert, timedelta(minutes=15))

    async def _escalate_to_oncall(self, alert: PerformanceAlert):
        """Escalate to on-call team"""
        logger.critical(
            "Critical alert escalated to on-call",
            alert_id=alert.alert_id,
            message=alert.message
        )
    
    async def _schedule_escalation(self, alert: PerformanceAlert, delay: timedelta):
        """Schedule alert escalation"""
        # In production, this would integrate with alerting systems
        logger.warning(
            "Alert escalation scheduled",
            alert_id=alert.alert_id,
            delay_minutes=delay.total_seconds() / 60
        )

class PaymentPerformanceMonitor:
    """Enterprise payment performance monitoring orchestrator"""
    
    def __init__(self, thresholds: Optional[PerformanceThresholds] = None):
        self.thresholds = thresholds or PerformanceThresholds()
        self.performance_tracker = PerformanceTracker()
        self.sla_monitor = SLAMonitor()
        self.alert_manager = AlertManager()
        
        # Performance optimization
        self._metrics_cache = {}
        self._cache_ttl = 60  # seconds
        
    async def monitor_payment_performance(
        self,
        payment_metrics: Dict[str, float],
        sla_level: SLALevel = SLALevel.HIGH
    ) -> Dict[str, Any]:
        """Comprehensive payment performance monitoring"""
        try:
            start_time = time.perf_counter()
            
            # Record all metrics
            recorded_metrics = []
            for metric_name, value in payment_metrics.items():
                try:
                    metric_type = PerformanceMetricType(metric_name)
                    metric = await self.performance_tracker.record_metric(
                        metric_type, value
                    )
                    recorded_metrics.append(metric)
                    
                    # Check thresholds and create alerts
                    await self._check_threshold_and_alert(metric_type, value)
                    
                except ValueError:
                    logger.warning(f"Unknown metric type: {metric_name}")
            
            # Monitor SLA compliance
            sla_status = await self.sla_monitor.monitor_sla_compliance(
                sla_level, payment_metrics
            )
            
            # Generate performance summary
            summary = await self.performance_tracker.get_metrics_summary()
            
            # Get active alerts
            active_alerts = list(self.alert_manager.active_alerts.values())
            
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "recorded_metrics": len(recorded_metrics),
                "sla_status": {
                    "level": sla_status.sla_level.value,
                    "compliance": sla_status.compliance,
                    "availability": sla_status.current_availability,
                    "target": sla_status.target_availability,
                    "breach_count": sla_status.breach_count,
                    "mttr_minutes": sla_status.mttr_minutes,
                    "mtbf_hours": sla_status.mtbf_hours
                },
                "performance_summary": summary,
                "active_alerts": len(active_alerts),
                "performance_score": await self._calculate_performance_score(
                    payment_metrics, sla_status
                )
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Payment performance monitoring completed",
                duration_ms=duration_ms,
                performance_score=result["performance_score"],
                active_alerts=len(active_alerts)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error monitoring payment performance: {e}")
            raise
    
    async def _check_threshold_and_alert(
        self,
        metric_type: PerformanceMetricType,
        value: float
    ):
        """Check performance thresholds and create alerts"""
        threshold_checks = {
            PerformanceMetricType.RESPONSE_TIME: (
                value > self.thresholds.response_time_ms,
                f"Response time {value}ms exceeds threshold {self.thresholds.response_time_ms}ms"
            ),
            PerformanceMetricType.ERROR_RATE: (
                value > self.thresholds.error_rate_percent,
                f"Error rate {value}% exceeds threshold {self.thresholds.error_rate_percent}%"
            ),
            PerformanceMetricType.AVAILABILITY: (
                value < self.thresholds.availability_percent,
                f"Availability {value}% below threshold {self.thresholds.availability_percent}%"
            ),
            PerformanceMetricType.THROUGHPUT: (
                value < self.thresholds.throughput_rps,
                f"Throughput {value} RPS below threshold {self.thresholds.throughput_rps} RPS"
            )
        }
        
        if metric_type in threshold_checks:
            breach, message = threshold_checks[metric_type]
            if breach:
                severity = self._determine_alert_severity(metric_type, value)
                await self.alert_manager.create_alert(
                    metric_type, severity, message
                )
    
    def _determine_alert_severity(
        self,
        metric_type: PerformanceMetricType,
        value: float
    ) -> AlertSeverity:
        """Determine alert severity based on metric and value"""
        if metric_type == PerformanceMetricType.AVAILABILITY:
            if value < 95.0:
                return AlertSeverity.CRITICAL
            elif value < 99.0:
                return AlertSeverity.HIGH
            else:
                return AlertSeverity.MEDIUM
        elif metric_type == PerformanceMetricType.RESPONSE_TIME:
            if value > 1000:  # 1 second
                return AlertSeverity.CRITICAL
            elif value > 500:  # 500ms
                return AlertSeverity.HIGH
            else:
                return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.MEDIUM
    
    async def _calculate_performance_score(
        self,
        metrics: Dict[str, float],
        sla_status: SLAStatus
    ) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            scores = []
            
            # Availability score (40% weight)
            availability = metrics.get('availability', 0)
            availability_score = min(100, availability)
            scores.append(availability_score * 0.4)
            
            # Response time score (30% weight)
            response_time = metrics.get('response_time', 1000)
            response_time_score = max(0, 100 - (response_time / 10))  # 1000ms = 0 score
            scores.append(response_time_score * 0.3)
            
            # Error rate score (20% weight)
            error_rate = metrics.get('error_rate', 100)
            error_rate_score = max(0, 100 - (error_rate * 10))  # 10% error = 0 score
            scores.append(error_rate_score * 0.2)
            
            # SLA compliance score (10% weight)
            sla_score = 100 if sla_status.compliance else 0
            scores.append(sla_score * 0.1)
            
            return sum(scores)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 0.0
    
    async def track_sla_compliance(
        self,
        sla_level: SLALevel = SLALevel.HIGH,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Track SLA compliance with comprehensive reporting"""
        try:
            # Get current metrics from tracker
            current_metrics = await self._get_current_metrics()
            
            # Monitor SLA
            sla_status = await self.sla_monitor.monitor_sla_compliance(
                sla_level, current_metrics, time_window
            )
            
            # Calculate compliance trends
            compliance_trend = await self._calculate_compliance_trend(time_window)
            
            result = {
                "sla_level": sla_status.sla_level.value,
                "current_availability": sla_status.current_availability,
                "target_availability": sla_status.target_availability,
                "compliance": sla_status.compliance,
                "breach_count": sla_status.breach_count,
                "last_breach": sla_status.last_breach.isoformat() if sla_status.last_breach else None,
                "mttr_minutes": sla_status.mttr_minutes,
                "mtbf_hours": sla_status.mtbf_hours,
                "compliance_trend": compliance_trend,
                "time_window_hours": time_window.total_seconds() / 3600
            }
            
            logger.info("SLA compliance tracked", **result)
            return result
            
        except Exception as e:
            logger.error(f"Error tracking SLA compliance: {e}")
            raise
    
    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        # In production, this would aggregate real-time metrics
        return {
            'availability': 99.5,
            'response_time': 150.0,
            'error_rate': 0.5,
            'throughput': 800.0
        }
    
    async def _calculate_compliance_trend(self, time_window: timedelta) -> str:
        """Calculate SLA compliance trend"""
        cutoff_time = datetime.utcnow() - time_window
        recent_sla_records = [
            record for record in self.sla_monitor.sla_history
            if record['timestamp'] >= cutoff_time
        ]
        
        if len(recent_sla_records) < 2:
            return "insufficient_data"
        
        # Calculate trend based on compliance rate
        compliance_rates = [
            record['compliance'] for record in recent_sla_records
        ]
        
        recent_rate = sum(compliance_rates[-10:]) / min(10, len(compliance_rates))
        older_rate = sum(compliance_rates[:10]) / min(10, len(compliance_rates))
        
        if recent_rate > older_rate + 0.1:
            return "improving"
        elif recent_rate < older_rate - 0.1:
            return "degrading"
        else:
            return "stable"
    
    async def analyze_performance_trends(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Analyze performance trends and patterns"""
        try:
            start_time = time.perf_counter()
            
            # Get metrics summary
            summary = await self.performance_tracker.get_metrics_summary(
                time_window=time_window
            )
            
            # Get SLA compliance data
            sla_data = await self.track_sla_compliance(time_window=time_window)
            
            # Analyze alert patterns
            alert_analysis = await self._analyze_alert_patterns(time_window)
            
            # Performance insights
            insights = await self._generate_performance_insights(summary, sla_data)
            
            result = {
                "time_window_hours": time_window.total_seconds() / 3600,
                "metrics_summary": summary,
                "sla_analysis": sla_data,
                "alert_patterns": alert_analysis,
                "performance_insights": insights,
                "recommendations": await self._generate_performance_recommendations(
                    summary, sla_data, alert_analysis
                )
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Performance trends analyzed",
                duration_ms=duration_ms,
                insights_count=len(insights)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            raise
    
    async def _analyze_alert_patterns(self, time_window: timedelta) -> Dict[str, Any]:
        """Analyze alert patterns and frequencies"""
        cutoff_time = datetime.utcnow() - time_window
        
        recent_alerts = [
            alert for alert in self.alert_manager.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        if not recent_alerts:
            return {"total_alerts": 0, "patterns": []}
        
        # Group by severity
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert.severity.value] += 1
        
        # Group by metric type
        metric_counts = defaultdict(int)
        for alert in recent_alerts:
            metric_counts[alert.metric_type.value] += 1
        
        return {
            "total_alerts": len(recent_alerts),
            "severity_distribution": dict(severity_counts),
            "metric_distribution": dict(metric_counts),
            "average_alerts_per_hour": len(recent_alerts) / (time_window.total_seconds() / 3600)
        }
    
    async def _generate_performance_insights(
        self,
        summary: Dict[str, Any],
        sla_data: Dict[str, Any]
    ) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        # Response time insights
        if summary.get('p95', 0) > self.thresholds.response_time_ms:
            insights.append(f"95th percentile response time ({summary['p95']:.1f}ms) exceeds threshold")
        
        # SLA insights
        if not sla_data.get('compliance', True):
            insights.append(f"SLA breach detected - availability {sla_data['current_availability']:.2f}%")
        
        # Trend insights
        if sla_data.get('compliance_trend') == 'degrading':
            insights.append("Performance trend is degrading - investigate root cause")
        
        return insights
    
    async def _generate_performance_recommendations(
        self,
        summary: Dict[str, Any],
        sla_data: Dict[str, Any],
        alert_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # High response time
        if summary.get('p95', 0) > self.thresholds.response_time_ms:
            recommendations.append("Consider scaling payment processing infrastructure")
            recommendations.append("Implement response time optimization strategies")
        
        # High alert frequency
        alert_rate = alert_analysis.get('average_alerts_per_hour', 0)
        if alert_rate > 5:
            recommendations.append("High alert frequency - review threshold configuration")
        
        # SLA issues
        if not sla_data.get('compliance', True):
            recommendations.append("Implement SLA recovery procedures")
            recommendations.append("Review availability monitoring and alerting")
        
        return recommendations

# Performance optimization decorator
def performance_monitor(func):
    """Decorator for monitoring function performance"""
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            if duration_ms > 10:  # Log if over 10ms
                logger.warning(
                    f"Function {func.__name__} took {duration_ms:.2f}ms",
                    function=func.__name__,
                    duration_ms=duration_ms
                )
            
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Function {func.__name__} failed after {duration_ms:.2f}ms",
                function=func.__name__,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise
    return wrapper

if __name__ == "__main__":
    # Enterprise testing and validation
    async def test_performance_monitoring():
        """Test performance monitoring functionality"""
        monitor = PaymentPerformanceMonitor()
        
        # Test metrics
        test_metrics = {
            'response_time': 75.0,
            'throughput': 1200.0,
            'error_rate': 0.3,
            'availability': 99.8
        }
        
        # Monitor performance
        result = await monitor.monitor_payment_performance(test_metrics)
        print(f"Performance monitoring result: {json.dumps(result, indent=2)}")
        
        # Analyze trends
        trends = await monitor.analyze_performance_trends()
        print(f"Performance trends: {json.dumps(trends, indent=2)}")
    
    # Run tests
    asyncio.run(test_performance_monitoring())