"""AI Performance Monitor - AI Service Performance Tracking and Analysis System
==============================================================================

Advanced performance monitoring system for AI services that tracks latency,
throughput, reliability, quality metrics, and provides insights for optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import statistics
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import hashlib

import aioredis
import aiofiles
import psutil
from prometheus_client import Counter, Histogram, Gauge, Summary

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Performance metric types."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    AVAILABILITY = "availability"
    QUALITY_SCORE = "quality_score"
    COST_EFFICIENCY = "cost_efficiency"
    TOKENS_PER_SECOND = "tokens_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NETWORK_IO = "network_io"


class AlertSeverity(Enum):
    """Performance alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformanceStatus(Enum):
    """Performance status levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceRecord:
    """Individual performance measurement record."""
    timestamp: datetime
    provider: str
    model: str
    service_type: str
    request_id: str
    user_id: Optional[str]
    
    # Timing metrics
    request_start: float
    request_end: float
    processing_duration_ms: float
    queue_time_ms: float
    network_time_ms: float
    
    # Resource metrics
    input_tokens: int
    output_tokens: int
    total_tokens: int
    
    # Quality metrics
    quality_score: float
    error_occurred: bool
    error_type: Optional[str]
    error_message: Optional[str]
    
    # System metrics
    cpu_usage: float
    memory_usage: float
    network_bytes_sent: int
    network_bytes_received: int
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    metric: PerformanceMetric
    provider: Optional[str]
    model: Optional[str]
    service_type: Optional[str]
    
    # Threshold values
    warning_threshold: float
    critical_threshold: float
    
    # Evaluation settings
    evaluation_window_minutes: int
    minimum_samples: int
    
    # Alert settings
    alert_enabled: bool = True
    cooldown_minutes: int = 15
    
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceAlert:
    """Performance alert."""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    metric: PerformanceMetric
    provider: str
    model: str
    service_type: str
    
    current_value: float
    threshold_value: float
    threshold_type: str  # "warning" or "critical"
    
    description: str
    recommendation: str
    
    # Alert metadata
    alert_count: int = 1
    first_occurrence: datetime = field(default_factory=datetime.utcnow)
    last_occurrence: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False


class PerformanceCollector:
    """Performance data collection system."""
    
    def __init__(self) -> None:
        self.performance_records: deque = deque(maxlen=50000)
        self.active_requests: Dict[str, dict] = {}
        
        # System monitoring
        self.process = psutil.Process()
        self.network_io_start = psutil.net_io_counters()
        
        # Metrics aggregation
        self.metric_aggregates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time calculations
        self.current_metrics: Dict[str, float] = defaultdict(float)
        self.last_calculation = datetime.utcnow()
    
    async def start_request_tracking(self, request_id: str, provider: str, model: str, 
                                   service_type: str, user_id: Optional[str] = None) -> dict:
        """Start tracking a request's performance."""
        start_time = time.time()
        
        # Get current system metrics
        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_usage = memory_info.rss / (1024 * 1024)  # MB
        
        network_io = psutil.net_io_counters()
        
        tracking_data = {
            "request_id": request_id,
            "provider": provider,
            "model": model,
            "service_type": service_type,
            "user_id": user_id,
            "start_time": start_time,
            "start_cpu": cpu_percent,
            "start_memory": memory_usage,
            "start_network_sent": network_io.bytes_sent,
            "start_network_recv": network_io.bytes_recv,
            "queue_start": time.time()
        }
        
        self.active_requests[request_id] = tracking_data
        return tracking_data
    
    async def update_request_tracking(self, request_id -> None: str, stage -> None: str, **kwargs) -> None:
        """Update request tracking with stage information."""
        if request_id not in self.active_requests:
            return
        
        current_time = time.time()
        tracking_data = self.active_requests[request_id]
        
        if stage == "processing_start":
            tracking_data["processing_start"] = current_time
            tracking_data["queue_time"] = current_time - tracking_data["queue_start"]
        
        elif stage == "processing_end":
            tracking_data["processing_end"] = current_time
            tracking_data["processing_time"] = current_time - tracking_data["processing_start"]
        
        # Update with any additional data
        tracking_data.update(kwargs)
    
    async def complete_request_tracking(self, request_id: str, 
                                      input_tokens: int = 0,
                                      output_tokens: int = 0,
                                      quality_score: float = 1.0,
                                      error_occurred: bool = False,
                                      error_type: Optional[str] = None,
                                      error_message: Optional[str] = None,
                                      **metadata) -> PerformanceRecord:
        """Complete request tracking and create performance record."""
        
        if request_id not in self.active_requests:
            raise ValueError(f"Request {request_id} not being tracked")
        
        tracking_data = self.active_requests[request_id]
        end_time = time.time()
        
        # Calculate timing metrics
        total_duration = (end_time - tracking_data["start_time"]) * 1000  # ms
        queue_time = tracking_data.get("queue_time", 0) * 1000  # ms
        processing_time = tracking_data.get("processing_time", total_duration / 1000) * 1000  # ms
        network_time = total_duration - processing_time - queue_time
        
        # Get final system metrics
        end_cpu = self.process.cpu_percent()
        end_memory_info = self.process.memory_info()
        end_memory = end_memory_info.rss / (1024 * 1024)  # MB
        
        end_network_io = psutil.net_io_counters()
        
        # Create performance record
        record = PerformanceRecord(
            timestamp=datetime.utcnow(),
            provider=tracking_data["provider"],
            model=tracking_data["model"],
            service_type=tracking_data["service_type"],
            request_id=request_id,
            user_id=tracking_data.get("user_id"),
            
            request_start=tracking_data["start_time"],
            request_end=end_time,
            processing_duration_ms=processing_time,
            queue_time_ms=queue_time,
            network_time_ms=network_time,
            
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            
            quality_score=quality_score,
            error_occurred=error_occurred,
            error_type=error_type,
            error_message=error_message,
            
            cpu_usage=(tracking_data["start_cpu"] + end_cpu) / 2,
            memory_usage=(tracking_data["start_memory"] + end_memory) / 2,
            network_bytes_sent=end_network_io.bytes_sent - tracking_data["start_network_sent"],
            network_bytes_received=end_network_io.bytes_recv - tracking_data["start_network_recv"],
            
            metadata=metadata
        )
        
        # Store record
        self.performance_records.append(record)
        
        # Update aggregates
        await self._update_metric_aggregates(record)
        
        # Clean up tracking
        del self.active_requests[request_id]
        
        return record
    
    async def _update_metric_aggregates(self, record -> None: PerformanceRecord) -> None:
        """Update metric aggregates with new record."""
        provider_key = f"{record.provider}_{record.model}"
        
        # Update timing aggregates
        self.metric_aggregates[f"{provider_key}_latency"].append(record.processing_duration_ms)
        self.metric_aggregates[f"{provider_key}_queue_time"].append(record.queue_time_ms)
        self.metric_aggregates[f"{provider_key}_network_time"].append(record.network_time_ms)
        
        # Update quality aggregates
        self.metric_aggregates[f"{provider_key}_quality"].append(record.quality_score)
        
        # Update throughput (tokens per second)
        if record.processing_duration_ms > 0:
            tokens_per_second = (record.total_tokens / record.processing_duration_ms) * 1000
            self.metric_aggregates[f"{provider_key}_throughput"].append(tokens_per_second)
        
        # Update error rate
        error_value = 1.0 if record.error_occurred else 0.0
        self.metric_aggregates[f"{provider_key}_errors"].append(error_value)
        
        # Update resource usage
        self.metric_aggregates[f"{provider_key}_cpu"].append(record.cpu_usage)
        self.metric_aggregates[f"{provider_key}_memory"].append(record.memory_usage)
    
    def get_recent_records(self, minutes: int = 60) -> List[PerformanceRecord]:
        """Get performance records from the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [r for r in self.performance_records if r.timestamp > cutoff_time]
    
    def get_provider_records(self, provider: str, model: Optional[str] = None, 
                           minutes: int = 60) -> List[PerformanceRecord]:
        """Get records for specific provider/model."""
        recent_records = self.get_recent_records(minutes)
        
        filtered_records = [r for r in recent_records if r.provider == provider]
        
        if model:
            filtered_records = [r for r in filtered_records if r.model == model]
        
        return filtered_records


class PerformanceAnalyzer:
    """Performance analysis and metrics calculation system."""
    
    def __init__(self, collector -> None: PerformanceCollector) -> None:
        self.collector = collector
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.alerts: Dict[str, PerformanceAlert] = {}
        
        # Prometheus metrics
        self.latency_histogram = Histogram('ai_request_latency_seconds', 'AI request latency', ['provider', 'model'])
        self.throughput_gauge = Gauge('ai_throughput_tokens_per_second', 'AI throughput', ['provider', 'model'])
        self.error_rate_gauge = Gauge('ai_error_rate', 'AI error rate', ['provider', 'model'])
        self.quality_gauge = Gauge('ai_quality_score', 'AI quality score', ['provider', 'model'])
        self.availability_gauge = Gauge('ai_availability', 'AI availability', ['provider', 'model'])
    
    async def calculate_metrics(self, provider: str, model: str, 
                              window_minutes: int = 60) -> Dict[PerformanceMetric, float]:
        """Calculate comprehensive performance metrics."""
        records = self.collector.get_provider_records(provider, model, window_minutes)
        
        if not records:
            return {}
        
        metrics = {}
        
        # Latency metrics
        latencies = [r.processing_duration_ms for r in records]
        metrics[PerformanceMetric.LATENCY] = statistics.mean(latencies)
        
        # Throughput metrics
        throughputs = []
        for record in records:
            if record.processing_duration_ms > 0:
                tps = (record.total_tokens / record.processing_duration_ms) * 1000
                throughputs.append(tps)
        
        if throughputs:
            metrics[PerformanceMetric.THROUGHPUT] = statistics.mean(throughputs)
            metrics[PerformanceMetric.TOKENS_PER_SECOND] = statistics.mean(throughputs)
        
        # Error rate
        errors = sum(1 for r in records if r.error_occurred)
        total_requests = len(records)
        metrics[PerformanceMetric.ERROR_RATE] = errors / total_requests if total_requests > 0 else 0
        metrics[PerformanceMetric.SUCCESS_RATE] = 1 - metrics[PerformanceMetric.ERROR_RATE]
        
        # Quality metrics
        qualities = [r.quality_score for r in records if r.quality_score > 0]
        if qualities:
            metrics[PerformanceMetric.QUALITY_SCORE] = statistics.mean(qualities)
        
        # Availability (based on error rate and response times)
        availability = metrics[PerformanceMetric.SUCCESS_RATE]
        if metrics[PerformanceMetric.LATENCY] > 30000:  # More than 30s is considered unavailable
            availability *= 0.5
        metrics[PerformanceMetric.AVAILABILITY] = availability
        
        # Requests per minute
        time_span = window_minutes
        metrics[PerformanceMetric.REQUESTS_PER_MINUTE] = total_requests / time_span if time_span > 0 else 0
        
        # Resource usage
        cpu_usage = [r.cpu_usage for r in records if r.cpu_usage > 0]
        memory_usage = [r.memory_usage for r in records if r.memory_usage > 0]
        
        if cpu_usage:
            metrics[PerformanceMetric.CPU_USAGE] = statistics.mean(cpu_usage)
        if memory_usage:
            metrics[PerformanceMetric.MEMORY_USAGE] = statistics.mean(memory_usage)
        
        # Update Prometheus metrics
        self._update_prometheus_metrics(provider, model, metrics)
        
        return metrics
    
    def _update_prometheus_metrics(self, provider -> None: str, model -> None: str, metrics -> None: Dict[PerformanceMetric, float]) -> None:
        """Update Prometheus metrics."""
        for metric, value in metrics.items():
            if metric == PerformanceMetric.LATENCY:
                self.latency_histogram.labels(provider=provider, model=model).observe(value / 1000)  # Convert to seconds
            elif metric == PerformanceMetric.THROUGHPUT:
                self.throughput_gauge.labels(provider=provider, model=model).set(value)
            elif metric == PerformanceMetric.ERROR_RATE:
                self.error_rate_gauge.labels(provider=provider, model=model).set(value)
            elif metric == PerformanceMetric.QUALITY_SCORE:
                self.quality_gauge.labels(provider=provider, model=model).set(value)
            elif metric == PerformanceMetric.AVAILABILITY:
                self.availability_gauge.labels(provider=provider, model=model).set(value)
    
    async def set_threshold(self, metric: PerformanceMetric, 
                          warning_threshold: float, 
                          critical_threshold: float,
                          provider: Optional[str] = None,
                          model: Optional[str] = None,
                          service_type: Optional[str] = None,
                          evaluation_window_minutes: int = 15,
                          minimum_samples: int = 5) -> str:
        """Set performance threshold for monitoring."""
        
        threshold_id = hashlib.md5(
            f"{metric.value}_{provider}_{model}_{service_type}_{time.time()}".encode()
        ).hexdigest()
        
        threshold = PerformanceThreshold(
            metric=metric,
            provider=provider,
            model=model,
            service_type=service_type,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            evaluation_window_minutes=evaluation_window_minutes,
            minimum_samples=minimum_samples
        )
        
        self.thresholds[threshold_id] = threshold
        
        logger.info(f"Set threshold for {metric.value}: warning={warning_threshold}, critical={critical_threshold}")
        return threshold_id
    
    async def check_thresholds(self) -> List[PerformanceAlert]:
        """Check all thresholds and generate alerts if needed."""
        new_alerts = []
        
        for threshold_id, threshold in self.thresholds.items():
            try:
                # Get applicable providers
                providers_to_check = []
                
                if threshold.provider and threshold.model:
                    providers_to_check.append((threshold.provider, threshold.model))
                else:
                    # Get all active provider/model combinations
                    recent_records = self.collector.get_recent_records(threshold.evaluation_window_minutes)
                    provider_models = set((r.provider, r.model) for r in recent_records)
                    
                    for provider, model in provider_models:
                        if threshold.provider and provider != threshold.provider:
                            continue
                        if threshold.model and model != threshold.model:
                            continue
                        providers_to_check.append((provider, model))
                
                # Check each provider/model combination
                for provider, model in providers_to_check:
                    records = self.collector.get_provider_records(
                        provider, model, threshold.evaluation_window_minutes
                    )
                    
                    if len(records) < threshold.minimum_samples:
                        continue
                    
                    # Filter by service type if specified
                    if threshold.service_type:
                        records = [r for r in records if r.service_type == threshold.service_type]
                        if len(records) < threshold.minimum_samples:
                            continue
                    
                    # Calculate current metric value
                    current_value = await self._calculate_threshold_metric(threshold.metric, records)
                    
                    # Check thresholds
                    alert = await self._check_single_threshold(
                        threshold, provider, model, current_value
                    )
                    
                    if alert:
                        new_alerts.append(alert)
            
            except Exception as e:
                logger.error(f"Threshold check failed for {threshold_id}: {str(e)}")
        
        return new_alerts
    
    async def _calculate_threshold_metric(self, metric: PerformanceMetric, 
                                        records: List[PerformanceRecord]) -> float:
        """Calculate metric value for threshold checking."""
        if not records:
            return 0.0
        
        if metric == PerformanceMetric.LATENCY:
            return statistics.mean(r.processing_duration_ms for r in records)
        
        elif metric == PerformanceMetric.ERROR_RATE:
            errors = sum(1 for r in records if r.error_occurred)
            return errors / len(records)
        
        elif metric == PerformanceMetric.SUCCESS_RATE:
            errors = sum(1 for r in records if r.error_occurred)
            return 1 - (errors / len(records))
        
        elif metric == PerformanceMetric.QUALITY_SCORE:
            qualities = [r.quality_score for r in records if r.quality_score > 0]
            return statistics.mean(qualities) if qualities else 0.0
        
        elif metric == PerformanceMetric.THROUGHPUT:
            throughputs = []
            for record in records:
                if record.processing_duration_ms > 0:
                    tps = (record.total_tokens / record.processing_duration_ms) * 1000
                    throughputs.append(tps)
            return statistics.mean(throughputs) if throughputs else 0.0
        
        elif metric == PerformanceMetric.AVAILABILITY:
            errors = sum(1 for r in records if r.error_occurred)
            success_rate = 1 - (errors / len(records))
            avg_latency = statistics.mean(r.processing_duration_ms for r in records)
            
            # Reduce availability for high latency
            if avg_latency > 30000:  # 30 seconds
                success_rate *= 0.5
            elif avg_latency > 10000:  # 10 seconds
                success_rate *= 0.8
            
            return success_rate
        
        elif metric == PerformanceMetric.CPU_USAGE:
            cpu_values = [r.cpu_usage for r in records if r.cpu_usage > 0]
            return statistics.mean(cpu_values) if cpu_values else 0.0
        
        elif metric == PerformanceMetric.MEMORY_USAGE:
            memory_values = [r.memory_usage for r in records if r.memory_usage > 0]
            return statistics.mean(memory_values) if memory_values else 0.0
        
        else:
            return 0.0
    
    async def _check_single_threshold(self, threshold: PerformanceThreshold,
                                    provider: str, model: str, 
                                    current_value: float) -> Optional[PerformanceAlert]:
        """Check a single threshold and generate alert if needed."""
        
        alert_key = f"{threshold.metric.value}_{provider}_{model}"
        
        # Determine if threshold is violated
        violated = False
        severity = AlertSeverity.INFO
        threshold_value = 0.0
        threshold_type = ""
        
        # Check critical threshold first
        if ((threshold.metric in [PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE, PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE] and 
             current_value >= threshold.critical_threshold) or
            (threshold.metric in [PerformanceMetric.SUCCESS_RATE, PerformanceMetric.QUALITY_SCORE, PerformanceMetric.AVAILABILITY, PerformanceMetric.THROUGHPUT] and 
             current_value <= threshold.critical_threshold)):
            violated = True
            severity = AlertSeverity.CRITICAL
            threshold_value = threshold.critical_threshold
            threshold_type = "critical"
        
        # Check warning threshold
        elif ((threshold.metric in [PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE, PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE] and 
               current_value >= threshold.warning_threshold) or
              (threshold.metric in [PerformanceMetric.SUCCESS_RATE, PerformanceMetric.QUALITY_SCORE, PerformanceMetric.AVAILABILITY, PerformanceMetric.THROUGHPUT] and 
               current_value <= threshold.warning_threshold)):
            violated = True
            severity = AlertSeverity.WARNING
            threshold_value = threshold.warning_threshold
            threshold_type = "warning"
        
        if not violated:
            # Clear existing alert if resolved
            if alert_key in self.alerts and not self.alerts[alert_key].resolved:
                self.alerts[alert_key].resolved = True
                logger.info(f"Alert resolved: {alert_key}")
            return None
        
        # Check cooldown period
        if alert_key in self.alerts:
            existing_alert = self.alerts[alert_key]
            time_since_last = datetime.utcnow() - existing_alert.last_occurrence
            
            if time_since_last.total_seconds() < threshold.cooldown_minutes * 60:
                # Update existing alert
                existing_alert.alert_count += 1
                existing_alert.last_occurrence = datetime.utcnow()
                existing_alert.current_value = current_value
                return None
        
        # Create new alert
        alert_id = hashlib.md5(f"{alert_key}_{time.time()}".encode()).hexdigest()
        
        description = self._generate_alert_description(
            threshold.metric, provider, model, current_value, threshold_value, threshold_type
        )
        
        recommendation = self._generate_alert_recommendation(
            threshold.metric, provider, model, current_value, threshold_value
        )
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            metric=threshold.metric,
            provider=provider,
            model=model,
            service_type=threshold.service_type or "all",
            current_value=current_value,
            threshold_value=threshold_value,
            threshold_type=threshold_type,
            description=description,
            recommendation=recommendation
        )
        
        self.alerts[alert_key] = alert
        
        logger.warning(f"Performance alert: {description}")
        return alert
    
    def _generate_alert_description(self, metric: PerformanceMetric, provider: str, 
                                  model: str, current_value: float, 
                                  threshold_value: float, threshold_type: str) -> str:
        """Generate human-readable alert description."""
        
        if metric == PerformanceMetric.LATENCY:
            return f"{provider} {model} latency is {current_value:.0f}ms (threshold: {threshold_value:.0f}ms)"
        
        elif metric == PerformanceMetric.ERROR_RATE:
            return f"{provider} {model} error rate is {current_value:.1%} (threshold: {threshold_value:.1%})"
        
        elif metric == PerformanceMetric.SUCCESS_RATE:
            return f"{provider} {model} success rate is {current_value:.1%} (threshold: {threshold_value:.1%})"
        
        elif metric == PerformanceMetric.QUALITY_SCORE:
            return f"{provider} {model} quality score is {current_value:.2f} (threshold: {threshold_value:.2f})"
        
        elif metric == PerformanceMetric.THROUGHPUT:
            return f"{provider} {model} throughput is {current_value:.1f} tokens/sec (threshold: {threshold_value:.1f})"
        
        elif metric == PerformanceMetric.AVAILABILITY:
            return f"{provider} {model} availability is {current_value:.1%} (threshold: {threshold_value:.1%})"
        
        else:
            return f"{provider} {model} {metric.value} is {current_value:.2f} (threshold: {threshold_value:.2f})"
    
    def _generate_alert_recommendation(self, metric: PerformanceMetric, provider: str, 
                                     model: str, current_value: float, 
                                     threshold_value: float) -> str:
        """Generate actionable recommendation for alert."""
        
        if metric == PerformanceMetric.LATENCY:
            return "Consider switching to a faster model, optimizing request size, or implementing caching"
        
        elif metric == PerformanceMetric.ERROR_RATE:
            return "Check API key validity, review request format, or implement retry logic"
        
        elif metric == PerformanceMetric.SUCCESS_RATE:
            return "Investigate error causes and implement error handling improvements"
        
        elif metric == PerformanceMetric.QUALITY_SCORE:
            return "Consider using a higher-quality model or adjusting prompt engineering"
        
        elif metric == PerformanceMetric.THROUGHPUT:
            return "Optimize request batching, consider parallel processing, or upgrade to faster models"
        
        elif metric == PerformanceMetric.AVAILABILITY:
            return "Check service status, implement fallback providers, or increase timeout values"
        
        else:
            return "Monitor the metric closely and consider optimization strategies"


class AIPerformanceMonitor:
    """Main AI performance monitoring system."""
    
    def __init__(self, redis_url -> None: str = None) -> None:
        self.collector = PerformanceCollector()
        self.analyzer = PerformanceAnalyzer(self.collector)
        self.redis_client = None
        self.redis_url = redis_url
        
        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Performance status tracking
        self.provider_status: Dict[str, PerformanceStatus] = defaultdict(lambda: PerformanceStatus.GOOD)
        
        # Default thresholds
        self.default_thresholds = {
            PerformanceMetric.LATENCY: (5000, 10000),  # 5s warning, 10s critical
            PerformanceMetric.ERROR_RATE: (0.05, 0.15),  # 5% warning, 15% critical
            PerformanceMetric.SUCCESS_RATE: (0.95, 0.85),  # 95% warning, 85% critical
            PerformanceMetric.QUALITY_SCORE: (0.8, 0.6),  # 0.8 warning, 0.6 critical
            PerformanceMetric.AVAILABILITY: (0.99, 0.95),  # 99% warning, 95% critical
            PerformanceMetric.CPU_USAGE: (80, 95),  # 80% warning, 95% critical
            PerformanceMetric.MEMORY_USAGE: (80, 95)  # 80% warning, 95% critical
        }
    
    async def initialize(self) -> None:
        """Initialize the performance monitoring system."""
        try:
            if self.redis_url:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
            
            # Set up default thresholds
            await self._setup_default_thresholds()
            
            # Start monitoring tasks
            self.monitoring_tasks = [
                asyncio.create_task(self._threshold_monitoring_loop()),
                asyncio.create_task(self._metrics_calculation_loop()),
                asyncio.create_task(self._status_update_loop())
            ]
            
            logger.info("AI performance monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {str(e)}")
            raise
    
    async def _setup_default_thresholds(self) -> None:
        """Set up default performance thresholds."""
        for metric, (warning, critical) in self.default_thresholds.items():
            await self.analyzer.set_threshold(
                metric=metric,
                warning_threshold=warning,
                critical_threshold=critical,
                evaluation_window_minutes=15,
                minimum_samples=5
            )
    
    @asynccontextmanager
    async def track_request(self, provider -> None: str, model -> None: str, service_type -> None: str, 
                          request_id -> None: Optional[str] = None, user_id -> None: Optional[str] = None) -> None:
        """Context manager for tracking request performance."""
        
        if not request_id:
            request_id = hashlib.md5(f"{provider}_{model}_{time.time()}".encode()).hexdigest()
        
        # Start tracking
        tracking_data = await self.collector.start_request_tracking(
            request_id, provider, model, service_type, user_id
        )
        
        try:
            yield tracking_data
            
            # Mark as successful
            await self.collector.update_request_tracking(request_id, "processing_end")
            
        except Exception as e:
            # Mark as failed
            await self.collector.update_request_tracking(
                request_id, "error", 
                error_occurred=True, 
                error_type=type(e).__name__, 
                error_message=str(e)
            )
            raise
        
        finally:
            # Complete tracking
            await self.collector.complete_request_tracking(
                request_id,
                error_occurred=tracking_data.get("error_occurred", False),
                error_type=tracking_data.get("error_type"),
                error_message=tracking_data.get("error_message"),
                **tracking_data
            )
    
    async def record_performance(self, provider: str, model: str, service_type: str,
                               request_id: str, input_tokens: int, output_tokens: int,
                               processing_time_ms: float, quality_score: float = 1.0,
                               error_occurred: bool = False, **kwargs) -> PerformanceRecord:
        """Manually record performance data."""
        
        # Create a minimal tracking record
        await self.collector.start_request_tracking(request_id, provider, model, service_type)
        
        return await self.collector.complete_request_tracking(
            request_id=request_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            quality_score=quality_score,
            error_occurred=error_occurred,
            **kwargs
        )
    
    async def get_performance_metrics(self, provider: str, model: str, 
                                    window_minutes: int = 60) -> Dict[PerformanceMetric, float]:
        """Get comprehensive performance metrics for provider/model."""
        return await self.analyzer.calculate_metrics(provider, model, window_minutes)
    
    async def get_performance_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        
        # Get all provider/model combinations
        recent_records = self.collector.get_recent_records(window_minutes)
        provider_models = set((r.provider, r.model) for r in recent_records)
        
        summary = {
            "window_minutes": window_minutes,
            "total_requests": len(recent_records),
            "providers": {},
            "overall_metrics": {},
            "alerts": [],
            "status_distribution": defaultdict(int)
        }
        
        # Calculate metrics for each provider/model
        all_latencies = []
        all_error_rates = []
        all_quality_scores = []
        
        for provider, model in provider_models:
            metrics = await self.analyzer.calculate_metrics(provider, model, window_minutes)
            
            provider_key = f"{provider}_{model}"
            summary["providers"][provider_key] = {
                "metrics": {metric.value: value for metric, value in metrics.items()},
                "status": self.provider_status[provider_key].value,
                "records_count": len(self.collector.get_provider_records(provider, model, window_minutes))
            }
            
            # Collect for overall metrics
            if PerformanceMetric.LATENCY in metrics:
                all_latencies.append(metrics[PerformanceMetric.LATENCY])
            if PerformanceMetric.ERROR_RATE in metrics:
                all_error_rates.append(metrics[PerformanceMetric.ERROR_RATE])
            if PerformanceMetric.QUALITY_SCORE in metrics:
                all_quality_scores.append(metrics[PerformanceMetric.QUALITY_SCORE])
            
            # Count status distribution
            summary["status_distribution"][self.provider_status[provider_key].value] += 1
        
        # Calculate overall metrics
        if all_latencies:
            summary["overall_metrics"]["average_latency"] = statistics.mean(all_latencies)
        if all_error_rates:
            summary["overall_metrics"]["average_error_rate"] = statistics.mean(all_error_rates)
        if all_quality_scores:
            summary["overall_metrics"]["average_quality_score"] = statistics.mean(all_quality_scores)
        
        # Include recent alerts
        recent_alerts = [alert for alert in self.analyzer.alerts.values() 
                        if not alert.resolved and 
                        (datetime.utcnow() - alert.timestamp).total_seconds() < window_minutes * 60]
        
        summary["alerts"] = [asdict(alert) for alert in recent_alerts]
        
        return summary
    
    async def _threshold_monitoring_loop(self) -> None:
        """Continuous threshold monitoring."""
        while True:
            try:
                alerts = await self.analyzer.check_thresholds()
                
                # Process new alerts
                for alert in alerts:
                    await self._process_alert(alert)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Threshold monitoring failed: {str(e)}")
                await asyncio.sleep(60)
    
    async def _metrics_calculation_loop(self) -> None:
        """Periodic metrics calculation."""
        while True:
            try:
                # Get all active provider/model combinations
                recent_records = self.collector.get_recent_records(60)
                provider_models = set((r.provider, r.model) for r in recent_records)
                
                # Calculate metrics for each
                for provider, model in provider_models:
                    await self.analyzer.calculate_metrics(provider, model, 60)
                
                await asyncio.sleep(300)  # Calculate every 5 minutes
                
            except Exception as e:
                logger.error(f"Metrics calculation failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _status_update_loop(self) -> None:
        """Update performance status for providers."""
        while True:
            try:
                recent_records = self.collector.get_recent_records(60)
                provider_models = set((r.provider, r.model) for r in recent_records)
                
                for provider, model in provider_models:
                    provider_key = f"{provider}_{model}"
                    metrics = await self.analyzer.calculate_metrics(provider, model, 60)
                    
                    # Determine status based on metrics
                    status = await self._calculate_provider_status(metrics)
                    self.provider_status[provider_key] = status
                
                await asyncio.sleep(180)  # Update every 3 minutes
                
            except Exception as e:
                logger.error(f"Status update failed: {str(e)}")
                await asyncio.sleep(180)
    
    async def _calculate_provider_status(self, metrics: Dict[PerformanceMetric, float]) -> PerformanceStatus:
        """Calculate overall performance status from metrics."""
        
        if not metrics:
            return PerformanceStatus.GOOD
        
        critical_issues = 0
        warning_issues = 0
        
        # Check each metric against thresholds
        for metric, value in metrics.items():
            if metric in self.default_thresholds:
                warning_threshold, critical_threshold = self.default_thresholds[metric]
                
                if metric in [PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE, PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE]:
                    # Higher values are worse
                    if value >= critical_threshold:
                        critical_issues += 1
                    elif value >= warning_threshold:
                        warning_issues += 1
                
                else:
                    # Lower values are worse
                    if value <= critical_threshold:
                        critical_issues += 1
                    elif value <= warning_threshold:
                        warning_issues += 1
        
        # Determine overall status
        if critical_issues >= 2:
            return PerformanceStatus.CRITICAL
        elif critical_issues >= 1:
            return PerformanceStatus.POOR
        elif warning_issues >= 3:
            return PerformanceStatus.POOR
        elif warning_issues >= 1:
            return PerformanceStatus.FAIR
        else:
            return PerformanceStatus.EXCELLENT
    
    async def _process_alert(self, alert -> None: PerformanceAlert) -> None:
        """Process a performance alert."""
        
        # Store alert in Redis
        if self.redis_client:
            alert_data = asdict(alert)
            await self.redis_client.lpush("performance_alerts", json.dumps(alert_data, default=str))
        
        # Log alert
        logger.warning(f"Performance Alert [{alert.severity.value.upper()}]: {alert.description}")
        logger.info(f"Recommendation: {alert.recommendation}")
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
                await self.redis_client.wait_closed()
            
            logger.info("AI performance monitor cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup performance monitor: {str(e)}")


# Global performance monitor instance
performance_monitor = AIPerformanceMonitor()


@asynccontextmanager
async def track_ai_performance(provider -> None: str, model -> None: str, service_type -> None: str, **kwargs) -> None:
    """Track AI request performance using global monitor."""
    async with performance_monitor.track_request(provider, model, service_type, **kwargs) as tracking:
        yield tracking


async def record_ai_performance(**kwargs) -> PerformanceRecord:
    """Record AI performance using global monitor."""
    return await performance_monitor.record_performance(**kwargs)


# Example usage
async def main() -> None:
    """Example usage of AI performance monitor."""
    await performance_monitor.initialize()
    
    # Example: Track a request
    async with track_ai_performance("openai", "gpt-4", "text_generation") as tracking:
        # Simulate AI request processing
        await asyncio.sleep(1)  # Simulate processing time
        
        # Update tracking with token counts
        tracking.update({
            "input_tokens": 100,
            "output_tokens": 150,
            "quality_score": 0.95
        })
    
    # Get performance metrics
    metrics = await performance_monitor.get_performance_metrics("openai", "gpt-4")
    print(f"OpenAI GPT-4 metrics: {metrics}")
    
    # Get overall summary
    summary = await performance_monitor.get_performance_summary()
    print(f"Performance summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())