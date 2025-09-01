"""Metrics Collector - Advanced Monitoring System

Enterprise metrics collection and monitoring with Prometheus integration,
custom metrics, alerting, and comprehensive observability features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

logger = logging.getLogger(__name__)


@dataclass
class MetricDefinition:
    """
Metric definition configuration"""
    name: str
    metric_type: str  # counter, histogram, gauge, summary
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # For histograms


@dataclass
class Alert:
    """
Alert configuration"""
    name: str
    condition: str
    threshold: float
    duration: int  # seconds
    severity: str = "warning"
    enabled: bool = True
    last_triggered: Optional[datetime] = None


class MetricsCollector:
    """
    Enterprise Metrics Collector
    
    Features:
    - Prometheus metrics integration
    - Custom metric definitions
    - Real-time metrics collection
    - Alert management
    - Performance monitoring
    - Resource utilization tracking
    - Service health metrics
    """
    
    def __init__(
        self,
        enabled: bool = True,
        registry: Optional[CollectorRegistry] = None,
        prometheus_endpoint: str = "/metrics"
    ):
        """Initialize metrics collector"""
        self.enabled = enabled
        self.registry = registry or CollectorRegistry()
        self.prometheus_endpoint = prometheus_endpoint
        
        # Metric instances
        self.metrics: Dict[str, Any] = {}
        
        # Alert system
        self.alerts: Dict[str, Alert] = {}
        self.alert_callbacks: List[Callable[[Alert, float], None]] = []
        
        # Custom metrics storage
        self.custom_metrics: Dict[str, List[float]] = defaultdict(list)
        self.custom_metrics_timestamps: Dict[str, List[datetime]] = defaultdict(list)
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        # Background tasks
        self._metrics_task: Optional[asyncio.Task] = None
        self._alerts_task: Optional[asyncio.Task] = None
        
        logger.info(f"Metrics collector initialized (enabled: {enabled})")
    
    def _initialize_default_metrics(self):
        """Initialize default API Gateway metrics"""
        try:
            # Request metrics
            self.metrics['requests_total'] = Counter(
                'api_gateway_requests_total',
                'Total number of requests processed',
                ['method', 'endpoint', 'status_code', 'service'],
                registry=self.registry
            )
            
            self.metrics['request_duration'] = Histogram(
                'api_gateway_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint', 'service'],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0],
                registry=self.registry
            )
            
            # Connection metrics
            self.metrics['active_connections'] = Gauge(
                'api_gateway_active_connections',
                'Number of active connections',
                registry=self.registry
            )
            
            self.metrics['connection_duration'] = Histogram(
                'api_gateway_connection_duration_seconds',
                'Connection duration in seconds',
                buckets=[1.0, 10.0, 60.0, 300.0, 600.0, 1800.0, 3600.0],
                registry=self.registry
            )
            
            # Service metrics
            self.metrics['upstream_requests'] = Counter(
                'api_gateway_upstream_requests_total',
                'Total upstream service requests',
                ['service', 'status_code'],
                registry=self.registry
            )
            
            self.metrics['upstream_duration'] = Histogram(
                'api_gateway_upstream_duration_seconds',
                'Upstream request duration in seconds',
                ['service'],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0],
                registry=self.registry
            )
            
            self.metrics['service_health'] = Gauge(
                'api_gateway_service_health',
                'Service health status (1=healthy, 0=unhealthy)',
                ['service'],
                registry=self.registry
            )
            
            # Rate limiting metrics
            self.metrics['rate_limit_hits'] = Counter(
                'api_gateway_rate_limit_hits_total',
                'Total rate limit hits',
                ['identifier_type', 'endpoint'],
                registry=self.registry
            )
            
            self.metrics['rate_limit_remaining'] = Gauge(
                'api_gateway_rate_limit_remaining',
                'Remaining rate limit quota',
                ['identifier', 'endpoint'],
                registry=self.registry
            )
            
            # Circuit breaker metrics
            self.metrics['circuit_breaker_state'] = Gauge(
                'api_gateway_circuit_breaker_state',
                'Circuit breaker state (0=closed, 1=open, 2=half_open)',
                ['service'],
                registry=self.registry
            )
            
            self.metrics['circuit_breaker_failures'] = Counter(
                'api_gateway_circuit_breaker_failures_total',
                'Circuit breaker failures',
                ['service'],
                registry=self.registry
            )
            
            # System metrics
            self.metrics['memory_usage'] = Gauge(
                'api_gateway_memory_usage_bytes',
                'Memory usage in bytes',
                registry=self.registry
            )
            
            self.metrics['cpu_usage'] = Gauge(
                'api_gateway_cpu_usage_percent',
                'CPU usage percentage',
                registry=self.registry
            )
            
            # Performance metrics
            self.metrics['response_size'] = Histogram(
                'api_gateway_response_size_bytes',
                'Response size in bytes',
                ['endpoint', 'content_type'],
                buckets=[100, 1000, 10000, 100000, 1000000, 10000000],
                registry=self.registry
            )
            
            self.metrics['cache_hits'] = Counter(
                'api_gateway_cache_hits_total',
                'Cache hits',
                ['cache_type'],
                registry=self.registry
            )
            
            self.metrics['cache_misses'] = Counter(
                'api_gateway_cache_misses_total',
                'Cache misses',
                ['cache_type'],
                registry=self.registry
            )
            
            # Info metrics
            self.metrics['build_info'] = Info(
                'api_gateway_build_info',
                'Build information',
                registry=self.registry
            )
            
            self.metrics['build_info'].info({
                'version': '1.0.0',
                'build_date': datetime.utcnow().isoformat(),
                'commit': 'unknown'
            })
            
            logger.info("Default metrics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize default metrics: {e}")
            raise
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        service: str,
        duration: float,
        response_size: int = 0
    ):
        """Record request metrics"""
        if not self.enabled:
            return
        
        try:
            # Request count
            self.metrics['requests_total'].labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                service=service
            ).inc()
            
            # Request duration
            self.metrics['request_duration'].labels(
                method=method,
                endpoint=endpoint,
                service=service
            ).observe(duration)
            
            # Response size
            if response_size > 0:
                self.metrics['response_size'].labels(
                    endpoint=endpoint,
                    content_type='application/json'  # Default
                ).observe(response_size)
            
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")
    
    def record_upstream_request(
        self,
        service: str,
        status_code: int,
        duration: float
    ):
        """Record upstream service request metrics"""
        if not self.enabled:
            return
        
        try:
            self.metrics['upstream_requests'].labels(
                service=service,
                status_code=status_code
            ).inc()
            
            self.metrics['upstream_duration'].labels(
                service=service
            ).observe(duration)
            
        except Exception as e:
            logger.error(f"Error recording upstream metrics: {e}")
    
    def update_service_health(self, service: str, healthy: bool):
        """Update service health metric"""
        if not self.enabled:
            return
        
        try:
            self.metrics['service_health'].labels(service=service).set(1 if healthy else 0)
            
        except Exception as e:
            logger.error(f"Error updating service health: {e}")
    
    def record_rate_limit_hit(self, identifier_type: str, endpoint: str):
        """Record rate limit hit"""
        if not self.enabled:
            return
        
        try:
            self.metrics['rate_limit_hits'].labels(
                identifier_type=identifier_type,
                endpoint=endpoint
            ).inc()
            
        except Exception as e:
            logger.error(f"Error recording rate limit hit: {e}")
    
    def update_rate_limit_remaining(self, identifier: str, endpoint: str, remaining: int):
        """Update rate limit remaining quota"""
        if not self.enabled:
            return
        
        try:
            self.metrics['rate_limit_remaining'].labels(
                identifier=identifier,
                endpoint=endpoint
            ).set(remaining)
            
        except Exception as e:
            logger.error(f"Error updating rate limit remaining: {e}")
    
    def update_circuit_breaker_state(self, service: str, state: str):
        """Update circuit breaker state"""
        if not self.enabled:
            return
        
        try:
            state_value = {"closed": 0, "open": 1, "half_open": 2}.get(state, 0)
            self.metrics['circuit_breaker_state'].labels(service=service).set(state_value)
            
        except Exception as e:
            logger.error(f"Error updating circuit breaker state: {e}")
    
    def record_circuit_breaker_failure(self, service: str):
        """Record circuit breaker failure"""
        if not self.enabled:
            return
        
        try:
            self.metrics['circuit_breaker_failures'].labels(service=service).inc()
            
        except Exception as e:
            logger.error(f"Error recording circuit breaker failure: {e}")
    
    def update_system_metrics(self, memory_usage: float, cpu_usage: float):
        """Update system resource metrics"""
        if not self.enabled:
            return
        
        try:
            self.metrics['memory_usage'].set(memory_usage)
            self.metrics['cpu_usage'].set(cpu_usage)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        if not self.enabled:
            return
        
        try:
            self.metrics['cache_hits'].labels(cache_type=cache_type).inc()
            
        except Exception as e:
            logger.error(f"Error recording cache hit: {e}")
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        if not self.enabled:
            return
        
        try:
            self.metrics['cache_misses'].labels(cache_type=cache_type).inc()
            
        except Exception as e:
            logger.error(f"Error recording cache miss: {e}")
    
    def add_custom_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Add custom metric value"""
        if not self.enabled:
            return
        
        try:
            # Store in custom metrics for analysis
            self.custom_metrics[name].append(value)
            self.custom_metrics_timestamps[name].append(datetime.utcnow())
            
            # Keep only last 1000 values
            if len(self.custom_metrics[name]) > 1000:
                self.custom_metrics[name] = self.custom_metrics[name][-1000:]
                self.custom_metrics_timestamps[name] = self.custom_metrics_timestamps[name][-1000:]
            
        except Exception as e:
            logger.error(f"Error adding custom metric: {e}")
    
    def create_custom_metric(
        self,
        name: str,
        metric_type: str,
        description: str,
        labels: Optional[List[str]] = None
    ) -> bool:
        """Create custom Prometheus metric"""
        if not self.enabled:
            return False
        
        try:
            labels = labels or []
            
            if metric_type == "counter":
                self.metrics[name] = Counter(
                    name, description, labels, registry=self.registry
                )
            elif metric_type == "gauge":
                self.metrics[name] = Gauge(
                    name, description, labels, registry=self.registry
                )
            elif metric_type == "histogram":
                self.metrics[name] = Histogram(
                    name, description, labels, registry=self.registry
                )
            elif metric_type == "summary":
                self.metrics[name] = Summary(
                    name, description, labels, registry=self.registry
                )
            else:
                logger.error(f"Unknown metric type: {metric_type}")
                return False
            
            logger.info(f"Created custom metric: {name} ({metric_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom metric: {e}")
            return False
    
    def add_alert(self, alert: Alert) -> bool:
        """Add alert configuration"""
        try:
            self.alerts[alert.name] = alert
            logger.info(f"Added alert: {alert.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            return False
    
    def remove_alert(self, alert_name: str) -> bool:
        """Remove alert configuration"""
        try:
            if alert_name in self.alerts:
                del self.alerts[alert_name]
                logger.info(f"Removed alert: {alert_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing alert: {e}")
            return False
    
    def add_alert_callback(self, callback: Callable[[Alert, float], None]):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    async def check_alerts(self):
        """
Check all alerts and trigger notifications"""
        if not self.enabled:
            return
        
        try:
            for alert in self.alerts.values():
                if not alert.enabled:
                    continue
                
                # This would implement actual alert condition checking
                # For now, placeholder implementation
                await self._check_individual_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _check_individual_alert(self, alert: Alert):
        """Check individual alert condition"""
        try:
            # Placeholder implementation
            # In reality, this would evaluate the alert condition
            # against current metrics
            
            current_time = datetime.utcnow()
            
            # Example: Check if request rate is too high
            if alert.name == "high_request_rate":
                # This would check actual metrics
                condition_met = False  # Placeholder
                
                if condition_met:
                    # Trigger alert
                    for callback in self.alert_callbacks:
                        callback(alert, 0.0)  # 0.0 is placeholder value
                    
                    alert.last_triggered = current_time
            
        except Exception as e:
            logger.error(f"Error checking alert {alert.name}: {e}")
    
    def get_metric_value(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get current value of a metric"""
        try:
            if metric_name not in self.metrics:
                return None
            
            metric = self.metrics[metric_name]
            
            if labels:
                # Get labeled metric value
                if hasattr(metric, 'labels'):
                    labeled_metric = metric.labels(**labels)
                    if hasattr(labeled_metric, '_value'):
                        return labeled_metric._value.get()
            else:
                # Get unlabeled metric value
                if hasattr(metric, '_value'):
                    return metric._value.get()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting metric value: {e}")
            return None
    
    def get_custom_metric_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for custom metric"""
        try:
            if name not in self.custom_metrics or not self.custom_metrics[name]:
                return {}
            
            values = self.custom_metrics[name]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "last_value": values[-1],
                "last_updated": self.custom_metrics_timestamps[name][-1].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting custom metric stats: {e}")
            return {}
    
    def generate_metrics(self) -> str:
        """Generate Prometheus metrics output"""
        if not self.enabled:
            return ""
        
        try:
            return generate_latest(self.registry).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return ""
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        try:
            summary = {
                "enabled": self.enabled,
                "total_metrics": len(self.metrics),
                "custom_metrics": len(self.custom_metrics),
                "alerts": len(self.alerts),
                "active_alerts": sum(1 for alert in self.alerts.values() if alert.enabled),
                "metrics_list": list(self.metrics.keys()),
                "custom_metrics_list": list(self.custom_metrics.keys())
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    async def start_background_collection(self):
        """Start background metrics collection"""
        if not self.enabled:
            return
        
        try:
            self._metrics_task = asyncio.create_task(self._metrics_collection_loop())
            self._alerts_task = asyncio.create_task(self._alerts_check_loop())
            
            logger.info("Started background metrics collection")
            
        except Exception as e:
            logger.error(f"Error starting background collection: {e}")
    
    async def stop_background_collection(self):
        """Stop background metrics collection"""
        try:
            if self._metrics_task:
                self._metrics_task.cancel()
            
            if self._alerts_task:
                self._alerts_task.cancel()
            
            logger.info("Stopped background metrics collection")
            
        except Exception as e:
            logger.error(f"Error stopping background collection: {e}")
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Sleep for collection interval
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(30)
    
    async def _alerts_check_loop(self):
        """Background alerts checking loop"""
        while True:
            try:
                await self.check_alerts()
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alerts check loop error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics"""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.update_system_metrics(
                memory_usage=memory.used,
                cpu_usage=psutil.cpu_percent()
            )
            
            # Update active connections (would be provided by the server)
            # This is a placeholder
            self.metrics['active_connections'].set(0)
            
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
