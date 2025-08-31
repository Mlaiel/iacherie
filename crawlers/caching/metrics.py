#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Metrics - Performance Monitoring and Analytics
===================================================

Advanced metrics collection and analysis for cache performance
with real-time monitoring, alerting, and optimization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Cache metric types."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class MetricSeverity(Enum):
    """Metric alert severity levels."""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MetricValue:
    """Individual metric measurement."""    timestamp: datetime
    value: Union[int, float]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricAlert:
    """Metric alert configuration."""    alert_id: str
    metric_name: str
    condition: str  # e.g., "> 0.9", "< 1000"
    severity: MetricSeverity
    message: str
    enabled: bool = True
    cooldown_seconds: int = 300
    last_triggered: Optional[datetime] = None

@dataclass
class CachePerformanceSnapshot:
    """Cache performance snapshot."""    timestamp: datetime
    hit_rate: float
    miss_rate: float
    total_operations: int
    average_response_time: float
    memory_usage: int
    key_count: int
    error_rate: float
    throughput: float

class CacheMetrics:
    """    Cache metrics collection and analysis.
    
    Features:
    - Real-time metrics collection
    - Performance analytics
    - Alert management
    - Historical trending
    - Optimization insights
    """    
    def __init__(self, retention_hours: int = 24, collection_interval: int = 60):
        """        Initialize cache metrics.
        
        Args:
            retention_hours: How long to keep metrics data
            collection_interval: Metrics collection interval in seconds
        """        self.retention_hours = retention_hours
        self.collection_interval = collection_interval
        self.logger = logging.getLogger(f"{__name__}.CacheMetrics")
        
        # Metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self._max_samples()))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Performance tracking
        self.operation_times: deque = deque(maxlen=1000)
        self.error_count = 0
        self.total_operations = 0
        self.start_time = datetime.now()
        
        # Alerts
        self.alerts: Dict[str, MetricAlert] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        # Collection task
        self._collection_task: Optional[asyncio.Task] = None
        self._running = False
        
        self.logger.info("Cache metrics initialized")
    
    def _max_samples(self) -> int:
        """Calculate maximum samples to keep."""        return int(self.retention_hours * 3600 / self.collection_interval)
    
    async def start_collection(self) -> None:
        """Start metrics collection."""        if self._collection_task is not None:
            return
        
        self._running = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        self.logger.info("Started metrics collection")
    
    async def stop_collection(self) -> None:
        """Stop metrics collection."""        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            self._collection_task = None
        self.logger.info("Stopped metrics collection")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop."""        try:
            while self._running:
                await self._collect_metrics()
                await self._check_alerts()
                await asyncio.sleep(self.collection_interval)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
    
    async def _collect_metrics(self) -> None:
        """Collect current metrics snapshot."""        try:
            timestamp = datetime.now()
            
            # Calculate derived metrics
            hit_rate = self._calculate_hit_rate()
            miss_rate = 1.0 - hit_rate
            error_rate = self._calculate_error_rate()
            throughput = self._calculate_throughput()
            avg_response_time = self._calculate_average_response_time()
            
            # Record metrics
            self._record_metric("hit_rate", hit_rate, timestamp)
            self._record_metric("miss_rate", miss_rate, timestamp)
            self._record_metric("error_rate", error_rate, timestamp)
            self._record_metric("throughput", throughput, timestamp)
            self._record_metric("average_response_time", avg_response_time, timestamp)
            self._record_metric("total_operations", self.total_operations, timestamp)
            
            # Memory and system metrics would be collected here
            # For now, we'll use placeholder values
            self._record_metric("memory_usage", self.gauges.get("memory_usage", 0), timestamp)
            self._record_metric("key_count", self.gauges.get("key_count", 0), timestamp)
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    def _record_metric(self, name: str, value: Union[int, float], 
                      timestamp: datetime, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value."""        metric_value = MetricValue(
            timestamp=timestamp,
            value=value,
            tags=tags or {}
        )
        self.metrics[name].append(metric_value)
    
    def increment_counter(self, name: str, value: int = 1, 
                         tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""        self.counters[name] += value
        self.total_operations += value
        
        # Record for trending
        self._record_metric(name, self.counters[name], datetime.now(), tags)
    
    def set_gauge(self, name: str, value: Union[int, float],
                 tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""        self.gauges[name] = value
        self._record_metric(name, value, datetime.now(), tags)
    
    def record_timer(self, name: str, duration: float,
                    tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timer metric."""        self.timers[name].append(duration)
        self.operation_times.append(duration)
        
        # Keep only recent timer values
        if len(self.timers[name]) > 1000:
            self.timers[name] = self.timers[name][-1000:]
        
        self._record_metric(name, duration, datetime.now(), tags)
    
    def record_operation(self, operation: str, duration: float, 
                        success: bool = True, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a cache operation."""        self.total_operations += 1
        
        # Record timing
        self.record_timer(f"{operation}_time", duration, tags)
        
        # Record success/error
        if success:
            self.increment_counter(f"{operation}_success", tags=tags)
        else:
            self.increment_counter(f"{operation}_error", tags=tags)
            self.error_count += 1
    
    def record_hit(self, key: str, cache_level: str = "default") -> None:
        """Record a cache hit."""        self.increment_counter("cache_hits", tags={"level": cache_level})
        self.increment_counter("cache_operations")
    
    def record_miss(self, key: str, cache_level: str = "default") -> None:
        """Record a cache miss."""        self.increment_counter("cache_misses", tags={"level": cache_level})
        self.increment_counter("cache_operations")
    
    def record_eviction(self, key: str, reason: str = "lru") -> None:
        """Record a cache eviction."""        self.increment_counter("cache_evictions", tags={"reason": reason})
    
    def _calculate_hit_rate(self) -> float:
        """Calculate current hit rate."""        hits = self.counters.get("cache_hits", 0)
        misses = self.counters.get("cache_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return hits / total
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""        if self.total_operations == 0:
            return 0.0
        
        return self.error_count / self.total_operations
    
    def _calculate_throughput(self) -> float:
        """Calculate operations per second."""        uptime = (datetime.now() - self.start_time).total_seconds()
        
        if uptime == 0:
            return 0.0
        
        return self.total_operations / uptime
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time."""        if not self.operation_times:
            return 0.0
        
        return sum(self.operation_times) / len(self.operation_times)
    
    async def get_metrics(self, metric_names: Optional[List[str]] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, List[MetricValue]]:
        """        Get metrics data.
        
        Args:
            metric_names: Specific metrics to retrieve
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            Metrics data
        """        result = {}
        
        metrics_to_get = metric_names or list(self.metrics.keys())
        
        for metric_name in metrics_to_get:
            if metric_name not in self.metrics:
                continue
            
            metric_values = list(self.metrics[metric_name])
            
            # Apply time filters
            if start_time or end_time:
                filtered_values = []
                for value in metric_values:
                    if start_time and value.timestamp < start_time:
                        continue
                    if end_time and value.timestamp > end_time:
                        continue
                    filtered_values.append(value)
                metric_values = filtered_values
            
            result[metric_name] = metric_values
        
        return result
    
    async def get_performance_snapshot(self) -> CachePerformanceSnapshot:
        """Get current performance snapshot."""        return CachePerformanceSnapshot(
            timestamp=datetime.now(),
            hit_rate=self._calculate_hit_rate(),
            miss_rate=1.0 - self._calculate_hit_rate(),
            total_operations=self.total_operations,
            average_response_time=self._calculate_average_response_time(),
            memory_usage=int(self.gauges.get("memory_usage", 0)),
            key_count=int(self.gauges.get("key_count", 0)),
            error_rate=self._calculate_error_rate(),
            throughput=self._calculate_throughput()
        )
    
    async def add_alert(self, alert: MetricAlert) -> bool:
        """Add metric alert."""        try:
            self.alerts[alert.alert_id] = alert
            self.logger.info(f"Added alert: {alert.alert_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding alert: {e}")
            return False
    
    async def remove_alert(self, alert_id: str) -> bool:
        """Remove metric alert."""        try:
            if alert_id in self.alerts:
                del self.alerts[alert_id]
                self.logger.info(f"Removed alert: {alert_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing alert: {e}")
            return False
    
    async def _check_alerts(self) -> None:
        """Check all configured alerts."""        for alert in self.alerts.values():
            if not alert.enabled:
                continue
            
            try:
                await self._evaluate_alert(alert)
            except Exception as e:
                self.logger.error(f"Error evaluating alert {alert.alert_id}: {e}")
    
    async def _evaluate_alert(self, alert: MetricAlert) -> None:
        """Evaluate individual alert condition."""        # Check cooldown
        if alert.last_triggered:
            cooldown_expires = alert.last_triggered + timedelta(seconds=alert.cooldown_seconds)
            if datetime.now() < cooldown_expires:
                return
        
        # Get current metric value
        current_value = None
        if alert.metric_name in self.counters:
            current_value = self.counters[alert.metric_name]
        elif alert.metric_name in self.gauges:
            current_value = self.gauges[alert.metric_name]
        elif alert.metric_name == "hit_rate":
            current_value = self._calculate_hit_rate()
        elif alert.metric_name == "error_rate":
            current_value = self._calculate_error_rate()
        elif alert.metric_name == "throughput":
            current_value = self._calculate_throughput()
        
        if current_value is None:
            return
        
        # Evaluate condition
        try:
            condition_met = self._evaluate_condition(current_value, alert.condition)
            
            if condition_met:
                await self._trigger_alert(alert, current_value)
                
        except Exception as e:
            self.logger.error(f"Error evaluating condition for {alert.alert_id}: {e}")
    
    def _evaluate_condition(self, value: Union[int, float], condition: str) -> bool:
        """Evaluate alert condition."""        # Simple condition evaluation
        # In production, use a proper expression evaluator
        try:
            return eval(f"{value} {condition}")
        except Exception:
            return False
    
    async def _trigger_alert(self, alert: MetricAlert, current_value: Union[int, float]) -> None:
        """Trigger alert notification."""        alert.last_triggered = datetime.now()
        
        alert_event = {
            "alert_id": alert.alert_id,
            "metric_name": alert.metric_name,
            "current_value": current_value,
            "condition": alert.condition,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.last_triggered.isoformat()
        }
        
        self.alert_history.append(alert_event)
        
        # Keep only recent alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        self.logger.warning(f"ALERT [{alert.severity.value}] {alert.message} (value: {current_value})")
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alert history."""        return self.alert_history[-limit:]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""        snapshot = await self.get_performance_snapshot()
        
        return {
            "performance": {
                "hit_rate": snapshot.hit_rate,
                "miss_rate": snapshot.miss_rate,
                "error_rate": snapshot.error_rate,
                "throughput": snapshot.throughput,
                "average_response_time": snapshot.average_response_time
            },
            "operations": {
                "total_operations": snapshot.total_operations,
                "cache_hits": self.counters.get("cache_hits", 0),
                "cache_misses": self.counters.get("cache_misses", 0),
                "cache_evictions": self.counters.get("cache_evictions", 0),
                "errors": self.error_count
            },
            "resources": {
                "memory_usage": snapshot.memory_usage,
                "key_count": snapshot.key_count
            },
            "alerts": {
                "total_alerts": len(self.alerts),
                "active_alerts": sum(1 for alert in self.alerts.values() if alert.enabled),
                "recent_triggers": len([
                    event for event in self.alert_history
                    if datetime.fromisoformat(event["timestamp"]) > datetime.now() - timedelta(hours=1)
                ])
            },
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }

class PerformanceMonitor:
    """    Advanced performance monitoring for cache systems.
    
    Provides detailed performance analysis and optimization recommendations.
    """    
    def __init__(self, metrics: CacheMetrics):
        """Initialize performance monitor."""        self.metrics = metrics
        self.logger = logging.getLogger(f"{__name__}.PerformanceMonitor")
        
        # Performance thresholds
        self.thresholds = {
            "hit_rate_warning": 0.8,
            "hit_rate_critical": 0.6,
            "response_time_warning": 100.0,  # ms
            "response_time_critical": 500.0,  # ms
            "error_rate_warning": 0.01,  # 1%
            "error_rate_critical": 0.05,  # 5%
            "memory_usage_warning": 0.8,  # 80%
            "memory_usage_critical": 0.95  # 95%
        }
        
        self.logger.info("Performance monitor initialized")
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current cache performance."""        snapshot = await self.metrics.get_performance_snapshot()
        
        analysis = {
            "overall_health": "healthy",
            "issues": [],
            "recommendations": [],
            "scores": {}
        }
        
        # Analyze hit rate
        hit_rate_score = self._analyze_hit_rate(snapshot.hit_rate, analysis)
        analysis["scores"]["hit_rate"] = hit_rate_score
        
        # Analyze response time
        response_time_score = self._analyze_response_time(snapshot.average_response_time, analysis)
        analysis["scores"]["response_time"] = response_time_score
        
        # Analyze error rate
        error_rate_score = self._analyze_error_rate(snapshot.error_rate, analysis)
        analysis["scores"]["error_rate"] = error_rate_score
        
        # Calculate overall score
        scores = list(analysis["scores"].values())
        analysis["overall_score"] = sum(scores) / len(scores) if scores else 0
        
        # Determine overall health
        if analysis["overall_score"] < 0.6:
            analysis["overall_health"] = "critical"
        elif analysis["overall_score"] < 0.8:
            analysis["overall_health"] = "warning"
        
        return analysis
    
    def _analyze_hit_rate(self, hit_rate: float, analysis: Dict[str, Any]) -> float:
        """Analyze cache hit rate."""        if hit_rate < self.thresholds["hit_rate_critical"]:
            analysis["issues"].append({
                "type": "critical",
                "metric": "hit_rate",
                "value": hit_rate,
                "description": f"Very low hit rate: {hit_rate:.1%}"
            })
            analysis["recommendations"].append(
                "Consider increasing cache size or reviewing cache policies"
            )
            return 0.2
        elif hit_rate < self.thresholds["hit_rate_warning"]:
            analysis["issues"].append({
                "type": "warning",
                "metric": "hit_rate",
                "value": hit_rate,
                "description": f"Low hit rate: {hit_rate:.1%}"
            })
            analysis["recommendations"].append(
                "Monitor cache usage patterns and consider optimization"
            )
            return 0.6
        else:
            return min(hit_rate / self.thresholds["hit_rate_warning"], 1.0)
    
    def _analyze_response_time(self, response_time: float, analysis: Dict[str, Any]) -> float:
        """Analyze cache response time."""        response_time_ms = response_time * 1000  # Convert to milliseconds
        
        if response_time_ms > self.thresholds["response_time_critical"]:
            analysis["issues"].append({
                "type": "critical",
                "metric": "response_time",
                "value": response_time_ms,
                "description": f"Very high response time: {response_time_ms:.1f}ms"
            })
            analysis["recommendations"].append(
                "Investigate performance bottlenecks in cache implementation"
            )
            return 0.2
        elif response_time_ms > self.thresholds["response_time_warning"]:
            analysis["issues"].append({
                "type": "warning",
                "metric": "response_time",
                "value": response_time_ms,
                "description": f"High response time: {response_time_ms:.1f}ms"
            })
            analysis["recommendations"].append(
                "Consider cache optimization or hardware upgrade"
            )
            return 0.6
        else:
            # Better score for lower response times
            normalized = max(0, 1 - response_time_ms / self.thresholds["response_time_warning"])
            return min(normalized, 1.0)
    
    def _analyze_error_rate(self, error_rate: float, analysis: Dict[str, Any]) -> float:
        """Analyze cache error rate."""        if error_rate > self.thresholds["error_rate_critical"]:
            analysis["issues"].append({
                "type": "critical",
                "metric": "error_rate",
                "value": error_rate,
                "description": f"High error rate: {error_rate:.1%}"
            })
            analysis["recommendations"].append(
                "Investigate cache errors and fix underlying issues"
            )
            return 0.2
        elif error_rate > self.thresholds["error_rate_warning"]:
            analysis["issues"].append({
                "type": "warning",
                "metric": "error_rate",
                "value": error_rate,
                "description": f"Elevated error rate: {error_rate:.1%}"
            })
            analysis["recommendations"].append(
                "Monitor error patterns and address common failures"
            )
            return 0.6
        else:
            # Better score for lower error rates
            normalized = max(0, 1 - error_rate / self.thresholds["error_rate_warning"])
            return min(normalized, 1.0)
