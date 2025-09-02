"""🎯 Quality Monitor - Real-time Quality Monitoring System

Professional audio quality monitoring system for continuous quality tracking,
alerting, and performance analysis. Provides real-time monitoring, historical
analysis, and automated quality reporting.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import deque, defaultdict
import statistics

from .metrics import QualityMetrics, QualityReport
from .validator import ValidationResult

logger = logging.getLogger(__name__)


class MonitoringLevel(Enum):
    """
Monitoring detail levels"""

    BASIC = "basic"           # Basic metrics only
    STANDARD = "standard"     # Standard monitoring
    DETAILED = "detailed"     # Detailed analysis
    DIAGNOSTIC = "diagnostic" # Full diagnostic monitoring


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of quality alerts"""

    QUALITY_DEGRADATION = "quality_degradation"
    THRESHOLD_BREACH = "threshold_breach"
    SYSTEM_ERROR = "system_error"
    PERFORMANCE_ISSUE = "performance_issue"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class QualityAlert:
    """Quality monitoring alert"""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    alert_id: str = field(default_factory=lambda: f"alert_{datetime.now().isoformat()}")


@dataclass
class MonitoringMetrics:
    """Real-time monitoring metrics"""
    average_score: float
    minimum_score: float
    maximum_score: float
    score_trend: float  # Positive = improving, negative = degrading
    processing_time_avg: float
    processing_time_max: float
    success_rate: float
    error_rate: float
    throughput: float  # Files per minute
    active_alerts: int
    total_processed: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityTrend:
    """
Quality trend analysis"""
    period: str
    trend_direction: str  # "improving", "stable", "degrading"
    trend_strength: float  # 0.0 to 1.0
    average_change: float
    significant_events: List[str]
    recommendations: List[str]


class QualityMonitor:
    """
    🎯 Professional Audio Quality Monitor
    
    Real-time quality monitoring system:
    - Continuous quality tracking
    - Alert generation and management
    - Performance analytics
    - Trend analysis
    - Historical reporting
    - Automated notifications
    """
    
    def __init__(self, monitoring_level: MonitoringLevel = MonitoringLevel.STANDARD):
        self.monitoring_level = monitoring_level
        
        # Historical data storage
        self.quality_history = deque(maxlen=10000)
        self.processing_times = deque(maxlen=1000)
        self.error_history = deque(maxlen=1000)
        
        # Real-time metrics
        self.current_metrics = MonitoringMetrics(
            average_score=0.0,
            minimum_score=1.0,
            maximum_score=0.0,
            score_trend=0.0,
            processing_time_avg=0.0,
            processing_time_max=0.0,
            success_rate=1.0,
            error_rate=0.0,
            throughput=0.0,
            active_alerts=0,
            total_processed=0
        )
        
        # Alert management
        self.active_alerts: Dict[str, QualityAlert] = {}
        self.alert_history = deque(maxlen=1000)
        self.alert_handlers: List[Callable] = []
        
        # Thresholds and rules
        self.quality_thresholds = {
            'critical_min': 0.3,
            'warning_min': 0.6,
            'degradation_threshold': 0.1,  # 10% degradation triggers alert
            'max_processing_time': 30.0,   # seconds
            'max_error_rate': 0.05         # 5%
        }
        
        # Performance tracking
        self.performance_window = timedelta(minutes=5)
        self.trend_window = timedelta(hours=1)
        
        # Background monitoring task
        self.monitoring_task = None
        self.is_monitoring = False
        
        logger.info(f"QualityMonitor initialized with {monitoring_level.value} level")
    
    async def start_monitoring(self):
        """Start background monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Quality monitoring started")
    
    async def stop_monitoring(self):
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "stop_monitoring",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
        try:
            logger.info(f"Executing record_quality_result")
            
            # Implementation for record_quality_result
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"record_quality_result completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"record_quality_result failed: {e}")
            raise
            self.error_history.append({
                'timestamp': timestamp,
                'error': error_details
            })
        
        # Update real-time metrics
        await self._update_metrics()
        
        # Check for alerts
        await self._check_alerts(quality_report, processing_time, success)
        
        logger.debug(f"Recorded quality result: score={quality_report.overall_score:.3f}, "
                    f"time={processing_time:.2f}s, success={success}")
    
    async def record_quality_decision(self, decision, validation_result: QualityReport):
        """Record a quality control decision"""
        await self.record_quality_result(
            validation_result,
            decision.processing_time,
            success=decision.action.value != "reject"
        )
    
    async def get_current_metrics(self) -> MonitoringMetrics:
        """Get current monitoring metrics"""
        await self._update_metrics()
        return self.current_metrics
    
    async def get_quality_trends(self, period: timedelta = None) -> QualityTrend:
        """
Analyze quality trends over specified period"""
        if period is None:
            period = self.trend_window
        
        cutoff_time = datetime.now() - period
        recent_data = [
            d for d in self.quality_history 
            if d['timestamp'] >= cutoff_time and d['success']
        ]
        
        if len(recent_data) < 10:
            return QualityTrend(
                period=str(period),
                trend_direction="insufficient_data",
                trend_strength=0.0,
                average_change=0.0,
                significant_events=[],
                recommendations=["Need more data for trend analysis"]
            )
        
        # Calculate trend
        scores = [d['score'] for d in recent_data]
        times = [(d['timestamp'] - cutoff_time).total_seconds() for d in recent_data]
        
        # Linear regression for trend
        if len(scores) > 1:
            correlation = np.corrcoef(times, scores)[0, 1]
            trend_strength = abs(correlation)
            
            # Determine trend direction
            if correlation > 0.1:
                trend_direction = "improving"
            elif correlation < -0.1:
                trend_direction = "degrading"
            else:
                trend_direction = "stable"
            
            # Calculate average change
            average_change = (scores[-1] - scores[0]) / len(scores)
        else:
            trend_direction = "stable"
            trend_strength = 0.0
            average_change = 0.0
        
        # Identify significant events
        significant_events = []
        if trend_direction == "degrading" and trend_strength > 0.5:
            significant_events.append("Significant quality degradation detected")
        
        # Generate recommendations
        recommendations = []
        if trend_direction == "degrading":
            recommendations.append("Investigate causes of quality degradation")
            recommendations.append("Review recent changes to audio processing pipeline")
        elif trend_direction == "stable" and np.mean(scores) < 0.7:
            recommendations.append("Consider optimizing quality thresholds")
        
        return QualityTrend(
            period=str(period),
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            average_change=average_change,
            significant_events=significant_events,
            recommendations=recommendations
        )
    
    async def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [d for d in self.quality_history if d['timestamp'] >= cutoff_time]
        
        if not recent_data:
            return {
                'period': f"{hours} hours",
                'status': 'no_data',
                'message': 'No data available for the specified period'
            }
        
        successful_data = [d for d in recent_data if d['success']]
        failed_data = [d for d in recent_data if not d['success']]
        
        # Basic statistics
        total_processed = len(recent_data)
        success_count = len(successful_data)
        error_count = len(failed_data)
        
        # Quality statistics
        if successful_data:
            quality_scores = [d['score'] for d in successful_data]
            processing_times = [d['processing_time'] for d in successful_data]
            
            quality_stats = {
                'average': statistics.mean(quality_scores),
                'median': statistics.median(quality_scores),
                'std_dev': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
                'minimum': min(quality_scores),
                'maximum': max(quality_scores),
                'percentile_95': np.percentile(quality_scores, 95),
                'percentile_5': np.percentile(quality_scores, 5)
            }
            
            performance_stats = {
                'average_time': statistics.mean(processing_times),
                'median_time': statistics.median(processing_times),
                'max_time': max(processing_times),
                'min_time': min(processing_times),
                'percentile_95_time': np.percentile(processing_times, 95)
            }
        else:
            quality_stats = {}
            performance_stats = {}
        
        # Calculate throughput
        if hours > 0:
            throughput_per_hour = total_processed / hours
        else:
            throughput_per_hour = 0
        
        # Alert summary
        period_alerts = [
            alert for alert in self.alert_history 
            if alert.timestamp >= cutoff_time
        ]
        
        alert_summary = {
            'total_alerts': len(period_alerts),
            'critical_alerts': len([a for a in period_alerts if a.severity == AlertSeverity.CRITICAL]),
            'error_alerts': len([a for a in period_alerts if a.severity == AlertSeverity.ERROR]),
            'warning_alerts': len([a for a in period_alerts if a.severity == AlertSeverity.WARNING]),
            'resolved_alerts': len([a for a in period_alerts if a.resolved])
        }
        
        # Trend analysis
        trend = await self.get_quality_trends(timedelta(hours=hours))
        
        return {
            'period': f"{hours} hours",
            'timestamp': datetime.now().isoformat(),
            'overview': {
                'total_processed': total_processed,
                'successful': success_count,
                'failed': error_count,
                'success_rate': success_count / max(total_processed, 1),
                'error_rate': error_count / max(total_processed, 1),
                'throughput_per_hour': throughput_per_hour
            },
            'quality_statistics': quality_stats,
            'performance_statistics': performance_stats,
            'alert_summary': alert_summary,
            'trend_analysis': {
                'direction': trend.trend_direction,
                'strength': trend.trend_strength,
                'significant_events': trend.significant_events,
                'recommendations': trend.recommendations
            },
            'active_alerts': len(self.active_alerts)
        }
    
    async def add_alert_handler(self, handler: Callable[[QualityAlert], None]):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
        logger.info("Added custom alert handler")
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            logger.info(f"Resolved alert: {alert_id}")
            return True
        
        return False
    
    async def get_active_alerts(self) -> List[QualityAlert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, hours: int = 24) -> List[QualityAlert]:
        """
Get alert history for specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
    
    async def _monitoring_loop(self):
        """
Background monitoring loop"""
        while self.is_monitoring:
            try:
                await self._update_metrics()
                await self._cleanup_old_data()
                await asyncio.sleep(10)  # Update every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(30)  # Back off on error
    
    async def _update_metrics(self):
        """Update current monitoring metrics"""
        now = datetime.now()
        window_start = now - self.performance_window
        
        # Get recent data within performance window
        recent_data = [d for d in self.quality_history if d['timestamp'] >= window_start]
        
        if not recent_data:
            return
        
        successful_data = [d for d in recent_data if d['success']]
        
        # Update metrics
        if successful_data:
            scores = [d['score'] for d in successful_data]
            times = [d['processing_time'] for d in successful_data]
            
            self.current_metrics.average_score = statistics.mean(scores)
            self.current_metrics.minimum_score = min(scores)
            self.current_metrics.maximum_score = max(scores)
            self.current_metrics.processing_time_avg = statistics.mean(times)
            self.current_metrics.processing_time_max = max(times)
            
            # Calculate trend (simple linear correlation with time)
            if len(scores) > 5:
                time_series = list(range(len(scores)))
                correlation = np.corrcoef(time_series, scores)[0, 1]
                self.current_metrics.score_trend = correlation
        
        # Calculate rates
        total_recent = len(recent_data)
        success_count = len(successful_data)
        error_count = total_recent - success_count
        
        self.current_metrics.success_rate = success_count / max(total_recent, 1)
        self.current_metrics.error_rate = error_count / max(total_recent, 1)
        
        # Calculate throughput (files per minute)
        window_minutes = self.performance_window.total_seconds() / 60
        self.current_metrics.throughput = total_recent / max(window_minutes, 1)
        
        # Update counters
        self.current_metrics.active_alerts = len(self.active_alerts)
        self.current_metrics.total_processed = len(self.quality_history)
        self.current_metrics.timestamp = now
    
    async def _check_alerts(
        self,
        quality_report: QualityReport,
        processing_time: float,
        success: bool
    ):
        """
Check for alert conditions"""
        
        # Critical quality threshold
        if success and quality_report.overall_score < self.quality_thresholds['critical_min']:
        try:
            logger.info(f"Executing _check_alerts")
            
            # Implementation for _check_alerts
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_check_alerts completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_check_alerts failed: {e}")
            raise
                }
            )
    
    async def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        details: Dict[str, Any]
    ):
        """Create and process a new alert"""
        
        alert = QualityAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            details=details
        )
        
        # Check for duplicate alerts (prevent spam)
        similar_alerts = [
            a for a in self.active_alerts.values()
            if a.alert_type == alert_type and a.severity == severity
        ]
        
        if similar_alerts and (datetime.now() - similar_alerts[0].timestamp).seconds < 300:
            logger.debug(f"Suppressing duplicate alert: {message}")
            return
        
        # Add to active alerts
        self.active_alerts[alert.alert_id] = alert
        
        # Log alert
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }[severity]
        
        logger.log(log_level, f"Quality Alert [{severity.value.upper()}]: {message}")
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                await asyncio.get_event_loop().run_in_executor(None, handler, alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        # Auto-resolve old alerts (24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        expired_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.timestamp < cutoff_time
        ]
        
        for alert_id in expired_alerts:
            await self.resolve_alert(alert_id)
    
    def configure_thresholds(self, thresholds: Dict[str, float]):
        """
Configure alert thresholds"""
        self.quality_thresholds.update(thresholds)
        logger.info(f"Updated quality thresholds: {thresholds}")
    
    async def export_metrics(self, format: str = "json") -> str:
        """Export monitoring metrics"""
        data = {
            'current_metrics': {
                'average_score': self.current_metrics.average_score,
                'minimum_score': self.current_metrics.minimum_score,
                'maximum_score': self.current_metrics.maximum_score,
                'score_trend': self.current_metrics.score_trend,
                'processing_time_avg': self.current_metrics.processing_time_avg,
                'processing_time_max': self.current_metrics.processing_time_max,
                'success_rate': self.current_metrics.success_rate,
                'error_rate': self.current_metrics.error_rate,
                'throughput': self.current_metrics.throughput,
                'active_alerts': self.current_metrics.active_alerts,
                'total_processed': self.current_metrics.total_processed,
                'timestamp': self.current_metrics.timestamp.isoformat()
            },
            'active_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'details': alert.details
                }
                for alert in self.active_alerts.values()
            ],
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def health_check(self) -> bool:
        """Perform monitor health check"""
        try:
            # Check if monitoring is active
            if not self.is_monitoring:
                return False
            
            # Check if we have recent data
            if self.quality_history and len(self.quality_history) > 0:
                latest_data = max(self.quality_history, key=lambda x: x['timestamp'])
                time_since_last = (datetime.now() - latest_data['timestamp']).total_seconds()
                
                # Consider healthy if we have data from the last 5 minutes
                return time_since_last < 300
            
            # No data yet, but monitoring is active
            return True
            
        except Exception as e:
            logger.error(f"Monitor health check failed: {e}")
            return False
