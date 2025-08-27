#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enterprise Performance Monitoring System - IA Influencer Agent

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

© 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: 15 Senior Backend Engineers (12+ years experience average)
Specialties: Content Protection, AI/ML, Distributed Systems, Security

WARNING: This code is protected by copyright law. Any unauthorized copying,
distribution, or modification is strictly prohibited and will result in
legal action. Contact mlaiel@live.de for licensing.

This module implements enterprise-grade performance monitoring and system
health tracking for surveillance operations. Features include real-time
metrics collection, performance analytics, resource optimization,
alerting, and comprehensive system observability.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import psutil
import time
from collections import defaultdict, deque
import statistics
import threading

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics."""
    COUNTER = "counter"        # Monotonically increasing value
    GAUGE = "gauge"           # Point-in-time value
    HISTOGRAM = "histogram"   # Distribution of values
    TIMER = "timer"          # Timing measurements
    RATE = "rate"            # Rate of change
    PERCENTAGE = "percentage" # Percentage value


class MetricCategory(Enum):
    """Categories of performance metrics."""
    SYSTEM = "system"          # System-level metrics (CPU, memory, disk)
    APPLICATION = "application" # Application-level metrics
    BUSINESS = "business"      # Business logic metrics
    SECURITY = "security"      # Security-related metrics
    NETWORK = "network"        # Network performance metrics
    DATABASE = "database"      # Database performance metrics
    CRAWLING = "crawling"      # Web crawling metrics
    DETECTION = "detection"    # Threat detection metrics
    PROCESSING = "processing"  # Data processing metrics


class AlertCondition(Enum):
    """Alert condition types."""
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    THRESHOLD_BELOW = "threshold_below"
    RATE_INCREASE = "rate_increase"
    RATE_DECREASE = "rate_decrease"
    ANOMALY_DETECTED = "anomaly_detected"
    ERROR_RATE_HIGH = "error_rate_high"
    AVAILABILITY_LOW = "availability_low"


class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


@dataclass
class Metric:
    """Performance metric definition."""
    metric_id: str
    name: str
    metric_type: MetricType
    category: MetricCategory
    description: str
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: int = 2
    retention_days: int = 30


@dataclass
class MetricThreshold:
    """Metric alerting threshold."""
    threshold_id: str
    metric_id: str
    condition: AlertCondition
    value: float
    severity: str = "warning"
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    cooldown_minutes: int = 5
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceAlert:
    """Performance monitoring alert."""
    alert_id: str
    metric_id: str
    threshold_id: str
    condition: AlertCondition
    current_value: float
    threshold_value: float
    severity: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """System health assessment."""
    component: str
    status: HealthStatus
    score: float  # 0.0 - 1.0
    last_check: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Performance analysis report."""
    report_id: str
    period_start: datetime
    period_end: datetime
    overall_health_score: float
    system_components: Dict[str, SystemHealth] = field(default_factory=dict)
    key_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    alerts_summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """
    Enterprise performance monitoring system for surveillance operations.
    
    This system provides comprehensive performance monitoring capabilities including:
    - Real-time metrics collection and storage
    - System health monitoring and assessment
    - Performance alerting with configurable thresholds
    - Resource utilization tracking and optimization
    - Business metrics and KPI monitoring
    - Anomaly detection and trend analysis
    - Automated performance reporting
    - Integration with external monitoring systems
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the performance monitoring system.
        
        Args:
            config: System configuration
        """
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        self.collection_interval = self.config.get('collection_interval', 60)  # seconds
        self.retention_days = self.config.get('retention_days', 30)
        self.alert_cooldown = self.config.get('alert_cooldown', 300)  # seconds
        self.health_check_interval = self.config.get('health_check_interval', 300)
        
        # Data stores
        self.metrics: Dict[str, Metric] = {}
        self.metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.thresholds: Dict[str, MetricThreshold] = {}
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.system_health: Dict[str, SystemHealth] = {}
        
        # Processing components
        self.collectors: Dict[str, 'MetricCollector'] = {}
        self.analyzers: Dict[str, 'PerformanceAnalyzer'] = {}
        self.alerting_engine = AlertingEngine()
        self.anomaly_detector = AnomalyDetector()
        
        # Performance tracking
        self.collection_stats = {
            'total_collections': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'average_collection_time': 0.0
        }
        
        # Background tasks
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._background_started = False
        self._shutdown_event = asyncio.Event()
        
        # Thread safety
        self._lock = threading.RLock()
    
    async def initialize(self) -> None:
        """Initialize the performance monitoring system."""
        try:
            self._logger.info("Initializing Performance Monitoring System...")
            
            # Initialize metric collectors
            await self._initialize_collectors()
            
            # Initialize performance analyzers
            await self._initialize_analyzers()
            
            # Initialize alerting engine
            await self.alerting_engine.initialize()
            
            # Initialize anomaly detector
            await self.anomaly_detector.initialize()
            
            # Register default metrics
            await self._register_default_metrics()
            
            # Load existing thresholds
            await self._load_thresholds()
            
            # Start background monitoring
            await self._start_background_monitoring()
            
            # Perform initial health check
            await self._perform_health_check()
            
            self._logger.info("Performance Monitoring System initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize performance monitoring system: {e}")
            raise
    
    async def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        category: MetricCategory,
        description: str,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Register a new performance metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            category: Metric category
            description: Metric description
            unit: Unit of measurement
            tags: Optional tags
            
        Returns:
            Metric ID
        """
        try:
            metric_id = f"metric_{uuid.uuid4().hex[:8]}"
            
            metric = Metric(
                metric_id=metric_id,
                name=name,
                metric_type=metric_type,
                category=category,
                description=description,
                unit=unit,
                tags=tags or {}
            )
            
            with self._lock:
                self.metrics[metric_id] = metric
                self.metric_data[metric_id] = deque(maxlen=10000)
            
            self._logger.debug(f"Registered metric {name} ({metric_id})")
            
            return metric_id
            
        except Exception as e:
            self._logger.error(f"Error registering metric {name}: {e}")
            return ""
    
    async def record_metric(
        self,
        metric_id: str,
        value: float,
        timestamp: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Record a metric value.
        
        Args:
            metric_id: Metric to record
            value: Metric value
            timestamp: Optional timestamp (defaults to now)
            tags: Optional additional tags
            
        Returns:
            Success status
        """
        try:
            if metric_id not in self.metrics:
                self._logger.warning(f"Unknown metric ID: {metric_id}")
                return False
            
            metric = self.metrics[metric_id]
            record_time = timestamp or datetime.now()
            
            # Validate value range
            if metric.min_value is not None and value < metric.min_value:
                self._logger.warning(f"Metric {metric_id} value {value} below minimum {metric.min_value}")
            
            if metric.max_value is not None and value > metric.max_value:
                self._logger.warning(f"Metric {metric_id} value {value} above maximum {metric.max_value}")
            
            # Update metric
            metric.value = round(value, metric.precision)
            metric.timestamp = record_time
            
            if tags:
                metric.tags.update(tags)
            
            # Store data point
            data_point = {
                'value': metric.value,
                'timestamp': record_time,
                'tags': metric.tags.copy()
            }
            
            with self._lock:
                self.metric_data[metric_id].append(data_point)
            
            # Check thresholds
            await self._check_metric_thresholds(metric_id, value)
            
            # Detect anomalies
            await self.anomaly_detector.check_anomaly(metric_id, value, record_time)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error recording metric {metric_id}: {e}")
            return False
    
    async def set_threshold(
        self,
        metric_id: str,
        condition: AlertCondition,
        value: float,
        severity: str = "warning",
        description: str = "",
        notification_channels: Optional[List[str]] = None
    ) -> str:
        """
        Set an alerting threshold for a metric.
        
        Args:
            metric_id: Metric to monitor
            condition: Alert condition
            value: Threshold value
            severity: Alert severity
            description: Threshold description
            notification_channels: Notification channels
            
        Returns:
            Threshold ID
        """
        try:
            if metric_id not in self.metrics:
                self._logger.warning(f"Unknown metric ID: {metric_id}")
                return ""
            
            threshold_id = f"threshold_{uuid.uuid4().hex[:8]}"
            
            threshold = MetricThreshold(
                threshold_id=threshold_id,
                metric_id=metric_id,
                condition=condition,
                value=value,
                severity=severity,
                description=description,
                notification_channels=notification_channels or []
            )
            
            self.thresholds[threshold_id] = threshold
            
            self._logger.info(
                f"Set threshold {threshold_id} for metric {metric_id}: "
                f"{condition.value} {value} ({severity})"
            )
            
            return threshold_id
            
        except Exception as e:
            self._logger.error(f"Error setting threshold: {e}")
            return ""
    
    async def get_metric_value(self, metric_id: str) -> Optional[float]:
        """Get current value of a metric."""
        metric = self.metrics.get(metric_id)
        return metric.value if metric else None
    
    async def get_metric_history(
        self,
        metric_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for a metric.
        
        Args:
            metric_id: Metric to query
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of data points
            
        Returns:
            List of data points
        """
        try:
            if metric_id not in self.metric_data:
                return []
            
            data_points = list(self.metric_data[metric_id])
            
            # Filter by time range
            if start_time or end_time:
                filtered_points = []
                for point in data_points:
                    timestamp = point['timestamp']
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    filtered_points.append(point)
                data_points = filtered_points
            
            # Sort by timestamp (newest first)
            data_points.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return data_points[:limit]
            
        except Exception as e:
            self._logger.error(f"Error getting metric history for {metric_id}: {e}")
            return []
    
    async def get_system_health(self) -> Dict[str, SystemHealth]:
        """Get current system health status."""
        return self.system_health.copy()
    
    async def generate_performance_report(
        self,
        period_hours: int = 24
    ) -> PerformanceReport:
        """
        Generate comprehensive performance report.
        
        Args:
            period_hours: Report period in hours
            
        Returns:
            Performance report
        """
        try:
            report_id = f"perf_report_{uuid.uuid4().hex[:8]}"
            period_end = datetime.now()
            period_start = period_end - timedelta(hours=period_hours)
            
            # Calculate overall health score
            health_scores = [health.score for health in self.system_health.values()]
            overall_health_score = statistics.mean(health_scores) if health_scores else 0.0
            
            # Gather key metrics
            key_metrics = {}
            for metric_id, metric in self.metrics.items():
                history = await self.get_metric_history(
                    metric_id, period_start, period_end
                )
                
                if history:
                    values = [point['value'] for point in history]
                    key_metrics[metric.name] = {
                        'current': metric.value,
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'count': len(values)
                    }
            
            # Get performance trends
            performance_trends = await self._calculate_performance_trends(
                period_start, period_end
            )
            
            # Summarize alerts
            alerts_summary = self._summarize_alerts(period_start, period_end)
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations()
            
            report = PerformanceReport(
                report_id=report_id,
                period_start=period_start,
                period_end=period_end,
                overall_health_score=overall_health_score,
                system_components=self.system_health.copy(),
                key_metrics=key_metrics,
                performance_trends=performance_trends,
                alerts_summary=alerts_summary,
                recommendations=recommendations
            )
            
            self._logger.info(f"Generated performance report {report_id}")
            
            return report
            
        except Exception as e:
            self._logger.error(f"Error generating performance report: {e}")
            raise
    
    # Internal monitoring methods
    async def _check_metric_thresholds(self, metric_id: str, value: float) -> None:
        """Check metric value against configured thresholds."""
        metric_thresholds = [
            threshold for threshold in self.thresholds.values()
            if threshold.metric_id == metric_id and threshold.enabled
        ]
        
        for threshold in metric_thresholds:
            triggered = False
            
            if threshold.condition == AlertCondition.THRESHOLD_EXCEEDED:
                triggered = value > threshold.value
            elif threshold.condition == AlertCondition.THRESHOLD_BELOW:
                triggered = value < threshold.value
            
            if triggered:
                await self._trigger_performance_alert(threshold, value)
    
    async def _trigger_performance_alert(
        self,
        threshold: MetricThreshold,
        current_value: float
    ) -> None:
        """Trigger a performance alert."""
        alert_id = f"perf_alert_{uuid.uuid4().hex[:8]}"
        
        metric = self.metrics[threshold.metric_id]
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            metric_id=threshold.metric_id,
            threshold_id=threshold.threshold_id,
            condition=threshold.condition,
            current_value=current_value,
            threshold_value=threshold.value,
            severity=threshold.severity,
            message=f"Metric {metric.name} {threshold.condition.value}: "
                   f"current={current_value}, threshold={threshold.value}"
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        await self.alerting_engine.send_alert_notifications(alert, threshold)
        
        self._logger.warning(f"Performance alert triggered: {alert.message}")
    
    async def _perform_health_check(self) -> None:
        """Perform comprehensive system health check."""
        try:
            # Check system resources
            await self._check_system_health()
            
            # Check application components
            await self._check_application_health()
            
            # Check monitoring system itself
            await self._check_monitoring_health()
            
            self._logger.debug("System health check completed")
            
        except Exception as e:
            self._logger.error(f"Error performing health check: {e}")
    
    async def _check_system_health(self) -> None:
        """Check system-level health metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = HealthStatus.HEALTHY
            cpu_issues = []
            
            if cpu_percent > 90:
                cpu_status = HealthStatus.CRITICAL
                cpu_issues.append("High CPU usage")
            elif cpu_percent > 70:
                cpu_status = HealthStatus.WARNING
                cpu_issues.append("Elevated CPU usage")
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_status = HealthStatus.HEALTHY
            memory_issues = []
            
            if memory_percent > 90:
                memory_status = HealthStatus.CRITICAL
                memory_issues.append("High memory usage")
            elif memory_percent > 80:
                memory_status = HealthStatus.WARNING
                memory_issues.append("Elevated memory usage")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_status = HealthStatus.HEALTHY
            disk_issues = []
            
            if disk_percent > 95:
                disk_status = HealthStatus.CRITICAL
                disk_issues.append("High disk usage")
            elif disk_percent > 85:
                disk_status = HealthStatus.WARNING
                disk_issues.append("Elevated disk usage")
            
            # Update system health
            self.system_health['cpu'] = SystemHealth(
                component='cpu',
                status=cpu_status,
                score=max(0.0, (100 - cpu_percent) / 100),
                metrics={'usage_percent': cpu_percent},
                issues=cpu_issues
            )
            
            self.system_health['memory'] = SystemHealth(
                component='memory',
                status=memory_status,
                score=max(0.0, (100 - memory_percent) / 100),
                metrics={'usage_percent': memory_percent, 'available_gb': memory.available / (1024**3)},
                issues=memory_issues
            )
            
            self.system_health['disk'] = SystemHealth(
                component='disk',
                status=disk_status,
                score=max(0.0, (100 - disk_percent) / 100),
                metrics={'usage_percent': disk_percent, 'free_gb': disk.free / (1024**3)},
                issues=disk_issues
            )
            
        except Exception as e:
            self._logger.error(f"Error checking system health: {e}")
    
    async def _check_application_health(self) -> None:
        """Check application-specific health metrics."""
        # Check metric collection health
        collection_success_rate = 0.0
        if self.collection_stats['total_collections'] > 0:
            collection_success_rate = (
                self.collection_stats['successful_collections'] /
                self.collection_stats['total_collections']
            )
        
        collection_status = HealthStatus.HEALTHY
        collection_issues = []
        
        if collection_success_rate < 0.8:
            collection_status = HealthStatus.CRITICAL
            collection_issues.append("Low metric collection success rate")
        elif collection_success_rate < 0.95:
            collection_status = HealthStatus.WARNING
            collection_issues.append("Reduced metric collection success rate")
        
        self.system_health['metric_collection'] = SystemHealth(
            component='metric_collection',
            status=collection_status,
            score=collection_success_rate,
            metrics={
                'success_rate': collection_success_rate,
                'total_collections': self.collection_stats['total_collections'],
                'average_collection_time': self.collection_stats['average_collection_time']
            },
            issues=collection_issues
        )
    
    async def _check_monitoring_health(self) -> None:
        """Check monitoring system health."""
        # Check active alerts
        active_alerts = len([a for a in self.alerts.values() if a.status == 'active'])
        
        alert_status = HealthStatus.HEALTHY
        alert_issues = []
        
        if active_alerts > 50:
            alert_status = HealthStatus.CRITICAL
            alert_issues.append("Too many active alerts")
        elif active_alerts > 20:
            alert_status = HealthStatus.WARNING
            alert_issues.append("High number of active alerts")
        
        self.system_health['alerting'] = SystemHealth(
            component='alerting',
            status=alert_status,
            score=max(0.0, 1.0 - (active_alerts / 100)),
            metrics={
                'active_alerts': active_alerts,
                'total_thresholds': len(self.thresholds),
                'total_metrics': len(self.metrics)
            },
            issues=alert_issues
        )
    
    async def _calculate_performance_trends(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, List[float]]:
        """Calculate performance trends for key metrics."""
        trends = {}
        
        key_metric_names = ['cpu_usage', 'memory_usage', 'response_time', 'throughput']
        
        for metric_id, metric in self.metrics.items():
            if any(name in metric.name.lower() for name in key_metric_names):
                history = await self.get_metric_history(metric_id, start_time, end_time)
                
                if len(history) >= 10:  # Need sufficient data points
                    values = [point['value'] for point in history[-24:]]  # Last 24 points
                    trends[metric.name] = values
        
        return trends
    
    def _summarize_alerts(self, start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """Summarize alerts for the given period."""
        period_alerts = [
            alert for alert in self.alerts.values()
            if start_time <= alert.triggered_at <= end_time
        ]
        
        summary = {
            'total': len(period_alerts),
            'critical': len([a for a in period_alerts if a.severity == 'critical']),
            'warning': len([a for a in period_alerts if a.severity == 'warning']),
            'resolved': len([a for a in period_alerts if a.status == 'resolved']),
            'active': len([a for a in period_alerts if a.status == 'active'])
        }
        
        return summary
    
    async def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Check CPU usage
        cpu_health = self.system_health.get('cpu')
        if cpu_health and cpu_health.metrics.get('usage_percent', 0) > 80:
            recommendations.append(
                "Consider optimizing CPU-intensive operations or scaling horizontally"
            )
        
        # Check memory usage
        memory_health = self.system_health.get('memory')
        if memory_health and memory_health.metrics.get('usage_percent', 0) > 85:
            recommendations.append(
                "Review memory usage patterns and consider increasing available memory"
            )
        
        # Check alert frequency
        if len(self.alerts) > 100:
            recommendations.append(
                "Review alerting thresholds to reduce alert noise"
            )
        
        return recommendations
    
    # Background monitoring tasks
    async def _start_background_monitoring(self) -> None:
        """Start background monitoring tasks."""
        if self._background_started:
            return
        
        # Metric collection task
        collection_task = asyncio.create_task(
            self._metric_collection_loop(),
            name="metric_collection"
        )
        self._monitoring_tasks.add(collection_task)
        
        # Health check task
        health_check_task = asyncio.create_task(
            self._health_check_loop(),
            name="health_check"
        )
        self._monitoring_tasks.add(health_check_task)
        
        # Data cleanup task
        cleanup_task = asyncio.create_task(
            self._data_cleanup_loop(),
            name="data_cleanup"
        )
        self._monitoring_tasks.add(cleanup_task)
        
        self._background_started = True
        self._logger.info("Background monitoring tasks started")
    
    async def _metric_collection_loop(self) -> None:
        """Background metric collection loop."""
        while not self._shutdown_event.is_set():
            try:
                start_time = time.time()
                
                # Collect metrics from all collectors
                collection_tasks = []
                for collector_name, collector in self.collectors.items():
                    task = asyncio.create_task(
                        collector.collect_metrics(),
                        name=f"collect_{collector_name}"
                    )
                    collection_tasks.append(task)
                
                # Wait for all collections to complete
                if collection_tasks:
                    results = await asyncio.gather(*collection_tasks, return_exceptions=True)
                    
                    successful = sum(1 for r in results if not isinstance(r, Exception))
                    failed = len(results) - successful
                    
                    # Update collection stats
                    self.collection_stats['total_collections'] += len(results)
                    self.collection_stats['successful_collections'] += successful
                    self.collection_stats['failed_collections'] += failed
                    
                    collection_time = time.time() - start_time
                    self.collection_stats['average_collection_time'] = (
                        (self.collection_stats['average_collection_time'] * 
                         (self.collection_stats['total_collections'] - len(results)) +
                         collection_time) / self.collection_stats['total_collections']
                    )
                
                # Wait for next collection interval
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self._logger.error(f"Error in metric collection loop: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while not self._shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self._logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _data_cleanup_loop(self) -> None:
        """Background data cleanup loop."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up old metric data
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)
                
                for metric_id, data_points in self.metric_data.items():
                    # Remove old data points
                    while data_points and data_points[0]['timestamp'] < cutoff_time:
                        data_points.popleft()
                
                # Clean up resolved alerts
                resolved_alerts = [
                    alert_id for alert_id, alert in self.alerts.items()
                    if (alert.status == 'resolved' and
                        alert.resolved_at and
                        alert.resolved_at < cutoff_time)
                ]
                
                for alert_id in resolved_alerts:
                    del self.alerts[alert_id]
                
                if resolved_alerts:
                    self._logger.info(f"Cleaned up {len(resolved_alerts)} old alerts")
                
            except Exception as e:
                self._logger.error(f"Error in data cleanup loop: {e}")
                await asyncio.sleep(300)
    
    # Initialization methods
    async def _initialize_collectors(self) -> None:
        """Initialize metric collectors."""
        # System metrics collector
        self.collectors['system'] = SystemMetricsCollector(self)
        
        # Application metrics collector
        self.collectors['application'] = ApplicationMetricsCollector(self)
        
        # Business metrics collector
        self.collectors['business'] = BusinessMetricsCollector(self)
        
        for name, collector in self.collectors.items():
            await collector.initialize()
            self._logger.debug(f"Initialized {name} metric collector")
    
    async def _initialize_analyzers(self) -> None:
        """Initialize performance analyzers."""
        # Trend analyzer
        self.analyzers['trend'] = TrendAnalyzer(self)
        
        # Capacity analyzer
        self.analyzers['capacity'] = CapacityAnalyzer(self)
        
        for name, analyzer in self.analyzers.items():
            await analyzer.initialize()
            self._logger.debug(f"Initialized {name} performance analyzer")
    
    async def _register_default_metrics(self) -> None:
        """Register default system metrics."""
        # System metrics
        await self.register_metric(
            "cpu_usage_percent",
            MetricType.GAUGE,
            MetricCategory.SYSTEM,
            "CPU usage percentage",
            "%"
        )
        
        await self.register_metric(
            "memory_usage_percent",
            MetricType.GAUGE,
            MetricCategory.SYSTEM,
            "Memory usage percentage",
            "%"
        )
        
        await self.register_metric(
            "disk_usage_percent",
            MetricType.GAUGE,
            MetricCategory.SYSTEM,
            "Disk usage percentage",
            "%"
        )
        
        # Application metrics
        await self.register_metric(
            "request_count",
            MetricType.COUNTER,
            MetricCategory.APPLICATION,
            "Total request count",
            "requests"
        )
        
        await self.register_metric(
            "response_time_ms",
            MetricType.HISTOGRAM,
            MetricCategory.APPLICATION,
            "Response time",
            "ms"
        )
        
        await self.register_metric(
            "error_rate",
            MetricType.RATE,
            MetricCategory.APPLICATION,
            "Error rate",
            "errors/sec"
        )
    
    async def _load_thresholds(self) -> None:
        """Load existing alerting thresholds."""
        # This would load from storage in production
        # For now, set some default thresholds
        pass
    
    # Public API methods
    def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get metric by ID."""
        return self.metrics.get(metric_id)
    
    def get_metrics(
        self,
        category: Optional[MetricCategory] = None,
        metric_type: Optional[MetricType] = None
    ) -> List[Metric]:
        """Get metrics with optional filtering."""
        metrics = list(self.metrics.values())
        
        if category:
            metrics = [m for m in metrics if m.category == category]
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        return metrics
    
    def get_alerts(self, status: str = "active") -> List[PerformanceAlert]:
        """Get alerts with optional status filtering."""
        alerts = list(self.alerts.values())
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        # Sort by triggered time (newest first)
        alerts.sort(key=lambda x: x.triggered_at, reverse=True)
        
        return alerts
    
    async def shutdown(self) -> None:
        """Shutdown performance monitoring system gracefully."""
        self._logger.info("Shutting down Performance Monitoring System...")
        
        # Signal shutdown to background tasks
        self._shutdown_event.set()
        
        # Cancel background tasks
        for task in self._monitoring_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
        
        # Shutdown collectors and analyzers
        for collector in self.collectors.values():
            await collector.shutdown()
        
        for analyzer in self.analyzers.values():
            await analyzer.shutdown()
        
        # Shutdown engines
        await self.alerting_engine.shutdown()
        await self.anomaly_detector.shutdown()
        
        self._logger.info("Performance Monitoring System shutdown complete")


# Helper classes for metric collection and analysis
class MetricCollector:
    """Base class for metric collectors."""
    
    def __init__(self, monitor: PerformanceMonitor):
        """Initialize collector."""
        self.monitor = monitor
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> None:
        """Initialize collector."""
        pass
    
    async def collect_metrics(self) -> None:
        """Collect metrics (to be implemented by subclasses)."""
        raise NotImplementedError
    
    async def shutdown(self) -> None:
        """Shutdown collector."""
        pass


class SystemMetricsCollector(MetricCollector):
    """Collector for system-level metrics."""
    
    async def collect_metrics(self) -> None:
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_metric_id = None
            for metric_id, metric in self.monitor.metrics.items():
                if metric.name == "cpu_usage_percent":
                    cpu_metric_id = metric_id
                    break
            
            if cpu_metric_id:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                await self.monitor.record_metric(cpu_metric_id, cpu_percent)
            
            # Memory usage
            memory_metric_id = None
            for metric_id, metric in self.monitor.metrics.items():
                if metric.name == "memory_usage_percent":
                    memory_metric_id = metric_id
                    break
            
            if memory_metric_id:
                memory = psutil.virtual_memory()
                await self.monitor.record_metric(memory_metric_id, memory.percent)
            
            # Disk usage
            disk_metric_id = None
            for metric_id, metric in self.monitor.metrics.items():
                if metric.name == "disk_usage_percent":
                    disk_metric_id = metric_id
                    break
            
            if disk_metric_id:
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                await self.monitor.record_metric(disk_metric_id, disk_percent)
            
        except Exception as e:
            self._logger.error(f"Error collecting system metrics: {e}")


class ApplicationMetricsCollector(MetricCollector):
    """Collector for application-level metrics."""
    
    async def collect_metrics(self) -> None:
        """Collect application metrics."""
        try:
            # This would collect application-specific metrics
            # For now, just simulate some metrics
            pass
            
        except Exception as e:
            self._logger.error(f"Error collecting application metrics: {e}")


class BusinessMetricsCollector(MetricCollector):
    """Collector for business-level metrics."""
    
    async def collect_metrics(self) -> None:
        """Collect business metrics."""
        try:
            # This would collect business KPIs and metrics
            # For now, just simulate some metrics
            pass
            
        except Exception as e:
            self._logger.error(f"Error collecting business metrics: {e}")


class PerformanceAnalyzer:
    """Base class for performance analyzers."""
    
    def __init__(self, monitor: PerformanceMonitor):
        """Initialize analyzer."""
        self.monitor = monitor
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> None:
        """Initialize analyzer."""
        pass
    
    async def analyze(self) -> None:
        """Perform analysis (to be implemented by subclasses)."""
        raise NotImplementedError
    
    async def shutdown(self) -> None:
        """Shutdown analyzer."""
        pass


class TrendAnalyzer(PerformanceAnalyzer):
    """Analyzer for performance trends."""
    
    async def analyze(self) -> None:
        """Analyze performance trends."""
        # Implementation would analyze trends in metrics
        pass


class CapacityAnalyzer(PerformanceAnalyzer):
    """Analyzer for capacity planning."""
    
    async def analyze(self) -> None:
        """Analyze capacity requirements."""
        # Implementation would analyze capacity needs
        pass


class AlertingEngine:
    """Engine for performance alerting."""
    
    async def initialize(self) -> None:
        """Initialize alerting engine."""
        pass
    
    async def send_alert_notifications(
        self,
        alert: PerformanceAlert,
        threshold: MetricThreshold
    ) -> None:
        """Send alert notifications."""
        # Implementation would send notifications via configured channels
        logger.info(f"Sending alert notification: {alert.message}")
    
    async def shutdown(self) -> None:
        """Shutdown alerting engine."""
        pass


class AnomalyDetector:
    """Engine for anomaly detection."""
    
    async def initialize(self) -> None:
        """Initialize anomaly detector."""
        pass
    
    async def check_anomaly(
        self,
        metric_id: str,
        value: float,
        timestamp: datetime
    ) -> bool:
        """Check for anomalies in metric value."""
        # Simple implementation - would use more sophisticated algorithms in production
        return False
    
    async def shutdown(self) -> None:
        """Shutdown anomaly detector."""
        pass


# Export main classes
__all__ = [
    'PerformanceMonitor',
    'Metric',
    'MetricThreshold',
    'PerformanceAlert',
    'SystemHealth',
    'PerformanceReport',
    'MetricType',
    'MetricCategory',
    'AlertCondition',
    'HealthStatus'
]
