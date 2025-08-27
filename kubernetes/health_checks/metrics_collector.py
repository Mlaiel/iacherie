"""
Health Metrics Collection and Analytics Service
Advanced metrics collection, aggregation, and performance analytics

This module provides comprehensive metrics collection for:
- Real-time health metrics aggregation and storage
- Performance trend analysis and predictive analytics
- Custom metrics dashboards and visualization data
- Health score calculations and SLA monitoring
- Anomaly detection and threshold-based alerting
- Historical data retention and archival policies
- Metrics export to external monitoring systems (Prometheus, Grafana)

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""

import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

from .core_health import HealthStatus, HealthCheckResult


@dataclass
class HealthMetric:
    """Individual health metric data point"""
    metric_name: str
    service_name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    threshold_breached: bool = False


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a time period"""
    service_name: str
    metric_name: str
    time_period_minutes: int
    count: int
    mean: float
    median: float
    min_value: float
    max_value: float
    std_deviation: float
    percentile_95: float
    percentile_99: float
    timestamp: datetime


@dataclass
class HealthTrend:
    """Health trend analysis result"""
    service_name: str
    metric_name: str
    trend_direction: str  # "improving", "degrading", "stable"
    trend_strength: float  # 0.0 to 1.0
    prediction_confidence: float
    next_period_prediction: float
    anomalies_detected: int
    trend_period_hours: int


class HealthMetricsCollector:
    """
    Advanced health metrics collection and analytics system
    
    Collects, aggregates, and analyzes health metrics from all platform
    components with real-time analytics and predictive capabilities.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize health metrics collector
        
        Args:
            config: Metrics collection configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics configuration
        self.metrics_config = config.get("metrics", {})
        self.retention_config = self.metrics_config.get("retention", {})
        self.aggregation_config = self.metrics_config.get("aggregation", {})
        self.alerting_config = self.metrics_config.get("alerting", {})
        
        # Data retention settings
        self.raw_metrics_retention_hours = self.retention_config.get("raw_metrics_hours", 168)  # 7 days
        self.aggregated_metrics_retention_days = self.retention_config.get("aggregated_metrics_days", 90)  # 3 months
        self.max_memory_metrics = self.retention_config.get("max_memory_metrics", 100000)
        
        # Aggregation intervals
        self.aggregation_intervals = self.aggregation_config.get("intervals_minutes", [5, 15, 60, 240])  # 5min, 15min, 1h, 4h
        
        # In-memory storage for real-time metrics
        self._raw_metrics = deque(maxlen=self.max_memory_metrics)
        self._aggregated_metrics = {}
        self._service_metrics = defaultdict(lambda: defaultdict(list))
        self._last_aggregation_time = {}
        
        # Anomaly detection models
        self._anomaly_detectors = {}
        self._anomaly_detection_enabled = self.metrics_config.get("anomaly_detection", {}).get("enabled", True)
        
        # Metrics thresholds
        self._metric_thresholds = self.metrics_config.get("thresholds", {})

    async def collect_health_metrics(self, health_results: List[HealthCheckResult]):
        """
        Collect metrics from health check results
        
        Args:
            health_results: List of health check results to extract metrics from
        """
        collection_time = datetime.utcnow()
        
        for result in health_results:
            try:
                # Extract primary metrics
                primary_metrics = [
                    HealthMetric(
                        metric_name="response_time_ms",
                        service_name=result.service,
                        value=result.response_time_ms,
                        unit="milliseconds",
                        timestamp=collection_time,
                        tags={"status": result.status.value}
                    ),
                    HealthMetric(
                        metric_name="health_status_numeric",
                        service_name=result.service,
                        value=self._status_to_numeric(result.status),
                        unit="score",
                        timestamp=collection_time,
                        tags={"status": result.status.value}
                    )
                ]
                
                # Extract detailed metrics from result details
                if result.details:
                    detailed_metrics = self._extract_detailed_metrics(result)
                    primary_metrics.extend(detailed_metrics)
                
                # Store metrics
                for metric in primary_metrics:
                    await self._store_metric(metric)
                    
            except Exception as e:
                self.logger.error(f"Failed to collect metrics from {result.service}: {str(e)}")

    def _status_to_numeric(self, status: HealthStatus) -> float:
        """Convert health status to numeric value for trend analysis"""
        status_mapping = {
            HealthStatus.HEALTHY: 100.0,
            HealthStatus.DEGRADED: 75.0,
            HealthStatus.UNHEALTHY: 50.0,
            HealthStatus.CRITICAL: 0.0
        }
        return status_mapping.get(status, 0.0)

    def _extract_detailed_metrics(self, result: HealthCheckResult) -> List[HealthMetric]:
        """Extract detailed metrics from health check result details"""
        metrics = []
        details = result.details
        
        if not details:
            return metrics
        
        # Common metrics extraction patterns
        metric_patterns = {
            "cpu_percent": ("cpu_usage_percent", "percent"),
            "memory_percent": ("memory_usage_percent", "percent"),
            "disk_percent": ("disk_usage_percent", "percent"),
            "connection_usage_percent": ("connection_usage_percent", "percent"),
            "cache_hit_ratio": ("cache_hit_ratio", "percent"),
            "queue_size": ("queue_size", "count"),
            "error_rate_percent": ("error_rate_percent", "percent"),
            "success_rate_percent": ("success_rate_percent", "percent"),
            "processing_speed_fps": ("processing_speed", "fps"),
            "accuracy_score": ("accuracy_score", "score"),
            "latency_ms": ("latency", "milliseconds"),
            "throughput_rps": ("throughput", "requests_per_second")
        }
        
        for detail_key, value in details.items():
            if isinstance(value, (int, float)) and detail_key in metric_patterns:
                metric_name, unit = metric_patterns[detail_key]
                
                metric = HealthMetric(
                    metric_name=metric_name,
                    service_name=result.service,
                    value=float(value),
                    unit=unit,
                    timestamp=result.timestamp,
                    tags={"source": "detailed_metrics"}
                )
                metrics.append(metric)
        
        # Extract nested metrics
        if isinstance(details, dict):
            for key, value in details.items():
                if isinstance(value, dict):
                    nested_metrics = self._extract_nested_metrics(result.service, key, value, result.timestamp)
                    metrics.extend(nested_metrics)
        
        return metrics

    def _extract_nested_metrics(self, service_name: str, prefix: str, data: Dict[str, Any], timestamp: datetime) -> List[HealthMetric]:
        """Extract metrics from nested data structures"""
        metrics = []
        
        for key, value in data.items():
            if isinstance(value, (int, float)):
                metric_name = f"{prefix}_{key}" if prefix else key
                
                metric = HealthMetric(
                    metric_name=metric_name,
                    service_name=service_name,
                    value=float(value),
                    unit="count" if isinstance(value, int) else "value",
                    timestamp=timestamp,
                    tags={"category": prefix}
                )
                metrics.append(metric)
            elif isinstance(value, dict):
                nested_metrics = self._extract_nested_metrics(
                    service_name, 
                    f"{prefix}_{key}" if prefix else key, 
                    value, 
                    timestamp
                )
                metrics.extend(nested_metrics)
        
        return metrics

    async def _store_metric(self, metric: HealthMetric):
        """Store metric in memory and check thresholds"""
        try:
            # Check threshold breaches
            threshold_key = f"{metric.service_name}.{metric.metric_name}"
            if threshold_key in self._metric_thresholds:
                threshold = self._metric_thresholds[threshold_key]
                metric.threshold_breached = self._check_threshold(metric.value, threshold)
            
            # Store in raw metrics
            self._raw_metrics.append(metric)
            
            # Store in service-specific collections
            self._service_metrics[metric.service_name][metric.metric_name].append(metric)
            
            # Perform anomaly detection if enabled
            if self._anomaly_detection_enabled:
                await self._detect_anomaly(metric)
            
        except Exception as e:
            self.logger.error(f"Failed to store metric {metric.metric_name}: {str(e)}")

    def _check_threshold(self, value: float, threshold: Dict[str, Any]) -> bool:
        """Check if metric value breaches configured threshold"""
        threshold_type = threshold.get("type", "upper")
        threshold_value = threshold.get("value", 0.0)
        
        if threshold_type == "upper":
            return value > threshold_value
        elif threshold_type == "lower":
            return value < threshold_value
        elif threshold_type == "range":
            min_val = threshold.get("min", 0.0)
            max_val = threshold.get("max", 100.0)
            return value < min_val or value > max_val
        
        return False

    async def _detect_anomaly(self, metric: HealthMetric):
        """Detect anomalies in metric values using statistical analysis"""
        try:
            service_metric_key = f"{metric.service_name}.{metric.metric_name}"
            
            # Get historical values for this metric
            historical_values = [
                m.value for m in self._service_metrics[metric.service_name][metric.metric_name]
                if (metric.timestamp - m.timestamp).total_seconds() <= 3600  # Last hour
            ]
            
            if len(historical_values) < 10:  # Need enough data points
                return
            
            # Initialize or update anomaly detector
            if service_metric_key not in self._anomaly_detectors:
                self._anomaly_detectors[service_metric_key] = IsolationForest(
                    contamination=0.1,  # Expect 10% anomalies
                    random_state=42
                )
                
                # Train with historical data
                if len(historical_values) >= 20:
                    X = np.array(historical_values[:-1]).reshape(-1, 1)
                    self._anomaly_detectors[service_metric_key].fit(X)
            
            # Detect anomaly
            detector = self._anomaly_detectors[service_metric_key]
            if hasattr(detector, 'predict'):
                prediction = detector.predict([[metric.value]])
                
                if prediction[0] == -1:  # Anomaly detected
                    await self._handle_anomaly(metric, historical_values)
                    
        except Exception as e:
            self.logger.error(f"Anomaly detection failed for {metric.metric_name}: {str(e)}")

    async def _handle_anomaly(self, metric: HealthMetric, historical_values: List[float]):
        """Handle detected anomaly"""
        mean_val = statistics.mean(historical_values)
        std_val = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
        
        self.logger.warning(
            f"Anomaly detected in {metric.service_name}.{metric.metric_name}: "
            f"Value {metric.value} (mean: {mean_val:.2f}, std: {std_val:.2f})"
        )
        
        # Could trigger alerting system here
        anomaly_data = {
            "service": metric.service_name,
            "metric": metric.metric_name,
            "value": metric.value,
            "expected_range": (mean_val - 2*std_val, mean_val + 2*std_val),
            "timestamp": metric.timestamp.isoformat(),
            "severity": "high" if abs(metric.value - mean_val) > 3*std_val else "medium"
        }

    async def aggregate_metrics(self, interval_minutes: int = 5) -> List[AggregatedMetrics]:
        """
        Aggregate metrics for specified time interval
        
        Args:
            interval_minutes: Aggregation interval in minutes
            
        Returns:
            List[AggregatedMetrics]: Aggregated metrics for the interval
        """
        try:
            current_time = datetime.utcnow()
            interval_start = current_time - timedelta(minutes=interval_minutes)
            
            # Group metrics by service and metric name
            grouped_metrics = defaultdict(lambda: defaultdict(list))
            
            for metric in self._raw_metrics:
                if metric.timestamp >= interval_start:
                    grouped_metrics[metric.service_name][metric.metric_name].append(metric.value)
            
            # Calculate aggregations
            aggregated_results = []
            
            for service_name, service_metrics in grouped_metrics.items():
                for metric_name, values in service_metrics.items():
                    if not values:
                        continue
                    
                    aggregated = AggregatedMetrics(
                        service_name=service_name,
                        metric_name=metric_name,
                        time_period_minutes=interval_minutes,
                        count=len(values),
                        mean=statistics.mean(values),
                        median=statistics.median(values),
                        min_value=min(values),
                        max_value=max(values),
                        std_deviation=statistics.stdev(values) if len(values) > 1 else 0.0,
                        percentile_95=np.percentile(values, 95),
                        percentile_99=np.percentile(values, 99),
                        timestamp=current_time
                    )
                    
                    aggregated_results.append(aggregated)
            
            # Store aggregated metrics
            interval_key = f"{interval_minutes}min"
            if interval_key not in self._aggregated_metrics:
                self._aggregated_metrics[interval_key] = deque(maxlen=1000)
            
            self._aggregated_metrics[interval_key].extend(aggregated_results)
            
            return aggregated_results
            
        except Exception as e:
            self.logger.error(f"Metrics aggregation failed: {str(e)}")
            return []

    async def analyze_health_trends(self, service_name: str, metric_name: str, 
                                  hours: int = 24) -> HealthTrend:
        """
        Analyze health trends for specific service and metric
        
        Args:
            service_name: Name of service to analyze
            metric_name: Name of metric to analyze
            hours: Number of hours to analyze
            
        Returns:
            HealthTrend: Trend analysis result
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Collect historical data
            historical_values = []
            timestamps = []
            
            for metric in self._service_metrics[service_name][metric_name]:
                if metric.timestamp >= cutoff_time:
                    historical_values.append(metric.value)
                    timestamps.append(metric.timestamp)
            
            if len(historical_values) < 5:
                return HealthTrend(
                    service_name=service_name,
                    metric_name=metric_name,
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    prediction_confidence=0.0,
                    next_period_prediction=0.0,
                    anomalies_detected=0,
                    trend_period_hours=hours
                )
            
            # Calculate trend using linear regression
            x_values = np.array([(t - timestamps[0]).total_seconds() for t in timestamps])
            y_values = np.array(historical_values)
            
            # Simple linear regression
            slope, intercept = np.polyfit(x_values, y_values, 1)
            
            # Determine trend direction and strength
            if abs(slope) < 0.01:  # Minimal change
                trend_direction = "stable"
                trend_strength = 0.0
            elif slope > 0:
                trend_direction = "improving" if metric_name in ["health_status_numeric", "success_rate_percent", "cache_hit_ratio"] else "degrading"
                trend_strength = min(abs(slope) * 100, 1.0)
            else:
                trend_direction = "degrading" if metric_name in ["health_status_numeric", "success_rate_percent", "cache_hit_ratio"] else "improving"
                trend_strength = min(abs(slope) * 100, 1.0)
            
            # Calculate prediction confidence based on R-squared
            y_mean = np.mean(y_values)
            ss_tot = np.sum((y_values - y_mean) ** 2)
            y_pred = slope * x_values + intercept
            ss_res = np.sum((y_values - y_pred) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            prediction_confidence = max(0.0, min(1.0, r_squared))
            
            # Predict next period value
            next_period_seconds = (timestamps[-1] - timestamps[0]).total_seconds() + 3600  # Next hour
            next_period_prediction = slope * next_period_seconds + intercept
            
            # Count anomalies
            anomalies_detected = len([v for v in historical_values if abs(v - y_mean) > 2 * np.std(y_values)])
            
            return HealthTrend(
                service_name=service_name,
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                prediction_confidence=prediction_confidence,
                next_period_prediction=next_period_prediction,
                anomalies_detected=anomalies_detected,
                trend_period_hours=hours
            )
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed for {service_name}.{metric_name}: {str(e)}")
            return HealthTrend(
                service_name=service_name,
                metric_name=metric_name,
                trend_direction="error",
                trend_strength=0.0,
                prediction_confidence=0.0,
                next_period_prediction=0.0,
                anomalies_detected=0,
                trend_period_hours=hours
            )

    async def get_metrics_summary(self, time_range_hours: int = 1) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary
        
        Args:
            time_range_hours: Time range for summary in hours
            
        Returns:
            Dict[str, Any]: Metrics summary with statistics and insights
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # Filter recent metrics
            recent_metrics = [m for m in self._raw_metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {
                    "status": "no_data",
                    "message": f"No metrics available for the last {time_range_hours} hours",
                    "time_range_hours": time_range_hours
                }
            
            # Group by service
            service_summaries = defaultdict(lambda: {
                "metric_count": 0,
                "avg_response_time": 0.0,
                "health_score": 0.0,
                "threshold_breaches": 0,
                "anomalies": 0
            })
            
            total_metrics = len(recent_metrics)
            total_threshold_breaches = 0
            response_times = []
            health_scores = []
            
            for metric in recent_metrics:
                service_summaries[metric.service_name]["metric_count"] += 1
                
                if metric.metric_name == "response_time_ms":
                    response_times.append(metric.value)
                    service_summaries[metric.service_name]["avg_response_time"] = statistics.mean([
                        m.value for m in recent_metrics 
                        if m.service_name == metric.service_name and m.metric_name == "response_time_ms"
                    ])
                
                if metric.metric_name == "health_status_numeric":
                    health_scores.append(metric.value)
                    service_summaries[metric.service_name]["health_score"] = statistics.mean([
                        m.value for m in recent_metrics 
                        if m.service_name == metric.service_name and m.metric_name == "health_status_numeric"
                    ])
                
                if metric.threshold_breached:
                    total_threshold_breaches += 1
                    service_summaries[metric.service_name]["threshold_breaches"] += 1
            
            # Calculate overall statistics
            overall_stats = {
                "total_metrics_collected": total_metrics,
                "unique_services": len(service_summaries),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0.0,
                "overall_health_score": statistics.mean(health_scores) if health_scores else 0.0,
                "total_threshold_breaches": total_threshold_breaches,
                "breach_rate_percent": (total_threshold_breaches / total_metrics) * 100 if total_metrics > 0 else 0.0,
                "collection_rate_per_minute": total_metrics / (time_range_hours * 60) if time_range_hours > 0 else 0.0
            }
            
            return {
                "time_range_hours": time_range_hours,
                "overall_statistics": overall_stats,
                "service_summaries": dict(service_summaries),
                "top_response_times": sorted(response_times, reverse=True)[:10] if response_times else [],
                "health_score_distribution": {
                    "healthy": len([s for s in health_scores if s >= 90]),
                    "degraded": len([s for s in health_scores if 70 <= s < 90]),
                    "unhealthy": len([s for s in health_scores if 50 <= s < 70]),
                    "critical": len([s for s in health_scores if s < 50])
                } if health_scores else {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate metrics summary: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format
        
        Returns:
            str: Metrics in Prometheus exposition format
        """
        try:
            prometheus_output = []
            current_time = int(datetime.utcnow().timestamp() * 1000)
            
            # Group metrics by name for Prometheus format
            metric_groups = defaultdict(list)
            
            for metric in self._raw_metrics:
                if (datetime.utcnow() - metric.timestamp).total_seconds() <= 300:  # Last 5 minutes
                    metric_groups[metric.metric_name].append(metric)
            
            # Generate Prometheus format
            for metric_name, metrics in metric_groups.items():
                # Add metric help and type
                prometheus_output.append(f"# HELP ia_influencer_{metric_name} Health metric: {metric_name}")
                prometheus_output.append(f"# TYPE ia_influencer_{metric_name} gauge")
                
                for metric in metrics:
                    labels = [f'service="{metric.service_name}"']
                    for tag_key, tag_value in metric.tags.items():
                        labels.append(f'{tag_key}="{tag_value}"')
                    
                    labels_str = "{" + ",".join(labels) + "}"
                    timestamp = int(metric.timestamp.timestamp() * 1000)
                    
                    prometheus_output.append(f"ia_influencer_{metric_name}{labels_str} {metric.value} {timestamp}")
            
            return "\n".join(prometheus_output)
            
        except Exception as e:
            self.logger.error(f"Failed to export Prometheus metrics: {str(e)}")
            return f"# Error exporting metrics: {str(e)}\n"

    async def cleanup_old_metrics(self):
        """Clean up old metrics based on retention policies"""
        try:
            current_time = datetime.utcnow()
            raw_cutoff = current_time - timedelta(hours=self.raw_metrics_retention_hours)
            
            # Clean raw metrics
            initial_count = len(self._raw_metrics)
            
            # Filter out old metrics
            filtered_metrics = deque(
                [m for m in self._raw_metrics if m.timestamp >= raw_cutoff],
                maxlen=self.max_memory_metrics
            )
            self._raw_metrics = filtered_metrics
            
            # Clean service metrics
            for service_name in self._service_metrics:
                for metric_name in self._service_metrics[service_name]:
                    self._service_metrics[service_name][metric_name] = [
                        m for m in self._service_metrics[service_name][metric_name]
                        if m.timestamp >= raw_cutoff
                    ]
            
            cleaned_count = initial_count - len(self._raw_metrics)
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old metrics")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {str(e)}")

    def get_current_metrics_stats(self) -> Dict[str, Any]:
        """Get current metrics collection statistics"""
        return {
            "total_raw_metrics": len(self._raw_metrics),
            "unique_services": len(self._service_metrics),
            "unique_metric_types": len(set(m.metric_name for m in self._raw_metrics)),
            "aggregation_intervals": list(self._aggregated_metrics.keys()),
            "anomaly_detectors_active": len(self._anomaly_detectors),
            "memory_usage_percent": (len(self._raw_metrics) / self.max_memory_metrics) * 100,
            "oldest_metric_age_hours": (
                (datetime.utcnow() - min(m.timestamp for m in self._raw_metrics)).total_seconds() / 3600
                if self._raw_metrics else 0
            ),
            "newest_metric_age_seconds": (
                (datetime.utcnow() - max(m.timestamp for m in self._raw_metrics)).total_seconds()
                if self._raw_metrics else 0
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
