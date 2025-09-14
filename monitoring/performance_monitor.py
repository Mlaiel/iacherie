"""
Performance monitoring and metrics collection system
Implements detailed metrics per endpoint as required by checklist

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import psutil
import threading
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

@dataclass
class EndpointMetrics:
    """Metrics for individual endpoints"""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    request_size_bytes: int
    response_size_bytes: int
    timestamp: datetime
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class PerformanceStats:
    """Performance statistics summary"""
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    total_requests: int
    error_rate: float
    throughput_rps: float

class PerformanceMonitor:
    """
    Enterprise-grade performance monitoring system
    Tracks detailed metrics per endpoint for optimization
    """
    
    def __init__(self) -> None:
        self.metrics_store: List[EndpointMetrics] = deque(maxlen=100000)
        self.endpoint_stats: Dict[str, List[float]] = defaultdict(list)
        self.real_time_metrics: Dict[str, Any] = {}
        self.prometheus_registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        self.monitoring_active = True
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging for performance monitoring"""
        logger = logging.getLogger("ainflue.performance")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics for monitoring"""
        self.request_duration = Histogram(
            'ainflue_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint', 'status'],
            registry=self.prometheus_registry
        )
        
        self.request_count = Counter(
            'ainflue_requests_total',
            'Total requests',
            ['method', 'endpoint', 'status'],
            registry=self.prometheus_registry
        )
        
        self.active_connections = Gauge(
            'ainflue_active_connections',
            'Active connections',
            registry=self.prometheus_registry
        )
        
        self.system_cpu_usage = Gauge(
            'ainflue_system_cpu_percent',
            'System CPU usage percentage',
            registry=self.prometheus_registry
        )
        
        self.system_memory_usage = Gauge(
            'ainflue_system_memory_percent',
            'System memory usage percentage',
            registry=self.prometheus_registry
        )
    
    def record_request(self, 
                      endpoint -> None: str,
                      method -> None: str,
                      response_time_ms -> None: float,
                      status_code -> None: int,
                      request_size -> None: int = 0,
                      response_size -> None: int = 0,
                      user_id -> None: Optional[str] = None,
                      user_agent -> None: Optional[str] = None,
                      ip_address -> None: Optional[str] = None) -> None:
        """Record metrics for a single request"""
        
        metric = EndpointMetrics(
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=status_code,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Store in memory
        self.metrics_store.append(metric)
        
        # Update endpoint-specific stats
        endpoint_key = f"{method}:{endpoint}"
        self.endpoint_stats[endpoint_key].append(response_time_ms)
        
        # Keep only last 1000 measurements per endpoint
        if len(self.endpoint_stats[endpoint_key]) > 1000:
            self.endpoint_stats[endpoint_key] = self.endpoint_stats[endpoint_key][-1000:]
        
        # Update Prometheus metrics
        self.request_duration.labels(
            method=method, 
            endpoint=endpoint, 
            status=str(status_code)
        ).observe(response_time_ms / 1000.0)
        
        self.request_count.labels(
            method=method, 
            endpoint=endpoint, 
            status=str(status_code)
        ).inc()
        
        # Log performance issues
        if response_time_ms > 100:  # > 100ms as per checklist requirement
            self.logger.warning(
                f"Slow response detected: {endpoint} took {response_time_ms}ms"
            )
        
        if status_code >= 500:
            self.logger.error(
                f"Server error on {endpoint}: {status_code}"
            )
    
    def get_endpoint_stats(self, endpoint: str, method: str = "GET") -> Optional[PerformanceStats]:
        """Get performance statistics for a specific endpoint"""
        endpoint_key = f"{method}:{endpoint}"
        response_times = self.endpoint_stats.get(endpoint_key, [])
        
        if not response_times:
            return None
        
        # Calculate statistics
        sorted_times = sorted(response_times)
        total_requests = len(sorted_times)
        
        avg_response_time = sum(sorted_times) / total_requests
        min_response_time = min(sorted_times)
        max_response_time = max(sorted_times)
        
        # Calculate percentiles
        p95_index = int(0.95 * total_requests)
        p99_index = int(0.99 * total_requests)
        p95_response_time = sorted_times[p95_index] if p95_index < total_requests else max_response_time
        p99_response_time = sorted_times[p99_index] if p99_index < total_requests else max_response_time
        
        # Calculate error rate (from recent metrics)
        recent_metrics = [m for m in self.metrics_store 
                         if m.endpoint == endpoint and m.method == method]
        error_count = len([m for m in recent_metrics if m.status_code >= 400])
        error_rate = error_count / len(recent_metrics) if recent_metrics else 0
        
        # Calculate throughput (requests per second over last minute)
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_requests = [m for m in recent_metrics if m.timestamp >= one_minute_ago]
        throughput_rps = len(recent_requests) / 60.0
        
        return PerformanceStats(
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            total_requests=total_requests,
            error_rate=error_rate,
            throughput_rps=throughput_rps
        )
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update Prometheus metrics
            self.system_cpu_usage.set(cpu_percent)
            self.system_memory_usage.set(memory.percent)
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            }
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time data for monitoring dashboard"""
        # Get recent metrics (last 5 minutes)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_metrics = [m for m in self.metrics_store if m.timestamp >= five_minutes_ago]
        
        # Group by endpoint
        endpoint_data = defaultdict(list)
        for metric in recent_metrics:
            endpoint_key = f"{metric.method}:{metric.endpoint}"
            endpoint_data[endpoint_key].append(metric)
        
        # Calculate real-time stats
        dashboard_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_requests_5m": len(recent_metrics),
            "avg_response_time_5m": sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            "error_rate_5m": len([m for m in recent_metrics if m.status_code >= 400]) / len(recent_metrics) if recent_metrics else 0,
            "system_metrics": self.get_system_metrics(),
            "endpoint_breakdown": {}
        }
        
        # Endpoint-specific breakdown
        for endpoint_key, metrics in endpoint_data.items():
            dashboard_data["endpoint_breakdown"][endpoint_key] = {
                "request_count": len(metrics),
                "avg_response_time": sum(m.response_time_ms for m in metrics) / len(metrics),
                "error_rate": len([m for m in metrics if m.status_code >= 400]) / len(metrics),
                "throughput_rps": len(metrics) / 300.0  # 5 minutes = 300 seconds
            }
        
        return dashboard_data
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds"""
        alerts = []
        
        # Check response time alerts (> 100ms as per checklist)
        for endpoint_key, response_times in self.endpoint_stats.items():
            if response_times:
                avg_time = sum(response_times[-10:]) / min(len(response_times), 10)  # Last 10 requests
                if avg_time > 100:
                    alerts.append({
                        "type": "performance",
                        "severity": "warning" if avg_time < 200 else "critical",
                        "endpoint": endpoint_key,
                        "message": f"High response time: {avg_time:.2f}ms",
                        "threshold": 100,
                        "current_value": avg_time
                    })
        
        # Check system resource alerts
        system_metrics = self.get_system_metrics()
        if system_metrics.get("cpu_percent", 0) > 80:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"High CPU usage: {system_metrics['cpu_percent']:.1f}%",
                "threshold": 80,
                "current_value": system_metrics["cpu_percent"]
            })
        
        if system_metrics.get("memory_percent", 0) > 85:
            alerts.append({
                "type": "system",
                "severity": "critical",
                "message": f"High memory usage: {system_metrics['memory_percent']:.1f}%",
                "threshold": 85,
                "current_value": system_metrics["memory_percent"]
            })
        
        return alerts
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        return generate_latest(self.prometheus_registry).decode('utf-8')
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        metrics_in_period = [m for m in self.metrics_store if m.timestamp >= cutoff_time]
        
        if not metrics_in_period:
            return {"error": "No metrics available for the specified period"}
        
        # Overall stats
        total_requests = len(metrics_in_period)
        total_errors = len([m for m in metrics_in_period if m.status_code >= 400])
        avg_response_time = sum(m.response_time_ms for m in metrics_in_period) / total_requests
        
        # Group by endpoint
        endpoint_breakdown = defaultdict(list)
        for metric in metrics_in_period:
            endpoint_key = f"{metric.method}:{metric.endpoint}"
            endpoint_breakdown[endpoint_key].append(metric)
        
        # Detailed endpoint analysis
        endpoint_analysis = {}
        for endpoint_key, metrics in endpoint_breakdown.items():
            response_times = [m.response_time_ms for m in metrics]
            status_codes = [m.status_code for m in metrics]
            
            endpoint_analysis[endpoint_key] = {
                "total_requests": len(metrics),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "error_rate": len([s for s in status_codes if s >= 400]) / len(status_codes),
                "throughput_rps": len(metrics) / (hours * 3600),
                "p95_response_time": sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0
            }
        
        # Performance recommendations
        recommendations = []
        for endpoint_key, stats in endpoint_analysis.items():
            if stats["avg_response_time"] > 100:
                recommendations.append(f"Optimize {endpoint_key}: avg response time {stats['avg_response_time']:.2f}ms > 100ms target")
            if stats["error_rate"] > 0.01:
                recommendations.append(f"Investigate errors in {endpoint_key}: {stats['error_rate']:.2%} error rate > 1% target")
        
        return {
            "report_period_hours": hours,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "overall_error_rate": total_errors / total_requests,
                "avg_response_time_ms": avg_response_time,
                "throughput_rps": total_requests / (hours * 3600)
            },
            "endpoint_analysis": endpoint_analysis,
            "recommendations": recommendations,
            "sla_compliance": {
                "response_time_target": "< 100ms",
                "response_time_actual": f"{avg_response_time:.2f}ms",
                "response_time_met": avg_response_time < 100,
                "error_rate_target": "< 1%",
                "error_rate_actual": f"{(total_errors / total_requests) * 100:.2f}%",
                "error_rate_met": (total_errors / total_requests) < 0.01
            }
        }

# Singleton instance for global use
performance_monitor = PerformanceMonitor()

# Middleware function for FastAPI
def performance_middleware(request, call_next) -> None:
    """FastAPI middleware to automatically track performance"""
    start_time = time.time()
    
    response = call_next(request)
    
    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    
    # Extract request info
    endpoint = request.url.path
    method = request.method
    status_code = getattr(response, 'status_code', 200)
    
    # Record metrics
    performance_monitor.record_request(
        endpoint=endpoint,
        method=method,
        response_time_ms=response_time_ms,
        status_code=status_code,
        request_size=len(str(request.body)) if hasattr(request, 'body') else 0,
        response_size=len(str(response.body)) if hasattr(response, 'body') else 0,
        user_agent=request.headers.get('user-agent'),
        ip_address=request.client.host if hasattr(request, 'client') else None
    )
    
    return response

if __name__ == "__main__":
    # Example usage and testing
    monitor = PerformanceMonitor()
    
    # Simulate some requests
    import random
    endpoints = ["/api/v1/validation/validate", "/api/v1/health", "/api/v1/monetization/analytics"]
    
    for _ in range(100):
        endpoint = random.choice(endpoints)
        method = random.choice(["GET", "POST"])
        response_time = random.uniform(50, 200)
        status_code = random.choice([200, 200, 200, 400, 500])
        
        monitor.record_request(endpoint, method, response_time, status_code)
    
    # Generate report
    report = monitor.generate_performance_report(hours=1)
    print(json.dumps(report, indent=2))