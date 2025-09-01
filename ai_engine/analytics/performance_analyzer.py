"""Performance Analyzer - Advanced Performance Analysis and Optimization
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive performance analysis, monitoring, and optimization
recommendations for the IA Influencer Agent platform.
"""

import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics
import json

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """
Types of performance metrics"""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    LATENCY = "latency"
    QUEUE_SIZE = "queue_size"
    CONNECTION_COUNT = "connection_count"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_CONNECTIONS = "database_connections"
    API_CALLS_PER_SECOND = "api_calls_per_second"
    CONCURRENT_USERS = "concurrent_users"

class PerformanceLevel(Enum):
    """Performance level classifications"""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"

class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceData:
    """Individual performance measurement"""
    metric: PerformanceMetric
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    unit: Optional[str] = None

@dataclass
class PerformanceThreshold:
    """
Performance threshold configuration"""
    metric: PerformanceMetric
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str = ">"  # >, <, ==, !=, >=, <=
    time_window_seconds: int = 300  # 5 minutes
    min_samples: int = 3
    enabled: bool = True

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    metric: PerformanceMetric
    severity: AlertSeverity
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    duration: Optional[timedelta] = None
    resolved: bool = False
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class PerformanceReport:
    """
Performance analysis report"""
    report_id: str
    analysis_period: Dict[str, datetime]
    overall_performance_level: PerformanceLevel
    metric_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    alerts_summary: Dict[str, int] = field(default_factory=dict)
    trend_analysis: Dict[str, str] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SystemResource:
    """
System resource information"""
    cpu_count: int
    cpu_frequency: Dict[str, float]
    memory_total: int
    memory_available: int
    memory_used: int
    memory_percentage: float
    disk_total: int
    disk_used: int
    disk_free: int
    disk_percentage: float
    boot_time: datetime
    load_average: Optional[List[float]] = None
    network_io: Optional[Dict[str, int]] = None
    process_count: int = 0

class PerformanceAnalyzer:
    """
Main performance analysis engine"""
    
    def __init__(self, history_size: int = 10000, monitoring_interval: int = 30):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.history_size = history_size
        self.monitoring_interval = monitoring_interval
        
        # Performance data storage
        self.performance_data = defaultdict(lambda: deque(maxlen=history_size))
        self.system_resources = None
        
        # Thresholds and alerts
        self.thresholds = {}
        self.active_alerts = {}
        self.alert_history = []
        
        # Analysis components
        self.trend_analyzer = TrendAnalyzer()
        self.bottleneck_detector = BottleneckDetector()
        self.recommendation_engine = RecommendationEngine()
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        self.logger.info("PerformanceAnalyzer initialized successfully")
    
    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds"""
        default_thresholds = [
            PerformanceThreshold(
                PerformanceMetric.CPU_USAGE,
                warning_threshold=70.0,
                critical_threshold=90.0,
                comparison_operator=">"
            ),
            PerformanceThreshold(
                PerformanceMetric.MEMORY_USAGE,
                warning_threshold=80.0,
                critical_threshold=95.0,
                comparison_operator=">"
            ),
            PerformanceThreshold(
                PerformanceMetric.RESPONSE_TIME,
                warning_threshold=2000.0,  # 2 seconds
                critical_threshold=5000.0,  # 5 seconds
                comparison_operator=">"
            ),
            PerformanceThreshold(
                PerformanceMetric.ERROR_RATE,
                warning_threshold=5.0,  # 5%
                critical_threshold=10.0,  # 10%
                comparison_operator=">"
            ),
            PerformanceThreshold(
                PerformanceMetric.DISK_USAGE,
                warning_threshold=85.0,
                critical_threshold=95.0,
                comparison_operator=">"
            ),
            PerformanceThreshold(
                PerformanceMetric.AVAILABILITY,
                warning_threshold=99.0,
                critical_threshold=95.0,
                comparison_operator="<"
            )
        ]
        
        for threshold in default_thresholds:
            self.thresholds[threshold.metric] = threshold
    
    def start_monitoring(self) -> bool:
        """Start automatic performance monitoring"""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring is already active")
                return False
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            self.logger.info(f"Performance monitoring started (interval: {self.monitoring_interval}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop automatic performance monitoring"""
        try:
            if not self.monitoring_active:
                self.logger.warning("Monitoring is not active")
                return False
            
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=10)
            
            self.logger.info("Performance monitoring stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check thresholds and generate alerts
                self._check_thresholds()
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric(PerformanceMetric.CPU_USAGE, cpu_percent, unit="percent")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_metric(PerformanceMetric.MEMORY_USAGE, memory.percent, unit="percent")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric(PerformanceMetric.DISK_USAGE, disk_percent, unit="percent")
            
            # Network I/O metrics
            try:
                network = psutil.net_io_counters()
                self.record_metric(PerformanceMetric.NETWORK_IO, 
                                 network.bytes_sent + network.bytes_recv, 
                                 unit="bytes")
            except Exception:
                pass  # Network stats might not be available
            
            # Process count
            process_count = len(psutil.pids())
            
            # Update system resources
            self.system_resources = SystemResource(
                cpu_count=psutil.cpu_count(),
                cpu_frequency=psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                memory_total=memory.total,
                memory_available=memory.available,
                memory_used=memory.used,
                memory_percentage=memory.percent,
                disk_total=disk.total,
                disk_used=disk.used,
                disk_free=disk.free,
                disk_percentage=disk_percent,
                boot_time=datetime.fromtimestamp(psutil.boot_time()),
                process_count=process_count
            )
            
            # Load average (Unix systems only)
            try:
                if hasattr(psutil, 'getloadavg'):
                    self.system_resources.load_average = list(psutil.getloadavg())
            except (AttributeError, OSError):
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def record_metric(self, metric: PerformanceMetric, value: Union[int, float],
                     tags: Optional[Dict[str, str]] = None,
                     source: Optional[str] = None,
                     unit: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record a performance metric"""
        try:
            data_point = PerformanceData(
                metric=metric,
                value=value,
                tags=tags or {},
                metadata=metadata or {},
                source=source,
                unit=unit
            )
            
            self.performance_data[metric].append(data_point)
            self.logger.debug(f"Recorded metric: {metric.value}={value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric.value}: {e}")
            return False
    
    def _check_thresholds(self):
        """Check performance thresholds and generate alerts"""
        try:
            for metric, threshold in self.thresholds.items():
                if not threshold.enabled:
                    continue
                
                # Get recent data points
                recent_data = self._get_recent_data(metric, threshold.time_window_seconds)
                
                if len(recent_data) < threshold.min_samples:
                    continue
                
                # Calculate average value
                avg_value = statistics.mean([d.value for d in recent_data])
                
                # Check thresholds
                critical_triggered = self._evaluate_threshold(
                    avg_value, threshold.critical_threshold, threshold.comparison_operator
                )
                warning_triggered = self._evaluate_threshold(
                    avg_value, threshold.warning_threshold, threshold.comparison_operator
                )
                
                # Generate alerts
                if critical_triggered:
                    self._create_alert(metric, AlertSeverity.CRITICAL, avg_value, threshold.critical_threshold)
                elif warning_triggered:
                    self._create_alert(metric, AlertSeverity.WARNING, avg_value, threshold.warning_threshold)
                else:
                    # Check if we should resolve existing alerts
                    self._check_alert_resolution(metric)
                    
        except Exception as e:
            self.logger.error(f"Failed to check thresholds: {e}")
    
    def _get_recent_data(self, metric: PerformanceMetric, seconds: int) -> List[PerformanceData]:
        """Get recent data points for a metric"""
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        data = self.performance_data[metric]
        return [d for d in data if d.timestamp >= cutoff]
    
    def _evaluate_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """
Evaluate if a value crosses a threshold"""
        try:
            if operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == ">=":
                return value >= threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "==":
                return abs(value - threshold) < 0.001
            elif operator == "!=":
                return abs(value - threshold) > 0.001
            else:
                self.logger.warning(f"Unknown threshold operator: {operator}")
                return False
        except Exception:
            return False
    
    def _create_alert(self, metric: PerformanceMetric, severity: AlertSeverity, 
                     current_value: float, threshold_value: float):
        """Create a performance alert"""
        try:
            alert_key = f"{metric.value}_{severity.value}"
            
            # Check if alert already exists and is recent
            if alert_key in self.active_alerts:
                existing_alert = self.active_alerts[alert_key]
                time_since_alert = datetime.utcnow() - existing_alert.timestamp
                if time_since_alert.total_seconds() < 300:  # 5 minutes
                    return  # Don't spam alerts
            
            alert_id = f"{metric.value}_{severity.value}_{int(time.time())}"
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                metric=metric,
                severity=severity,
                current_value=current_value,
                threshold_value=threshold_value,
                message=f"{metric.value} is {current_value:.2f} (threshold: {threshold_value:.2f})"
            )
            
            self.active_alerts[alert_key] = alert
            self.alert_history.append(alert)
            
            # Keep alert history limited
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-500:]
            
            self.logger.warning(f"PERFORMANCE ALERT [{severity.value.upper()}]: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
    
    def _check_alert_resolution(self, metric: PerformanceMetric):
        """Check if alerts should be resolved"""
        try:
            alerts_to_resolve = []
            
            for alert_key, alert in self.active_alerts.items():
                if alert.metric != metric or alert.resolved:
                    continue
                
                # Get threshold for this metric
                threshold = self.thresholds.get(metric)
                if not threshold:
                    continue
                
                # Get recent data
                recent_data = self._get_recent_data(metric, threshold.time_window_seconds)
                if len(recent_data) < threshold.min_samples:
                    continue
                
                avg_value = statistics.mean([d.value for d in recent_data])
                
                # Check if condition is no longer met
                if alert.severity == AlertSeverity.CRITICAL:
                    condition_met = self._evaluate_threshold(
                        avg_value, threshold.critical_threshold, threshold.comparison_operator
                    )
                else:
                    condition_met = self._evaluate_threshold(
                        avg_value, threshold.warning_threshold, threshold.comparison_operator
                    )
                
                if not condition_met:
                    alert.resolved = True
                    alert.duration = datetime.utcnow() - alert.timestamp
                    alerts_to_resolve.append(alert_key)
                    
                    self.logger.info(f"PERFORMANCE ALERT RESOLVED: {alert.message}")
            
            # Remove resolved alerts from active alerts
            for key in alerts_to_resolve:
                del self.active_alerts[key]
                
        except Exception as e:
            self.logger.error(f"Failed to check alert resolution: {e}")
    
    def analyze_performance(self, hours_back: int = 24) -> PerformanceReport:
        """Generate comprehensive performance analysis report"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            report_id = f"perf_report_{int(time.time())}"
            
            # Analyze each metric
            metric_summaries = {}
            bottlenecks = []
            
            for metric in PerformanceMetric:
                summary = self._analyze_metric(metric, start_time, end_time)
                if summary:
                    metric_summaries[metric.value] = summary
                    
                    # Check if this is a bottleneck
                    if summary.get('performance_level') in ['poor', 'critical']:
                        bottlenecks.append(f"{metric.value}: {summary.get('issue_description', '')}")
            
            # Determine overall performance level
            performance_levels = [s.get('performance_level', 'average') for s in metric_summaries.values()]
            overall_level = self._determine_overall_performance(performance_levels)
            
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(
                metric_summaries, bottlenecks, self.system_resources
            )
            
            # Summarize alerts
            alerts_summary = self._summarize_alerts(start_time, end_time)
            
            # Trend analysis
            trend_analysis = self.trend_analyzer.analyze_trends(
                self.performance_data, start_time, end_time
            )
            
            report = PerformanceReport(
                report_id=report_id,
                analysis_period={'start': start_time, 'end': end_time},
                overall_performance_level=PerformanceLevel(overall_level),
                metric_summaries=metric_summaries,
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                alerts_summary=alerts_summary,
                trend_analysis=trend_analysis
            )
            
            self.logger.info(f"Generated performance report: {report_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to analyze performance: {e}")
            # Return basic report
            return PerformanceReport(
                report_id="error_report",
                analysis_period={'start': start_time, 'end': end_time},
                overall_performance_level=PerformanceLevel.AVERAGE
            )
    
    def _analyze_metric(self, metric: PerformanceMetric, 
                       start_time: datetime, end_time: datetime) -> Optional[Dict[str, Any]]:
        """Analyze a specific metric"""
        try:
            data = [d for d in self.performance_data[metric] 
                   if start_time <= d.timestamp <= end_time]
            
            if not data:
                return None
            
            values = [d.value for d in data]
            
            summary = {
                'metric': metric.value,
                'sample_count': len(values),
                'average': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'current': values[-1] if values else 0
            }
            
            # Add median and stddev if enough samples
            if len(values) > 1:
                summary['median'] = statistics.median(values)
                try:
                    summary['stddev'] = statistics.stdev(values)
                except statistics.StatisticsError:
                    summary['stddev'] = 0
            
            # Determine performance level
            threshold = self.thresholds.get(metric)
            if threshold:
                current_value = summary['average']
                
                if self._evaluate_threshold(current_value, threshold.critical_threshold, threshold.comparison_operator):
                    summary['performance_level'] = 'critical'
                    summary['issue_description'] = f"Average {metric.value} ({current_value:.2f}) exceeds critical threshold ({threshold.critical_threshold})"
                elif self._evaluate_threshold(current_value, threshold.warning_threshold, threshold.comparison_operator):
                    summary['performance_level'] = 'poor'
                    summary['issue_description'] = f"Average {metric.value} ({current_value:.2f}) exceeds warning threshold ({threshold.warning_threshold})"
                else:
                    summary['performance_level'] = 'good'
                    summary['issue_description'] = f"Average {metric.value} ({current_value:.2f}) is within acceptable range"
            else:
                summary['performance_level'] = 'average'
                summary['issue_description'] = f"No threshold defined for {metric.value}"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to analyze metric {metric.value}: {e}")
            return None
    
    def _determine_overall_performance(self, performance_levels: List[str]) -> str:
        """Determine overall performance level from individual metric levels"""
        if not performance_levels:
            return 'average'
        
        level_counts = {
            'critical': performance_levels.count('critical'),
            'poor': performance_levels.count('poor'),
            'average': performance_levels.count('average'),
            'good': performance_levels.count('good'),
            'excellent': performance_levels.count('excellent')
        }
        
        # If any metric is critical, overall is critical
        if level_counts['critical'] > 0:
            return 'critical'
        
        # If more than 25% of metrics are poor, overall is poor
        if level_counts['poor'] > len(performance_levels) * 0.25:
            return 'poor'
        
        # If more than 75% of metrics are good or excellent, overall is good
        if (level_counts['good'] + level_counts['excellent']) > len(performance_levels) * 0.75:
            return 'good'
        
        return 'average'
    
    def _summarize_alerts(self, start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """
Summarize alerts within time period"""
        try:
            period_alerts = [
                a for a in self.alert_history
                if start_time <= a.timestamp <= end_time
            ]
            
            return {
                'total_alerts': len(period_alerts),
                'critical_alerts': len([a for a in period_alerts if a.severity == AlertSeverity.CRITICAL]),
                'warning_alerts': len([a for a in period_alerts if a.severity == AlertSeverity.WARNING]),
                'resolved_alerts': len([a for a in period_alerts if a.resolved]),
                'active_alerts': len(self.active_alerts)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to summarize alerts: {e}")
            return {}
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current values for all metrics"""
        try:
            current_metrics = {}
            
            for metric in PerformanceMetric:
                data = self.performance_data[metric]
                if data:
                    current_metrics[metric.value] = data[-1].value
                else:
                    current_metrics[metric.value] = 0.0
            
            return current_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get current metrics: {e}")
            return {}
    
    def get_system_resources(self) -> Optional[SystemResource]:
        """Get current system resource information"""
        return self.system_resources
    
    def add_threshold(self, threshold: PerformanceThreshold) -> bool:
        """
Add or update a performance threshold"""
        try:
            self.thresholds[threshold.metric] = threshold
            self.logger.info(f"Added threshold for {threshold.metric.value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add threshold: {e}")
            return False
    
    def remove_threshold(self, metric: PerformanceMetric) -> bool:
        """Remove a performance threshold"""
        try:
            if metric in self.thresholds:
                del self.thresholds[metric]
                self.logger.info(f"Removed threshold for {metric.value}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove threshold: {e}")
            return False
    
    def export_data(self, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """Export performance data"""
        try:
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "system_resources": self.system_resources.__dict__ if self.system_resources else {},
                "current_metrics": self.get_current_metrics(),
                "active_alerts": len(self.active_alerts),
                "thresholds": {
                    metric.value: {
                        "warning": threshold.warning_threshold,
                        "critical": threshold.critical_threshold,
                        "operator": threshold.comparison_operator
                    }
                    for metric, threshold in self.thresholds.items()
                },
                "data_points": {
                    metric.value: len(data)
                    for metric, data in self.performance_data.items()
                }
            }
            
            if format_type.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                return export_data
                
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            return {"error": str(e)}

class TrendAnalyzer:
    """Analyzes performance trends"""
    
    def analyze_trends(self, performance_data: Dict, start_time: datetime, end_time: datetime) -> Dict[str, str]:
        """
Analyze performance trends"""
        trends = {}
        
        for metric, data in performance_data.items():
            try:
                period_data = [d for d in data if start_time <= d.timestamp <= end_time]
                if len(period_data) < 2:
                    trends[metric.value] = "insufficient_data"
                    continue
                
                values = [d.value for d in period_data]
                
                # Simple trend detection using linear regression
                n = len(values)
                x_sum = sum(range(n))
                y_sum = sum(values)
                xy_sum = sum(i * values[i] for i in range(n))
                x_squared_sum = sum(i * i for i in range(n))
                
                slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
                
                # Normalize slope by average value to get relative trend
                avg_value = statistics.mean(values)
                if avg_value != 0:
                    normalized_slope = slope / avg_value
                else:
                    normalized_slope = 0
                
                if normalized_slope > 0.05:
                    trends[metric.value] = "increasing"
                elif normalized_slope < -0.05:
                    trends[metric.value] = "decreasing"
                else:
                    trends[metric.value] = "stable"
                    
            except Exception as e:
                logger.error(f"Failed to analyze trend for {metric}: {e}")
                trends[metric.value] = "error"
        
        return trends

class BottleneckDetector:
    """Detects performance bottlenecks"""
    
    def detect_bottlenecks(self, metric_summaries: Dict[str, Dict[str, Any]]) -> List[str]:
        """
Detect performance bottlenecks"""
        bottlenecks = []
        
        # Check for high resource utilization
        for metric_name, summary in metric_summaries.items():
            if summary.get('performance_level') in ['poor', 'critical']:
                bottlenecks.append(f"High {metric_name}: {summary.get('issue_description', '')}")
        
        return bottlenecks

class RecommendationEngine:
    """Generates performance optimization recommendations"""
    
    def generate_recommendations(self, metric_summaries: Dict[str, Dict[str, Any]], 
                               bottlenecks: List[str], 
                               system_resources: Optional[SystemResource]) -> List[str]:
        """
Generate performance optimization recommendations"""
        recommendations = []
        
        try:
            # CPU-related recommendations
            cpu_summary = metric_summaries.get('cpu_usage')
            if cpu_summary and cpu_summary.get('performance_level') in ['poor', 'critical']:
                recommendations.extend([
                    "Consider optimizing CPU-intensive operations",
                    "Implement caching to reduce computational load",
                    "Review and optimize database queries",
                    "Consider horizontal scaling or load balancing"
                ])
            
            # Memory-related recommendations
            memory_summary = metric_summaries.get('memory_usage')
            if memory_summary and memory_summary.get('performance_level') in ['poor', 'critical']:
                recommendations.extend([
                    "Review memory usage patterns and optimize memory leaks",
                    "Implement memory pooling or object recycling",
                    "Consider increasing available memory",
                    "Optimize data structures and algorithms"
                ])
            
            # Disk-related recommendations
            disk_summary = metric_summaries.get('disk_usage')
            if disk_summary and disk_summary.get('performance_level') in ['poor', 'critical']:
                recommendations.extend([
                    "Clean up temporary files and logs",
                    "Implement log rotation policies",
                    "Consider adding more storage capacity",
                    "Move large files to external storage"
                ])
            
            # Response time recommendations
            response_summary = metric_summaries.get('response_time')
            if response_summary and response_summary.get('performance_level') in ['poor', 'critical']:
                recommendations.extend([
                    "Optimize API endpoints and database queries",
                    "Implement request caching strategies",
                    "Consider using a Content Delivery Network (CDN)",
                    "Review and optimize third-party API calls"
                ])
            
            # General recommendations if no specific issues found
            if not recommendations:
                recommendations.extend([
                    "System performance appears to be within acceptable ranges",
                    "Continue monitoring key metrics",
                    "Consider implementing proactive optimization strategies",
                    "Review capacity planning for future growth"
                ])
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations due to analysis error")
        
        return recommendations[:10]  # Limit to top 10 recommendations

# Export main classes
__all__ = [
    'PerformanceAnalyzer',
    'PerformanceData',
    'PerformanceThreshold',
    'PerformanceAlert',
    'PerformanceReport',
    'SystemResource',
    'PerformanceMetric',
    'PerformanceLevel',
    'AlertSeverity',
    'TrendAnalyzer',
    'BottleneckDetector',
    'RecommendationEngine'
]

logger.info("Performance analyzer module loaded successfully")
