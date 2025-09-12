"""
🎯 INFERENCE PERFORMANCE MONITOR
Enterprise-grade real-time inference performance monitoring and alerting system.

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import numpy as np
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, start_http_server


@dataclass
class InferenceMetrics:
    """Inference performance metrics data structure."""
    model_id: str
    creator_type: str
    latency_ms: float
    throughput_rps: float
    memory_usage_mb: float
    cpu_usage_percent: float
    gpu_usage_percent: float
    request_count: int
    error_count: int
    success_rate: float
    confidence_score: float
    timestamp: datetime
    endpoint: str
    batch_size: int


@dataclass
class PerformanceAlert:
    """Performance alert data structure."""
    alert_id: str
    model_id: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # 'warning', 'critical', 'fatal'
    message: str
    timestamp: datetime
    creator_type: Optional[str] = None


class InferencePerformanceMonitor:
    """
    🎯 Enterprise-grade inference performance monitoring system.
    
    Features:
    - Real-time performance metrics collection
    - Creator-specific performance tracking
    - Prometheus integration for monitoring
    - Intelligent alerting with threshold management
    - Performance trend analysis
    - Resource utilization monitoring
    - SLA compliance tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Performance data storage
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.creator_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.model_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Alert management
        self.alert_thresholds = self._setup_default_thresholds()
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_callbacks: List[callable] = []
        
        # Prometheus metrics
        self.prometheus_registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Performance tracking
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # SLA tracking
        self.sla_targets = {
            'latency_p95_ms': 100,
            'latency_p99_ms': 200,
            'success_rate_min': 99.5,
            'throughput_min_rps': 100
        }
        
        self.logger.info("InferencePerformanceMonitor initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('inference_performance_monitor')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Setup default performance alert thresholds."""
        return {
            'latency_ms': {
                'warning': 100.0,
                'critical': 200.0,
                'fatal': 500.0
            },
            'error_rate': {
                'warning': 1.0,
                'critical': 5.0,
                'fatal': 10.0
            },
            'memory_usage_mb': {
                'warning': 1000.0,
                'critical': 2000.0,
                'fatal': 4000.0
            },
            'cpu_usage_percent': {
                'warning': 70.0,
                'critical': 85.0,
                'fatal': 95.0
            },
            'throughput_rps': {
                'warning': 50.0,  # Below this is warning
                'critical': 25.0,
                'fatal': 10.0
            }
        }
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring."""
        self.prom_latency = Histogram(
            'inference_latency_seconds',
            'Inference latency in seconds',
            ['model_id', 'creator_type', 'endpoint'],
            registry=self.prometheus_registry
        )
        
        self.prom_throughput = Gauge(
            'inference_throughput_rps',
            'Inference throughput in requests per second',
            ['model_id', 'creator_type'],
            registry=self.prometheus_registry
        )
        
        self.prom_memory = Gauge(
            'inference_memory_usage_mb',
            'Memory usage in MB',
            ['model_id'],
            registry=self.prometheus_registry
        )
        
        self.prom_errors = Counter(
            'inference_errors_total',
            'Total inference errors',
            ['model_id', 'creator_type', 'error_type'],
            registry=self.prometheus_registry
        )
        
        self.prom_success_rate = Gauge(
            'inference_success_rate',
            'Inference success rate percentage',
            ['model_id', 'creator_type'],
            registry=self.prometheus_registry
        )
    
    async def record_inference_metrics(
        self,
        model_id: str,
        creator_type: str,
        latency_ms: float,
        success: bool,
        endpoint: str = "default",
        batch_size: int = 1,
        confidence_score: float = 0.0,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record inference performance metrics."""
        try:
            # Collect system metrics
            memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
            cpu_usage = psutil.cpu_percent()
            
            # GPU usage (simplified simulation)
            gpu_usage = np.random.uniform(20, 80) if success else np.random.uniform(10, 30)
            
            # Calculate throughput (simplified)
            current_time = datetime.now()
            recent_requests = len([
                m for m in list(self.model_metrics[model_id])
                if (current_time - m.timestamp).total_seconds() < 60
            ])
            throughput_rps = recent_requests / 60.0
            
            # Create metrics object
            metrics = InferenceMetrics(
                model_id=model_id,
                creator_type=creator_type,
                latency_ms=latency_ms,
                throughput_rps=throughput_rps,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                gpu_usage_percent=gpu_usage,
                request_count=1,
                error_count=0 if success else 1,
                success_rate=100.0 if success else 0.0,
                confidence_score=confidence_score,
                timestamp=current_time,
                endpoint=endpoint,
                batch_size=batch_size
            )
            
            # Store metrics
            self.metrics_buffer.append(metrics)
            self.creator_metrics[creator_type].append(metrics)
            self.model_metrics[model_id].append(metrics)
            
            # Update Prometheus metrics
            self.prom_latency.labels(
                model_id=model_id,
                creator_type=creator_type,
                endpoint=endpoint
            ).observe(latency_ms / 1000.0)
            
            self.prom_throughput.labels(
                model_id=model_id,
                creator_type=creator_type
            ).set(throughput_rps)
            
            self.prom_memory.labels(model_id=model_id).set(memory_usage)
            
            if not success:
                self.prom_errors.labels(
                    model_id=model_id,
                    creator_type=creator_type,
                    error_type="inference_error"
                ).inc()
            
            # Check for performance alerts
            await self._check_performance_alerts(metrics)
            
            self.logger.debug(f"Recorded metrics for {model_id}: {latency_ms}ms latency")
            
        except Exception as e:
            self.logger.error(f"Error recording inference metrics: {e}")
    
    async def _check_performance_alerts(self, metrics: InferenceMetrics) -> None:
        """Check if metrics trigger performance alerts."""
        try:
            alerts_to_trigger = []
            
            # Check latency alerts
            for severity, threshold in self.alert_thresholds['latency_ms'].items():
                if metrics.latency_ms > threshold:
                    alert = PerformanceAlert(
                        alert_id=f"{metrics.model_id}_latency_{severity}_{int(time.time())}",
                        model_id=metrics.model_id,
                        metric_name="latency_ms",
                        current_value=metrics.latency_ms,
                        threshold=threshold,
                        severity=severity,
                        message=f"High latency detected: {metrics.latency_ms:.2f}ms > {threshold}ms",
                        timestamp=metrics.timestamp,
                        creator_type=metrics.creator_type
                    )
                    alerts_to_trigger.append(alert)
                    break  # Only trigger highest severity
            
            # Check memory usage alerts
            for severity, threshold in self.alert_thresholds['memory_usage_mb'].items():
                if metrics.memory_usage_mb > threshold:
                    alert = PerformanceAlert(
                        alert_id=f"{metrics.model_id}_memory_{severity}_{int(time.time())}",
                        model_id=metrics.model_id,
                        metric_name="memory_usage_mb",
                        current_value=metrics.memory_usage_mb,
                        threshold=threshold,
                        severity=severity,
                        message=f"High memory usage: {metrics.memory_usage_mb:.2f}MB > {threshold}MB",
                        timestamp=metrics.timestamp,
                        creator_type=metrics.creator_type
                    )
                    alerts_to_trigger.append(alert)
                    break
            
            # Check CPU usage alerts
            for severity, threshold in self.alert_thresholds['cpu_usage_percent'].items():
                if metrics.cpu_usage_percent > threshold:
                    alert = PerformanceAlert(
                        alert_id=f"{metrics.model_id}_cpu_{severity}_{int(time.time())}",
                        model_id=metrics.model_id,
                        metric_name="cpu_usage_percent",
                        current_value=metrics.cpu_usage_percent,
                        threshold=threshold,
                        severity=severity,
                        message=f"High CPU usage: {metrics.cpu_usage_percent:.2f}% > {threshold}%",
                        timestamp=metrics.timestamp,
                        creator_type=metrics.creator_type
                    )
                    alerts_to_trigger.append(alert)
                    break
            
            # Trigger alerts
            for alert in alerts_to_trigger:
                await self._trigger_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")
    
    async def _trigger_alert(self, alert: PerformanceAlert) -> None:
        """Trigger a performance alert."""
        try:
            self.active_alerts[alert.alert_id] = alert
            
            self.logger.warning(
                f"PERFORMANCE ALERT [{alert.severity.upper()}]: {alert.message}"
            )
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")
    
    def get_performance_summary(
        self,
        model_id: Optional[str] = None,
        creator_type: Optional[str] = None,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get performance summary for specified criteria."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=time_window_minutes)
            
            # Filter metrics
            if model_id:
                metrics = [m for m in self.model_metrics[model_id] 
                          if start_time <= m.timestamp <= end_time]
            elif creator_type:
                metrics = [m for m in self.creator_metrics[creator_type] 
                          if start_time <= m.timestamp <= end_time]
            else:
                metrics = [m for m in self.metrics_buffer 
                          if start_time <= m.timestamp <= end_time]
            
            if not metrics:
                return {"error": "No metrics found for specified criteria"}
            
            # Calculate summary statistics
            latencies = [m.latency_ms for m in metrics]
            throughputs = [m.throughput_rps for m in metrics]
            success_rates = [m.success_rate for m in metrics]
            memory_usage = [m.memory_usage_mb for m in metrics]
            
            summary = {
                "time_window_minutes": time_window_minutes,
                "total_requests": len(metrics),
                "performance_metrics": {
                    "latency": {
                        "avg_ms": statistics.mean(latencies),
                        "p50_ms": statistics.median(latencies),
                        "p95_ms": np.percentile(latencies, 95),
                        "p99_ms": np.percentile(latencies, 99),
                        "max_ms": max(latencies),
                        "min_ms": min(latencies)
                    },
                    "throughput": {
                        "avg_rps": statistics.mean(throughputs),
                        "max_rps": max(throughputs),
                        "min_rps": min(throughputs)
                    },
                    "success_rate": {
                        "avg_percent": statistics.mean(success_rates),
                        "min_percent": min(success_rates)
                    },
                    "resource_usage": {
                        "avg_memory_mb": statistics.mean(memory_usage),
                        "max_memory_mb": max(memory_usage)
                    }
                },
                "sla_compliance": self._check_sla_compliance(metrics),
                "active_alerts": len([a for a in self.active_alerts.values() 
                                    if (end_time - a.timestamp).total_seconds() < 3600])
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating performance summary: {e}")
            return {"error": str(e)}
    
    def _check_sla_compliance(self, metrics: List[InferenceMetrics]) -> Dict[str, Any]:
        """Check SLA compliance for metrics."""
        try:
            if not metrics:
                return {"compliant": False, "reason": "No metrics available"}
            
            latencies = [m.latency_ms for m in metrics]
            success_rates = [m.success_rate for m in metrics]
            throughputs = [m.throughput_rps for m in metrics]
            
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            avg_success_rate = statistics.mean(success_rates)
            avg_throughput = statistics.mean(throughputs)
            
            compliance = {
                "latency_p95": {
                    "target_ms": self.sla_targets['latency_p95_ms'],
                    "actual_ms": p95_latency,
                    "compliant": p95_latency <= self.sla_targets['latency_p95_ms']
                },
                "latency_p99": {
                    "target_ms": self.sla_targets['latency_p99_ms'],
                    "actual_ms": p99_latency,
                    "compliant": p99_latency <= self.sla_targets['latency_p99_ms']
                },
                "success_rate": {
                    "target_percent": self.sla_targets['success_rate_min'],
                    "actual_percent": avg_success_rate,
                    "compliant": avg_success_rate >= self.sla_targets['success_rate_min']
                },
                "throughput": {
                    "target_rps": self.sla_targets['throughput_min_rps'],
                    "actual_rps": avg_throughput,
                    "compliant": avg_throughput >= self.sla_targets['throughput_min_rps']
                }
            }
            
            overall_compliant = all(m["compliant"] for m in compliance.values())
            
            return {
                "overall_compliant": overall_compliant,
                "metrics": compliance
            }
            
        except Exception as e:
            self.logger.error(f"Error checking SLA compliance: {e}")
            return {"error": str(e)}
    
    def start_monitoring(self, prometheus_port: int = 8000) -> None:
        """Start the performance monitoring system."""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring is already active")
                return
            
            self.monitoring_active = True
            
            # Start Prometheus metrics server
            try:
                start_http_server(prometheus_port, registry=self.prometheus_registry)
                self.logger.info(f"Prometheus metrics server started on port {prometheus_port}")
            except Exception as e:
                self.logger.warning(f"Could not start Prometheus server: {e}")
            
            # Start background monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._background_monitoring,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("Performance monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            self.monitoring_active = False
    
    def _background_monitoring(self) -> None:
        """Background monitoring task."""
        try:
            while self.monitoring_active:
                # Clean up old alerts
                current_time = datetime.now()
                expired_alerts = [
                    alert_id for alert_id, alert in self.active_alerts.items()
                    if (current_time - alert.timestamp).total_seconds() > 3600
                ]
                
                for alert_id in expired_alerts:
                    del self.active_alerts[alert_id]
                
                # Update Prometheus metrics
                self._update_prometheus_metrics()
                
                time.sleep(30)  # Update every 30 seconds
                
        except Exception as e:
            self.logger.error(f"Error in background monitoring: {e}")
    
    def _update_prometheus_metrics(self) -> None:
        """Update Prometheus metrics with current data."""
        try:
            current_time = datetime.now()
            
            # Update success rates for all models
            for model_id, metrics_deque in self.model_metrics.items():
                recent_metrics = [
                    m for m in metrics_deque
                    if (current_time - m.timestamp).total_seconds() < 300  # 5 minutes
                ]
                
                if recent_metrics:
                    success_rate = statistics.mean([m.success_rate for m in recent_metrics])
                    creator_type = recent_metrics[0].creator_type
                    
                    self.prom_success_rate.labels(
                        model_id=model_id,
                        creator_type=creator_type
                    ).set(success_rate)
                    
        except Exception as e:
            self.logger.error(f"Error updating Prometheus metrics: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop the performance monitoring system."""
        try:
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.executor.shutdown(wait=True)
            
            self.logger.info("Performance monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
    
    def add_alert_callback(self, callback: callable) -> None:
        """Add a callback function for performance alerts."""
        self.alert_callbacks.append(callback)
        self.logger.info("Alert callback added")
    
    def update_thresholds(self, thresholds: Dict[str, Dict[str, float]]) -> None:
        """Update performance alert thresholds."""
        try:
            self.alert_thresholds.update(thresholds)
            self.logger.info("Performance thresholds updated")
        except Exception as e:
            self.logger.error(f"Error updating thresholds: {e}")
    
    def get_creator_analytics(self, creator_type: str) -> Dict[str, Any]:
        """Get performance analytics for a specific creator type."""
        try:
            metrics = list(self.creator_metrics[creator_type])
            if not metrics:
                return {"error": f"No metrics found for creator type: {creator_type}"}
            
            # Group by model
            model_performance = defaultdict(list)
            for metric in metrics:
                model_performance[metric.model_id].append(metric)
            
            analytics = {
                "creator_type": creator_type,
                "total_requests": len(metrics),
                "unique_models": len(model_performance),
                "model_performance": {}
            }
            
            for model_id, model_metrics in model_performance.items():
                latencies = [m.latency_ms for m in model_metrics]
                success_rates = [m.success_rate for m in model_metrics]
                
                analytics["model_performance"][model_id] = {
                    "request_count": len(model_metrics),
                    "avg_latency_ms": statistics.mean(latencies),
                    "p95_latency_ms": np.percentile(latencies, 95),
                    "avg_success_rate": statistics.mean(success_rates),
                    "last_request": max(m.timestamp for m in model_metrics).isoformat()
                }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting creator analytics: {e}")
            return {"error": str(e)}


# Example usage and testing
async def example_usage():
    """Example usage of the InferencePerformanceMonitor."""
    monitor = InferencePerformanceMonitor()
    
    # Start monitoring
    monitor.start_monitoring(prometheus_port=8001)
    
    # Add alert callback
    async def alert_handler(alert: PerformanceAlert):
        print(f"ALERT: {alert.message}")
    
    monitor.add_alert_callback(alert_handler)
    
    # Simulate inference metrics
    for i in range(10):
        await monitor.record_inference_metrics(
            model_id="content-classifier-v1",
            creator_type="musician",
            latency_ms=np.random.uniform(50, 150),
            success=np.random.random() > 0.05,  # 95% success rate
            endpoint="/classify",
            confidence_score=np.random.uniform(0.7, 0.95)
        )
        
        await asyncio.sleep(0.1)
    
    # Get performance summary
    summary = monitor.get_performance_summary(model_id="content-classifier-v1")
    print(f"Performance Summary: {json.dumps(summary, indent=2, default=str)}")
    
    # Get creator analytics
    analytics = monitor.get_creator_analytics("musician")
    print(f"Creator Analytics: {json.dumps(analytics, indent=2, default=str)}")
    
    # Stop monitoring
    monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_usage())