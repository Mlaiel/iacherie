"""
Metrics Aggregator
Aggregates metrics for Prometheus monitoring
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime


class MetricsAggregator:
    """Aggregate metrics for monitoring"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
        
        # In production, use Prometheus client library
        # from prometheus_client import Counter, Histogram, Gauge
        # 
        # self.request_counter = Counter(
        #     'http_requests_total',
        #     'Total HTTP requests',
        #     ['method', 'endpoint', 'status']
        # )
        # 
        # self.request_duration = Histogram(
        #     'http_request_duration_seconds',
        #     'HTTP request duration',
        #     ['method', 'endpoint']
        # )
        # 
        # self.active_users = Gauge(
        #     'active_users',
        #     'Number of active users',
        #     ['module']
        # )
        
        # In-memory metrics for development
        self.metrics: Dict[str, Any] = {
            'requests': {},
            'errors': {},
            'active_users': {},
            'custom': {}
        }
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float
    ) -> None:
        """
        Record an HTTP request metric
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: Response status code
            duration_seconds: Request duration
        """
        if not self.enabled:
            return
        
        # In production:
        # self.request_counter.labels(
        #     method=method,
        #     endpoint=endpoint,
        #     status=status_code
        # ).inc()
        # 
        # self.request_duration.labels(
        #     method=method,
        #     endpoint=endpoint
        # ).observe(duration_seconds)
        
        key = f"{method}:{endpoint}:{status_code}"
        if key not in self.metrics['requests']:
            self.metrics['requests'][key] = {'count': 0, 'total_duration': 0}
        
        self.metrics['requests'][key]['count'] += 1
        self.metrics['requests'][key]['total_duration'] += duration_seconds
    
    def record_error(
        self,
        error_type: str,
        module: str,
        severity: str = 'error'
    ) -> None:
        """
        Record an error metric
        
        Args:
            error_type: Type of error
            module: Module name
            severity: Error severity (info, warning, error, critical)
        """
        if not self.enabled:
            return
        
        key = f"{module}:{error_type}:{severity}"
        if key not in self.metrics['errors']:
            self.metrics['errors'][key] = 0
        
        self.metrics['errors'][key] += 1
        print(f"[Metrics] Error recorded: {key}")
    
    def set_active_users(self, module: str, count: int) -> None:
        """
        Set active users count for a module
        
        Args:
            module: Module name
            count: Number of active users
        """
        if not self.enabled:
            return
        
        # In production:
        # self.active_users.labels(module=module).set(count)
        
        self.metrics['active_users'][module] = count
    
    def increment_counter(
        self,
        metric_name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Increment a custom counter
        
        Args:
            metric_name: Metric name
            value: Value to add
            labels: Optional labels
        """
        if not self.enabled:
            return
        
        key = metric_name
        if labels:
            label_str = ','.join(f"{k}={v}" for k, v in labels.items())
            key = f"{metric_name}{{{label_str}}}"
        
        if key not in self.metrics['custom']:
            self.metrics['custom'][key] = 0
        
        self.metrics['custom'][key] += value
    
    def set_gauge(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Set a gauge metric
        
        Args:
            metric_name: Metric name
            value: Metric value
            labels: Optional labels
        """
        if not self.enabled:
            return
        
        key = metric_name
        if labels:
            label_str = ','.join(f"{k}={v}" for k, v in labels.items())
            key = f"{metric_name}{{{label_str}}}"
        
        self.metrics['custom'][key] = value
    
    def record_histogram(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a histogram observation
        
        Args:
            metric_name: Metric name
            value: Observed value
            labels: Optional labels
        """
        if not self.enabled:
            return
        
        key = f"{metric_name}_histogram"
        if labels:
            label_str = ','.join(f"{k}={v}" for k, v in labels.items())
            key = f"{metric_name}_histogram{{{label_str}}}"
        
        if key not in self.metrics['custom']:
            self.metrics['custom'][key] = []
        
        self.metrics['custom'][key].append(value)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics
        
        Returns:
            Dict with metrics summary
        """
        return {
            'requests': len(self.metrics['requests']),
            'errors': sum(self.metrics['errors'].values()),
            'active_users': self.metrics['active_users'],
            'custom_metrics': len(self.metrics['custom']),
            'enabled': self.enabled
        }
    
    def get_request_stats(self) -> Dict[str, Any]:
        """
        Get request statistics
        
        Returns:
            Dict with request stats
        """
        total_requests = sum(m['count'] for m in self.metrics['requests'].values())
        total_duration = sum(m['total_duration'] for m in self.metrics['requests'].values())
        
        avg_duration = total_duration / total_requests if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'average_duration_seconds': avg_duration,
            'endpoints': list(self.metrics['requests'].keys())
        }
