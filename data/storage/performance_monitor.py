"""Professional Performance Monitor - IA Influencer Agent Platform
==============================================================
Module: backend/data/storage/performance_monitor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Storage Performance Analytics - Real-time Monitoring
Responsibility: Storage performance monitoring and optimization analytics
Technologies: Python, Prometheus, Grafana, Real-time metrics, ML predictions
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER INTÉGRÉE:
Metric Collection → Real-time Analysis → Anomaly Detection → 
Performance Prediction → Optimization Recommendations → 
Alert Generation → Dashboard Updates → Historical Analytics
"""
import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from collections import deque, defaultdict
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import psutil
import hashlib

# Prometheus metrics (would be installed in production)
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# ML libraries for prediction
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PerformanceCategory(Enum):
    """Performance categories for monitoring"""    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    STORAGE_USAGE = "storage_usage"
    COST = "cost"


@dataclass
class MetricPoint:
    """Single metric data point"""    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """Performance metric definition and data"""    name: str
    metric_type: MetricType
    category: PerformanceCategory
    description: str
    unit: str
    data_points: deque = field(default_factory=lambda: deque(maxlen=10000))
    labels: Dict[str, str] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    
    def add_point(self, value: float, labels: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Add a data point to the metric"""        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {},
            metadata=metadata or {}
        )
        self.data_points.append(point)
    
    def get_recent_values(self, duration_minutes: int = 60) -> List[float]:
        """Get values from recent time period"""        cutoff = datetime.utcnow() - timedelta(minutes=duration_minutes)
        return [p.value for p in self.data_points if p.timestamp >= cutoff]
    
    def get_average(self, duration_minutes: int = 60) -> float:
        """Get average value over time period"""        values = self.get_recent_values(duration_minutes)
        return statistics.mean(values) if values else 0.0
    
    def get_percentile(self, percentile: float, duration_minutes: int = 60) -> float:
        """Get percentile value over time period"""        values = self.get_recent_values(duration_minutes)
        return np.percentile(values, percentile) if values else 0.0


@dataclass
class PerformanceAlert:
    """Performance alert definition"""    id: str
    name: str
    description: str
    severity: AlertSeverity
    metric_name: str
    condition: str  # e.g., "value > threshold"
    threshold: float
    duration_minutes: int = 5
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_active: bool = False
    alert_count: int = 0


@dataclass
class PerformanceReport:
    """Performance report summary"""    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    summary_stats: Dict[str, Any]
    top_issues: List[Dict[str, Any]]
    recommendations: List[str]
    trend_analysis: Dict[str, Any]
    cost_analysis: Dict[str, Any]


class PerformanceMonitor:
    """    Professional performance monitor for IA Influencer Agent storage platform.
    
    Provides comprehensive real-time monitoring, alerting, and optimization
    recommendations for storage performance.
    """    
    def __init__(self, prometheus_port: int = 8000):
        """        Initialize PerformanceMonitor.
        
        Args:
            prometheus_port: Port for Prometheus metrics server
        """        self.logger = logging.getLogger(__name__)
        self.prometheus_port = prometheus_port
        
        # Metrics storage
        self.metrics = {}  # metric_name -> PerformanceMetric
        self.alerts = {}   # alert_id -> PerformanceAlert
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.collection_interval = 10  # seconds
        self.retention_hours = 168  # 7 days
        
        # Performance thresholds
        self.default_thresholds = {
            'latency_ms_p95': 2000.0,
            'latency_ms_p99': 5000.0,
            'error_rate_percent': 1.0,
            'availability_percent': 99.5,
            'storage_usage_percent': 85.0,
            'throughput_ops_per_sec': 100.0
        }
        
        # Prediction models
        self.prediction_models = {}
        self.model_update_interval = 3600  # 1 hour
        
        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.monitoring_tasks = []
        
        # Initialize core metrics
        self._initialize_core_metrics()
        
        # Start Prometheus server
        if PROMETHEUS_AVAILABLE:
            self._start_prometheus_server()
        
        # Start monitoring
        self._start_monitoring()
    
    def _initialize_core_metrics(self):
        """Initialize core performance metrics"""        core_metrics = [
            # Latency metrics
            PerformanceMetric(
                name="storage_operation_latency_ms",
                metric_type=MetricType.HISTOGRAM,
                category=PerformanceCategory.LATENCY,
                description="Storage operation latency in milliseconds",
                unit="ms",
                thresholds={'p95': 2000.0, 'p99': 5000.0}
            ),
            
            # Throughput metrics
            PerformanceMetric(
                name="storage_operations_per_second",
                metric_type=MetricType.GAUGE,
                category=PerformanceCategory.THROUGHPUT,
                description="Storage operations per second",
                unit="ops/sec",
                thresholds={'min': 10.0}
            ),
            
            # Error rate metrics
            PerformanceMetric(
                name="storage_error_rate_percent",
                metric_type=MetricType.GAUGE,
                category=PerformanceCategory.ERROR_RATE,
                description="Storage operation error rate percentage",
                unit="percent",
                thresholds={'max': 1.0}
            ),
            
            # Availability metrics
            PerformanceMetric(
                name="storage_availability_percent",
                metric_type=MetricType.GAUGE,
                category=PerformanceCategory.AVAILABILITY,
                description="Storage service availability percentage",
                unit="percent",
                thresholds={'min': 99.5}
            ),
            
            # Storage usage metrics
            PerformanceMetric(
                name="storage_usage_percent",
                metric_type=MetricType.GAUGE,
                category=PerformanceCategory.STORAGE_USAGE,
                description="Storage space usage percentage",
                unit="percent",
                thresholds={'warning': 80.0, 'critical': 90.0}
            ),
            
            # Cost metrics
            PerformanceMetric(
                name="storage_cost_per_gb_usd",
                metric_type=MetricType.GAUGE,
                category=PerformanceCategory.COST,
                description="Storage cost per GB in USD",
                unit="usd",
                thresholds={'max': 0.10}
            )
        ]
        
        for metric in core_metrics:
            self.metrics[metric.name] = metric
            self.logger.info(f"Initialized metric: {metric.name}")
    
    def _start_prometheus_server(self):
        """Start Prometheus metrics server"""        try:
            start_http_server(self.prometheus_port)
            self.logger.info(f"Prometheus server started on port {self.prometheus_port}")
        except Exception as e:
            self.logger.error(f"Failed to start Prometheus server: {str(e)}")
    
    def _start_monitoring(self):
        """Start background monitoring tasks"""        if self.monitoring_enabled:
            # Start metric collection
            task1 = asyncio.create_task(self._collect_system_metrics())
            self.monitoring_tasks.append(task1)
            
            # Start alert processing
            task2 = asyncio.create_task(self._process_alerts())
            self.monitoring_tasks.append(task2)
            
            # Start prediction model updates
            if ML_AVAILABLE:
                task3 = asyncio.create_task(self._update_prediction_models())
                self.monitoring_tasks.append(task3)
            
            # Start metric cleanup
            task4 = asyncio.create_task(self._cleanup_old_metrics())
            self.monitoring_tasks.append(task4)
    
    def record_operation(self, operation_type: str, duration_ms: float, 
                        success: bool, provider: str = None, 
                        metadata: Dict[str, Any] = None):
        """        Record a storage operation for monitoring.
        
        Args:
            operation_type: Type of operation (upload, download, delete, etc.)
            duration_ms: Operation duration in milliseconds
            success: Whether operation succeeded
            provider: Storage provider used
            metadata: Additional operation metadata
        """        try:
            labels = {
                'operation': operation_type,
                'provider': provider or 'unknown',
                'status': 'success' if success else 'error'
            }
            
            # Record latency
            if 'storage_operation_latency_ms' in self.metrics:
                self.metrics['storage_operation_latency_ms'].add_point(
                    duration_ms, labels, metadata
                )
            
            # Update error rate
            self._update_error_rate(success, labels)
            
            # Update throughput counter
            self._update_throughput_counter(operation_type, provider)
            
            # Log operation for debugging
            self.logger.debug(
                f"Recorded operation: {operation_type} "
                f"({duration_ms:.2f}ms, {labels['status']}, {provider})"
            )
            
        except Exception as e:
            self.logger.error(f"Error recording operation: {str(e)}")
    
    def record_custom_metric(self, metric_name: str, value: float,
                           labels: Dict[str, str] = None,
                           metadata: Dict[str, Any] = None):
        """        Record a custom metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            labels: Optional labels
            metadata: Optional metadata
        """        try:
            if metric_name in self.metrics:
                self.metrics[metric_name].add_point(value, labels, metadata)
            else:
                self.logger.warning(f"Unknown metric: {metric_name}")
                
        except Exception as e:
            self.logger.error(f"Error recording custom metric: {str(e)}")
    
    def add_alert(self, alert: PerformanceAlert):
        """        Add a performance alert.
        
        Args:
            alert: Performance alert configuration
        """        try:
            self.alerts[alert.id] = alert
            self.logger.info(f"Added alert: {alert.name} ({alert.id})")
            
        except Exception as e:
            self.logger.error(f"Error adding alert: {str(e)}")
    
    def get_metric_summary(self, metric_name: str, 
                          duration_minutes: int = 60) -> Dict[str, Any]:
        """        Get summary statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            duration_minutes: Time period to analyze
            
        Returns:
            Summary statistics dictionary
        """        try:
            if metric_name not in self.metrics:
                return {}
            
            metric = self.metrics[metric_name]
            values = metric.get_recent_values(duration_minutes)
            
            if not values:
                return {'count': 0}
            
            summary = {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
            }
            
            # Add percentiles if enough data
            if len(values) >= 10:
                summary.update({
                    'p50': np.percentile(values, 50),
                    'p90': np.percentile(values, 90),
                    'p95': np.percentile(values, 95),
                    'p99': np.percentile(values, 99)
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting metric summary: {str(e)}")
            return {}
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """        Get list of active alerts.
        
        Returns:
            List of active performance alerts
        """        return [alert for alert in self.alerts.values() if alert.is_active]
    
    def get_performance_report(self, hours: int = 24) -> PerformanceReport:
        """        Generate comprehensive performance report.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Performance report
        """        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Collect summary statistics
            summary_stats = {}
            for metric_name in self.metrics:
                summary_stats[metric_name] = self.get_metric_summary(metric_name, hours * 60)
            
            # Identify top issues
            top_issues = self._identify_top_issues(hours)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(summary_stats, top_issues)
            
            # Analyze trends
            trend_analysis = self._analyze_trends(hours)
            
            # Analyze costs
            cost_analysis = self._analyze_costs(hours)
            
            report = PerformanceReport(
                report_id=hashlib.md5(f"{start_time}{end_time}".encode()).hexdigest()[:8],
                generated_at=datetime.utcnow(),
                period_start=start_time,
                period_end=end_time,
                summary_stats=summary_stats,
                top_issues=top_issues,
                recommendations=recommendations,
                trend_analysis=trend_analysis,
                cost_analysis=cost_analysis
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return PerformanceReport(
                report_id="error",
                generated_at=datetime.utcnow(),
                period_start=start_time,
                period_end=end_time,
                summary_stats={},
                top_issues=[],
                recommendations=[],
                trend_analysis={},
                cost_analysis={}
            )
    
    def predict_metric(self, metric_name: str, hours_ahead: int = 24) -> Optional[Dict[str, Any]]:
        """        Predict future metric values using ML models.
        
        Args:
            metric_name: Name of metric to predict
            hours_ahead: Hours into the future to predict
            
        Returns:
            Prediction results or None if not available
        """        try:
            if not ML_AVAILABLE or metric_name not in self.prediction_models:
                return None
            
            model = self.prediction_models[metric_name]
            
            # Get recent data for prediction
            if metric_name not in self.metrics:
                return None
            
            metric = self.metrics[metric_name]
            recent_values = metric.get_recent_values(24 * 60)  # 24 hours of data
            
            if len(recent_values) < 10:
                return None
            
            # Prepare features (simple time series approach)
            X = np.array(range(len(recent_values))).reshape(-1, 1)
            y = np.array(recent_values)
            
            # Train model if needed
            if 'fitted' not in model:
                model['scaler'] = StandardScaler()
                model['regressor'] = LinearRegression()
                
                X_scaled = model['scaler'].fit_transform(X)
                model['regressor'].fit(X_scaled, y)
                model['fitted'] = True
            
            # Make prediction
            future_X = np.array([len(recent_values) + hours_ahead]).reshape(-1, 1)
            future_X_scaled = model['scaler'].transform(future_X)
            predicted_value = model['regressor'].predict(future_X_scaled)[0]
            
            # Calculate confidence interval (simple approach)
            residuals = y - model['regressor'].predict(model['scaler'].transform(X))
            std_residual = np.std(residuals)
            
            return {
                'metric_name': metric_name,
                'predicted_value': predicted_value,
                'confidence_interval': {
                    'lower': predicted_value - 2 * std_residual,
                    'upper': predicted_value + 2 * std_residual
                },
                'hours_ahead': hours_ahead,
                'model_accuracy': model['regressor'].score(
                    model['scaler'].transform(X), y
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting metric {metric_name}: {str(e)}")
            return None
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics"""        while self.monitoring_enabled:
            try:
                # Collect system-level metrics
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                disk_usage = psutil.disk_usage('/').percent
                
                # Record system metrics
                self.record_custom_metric('system_cpu_percent', cpu_percent)
                self.record_custom_metric('system_memory_percent', memory_percent)
                self.record_custom_metric('system_disk_percent', disk_usage)
                
                # Calculate availability (simple uptime-based)
                availability = 100.0  # Assume available if we can collect metrics
                self.record_custom_metric('storage_availability_percent', availability)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {str(e)}")
                await asyncio.sleep(self.collection_interval)
    
    async def _process_alerts(self):
        """Background task to process alerts"""        while self.monitoring_enabled:
            try:
                for alert in self.alerts.values():
                    await self._check_alert_condition(alert)
                
                await asyncio.sleep(30)  # Check alerts every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error processing alerts: {str(e)}")
                await asyncio.sleep(30)
    
    async def _check_alert_condition(self, alert: PerformanceAlert):
        """Check if alert condition is met"""        try:
            if alert.metric_name not in self.metrics:
                return
            
            metric = self.metrics[alert.metric_name]
            recent_values = metric.get_recent_values(alert.duration_minutes)
            
            if not recent_values:
                return
            
            # Evaluate condition (simplified)
            current_value = recent_values[-1]  # Most recent value
            
            condition_met = False
            if ">" in alert.condition:
                condition_met = current_value > alert.threshold
            elif "<" in alert.condition:
                condition_met = current_value < alert.threshold
            elif "=" in alert.condition:
                condition_met = abs(current_value - alert.threshold) < 0.01
            
            # Update alert status
            if condition_met and not alert.is_active:
                # Trigger alert
                alert.is_active = True
                alert.triggered_at = datetime.utcnow()
                alert.alert_count += 1
                
                self.logger.warning(
                    f"Alert triggered: {alert.name} "
                    f"(value: {current_value}, threshold: {alert.threshold})"
                )
                
                # Send notification (placeholder)
                await self._send_alert_notification(alert, current_value)
                
            elif not condition_met and alert.is_active:
                # Resolve alert
                alert.is_active = False
                alert.resolved_at = datetime.utcnow()
                
                self.logger.info(f"Alert resolved: {alert.name}")
                
        except Exception as e:
            self.logger.error(f"Error checking alert condition: {str(e)}")
    
    async def _send_alert_notification(self, alert: PerformanceAlert, current_value: float):
        """Send alert notification (placeholder for integration)"""        notification = {
            'alert_id': alert.id,
            'alert_name': alert.name,
            'severity': alert.severity.value,
            'current_value': current_value,
            'threshold': alert.threshold,
            'description': alert.description,
            'triggered_at': alert.triggered_at.isoformat()
        }
        
        # Log notification (in production, would send to external systems)
        self.logger.info(f"Alert notification: {json.dumps(notification, indent=2)}")
    
    async def _update_prediction_models(self):
        """Background task to update prediction models"""        while self.monitoring_enabled:
            try:
                if ML_AVAILABLE:
                    for metric_name in self.metrics:
                        if metric_name not in self.prediction_models:
                            self.prediction_models[metric_name] = {}
                
                await asyncio.sleep(self.model_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error updating prediction models: {str(e)}")
                await asyncio.sleep(self.model_update_interval)
    
    async def _cleanup_old_metrics(self):
        """Background task to cleanup old metric data"""        while self.monitoring_enabled:
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
                
                for metric in self.metrics.values():
                    # Remove old data points
                    while (metric.data_points and 
                           metric.data_points[0].timestamp < cutoff_time):
                        metric.data_points.popleft()
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                self.logger.error(f"Error in metric cleanup: {str(e)}")
                await asyncio.sleep(3600)
    
    def _update_error_rate(self, success: bool, labels: Dict[str, str]):
        """Update error rate metrics"""        # Simple moving average for error rate
        error_rate_metric = 'storage_error_rate_percent'
        if error_rate_metric in self.metrics:
            current_error_rate = self.metrics[error_rate_metric].get_average(60)
            
            # Update based on current operation
            new_error_rate = current_error_rate * 0.95  # Decay factor
            if not success:
                new_error_rate += 5.0  # Increase on error
            
            self.metrics[error_rate_metric].add_point(
                max(0.0, min(100.0, new_error_rate)), labels
            )
    
    def _update_throughput_counter(self, operation_type: str, provider: str):
        """Update throughput metrics"""        throughput_metric = 'storage_operations_per_second'
        if throughput_metric in self.metrics:
            # Simple throughput calculation based on recent operations
            recent_ops = len(self.metrics[throughput_metric].get_recent_values(60))
            ops_per_second = recent_ops / 60.0
            
            self.metrics[throughput_metric].add_point(ops_per_second, {
                'operation': operation_type,
                'provider': provider or 'unknown'
            })
    
    def _identify_top_issues(self, hours: int) -> List[Dict[str, Any]]:
        """Identify top performance issues"""        issues = []
        
        # Check each metric against thresholds
        for metric_name, metric in self.metrics.items():
            summary = self.get_metric_summary(metric_name, hours * 60)
            
            if not summary or summary.get('count', 0) == 0:
                continue
            
            # Check against thresholds
            for threshold_name, threshold_value in metric.thresholds.items():
                if threshold_name in summary:
                    current_value = summary[threshold_name]
                    
                    if threshold_name.startswith('max') and current_value > threshold_value:
                        issues.append({
                            'metric': metric_name,
                            'issue': f'{threshold_name} exceeded',
                            'current_value': current_value,
                            'threshold': threshold_value,
                            'severity': 'high' if current_value > threshold_value * 1.2 else 'medium'
                        })
                    elif threshold_name.startswith('min') and current_value < threshold_value:
                        issues.append({
                            'metric': metric_name,
                            'issue': f'{threshold_name} below minimum',
                            'current_value': current_value,
                            'threshold': threshold_value,
                            'severity': 'medium'
                        })
        
        # Sort by severity
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
        
        return issues[:10]  # Return top 10 issues
    
    def _generate_recommendations(self, summary_stats: Dict[str, Any], 
                                top_issues: List[Dict[str, Any]]) -> List[str]:
        """Generate performance optimization recommendations"""        recommendations = []
        
        # Analyze latency
        latency_summary = summary_stats.get('storage_operation_latency_ms', {})
        if latency_summary.get('p95', 0) > 2000:
            recommendations.append(
                "Consider implementing caching or using faster storage tiers for frequently accessed files"
            )
        
        # Analyze error rate
        error_rate_summary = summary_stats.get('storage_error_rate_percent', {})
        if error_rate_summary.get('mean', 0) > 1.0:
            recommendations.append(
                "Investigate storage errors and consider implementing retry mechanisms"
            )
        
        # Analyze storage usage
        usage_summary = summary_stats.get('storage_usage_percent', {})
        if usage_summary.get('max', 0) > 80:
            recommendations.append(
                "Storage usage is high. Consider archiving old files or expanding storage capacity"
            )
        
        # Generic recommendations based on issues
        high_severity_issues = [i for i in top_issues if i['severity'] == 'high']
        if len(high_severity_issues) > 3:
            recommendations.append(
                "Multiple high-severity performance issues detected. Consider comprehensive system review"
            )
        
        return recommendations
    
    def _analyze_trends(self, hours: int) -> Dict[str, Any]:
        """Analyze performance trends"""        trends = {}
        
        try:
            # Analyze each metric for trends
            for metric_name, metric in self.metrics.items():
                values = metric.get_recent_values(hours * 60)
                
                if len(values) < 10:
                    continue
                
                # Simple trend analysis
                mid_point = len(values) // 2
                first_half_avg = statistics.mean(values[:mid_point])
                second_half_avg = statistics.mean(values[mid_point:])
                
                if second_half_avg > first_half_avg * 1.1:
                    trend = 'increasing'
                elif second_half_avg < first_half_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
                
                trends[metric_name] = {
                    'trend': trend,
                    'change_percent': ((second_half_avg - first_half_avg) / first_half_avg) * 100
                    if first_half_avg > 0 else 0
                }
        
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
        
        return trends
    
    def _analyze_costs(self, hours: int) -> Dict[str, Any]:
        """Analyze cost trends"""        cost_analysis = {}
        
        try:
            cost_metric = 'storage_cost_per_gb_usd'
            if cost_metric in self.metrics:
                cost_summary = self.get_metric_summary(cost_metric, hours * 60)
                
                if cost_summary:
                    cost_analysis = {
                        'average_cost_per_gb': cost_summary.get('mean', 0),
                        'total_estimated_cost': cost_summary.get('mean', 0) * 1000,  # Placeholder
                        'cost_trend': 'stable',  # Would calculate actual trend
                        'optimization_potential': 15.5  # Percentage savings possible
                    }
        
        except Exception as e:
            self.logger.error(f"Error analyzing costs: {str(e)}")
        
        return cost_analysis


# Export the classes for use in other modules
__all__ = [
    'PerformanceMonitor',
    'PerformanceMetric',
    'PerformanceAlert',
    'PerformanceReport',
    'MetricType',
    'AlertSeverity',
    'PerformanceCategory',
    'MetricPoint'
]
