"""Metrics Collector - Advanced Metrics Collection System
=======================================================

Advanced metrics collection and analysis capabilities for Ainflue integrations.
Provides comprehensive data gathering, statistical analysis, and performance insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

from .performance_monitor_core import (
    PerformanceMetric, MetricType, IntegrationProfile
)

logger = logging.getLogger(__name__)

class PerformanceCollector:
    """Advanced performance data collector and analyzer."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.start_time = time.time()

    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a performance metric to the collector."""
        key = f"{metric.integration_name or 'global'}:{metric.metric_name}"
        self.metrics[key].append(metric)
        
        # Cleanup old metrics periodically
        if len(self.metrics[key]) >= self.window_size:
            self._cleanup_old_metrics()

    def get_metrics(self, metric_name: str, integration_name: Optional[str] = None) -> List[PerformanceMetric]:
        """Get metrics by name and optional integration."""
        key = f"{integration_name or 'global'}:{metric_name}"
        return list(self.metrics.get(key, []))

    def get_latest_value(self, metric_name: str, integration_name: Optional[str] = None) -> Optional[float]:
        """Get the latest value for a metric."""
        metrics = self.get_metrics(metric_name, integration_name)
        return metrics[-1].value if metrics else None

    def calculate_statistics(
        self,
        metric_name: str,
        integration_name: Optional[str] = None,
        time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive statistics for a metric."""
        metrics = self.get_metrics(metric_name, integration_name)
        
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
        if not metrics:
            return {
                'count': 0,
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std_dev': 0.0,
                'percentiles': {}
            }
            
        values = [m.value for m in metrics]
        
        stats = {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'percentiles': {
                '50': self._percentile(values, 50),
                '90': self._percentile(values, 90),
                '95': self._percentile(values, 95),
                '99': self._percentile(values, 99)
            }
        }
        
        return stats

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight

    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics to maintain performance."""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=24)
        
        for key, metric_deque in self.metrics.items():
            # Convert to list, filter, and recreate deque
            filtered_metrics = [m for m in metric_deque if m.timestamp >= cutoff_time]
            self.metrics[key] = deque(filtered_metrics, maxlen=self.window_size)

    def get_trend_analysis(
        self,
        metric_name: str,
        integration_name: Optional[str] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Analyze trends in metric data."""
        metrics = self.get_metrics(metric_name, integration_name)
        
        if len(metrics) < 2:
            return {
                'trend': 'insufficient_data',
                'slope': 0.0,
                'correlation': 0.0,
                'prediction': None
            }
            
        # Filter by time window
        cutoff_time = datetime.utcnow() - time_window
        recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        if len(recent_metrics) < 2:
            return {
                'trend': 'insufficient_recent_data',
                'slope': 0.0,
                'correlation': 0.0,
                'prediction': None
            }
            
        # Calculate trend using linear regression
        timestamps = [m.timestamp.timestamp() for m in recent_metrics]
        values = [m.value for m in recent_metrics]
        
        # Normalize timestamps to start from 0
        start_time = min(timestamps)
        x_values = [t - start_time for t in timestamps]
        
        # Calculate linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0.0
            intercept = sum_y / n if n > 0 else 0.0
            
        # Calculate correlation coefficient
        if len(values) > 1:
            mean_x = statistics.mean(x_values)
            mean_y = statistics.mean(values)
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
            denominator_x = sum((x - mean_x) ** 2 for x in x_values)
            denominator_y = sum((y - mean_y) ** 2 for y in values)
            
            if denominator_x > 0 and denominator_y > 0:
                correlation = numerator / (denominator_x * denominator_y) ** 0.5
            else:
                correlation = 0.0
        else:
            correlation = 0.0
            
        # Determine trend direction
        if abs(slope) < 0.001:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
            
        # Make prediction for next time point
        next_time = max(x_values) + (time_window.total_seconds() / len(x_values))
        prediction = slope * next_time + intercept
        
        return {
            'trend': trend,
            'slope': slope,
            'correlation': correlation,
            'prediction': max(0, prediction),  # Ensure non-negative
            'confidence': abs(correlation)
        }

    def get_anomaly_detection(
        self,
        metric_name: str,
        integration_name: Optional[str] = None,
        sensitivity: float = 2.0
    ) -> Dict[str, Any]:
        """Detect anomalies in metric data using statistical methods."""
        metrics = self.get_metrics(metric_name, integration_name)
        
        if len(metrics) < 10:
            return {
                'anomalies_detected': False,
                'anomaly_count': 0,
                'latest_is_anomaly': False,
                'anomaly_score': 0.0
            }
            
        values = [m.value for m in metrics]
        
        # Calculate baseline statistics (excluding recent values for comparison)
        baseline_values = values[:-5] if len(values) > 10 else values[:-1]
        
        if len(baseline_values) < 5:
            return {
                'anomalies_detected': False,
                'anomaly_count': 0,
                'latest_is_anomaly': False,
                'anomaly_score': 0.0
            }
            
        baseline_mean = statistics.mean(baseline_values)
        baseline_std = statistics.stdev(baseline_values) if len(baseline_values) > 1 else 0.0
        
        # Detect anomalies using z-score
        anomalies = []
        anomaly_threshold = sensitivity
        
        for i, value in enumerate(values):
            if baseline_std > 0:
                z_score = abs((value - baseline_mean) / baseline_std)
                if z_score > anomaly_threshold:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'z_score': z_score,
                        'timestamp': metrics[i].timestamp.isoformat()
                    })
                    
        # Check if latest value is anomaly
        latest_is_anomaly = False
        latest_anomaly_score = 0.0
        
        if values and baseline_std > 0:
            latest_z_score = abs((values[-1] - baseline_mean) / baseline_std)
            latest_is_anomaly = latest_z_score > anomaly_threshold
            latest_anomaly_score = latest_z_score
            
        return {
            'anomalies_detected': len(anomalies) > 0,
            'anomaly_count': len(anomalies),
            'latest_is_anomaly': latest_is_anomaly,
            'anomaly_score': latest_anomaly_score,
            'anomalies': anomalies,
            'baseline_mean': baseline_mean,
            'baseline_std': baseline_std,
            'threshold': anomaly_threshold
        }

    def get_performance_insights(
        self,
        integration_name: Optional[str] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Generate comprehensive performance insights."""
        insights = {
            'timestamp': datetime.utcnow().isoformat(),
            'integration': integration_name,
            'time_window_hours': time_window.total_seconds() / 3600,
            'metrics_analysis': {},
            'recommendations': [],
            'overall_health': 'unknown'
        }
        
        # Analyze key metrics
        key_metrics = ['latency', 'throughput', 'error_rate', 'memory_usage']
        
        for metric_name in key_metrics:
            stats = self.calculate_statistics(metric_name, integration_name, time_window)
            trend = self.get_trend_analysis(metric_name, integration_name, time_window)
            anomalies = self.get_anomaly_detection(metric_name, integration_name)
            
            insights['metrics_analysis'][metric_name] = {
                'statistics': stats,
                'trend': trend,
                'anomalies': anomalies
            }
            
            # Generate recommendations based on analysis
            if metric_name == 'latency' and stats['mean'] > 1.0:
                insights['recommendations'].append({
                    'type': 'performance',
                    'priority': 'high',
                    'metric': metric_name,
                    'message': f"High average latency detected: {stats['mean']:.2f}s. Consider optimization."
                })
                
            if metric_name == 'error_rate' and stats['mean'] > 0.05:
                insights['recommendations'].append({
                    'type': 'reliability',
                    'priority': 'critical',
                    'metric': metric_name,
                    'message': f"High error rate detected: {stats['mean']*100:.1f}%. Investigate immediately."
                })
                
            if anomalies['latest_is_anomaly']:
                insights['recommendations'].append({
                    'type': 'anomaly',
                    'priority': 'medium',
                    'metric': metric_name,
                    'message': f"Anomaly detected in {metric_name} (score: {anomalies['anomaly_score']:.2f})"
                })
                
        # Determine overall health
        critical_recommendations = [r for r in insights['recommendations'] if r['priority'] == 'critical']
        high_recommendations = [r for r in insights['recommendations'] if r['priority'] == 'high']
        
        if critical_recommendations:
            insights['overall_health'] = 'critical'
        elif high_recommendations:
            insights['overall_health'] = 'warning'
        elif insights['recommendations']:
            insights['overall_health'] = 'degraded'
        else:
            insights['overall_health'] = 'healthy'
            
        return insights

    def export_metrics(
        self,
        format_type: str = 'json',
        integration_name: Optional[str] = None,
        time_window: Optional[timedelta] = None
    ) -> Union[str, Dict[str, Any]]:
        """Export metrics in specified format."""
        
        # Collect metrics to export
        export_data = {
            'metadata': {
                'export_timestamp': datetime.utcnow().isoformat(),
                'integration': integration_name,
                'time_window_hours': time_window.total_seconds() / 3600 if time_window else None,
                'total_metrics': 0
            },
            'metrics': []
        }
        
        for key, metric_deque in self.metrics.items():
            # Filter by integration if specified
            if integration_name:
                key_integration = key.split(':')[0]
                if key_integration != integration_name and key_integration != 'global':
                    continue
                    
            metrics_list = list(metric_deque)
            
            # Filter by time window if specified
            if time_window:
                cutoff_time = datetime.utcnow() - time_window
                metrics_list = [m for m in metrics_list if m.timestamp >= cutoff_time]
                
            # Convert metrics to serializable format
            for metric in metrics_list:
                export_data['metrics'].append({
                    'timestamp': metric.timestamp.isoformat(),
                    'metric_name': metric.metric_name,
                    'metric_type': metric.metric_type.value,
                    'value': metric.value,
                    'integration_name': metric.integration_name,
                    'tags': metric.tags
                })
                
        export_data['metadata']['total_metrics'] = len(export_data['metrics'])
        
        if format_type.lower() == 'json':
            return json.dumps(export_data, indent=2)
        else:
            return export_data

    def clear_metrics(self, integration_name: Optional[str] = None) -> int:
        """Clear metrics, optionally for a specific integration."""
        cleared_count = 0
        
        if integration_name:
            # Clear metrics for specific integration
            keys_to_clear = [key for key in self.metrics.keys() 
                           if key.startswith(f"{integration_name}:")]
            for key in keys_to_clear:
                cleared_count += len(self.metrics[key])
                del self.metrics[key]
        else:
            # Clear all metrics
            for key, metric_deque in self.metrics.items():
                cleared_count += len(metric_deque)
            self.metrics.clear()
            
        return cleared_count


# Export main classes
__all__ = [
    "PerformanceCollector"
]