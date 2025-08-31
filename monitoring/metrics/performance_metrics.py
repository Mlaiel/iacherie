"""📊 Performance Metrics - Advanced Performance Monitoring System
===============================================================

Enterprise-grade performance monitoring for the Ainflue platform with
real-time metrics, APM integration, and comprehensive performance analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from functools import wraps
from collections import defaultdict, deque
from enum import Enum
import statistics
import json

# Try to import psutil, fallback to mock implementation if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for testing environments
    class MockProcess:
        pid = 12345
        
        def memory_info(self):
            class MemInfo:
                rss = 1024 * 1024 * 50  # 50MB
                vms = 1024 * 1024 * 100  # 100MB
            return MemInfo()
        
        def cpu_percent(self):
            return 25.0
        
        def num_threads(self):
            return 10
        
        def open_files(self):
            return []
        
        def connections(self):
            return []
    
    class MockPsutil:
        @staticmethod
        def cpu_percent(interval=1):
            return 35.5
        
        @staticmethod
        def cpu_count():
            return 4
        
        @staticmethod
        def virtual_memory():
            class VMem:
                total = 8 * 1024 * 1024 * 1024  # 8GB
                available = 4 * 1024 * 1024 * 1024  # 4GB
                percent = 50.0
                used = 4 * 1024 * 1024 * 1024
                free = 4 * 1024 * 1024 * 1024
            return VMem()
        
        @staticmethod
        def swap_memory():
            class SwapMem:
                total = 2 * 1024 * 1024 * 1024  # 2GB
                used = 512 * 1024 * 1024  # 512MB
                percent = 25.0
            return SwapMem()
        
        @staticmethod
        def disk_usage(path):
            class DiskUsage:
                total = 100 * 1024 * 1024 * 1024  # 100GB
                used = 60 * 1024 * 1024 * 1024  # 60GB
                free = 40 * 1024 * 1024 * 1024  # 40GB
                percent = 60.0
            return DiskUsage()
        
        @staticmethod
        def disk_io_counters():
            class DiskIO:
                read_count = 1000
                write_count = 500
                read_bytes = 1024 * 1024 * 100  # 100MB
                write_bytes = 1024 * 1024 * 50  # 50MB
            return DiskIO()
        
        @staticmethod
        def net_io_counters():
            class NetIO:
                bytes_sent = 1024 * 1024 * 10  # 10MB
                bytes_recv = 1024 * 1024 * 20  # 20MB
                packets_sent = 1000
                packets_recv = 2000
                errin = 0
                errout = 0
                dropin = 0
                dropout = 0
            return NetIO()
        
        @staticmethod
        def Process():
            return MockProcess()
        
        @staticmethod
        def getloadavg():
            return (0.5, 0.7, 0.9)
    
    psutil = MockPsutil()

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance levels for classification"""    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""    name: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert definition"""    metric_name: str
    threshold: float
    condition: str  # 'greater_than', 'less_than', 'equals'
    severity: str
    message: str
    enabled: bool = True


class PerformanceProfiler:
    """    Performance profiler for function and method execution tracking
    """    
    def __init__(self):
        self.profiles = defaultdict(list)
        self.active_profiles = {}
        
    def start_profile(self, operation_name: str) -> str:
        """Start profiling an operation"""        profile_id = f"{operation_name}_{time.time()}"
        self.active_profiles[profile_id] = {
            "name": operation_name,
            "start_time": time.time(),
            "start_memory": psutil.Process().memory_info().rss,
            "thread_id": threading.get_ident()
        }
        return profile_id
    
    def end_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """End profiling and return results"""        if profile_id not in self.active_profiles:
            return None
        
        profile = self.active_profiles.pop(profile_id)
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        result = {
            "operation": profile["name"],
            "duration_ms": (end_time - profile["start_time"]) * 1000,
            "memory_delta_mb": (end_memory - profile["start_memory"]) / (1024 * 1024),
            "start_time": profile["start_time"],
            "end_time": end_time,
            "thread_id": profile["thread_id"]
        }
        
        self.profiles[profile["name"]].append(result)
        return result


def performance_monitor(operation_name: str = None):
    """Decorator for automatic performance monitoring"""    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            profiler = PerformanceProfiler()
            profile_id = profiler.start_profile(name)
            
            try:
                result = await func(*args, **kwargs)
                profile_result = profiler.end_profile(profile_id)
                
                if profile_result:
                    logger.debug(f"⚡ {name}: {profile_result['duration_ms']:.2f}ms")
                
                return result
            except Exception as e:
                profiler.end_profile(profile_id)
                logger.error(f"❌ {name} failed: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            profiler = PerformanceProfiler()
            profile_id = profiler.start_profile(name)
            
            try:
                result = func(*args, **kwargs)
                profile_result = profiler.end_profile(profile_id)
                
                if profile_result:
                    logger.debug(f"⚡ {name}: {profile_result['duration_ms']:.2f}ms")
                
                return result
            except Exception as e:
                profiler.end_profile(profile_id)
                logger.error(f"❌ {name} failed: {str(e)}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class PerformanceMetricsCollector:
    """    Advanced performance metrics collection and analysis system
    
    Features:
    - Real-time performance monitoring
    - System resource tracking
    - Application performance metrics
    - Custom metric collection
    - Performance profiling
    - Alert management
    - Historical analysis
    - Performance benchmarking
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance metrics collector"""        self.config = config or {}
        
        # Metrics storage
        self.metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.recent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Performance tracking
        self.profiler = PerformanceProfiler()
        self.request_metrics = deque(maxlen=10000)  # Track recent requests
        
        # Alerts
        self.alerts: List[PerformanceAlert] = []
        self.triggered_alerts: List[Dict[str, Any]] = []
        
        # System monitoring
        self.system_monitor_enabled = True
        self.monitoring_interval = 30  # seconds
        self.monitoring_task = None
        
        # Performance baselines
        self.baselines = {
            "api_response_time": 200.0,  # ms
            "database_query_time": 50.0,  # ms
            "cpu_usage": 70.0,  # percent
            "memory_usage": 80.0,  # percent
            "disk_io_latency": 10.0,  # ms
            "network_latency": 100.0  # ms
        }
        
        # Initialize default alerts
        self._initialize_alerts()
        
        logger.info("PerformanceMetricsCollector initialized successfully")
    
    async def start_monitoring(self) -> bool:
        """Start performance monitoring"""        try:
            if self.system_monitor_enabled:
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("🚀 Performance monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop performance monitoring"""        try:
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("⏹️ Performance monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop performance monitoring: {e}")
            return False
    
    async def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        source: str = "system",
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a performance metric"""        try:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.utcnow(),
                source=source,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            self.metrics[name].append(metric)
            self.recent_metrics[name].append(metric)
            
            # Check alerts
            await self._check_alerts(metric)
            
        except Exception as e:
            logger.error(f"Error recording metric {name}: {e}")
    
    async def record_request_metrics(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: Optional[int] = None
    ) -> None:
        """Record request performance metrics"""        try:
            request_data = {
                "endpoint": endpoint,
                "method": method,
                "response_time": response_time,
                "status_code": status_code,
                "timestamp": datetime.utcnow(),
                "user_id": user_id
            }
            
            self.request_metrics.append(request_data)
            
            # Record as performance metric
            await self.record_metric(
                "api_response_time",
                response_time,
                "ms",
                "api",
                {"endpoint": endpoint, "method": method}
            )
            
            # Record error rate if error
            if status_code >= 400:
                await self.record_metric(
                    "api_error_rate",
                    1,
                    "count",
                    "api",
                    {"endpoint": endpoint, "status": str(status_code)}
                )
            
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")
    
    async def record_database_metrics(
        self,
        query_type: str,
        execution_time: float,
        rows_affected: int = 0,
        table: str = "",
        success: bool = True
    ) -> None:
        """Record database performance metrics"""        try:
            labels = {
                "query_type": query_type,
                "table": table,
                "success": str(success)
            }
            
            metadata = {
                "rows_affected": rows_affected,
                "success": success
            }
            
            await self.record_metric(
                "database_query_time",
                execution_time,
                "ms",
                "database",
                labels,
                metadata
            )
            
        except Exception as e:
            logger.error(f"Error recording database metrics: {e}")
    
    async def get_system_performance(self) -> Dict[str, Any]:
        """Get current system performance metrics"""        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_avg": list(load_avg),
                    "performance_level": self._classify_performance(cpu_percent, "cpu")
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_percent": swap.percent,
                    "performance_level": self._classify_performance(memory.percent, "memory")
                },
                "disk": {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": disk_usage.percent,
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0,
                    "performance_level": self._classify_performance(disk_usage.percent, "disk")
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv,
                    "errin": network_io.errin,
                    "errout": network_io.errout,
                    "dropin": network_io.dropin,
                    "dropout": network_io.dropout
                },
                "process": {
                    "pid": process.pid,
                    "memory_rss": process_memory.rss,
                    "memory_vms": process_memory.vms,
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system performance: {e}")
            return {"error": str(e)}
    
    async def get_application_performance(self) -> Dict[str, Any]:
        """Get application performance metrics"""        try:
            current_time = datetime.utcnow()
            last_hour = current_time - timedelta(hours=1)
            
            # Recent request metrics
            recent_requests = [
                req for req in self.request_metrics
                if req["timestamp"] >= last_hour
            ]
            
            if recent_requests:
                response_times = [req["response_time"] for req in recent_requests]
                status_codes = [req["status_code"] for req in recent_requests]
                
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                error_count = len([sc for sc in status_codes if sc >= 400])
                error_rate = (error_count / len(recent_requests)) * 100
                
                # Get endpoint performance
                endpoint_stats = defaultdict(list)
                for req in recent_requests:
                    endpoint_stats[req["endpoint"]].append(req["response_time"])
                
                slowest_endpoints = []
                for endpoint, times in endpoint_stats.items():
                    avg_time = statistics.mean(times)
                    slowest_endpoints.append({
                        "endpoint": endpoint,
                        "avg_response_time": avg_time,
                        "request_count": len(times)
                    })
                
                slowest_endpoints.sort(key=lambda x: x["avg_response_time"], reverse=True)
                
            else:
                avg_response_time = 0
                p95_response_time = 0
                error_rate = 0
                slowest_endpoints = []
            
            return {
                "timestamp": current_time.isoformat(),
                "requests": {
                    "total_count": len(recent_requests),
                    "avg_response_time": round(avg_response_time, 2),
                    "p95_response_time": round(p95_response_time, 2),
                    "error_rate": round(error_rate, 2),
                    "performance_level": self._classify_performance(avg_response_time, "response_time")
                },
                "slowest_endpoints": slowest_endpoints[:10],
                "profiler_stats": {
                    "active_profiles": len(self.profiler.active_profiles),
                    "completed_profiles": sum(len(profiles) for profiles in self.profiler.profiles.values())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting application performance: {e}")
            return {"error": str(e)}
    
    async def get_performance_summary(self, period_hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for a time period"""        try:
            current_time = datetime.utcnow()
            start_time = current_time - timedelta(hours=period_hours)
            
            summary = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": current_time.isoformat(),
                    "hours": period_hours
                },
                "metrics_summary": {},
                "alerts_summary": {
                    "total_alerts": len(self.triggered_alerts),
                    "critical_alerts": len([a for a in self.triggered_alerts if a.get("severity") == "critical"]),
                    "recent_alerts": [
                        a for a in self.triggered_alerts 
                        if datetime.fromisoformat(a["timestamp"]) >= start_time
                    ]
                },
                "top_performance_issues": []
            }
            
            # Summarize metrics for the period
            for metric_name, metric_list in self.metrics.items():
                period_metrics = [
                    m for m in metric_list
                    if start_time <= m.timestamp <= current_time
                ]
                
                if period_metrics:
                    values = [m.value for m in period_metrics]
                    summary["metrics_summary"][metric_name] = {
                        "count": len(values),
                        "avg": round(statistics.mean(values), 2),
                        "min": round(min(values), 2),
                        "max": round(max(values), 2),
                        "p95": round(statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values), 2)
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def _classify_performance(self, value: float, metric_type: str) -> str:
        """Classify performance level based on value and type"""        try:
            if metric_type == "cpu":
                if value <= 50:
                    return PerformanceLevel.EXCELLENT.value
                elif value <= 70:
                    return PerformanceLevel.GOOD.value
                elif value <= 85:
                    return PerformanceLevel.FAIR.value
                elif value <= 95:
                    return PerformanceLevel.POOR.value
                else:
                    return PerformanceLevel.CRITICAL.value
            
            elif metric_type in ["memory", "disk"]:
                if value <= 60:
                    return PerformanceLevel.EXCELLENT.value
                elif value <= 75:
                    return PerformanceLevel.GOOD.value
                elif value <= 85:
                    return PerformanceLevel.FAIR.value
                elif value <= 95:
                    return PerformanceLevel.POOR.value
                else:
                    return PerformanceLevel.CRITICAL.value
            
            elif metric_type == "response_time":
                if value <= 100:
                    return PerformanceLevel.EXCELLENT.value
                elif value <= 200:
                    return PerformanceLevel.GOOD.value
                elif value <= 500:
                    return PerformanceLevel.FAIR.value
                elif value <= 1000:
                    return PerformanceLevel.POOR.value
                else:
                    return PerformanceLevel.CRITICAL.value
            
            else:
                return PerformanceLevel.GOOD.value
                
        except Exception:
            return PerformanceLevel.GOOD.value
    
    def _initialize_alerts(self):
        """Initialize default performance alerts"""        try:
            default_alerts = [
                PerformanceAlert(
                    "api_response_time",
                    1000.0,
                    "greater_than",
                    "warning",
                    "API response time is high"
                ),
                PerformanceAlert(
                    "api_response_time",
                    2000.0,
                    "greater_than",
                    "critical",
                    "API response time is critically high"
                ),
                PerformanceAlert(
                    "database_query_time",
                    500.0,
                    "greater_than",
                    "warning",
                    "Database queries are slow"
                ),
                PerformanceAlert(
                    "api_error_rate",
                    5.0,
                    "greater_than",
                    "warning",
                    "API error rate is high"
                ),
                PerformanceAlert(
                    "api_error_rate",
                    10.0,
                    "greater_than",
                    "critical",
                    "API error rate is critically high"
                )
            ]
            
            self.alerts.extend(default_alerts)
            
        except Exception as e:
            logger.error(f"Error initializing alerts: {e}")
    
    async def _check_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts"""        try:
            for alert in self.alerts:
                if not alert.enabled or alert.metric_name != metric.name:
                    continue
                
                triggered = False
                
                if alert.condition == "greater_than" and metric.value > alert.threshold:
                    triggered = True
                elif alert.condition == "less_than" and metric.value < alert.threshold:
                    triggered = True
                elif alert.condition == "equals" and metric.value == alert.threshold:
                    triggered = True
                
                if triggered:
                    await self._trigger_alert(alert, metric)
                    
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _trigger_alert(self, alert: PerformanceAlert, metric: PerformanceMetric):
        """Trigger performance alert"""        try:
            alert_data = {
                "alert_name": f"{alert.metric_name}_{alert.condition}_{alert.threshold}",
                "metric_name": alert.metric_name,
                "metric_value": metric.value,
                "threshold": alert.threshold,
                "condition": alert.condition,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": metric.timestamp.isoformat(),
                "source": metric.source,
                "labels": metric.labels
            }
            
            self.triggered_alerts.append(alert_data)
            
            # Log alert
            if alert.severity == "critical":
                logger.critical(f"🚨 CRITICAL PERFORMANCE ALERT: {alert.message} (value: {metric.value}, threshold: {alert.threshold})")
            else:
                logger.warning(f"⚠️ PERFORMANCE ALERT: {alert.message} (value: {metric.value}, threshold: {alert.threshold})")
                
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _monitoring_loop(self):
        """Continuous system monitoring loop"""        while True:
            try:
                # Get system performance
                system_perf = await self.get_system_performance()
                
                # Record system metrics
                if "cpu" in system_perf:
                    await self.record_metric("cpu_usage", system_perf["cpu"]["percent"], "percent", "system")
                
                if "memory" in system_perf:
                    await self.record_metric("memory_usage", system_perf["memory"]["percent"], "percent", "system")
                
                if "disk" in system_perf:
                    await self.record_metric("disk_usage", system_perf["disk"]["percent"], "percent", "system")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    def get_collector_stats(self) -> Dict[str, Any]:
        """Get performance collector statistics"""        return {
            "version": "1.0.0",
            "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
            "unique_metric_types": len(self.metrics),
            "total_requests_tracked": len(self.request_metrics),
            "active_profiles": len(self.profiler.active_profiles),
            "completed_profiles": sum(len(profiles) for profiles in self.profiler.profiles.values()),
            "total_alerts": len(self.alerts),
            "triggered_alerts": len(self.triggered_alerts),
            "monitoring_enabled": self.system_monitor_enabled,
            "monitoring_interval": self.monitoring_interval
        }


# Export classes
__all__ = [
    "PerformanceMetricsCollector",
    "PerformanceMetric",
    "PerformanceAlert",
    "PerformanceProfiler",
    "PerformanceLevel",
    "performance_monitor"
]
