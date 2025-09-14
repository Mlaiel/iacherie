"""
Real Time Analytics Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Real-time Analytics Service
Real-time data processing and analytics for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import json
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import math

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event type enumeration"""
    USER_ACTION = "user_action"
    SYSTEM_METRIC = "system_metric"
    BUSINESS_EVENT = "business_event"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_EVENT = "error_event"
    SECURITY_EVENT = "security_event"
    CUSTOM_EVENT = "custom_event"

class AggregationType(Enum):
    """Aggregation type enumeration"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    RATE = "rate"
    UNIQUE_COUNT = "unique_count"

class TimeWindow(Enum):
    """Time window enumeration"""
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    event_type: EventType
    source: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricDefinition:
    """Metric definition for real-time calculation"""
    metric_name: str
    event_filter: Callable[[AnalyticsEvent], bool]
    aggregation_type: AggregationType
    aggregation_field: Optional[str] = None
    time_windows: List[TimeWindow] = field(default_factory=lambda: [TimeWindow.MINUTE, TimeWindow.HOUR])
    percentile: Optional[float] = None  # For percentile aggregations
    enabled: bool = True
    tags: List[str] = field(default_factory=list)

@dataclass
class MetricValue:
    """Metric value with timestamp"""
    metric_name: str
    value: float
    timestamp: float
    window: TimeWindow
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Real-time alert"""
    alert_id: str
    metric_name: str
    condition: str
    threshold: float
    current_value: float
    severity: str  # low, medium, high, critical
    message: str
    triggered_at: float
    resolved_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Dashboard:
    """Real-time dashboard configuration"""
    dashboard_id: str
    name: str
    metrics: List[str] = field(default_factory=list)
    refresh_interval: int = 60  # seconds
    filters: Dict[str, Any] = field(default_factory=dict)
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

class RealTimeAnalyticsService:
    """
    Enterprise Real-time Analytics Service
    
    Provides comprehensive real-time analytics with:
    - High-throughput event ingestion
    - Real-time metric calculation
    - Configurable time windows
    - Alert system
    - Dashboard support
    - Stream processing
    """
    
    def __init__(self, max_events_memory -> None: int = 100000) -> None:
        """Initialize real-time analytics service"""
        self.max_events_memory = max_events_memory
        
        # Event storage
        self.event_stream: deque = deque(maxlen=max_events_memory)
        self.event_index: Dict[str, List[int]] = defaultdict(list)  # source -> event indices
        
        # Metrics
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metric_values: Dict[str, Dict[TimeWindow, deque]] = defaultdict(lambda: defaultdict(deque))
        self.real_time_values: Dict[str, float] = {}
        
        # Time-windowed event storage
        self.windowed_events: Dict[TimeWindow, deque] = {
            window: deque() for window in TimeWindow
        }
        
        # Alerts
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alert_history: List[Alert] = []
        
        # Dashboards
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Performance tracking
        self.service_metrics = {
            "events_processed": 0,
            "events_per_second": 0.0,
            "processing_latency": 0.0,
            "active_metrics": 0,
            "active_alerts": 0,
            "memory_usage": 0,
            "last_event_time": 0.0
        }
        
        # Configuration
        self.config = {
            "enable_persistence": False,
            "enable_alerts": True,
            "enable_real_time_processing": True,
            "batch_processing_size": 1000,
            "metric_retention_hours": 24,
            "alert_cooldown_seconds": 300,
            "dashboard_refresh_rate": 5,
            "max_alert_history": 10000
        }
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Background tasks
        self.processing_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.alert_task: Optional[asyncio.Task] = None
        
        # Processing queue
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info("RealTimeAnalyticsService initialized")
    
    async def start(self) -> None:
        """Start the real-time analytics service"""
        try:
            # Start background processing tasks
            self.processing_task = asyncio.create_task(self._processing_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.alert_task = asyncio.create_task(self._alert_loop())
            
            # Initialize default metrics
            await self._initialize_default_metrics()
            
            logger.info("RealTimeAnalyticsService started successfully")
        except Exception as e:
            logger.error("Failed to start RealTimeAnalyticsService: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the real-time analytics service"""
        try:
            self.shutdown_event.set()
            
            # Stop background tasks
            for task in [self.processing_task, self.cleanup_task, self.alert_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("RealTimeAnalyticsService stopped successfully")
        except Exception as e:
            logger.error("Error stopping RealTimeAnalyticsService: %s", e)
    
    async def ingest_event(self, event -> None: AnalyticsEvent) -> None:
        """Ingest a single analytics event"""
        if not self.config["enable_real_time_processing"]:
            return
        
        # Add to processing queue for async processing
        await self.processing_queue.put(event)
    
    async def ingest_events_batch(self, events -> None: List[AnalyticsEvent]) -> None:
        """Ingest a batch of analytics events"""
        if not self.config["enable_real_time_processing"]:
            return
        
        for event in events:
            await self.processing_queue.put(event)
    
    async def register_metric(self, metric_def -> None: MetricDefinition) -> None:
        """Register a new metric definition"""
        async with self._lock:
            self.metric_definitions[metric_def.metric_name] = metric_def
            
            # Initialize metric storage
            for window in metric_def.time_windows:
                if metric_def.metric_name not in self.metric_values:
                    self.metric_values[metric_def.metric_name][window] = deque()
            
            self.service_metrics["active_metrics"] = len(self.metric_definitions)
        
        logger.info("Registered metric: %s", metric_def.metric_name)
    
    async def get_real_time_metrics(
        self,
        metric_names: Optional[List[str]] = None,
        time_window: TimeWindow = TimeWindow.MINUTE
    ) -> Dict[str, float]:
        """Get current real-time metric values"""
        async with self._lock:
            if metric_names is None:
                metric_names = list(self.metric_definitions.keys())
            
            current_metrics = {}
            
            for metric_name in metric_names:
                if metric_name in self.real_time_values:
                    current_metrics[metric_name] = self.real_time_values[metric_name]
                elif metric_name in self.metric_values and time_window in self.metric_values[metric_name]:
                    # Calculate current value from recent data
                    recent_values = list(self.metric_values[metric_name][time_window])
                    if recent_values:
                        # Get most recent value
                        current_metrics[metric_name] = recent_values[-1].value
                    else:
                        current_metrics[metric_name] = 0.0
                else:
                    current_metrics[metric_name] = 0.0
            
            return current_metrics
    
    async def get_metric_history(
        self,
        metric_name: str,
        time_window: TimeWindow = TimeWindow.MINUTE,
        limit: int = 100
    ) -> List[MetricValue]:
        """Get historical metric values"""
        async with self._lock:
            if metric_name not in self.metric_values:
                return []
            
            history = list(self.metric_values[metric_name][time_window])
            return history[-limit:]
    
    async def create_alert_rule(
        self,
        rule_name -> None: str,
        metric_name -> None: str,
        condition -> None: str,  # e.g., "greater_than", "less_than", "equals"
        threshold -> None: float,
        severity -> None: str = "medium",
        message_template -> None: str = "Alert triggered for {metric_name}"
    ) -> None:
        """Create a new alert rule"""
        if not self.config["enable_alerts"]:
            return
        
        async with self._lock:
            self.alert_rules[rule_name] = {
                "metric_name": metric_name,
                "condition": condition,
                "threshold": threshold,
                "severity": severity,
                "message_template": message_template,
                "enabled": True,
                "last_triggered": 0.0
            }
        
        logger.info("Created alert rule: %s for metric %s", rule_name, metric_name)
    
    async def create_dashboard(self, dashboard -> None: Dashboard) -> None:
        """Create a new dashboard"""
        async with self._lock:
            self.dashboards[dashboard.dashboard_id] = dashboard
        
        logger.info("Created dashboard: %s", dashboard.dashboard_id)
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get current data for a dashboard"""
        async with self._lock:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                raise ValueError(f"Dashboard not found: {dashboard_id}")
            
            # Get current metrics for dashboard
            metrics_data = {}
            for metric_name in dashboard.metrics:
                # Get real-time value
                current_value = self.real_time_values.get(metric_name, 0.0)
                
                # Get recent history
                history = await self.get_metric_history(metric_name, TimeWindow.MINUTE, 60)
                
                metrics_data[metric_name] = {
                    "current_value": current_value,
                    "history": [{"timestamp": mv.timestamp, "value": mv.value} for mv in history]
                }
            
            return {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "metrics": metrics_data,
                "last_updated": time.time(),
                "refresh_interval": dashboard.refresh_interval
            }
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        async with self._lock:
            return [alert for alert in self.alerts.values() if alert.resolved_at is None]
    
    async def resolve_alert(self, alert_id -> None: str) -> None:
        """Resolve an active alert"""
        async with self._lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolved_at = time.time()
                self.service_metrics["active_alerts"] = len([
                    a for a in self.alerts.values() if a.resolved_at is None
                ])
        
        logger.info("Resolved alert: %s", alert_id)
    
    async def query_events(
        self,
        filters: Dict[str, Any],
        time_range: Optional[Tuple[float, float]] = None,
        limit: int = 1000
    ) -> List[AnalyticsEvent]:
        """Query events with filters"""
        async with self._lock:
            filtered_events = []
            
            # Convert deque to list for easier processing
            events_list = list(self.event_stream)
            
            for event in events_list:
                # Apply time range filter
                if time_range:
                    start_time, end_time = time_range
                    if not (start_time <= event.timestamp <= end_time):
                        continue
                
                # Apply other filters
                match = True
                for key, value in filters.items():
                    if key == "event_type" and event.event_type.value != value:
                        match = False
                        break
                    elif key == "source" and event.source != value:
                        match = False
                        break
                    elif key == "user_id" and event.user_id != value:
                        match = False
                        break
                    elif key in event.properties and event.properties[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_events.append(event)
                    
                    if len(filtered_events) >= limit:
                        break
            
            return filtered_events
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        async with self._lock:
            # Calculate current events per second
            current_time = time.time()
            recent_events = [
                e for e in list(self.event_stream)
                if current_time - e.timestamp <= 60  # Last minute
            ]
            
            self.service_metrics["events_per_second"] = len(recent_events) / 60.0
            self.service_metrics["memory_usage"] = len(self.event_stream)
            
            return dict(self.service_metrics)
    
    async def _process_event(self, event -> None: AnalyticsEvent) -> None:
        """Process a single event"""
        start_time = time.time()
        
        async with self._lock:
            # Store event
            self.event_stream.append(event)
            self.event_index[event.source].append(len(self.event_stream) - 1)
            
            # Add to time-windowed storage
            for window in TimeWindow:
                self.windowed_events[window].append(event)
                # Clean old events
                cutoff_time = event.timestamp - window.value
                while (self.windowed_events[window] and 
                       self.windowed_events[window][0].timestamp < cutoff_time):
                    self.windowed_events[window].popleft()
            
            # Update metrics
            await self._update_metrics(event)
            
            # Update service metrics
            self.service_metrics["events_processed"] += 1
            self.service_metrics["last_event_time"] = event.timestamp
            
            processing_time = time.time() - start_time
            self.service_metrics["processing_latency"] = (
                self.service_metrics["processing_latency"] * 0.9 + processing_time * 0.1
            )
    
    async def _update_metrics(self, event -> None: AnalyticsEvent) -> None:
        """Update all relevant metrics for an event"""
        for metric_name, metric_def in self.metric_definitions.items():
            if not metric_def.enabled:
                continue
            
            # Check if event matches metric filter
            if not metric_def.event_filter(event):
                continue
            
            # Calculate metric value
            metric_value = await self._calculate_metric_value(event, metric_def)
            
            if metric_value is not None:
                # Update real-time value
                self.real_time_values[metric_name] = metric_value
                
                # Store in time windows
                for window in metric_def.time_windows:
                    metric_val = MetricValue(
                        metric_name=metric_name,
                        value=metric_value,
                        timestamp=event.timestamp,
                        window=window
                    )
                    
                    self.metric_values[metric_name][window].append(metric_val)
                    
                    # Limit storage size
                    max_values = self._get_max_values_for_window(window)
                    while len(self.metric_values[metric_name][window]) > max_values:
                        self.metric_values[metric_name][window].popleft()
    
    async def _calculate_metric_value(self, event: AnalyticsEvent, metric_def: MetricDefinition) -> Optional[float]:
        """Calculate metric value based on aggregation type"""
        aggregation_type = metric_def.aggregation_type
        field = metric_def.aggregation_field
        
        if aggregation_type == AggregationType.COUNT:
            # For count, we increment by 1 for each matching event
            current_count = self.real_time_values.get(metric_def.metric_name, 0.0)
            return current_count + 1.0
        
        elif aggregation_type == AggregationType.SUM:
            if field and field in event.data:
                current_sum = self.real_time_values.get(metric_def.metric_name, 0.0)
                return current_sum + float(event.data[field])
        
        elif aggregation_type in [AggregationType.AVERAGE, AggregationType.MIN, AggregationType.MAX]:
            # For these, we need to recalculate from recent events
            return await self._calculate_aggregate_metric(metric_def, TimeWindow.MINUTE)
        
        elif aggregation_type == AggregationType.RATE:
            # Calculate rate over time window
            return await self._calculate_rate_metric(metric_def, TimeWindow.MINUTE)
        
        elif aggregation_type == AggregationType.UNIQUE_COUNT:
            # Count unique values
            return await self._calculate_unique_count_metric(metric_def, TimeWindow.MINUTE)
        
        return None
    
    async def _calculate_aggregate_metric(self, metric_def: MetricDefinition, window: TimeWindow) -> float:
        """Calculate aggregate metrics (avg, min, max) over time window"""
        # Get events matching the metric within the time window
        current_time = time.time()
        cutoff_time = current_time - window.value
        
        matching_events = []
        for event in self.windowed_events[window]:
            if (event.timestamp >= cutoff_time and 
                metric_def.event_filter(event) and
                metric_def.aggregation_field in event.data):
                matching_events.append(float(event.data[metric_def.aggregation_field]))
        
        if not matching_events:
            return 0.0
        
        if metric_def.aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(matching_events)
        elif metric_def.aggregation_type == AggregationType.MIN:
            return min(matching_events)
        elif metric_def.aggregation_type == AggregationType.MAX:
            return max(matching_events)
        elif metric_def.aggregation_type == AggregationType.MEDIAN:
            return statistics.median(matching_events)
        elif metric_def.aggregation_type == AggregationType.PERCENTILE and metric_def.percentile:
            return statistics.quantiles(matching_events, n=100)[int(metric_def.percentile) - 1]
        
        return 0.0
    
    async def _calculate_rate_metric(self, metric_def: MetricDefinition, window: TimeWindow) -> float:
        """Calculate rate metric (events per second)"""
        current_time = time.time()
        cutoff_time = current_time - window.value
        
        matching_events = sum(
            1 for event in self.windowed_events[window]
            if event.timestamp >= cutoff_time and metric_def.event_filter(event)
        )
        
        return matching_events / window.value
    
    async def _calculate_unique_count_metric(self, metric_def: MetricDefinition, window: TimeWindow) -> float:
        """Calculate unique count metric"""
        current_time = time.time()
        cutoff_time = current_time - window.value
        
        if not metric_def.aggregation_field:
            return 0.0
        
        unique_values = set()
        for event in self.windowed_events[window]:
            if (event.timestamp >= cutoff_time and 
                metric_def.event_filter(event) and
                metric_def.aggregation_field in event.data):
                unique_values.add(event.data[metric_def.aggregation_field])
        
        return len(unique_values)
    
    def _get_max_values_for_window(self, window: TimeWindow) -> int:
        """Get maximum number of values to store for a time window"""
        base_retention = self.config["metric_retention_hours"] * 3600
        
        if window == TimeWindow.SECOND:
            return min(3600, base_retention)  # Max 1 hour of seconds
        elif window == TimeWindow.MINUTE:
            return min(1440, base_retention // 60)  # Max 24 hours of minutes
        elif window == TimeWindow.HOUR:
            return min(168, base_retention // 3600)  # Max 7 days of hours
        else:
            return min(30, base_retention // 86400)  # Max 30 days
    
    async def _processing_loop(self) -> None:
        """Main event processing loop"""
        batch = []
        batch_size = self.config["batch_processing_size"]
        
        while not self.shutdown_event.is_set():
            try:
                # Collect events in batches for efficiency
                while len(batch) < batch_size:
                    try:
                        event = await asyncio.wait_for(self.processing_queue.get(), timeout=0.1)
                        batch.append(event)
                    except asyncio.TimeoutError:
                        break
                
                # Process batch
                if batch:
                    for event in batch:
                        await self._process_event(event)
                    batch.clear()
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in processing loop: %s", e)
                await asyncio.sleep(1)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup loop: %s", e)
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old data to manage memory"""
        current_time = time.time()
        retention_seconds = self.config["metric_retention_hours"] * 3600
        cutoff_time = current_time - retention_seconds
        
        async with self._lock:
            # Clean old events from main stream
            while (self.event_stream and 
                   self.event_stream[0].timestamp < cutoff_time):
                self.event_stream.popleft()
            
            # Clean old metric values
            for metric_name in self.metric_values:
                for window in self.metric_values[metric_name]:
                    values = self.metric_values[metric_name][window]
                    while values and values[0].timestamp < cutoff_time:
                        values.popleft()
            
            # Clean old alerts from history
            max_history = self.config["max_alert_history"]
            if len(self.alert_history) > max_history:
                self.alert_history = self.alert_history[-max_history:]
        
        logger.debug("Completed data cleanup")
    
    async def _alert_loop(self) -> None:
        """Background alert checking loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config["dashboard_refresh_rate"])
                await self._check_alerts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in alert loop: %s", e)
    
    async def _check_alerts(self) -> None:
        """Check all alert rules"""
        if not self.config["enable_alerts"]:
            return
        
        current_time = time.time()
        cooldown = self.config["alert_cooldown_seconds"]
        
        async with self._lock:
            for rule_name, rule in self.alert_rules.items():
                if not rule["enabled"]:
                    continue
                
                # Check cooldown
                if current_time - rule["last_triggered"] < cooldown:
                    continue
                
                metric_name = rule["metric_name"]
                condition = rule["condition"]
                threshold = rule["threshold"]
                
                # Get current metric value
                current_value = self.real_time_values.get(metric_name, 0.0)
                
                # Check condition
                triggered = False
                if condition == "greater_than" and current_value > threshold:
                    triggered = True
                elif condition == "less_than" and current_value < threshold:
                    triggered = True
                elif condition == "equals" and abs(current_value - threshold) < 0.001:
                    triggered = True
                elif condition == "greater_than_or_equal" and current_value >= threshold:
                    triggered = True
                elif condition == "less_than_or_equal" and current_value <= threshold:
                    triggered = True
                
                if triggered:
                    await self._trigger_alert(rule_name, rule, current_value)
    
    async def _trigger_alert(self, rule_name -> None: str, rule -> None: Dict[str, Any], current_value -> None: float) -> None:
        """Trigger an alert"""
        alert_id = f"alert_{int(time.time())}_{rule_name}"
        
        message = rule["message_template"].format(
            metric_name=rule["metric_name"],
            current_value=current_value,
            threshold=rule["threshold"]
        )
        
        alert = Alert(
            alert_id=alert_id,
            metric_name=rule["metric_name"],
            condition=rule["condition"],
            threshold=rule["threshold"],
            current_value=current_value,
            severity=rule["severity"],
            message=message,
            triggered_at=time.time()
        )
        
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        rule["last_triggered"] = time.time()
        
        self.service_metrics["active_alerts"] = len([
            a for a in self.alerts.values() if a.resolved_at is None
        ])
        
        logger.warning("Alert triggered: %s - %s", alert_id, message)
    
    async def _initialize_default_metrics(self) -> None:
        """Initialize default system metrics"""
        # Events per second metric
        await self.register_metric(MetricDefinition(
            metric_name="events_per_second",
            event_filter=lambda e: True,  # All events
            aggregation_type=AggregationType.RATE,
            time_windows=[TimeWindow.MINUTE, TimeWindow.HOUR]
        ))
        
        # Error rate metric
        await self.register_metric(MetricDefinition(
            metric_name="error_rate",
            event_filter=lambda e: e.event_type == EventType.ERROR_EVENT,
            aggregation_type=AggregationType.RATE,
            time_windows=[TimeWindow.MINUTE, TimeWindow.HOUR]
        ))
        
        # User actions metric
        await self.register_metric(MetricDefinition(
            metric_name="user_actions",
            event_filter=lambda e: e.event_type == EventType.USER_ACTION,
            aggregation_type=AggregationType.COUNT,
            time_windows=[TimeWindow.MINUTE, TimeWindow.HOUR, TimeWindow.DAY]
        ))
        
        # Unique users metric
        await self.register_metric(MetricDefinition(
            metric_name="unique_users",
            event_filter=lambda e: e.user_id is not None,
            aggregation_type=AggregationType.UNIQUE_COUNT,
            aggregation_field="user_id",
            time_windows=[TimeWindow.HOUR, TimeWindow.DAY]
        ))

# Global real-time analytics service instance
_analytics_service: Optional[RealTimeAnalyticsService] = None

async def get_analytics_service() -> RealTimeAnalyticsService:
    """Get global real-time analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = RealTimeAnalyticsService()
        await _analytics_service.start()
    return _analytics_service

async def shutdown_analytics_service() -> None:
    """Shutdown global real-time analytics service"""
    global _analytics_service
    if _analytics_service:
        await _analytics_service.stop()
        _analytics_service = None

if __name__ == "__main__":
    async def test_analytics_service() -> None:
        """Test real-time analytics service functionality"""
        service = RealTimeAnalyticsService()
        await service.start()
        
        try:
            # Create test events
            events = [
                AnalyticsEvent(
                    event_id=f"event_{i}",
                    event_type=EventType.USER_ACTION,
                    source="test_app",
                    timestamp=time.time(),
                    user_id=f"user_{i % 10}",
                    data={"action": "click", "value": i * 10},
                    properties={"page": "home"}
                )
                for i in range(50)
            ]
            
            # Ingest events
            for event in events:
                await service.ingest_event(event)
            
            # Wait for processing
            await asyncio.sleep(1)
            
            # Get real-time metrics
            metrics = await service.get_real_time_metrics()
            print(f"Real-time metrics: {metrics}")
            
            # Create custom metric
            await service.register_metric(MetricDefinition(
                metric_name="click_value_average",
                event_filter=lambda e: e.data.get("action") == "click",
                aggregation_type=AggregationType.AVERAGE,
                aggregation_field="value"
            ))
            
            # Create alert rule
            await service.create_alert_rule(
                "high_user_activity",
                "user_actions",
                "greater_than",
                30.0,
                "medium",
                "High user activity detected: {metric_name} = {current_value}"
            )
            
            # Create dashboard
            dashboard = Dashboard(
                dashboard_id="main_dashboard",
                name="Main Analytics Dashboard",
                metrics=["events_per_second", "user_actions", "unique_users"],
                refresh_interval=30
            )
            await service.create_dashboard(dashboard)
            
            # Get dashboard data
            dashboard_data = await service.get_dashboard_data("main_dashboard")
            print(f"Dashboard data: {dashboard_data}")
            
            # Get service metrics
            service_metrics = await service.get_service_metrics()
            print(f"Service metrics: {service_metrics}")
            
            # Query events
            filtered_events = await service.query_events(
                {"event_type": "user_action"},
                limit=10
            )
            print(f"Filtered events: {len(filtered_events)}")
            
        finally:
            await service.stop()
    
    # Run test
    asyncio.run(test_analytics_service())