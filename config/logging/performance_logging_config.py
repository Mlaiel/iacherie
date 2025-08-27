"""
Performance Logging Configuration for IA-Influencer Agent Platform
=================================================================

Advanced performance monitoring and logging for multi-format content processing,
AI inference optimization, and system resource tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import time
import threading
import psutil
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque, defaultdict
import statistics
import logging
import asyncio
from contextlib import contextmanager

import structlog
import numpy as np


class MetricType(str, Enum):
    """Types of performance metrics"""
    # Timing metrics
    RESPONSE_TIME = "response_time"
    PROCESSING_TIME = "processing_time"
    INFERENCE_TIME = "inference_time"
    DATABASE_QUERY_TIME = "database_query_time"
    CACHE_ACCESS_TIME = "cache_access_time"
    
    # Throughput metrics
    REQUESTS_PER_SECOND = "requests_per_second"
    OPERATIONS_PER_SECOND = "operations_per_second"
    FILES_PROCESSED_PER_MINUTE = "files_processed_per_minute"
    
    # Resource metrics
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    GPU_USAGE = "gpu_usage"
    
    # AI/ML specific metrics
    MODEL_ACCURACY = "model_accuracy"
    MODEL_CONFIDENCE = "model_confidence"
    FINGERPRINT_GENERATION_TIME = "fingerprint_generation_time"
    SIMILARITY_SEARCH_TIME = "similarity_search_time"
    
    # Business metrics
    CONTENT_UPLOAD_TIME = "content_upload_time"
    PROTECTION_ACTIVATION_TIME = "protection_activation_time"
    VIOLATION_DETECTION_TIME = "violation_detection_time"
    
    # Queue metrics
    QUEUE_SIZE = "queue_size"
    QUEUE_WAIT_TIME = "queue_wait_time"
    QUEUE_PROCESSING_TIME = "queue_processing_time"
    
    # Error metrics
    ERROR_RATE = "error_rate"
    TIMEOUT_RATE = "timeout_rate"
    RETRY_RATE = "retry_rate"


class PerformanceLevel(str, Enum):
    """Performance alert levels"""
    OPTIMAL = "optimal"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"


@dataclass
class MetricThreshold:
    """Performance metric threshold configuration"""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    unit: str = ""
    comparison: str = "greater"  # greater, less, equal
    enabled: bool = True
    description: str = ""


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    component: str
    operation: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    alert_id: str
    timestamp: datetime
    metric_type: MetricType
    level: PerformanceLevel
    current_value: float
    threshold_value: float
    component: str
    operation: Optional[str] = None
    description: str = ""
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


@dataclass
class ComponentProfile:
    """Performance profile for a system component"""
    name: str
    enabled: bool = True
    metrics: List[MetricType] = field(default_factory=list)
    sampling_interval: float = 1.0  # seconds
    aggregation_window: int = 300  # seconds
    retention_period: int = 3600  # seconds
    custom_thresholds: List[MetricThreshold] = field(default_factory=list)


class PerformanceLoggingConfig:
    """
    Enterprise performance logging configuration for IA-Influencer platform.
    
    Provides comprehensive performance monitoring with adaptive thresholds,
    predictive alerting, and optimization recommendations for multi-format
    content processing and AI operations.
    """
    
    def __init__(
        self,
        enabled: bool = True,
        sampling_interval: float = 1.0,
        aggregation_window: int = 300,
        retention_period: int = 3600,
        enable_system_monitoring: bool = True,
        enable_ai_monitoring: bool = True,
        enable_business_monitoring: bool = True,
        enable_predictive_alerts: bool = True,
        alert_cooldown: int = 300,
        component_profiles: Optional[List[ComponentProfile]] = None,
        metric_thresholds: Optional[List[MetricThreshold]] = None,
        enable_optimization_suggestions: bool = True,
        enable_anomaly_detection: bool = True,
        webhook_urls: Optional[List[str]] = None,
        enable_detailed_tracing: bool = False
    ):
        """
        Initialize performance logging configuration.
        
        Args:
            enabled: Enable performance logging
            sampling_interval: Sampling interval in seconds
            aggregation_window: Aggregation window in seconds
            retention_period: Data retention period in seconds
            enable_system_monitoring: Enable system resource monitoring
            enable_ai_monitoring: Enable AI/ML performance monitoring
            enable_business_monitoring: Enable business metrics monitoring
            enable_predictive_alerts: Enable predictive alerting
            alert_cooldown: Cooldown period between alerts
            component_profiles: Component-specific performance profiles
            metric_thresholds: Performance thresholds
            enable_optimization_suggestions: Enable optimization suggestions
            enable_anomaly_detection: Enable anomaly detection
            webhook_urls: Webhook URLs for alerts
            enable_detailed_tracing: Enable detailed performance tracing
        """
        self.enabled = enabled
        self.sampling_interval = sampling_interval
        self.aggregation_window = aggregation_window
        self.retention_period = retention_period
        self.enable_system_monitoring = enable_system_monitoring
        self.enable_ai_monitoring = enable_ai_monitoring
        self.enable_business_monitoring = enable_business_monitoring
        self.enable_predictive_alerts = enable_predictive_alerts
        self.alert_cooldown = alert_cooldown
        self.enable_optimization_suggestions = enable_optimization_suggestions
        self.enable_anomaly_detection = enable_anomaly_detection
        self.webhook_urls = webhook_urls or []
        self.enable_detailed_tracing = enable_detailed_tracing
        
        # Initialize component profiles
        self.component_profiles = {
            profile.name: profile for profile in (component_profiles or self._create_default_profiles())
        }
        
        # Initialize thresholds
        self.metric_thresholds = {
            threshold.metric_type: threshold for threshold in (metric_thresholds or self._create_default_thresholds())
        }
        
        # Data storage
        self._metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=int(retention_period / sampling_interval)))
        self._aggregated_metrics: Dict[str, Dict] = defaultdict(dict)
        self._active_alerts: Dict[str, PerformanceAlert] = {}
        self._alert_history: deque = deque(maxlen=1000)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'total_metrics': 0,
            'active_alerts': 0,
            'resolved_alerts': 0,
            'components_monitored': len(self.component_profiles),
            'last_collection': None
        }
        
        # Initialize monitoring
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        
        # Initialize logger
        self._performance_logger = structlog.get_logger("ia_influencer_performance")
        
        # GPU monitoring (if available)
        self._gpu_available = self._check_gpu_availability()
        
        # Start monitoring if enabled
        if self.enabled:
            self.start_monitoring()
    
    def _create_default_profiles(self) -> List[ComponentProfile]:
        """Create default component profiles"""
        return [
            ComponentProfile(
                name="api_gateway",
                metrics=[
                    MetricType.RESPONSE_TIME,
                    MetricType.REQUESTS_PER_SECOND,
                    MetricType.ERROR_RATE,
                    MetricType.CPU_USAGE,
                    MetricType.MEMORY_USAGE
                ],
                sampling_interval=1.0
            ),
            ComponentProfile(
                name="ai_engine",
                metrics=[
                    MetricType.INFERENCE_TIME,
                    MetricType.MODEL_CONFIDENCE,
                    MetricType.GPU_USAGE,
                    MetricType.MEMORY_USAGE
                ],
                sampling_interval=2.0
            ),
            ComponentProfile(
                name="content_protection",
                metrics=[
                    MetricType.FINGERPRINT_GENERATION_TIME,
                    MetricType.SIMILARITY_SEARCH_TIME,
                    MetricType.VIOLATION_DETECTION_TIME,
                    MetricType.PROCESSING_TIME
                ],
                sampling_interval=1.0
            ),
            ComponentProfile(
                name="database",
                metrics=[
                    MetricType.DATABASE_QUERY_TIME,
                    MetricType.CPU_USAGE,
                    MetricType.MEMORY_USAGE,
                    MetricType.DISK_USAGE
                ],
                sampling_interval=5.0
            ),
            ComponentProfile(
                name="cache_layer",
                metrics=[
                    MetricType.CACHE_ACCESS_TIME,
                    MetricType.MEMORY_USAGE,
                    MetricType.CPU_USAGE
                ],
                sampling_interval=2.0
            ),
            ComponentProfile(
                name="queue_system",
                metrics=[
                    MetricType.QUEUE_SIZE,
                    MetricType.QUEUE_WAIT_TIME,
                    MetricType.QUEUE_PROCESSING_TIME,
                    MetricType.OPERATIONS_PER_SECOND
                ],
                sampling_interval=1.0
            )
        ]
    
    def _create_default_thresholds(self) -> List[MetricThreshold]:
        """Create default performance thresholds"""
        return [
            # Response time thresholds
            MetricThreshold(
                metric_type=MetricType.RESPONSE_TIME,
                warning_threshold=1000.0,  # 1 second
                critical_threshold=3000.0,  # 3 seconds
                unit="ms",
                description="API response time threshold"
            ),
            
            # CPU usage thresholds
            MetricThreshold(
                metric_type=MetricType.CPU_USAGE,
                warning_threshold=70.0,
                critical_threshold=90.0,
                unit="%",
                description="CPU usage threshold"
            ),
            
            # Memory usage thresholds
            MetricThreshold(
                metric_type=MetricType.MEMORY_USAGE,
                warning_threshold=80.0,
                critical_threshold=95.0,
                unit="%",
                description="Memory usage threshold"
            ),
            
            # AI inference time thresholds
            MetricThreshold(
                metric_type=MetricType.INFERENCE_TIME,
                warning_threshold=5000.0,  # 5 seconds
                critical_threshold=15000.0,  # 15 seconds
                unit="ms",
                description="AI inference time threshold"
            ),
            
            # Fingerprint generation thresholds
            MetricThreshold(
                metric_type=MetricType.FINGERPRINT_GENERATION_TIME,
                warning_threshold=2000.0,  # 2 seconds
                critical_threshold=10000.0,  # 10 seconds
                unit="ms",
                description="Content fingerprint generation time"
            ),
            
            # Error rate thresholds
            MetricThreshold(
                metric_type=MetricType.ERROR_RATE,
                warning_threshold=5.0,  # 5%
                critical_threshold=15.0,  # 15%
                unit="%",
                description="Error rate threshold"
            ),
            
            # Queue size thresholds
            MetricThreshold(
                metric_type=MetricType.QUEUE_SIZE,
                warning_threshold=1000.0,
                critical_threshold=5000.0,
                unit="items",
                description="Queue size threshold"
            ),
            
            # Database query time thresholds
            MetricThreshold(
                metric_type=MetricType.DATABASE_QUERY_TIME,
                warning_threshold=500.0,  # 500ms
                critical_threshold=2000.0,  # 2 seconds
                unit="ms",
                description="Database query time threshold"
            )
        ]
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU monitoring is available"""
        try:
            import GPUtil
            return len(GPUtil.getGPUs()) > 0
        except ImportError:
            return False
    
    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            daemon=True
        )
        self._monitoring_thread.start()
        
        logging.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        if self._monitoring_thread:
            self._stop_event.set()
            self._monitoring_thread.join(timeout=30)
        
        logging.info("Performance monitoring stopped")
    
    def _monitoring_worker(self) -> None:
        """Background monitoring worker"""
        while not self._stop_event.is_set():
            try:
                start_time = time.time()
                
                # Collect metrics from all enabled components
                for profile in self.component_profiles.values():
                    if profile.enabled:
                        self._collect_component_metrics(profile)
                
                # Aggregate metrics
                self._aggregate_metrics()
                
                # Check thresholds and generate alerts
                self._check_thresholds()
                
                # Update statistics
                with self._lock:
                    self._stats['last_collection'] = datetime.now(timezone.utc)
                
                # Sleep for remaining time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.sampling_interval - elapsed)
                
                if self._stop_event.wait(sleep_time):
                    break
                    
            except Exception as e:
                logging.error(f"Error in performance monitoring worker: {e}")
                time.sleep(self.sampling_interval)
    
    def _collect_component_metrics(self, profile: ComponentProfile) -> None:
        """Collect metrics for a specific component"""
        timestamp = datetime.now(timezone.utc)
        
        for metric_type in profile.metrics:
            try:
                value = self._collect_metric_value(metric_type, profile.name)
                if value is not None:
                    metric = PerformanceMetric(
                        metric_type=metric_type,
                        value=value,
                        unit=self._get_metric_unit(metric_type),
                        timestamp=timestamp,
                        component=profile.name
                    )
                    
                    self._store_metric(metric)
                    self._log_metric(metric)
                    
            except Exception as e:
                logging.error(f"Failed to collect metric {metric_type} for {profile.name}: {e}")
    
    def _collect_metric_value(self, metric_type: MetricType, component: str) -> Optional[float]:
        """Collect value for a specific metric type"""
        if metric_type == MetricType.CPU_USAGE:
            return psutil.cpu_percent(interval=None)
        
        elif metric_type == MetricType.MEMORY_USAGE:
            memory = psutil.virtual_memory()
            return memory.percent
        
        elif metric_type == MetricType.DISK_USAGE:
            disk = psutil.disk_usage('/')
            return (disk.used / disk.total) * 100
        
        elif metric_type == MetricType.NETWORK_IO:
            net_io = psutil.net_io_counters()
            return net_io.bytes_sent + net_io.bytes_recv
        
        elif metric_type == MetricType.GPU_USAGE and self._gpu_available:
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].load * 100
            except Exception:
                pass
            return None
        
        elif metric_type == MetricType.QUEUE_SIZE:
            # This would integrate with actual queue systems (Redis, Celery, etc.)
            return self._get_queue_size(component)
        
        # For timing metrics, we need to track them during operations
        # These are typically logged via the record_performance_metric method
        else:
            return self._get_cached_metric_value(metric_type, component)
    
    def _get_metric_unit(self, metric_type: MetricType) -> str:
        """Get unit for metric type"""
        units = {
            MetricType.RESPONSE_TIME: "ms",
            MetricType.PROCESSING_TIME: "ms",
            MetricType.INFERENCE_TIME: "ms",
            MetricType.DATABASE_QUERY_TIME: "ms",
            MetricType.CACHE_ACCESS_TIME: "ms",
            MetricType.FINGERPRINT_GENERATION_TIME: "ms",
            MetricType.SIMILARITY_SEARCH_TIME: "ms",
            MetricType.CONTENT_UPLOAD_TIME: "ms",
            MetricType.PROTECTION_ACTIVATION_TIME: "ms",
            MetricType.VIOLATION_DETECTION_TIME: "ms",
            MetricType.QUEUE_WAIT_TIME: "ms",
            MetricType.QUEUE_PROCESSING_TIME: "ms",
            
            MetricType.REQUESTS_PER_SECOND: "req/s",
            MetricType.OPERATIONS_PER_SECOND: "ops/s",
            MetricType.FILES_PROCESSED_PER_MINUTE: "files/min",
            
            MetricType.CPU_USAGE: "%",
            MetricType.MEMORY_USAGE: "%",
            MetricType.DISK_USAGE: "%",
            MetricType.GPU_USAGE: "%",
            MetricType.ERROR_RATE: "%",
            MetricType.TIMEOUT_RATE: "%",
            MetricType.RETRY_RATE: "%",
            
            MetricType.MODEL_ACCURACY: "score",
            MetricType.MODEL_CONFIDENCE: "score",
            
            MetricType.NETWORK_IO: "bytes",
            MetricType.QUEUE_SIZE: "items"
        }
        return units.get(metric_type, "")
    
    def _get_queue_size(self, component: str) -> Optional[float]:
        """Get queue size for component (placeholder implementation)"""
        # This would integrate with actual queue systems
        # For now, return a simulated value
        return 0.0
    
    def _get_cached_metric_value(self, metric_type: MetricType, component: str) -> Optional[float]:
        """Get cached metric value from recent measurements"""
        key = f"{component}_{metric_type.value}"
        with self._lock:
            if key in self._metrics_buffer:
                metrics = list(self._metrics_buffer[key])
                if metrics:
                    # Return average of recent values
                    values = [m.value for m in metrics[-10:]]  # Last 10 values
                    return statistics.mean(values)
        return None
    
    def _store_metric(self, metric: PerformanceMetric) -> None:
        """Store metric in buffer"""
        key = f"{metric.component}_{metric.metric_type.value}"
        with self._lock:
            self._metrics_buffer[key].append(metric)
            self._stats['total_metrics'] += 1
    
    def _log_metric(self, metric: PerformanceMetric) -> None:
        """Log performance metric"""
        if self.enable_detailed_tracing or metric.value > self._get_warning_threshold(metric.metric_type):
            self._performance_logger.info(
                "Performance metric collected",
                metric_type=metric.metric_type.value,
                value=metric.value,
                unit=metric.unit,
                component=metric.component,
                operation=metric.operation,
                timestamp=metric.timestamp.isoformat(),
                **metric.context,
                **metric.tags
            )
    
    def _aggregate_metrics(self) -> None:
        """Aggregate metrics over time windows"""
        current_time = datetime.now(timezone.utc)
        
        with self._lock:
            for key, metrics in self._metrics_buffer.items():
                if not metrics:
                    continue
                
                # Filter metrics within aggregation window
                cutoff_time = current_time - timedelta(seconds=self.aggregation_window)
                recent_metrics = [m for m in metrics if m.timestamp > cutoff_time]
                
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    
                    # Calculate aggregated statistics
                    self._aggregated_metrics[key] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': statistics.mean(values),
                        'median': statistics.median(values),
                        'std': statistics.stdev(values) if len(values) > 1 else 0,
                        'p95': np.percentile(values, 95) if len(values) > 1 else values[0],
                        'p99': np.percentile(values, 99) if len(values) > 1 else values[0],
                        'timestamp': current_time
                    }
    
    def _check_thresholds(self) -> None:
        """Check metric thresholds and generate alerts"""
        current_time = datetime.now(timezone.utc)
        
        with self._lock:
            for key, aggregated in self._aggregated_metrics.items():
                component, metric_type_str = key.rsplit('_', 1)
                metric_type = MetricType(metric_type_str)
                
                if metric_type in self.metric_thresholds:
                    threshold = self.metric_thresholds[metric_type]
                    if not threshold.enabled:
                        continue
                    
                    current_value = aggregated['mean']
                    alert_level = self._evaluate_threshold(current_value, threshold)
                    
                    if alert_level and alert_level != PerformanceLevel.OPTIMAL:
                        alert_key = f"{component}_{metric_type.value}_{alert_level.value}"
                        
                        # Check if alert already exists or is in cooldown
                        if not self._is_alert_in_cooldown(alert_key):
                            alert = self._create_performance_alert(
                                metric_type, alert_level, current_value, threshold, component
                            )
                            self._handle_performance_alert(alert)
    
    def _evaluate_threshold(self, value: float, threshold: MetricThreshold) -> Optional[PerformanceLevel]:
        """Evaluate metric value against threshold"""
        if threshold.comparison == "greater":
            if value >= threshold.critical_threshold:
                return PerformanceLevel.CRITICAL
            elif value >= threshold.warning_threshold:
                return PerformanceLevel.WARNING
            else:
                return PerformanceLevel.OPTIMAL
        elif threshold.comparison == "less":
            if value <= threshold.critical_threshold:
                return PerformanceLevel.CRITICAL
            elif value <= threshold.warning_threshold:
                return PerformanceLevel.WARNING
            else:
                return PerformanceLevel.OPTIMAL
        
        return PerformanceLevel.OPTIMAL
    
    def _get_warning_threshold(self, metric_type: MetricType) -> float:
        """Get warning threshold for metric type"""
        if metric_type in self.metric_thresholds:
            return self.metric_thresholds[metric_type].warning_threshold
        return float('inf')
    
    def _is_alert_in_cooldown(self, alert_key: str) -> bool:
        """Check if alert is in cooldown period"""
        if alert_key in self._active_alerts:
            alert = self._active_alerts[alert_key]
            if not alert.resolved:
                time_since = (datetime.now(timezone.utc) - alert.timestamp).total_seconds()
                return time_since < self.alert_cooldown
        return False
    
    def _create_performance_alert(
        self,
        metric_type: MetricType,
        level: PerformanceLevel,
        current_value: float,
        threshold: MetricThreshold,
        component: str
    ) -> PerformanceAlert:
        """Create a performance alert"""
        alert_id = f"PERF_{datetime.now().strftime('%Y%m%d%H%M%S')}_{component}_{metric_type.value}"
        
        threshold_value = (
            threshold.critical_threshold if level == PerformanceLevel.CRITICAL 
            else threshold.warning_threshold
        )
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            timestamp=datetime.now(timezone.utc),
            metric_type=metric_type,
            level=level,
            current_value=current_value,
            threshold_value=threshold_value,
            component=component,
            description=f"{metric_type.value} {level.value}: {current_value:.2f}{threshold.unit} (threshold: {threshold_value:.2f}{threshold.unit})"
        )
        
        return alert
    
    def _handle_performance_alert(self, alert: PerformanceAlert) -> None:
        """Handle performance alert"""
        alert_key = f"{alert.component}_{alert.metric_type.value}_{alert.level.value}"
        
        with self._lock:
            self._active_alerts[alert_key] = alert
            self._alert_history.append(alert)
            self._stats['active_alerts'] += 1
        
        # Log alert
        log_level = logging.CRITICAL if alert.level == PerformanceLevel.CRITICAL else logging.WARNING
        self._performance_logger.log(
            log_level,
            "Performance alert triggered",
            alert_id=alert.alert_id,
            metric_type=alert.metric_type.value,
            level=alert.level.value,
            current_value=alert.current_value,
            threshold_value=alert.threshold_value,
            component=alert.component,
            description=alert.description
        )
        
        # Send webhook notifications
        if alert.level in [PerformanceLevel.CRITICAL, PerformanceLevel.WARNING]:
            self._send_alert_webhook(alert)
        
        # Generate optimization suggestions
        if self.enable_optimization_suggestions:
            suggestions = self._generate_optimization_suggestions(alert)
            if suggestions:
                self._performance_logger.info(
                    "Optimization suggestions",
                    alert_id=alert.alert_id,
                    suggestions=suggestions
                )
    
    def _send_alert_webhook(self, alert: PerformanceAlert) -> None:
        """Send webhook notification for performance alert"""
        if not self.webhook_urls:
            return
        
        try:
            import requests
            
            alert_data = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'metric_type': alert.metric_type.value,
                'level': alert.level.value,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'component': alert.component,
                'description': alert.description
            }
            
            for webhook_url in self.webhook_urls:
                try:
                    response = requests.post(
                        webhook_url,
                        json=alert_data,
                        timeout=10,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                except requests.RequestException as e:
                    logging.error(f"Failed to send performance alert webhook to {webhook_url}: {e}")
                    
        except ImportError:
            logging.warning("requests library not available for webhook alerts")
        except Exception as e:
            logging.error(f"Error sending performance alert webhook: {e}")
    
    def _generate_optimization_suggestions(self, alert: PerformanceAlert) -> List[str]:
        """Generate optimization suggestions for performance issues"""
        suggestions = []
        
        if alert.metric_type == MetricType.RESPONSE_TIME:
            suggestions.extend([
                "Consider implementing response caching",
                "Optimize database queries",
                "Add request rate limiting",
                "Scale horizontally with load balancer"
            ])
        
        elif alert.metric_type == MetricType.CPU_USAGE:
            suggestions.extend([
                "Scale CPU resources vertically",
                "Implement CPU-intensive task queuing",
                "Optimize algorithms for better CPU efficiency",
                "Consider horizontal scaling"
            ])
        
        elif alert.metric_type == MetricType.MEMORY_USAGE:
            suggestions.extend([
                "Implement memory cleanup routines",
                "Optimize data structures",
                "Add memory-based caching limits",
                "Scale memory resources"
            ])
        
        elif alert.metric_type == MetricType.INFERENCE_TIME:
            suggestions.extend([
                "Implement model caching",
                "Consider model quantization",
                "Use batch processing for multiple requests",
                "Optimize model architecture"
            ])
        
        elif alert.metric_type == MetricType.DATABASE_QUERY_TIME:
            suggestions.extend([
                "Add database indexes",
                "Implement query result caching",
                "Optimize SQL queries",
                "Consider database sharding"
            ])
        
        elif alert.metric_type == MetricType.QUEUE_SIZE:
            suggestions.extend([
                "Increase worker processes",
                "Implement priority queuing",
                "Add queue overflow handling",
                "Scale queue processing capacity"
            ])
        
        return suggestions
    
    def record_performance_metric(
        self,
        metric_type: MetricType,
        value: float,
        component: str,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a performance metric.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            component: Component name
            operation: Operation name
            context: Additional context
            tags: Metric tags
        """
        if not self.enabled:
            return
        
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=self._get_metric_unit(metric_type),
            timestamp=datetime.now(timezone.utc),
            component=component,
            operation=operation,
            context=context or {},
            tags=tags or {}
        )
        
        self._store_metric(metric)
        self._log_metric(metric)
    
    @contextmanager
    def measure_operation(
        self,
        operation: str,
        component: str,
        metric_type: MetricType = MetricType.PROCESSING_TIME,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Context manager to measure operation performance.
        
        Args:
            operation: Operation name
            component: Component name
            metric_type: Type of timing metric
            context: Additional context
            tags: Metric tags
        """
        start_time = time.time()
        exception_occurred = False
        
        try:
            yield
        except Exception as e:
            exception_occurred = True
            raise
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Add exception context
            final_context = context or {}
            if exception_occurred:
                final_context['exception_occurred'] = True
            
            self.record_performance_metric(
                metric_type=metric_type,
                value=duration_ms,
                component=component,
                operation=operation,
                context=final_context,
                tags=tags
            )
    
    def get_performance_metrics(
        self,
        component: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[PerformanceMetric]:
        """
        Get performance metrics with filtering.
        
        Args:
            component: Filter by component
            metric_type: Filter by metric type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of metrics to return
            
        Returns:
            List of performance metrics
        """
        metrics = []
        
        with self._lock:
            for key, metric_deque in self._metrics_buffer.items():
                for metric in metric_deque:
                    # Apply filters
                    if component and metric.component != component:
                        continue
                    if metric_type and metric.metric_type != metric_type:
                        continue
                    if start_time and metric.timestamp < start_time:
                        continue
                    if end_time and metric.timestamp > end_time:
                        continue
                    
                    metrics.append(metric)
        
        # Sort by timestamp (newest first) and limit
        metrics.sort(key=lambda m: m.timestamp, reverse=True)
        return metrics[:limit]
    
    def get_aggregated_metrics(
        self,
        component: Optional[str] = None,
        metric_type: Optional[MetricType] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get aggregated performance metrics.
        
        Args:
            component: Filter by component
            metric_type: Filter by metric type
            
        Returns:
            Dictionary of aggregated metrics
        """
        filtered_metrics = {}
        
        with self._lock:
            for key, aggregated in self._aggregated_metrics.items():
                key_component, key_metric_type = key.rsplit('_', 1)
                
                # Apply filters
                if component and key_component != component:
                    continue
                if metric_type and key_metric_type != metric_type.value:
                    continue
                
                filtered_metrics[key] = aggregated.copy()
        
        return filtered_metrics
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get active performance alerts"""
        with self._lock:
            return [alert for alert in self._active_alerts.values() if not alert.resolved]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert"""
        with self._lock:
            for alert in self._active_alerts.values():
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolution_timestamp = datetime.now(timezone.utc)
                    self._stats['active_alerts'] -= 1
                    self._stats['resolved_alerts'] += 1
                    
                    self._performance_logger.info(
                        "Performance alert resolved",
                        alert_id=alert_id
                    )
                    return True
        return False
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance monitoring statistics"""
        with self._lock:
            stats = self._stats.copy()
            stats['components_profiles'] = len(self.component_profiles)
            stats['metric_thresholds'] = len(self.metric_thresholds)
            stats['buffer_keys'] = len(self._metrics_buffer)
            stats['aggregated_metrics'] = len(self._aggregated_metrics)
            stats['alert_history_size'] = len(self._alert_history)
        
        return stats
    
    def add_component_profile(self, profile: ComponentProfile) -> None:
        """Add component performance profile"""
        self.component_profiles[profile.name] = profile
        logging.info(f"Added performance profile for component: {profile.name}")
    
    def update_metric_threshold(self, threshold: MetricThreshold) -> None:
        """Update metric threshold"""
        self.metric_thresholds[threshold.metric_type] = threshold
        logging.info(f"Updated threshold for metric: {threshold.metric_type}")
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get current configuration status"""
        return {
            "enabled": self.enabled,
            "sampling_interval": self.sampling_interval,
            "aggregation_window": self.aggregation_window,
            "retention_period": self.retention_period,
            "system_monitoring": self.enable_system_monitoring,
            "ai_monitoring": self.enable_ai_monitoring,
            "business_monitoring": self.enable_business_monitoring,
            "predictive_alerts": self.enable_predictive_alerts,
            "optimization_suggestions": self.enable_optimization_suggestions,
            "anomaly_detection": self.enable_anomaly_detection,
            "detailed_tracing": self.enable_detailed_tracing,
            "gpu_available": self._gpu_available,
            "component_profiles": len(self.component_profiles),
            "metric_thresholds": len(self.metric_thresholds),
            "webhook_urls": len(self.webhook_urls),
            "monitoring_active": self._monitoring_thread and self._monitoring_thread.is_alive()
        }


# Global performance logging configuration instance
_performance_config: Optional[PerformanceLoggingConfig] = None


def initialize_performance_logging(
    config: Optional[PerformanceLoggingConfig] = None
) -> PerformanceLoggingConfig:
    """
    Initialize global performance logging configuration.
    
    Args:
        config: Custom PerformanceLoggingConfig instance
        
    Returns:
        Initialized performance logging configuration
    """
    global _performance_config
    
    if config:
        _performance_config = config
    else:
        _performance_config = PerformanceLoggingConfig()
    
    return _performance_config


def get_performance_config() -> PerformanceLoggingConfig:
    """Get the global performance logging configuration"""
    if not _performance_config:
        initialize_performance_logging()
    
    return _performance_config


def record_performance_metric(
    metric_type: MetricType,
    value: float,
    component: str,
    operation: Optional[str] = None,
    **kwargs
) -> None:
    """
    Record a performance metric using global configuration.
    
    Args:
        metric_type: Type of metric
        value: Metric value
        component: Component name
        operation: Operation name
        **kwargs: Additional arguments
    """
    config = get_performance_config()
    config.record_performance_metric(metric_type, value, component, operation, **kwargs)


def measure_operation(
    operation: str,
    component: str,
    metric_type: MetricType = MetricType.PROCESSING_TIME,
    **kwargs
):
    """
    Context manager to measure operation performance using global configuration.
    
    Args:
        operation: Operation name
        component: Component name
        metric_type: Type of timing metric
        **kwargs: Additional arguments
    """
    config = get_performance_config()
    return config.measure_operation(operation, component, metric_type, **kwargs)
