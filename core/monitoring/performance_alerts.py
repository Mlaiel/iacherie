"""
Performance Monitoring with Automated Alert Thresholds
Comprehensive monitoring system for performance metrics and alerting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json


logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to monitor"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    ACTIVE_CONNECTIONS = "active_connections"
    QUEUE_LENGTH = "queue_length"
    CACHE_HIT_RATIO = "cache_hit_ratio"


@dataclass
class AlertThreshold:
    """Configuration for alert thresholds"""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str = ">"  # >, <, >=, <=, ==, !=
    evaluation_window: int = 300  # seconds
    min_samples: int = 3
    severity: AlertSeverity = AlertSeverity.HIGH
    enabled: bool = True


@dataclass
class MetricSample:
    """A single metric sample"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    source: str = "unknown"


@dataclass
class Alert:
    """An active alert"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    metric_type: MetricType
    current_value: float
    threshold_value: float
    triggered_at: float
    resolved_at: Optional[float] = None


class MetricsCollector:
    """Collects and stores performance metrics"""
    
    def __init__(self, retention_period: int = 3600):  # 1 hour default
        self.metrics: Dict[MetricType, List[MetricSample]] = {
            metric_type: [] for metric_type in MetricType
        }
        self.retention_period = retention_period
        self.lock = asyncio.Lock()
    
    async def add_sample(self, metric_type: MetricType, value: float, 
                        labels: Optional[Dict[str, str]] = None, source: str = "unknown"):
        """Add a metric sample"""
        async with self.lock:
            sample = MetricSample(
                timestamp=time.time(),
                value=value,
                labels=labels or {},
                source=source
            )
            
            self.metrics[metric_type].append(sample)
            
            # Clean up old samples
            await self._cleanup_old_samples(metric_type)
    
    async def _cleanup_old_samples(self, metric_type: MetricType):
        """Remove samples older than retention period"""
        cutoff_time = time.time() - self.retention_period
        self.metrics[metric_type] = [
            sample for sample in self.metrics[metric_type]
            if sample.timestamp > cutoff_time
        ]
    
    async def get_metric_statistics(self, metric_type: MetricType, 
                                  window_seconds: int = 300) -> Dict[str, float]:
        """Get statistical summary of metric within time window"""
        async with self.lock:
            cutoff_time = time.time() - window_seconds
            samples = [
                sample for sample in self.metrics[metric_type]
                if sample.timestamp > cutoff_time
            ]
        
        if not samples:
            return {}
        
        values = [sample.value for sample in samples]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
            'p99': statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values),
        }


class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_thresholds: List[AlertThreshold] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Setup default thresholds
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self):
        """Setup default performance thresholds"""
        
        # Response time thresholds
        self.alert_thresholds.append(AlertThreshold(
            metric_type=MetricType.RESPONSE_TIME,
            warning_threshold=500.0,  # 500ms
            critical_threshold=1000.0,  # 1s
            comparison_operator=">",
            severity=AlertSeverity.HIGH
        ))
        
        # Error rate thresholds
        self.alert_thresholds.append(AlertThreshold(
            metric_type=MetricType.ERROR_RATE,
            warning_threshold=0.05,  # 5%
            critical_threshold=0.10,  # 10%
            comparison_operator=">",
            severity=AlertSeverity.CRITICAL
        ))
        
        # CPU usage thresholds
        self.alert_thresholds.append(AlertThreshold(
            metric_type=MetricType.CPU_USAGE,
            warning_threshold=80.0,  # 80%
            critical_threshold=95.0,  # 95%
            comparison_operator=">",
            severity=AlertSeverity.HIGH
        ))
        
        # Memory usage thresholds
        self.alert_thresholds.append(AlertThreshold(
            metric_type=MetricType.MEMORY_USAGE,
            warning_threshold=85.0,  # 85%
            critical_threshold=95.0,  # 95%
            comparison_operator=">",
            severity=AlertSeverity.HIGH
        ))
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if not self.running:
            self.running = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._evaluate_alerts()
                await asyncio.sleep(10)  # Check every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _evaluate_alerts(self):
        """Evaluate all alert thresholds"""
        for threshold in self.alert_thresholds:
            if not threshold.enabled:
                continue
            
            # Get metric statistics
            stats = await self.metrics_collector.get_metric_statistics(
                threshold.metric_type, threshold.evaluation_window
            )
            
            if not stats or stats['count'] < threshold.min_samples:
                continue
            
            # Evaluate threshold
            current_value = stats['mean']  # Use mean for evaluation
            triggered = self._evaluate_threshold(
                current_value, threshold.critical_threshold, threshold.comparison_operator
            )
            
            alert_id = f"{threshold.metric_type.value}_critical"
            
            if triggered and alert_id not in self.active_alerts:
                # Create new alert
                alert = Alert(
                    id=alert_id,
                    name=f"{threshold.metric_type.value.replace('_', ' ').title()} Alert",
                    description=f"Metric exceeded threshold",
                    severity=threshold.severity,
                    metric_type=threshold.metric_type,
                    current_value=current_value,
                    threshold_value=threshold.critical_threshold,
                    triggered_at=time.time()
                )
                
                self.active_alerts[alert_id] = alert
                await self._send_alert(alert)
                
            elif not triggered and alert_id in self.active_alerts:
                # Resolve alert
                alert = self.active_alerts[alert_id]
                alert.resolved_at = time.time()
                del self.active_alerts[alert_id]
                await self._resolve_alert(alert)
    
    def _evaluate_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate if threshold is breached"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        else:
            return False
    
    async def _send_alert(self, alert: Alert):
        """Send alert notification"""
        logger.warning(
            f"🚨 ALERT: {alert.name} - {alert.metric_type.value} "
            f"= {alert.current_value:.2f} (threshold: {alert.threshold_value})"
        )
    
    async def _resolve_alert(self, alert: Alert):
        """Send alert resolution notification"""
        logger.info(
            f"✅ RESOLVED: {alert.name} - {alert.metric_type.value}"
        )
    
    async def record_response_time(self, duration_ms: float, endpoint: str = "unknown"):
        """Record API response time"""
        await self.metrics_collector.add_sample(
            MetricType.RESPONSE_TIME, 
            duration_ms,
            labels={"endpoint": endpoint},
            source="api"
        )
    
    async def record_error_rate(self, error_rate: float, service: str = "unknown"):
        """Record error rate"""
        await self.metrics_collector.add_sample(
            MetricType.ERROR_RATE,
            error_rate,
            labels={"service": service},
            source="api"
        )
    
    async def record_resource_usage(self, cpu_percent: float, memory_percent: float):
        """Record system resource usage"""
        await self.metrics_collector.add_sample(
            MetricType.CPU_USAGE,
            cpu_percent,
            source="system"
        )
        
        await self.metrics_collector.add_sample(
            MetricType.MEMORY_USAGE,
            memory_percent,
            source="system"
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        return {
            'active_alerts': [
                {
                    'name': alert.name,
                    'severity': alert.severity.value,
                    'metric': alert.metric_type.value,
                    'current_value': alert.current_value,
                    'threshold': alert.threshold_value,
                    'triggered_at': alert.triggered_at
                }
                for alert in self.active_alerts.values()
            ],
            'total_alerts': len(self.active_alerts),
            'monitoring_running': self.running,
            'timestamp': time.time()
        }


# Global monitor instance
performance_monitor = PerformanceMonitor()