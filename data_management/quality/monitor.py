"""
Quality Monitor - Real-time Quality Monitoring System
==================================================

Enterprise-grade real-time quality monitoring system with alerting, trend analysis,
performance tracking, and automated quality assurance workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted under international copyright law.

Business Logic: Continuous monitoring → Quality tracking → Threshold detection → 
Alert generation → Trend analysis → Performance optimization → Automated responses
"""

import logging
import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics
from concurrent.futures import ThreadPoolExecutor

# Monitoring and alerting
try:
    import psutil
    import redis
    HAS_MONITORING_LIBS = True
except ImportError:
    HAS_MONITORING_LIBS = False

# Metrics and analytics
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_, or_, desc

from ..models.quality_models import QualityAssessment, QualityAlert, QualityTrend, MonitoringMetric


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    """Types of quality alerts"""
    QUALITY_DEGRADATION = "quality_degradation"
    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY_DETECTED = "anomaly_detected"
    SYSTEM_PERFORMANCE = "system_performance"
    COMPLIANCE_VIOLATION = "compliance_violation"
    TREND_ALERT = "trend_alert"
    VOLUME_ALERT = "volume_alert"


class MonitoringStatus(Enum):
    """Monitoring system status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class QualityThreshold:
    """Quality monitoring threshold definition"""
    name: str
    metric: str
    operator: str  # >, <, >=, <=, ==
    value: float
    severity: AlertSeverity
    description: str
    enabled: bool = True
    consecutive_violations: int = 1
    current_violations: int = 0


@dataclass
class QualityAlert:
    """Quality alert structure"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    threshold_name: Optional[str]
    metric_value: Optional[float]
    threshold_value: Optional[float]
    content_id: Optional[str]
    user_id: Optional[str]
    created_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringMetrics:
    """System monitoring metrics"""
    timestamp: datetime
    quality_scores: Dict[str, float]
    processing_times: Dict[str, float]
    system_metrics: Dict[str, float]
    content_volume: Dict[str, int]
    error_rates: Dict[str, float]
    user_metrics: Dict[str, float]


class MetricsCollector:
    """Metrics collection and aggregation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        
        # Metrics storage
        self.metrics_buffer = deque(maxlen=config.get('buffer_size', 1000))
        self.aggregated_metrics = {}
        
        # Prometheus metrics (if available)
        if HAS_PROMETHEUS:
            self.quality_score_histogram = Histogram(
                'quality_score_distribution',
                'Distribution of quality scores',
                buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
            )
            self.processing_time_histogram = Histogram(
                'processing_time_seconds',
                'Content processing time in seconds'
            )
            self.content_counter = Counter(
                'content_processed_total',
                'Total number of content items processed',
                ['content_type', 'quality_level']
            )
            self.system_metrics_gauge = Gauge(
                'system_performance',
                'System performance metrics',
                ['metric_name']
            )
    
    async def collect_metrics(
        self,
        quality_assessments: List[Dict[str, Any]],
        system_info: Optional[Dict[str, Any]] = None
    ) -> MonitoringMetrics:
        """Collect and aggregate quality metrics."""
        timestamp = datetime.utcnow()
        
        # Quality score metrics
        quality_scores = {}
        if quality_assessments:
            scores = [qa['overall_score'] for qa in quality_assessments]
            quality_scores = {
                'average': np.mean(scores),
                'median': np.median(scores),
                'std_dev': np.std(scores),
                'min': np.min(scores),
                'max': np.max(scores),
                'p95': np.percentile(scores, 95),
                'p99': np.percentile(scores, 99)
            }
            
            # Update Prometheus metrics
            if HAS_PROMETHEUS:
                for score in scores:
                    self.quality_score_histogram.observe(score)
        
        # Processing time metrics
        processing_times = {}
        if quality_assessments:
            times = [qa.get('processing_time', 0) for qa in quality_assessments if qa.get('processing_time')]
            if times:
                processing_times = {
                    'average': np.mean(times),
                    'median': np.median(times),
                    'p95': np.percentile(times, 95),
                    'p99': np.percentile(times, 99)
                }
                
                # Update Prometheus metrics
                if HAS_PROMETHEUS:
                    for time_val in times:
                        self.processing_time_histogram.observe(time_val)
        
        # System metrics
        system_metrics = {}
        if system_info:
            system_metrics = system_info
        elif HAS_MONITORING_LIBS:
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
            
            # Update Prometheus metrics
            if HAS_PROMETHEUS:
                for metric_name, value in system_metrics.items():
                    self.system_metrics_gauge.labels(metric_name=metric_name).set(value)
        
        # Content volume metrics
        content_volume = {}
        if quality_assessments:
            content_types = [qa['content_type'] for qa in quality_assessments]
            content_volume = dict(Counter(content_types))
            
            # Quality level distribution
            quality_levels = [qa.get('quality_level', 'unknown') for qa in quality_assessments]
            
            # Update Prometheus metrics
            if HAS_PROMETHEUS:
                for content_type in content_types:
                    for quality_level in quality_levels:
                        self.content_counter.labels(
                            content_type=content_type,
                            quality_level=quality_level
                        ).inc()
        
        # Error rate metrics (simplified)
        error_rates = {}
        if quality_assessments:
            total_assessments = len(quality_assessments)
            failed_assessments = len([qa for qa in quality_assessments if qa.get('status') == 'failed'])
            error_rates['overall_error_rate'] = failed_assessments / total_assessments if total_assessments > 0 else 0
        
        # User metrics (aggregated)
        user_metrics = {}
        if quality_assessments:
            user_scores = defaultdict(list)
            for qa in quality_assessments:
                if qa.get('user_id'):
                    user_scores[qa['user_id']].append(qa['overall_score'])
            
            if user_scores:
                user_metrics = {
                    'active_users': len(user_scores),
                    'avg_user_score': np.mean([np.mean(scores) for scores in user_scores.values()]),
                    'user_score_variance': np.var([np.mean(scores) for scores in user_scores.values()])
                }
        
        # Create metrics object
        metrics = MonitoringMetrics(
            timestamp=timestamp,
            quality_scores=quality_scores,
            processing_times=processing_times,
            system_metrics=system_metrics,
            content_volume=content_volume,
            error_rates=error_rates,
            user_metrics=user_metrics
        )
        
        # Add to buffer
        self.metrics_buffer.append(metrics)
        
        return metrics
    
    async def get_historical_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
        aggregation_interval: timedelta = timedelta(minutes=5)
    ) -> List[MonitoringMetrics]:
        """Get historical metrics from buffer."""
        historical_metrics = []
        
        for metrics in self.metrics_buffer:
            if start_time <= metrics.timestamp <= end_time:
                historical_metrics.append(metrics)
        
        # Sort by timestamp
        historical_metrics.sort(key=lambda m: m.timestamp)
        
        return historical_metrics


class AlertManager:
    """Alert management and notification system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AlertManager")
        
        # Alert storage
        self.active_alerts = {}
        self.alert_history = deque(maxlen=config.get('alert_history_size', 10000))
        
        # Alert suppression
        self.suppressed_alerts = set()
        self.alert_cooldowns = {}
        
        # Notification handlers
        self.notification_handlers = []
        
        # Default alert thresholds
        self.thresholds = [
            QualityThreshold(
                name="critical_quality_degradation",
                metric="quality_scores.average",
                operator="<",
                value=0.5,
                severity=AlertSeverity.CRITICAL,
                description="Average quality score below critical threshold",
                consecutive_violations=2
            ),
            QualityThreshold(
                name="high_processing_time",
                metric="processing_times.p95",
                operator=">",
                value=10.0,
                severity=AlertSeverity.HIGH,
                description="95th percentile processing time exceeds threshold",
                consecutive_violations=3
            ),
            QualityThreshold(
                name="high_error_rate",
                metric="error_rates.overall_error_rate",
                operator=">",
                value=0.1,
                severity=AlertSeverity.HIGH,
                description="Error rate exceeds 10%",
                consecutive_violations=2
            ),
            QualityThreshold(
                name="system_resource_high",
                metric="system_metrics.cpu_percent",
                operator=">",
                value=80.0,
                severity=AlertSeverity.MEDIUM,
                description="CPU usage exceeds 80%",
                consecutive_violations=5
            )
        ]
    
    async def check_thresholds(self, metrics: MonitoringMetrics) -> List[QualityAlert]:
        """Check metrics against defined thresholds."""
        alerts = []
        
        for threshold in self.thresholds:
            if not threshold.enabled:
                continue
            
            # Get metric value
            metric_value = self._get_metric_value(metrics, threshold.metric)
            if metric_value is None:
                continue
            
            # Check threshold
            violation = self._check_threshold_violation(metric_value, threshold)
            
            if violation:
                threshold.current_violations += 1
                
                # Check if consecutive violations threshold is met
                if threshold.current_violations >= threshold.consecutive_violations:
                    alert = await self._create_threshold_alert(threshold, metric_value, metrics)
                    alerts.append(alert)
                    
                    # Reset violation count after creating alert
                    threshold.current_violations = 0
            else:
                # Reset violation count if no violation
                threshold.current_violations = 0
        
        return alerts
    
    def _get_metric_value(self, metrics: MonitoringMetrics, metric_path: str) -> Optional[float]:
        """Get metric value from metrics object using dot notation."""



        try:
            parts = metric_path.split('.')
            value = metrics
            
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            
            return float(value) if value is not None else None
            
        except (AttributeError, KeyError, ValueError, TypeError):
            return None
    
    def _check_threshold_violation(self, metric_value: float, threshold: QualityThreshold) -> bool:
        """Check if metric value violates threshold."""
        if threshold.operator == ">":
            return metric_value > threshold.value
        elif threshold.operator == "<":
            return metric_value < threshold.value
        elif threshold.operator == ">=":
            return metric_value >= threshold.value
        elif threshold.operator == "<=":
            return metric_value <= threshold.value
        elif threshold.operator == "==":
            return abs(metric_value - threshold.value) < 0.001  # Float comparison
        else:
            return False
    
    async def _create_threshold_alert(
        self,
        threshold: QualityThreshold,
        metric_value: float,
        metrics: MonitoringMetrics
    ) -> QualityAlert:
        """Create alert for threshold violation."""
        alert_id = f"alert_{int(datetime.utcnow().timestamp())}_{threshold.name}"
        
        alert = QualityAlert(
            alert_id=alert_id,
            alert_type=AlertType.THRESHOLD_BREACH,
            severity=threshold.severity,
            title=f"Threshold Violation: {threshold.name}",
            description=f"{threshold.description}. Current value: {metric_value:.3f}, Threshold: {threshold.value}",
            threshold_name=threshold.name,
            metric_value=metric_value,
            threshold_value=threshold.value,
            content_id=None,
            user_id=None,
            created_at=datetime.utcnow(),
            metadata={
                'metric_path': threshold.metric,
                'operator': threshold.operator,
                'consecutive_violations': threshold.consecutive_violations
            }
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(f"Alert created: {alert.title}")
        
        # Send notifications
        await self._send_notifications(alert)
        
        return alert
    
    async def create_custom_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        content_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityAlert:
        """Create custom alert."""
        alert_id = f"custom_{int(datetime.utcnow().timestamp())}"
        
        alert = QualityAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            threshold_name=None,
            metric_value=None,
            threshold_value=None,
            content_id=content_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        self.logger.info(f"Custom alert created: {title}")
        
        # Send notifications
        await self._send_notifications(alert)
        
        return alert
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            
            self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert {alert_id} resolved")
            return True
        
        return False
    
    async def get_active_alerts(
        self,
        severity_filter: Optional[AlertSeverity] = None,
        alert_type_filter: Optional[AlertType] = None
    ) -> List[QualityAlert]:
        """Get list of active alerts with optional filtering."""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        if alert_type_filter:
            alerts = [a for a in alerts if a.alert_type == alert_type_filter]
        
        # Sort by severity and creation time
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
            AlertSeverity.INFO: 4
        }
        
        alerts.sort(key=lambda a: (severity_order[a.severity], a.created_at))
        
        return alerts
    
    async def _send_notifications(self, alert: QualityAlert):
        """Send alert notifications."""
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Notification handler failed: {str(e)}")
    
    def add_notification_handler(self, handler: Callable[[QualityAlert], None]):
        """Add notification handler."""
        self.notification_handlers.append(handler)


class TrendAnalyzer:
    """Quality trend analysis system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.TrendAnalyzer")
        
        # Trend detection parameters
        self.trend_window = config.get('trend_window_hours', 24)
        self.trend_sensitivity = config.get('trend_sensitivity', 0.1)
        self.min_data_points = config.get('min_data_points', 10)
    
    async def analyze_trends(
        self,
        historical_metrics: List[MonitoringMetrics],
        lookback_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze quality trends from historical metrics."""
        if len(historical_metrics) < self.min_data_points:
            return {'status': 'insufficient_data', 'trends': {}}
        
        # Sort by timestamp
        sorted_metrics = sorted(historical_metrics, key=lambda m: m.timestamp)
        
        # Filter by lookback period
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        recent_metrics = [m for m in sorted_metrics if m.timestamp >= cutoff_time]
        
        if len(recent_metrics) < self.min_data_points:
            return {'status': 'insufficient_recent_data', 'trends': {}}
        
        trends = {}
        
        # Quality score trends
        quality_trends = await self._analyze_quality_score_trends(recent_metrics)
        trends['quality_scores'] = quality_trends
        
        # Processing time trends
        performance_trends = await self._analyze_performance_trends(recent_metrics)
        trends['performance'] = performance_trends
        
        # Volume trends
        volume_trends = await self._analyze_volume_trends(recent_metrics)
        trends['volume'] = volume_trends
        
        # Error rate trends
        error_trends = await self._analyze_error_rate_trends(recent_metrics)
        trends['error_rates'] = error_trends
        
        # Overall trend summary
        overall_trend = await self._calculate_overall_trend(trends)
        
        return {
            'status': 'success',
            'analysis_period': f"{recent_metrics[0].timestamp} to {recent_metrics[-1].timestamp}",
            'data_points': len(recent_metrics),
            'trends': trends,
            'overall_trend': overall_trend
        }
    
    async def _analyze_quality_score_trends(self, metrics: List[MonitoringMetrics]) -> Dict[str, Any]:
        """Analyze quality score trends."""
        scores = [m.quality_scores.get('average', 0) for m in metrics if m.quality_scores]
        
        if len(scores) < 2:
            return {'status': 'insufficient_data'}
        
        # Calculate trend direction and strength
        x = np.arange(len(scores))
        
        # Linear regression
        slope, intercept = np.polyfit(x, scores, 1)
        correlation = np.corrcoef(x, scores)[0, 1]
        
        # Determine trend direction
        if abs(slope) < self.trend_sensitivity:
            direction = 'stable'
        elif slope > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        # Calculate trend strength
        strength = abs(correlation)
        if strength >= 0.8:
            strength_level = 'strong'
        elif strength >= 0.5:
            strength_level = 'moderate'
        else:
            strength_level = 'weak'
        
        # Recent change
        recent_change = scores[-1] - scores[0] if len(scores) >= 2 else 0
        recent_change_percent = (recent_change / scores[0] * 100) if scores[0] != 0 else 0
        
        return {
            'status': 'analyzed',
            'direction': direction,
            'strength': strength_level,
            'slope': slope,
            'correlation': correlation,
            'recent_change': recent_change,
            'recent_change_percent': recent_change_percent,
            'current_value': scores[-1],
            'trend_data': scores
        }
    
    async def _analyze_performance_trends(self, metrics: List[MonitoringMetrics]) -> Dict[str, Any]:
        """Analyze processing time trends."""
        times = [m.processing_times.get('average', 0) for m in metrics if m.processing_times]
        
        if len(times) < 2:
            return {'status': 'insufficient_data'}
        
        # Similar analysis to quality scores
        x = np.arange(len(times))
        slope, intercept = np.polyfit(x, times, 1)
        correlation = np.corrcoef(x, times)[0, 1]
        
        # For processing times, increasing is bad, decreasing is good
        if abs(slope) < 0.01:  # 0.01 seconds threshold
            direction = 'stable'
        elif slope > 0:
            direction = 'degrading'
        else:
            direction = 'improving'
        
        strength = abs(correlation)
        strength_level = 'strong' if strength >= 0.8 else 'moderate' if strength >= 0.5 else 'weak'
        
        return {
            'status': 'analyzed',
            'direction': direction,
            'strength': strength_level,
            'slope': slope,
            'correlation': correlation,
            'current_value': times[-1],
            'trend_data': times
        }
    
    async def _analyze_volume_trends(self, metrics: List[MonitoringMetrics]) -> Dict[str, Any]:
        """Analyze content volume trends."""
        volumes = [sum(m.content_volume.values()) for m in metrics if m.content_volume]
        
        if len(volumes) < 2:
            return {'status': 'insufficient_data'}
        
        x = np.arange(len(volumes))
        slope, intercept = np.polyfit(x, volumes, 1)
        correlation = np.corrcoef(x, volumes)[0, 1]
        
        if abs(slope) < 1:  # 1 item threshold
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        strength = abs(correlation)
        strength_level = 'strong' if strength >= 0.8 else 'moderate' if strength >= 0.5 else 'weak'
        
        return {
            'status': 'analyzed',
            'direction': direction,
            'strength': strength_level,
            'slope': slope,
            'correlation': correlation,
            'current_value': volumes[-1],
            'trend_data': volumes
        }
    
    async def _analyze_error_rate_trends(self, metrics: List[MonitoringMetrics]) -> Dict[str, Any]:
        """Analyze error rate trends."""
        error_rates = [m.error_rates.get('overall_error_rate', 0) for m in metrics if m.error_rates]
        
        if len(error_rates) < 2:
            return {'status': 'insufficient_data'}
        
        x = np.arange(len(error_rates))
        slope, intercept = np.polyfit(x, error_rates, 1)
        correlation = np.corrcoef(x, error_rates)[0, 1]
        
        # For error rates, increasing is bad, decreasing is good
        if abs(slope) < 0.001:  # 0.1% threshold
            direction = 'stable'
        elif slope > 0:
            direction = 'worsening'
        else:
            direction = 'improving'
        
        strength = abs(correlation)
        strength_level = 'strong' if strength >= 0.8 else 'moderate' if strength >= 0.5 else 'weak'
        
        return {
            'status': 'analyzed',
            'direction': direction,
            'strength': strength_level,
            'slope': slope,
            'correlation': correlation,
            'current_value': error_rates[-1],
            'trend_data': error_rates
        }
    
    async def _calculate_overall_trend(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system trend."""
        trend_scores = []
        
        # Quality score trend (weight: 40%)
        quality_trend = trends.get('quality_scores', {})
        if quality_trend.get('status') == 'analyzed':
            if quality_trend['direction'] == 'improving':
                trend_scores.append(0.4 * 1.0)
            elif quality_trend['direction'] == 'declining':
                trend_scores.append(0.4 * -1.0)
            else:
                trend_scores.append(0.4 * 0.0)
        
        # Performance trend (weight: 30%)
        perf_trend = trends.get('performance', {})
        if perf_trend.get('status') == 'analyzed':
            if perf_trend['direction'] == 'improving':
                trend_scores.append(0.3 * 1.0)
            elif perf_trend['direction'] == 'degrading':
                trend_scores.append(0.3 * -1.0)
            else:
                trend_scores.append(0.3 * 0.0)
        
        # Error rate trend (weight: 20%)
        error_trend = trends.get('error_rates', {})
        if error_trend.get('status') == 'analyzed':
            if error_trend['direction'] == 'improving':
                trend_scores.append(0.2 * 1.0)
            elif error_trend['direction'] == 'worsening':
                trend_scores.append(0.2 * -1.0)
            else:
                trend_scores.append(0.2 * 0.0)
        
        # Volume trend (weight: 10%)
        volume_trend = trends.get('volume', {})
        if volume_trend.get('status') == 'analyzed':
            if volume_trend['direction'] == 'increasing':
                trend_scores.append(0.1 * 1.0)
            elif volume_trend['direction'] == 'decreasing':
                trend_scores.append(0.1 * -1.0)
            else:
                trend_scores.append(0.1 * 0.0)
        
        if not trend_scores:
            return {'status': 'insufficient_data'}
        
        overall_score = sum(trend_scores)
        
        if overall_score > 0.3:
            overall_direction = 'positive'
        elif overall_score < -0.3:
            overall_direction = 'negative'
        else:
            overall_direction = 'neutral'
        
        return {
            'status': 'calculated',
            'direction': overall_direction,
            'score': overall_score,
            'confidence': len(trend_scores) / 4.0  # 4 possible trend components
        }


class QualityMonitor:
    """
    Enterprise quality monitoring system.
    
    Provides real-time monitoring of quality metrics, automated alerting,
    trend analysis, and performance tracking for the quality management system.
    """
    
    def __init__(
        self,
        db_session: sessionmaker,
        config: Optional[Dict[str, Any]] = None
    ):
        self.db_session = db_session
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.metrics_collector = MetricsCollector(self.config.get('metrics', {}))
        self.alert_manager = AlertManager(self.config.get('alerts', {}))
        self.trend_analyzer = TrendAnalyzer(self.config.get('trends', {}))
        
        # Monitoring state
        self.status = MonitoringStatus.STOPPED
        self.monitoring_task = None
        self.monitoring_interval = self.config.get('monitoring_interval_seconds', 60)
        
        # Data collection
        self.collection_batch_size = self.config.get('collection_batch_size', 100)
        self.max_age_hours = self.config.get('max_data_age_hours', 168)  # 1 week
        
        # Performance tracking
        self.performance_stats = {
            'monitoring_cycles': 0,
            'alerts_generated': 0,
            'trends_analyzed': 0,
            'last_collection_time': None,
            'avg_collection_time': 0.0
        }
        
        self.logger.info("QualityMonitor initialized successfully")
    
    async def start_monitoring(self):
        """Start continuous quality monitoring."""
        if self.status == MonitoringStatus.ACTIVE:
            self.logger.warning("Monitoring already active")
            return
        
        self.status = MonitoringStatus.ACTIVE
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("Quality monitoring started")
    
    async def stop_monitoring(self):
        """Stop quality monitoring."""
        if self.status != MonitoringStatus.ACTIVE:
            return
        
        self.status = MonitoringStatus.STOPPED
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Quality monitoring stopped")
    
    async def pause_monitoring(self):
        """Pause quality monitoring."""
        if self.status == MonitoringStatus.ACTIVE:
            self.status = MonitoringStatus.PAUSED
            self.logger.info("Quality monitoring paused")
    
    async def resume_monitoring(self):
        """Resume quality monitoring."""
        if self.status == MonitoringStatus.PAUSED:
            self.status = MonitoringStatus.ACTIVE
            self.logger.info("Quality monitoring resumed")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.info("Starting monitoring loop")
        
        while self.status != MonitoringStatus.STOPPED:
            try:
                if self.status == MonitoringStatus.ACTIVE:
                    await self._perform_monitoring_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                self.status = MonitoringStatus.ERROR
                await asyncio.sleep(self.monitoring_interval)
    
    async def _perform_monitoring_cycle(self):
        """Perform one monitoring cycle."""
        cycle_start = datetime.utcnow()
        
        try:
            # Collect quality data
            quality_data = await self._collect_quality_data()
            
            # Collect system metrics
            system_info = await self._collect_system_info()
            
            # Generate monitoring metrics
            metrics = await self.metrics_collector.collect_metrics(quality_data, system_info)
            
            # Check thresholds and generate alerts
            alerts = await self.alert_manager.check_thresholds(metrics)
            
            # Perform trend analysis periodically
            if self.performance_stats['monitoring_cycles'] % 10 == 0:  # Every 10 cycles
                await self._perform_trend_analysis()
            
            # Update performance stats
            cycle_time = (datetime.utcnow() - cycle_start).total_seconds()
            self.performance_stats['monitoring_cycles'] += 1
            self.performance_stats['alerts_generated'] += len(alerts)
            self.performance_stats['last_collection_time'] = cycle_start
            
            # Update average collection time
            if self.performance_stats['avg_collection_time'] == 0:
                self.performance_stats['avg_collection_time'] = cycle_time
            else:
                # Exponential moving average
                alpha = 0.1
                self.performance_stats['avg_collection_time'] = (
                    alpha * cycle_time + (1 - alpha) * self.performance_stats['avg_collection_time']
                )
            
            self.logger.debug(f"Monitoring cycle completed in {cycle_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Monitoring cycle failed: {str(e)}")
            self.status = MonitoringStatus.ERROR
    
    async def _collect_quality_data(self) -> List[Dict[str, Any]]:
        """Collect recent quality assessment data."""



        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=self.monitoring_interval // 60 + 5)
            
            async with self.db_session() as session:
                # Query recent quality assessments
                query = session.query(QualityAssessment).filter(
                    QualityAssessment.created_at >= cutoff_time
                ).order_by(desc(QualityAssessment.created_at)).limit(self.collection_batch_size)
                
                results = await query.all()
                
                # Convert to dictionaries
                quality_data = []
                for result in results:
                    quality_data.append({
                        'id': result.id,
                        'user_id': result.user_id,
                        'content_type': result.content_type,
                        'overall_score': result.overall_score,
                        'quality_level': result.quality_level,
                        'processing_time': result.processing_time,
                        'status': getattr(result, 'status', 'completed'),
                        'created_at': result.created_at,
                        'dimension_scores': result.dimension_scores or {}
                    })
                
                return quality_data
                
        except Exception as e:
            self.logger.error(f"Error collecting quality data: {str(e)}")
            return []
    
    async def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system performance information."""
        system_info = {}
        
        try:
            if HAS_MONITORING_LIBS:
                system_info = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'network_connections': len(psutil.net_connections()),
                    'process_count': len(psutil.pids())
                }
                
                # Load average (if available)
                if hasattr(psutil, 'getloadavg'):
                    load1, load5, load15 = psutil.getloadavg()
                    system_info.update({
                        'load_1min': load1,
                        'load_5min': load5,
                        'load_15min': load15
                    })
            
        except Exception as e:
            self.logger.error(f"Error collecting system info: {str(e)}")
        
        return system_info
    
    async def _perform_trend_analysis(self):
        """Perform periodic trend analysis."""



        try:
            # Get historical metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            historical_metrics = await self.metrics_collector.get_historical_metrics(
                start_time, end_time
            )
            
            # Analyze trends
            trend_analysis = await self.trend_analyzer.analyze_trends(historical_metrics)
            
            # Generate trend alerts if needed
            await self._check_trend_alerts(trend_analysis)
            
            self.performance_stats['trends_analyzed'] += 1
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
    
    async def _check_trend_alerts(self, trend_analysis: Dict[str, Any]):
        """Check if trend analysis should generate alerts."""
        if trend_analysis.get('status') != 'success':
            return
        
        overall_trend = trend_analysis.get('overall_trend', {})
        
        # Alert on negative trends
        if (overall_trend.get('direction') == 'negative' and 
            overall_trend.get('confidence', 0) > 0.7):
            
            await self.alert_manager.create_custom_alert(
                alert_type=AlertType.TREND_ALERT,
                severity=AlertSeverity.MEDIUM,
                title="Negative Quality Trend Detected",
                description=f"Overall quality trend is negative with {overall_trend['confidence']:.1%} confidence",
                metadata={
                    'trend_score': overall_trend.get('score', 0),
                    'confidence': overall_trend.get('confidence', 0),
                    'analysis_period': trend_analysis.get('analysis_period', 'unknown')
                }
            )
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status and statistics."""



        return {
            'status': self.status.value,
            'monitoring_interval': self.monitoring_interval,
            'performance_stats': self.performance_stats.copy(),
            'active_alerts_count': len(self.alert_manager.active_alerts),
            'metrics_buffer_size': len(self.metrics_collector.metrics_buffer),
            'last_cycle_time': self.performance_stats.get('last_collection_time'),
            'uptime_seconds': (
                (datetime.utcnow() - self.performance_stats['last_collection_time']).total_seconds()
                if self.performance_stats['last_collection_time'] else 0
            )
        }
    
    async def get_current_metrics(self) -> Optional[MonitoringMetrics]:
        """Get most recent monitoring metrics."""
        if self.metrics_collector.metrics_buffer:
            return self.metrics_collector.metrics_buffer[-1]
        return None
    
    async def get_alerts(
        self,
        severity_filter: Optional[AlertSeverity] = None,
        limit: int = 50
    ) -> List[QualityAlert]:
        """Get recent alerts with optional filtering."""
        alerts = await self.alert_manager.get_active_alerts(severity_filter)
        return alerts[:limit]
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""



        return await self.alert_manager.acknowledge_alert(alert_id, acknowledged_by)
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""



        return await self.alert_manager.resolve_alert(alert_id)
    
    async def add_custom_threshold(
        self,
        name: str,
        metric: str,
        operator: str,
        value: float,
        severity: AlertSeverity,
        description: str,
        consecutive_violations: int = 1
    ) -> bool:
        """Add custom monitoring threshold."""



        try:
            threshold = QualityThreshold(
                name=name,
                metric=metric,
                operator=operator,
                value=value,
                severity=severity,
                description=description,
                consecutive_violations=consecutive_violations
            )
            
            self.alert_manager.thresholds.append(threshold)
            self.logger.info(f"Added custom threshold: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding custom threshold: {str(e)}")
            return False
    
    async def remove_threshold(self, threshold_name: str) -> bool:
        """Remove a monitoring threshold."""



        try:
            self.alert_manager.thresholds = [
                t for t in self.alert_manager.thresholds 
                if t.name != threshold_name
            ]
            self.logger.info(f"Removed threshold: {threshold_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing threshold: {str(e)}")
            return False
    
    async def get_trend_analysis(
        self,
        lookback_hours: int = 24
    ) -> Dict[str, Any]:
        """Get current trend analysis."""



        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=lookback_hours)
            
            historical_metrics = await self.metrics_collector.get_historical_metrics(
                start_time, end_time
            )
            
            return await self.trend_analyzer.analyze_trends(historical_metrics, lookback_hours)
            
        except Exception as e:
            self.logger.error(f"Error getting trend analysis: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def export_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
        format: str = 'json'
    ) -> Union[str, Dict[str, Any]]:
        """Export metrics data for external analysis."""



        try:
            historical_metrics = await self.metrics_collector.get_historical_metrics(
                start_time, end_time
            )
            
            if format == 'json':
                return {
                    'export_time': datetime.utcnow().isoformat(),
                    'period': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat()
                    },
                    'metrics_count': len(historical_metrics),
                    'metrics': [
                        {
                            'timestamp': m.timestamp.isoformat(),
                            'quality_scores': m.quality_scores,
                            'processing_times': m.processing_times,
                            'system_metrics': m.system_metrics,
                            'content_volume': m.content_volume,
                            'error_rates': m.error_rates,
                            'user_metrics': m.user_metrics
                        }
                        for m in historical_metrics
                    ]
                }
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup_old_data(self):
        """Clean up old monitoring data."""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.max_age_hours)
            
            # Clean up metrics buffer
            self.metrics_collector.metrics_buffer = deque(
                [m for m in self.metrics_collector.metrics_buffer if m.timestamp >= cutoff_time],
                maxlen=self.metrics_collector.config.get('buffer_size', 1000)
            )
            
            # Clean up alert history
            self.alert_manager.alert_history = deque(
                [a for a in self.alert_manager.alert_history if a.created_at >= cutoff_time],
                maxlen=self.alert_manager.config.get('alert_history_size', 10000)
            )
            
            self.logger.info("Cleaned up old monitoring data")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
    
    async def shutdown(self):
        """Shutdown the monitoring system."""
        self.logger.info("Shutting down QualityMonitor")
        
        await self.stop_monitoring()
        await self.cleanup_old_data()
        
        self.logger.info("QualityMonitor shutdown completed")
