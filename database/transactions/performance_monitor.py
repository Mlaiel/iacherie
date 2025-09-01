"""Transaction Performance Monitor - Real-time Transaction Analytics

Enterprise-grade performance monitoring system for database transactions,
providing real-time metrics, performance analytics, and optimization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.
"""

import asyncio
import time
import statistics
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from enum import Enum
import threading
import json
import weakref

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """
Metric type enumeration"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TransactionMetrics:
    """Comprehensive transaction performance metrics"""
    transaction_id: str
    transaction_type: str = "unknown"
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    state: str = "active"
    participant_count: int = 0
    retry_count: int = 0
    error_count: int = 0
    bytes_processed: int = 0
    rows_affected: int = 0
    lock_wait_time: float = 0.0
    cpu_time: float = 0.0
    memory_usage: int = 0
    network_io: int = 0
    disk_io: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def mark_completed(self, success: bool = True) -> None:
        """Mark transaction as completed"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.state = "completed" if success else "failed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "state": self.state,
            "participant_count": self.participant_count,
            "retry_count": self.retry_count,
            "error_count": self.error_count,
            "bytes_processed": self.bytes_processed,
            "rows_affected": self.rows_affected,
            "lock_wait_time": self.lock_wait_time,
            "cpu_time": self.cpu_time,
            "memory_usage": self.memory_usage,
            "network_io": self.network_io,
            "disk_io": self.disk_io,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "custom_metrics": self.custom_metrics,
        }


@dataclass
class AggregatedMetrics:
    """Aggregated performance metrics over time period"""
    period_start: datetime
    period_end: datetime
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    p50_duration: float = 0.0
    p95_duration: float = 0.0
    p99_duration: float = 0.0
    throughput: float = 0.0  # transactions per second
    error_rate: float = 0.0
    retry_rate: float = 0.0
    total_bytes_processed: int = 0
    total_rows_affected: int = 0
    avg_lock_wait_time: float = 0.0
    cache_hit_rate: float = 0.0
    
    def calculate_percentiles(self, durations: List[float]) -> None:
        """
Calculate duration percentiles"""
        if durations:
            sorted_durations = sorted(durations)
            self.p50_duration = statistics.median(sorted_durations)
            self.p95_duration = sorted_durations[int(0.95 * len(sorted_durations))]
            self.p99_duration = sorted_durations[int(0.99 * len(sorted_durations))]


class AlertRule:
    """
Performance alert rule definition"""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[AggregatedMetrics], bool],
        level: AlertLevel = AlertLevel.WARNING,
        message_template: str = "Alert triggered for {name}",
        cooldown_seconds: int = 300
    ):
        self.name = name
        self.condition = condition
        self.level = level
        self.message_template = message_template
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered: Optional[datetime] = None
    
    def should_trigger(self, metrics: AggregatedMetrics) -> bool:
        """Check if alert should be triggered"""
        now = datetime.now(timezone.utc)
        
        # Check cooldown
        if (self.last_triggered and 
            (now - self.last_triggered).total_seconds() < self.cooldown_seconds):
            return False
        
        # Check condition
        if self.condition(metrics):
            self.last_triggered = now
            return True
        
        return False
    
    def format_message(self, metrics: AggregatedMetrics) -> str:
        """
Format alert message"""
        return self.message_template.format(
            name=self.name,
            metrics=metrics,
            **metrics.__dict__
        )


class PerformanceMonitor:
    """
    Real-time transaction performance monitoring system
    
    Features:
    - Real-time metrics collection
    - Statistical analysis and aggregation
    - Performance alerting
    - Historical data retention
    - Custom metric support
    - Multi-dimensional analysis
    - Export capabilities
    """
    
    def __init__(
        self,
        retention_hours: int = 24,
        aggregation_interval_seconds: int = 60,
        max_transactions_memory: int = 10000
    ):
        self.retention_hours = retention_hours
        self.aggregation_interval = aggregation_interval_seconds
        self.max_transactions_memory = max_transactions_memory
        
        # Active transaction metrics
        self.active_transactions: Dict[str, TransactionMetrics] = {}
        
        # Historical metrics storage
        self.historical_metrics: deque = deque(maxlen=retention_hours * 60)  # One minute intervals
        
        # Real-time metrics buffer
        self.metrics_buffer: deque = deque(maxlen=max_transactions_memory)
        
        # Alert rules
        self.alert_rules: List[AlertRule] = []
        self.alert_callbacks: List[Callable[[str, AlertLevel, str], None]] = []
        
        # Performance counters
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Background tasks
        self._shutdown = False
        self._monitor_task = None
        
        # Initialize default alert rules
        self._setup_default_alerts()
        
        logger.info("PerformanceMonitor initialized with retention=%dh, interval=%ds", 
                   retention_hours, aggregation_interval_seconds)
    
    def start_monitoring(self) -> None:
        """Start background monitoring tasks"""
        if not self._monitor_task or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._background_monitor())
            logger.info("Performance monitoring started")
    
    def start_transaction(self, transaction_id: str, transaction_type: str = "unknown") -> TransactionMetrics:
        """Start tracking a new transaction"""
        
        with self.lock:
            metrics = TransactionMetrics(
                transaction_id=transaction_id,
                transaction_type=transaction_type
            )
            
            self.active_transactions[transaction_id] = metrics
            self.counters["transactions_started"] += 1
            
            logger.debug("Started tracking transaction: %s (type=%s)", transaction_id, transaction_type)
            return metrics
    
    def end_transaction(self, transaction_id: str, success: bool = True) -> Optional[TransactionMetrics]:
        """End transaction tracking"""
        
        with self.lock:
            metrics = self.active_transactions.pop(transaction_id, None)
            
            if metrics:
                metrics.mark_completed(success)
                
                # Add to buffer for aggregation
                self.metrics_buffer.append(metrics)
                
                # Update counters
                self.counters["transactions_completed"] += 1
                if success:
                    self.counters["transactions_successful"] += 1
                else:
                    self.counters["transactions_failed"] += 1
                
                # Update histograms
                if metrics.duration:
                    self.histograms["transaction_duration"].append(metrics.duration)
                
                logger.debug("Completed tracking transaction: %s (duration=%.3fs, success=%s)", 
                           transaction_id, metrics.duration or 0, success)
                
                return metrics
            
            logger.warning("Transaction not found for completion: %s", transaction_id)
            return None
    
    def update_transaction_metric(self, transaction_id: str, metric_name: str, value: Any) -> bool:
        """Update a specific metric for an active transaction"""
        
        with self.lock:
            metrics = self.active_transactions.get(transaction_id)
            
            if metrics:
                if hasattr(metrics, metric_name):
                    setattr(metrics, metric_name, value)
                else:
                    metrics.custom_metrics[metric_name] = value
                
                logger.debug("Updated metric %s=%s for transaction %s", metric_name, value, transaction_id)
                return True
            
            return False
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric"""
        with self.lock:
            self.counters[name] += value
    
    def set_gauge(self, name: str, value: float) -> None:
        """
Set a gauge metric value"""
        with self.lock:
            self.gauges[name] = value
    
    def record_histogram(self, name: str, value: float) -> None:
        """
Record a histogram value"""
        with self.lock:
            self.histograms[name].append(value)
            
            # Limit histogram size
            if len(self.histograms[name]) > 1000:
                self.histograms[name] = self.histograms[name][-1000:]
    
    def add_alert_rule(self, alert_rule: AlertRule) -> None:
        """
Add performance alert rule"""
        with self.lock:
            self.alert_rules.append(alert_rule)
        
        logger.info("Added alert rule: %s", alert_rule.name)
    
    def add_alert_callback(self, callback: Callable[[str, AlertLevel, str], None]) -> None:
        """Add alert notification callback"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
Get current real-time metrics"""
        
        with self.lock:
            active_count = len(self.active_transactions)
            
            # Calculate current rates
            recent_transactions = [m for m in self.metrics_buffer 
                                 if m.end_time and (time.time() - m.end_time) < 60]
            
            current_throughput = len(recent_transactions) / 60.0 if recent_transactions else 0.0
            
            # Calculate current averages
            current_durations = [m.duration for m in recent_transactions if m.duration]
            avg_duration = statistics.mean(current_durations) if current_durations else 0.0
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "active_transactions": active_count,
                "current_throughput": current_throughput,
                "average_duration": avg_duration,
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histogram_counts": {name: len(values) for name, values in self.histograms.items()}
            }
    
    def get_aggregated_metrics(self, period_minutes: int = 60) -> AggregatedMetrics:
        """Get aggregated metrics for specified time period"""
        
        with self.lock:
            cutoff_time = time.time() - (period_minutes * 60)
            period_transactions = [
                m for m in self.metrics_buffer 
                if m.end_time and m.end_time >= cutoff_time
            ]
            
            if not period_transactions:
                return AggregatedMetrics(
                    period_start=datetime.now(timezone.utc) - timedelta(minutes=period_minutes),
                    period_end=datetime.now(timezone.utc)
                )
            
            # Calculate aggregated metrics
            total_transactions = len(period_transactions)
            successful_transactions = sum(1 for m in period_transactions if m.state == "completed")
            failed_transactions = total_transactions - successful_transactions
            
            durations = [m.duration for m in period_transactions if m.duration]
            total_duration = sum(durations)
            avg_duration = statistics.mean(durations) if durations else 0.0
            min_duration = min(durations) if durations else 0.0
            max_duration = max(durations) if durations else 0.0
            
            throughput = total_transactions / (period_minutes * 60) if period_minutes > 0 else 0.0
            error_rate = failed_transactions / total_transactions if total_transactions > 0 else 0.0
            
            total_retries = sum(m.retry_count for m in period_transactions)
            retry_rate = total_retries / total_transactions if total_transactions > 0 else 0.0
            
            total_bytes = sum(m.bytes_processed for m in period_transactions)
            total_rows = sum(m.rows_affected for m in period_transactions)
            
            lock_wait_times = [m.lock_wait_time for m in period_transactions if m.lock_wait_time > 0]
            avg_lock_wait = statistics.mean(lock_wait_times) if lock_wait_times else 0.0
            
            total_cache_hits = sum(m.cache_hits for m in period_transactions)
            total_cache_misses = sum(m.cache_misses for m in period_transactions)
            cache_hit_rate = (total_cache_hits / (total_cache_hits + total_cache_misses) 
                            if (total_cache_hits + total_cache_misses) > 0 else 0.0)
            
            metrics = AggregatedMetrics(
                period_start=datetime.now(timezone.utc) - timedelta(minutes=period_minutes),
                period_end=datetime.now(timezone.utc),
                total_transactions=total_transactions,
                successful_transactions=successful_transactions,
                failed_transactions=failed_transactions,
                total_duration=total_duration,
                avg_duration=avg_duration,
                min_duration=min_duration,
                max_duration=max_duration,
                throughput=throughput,
                error_rate=error_rate,
                retry_rate=retry_rate,
                total_bytes_processed=total_bytes,
                total_rows_affected=total_rows,
                avg_lock_wait_time=avg_lock_wait,
                cache_hit_rate=cache_hit_rate
            )
            
            # Calculate percentiles
            metrics.calculate_percentiles(durations)
            
            return metrics
    
    def get_transaction_details(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metrics for specific transaction"""
        
        with self.lock:
            # Check active transactions
            if transaction_id in self.active_transactions:
                return self.active_transactions[transaction_id].to_dict()
            
            # Check completed transactions
            for metrics in self.metrics_buffer:
                if metrics.transaction_id == transaction_id:
                    return metrics.to_dict()
            
            return None
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        
        current_metrics = self.get_current_metrics()
        aggregated_metrics = self.get_aggregated_metrics()
        
        export_data = {
            "current": current_metrics,
            "aggregated": aggregated_metrics.__dict__,
            "active_transactions": [m.to_dict() for m in self.active_transactions.values()]
        }
        
        if format_type.lower() == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _setup_default_alerts(self) -> None:
        """Setup default performance alert rules"""
        
        # High error rate alert
        self.add_alert_rule(AlertRule(
            name="high_error_rate",
            condition=lambda m: m.error_rate > 0.05,  # 5% error rate
            level=AlertLevel.WARNING,
            message_template="High error rate detected: {error_rate:.2%}",
            cooldown_seconds=300
        ))
        
        # High average duration alert
        self.add_alert_rule(AlertRule(
            name="high_average_duration",
            condition=lambda m: m.avg_duration > 10.0,  # 10 second average
            level=AlertLevel.WARNING,
            message_template="High average transaction duration: {avg_duration:.2f}s",
            cooldown_seconds=300
        ))
        
        # Low throughput alert
        self.add_alert_rule(AlertRule(
            name="low_throughput",
            condition=lambda m: m.throughput < 1.0 and m.total_transactions > 0,  # < 1 TPS
            level=AlertLevel.WARNING,
            message_template="Low transaction throughput: {throughput:.2f} TPS",
            cooldown_seconds=600
        ))
        
        # Critical error rate alert
        self.add_alert_rule(AlertRule(
            name="critical_error_rate",
            condition=lambda m: m.error_rate > 0.20,  # 20% error rate
            level=AlertLevel.CRITICAL,
            message_template="Critical error rate detected: {error_rate:.2%}",
            cooldown_seconds=60
        ))
    
    async def _background_monitor(self) -> None:
        """Background monitoring and aggregation task"""
        
        while not self._shutdown:
            try:
                # Generate aggregated metrics
                metrics = self.get_aggregated_metrics(1)  # 1 minute window
                
                # Store historical metrics
                with self.lock:
                    self.historical_metrics.append({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "metrics": metrics.__dict__
                    })
                
                # Check alert rules
                await self._check_alerts(metrics)
                
                # Clean up old histogram data
                self._cleanup_histograms()
                
                await asyncio.sleep(self.aggregation_interval)
                
            except Exception as e:
                logger.error("Error in background monitoring: %s", str(e))
                await asyncio.sleep(10)
    
    async def _check_alerts(self, metrics: AggregatedMetrics) -> None:
        """Check alert rules and trigger notifications"""
        
        for alert_rule in self.alert_rules:
            try:
                if alert_rule.should_trigger(metrics):
                    message = alert_rule.format_message(metrics)
                    
                    logger.warning("Performance alert triggered: %s - %s", 
                                 alert_rule.name, message)
                    
                    # Notify callbacks
                    for callback in self.alert_callbacks:
                        try:
                            await asyncio.get_event_loop().run_in_executor(
                                None, callback, alert_rule.name, alert_rule.level, message
                            )
                        except Exception as e:
                            logger.error("Alert callback failed: %s", str(e))
                            
            except Exception as e:
                logger.error("Error checking alert rule %s: %s", alert_rule.name, str(e))
    
    def _cleanup_histograms(self) -> None:
        """Clean up old histogram data"""
        
        with self.lock:
            for name, values in self.histograms.items():
                if len(values) > 1000:
                    # Keep only recent 1000 values
                    self.histograms[name] = values[-1000:]
    
    async def shutdown(self) -> None:
        """
Graceful shutdown of performance monitor"""
        logger.info("Shutting down PerformanceMonitor...")
        
        self._shutdown = True
        
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("PerformanceMonitor shutdown complete")
