"""
📊 Performance Monitor - Real-time Performance Tracking
Enterprise-grade performance monitoring and metrics collection

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import time
import psutil
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_QUERY_TIME = "database_query_time"
    API_CALL_TIME = "api_call_time"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    unit: str


class PerformanceMonitor:
    """
    Real-time performance monitoring with alerting and historical tracking
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics: Dict[MetricType, List[PerformanceMetric]] = defaultdict(list)
        self.thresholds: Dict[MetricType, PerformanceThreshold] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
        # Configure default thresholds
        self._configure_default_thresholds()
        
        logger.info("📊 Performance Monitor initialized")
    
    def track(self, metric_type: MetricType, value: float, tags: Optional[Dict[str, str]] = None, 
              metadata: Optional[Dict[str, Any]] = None):
        """
        Track a performance metric
        
        Args:
            metric_type: Type of metric
            value: Metric value
            tags: Optional tags for categorization
            metadata: Optional additional metadata
        """
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics[metric_type].append(metric)
        
        # Check thresholds
        self._check_thresholds(metric)
        
        # Keep only last 1000 metrics per type to avoid memory bloat
        if len(self.metrics[metric_type]) > 1000:
            self.metrics[metric_type] = self.metrics[metric_type][-1000:]
    
    def track_execution_time(self, operation_name: str, execution_time: float):
        """
        Track operation execution time
        
        Args:
            operation_name: Name of the operation
            execution_time: Execution time in seconds
        """
        self.track(
            MetricType.RESPONSE_TIME,
            execution_time * 1000,  # Convert to milliseconds
            tags={"operation": operation_name},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def track_system_metrics(self):
        """Track current system metrics (CPU, memory, disk, network)"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.track(MetricType.CPU_USAGE, cpu_percent, tags={"source": "system"})
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.track(MetricType.MEMORY_USAGE, memory.percent, tags={"source": "system"})
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            self.track(
                MetricType.DISK_IO,
                disk_io.read_bytes + disk_io.write_bytes,
                tags={"source": "system"},
                metadata={"read_bytes": disk_io.read_bytes, "write_bytes": disk_io.write_bytes}
            )
        
        # Network I/O
        network_io = psutil.net_io_counters()
        if network_io:
            self.track(
                MetricType.NETWORK_IO,
                network_io.bytes_sent + network_io.bytes_recv,
                tags={"source": "system"},
                metadata={"bytes_sent": network_io.bytes_sent, "bytes_recv": network_io.bytes_recv}
            )
    
    def get_metrics(self, metric_type: Optional[MetricType] = None, 
                   limit: int = 100) -> Dict[str, Any]:
        """
        Get performance metrics
        
        Args:
            metric_type: Optional specific metric type
            limit: Maximum number of metrics to return per type
            
        Returns:
            Dict: Performance metrics data
        """
        if metric_type:
            metrics_list = self.metrics.get(metric_type, [])[-limit:]
            return {
                "metric_type": metric_type.value,
                "count": len(metrics_list),
                "latest": self._serialize_metric(metrics_list[-1]) if metrics_list else None,
                "average": self._calculate_average(metrics_list),
                "min": min(m.value for m in metrics_list) if metrics_list else None,
                "max": max(m.value for m in metrics_list) if metrics_list else None,
                "data": [self._serialize_metric(m) for m in metrics_list]
            }
        
        # Return all metrics
        result = {
            "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
            "uptime_seconds": time.time() - self.start_time,
            "metrics_by_type": {}
        }
        
        for mtype, metrics_list in self.metrics.items():
            recent_metrics = metrics_list[-limit:]
            result["metrics_by_type"][mtype.value] = {
                "count": len(recent_metrics),
                "average": self._calculate_average(recent_metrics),
                "latest": self._serialize_metric(recent_metrics[-1]) if recent_metrics else None
            }
        
        return result
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary with key statistics
        
        Returns:
            Dict: Performance summary
        """
        current_system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent
        }
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_metrics_tracked": sum(len(m) for m in self.metrics.values()),
            "active_alerts": len([a for a in self.alerts if not a.get("resolved", False)]),
            "system_health": self._calculate_system_health(),
            "current_system": current_system_metrics,
            "thresholds_configured": len(self.thresholds)
        }
    
    def set_threshold(self, metric_type: MetricType, warning: float, 
                     critical: float, unit: str = ""):
        """
        Set performance threshold
        
        Args:
            metric_type: Type of metric
            warning: Warning threshold value
            critical: Critical threshold value
            unit: Unit of measurement
        """
        self.thresholds[metric_type] = PerformanceThreshold(
            metric_type=metric_type,
            warning_threshold=warning,
            critical_threshold=critical,
            unit=unit
        )
        logger.info(f"🎯 Threshold set for {metric_type.value}: Warning={warning}, Critical={critical}")
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get performance alerts
        
        Args:
            resolved: Filter by resolved status (None = all)
            
        Returns:
            List: Performance alerts
        """
        if resolved is None:
            return self.alerts
        return [a for a in self.alerts if a.get("resolved", False) == resolved]
    
    def resolve_alert(self, alert_id: str):
        """
        Resolve a performance alert
        
        Args:
            alert_id: Alert identifier
        """
        for alert in self.alerts:
            if alert.get("alert_id") == alert_id:
                alert["resolved"] = True
                alert["resolved_at"] = datetime.utcnow().isoformat()
                logger.info(f"✅ Alert resolved: {alert_id}")
                break
    
    def _configure_default_thresholds(self):
        """Configure default performance thresholds"""
        self.set_threshold(MetricType.CPU_USAGE, 70.0, 90.0, "%")
        self.set_threshold(MetricType.MEMORY_USAGE, 75.0, 90.0, "%")
        self.set_threshold(MetricType.RESPONSE_TIME, 1000.0, 3000.0, "ms")
        self.set_threshold(MetricType.ERROR_RATE, 5.0, 10.0, "%")
    
    def _check_thresholds(self, metric: PerformanceMetric):
        """Check if metric exceeds thresholds"""
        threshold = self.thresholds.get(metric.metric_type)
        if not threshold:
            return
        
        severity = None
        if metric.value >= threshold.critical_threshold:
            severity = "critical"
        elif metric.value >= threshold.warning_threshold:
            severity = "warning"
        
        if severity:
            alert = {
                "alert_id": f"{metric.metric_type.value}_{int(time.time())}",
                "severity": severity,
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "threshold": threshold.critical_threshold if severity == "critical" else threshold.warning_threshold,
                "unit": threshold.unit,
                "timestamp": metric.timestamp.isoformat(),
                "resolved": False,
                "tags": metric.tags
            }
            self.alerts.append(alert)
            logger.warning(f"⚠️ Performance Alert: {severity.upper()} - {metric.metric_type.value}={metric.value}{threshold.unit}")
    
    def _calculate_average(self, metrics: List[PerformanceMetric]) -> Optional[float]:
        """Calculate average value of metrics"""
        if not metrics:
            return None
        return sum(m.value for m in metrics) / len(metrics)
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health status"""
        active_critical = len([a for a in self.alerts if a.get("severity") == "critical" and not a.get("resolved")])
        active_warnings = len([a for a in self.alerts if a.get("severity") == "warning" and not a.get("resolved")])
        
        if active_critical > 0:
            return "critical"
        elif active_warnings > 2:
            return "degraded"
        elif active_warnings > 0:
            return "warning"
        return "healthy"
    
    def _serialize_metric(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """Serialize metric to dictionary"""
        return {
            "type": metric.metric_type.value,
            "value": metric.value,
            "timestamp": metric.timestamp.isoformat(),
            "tags": metric.tags,
            "metadata": metric.metadata
        }


# Global performance monitor instance
_global_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get global performance monitor instance
    
    Returns:
        PerformanceMonitor: Global performance monitor
    """
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor


# Auto-initialize
_global_performance_monitor = PerformanceMonitor()

logger.info("📊 Performance Monitor module initialized")
