"""
Cache Metrics Configuration for IA-Influencer Agent Platform
============================================================

Advanced cache metrics collection, monitoring, and analytics
for performance optimization and operational insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import asyncio
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque
from pydantic import BaseModel, validator


class MetricType(str, Enum):
    """Types of cache metrics"""
    COUNTER = "counter"  # Cumulative count
    GAUGE = "gauge"  # Current value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Time-based measurements
    RATE = "rate"  # Rate per time unit


class AggregationMethod(str, Enum):
    """Aggregation methods for metrics"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    MEDIAN = "median"
    STDDEV = "stddev"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class MetricValue:
    """Individual metric value with metadata"""
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    region: Optional[str] = None


@dataclass
class MetricDefinition:
    """Cache metric definition"""
    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    labels: List[str] = field(default_factory=list)
    aggregation_methods: List[AggregationMethod] = field(default_factory=lambda: [AggregationMethod.AVERAGE])
    retention_hours: int = 168  # 1 week
    collection_interval: int = 60  # seconds
    enabled: bool = True


@dataclass
class AlertRule:
    """Alert rule for cache metrics"""
    name: str
    metric_name: str
    condition: str  # e.g., "> 0.9", "< 0.1", "== 0"
    threshold_value: float
    severity: AlertSeverity
    duration_minutes: int = 5  # Alert after condition persists for this duration
    cooldown_minutes: int = 15  # Wait before re-alerting
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    def evaluate_condition(self, value: float) -> bool:
        """Evaluate alert condition"""
        condition = self.condition.strip()
        
        if condition.startswith(">="):
            return value >= self.threshold_value
        elif condition.startswith("<="):
            return value <= self.threshold_value
        elif condition.startswith(">"):
            return value > self.threshold_value
        elif condition.startswith("<"):
            return value < self.threshold_value
        elif condition.startswith("=="):
            return abs(value - self.threshold_value) < 0.001
        elif condition.startswith("!="):
            return abs(value - self.threshold_value) >= 0.001
        
        return False


class CacheMetricsConfig(BaseModel):
    """
    Comprehensive cache metrics configuration
    """
    
    # General settings
    enabled: bool = True
    collection_enabled: bool = True
    export_enabled: bool = True
    
    # Collection settings
    default_collection_interval: int = 60  # seconds
    batch_size: int = 1000
    max_queue_size: int = 100000
    collection_timeout: int = 30  # seconds
    
    # Metric definitions
    metric_definitions: List[MetricDefinition] = field(default_factory=list)
    
    # Retention settings
    default_retention_hours: int = 168  # 1 week
    high_frequency_retention_hours: int = 24  # 1 day for high-freq metrics
    aggregated_retention_days: int = 90  # 90 days for aggregated data
    
    # Storage settings
    storage_backend: str = "prometheus"  # prometheus, influxdb, elasticsearch
    storage_connection_string: str = ""
    compression_enabled: bool = True
    
    # Aggregation settings
    enable_aggregation: bool = True
    aggregation_intervals: List[int] = field(default_factory=lambda: [300, 900, 3600])  # 5min, 15min, 1hour
    aggregation_worker_count: int = 2
    
    # Multi-tenant metrics
    tenant_isolation: bool = True
    per_tenant_metrics: bool = True
    tenant_quota_enabled: bool = True
    max_metrics_per_tenant: int = 10000
    
    # Performance monitoring
    track_cache_operations: bool = True
    track_hit_ratios: bool = True
    track_response_times: bool = True
    track_memory_usage: bool = True
    track_connection_metrics: bool = True
    track_error_rates: bool = True
    
    # Alerting
    alerting_enabled: bool = True
    alert_rules: List[AlertRule] = field(default_factory=list)
    alert_evaluation_interval: int = 60  # seconds
    
    # Export settings
    prometheus_port: int = 9090
    prometheus_path: str = "/metrics"
    influxdb_database: str = "cache_metrics"
    elasticsearch_index_pattern: str = "cache-metrics-*"
    
    # Dashboard integration
    grafana_integration: bool = False
    grafana_dashboard_uid: Optional[str] = None
    custom_dashboards: List[str] = field(default_factory=list)
    
    # Sampling and filtering
    sampling_enabled: bool = False
    sampling_rate: float = 1.0  # 1.0 = 100% sampling
    metric_filters: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('sampling_rate')
    def validate_sampling_rate(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Sampling rate must be between 0.0 and 1.0")
        return v
    
    @validator('default_collection_interval')
    def validate_collection_interval(cls, v):
        if v <= 0:
            raise ValueError("Collection interval must be positive")
        return v
    
    def add_metric_definition(self, metric_def: MetricDefinition):
        """Add metric definition"""
        # Check for duplicate names
        if any(m.name == metric_def.name for m in self.metric_definitions):
            raise ValueError(f"Metric definition with name '{metric_def.name}' already exists")
        
        self.metric_definitions.append(metric_def)
    
    def add_alert_rule(self, alert_rule: AlertRule):
        """Add alert rule"""
        # Check if metric exists
        if not any(m.name == alert_rule.metric_name for m in self.metric_definitions):
            raise ValueError(f"Metric '{alert_rule.metric_name}' not found in definitions")
        
        # Check for duplicate names
        if any(a.name == alert_rule.name for a in self.alert_rules):
            raise ValueError(f"Alert rule with name '{alert_rule.name}' already exists")
        
        self.alert_rules.append(alert_rule)
    
    def get_metric_definition(self, name: str) -> Optional[MetricDefinition]:
        """Get metric definition by name"""
        for metric_def in self.metric_definitions:
            if metric_def.name == name:
                return metric_def
        return None
    
    def get_enabled_metrics(self) -> List[MetricDefinition]:
        """Get list of enabled metrics"""



        return [m for m in self.metric_definitions if m.enabled]
    
    def get_enabled_alerts(self) -> List[AlertRule]:
        """Get list of enabled alert rules"""



        return [a for a in self.alert_rules if a.enabled]
    
    def should_collect_metric(self, metric_name: str, labels: Dict[str, str] = None) -> bool:
        """Check if metric should be collected based on filters"""
        if not self.collection_enabled:
            return False
        
        # Check metric filters
        if self.metric_filters and metric_name not in self.metric_filters:
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in metric_name:
                return False
        
        # Check sampling
        if self.sampling_enabled and self.sampling_rate < 1.0:
            import random
            return random.random() < self.sampling_rate
        
        return True


class MetricsCollector:
    """
    Cache metrics collector and processor
    """
    
    def __init__(self, config: CacheMetricsConfig):
        self.config = config
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.alert_states: Dict[str, Dict[str, Any]] = {}
        self.collection_task = None
        self.aggregation_task = None
        self.alert_task = None
        self.running = False
    
    async def start(self):
        """Start metrics collection"""
        if self.running:
            return
        
        self.running = True
        
        if self.config.collection_enabled:
            self.collection_task = asyncio.create_task(self._collection_loop())
        
        if self.config.enable_aggregation:
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
        
        if self.config.alerting_enabled:
            self.alert_task = asyncio.create_task(self._alert_evaluation_loop())
    
    async def stop(self):
        """Stop metrics collection"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel tasks
        for task in [self.collection_task, self.aggregation_task, self.alert_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    
    def record_metric(self, metric_name: str, value: Union[int, float], 
                     labels: Dict[str, str] = None, tenant_id: Optional[str] = None):
        """Record a metric value"""
        if not self.config.should_collect_metric(metric_name, labels):
            return
        
        metric_value = MetricValue(
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            tenant_id=tenant_id
        )
        
        self.metrics_buffer[metric_name].append(metric_value)
    
    def record_cache_hit(self, tenant_id: Optional[str] = None, region: Optional[str] = None):
        """Record cache hit"""
        labels = {}
        if region:
            labels["region"] = region
        
        self.record_metric("cache_hits_total", 1, labels, tenant_id)
    
    def record_cache_miss(self, tenant_id: Optional[str] = None, region: Optional[str] = None):
        """Record cache miss"""
        labels = {}
        if region:
            labels["region"] = region
        
        self.record_metric("cache_misses_total", 1, labels, tenant_id)
    
    def record_cache_set(self, tenant_id: Optional[str] = None, region: Optional[str] = None):
        """Record cache set operation"""
        labels = {}
        if region:
            labels["region"] = region
        
        self.record_metric("cache_sets_total", 1, labels, tenant_id)
    
    def record_cache_delete(self, tenant_id: Optional[str] = None, region: Optional[str] = None):
        """Record cache delete operation"""
        labels = {}
        if region:
            labels["region"] = region
        
        self.record_metric("cache_deletes_total", 1, labels, tenant_id)
    
    def record_response_time(self, operation: str, duration_ms: float, 
                           tenant_id: Optional[str] = None, region: Optional[str] = None):
        """Record operation response time"""
        labels = {"operation": operation}
        if region:
            labels["region"] = region
        
        self.record_metric("cache_operation_duration_ms", duration_ms, labels, tenant_id)
    
    def record_memory_usage(self, memory_mb: float, node_id: Optional[str] = None):
        """Record memory usage"""
        labels = {}
        if node_id:
            labels["node"] = node_id
        
        self.record_metric("cache_memory_usage_mb", memory_mb, labels)
    
    def record_connection_count(self, connection_count: int, pool_name: str = "default"):
        """Record connection pool metrics"""
        labels = {"pool": pool_name}
        self.record_metric("cache_connections_active", connection_count, labels)
    
    def record_error(self, error_type: str, tenant_id: Optional[str] = None):
        """Record cache error"""
        labels = {"error_type": error_type}
        self.record_metric("cache_errors_total", 1, labels, tenant_id)
    
    def get_hit_ratio(self, window_minutes: int = 5, tenant_id: Optional[str] = None) -> float:
        """Calculate cache hit ratio for time window"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        hits = self._get_metric_count("cache_hits_total", start_time, end_time, tenant_id)
        misses = self._get_metric_count("cache_misses_total", start_time, end_time, tenant_id)
        
        total = hits + misses
        return hits / total if total > 0 else 0.0
    
    def get_average_response_time(self, operation: str, window_minutes: int = 5, 
                                tenant_id: Optional[str] = None) -> float:
        """Get average response time for operation"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        values = self._get_metric_values("cache_operation_duration_ms", start_time, end_time, 
                                       tenant_id, {"operation": operation})
        
        return statistics.mean(values) if values else 0.0
    
    def get_percentile_response_time(self, operation: str, percentile: float, 
                                   window_minutes: int = 5, tenant_id: Optional[str] = None) -> float:
        """Get percentile response time for operation"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        values = self._get_metric_values("cache_operation_duration_ms", start_time, end_time, 
                                       tenant_id, {"operation": operation})
        
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100.0)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_metrics_summary(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        window_minutes = 5
        
        return {
            "hit_ratio": self.get_hit_ratio(window_minutes, tenant_id),
            "avg_response_time_ms": self.get_average_response_time("get", window_minutes, tenant_id),
            "p95_response_time_ms": self.get_percentile_response_time("get", 95, window_minutes, tenant_id),
            "p99_response_time_ms": self.get_percentile_response_time("get", 99, window_minutes, tenant_id),
            "error_rate": self._get_error_rate(window_minutes, tenant_id),
            "operations_per_second": self._get_operations_per_second(window_minutes, tenant_id),
            "memory_usage_mb": self._get_current_memory_usage(),
            "active_connections": self._get_current_connection_count()
        }
    
    async def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                await self._process_metrics_buffer()
                await asyncio.sleep(self.config.default_collection_interval)
            except Exception as e:
                # Log error and continue
                await asyncio.sleep(self.config.default_collection_interval)
    
    async def _aggregation_loop(self):
        """Metrics aggregation loop"""
        while self.running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(300)  # Aggregate every 5 minutes
            except Exception as e:
                # Log error and continue
                await asyncio.sleep(300)
    
    async def _alert_evaluation_loop(self):
        """Alert evaluation loop"""
        while self.running:
            try:
                await self._evaluate_alerts()
                await asyncio.sleep(self.config.alert_evaluation_interval)
            except Exception as e:
                # Log error and continue
                await asyncio.sleep(self.config.alert_evaluation_interval)
    
    async def _process_metrics_buffer(self):
        """Process buffered metrics"""
        for metric_name, buffer in self.metrics_buffer.items():
            if not buffer:
                continue
            
            # Export metrics to configured backend
            if self.config.export_enabled:
                await self._export_metrics(metric_name, list(buffer))
            
            # Clear processed metrics (keep recent ones)
            while len(buffer) > self.config.batch_size:
                buffer.popleft()
    
    async def _export_metrics(self, metric_name: str, values: List[MetricValue]):
        """Export metrics to configured backend"""
        # Implementation would depend on the selected storage backend
        # This is a placeholder for the export logic
        pass
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for different time intervals"""
        for interval in self.config.aggregation_intervals:
            for metric_name in self.metrics_buffer.keys():
                await self._aggregate_metric_for_interval(metric_name, interval)
    
    async def _aggregate_metric_for_interval(self, metric_name: str, interval_seconds: int):
        """Aggregate specific metric for time interval"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=interval_seconds)
        
        values = self._get_metric_values(metric_name, start_time, end_time)
        
        if not values:
            return
        
        # Calculate aggregations
        aggregation_key = f"{metric_name}_{interval_seconds}s"
        self.aggregated_metrics[aggregation_key] = {
            "sum": sum(values),
            "count": len(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "timestamp": end_time,
            "interval_seconds": interval_seconds
        }
    
    async def _evaluate_alerts(self):
        """Evaluate all alert rules"""
        for alert_rule in self.config.get_enabled_alerts():
            await self._evaluate_single_alert(alert_rule)
    
    async def _evaluate_single_alert(self, alert_rule: AlertRule):
        """Evaluate single alert rule"""
        # Get current metric value
        current_value = self._get_current_metric_value(alert_rule.metric_name)
        
        if current_value is None:
            return
        
        # Evaluate condition
        condition_met = alert_rule.evaluate_condition(current_value)
        
        # Get alert state
        alert_key = alert_rule.name
        if alert_key not in self.alert_states:
            self.alert_states[alert_key] = {
                "active": False,
                "condition_met_since": None,
                "last_triggered": None,
                "trigger_count": 0
            }
        
        alert_state = self.alert_states[alert_key]
        current_time = datetime.utcnow()
        
        if condition_met:
            if not alert_state["condition_met_since"]:
                alert_state["condition_met_since"] = current_time
            
            # Check if condition has been met for required duration
            duration = (current_time - alert_state["condition_met_since"]).total_seconds() / 60
            
            if duration >= alert_rule.duration_minutes:
                # Check cooldown period
                if (not alert_state["last_triggered"] or 
                    (current_time - alert_state["last_triggered"]).total_seconds() / 60 >= alert_rule.cooldown_minutes):
                    
                    # Trigger alert
                    await self._trigger_alert(alert_rule, current_value)
                    alert_state["active"] = True
                    alert_state["last_triggered"] = current_time
                    alert_state["trigger_count"] += 1
        else:
            # Condition no longer met
            alert_state["condition_met_since"] = None
            if alert_state["active"]:
                # Resolve alert
                await self._resolve_alert(alert_rule, current_value)
                alert_state["active"] = False
    
    async def _trigger_alert(self, alert_rule: AlertRule, current_value: float):
        """Trigger alert notification"""
        # Implementation would send actual alerts (email, Slack, webhook, etc.)
        # This is a placeholder for the alerting logic
        pass
    
    async def _resolve_alert(self, alert_rule: AlertRule, current_value: float):
        """Resolve alert notification"""
        # Implementation would send alert resolution notifications
        # This is a placeholder for the alert resolution logic
        pass
    
    def _get_metric_count(self, metric_name: str, start_time: datetime, end_time: datetime, 
                         tenant_id: Optional[str] = None) -> int:
        """Get count of metric occurrences in time window"""
        if metric_name not in self.metrics_buffer:
            return 0
        
        count = 0
        for metric_value in self.metrics_buffer[metric_name]:
            if (start_time <= metric_value.timestamp <= end_time and
                (tenant_id is None or metric_value.tenant_id == tenant_id)):
                count += metric_value.value
        
        return count
    
    def _get_metric_values(self, metric_name: str, start_time: datetime, end_time: datetime, 
                          tenant_id: Optional[str] = None, 
                          labels_filter: Dict[str, str] = None) -> List[float]:
        """Get metric values in time window"""
        if metric_name not in self.metrics_buffer:
            return []
        
        values = []
        for metric_value in self.metrics_buffer[metric_name]:
            if (start_time <= metric_value.timestamp <= end_time and
                (tenant_id is None or metric_value.tenant_id == tenant_id)):
                
                # Check label filters
                if labels_filter:
                    if not all(metric_value.labels.get(k) == v for k, v in labels_filter.items()):
                        continue
                
                values.append(metric_value.value)
        
        return values
    
    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for metric"""
        if metric_name not in self.metrics_buffer:
            return None
        
        buffer = self.metrics_buffer[metric_name]
        if not buffer:
            return None
        
        # Return most recent value
        return buffer[-1].value
    
    def _get_error_rate(self, window_minutes: int, tenant_id: Optional[str] = None) -> float:
        """Calculate error rate for time window"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        errors = self._get_metric_count("cache_errors_total", start_time, end_time, tenant_id)
        total_ops = (self._get_metric_count("cache_hits_total", start_time, end_time, tenant_id) +
                    self._get_metric_count("cache_misses_total", start_time, end_time, tenant_id) +
                    self._get_metric_count("cache_sets_total", start_time, end_time, tenant_id))
        
        return errors / total_ops if total_ops > 0 else 0.0
    
    def _get_operations_per_second(self, window_minutes: int, tenant_id: Optional[str] = None) -> float:
        """Calculate operations per second for time window"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        total_ops = (self._get_metric_count("cache_hits_total", start_time, end_time, tenant_id) +
                    self._get_metric_count("cache_misses_total", start_time, end_time, tenant_id) +
                    self._get_metric_count("cache_sets_total", start_time, end_time, tenant_id) +
                    self._get_metric_count("cache_deletes_total", start_time, end_time, tenant_id))
        
        window_seconds = window_minutes * 60
        return total_ops / window_seconds if window_seconds > 0 else 0.0
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage"""



        return self._get_current_metric_value("cache_memory_usage_mb") or 0.0
    
    def _get_current_connection_count(self) -> int:
        """Get current connection count"""



        return int(self._get_current_metric_value("cache_connections_active") or 0)


# Standard metric definitions for cache systems
STANDARD_METRICS = [
    MetricDefinition("cache_hits_total", MetricType.COUNTER, "Total cache hits", "count"),
    MetricDefinition("cache_misses_total", MetricType.COUNTER, "Total cache misses", "count"),
    MetricDefinition("cache_sets_total", MetricType.COUNTER, "Total cache set operations", "count"),
    MetricDefinition("cache_deletes_total", MetricType.COUNTER, "Total cache delete operations", "count"),
    MetricDefinition("cache_errors_total", MetricType.COUNTER, "Total cache errors", "count"),
    MetricDefinition("cache_operation_duration_ms", MetricType.HISTOGRAM, "Operation duration", "milliseconds"),
    MetricDefinition("cache_memory_usage_mb", MetricType.GAUGE, "Memory usage", "megabytes"),
    MetricDefinition("cache_connections_active", MetricType.GAUGE, "Active connections", "count"),
    MetricDefinition("cache_keys_total", MetricType.GAUGE, "Total cached keys", "count"),
    MetricDefinition("cache_key_size_bytes", MetricType.HISTOGRAM, "Key size distribution", "bytes"),
    MetricDefinition("cache_value_size_bytes", MetricType.HISTOGRAM, "Value size distribution", "bytes"),
    MetricDefinition("cache_ttl_seconds", MetricType.HISTOGRAM, "TTL distribution", "seconds"),
    MetricDefinition("cache_evictions_total", MetricType.COUNTER, "Total evictions", "count"),
    MetricDefinition("cache_network_bytes_sent", MetricType.COUNTER, "Network bytes sent", "bytes"),
    MetricDefinition("cache_network_bytes_received", MetricType.COUNTER, "Network bytes received", "bytes")
]

# Standard alert rules
STANDARD_ALERTS = [
    AlertRule("low_hit_ratio", "cache_hit_ratio", "< 0.8", 0.8, AlertSeverity.MEDIUM, 5, 15),
    AlertRule("very_low_hit_ratio", "cache_hit_ratio", "< 0.5", 0.5, AlertSeverity.HIGH, 3, 10),
    AlertRule("high_error_rate", "cache_error_rate", "> 0.05", 0.05, AlertSeverity.HIGH, 2, 10),
    AlertRule("critical_error_rate", "cache_error_rate", "> 0.1", 0.1, AlertSeverity.CRITICAL, 1, 5),
    AlertRule("slow_response_time", "cache_avg_response_time", "> 1000", 1000, AlertSeverity.MEDIUM, 5, 15),
    AlertRule("very_slow_response_time", "cache_avg_response_time", "> 5000", 5000, AlertSeverity.HIGH, 2, 10),
    AlertRule("high_memory_usage", "cache_memory_usage_percent", "> 85", 85, AlertSeverity.MEDIUM, 10, 30),
    AlertRule("critical_memory_usage", "cache_memory_usage_percent", "> 95", 95, AlertSeverity.CRITICAL, 5, 15)
]

# Default configurations
DEFAULT_CONFIG = CacheMetricsConfig(
    metric_definitions=STANDARD_METRICS,
    alert_rules=STANDARD_ALERTS
)

PRODUCTION_CONFIG = CacheMetricsConfig(
    enabled=True,
    collection_enabled=True,
    export_enabled=True,
    metric_definitions=STANDARD_METRICS,
    alert_rules=STANDARD_ALERTS,
    default_collection_interval=30,  # More frequent collection
    batch_size=2000,
    enable_aggregation=True,
    aggregation_intervals=[300, 900, 3600, 86400],  # 5min, 15min, 1h, 1day
    alerting_enabled=True,
    tenant_isolation=True,
    per_tenant_metrics=True,
    prometheus_port=9090,
    grafana_integration=True
)

DEVELOPMENT_CONFIG = CacheMetricsConfig(
    enabled=True,
    collection_enabled=True,
    export_enabled=False,
    metric_definitions=STANDARD_METRICS[:8],  # Basic metrics only
    alert_rules=STANDARD_ALERTS[:4],  # Basic alerts only
    default_collection_interval=60,
    alerting_enabled=False,
    tenant_isolation=False,
    enable_aggregation=False
)
