"""
Performance Monitor - ML Model Performance Tracking

Advanced performance monitoring system for ML models in the IA Influencer platform.
Tracks real-time performance, resource usage, business metrics, and system health.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import deque, defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

# Performance monitoring dependencies
import torch
import numpy as np
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ACCURACY = "accuracy"
    RESOURCE_USAGE = "resource_usage"
    ERROR_RATE = "error_rate"
    BUSINESS_KPI = "business_kpi"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""


@dataclass
class Alert:
    """Performance alert data structure"""
    id: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold_value: float
    actual_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class ModelPerformanceReport:
    """Comprehensive model performance report"""
    model_id: str
    model_name: str
    report_period_start: datetime
    report_period_end: datetime
    
    # Performance metrics
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    
    # Quality metrics
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    # Resource metrics
    avg_memory_usage_mb: float = 0.0
    peak_memory_usage_mb: float = 0.0
    avg_cpu_usage: float = 0.0
    avg_gpu_usage: float = 0.0
    
    # Business metrics for IA Influencer platform
    content_processed: int = 0
    successful_analyses: int = 0
    creator_satisfaction_score: float = 0.0
    seo_improvements_count: int = 0
    collaboration_matches: int = 0
    revenue_impact: float = 0.0
    
    # Error tracking
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0
    
    # Alert summary
    alerts_triggered: int = 0
    critical_alerts: int = 0
    
    # Platform-specific metrics
    platform_performance: Dict[str, float] = field(default_factory=dict)
    content_type_performance: Dict[str, float] = field(default_factory=dict)
    creator_type_effectiveness: Dict[str, float] = field(default_factory=dict)


class MLPerformanceMonitor:
    """
    Advanced ML model performance monitoring system
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_storage: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: List[Alert] = []
        self.active_monitors: Dict[str, bool] = {}
        
        # Performance thresholds
        self.thresholds = self.config.get('thresholds', {
            'max_latency_ms': 1000,
            'min_throughput_rps': 10,
            'max_error_rate': 0.05,
            'max_memory_usage_mb': 2048,
            'max_cpu_usage': 0.8,
            'min_accuracy': 0.7
        })
        
        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Redis connection (if available)
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis.from_url(
                    self.config.get('redis_url', 'redis://localhost:6379/1')
                )
                self.redis_client.ping()
                self.redis_enabled = True
            except:
                self.redis_enabled = False
        else:
            self.redis_enabled = False
        
        # Background monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[Alert], None]] = []
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics if available"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        self.prom_latency = Histogram(
            'ml_model_latency_seconds',
            'Model inference latency',
            ['model_name', 'model_type']
        )
        
        self.prom_throughput = Gauge(
            'ml_model_throughput_rps',
            'Model throughput in requests per second',
            ['model_name', 'model_type']
        )
        
        self.prom_accuracy = Gauge(
            'ml_model_accuracy',
            'Model accuracy score',
            ['model_name', 'model_type']
        )
        
        self.prom_memory = Gauge(
            'ml_model_memory_usage_bytes',
            'Model memory usage',
            ['model_name', 'model_type']
        )
        
        self.prom_requests_total = Counter(
            'ml_model_requests_total',
            'Total model requests',
            ['model_name', 'model_type', 'status']
        )
    
    async def start_monitoring(self, models: List[Dict[str, Any]]):
        """Start performance monitoring for specified models"""
        self.monitoring_active = True
        
        # Start background monitoring thread
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(
                target=self._background_monitoring_loop,
                args=(models,),
                daemon=True
            )
            self.monitoring_thread.start()
        
        # Start Prometheus metrics server if available
        if PROMETHEUS_AVAILABLE and self.config.get('prometheus_port'):
            try:
                start_http_server(self.config['prometheus_port'])
                logger.info(f"Prometheus metrics server started on port {self.config['prometheus_port']}")
            except Exception as e:
                logger.warning(f"Failed to start Prometheus server: {e}")
        
        logger.info(f"Performance monitoring started for {len(models)} models")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    async def record_inference_metrics(self, model_id: str, model_name: str, 
                                     latency_ms: float, success: bool = True,
                                     custom_metrics: Optional[Dict[str, float]] = None):
        """Record inference performance metrics"""
        timestamp = datetime.utcnow()
        
        # Store latency metric
        latency_metric = PerformanceMetric(
            name=f"{model_id}_latency",
            value=latency_ms,
            metric_type=MetricType.LATENCY,
            timestamp=timestamp,
            labels={"model_name": model_name, "model_id": model_id},
            unit="ms",
            description="Model inference latency"
        )
        self.metrics_storage[f"{model_id}_latency"].append(latency_metric)
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.prom_latency.labels(
                model_name=model_name,
                model_type=self._get_model_type(model_id)
            ).observe(latency_ms / 1000)  # Convert to seconds
            
            self.prom_requests_total.labels(
                model_name=model_name,
                model_type=self._get_model_type(model_id),
                status="success" if success else "error"
            ).inc()
        
        # Store custom metrics
        if custom_metrics:
            for metric_name, value in custom_metrics.items():
                custom_metric = PerformanceMetric(
                    name=f"{model_id}_{metric_name}",
                    value=value,
                    metric_type=MetricType.BUSINESS_KPI,
                    timestamp=timestamp,
                    labels={"model_name": model_name, "model_id": model_id}
                )
                self.metrics_storage[f"{model_id}_{metric_name}"].append(custom_metric)
        
        # Check thresholds and trigger alerts
        await self._check_thresholds(model_id, model_name, latency_ms, success)
        
        # Store in Redis if available
        if self.redis_enabled:
            try:
                metric_data = {
                    'model_id': model_id,
                    'model_name': model_name,
                    'latency_ms': latency_ms,
                    'success': success,
                    'timestamp': timestamp.isoformat()
                }
                if custom_metrics:
                    metric_data.update(custom_metrics)
                
                self.redis_client.lpush(
                    f"ml_metrics:{model_id}",
                    json.dumps(metric_data)
                )
                self.redis_client.expire(f"ml_metrics:{model_id}", 86400)  # 24 hours
                
            except Exception as e:
                logger.warning(f"Failed to store metrics in Redis: {e}")
    
    async def record_resource_metrics(self, model_id: str, model_name: str,
                                    memory_usage_mb: float, cpu_usage: float,
                                    gpu_usage: Optional[float] = None):
        """Record resource usage metrics"""
        timestamp = datetime.utcnow()
        
        # Memory usage metric
        memory_metric = PerformanceMetric(
            name=f"{model_id}_memory_usage",
            value=memory_usage_mb,
            metric_type=MetricType.RESOURCE_USAGE,
            timestamp=timestamp,
            labels={"model_name": model_name, "model_id": model_id},
            unit="MB",
            description="Model memory usage"
        )
        self.metrics_storage[f"{model_id}_memory_usage"].append(memory_metric)
        
        # CPU usage metric
        cpu_metric = PerformanceMetric(
            name=f"{model_id}_cpu_usage",
            value=cpu_usage,
            metric_type=MetricType.RESOURCE_USAGE,
            timestamp=timestamp,
            labels={"model_name": model_name, "model_id": model_id},
            unit="%",
            description="Model CPU usage"
        )
        self.metrics_storage[f"{model_id}_cpu_usage"].append(cpu_metric)
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.prom_memory.labels(
                model_name=model_name,
                model_type=self._get_model_type(model_id)
            ).set(memory_usage_mb * 1024 * 1024)  # Convert to bytes
        
        # Check resource thresholds
        if memory_usage_mb > self.thresholds['max_memory_usage_mb']:
            await self._create_alert(
                model_id, model_name,
                AlertLevel.WARNING,
                f"High memory usage: {memory_usage_mb:.1f} MB",
                "memory_usage", self.thresholds['max_memory_usage_mb'], memory_usage_mb
            )
        
        if cpu_usage > self.thresholds['max_cpu_usage']:
            await self._create_alert(
                model_id, model_name,
                AlertLevel.WARNING,
                f"High CPU usage: {cpu_usage:.1f}%",
                "cpu_usage", self.thresholds['max_cpu_usage'], cpu_usage
            )
    
    async def record_business_metrics(self, model_id: str, model_name: str,
                                    content_processed: int = 0,
                                    successful_matches: int = 0,
                                    creator_satisfaction: float = 0.0,
                                    seo_improvements: int = 0,
                                    revenue_impact: float = 0.0):
        """Record business-specific metrics for IA Influencer platform"""
        timestamp = datetime.utcnow()
        
        business_metrics = {
            'content_processed': content_processed,
            'successful_matches': successful_matches,
            'creator_satisfaction': creator_satisfaction,
            'seo_improvements': seo_improvements,
            'revenue_impact': revenue_impact
        }
        
        for metric_name, value in business_metrics.items():
            if value > 0 or metric_name == 'creator_satisfaction':  # Always record satisfaction
                metric = PerformanceMetric(
                    name=f"{model_id}_{metric_name}",
                    value=value,
                    metric_type=MetricType.BUSINESS_KPI,
                    timestamp=timestamp,
                    labels={"model_name": model_name, "model_id": model_id}
                )
                self.metrics_storage[f"{model_id}_{metric_name}"].append(metric)
        
        # Check business metric thresholds
        if creator_satisfaction < 0.6 and creator_satisfaction > 0:
            await self._create_alert(
                model_id, model_name,
                AlertLevel.WARNING,
                f"Low creator satisfaction: {creator_satisfaction:.2f}",
                "creator_satisfaction", 0.6, creator_satisfaction
            )
    
    async def get_model_performance_report(self, model_id: str, 
                                         hours_back: int = 24) -> ModelPerformanceReport:
        """Generate comprehensive performance report for a model"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Initialize report
        report = ModelPerformanceReport(
            model_id=model_id,
            model_name=self._get_model_name(model_id),
            report_period_start=start_time,
            report_period_end=end_time
        )
        
        # Calculate performance metrics
        latency_metrics = self._get_metrics_in_timeframe(
            f"{model_id}_latency", start_time, end_time
        )
        
        if latency_metrics:
            latencies = [m.value for m in latency_metrics]
            report.avg_latency_ms = statistics.mean(latencies)
            report.p95_latency_ms = np.percentile(latencies, 95)
            report.p99_latency_ms = np.percentile(latencies, 99)
            
            # Calculate throughput (requests per hour)
            time_span_hours = (end_time - start_time).total_seconds() / 3600
            report.throughput_rps = len(latencies) / (time_span_hours * 3600)
        
        # Calculate resource metrics
        memory_metrics = self._get_metrics_in_timeframe(
            f"{model_id}_memory_usage", start_time, end_time
        )
        if memory_metrics:
            memory_values = [m.value for m in memory_metrics]
            report.avg_memory_usage_mb = statistics.mean(memory_values)
            report.peak_memory_usage_mb = max(memory_values)
        
        cpu_metrics = self._get_metrics_in_timeframe(
            f"{model_id}_cpu_usage", start_time, end_time
        )
        if cpu_metrics:
            report.avg_cpu_usage = statistics.mean([m.value for m in cpu_metrics])
        
        # Calculate business metrics
        business_metric_names = [
            'content_processed', 'successful_matches', 'creator_satisfaction',
            'seo_improvements', 'revenue_impact'
        ]
        
        for metric_name in business_metric_names:
            metrics = self._get_metrics_in_timeframe(
                f"{model_id}_{metric_name}", start_time, end_time
            )
            if metrics:
                if metric_name == 'content_processed':
                    report.content_processed = sum(int(m.value) for m in metrics)
                elif metric_name == 'successful_matches':
                    report.collaboration_matches = sum(int(m.value) for m in metrics)
                elif metric_name == 'creator_satisfaction':
                    report.creator_satisfaction_score = statistics.mean([m.value for m in metrics])
                elif metric_name == 'seo_improvements':
                    report.seo_improvements_count = sum(int(m.value) for m in metrics)
                elif metric_name == 'revenue_impact':
                    report.revenue_impact = sum(m.value for m in metrics)
        
        # Calculate success/failure rates
        report.total_requests = len(latency_metrics) if latency_metrics else 0
        report.successful_requests = report.total_requests  # Assume success if latency recorded
        report.failed_requests = 0  # Would need separate error tracking
        report.error_rate = report.failed_requests / max(report.total_requests, 1)
        
        # Count alerts in the time period
        period_alerts = [
            alert for alert in self.alerts
            if start_time <= alert.timestamp <= end_time and model_id in alert.id
        ]
        report.alerts_triggered = len(period_alerts)
        report.critical_alerts = len([a for a in period_alerts if a.level == AlertLevel.CRITICAL])
        
        return report
    
    def _background_monitoring_loop(self, models: List[Dict[str, Any]]):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                for model_info in models:
                    model_id = model_info['id']
                    
                    # Collect system metrics if available
                    if PSUTIL_AVAILABLE:
                        # Get current process metrics
                        process = psutil.Process()
                        memory_mb = process.memory_info().rss / (1024 * 1024)
                        cpu_percent = process.cpu_percent()
                        
                        # Store resource metrics
                        asyncio.run(self.record_resource_metrics(
                            model_id, model_info['name'], memory_mb, cpu_percent
                        ))
                
                # Sleep between monitoring cycles
                time.sleep(self.config.get('monitoring_interval', 60))
                
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                time.sleep(30)  # Shorter sleep on error
    
    def _get_metrics_in_timeframe(self, metric_key: str, 
                                 start_time: datetime, end_time: datetime) -> List[PerformanceMetric]:
        """Get metrics within specified timeframe"""
        metrics = self.metrics_storage.get(metric_key, [])
        return [
            m for m in metrics 
            if start_time <= m.timestamp <= end_time
        ]
    
    async def _check_thresholds(self, model_id: str, model_name: str,
                               latency_ms: float, success: bool):
        """Check performance thresholds and create alerts"""
        if latency_ms > self.thresholds['max_latency_ms']:
            await self._create_alert(
                model_id, model_name,
                AlertLevel.WARNING,
                f"High latency: {latency_ms:.1f} ms",
                "latency", self.thresholds['max_latency_ms'], latency_ms
            )
        
        if not success:
            await self._create_alert(
                model_id, model_name,
                AlertLevel.CRITICAL,
                "Model inference failed",
                "success_rate", 1.0, 0.0
            )
    
    async def _create_alert(self, model_id: str, model_name: str,
                           level: AlertLevel, message: str,
                           metric_name: str, threshold: float, actual: float):
        """Create and handle performance alert"""
        alert_id = f"{model_id}_{metric_name}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            level=level,
            message=message,
            metric_name=metric_name,
            threshold_value=threshold,
            actual_value=actual
        )
        
        self.alerts.append(alert)
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(f"Alert created: {alert.level.value} - {alert.message}")
    
    def _get_model_type(self, model_id: str) -> str:
        """Get model type from model ID (simplified)"""
        # This would normally lookup model type from registry
        if 'content' in model_id.lower():
            return 'content_analysis'
        elif 'recommendation' in model_id.lower():
            return 'recommendation'
        elif 'sentiment' in model_id.lower():
            return 'sentiment_analysis'
        else:
            return 'unknown'
    
    def _get_model_name(self, model_id: str) -> str:
        """Get model name from model ID (simplified)"""
        # This would normally lookup model name from registry
        return model_id.replace('_', ' ').title()
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                break


class InferenceProfiler:
    """
    Detailed profiling of model inference performance
    """
    
    def __init__(self):
        self.profiling_enabled = False
        self.profile_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    async def profile_inference(self, model_id: str, model: torch.nn.Module,
                               input_data: torch.Tensor) -> Dict[str, Any]:
        """Profile model inference with detailed timing"""
        if not self.profiling_enabled:
            return {}
        
        profile_result = {
            'model_id': model_id,
            'input_shape': list(input_data.shape),
            'timestamp': datetime.utcnow().isoformat(),
            'device': str(input_data.device),
            'profiling_data': {}
        }
        
        # Memory before inference
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            memory_before = torch.cuda.memory_allocated()
            profile_result['memory_before_mb'] = memory_before / (1024 * 1024)
        
        # Time inference
        start_time = time.perf_counter()
        
        with torch.no_grad():
            # Warm-up run
            _ = model(input_data)
            
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            
            # Actual profiled run
            inference_start = time.perf_counter()
            output = model(input_data)
            
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            
            inference_end = time.perf_counter()
        
        inference_time = (inference_end - inference_start) * 1000  # Convert to ms
        profile_result['inference_time_ms'] = inference_time
        
        # Memory after inference
        if torch.cuda.is_available():
            memory_after = torch.cuda.memory_allocated()
            profile_result['memory_after_mb'] = memory_after / (1024 * 1024)
            profile_result['memory_increase_mb'] = (memory_after - memory_before) / (1024 * 1024)
        
        # Output analysis
        if isinstance(output, torch.Tensor):
            profile_result['output_shape'] = list(output.shape)
            profile_result['output_dtype'] = str(output.dtype)
        
        # Store profiling data
        self.profile_data[model_id].append(profile_result)
        
        return profile_result
    
    def enable_profiling(self):
        """Enable inference profiling"""
        self.profiling_enabled = True
        logger.info("Inference profiling enabled")
    
    def disable_profiling(self):
        """Disable inference profiling"""
        self.profiling_enabled = False
        logger.info("Inference profiling disabled")
    
    def get_profiling_summary(self, model_id: str) -> Dict[str, Any]:
        """Get profiling summary for a model"""
        if model_id not in self.profile_data:
            return {}
        
        data = self.profile_data[model_id]
        if not data:
            return {}
        
        inference_times = [d['inference_time_ms'] for d in data]
        
        summary = {
            'model_id': model_id,
            'total_profiles': len(data),
            'avg_inference_time_ms': statistics.mean(inference_times),
            'min_inference_time_ms': min(inference_times),
            'max_inference_time_ms': max(inference_times),
            'p95_inference_time_ms': np.percentile(inference_times, 95),
            'p99_inference_time_ms': np.percentile(inference_times, 99)
        }
        
        # Memory statistics (if available)
        memory_increases = [d.get('memory_increase_mb', 0) for d in data if 'memory_increase_mb' in d]
        if memory_increases:
            summary['avg_memory_increase_mb'] = statistics.mean(memory_increases)
            summary['max_memory_increase_mb'] = max(memory_increases)
        
        return summary


class ResourceMonitor:
    """
    System resource monitoring for ML workloads
    """
    
    def __init__(self):
        self.monitoring_active = False
        self.resource_data: List[Dict[str, Any]] = []
    
    async def start_resource_monitoring(self, interval: int = 30):
        """Start continuous resource monitoring"""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - resource monitoring disabled")
            return
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                resource_snapshot = await self._collect_resource_snapshot()
                self.resource_data.append(resource_snapshot)
                
                # Keep only last 1000 snapshots
                if len(self.resource_data) > 1000:
                    self.resource_data.pop(0)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_resource_snapshot(self) -> Dict[str, Any]:
        """Collect current resource usage snapshot"""
        snapshot = {
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if PSUTIL_AVAILABLE:
            # CPU metrics
            snapshot['cpu_percent'] = psutil.cpu_percent(interval=1)
            snapshot['cpu_count'] = psutil.cpu_count()
            snapshot['load_avg'] = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Memory metrics
            memory = psutil.virtual_memory()
            snapshot['memory_total_gb'] = memory.total / (1024**3)
            snapshot['memory_available_gb'] = memory.available / (1024**3)
            snapshot['memory_percent'] = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            snapshot['disk_total_gb'] = disk.total / (1024**3)
            snapshot['disk_free_gb'] = disk.free / (1024**3)
            snapshot['disk_percent'] = (disk.used / disk.total) * 100
        
        # GPU metrics (if CUDA available)
        if torch.cuda.is_available():
            try:
                snapshot['gpu_count'] = torch.cuda.device_count()
                snapshot['gpu_memory_allocated_mb'] = torch.cuda.memory_allocated() / (1024**2)
                snapshot['gpu_memory_reserved_mb'] = torch.cuda.memory_reserved() / (1024**2)
            except Exception as e:
                logger.debug(f"GPU metrics collection failed: {e}")
        
        return snapshot
    
    def stop_resource_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
    
    def get_resource_summary(self, hours_back: int = 1) -> Dict[str, Any]:
        """Get resource usage summary for specified time period"""
        if not self.resource_data:
            return {}
        
        # Filter data for time period
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        recent_data = [
            d for d in self.resource_data
            if datetime.fromisoformat(d['timestamp']) >= cutoff_time
        ]
        
        if not recent_data:
            return {}
        
        # Calculate statistics
        summary = {
            'time_period_hours': hours_back,
            'data_points': len(recent_data)
        }
        
        # CPU statistics
        cpu_values = [d.get('cpu_percent', 0) for d in recent_data]
        if cpu_values:
            summary['cpu_avg'] = statistics.mean(cpu_values)
            summary['cpu_max'] = max(cpu_values)
            summary['cpu_min'] = min(cpu_values)
        
        # Memory statistics
        memory_values = [d.get('memory_percent', 0) for d in recent_data]
        if memory_values:
            summary['memory_avg'] = statistics.mean(memory_values)
            summary['memory_max'] = max(memory_values)
            summary['memory_min'] = min(memory_values)
        
        # GPU statistics (if available)
        gpu_memory_values = [d.get('gpu_memory_allocated_mb', 0) for d in recent_data]
        if any(gpu_memory_values):
            summary['gpu_memory_avg_mb'] = statistics.mean(gpu_memory_values)
            summary['gpu_memory_max_mb'] = max(gpu_memory_values)
        
        return summary
