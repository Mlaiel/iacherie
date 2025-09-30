"""📈 Detection Metrics and Analytics
==================================

Advanced metrics collection and analytics for piracy detection system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides:
- Real-time performance metrics collection
- System health monitoring and alerting
- Advanced analytics and insights
- Performance optimization recommendations
- Comprehensive dashboards and KPIs
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import json

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """
Types of metrics collected."""

    DETECTION_PERFORMANCE = "detection_performance"
    SYSTEM_PERFORMANCE = "system_performance"
    ENFORCEMENT_METRICS = "enforcement_metrics"
    REVENUE_METRICS = "revenue_metrics"
    USER_ENGAGEMENT = "user_engagement"
    PLATFORM_METRICS = "platform_metrics"

class MetricAggregation(Enum):
    """Metric aggregation methods."""

    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"

@dataclass
class MetricPoint:
    """Individual metric data point."""
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    context: Dict[str, Any]

@dataclass
class AggregatedMetric:
    """
Aggregated metric result."""
    metric_name: str
    aggregation: MetricAggregation
    value: float
    time_range_start: datetime
    time_range_end: datetime
    sample_count: int
    confidence_interval: Tuple[float, float]

class DetectionMetrics:
    """
    Advanced metrics collection and analytics system.
    
    Provides comprehensive metrics collection, real-time analytics,
    and performance monitoring for the piracy detection system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Detection Metrics system.
        
        Args:
            config: Metrics configuration parameters
        """
        self.config = config or {}
        self._initialized = False
        
        # Metrics configuration
        self.retention_days = self.config.get('retention_days', 90)
        self.aggregation_intervals = self.config.get('aggregation_intervals', [
            '1m', '5m', '15m', '1h', '6h', '24h'
        ])
        self.alert_thresholds = self.config.get('alert_thresholds', {})
        
        # Metrics storage
        self.raw_metrics: List[MetricPoint] = []
        self.aggregated_metrics: Dict[str, List[AggregatedMetric]] = {}
        self.metric_definitions = {}
        
        # Performance tracking
        self.performance_baselines = {}
        self.anomaly_detector = None
        self.trend_analyzer = None
        
        # Real-time metrics
        self.current_metrics = {}
        self.metric_streams = {}
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_ttl_seconds = 300  # 5 minutes
        
        logger.info("Detection Metrics system initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize metrics system components.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Detection Metrics system...")
            
            # Initialize metric definitions
            await self._initialize_metric_definitions()
            
            # Initialize performance baselines
            await self._initialize_performance_baselines()
            
            # Initialize anomaly detection
            await self._initialize_anomaly_detector()
            
            # Initialize trend analyzer
            await self._initialize_trend_analyzer()
            
            # Start metrics aggregation task
            asyncio.create_task(self._metrics_aggregation_task())
            
            # Start anomaly detection task
            asyncio.create_task(self._anomaly_detection_task())
            
            # Start metrics cleanup task
            asyncio.create_task(self._metrics_cleanup_task())
            
            self._initialized = True
            logger.info("Detection Metrics system successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Detection Metrics system: {str(e)}")
            return False
    
    async def _initialize_metric_definitions(self) -> None:
        """Initialize metric definitions and metadata."""
        self.metric_definitions = {
            # Detection Performance Metrics
            'detection_accuracy': {
                'type': MetricType.DETECTION_PERFORMANCE,
                'unit': 'percentage',
                'description': 'Accuracy of piracy detection algorithm',
                'target_range': (0.90, 1.0),
                'alert_threshold': 0.85
            },
            'false_positive_rate': {
                'type': MetricType.DETECTION_PERFORMANCE,
                'unit': 'percentage',
                'description': 'Rate of false positive detections',
                'target_range': (0.0, 0.10),
                'alert_threshold': 0.15
            },
            'detection_latency': {
                'type': MetricType.DETECTION_PERFORMANCE,
                'unit': 'milliseconds',
                'description': 'Time taken to detect violations',
                'target_range': (0, 5000),
                'alert_threshold': 10000
            },
            'confidence_score_avg': {
                'type': MetricType.DETECTION_PERFORMANCE,
                'unit': 'score',
                'description': 'Average confidence score of detections',
                'target_range': (0.80, 1.0),
                'alert_threshold': 0.70
            },
            
            # System Performance Metrics
            'api_response_time': {
                'type': MetricType.SYSTEM_PERFORMANCE,
                'unit': 'milliseconds',
                'description': 'API endpoint response times',
                'target_range': (0, 1000),
                'alert_threshold': 2000
            },
            'system_uptime': {
                'type': MetricType.SYSTEM_PERFORMANCE,
                'unit': 'percentage',
                'description': 'System availability and uptime',
                'target_range': (0.99, 1.0),
                'alert_threshold': 0.95
            },
            'memory_usage': {
                'type': MetricType.SYSTEM_PERFORMANCE,
                'unit': 'percentage',
                'description': 'Memory utilization',
                'target_range': (0, 80),
                'alert_threshold': 90
            },
            'cpu_usage': {
                'type': MetricType.SYSTEM_PERFORMANCE,
                'unit': 'percentage',
                'description': 'CPU utilization',
                'target_range': (0, 70),
                'alert_threshold': 85
            },
            
            # Enforcement Metrics
            'enforcement_success_rate': {
                'type': MetricType.ENFORCEMENT_METRICS,
                'unit': 'percentage',
                'description': 'Success rate of enforcement actions',
                'target_range': (0.80, 1.0),
                'alert_threshold': 0.70
            },
            'enforcement_response_time': {
                'type': MetricType.ENFORCEMENT_METRICS,
                'unit': 'hours',
                'description': 'Time from detection to enforcement',
                'target_range': (0, 24),
                'alert_threshold': 72
            },
            
            # Revenue Metrics
            'revenue_protected': {
                'type': MetricType.REVENUE_METRICS,
                'unit': 'currency',
                'description': 'Revenue protected from piracy',
                'target_range': (0, float('inf')),
                'alert_threshold': None
            },
            'roi_percentage': {
                'type': MetricType.REVENUE_METRICS,
                'unit': 'percentage',
                'description': 'Return on investment for protection',
                'target_range': (200, float('inf')),
                'alert_threshold': 100
            }
        }
        
        logger.info(f"Initialized {len(self.metric_definitions)} metric definitions")
    
    async def _initialize_performance_baselines(self) -> None:
        """Initialize performance baselines for comparison."""
        self.performance_baselines = {
            'detection_accuracy': 0.92,
            'false_positive_rate': 0.08,
            'detection_latency': 2500,
            'api_response_time': 150,
            'enforcement_success_rate': 0.85,
            'enforcement_response_time': 18.5
        }
        
        logger.info("Performance baselines initialized")
    
    async def _initialize_anomaly_detector(self) -> None:
        """Initialize anomaly detection system."""
        self.anomaly_detector = {
            'algorithms': ['statistical', 'isolation_forest', 'lstm'],
            'sensitivity': 0.95,
            'min_samples': 100,
            'enabled': True
        }
        
        logger.info("Anomaly detector initialized")
    
    async def _initialize_trend_analyzer(self) -> None:
        """Initialize trend analysis system."""
        self.trend_analyzer = {
            'algorithms': ['linear_regression', 'seasonal_decomposition', 'arima'],
            'forecast_horizon_days': 30,
            'confidence_level': 0.95,
            'enabled': True
        }
        
        logger.info("Trend analyzer initialized")
    
    async def record_metric(self, metric_name: str, value: float, 
                          tags: Optional[Dict[str, str]] = None,
                          context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a single metric point.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for metric categorization
            context: Optional additional context data
        """
        if not self._initialized:
            logger.warning("Metrics system not initialized, skipping metric recording")
            return
        
        # Validate metric name
        if metric_name not in self.metric_definitions:
            logger.warning(f"Unknown metric: {metric_name}")
            return
        
        metric_def = self.metric_definitions[metric_name]
        
        # Create metric point
        metric_point = MetricPoint(
            metric_name=metric_name,
            metric_type=metric_def['type'],
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            context=context or {}
        )
        
        # Store raw metric
        self.raw_metrics.append(metric_point)
        
        # Update current metrics
        self.current_metrics[metric_name] = metric_point
        
        # Check for alerts
        await self._check_metric_alerts(metric_point)
        
        # Cleanup old metrics periodically
        if len(self.raw_metrics) % 1000 == 0:
            await self._cleanup_old_metrics()
    
    async def record_detection_scan(self, content_id: str, platform: str, 
                                  violations_found: int, scan_duration_ms: float,
                                  confidence_scores: List[float]) -> None:
        """
        Record metrics for a detection scan.
        
        Args:
            content_id: Content being scanned
            platform: Platform scanned
            violations_found: Number of violations found
            scan_duration_ms: Scan duration in milliseconds
            confidence_scores: List of confidence scores for violations
        """
        tags = {'platform': platform, 'content_id': content_id}
        
        # Record scan duration
        await self.record_metric('detection_latency', scan_duration_ms, tags)
        
        # Record violations found
        await self.record_metric('violations_detected', violations_found, tags)
        
        # Record confidence scores
        if confidence_scores:
            avg_confidence = statistics.mean(confidence_scores)
            await self.record_metric('confidence_score_avg', avg_confidence, tags)
            
            # Record confidence distribution
            high_confidence_count = sum(1 for score in confidence_scores if score >= 0.9)
            high_confidence_rate = high_confidence_count / len(confidence_scores)
            await self.record_metric('high_confidence_rate', high_confidence_rate, tags)
    
    async def record_monitoring_scan(self, session_id: str, content_id: str,
                                   violations_found: int, platforms_scanned: int) -> None:
        """
        Record metrics for a monitoring scan.
        
        Args:
            session_id: Monitoring session ID
            content_id: Content being monitored
            violations_found: Number of violations found
            platforms_scanned: Number of platforms scanned
        """
        tags = {'session_id': session_id, 'content_id': content_id}
        
        await self.record_metric('monitoring_violations_found', violations_found, tags)
        await self.record_metric('monitoring_platforms_scanned', platforms_scanned, tags)
    
    async def record_enforcement_action(self, enforcement_id: str, platform: str,
                                      action_type: str, success: bool,
                                      response_time_hours: float) -> None:
        """
        Record metrics for enforcement actions.
        
        Args:
            enforcement_id: Enforcement request ID
            platform: Target platform
            action_type: Type of enforcement action
            success: Whether enforcement was successful
            response_time_hours: Time from submission to response
        """
        tags = {
            'platform': platform,
            'action_type': action_type,
            'enforcement_id': enforcement_id
        }
        
        # Record success/failure
        success_value = 1.0 if success else 0.0
        await self.record_metric('enforcement_success', success_value, tags)
        
        # Record response time
        await self.record_metric('enforcement_response_time', response_time_hours, tags)
    
    async def record_system_performance(self, cpu_percent: float, memory_percent: float,
                                      disk_usage_percent: float, network_io_mbps: float) -> None:
        """
        Record system performance metrics.
        
        Args:
            cpu_percent: CPU utilization percentage
            memory_percent: Memory utilization percentage
            disk_usage_percent: Disk usage percentage
            network_io_mbps: Network I/O in Mbps
        """
        await self.record_metric('cpu_usage', cpu_percent)
        await self.record_metric('memory_usage', memory_percent)
        await self.record_metric('disk_usage', disk_usage_percent)
        await self.record_metric('network_io', network_io_mbps)
    
    async def get_metric_summary(self, metric_name: str, 
                               time_range_hours: int = 24) -> Dict[str, Any]:
        """
        Get summary statistics for a metric.
        
        Args:
            metric_name: Name of metric to summarize
            time_range_hours: Time range in hours for analysis
            
        Returns:
            Metric summary statistics
        """
        if metric_name not in self.metric_definitions:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # Filter metrics by time range
        relevant_metrics = [
            m for m in self.raw_metrics
            if m.metric_name == metric_name and start_time <= m.timestamp <= end_time
        ]
        
        if not relevant_metrics:
            return {
                'metric_name': metric_name,
                'time_range_hours': time_range_hours,
                'sample_count': 0,
                'summary': 'No data available'
            }
        
        # Calculate statistics
        values = [m.value for m in relevant_metrics]
        
        summary = {
            'metric_name': metric_name,
            'time_range_hours': time_range_hours,
            'sample_count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'percentile_95': self._calculate_percentile(values, 95),
            'percentile_99': self._calculate_percentile(values, 99),
            'current_value': relevant_metrics[-1].value,
            'trend': await self._calculate_trend(relevant_metrics),
            'baseline_comparison': await self._compare_to_baseline(metric_name, statistics.mean(values))
        }
        
        return summary
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive performance dashboard data.
        
        Returns:
            Dashboard data with key metrics and insights
        """
        cache_key = 'performance_dashboard'
        
        # Check cache
        if cache_key in self.analytics_cache:
            cached_data = self.analytics_cache[cache_key]
            if (datetime.utcnow() - cached_data['timestamp']).total_seconds() < self.cache_ttl_seconds:
                return cached_data['data']
        
        # Generate dashboard data
        dashboard = {
            'generated_at': datetime.utcnow().isoformat(),
            'system_health': await self._get_system_health_status(),
            'detection_performance': await self._get_detection_performance_summary(),
            'enforcement_metrics': await self._get_enforcement_metrics_summary(),
            'platform_breakdown': await self._get_platform_performance_breakdown(),
            'alerts_summary': await self._get_active_alerts_summary(),
            'trends': await self._get_key_trends(),
            'recommendations': await self._get_performance_recommendations()
        }
        
        # Cache result
        self.analytics_cache[cache_key] = {
            'data': dashboard,
            'timestamp': datetime.utcnow()
        }
        
        return dashboard
    
    async def _get_system_health_status(self) -> Dict[str, Any]:
        """
Get overall system health status."""
        health_metrics = ['system_uptime', 'api_response_time', 'memory_usage', 'cpu_usage']
        health_scores = []
        
        for metric_name in health_metrics:
            if metric_name in self.current_metrics:
                current_value = self.current_metrics[metric_name].value
                metric_def = self.metric_definitions[metric_name]
                
                # Calculate health score based on target range
                target_range = metric_def.get('target_range', (0, 100))
                if metric_name in ['system_uptime']:
                    # Higher is better
                    health_score = min(1.0, current_value / target_range[1])
                else:
                    # Lower is better for response times and usage
                    health_score = max(0.0, 1.0 - (current_value / target_range[1]))
                
                health_scores.append(health_score)
        
        overall_health = statistics.mean(health_scores) if health_scores else 0.5
        
        return {
            'overall_health_score': overall_health,
            'status': 'healthy' if overall_health > 0.8 else 'warning' if overall_health > 0.6 else 'critical',
            'individual_scores': dict(zip(health_metrics, health_scores)),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def _get_detection_performance_summary(self) -> Dict[str, Any]:
        """
Get detection performance summary."""
        detection_metrics = ['detection_accuracy', 'false_positive_rate', 'confidence_score_avg', 'detection_latency']
        
        summary = {}
        for metric_name in detection_metrics:
            metric_summary = await self.get_metric_summary(metric_name, 24)
            summary[metric_name] = {
                'current': metric_summary.get('current_value', 0),
                'avg_24h': metric_summary.get('mean', 0),
                'trend': metric_summary.get('trend', 'stable')
            }
        
        return summary
    
    async def _get_enforcement_metrics_summary(self) -> Dict[str, Any]:
        """
Get enforcement metrics summary."""
        enforcement_metrics = ['enforcement_success_rate', 'enforcement_response_time']
        
        summary = {}
        for metric_name in enforcement_metrics:
            metric_summary = await self.get_metric_summary(metric_name, 24)
            summary[metric_name] = {
                'current': metric_summary.get('current_value', 0),
                'avg_24h': metric_summary.get('mean', 0),
                'trend': metric_summary.get('trend', 'stable')
            }
        
        return summary
    
    async def _get_platform_performance_breakdown(self) -> Dict[str, Any]:
        """
Get performance breakdown by platform."""
        platforms = ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook']
        platform_data = {}
        
        for platform in platforms:
            # Get metrics for this platform
            platform_metrics = [
                m for m in self.raw_metrics[-1000:]  # Last 1000 metrics
                if m.tags.get('platform') == platform
            ]
            
            if platform_metrics:
                violations = [m.value for m in platform_metrics if m.metric_name == 'violations_detected']
                enforcement_success = [m.value for m in platform_metrics if m.metric_name == 'enforcement_success']
                
                platform_data[platform] = {
                    'total_violations': sum(violations),
                    'success_rate': statistics.mean(enforcement_success) if enforcement_success else 0,
                    'activity_level': 'high' if len(platform_metrics) > 50 else 'medium' if len(platform_metrics) > 20 else 'low'
                }
        
        return platform_data
    
    async def _get_active_alerts_summary(self) -> Dict[str, Any]:
        """
Get summary of active alerts."""
        # Check current metrics against thresholds
        active_alerts = []
        
        for metric_name, current_metric in self.current_metrics.items():
            metric_def = self.metric_definitions.get(metric_name, {})
            alert_threshold = metric_def.get('alert_threshold')
            
            if alert_threshold is not None:
                if (metric_name in ['detection_accuracy', 'system_uptime', 'enforcement_success_rate'] and
                    current_metric.value < alert_threshold):
                    active_alerts.append({
                        'metric': metric_name,
                        'current_value': current_metric.value,
                        'threshold': alert_threshold,
                        'severity': 'high' if current_metric.value < alert_threshold * 0.9 else 'medium'
                    })
                elif (metric_name in ['false_positive_rate', 'detection_latency', 'api_response_time'] and
                      current_metric.value > alert_threshold):
                    active_alerts.append({
                        'metric': metric_name,
                        'current_value': current_metric.value,
                        'threshold': alert_threshold,
                        'severity': 'high' if current_metric.value > alert_threshold * 1.5 else 'medium'
                    })
        
        return {
            'total_alerts': len(active_alerts),
            'high_severity': len([a for a in active_alerts if a['severity'] == 'high']),
            'medium_severity': len([a for a in active_alerts if a['severity'] == 'medium']),
            'alerts': active_alerts
        }
    
    async def _get_key_trends(self) -> Dict[str, Any]:
        """
Get key performance trends."""
        key_metrics = ['detection_accuracy', 'enforcement_success_rate', 'api_response_time']
        trends = {}
        
        for metric_name in key_metrics:
            # Get last 7 days of data
            recent_metrics = [
                m for m in self.raw_metrics
                if (m.metric_name == metric_name and 
                    m.timestamp >= datetime.utcnow() - timedelta(days=7))
            ]
            
            if len(recent_metrics) >= 2:
                trend = await self._calculate_trend(recent_metrics)
                trends[metric_name] = trend
        
        return trends
    
    async def _get_performance_recommendations(self) -> List[str]:
        """
Get performance optimization recommendations."""
        recommendations = []
        
        # Check detection accuracy
        if 'detection_accuracy' in self.current_metrics:
            accuracy = self.current_metrics['detection_accuracy'].value
            if accuracy < 0.9:
                recommendations.append("Consider retraining detection models to improve accuracy")
        
        # Check false positive rate
        if 'false_positive_rate' in self.current_metrics:
            fp_rate = self.current_metrics['false_positive_rate'].value
            if fp_rate > 0.1:
                recommendations.append("Optimize detection thresholds to reduce false positives")
        
        # Check response times
        if 'api_response_time' in self.current_metrics:
            response_time = self.current_metrics['api_response_time'].value
            if response_time > 1000:
                recommendations.append("Optimize API performance to reduce response times")
        
        # Check system resources
        if 'memory_usage' in self.current_metrics:
            memory_usage = self.current_metrics['memory_usage'].value
            if memory_usage > 80:
                recommendations.append("Consider scaling system resources due to high memory usage")
        
        return recommendations
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    async def _calculate_trend(self, metrics: List[MetricPoint]) -> str:
        """
Calculate trend direction for metrics."""
        if len(metrics) < 2:
            return 'stable'
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        values = [m.value for m in sorted_metrics]
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return 'stable'
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_threshold = 0.05  # 5% change threshold
        relative_change = abs(second_avg - first_avg) / first_avg if first_avg != 0 else 0
        
        if relative_change < change_threshold:
            return 'stable'
        elif second_avg > first_avg:
            return 'increasing'
        else:
            return 'decreasing'
    
    async def _compare_to_baseline(self, metric_name: str, current_value: float) -> Dict[str, Any]:
        """
Compare current value to baseline."""
        baseline = self.performance_baselines.get(metric_name)
        if baseline is None:
            return {'status': 'no_baseline', 'difference': 0}
        
        difference = current_value - baseline
        relative_difference = difference / baseline if baseline != 0 else 0
        
        # Determine status based on metric type
        metric_def = self.metric_definitions.get(metric_name, {})
        unit = metric_def.get('unit', '')
        
        if metric_name in ['detection_accuracy', 'enforcement_success_rate', 'system_uptime']:
            # Higher is better
            status = 'better' if difference > 0 else 'worse' if difference < 0 else 'same'
        else:
            # Lower is better (latency, error rates, etc.)
            status = 'better' if difference < 0 else 'worse' if difference > 0 else 'same'
        
        return {
            'status': status,
            'difference': difference,
            'relative_difference': relative_difference,
            'baseline': baseline,
            'current': current_value
        }
    
    async def _check_metric_alerts(self, metric_point: MetricPoint) -> None:
        """
Check if metric triggers any alerts."""
        metric_def = self.metric_definitions.get(metric_point.metric_name, {})
        alert_threshold = metric_def.get('alert_threshold')
        
        if alert_threshold is not None:
            should_alert = False
            
            # Check if threshold is crossed
            if metric_point.metric_name in ['detection_accuracy', 'system_uptime', 'enforcement_success_rate']:
                # Lower values are bad
                should_alert = metric_point.value < alert_threshold
            else:
                # Higher values are bad
                should_alert = metric_point.value > alert_threshold
            
            if should_alert:
                await self._send_metric_alert(metric_point, alert_threshold)
    
    async def _send_metric_alert(self, metric_point: MetricPoint, threshold: float) -> None:
        """
Send alert for metric threshold violation."""
        alert_data = {
            'metric_name': metric_point.metric_name,
            'current_value': metric_point.value,
            'threshold': threshold,
            'timestamp': metric_point.timestamp.isoformat(),
            'tags': metric_point.tags,
            'severity': 'high' if abs(metric_point.value - threshold) / threshold > 0.5 else 'medium'
        }
        
        # In production, this would send to alerting system
        logger.warning(f"Metric alert: {metric_point.metric_name} = {metric_point.value} (threshold: {threshold})")
    
    async def _metrics_aggregation_task(self) -> None:
        """Background task for metrics aggregation."""
        while True:
            try:
                # Aggregate metrics every 5 minutes
                await self._aggregate_metrics()
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in metrics aggregation task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _aggregate_metrics(self) -> None:
        """Aggregate raw metrics into time-based summaries."""
        # Group metrics by name and time interval
        time_intervals = [
            ('1h', timedelta(hours=1)),
            ('6h', timedelta(hours=6)),
            ('24h', timedelta(hours=24))
        ]
        
        for interval_name, interval_duration in time_intervals:
            current_time = datetime.utcnow()
            start_time = current_time - interval_duration
            
            # Group metrics by name
            metric_groups = {}
            for metric in self.raw_metrics:
                if start_time <= metric.timestamp <= current_time:
                    if metric.metric_name not in metric_groups:
                        metric_groups[metric.metric_name] = []
                    metric_groups[metric.metric_name].append(metric)
            
            # Create aggregated metrics
            for metric_name, metrics in metric_groups.items():
                if len(metrics) >= 2:  # Need at least 2 points for aggregation
                    values = [m.value for m in metrics]
                    
                    # Calculate aggregations
                    aggregations = {
                        MetricAggregation.AVERAGE: statistics.mean(values),
                        MetricAggregation.MIN: min(values),
                        MetricAggregation.MAX: max(values),
                        MetricAggregation.COUNT: len(values),
                        MetricAggregation.PERCENTILE_95: self._calculate_percentile(values, 95),
                        MetricAggregation.PERCENTILE_99: self._calculate_percentile(values, 99)
                    }
                    
                    # Store aggregated metrics
                    for agg_type, agg_value in aggregations.items():
                        agg_key = f"{metric_name}_{interval_name}_{agg_type.value}"
                        
                        if agg_key not in self.aggregated_metrics:
                            self.aggregated_metrics[agg_key] = []
                        
                        agg_metric = AggregatedMetric(
                            metric_name=metric_name,
                            aggregation=agg_type,
                            value=agg_value,
                            time_range_start=start_time,
                            time_range_end=current_time,
                            sample_count=len(values),
                            confidence_interval=(min(values), max(values))  # Simplified CI
                        )
                        
                        self.aggregated_metrics[agg_key].append(agg_metric)
                        
                        # Keep only last 100 aggregated metrics per key
                        if len(self.aggregated_metrics[agg_key]) > 100:
                            self.aggregated_metrics[agg_key] = self.aggregated_metrics[agg_key][-100:]
    
    async def _anomaly_detection_task(self) -> None:
        """Background task for anomaly detection."""
        while True:
            try:
                await self._detect_anomalies()
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in anomaly detection task: {str(e)}")
                await asyncio.sleep(300)
    
    async def _detect_anomalies(self) -> None:
        """Detect anomalies in metrics."""
        if not self.anomaly_detector['enabled']:
            return
        
        # Simple statistical anomaly detection
        for metric_name in self.metric_definitions.keys():
            recent_metrics = [
                m for m in self.raw_metrics[-1000:]  # Last 1000 metrics
                if m.metric_name == metric_name
            ]
            
            if len(recent_metrics) >= self.anomaly_detector['min_samples']:
                values = [m.value for m in recent_metrics]
                
                # Calculate statistical boundaries
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else 0
                
                # Define anomaly threshold (2 standard deviations)
                threshold = 2 * std_val
                
                # Check recent values for anomalies
                recent_values = values[-10:]  # Last 10 values
                for i, value in enumerate(recent_values):
                    if abs(value - mean_val) > threshold:
                        await self._handle_anomaly(metric_name, value, mean_val, threshold)
    
    async def _handle_anomaly(self, metric_name: str, anomalous_value: float, 
                            expected_value: float, threshold: float) -> None:
        """
Handle detected anomaly."""
        anomaly_data = {
            'metric_name': metric_name,
            'anomalous_value': anomalous_value,
            'expected_value': expected_value,
            'threshold': threshold,
            'deviation': abs(anomalous_value - expected_value),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.warning(f"Anomaly detected in {metric_name}: {anomalous_value} (expected: {expected_value:.2f})")
        
        # In production, this would trigger alerting systems
    
    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics based on retention policy."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # Remove old raw metrics
        self.raw_metrics = [
            m for m in self.raw_metrics
            if m.timestamp > cutoff_date
        ]
        
        # Clean up aggregated metrics
        for key in list(self.aggregated_metrics.keys()):
            self.aggregated_metrics[key] = [
                m for m in self.aggregated_metrics[key]
                if m.time_range_end > cutoff_date
            ]
            
            # Remove empty keys
            if not self.aggregated_metrics[key]:
                del self.aggregated_metrics[key]
    
    async def _metrics_cleanup_task(self) -> None:
        """
Background task for periodic metrics cleanup."""
        while True:
            try:
                await self._cleanup_old_metrics()
                
                # Clear analytics cache
                self.analytics_cache.clear()
                
                logger.info(f"Metrics cleanup completed. Current metrics count: {len(self.raw_metrics)}")
                
                # Run cleanup daily
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Error in metrics cleanup task: {str(e)}")
                await asyncio.sleep(3600)  # Retry after 1 hour
    
    async def get_metrics_stats(self) -> Dict[str, Any]:
        """Get metrics system statistics."""
        return {
            'total_raw_metrics': len(self.raw_metrics),
            'total_aggregated_metrics': sum(len(metrics) for metrics in self.aggregated_metrics.values()),
            'active_metric_types': len(set(m.metric_name for m in self.raw_metrics[-1000:])),
            'retention_days': self.retention_days,
            'cache_size': len(self.analytics_cache),
            'oldest_metric': min(m.timestamp for m in self.raw_metrics).isoformat() if self.raw_metrics else None,
            'newest_metric': max(m.timestamp for m in self.raw_metrics).isoformat() if self.raw_metrics else None
        }
    
    async def shutdown(self) -> None:
        """
Gracefully shutdown the metrics system."""
        logger.info("Shutting down Detection Metrics system...")
        
        # Final metrics aggregation
        await self._aggregate_metrics()
        
        # Clear caches
        self.analytics_cache.clear()
        
        logger.info("Detection Metrics system shutdown complete")
