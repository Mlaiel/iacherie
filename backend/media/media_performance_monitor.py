"""Media Performance Monitor - Advanced Media Performance Analytics & Monitoring
=============================================================================

Advanced performance monitoring system providing comprehensive media performance tracking,
real-time analytics, performance optimization recommendations, and system health monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary performance monitoring system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or monitoring technology appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import time
import psutil
import statistics
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from collections import defaultdict, deque
import hashlib
import threading

# Performance monitoring imports with graceful fallbacks
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logging.warning("psutil not available - limited system monitoring")

try:
    import prometheus_client
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logging.warning("Prometheus client not available - using basic metrics")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not available - using basic calculations")

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Performance metric types"""
    SYSTEM = "system"
    APPLICATION = "application"
    MEDIA = "media"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    API = "api"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MonitoringScope(Enum):
    """Monitoring scope"""
    GLOBAL = "global"
    SERVICE = "service"
    ENDPOINT = "endpoint"
    RESOURCE = "resource"
    USER = "user"


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    # Collection settings
    collection_interval_seconds: int = 30
    metric_retention_hours: int = 168  # 7 days
    alert_check_interval_seconds: int = 60
    
    # Thresholds
    cpu_warning_threshold: float = 70.0
    cpu_critical_threshold: float = 90.0
    memory_warning_threshold: float = 80.0
    memory_critical_threshold: float = 95.0
    disk_warning_threshold: float = 85.0
    disk_critical_threshold: float = 95.0
    
    # Performance thresholds
    response_time_warning_ms: float = 1000.0
    response_time_critical_ms: float = 5000.0
    error_rate_warning_percent: float = 5.0
    error_rate_critical_percent: float = 10.0
    
    # Advanced settings
    enable_predictions: bool = True
    enable_anomaly_detection: bool = True
    enable_auto_scaling_recommendations: bool = True
    
    # Alert settings
    enable_alerts: bool = True
    alert_cooldown_minutes: int = 15
    max_alerts_per_hour: int = 20


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """System health status"""
    component: str
    status: HealthStatus
    score: float  # 0-100
    metrics: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    component: str
    metric_name: str
    current_value: float
    threshold_value: float
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    acknowledgment: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceTrend:
    """Performance trend analysis"""
    metric_name: str
    component: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    prediction: Optional[Dict[str, Any]] = None
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    analysis_period: timedelta = field(default_factory=lambda: timedelta(hours=24))
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SystemMetricsCollector:
    """Collects system-level performance metrics"""
    
    def __init__(self, config -> None: MonitoringConfig) -> None:
        self.config = config
        self.metrics_buffer = deque(maxlen=1000)
        self.collection_active = False
        
        logger.info("📊 System Metrics Collector initialized")
    
    async def start_collection(self) -> None:
        """Start metrics collection"""
        try:
            self.collection_active = True
            asyncio.create_task(self._collection_loop())
            logger.info("System metrics collection started")
            
        except Exception as e:
            logger.error(f"Failed to start metrics collection: {e}")
    
    async def stop_collection(self) -> None:
        """Stop metrics collection"""
        self.collection_active = False
        logger.info("System metrics collection stopped")
    
    async def collect_current_metrics(self) -> List[PerformanceMetric]:
        """Collect current system metrics"""
        try:
            metrics = []
            timestamp = datetime.now(timezone.utc)
            
            if HAS_PSUTIL:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.SYSTEM,
                    name="cpu_usage_percent",
                    value=cpu_percent,
                    unit="percent",
                    timestamp=timestamp
                ))
                
                # Memory metrics
                memory = psutil.virtual_memory()
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.SYSTEM,
                    name="memory_usage_percent",
                    value=memory.percent,
                    unit="percent",
                    timestamp=timestamp
                ))
                
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.SYSTEM,
                    name="memory_available_gb",
                    value=memory.available / (1024**3),
                    unit="gigabytes",
                    timestamp=timestamp
                ))
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.SYSTEM,
                    name="disk_usage_percent",
                    value=disk_percent,
                    unit="percent",
                    timestamp=timestamp
                ))
                
                # Network metrics
                network = psutil.net_io_counters()
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.NETWORK,
                    name="network_bytes_sent",
                    value=network.bytes_sent,
                    unit="bytes",
                    timestamp=timestamp
                ))
                
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.NETWORK,
                    name="network_bytes_received",
                    value=network.bytes_recv,
                    unit="bytes",
                    timestamp=timestamp
                ))
                
                # Load average (Unix systems)
                try:
                    load_avg = psutil.getloadavg()
                    metrics.append(PerformanceMetric(
                        metric_id=str(uuid.uuid4()),
                        metric_type=MetricType.SYSTEM,
                        name="load_average_1min",
                        value=load_avg[0],
                        unit="ratio",
                        timestamp=timestamp
                    ))
                except (AttributeError, OSError):
                    # getloadavg not available on Windows
                    pass
            
            # Add custom application metrics
            app_metrics = await self._collect_application_metrics(timestamp)
            metrics.extend(app_metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return []
    
    async def _collection_loop(self) -> None:
        """Main collection loop"""
        while self.collection_active:
            try:
                metrics = await self.collect_current_metrics()
                
                # Add metrics to buffer
                for metric in metrics:
                    self.metrics_buffer.append(metric)
                
                # Wait for next collection interval
                await asyncio.sleep(self.config.collection_interval_seconds)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.config.collection_interval_seconds)
    
    async def _collect_application_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect application-specific metrics"""
        metrics = []
        
        # Process count
        try:
            process_count = len(psutil.pids()) if HAS_PSUTIL else 0
            metrics.append(PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.APPLICATION,
                name="process_count",
                value=process_count,
                unit="count",
                timestamp=timestamp
            ))
        except:
            pass
        
        # Thread count for current process
        try:
            thread_count = threading.active_count()
            metrics.append(PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.APPLICATION,
                name="thread_count",
                value=thread_count,
                unit="count",
                timestamp=timestamp
            ))
        except:
            pass
        
        return metrics
    
    def get_recent_metrics(self, metric_name: str, minutes: int = 60) -> List[PerformanceMetric]:
        """Get recent metrics for specific metric name"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        return [
            metric for metric in self.metrics_buffer
            if metric.name == metric_name and metric.timestamp >= cutoff_time
        ]


class PerformanceAnalyzer:
    """Analyzes performance metrics and detects issues"""
    
    def __init__(self, config -> None: MonitoringConfig) -> None:
        self.config = config
        self.trend_cache = {}
        self.baseline_metrics = {}
        
        logger.info("📈 Performance Analyzer initialized")
    
    async def analyze_metrics(
        self, 
        metrics: List[PerformanceMetric],
        component: str = "system"
    ) -> Dict[str, Any]:
        """Analyze performance metrics for insights"""
        try:
            analysis = {
                'component': component,
                'health_score': 100.0,
                'issues': [],
                'recommendations': [],
                'trends': {},
                'anomalies': [],
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            if not metrics:
                analysis['health_score'] = 0.0
                analysis['issues'].append("No metrics available for analysis")
                return analysis
            
            # Group metrics by name
            metrics_by_name = defaultdict(list)
            for metric in metrics:
                metrics_by_name[metric.name].append(metric)
            
            # Analyze each metric type
            for metric_name, metric_list in metrics_by_name.items():
                metric_analysis = await self._analyze_metric_series(metric_name, metric_list)
                
                # Update overall health score
                if metric_analysis['health_impact'] < 0:
                    analysis['health_score'] += metric_analysis['health_impact']
                
                # Add issues and recommendations
                analysis['issues'].extend(metric_analysis.get('issues', []))
                analysis['recommendations'].extend(metric_analysis.get('recommendations', []))
                analysis['trends'][metric_name] = metric_analysis.get('trend', {})
                
                # Add anomalies
                if metric_analysis.get('anomalies'):
                    analysis['anomalies'].extend(metric_analysis['anomalies'])
            
            # Ensure health score is within bounds
            analysis['health_score'] = max(0.0, min(100.0, analysis['health_score']))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {
                'component': component,
                'health_score': 0.0,
                'error': str(e),
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def _analyze_metric_series(
        self, 
        metric_name: str, 
        metrics: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Analyze a series of metrics for a specific metric type"""
        if not metrics:
            return {'health_impact': 0, 'issues': [], 'recommendations': []}
        
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        values = [m.value for m in sorted_metrics]
        
        analysis = {
            'health_impact': 0,
            'issues': [],
            'recommendations': [],
            'trend': {},
            'anomalies': []
        }
        
        # Current value analysis
        current_value = values[-1] if values else 0
        analysis['current_value'] = current_value
        
        # Threshold analysis
        threshold_analysis = self._check_thresholds(metric_name, current_value)
        analysis['health_impact'] += threshold_analysis['health_impact']
        analysis['issues'].extend(threshold_analysis['issues'])
        analysis['recommendations'].extend(threshold_analysis['recommendations'])
        
        # Trend analysis
        if len(values) >= 3:
            trend_analysis = self._analyze_trend(metric_name, values)
            analysis['trend'] = trend_analysis
            
            # Health impact from trends
            if trend_analysis.get('concerning', False):
                analysis['health_impact'] -= 10
                analysis['issues'].append(f"{metric_name} shows concerning trend: {trend_analysis.get('description', 'unknown')}")
        
        # Anomaly detection
        if len(values) >= 10 and self.config.enable_anomaly_detection:
            anomalies = self._detect_anomalies(metric_name, values)
            analysis['anomalies'] = anomalies
            
            if anomalies:
                analysis['health_impact'] -= len(anomalies) * 5
                analysis['issues'].append(f"{len(anomalies)} anomalies detected in {metric_name}")
        
        return analysis
    
    def _check_thresholds(self, metric_name: str, value: float) -> Dict[str, Any]:
        """Check if metric value exceeds thresholds"""
        result = {'health_impact': 0, 'issues': [], 'recommendations': []}
        
        # Define thresholds for different metrics
        thresholds = {
            'cpu_usage_percent': {
                'warning': self.config.cpu_warning_threshold,
                'critical': self.config.cpu_critical_threshold
            },
            'memory_usage_percent': {
                'warning': self.config.memory_warning_threshold,
                'critical': self.config.memory_critical_threshold
            },
            'disk_usage_percent': {
                'warning': self.config.disk_warning_threshold,
                'critical': self.config.disk_critical_threshold
            }
        }
        
        if metric_name in thresholds:
            metric_thresholds = thresholds[metric_name]
            
            if value >= metric_thresholds.get('critical', 100):
                result['health_impact'] = -50
                result['issues'].append(f"{metric_name} is critically high: {value:.1f}%")
                result['recommendations'].append(f"Immediate action required for {metric_name}")
                
            elif value >= metric_thresholds.get('warning', 80):
                result['health_impact'] = -20
                result['issues'].append(f"{metric_name} is above warning threshold: {value:.1f}%")
                result['recommendations'].append(f"Monitor {metric_name} closely and consider optimization")
        
        return result
    
    def _analyze_trend(self, metric_name: str, values: List[float]) -> Dict[str, Any]:
        """Analyze trend in metric values"""
        if len(values) < 3:
            return {}
        
        # Calculate simple linear trend
        x = list(range(len(values)))
        y = values
        
        # Simple linear regression
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0
        
        # Determine trend direction and strength
        trend_direction = "stable"
        if slope > 0.1:
            trend_direction = "increasing"
        elif slope < -0.1:
            trend_direction = "decreasing"
        
        # Calculate trend strength (correlation coefficient approximation)
        if n > 1:
            mean_y = sum_y / n
            variance_y = sum((yi - mean_y) ** 2 for yi in y) / n
            trend_strength = abs(slope) / max(variance_y, 0.001)
            trend_strength = min(trend_strength, 1.0)
        else:
            trend_strength = 0.0
        
        # Determine if trend is concerning
        concerning = False
        description = f"{trend_direction} trend"
        
        if metric_name in ['cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent']:
            if trend_direction == "increasing" and trend_strength > 0.5:
                concerning = True
                description = f"Rapidly increasing {metric_name}"
        
        return {
            'direction': trend_direction,
            'strength': trend_strength,
            'slope': slope,
            'concerning': concerning,
            'description': description
        }
    
    def _detect_anomalies(self, metric_name: str, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values"""
        if len(values) < 10:
            return []
        
        anomalies = []
        
        # Simple statistical anomaly detection using standard deviation
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        threshold = 2.5 * std_dev  # 2.5 sigma threshold
        
        for i, value in enumerate(values):
            if abs(value - mean_value) > threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'expected_range': [mean_value - threshold, mean_value + threshold],
                    'severity': 'high' if abs(value - mean_value) > 3 * std_dev else 'medium'
                })
        
        return anomalies


class AlertManager:
    """Manages performance alerts and notifications"""
    
    def __init__(self, config -> None: MonitoringConfig) -> None:
        self.config = config
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.alert_cooldowns: Dict[str, datetime] = {}
        self.alerts_sent_this_hour = 0
        self.hour_reset_time = datetime.now(timezone.utc)
        
        logger.info("🚨 Alert Manager initialized")
    
    async def check_for_alerts(self, analysis -> None: Dict[str, Any], component -> None: str) -> None:
        """Check analysis results and create alerts if needed"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Reset hourly alert counter
            if current_time.hour != self.hour_reset_time.hour:
                self.alerts_sent_this_hour = 0
                self.hour_reset_time = current_time
            
            # Check if we've hit the alert limit
            if self.alerts_sent_this_hour >= self.config.max_alerts_per_hour:
                return
            
            # Check health score for critical alerts
            health_score = analysis.get('health_score', 100)
            if health_score <= 20:
                await self._create_alert(
                    severity=AlertSeverity.CRITICAL,
                    title=f"Critical Health Score for {component}",
                    description=f"Health score has dropped to {health_score:.1f}%",
                    component=component,
                    metric_name="health_score",
                    current_value=health_score,
                    threshold_value=20
                )
            elif health_score <= 50:
                await self._create_alert(
                    severity=AlertSeverity.WARNING,
                    title=f"Low Health Score for {component}",
                    description=f"Health score has dropped to {health_score:.1f}%",
                    component=component,
                    metric_name="health_score",
                    current_value=health_score,
                    threshold_value=50
                )
            
            # Check for specific issues
            issues = analysis.get('issues', [])
            for issue in issues:
                if 'critically high' in issue.lower():
                    await self._create_alert(
                        severity=AlertSeverity.CRITICAL,
                        title=f"Critical Metric Alert - {component}",
                        description=issue,
                        component=component,
                        metric_name="unknown",
                        current_value=0,
                        threshold_value=0
                    )
                elif 'warning threshold' in issue.lower():
                    await self._create_alert(
                        severity=AlertSeverity.WARNING,
                        title=f"Warning Threshold Exceeded - {component}",
                        description=issue,
                        component=component,
                        metric_name="unknown",
                        current_value=0,
                        threshold_value=0
                    )
            
            # Check anomalies
            anomalies = analysis.get('anomalies', [])
            if len(anomalies) > 5:  # Many anomalies indicate a problem
                await self._create_alert(
                    severity=AlertSeverity.ERROR,
                    title=f"Multiple Anomalies Detected - {component}",
                    description=f"{len(anomalies)} anomalies detected in performance metrics",
                    component=component,
                    metric_name="anomaly_count",
                    current_value=len(anomalies),
                    threshold_value=5
                )
            
        except Exception as e:
            logger.error(f"Alert checking failed: {e}")
    
    async def _create_alert(
        self,
        severity -> None: AlertSeverity,
        title -> None: str,
        description -> None: str,
        component -> None: str,
        metric_name -> None: str,
        current_value -> None: float,
        threshold_value -> None: float
    ) -> None:
        """Create new alert"""
        try:
            # Check cooldown
            cooldown_key = f"{component}_{metric_name}_{severity.value}"
            if cooldown_key in self.alert_cooldowns:
                cooldown_end = self.alert_cooldowns[cooldown_key] + timedelta(minutes=self.config.alert_cooldown_minutes)
                if datetime.now(timezone.utc) < cooldown_end:
                    return  # Still in cooldown
            
            alert_id = str(uuid.uuid4())
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=severity,
                title=title,
                description=description,
                component=component,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Set cooldown
            self.alert_cooldowns[cooldown_key] = datetime.now(timezone.utc)
            
            # Increment counter
            self.alerts_sent_this_hour += 1
            
            # Send notification
            await self._send_alert_notification(alert)
            
            logger.warning(f"Alert created: {title}")
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def _send_alert_notification(self, alert -> None: PerformanceAlert) -> None:
        """Send alert notification"""
        # Placeholder for notification implementation
        # In production, would integrate with email, Slack, PagerDuty, etc.
        logger.warning(f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.description}")
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """Resolve an active alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved_at = datetime.now(timezone.utc)
                alert.metadata['resolution_note'] = resolution_note
                
                del self.active_alerts[alert_id]
                
                logger.info(f"Alert {alert_id} resolved: {resolution_note}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        active_alerts = list(self.active_alerts.values())
        
        return {
            'active_alerts': len(active_alerts),
            'critical_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            'warning_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.WARNING]),
            'error_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.ERROR]),
            'total_alerts_today': len([
                a for a in self.alert_history 
                if a.triggered_at.date() == datetime.now(timezone.utc).date()
            ]),
            'alerts_sent_this_hour': self.alerts_sent_this_hour,
            'alert_rate_limit_reached': self.alerts_sent_this_hour >= self.config.max_alerts_per_hour
        }


class PerformanceOptimizer:
    """Provides performance optimization recommendations"""
    
    def __init__(self, config -> None: MonitoringConfig) -> None:
        self.config = config
        self.optimization_cache = {}
        
        logger.info("⚡ Performance Optimizer initialized")
    
    async def generate_recommendations(
        self, 
        analysis: Dict[str, Any],
        component: str
    ) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations"""
        try:
            recommendations = []
            
            health_score = analysis.get('health_score', 100)
            issues = analysis.get('issues', [])
            trends = analysis.get('trends', {})
            
            # High-level recommendations based on health score
            if health_score < 30:
                recommendations.append({
                    'priority': 'critical',
                    'category': 'system_health',
                    'title': 'Critical Performance Issues Detected',
                    'description': 'Multiple critical performance issues require immediate attention',
                    'actions': [
                        'Review system resources and scale if necessary',
                        'Check for resource leaks or inefficient processes',
                        'Consider emergency maintenance window'
                    ],
                    'impact': 'high',
                    'effort': 'high'
                })
            
            # CPU-specific recommendations
            cpu_recommendations = await self._get_cpu_recommendations(analysis)
            recommendations.extend(cpu_recommendations)
            
            # Memory-specific recommendations
            memory_recommendations = await self._get_memory_recommendations(analysis)
            recommendations.extend(memory_recommendations)
            
            # Disk-specific recommendations
            disk_recommendations = await self._get_disk_recommendations(analysis)
            recommendations.extend(disk_recommendations)
            
            # Trend-based recommendations
            trend_recommendations = await self._get_trend_recommendations(trends)
            recommendations.extend(trend_recommendations)
            
            # Auto-scaling recommendations
            if self.config.enable_auto_scaling_recommendations:
                scaling_recommendations = await self._get_scaling_recommendations(analysis)
                recommendations.extend(scaling_recommendations)
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            recommendations.sort(key=lambda r: priority_order.get(r.get('priority', 'low'), 3))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def _get_cpu_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get CPU-specific recommendations"""
        recommendations = []
        issues = analysis.get('issues', [])
        
        cpu_issues = [issue for issue in issues if 'cpu_usage_percent' in issue.lower()]
        
        if cpu_issues:
            if any('critically high' in issue for issue in cpu_issues):
                recommendations.append({
                    'priority': 'critical',
                    'category': 'cpu',
                    'title': 'Critical CPU Usage',
                    'description': 'CPU usage is critically high and affecting system performance',
                    'actions': [
                        'Identify and terminate resource-intensive processes',
                        'Scale horizontally by adding more instances',
                        'Optimize application code for better CPU efficiency',
                        'Consider upgrading to higher CPU capacity'
                    ],
                    'impact': 'high',
                    'effort': 'medium'
                })
            else:
                recommendations.append({
                    'priority': 'high',
                    'category': 'cpu',
                    'title': 'High CPU Usage',
                    'description': 'CPU usage is above warning threshold',
                    'actions': [
                        'Monitor CPU usage patterns',
                        'Identify CPU-intensive processes',
                        'Consider load balancing',
                        'Review application performance'
                    ],
                    'impact': 'medium',
                    'effort': 'low'
                })
        
        return recommendations
    
    async def _get_memory_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get memory-specific recommendations"""
        recommendations = []
        issues = analysis.get('issues', [])
        
        memory_issues = [issue for issue in issues if 'memory_usage_percent' in issue.lower()]
        
        if memory_issues:
            if any('critically high' in issue for issue in memory_issues):
                recommendations.append({
                    'priority': 'critical',
                    'category': 'memory',
                    'title': 'Critical Memory Usage',
                    'description': 'Memory usage is critically high, system may become unstable',
                    'actions': [
                        'Immediately restart memory-intensive processes',
                        'Check for memory leaks in applications',
                        'Clear caches and temporary files',
                        'Add more RAM or scale horizontally'
                    ],
                    'impact': 'high',
                    'effort': 'medium'
                })
            else:
                recommendations.append({
                    'priority': 'high',
                    'category': 'memory',
                    'title': 'High Memory Usage',
                    'description': 'Memory usage is above warning threshold',
                    'actions': [
                        'Monitor memory usage patterns',
                        'Optimize application memory usage',
                        'Implement memory caching strategies',
                        'Consider memory cleanup routines'
                    ],
                    'impact': 'medium',
                    'effort': 'low'
                })
        
        return recommendations
    
    async def _get_disk_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get disk-specific recommendations"""
        recommendations = []
        issues = analysis.get('issues', [])
        
        disk_issues = [issue for issue in issues if 'disk_usage_percent' in issue.lower()]
        
        if disk_issues:
            if any('critically high' in issue for issue in disk_issues):
                recommendations.append({
                    'priority': 'critical',
                    'category': 'disk',
                    'title': 'Critical Disk Usage',
                    'description': 'Disk usage is critically high, system operations may fail',
                    'actions': [
                        'Immediately clean up unnecessary files',
                        'Archive or delete old logs',
                        'Move large files to external storage',
                        'Add more disk space urgently'
                    ],
                    'impact': 'high',
                    'effort': 'low'
                })
            else:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'disk',
                    'title': 'High Disk Usage',
                    'description': 'Disk usage is above warning threshold',
                    'actions': [
                        'Implement log rotation',
                        'Set up automated cleanup tasks',
                        'Monitor disk usage growth trends',
                        'Plan for storage expansion'
                    ],
                    'impact': 'medium',
                    'effort': 'low'
                })
        
        return recommendations
    
    async def _get_trend_recommendations(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trend-based recommendations"""
        recommendations = []
        
        for metric_name, trend_data in trends.items():
            if trend_data.get('concerning', False):
                recommendations.append({
                    'priority': 'medium',
                    'category': 'trends',
                    'title': f'Concerning Trend in {metric_name}',
                    'description': trend_data.get('description', 'Metric showing concerning trend'),
                    'actions': [
                        f'Investigate root cause of {metric_name} trend',
                        'Implement proactive monitoring',
                        'Consider preventive measures',
                        'Set up predictive alerts'
                    ],
                    'impact': 'medium',
                    'effort': 'medium'
                })
        
        return recommendations
    
    async def _get_scaling_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get auto-scaling recommendations"""
        recommendations = []
        health_score = analysis.get('health_score', 100)
        
        if health_score < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'scaling',
                'title': 'Scale System Resources',
                'description': 'System performance indicates need for additional resources',
                'actions': [
                    'Evaluate current resource utilization',
                    'Scale horizontally by adding instances',
                    'Consider vertical scaling for immediate relief',
                    'Implement auto-scaling policies'
                ],
                'impact': 'high',
                'effort': 'medium'
            })
        
        return recommendations


class MediaPerformanceMonitor:
    """Main media performance monitoring system"""
    
    def __init__(self, config -> None: Optional[MonitoringConfig] = None) -> None:
        """Initialize media performance monitor"""
        self.config = config or MonitoringConfig()
        
        # Initialize components
        self.metrics_collector = SystemMetricsCollector(self.config)
        self.performance_analyzer = PerformanceAnalyzer(self.config)
        self.alert_manager = AlertManager(self.config)
        self.performance_optimizer = PerformanceOptimizer(self.config)
        
        # System state
        self.monitoring_active = False
        self.component_health: Dict[str, SystemHealth] = {}
        self.monitoring_session_id = str(uuid.uuid4())
        
        logger.info("🎯 Media Performance Monitor initialized")
    
    async def start_monitoring(self) -> bool:
        """Start performance monitoring"""
        try:
            if self.monitoring_active:
                logger.warning("Monitoring is already active")
                return True
            
            self.monitoring_active = True
            self.monitoring_session_id = str(uuid.uuid4())
            
            # Start metrics collection
            await self.metrics_collector.start_collection()
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            logger.info("Performance monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop performance monitoring"""
        try:
            self.monitoring_active = False
            
            # Stop metrics collection
            await self.metrics_collector.stop_collection()
            
            logger.info("Performance monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    async def get_system_health(self, component: str = "system") -> SystemHealth:
        """Get current system health status"""
        try:
            # Get recent metrics
            recent_metrics = list(self.metrics_collector.metrics_buffer)[-50:]  # Last 50 metrics
            
            if not recent_metrics:
                return SystemHealth(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    score=0.0,
                    issues=["No metrics available"],
                    last_check=datetime.now(timezone.utc)
                )
            
            # Analyze performance
            analysis = await self.performance_analyzer.analyze_metrics(recent_metrics, component)
            
            # Determine health status
            health_score = analysis.get('health_score', 0)
            
            if health_score >= 90:
                status = HealthStatus.HEALTHY
            elif health_score >= 70:
                status = HealthStatus.DEGRADED
            elif health_score >= 30:
                status = HealthStatus.UNHEALTHY
            else:
                status = HealthStatus.CRITICAL
            
            # Get performance recommendations
            recommendations = await self.performance_optimizer.generate_recommendations(analysis, component)
            
            health = SystemHealth(
                component=component,
                status=status,
                score=health_score,
                metrics={
                    metric.name: metric.value 
                    for metric in recent_metrics[-10:]  # Last 10 metrics
                },
                issues=analysis.get('issues', []),
                recommendations=[rec['title'] for rec in recommendations[:5]]  # Top 5 recommendations
            )
            
            self.component_health[component] = health
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return SystemHealth(
                component=component,
                status=HealthStatus.UNKNOWN,
                score=0.0,
                issues=[f"Health check failed: {str(e)}"],
                last_check=datetime.now(timezone.utc)
            )
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard"""
        try:
            # Get system health
            system_health = await self.get_system_health("system")
            
            # Get recent metrics summary
            recent_metrics = list(self.metrics_collector.metrics_buffer)[-20:]
            
            # Calculate metric summaries
            metric_summaries = {}
            if recent_metrics:
                metrics_by_name = defaultdict(list)
                for metric in recent_metrics:
                    metrics_by_name[metric.name].append(metric.value)
                
                for name, values in metrics_by_name.items():
                    metric_summaries[name] = {
                        'current': values[-1] if values else 0,
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values)
                    }
            
            # Get alert summary
            alert_summary = self.alert_manager.get_alert_summary()
            
            # Get active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Get performance recommendations
            analysis = await self.performance_analyzer.analyze_metrics(recent_metrics, "system")
            recommendations = await self.performance_optimizer.generate_recommendations(analysis, "system")
            
            return {
                'monitoring_session_id': self.monitoring_session_id,
                'monitoring_active': self.monitoring_active,
                'system_health': {
                    'status': system_health.status.value,
                    'score': system_health.score,
                    'issues_count': len(system_health.issues)
                },
                'metrics_summary': metric_summaries,
                'alerts': {
                    'summary': alert_summary,
                    'active_alerts': [
                        {
                            'id': alert.alert_id,
                            'severity': alert.severity.value,
                            'title': alert.title,
                            'component': alert.component,
                            'triggered_at': alert.triggered_at.isoformat()
                        }
                        for alert in active_alerts[:10]  # Latest 10 alerts
                    ]
                },
                'recommendations': [
                    {
                        'priority': rec.get('priority', 'medium'),
                        'category': rec.get('category', 'general'),
                        'title': rec.get('title', 'No title'),
                        'impact': rec.get('impact', 'unknown')
                    }
                    for rec in recommendations[:5]  # Top 5 recommendations
                ],
                'dashboard_generated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance dashboard: {e}")
            return {'error': str(e)}
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Get recent metrics for analysis
                recent_metrics = list(self.metrics_collector.metrics_buffer)[-30:]  # Last 30 metrics
                
                if recent_metrics:
                    # Analyze performance
                    analysis = await self.performance_analyzer.analyze_metrics(recent_metrics, "system")
                    
                    # Check for alerts
                    if self.config.enable_alerts:
                        await self.alert_manager.check_for_alerts(analysis, "system")
                
                # Wait for next check interval
                await asyncio.sleep(self.config.alert_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.config.alert_check_interval_seconds)
    
    async def get_metrics_history(
        self, 
        metric_name: str, 
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get historical metrics data"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            historical_metrics = [
                {
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value,
                    'unit': metric.unit
                }
                for metric in self.metrics_collector.metrics_buffer
                if metric.name == metric_name and metric.timestamp >= cutoff_time
            ]
            
            return sorted(historical_metrics, key=lambda m: m['timestamp'])
            
        except Exception as e:
            logger.error(f"Failed to get metrics history: {e}")
            return []


# Export all classes for import
__all__ = [
    'MediaPerformanceMonitor',
    'SystemMetricsCollector',
    'PerformanceAnalyzer',
    'AlertManager',
    'PerformanceOptimizer',
    'MonitoringConfig',
    'PerformanceMetric',
    'SystemHealth',
    'PerformanceAlert',
    'PerformanceTrend',
    'MetricType',
    'AlertSeverity',
    'HealthStatus',
    'MonitoringScope'
]